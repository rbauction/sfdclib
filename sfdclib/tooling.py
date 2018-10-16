''' Class to work with Salesforce Tooling API '''
import json
import datetime
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


class SfdcToolingApi():
    ''' Class to work with Salesforce Tooling API  '''
    _TOOLING_API_BASE_URI = "/services/data/v{version}/tooling"
    _ANON_QUERY_URI = "/query/?{query}"
    _EXECUTE_ANON_APEX_URI = "/executeAnonymous/?{a}"
    _TRACE_FLAG_URI = "/sobjects/traceFlag"
    _APEX_LOG_URI = "/sobjects/ApexLog/{uid}/Body"
    
    def __init__(self, session):
        if not session.is_connected():
            raise Exception("Session must be connected prior to instantiating this class")
        self._session = session

    def _get_tooling_api_uri(self):
        ''' Returns Tooling API base URI for this connection '''
        return self._TOOLING_API_BASE_URI.format(**{'version': self._session.get_api_version()})

    def _get_headers(self):
        ''' Compose HTTP header for request '''
        return {
            'Authorization': 'Bearer %s' % self._session.get_session_id(),
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json'}

    @staticmethod
    def _parse_get_post_response(response):
        try:
            return json.loads(response.text)
        except ValueError:
            raise Exception("Request failed, response is not JSON: %s" % response.text)
    @staticmethod
    def _parse_get_post_response_text(response):
        return response.text
                 

    def get(self, uri):
        ''' HTTP GET request '''
        url = self._session.construct_url(self._get_tooling_api_uri() + uri)
        response = self._session.get(url, headers=self._get_headers())
        return self._parse_get_post_response(response)

    def get_textBody(self, uri):
        ''' HTTP GET request '''
        url = self._session.construct_url(self._get_tooling_api_uri() + uri)
        response = self._session.get(url, headers=self._get_headers())
        return response.text

    def post(self, uri, data):
        ''' HTTP POST request '''
        url = self._session.construct_url(self._get_tooling_api_uri() + uri)
        response = self._session.post(url, headers=self._get_headers(), data=data)
        return self._parse_get_post_response(response)

    def delete(self, uri):
        ''' HTTP DELETE request '''
        try:
            url = self._session.construct_url(self._get_tooling_api_uri() + uri)
            response = self._session.delete(url, headers=self._get_headers())
            if response.status_code != 204:
                raise Exception("Request failed, status code is not 204: %s" % response.text)
        except ValueError:
            raise Exception("Request failed, response is not JSON: %s" % response.text)

    def anon_query(self, query):
        ''' Anonymous query '''
        res = self.get(self._ANON_QUERY_URI.format(**{'query': urlencode({'q': query})}))
        if not isinstance(res, dict):
            raise Exception("Request failed. Response: %s" % res)
        return res

    def getDebug(self, uri):
        ''' HTTP GET request '''
        url = self._session.construct_url(self._get_tooling_api_uri() + uri)
        response = self._session.get(url, headers=self._get_headers())
        return self._parse_get_post_response(response)

    def anon_apex(self, apex):
        ''' Anonymous APEX '''
        res = self.getDebug(self._EXECUTE_ANON_APEX_URI.format(**{'a': urlencode({'anonymousBody': apex})}))
        if not isinstance(res, dict):
            raise Exception("Request failed. Response: %s" % res)
        return res

    def apexLog_Q(self, id):
        ''' Anonymous APEX '''
        res = self.get_textBody(self._APEX_LOG_URI.format(**{'uid': id}))
        return res

    def set_Traceflag(self,tfid):
        # check if there is an existing traceflag
        userId = self.get_sf_user_id(self._session._username)

        tfCheckQ = "SELECT Id FROM TraceFlag WHERE TracedEntityId = '{}'".format(userId)


        tfCheck = self.anon_query(tfCheckQ)
        json_string = json.dumps(tfCheck)
        parsedJSON = json.loads(json_string)
        
        tf_id = ''
        for q in parsedJSON['records']:
            uId = q['Id']
            tf_id = uId
        
        if (tf_id):
            self.delete_Traceflag(tf_id)
        #tomorrowsDate = datetime.date.today() + datetime.timedelta(days=1)
        tomorrowsDate = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        tomorrowsDate = tomorrowsDate.strftime('%Y-%m-%d')
        debugLevelId = self.get_DevDebugLevelId()
        traceFlagPL = '''{
            "ApexCode": "Finest",
            "ApexProfiling": "Error",
            "Callout": "Error",
            "Database": "Error",
            "ExpirationDate": "%s",
            "TracedEntityId": "%s",
            "Validation": "Error",
            "Visualforce": "Error",
            "Workflow": "Error",
            "System": "Error",
            "LogType": "DEVELOPER_LOG",
            "DebugLevelId": "%s"
        }''' % (tomorrowsDate,tfid,debugLevelId)

        # POST
        res = self.post(self._TRACE_FLAG_URI, traceFlagPL)
        return res

    def delete_Traceflag(self,tfID):
        delURI = self._TRACE_FLAG_URI + '/' + tfID
        res = self.delete(delURI)
        return res

    def execute_AnonApex(self,apex):

        # === setup TraceFlag ===
        # get the user id
        userId = self.get_sf_user_id(self._session._username)
        # create traceflag and store it's id for removal later
        traceflagCreationRes = self.set_Traceflag(userId)
        # get the traceflag ID

        traceFlagId = self.get_traceflag_id(traceflagCreationRes)
        # run the apex
        anonApexResponse = self.anon_apex(apex)

        # get auditlog id
        logQuery = "SELECT Id FROM ApexLog WHERE LogUserId = '{}' ORDER BY SystemModstamp DESC NULLS LAST LIMIT 1".format(userId)

        logQRes = self.anon_query(logQuery)
        AuditLogId = self.parse_JSON_Response(logQRes)
        queryResponse = self.apexLog_Q(AuditLogId)
        # remove the traceflag
        self.delete_Traceflag(traceFlagId)
        # return the auditlog body 
        return queryResponse

    def parse_JSON_Response(self, jsonRes):
        json_string = json.dumps(jsonRes)
        parsedJSON = json.loads(json_string)

        for q in parsedJSON['records']:
            uId = q['Id']
            return uId
 

    def get_sf_user_id(self, username):
        userIdQ = "SELECT Id FROM User WHERE Username = '%s'" % (username) 
        userIdQRes = self.anon_query(userIdQ)
        userId = self.parse_JSON_Response(userIdQRes)
        return userId

    def get_traceflag_id(self,traceflagResponse):
        json_string = json.dumps(traceflagResponse)
        parsedJSON = json.loads(json_string)
        traceFlagId = parsedJSON['id']
        return traceFlagId

    def get_DevDebugLevelId(self):
        devDebuglogIdRes = self.anon_query("select DebugLevelId from TraceFlag WHERE LogType = 'DEVELOPER_LOG' LIMIT 1")
        json_string = json.dumps(devDebuglogIdRes)
        parsedJSON = json.loads(json_string)
        for d in parsedJSON['records']:
            debugLevelId = d['DebugLevelId']
            return debugLevelId
