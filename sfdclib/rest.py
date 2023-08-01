""" Class to work with Salesforce REST API """
import json
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


class SfdcRestApi:
    """ Class to work with Salesforce REST API """
    _API_BASE_URI = "/services/data/v{version}"
    _SOQL_QUERY_URI = "/query/?{query}"
    _API_APEXREST_URI = "/services/apexrest"

    def __init__(self, session):
        if not session.is_connected():
            raise Exception("Session must be connected prior to instantiating this class")
        self._session = session

    def _get_apexrest_api_uri(self):
        """Returns APEXREST API base URI without the version for this connection"""
        return self._API_APEXREST_URI

    def _get_api_uri(self):
        """ Returns REST API base URI for this connection """
        return self._API_BASE_URI.format(**{'version': self._session.get_api_version()})

    def _get_headers(self):
        """ Compose HTTP header for request """
        return {
            'Authorization': 'Bearer %s' % self._session.get_session_id(),
            'Accept-Encoding': 'gzip',
            'Content_Type': 'application/json'}

    @staticmethod
    def _parse_get_post_response(response):
        try:
            return json.loads(response.text)
        except ValueError:
            raise Exception("Request failed, response is not JSON: %s" % response.text)

    def get(self, uri):
        """ HTTP GET request """
        url = self._session.construct_url(self._get_api_uri() + uri)
        response = self._session.get(url, headers=self._get_headers())
        return self._parse_get_post_response(response)

    def post(self, uri, data):
        """ HTTP POST request """
        url = self._session.construct_url(self._get_api_uri() + uri)
        response = self._session.post(url, headers=self._get_headers(), json=data)
        return self._parse_get_post_response(response)

    def patch(self, uri, data):
        """" HTTP PATCH request"""
        url = self._session.construct_url(self._get_api_uri() + uri)
        response = self._session.patch(url, headers=self._get_headers(), json=data)
        return self._parse_get_post_response(response)

    def delete(self, uri):
        """ HTTP DELETE request """
        try:
            url = self._session.construct_url(self._get_api_uri() + uri)
            response = self._session.delete(url, headers=self._get_headers())
            if response.status_code != 204:
                raise Exception("Request failed, status code is not 204: %s" % response.text)
        except ValueError:
            raise Exception("Request failed, response is not JSON: %s" % response.text)

    def soql_query(self, query):
        """ SOQL query """
        res = self.get(self._SOQL_QUERY_URI.format(**{'query': urlencode({'q': query})}))
        if not isinstance(res, dict):
            raise Exception("Request failed. Response: %s" % res)
        return res
