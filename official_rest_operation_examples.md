Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Fetching a NONCE Token from a Service
Fetching a NONCE Token from a Service
This example shows you how to fetch a NONCE token from a service. Use the following GET request.
URI
https://<Windchill server>/Windchill/servlet/odata/PTC/GetCSRFToken()
The token is returned in the JSON response. For example, the response is as shown below:
{
 "@odata.context": "https://windchill.ptc.com/Windchill/servlet/odata/v1/PTC/$metadata#CSRFToken",
 "NonceKey": "CSRF_NONCE",
 "NonceValue": "8q87WtSxvWkSH9FMtsQUboOI5TtCS7gWh8RUb4OG ="
}
The value of CSRF_NONCE returned from this request must be passed as request header in all the examples provided in this User’s Guide to create (POST requests), modify (PUT and PATCH requests), or delete (DELETE request) entities.



Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Creating a Part
Creating a Part
This example shows you how to create a part. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/ProdMgmt/Parts HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
		"Name":"TestWTPart_001",
		"AssemblyMode": {
		"Value": "separable",
		"Display": "Separable"
	},

		"PhantomManufacturingPart" : false,
		"Context@odata.bind": "Containers('OR:wt.pdmlink.PDMLinkProduct:48507000')"
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Creating Multiple Parts
Creating Multiple Parts
This example shows you how to create multiple parts. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/ProdMgmt/CreateParts HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
"Parts": [	
    {
      "Name": "test1",
      "AssemblyMode":
      {"Value": "inseparable"}
     ,
      "DefaultUnit" :
      "Value": "kg"}
     ,
      "DefaultTraceCode":
      {"Value": "X"}
     ,
      "Source":
      {"Value":"buy"}
     ,
      "Context@odata.bind": "Containers('OR:wt.pdmlink.PDMLinkProduct:302725')"
    },
    {
      "Name": "test2",
      "AssemblyMode":
      {"Value": "separable"}
    ,
      "DefaultUnit" :
      {"Value": "ea"}
    ,
      "DefaultTraceCode":
      {"Value": "L"}
    ,
      "Source":
      {"Value":"make"}
    ,
      "Context@odata.bind": "Containers('OR:wt.pdmlink.PDMLinkProduct:302725')"
   }
  ]
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Creating a Part in a Different Organization
Creating a Part in a Different Organization
This example shows you how to create a part in a different organization. In Windchill, set the preference Expose Organization in Preference Management utility to Yes. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/ProdMgmt/Parts HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
		"Name":"TestWTPart_001",
		"AssemblyMode": {
		"Value": "separable",
		"Display": "Separable"
		 },

		"PhantomManufacturingPart" : false,
	    "Organization@odata.bind": "Groups('OR:wt.org.WTOrganization:274098')",
		"Context@odata.bind": "Containers('OR:wt.pdmlink.PDMLinkProduct:48507000')"
	}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Create a Part Usage Link with Occurrences
Create a Part Usage Link with Occurrences
This example shows you how to create a part usage link with occurrences. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:48796525')/Uses HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
 "Quantity" : 2,
 "Unit" : {
	  "Value": "ea",
    "Display": "Each"
  },
 "FindNumber" : "100",
 "LineNumber" : 100,
 "TraceCode": {
	  "Value": "0",
    "Display": "Untraced"
  },
 "Uses@odata.bind" : "Parts('OR:wt.part.WTPart:48796415')",
   "Occurrences": [
        {
            "ReferenceDesignator": "R1",
            "Location": {
                "PointX": 0,
                "PointY": 1,
                "PointZ": 1,
                "PointUnit": "m",
                "AngleX": 1.04,
                "AngleY": 1.04,
                "AngleZ": 1.04,
                "AngleUnit": "r"
            }
        },
        {
            "ReferenceDesignator": "R2",
            "Location":  {
                "PointX": 1,
                "PointY": 1,
                "PointZ": 0,
                "PointUnit": "m",
                "AngleX": 3.14,
                "AngleY": 3.14,
                "AngleZ": 3.14,
                "AngleUnit": "r"
            }
        }
    ]

}



Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Deleting a Part Usage Link
Deleting a Part Usage Link
This example shows you how to delete a part usage link. Use the following DELETE request.
URI
DELETE /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:48796526')/Uses('OR:wt.part.WTPartUsageLink:48796528') HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Reading the Bill of Material (BOM)
Reading the Bill of Material (BOM)
This example shows you how to read the bill of material (BOM) for a product structure. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:44148884')/PTC.ProdMgmt.GetBOM?$expand=Components($expand=Part($select=Name,Number),PartUse,Occurrences;$levels=max) HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{NavigationCriteria={"ID":"OR:wt.filter.NavigationCriteria:186213"}}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Reading the Bill of Material (BOM) Along with Path Details
Reading the Bill of Material (BOM) Along with Path Details
This example shows you how to read the bill of material (BOM) for a product structure.
Use the following POST URI with the request body to retrieve the BOM with expand on occurrences.
URI
POST /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:254405')/PTC.ProdMgmt.GetPartStructure?$expand=Components($expand=Part,PartUse,Occurrence) HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{NavigationCriteria={"ID":"OR:wt.filter.NavigationCriteria:186213"}}
Use the following POST URI with the request body to retrieve the BOM without occurrences.
URI
POST /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:254405')/PTC.ProdMgmt.GetPartStructure?$expand=Components($expand=Part,PartUse)  HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{NavigationCriteria={"ID":"OR:wt.filter.NavigationCriteria:48786407"}}

Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Querying the Part Using a Filter
Querying the Part Using a Filter
This example shows you how to query a part using a filter. Use the following GET request.
URI for Filter Based on Soft Attribute
GET /Windchill/servlet/odata/ProdMgmt/Parts?$filter=contains(CustomAttribute,'value') HTTP/1.1
URI for Filter Based on Part Name
GET /Windchill/servlet/odata/ProdMgmt/Parts?$filter=Name eq 'TestWTPart_001' HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Reading a Part by ID with Expanded Navigation
Reading a Part by ID with Expanded Navigation
This example shows you how to read a part with its ID with expanded navigation. Use the following GET request.
URI for Part Uses Link with Expand Filter
GET /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:48796184')?$expand=Uses HTTP/1.1
URI for Part Uses Link and Its Occurrences with Expand Filter
GET /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:48796184')?$expand=Uses($expand=Occurrences) HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Checking Out a Part
Checking Out a Part
This example shows you how to check out a part. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:48796184')/PTC.ProdMgmt.CheckOut HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  "CheckOutNote" : "This is checkout note."	
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Checking In a Part
Checking In a Part
This example shows you how to check in a part. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:48796184')/PTC.ProgMgmt.CheckIn HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  "CheckInNote" : "This is checkin note."
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Revising Multiple Parts
Revising Multiple Parts
This example shows you how to change the revision of multiple parts. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/ProdMgmt/ReviseParts HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
   "Parts":[
     { "ID": "OR:wt.part.WTPart:270209" }
     ,
     { "ID": "OR:wt.part.WTPart:270219" }
   ]
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Retrieving the Components List for a Part Structure
Retrieving the Components List for a Part Structure
This example shows you how to retrieve a components list for a part structure with the action GetPartsList and by expanding navigation properties Part and PartUses. Use the following POST request.
URI
POST /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:12345')/PTC.ProdMgmt.GetPartsList?$expand=Part,PartUses HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Accept: application/json;odata.metadata=full 


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Updating the Common Attributes of a Part
Updating the Common Attributes of a Part
This example shows you how to update the common attributes of a part. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:918283')/PTC.ProdMgmt.UpdateCommonProperties HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
	  "Updates": {
		"Name":"NewName",
		"Number":"NewNumber",
		"DefaultTraceCode": 
   {
    "Value": "L",
    "Display": "Buy"
   }
	}
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Updating Multiple Parts
Updating Multiple Parts
This example shows you how to update multiple parts in a single call. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/ProdMgmt/UpdateParts HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
   "Parts": [	
     {
        "ID":"OR:wt.part.WTPart:2200087",
        "AssemblyMode":
        {"Value": "inseparable"}
        ,
        "DefaultUnit" :
        {"Value": "kg"}
        ,
        "DefaultTraceCode":
        {"Value": "L"}
     },
    {
       "ID":"OR:wt.part.WTPart:2200095",
       "AssemblyMode":
       {"Value": "separable"}
       ,
       "DefaultUnit" :
       {"Value": "ea"}
       ,
       "DefaultTraceCode":
       {"Value": "S"}
    }
   ]
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Creating a Classified Part
Creating a Classified Part
This example shows you how to create a classified part. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/ProdMgmt/Parts HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  
  "Name": "PartName",
  "EndItem": false,
  "AssemblyMode": {
     "Value": "separable"
  },
  "DefaultUnit": {
     "Value": "ea"
  },
  "DefaultTraceCode": {
     "Value": "0"
  },
  "Source": {
     "Value": "make"
  },
  "GatheringPart": false,            
  "Classification": {
  "ClfNodeInternalName":"CHIPSET",
  "ClassificationAttributes": [{
       "InternalName":"xje136",
       "Value":"10"
     }
    ]
  },
  "Context@odata.bind":"Containers('OR:wt.pdmlink.PDMLinkProduct:146821')",
  "PhantomManufacturingPart": false
            
  }


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Retrieving Information About Classification Attributes
Retrieving Information About Classification Attributes
This example shows you how to retrieve information about classification attributes for the specified classification node. Use the following GET request.
URI
GET /Windchill/servlet/odata/ClfStructure/GetClassificationNodeInfo(clfStructureNameSpace='com.ptc.csm.default_namespace',clfNodeInternalName=’Part’) HTTP/1.1
Response
{
    "@odata.context": "/Windchill/servlet/odata/ClfStructure/$metadata#ClassificationInfo",
    "ClfNodeInternalName": "Part",
    "ClfNodeDisplayName": "Part",
    "ClfNodeHierarchyDisplayName": "Part",
    "ClassificationAttributes": [
        {
            "InternalName": "xje136",
            "DisplayName": "Weight",
            "Value": "0.0",
            "DisplayValue": "0.0"
        },
        {
            "InternalName": "CB89D0417f",
            "DisplayName": "General Description",
            "Value": "0",
            "DisplayValue": "0"
        }
    ]
}
The response returned by the function can be specified as payload to create a classified part.


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Creating a Document in a Different Organization
Creating a Document in a Different Organization
This example shows you how to create a document in a different organization. In Windchill, set the preference Expose Organization in Preference Management utility to Yes. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/DocMgmt/Documents HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  "Name": "TestDoc1", 
  "Description": "TestDoc1_Description", 
  "Title": "TestDoc1_Title", 
  "Organization@odata.bind": "Organizations('OR:wt.inf.container.OrgContainer:373739')", 
  "Context@odata.bind": "Containers('OR:wt.pdmlink.PDMLinkProduct:48788507')"
} 


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Creating a Document
Creating a Document
This example shows you how to create a document. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/DocMgmt/Documents HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  "Name": "TestDoc1",
  "Description": "TestDoc1_Description",
  "Title": "TestDoc1_Title",
  "Context@odata.bind": "Containers('OR:wt.pdmlink.PDMLinkProduct:48788507')"
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Creating Multiple Documents
Creating Multiple Documents
This example shows you how to create multiple documents. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/DocMgmt/CreateDocuments HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  "Documents": [
   { "Name": "test doc1", "Context@odata.bind": "Containers('OR:wt.pdmlink.PDMLinkProduct:302725')" }
    ,
   { "Name": "test doc2", "Context@odata.bind": "Containers('OR:wt.pdmlink.PDMLinkProduct:302725')" }
  ]
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Checking Out a Document
Checking Out a Document
This example shows you how to check out a document. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/DocMgmt/Documents('OR:wt.doc.WTDocument:164057')/PTC.DocMgmt.CheckOut HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
   "CheckOutNote" : "This is checkout note."
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Updating a Document
Updating a Document
This example shows you how to update a document. Use the following PATCH URI with the request body.
URI
PATCH /Windchill/servlet/odata/DocMgmt/Documents('OR:wt.doc.WTDocument:48796553') HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
   "Description": "TestDoc1_Description_Update",
   "CustomAttribute": "This is Test Attribute"
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Updating Multiple Documents
Updating Multiple Documents
This example shows you how to update multiple documents. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/DocMgmt/UpdateDocuments HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
    "Documents": [
       { "ID":"OR:wt.doc.WTDocument:2276131", "Description":"Updated description1", "Title":"Updated title1" }
       ,
       { "ID":"OR:wt.doc.WTDocument:2276126", "Title":"Updated title2" }
   ]
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Uploading Content for a Document
Uploading Content for a Document
This example shows you how to upload content for a document in the following cases:
•Using a local file
•Using URL data
•Using external data
Use the following POST URI with the request body.
Using a Local File
The content can be uploaded in the following stages:
•Stage1—POST URI
POST /Windchill/servlet/odata/DocMgmt/Documents('OR:wt.doc.WTDocument:48796581')/PTC.DocMgmt.uploadStage1Action HTTP/1.1
Stage 1—Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Stage1—Request Body
{
		"noOfFiles":3
	}
Stage1—Sample Output
{
 "@odata.context": "$metadata#CacheDescriptor",
 "value": [
  {
   "ID": null,
   "ReplicaUrl": "https://windchill.ptc.com/Windchill/servlet/WindchillGW/wt.fv.uploadtocache.DoUploadToCache_Server/doUploadToChache_Master?mk=wt.fv.uploadtocache.DoUploadToCache_Server&VaultId=150301&FolderId=150329&CheckSum=456186&sT=1507542170&sign=Ca4ouGGOZiopnqbd4mbUVg%3D%3D&site=https%3A%2F%2Fwindchill.ptc.com%2FWindchill%2Fservlet%2FWindchillGW&AUTH_CODE=HmacMD5&isProxy=true&delegate=wt.fv.uploadtocache.DefaultRestFormGeneratorDelegate",
   "MasterUrl": "https://windchill.ptc.com/Windchill/servlet/WindchillGW",
   "VaultId": 150301,
   "FolderId": 150329,
   "StreamIds": [
                76030,
                76032,
                76031
      ],
   "FileNames": [
                76030,
                76032,
                76031
            ]
        }
		]
	}
•Stage2—The HTTP request for Stage2 must be constructed from ReplicaUrl attribute which is retrieved from Stage1.
Stage2—POST URI
https://windchill.ptc.com/Windchill/servlet/WindchillGW/wt.fv.uploadtocache.DoUploadToCache_Server/doUploadToChache_Master?mk=wt.fv.uploadtocache.DoUploadToCache_Server&VaultId=150301&FolderId=150329&CheckSum=456186&sT=1507542170&sign=Ca4ouGGOZiopnqbd4mbUVg%3D%3D&site=https%3A%2F%2Fwindchill.ptc.com%2FWindchill%2Fservlet%2FWindchillGW&AUTH_CODE=HmacMD5&isProxy=true&delegate=wt.fv.uploadtocache.DefaultRestFormGeneratorDelegate
Stage 2—Request Headers
Content-Type: multipart/form-data; boundary=-----------------------------boundary
Stage2—Request Body
-----------------------------boundary 
Content-Disposition: form-data; name="Master_URL" 
https://windchill.ptc.com/Windchill/servlet/WindchillGW
	----------------------------boundary 
Content-Disposition: form-data; name="CacheDescriptor_array" 
	76030: 76030: 76030; 76031: 76031: 76031; 76032: 76032: 76032; 
	----------------------------boundary 
Content-Disposition: form-data; name="76030"; filename="TestFile1.txt" 
is content of test file 1. 
	----------------------------boundary 
Content-Disposition: form-data; name="76031"; filename="TestFile3.txt" 
is content of test file 3. 
	----------------------------boundary 
Content-Disposition: form-data; name="76032"; filename="TestFile2.txt" 
is content of test file 2. 
	----------------------------boundary
* 
The CacheDescriptor_array contains the following information <streamid>:<filename>:<contentid>:<filesize> where,
•streamid—Specifies the unique content ID from the Stage1 response.
•filename—Specifies the name of the file from the Stage1 response.
•contentid—Same as streamid.
•filesize—Specifies size of the file to be uploaded in bytes (Optional).
The response from Stage2 contains information about the streamId, size of the file created, and encoded CachedContentDescriptor, which is used in Stage3 for uploading content to the document.
Stage2—Sample Output
{
		"contentInfos": [
			{
				"streamId": 76030,
				"fileSize": 2,
				"encodedInfo": "76035%3A2%3A150329%3A76035"
			},
			{
				"streamId": 76031,
				"fileSize": 2,
				"encodedInfo": "76034%3A2%3A150329%3A76034"
			},
			{
				"streamId": 76032,
				"fileSize": 2,
				"encodedInfo": "76033%3A2%3A150329%3A76033"
			}
		]
	}
•Stage3—POST URI
POST /Windchill/servlet/odata/DocMgmt/Documents('OR:wt.doc.WTDocument:48796581')/PTC.DocMgmt.uploadStage3Action HTTP/1.1
Stage 3—Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Stage3—Request body
{
	"contentInfo" : [
		{	
		"StreamId" :76030,
		"EncodedInfo" : "76033%3A2%3A150329%3A76033",
		"FileName" : "DesignSpec.doc",
		"PrimaryContent" : true,
		"MimeType" : "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
		"FileSize" : 2
		},
		{	
		"StreamId" :76031,
		"EncodedInfo" : "76035%3A2%3A150329%3A76035",
		"FileName" : "ReferenceDoc1.doc",
		"PrimaryContent" : false,
		"MimeType" : "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
		"FileSize" : 2
		},
		{	
		"StreamId" :76032,
		"EncodedInfo" : "76034%3A2%3A150329%3A76034",
		"FileName" : "ReferenceDoc2.doc",
		"PrimaryContent" : false,
		"MimeType" : "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
		"FileSize" : 2
		}
	]
	}
Using a URL Data
To create or update primary content from URL data, use the following PUT URI with the request body.
URI
PUT /Windchill/servlet/odata/DocMgmt/Documents('OR:wt.doc.WTDocument:2626068')/PrimaryContent HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
	"UrlLocation" :"https://www.ptc.com",
	"DisplayName" : "Test_PrimaryContent"
}
Using External Storage
To create or update the primary content from external storage, use the following PUT URI with the request body.
URI
PUT /Windchill/servlet/odata/DocMgmt/Documents('OR:wt.doc.WTDocument:2626068')/PrimaryContent HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
	"ExternalLocation" :"TestExternalLocation",
	"DisplayName" : "TestExternalLocation_DisplayName"
}
To create new attachments, use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/DocMgmt/Documents('OR:wt.doc.WTDocument:2626099')/Attachments HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
	"ExternalLocation" :"TestExternalLocation",
	"DisplayName" : "TestExternalLocation"
}
To update existing attachments, use the following PUT URI with the request body.
URI
PUT /Windchill/servlet/odata/DocMgmt/Documents('OR:wt.doc.WTDocument:2626099')/Attachments('OR:wt.content.ExternalStoredData:2626811') HTTP/1.1
Request Body
{
	"ExternalLocation" :"TestExternalLocation_Update",
	"DisplayName" : "TestExternalLocation_Update"
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Data Administration Domain > Create a Folder and Subfolder
Create a Folder and Subfolder
This example shows you how to create a folder and subfolder. Use the following POST URI with the request body.
URI to Create a Folder
POST /Windchill/servlet/odata/DataAdmin/Containers(<oid>)/Folders HTTP/1.1
URI to Create a Subfolder
POST /Windchill/servlet/odata/DataAdmin/Containers(<oid>)/Folders(<oid>)/Folders HTTP/1.1
You can pass the following information in the request header and body for both the URIs.
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
	"Name": "Demo",
	"Description": "Folder for CAD parts"
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Data Administration Domain > Update a Folder
Update a Folder
This example shows you how to update a folder. Use the following PATCH URI with the request body.
URI
PATCH /Windchill/servlet/odata/DataAdmin/Containers(<oid>)/Folders(<oid>) HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
	"Name": "Demo_Updated",
	"Description": "<Description_Update>"
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Data Administration Domain > Delete a Folder
Delete a Folder
This example shows you how to delete a folder. Use the following DELETE URI with the request body.
URI
DELETE /Windchill/servlet/odata/DataAdmin/Containers(<oid>)/Folders(<oid>) HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Principal Management Domain > Retrieving License Groups for a User
Retrieving License Groups for a User
This example shows you how to retrieve license groups for a user. Specify the OID for the user. Use the following GET request.
URI
GET /Windchill/servlet/odata/PrincipalMgmt/Users('<oid>')/LicenseGroups HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Principal Management Domain > Retrieving License Groups for a User with Expanded Navigation
Retrieving License Groups for a User with Expanded Navigation
This example shows you how to retrieve license groups for a user with expanded navigation. Specify the OID for the user. Use the following GET request.
URI
GET /Windchill/servlet/odata/PrincipalMgmt/Users('<oid>')?$expand=LicenseGroups HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Parts List Management Domain > Retrieving Parts List
Retrieving Parts List
This example shows you how to retrieve parts list. Use the following GET request.
URI
GET /Windchill/servlet/odata/PartListMgmt/PartLists HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Parts List Management Domain > Retrieving Information for a Specific Part List
Retrieving Information for a Specific Part List
This example shows you how to retrieve a specific part list. Use the following GET request.
URI
GET /Windchill/servlet/odata/PartListMgmt/PartLists('OR:com.ptc.arbortext.windchill.partlist.PartList:197855') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Parts List Management Domain > Retrieving Parts List Items for a Specific Part List
Retrieving Parts List Items for a Specific Part List
This example shows you how to retrieve parts list items for a specific part list. Use the following GET request.
URI
GET /Windchill/servlet/odata/PartListMgmt/PartLists('OR:com.ptc.arbortext.windchill.partlist.PartList:197855')/Uses HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Parts List Management Domain > Retrieving a Specific Part List Item
Retrieving a Specific Part List Item
This example shows you how to retrieve a specific part list item. Use the following GET request.
URI
GET /Windchill/servlet/odata/PartListMgmt/PartLists('OR:com.ptc.arbortext.windchill.partlist.PartList:197855')/Uses('OR:com.ptc.arbortext.windchill.partlist.PartListItem:240518') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Parts List Management Domain > Retrieving Parts from a Part List with Expanded Navigation
Retrieving Parts from a Part List with Expanded Navigation
This example shows you how to retrieve parts from a part list item with expanded navigation. The response returns information about a part list item along with information about parts that are related to the part list item. Use the following GET request.
URI
GET /Windchill/servlet/odata/PartListMgmt/PartLists('OR:com.ptc.arbortext.windchill.partlist.PartList:197855')/Uses?$expand=Uses HTTP/1.1




Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Parts List Management Domain > Retrieving EPMDocuments from a Part List with Expanded Navigation
Retrieving EPMDocuments from a Part List with Expanded Navigation
This example shows you how to retrieve EPMDocuments from a part list item with expanded navigation. The response returns information about illustrations along with information about EPMDocuments that are related to the illustrations. Use the following GET request.
URI
GET /Windchill/servlet/odata/PartListMgmt/PartLists('OR:com.ptc.arbortext.windchill.partlist.PartList:240515')/DescribedBy('OR:com.ptc.arbortext.windchill.partlist.PartListToEPMDocumentLink:240527')?$expand=DescribedBy HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Parts List Management Domain > Retrieving Illustrations for a Parts List
Retrieving Illustrations for a Parts List
This example shows you how to retrieve illustration for a parts list. Use the following GET request.
URI
GET /Windchill/servlet/odata/PartListMgmt/PartLists('OR:com.ptc.arbortext.windchill.partlist.PartList:197856')/DescribedBy HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Parts List Management Domain > Retrieving a Specific Illustration
Retrieving a Specific Illustration
This example shows you how to retrieve a specific illustration. Use the following GET request.
URI
GET /Windchill/servlet/odata/PartListMgmt/PartLists('OR:com.ptc.arbortext.windchill.partlist.PartList:240515')/DescribedBy('OR:com.ptc.arbortext.windchill.partlist.PartListToEPMDocumentLink:240527') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Parts List Management Domain > Retrieving a Specific Substitute Part
Retrieving a Specific Substitute Part
This example shows you how to retrieve a specific substitute part from a part list item. Use the following GET request.
URI
GET /Windchill/servlet/odata/PartListMgmt/PartListItems('OR:com.ptc.arbortext.windchill.partlist.PartListItem:240521')/Substitutes('OR:com.ptc.arbortext.windchill.partlist.PartListItemSubstituteLink:243635') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Parts List Management Domain > Retrieving a Specific Supplementary Part
Retrieving a Specific Supplementary Part
This example shows you how to retrieve a specific supplementary part from a part list item. Use the following GET request.
URI
GET /Windchill/servlet/odata/PartListMgmt/PartListItems('OR:com.ptc.arbortext.windchill.partlist.PartListItem:240521')/Supplements('OR:com.ptc.arbortext.windchill.partlist.SupplementaryReplacementLink:243640') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Service Information Management Domain > Retrieving Information Structures
Retrieving Information Structures
This example shows you how to retrieve all the information structures. Use the following GET request.
URI
GET /Windchill/servlet/odata/ServiceInfoMgmt/InformationStructures HTTP/1.1
To retrieve a specific information structure, use the following GET request:
URI
GET /Windchill/servlet/odata/ServiceInfoMgmt/InformationStructures(‘OR:wt.part.WTPart:258669’) HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Service Information Management Domain > Retrieving Publication Structures
Retrieving Publication Structures
This example shows you how to retrieve all the publication structures. Use the following GET request.
URI
GET /Windchill/servlet/odata/ServiceInfoMgmt/PublicationStructures HTTP/1.1
To retrieve a specific publication structure, use the following GET request:
URI
GET /Windchill/servlet/odata/ServiceInfoMgmt/PublicationStructures(‘OR:wt.part.WTPart:258623’) HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Service Information Management Domain > Retrieving Publication Structures for Authoring Language French
Retrieving Publication Structures for Authoring Language French
This example shows you how to retrieve all the publication structures, where the authoring language is set to French. Use the following GET request.
URI
GET /Windchill/servlet/odata/ServiceInfoMgmt/PublicationStructures?$filter=AuthoringLanguage/Value eq 'fr' HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Service Information Management Domain > Retrieving and Expanding the Contents of an Information Structure
Retrieving and Expanding the Contents of an Information Structure
This example shows you how to retrieve and expand the contents of an information structure. Use the following POST request.
URI
POST /Windchill/servlet/odata/ServiceInfoMgmt/InformationStructures('OR:wt.part.WTPart:258669')/PTC.ServiceInfoMgmt.GetStructure?$expand=Children($levels=max) HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  "NavigationCriteriaId":"OR:wt.filter.NavigationCriteria:270048"
}
You can choose not to specify the navigation criteria. In this case, the request body is empty, that is, {}. The default navigation criteria is used.


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Service Information Management Domain > Retrieving and Expanding the Contents of a Publication Structure
Retrieving and Expanding the Contents of a Publication Structure
This example shows you how to retrieve and expand the contents of a publication structure. The retrieved contents are sorted by line number. Use the following POST request, with the ServiceObjectUsesLineNumber property.
URI
POST /Windchill/servlet/odata/ServiceInfoMgmt/PublicationStructures('OR:wt.part.WTPart:258646')/PTC.ServiceInfoMgmt.GetStructure?$expand=Children($levels=max ;$orderby=ServiceObjectUsesLineNumber) HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
   "NavigationCriteriaId":"OR:wt.filter.NavigationCriteria:270048"
}
You can choose not to specify the navigation criteria. In this case, the request body is empty, that is, {}. The default navigation criteria is used.


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Example for the PTC Info*Engine System Domain > Invoking an Info*Engine Task
Invoking an Info*Engine Task
This example shows you how to invoke an Info*Engine task.
Consider a task:
wt/federation/delegates/windchill/QueryObjects.xml
The task has two inputs: the Windchill type and a where clause for querying objects.
Use the following POST URI to invoke the task.
URI
POST /Windchill/servlet/odata/IE/InvokeIETask
Request Body
{
    "Task": "wt/federation/delegates/windchill/QueryObjects.xml",
    "Params": [
        {
            "Name": "type",
            "Value": "wt.part.WTPart"
        },
        {
            "Name": "where",
            "Value": "name=GOLF_CART"
        }
    ]
}
The output of this task is a JSON representation of groups and elements contained in the output group of the task.


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Manufacturing Process Management Domain > Retrieving Operations For a Process Plan Using System Default NCs
Retrieving Operations For a Process Plan Using System Default NCs
This example shows you how to retrieve the first-level operations for a process plan. Use the following GET request.
URI
GET /Windchill/servlet/odata/MfgProcMgmt/ProcessPlans('OR:com.ptc.windchill.mpml.processplan.MPMProcessPlan:44148884')/PTC.MfgProcMgmt.Operations(processPlanNavigationCriteriaId='',relatedAssemblyNavigationCriteriaId='') HTTP/1.1
Request Headers
Content-Type: application/json


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Manufacturing Process Management Domain > Retrieving Illustration-Related Contents from an Operation
Retrieving Illustration-Related Contents from an Operation
This example shows you how to retrieve the illustration-related contents associated with an operation. Use the following GET request.
URI
GET /Windchill/servlet/odata/MfgProcMgmt/Operations('OR:com.ptc.windchill.mpml.processplan.operation.MPMOperation:55667788')/PTC.MfgProcMgmt.DownloadUrls() HTTP/1.1
Request Headers
Content-Type: application/json


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Manufacturing Process Management Domain > Retrieving Document-Related Contents from a Sequence
Retrieving Document-Related Contents from a Sequence
This example shows you how to retrieve the primary contents of a document associated with a sequence. Use the following GET request.
URI
GET /Windchill/servlet/odata/MfgProcMgmt/Sequences('OR:com.ptc.windchill.mpml.processplan.sequence.MPMSequence:11223344')/DocumentDescribeLinks?$expand=DescribedBy($expand=PrimaryContent) HTTP/1.1
Request Headers
Content-Type: application/json


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Manufacturing Process Management Domain > Reading the Bill of Process (BOP)
Reading the Bill of Process (BOP)
This example shows you how to read the bill of process (BOP) for a process plan. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/MfgProcMgmt/ProcessPlans('OR:com.ptc.windchill.mpml.processplan.MPMProcessPlan:44148884')/PTC.MfgProcMgmt.GetBOP?$expand=Components($expand=OperationHolder($select=Name,Number),OperationHolderUsageLink;$levels=max) HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
"processPlanNavigationCriteriaId" : "OR:wt.filter.NavigationCriteria:48796407",
"relatedAssemblyNavigationCriteriaId" : "OR:wt.filter.NavigationCriteria:48796408"
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving Problem Reports
Retrieving Problem Reports
This example shows you how to retrieve problem reports. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ProblemReports HTTP/1.1
To retrieve a specific problem report, use the following GET request:
URI
GET /Windchill/servlet/odata/ChangeMgmt/ProblemReports('OR:wt.change2.WTChangeIssue:233708') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving Variances
Retrieving Variances
This example shows you how to retrieve variances. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/Variances HTTP/1.1
To retrieve a specific variance, use the following GET request:
URI
GET /Windchill/servlet/odata/ChangeMgmt/Variances('OR:wt.change2.WTVariance:233682') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving Variances Along with Variance Owners Information
Retrieving Variances Along with Variance Owners Information
This example shows you how to retrieve information about variance owners along with variances. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/Variances?$expand=VarianceOwners HTTP/1.1
To retrieve a specific variance, use the following GET request:
URI
GET /Windchill/servlet/odata/ChangeMgmt/Variances('OR:wt.change2.WTVariance:233682')?$expand=VarianceOwners HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving Change Requests
Retrieving Change Requests
This example shows you how to retrieve change requests. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests HTTP/1.1
To retrieve a specific change request, use the following GET request:
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests('OR:wt.change2.WTChangeRequest2:229667') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving Change Notices
Retrieving Change Notices
This example shows you how to retrieve change notices. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeNotices HTTP/1.1
To retrieve a specific change notice, use the following GET request:
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeNotices('OR:wt.change2.WTChangeOrder2:234109') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving Change Tasks
Retrieving Change Tasks
This example shows you how to retrieve change tasks. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeTasks HTTP/1.1
To retrieve a specific change request, use the following GET request:
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeTasks('OR:wt.change2.WTChangeActivity2:229667') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving the Process Links for Change Objects
Retrieving the Process Links for Change Objects
This example shows you how to retrieve the process links for change objects. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests?$expand=ProcessLinks HTTP/1.1
To retrieve the process links for a specific change object, use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests('OR:wt.change2.WTChangeRequest2:250651')?$expand=ProcessLinks HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving Process Links for a Specific Change Object
Retrieving Process Links for a Specific Change Object
This example shows you how to retrieve process link for a specific change object. Use the following GET request.
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests('OR:wt.change2.WTChangeRequest2:251664')/ProcessLinks HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving the Process Objects for Change Objects
Retrieving the Process Objects for Change Objects
This example shows you how to retrieve the process objects for change objects. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests?$expand=ProcessObjects HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving Process Objects for a Specific Change Object
Retrieving Process Objects for a Specific Change Object
This example shows you how to retrieve process objects for a specific change object. Use the following GET request.
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests('OR:wt.change2.WTChangeRequest2:251664')/ProcessObjects HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving the Reference Objects for Change Objects
Retrieving the Reference Objects for Change Objects
This example shows you how to retrieve the reference objects for change objects. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests?$expand=ReferenceObjects HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving Reference Objects for a Specific Change Object
Retrieving Reference Objects for a Specific Change Object
This example shows you how to retrieve reference objects for a specific change object. Use the following GET request.
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests('OR:wt.change2.WTChangeRequest2:251664')/ReferenceObjects HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving the Reference Links for Change Objects
Retrieving the Reference Links for Change Objects
This example shows you how to retrieve the reference links for change objects. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests?$expand=ReferenceLinks HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving Reference Links for a Specific Change Object
Retrieving Reference Links for a Specific Change Object
This example shows you how to retrieve reference link for a specific change object. Use the following GET request.
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests('OR:wt.change2.WTChangeRequest2:251664')/ReferenceLinks HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving the Affected Links
Retrieving the Affected Links
This example shows you how to the retrieve AffectedLinks for change objects. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests('OR:wt.change2.WTChangeRequest2:250300')?$expand=AffectsLinks HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving the AffectedByLinks
Retrieving the AffectedByLinks
This example shows you how to retrieve the AffectedByLinks links for changeables. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/Changeables('OR:wt.part.WTPart:183749')?$expand=AffectedByLinks HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving the Affected Objects
Retrieving the Affected Objects
This example shows you how to retrieve the AffectedObjects for change objects. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests?$expand=AffectedObjects HTTP/1.1
To retrieve the AffectedObjects for a specific change object, use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests('OR:wt.change2.WTChangeRequest2:250300')?$expand=AffectedObjects HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving the AffectedBy Objects
Retrieving the AffectedBy Objects
This example shows you how to retrieve the AffectedByObjects for changeables. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/Changeables?$expand=AffectedByObjects HTTP/1.1
To retrieve the AffectedByObjects for a specific changeable, use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/Changeables('OR:wt.part.WTPart:262627')?$expand=AffectedByObjects HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving the Affected Links and Affected Objects
Retrieving the Affected Links and Affected Objects
This example shows you how to retrieve the AffectedLinks for change objects, and further retrieve the AffectedObjects. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests('OR:wt.change2.WTChangeRequest2:250300')?$expand=AffectsLinks($expand=AffectedObjects) HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving and Downloading the Attachments Associated with Change Objects
Retrieving and Downloading the Attachments Associated with Change Objects
This example shows you how to retrieve the list of attachments associated with the change objects. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests('OR:wt.change2.WTChangeRequest2:229667')/Attachments HTTP/1.1
To view and download the attachment, use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeRequests('OR:wt.change2.WTChangeRequest2:229667')/Attachments('OR:wt.content.ApplicationData:278667')/$value HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving the Resulting Links
Retrieving the Resulting Links
This example shows you how to the retrieve resulting links for change notices. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeNotices?$expand=ResultingLinks HTTP/1.1
To get details of resulting links and change tasks (ResultedByObjects) , use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeNotices('OR:wt.change2.WTChangeOrder2:264082')?$expand=ResultingLinks($expand=ResultedByObjects) HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving the Resulting Objects
Retrieving the Resulting Objects
This example shows you how to the retrieve resulting objects for change notices. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeNotices?$expand=ResultingObjects HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Change Management Domain > Retrieving the Unincorporated Links
Retrieving the Unincorporated Links
This example shows you how to the retrieve unincorporated links for change notices. Use the following GET request.
URI
GET /Windchill/servlet/odata/ChangeMgmt/ChangeNotices?$expand=UnincorporatedLinks HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Classification Structure Domain > Query Classification Nodes > Retrieving the First Child Node of a Root Node
Retrieving the First Child Node of a Root Node
This example shows you how to retrieve the first child node of a root node. Use the following GET request.
URI
GET /Windchill/servlet/odata/ClfStructure/ClfNodes HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Classification Structure Domain > Query Classification Nodes > Retrieving a Specific Classification Node
Retrieving a Specific Classification Node
This example shows you how to retrieve a specific classification node. Use the following GET request.
URI
GET /Windchill/servlet/odata/ClfStructure/ClfNodes(‘SPRING’) HTTP/1.1
GET /Windchill/servlet/odata/ClfStructure/ClfNodes(‘ElectronicParts’) HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Classification Structure Domain > Query Classification Nodes > Retrieving the Parent Node of a Classification Node
Retrieving the Parent Node of a Classification Node
This example shows you how to retrieve the parent node of the specified classification node. Use the following GET request.
URI
GET /Windchill/servlet/odata/ClfStructure/ClfNodes(‘SPRING’)/ParentNode HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Classification Structure Domain > Query Classification Nodes > Retrieving the Child Nodes of a Classification Node
Retrieving the Child Nodes of a Classification Node
This example shows you how to retrieve all the child nodes of the specified classification node. Use the following GET request.
URI
GET /Windchill/servlet/odata/ClfStructure/ClfNodes(‘SPRING’)/ChildNodes HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Classification Structure Domain > Query Classified Objects > Retrieving Classified Objects Associated with a Classification Node
Retrieving Classified Objects Associated with a Classification Node
This example shows you how to retrieve classified objects, which are associated with a classification node. Use the following GET request.
URI
GET /Windchill/servlet/odata/v1/ClfStructure/ClfNodes(‘SPRING’)/ClassifiedObjects HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Classification Structure Domain > Query Classified Objects > Retrieving a Specific Classified Object
Retrieving a Specific Classified Object
This example shows you how to retrieve a specific classified object. Use the following GET request.
URI
GET /Windchill/servlet/odata/ClfStructure/ClfNodes(‘SPRING’)/ClassifiedObjects(‘OR:wt.part.WTPart:12345’) HTTP/1.11


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Classification Structure Domain > Retrieving Legal or Enumeration values for a Classification Attribute
Retrieving Legal or Enumeration values for a Classification Attribute
This example shows you how to retrieve legal or enumeration values for the specified classification attribute. Use the following GET request.
URI
GET /Windchill/servlet/odata/ClfStructure/GetEnumTypeConstraintOnClfAttributes(nodeInternalName=’SPRING’,clfStructureNameSpace=’com.ptc.csm.default_clf_namespace’,attributeInternalName=’color’) HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Classification Structure Domain > Retrieving Binding Attributes for Classified Object
Retrieving Binding Attributes for Classified Object
This example shows you how to retrieve information about the classification binding attribute for a classified object. Use the following GET request.
URI
GET /Windchill/servlet/odata/ClfStructure/GetClfBindingInfo(oid=’OR:wt.part.WTPart:12345’,clfStructureNameSpace='com.ptc.csm.default_clf_namespace’) HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Saved Search Domain > Retrieving Saved Searches
Retrieving Saved Searches
This example shows you how to retrieve saved searches. Use the following GET request.
URI
GET /Windchill/servlet/odata/SavedSearch/SavedQueries HTTP/1.1
To retrieve a specific saved search, use the following GET request:
URI
GET /Windchill/servlet/odata/SavedSearch/SavedQueries('OR:wt.query.SavedQuery:322032') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Saved Search Domain > Executing a Saved Search
Executing a Saved Search
This example shows you how to execute a saved search. Use the following GET request.
URI
GET /Windchill/servlet/odata/SavedSearch/SavedQueries('OR:wt.query.SavedQuery:313313')/PTC.SavedSearch.ExecuteSavedSearch(Keyword='') HTTP/1.1
URI for Latest Version Search
This example shows you how to execute a saved search using the custom query optionptc.search.latestversion. When the saved search is executed, it retrieves the latest version of the objects. Use the following GET request.
GET  /Windchill/servlet/odata/SavedSearch/SavedQueries('OR:wt.query.SavedQuery:322728')/PTC.SavedSearch.ExecuteSavedSearch(Keyword='')?ptc.search.latestversion=true  


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Saved Search Domain > Retrieving Object Types for a Saved Searches
Retrieving Object Types for a Saved Searches
This example shows you how to retrieve the object types for a saved search. Use the following GET request.
URI
GET /Windchill/servlet/odata/SavedSearch/SavedQueries('OR:wt.query.SavedQuery:311158')/PTC.SavedSearch.GetSelectedTypesFromSavedSearch() HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Visualization Domain > Retrieving a Representation
Retrieving a Representation
This example shows you how to download a representation. Use the following GET request.
URI
GET /Windchill/servlet/odata/Visualization/Representations('OR:wt.viewmarkup.DerivedImage:786687') HTTP/1.1
You can use the function GetPVZ() to download a representation. For this representation, pass the parameter value as true for IncludeAnnotations. Pass the fidelity value as Low Fidelity for the parameter Fidelity.
URI
GET /Windchill/servlet/odata/Visualization/Representations('OR:wt.viewmarkup.DerivedImage:786687')/PTC.Visualization.GetPVZ(IncludeAnnotations=true,Fidelity='Low Fidelity') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Visualization Domain > Retrieving Fidelity Names
Retrieving Fidelity Names
This example shows you how to retrieve the fidelity values associated with a representation. The function GetFidelities() retrieves the fidelity values as PTC.EnumType, in a value-display format. Use the following GET request.
URI
GET /Windchill/servlet/odata/Visualization/Representations('OR:wt.viewmarkup.MultiFidelityDerivedImage:786687')/PTC.Visualization.GetFidelities() HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Audit Domain > Retrieving Audits
Retrieving Audits
This example shows you how to retrieve audits. Use the following GET request.
URI
GET /Windchill/servlet/odata/Audit/Audits HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Audit Domain > Retrieving Information for a Specific Audit
Retrieving Information for a Specific Audit
This example shows you how to retrieve information for a specific audit. Use the following GET request.
URI
GET /Windchill/servlet/odata/Audit/Audits('OR:com.ptc.qualitymanagement.audit.WTChangeAudit:267253')/ HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Audit Domain > Updating Audit Score for a Specific Audit Detail
Updating Audit Score for a Specific Audit Detail
This example shows you how to update the audit score for a specific audit detail. Use the following GET request.
URI
PATCH /Windchill/servlet/odata/Audit/Audits('OR:com.ptc.qualitymanagement.audit.WTChangeAudit:267253')/AuditDetails('OR:com.ptc.qualitymanagement.audit.AuditDetail:267264')/ HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
    “OnSiteAuditScore”:82
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Product Platform Management Domain > Retrieving Options
Retrieving Options
This example shows you how to retrieve options. Use the following GET request.
URI
GET /Windchill/servlet/odata/ProdPlatformMgmt/Options HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Product Platform Management Domain > Retrieving Option Groups for All Options
Retrieving Option Groups for All Options
This example shows you how to retrieve option groups for all options. Use the following GET request
URI
GET /Windchill/servlet/odata/ProdPlatformMgmt/Options?$expand=OptionGroup HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Product Platform Management Domain > Retrieving the Option Group for a Specific Option
Retrieving the Option Group for a Specific Option
This example shows you how to retrieve the option group for a specific option. Use the following GET request
URI
GET /Windchill/servlet/odata/ProdPlatformMgmt/Options('OR:com.ptc.windchill.option.model.Option:139849')/OptionGroup HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Product Platform Management Domain > Retrieving a Specific Option With Option Group
Retrieving a Specific Option With Option Group
This example shows you how to retrieve a specific option with its option group. Use the following GET request
URI
GET /Windchill/servlet/odata/PProdPlatformMgmt/Options('OR:com.ptc.windchill.option.model.Option:139849')?$expand=OptionGroup HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC CAD Document Management Domain > Retrieving a Specific CAD Document
Retrieving a Specific CAD Document
This example shows you how to retrieve a specific CAD document. Use the following GET request.
URI
GET /Windchill/servlet/odata/v1/CADDocumentMgmt/CADDocuments('OR%3Awt.epm.EPMDocument%3A167183') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC CAD Document Management Domain > Retrieving a Specific CAD Document with Expanded Navigation
Retrieving a Specific CAD Document with Expanded Navigation
This example shows you how to retrieve a specific CAD document with expanded navigation. Use the following GET request.
URI
GET /Windchill/servlet/odata/v1/CADDocumentMgmt/CADDocuments('OR%3Awt.epm.EPMDocument%3A167183')?$expand=Uses HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC CAD Document Management Domain > Querying the CAD Document Using a Filter
Querying the CAD Document Using a Filter
This example shows you how to query a specific CAD document using a filter based on document name. Use the following GET request.
URI
GET /Windchill/servlet/odata/v1/CADDocumentMgmt/CADDocuments?$filter=FileName eq ‘ABC.prt’ HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC CAD Document Management Domain > Retrieving Related Parts Information for a Specific CAD Document
Retrieving Related Parts Information for a Specific CAD Document
This example shows you how to retrieve related parts information for a specific CAD document. Use the following GET request.
URI
GET /Windchill/servlet/odata/v1/CADDocumentMgmt/CADDocuments('OR%3Awt.epm.EPMDocument%3A167183')?$expand=PartAssociations($expand=RelatedParts) HTTP/1.1
* 
The related parts information is not returned with this navigation in the following cases:
•When a CAD document contains model items that are related to a Part
•When a CAD document has a custom association to a Part
•When a CAD document drawing has a calculated association to a Part.


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC CAD Document Management Domain > Retrieving References Information for a Specific CAD Document
Retrieving References Information for a Specific CAD Document
This example shows you how to retrieve references information for a specific CAD document. Use the following GET request.
URI
GET /Windchill/servlet/odata/v1/CADDocumentMgmt/CADDocuments('OR%3Awt.epm.EPMDocument%3A167183')?$expand=References HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC CAD Document Management Domain > Retrieving Source Information for a Specific Image CAD Document
Retrieving Source Information for a Specific Image CAD Document
This example shows you how to retrieve the source CAD document for a specific image CAD document. Use the following GET request.
URI
GET /Windchill/servlet/odata/v1/CADDocumentMgmt/CADDocuments('OR%3Awt.epm.EPMDocument%3A167183')?$expand=DerivedSources($expand=SourceCADDocuments) HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC CAD Document Management Domain > Retrieving the CAD Structure using BOMMembersOnly Parameter
Retrieving the CAD Structure using BOMMembersOnly Parameter
This example shows you how to retrieve a CAD structure using BOMMembersOnly parameter. Use the following POST request.
URI
POST /Windchill/servlet/odata/v1/CADDocumentMgmt/CADDocuments('OR%3Awt.epm.EPMDocument%3A167183')/PTC.CADDocumentMgmt.GetStructure?$expand=Components($levels=max) HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
    "BOMMembersOnly" : true
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Effectivity Management Domain > Retrieving Effectivity Contexts
Retrieving Effectivity Contexts
This example shows you how to retrieve effectivity contexts. Use the following GET request.
URI
GET /Windchill/servlet/odata/EffectivityMgmt/PartEffectivityContexts HTTP/1.1
URI to Retrieve a Specific Effectivity Context
This example shows you how to retrieve a specific effectivity context. Use the following GET request.
URI
GET /Windchill/servlet/odata/EffectivityMgmt/PartEffectivityContexts('OR:wt.part.WTPartMaster:156014') HTTP/1.1
URI to Retrieve the Organization of an Effectivity Context
This example shows you how to retrieve the organization of an effectivity context. Use the following GET request.
URI
GET /Windchill/servlet/odata/EffectivityMgmt/PartEffectivityContexts('OR:wt.part.WTPartMaster:156014')?$expand=Organization HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Effectivity Management Domain > Retrieving Effectivities of a Part
Retrieving Effectivities of a Part
This example shows you how to retrieve the effectivities of a part. Use the following GET request.
URI
GET /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:156011')/Effectivities HTTP/1.1
URI with Expand on Effectivities
GET /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:156011')?$expand=Effectivities HTTP/1.1
URI for Retrieving Effectivities and Effectivity Context of a Part
GET /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:156011')?$expand=Effectivities($expand=EffectivityContext) HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Effectivity Management Domain > Retrieving Block Effectivities of a Part
Retrieving Block Effectivities of a Part
This example shows you how to retrieve block effectivities of a part. Use the following GET request.
URI
GET /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:156011')?$expand=Effectivities/PTC.EffectivityMgmt.BlockEffectivity HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Effectivity Management Domain > Retrieving Date Effectivities of a Part
Retrieving Date Effectivities of a Part
This example shows you how to retrieve date effectivities of a part. Use the following GET request.
URI
GET /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:156011')?$expand=Effectivities/PTC.EffectivityMgmt.DateEffectivity HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Effectivity Management Domain > Retrieving Unit Effectivities of a Part
Retrieving Unit Effectivities of a Part
This example shows you how to retrieve unit effectivities, such as, block, MSN, lot, serial-number, of a part. Use the following GET request.
URI
GET /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:156011')?$expand=Effectivities/PTC.EffectivityMgmt.UnitEffectivity HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Effectivity Management Domain > Retrieving Effectivities on an Independent Assigned Expression
Retrieving Effectivities on an Independent Assigned Expression
This example shows you how to retrieve effectivities on an independent assigned expression of a part. Use the following GET request.
URI
GET /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:156011')?$expand=AssignedExpression($expand=Effectivities) HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Event Management Domain > Subscribing to an Event of a Windchill Object Instance
Subscribing to an Event of a Windchill Object Instance
This example shows you how to subscribe to an event that occurs on the specified Windchill object instance. Use the following POST request.
URI
POST /Windchill/servlet/odata/EventMgmt/EventSubscriptions HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  "Name": "TestSubscriptionForDoc",
  "CallbackURL": "https://windchill.ptc.com/Windchill",
  "SubscribedEvent@odata.bind": "Events(' CHANGE_LIFECYCLE_STATE')",
  "LifeCycleState":
  {"Value": "RELEASED"},
  "SubscribedOnEntity@odata.bind": "WindchillEntities('OR:wt.doc.WTDocument:4326293')",
  "SubscribeAllVersions": true,
  "@odata.type":"PTC.EventMgmt.EntityEventSubscription"
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Event Management Domain > Subscribing to an Event of a Windchill Object Type in the Specified Container
Subscribing to an Event of a Windchill Object Type in the Specified Container
This example shows you how to subscribe to an event that occurs on the specified type of Windchill object in the specified container. Use the following POST request.
URI
POST /Windchill/servlet/odata/EventMgmt/EventSubscriptions HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  "Name": "TestContainerSubscription",
  "CallbackURL": "https://windchill.ptc.com/Windchill",
  "SubscribedEvent@odata.bind": "Events(‘EDIT_IDENTITY’)", 
  "SubscribedOnEntityType": "PTC.DocMgmt.Document", 
  "ExpirationDate": "2018-12-20T11:30:00Z", 
  "SubscribedOnContext@odata.bind": "Containers('OR:wt.pdmlink.PDMLinkProduct:79638')", 
  "@odata.type":"PTC.EventMgmt.EntityTypeInContainerEventSubscription" 
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Event Management Domain > Subscribing to an Event of a Windchill Object Type in the Specified Folder
Subscribing to an Event of a Windchill Object Type in the Specified Folder
This example shows you how to subscribe to an event that occurs on the type of specified Windchill object in the specified folder. Use the following POST request.
URI
POST /Windchill/servlet/odata/EventMgmt/EventSubscriptions HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  "Name": "TestFolderSubscription",
  "CallbackURL": "https://windchill.ptc.com/Windchill",
  "SubscribedOnEntityType": "PTC.DocMgmt.Document", 
  "ExpirationDate": "2018-12-20T11:30:00Z", 
  "SubscribedEvent@odata.bind": "Events(' EDIT_ATTRIBUTES’)", 
  "SubscribedOnFolder@odata.bind": "Folders('OR:wt.folder.SubFolder:5012381')", 
  "@odata.type":"PTC.EventMgmt.EntityTypeInFolderEventSubscription" }


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Event Management Domain > Deleting a Subscription
Deleting a Subscription
This example shows you how to delete a subscription. Use the following DELETE request.
URI
DELETE /Windchill/servlet/odata/EventMgmt/EventSubscriptions('OR:wt.notify.NotificationSubscription:5012541') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Supplier Management Domain > Retrieving Sourcing Contexts
Retrieving Sourcing Contexts
This example shows you how to retrieve all the sourcing contexts. Use the following GET request.
URI
GET /Windchill/servlet/odata/SupplierMgmt/SourcingContexts HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Supplier Management Domain > Retrieving Supplier, Manufacturer, and Vendor Parts
Retrieving Supplier, Manufacturer, and Vendor Parts
This example shows you how to retrieve supplier, manufacturer, and vendor parts. Use the following GET requests.
URI for Supplier Parts
GET /Windchill/servlet/odata/ProdMgmt/SupplierParts HTTP/1.1
URI for Manufacturer Parts
GET /Windchill/servlet/odata/ProdMgmt/ManufacturerParts HTTP/1.1
URI for Vendor Parts
GET /Windchill/servlet/odata/ProdMgmt/VendorParts HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Supplier Management Domain > Retrieving AXLEntry for Parts
Retrieving AXLEntry for Parts
This example shows you how to retrieve AXLEntry for parts. Use the following GET requests.
URI for Retrieving AXLEntry
GET /Windchill/servlet/odata/ProdMgmt/Parts?$expand=AXLEntries HTTP/1.1
URI for Retrieving AXLEntry for the Specified Part
GET /Windchill/servlet/odata/ProdMgmt/Parts(‘<Part_ID>’)/AXLEntries HTTP/1.1
URI for Retrieving a Souring Context for a Specified AXLEntry
GET /Windchill/servlet/odata/ProdMgmt/Parts('<Part_ID>')/AXLEntries('<AXLEntry_ID>')/SourcingContext HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Supplier Management Domain > Filtering Parts Based on Sourcing Context and Sourcing Status Using Lambda Expression
Filtering Parts Based on Sourcing Context and Sourcing Status Using Lambda Expression
This example shows you how to filter parts based on sourcing context and sourcing status using the lambda expression. Use the following GET requests.
URI for Filtering Parts with Specified Sourcing Context ID and Sourcing Status Value
GET /Windchill/servlet/odata/ProdMgmt/Parts?$filter=(OEMPartSourcingStatus/any(d:d/SourcingStatus/Value eq 'preferred' and d/SourcingContext/SourcingContextId eq 'com.ptc.windchill.suma.axl.AXLContext:204742')) HTTP/1.1
URI for Filtering Parts with Combinations of Sourcing Status and Contexts
GET /Windchill/servlet/odata/ProdMgmt/ProdMgmt/Parts?$filter=startswith(Name,'OEM') and (OEMPartSourcingStatus/any(d:d/SourcingStatus/Value eq 'preferred' and d/SourcingContext/SourcingContextId eq 'com.ptc.windchill.suma.axl.AXLContext:204742') or OEMPartSourcingStatus/any(d:d/SourcingStatus/Value eq 'do_not_use' and d/SourcingContext/SourcingContextId eq 'com.ptc.windchill.suma.axl.AXLContext:204742')) HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Supplier Management Domain > Creating an AML Entry
Creating an AML Entry
This example shows you how to create an AML entry. Use the following POST request.
URI
POST /Windchill/servlet/odata/ProdMgmt/Parts(‘OEM PART ID’)/AXLEntries HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  "ManufacturerPartSourcingStatus":{"Value":"preferred ","Display":"Preferred"},
  "SourcingContext@odata.bind":"SourcingContexts('OR:com.ptc.windchill.suma.axl.AXLContext:92498')",                   
  "ManufacturerPartReference@odata.bind":"ManufacturerParts('OR:com.ptc.windchill.suma.part.ManufacturerPart:341833')"
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Supplier Management Domain > Creating an AVL Entry
Creating an AVL Entry
This example shows you how to create an AVL entry. Use the following POST request.
URI
POST /Windchill/servlet/odata/ProdMgmt/Parts(‘OEM PART ID’)/AXLEntries HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  "VendorPartSourcingStatus":{"Value":"approved","Display":"Approved"},
  "SourcingContext@odata.bind":"SourcingContexts('OR:com.ptc.windchill.suma.axl.AXLContext:92498')",               
  "VendorPartReference@odata.bind":"VendorParts('OR:com.ptc.windchill.suma.part.VendorPart:341833')"
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Supplier Management Domain > Updating an AXL Entry
Updating an AXL Entry
This example shows you how to update the AXL entry by adding a new vendor part. Use the following PATCH request.
URI
UPDATE /Windchill/servlet/odata/ProdMgmt/Parts('VR:wt.part.WTPart:287234')/AXLEntries('OR:com.ptc.windchill.suma.axl.AXLEntry:304030') HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  "SourcingContext@odata.bind":"SourcingContexts('OR:com.ptc.windchill.suma.axl.AXLContext:93056')",
  "VendorPartReference@odata.bind":"VendorParts('OR:com.ptc.windchill.suma.part.VendorPart:266317')",
  "VendorPartSourcingStatus": {
    "Value": "approved",
    "Display": "Approved"
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Supplier Management Domain > Deleting an AXL Entry
Deleting an AXL Entry
This example shows you how to delete an AXL entry. Use the following DELETE request.
URI
DELETE /Windchill/servlet/odata/ProdMgmt/Parts('OR:wt.part.WTPart:339875')/AXLEntries(‘<ID>’) HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Regulatory Master Domain > Retrieving Regulatory Submissions
Retrieving Regulatory Submissions
This example shows how to retrieve regulatory submissions. Use the following GET request.
URI
GET /Windchill/servlet/odata/RegMstr HTTP/1.1
To retrieve a specific regulatory submission, use the following GET request.
URI
GET /Windchill/servlet/odata/RegMstr('OR:com.ptc.qualitymanagement.regmstr.RegulatorySubmission:237897') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Regulatory Master Domain > Creating a Regulatory Submission
Creating a Regulatory Submission
This example shows how to create a regulatory submission. Use the following POST URI with the request body.
URI
POST /Windchill/servlet/odata/RegMstr/RegulatorySubmissions HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body
{
  "@odata.type": "PTC.RegMstr.org.rnd.SampleInternal",
  "SubmittedTo@odata.bind": "Places(PLACE_ID)",
  "Context@odata.bind": "Containers('Container_ID')",
  "Subject@odata.bind": "Subjects(wtPART_ID)",
  "Name": "Test"
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Workflow Domain > Retrieving Work Items
Retrieving Work Items
This example shows you how to retrieve all the work items. Use the following GET request.
URI
GET /Windchill/servlet/odata/Workflow/WorkItems HTTP/1.1
To get a list of work items assigned to you, use the following GET request.
URI
GET /Windchill/Workflow/GetEnumTypeConstraint(entityName='PTC.Workflow.WorkItem',propertyName='Status') HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Workflow Domain > Querying the Work Items Using a Filter
Querying the Work Items Using a Filter
This example shows you how to query work items using a filter based on activity and status. Use the following GET request.
URI
GET /Windchill/servlet/odata/Workflow/WorkItems?$expand=Activity&$filter=Activity/Name eq 'Analyze Change Request' and Status/Display eq 'Potential' HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Workflow Domain > Retrieving the Routing Options for a Work Item
Retrieving the Routing Options for a Work Item
This example shows you how to retrieve routing options for a specified work item. Use the following GET request.
URI
GET /Windchill/servlet/odata/Workflow/WorkItems('OR:wt.workflow.work.WorkItem:178380')/Activity/UserEventList HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Workflow Domain > Retrieving the Subjects for Work Items
Retrieving the Subjects for Work Items
This example shows you how to retrieve subjects for work items. Use the following GET request.
URI
GET /Windchill/ servlet/odata/Workflow/WorkItems?$expand=Subject HTTP/1.1


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Workflow Domain > Completing a Work Item
Completing a Work Item
This example shows you how to complete a work item. Use the following POST request.
URI
POST /Windchill/servlet/odata/Workflow/WorkItems('OR:wt.workflow.work.WorkItem:{{<workitem_id>}}')/PTC.Workflow.CompleteWorkitem HTTP/1.1
You can pass the following information in the request header.
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Depending on what options you want to set, you can specify those options in the request body.
Request Body for Default Activity
{
 "UserEventList":[],
 "WorkitemComment":"Completing Workitem",
 "VoteAction":"",
 "AutomateFastTrack":false,
 "Variables":[]
}
Request Body with Valid Routing Option
{
 "UserEventList":[ "Reject"],
 "WorkitemComment":"Completing Workitem",
 "VoteAction":"",
 "AutomateFastTrack":false,
 "Variables":[]
}
Request Body with Valid Voting Option
{
 "UserEventList":[],
 "WorkitemComment":"Completing Workitem",
 "VoteAction":"Approve",
 "AutomateFastTrack":false,
 "Variables":[]
}
Request Body with Variables
{
 "UserEventList":[],
 "WorkitemComment":"Completing Workitem",
 "VoteAction":"",
 "AutomateFastTrack":false,
 "Variables":[{
	"Name":"act3_string",
	"Value":"vxcvcvxcv"
	},{
	"Name":"act3_int",
	"Value":"1234"
	},{
	"Name":"act3_boolean",
	"Value":"false"
	},{
	"Name":"act3_date",
	"Value":"01/05/2019"
	}]
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Workflow Domain > Saving a Work Item
Saving a Work Item
This example shows you how to save a work item. Use the following POST request.
URI
POST /Windchill/servlet/odata/v1/Workflow/WorkItems('OR:wt.workflow.work.WorkItem:{{<workitem_id>}}')/PTC.Workflow.SaveWorkitem HTTP/1.1
You can pass the following information in the request header.
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Depending on what options you want to set, you can specify those options in the request body.
Request Body for Default Activity
{	
 "UserEventList":[],
 "WorkitemComment":"Saving Workitem",
 "VoteAction":"",
 "AutomateFastTrack":false,
 "Variables":[]
}
Request Body with Valid Routing Option
{	
 "UserEventList":["Accept"],
 "WorkitemComment":"Saving Workitem",
 "VoteAction":"",
 "AutomateFastTrack":false,
 "Variables":[]
}
Request Body with Valid Voting Option
{
 "UserEventList":[],
 "WorkitemComment":"Saving Workitem",
 "VoteAction":"Do not approve",
 "AutomateFastTrack":false,
 "Variables":[]
}
Request Body with Variables
{	
 "UserEventList":[],
 "WorkitemComment":"Saving Workitem",
 "VoteAction":"",
 "AutomateFastTrack":false,
 "Variables":[{
	"Name":"act3_string",
	"Value":"vxcvcvxcv"
	},{
	"Name":"act3_int",
	"Value":"1234"
	},{
	"Name":"act3_boolean",
	"Value":"false"
	},{
	"Name":"act3_date",
	"Value":"01/05/2019"
	}]
}


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Workflow Domain > Retrieving the List of Valid Users to Reassign Work Items
Retrieving the List of Valid Users to Reassign Work Items
This example shows you how to retrieve list of users to whom the specified work items can be reassigned. Use the following GET request.
URI
GET /Windchill/servlet/odata/v1/Workflow/GetWorkItemReassignUserList(WorkItems=@wi)?@wi=["OR:wt.workflow.work.WorkItem:232279","OR:wt.workflow.work.WorkItem:232290","OR:wt.workflow.work.WorkItem:232297"] HTTP/1.1
@wi represents an alias, which can be replaced with any other name.


Windchill REST Services Domain Capabilities > Examples for Performing Basic REST Operations > Examples for the PTC Workflow Domain > Reassigning Work Items to Another User
Reassigning Work Items to Another User
This example shows you how to reassign work items to another user. Use the following POST request.
URI
GET /Windchill/servlet/odata/Workflow/ReassignWorkItems HTTP/1.1
Request Headers
Content-Type: application/json
CSRF_NONCE: <Use the value from Fetch NONCE example>
Request Body for Default Activity
{ 
 "WorkItems": [{"ID":"OR:wt.workflow.work.WorkItem:162155"}],
 "User": {"ID":"OR:wt.org.WTUser:11"},
 "Comment": "<Reassign_Comment_Optional>" 
}


Windchill REST Services Domain Capabilities > Customizing Domains > Extending Domains > Adding Type Extensions of Windchill Types to PTC Domains
Adding Type Extensions of Windchill Types to PTC Domains
A PTC domain can be extended to add an OData entity that corresponds to a custom soft type created in Windchill. Customizers often create a custom soft type extension in Windchill to add a new behavior to Windchill. For example, consider the case where customizers have created a subclass of WTPart. A soft type com.custom.PurchasePart is created for WTPart. Further an additional string attribute called SupplierName on PurchasePart is also added.
To enable this soft type in Product Management domain, customizers first mirror the ProdMgmt domain folder structure in the custom configuration path. Then, create the PurchasePart.json file. Perform the following steps to enable a soft type:
1.In the custom configuration path, create the following folder structure for the Product Management domain at <Windchill>/codebase/rest/custom/domain/:
◦ProdMgmt
▪<version>
▪entity
2.Create the PurchaseParts.json file at <Windchill>/codebase/rest/custom/domain/ProdMgmt/<version>/entity and add the following content in the file:
{
 "name": "PurchasePart",
 "type": “wcType",
 "wcType": “com.custom.PurchasePart",
 "collectionName": “PurchaseParts",
 "includeInServiceDocument": "false",
 "parent": {
   "name": "Part"
  },
   "attributes": [
  {
   "name": "SupplierName",
   "internalName": "SupplierName",
   "type": "String"
  }
 ]
}
After the configuration, when you visit the metadata URL for Product Management domain, the new entity PurchasePart, which is derived from the part entity is available. The PurchasePart entity also has the SupplierName property. Since the PurchasePart entity is now in the EDM, standard OData URLs can be used to access PurchasePart.


Windchill REST Services Domain Capabilities > Customizing Domains > Extending Domains > Adding Custom Properties to Entities in PTC Domains
Adding Custom Properties to Entities in PTC Domains
A PTC domain can be extended to have custom properties which have been added to Windchill types by customizers. Customizers add new properties for Windchill types such as, WTParts, WTDocuments, and so on. WTParts and WTDocuments are available as Part and Document entities in the Product Management and Document Management domains respectively. You can add new attributes as properties for these entities. To add OwningBusinessUnit and DesignCost attributes to the Part entity from the Product Management domain, the customizers mirror the ProdMgmt domain folder structure in the custom configuration path. Then, create the PartsExt.json file to add custom configuration. In the JSON file, under extends property, add the PTC domain entity which you want to extend. In the attributes property, add the new attributes. Perform the following steps to add custom properties to entities:
1.In the custom configuration path, create the following folder structure for the Product Management domain at <Windchill>/codebase/rest/custom/domain/:
◦ProdMgmt
▪<version>
▪entity
2.Create the PartsExt.json file at <Windchill>/codebase/rest/custom/domain/ProdMgmt/<version>/entity and add the following content in the file:
{
 "extends": "Part",
 "attributes": [
  {
   "name": "OwningBusinessUnit",
   "internalName": "OwningBusinessUnit",
   "type": "String"
  },
  {
   "name": "DesignCost",
   "internalName": "DesignCost",
   "type": "Double"
  }
 ]
}
After the configuration, when you visit the metadata URL for Product Management domain, it shows the new properties OwningBusinessUnit and DesignCost on the Part entity for ProdMgmt domain. Since the Part entity has additional attributes, they can be used in standard OData URLs.


Windchill REST Services Domain Capabilities > Customizing Domains > Extending Domains > Adding Custom Navigation Between Entities in PTC Domains
Adding Custom Navigation Between Entities in PTC Domains
A PTC domain can be extended to have new navigation between entities in a PTC domain. For example, the Product Management domain, does not provide any navigation between Part entities to show parts that are alternates of each other. To provide this navigation, customizers must extend the Product Management domain. To add Alternates navigation between Part entities in the Product Management domain, the customizers mirror the ProdMgmt domain folder structure in the custom configuration path. Then create the PartsExt.json file to add custom configuration. In the JSON file, under extends property, add the PTC domain entity which you want to extend. In the navigations property, add the new navigation. Apart from providing the configurations in the .json file, customizers must also provide the programming logic to create the target entity set while navigating from the source to target entity. This is done in the .js file corresponding to the entity, in this case, PartsExt.js file. Perform the following steps to add custom navigation between entities:
1.In the custom configuration path, create the following folder structure for the Product Management domain at <Windchill>/codebase/rest/custom/domain/:
◦ProdMgmt
▪<version>
▪entity
2.Create the PartsExt.json file at <Windchill>/codebase/rest/custom/domain/ProdMgmt/<version>/entity and add the following content in the file:
{
 "extends": "Part",
 "navigations": [
  {
    "name": "Alternates",
    "target": "Parts",
    "type": "Part",
    "isCollection": true,
    "containsTarget": true
  }
 ]
}
3.Create the PartsExt.js file at <Windchill>/codebase/rest/custom/domain/ProdMgmt/<version>/entity and implement the following hooks:
◦getRelatedEntityCollection—The hook returns the following information:
1.Gets the alternate part entities from the source entities.
2.Puts the alternate part entities in an entity collection.
3.Returns the entity collection in a map.
◦isValidNavigation—The hook returns the following information:
1.Checks if the navigation being carried out is Alternates. If not, it returns null so that the framework can continue processing other navigations.
2.Gets the source part.
3.Navigates to the target part.
4.Verifies that the target part is the same as specified in the input.
5.Returns true or false to indicate the success of the validation.
Many of the hooks have been implemented in PTC provided domains. For code examples of hook implementations, you can see their implementations in any of PTC provided domains.
After the configuration, when you visit the metadata URL for Product Management domain, the Alternates navigation is available for the Part entity. You can navigate from a part to get its alternate parts.


Windchill REST Services Domain Capabilities > Customizing Domains > Extending Domains > Adding New Functions to PTC Domains
Adding New Functions to PTC Domains
A PTC domain can be extended to add both bound and unbound OData functions. OData functionsare available in the EDM of a domain. They are invoked with a GET request to the Odata URL of the function. For example, consider a case where you want to add a bound function to the Product Management domain that identifies costly parts in an entity set Parts. Perform the following steps to add a bound function:
1.In the custom configuration path, create the following folder structure for the PTC Product Management domain at <Windchill>/codebase/rest/custom/domain/:
◦ProdMgmt
▪<version>
▪entity
2.Create the PartsExt.json file at <Windchill>/codebase/rest/custom/domain/ProdMgmt/<version>/entity and add the following content in the file:
{
  "extends": "Part",
  "functions": [
    {
      "name": "GetCostlyParts",
      "description": "Return expensive parts",
      "isComposable": false,
      "parameters": [
    {
      "name": "PartSet",
      "type": "Part",
      "isCollection": true,
      "isNullable": false
    }
    ],
      "returnType": {
      "type": "Part",
      "isCollection": true
      }
    }
  ]
}
Create the PartsExt.js file at <Windchill>/codebase/rest/custom/domain/ProdMgmt/<version>/entity and implement the function. Ensure that the Part entity has a numeric property DevelopmentCost.
function function_GetCostlyParts(data, params) {
    var EntityCollection = Java.type('org.apache.olingo.commons.api.data.EntityCollection');
    var entityCollection = new EntityCollection();
    var partEntities = params.get("PartSet").getValue().getEntities();
    for (var i = 0; i < partEntities.size(); i++) {
        var partEntity = partEntities.get(i);
        var partCostProperty = partEntity.getProperty('DevelopmentCost');
        if (partCostProperty) {
            var partCost = partCostProperty.getValue();
            if (partCost && partCost > 0.10) {
                entityCollection.getEntities().add(partEntity);
            }
        }
    }
    return entityCollection;
}
After the configuration, the GetCostlyParts function is available for the Part entity in the metadata URL of the PTC Product Management domain. You can call the function on the Parts entity set and get a list of the costly parts for the specified set. For example, to get a list of costly parts associated with a specific part in the entity set, use the following URL:
/Parts(<oid>)/UsedBy/PTC.ProdMgmt.GetCostlyParts()
Use unbound functions to work with operations that access or process large entity sets. If you perform operations on bound entity sets, all the entities in the entity set may be passed as input to the function. If an operation accesses a bound entity set, which contains more than 2000 entities, the BoundParameterLimitExceededException is thrown. You can catch the exception by having an alternate implementation in the event if the entity limit is exceeded.
function function_GetCostlyParts(data, params) {
  try {
     var partEntities = params.get("PartSet").getValue().getEntities();
     // Continue on normally...
    }
  catch (ex) {
     var BoundParameterLimitExceededException = Java.type('com.ptc.odata.core.entity.operation.BoundParameterLimitExceededException');
     if (ex instanceof BoundParameterLimitExceededException) {
          // Entity limit exceeded...
       }
    }
}


Windchill REST Services Domain Capabilities > Customizing Domains > Extending Domains > Adding New Actions to PTC Domains
Adding New Actions to PTC Domains
OData actions change the state of the entities and are called with a POST request. These are the basic differences between actions and functions.
In terms of definition, actions are similar to functions. However, there are some differences in definition between actions and functions:
•Actions are defined in the actions property of imports and entity JSON files.
•Actions are named with a prefix of action_.


Windchill REST Services Domain Capabilities > Customizing Domains > Creating New Domains
Creating New Domains
Windchill REST Services enables you to create new domains. The new domains are created in the custom configuration path.
To create a new domain, perform the following steps:
1.Decide a domain identifier and the domain version. Create the domain folder <Windchill>/codebase/rest/custom/domain/<Domain_Identifier>/<Domain_Version>
2.Create the <Windchill>/codebase/rest/custom/domain/<Domain_Identifier>.json file and provide values for domain metadata attributes.
3.Decide which other domains to import and set up the <Windchill>/codebase/rest/custom/domain/<Domain_Identifier>/<Domain_Version>/import.json file.
4.Decide if the domain must have unbound actions or functions and set up the <Windchill>/codebase/rest/custom/domain/<Domain_Identifier>/<Domain_Version>/import.json and <Windchill>/codebase/rest/custom/domain/<Domain_Identifier>/<Domain_Version>/import.js files.
5.If complexTypes are required then set up the complex type JSON files at <Windchill>/codebase/rest/custom/domain/<Domain_Identifier>/<Domain_Version>/complexType.
6.Configure entities and entity relations at <Windchill>/codebase/rest/custom/domain/<Domain_Identifier>/<Domain_Version>/entity.
After these files are setup, the domain is available at the REST root URL and can be accessed by OData URLs.
These are generic instructions to create a domain. You have to create and configure files depending on the entities of the domain. In this User’s Guide, we have provided an example, that shows how to create a domain. The example helps you understand which files to create while configuring a domain.


Windchill REST Services Domain Capabilities > Examples for Customizing Domains > Creating a New Domain
Creating a New Domain
This example shows you how to create a new domain.
Consider an example, where a new domain with the name NewDomain should be created. The Windchill types, WTChangeIssue and Changeable2 must be exposed as ProblemReport and ChangeableItem entities respectively. Further, the ReportedAgainst relationship between ProblemReport and ChangeItem entities must also be exposed. The version v1 should also be set up for NewDomain. Information can only be read from Windchill using the domain. The following properties of the two entities of the domain are exposed:
•ProblemReport
◦Number
◦Name
◦Occurrence date
◦Need date
◦Priority
◦Category
◦State
•ChangeableItem
◦Number
◦Name
◦Revision
◦State
To configure a domain for all the criteria mentioned in the example, perform the following steps:
1.Create the folder <Windchill>/codebase/rest/custom/domain/NewDomain.
2.Create the file <Windchill>/codebase/rest/custom/domain/NewDomain.json with the following content:
{
  "name": "NewDomain",
  "id": "NewDomain",
  "description": "NewDomain Domain",
  "nameSpace": "Custom.NewDomain",
  "containerName": "Windchill",
  "defaultVersion": "1"
   }
3.Create the folder <Windchill>/codebase/rest/custom/domain/NewDomain/v1.
4.Create the file <Windchill>/codebase/rest/custom/domain/NewDomain/v1/import.json with the following content:
{
   "imports": [
   {"name": "PTC", "version": "1"}
  ]
}	
5.Create the folder <Windchill>/codebase/rest/custom/domain/NewDomain/v1/entity.
6.Create the file <Windchill>/codebase/rest/custom/domain/NewDomain/v1/entity/ChangeableItems.json with the following content:
{
  "name": "ChangeableItem",
  "collectionName": "ChangeableItems",
  "type": "wcType",
  "wcType": "wt.change2.Changeable2",
  "description": "Changeable Item",
  "operations": "READ",
  "attributes": [
    {"name": "Name", "internalName": "name", "type": "String"},
    {"name": "Number", "internalName": "number", "type": "String"}
  ],
  "inherits": [
    {"name": "lifecycleManaged"},
    {"name": "versioned"}
  ]
}
7.Create the file <Windchill>/codebase/rest/custom/domain/NewDomain/v1/entity/ProblemReports.json with the following content:
{
 "name": "ProblemReport",
 "collectionName": "ProblemReports",
 "type": "wcType",
 "wcType": "wt.change2.WTChangeIssue",
 "description": "Problem Report",
 "operations": "READ",
 "attributes": [
    {"name": "Name", "internalName": "name", "type": "String"},
    {"name": "Number", "internalName": "number", "type": "String"},
    {"name": "Priority", "internalName": "theIssuePriority", "type": "String"},
    {"name": "Category", "internalName": "theCategory", "type": "String"},
    {"name": "OccurrenceDate", "internalName": "occurrenceDate", "type": "DateTimeOffset"},
    {"name": "NeedDate", "internalName": "needDate", "type": "DateTimeOffset"}
  ],
 "navigations": [
 {"name": "ReportedAgainst", "target": "ChangeableItems", "type": "ChangeableItem", "containsTarget": true, "isCollection": true}
 ],
  "inherits": [
    {"name": "lifecycleManaged"}
  ]
}
8.Create the file <Windchill>/codebase/rest/custom/domain/NewDomain/v1/entity/ProblemReports.js with the following content:
function getRelatedEntityCollection(navProcessorData) {
  var HashMap = Java.type('java.util.HashMap');
  var ArrayList = Java.type('java.util.ArrayList');
  var WTArrayList = Java.type('wt.fc.collections.WTArrayList');
  var ChangeHelper2 = Java.type('wt.change2.ChangeHelper2');
  var targetName = navProcessorData.getTargetSetName();
  var map = new HashMap();
  var sourcePRs = new WTArrayList(navProcessorData.getSourceObjects());
  if("ReportedAgainst".equals(targetName)) {
    for(var i = 0; i < sourcePRs.size(); i++) {
      var sourcePR = sourcePRs.getPersistable(i);
      var reportedAgainstItems = ChangeHelper2.service.getChangeables(sourcePR, true);
      var list = new ArrayList();
      while(reportedAgainstItems.hasMoreElements()) {
        list.add(reportedAgainstItems.nextElement());
      }
      map.put(sourcePR, list);
    }
  }
  return map;
}
This creates a new domain called NewDomain with all the entities and relationships described in the example. To test the domain, use the following URLs:
•To see the EDM for NewDomain, use the URL:
https://<Windchill server>/Windchill/servlet/odata/NewDomain/$metadata
•To see the list of ProblemReports, use the URL:
https://<Windchill server>/Windchill/servlet/odata/NewDomain/ProblemReports
•To see the list of ProblemReport with ChangeableItems, use the URL:
https://<Windchill server>/Windchill/servlet/odata/NewDomain/ProblemReports?$expand=ReportedAgainst


Windchill REST Services Domain Capabilities > Examples for Customizing Domains > Extending Product Management Domain to Add A Soft Type
Extending Product Management Domain to Add A Soft Type
This example shows you how to extend the Product Management domain to add a soft type of an existing part. Consider a case where you want to create WTPart of soft type Capacitor which has its parent soft type as Electrical Part.
To extend the domain to add the soft type, create a custom configuration file Capacitors.json at:
<Windchill>/codebase/rest/custom/domain/ProdMgmt/<version>/entity
wcType property must have the same Internal Name as defined for the soft type in Type Management.

{
    "name": "Capacitor",
    "collectionName": "Capacitors",
    "wcType": "com.ptc.ptcnet.Capacitor",
    "description": "This part extends ElectricalParts entity.",
    "parent": {
        "name": "ElectricalParts"
    },
    "attributes": [
     	{
    	     "name":"Capacitance",
    	     "internalName":"Capacitance",
    	     "type":"String"
  	}
  ]
}

Sample request to create WTPart with soft type ‘Capacitor’:
{
  "@odata.type": "PTC.ProdMgmt.Capacitor",
  "Name":"TestWTPart_002",
  "Number":"TestWTPart_002",
  "AssemblyMode": {
  "Value": "component",
  "Display": "Component"
 },
  "Context@odata.bind": "Containers('OR:wt.pdmlink.PDMLinkProduct:48788507')"
}


Windchill REST Services Domain Capabilities > Examples for Customizing Domains > Extending Document Management Domain to Add a Soft Attribute
Extending Document Management Domain to Add a Soft Attribute
This example shows you how to extend the Document Management domain to add a soft attribute on a WTDocument soft type.
To extend the domain to add the soft attribute, create a custom configuration file DocumentsExt.json at <Windchill>/codebase/rest/custom/domain/DocMgmt/<version>/entity.
{
    "extends”: "Document",
    "description”: "This config extends Documents.json.”,
    "attributes”: [
    
	{
         "name":"ODATASTR1",
         "internalName":"ODATASTR1",
         "type":"String"
        }, 
        {      
	  "name":"ODATAINT1",
	  "internalName":"ODATAINT1",
	  "type":"Int16"
        },
        {    
         "name":"ODATAFPN1",
         "internalName":"ODATAFPN1",
         "type":"Double"
        }, 
        {      
         "name":"ODATABOOL1",
         "internalName":"ODATABOOL1",
         "type":"Boolean"
        },
        {      
         "name":"ODATADATE1",
         "internalName":"ODATADATE1",
         "type":"DateTimeOffset"
        }
     ]
  
}
To create a WTDocument with these extended soft attributes use the following request:
POST /Windchill/servlet/odata/<version>/DocMgmt/Documents HTTP/1.1
{
    "Name": "Test1",
    "Description": "Test1_Desc",
    "Title": "Test1_Title",
	
    "ODATASTR1": "This is String attribute",
    "ODATAINT1": 1,
    "ODATAFPN1": 1.555,
    "ODATABOOL1": true,
    "ODATADATE1": "2017-10-09T09:42:39Z",
    
    "Context@odata.bind": "Containers('OR:wt.pdmlink.PDMLinkProduct:48788507')"
	
}


