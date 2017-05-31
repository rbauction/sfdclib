*******
SFDClib
*******

SFDClib is a Salesforce.com Metadata API and Tooling API client built for Python 3.3 and 3.4.

Usage
-----
To use API classes one needs to create a session first by instantiating SfdcSession class and passing login details to the constructor.

One method is to pass in the username, password, and token:

.. code-block:: python

    from sfdclib import SfdcSession

    s = SfdcSession(
        'username': 'sfdcadmin@company.com.sandbox',
        'password': 'Pa$sw0rd',
        'token': 'TOKEN',
        'is_sandbox': True
    )
    s.login()

A second method, if you've already logged in elsewhere, is to pass in the instance and session_id. This method does not require calling login().

.. code-block:: python

    from sfdclib import SfdcSession

    s = SfdcSession(
        'session_id': 'thiswillbeaverylongstringofcharactersincludinglettersspacesandsymbols',
        'instance': 'custom-sf-site.my'
    )
    # Notice we are not calling the login() method for this example.

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
| **deploy(zipfile, options)** - submits deploy request
| **check_deploy_status(id)** - returns 3-tuple containing state, state detail and test result errors
| **retrieve(options)** - submits retrieve request
| **check_retrieve_status(id)** - retrieves retrieve call status. returns 3-tuple containing state, state detail and warning/error messages
| **retrieve_zip(id)** - retrieves resulting ZIP file for the specified Id of retrieve call. returns 4-tuple containing state, state detail, warning/error messages and ZIP file
|

SfdcToolingApi
^^^^^^^^^^^^^^
|
| **anon_query(query)** - executes anonymous SOQL query and returns results in a form of `requests.Response <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_
| **get(uri)** - sends GET request to specified URI
| **post(uri, data)** - sends passed data in a POST request to specified URI
| **delete(uri)** - sends DELETE request to specified URI
|

SfdcBulkApi
^^^^^^^^^^^
|
| **export(object_name, query=None)** - exports data of specified object. If query is not passed only Id field will be exported
| **upsert(object_name, csv_data, external_id_field)** - upserts data to specified object. Records will be matched by external id field
| **update(object_name, csv_data)** - updates data in specified object. Records will be matched by Id field
| **delete(object_name, csv_data)** - deletes data from specified object. Records will be matched by Id field
|

License
-------

This package is released under the MIT license.
