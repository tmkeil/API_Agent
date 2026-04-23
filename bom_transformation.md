Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs
This section describes the key actions available in the BOM transformation domain for creating or updating downstream manufacturing BOMs.
Refer to the domain EDM for a complete list of actions.


Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > NewDownstreamPart
NewDownstreamPart
The NewDownstreamPart action creates a new downstream part and then creates new equivalent links to the specified upstream part. The action creates an equivalent downstream assembly with a new part number and view. You can create a new downstream part for the specified upstream part using inline or specific upstream and downstream navigation criteria.
You can also create the new downstream part in the context of change (change task or change notice).
The attributes in the request payload of the NewDownstreamPart action are described in the following table:
Request Attribute
Description
Required
SourcePart
Attribute in the TransformationDefinitions collection to specify the OID of the upstream part for which you want to create a new downstream part.
Yes
ReviseExistingDownstream
Flag in the TransformationDefinitions collection to specify whether the existing downstream objects should be revised or not during the transformation.
* 
*ReviseExistingDownstream is a required attribute when you specify ExistingDownstreamAssociations.
When ExistingDownstreamAssociations is not specified, the ReviseExistingDownstream flag is ignored, even if it is provided.
Yes*
TransformationOption
Attribute in the TransformationDefinitions collection to specify the child structure option such as Do not duplicate, Duplicate with propagating, or Duplicate without propagating for the transformation.
* 
*TransformationOption is not applicable when you specify ExistingDownstreamAssociations.
Yes*
ExistingDownstreamAssociations
Array type of attribute in the TransformationDefinitions collection to specify the OID of the equivalent link between a specified upstream part and its existing downstream equivalent object.
Alternatively, you can specify the value composed of an upstream part OID and its existing downstream part OID. The value is specified for the upstream part when its existing downstream object is not equivalent to it.
Optional
View
Attribute in the TransformationEntity entity type to specify the downstream view to be used in the transformation.
Yes
BOMType
Attribute in the TransformationEntity entity type to specify the type of downstream BOM being used.
Optional
AlternateBOM
Attribute in the TransformationEntity entity type to specify an alternate BOM for the transformation.
Optional
Context
Attribute in the TransformationEntity entity type to specify the context in which you want to create the downstream object.
Yes
Folder
Attribute in the TransformationEntity entity type to specify the location at which you want to create the downstream object.
Yes
Number
Attribute in the TransformationEntity collection to specify an identification number for the new part in the downstream.
If you specify an existing part number, then the system searches for that part in Windchill and shows it as an existing downstream part along with the other existing downstream parts.
Optional
DownstreamNavigationCriteria
Inline or specific navigation criteria applied in the downstream.
Yes
UpstreamNavigationCriteria
Inline or specific navigation criteria applied in the upstream.
Yes
ChangeOid
Attribute to specify the change task or change notice.
Optional
The request creates a new downstream part and an equivalence link between the new downstream part and the specified upstream part. The request also returns information for the equivalence link.
If child parts exist for a specified upstream part, the request also returns information about the equivalence link for each child part, according to the specified child structure option.
POST  Windchill/servlet/odata/BomTransformation/NewDownstreamPart
For example, the response to the request URI is as follows:
{
  "@odata.context": "$metadata#ExistingDownstreamAssociations",
  "value": [
    {
      "ID": "OR:wt.associativity.EquivalenceLink:213450",
      "UpstreamPartId": "OR:wt.part.WTPart:213274",
      "DownstreamPartId": "OR:wt.part.WTPart:213408",
      "EquivalenceLinkId": "OR:wt.associativity.EquivalenceLink:213440",
      "IsEquivalenceLinkOutdated": false
    }
  "@PTC.AppliedContainerContext.LocalTimeZone": "Europe/Warsaw"
}
The attributes in the response for the NewDownstreamPart action are described in detail in the following table:
Response Attribute
Description
ID
Attribute in a collection that returns the ID of the associative link between the upstream part specified in the request and the newly created downstream equivalent part.
UpstreamPartId
Attribute in a collection that returns the ID of the upstream part specified in the request for which a new downstream part is created.
* 
If child parts exist for the specified upstream part, the attribute also returns the ID of each upstream child part for which a new downstream equivalent part is created.
DownstreamPartId
Attribute in a collection that returns the ID of the newly created downstream equivalent part.
EquivalenceLinkId
Attribute in a collection that returns the ID of the equivalence link between the upstream part and the newly created downstream equivalent part.
IsEquivalenceLinkOutdated
Attribute in a collection that indicates whether the equivalence link between the upstream part specified in the request and the newly created downstream equivalent part is outdated or not.




Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > NewDownstreamBranch
NewDownstreamBranch
The NewDownstreamBranch action creates a new downstream branch iteration for the specified upstream part to create an equivalent downstream assembly. You can specify a single or multiple upstream parts to create a new downstream branch for each part using inline or specific upstream and downstream navigation criteria.
You can also create the new downstream branch iteration in the context of change (change task or change notice).
The attributes in the request payload of the NewDownstreamBranch action are described in the following table:
Request Attribute
Description
Required
SourcePart
Attribute in the TransformationDefinitions collection to specify the OID of the upstream part for which you want to create a new branch.
Yes
ReviseExistingDownstream
Flag in the TransformationDefinitions collection to specify whether the existing downstream objects should be revised or not during the transformation.
Optional
TransformationOption
Attribute in the TransformationDefinitions collection to specify the child structure option such as Do not duplicate, Duplicate with propagating, or Duplicate without propagating for the transformation.
Yes
ExistingDownstreamAssociations
Array type of attribute in the TransformationDefinitions collection to specify the OID of the equivalent link between a specified upstream part and its existing downstream equivalent object.
Optional
View
Attribute in the TransformationEntity entity type to specify the downstream view to be used in the transformation.
Yes
BOMType
Attribute in the TransformationEntity entity type to specify the type of downstream BOM being used.
Optional
AlternateBOM
Attribute in the TransformationEntity entity type to specify an alternate BOM for the transformation.
Optional
Context
Attribute in the TransformationEntity entity type to specify the context in which you want to create the downstream object.
* 
When not specified, the new downstream part is created in one of the following contexts:
•Default context. This context is the same as that of the specified upstream part.
•The context set in the Associativity > Downstream Creation > Context preference in Windchill.
Optional
Folder
Attribute in the TransformationEntity entity type to specify the location at which you want to create the downstream object.
* 
When not specified, the new downstream part is created at one of the following locations:
•Default location. This location is the same as that of the specified upstream part.
•The location set in the Associativity > Downstream Creation > Location preference in Windchill.
Optional
DownstreamNavigationCriteria
Inline or specific navigation criteria applied in the downstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
UpstreamNavigationCriteria
Inline or specific navigation criteria applied in the upstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
ChangeOid
Attribute to specify the change task or change notice.
Optional
The request creates an equivalence link between the new downstream branch iteration and the specified upstream part and returns information about the equivalence link.
If child parts exist for a specified upstream part, the request also returns information about the equivalence link for each child part, according to the specified child structure option.
POST  Windchill/servlet/odata/BomTransformation/NewDownstreamBranch
For example, the response to the request URI is as follows:
{
  "@odata.context": "$metadata#ExistingDownstreamAssociations",
  "value": [
    {
      "ID": "OR:wt.associativity.EquivalenceLink:213440",
      "UpstreamPartId": "OR:wt.part.WTPart:213274",
      "DownstreamPartId": "OR:wt.part.WTPart:213408",
      "EquivalenceLinkId": "OR:wt.associativity.EquivalenceLink:213440",
      "IsEquivalenceLinkOutdated": false
    },
    {
      "ID": "OR:wt.associativity.EquivalenceLink:213450",
      "UpstreamPartId": "OR:wt.part.WTPart:213845",
      "DownstreamPartId": "OR:wt.part.WTPart:213407",
      "EquivalenceLinkId": "OR:wt.associativity.EquivalenceLink:213450",
      "IsEquivalenceLinkOutdated": false
    }
  ],
  "@PTC.AppliedContainerContext.LocalTimeZone": "Europe/Warsaw"
}
The attributes in the response for the NewDownstreamBranch action are described in the following table:
Response Attribute
Description
ID
Attribute in a collection that returns the ID of the equivalence link between the upstream part specified in the request and the newly created downstream equivalent part.
UpstreamPartId
Attribute in a collection that returns the ID of the upstream part specified in the request for which a new downstream branch is created.
* 
When child parts exist for the specified upstream part, the attribute also returns the ID of each upstream child part for which a new downstream equivalent part is created.
DownstreamPartId
Attribute in a collection that returns the ID of the newly created downstream equivalent part.
EquivalenceLinkId
Attribute in a collection that returns the ID of the equivalence link between the upstream part and the newly created downstream equivalent part.
IsEquivalenceLinkOutdated
Attribute in a collection that indicates whether the equivalence link between the upstream part specified in the request and the newly created downstream equivalent part is outdated or not.





Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > GenerateDownstreamStructure
GenerateDownstreamStructure
The GenerateDownstreamStructure action by default first matches the specified upstream parent part with its downstream parent part using custom attribute values. The action then transfers the parts in the upstream structure to the downstream using the PasteAsIs action. You can customize the logic by applying the restructuring rules in Windchill in the associativity.properties.xconf file located in Windchill/codebase/com/ptc/core/foundation/associativity.
* 
•To perform this action, an equivalent link must exist between the upstream and downstream root parts.
•You can use custom usage attributes and custom part attributes. Ensure that you update or add the properties accordingly in Windchill for performing this action.
You can generate a downstream structure for parts under an assembly using inline or specific upstream and downstream navigation criteria.
You can also generate the downstream structure in the context of change (change task or change notice).
See the Overview of Generate Downstream Structure Action topic in the Windchill Help Center, for more information.
The attributes in the request payload of the GenerateDownstreamStructure action are described in the following table:
Request Attribute
Description
Required
SourceRoot
Attribute in the DiscrepancyContext entity type to specify the root part of the upstream structure.
Yes
SourcePartSelection
Attribute in the DiscrepancyContext entity type to specify the parent Part from the upstream structure.
Alternatively, you can specify the Path of the parent part.
* 
SourcePartSelection is a collection for specifying a single upstream parent part or its path.
Optional
UpstreamNavigationCriteria
Attribute in the DiscrepancyContext entity type to specify the navigation criteria applied in the upstream.
Yes
DownstreamNavigationCriteria
Attribute in the DiscrepancyContext entity type to specify the navigation criteria applied in the downstream.
Yes
TargetRoot
Attribute in the DiscrepancyContext entity type to specify the root part of the downstream structure.
Yes
TargetPart
Attribute in the DiscrepancyContext entity type to specify the parent part of a downstream structure to which you want to paste the copied parts.
Alternatively, you can specify the path of the downstream parent part, that is, TargetPath to which you want to paste the copied parts.
* 
*TargetPart is a required attribute when you want to specify a parent part of the downstream structure that you want to traverse for pasting the copied parts.
Yes*
ChangeOid
Attribute to specify the change task or change notice.
Optional
The request, by default, copies the parts from the specified upstream structure and pastes those as is to the downstream or it copies and pastes the parts based on the restructuring rules applied in the custom logic. The request creates new equivalence links between the downstream BOM and the upstream BOM.
POST  Windchill/servlet/odata/BomTransformation/GenerateDownstreamStructure
For example, the following is the response:
{
  "@odata.context": "$metadata#EquivalentUsageAssociations",
  "value": [
    {
      "UpstreamPartId": "OR:wt.part.WTPart:189986",
      "DownstreamPartId": "OR:wt.part.WTPart:189986",
      "EquivalenceLinkId": "OR:wt.associativity.EquivalenceLink:190604",
      "UsageLinkId": "OR:wt.part.WTPartUsageLink:190605"
    }
  ],
  "@PTC.AppliedContainerContext.LocalTimeZone": "Europe/Warsaw"
}
The attributes in the response for the GenerateDownstreamStructure action are described in the following table:
Response Attribute
Description
UpstreamPartId
Attribute in a collection that returns the ID of the upstream part which was copied.
DownstreamPartId
Attribute in a collection that returns the ID of the downstream equivalent part.
EquivalenceLinkId
Attribute in a collection that returns the ID of the equivalence link between the upstream part and the downstream equivalent part.
UsageLinkId
Attribute in a collection that returns the ID of the usage link between the downstream parent part and the added downstream part.









Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > NewDownstreamAlternate
NewDownstreamAlternate
The NewDownstreamAlternate action enables you to specify an existing downstream iteration and create a new iteration at the downstream branch. You can create the new downstream alternate only within the same view and BOM type as that of the existing downstream iteration. You can specify a single or multiple existing downstream iterations to create new iterations in the downstream structure. You can create a new iteration using inline or specific upstream and downstream navigation criteria.
You can also create the new downstream alternate in the context of change (change task or change notice).
See the Creating Alternate BOMs topic in the Windchill Help Center, for more information.
The attributes in the request payload of the NewDownstreamAlternate action are described in the following table:
Request Attribute
Description
Required
SourcePart
Attribute in the TransformationDefinitions collection to specify the OID of the existing downstream iteration for which you want to create a new iteration at the downstream branch.
Yes
TransformationOption
Attribute in the TransformationDefinitions collection to specify the child structure option such as Do not duplicate or Duplicate without propagating for the transformation.
Yes
AlternateBOM
Attribute in the TransformationEntity entity type to specify an alternate BOM for the transformation.
* 
Since the action allows you to create alternates only within the same view and BOM type, the attributes View and BOMType are not applicable.
Yes
Context
Attribute in the TransformationEntity entity type to specify the context in which you want to create the new downstream iteration.
Yes
Folder
Attribute in the TransformationEntity entity type to specify the location at which you want to create the new downstream iteration.
* 
When not specified, the new downstream iteration is created at one of the following locations:
•Default location. This location is the same as that of the specified upstream part.
•The location set in the Associativity > Downstream Creation > Location preference in Windchill.
Optional
DownstreamNavigationCriteria
Inline or specific navigation criteria applied in the downstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
UpstreamNavigationCriteria
Inline or specific navigation criteria applied in the upstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
ChangeOid
Attribute to specify the change task or change notice.
Optional
The request creates a new iteration at the downstream branch from the specified existing downstream iteration. The request retains the equivalence between the specified existing downstream iteration and its upstream equivalent iteration. The same equivalence persists between the new downstream iteration and the upstream iteration. The request also returns information for the equivalence link.
If child parts exist for the specified existing downstream iteration, the request retains the equivalence link between each child part in the existing downstream iteration and in the upstream equivalent iteration. The request retains the equivalent links between the downstream and upstream equivalent child parts according to the specified child structure option.
POST  Windchill/servlet/odata/BomTransformation/NewDownstreamAlternate
For example, the response to the request URI is as follows:
{
  "@odata.context": "$metadata#ExistingDownstreamAssociations",
  "value": [
    {
      "ID": "OR:wt.associativity.EquivalenceLink:213440",
      "UpstreamPartId": "OR:wt.part.WTPart:213274",
      "DownstreamPartId": "OR:wt.part.WTPart:213408",
      "EquivalenceLinkId": "OR:wt.associativity.EquivalenceLink:213440",
      "IsEquivalenceLinkOutdated": false
    }
  ],
  "@PTC.AppliedContainerContext.LocalTimeZone": "Europe/Warsaw"
}
The attributes in the response for the NewDownstreamAlternate action are described in detail in the following table:
Response Attribute
Description
ID
Attribute in a collection that returns the ID of the equivalence link between the new downstream iteration and the existing upstream equivalent part.
UpstreamPartId
Attribute in a collection that returns the ID of the upstream part equivalent to the specified existing downstream iteration.
* 
If child parts exist for the specified upstream part, the attribute also returns the ID of each upstream child part.
DownstreamPartId
Attribute in a collection that returns the ID of the new downstream iteration.
EquivalenceLinkId
Attribute in a collection that returns the ID of the equivalence link between the new downstream iteration and the existing upstream equivalent part.
IsEquivalenceLinkOutdated
Attribute in a collection that indicates whether the equivalence link between the new downstream iteration and the upstream equivalent part is outdated or not.










Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > PasteAsIs
PasteAsIs
The PasteAsIs action adds the copied part and its upstream structure to the specified part in the downstream structure, as is. The action creates new equivalence links between the downstream BOM and the upstream BOM. You can add the copied parts using inline or specific upstream and downstream navigation criteria.
You can also add the copied upstream part as is to the downstream structure in the context of change (change task or change notice).
The attributes in the request payload of the PasteAsIs action are described in detail in the following table:
Request Attribute
Description
Required
TargetRoot
Attribute to specify the root part of the target (downstream) structure in the BOM transformer.
Yes
TargetPath
Attribute to specify the path of the downstream part under which you want to add the copied part.
Yes
SourceRoot
Attribute to specify the root part of the upstream structure in the BOM transformer.
Yes
SourcePart
Attribute in the TransformationDefinitions collection to specify the OID of the upstream part that you want to copy.
Yes
SourcePaths
Array type attribute in the TransformationDefinitions collection to specify the path of the specified upstream part occurrence from its upstream root part.
Yes
ReviseExistingDownstream
Flag in the TransformationDefinitions collection to specify whether you want to allow the existing downstream objects to be revised or not during the transformation.
Optional
ExistingDownstreamAssociations
Array type of attribute in the TransformationDefinitions collection to specify the OID of the equivalent link between a specified upstream part and its existing downstream equivalent object.
Optional
DownstreamNavigationCriteria
Inline or specific navigation criteria applied in the downstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
UpstreamNavigationCriteria
Inline or specific navigation criteria applied in the upstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
ChangeOid
Attribute to specify the change task or change notice.
Optional
The request adds the specified upstream part and its structure under the specified downstream part and creates new equivalence links between the downstream BOM and the upstream BOM.
POST  Windchill/servlet/odata/BomTransformation/PasteAsIs
For example, the response to the request URI is as follows:
{
  "@odata.context": "$metadata#ExistingDownstreamAssociations",
  "value": [
    {
      "ID": "OR:wt.associativity.EquivalenceLink:213450",
      "UpstreamPartId": "OR:wt.part.WTPart:213274",
      "DownstreamPartId": "OR:wt.part.WTPart:213408",
      "EquivalenceLinkId": "OR:wt.associativity.EquivalenceLink:213440",
      "IsEquivalenceLinkOutdated": false
    }
  "@PTC.AppliedContainerContext.LocalTimeZone": "Europe/Warsaw"
}
The attributes in the response for the PasteAsIs action are described in the following table:
Response Attribute
Description
ID
Attribute in a collection that returns the ID of the equivalent link between the upstream part and the downstream equivalent part.
UpstreamPartId
Attribute in a collection that returns the ID of the upstream part which was copied.
DownstreamPartId
Attribute in a collection that returns the ID of the downstream equivalent part.
EquivalenceLinkId
Attribute in a collection that returns the ID of the equivalence link between the upstream part and the downstream equivalent part.
IsEquivalenceLinkOutdated
Attribute in a collection that indicates whether the equivalence link between the upstream part and the downstream equivalent part is outdated or not.








Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > PasteAsNewPart
PasteAsNewPart
The PasteAsNewPart action adds a copied part and its upstream structure as a new part in the downstream structure and creates a new equivalence link to the copied upstream part. You can add the copied parts using inline or specific upstream and downstream navigation criteria.
You can also add the copied upstream part as a new part to the downstream structure in the context of change (change task or change notice).
The attributes in the request payload of the PasteAsNewPart action are described in the following table:
Request Attribute
Description
Required
TargetRoot
Attribute to specify the root part of the downstream structure in the BOM transformer.
Yes
TargetPath
Attribute to specify the path of the downstream part under which you want to add the copied part.
Yes
SourceRoot
Attribute to specify the root part of the upstream structure in the BOM transformer.
Yes
SourcePart
Attribute in the TransformationDefinitions collection to specify the OID of the upstream part that you want to copy.
Yes
SourcePaths
Array type of attribute in the TransformationDefinitions collection to specify the path of the specified upstream part occurrence from its upstream root part.
Yes
TransformationOption
Attribute in the TransformationDefinitions collection to specify the child structure option such as Do not duplicate, Duplicate with propagating, or Duplicate without propagating for the transformation.
* 
*TransformationOption is not applicable when you specify ExistingDownstreamAssociations.
Yes*
ReviseExistingDownstream
Flag in the TransformationDefinitions collection to specify whether you want the existing downstream objects to be revised or not during the transformation.
* 
*ReviseExistingDownstream is a required attribute when you specify ExistingDownstreamAssociations.
When ExistingDownstreamAssociations is not specified, the ReviseExistingDownstream flag is ignored, even if it is provided.
Yes*
ExistingDownstreamAssociations
Array type of attribute in the TransformationDefinitions collection to specify the OID of the equivalent link between a specified upstream part and its existing downstream equivalent object.
Alternatively, you can specify the value composed of an upstream part OID and its existing downstream part OID. The value is specified for the upstream part when its existing downstream object is not equivalent to it.
Optional
View
Attribute in the TransformationEntity entity type to specify the downstream view to be used in the transformation.
Yes
BOMType
Attribute in the TransformationEntity entity type to specify the type of downstream BOM being used.
Optional
AlternateBOM
Attribute in the TransformationEntity entity type to specify an alternate BOM for the transformation.
Optional
Context
Attribute in the TransformationEntity entity type to specify the context in which you want to create the downstream object.
Yes
Folder
Attribute in the TransformationEntity entity type to specify the location in which you want to create the downstream object.
Yes
Number
Attribute in the TransformationEntity collection to specify an identification number for the new part in the downstream.
If you specify an existing part number, then the system searches for that part in Windchill and shows it as an existing downstream part along with the other existing downstream parts.
Optional
DownstreamNavigationCriteria
Inline or specific navigation criteria applied in the downstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
UpstreamNavigationCriteria
Inline or specific navigation criteria applied in the upstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
ChangeOid
Attribute to specify the change task or change notice.
Optional
The request adds the specified upstream part and its structure as a new part in the downstream structure and creates a new equivalence link to the copied upstream part.
POST  Windchill/servlet/odata/BomTransformation/PasteAsNewPart
For example, the response to the request URI is as follows:
{
  "@odata.context": "$metadata#ExistingDownstreamAssociations",
  "value": [
    {
      "ID": "OR:wt.associativity.EquivalenceLink:213450",
      "UpstreamPartId": "OR:wt.part.WTPart:213274",
      "DownstreamPartId": "OR:wt.part.WTPart:213408",
      "EquivalenceLinkId": "OR:wt.associativity.EquivalenceLink:213440",
      "IsEquivalenceLinkOutdated": false
    }
  "@PTC.AppliedContainerContext.LocalTimeZone": "Europe/Warsaw"
}
The attributes in the response for the PasteAsNewPart action are described in the following table:
Response Attribute
Description
ID
Attribute in a collection that returns the ID of the equivalent link between the upstream part and the new downstream equivalent part.
UpstreamPartId
Attribute in a collection that returns the ID of the upstream part which was copied.
DownstreamPartId
Attribute in a collection that returns the ID of the new downstream equivalent part.
EquivalenceLinkId
Attribute in a collection that returns the ID of the equivalence link between the upstream part and the new downstream equivalent part.
IsEquivalenceLinkOutdated
Attribute in a collection that indicates whether the equivalence link between the upstream part and the new downstream equivalent part is outdated or not.






Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > PasteAsNewBranch
PasteAsNewBranch
The PasteAsNewBranch action adds a copied part and its upstream structure as a new branch iteration to the downstream structure and creates new equivalence links to the upstream BOM. You can add the copied parts using inline or specific upstream and downstream navigation criteria.
You can also add the copied upstream part as a new branch iteration to the downstream structure in the context of change (change task or change notice).
The attributes in the request payload of the PasteAsNewBranch action are described in the following table:
Request Attribute
Description
Required
TargetRoot
Attribute to specify the root part of the downstream structure in the BOM transformer.
Yes
TargetPath
Attribute to specify the path of the downstream part under which you want to add the copied part.
Yes
SourceRoot
Attribute to specify the root part of the upstream structure in the BOM transformer.
Yes
SourcePart
Attribute in the TransformationDefinitions collection to specify the OID of the upstream part that you want to copy.
Yes
SourcePaths
Array type of attribute in the TransformationDefinitions collection to specify the path of the specified upstream part occurrence from its upstream root part.
Yes
TransformationOption
Attribute in the TransformationDefinitions collection to specify the child structure option such as Do not duplicate, Duplicate with propagating, or Duplicate without propagating for the transformation.
* 
TransformationOption is not applicable when you specify ExistingDownstreamAssociations.
Yes*
ReviseExistingDownstream
Flag in the TransformationDefinitions collection to specify whether you want to allow the existing downstream objects to be revised or not during the transformation.
* 
ReviseExistingDownstream is a required attribute when you specify ExistingDownstreamAssociations.
Yes*
ExistingDownstreamAssociations
Array type of attribute in the TransformationDefinitions collection to specify the OID of the equivalent link between a specified upstream part and its existing downstream equivalent object.
* 
TransformationEntity and its attributes are not applicable when you specify ExistingDownstreamAssociations for this action.
Optional
View
Attribute in the TransformationEntity entity type to specify the downstream view to be used in the transformation.
Yes
BOMType
Attribute in the TransformationEntity entity type to specify the type of downstream BOM being used.
Optional
AlternateBOM
Attribute in the TransformationEntity entity type to specify an alternate BOM for the transformation.
Optional
Context
Attribute in the TransformationEntity entity type to specify the context in which you want to create the downstream object.
* 
When not specified, the new downstream branch is created in one of the following contexts:
•Default context. This context is the same as that of the specified upstream part.
•The context set in the Associativity > Downstream Creation > Context preference in Windchill.
Optional
Folder
Attribute in the TransformationEntity entity type to specify the location in which you want to create the downstream object.
* 
When not specified, the new downstream object is created at one of the following locations:
•Default location. This location is the same as that of the specified upstream part.
•The location set in the Associativity > Downstream Creation > Location preference in Windchill.
Optional
DownstreamNavigationCriteria
Inline or specific navigation criteria applied in the downstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
UpstreamNavigationCriteria
Inline or specific navigation criteria applied in the upstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
ChangeOid
Attribute to specify the change task or change notice.
Optional
The request adds the specified upstream part and its structure as a new branch iteration in the downstream structure and creates new equivalence links between the downstream BOM and the upstream BOM.
POST  Windchill/servlet/odata/BomTransformation/PasteAsNewBranch
For example, the response to the request URI is as follows:
{
  "@odata.context": "$metadata#ExistingDownstreamAssociations",
  "value": [
    {
      "ID": "OR:wt.associativity.EquivalenceLink:213450",
      "UpstreamPartId": "OR:wt.part.WTPart:213274",
      "DownstreamPartId": "OR:wt.part.WTPart:213408",
      "EquivalenceLinkId": "OR:wt.associativity.EquivalenceLink:213440",
      "IsEquivalenceLinkOutdated": false
    }
  "@PTC.AppliedContainerContext.LocalTimeZone": "Europe/Warsaw"
}
The attributes in the response for the PasteAsNewBranch action are described in the following table:
Response Attribute
Description
ID
Attribute in a collection that returns the ID of the equivalent link between the upstream part and the new downstream equivalent part.
UpstreamPartId
Attribute in a collection that returns the ID of the upstream part which was copied.
DownstreamPartId
Attribute in a collection that returns the ID of the new downstream equivalent part.
EquivalenceLinkId
Attribute in a collection that returns the ID of the equivalence link between the upstream part and the new downstream equivalent part.
IsEquivalenceLinkOutdated
Attribute in a collection that indicates whether the equivalence link between the upstream part and the new downstream equivalent part is outdated or not.





Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > PasteSpecial
PasteSpecial
The PasteSpecial action validates the information that is copied on the upstream parts and pastes the information to the specified downstream part. The action pastes the information based on the configuration you specify in the automatic BOM transformation template. You can add the copied parts using inline or specific upstream and downstream navigation criteria.
You can also copy and paste using PasteSpecial in the context of change (change task or change notice).
* 
The action is not available in the Occurrence mode.
See the Configuring and Customizing Automatic BOM Transformation topic in the Windchill Help Center, for more information.
The attributes in the request payload of the PasteSpecial action are described in the following table:
Request Attribute
Description
Required
SourceRoot
Attribute in the DiscrepancyContext entity type to specify the root part of the upstream structure.
Yes
SourcePartSelection
Attribute in the DiscrepancyContext entity type to specify the parent Part from the upstream structure.
Alternatively, you can specify the Path of the parent part.
* 
SourcePartSelection is a collection for specifying either a single or multiple parent parts or their paths from an upstream structure.
Yes
UpstreamNavigationCriteria
Attribute in the DiscrepancyContext entity type to specify the navigation criteria applied in the upstream.
Yes
DownstreamNavigationCriteria
Attribute in the DiscrepancyContext entity type to specify the navigation criteria applied in the downstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
TargetRoot
Attribute in the DiscrepancyContext entity type to specify the root part of the downstream structure.
Yes
TargetPart
Attribute in the DiscrepancyContext entity type to specify the downstream part to which you want to paste the copied parts.
Alternatively, you can specify the path of the downstream part, that is, TargetPath to which you want to paste the copied parts.
Yes
ChangeOid
Attribute to specify the change task or change notice.
Optional
The request adds each specified upstream part as a new part under the specified downstream part based on the configuration in the automatic BOM transformation template. The request creates new equivalence links between the downstream BOM and the upstream BOM.
POST  Windchill/servlet/odata/BomTransformation/PasteSpecial
For example, the response to the request URI is as follows:
{
  "@odata.context": "$metadata#EquivalentUsageAssociations",
  "value": [
    {
      "UpstreamPartId": "OR:wt.part.WTPart:189986",
      "DownstreamPartId": "OR:wt.part.WTPart:189986",
      "EquivalenceLinkId": "OR:wt.associativity.EquivalenceLink:190604",
      "UsageLinkId": "OR:wt.part.WTPartUsageLink:190605"
    }
  ],
  "@PTC.AppliedContainerContext.LocalTimeZone": "Europe/Warsaw"
}
The attributes in the response for the PasteSpecial action are described in the following table:
Response Attribute
Description
UpstreamPartId
Attribute in a collection that returns the ID of the upstream part which was copied.
DownstreamPartId
Attribute in a collection that returns the ID of the downstream equivalent part.
EquivalenceLinkId
Attribute in a collection that returns the ID of the equivalence link between the upstream part and the downstream equivalent part.
UsageLinkId
Attribute in a collection that returns the ID of the usage link between the downstream target part and the added downstream part.




Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > DetectAndResolveDiscrepancies
DetectAndResolveDiscrepancies
The DetectAndResolveDiscrepancies action detects all discrepancies between the upstream and downstream parts in the BOM transformer and only resolves those that have the status as Auto. The action detects and resolves discrepancies for a single or multiple upstream parts using inline or specific upstream and downstream navigation criteria.
You can also detect and resolve the discrepancies in the context of change (change task or change notice).
* 
The action does not support detection of discrepancies for a resource structure.
See the Detecting and Resolving Discrepancies in the BOM Transformer topic in the Windchill Help Center, for more information.
The attributes in the request payload of the DetectAndResolveDiscrepancies action are described in the following table:
Request Attribute
Description
Required
CheckInDownstreamObject
Flag to specify whether the affected object in the downstream structure should be checked in after propagation or not after resolving discrepancies.
* 
The affected object in the downstream structure remains checked out after resolving discrepancies, if CheckInDownstreamObject is not specified.
Optional
SourceRoot
Attribute in the DiscrepancyContext entity type to specify the root part of the upstream structure.
Yes
SourcePartSelection
Attribute in the DiscrepancyContext entity type to specify the parent Part from the upstream structure.
Alternatively, you can specify the Path of the parent part.
* 
SourcePartSelection is a collection for specifying either a single or multiple upstream parent parts or their paths.
Yes
UpstreamNavigationCriteria
Attribute in the DiscrepancyContext entity type to specify the navigation criteria applied in the upstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
DownstreamNavigationCriteria
Attribute in the DiscrepancyContext entity type to specify the navigation criteria applied in the downstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
TargetRoot
Attribute in the DiscrepancyContext entity type to specify the root part of the downstream structure.
Optional
TargetPart
Attribute in the DiscrepancyContext entity type to specify the downstream part.
Optional
TargetPath
Attribute in the DiscrepancyContext entity type to specify the path of the specified downstream part.
Optional
UpstreamChangeOid
Attribute in the DiscrepancyContext entity type to specify the change object (change task or change notice) for detecting discrepancies when the relevant part is not iterated.
* 
*UpstreamChangeOid is a required attribute for detecting the discrepancies of Item Expressions or Plant Attributes criteria.
Yes*
ChangeOid
Attribute to specify the change task or change notice.
Optional
The action returns information for each resolved discrepancy that is detected with status as Auto. The action returns the following attributes for each specified upstream part for which the discrepancy was resolved:
•Identity
•Number
•Name
•Version
In the same set of attributes, it also returns the following attributes:
•Criteria of the detected discrepancy.
•CurrentValue
* 
The attribute is returned only for discrepancies of the Added Parts criteria.
•PreviousValue
* 
The attribute is returned only for discrepancies of the Removed Parts criteria.
•DownstreamParentPath, which is valid only for discrepancies of the Added Parts criteria.
•Status of the detected discrepancy.
•InternalMetadata, which is an internal encoded information.
The URI
POST  Windchill/servlet/odata/BomTransformation/DetectAndResolveDiscrepancies
returns the following response, for example:
{
  "@odata.context": "$metadata#DiscrepancyItems",
  "value": [
    {
      "Identity": "0000000305, ChildChild1, A.1 (Design)",
      "Number": "0000000305",
      "Name": "ChildChild1",
      "Version": "A.1 (Design)",
      "Criteria": "Removed Parts",
      "CurrentValue": "",
      "PreviousValue": "0000000302|0000000305",
      "DownstreamParentPath": [
        "0000000302"
      ],
      "Status": "Resolved",
      "InternalMetadata": "eyJTdGF0dXMiOiJBdXRvIiwiQ3VycmVudFZhbHVlSW50ZXJuYWxOYW1lIjoiIiwiRGlzY3JlcGFuY3lTdGF0dXNNZXNzYWdlIjoiIiwiZG93bnN0cmVhbVBhcmVudCI6IjAwMDAwMDAzMDJ8MDAwMDAwMDMwNSIsIlJlbW92ZWRDaGlsZCI6Ind0LnBhcnQuV1RQYXJ0OjI2NTkyMiIsInVwc3RyZWFtSW1wYWN0ZWRPYmplY3QiOiIiLCJEaXNjcmVwYW50UGF0aFJvb3QiOiJ3dC5wYXJ0LldUUGFydE1hc3RlcjoyNjU4NjciLCJDdXJyZW50VmFsdWUiOiIiLCJTdGF0dXNJbnRlcm5hbE5hbWUiOiJBVVRPIiwiUHJldmlvdXNWYWx1ZUludGVybmFsTmFtZSI6IjAwMDAwMDAzMDJ8MDAwMDAwMDMwNSIsIlByZXZpb3VzVmFsdWUiOiIwMDAwMDAwMzAyfDAwMDAwMDAzMDUiLCJUYXJnZXRQYXRocyI6W3siUGF0aCI6Ii85MTI4MjBhMy0yZjIwLTRhYWEtYjAxOS05M2I4NDNkNDQ0MzkiLCJSb290Ijoid3QucGFydC5XVFBhcnRNYXN0ZXI6MjY1ODY3IiwiTGVhZiI6Ind0LnBhcnQuV1RQYXJ0TWFzdGVyOjI2NTkxOSJ9XSwibnVtYmVyIjoiMDAwMDAwMDMwNSIsIlR5cGUiOiJSZW1vdmVkIFBhcnRzIiwiVHlwZUludGVybmFsTmFtZSI6IlJFTU9WRURfVVNBR0UiLCJEaXNjcmVwYW50UGF0aCI6Ii8iLCJWZXJzaW9uIjoiQS4xIChEZXNpZ24pIiwiaWRlbnRpdHkiOiIwMDAwMDAwMzA1LCBDaGlsZENoaWxkMSwgQS4xIChEZXNpZ24pIiwibmFtZSI6IkNoaWxkQ2hpbGQxIiwiUmVtb3ZlZFVzYWdlIjoid3QucGFydC5XVFBhcnRVc2FnZUxpbms6MjY1OTMxIiwiSWQiOiJmZWY0ZjI1MC00YzQ2LTQxYWItYjY5Mi02OTBkMDIyNWZkNDkiLCJpc0Rpc2NyZXBhbnRQYXRoSW5PY2N1cnJlbmNlTW9kZSI6ZmFsc2UsIkRvd25zdHJlYW1Db250ZXh0IjoiTWFudWZhY3R1cmluZyIsIkRpc2NyZXBhbnRQYXRoTGVhZiI6Ind0LnBhcnQuV1RQYXJ0TWFzdGVyOjI2NTg2NyJ9"
    }
  ],
  "@PTC.AppliedContainerContext.LocalTimeZone": "Europe/Warsaw"
}







Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > ResolveDiscrepancies
ResolveDiscrepancies
The ResolveDiscrepancies action resolves discrepancies of the Auto status from the detected discrepancies. The action resolves the Auto discrepancies using the set of attributes that the DetectDiscrepancies action returns in its response.
See the Detecting and Resolving Discrepancies in the BOM Transformer topic in the Windchill Help Center, for more information.
The attributes in the request payload of the ResolveDiscrepancies action are described in the following table:
Request Attribute
Description
Required
CheckInDownstreamObject
Flag to specify whether the affected object in the downstream structure should be checked in after propagation or not upon resolving discrepancies.
Optional
DiscrepancyItems
Array to specify a set of attributes for a discrepancy that you want to resolve.
The set of attributes returned for each detected discrepancy in the DetectDiscrepancies response is specified as an input in the ResolveDiscrepancies request payload.
* 
•The request resolves discrepancies of the Auto status only. If you specify a set of attributes for a discrepancy of status other than Auto, the request ignores those discrepancies.
•DownstreamParentPath is required as an input attribute to propagate a newly added upstream part either to a different parent in the downstream or to the downstream root part. This input attribute is valid only for resolving discrepancies that have the criteria as Added Parts, status as Auto, and a single downstream parent part.
Use a solidus (/) to specify the path for the downstream root part.
•If the value of DownstreamParentPath is returned as empty ("") in the DetectDiscrepancies response, then the downstream equivalent parent part is considered for resolving the discrepancy.
Yes
DiscrepancyContext
Entity type from the DetectDiscrepancies request payload which specifies the source root part (here, upstream root part), target root part (here, downstream root part), upstream navigation criteria, and downstream navigation criteria attributes.
* 
DiscrepancyContext reviews the detected discrepancies internally, before those are resolved.
Yes






Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > DetectDiscrepancies
DetectDiscrepancies
The DetectDiscrepancies action detects discrepancies of all statuses and criteria that exist between the upstream and downstream structures in the BOM transformer.
* 
The action does not support detection of discrepancies for a resource structure.
The action detects discrepancies for a single or multiple upstream parts using inline or specific upstream and downstream navigation criteria.
* 
PTC recommends that you specify the navigation criteria when you perform this action. If not specified, the System Default filter is applied.
See the Detecting and Resolving Discrepancies in the BOM Transformer topic in the Windchill Help Center, for more information.
The action returns information for each detected discrepancy. Each discrepancy returns the following attributes for each change made to the specified upstream parts:
•Identity
•Number
•Name
•Version
In the same set of attributes, it also returns the following attributes:
•Criteria of the detected discrepancy.
•CurrentValue
* 
The attribute is returned only for discrepancies of the Added Parts criteria.
•PreviousValue
* 
The attribute is returned only for discrepancies of the Removed Parts criteria.
•DownstreamParentPath, which is valid only for discrepancies of the Added Parts criteria.
•Status of the detected discrepancy.
•InternalMetadata, which is an internal encoded information.
The URI
POST  Windchill/servlet/odata/BomTransformation/DetectDiscrepancies
returns the following response, for example:
{
  "@odata.context": "$metadata#DiscrepancyItems",
  "value": [
    {
      "Identity": "0000000305, ChildChild1, A.1 (Design)",
      "Number": "0000000305",
      "Name": "ChildChild1",
      "Version": "A.1 (Design)",
      "Criteria": "Removed Parts",
      "CurrentValue": "",
      "PreviousValue": "0000000302|0000000305",
      "DownstreamParentPath": [
        ""
      ],
      "Status": "Auto",
      "InternalMetadata": "eyJTdGF0dXMiOiJBdXRvIiwiQ3VycmVudFZhbHVlSW50ZXJuYWxOYW1lIjoiIiwiRGlzY3JlcGFuY3lTdGF0dXNNZXNzYWdlIjoiIiwiZG93bnN0cmVhbVBhcmVudCI6IjAwMDAwMDAzMDJ8MDAwMDAwMDMwNSIsIlJlbW92ZWRDaGlsZCI6Ind0LnBhcnQuV1RQYXJ0OjI2NTkyMiIsInVwc3RyZWFtSW1wYWN0ZWRPYmplY3QiOiIiLCJEaXNjcmVwYW50UGF0aFJvb3QiOiJ3dC5wYXJ0LldUUGFydE1hc3RlcjoyNjU4NjciLCJDdXJyZW50VmFsdWUiOiIiLCJTdGF0dXNJbnRlcm5hbE5hbWUiOiJBVVRPIiwiUHJldmlvdXNWYWx1ZUludGVybmFsTmFtZSI6IjAwMDAwMDAzMDJ8MDAwMDAwMDMwNSIsIlByZXZpb3VzVmFsdWUiOiIwMDAwMDAwMzAyfDAwMDAwMDAzMDUiLCJUYXJnZXRQYXRocyI6W3siUGF0aCI6Ii85MTI4MjBhMy0yZjIwLTRhYWEtYjAxOS05M2I4NDNkNDQ0MzkiLCJSb290Ijoid3QucGFydC5XVFBhcnRNYXN0ZXI6MjY1ODY3IiwiTGVhZiI6Ind0LnBhcnQuV1RQYXJ0TWFzdGVyOjI2NTkxOSJ9XSwibnVtYmVyIjoiMDAwMDAwMDMwNSIsIlR5cGUiOiJSZW1vdmVkIFBhcnRzIiwiVHlwZUludGVybmFsTmFtZSI6IlJFTU9WRURfVVNBR0UiLCJEaXNjcmVwYW50UGF0aCI6Ii8iLCJWZXJzaW9uIjoiQS4xIChEZXNpZ24pIiwiaWRlbnRpdHkiOiIwMDAwMDAwMzA1LCBDaGlsZENoaWxkMSwgQS4xIChEZXNpZ24pIiwibmFtZSI6IkNoaWxkQ2hpbGQxIiwiUmVtb3ZlZFVzYWdlIjoid3QucGFydC5XVFBhcnRVc2FnZUxpbms6MjY1OTMxIiwiSWQiOiJmZWY0ZjI1MC00YzQ2LTQxYWItYjY5Mi02OTBkMDIyNWZkNDkiLCJpc0Rpc2NyZXBhbnRQYXRoSW5PY2N1cnJlbmNlTW9kZSI6ZmFsc2UsIkRvd25zdHJlYW1Db250ZXh0IjoiTWFudWZhY3R1cmluZyIsIkRpc2NyZXBhbnRQYXRoTGVhZiI6Ind0LnBhcnQuV1RQYXJ0TWFzdGVyOjI2NTg2NyJ9"
    }
  ],
  "@PTC.AppliedContainerContext.LocalTimeZone": "Europe/Warsaw"
}








Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > CreateEquivalenceUsageLinks
CreateEquivalenceUsageLinks
The CreateEquivalenceUsageLinks action creates equivalent usage links between upstream part usages and their respective equivalent downstream part usages. You can create a single or multiple equivalent usage links using inline or specific upstream and downstream navigation criteria.
See the Equivalent Usages and Creating an Equivalent Usage Link topics in the Windchill Help Center, for more information.
The attributes in the request payload of the CreateEquivalenceUsageLinks action are described in the following table:
Request Attribute
Description
Required
UpstreamRoot
Attribute in the EquivalenceUsageAssociation entity type to specify the OID of the upstream root part.
* 
EquivalenceUsageAssociation is a collection of a single or multiple sets of upstream part usages and their equivalent downstream part usages for which you want to create the equivalent usage links.
Yes
UpstreamPath
Attribute in the EquivalenceUsageAssociation entity type to specify the usage path between an upstream part and its upstream root part.
The attribute value combines the part ID and the path ID of the upstream part.
Yes
DownstreamRoot
Attribute in the EquivalenceUsageAssociation entity type to specify the OID of the equivalent downstream root part.
Yes
DownstreamPath
Attribute in the EquivalenceUsageAssociation entity type to specify the usage path between an equivalent downstream part and its downstream root part.
The attribute value combines the part ID and the path ID of the downstream part.
Yes
DownstreamNavigationCriteria
Inline or specific navigation criteria applied in the downstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
UpstreamNavigationCriteria
Inline or specific navigation criteria applied in the upstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
The following URI with expand returns information for each equivalence usage link that is created:
POST  Windchill/servlet/odata/BomTransformation/CreateEquivalenceUsageLinks?$expand=EquivalenceUsageLink
For example, the response is as follows:
{
  "@odata.context": "$metadata#EquivalenceUsageAssociations",
  "value": [
    {
      "DownstreamPath": "33b682f1-085c-4c3d-a535-63287e4dd993",
      "UpstreamPath": "23d3aab1-1932-4e0c-9980-af0121c09f10",
      "EquivalenceUsageLink": {
        "ID": "wt.associativity.PartUsagePath:195739",
        "DownstreamPath": "33b682f1-085c-4c3d-a535-63287e4dd993",
        "UpstreamPath": "23d3aab1-1932-4e0c-9980-af0121c09f10"
      }
    },
    {
      "DownstreamPath": "741a8cc1-3792-4388-b31a-f50a7b0777fe",
      "UpstreamPath": "23d3aab1-1932-4e0c-9980-af0121c09f10",
      "EquivalenceUsageLink": {
        "ID": "wt.associativity.PartUsagePath:195739",
        "DownstreamPath": "741a8cc1-3792-4388-b31a-f50a7b0777fe",
        "UpstreamPath": "23d3aab1-1932-4e0c-9980-af0121c09f10"
      }
    }
  ],
  "@PTC.AppliedContainerContext.LocalTimeZone": "Europe/Warsaw"
}












Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > RemoveEquivalenceLinks
RemoveEquivalenceLinks
The RemoveEquivalenceLinks action removes an equivalence link for the specified downstream part iteration. You can specify and remove a single or multiple sets of equivalent links and downstream parts.
You can also remove the equivalent links in the context of change (change task or change notice).











Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > UpdateToCurrentUpstreamEquivalents
UpdateToCurrentUpstreamEquivalents
The UpdateToCurrentUpstreamEquivalents action updates the out-of-date equivalent links between the downstream parts and an upstream iteration to which those are currently linked. The action updates the out-of-date equivalent links along with propagating the information from upstream to downstream. You can specify and update single or multiple downstream parts linked to an upstream iteration using inline or specific upstream and downstream navigation criteria. If you do not specify the navigation criteria, the System Default filter is applied.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
When an out-of-date equivalent link is updated, a new equivalent link is created to the latest valid upstream iteration.
You can also update the equivalent links in the context of change (change task or change notice).
* 
The action updates the out-of-date equivalent links for the specified downstream equivalent parts without resolving discrepancies.
To propagate information from upstream to downstream, the Ask To Carry Over During Create or Update preference is set to Yes in the Windchill UI and the DoCopyOver flag is specified as true in the request.
If the Ask To Carry Over During Create or Update preference is set to No and if the DoCopyOver flag is not provided in the request, then the flag is always true and the information is propagated from upstream to downstream.
If the Ask To Carry Over During Create or Update preference is set to Yes and if the DoCopyOver flag is not provided in the request, then the default value of the flag is false and no information is propagated from upstream to downstream.
See the Updating Equivalent Links in the Downstream Structure and Resolving Discrepancies topic in the Windchill Help Center, for more information.








Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > CreateEquivalenceLinks
CreateEquivalenceLinks
The CreateEquivalenceLinks action creates an equivalent link between the specified downstream part or assembly and the specified upstream part or assembly. You can create one or more equivalent links by specifying a single or multiple sets of downstream and upstream parts along with inline or specific upstream and downstream navigation criteria.
You can also create equivalent links in the context of change (change task or change notice).
See the Creating an Equivalent Link topic in the Windchill Help Center, for more information.
The attributes in the request payload of the CreateEquivalenceLinks action are described in the following table:
Request Attribute
Description
Required
UpstreamRoot
Attribute in the EquivalenceLinkAssociations entity type to specify the OID of the upstream root part.
* 
EquivalenceLinkAssociations is a collection of a single or multiple sets of downstream and upstream parts for which you want to create equivalent links.
Yes
UpstreamPath
Attribute in the EquivalenceLinkAssociations entity type to specify the path of an upstream part from its upstream root part.
The attribute value combines the part ID and the path ID of the upstream part.
* 
*UpstreamPath is a required attribute when you want to provide an upstream part from a structure for creating an equivalent link.
Yes*
DownstreamRoot
Attribute in the EquivalenceLinkAssociations entity type to specify the OID of the downstream root part.
Yes
DownstreamPath
Attribute in the EquivalenceLinkAssociations entity type to specify the path of a downstream part from its downstream root part.
The attribute value combines the part ID and the path ID of the downstream part.
* 
*DownstreamPath is a required attribute only when you want to specify a downstream part from a structure for creating an equivalent link.
Yes*
Description
Attribute in the EquivalenceLinkAssociations entity type to specify the description for the new equivalent link.
Optional
LinkType
Attribute in the EquivalenceLinkAssociations entity type to specify the type of the equivalent link that you want to create.
When the value is empty, an equivalent link is created.
When you specify AlternateEquivalent, an alternate equivalent link is created.
Optional
IsConsumable
Flag in the EquivalenceLinkAssociations entity type to specify whether you want to allow the equivalent link to be used as a context for creating occurrence links or not.
Yes
DoCopyOver
Flag in the EquivalenceLinkAssociations entity type to specify whether you want to allow the attributes from the upstream part to be used on the equivalent downstream part or not.
Yes
DownstreamNavigationCriteria
Inline or specific navigation criteria applied in the downstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
UpstreamNavigationCriteria
Inline or specific navigation criteria applied in the upstream.
* 
PTC recommends that you specify the navigation criteria when you perform this action.
If not specified, the System Default filter is applied.
Optional
ChangeOid
Attribute to specify the OID of a change task or change notice.
Optional
The following URI with expand returns information for each equivalence link that is created:
POST  Windchill/servlet/odata/BomTransformation/CreateEquivalenceLinks?$expand=EquivalenceLink
For example, the response is as follows:
{
  "@odata.context": "$metadata#EquivalenceLinkAssociations",
  "value": [
    {
      "ID": "wt.associativity.EquivalenceLink:561118",
      "DownstreamPath": "39a15ac0-658b-4b4d-aa35-91b79015bdf1",
      "UpstreamPath": "0152daed-0579-4698-91bb-a67e764b072d",
      "Description": "EquivalentLink1",
      "DoCopyOver": true,
      "IsConsumable": false,
      "LinkType": "",
      "UpstreamId": "wt.part.WTPart:560915",
      "DownstreamId": "wt.part.WTPart:561059",
      "EquivalenceLink": {
        "CreatedOn": "2022-08-23T10:30:46+02:00",
        "ID": "OR:wt.associativity.EquivalenceLink:561220",
        "LastModified": "2022-08-23T10:30:46+02:00",
        "Annotations": "0",
        "Consumable": false,
        "Description": "EquivalentLink1",
        "DownstreamContext": "Manufacturing",
        "EquivalenceIdentifier": "1642",
        "ObjectType": "Manufacturing Equivalence Link",
        "UpstreamContext": "Design"
      }
    }
  ],
  "@PTC.AppliedContainerContext.LocalTimeZone": "Europe/Warsaw"
}





Windchill REST Services Domain Capabilities > PTC Domains > PTC BOM Transformation Domain > Actions Available in the BOM Transformation Domain for Creating or Updating Downstream BOMs > GetExistingDownstreamObjects
GetExistingDownstreamObjects
The GetExistingDownstreamObjects action returns details about existing downstream equivalent objects for the upstream parts before transformation. It also returns details about whether the returned downstream equivalent objects are consumed or not and whether they are allowed to be revised or not upon transformation.
You can retrieve existing downstream objects for transformation actions such as NEW_BRANCH, NEW_PART, ADD_SAME, ALTERNATE, or SPLIT.
Transformation actions are actions that you intend to perform after you execute this action.
See the Adding Parts with Associative BOM Links topic in the Windchill Help Center, for more information.
The attributes in the request payload of the GetExistingDownstreamObjects action are described in the following table:
Request Attribute
Description
Required
DownstreamRoot
OID of the downstream equivalent root part.
Optional
DownstreamPathId
Path ID of the downstream equivalent part from the specified downstream root part. It provides information for executing following actions for the transformation: Paste as New Branch, Assemble As New Branch, Paste as New Part, or Assemble As New Branch.
Optional
DownstreamNavigationCriteria
Inline or specific navigation criteria applied in the downstream.
Yes
View
Attribute in the DownstreamBranchAttributes complex type to specify the downstream view to be used in the transformation.
Yes
BomType
Attribute in the DownstreamBranchAttributes complex type to specify the type of downstream BOM being used.
Optional
AlternateBOM
Attribute in the DownstreamBranchAttributes complex type to specify an alternate BOM for the transformation.
Optional
UpstreamRoot
OID of the upstream root part.
Optional
UpstreamNavigationCriteria
Inline or specific navigation criteria applied in the upstream.
Yes
TransformationActionType
Enum type attribute for the transformation action that you intend to perform after executing the GetExistingDownstreamObjects action.
The attribute supports following enum values: NEW_BRANCH, NEW_PART, ADD_SAME, ALTERNATE, SPLIT.
* 
See the EDM of the domain that is available at the metadata URL Windchill/servlet/odata/BomTransformation/$metadata for details.
Yes
UpstreamPart
Attribute in the ExistingDownstreamObjectQueryParams collection to specify the OID of the upstream part for which you want to get the existing downstream object.
* 
ExistingDownstreamObjectQueryParams is a collection of single or multiple upstream parts.
Yes
UpstreamPathId
Attribute in the ExistingDownstreamObjectQueryParams collection to specify the path ID of the specified upstream part from its root or parent part for which you want to get the existing downstream object.
* 
•For multiple upstream parts, the path ID specified for each upstream part corresponds to its path from the same upstream root part specified in the UpstreamRoot attribute.
•When a specified upstream part has multiple occurrences in a BOM structure, you can specify UpstreamPathId for the exact part occurrence for which you want to get the existing downstream object.
Optional
Number
Attribute in the ExistingDownstreamObjectQueryParams collection to specify the identification number of the specified upstream part, for which you want to get the existing downstream object, when transformation action type is specified as NEW_PART.
* 
*Number is a required attribute only when the Number field in the BOM Transformer UI in Windchill is editable.
Yes*
The request URI with expand returns all the information for each equivalent link between a specified upstream part and its existing downstream object. Additionally, the request returns the ID and Identity information for each of the following objects that are returned by the DownstreamObjects entity:
•UpstreamPart– specified upstream part
•DownstreamPart– existing downstream equivalent object for the specified upstream part
•EquivalenceLink– equivalence link
POST /Windchill/servlet/odata/BomTransformation/GetExistingDownstreamObjects?$expand=DownstreamObjects($expand=UpstreamPart($select=ID,Identity),DownstreamPart($select=ID,Identity),EquivalenceLink($select=ID,Annotations,DownstreamContext,UpstreamContext))
For example, the response to the request URI is an follows:
{
  "@odata.context": "http://<host>:<port>/Windchill/servlet/odata/v1/BomTransformation/$metadata#Collection(PTC.BomTransformation.ExistingDownstreamObjectsListItem)",
  "value": [
    {
      "DownstreamBranchAttributes": {
        "View": "Manufacturing",
        "BOMType": null,
        "AlternateBOM": null
      },
      "UpstreamPartId": "OR:wt.part.WTPart:213274",
      "UpstreamPathId": "2bbb6e8b-d89f-4e05-96aa-bb7bcc1e7bf0",
      "IsConsumed": false,
      "IsReviseAllowed": false,
      "DownstreamObjects": [
        {
          "ID": "OR:wt.associativity.EquivalenceLink:213440",
          "UpstreamPartId": "OR:wt.part.WTPart:213274",
          "DownstreamPartId": "OR:wt.part.WTPart:213408",
          "EquivalenceLinkId": "OR:wt.associativity.EquivalenceLink:213440",
          "IsEquivalenceLinkOutdated": false,
          "UpstreamPart": {
            "ID": "OR:wt.part.WTPart:213274",
            "Identity": "Part - 0000000126, s1, A.2 (Design)"
          },
          "DownstreamPart": {
            "ID": "OR:wt.part.WTPart:213408",
            "Identity": "Part - 0000000126, s1, A.1 (Manufacturing)"
          },
          "EquivalenceLink": {
            "ID": "OR:wt.associativity.EquivalenceLink:213440",
            "Annotations": "0",
            "DownstreamContext": "Manufacturing",
            "UpstreamContext": "Design"
          }
        }
      ]
    }
  ]
}
The attributes in the response for the GetExistingDownstreamObjects action are described in the following table:
Response Attribute
Description
IsReviseAllowed
Flag that indicates whether revision of the existing downstream objects is allowed or not for the transformation.
IsConsumed
Flag that returns whether the existing downstream objects are consumed or not.
UpstreamPathId
Returns the ID specified in the request for the upstream path for which you want to get the existing downstream object.
View
Attribute in the DownstreamBranchAttributes complex type that returns the downstream view specified in the request.
BomType
Attribute in the DownstreamBranchAttributes complex type that returns the type of downstream BOM specified in the request. When it is not specified in the input, it returns NULL.
AlternateBOM
Attribute in the DownstreamBranchAttributes complex type that returns the alternate BOM specified in the request. When it is not specified in the input, it returns NULL.
ID
Attribute in the DownstreamObjects collection that returns the ID of the equivalence link between the upstream object specified in the request and the existing downstream object.
* 
DownstreamObjects is a collection of single or multiple existing downstream equivalent objects.
UpstreamPartId
Attribute in the DownstreamObjects collection that returns the ID of the upstream part specified in the request.
DownstreamPartId
Attribute in the DownstreamObjects collection that returns the ID of the existing downstream equivalent object.
EquivalenceLinkId
Attribute in the DownstreamObjects collection that returns the ID of the equivalence link between the upstream part specified in the request and the existing downstream object.
IsEquivalenceLinkOutdated
Flag in the DownstreamObjects collection that indicates whether the equivalence link between the upstream part specified in the request and the existing downstream equivalent object is outdated or not.
UpstreamPart
Attribute in the DownstreamObjects collection that returns the information and attributes of each upstream part returned in the DownstreamObjects entity.
DownstreamPart
Attribute in the DownstreamObjects collection that returns the information and attributes of each existing downstream object returned in the DownstreamObjects entity.
EquivalenceLink
Attribute in the DownstreamObjects collection that returns the information and attributes of each equivalence link returned in the DownstreamObjects entity.






