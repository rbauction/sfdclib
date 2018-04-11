"""Class to work with the Salesforce SOAP API.
"""

from base64 import b64encode, b64decode
from xml.etree import ElementTree as ET

import sfdclib.messages as msg


class SfdcSoapApi(object):
    """Class to work with the Salesforce SOAP API.
    """
    _SOAP_API_BASE_URI = "/services/Soap/c/{version}"
    _XML_NAMESPACES = {
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
        'ep': 'urn:enterprise.soap.sforce.com'
    }

    def __init__(self, session):
        if not session.is_connected():
            raise Exception("Session must be connected prior to instantiating this class")
        self._session = session
        self._deploy_zip = None

    def _get_api_url(self):
        return "%s%s" % (
            self._session.get_server_url(),
            self._SOAP_API_BASE_URI.format(**{'version': self._session.get_api_version()}))

    def describe_sobject_type(self, sobject_name):
        """Gets details for an object through the describeSObjec SOAP API.

        :param sobject_name: The name of the object
        """
        version_string = str(self._session.get_api_version())
        attributes = {
            'sessionId': self._session.get_session_id(),
            'majorNumber': version_string.split(".")[0],
            'minorNumber': version_string.split(".")[1],
            'sobjectName': sobject_name
        }

        request = msg.DESCRIBE_SOBJECT_MSG.format(**attributes)
        headers = {'Content-type': 'text/xml', 'SOAPAction': 'describeSObject'}
        res = self._session.post(self._get_api_url(), headers=headers, data=request)
        if res.status_code != 200:
            raise Exception(
                "Request failed with %d code and error [%s]" %
                (res.status_code, res.text))

        root = ET.fromstring(res.text)
        return root
