''' Class to work with Salesforce Metadata API '''
from base64 import b64encode
from xml.etree import ElementTree as ET

import sfdclib.messages as msg


class SfdcMetadataApi:
    ''' Class to work with Salesforce Metadata API '''
    _METADATA_API_BASE_URI = "/services/Soap/m/{version}"
    _XML_NAMESPACES = {
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
        'mt': 'http://soap.sforce.com/2006/04/metadata'
    }

    def __init__(self, session):
        if not session.is_connected():
            raise Exception("Session must be connected prior to instantiating this class")
        self._session = session
        self._deploy_zip = None

    def _get_api_url(self):
        return "%s%s" % (
            self._session.get_server_url(),
            self._METADATA_API_BASE_URI.format(**{'version': self._session.get_api_version()}))

    def deploy(self, zipfile, options):
        ''' Kicks off async deployment, returns deployment id '''
        tests_tag = ""
        if options['tests'] is not None:
            for test in options['tests']:
                tests_tag += "            <met:runTests>%s</met:runTests>\n" % test

        attributes = {
            'client': 'Metahelper',
            'sessionId': self._session.get_session_id(),
            'ZipFile': self._read_deploy_zip(zipfile),
            'checkOnly': options['checkonly'],
            'testLevel': options['testlevel'],
            'tests': tests_tag
        }
        request = msg.DEPLOY_MSG.format(**attributes)

        headers = {'Content-type': 'text/xml', 'SOAPAction': 'deploy'}
        res = self._session.post(self._get_api_url(), headers=headers, data=request)
        if res.status_code != 200:
            raise Exception(
                "Request failed with %d code and error [%s]" %
                (res.status_code, res.text))

        async_process_id = ET.fromstring(res.text).find(
            'soapenv:Body/mt:deployResponse/mt:result/mt:id',
            self._XML_NAMESPACES).text
        state = ET.fromstring(res.text).find(
            'soapenv:Body/mt:deployResponse/mt:result/mt:state',
            self._XML_NAMESPACES).text

        return async_process_id, state

    @staticmethod
    def _read_deploy_zip(zipfile):
        file = open(zipfile, 'rb')
        raw = file.read()
        file.close()
        return b64encode(raw).decode("utf-8")

    def _retrieve_deploy_result(self, async_process_id):
        ''' Retrieves status for specified deployment id '''
        attributes = {
            'client': 'Metahelper',
            'sessionId': self._session.get_session_id(),
            'asyncProcessId': async_process_id,
            'includeDetails': 'true'
            }
        mt_request = msg.CHECK_DEPLOY_STATUS_MSG.format(**attributes)
        headers = {'Content-type': 'text/xml', 'SOAPAction': 'checkDeployStatus'}
        res = self._session.post(self._get_api_url(), headers=headers, data=mt_request)
        root = ET.fromstring(res.text)
        result = root.find(
            'soapenv:Body/mt:checkDeployStatusResponse/mt:result',
            self._XML_NAMESPACES)
        if result is None:
            raise Exception("Result node could not be found: %s" % res.text)

        return result

    def check_deploy_status(self, async_process_id):
        ''' Checks whether deployment succeeded '''
        result = self._retrieve_deploy_result(async_process_id)
        state = result.find('mt:status', self._XML_NAMESPACES).text
        state_detail = result.find('mt:stateDetail', self._XML_NAMESPACES)
        if state_detail is not None:
            state_detail = state_detail.text

        unit_test_errors = []
        deployment_errors = []
        if state == 'Failed':
            # Deployment failures
            failures = result.findall('mt:details/mt:componentFailures', self._XML_NAMESPACES)
            for failure in failures:
                deployment_errors.append({
                    'type': failure.find('mt:componentType', self._XML_NAMESPACES).text,
                    'file': failure.find('mt:fileName', self._XML_NAMESPACES).text,
                    'status': failure.find('mt:problemType', self._XML_NAMESPACES).text,
                    'message': failure.find('mt:problem', self._XML_NAMESPACES).text})
            # Unit test failures
            failures = result.findall(
                'mt:details/mt:runTestResult/mt:failures',
                self._XML_NAMESPACES)
            for failure in failures:
                unit_test_errors.append({
                    'class': failure.find('mt:name', self._XML_NAMESPACES).text,
                    'method': failure.find('mt:methodName', self._XML_NAMESPACES).text,
                    'message': failure.find('mt:message', self._XML_NAMESPACES).text})

        deployment_detail = {
            'total_count': result.find('mt:numberComponentsTotal', self._XML_NAMESPACES).text,
            'failed_count': result.find('mt:numberComponentErrors', self._XML_NAMESPACES).text,
            'deployed_count': result.find('mt:numberComponentsDeployed', self._XML_NAMESPACES).text,
            'errors': deployment_errors
        }
        unit_test_detail = {
            'total_count': result.find('mt:numberTestsTotal', self._XML_NAMESPACES).text,
            'failed_count': result.find('mt:numberTestErrors', self._XML_NAMESPACES).text,
            'completed_count': result.find('mt:numberTestsCompleted', self._XML_NAMESPACES).text,
            'errors': unit_test_errors
        }

        return state, state_detail, deployment_detail, unit_test_detail

    def download_unit_test_logs(self, async_process_id):
        ''' Downloads Apex logs for unit tests executed during specified deployment '''
        result = self._retrieve_deploy_result(async_process_id)
        print("Results: %s" % ET.tostring(result, encoding="us-ascii", method="xml"))
