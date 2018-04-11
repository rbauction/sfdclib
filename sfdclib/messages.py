""" Salesforce API message templates """
DEPLOY_MSG = \
    """<soapenv:Envelope
xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:met="http://soap.sforce.com/2006/04/metadata">
   <soapenv:Header>
      <met:CallOptions>
         <met:client>{client}</met:client>
      </met:CallOptions>
      <met:SessionHeader>
         <met:sessionId>{sessionId}</met:sessionId>
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:deploy>
         <met:ZipFile>{ZipFile}</met:ZipFile>
         <met:DeployOptions>
            <met:allowMissingFiles>false</met:allowMissingFiles>
            <met:autoUpdatePackage>false</met:autoUpdatePackage>
            {checkOnly}
            <met:ignoreWarnings>false</met:ignoreWarnings>
            <met:performRetrieve>false</met:performRetrieve>
            <met:purgeOnDelete>false</met:purgeOnDelete>
            <met:rollbackOnError>true</met:rollbackOnError>
            <met:singlePackage>true</met:singlePackage>
            {testLevel}
            {tests}
         </met:DeployOptions>
      </met:deploy>
   </soapenv:Body>
</soapenv:Envelope>"""

CHECK_DEPLOY_STATUS_MSG = \
    """<soapenv:Envelope
xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:met="http://soap.sforce.com/2006/04/metadata">
   <soapenv:Header>
      <met:CallOptions>
         <met:client>{client}</met:client>
      </met:CallOptions>
      <met:SessionHeader>
         <met:sessionId>{sessionId}</met:sessionId>
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:checkDeployStatus>
         <met:asyncProcessId>{asyncProcessId}</met:asyncProcessId>
         <met:includeDetails>{includeDetails}</met:includeDetails>
      </met:checkDeployStatus>
   </soapenv:Body>
</soapenv:Envelope>"""

RETRIEVE_MSG = \
    """<soapenv:Envelope
xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:met="http://soap.sforce.com/2006/04/metadata">
   <soapenv:Header>
      <met:CallOptions>
         <met:client>{client}</met:client>
      </met:CallOptions>
      <met:SessionHeader>
         <met:sessionId>{sessionId}</met:sessionId>
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:retrieve>
         <met:retrieveRequest>
            <met:apiVersion>{apiVersion}</met:apiVersion>
            <met:singlePackage>{singlePackage}</met:singlePackage>
            <met:unpackaged>{unpackaged}</met:unpackaged>
         </met:retrieveRequest>
      </met:retrieve>
   </soapenv:Body>
</soapenv:Envelope>"""

CHECK_RETRIEVE_STATUS_MSG = \
    """<soapenv:Envelope
xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:met="http://soap.sforce.com/2006/04/metadata">
   <soapenv:Header>
      <met:CallOptions>
         <met:client>{client}</met:client>
      </met:CallOptions>
      <met:SessionHeader>
         <met:sessionId>{sessionId}</met:sessionId>
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:checkRetrieveStatus>
         <met:asyncProcessId>{asyncProcessId}</met:asyncProcessId>
         <met:includeZip>{includeZip}</met:includeZip>
      </met:checkRetrieveStatus>
   </soapenv:Body>
</soapenv:Envelope>"""

DESCRIBE_METADATA_MSG = """
<soapenv:Envelope
   xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
   xmlns:met="http://soap.sforce.com/2006/04/metadata"
>
   <soapenv:Header>
      <met:CallOptions>
         <met:client>{client}</met:client>
      </met:CallOptions>
      <met:SessionHeader>
         <met:sessionId>{sessionId}</met:sessionId>
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:describeMetadata>
         <met:asOfVersion>{apiVersion}</met:asOfVersion>
      </met:describeMetadata>
   </soapenv:Body>
</soapenv:Envelope>
"""

LIST_METADATA_MSG = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:met="http://soap.sforce.com/2006/04/metadata">
   <soapenv:Header>
      <met:CallOptions>
         <met:client>{client}</met:client>
      </met:CallOptions>
      <met:SessionHeader>
         <met:sessionId>{sessionId}</met:sessionId>
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:listMetadata>
         {queries}
         <met:asOfVersion>{apiVersion}</met:asOfVersion>
      </met:listMetadata>
   </soapenv:Body>
</soapenv:Envelope>
"""

DESCRIBE_SOBJECT_MSG = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:enterprise.soap.sforce.com">
   <soapenv:Header>>
      <urn:PackageVersionHeader>
         <urn:packageVersions>
            <urn:majorNumber>{majorNumber}</urn:majorNumber>
            <urn:minorNumber>{minorNumber}</urn:minorNumber>
         </urn:packageVersions>
      </urn:PackageVersionHeader>
      <urn:SessionHeader>
         <urn:sessionId>{sessionId}</urn:sessionId>
      </urn:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <urn:describeSObject>
         <urn:sObjectType>{sobjectName}</urn:sObjectType>
      </urn:describeSObject>
   </soapenv:Body>
</soapenv:Envelope>
"""
