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

    def deploy(self, zipfile, checkonly=False, testlevel="NoTestRun", tests=None):
        ''' Kicks off async deployment, returns deployment id '''
        tests_tag = ""
        if tests is not None:
            for test in tests:
                tests_tag += "            <met:runTests>%s</met:runTests>\n" % test

        attributes = {
            'checkOnly': checkonly,
            'testLevel': testlevel,
            'client': 'Metahelper',
            'sessionId': self._session.get_session_id(),
            'ZipFile': self._read_deploy_zip(zipfile),
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

    def check_deploy_status(self, async_process_id):
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
        state = result.find('mt:status', self._XML_NAMESPACES).text
        state_detail = result.find('mt:stateDetail', self._XML_NAMESPACES)
        state_detail = state_detail.text if state_detail else ""

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

        return state, state_detail, deployment_errors, unit_test_errors
