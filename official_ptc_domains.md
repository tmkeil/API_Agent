Windchill REST Services Domain Capabilities > PTC Domains
PTC Domains
This section explains the domains provided by PTC in Windchill REST Services.
When you install Windchill REST Services, some domains defined by PTC are also installed. These domains enable you to work with Windchill types in the REST architecture. You can also create new custom domains, or extend an existing domain to enable more entities.
A domain in Windchill REST Services represents a RESTful web service, which follows the OData standard. A domain describes its Entity Data Model (EDM) by defining the entity sets, relationships, entity types, and operations.


Windchill REST Services Domain Capabilities > PTC Domains > Overview
Overview
This section explains the domains provided by PTC in Windchill REST Services.
The following domains are provided as a part of Windchill REST Services:
•ProdMgmt—PTC Product Management domain exposes entities representing parts and BOMs, Windchill objects that are most frequently used while developing products. See the section PTC Product Management Domain, for more information on the domain.
•DocMgmt—PTC Document Management domain provides entities that enable users to manage Windchill documents (WTDocuments). See the section PTC Document Management Domain, for more information on the domain.
•DataAdmin—PTC Data Administration domain provides entities that enable users to manage data containers such as, organizations, products, libraries and projects in Windchill. See the section PTC Data Administration Domain, for more information on the domain.
•PrincipalMgmt—PTC Principal Management domain provides entities that work with Windchill groups and users. See the section PTC Principal Management Domain, for more information on the domain.
•PTC—PTC Common domain provides some utility entity types that are commonly used. See the section PTC Common Domain, for more information on the domain.
•NavCriteria—PTC Navigation Criteria domain provides entities that access the filters available in a part structure in Windchill. See the section PTC Navigation Criteria Domain, for more information on the domain.
•DynamicDocMgmt—PTC Dynamic Document Management domain provides entities that work with dynamic documents of Windchill. See the section PTC Dynamic Document Management Domain, for more information on the domain.
•PartListMgmt—PTC Parts List Management domain provides entities that work with parts list and parts list items of Windchill. See the section PTC Parts List Management Domain, for more information on the domain.
•ServiceInfoMgmt—PTC Service Information Management domain provides entities that work with objects and structures of Windchill Service Information Manager. See the section PTC Service Information Management Domain, for more information on the domain.
•Quality domains—The domains provide entities that work with Quality Management Services of Windchill. The Quality domains are available only if you have installed the relevant Quality products during Windchill installation. See the section PTC Quality Domains, for more information on the domain.
The following Quality domains are available:
◦PTC Quality Management System Domain
◦PTC Nonconformance Domain
◦PTC Customer Experience Management Domain
◦PTC Regulatory Master Domain
◦PTC CAPA Domain
◦PTC Audit Domain
•IE—PTC Info*Engine System domain provides entities that work with Info*Engine tasks of Windchill. See the section PTC Info*Engine System Domain, for more information on the domain.
•Factory—PTC Factory domain provides entities that work with the manufacturing data management capabilities of Windchill. The domain is available only if you have installed Windchill MPMLink. See the section PTC Factory Domain, for more information on the domain.
•MfgProcMgmt—PTC Manufacturing Process Management domain provides entities that work with the manufacturing process management capabilities (MPM) of Windchill. The domain is available only if you have installed Windchill MPMLink. See the section PTC Manufacturing Process Management Domain, for more information on the domain.
•ChangeMgmt—PTC Change Management domain provides entities that work with the change management capabilities of Windchill. See the section PTC Change Management Domain, for more information on the domain.
•ClfStructure—PTC Classification Structure domain provides access to the classification structure and classification nodes in Windchill. See the section PTC Classification Structure Domain, for more information on the domain.
•SavedSearch—PTC Saved Search domain provides access to saved searches in Windchill. See the section PTC Saved Search Domain, for more information on the domain.
•Visualization—PTC Visualization domain provides access to visualization services of Windchill. See the section PTC Visualization Domain, for more information on the domain.
•ProdPlatformMgmt—PTC Product Platform Management domain provides access to Options and Variants capabilities of Windchill. See the section PTC Product Platform Management Domain, for more information on the domain.
•CADDocumentMgmt—PTC CAD Document Management domain provides access to CAD data management capabilities of Windchill. See the section PTC CAD Document Management Domain, for more information on the domain.
•EffectivityMgmt—PTC Effectivity Management domain provides access to effectivity information of Windchill objects. See the section PTC Effectivity Management Domain, for more information on the domain.
•EventMgmt—PTC Event Management domain provides access to the webhook subscription capabilities of Windchill. See the section PTC Event Management Domain, for more information on the domain.
•SupplierMgmt—PTC Supplier Management domain provides access to the supplier management capabilities of Windchill. See the section PTC Supplier Management Domain, for more information on the domain.
•Workflow—PTC Workflow domain provides access to the workflow capabilities of Windchill. See the section PTC Workflow Domain, for more information on the domain.
•PDM— The domain is a read-only domain that combines all core Windchill domains into a single domain. The domain is accessed by OData clients, such as, Microsoft PowerBI and Excel, that cannot get data directly from core domains. If you want to build Windchill reports or dashboards using Microsoft PowerBI and Excel, you should use the PDM domain instead of using the core domains directly. See the section PDM Domain, for more information on the domain.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Product Management Domain
PTC Product Management Domain
The PTC Product Management domain provides access to the product management capabilities of Windchill. It provides OData entities that represent business objects, such as, Part and BOM. The following table shows the Windchill items that are enabled with OData entities in the Product Management domain. The Product Management domain references the PTC Document Management domain to provide navigations to reference and describe documents.
You can work with classified objects in the PTC Product Management domain only if Windchill PartsLink module is installed.
You can create classified objects. To create a classified object, using Windchill REST Services, follow the same initial steps as in Windchill user interface. Import the classification structure, create a classification binding attribute on the part object, and use the endpoints with relevant payload to create a classified part. See the Windchill Help Center for more details on classifying an object.
You can also update the classification attributes of an existing classified part. When classifying a part, if you specify the incorrect classification node name, or incorrect classification attribute name and value, relevant error messages are returned.
The supplier management entities such as, SupplierPart, ManufacturerPart, VendorPart, AXLEntry, and so on are available in PTC Product Management domain. These entities are available only if Supplier Management module is installed in Windchill. Classification is supported for manufacturer and vendor parts. See the section PTC Supplier Management Domain, for more information about PTC Supplier Management domain.
The following table lists the significant OData entities available in the Product Management domain. To see all the OData entities available in the Product Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Part
Part
ElectricalPart
The Part entity represents a part version. In Windchill, use the WTPart and WTPartMaster classes to work with part versions.
ElectricalPart is derived from Part and represents the soft type that is available in Windchill.
See the section Navigation Properties Available for Part Entity, for information on some of the navigation properties available with Part entity.
Bill of material
BOM
PartUse
UsageOccurrence
The BOM entity represents the part structure expanded to some levels.
PartUse is an OData entity that represents the association between parent and child parts. It has attributes such as, quantity, unit, line number, and so on. These attributes of entity models are also available in the WTPartUsageLink class.
The UsageOccurrence entity represents the reference designator when a component is used multiple times in a BOM.
Part that resides in a Windchill folder
PartContent
This entity is derived from FolderContent entity that is available in the DataAdmin domain. The entity represents a part residing in a folder.
Supplier part
SupplierPart
Supplier part is a subtype of part.
You can perform only read operation on this entity.
Manufacturer part
ManufacturerPart
Manufacturer part is a subtype of supplier part. It is produced by a manufacturer other than the Original Equipment Manufacturer (OEM).
The AXLEntry entity is used to associate the ManufacturerPart entity with the Part entity.
Vendor part
VendorPart
Vendor part is a subtype of supplier part. It is a part that is supplied by the vendor.
The AXLEntry entity is used to associate the VendorPart entity with the Part entity.
AXLEntry (AML/AVL)
AXLEntry
AXLEntry entity represent the association between SupplierPart, that is, ManufacturerPart and VendorPart and the Part entity. An OEM part can be associated with several manufacturer parts or vendor parts.
The AXLEntry entity is available as navigation property on the Part entity, which retrieves the manufacturer and vendor parts that are associated with the part.
Navigation Properties Available for Part Entity
The Part entity contains navigation properties. See the descriptions that follow for some navigation properties:
•AssignedOptionSet—Retrieves the option set assigned to the part. You can also expand the navigation property to get detailed information about the option set. See the section PTC Product Platform Management Domain, for more information about OptionSet entity.
* 
The navigation property is available only if the option Configurable Module Support is set to Yes in Utilities > Preference Management > Options and Variants.
•AXLEntries—Creates, updates, and deletes associations between Original Equipment Manufacturer (OEM) and the following:
◦Manufacture parts (AML)
◦Vendor parts (AVL)
◦Both manufacture and vendor parts (AXL)
For example, to create association between AXL and OEM parts, use the following POST URL and specify the following payload:
POST https://windchill.ptc.com/Windchill/servlet/odata/ProdMgmt/Parts('OEM PART ID')/AXLEntries
{
  "SourcingContext@odata.bind":"SourcingContexts('OR:com.ptc.windchill.suma.axl.AXLContext:232901')",
  "VendorPartSourcingStatus":{"Value":"approved","Display":"Approved"},
  "ManufacturerPartSourcingStatus":{"Value":"preferred","Display":"Preferred"},
  "ManufacturerPartReference@odata.bind":"ManufacturerParts('OR:com.ptc.windchill.suma.part.ManufacturerPart:280604')",
  "VendorPartReference@odata.bind":"VendorParts('OR:com.ptc.windchill.suma.part.VendorPart:280463')"
}
The sourcing context and part reference parameters are mandatory.
Type of AXL Entry
Sourcing Context
Part Reference
Manufacture parts (AML)
Required
ManufacturerPartReference
Vendor parts (AVL)
Required
VendorPartReference
Both manufacture and vendor parts (AXL)
Required
•ManufacturerPartReference
•VendorPartReference
Sourcing status is an optional parameter. The following rules apply to sourcing status:
◦The value specified for sourcing status in the request payload gets precedence over the sourcing rules set in Windchill.
◦If the value for sourcing status is not specified in the request payload, and if the supplier administrator has set sourcing rules in Windchill, then the value specified for sourcing status in Windchill is used.
◦If the value for sourcing status is not set in the request payload and no sourcing rules are set in Windchill, then the default status Do Not Use is set for the AXL entry.
You can update the following information using the PATCH request:
◦Sourcing status for manufacture and vendor parts.
◦Add new vendor part reference in AXL and AML parts.
•PartAssociations—Retrieves the association links between a part and CAD document. You can also retrieve the related CAD document using the navigation property RelatedCADDoc.
/ProdMgmt/Parts('OR:wt.part.WTPart:108618')?$expand=PartAssociations($expand=RelatedCADDoc)
•Effectivities—Retrieves the effectivities associated with the part.
Navigation URLs for AssignedOptionSet
You can use the following URLs to retrieve information about assigned option set that is associated with product or library containers.
•To get all the parts with their assigned option sets:
/ProdMgmt/Parts(<oid>)/AssignedOptionSet
•To get all the parts with their assigned option sets with expanded navigation:
/ProdMgmt/Parts?$expand=AssignedOptionSet
•To get a specific part along with its assigned option set:
/ProdMgmt/Parts(<oid>)?$expand=AssignedOptionSet


Windchill REST Services Domain Capabilities > PTC Domains > PTC Product Management Domain > Actions Available in the PTC Product Management Domain
Actions Available in the PTC Product Management Domain
The following actions are available in the PTC Product Management domain:
GetBOM
The action GetBOM returns the bill of materials (BOM) for the product structure. The action is bound to the entity NavigationCriteria, that is, to the filter saved in Windchill.
When you call the GetBOM action, in the request body of the URL, you can specify the ID of the NavigationCriteria. This is the ID of the saved filter you want to use as the filter criteria. If you do not specify the ID of the filter in the request body, then the default filter is used to work with the product structure. Alternatively, you can specify the navigation criteria in the request payload.
This action will be deprecated in a future release of Windchill REST Services. Use the action GetPartStructure instead.
GetBOMWithInlineNavCriteria
The action GetBOMWithInlineNavCriteria returns the bill of materials (BOM) for the product structure. Pass the navigation criteria as the input parameter. The action is bound to the entity NavigationCriteria, that is, to the filter saved in Windchill. You can pass partial representation of the navigation criteria.
If the navigation criteria contains the property ApplyToTopLevelObject, which is set as True, and no qualifying version is found for the top level object, a relevant error message is returned.
For example, the following partial navigation criteria returns the Bill of Material for Manufacturing view that includes working copies of parts.
POST /ProdMgmt/Parts(<oid>)/PTC.ProdMgmt.GetBOMWithInlineNavCriteria
{
  "NavigationCriteria": {
      "ApplyToTopLevelObject": true,
      "ApplicableType": "wt.part.WTPart",
      "ConfigSpecs": [
        {
          "@odata.type": "#PTC.NavCriteria.WTPartStandardConfigSpec",
          "WorkingIncluded": true,
          "View": "Manufacturing"
        }
      ]
  }
}
This action will be deprecated in a future release of Windchill REST Services. Use the action GetPartStructure instead.
GetPartStructure
The action GetPartStructure returns the bill of materials (BOM) for a product structure along with path details for occurrences. The action is bound to the entity NavigationCriteria, that is, to the filter saved in Windchill.
When you call the GetPartStructure action, in the request body of the URL, you can specify the ID of the NavigationCriteria. This is the ID of the saved filter you want to use as the filter criteria. If you do not specify the ID of the filter in the request body, then the default filter is used to work with the product structure. Alternatively, you can specify the navigation criteria in the request payload.
As compared to the GetBOM and GetBOMWithInlineNavCriteria actions, when you call the GetPartStructure action, the following additional URLs are returned:
•PathId is the occurrence path of the component part in the BOM structure. The complete path from the root of the BOM structure is returned. This URL can be used in path filters to filter on the specific component.
•PVTreeId is the occurrence path of the component part in the viewable file. The complete path from the root of the BOM structure is returned. This URL can be used to work with Visualization tree. For example, in an application you consume this URL and highlight the component in the Visualization tree.
•PVParentTreeId is the occurrence path to the parent of the component part in the viewable file. The complete path from the root of the BOM structure is returned.
When you call the GetPartStructure action along with expand on occurrences, the component along with its details is returned as many times as the component is available in the BOM structure.
For example, consider a part A1 which has the following components:
•Component C1—Quantity 2 with occurrences R1 and R2
•Component C2—Quantity 1 with no occurrences
When you use the GetPartStructure action with occurrences to get the BOM, the following response is returned:
{
  "PartName": "A1"
  "PartUseId": null,
  "Part": {
      "ID": "<oid>",
      "Name": "A1",
      ...
  },
  "PartUse": null,
  "Ocurrences": [],
  "Components": [
      {
        "PartName": "C1"
        "PartUseId": "<linkoid>",
        "PartId": "<pathidofcomponent>",
        "PVTreeId": "<treeidfromviz>",
        "PVParentTreeId": "<parenttreeidfromviz>",
        "Part": {
            "ID": "<oid>",
            "Name": "C1",
            ...
        },
        "PartUse": {
            "ID": "<linkoid>",
            "Qty": 1,
            ...
        },
        "Ocurrence": {
              "ID": "<occoid>",
              "ReferenceDesignator": "R1"
              ...
        },
        "Components": []
      },
      {
        "PartName": "C1"
        "PartUseId": "<linkoid>",
        "PartId": "<pathidofcomponent>",
        "PVTreeId": "<treeidfromviz>",
        "PVParentTreeId": "<parenttreeidfromviz>",
        "Part": {
            "ID": "<oid>",
            "Name": "C1",
            ...
        },
        "PartUse": {
            "ID": "<linkoid>",
            "Qty": 1,
            ...
        },
        "Ocurrence": {
              "ID": "<occoid>",
              "ReferenceDesignator": "R2"
              ...
        },
        "Components": []
      },
      {
        "PartName": "C2"
        "PartUseId": <linkoid>",
        "PartId": "<pathidofcomponent>",
        "PVTreeId": "<treeidfromviz>",
        "PVParentTreeId": "<parenttreeidfromviz>",
        "Part": {
            "ID": "<oid>",
            "Name": "C2",
            ...
        },
        "PartUse": {
            "ID": "<linkoid>",
            "Qty": 1,
            ...
        },
        "Ocurrences": [],
        "Components": []
      }
  ]
}
GetPartsList
The action GetPartsList returns a consolidated flat list of components for the specified part structure. The action returns:
•Number of occurrences, that is, quantity of the component in the part list. Each component is only listed once with a consolidated total quantity.
•Unit of the component
To get more details on the components of a part structure, specify the value application/json;odata.metadata=full in the Accept header of the HTTP request. The odata.metadata parameter controls how much information is included in the response. When you specify the value as full, the response includes all the information.
When you specify the OID of the part and Accept header value application/json;odata.metadata=full in the URL request, the action GetPartsList() returns the following information:
•OData type for the part component
•Quantity of the part component in the specified part structure
•Unit of the component
•Navigation URL to the part component
You can expand the Part and PartUses navigation properties for more details of the components.
UpdateCommonProperties
The action UpdateCommonProperties edits the common properties of parts. The action is available only if you set the property hasCommonProperties to true in the Parts.json file.
The action must not be called on objects that are checked out.
Common part attributes, Name, Number, EndItem, DefaultUnit, DefaultTraceCode, ConfigurableModule, GatheringPart, Organization, and PhantomManufacturingPart can be edited.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Product Management Domain > Function Available in the PTC Product Management Domain
Function Available in the PTC Product Management Domain
The following function is available in the PTC Product Management domain:
GetAssignedExpression()
The function GetAssignedExpression() returns the assigned expressions for Part, PartUse, and UsageOccurrence entities. The function is bound to these entities. You can specify a single entity as the input parameter. Basic and advanced types of expressions are supported.
The information related to assigned expressions is retrieved using the complex type, AssignedExpression, which is defined in the PTC Product Platform Management domain.
To retrieve the assigned expressions for multiple objects, use the GetAssignedExpressions action defined in the PTC Product Platform Management domain. See the section Action Available in the PTC Product Platform Management Domain, for more information.
Both dependent and independent expression modes are supported.
GetAllVariantSpecifications()
The function GetAllVariantSpecifications() retrieves all the variant specifications related to the configurable module. It returns all the variant specifications that are created from any iteration or revision of the part.
* 
This function is available only if the option Configurable Module Support is set to Yes in Utilities > Preference Management > Options and Variants in Windchill.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Document Management Domain
PTC Document Management Domain
The Document Management domain provides access to the document management capabilities of Windchill. It enables you to create documents. You can also upload and download content from documents.
The following table lists the significant OData entities available in the Document Management domain. To see all the OData entities available in the Document Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Business document
Document
The Document entity represents a document version. In Windchill, use the WTDocument and WTDocumentMaster classes to work with document versions.
Content information
ContentInfo
The ContentInfo entity contains content information which is used in Stage 3 for uploading content to the document.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Document Management Domain > Action Available in the PTC Document Management Domain
Action Available in the PTC Document Management Domain
The following action is available in the PTC Document Management domain:
UpdateCommonProperties
The action UpdateCommonProperties edits the common properties of documents. The action is available only if you set the property hasCommonProperties to true in the Documents.json file.
The action must not be called on objects that are checked out.
In this release, you can only edit the attributes Name, Number, and Organization.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Data Administration Domain
PTC Data Administration Domain
The PTC Data Administration domain provides access to data administration capabilities of Windchill. The domain includes entities that represent Windchill containers such as, site, organization, product, libraries, project containers, and so on. It also includes entities that represent the folder hierarchy in these containers. This domain contains an entity set called Containers that enables clients to read the containers available in their Windchill system.
* 
Containers entity set is read-only, and does not support update, delete and create operations.
The following table lists the significant OData entities available in the Data Administration domain. To see all the OData entities available in the Data Administration domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Windchill container
Container
A Windchill container. This entity exposes only those attributes that are common across all types of containers.
Site container
Site
A site container which is derived from the Container entity.
Organization container
OrganizationContainer
An organization container, which is derived from the Container entity.
Product container
ProductContainer
A product container, which is derived from the Container entity.
This entity provides the following navigation properties:
•OptionPool —Retrieves the options group and options available in the option pool for the specified container. See the section PTC Product Platform Management Domain, for more information about OptionPoolItem entity.
•AssignedOptionSet—Retrieves the option set assigned to the specified container. See the section PTC Product Platform Management Domain, for more information about OptionSet entity.
•OptionPoolAliases—Retrieves the expression aliases assigned to the specified container.
* 
These navigation properties are available only if the option Configurable Module Support is set to Yes in Utilities > Preference Management > Options and Variants.
Library container
LibraryContainer
A library container
This entity provides the following navigation properties:
•OptionPool —Retrieves the options group and options available in the option pool for the specified container. See the section PTC Product Platform Management Domain, for more information about OptionPoolItem entity.
•AssignedOptionSet—Retrieves the option set assigned to the specified container. See the section PTC Product Platform Management Domain, for more information about OptionSet entity.
•OptionPoolAliases—Retrieves the expression aliases assigned to the specified container.
* 
These navigation properties are available only if the option Configurable Module Support is set to Yes in Utilities > Preference Management > Options and Variants.
Project container
ProjectContainer
A project container
Folders and subfolders
Folder
A folder, which is derived from the Container entity. You can use folders to organize objects.
You can create, update, and delete folders and subfolders.
Generic item that resides in the Windchill folder
FolderContent
The FolderContent entity represents the generic view of an item that resides in a folder.
Other domain entities can derive from this entity to create more specific views. For example, in the Product Management domain, the PartContent entities derive from FolderContent.
Navigation URLs for OptionPool, AssignedOptionSet, and OptionPoolAliases
You can use the following URLs to retrieve option pool items (option groups and options), an assigned option set, and expression aliases. These navigation properties are available for product and library containers.
•OptionPool Navigation Property:
◦To get the option pool items for a specific container:
▪/DataAdmin/Containers/PTC.DataAdmin.ProductContainer(<oid>)/OptionPool
▪/DataAdmin/Containers/PTC.DataAdmin.LibraryContainer(<oid>)/OptionPool
◦To get the containers along with the option pool items:
▪/DataAdmin/Containers/PTC.DataAdmin.ProductContainer?$expand=OptionPool
▪/DataAdmin/Containers/PTC.DataAdmin.LibraryContainer?$expand=OptionPool
◦To get the option groups from the option pool for a specific container typecast to the OptionGroup entity:
▪/DataAdmin/Containers/PTC.DataAdmin.ProductContainer(<oid>)/OptionPool/PTC.ProdPlatformMgmt.OptionGroup
▪/DataAdmin/Containers/PTC.DataAdmin.LibraryContainer(<oid>)/OptionPool/PTC.ProdPlatformMgmt.OptionGroup
◦To get the top-level options from the option pool for a specific container typecast to the Option entity:
▪/DataAdmin/Containers/PTC.DataAdmin.ProductContainer(<oid>)/OptionPool/PTC.ProdPlatformMgmt.Option
▪/DataAdmin/Containers/PTC.DataAdmin.LibraryContainer(<oid>)/OptionPool/PTC.ProdPlatformMgmt.Option
•AssignedOptionSet Navigation Property:
◦To get the assigned option set with details:
▪/DataAdmin/Containers/PTC.DataAdmin.ProductContainer?$expand=AssignedOptionSet
▪/DataAdmin/Containers/PTC.DataAdmin.LibraryContainer?$expand=AssignedOptionSet
◦To get the assigned option set with details for a specific container:
▪/DataAdmin/Containers/PTC.DataAdmin.ProductContainer(<oid>)?$expand=AssignedOptionSet
▪/DataAdmin/Containers/PTC.DataAdmin.LibraryContainer(<oid>)?$expand=AssignedOptionSet
•OptionPoolAliases Navigation Property:
◦To get the expression aliases with details:
▪/DataAdmin/Containers/PTC.DataAdmin.ProductContainer?$expand=OptionPoolAliases
▪/DataAdmin/Containers/PTC.DataAdmin.LibraryContainer?$expand=OptionPoolAliases
◦To get the expression aliases with details for a specific container:
▪/DataAdmin/Containers/PTC.DataAdmin.ProductContainer(<oid>)?$expand=OptionPoolAliases
▪/DataAdmin/Containers/PTC.DataAdmin.LibraryContainer(<oid>)?$expand=OptionPoolAliases


Windchill REST Services Domain Capabilities > PTC Domains > PTC Principal Management Domain
PTC Principal Management Domain
The Principal Management domain provides read access to the information related to principals in Windchill. The Windchill principals can be users, groups, license groups and so on.
The following table lists the significant OData entities available in the Principal Management domain. To see all the OData entities available in the Principal Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Windchill principal
Principal
The Principal entity represents the generic view of a Windchill principal.
Windchill user
User
The User entity represents a principal who is the user. In Windchill, use the WTUser class to work with users.
Windchill group
Group
The Group entity represents a principal who is the group. In Windchill, use the WTGroup class to work with groups.
Windchill organization principal
Organization
The Organization entity represents a Windchill group that is an organization principal. In Windchill, use the WTOrganization class to work with organization principals.
License group
LicenseGroup
The LicenseGroup entity represents a Windchill license groups.
Windchill license groups are available at the site level to help you manage your license compliances.
You must add the user to the appropriate license group depending on the licenses allocated to them.
This entity provides navigation property that lists all the license groups for a user. You can also expand the navigation property.
License groups are access controlled.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Common Domain
PTC Common Domain
PTC Common (PTC) domain provides access to entities that are common to multiple domains. It is recommended to store common entities in this domain. The domain also provides complex types and functions that are used in other domains.
The following table lists the significant OData entities available in the PTC Common domain. To see all the OData entities available in the PTC Common domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Content file associated to a business document
ContentItem
The ContentItem entity provides a generic view of the content that is associated to a business document. More specialized entities are derived from ContentItem are ExternalStoredData, ApplicationData, and URLData.
You can use PATCH requests to update the Comments and Description properties. In the body of the PATCH request, specify the values for the attributes.
Content stored in an external location
ExternalStoredData
The ExternalStoredData entity provides a specialized view of an externally stored ContentItem, which is stored in a document
A URL that is stored in a business document
URLData
The URLData entity provides a specialized view of the URL ContentItem that is stored in a document
Content stored in Windchill application
ApplicationData
The ApplicationData entity provides a specialized view of the content stored by the Windchill application.
Windchill Objects
WindchillEntity
Some of the Windchill objects types are not available in Windchill REST Services. All the object types that are not available in Windchill REST Services are represented as WindchillEntity.
WindchillEntity returns only the ID, created by, and last modified by, attributes for these objects.
If you want to return Windchill objects that are not available in Windchill REST Services, use this entity to represent such objects.
The object types, which are available in Windchill REST Services, are automatically mapped to the relevant entity type.
In addition to the entities, this domain also contains the following complex types which represent:
•QuantityOfMeasureType—Real number with unit data type in Windchill.
•Hyperlink—URL data type in Windchill.
•Icon—Icon in Windchill.
•EnumType—Attributes that are enumerated types in Windchill or attributes that have type constraints defined.
•ClassificationInfo—Classification binding attribute.
•ClassificationAttribute—Classifications attributes.
•EntityMetaInfo—Windchill metadata information for entity types.
•PropertyMetaInfo—Windchill metadata information for properties.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Common Domain > Functions Available in the PTC Common Domain
Functions Available in the PTC Common Domain
The following functions are available in the PTC Common domain:
GetEnumTypeConstraint()
The function GetEnumTypeConstraint() is used to query the valid values for a property, which are represented as EnumType. These values are used for implementing validations on client side.
GetAllStates()
The function GetAllStates() returns a list of life cycle states, which are available and can be selected in Windchill. The life cycle states that cannot be selected in Windchill are not returned. The life cycle states are retrieved from the StateRb.rbinfo file.
GetAllStates() is an unbound function, which is available in all the domains which import the PTC Common domain.
If the URL used to execute the function is not formed correctly, the function throws the URL malformed exception.
GetWindchillMetaInfo()
The GetWindchillMetaInfo() function returns the Windchill metadata for OData entity types and properties that are available in the domain from which the function is called. The function is available in the all domains that import the PTC Common domain.
The function uses the complex types EntityMetaInfo and PropertyMetaInfo to retrieve the Windchill metadata.
Note the following points while retrieving the Windchill metadata using the GetWindchillMetaInfo() function:
•For entity types that are backed by Windchill types, the display and internal names of the entity are retrieved.
•For entity types that are not backed by Windchill types, the display and internal names of the entity are retrieved as null.
•For properties that are available on the OData entity type, but are not available in Windchill, the value of display name is retrieved as null.
For example, consider the VersionID property which is available on many OData entity types. For this property, there is no equivalent property in Windchill. In this case, the display name is always retrieved as null.
•The function returns internal names and localized display names for Windchill types and properties depending on the language that you have set.
For example, if you call the function from the PTC Product Management domain, the following response is returned.
Request URL
GET ProdMgmt/GetWindchillMetaInfo()
The response is:
[
  {
    "EntityType": "PTC.ProdMgmt.Part",
    "BaseType": "PTC.WindchillEntity",
    "HasWindchillType": true,
    "DisplayName": "Part",
    "InternalName": "wt.part.WTPart",
    "PropertyInfo": [
      {
         "PropertyName": "DefaultUnit",
         "DisplayName": "Default Unit",
         "InternalName": "defaultUnit"
       },
       {
         "PropertyName": "EndItem",
         "DisplayName": "End Item",
         "InternalName": "endItem"
       },
         ...
       ]
  },
  {
         "EntityType": "PTC.ProdMgmt.PartUse",
         "BaseType": "PTC.WindchillEntity",
         "HasWindchillType": true,
         "DisplayName": "Part Usage Link",
         "InternalName": "wt.part.WTPartUsageLink",
         "PropertyInfo": [
       {
         "PropertyName": "QuantityUnit",
         "DisplayName": "Quantity Unit",
         "InternalName": "quantityUnit"
       },
       {
         "PropertyName": "LineNumber",
         "DisplayName": "Line Number",
         "InternalName": "lineNumber"
       },
         ...
       ]
    },
    ...
]
To get the Windchill metadata for a specific entity in the domain from which the function is called, specify the following URL:
GET <Domain_Name>/GetWindchillMetaInfo(EntityName='<name_of_the_entity>')
For example, to get information about the Part entity, use the following URL:
GET ProdMgmt/GetWindchillMetaInfo(EntityName='PTC.ProdMgmt.Part')


Windchill REST Services Domain Capabilities > PTC Domains > PTC Navigation Criteria Domain
PTC Navigation Criteria Domain
The PTC Navigation Criteria domain provides access to the filters available in a part structure in Windchill. The filters are divided into two categories, configuration specifications that display a complete bill of material, and specialized filters that show a subset of parts relevant to a design task. The following table shows the Windchill items that are enabled with OData entities in the PTC navigation Criteria domain.
The following table lists the significant OData entities available in the PTC Navigation Criteria domain. To see all the OData entities available in the PTC Navigation Criteria domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Saved filters or navigation criteria in Windchill
NavigationCriteria
The NavigationCriteria entity represents filters, which are created and saved in Windchill. The criteria defined in the filter is used when you work with product structures.
To define the filter criteria, specify and save values in the filter. The values specified in the filter are access-controlled as is NavigationCriteria.
The entity includes complex types that represent different types of configuration specifications, spatial, option, and attribute filters.
In addition to the entity, this domain also contains the following complex types:
•ConfigSpec—Collection of configuration specifications in a part and CAD document structure. A configuration specification filters the part or CAD document structure to show complete product configurations with a part and document version displayed for each structure node.
* 
If ConfigSpec is not specified for CAD documents, then no configuration specification is used, and all the children are unresolved. The document masters are returned for the CAD documents.
The configuration specification filters are represented as the following complex types:
◦Date Effectivity configuration specification—View the configuration of a product based on a specified date, or date and time effectivity. This filter is available only for parts. Use the WTPartEffectivityDateConfigSpec complex type to work with parts.
◦As Matured configuration specification—View the parts that are in their most mature state with reference to the specified date. This filter is available only for parts. Use the WTPartAsMaturedConfigSpec complex type to work with parts.
◦Unit Effectivity configuration specification—View the configuration of a product based upon the serial number or lot number. This filter is available only for parts. Use the WTPartEffectivityUnitConfigSpec complex type to work with parts.
◦Baseline configuration specification—Get the design from a specific event in time, that is, from a previously created baseline. Depending on the type of Windchill object use the following complex types:
▪WTPartBaselineConfigSpec—To work with parts.
▪EPMDocBaselineConfigSpec—To work with CAD documents.
◦Promotion Request configuration specification—Get the data related to the specified promotion request. Depending on the type of Windchill object use the following complex types:
▪WTPartPromotionNoticeConfigSpec—To work with parts.
▪EPMDocPromotionNoticeConfigSpec—To work with CAD documents.
◦Latest configuration specification—Find the latest designs, that is, the most recently created versions of a selected view and life cycle state. Depending on the type of Windchill object use the following complex types:
▪WTPartStandardConfigSpec—To work with parts.
▪EPMDocStandardConfigSpec—To work with CAD documents.
* 
If you specify the navigation criteria in the request body with only ApplicableType parameter set, the URL returns unresolved dependents for the CAD structure. However, if additionally, the UseDefaultForUnresolved parameter is also set to true in the request body, then Latest configuration specification is applied to the structure.
◦As Stored configuration specification—Get the most recent configuration stored for a CAD document. This filter is available only for CAD documents. Use the EPMDocAsStoredConfigSpec complex type to work with CAD documents. If this filter is used with other Windchill object types, an error message is returned.
•Filter—Collection of specialized filters in a part structure. The specialized part structure filters reduce the complexity of the part structure by showing only those parts that are relevant to a design task or optional product configuration. The specialized filters are represented as the following complex types:
◦AttributeFilter—Attribute filters use part and usage link attribute information to determine what parts to include or exclude in the display of part structure.
◦OptionFilter—Option filter is used to include or exclude parts in a part structure based on expressions assigned to the parts.
◦SpatialFilter—Spatial filters use volumetric information to determine what components to display or hide in a part or CAD document structure. It is represented by following complex types:
▪ProximitySpatialFilter
▪SphereSpatialFilter
▪BoxSpatialFilter
◦PathFilter—Filters the display of large assemblies so that only the subassemblies that you are currently working on are displayed.
◦OccurrencePathFilter—Filters the display based on basic or advanced expressions assigned to an occurrence.
◦UsagePathFilter—Filters the display based on expressions assigned to usage links and parts.
If you have a spherical spatial filter with bounding box set as partial, the navigation criteria for this is represented as shown below in Windchill REST Services. Use the following URL to retrieve the navigation criteria:
GET /Windchill/servlet/odata/NavCriteria/NavigationCriterias?$filter=Name eq 'Sphere_filter001'
The response is as follows:
"value": [
        {
            "ID": "OR:wt.filter.NavigationCriteria:261602",
            "Name": "Sphere_filter001",
            "ApplyToTopLevelObject": true,
            "UseDefaultForUnresolved": false,
            "SharedToAll": false,
            "ApplicableType": "wt.part.WTPart",
            "Centricity": false,
            "HideUnresolvedDependents": false,
            "Filters": [
                {
                    "@odata.type": "#PTC.NavCriteria.SphereSpatialFilter",
                    "SpatialMethod": {
                        "Value": "PARTIALLY_IN",
                        "Display": "Partially in"
                    },
                    "XCenter": -0.5334005391706416,
                    "YCenter": 0.0503675,
                    "ZCenter": 0.00136,
                    "Radius": 0.40648001432418823
                    "Unit": "m"
                }
            ],
            "ConfigSpecs": [
                {
                    "@odata.type": "#PTC.NavCriteria.WTPartStandardConfigSpec",
                    "WorkingIncluded": true,
                    "View": "Design",
                    "LifeCycleState": null,
                    "Variation1": null,
                    "Variation2": null
                }
            ],
            "CreatedOn": "2018-10-01T11:38:16Z",
            "LastModified": "2018-10-01T11:38:16Z"
        }
    ]
}


Windchill REST Services Domain Capabilities > PTC Domains > PTC Dynamic Document Management Domain
PTC Dynamic Document Management Domain
PTC Dynamic Document Management domain provides access to the dynamic document capabilities of Windchill. Dynamic documents are compound documents that are encoded in a markup language such as XML. Dynamic documents include files that are authored in Arbortext Editor and can also contain other document-related files, such as graphics. Dynamic documents can contain parent and child documents, where the child documents can be transcluded into the parent. Dynamic documents can also reference other dynamic documents. With this domain, you can manage and share dynamic documents in Windchill.
* 
If you add <image> elements to a dynamic document, which is in DITA format, and check in the document, links to the graphics are automatically created in Windchill. If you delete the <image> elements, the links are retained.
In XML content, dynamic documents are identified by the CADName attribute of the document. OData endpoint can find dynamic documents with either the object identifier Oid or the CADName attribute.
The following table lists the significant OData entities available in the PTC Dynamic Document Management domain. To see all the OData entities available in the PTC Dynamic Document Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Dynamic document
DynamicDocuments
The DynamicDocuments entity represents a compound XML document that can be used to generate formatted output.
In Windchill, dynamic documents are associated with EPMMemberLinks and EPMReferenceLinks classes.
The entity provides two navigation properties to support Service Information Manager Translation.
•Navigation from a dynamic document to the associated translated dynamic documents is possible.
•For a Creo Illustrate 3D illustration file (.c3di), navigation is provided from the document to the associated XLIFF dynamic document. XLIFF contains translatable strings of the illustration.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Parts List Management Domain
PTC Parts List Management Domain
PTC Parts List Management (PartListMgmt) domain provides access to parts lists and parts list items, which are available in Windchill Service Parts module. Windchill Service Parts transforms eBOMs and mBOMs into service BOMs (sBOMs). A service BOM is a list of components in any order. Transforming the service BOM and the service BOM graphical representation into a parts list enables you to order the components in a meaningful way. Use the PTC Parts List Management domain to retrieve part lists, part list items, illustrations, substitute, and supplementary parts.
The following table lists the significant OData entities available in the PTC Parts List Management domain. To see all the OData entities available in the PTC Parts List Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Parts list
PartList
A parts list is an ordered list of parts, which also includes metadata, such as, information about the conditions under which the parts are used.
Part list item
PartListItem
A part item list is a reference to a part in the parts list.
Illustrations
Illustration
An illustration is a graphic document that is linked to a parts list.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Service Information Management Domain
PTC Service Information Management Domain
PTC Service Information Management (ServiceInfoMgmt) domain provides access to the objects and structures of Windchill Service Information Manager.
Use Windchill Service Information Manager to organize service content, specify the content applicability rules and create publications. You can also automatically deliver the service information for every product configuration throughout the product lifecycle. PTC Service Information Management domain is available only if you install Windchill Service Information Manager.
* 
You should not call entities of other domains which are imported in PTC Service Information Management domain. For example, PTC Service Information Management domain imports PTC PartList Management domain. It is recommended not to call PartListMgmt entities such as, PartList, PartListItem, Supplement, and so on from the ServiceInfoMgmt domain.
The following table lists the significant OData entities available in the PTC Service Information Management domain. To see all the OData entities available in the PTC Service Information Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Information structure
InformationStructure
A hierarchical structure that organizes information related to a product.
Information group
InformationGroup
In an information structure, subgroups of information are referred to as information groups. These groups organize content.
Publication structure
PublicationStructure
Organizes service information associated with an information structure. Or, organizes service information that is stored independently in Windchill into a hierarchical structure that can be published.
Publication section
PublicationSection
A section of content in the publication structure.
Textual information element
TextualInformationElement
A textual content object in an information structure or publication structure.
A textual information element is related to a dynamic document in the Dynamic Document Management domain. The dynamic document must contain XML data.
Graphical information element
GraphicalInformationElement
A graphical content object in an information structure or publication structure.
A graphical information element is related to a dynamic document in the Dynamic Document Management domain. The dynamic document must contain graphical content.
Document information element
DocumentInformationElement
A document content object in an information structure or publication structure.
A document information element is related to a document in the Document Management domain. The document can be of any format, for example, Microsoft Word, PDF, and so on.
Part List information element
PartListInformationElement
A content object of type parts list in an information structure or publication structure.
A parts list information element is related to a parts list in the Parts List Management domain.
Generic information element
GenericInformationElement
A node in an information structure or publication structure, which points to other information elements.
The applicability rules determine which information elements are included while publishing.
Table of Contents
TableOfContent
A content object of type table of contents.
Table of contents object in a publication structure indicates that the published output should contain a table of contents at the specified location in the document.
Indexes
Indexes
A content object of type index.
Index object in publication structure indicates that the published output should contain an index at the specified location in the document.
Transversal in document
SIMDocument
Supports transversal to the information element for a document.
Transversal in dynamic document
SIMDynamicDocument
Supports transversal to the information element for a dynamic document.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Service Information Management Domain > Action Available in the PTC Service Information Management Domain
Action Available in the PTC Service Information Management Domain
The following action is available in the PTC Service Information Management domain:
GetStructure()
The action GetStructure() expands a publication and information structure, and retrieves its contents. The action is bound to the entity NavigationCriteria, that is, to the filter saved in Windchill. The action is available for InformationStructure, InformationGroup, PublicationStructure, PublicationSection, and GenericInformationElement entities.
When you call the GetStructure() action, in the request body of the URL, you must specify the ID of the NavigationCriteria. This is the ID of the saved filter you want to use as the filter criteria. If you do not specify the ID of the filter in the request body, then the default filter is used to work with the structure.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Quality Domains
PTC Quality Domains
This section explains the Quality domains provided by PTC. These domains are available only if you have installed the relevant Quality products during Windchill installation.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Quality Domains > PTC Quality Management System Domain
PTC Quality Management System Domain
PTC Quality Management System (QMS) domain provides access to the people and places administration capability of Windchill. The domain enables you to create and manage people and places for a quality context.
The following table lists the significant OData entities available in the PTC Quality domain. To see all the OData entities available in the PTC Quality domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
* 
The GetDriverProperties(), GetPregeneratedValue(), and the two GetConstraints() functions are not supported, though they are available in the metadata of the domain.
Items
OData Entities
Description
Quality
Quality
The Quality entity represents a Quality container.
Person or place
PersonPlace
Place
BusinessUnit
RegulatoryAgency
Manufacturer
Supplier
Distributor
FacilityHospital
Person
MedicalProfessional
Patient
The PersonPlace and all the subentities represent a person or place which is related to a Quality entity.
Address
Address
The Address entity represents the addresses associated with a person or place.
Email
Email
The Email entity represents the email addresses associated with a person or place.
Phone number
PhoneNumber
The PhoneNumber entity represents the phone numbers associated with a person or place.
Cross reference
Xreference
The Xreference entity represents cross referenced items, such as, ERP system IDs or medical record numbers, that are associated with a person or place.
Relationships
Relationship
The Relationship entity represents the relationships between people or places.
Subject
Subject
Document
PartInstance
Part
The Subject entity represents the subject of a Quality entity. Subject is the object on which you want to perform an action. The Subject entity can be extended to include any changeable Windchill object such as, document, part and part instance.
Quality contact
QualityContact
PatientContact
RegulatoryAgencyContact
BusinessUnitOrOfficeContact
MedicalProfessionalContact
SupplierContact
ManufacturerContact
FacilityContact
These entities represent a person or place that can be linked to a Quality entity. The entities are not directly used in the PTC Quality domain. However, they can be used in other domains that extend the Quality domain.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Quality Domains > PTC Nonconformance Domain
PTC Nonconformance Domain
PTC NC (Nonconformance) domain provides access to the Windchill Nonconformance capabilities. The domain enables you to manage nonconformances. A nonconformance occurs when a product, manufacturing material, process, document, or other item does not conform to specifications.
The following table lists the significant OData entities available in the PTC Nonconformance domain. To see all the OData entities available in the PTC Nonconformance domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
The PTC NC domain extends the PTC Quality domain.
Items
OData Entities
Description
Nonconformance
Nonconformance
The Nonconformance entity represents a nonconformance process in Windchill.
Originating location
Place
The Place entity represents the location where the nonconformance originated. For example, the manufacturing site.
Originated by
User
The User entity represents the user who created the new nonconformance.
Related personal or location
QualityContact
The QualityContact entity represents a person or place relevant to the nonconformance request.
Affected objects
AffectedObject
The AffectedObject entity represents the subject that is affected by the nonconformance. This entity allows navigation to the Quality subject.
Other items
OtherItem
The OtherItem entity represents the objects that are stored outside of Windchill that are involved in the nonconformance. These items are not available as Quality subject.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Quality Domains > PTC Customer Experience Management Domain
PTC Customer Experience Management Domain
PTC Customer Experience Management (CEM) domain provides access to the Windchill customer experience capabilities. The domain enables you to manage customer experiences in their given workflow state. You can collect, document, track, trend, and report product quality issues recorded by customers as customer experiences.
The following table lists the significant OData entities available in the PTC Customer Experience domain. To see all the OData entities available in the PTC Customer Experience Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
The PTC Customer Experience Management domain extends the PTC Quality domain.
Items
OData Entities
Description
Customer experience
CustomerExperience
The CustomerExperience entity represents the customer experience process in Windchill.
Related products
RelatedProduct
The RelatedProduct entity represents a subject which is impacted by the customer experience. This entity allows navigation to the Quality subject.
Related personal or location
QualityContact
The QualityContact entity represents a person or place that is relevant to the customer experience request.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Quality Domains > PTC Regulatory Master Domain
PTC Regulatory Master Domain
PTC Regulatory Master (RegMstr) domain provides access to the regulatory submission capabilities of Windchill. The domain enables you to create and manage regulatory submissions.
To be authorized to sell products in a specific geography, most companies are required to provide a qualification submission. The regulatory submission feature provides a centralized mechanism to track, manage, and maintain artifacts that are submitted to regulatory agencies.
* 
The PTC Regulatory Master (RegMstr) domain is not available in the Windchill 11.1-M020-CPS05 release.
The following table lists the significant OData entities available in the PTC Regulatory Master domain. To see all the OData entities available in the PTC Regulatory Master domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
The PTC Regulatory Master domain extends the PTC Quality domain.
Items
OData Entities
Description
Regulatory submission sent to a regulatory agency
RegulatorySubmission
The RegulatorySubmission entity represents a version of the regulatory submission.
In Windchill, the RegulatorySubmission class is used to work with regulatory submissions.
You can create subtypes for every type of regulatory submission that is sent to a regulatory agency.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Quality Domains > PTC Regulatory Master Domain > Action Available in the PTC Regulatory Master Domain
Action Available in the PTC Regulatory Master Domain
The following action is available in the PTC Regulatory Master domain:
CreateFollowup
The CreateFollowup action creates a new iteration of the regulatory submission. You can create follow-ups for a completed or expired regulatory submission. After creating a follow-up task, the new iteration of the regulatory submission undergoes the same lifecycle to be submitted to the agency.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Quality Domains > PTC CAPA Domain
PTC CAPA Domain
PTC CAPA domain provides access to the Windchill CAPA capabilities. The domain enables you to manage and view corrective and preventive action objects (CAPAs) in their given workflow state.
The following table lists the significant OData entities available in the PTC CAPA domain. To see all the OData entities available in the PTC CAPA domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
The PTC CAPA domain extends the PTC Quality domain.
Items
OData Entities
Description
CAPA
CAPA
The CAPA entity represents the CAPA process in Windchill.
Sites
CAPASite
The CAPASite entity represents the locations which are impacted by CAPA. For example, the manufacturing site.
Affected Object
AffectedObjects
The AffectedObject entity represents the subject which is affected by CAPA. This entity allows navigation to the Quality subject.
Related personal or location
QualityContact
The QualityContact entity represents a person or place that is relevant to the CAPA request.
Plan
Plan
The entity Plan represents a plan state in CAPA, where further actions are decided.
Action
Action
The entity Action represents the actions of the CAPA plan.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Quality Domains > PTC Audit Domain
PTC Audit Domain
PTC Audit domain provides access to the auditing capabilities available in the Quality product of Windchill. The owner of a quality container can create an audit. This domain enables you to retrieve the audits along with the audit details.
The following table lists the significant OData entities available in the PTC Audit domain. To see all the OData entities available in the PTC Audit domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
The PTC Audit domain extends the PTC Quality domain.
Items
OData Entities
Description
Audit
Audit
The Audit entity represents an audit. The entity supports only GET operation.
Audit details
AuditDetail
The AuditDetail entity represents an audit criterion, which is an individual audit question. The entity supports GET and PATCH operations.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Info*Engine System Domain
PTC Info*Engine System Domain
PTC Info*Engine System domain provides access to the Info*Engine tasks of Windchill. Info*Engine enables you to access, manage, and present data from different information systems. The Info*Engine tasks help in retrieval and manipulation of data within the Info*Engine environment.
The domain provides an unbound function InvokeIETask to invoke the Info*Engine tasks on Windchill. Info*Engine tasks that take their input from web based forms or as URL parameters can be called with this function. Refer to the example Invoking an Info*Engine Task, for more information.
The following table lists the significant OData entities available in the PTC Info*Engine System domain. To see all the OData entities available in the PTC Info*Engine System domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Info*Engine output group
Group
The Group entity represents the XML output of an Info*Engine task. The entity consists of a collection of elements, where every element is a collection of attributes. An attribute is represented with a name-value pair.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Factory Domain
PTC Factory Domain
The PTC Factory domain provides access to the manufacturing data management capabilities of Windchill. It also supports manufacturing process management (MPM) processes, which enable concurrent and collaborative development of product designs and manufacturing processes. The domain is available only if you install Windchill MPMLink.
The following table lists the significant OData entities available in the PTC Factory domain. To see all the OData entities available in the PTC Factory domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Standard operation
StandardOperations
The StandardOperations entity represents the version of a standard operation. In Windchill, use the MPMStandardOperation class to work with the versions of standard operations.
Control characteristic linked to a standard operation
SOPSCCLinks
DDLinks
ResourceLinks
SPLinks
SOPSCCLinks is an OData entity that represents the association between a standard operation and standard control characteristic. It contains attributes, such as, ModelItemUID and GraphicData.
DDLinks is an OData entity that represents the association between a control characteristic, which is linked to a standard operation and describe documents.
ResourceLinks is an OData entity that represents the association between a control characteristic, which is linked to standard operation and processing resources.
SPLinks is an OData entity that represents the association between a control characteristic, which is linked to a standard operation and standard procedures.
Standard control characteristic
StandardControlCharacteristics
SCCDDLinks
SCCSPLinks
SCCResourceLinks
The StandardControlCharacteristics entity represents the version of a control characteristic. In Windchill, use the MPMStandardCC class to work with the versions of standard control characteristics.
SCCDDLinks is an OData entity that represents the association between a standard control characteristic and describe documents.
SCCSPLinks is an OData entity that represents the association between a standard control characteristic and standard procedure.
SCCResourceLinks is an OData entity that represents the association between a standard control characteristic and processing resources.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Manufacturing Process Management Domain
PTC Manufacturing Process Management Domain
The PTC Manufacturing Process Management (MfgProcMgmt) domain provides access to the manufacturing process management capabilities (MPM) of Windchill. Manufacturing Process Management is the process of defining and managing the manufacturing processes, which are used to make parts, assemble final products, and perform inspections. The domain provides OData entities that represent business objects such as process plan, operation, and bill of process (BOP). The domain is available only if you install Windchill MPMLink.
The PTC Manufacturing Process Management domain references the PTC Document Management domain to provide navigation to allocated parts and operated on parts.
The following table lists the significant OData entities available in the PTC Manufacturing Process Management domain. To see all the OData entities available in the PTC Manufacturing Process Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Process Plan
ProcessPlan
StandardProcedure
The ProcessPlan entity represents the version of a process plan. In Windchill, the MPMProcessPlan and MPMProcessPlanMaster classes are used to work with process plan versions.
The StandardProcedure entity is derived from the ProcessPlan entity. StandardProcedure represents an instance of MPMProcessPlan class, where standard attribute is set to true.
Operation
Operation
The Operation entity represents the version of an operation. In Windchill, the MPMOperation and MPMOperationMaster classes are used to work with operation versions.
Sequence
Sequence
The Sequence entity represents the version of a sequence. In Windchill, the MPMSequence and MPMSequenceMaster classes are used to work with sequence versions.
Bill of Process
BOP
OperationHolder
OperationHolderUsageLink
The BOP entity represents the process plan structure. BOP is an operation structure, which is expanded to the required number of levels.
The OperationHolderUsageLink entity represents the association between parent and child parts in OperationHolder entities.
In Windchill, the MPMOperationUsageLink, MPMSequenceUsageLink, and MPMStandardProcessLink classes are used to work with parent-child associations.
Resource
WorkCenter
Skill
Tooling
ProcessingMaterial
The WorkCenter, Skill, Tooling, and ProcessingMaterial entities represent the MPM resources. In Windchill, resources represent objects such as, personnel, material, equipment and so on, that perform the production activities. Manufacturing resources are the resources needed on the shop floor during the production, maintenance, inspection, or repair of parts.
Control Characteristic
StandardControlCharacteristic
The StandardControlCharacteric entity represents a control characteristic version. In Windchill, the MPMStandardCC class is used to work with control characteristics.
subtypeable and softattributable Attributes
The PTC Manufacturing Process Management domain supports the subtypeable and softattributable attributes of Windchill. All the PTC Manufacturing Process Management domain entities that are backed by a persistable which implements the Typed interface, support these attributes.
* 
The subtypeable and softattributable attributes are not supported for the ProcessPlan entity. However, you can add the subentities of the ProcessPlan entity by explicitly configuring the entities in the domain.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Manufacturing Process Management Domain > Actions Available in the PTC Manufacturing Process Management Domain
Actions Available in the PTC Manufacturing Process Management Domain
The following actions are available in the PTC Manufacturing Process Management domain:
GetBOP
The action GetBOP returns the bill of process (BOP) for the process plan structure. The action is bound to the entity NavigationCriteria, that is, to the filter saved in Windchill.
When you call the GetBOP action you can specify the IDs of two NavigationCriteria, that is, processPlanNavigationCriteriaId and relatedAssemblyNavigationCriteriaId in the request body. These are the IDs of the saved filters you want to use as the filter criteria. If you do not specify the IDs of the filter in the request body, then the default filters are used to work with the process plan structure.
GetBOPWithInlineNavCriteria
The GetBOPWithInlineNavCriteria action returns the bill of process (BOP) for the process plan structure for the specified navigation criteria. Pass processPlanNavigationCriteria and relatedAssemblyNavigationCriteria as the input parameters.
In the navigation criteria, if the property ApplyToTopLevelObject is set to True, and no qualifying version is found for the top-level object, an error message is returned.
GetConsumed
The GetConsumed action returns the object associated to a consuming operation for the specified navigation criteria. Pass processPlanNavigationCriteriaId and relatedAssemblyNavigationCriteriaId as the input parameters.
GetConsumedWithInlineNavCriteria
The GetConsumedWithInlineNavCriteria action returns the object associated to a consuming operation for the specified navigation criteria. Pass processPlanNavigationCriteria and relatedAssemblyNavigationCriteria as the input parameters.
In the navigation criteria, if the property ApplyToTopLevelObject is set to True, and no qualifying version is found for the top-level object, an error message is returned.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Change Management Domain
PTC Change Management Domain
The PTC Change Management domain provides access to the change management capabilities of Windchill. The domain includes entities that represent business objects such as, problem report, variance, change request, change notice, and so on. The domain provides navigation to associated process objects and associated reference objects.
The following table lists the significant OData entities available in the PTC Change Management domain. To see all the OData entities available in the PTC Change Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Problem report
ProblemReport
The ProblemReport entity represents the version of a problem report. In Windchill, the WTChangeIssue and WTChangeIssueMaster classes are used to work with versions of a problem report.
Variance
Variance
The Variance entity represents the version of a variance. In Windchill, the WTVariance and WTVarianceMaster classes are used to work with versions of a variance.
Change request
ChangeRequest
The ChangeRequest entity represents the version of a change request. In Windchill, the WTChangeRequest2 and WTChangeRequest2Master classes are used to work with versions of a change request.
Change notice
ChangeNotice
The ChangeNotice entity represents the version of a change notice. In Windchill, the WTChangeOrder2 and WTChangeOrder2Master classes are used to work with versions of a problem report.
Use the navigation property ImplementationPlan to retrieve implementation plans associated with the change notice.
Change task
ChangeTask
The ChangeTask entity represents a version of the change task.
Change tasks are work instructions that are associated with change notices.
In Windchill, the WTChangeActivity2 and WTChangeActivity2Master classes are used to work with versions of a change task.
Associated process links
ProcessLinks
The ProcessLinks entity represents process links between a change object and its associated change objects.
A process link contains only the description attribute and provides information about the attribute.
* 
This entity is supported only for flexible change links.
Associated reference links
ReferenceLinks
The ReferenceLinks entity represents reference links between a change object and its associated change objects.
A reference link contains only the description attribute and provides information about the attribute.
Associated Process Objects
ProcessObjects
The ProcessObjects entity represents associated change objects with parent and child relationships for the given change object.
* 
This entity is supported only for flexible change links.
Associated reference objects
ReferenceObjects
The ReferenceObjects entity represents associated reference objects with parent and child relationships for the given change object. These are references to other change objects.
The following navigation properties are available:
•AffectedLinks—Links between change objects and their affected objects.
•AffectedObjects—Affected objects that are associated with the change objects.
•AffectedByLinks—Links between change objects and their affected objects.
•AffectedByObjects—Change objects that have affected the specified object.
•Attachments—Attachments associated with the change objects. You can see the contents of an attachment and download it.
•ResultingObjects—Resulting objects that are associated with change notices either through resulting links or unincorporated links.
•ResultedByObjects—Change task information for the specified resulting objects, resulting links and unincorporated links.
•ResultingLinks—Resulting links information for the specified change notice.
•ResultingByLinks—Resulting links information for the specified resulting object.
•UnincorporatedLinks—Unincorporated (hanging change) links information for the specified change notice.
•UnincorporatedByLinks—Unincorporated (hanging change) links information for the specified resulting object.
•ChangeAdministratorI—User details about change administrator I.
•ChangeAdministratorII—User details about change administrator II.
•VarianceOwners—User details about variance owner.
The following navigation properties support multiple objects:
•ProcessLinks—Process links for all the change objects.
•ProcessObjects—Process objects for all the change objects.
•ReferenceLinks—Reference links for all the change objects.
•ReferenceObjects—Reference objects for all the change objects.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Classification Structure Domain
PTC Classification Structure Domain
The PTC Classification Structure (ClfStructure) domain provides access to classification nodes and the hierarchy of classification nodes in Windchill. In this domain, you can perform a classification search. The domain includes entities that represent classification node and classified object.
The domain provides navigations to the child nodes or parent node of a classification node. It also provides navigation to the classified objects associated with a classification node.
The following table lists the significant OData entities available in the PTC Classification Structure domain. To see all the OData entities available in the PTC Classification Structure domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Classification node
ClfNode
The ClfNode entity represents a classification node. In Windchill, all the nodes which are accessible from the classification tree are represented using this entity. For example, the entity represents nodes accessed from classification administration, classification explorer, and so on.
* 
In the ClfNodes.json file, the clfStructureNameSpace property specifies the default namespace com.ptc.csm.default_clf_namespace for the classification node. If you want to use some other namespace, specify the namespace in the clfStructureNameSpace property.
The property supports only one namespace.
Classified object
ClassifiedObject
The ClassifiedObject entity represents a classified object associated with a classification node.
In Windchill REST Services 1.3 or later, the property Required is added to the ClfAttributeType complex type. This property specifies if the attribute is a mandatory attribute for classification.
Support Classification Search Using ANY Operator with $filter Expression
You can use classification attributes to perform a classification search. To perform the search, use the $filter parameter along with the lambda operator ANY in the URL. You must query on the ClassificationAttributes property, which is available in the ClassifiedObject entity.
To query, follow these guidelines:
•In the query, you must specify the internal name, followed by the display value of the classification attribute. If both the parameters are not specified in the required sequence, the URL malformed exception is thrown.
•Enclose the name-value pair in parentheses.
•You can use the AND operator for the name-value pair.
•The InternalName property supports only EQ operator.
•Calls to methods startswith, endswith, and contains are supported for attributes, which are of type String. An exception is thrown for other attribute types.
The GET request URL for classification search is:
https://windchill.ptc.com/Windchill/servlet/odata/v1/ClfStructure/ClfNodes('classificationNode')/ClassifiedObjects?$filter=ClassificationAttributes/any(d:d/InternalName eq 'attributeInternalName' and d/DisplayValue eq 'attributeDisplayValue')
For example, consider classification attribute with internal name xje136 and display value 12. To perform a classification search on the classification node FASTENER-THREADEDINSERT, use the following GET request:
GET https://windchill.ptc.com/Windchill/servlet/odata/ClfStructure/ClfNodes('FASTENER-THREADEDINSERT')/ClassifiedObjects?$filter=ClassificationAttributes/any(d:d/InternalName eq ‘xje136’ and d/DisplayValue eq '12') HTTP/1.1


Windchill REST Services Domain Capabilities > PTC Domains > PTC Classification Structure Domain > Functions Available in the PTC Classification Structure Domain
Functions Available in the PTC Classification Structure Domain
The following functions are available in the PTC Classification Structure domain:
GetClassificationNodeInfo()
The function GetClassificationNodeInfo() returns the information about classification attributes for the specified classification node. The input parameters for the function are the namespace of the classification structure and internal name of the classification node.
The function returns the attribute details as a collection of ClassificationInfo complex type. Use this as a payload to classify an object.
GetClfBindingInfo()
The function GetClfBindingInfo() returns information about the classification binding attribute and the node associated with the classified object. The input parameters for the function are the OID of the classified object and namespace of the classification structure. If an object is not classified, then the function returns an empty response.
GetEnumTypeConstraintOnClfAttributes()
The function GetSelectedTypesFromSavedSearch() gets the legal or enumeration values for the specified classification attribute. In the response, the function returns a pair of internal name and display name for every legal or enumeration value.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Saved Search Domain
PTC Saved Search Domain
The PTC Saved Search domain provides access to saved searches in Windchill. You can use the saved searches to execute a search.
The following table lists the significant OData entities available in the PTC Saved Search domain. To see all the OData entities available in the PTC Saved Search domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Saved Search
SavedQuery
The SavedQuery entity represents the saved searches in Windchill.
You can use $filter expressions to query the attributes available in the entity.
* 
The attribute ID cannot be queried using the $filter expressions.
Saved searches are not access controlled. When you query for saved searches, you get a list of all the saved searches from Windchill, even if the saved search was not created by you, or shared with you.
You can share a saved search with members of a context, organization, or site. Such saved searches are set as global search. GlobalSavedSearchVisibility property represents global search. The information that appears in global searches for the GlobalSavedSearchVisibility property is access controlled, because context, organization, and site are access controlled. For global searches, if you do not have the required context, organization, and site level access, the search-related information appears as Secured information.
When you query or execute saved searches, the search queries are logged in the Security Audit Reporting utility in Windchill.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Saved Search Domain > Functions Available in the PTC Saved Search Domain
Functions Available in the PTC Saved Search Domain
The following functions are available in the PTC Saved Search domain:
GetSelectedTypesFromSavedSearch()
The function GetSelectedTypesFromSavedSearch() returns the object types, which were selected when the search was saved. This function is bound to the SavedQuery entity of an object.
ExecuteSavedSearch()
The function ExecuteSavedSearch() is used to execute a saved search. This function is bound to the SavedQuery entity of an object. The function supports pagination. It also supports latest version search. See the section Retrieving the Latest Version of an Entity, for more information on custom query for latest version search.
When you execute a saved search, you can override the keyword defined in the saved search. The keyword specified in the URL takes precedence over the keyword defined in the saved search. The override is applied only when the search is executed. The saved search is not updated with the keyword specified in the request URL.
When you use a saved search to execute a search, the result set may contain Windchill objects of various types. Some of the Windchill objects types are not available in Windchill REST Services. All the object types that are not available in Windchill REST Services are represented as WindchillEntity. For such Windchill objects, the function returns only the ID, created by, and last modified by attributes.
The object types, which are available in Windchill REST Services, are automatically mapped to the relevant entity type. The function returns all the information related to these objects in the search result.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Visualization Domain
PTC Visualization Domain
The PTC Visualization (Visualization) domain provides access to the visualization services of Windchill.
Use Windchill Visualization Services (WVS) to publish lightweight representations of native document content in Windchill. These lightweight representations are then stored in the Windchill database and can be viewed, managed and modified. You can open representations of Windchill documents, such as, CAD Documents, EPMDocuments, and WTDocuments, in Creo View. You can view and annotate the primary content and attachments of the documents in Creo View.
Use the PTC Visualization domain to download CAD data and view it in Creo View.
The following table lists the significant OData entities available in the PTC Visualization domain. To see all the OData entities available in the PTC Visualization domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Windchill representation
Representation
The Representation entity is a lightweight representation of CAD data that is stored in Windchill and is associated with parts and documents. The entity returns the following URLs, which you can use to start Creo View and download CAD data:
•CreoViewURL
•3DThumbnailURL
•2DThumbnailURL
•AdditionalFiles
Refer to the section URLs Retrieved in the Representation Entity, for more information.
In addition to the entities, this domain also contains RepresentationHyperlink complex type, which retrieves additional information for a Representation. It contains a URL and additional attributes, such as, Object ID, Comments, Description, FormatIcon, CreatedOn, LastModified, FileName, FileSize, MimeType, Format and so on.
URLs Retrieved in the Representation Entity
Windchill Visualization Services converts CAD, XML, document, and other data formats into a neutral file format. The converted data is stored as a representation. You can view representations as thumbnail images, which are displayed on information pages of parts and listings throughout Windchill.
In Windchill REST Services, the Representation entity retrieves the following URLs. You can use these URLs to download the CAD data. The URLs are returned in the body of the response. Along with the URL, the entity also retrieves attributes such as, FileSize, MimeType, FileName, Format, and so on for 3D thumbnail, 2D thumbnail, and additional files.
•CreoViewURL—Contains the URL that starts the Creo View application.
•3DThumbnailURL—Contains the URL for 3D thumbnail.
•2DThumbnailURL—Contains the URL for 2D thumbnail.
•AdditionalFiles—Contains the URL to download additional files, which are non-native Creo View files. These files are associated with the specified representation.
For example, consider a DerivedImage with OID 786687. To retrieve the URLs for Creo View, thumbnail and additional files, send the following GET request:

GET /Windchill/servlet/odata/Visualization/Representations('OR:wt.viewmarkup.DerivedImage:786687') HTTP/1.1
The function GetDynamicStructureRepresentation() returns a URL you can use to download the dynamic structure of a Creo View representation. Refer to the section on GetDynamicStructureRepresentation(), for more information.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Visualization Domain > Functions Available in the PTC Visualization Domain
Functions Available in the PTC Visualization Domain
The following functions are available in the PTC Visualization domain:
GetDynamicStructureRepresentation()
The function GetDynamicStructureRepresentation() returns a URL which you can use to download the dynamic structure of a Creo View representation. This function is bound to the Representation entity of an object. The function accepts navigation criteria NavigationCriteriaId as the input parameter. It is an optional parameter. The navigation criteria define which parts and objects are displayed in the dynamic structure. If the navigation criteria is not specified, the function uses the default navigation criteria to generate the URL for the dynamic structure.
You can use the product structure URL to load the CAD data in the WebGL viewer. The viewer uses Creo View WebGL Toolkit APIs.
GetFidelities()
You can get a list of fidelity values associated with a representation. The function GetFidelities() returns a list of fidelity values, which are represented as PTC.EnumType. The function retrieves the fidelity information in a value-display format.
GetPVZ()
You can get a PVZ file from a Creo View representation. The function GetPVZ() returns a ZIP file, which contains the OL, PVS, PVT, and other Creo View files. The PVZ file is created from the associated representation. The function is bound to the Representation entity of an object.
The function contains the following parameters:
•IncludeAnnotations—Includes or excludes annotations in the PVZ file. Pass the parameter as true to include annotations, when the PVZ file is created.
•Fidelity—This is an optional parameter. Specifies the value of fidelity.
* 
The function GetPVZ() does not retrieve multi-fidelity representations for releases prior to Windchill 11.1 M020.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Product Platform Management Domain
PTC Product Platform Management Domain
The PTC Product Platform Management domain provides access to the Options and Variants capabilities of Windchill. The Options and Variants capabilities define fixed options and choices that are used to specify discrete configurations for a product. The domain provides OData entities that represent business objects such as options, choices, option sets, variant specifications, and so on.
* 
This domain is available only when you perform the following actions:
•You install Windchill PDMLink.
•In Windchill, the option Configurable Module Support is set to Yes in Utilities > Preference Management > Options and Variants.
The following table lists the significant OData entities available in the PTC Product Platform Management domain. To see all the OData entities available in the PTC Product Platform Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Options
Option
The Option entity represents a capability or feature of a product that can be designed with variations. An option may have several choices.
The entity provides navigation to Choice or OptionGroup entities.
Choices in an option
Choice
The Choice entity represents the values that are associated with an option.
This entity provides a navigation property that lists the options associated with the choice. You can also expand the navigation property to list the details of the option.
Collection of options
OptionSet
An OptionSet is a collection of options and choices. These options and choices are referenced from the option pool.
This entity provides navigation property that lists all the options available in the option set. You can also expand the navigation property to list the choices available in each option.
Variant specification
VariantSpecification
Variant specification is a collection of inputs and selections specified for a configurable structure when you create a variant.
See the section Navigation Properties Available for VariantSpecification Entity, for information on some of the navigation properties available with VariantSpecification entity.
Information About Other Entities
The following entities are not a part of the service document.
•OptionGroup—Collection of options that enables you to organize the options available for a product.
•OptionPoolItem—Option groups and top-level options created for a Windchill product or library context. Every Windchill product or library context can have a pool of options that are used in option sets.
•DesignOption—Options created for product design.
For example, the following URL retrieves design options:
/ProdPlatformMgmt/Options/PTC.ProdPlatformMgmt.DesignOption
•DesignChoice—Choices created for product design.
For example, the following URL retrieves design choices:
/ProdPlatformMgmt/Choices/PTC.ProdPlatformMgmt.DesignChoice
•SalesOption—Options created for sales.
For example, the following URL retrieves sales options:
/ProdPlatformMgmt/Options/PTC.ProdPlatformMgmt.SalesOption
•SalesChoice—Choices created for sales.
For example, the following URL retrieves sales choices:
/ProdPlatformMgmt/Choices/PTC.ProdPlatformMgmt.SalesChoice
•IndependentAssignedExpression—Independent expressions that are assigned to objects. The entity contains the following navigation properties:
◦AssignedExpression—Retrieves the details for independent expressions. Information about the expression aliases is also returned.
◦Effectivities—Retrieves the effectivities associated with the independent expressions.
Navigation Properties Available for VariantSpecification Entity
The following navigation properties are available for the VariantSpecification entity:
•NavigationCriteria—Retrieves the navigation criteria, which is saved with the variant specification.
•ConfigurableModule—Retrieves the configurable module, which is associated with the variant specification.
•OptionSet—Retrieves the option set assigned to the variant specification.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Product Platform Management Domain > Action Available in the PTC Product Platform Management Domain
Action Available in the PTC Product Platform Management Domain
The following action is available in the PTC Product Platform Management domain:
GetAssignedExpressions
The GetAssignedExpressions action returns the assigned expressions for Part, PartUse, and UsageOccurrence entities. You can specify multiple objects as the input parameter. Basic and advanced types of expressions are supported.
The information related to assigned expressions is retrieved using the complex type, AssignedExpression.
To retrieve the assigned expressions for a single object, use the GetAssignedExpression() function defined in the PTC Product Management domain. See the section Function Available in the PTC Product Management Domain, for more information.
Both dependent and independent expression modes are supported.


Windchill REST Services Domain Capabilities > PTC Domains > PTC CAD Document Management Domain
PTC CAD Document Management Domain
PTC CAD Document Management domain provides access to the CAD data management capabilities of Windchill. CAD data management uses business objects, referred to as CAD documents to contain and manage CAD information in a Windchill database. A CAD document is a revision-controlled and lifecycle-managed object containing a CAD model or drawing file. The CAD model can be a file or a set of files containing information in a CAD application format. This domain enables you to get all the information related to a CAD document.
The following table lists the significant OData entities available in the PTC CAD Document Management domain. To see all the OData entities available in the PTC CAD Document Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
CAD document
CADDocument
CADDocumentUse
CADDocumentReference
DerivedSource
The CADDocument entity represents a version of CAD document. Use the navigation property AllPrimaryContents to get details about the primary content associated with the CAD document.
* 
•AllPrimaryContents navigation property supports all the primary content that is directly downloaded in Windchill. It returns URLs to download the content.
•The primary content that is not directly downloadable in Windchill and opens in other applications is not supported. For example, CAD assembly opens in Creo Parametric, and is not downloadable in Windchill. Such primary contents are not supported by the navigation property.
•When the CAD document does not contain any primary content or contains primary content that is not supported by the navigation, the response returns an empty primary content.
"AllPrimaryContents": []
•The navigation PrimaryContent is not supported for CADDocument entity.
In Windchill, the types with internal names, DefaultEPMDocument and DefaultEPMDocumentMaster, represent the versions of CAD document. Use the classes EPMDocument and EPMDocumentMaster to work with versions of CAD documents.
The CADDocumentUse entity represents the link between a parent assembly and its components. It contains attributes such as, quantity, unit, location, and so on. In Windchill, DefaultEPMMemberLink type and EPMMemberLink class represent this association.
The CADDocumentReference entity represents the link between a CAD document and its references. References are relationships between files that do not have a hierarchical or structural relationship. In Windchill, DefaultEPMReferenceLink type and EPMReferenceLink class represent this association.
The DerivedSource entity represents the link between an image CAD document and its source. An image is an object that has copied most of its content from a source object. In Windchill, EPMDerivedRepHistory class represents this association.
Part associations
PartAssociation
BuildRuleAssociation
BuildHistoryAssociation
ContentAssociation
The PartAssociation entity represents the association links between a CAD document and a WTPart. The types of association links are further represented by the BuildRuleAssociation, BuildHistoryAssociation, and ContentAssociation entities.
The BuildRuleAssociation and BuildHistoryAssociation entities represent the link between a CAD document and WTPart for all associations except Content. In Windchill, the EPMBuildRule and EPMBuildHistory classes represent this association.
The ContentAssociation entity represents the link between a CAD document and WTPart for content association type. In Windchill, it is represented by EPMDescribeLink class.
CAD document structure
CADStructure
The CADStructure entity represents the CAD structure, which is expanded to required number of levels. Use the action GetStructure to retrieve the CAD structure.


Windchill REST Services Domain Capabilities > PTC Domains > PTC CAD Document Management Domain > Action Available in the PTC CAD Document Management Domain
Action Available in the PTC CAD Document Management Domain
The following action is available in the PTC CAD Document Management domain:
GetStructure
The action GetStructure returns a CAD structure. The action is bound to the CADDocument entity.
You can expand the CADDocument and CADDocumentUse navigation properties for more details of the documents.
When you call the GetStructure action in the request body of the URL, you can specify the ID of the NavigationCriteria. This is the ID of the saved filter you want to use as the filter criteria. If you do not specify the ID of the filter in the request body, then the default filter is used to work with the CAD structure. Alternatively, you can specify the navigation criteria in the request payload.
The action additionally returns an attribute Resolved in the response body. The attribute indicates if the link to the document is resolved in the configuration specification. The attribute returns the boolean value true or false depending on whether the link is resolved.
When you call the GetStructure action, the following additional URLs are returned:
•PVTreeId is the occurrence path of the CAD assembly to its member subcomponents in the viewable file. The complete path from the root of the BOM structure is returned. This URL can be used to work with Visualization tree. For example, in an application you consume this URL and highlight the component in the Visualization tree.
•PVParentTreeId is the occurrence path to the parent of the component part in the viewable file. The complete path from the root of the BOM structure is returned.
The action supports the parameter BOMMembersOnly. If you specify BOMMembersOnly as true in the request body, only the CAD documents that participate in the BOM structure are returned. The default value of BOMMembersOnly is false. If the request body is empty, the default value of the parameter is used, and all the structure members are returned.
* 
If the BOM structure contains documents that do not contribute to the BOM, and the user does not have access to such documents, then even though the BOMMembersOnly parameter is set to true in the request body and navigation criteria, the unresolved dependents are returned.
In the request body, use the following code to specify the BOMMembersOnly parameter:
{
"BOMMembersOnly" : true
}
The preferences set for the Auto Associate action in Windchill are honored by GetStructure while returning the structure. The document types and subtypes added in this preference do not participate in the BOM structure of the CAD document.
For example, CAD documents are not included in the structure in the following cases when BOMMembersOnly is set to true:
•If you add the document types and subtypes in the following preference:
Utilities > Preference Management > Operation > Auto Associate > Disallow Structure CAD Document Types
•If the CAD document has a reusable attribute set in the following preference:
Utilities > Preference Management > Operation > Auto Associate > Part Structure Override Attribute Name


Windchill REST Services Domain Capabilities > PTC Domains > PTC Effectivity Management Domain
PTC Effectivity Management Domain
PTC Effectivity Management domain enables you to access effectivity information of Windchill objects. Effectivity is the planned date, lot, or serial number at which old versions of the object are replaced with new versions in production. Objects that are effectivity-managed include parts, documents, manufacturing process objects such as, process plans (manufacturing process plans, sequences, and operations), and manufacturing resources (plants, resource groups, skills, process materials, tooling, and work center).
* 
In this release, product effectivity is supported. You can retrieve the effectivities of Part and IndependentAssignedExpression entities using the Effectivities navigation property. Pending effectivity is not supported.
The following table lists the significant OData entities available in the PTC Effectivity Management domain. To see all the OData entities available in the PTC Effectivity Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Effectivity
Effectivity
SerialNumberEffectivity
LotEffectivity
UnitEffectivity
MSNEffectivity
BlockEffectivity
DateEffectivity
The Effectivity entity represents the effectivity of a Windchill object.
SerialNumberEffectivity, LotEffectivity, UnitEffectivity, MSNEffectivity, and BlockEffectivity entities represent number or range-based effectivities.
DateEffectivity represents date-based effectivity.
Effectivity context
PartEffectivityContext
The PartEffectivityContext entity represents an effectivity context, which is a Part Master.
The entity provides navigation to Context and Organization entities.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Event Management Domain
PTC Event Management Domain
The PTC Event Management domain provides access to the webhook subscription capabilities of Windchill. Webhook subscriptions enable Windchill to send event notifications to external systems when certain events or actions occur on object, folder, or context in Windchill through a webhook URL. The domain must be used along webhook to subscribe to events.
* 
•Webhook subscription is not supported for Windchill soft types.
•Subscription to events using the PTC Event Management domain is supported only for entities available in the following domains:
◦PTC Product Management domain
◦PTC Document Management domain
◦PTC Data Administration domain
◦PTC Change Management domain
◦PTC CAD Document Management domain
◦PTC Service Information Management domain
◦PTC Parts List Management domain
◦PTC Dynamic Document Management domain
The following table lists the significant OData entities available in the PTC Event Management domain. To see all the OData entities available in the PTC Event Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Subscription to an event
EventSubscription
The EventSubscription entity represents the subscription to an event.
Specify the URL to the external system in the CallbackURL property. Notification of the event is sent to this URL.
To create a new subscription, use the POST operation. See the examples in the section Examples for the PTC Event Management Domain for more information on how to specify the payload while creating a subscription.
To delete a subscription, use the DELETE operation.
The EventSubscription entity has a navigation property SubscribedEvent that enables you to see the subscribed event.
Events
Event
The Event entity represents the Windchill events to which you can subscribe.
Subscription to events that occur on a Windchill object
EntityEventSubscription
The EntityEventSubscription entity represents the subscription to events that occur on a Windchill object.
The entity has a navigation property SubscribedOnEntity that enables you to see the entity instance for the subscription.
Subscription to events that occur on a container
EntityTypeInContainerEventSubscription
The EntityTypeInContainerEventSubscription entity represents the subscription to events that occur on a type of Windchill object in the specified context. For example, a Windchill product or library can serve as a context for a subscription.
The entity has a navigation property SubscribedOnContext that enables you to see the context of the subscription.
Subscription to events that occur on a folder
EntityTypeInFolderEventSubscription
The EntityTypeInFolderEventSubscription entity represents the subscription to events that occur on a type of Windchill object in the specified folder.
The entity has a navigation property SubscribedOnFolder that enables you to see the folder that serves as a context of the subscription.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Event Management Domain > Function Available in the PTC Event Management Domain
Function Available in the PTC Event Management Domain
The following function is available in the PTC Event Management domain:
GetApplicableEvents
The function GetApplicableEvents returns a list of all the events that are available for subscription for the specified Windchill object. Specify the Windchill object in the format PTC.<Domain_Name>.<Entity_Type>. For example, to specify a Part, pass the information as PTC.ProdMgmt.Part in the URL:
GET /Windchill/servlet/odata/EventMgmt/GetApplicableEvents(EntityName='PTC.ProdMgmt.Part')


Windchill REST Services Domain Capabilities > PTC Domains > PTC Supplier Management Domain
PTC Supplier Management Domain
The PTC Supplier Management domain provides access to the supplier management capabilities of Windchill. Supplier management enables companies to integrate and manage supply chain data in Windchill. You can create supplier organizations in Windchill PDMLink and populate the database with manufacturer and vendor parts. You can also create and update Approved Manufacturer Part Lists (AMLs) and Approved Vendor Part Lists (AVLs). The AMLs and AVLs are created using the sourcing contexts. PTC Supplier Management domain is available only if you install Supplier Management module in Windchill.
The PTC Supplier Management domain enables you to read sourcing contexts. Other supplier management objects such as, supplier part, manufacturer part, vendor part, and AXLEntry are available in the PTC Product Management domain. See the section PTC Product Management Domain, for more information.
The following table lists the significant OData entities available in the PTC Supplier Management domain. To see all the OData entities available in the PTC Supplier Management domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Sourcing context (sourcing relationship)
SourcingContext
The SourcingContext entity represents the relationship between sourcing contexts in Windchill. Souring context is created in an organization and is used to create an AML or AVL in a specific context.
The SourcingContext entity and SourcingStatus complex type support filtering using $filter parameter along with the lambda operator ANY in the URL.
For more information on how to use lambda operator, see the guidelines explained in the section Support Classification Search Using ANY Operator with $filter Expression.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Workflow Domain
PTC Workflow Domain
PTC Workflow (Workflow) domain provides access to the workflow capabilities of Windchill. A workflow enables you to automate procedures in which information, tasks, and documents are passed to several participants, maybe across multiple companies.
The domain enables you to get all the information related to a workflow task that is associated with a user. Use this domain to perform the following actions:
•Get the list of states of the workitems.
•Get the workitems assigned to you.
•Save tasks.
•Complete tasks.
•Get the list of users to whom a specified task can be reassigned.
•Reassign your tasks to other users.
The following table lists the significant OData entities available in the PTC Workflow domain. To see all the OData entities available in the PTC Workflow domain, refer to the EDM of the domain. The domain EDM is available at the metadata URL.
Items
OData Entities
Description
Work item in Windchill
WorkItem
The WorkItem entity represents tasks in Windchill. A work item is a task that is assigned to a user.
Subject of a workflow
Subject
The Subject entity represents a business object that is associated with the WorkItem entity. Subject can be any business object that is lifecyle managed. For example, parts, CAD documents, change requests, and so on.
Activity in workflow
Activity
Activity represents an action in a process which is assigned in the form of tasks or workitems to users. Every WorkItem entity is associated with Activity.
Templates in a workflow
WorkItemProcessTemplate
The WorkItemProcessTemplate entity represents a workflow template. It is represented as WfProcessTemplate object in Windchill. The Workitem entity is associated with a workflow template.
Information about the user
Owner
CompletedBy
OriginalOwner
The Owner, CompletedBy, and OriginalOwner entities represent the WTUser object in Windchill. Owner information is available for every WorkItem. The CompletedBy and OriginalOwner entities are populated using the complete, reassign, or delegate action.
Auditing details of a task
VotingEventAudit
WfEventAudit
These entities represent WorkItem that is associated with the Activity entity.
The WfEventAudit and VotingEventAudit entities contain the audit information for a specific task. They are associated with work items that are complete.


Windchill REST Services Domain Capabilities > PTC Domains > PTC Workflow Domain > Actions Available in the PTC Workflow Domain
Actions Available in the PTC Workflow Domain
The following actions are available in the PTC Workflow domain:
CompleteWorkitem
The CompleteWorkitem action completes the specified task. The action is bound to the Workitem entity.
You must provide the following mandatory parameters as input to the action in the request body:
{
  "UserEventList":[<routing_options >],
	"WorkitemComment":"<comment_for_the_workitem>",
	"VoteAction":"<Vote_option_selected_by_the_participant>",
	"AutomateFastTrack":<option_to_specify_if_change_notice_should_be_explicitly_created, valid values true or false>,
	"Variables":[<workflow_activity_variables>]
}
SaveWorkitem
The SaveWorkitem action saves the specified task. The action is bound to the Workitem entity.
You must provide the following mandatory parameters as input to the action in the request body:
{
  "UserEventList":[<routing_options >],
	"WorkitemComment":"<comment_for_the_workitem>",
	"VoteAction":"<Vote_option_selected_by_the_participant>",
	"AutomateFastTrack":<option_to_specify_if_change_notice_should_be_explicitly_created, valid values true or false>,
	"Variables":[<workflow_activity_variables>]
}
ReassignWorkItems
The ReassignWorkItems action reassigns the work items or tasks to a specified user. This is an unbound action.
You should provide the following parameters as input to the action in the request body. You can pass the corresponding entities or entity IDs as input parameters.
•WorkItems—Mandatory parameter. List of work item entities.
* 
While reassigning the work items, if you pass all the attributes of a work item as input, the action only considers the work item ID attribute. The other work item attributes are ignored.
•User—Mandatory parameter. User entity.
•Comment—Optional parameter. User comment.
{
  "WorkItems":[{"ID":"<workitem_entity_ID>"}],
  "User":{"ID":"<user_entity_ID>"},
  "Comment":"<user_comment>"
}                               


Windchill REST Services Domain Capabilities > PTC Domains > PTC Workflow Domain > Function Available in the PTC Workflow Domain
Function Available in the PTC Workflow Domain
The following function is available in the PTC Workflow domain:
GetWorkItemReassignUserList
The GetWorkItemReassignUserList function returns a list of valid users to whom the specified work items can be reassigned.


Windchill REST Services Domain Capabilities > PTC Domains > PDM Domain
PDM Domain
The PDM domain is a conglomerate domain that combines the following core Windchill domains:
•PTC Product Management
•PTC Document Management
•PTC Change Management
•PTC Principal Management
•PTC CAD Document Management
The PDM domain also includes the dependent domains of the core Windchill domains. For example, the dependent domains such as PTC Data Administration, PTC Navigation Criteria, and so on are also imported in the PDM domain.
PTC domains use edmx:Reference to reference the EDM of other domains. A client that does not understand reference, cannot access the PTC domains. The EDM of the conglomerate domain includes EDMs of all the core and dependent domains.
As the PDM domain is a conglomerate domain, it does not reference any external schema. This domain enables clients that do not understand edmx:Reference to access and work with the PTC domains.
The domain is accessed by OData clients, such as, Microsoft PowerBI and Excel, that cannot get data directly from core domains. If you want to build Windchill reports or dashboards using Microsoft PowerBI and Excel, you should use the PDM domain instead of using the core domains directly.
You can perform only READ operations on entities and execution of functions for the imported domains. CREATE, UPDATE, and DELETE operations, and actions are not supported. In this domain, you cannot define new entities, complex types, actions, and functions.
You can also create your own customized conglomerate domain. To create a conglomerate domain, specify the conglomerate property as true in the <Domain JSON File>. Ensure that no entities, complex types, actions or functions are defined in the domain. See the sections Domain JSON File for more information on domain JSON file and Creating New Domains for instructions on creating a new domain.


Windchill REST Services Domain Capabilities > PTC Domains > Accessing Domains
Accessing Domains
This section describes how clients work with domains. The information in this section applies to all the domains installed with Windchill REST Services.
When Windchill REST Services is installed, the servlet WcRestServlet is enabled in the Windchill installation. All requests to the domain resources, which are enabled by Windchill REST Services, pass through this servlet. The root URL to access this servlet is https://<Windchill server>/Windchill/servlet/odata/. When an HTTP GET request is sent to this URL, the servlet responds back with a list of domains available on the server.
From the servlet response, clients can select a domain, and send a GET request to the root URL of the domain to get a list of available entity sets. Clients can send GET, POST, PUT, and DELETE requests to the URLs of the entity sets.
The following URLs are used to interact with Windchill REST Services:
•REST Root URL—https://<Windchill server>/Windchill/servlet/odata/
A GET request to this URL lists the domains available on the Windchill server. Clients can use this URL to get the list of services that are available on a Windchill server.
For example, the request URL is as shown below:
GET https://windchill.ptc.com/Windchill/servlet/odata
•Domain Root URL—https://<Windchill server>/Windchill/servlet/odata/<Domain>
A GET request to this URL returns the information about the entity sets available in the domain. This request is same as that defined in OData protocol for the Service Root URL. The <Domain> in the URL refers to the domain identifier id, which is returned by the REST Root URL in the list of domains.
For example, the request URL to the Domain Root URL of the ProdMgmt domain is as shown below.
GET https://windchill.ptc.com/Windchill/servlet/odata/ProdMgmt/
•Domain Metadata URL—https://<Windchill server>/Windchill/servlet/odata/<Domain>/$metadata
A GET request to this URL returns the entity data model for the domain defined in the Common Schema Definition Language (CSDL). In the OData protocol, this is called the Metadata Document URL.
For example, the output from a GET request to this URL for the PrincipalMgmt domain is as shown below. This URL is used to get information about the entity sets, entities, and entity relations provided by the service. For more information on entity sets, entities, and entity relations, please refer to the OData protocol documentation.
GET https://windchill.ptc.com/Windchill/servlet/odata/PrincipalMgmt/$metadata
Entity Set URL—https://<Windchill server>/Windchill/servlet/odata/<Domain>/<EntitySetURL>
An Entity Set URL references an entity set, which is available in the response of a domain, to a GET request by the Domain Root URL.
For example, if a Domain Root URL contains an entity set called Parts, the Entity Set URL is https://windchill.ptc.com/Windchill/servlet/odata/ProdMgmt/Parts. A GET request to this URL returns a set of entities.
Request URL:
GET https://windchill.ptc.com/Windchill/servlet/odata/ProdMgmt/Parts
Entity Set URL is the main endpoint to perform create, read, update, and delete operations using the HTTP requests POST, GET, PATCH and DELETE respectively.
Let us continue using the above example. To create a part the client sends a POST request to the URL https://windchill.ptc.com/Windchill/servlet/odata/ProdMgmt/Parts. The body of the request contains a set of property names and values specified in a format that is acceptable to the server. JSON is the preferred format when interacting with Windchill REST service.
To update the part, clients send a PATCH request on the same URL. The body of the PATCH request contains a set of property names and values that will be modified.
To delete a part, clients send a DELETE request to the URL https://windchill.ptc.com/Windchill/servlet/odata/ProdMgmt/Parts(‘<key>’). In this URL, key is the unique identifier for the part in the entity set. The object reference string in Windchill is treated as the key. To delete a part with object reference ‘OR:wt.part.WTPart:668899’, the DELETE request is https://windchill.ptc.com/Windchill/servlet/odata/ProdMgmt/Parts(‘OR:wt.part.WTPart:668899’).
Clients usually interact with the REST APIs using the Entity Set URL. All the entities in a domain may not have entity sets. Therefore, some entities in the domain are available using navigations. For example, a specific PartUse entity in the ProdMgmt domain is accessed by https://windchill.ptc.com/Windchill/servlet/odata/ProdMgmt/Parts(<part_key>)/Uses(<uses_key>). Here <part_key> and <uses_key> are object reference strings that uniquely identify a part and a usage link.


Windchill REST Services Domain Capabilities > PTC Domains > Actions Available for Single and Multiple Objects
Actions Available for Single and Multiple Objects
Actions are available to support the following operations for single and multiple objects.
These following actions are available for PTC Product Management and PTC Document Management domains, for parts and documents respectively.
•Creating objects
•Updating objects
•Deleting objects
•Checking in objects—Available for all entities that inherit workable capability
•Checking out objects—Available for all entities that inherit workable capability
•Undoing a check out—Available for all entities that inherit workable capability
Action to create a revision of objects is available for all the entities of a domain that inherit the versioned capability.
Actions for Single Object
The following actions take a single object as input parameter.
•These actions are available in PTC Product Management and PTC Document Management domains.
◦CheckIn—Pass the following input parameters:
▪Part or document to check in depending on the domain
▪Check in note
▪KeepCheckedOut
▪CheckOutNote
◦CheckOut—Pass the following input parameters:
▪Part or document to check out depending on the domain
▪Check out note
◦UndoCheckOut—Pass as input parameter the part or document for which you want to undo the check out.
•Revise action is available for domains that inherit the versioned capability. Pass as input parameter the part or document ID that you want to revise. You can also pass other optional parameters such as VersionId if the preference Allow Override On Revise is set to Yes.
Actions for Multiple Objects
The following actions take a collection of objects as the input parameter.
•These actions are available for all the entities that inherit the workable capability.
◦CheckIn<EntitySet_name>
◦CheckOut<EntitySet_name>
◦UndoCheckOut<EntitySet_name>
•Delete<EntitySet_name>—Available for entities in a domain where "multiOperations": "DELETE" is specified in the Entity JSON file.
•Revise<EntitySet_name>—Available for entities in a domain that inherits the versioned capability.
•These actions are available for all the entities in the PTC Product Management and PTC Document Management domains.
◦Create<EntitySet_name>—Available for entities where "multiOperations": "CREATE" is specified in the Entity JSON file.
◦Update<EntitySet_name>—Available for entities where "multiOperations": "UPDATE" is specified in the Entity JSON file.
For example, the actions available in the PTC Product Management domain are as follows:
•CreateParts—Pass the following input parameters:
◦Collection of parts to create
◦ID of the container in which you want to create the parts and other required attributes to create a part
•UpdateParts—Pass the following input parameters:
◦Collection of parts to update
◦Attributes of part with updated values
•CheckInParts—Pass the following input parameters:
◦Collection of parts to check in
◦Check in note
◦KeepCheckedOut
◦CheckOutNote
•CheckOutParts—Pass the following input parameters:
◦Collection of parts to check out
◦Check out note
•UndoCheckOutParts—Pass as input parameter a collection of parts for which you want to undo the check out operation.
•DeleteParts—Pass as input parameter a collection of parts which you want to delete. When the objects to delete have iterations and revisions, the delete operation is executed as described in the following table:
Details of URL Payload
Delete Operation
Part entity specified in the payload is not the latest iteration in its revision
Part object is not deleted and delete operation is rolled back
Part entity specified in the payload is not the latest iteration in its revision, and later revisions of the part object exist but are not specified in the payload
Part object is not deleted and delete operation is rolled back
Part entity specified in the payload is the latest iteration in its revision, and all the latest revisions of the part entity are also specified in the payload
Deletes all iterations of all revisions
Part entity specified in the payload is the latest iteration of the latest revision
Deletes all iterations of the latest revision
•ReviseParts—Pass as input parameter a collection of parts that you want to revise.
Similarly, CheckInDocuments, CheckOutDocuments, and so on are available in PTC Document Management domain.
Execution of Actions on Multiple Objects
When you perform multiple objects actions, consider the following:
•You can perform the multiple object action on one or more objects.
•The action is successfully executed for all objects. If the action fails for any object in the collection, the entire action is rolled back, the operation stops, and an error message is returned to the caller.


Windchill REST Services Domain Capabilities > PTC Domains > Common Navigation Properties Available in All the Domains
Common Navigation Properties Available in All the Domains
Windchill REST Services provides the following navigations properties which contain all the information related to the user. The navigation properties are available in all the domains that import the PTC Principal Management domain and for all the Windchill entities that support the creator and modifier attributes.
•Creator—Information about user who created the entity.
•Modifier—Information about user who modified the entity.
The navigation properties enable filtering on the source entity for the following user attributes:
•User name
•Full name
•Last name
•Email address