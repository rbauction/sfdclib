from urllib.parse import urlencode
from xml.etree import ElementTree as ET


class SfdcToolingApi():
    _TOOLING_API_BASE_URI = "/services/data/v{version}/tooling"
    _ANON_QUERY_URI = "/query/?{query}"

    def __init__(self, session):
        if not session.is_connected():
            raise Exception("Session must be connected prior to instantiating this class")
        self._session = session

    def get_tooling_api_uri(self):
        return SfdcToolingApi._TOOLING_API_BASE_URI.format(**{'version': self._session.get_api_version()})

    def anon_query(self, query):
        return self.get(SfdcToolingApi._ANON_QUERY_URI.format(**{'query': urlencode({'q': query})}))

    def _get_headers(self):
        return {
            'Authorization': 'Bearer %s' % self._session.get_session_id(),
            'Accept-Encoding': 'gzip',
            'Content_Type': 'application/json'}

    def get(self, uri):
        url = self._session.construct_url(self.get_tooling_api_uri() + uri)
        r = self._session.get(url, headers=self._get_headers())
        return r.text

    def post(self, uri, data):
        url = self._session.construct_url(self.get_tooling_api_uri() + uri)
        r = self._session.post(url, headers=self._get_headers(), json=data)
        return r.text

    def delete(self, uri):
        url = self._session.construct_url(self.get_tooling_api_uri() + uri)
        r = self._session.delete(url, headers=self._get_headers())
        return r.text
