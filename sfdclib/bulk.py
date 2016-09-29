""" Class to work with Salesforce Bulk API """
import json
import time
from xml.etree import ElementTree as ET


class SfdcBulkApi:
    """ Class to work with Salesforce Bulk API """
    _API_BASE_URI = "/services/async/{version}"
    _SOQL_QUERY_URI = "/query/?{query}"
    _XML_NAMESPACES = {
        'asyncapi': 'http://www.force.com/2009/06/asyncapi/dataload'
    }

    def __init__(self, session):
        if not session.is_connected():
            raise Exception("Session must be connected prior to instantiating this class")
        self._session = session

    def _get_api_uri(self):
        """ Returns Bulk API base URI for this connection """
        return self._API_BASE_URI.format(**{'version': self._session.get_api_version()})

    def _get_headers(self, content_type='application/json'):
        """ Compose HTTP header for request """
        return {
            'X-SFDC-Session': self._session.get_session_id(),
            'Accept-Encoding': 'gzip',
            'Content-Type': "{0}; charset=UTF-8".format(content_type)
        }

    def _create_job(self, operation, object_name, content_type):
        """ Create a job """
        request = {
            'operation': operation,
            'object': object_name,
            'contentType': content_type
        }

        url = self._session.construct_url(self._get_api_uri() + "/job")
        res = self._session.post(url, headers=self._get_headers(), json=request)
        if res.status_code != 201:
            raise Exception(
                "Request failed with %d code and error [%s]" %
                (res.status_code, res.text))
        res_obj = json.loads(res.text)

        return res_obj['id']

    def _close_job(self, job_id):
        """ Close job """
        request = {'state': 'Closed'}

        url = self._session.construct_url(self._get_api_uri() + "/job/{0}".format(job_id))
        res = self._session.post(url, headers=self._get_headers(), json=request)
        if res.status_code != 200:
            raise Exception(
                "Request failed with %d code and error [%s]" %
                (res.status_code, res.text))

    def _add_query_batch(self, job_id, query):
        """ Add query batch to job """
        url = self._session.construct_url(self._get_api_uri() + "/job/{0}/batch".format(job_id))
        res = self._session.post(url, headers=self._get_headers('text/csv'), data=query)

        if res.status_code != 201:
            raise Exception(
                "Request failed with %d code and error [%s]" %
                (res.status_code, res.text))

        return ET.fromstring(res.text).find('asyncapi:id', self._XML_NAMESPACES).text

    def _get_batch_state(self, job_id, batch_id):
        """ Get batch's state """
        url = self._session.construct_url(self._get_api_uri() + "/job/{0}/batch".format(job_id))
        res = self._session.get(url, headers=self._get_headers())

        if res.status_code != 200:
            raise Exception(
                "Request failed with %d code and error [%s]" %
                (res.status_code, res.text))

        batches = ET.fromstring(res.text).findall('asyncapi:batchInfo', self._XML_NAMESPACES)
        for batch in batches:
            if batch_id == batch.find('asyncapi:id', self._XML_NAMESPACES).text:
                return batch.find('asyncapi:state', self._XML_NAMESPACES).text

        raise Exception("Batch was not found")

    def _get_batch_result(self, job_id, batch_id):
        """ Get batch's result """
        # Get result Id first
        url = self._session.construct_url(self._get_api_uri() + "/job/{0}/batch/{1}/result".format(job_id, batch_id))
        res = self._session.get(url, headers=self._get_headers())

        if res.status_code != 200:
            raise Exception(
                "Request failed with %d code and error [%s]" %
                (res.status_code, res.text))

        result_id = ET.fromstring(res.text).find('asyncapi:result', self._XML_NAMESPACES).text

        # Download CSV
        url = self._session.construct_url(
            self._get_api_uri() + "/job/{0}/batch/{1}/result/{2}".format(job_id, batch_id, result_id))
        res = self._session.get(url, headers=self._get_headers('text/csv'))

        if res.status_code != 200:
            raise Exception(
                "Request failed with %d code and error [%s]" %
                (res.status_code, res.text))
        # TODO: Replace with stream object
        return res.text

    def export_object(self, object_name, query=None):
        if query is None:
            query = "SELECT Id FROM {0}".format(object_name)

        # Create async job and add query batch
        job_id = self._create_job('query', object_name, 'CSV')
        batch_id = self._add_query_batch(job_id, query)
        self._close_job(job_id)

        # Wait until batch is processed
        batch_state = self._get_batch_state(job_id, batch_id)
        while batch_state not in ['Completed', 'Failed', 'Not Processed']:
            time.sleep(5)
            batch_state = self._get_batch_state(job_id, batch_id)

        # Retrieve and return data in CSV format
        return self._get_batch_result(job_id, batch_id)
