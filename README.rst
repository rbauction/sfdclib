*******
SFDClib
*******

SFDClib is a Salesforce.com Metadata API and Tooling API client built for Python 3.3 and 3.4.

Usage
-----
To use API classes one needs to create a session first by instantiating SfdcSession class and passing login details to the constructor.

.. code-block:: python

    from sfdclib import SfdcSession

    s = SfdcSession(
        'username': 'sfdcadmin@company.com.sandbox',
        'password': 'Pa$sw0rd',
        'token': 'TOKEN',
        'is_sandbox': True
    )
    s.login()

Then create an instance of corresponding API class passing session object.

.. code-block:: python

    from sfdclib import SfdcToolingApi

    tooling = SfdcToolingApi(s)
    r = tooling.anon_query("SELECT Id, Name FROM User LIMIT 10")

Implemented methods
-------------------

SfdcSession
^^^^^^^^^^^
|
| **login()** - establishes a session with Salesforce
| **is_connected()** - returns True if session has been established
| **get_session_id()** - returns Salesforce session ID
| **get_server_url()** - returns url to the login server (https://**test**.salesforce.com when not connected and https://**instance_name**.salesforce.com when connected)
| **get_api_version()** - returns API version being used (36.0, 37.0, ...)
|

SfdcMetadataApi
^^^^^^^^^^^^^^^
|
| **deploy(zipfile, zipfile, checkonly=False, testlevel="NoTestRun", tests=None)** - deploys or verifies deployment package
| **check_deploy_status(id)** - returns 3-tuple containing state, state detail and test result errors
|

SfdcToolingApi
^^^^^^^^^^^^^^
|
| **anon_query(query)** - executes anonymous SOQL query and returns results in a form of `requests.Response <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_
| **get(uri)** - sends GET request to specified URI
| **post(uri, data)** - sends passed data in a POST request to specified URI
| **delete(uri)** - sends DELETE request to specified URI
|

License
-------

This package is released under the MIT license.
