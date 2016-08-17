import sfdclib.messages as msg

from base64 import b64encode
from xml.etree import ElementTree as ET


class SfdcMetadataApi:
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
            SfdcMetadataApi._METADATA_API_BASE_URI.format(**{'version': self._session.get_api_version()}))

    def deploy(self, zipfile, checkonly=False, testlevel="NoTestRun", tests=None):
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
        mtRequest = msg.DEPLOY_MSG.format(**attributes)

        headers = {'Content-type': 'text/xml', 'SOAPAction': 'deploy'}
        r = self._session.post(self._get_api_url(), headers=headers, data=mtRequest)
        if r.status_code != 200:
            raise Exception("Request failed with %d code and error [%s]" % (r.status_code, r.text))

        asyncProcessId = ET.fromstring(r.text).find('soapenv:Body/mt:deployResponse/mt:result/mt:id', SfdcMetadataApi._XML_NAMESPACES).text
        state = ET.fromstring(r.text).find('soapenv:Body/mt:deployResponse/mt:result/mt:state', SfdcMetadataApi._XML_NAMESPACES).text

        return asyncProcessId, state

    def _read_deploy_zip(self, zipfile):
        f = open(zipfile, 'rb')
        raw = f.read()
        f.close()
        return b64encode(raw).decode("utf-8")

    def check_deploy_status(self, id):
        attributes = {
            'client': 'Metahelper',
            'sessionId': self._session.get_session_id(),
            'asyncProcessId': id,
            'includeDetails': 'true'
            }
        mtRequest = msg.CHECK_DEPLOY_STATUS_MSG.format(**attributes)
        headers = {'Content-type': 'text/xml', 'SOAPAction': 'checkDeployStatus'}
        r = self._session.post(self._get_api_url(), headers=headers, data=mtRequest)
        root = ET.fromstring(r.text)
        state = root.find('soapenv:Body/mt:checkDeployStatusResponse/mt:result/mt:status', SfdcMetadataApi._XML_NAMESPACES).text
        x = root.find('soapenv:Body/mt:checkDeployStatusResponse/mt:result/mt:stateDetail', SfdcMetadataApi._XML_NAMESPACES)
        state_detail = ""
        if x:
            state_detail = x.text
        errors = []
        if state == 'Failed':
            failures = root.findall(
                'soapenv:Body/mt:checkDeployStatusResponse/mt:result/mt:details/mt:runTestResult/mt:failures',
                SfdcMetadataApi._XML_NAMESPACES)
            for f in failures:
                errors.append({
                    'class': f.find('mt:name', SfdcMetadataApi._XML_NAMESPACES).text,
                    'method': f.find('mt:methodName', SfdcMetadataApi._XML_NAMESPACES).text,
                    'message': f.find('mt:message', SfdcMetadataApi._XML_NAMESPACES).text})

        return state, state_detail, errors
