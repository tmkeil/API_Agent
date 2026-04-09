PTC.Reporting:
/AllOpenChangeNoticess
/Containers
/Containers('{ContainerId}')



PTC.Workflow:
/WorkItems



PTC.ViewMgmt:
/Views
/Views('{ViewId}')







PTC.ChangeMgmt:
GET
/ChangeNotices
Get ChangeNotices

POST
/ChangeNotices
Create ChangeNotice

GET
/ChangeNotices('{ChangeNoticeId}')
Get ChangeNotice for a given ChangeNoticeId

PATCH
/ChangeNotices('{ChangeNoticeId}')
Update an existing ChangeNotice

GET
/ChangeNotices('{ChangeNoticeId}')/Attachments
Get ContentItem

POST
/ChangeNotices('{ChangeNoticeId}')/Attachments
Create ContentItem



PTC.Factory:
POST
/CheckInDocuments
Execute CheckInDocuments

POST
/CheckOutDocuments

GET
/Documents
Get Documents


GET
/Documents('{DocumentId}')
Get Document for a given DocumentId


DELETE
/Documents('{DocumentId}')
DeleteDocument


PATCH
/Documents('{DocumentId}')
Update an existing Document







PTC.DocMgmt:
POST
/CheckInDocuments
Execute CheckInDocuments


POST
/CheckOutDocuments
Execute CheckOutDocuments


POST
/CreateDocuments
Execute CreateDocuments


POST
/DeleteDocuments
Execute DeleteDocuments


GET
/Documents
Get Documents


POST
/Documents
Create Document



PTC.DataAdmin:
GET
/Containers
Get Containers


GET
/Containers('{ContainerId}')
Get Container for a given ContainerId




PTC.ProdMgmt:
POST
/CheckInParts
Execute CheckInParts


POST
/CheckOutParts
Execute CheckOutParts


POST
/CreateAssociations
Create Single or Multiple Associations between Parts and CAD documents.


POST
/CreateParts
Execute CreateParts


GET
/Parts
Get Parts


POST
/Parts
Create Part


GET
/Parts('{PartId}')
Get Part for a given PartId


DELETE
/Parts('{PartId}')
DeletePart


PATCH
/Parts('{PartId}')
Update an existing Part


GET
/Parts('{PartId}')/Attachments
Get ContentItem


POST
/Parts('{PartId}')/Attachments
Create ContentItem


GET
/Parts('{PartId}')/Attachments('{ContentItemId}')
Get ContentItem for a given ContentItemId


DELETE
/Parts('{PartId}')/Attachments('{ContentItemId}')
Delete an existing ContentItem


PATCH
/Parts('{PartId}')/Attachments('{ContentItemId}')
Update an existing ContentItem


GET
/Parts('{PartId}')/BAL_DOWNSTREAMNav
Get ObjectReferenceable


GET
/Parts('{PartId}')/BAL_DOWNSTREAMNav('{ObjectReferenceableId}')
Get ObjectReferenceable for a given ObjectReferenceableId


DELETE
/Parts('{PartId}')/BAL_DOWNSTREAMNav('{ObjectReferenceableId}')
Delete an existing ObjectReferenceable


PATCH
/Parts('{PartId}')/BAL_DOWNSTREAMNav('{ObjectReferenceableId}')
Update an existing ObjectReferenceable


GET
/Parts('{PartId}')/DescribedBy
Get PartDescribeLink


POST
/Parts('{PartId}')/DescribedBy
Create PartDescribeLink


GET
/Parts('{PartId}')/DescribedBy('{PartDescribeLinkId}')
Get PartDescribeLink for a given PartDescribeLinkId


DELETE
/Parts('{PartId}')/DescribedBy('{PartDescribeLinkId}')
Delete an existing PartDescribeLink


PATCH
/Parts('{PartId}')/DescribedBy('{PartDescribeLinkId}')
Update an existing PartDescribeLink


GET
/Parts('{PartId}')/DescribedBy('{PartDescribeLinkId}')/DescribedBy
Get Document


GET
/Parts('{PartId}')/DescribedBy('{PartDescribeLinkId}')/Describes
Get Part


GET
/Parts('{PartId}')/DownstreamEquivalanceLinks
Get EquivalenceLink


GET
/Parts('{PartId}')/DownstreamEquivalanceLinks('{EquivalenceLinkId}')
Get EquivalenceLink for a given EquivalenceLinkId


GET
/Parts('{PartId}')/DownstreamEquivalanceLinks('{EquivalenceLinkId}')/Downstream
Get WindchillEntity


POST
/ReviseParts
Execute ReviseParts


GET
/Parts(@PartId)/PTC.ProdMgmt.GetValidStateTransitions()
Execute GetValidStateTransitions


GET
/Parts(@PartId)/PTC.ProdMgmt.IsCheckoutAllowed()
Execute IsCheckoutAllowed


GET
/Parts/PTC.ProdMgmt.BAL_AUX_PART
Get Parts of type BAL_AUX_PART


GET
/Parts/PTC.ProdMgmt.BAL_CERT_COLLECTION_PART
Get Parts of type BAL_CERT_COLLECTION_PART


GET
/Parts/PTC.ProdMgmt.BAL_CERT_PART
Get Parts of type BAL_CERT_PART


GET
/Parts/PTC.ProdMgmt.BAL_COLLECTION_PART
Get Parts of type BAL_COLLECTION_PART


GET
/Parts/PTC.ProdMgmt.BAL_DMY_PART
Get Parts of type BAL_DMY_PART


GET
/Parts/PTC.ProdMgmt.BAL_ENC_DOC_PART
Get Parts of type BAL_ENC_DOC_PART


GET
/Parts/PTC.ProdMgmt.BAL_EQUIPMENT_PART
Get Parts of type BAL_EQUIPMENT_PART


GET
/Parts/PTC.ProdMgmt.BAL_INT_DOC_PART
Get Parts of type BAL_INT_DOC_PART


GET
/Parts/PTC.ProdMgmt.BAL_MANUFACTURER_PART
Get Parts of type BAL_MANUFACTURER_PART


GET
/Parts/PTC.ProdMgmt.BAL_MECHATRONIC_PART
Get Parts of type BAL_MECHATRONIC_PART


GET
/Parts/PTC.ProdMgmt.BAL_PACKAGE_PART
Get Parts of type BAL_PACKAGE_PART


GET
/Parts/PTC.ProdMgmt.BAL_PRODUCT_PART
Get Parts of type BAL_PRODUCT_PART


GET
/Parts/PTC.ProdMgmt.BAL_RAWMATERIAL
Get Parts of type BAL_RAWMATERIAL


GET
/Parts/PTC.ProdMgmt.BAL_SAP_PRODUCT_PART
Get Parts of type BAL_SAP_PRODUCT_PART


GET
/Parts/PTC.ProdMgmt.BAL_SOFTWARE_PART
Get Parts of type BAL_SOFTWARE_PART


GET
/Parts/PTC.ProdMgmt.BAL_SOURCING_PART
Get Parts of type BAL_SOURCING_PART


GET
/Parts/PTC.ProdMgmt.ElectricalPart
Get Parts of type ElectricalPart


GET
/Parts('{PartId}')/UpstreamEquivalanceLinks
Get EquivalenceLink


GET
/Parts('{PartId}')/UpstreamEquivalanceLinks('{EquivalenceLinkId}')
Get EquivalenceLink for a given EquivalenceLinkId


GET
/Parts('{PartId}')/UpstreamEquivalanceLinks('{EquivalenceLinkId}')/Downstream
Get WindchillEntity


GET
/Parts('{PartId}')/UpstreamEquivalanceLinks('{EquivalenceLinkId}')/Downstream('{WindchillEntityId}')
Get WindchillEntity for a given WindchillEntityId


GET
/Parts('{PartId}')/UpstreamEquivalanceLinks('{EquivalenceLinkId}')/Upstream
Get WindchillEntity


GET
/Parts('{PartId}')/UpstreamEquivalanceLinks('{EquivalenceLinkId}')/Upstream('{WindchillEntityId}')
Get WindchillEntity for a given WindchillEntityId


GET
/Parts('{PartId}')/UsedBy
Get Part


GET
/Parts('{PartId}')/UsedBy('{UsedById}')
Get Part for a given UsedById


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/AXLEntries
Get AXLEntry


POST
/Parts('{PartId}')/UsedBy('{UsedById}')/AXLEntries
Create AXLEntry


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/AXLEntries('{AXLEntryId}')
Get AXLEntry for a given AXLEntryId


DELETE
/Parts('{PartId}')/UsedBy('{UsedById}')/AXLEntries('{AXLEntryId}')
Delete an existing AXLEntry


PATCH
/Parts('{PartId}')/UsedBy('{UsedById}')/AXLEntries('{AXLEntryId}')
Update an existing AXLEntry


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Alternates
Get PartAlternateLink


POST
/Parts('{PartId}')/UsedBy('{UsedById}')/Alternates
Create PartAlternateLink


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Alternates('{PartAlternateLinkId}')
Get PartAlternateLink for a given PartAlternateLinkId


DELETE
/Parts('{PartId}')/UsedBy('{UsedById}')/Alternates('{PartAlternateLinkId}')
Delete an existing PartAlternateLink


PATCH
/Parts('{PartId}')/UsedBy('{UsedById}')/Alternates('{PartAlternateLinkId}')
Update an existing PartAlternateLink


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/AssignedOptionSet
Get OptionSet


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Attachments
Get ContentItem


POST
/Parts('{PartId}')/UsedBy('{UsedById}')/Attachments
Create ContentItem


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Attachments('{ContentItemId}')
Get ContentItem for a given ContentItemId


DELETE
/Parts('{PartId}')/UsedBy('{UsedById}')/Attachments('{ContentItemId}')
Delete an existing ContentItem


PATCH
/Parts('{PartId}')/UsedBy('{UsedById}')/Attachments('{ContentItemId}')
Update an existing ContentItem


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/BAL_DOWNSTREAMNav
Get ObjectReferenceable


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/BAL_DOWNSTREAMNav('{ObjectReferenceableId}')
Get ObjectReferenceable for a given ObjectReferenceableId


DELETE
/Parts('{PartId}')/UsedBy('{UsedById}')/BAL_DOWNSTREAMNav('{ObjectReferenceableId}')
Delete an existing ObjectReferenceable


PATCH
/Parts('{PartId}')/UsedBy('{UsedById}')/BAL_DOWNSTREAMNav('{ObjectReferenceableId}')
Update an existing ObjectReferenceable


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Context
Get Container


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Creator
Get User


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/DescribedBy
Get PartDescribeLink


POST
/Parts('{PartId}')/UsedBy('{UsedById}')/DescribedBy
Create PartDescribeLink


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/DescribedBy('{PartDescribeLinkId}')
Get PartDescribeLink for a given PartDescribeLinkId


DELETE
/Parts('{PartId}')/UsedBy('{UsedById}')/DescribedBy('{PartDescribeLinkId}')
Delete an existing PartDescribeLink


PATCH
/Parts('{PartId}')/UsedBy('{UsedById}')/DescribedBy('{PartDescribeLinkId}')
Update an existing PartDescribeLink


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/DownstreamEquivalanceLinks
Get EquivalenceLink


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/DownstreamEquivalanceLinks('{EquivalenceLinkId}')
Get EquivalenceLink for a given EquivalenceLinkId


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Effectivities
Get Effectivity


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Effectivities('{EffectivityId}')
Get Effectivity for a given EffectivityId


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/ExtendedData
Get ExtendedData


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/ExtendedData('{ExtendedDataId}')
Get ExtendedData for a given ExtendedDataId


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Folder
Get Folder


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/MadeFromLink
Get RawMaterialLink


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/MadeFromLink('{RawMaterialLinkId}')
Get RawMaterialLink for a given RawMaterialLinkId


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Modifier
Get User


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/ModuleVariantInformationLinks
Get ModuleVariantInformationLink


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/ModuleVariantInformationLinks('{ModuleVariantInformationLinkId}')
Get ModuleVariantInformationLink for a given ModuleVariantInformationLinkId


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Organization
Get Organization


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/PartDocAssociations
Get PartDocAssociation


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/PartDocAssociations('{PartDocAssociationId}')
Get PartDocAssociation for a given PartDocAssociationId


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/PartMadeFrom
Get Part


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/PartMadeFrom('{PartMadeFromId}')
Get Part for a given PartMadeFromId


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/References
Get PartReferenceLink


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/References('{PartReferenceLinkId}')
Get PartReferenceLink for a given PartReferenceLinkId


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Representations
Get Representation


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Representations('{RepresentationId}')
Get Representation for a given RepresentationId


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Revisions
Get Part


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Revisions('{RevisionsId}')
Get Part for a given RevisionsId


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Substitutes
Get PartSubstituteLink


POST
/Parts('{PartId}')/UsedBy('{UsedById}')/Substitutes
Create PartSubstituteLink


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Substitutes('{PartSubstituteLinkId}')
Get PartSubstituteLink for a given PartSubstituteLinkId


DELETE
/Parts('{PartId}')/UsedBy('{UsedById}')/Substitutes('{PartSubstituteLinkId}')
Delete an existing PartSubstituteLink


PATCH
/Parts('{PartId}')/UsedBy('{UsedById}')/Substitutes('{PartSubstituteLinkId}')
Update an existing PartSubstituteLink


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/UpstreamEquivalanceLinks
Get EquivalenceLink


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/UpstreamEquivalanceLinks('{EquivalenceLinkId}')
Get EquivalenceLink for a given EquivalenceLinkId


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/UsedBy
Get Part


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/UsedBy('{UsedById}')
Get Part for a given UsedById


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Uses
Get PartUse


POST
/Parts('{PartId}')/UsedBy('{UsedById}')/Uses
Create PartUse


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Uses('{PartUseId}')
Get PartUse for a given PartUseId


DELETE
/Parts('{PartId}')/UsedBy('{UsedById}')/Uses('{PartUseId}')
Delete an existing PartUse


PATCH
/Parts('{PartId}')/UsedBy('{UsedById}')/Uses('{PartUseId}')
Update an existing PartUse


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Versions
Get Part


GET
/Parts('{PartId}')/UsedBy('{UsedById}')/Versions('{VersionsId}')
Get Part for a given VersionsId


GET
/Parts('{PartId}')/Uses
Get PartUse


POST
/Parts('{PartId}')/Uses
Create PartUse


GET
/Parts('{PartId}')/Uses('{PartUseId}')
Get PartUse for a given PartUseId


DELETE
/Parts('{PartId}')/Uses('{PartUseId}')
Delete an existing PartUse


PATCH
/Parts('{PartId}')/Uses('{PartUseId}')
Update an existing PartUse


GET
/Parts('{PartId}')/Uses('{PartUseId}')/Occurrences
Get UsageOccurrence


POST
/Parts('{PartId}')/Uses('{PartUseId}')/Occurrences
Create UsageOccurrence


GET
/Parts('{PartId}')/Uses('{PartUseId}')/Occurrences('{UsageOccurrenceId}')
Get UsageOccurrence for a given UsageOccurrenceId


DELETE
/Parts('{PartId}')/Uses('{PartUseId}')/Occurrences('{UsageOccurrenceId}')
Delete an existing UsageOccurrence


PATCH
/Parts('{PartId}')/Uses('{PartUseId}')/Occurrences('{UsageOccurrenceId}')
Update an existing UsageOccurrence


GET
/Parts('{PartId}')/Uses('{PartUseId}')/UsedBy
Get Part


GET
/Parts('{PartId}')/Uses('{PartUseId}')/Uses
Get Part


GET
/Parts('{PartId}')/Versions
Get Part


GET
/Parts('{PartId}')/Versions('{VersionsId}')
Get Part for a given VersionsId


GET
/Parts('{PartId}')/Versions('{VersionsId}')/AXLEntries
Get AXLEntry


POST
/Parts('{PartId}')/Versions('{VersionsId}')/AXLEntries
Create AXLEntry


GET
/Parts('{PartId}')/Versions('{VersionsId}')/AXLEntries('{AXLEntryId}')
Get AXLEntry for a given AXLEntryId


DELETE
/Parts('{PartId}')/Versions('{VersionsId}')/AXLEntries('{AXLEntryId}')
Delete an existing AXLEntry


PATCH
/Parts('{PartId}')/Versions('{VersionsId}')/AXLEntries('{AXLEntryId}')
Update an existing AXLEntry


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Alternates
Get PartAlternateLink


POST
/Parts('{PartId}')/Versions('{VersionsId}')/Alternates
Create PartAlternateLink


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Alternates('{PartAlternateLinkId}')
Get PartAlternateLink for a given PartAlternateLinkId


DELETE
/Parts('{PartId}')/Versions('{VersionsId}')/Alternates('{PartAlternateLinkId}')
Delete an existing PartAlternateLink


PATCH
/Parts('{PartId}')/Versions('{VersionsId}')/Alternates('{PartAlternateLinkId}')
Update an existing PartAlternateLink


GET
/Parts('{PartId}')/Versions('{VersionsId}')/AssignedOptionSet
Get OptionSet


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Attachments
Get ContentItem


POST
/Parts('{PartId}')/Versions('{VersionsId}')/Attachments
Create ContentItem


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Attachments('{ContentItemId}')
Get ContentItem for a given ContentItemId


DELETE
/Parts('{PartId}')/Versions('{VersionsId}')/Attachments('{ContentItemId}')
Delete an existing ContentItem


PATCH
/Parts('{PartId}')/Versions('{VersionsId}')/Attachments('{ContentItemId}')
Update an existing ContentItem


GET
/Parts('{PartId}')/Versions('{VersionsId}')/BAL_DOWNSTREAMNav
Get ObjectReferenceable


GET
/Parts('{PartId}')/Versions('{VersionsId}')/BAL_DOWNSTREAMNav('{ObjectReferenceableId}')
Get ObjectReferenceable for a given ObjectReferenceableId


DELETE
/Parts('{PartId}')/Versions('{VersionsId}')/BAL_DOWNSTREAMNav('{ObjectReferenceableId}')
Delete an existing ObjectReferenceable


PATCH
/Parts('{PartId}')/Versions('{VersionsId}')/BAL_DOWNSTREAMNav('{ObjectReferenceableId}')
Update an existing ObjectReferenceable


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Context
Get Container


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Creator
Get User


GET
/Parts('{PartId}')/Versions('{VersionsId}')/DescribedBy
Get PartDescribeLink


POST
/Parts('{PartId}')/Versions('{VersionsId}')/DescribedBy
Create PartDescribeLink


GET
/Parts('{PartId}')/Versions('{VersionsId}')/DescribedBy('{PartDescribeLinkId}')
Get PartDescribeLink for a given PartDescribeLinkId


DELETE
/Parts('{PartId}')/Versions('{VersionsId}')/DescribedBy('{PartDescribeLinkId}')
Delete an existing PartDescribeLink


PATCH
/Parts('{PartId}')/Versions('{VersionsId}')/DescribedBy('{PartDescribeLinkId}')
Update an existing PartDescribeLink


GET
/Parts('{PartId}')/Versions('{VersionsId}')/DownstreamEquivalanceLinks
Get EquivalenceLink


GET
/Parts('{PartId}')/Versions('{VersionsId}')/DownstreamEquivalanceLinks('{EquivalenceLinkId}')
Get EquivalenceLink for a given EquivalenceLinkId


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Effectivities
Get Effectivity


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Effectivities('{EffectivityId}')
Get Effectivity for a given EffectivityId


GET
/Parts('{PartId}')/Versions('{VersionsId}')/ExtendedData
Get ExtendedData


GET
/Parts('{PartId}')/Versions('{VersionsId}')/ExtendedData('{ExtendedDataId}')
Get ExtendedData for a given ExtendedDataId


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Folder
Get Folder


GET
/Parts('{PartId}')/Versions('{VersionsId}')/MadeFromLink
Get RawMaterialLink


GET
/Parts('{PartId}')/Versions('{VersionsId}')/MadeFromLink('{RawMaterialLinkId}')
Get RawMaterialLink for a given RawMaterialLinkId


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Modifier
Get User


GET
/Parts('{PartId}')/Versions('{VersionsId}')/ModuleVariantInformationLinks
Get ModuleVariantInformationLink


GET
/Parts('{PartId}')/Versions('{VersionsId}')/ModuleVariantInformationLinks('{ModuleVariantInformationLinkId}')
Get ModuleVariantInformationLink for a given ModuleVariantInformationLinkId


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Organization
Get Organization


GET
/Parts('{PartId}')/Versions('{VersionsId}')/PartDocAssociations
Get PartDocAssociation


GET
/Parts('{PartId}')/Versions('{VersionsId}')/PartDocAssociations('{PartDocAssociationId}')
Get PartDocAssociation for a given PartDocAssociationId


GET
/Parts('{PartId}')/Versions('{VersionsId}')/PartMadeFrom
Get Part


GET
/Parts('{PartId}')/Versions('{VersionsId}')/PartMadeFrom('{PartMadeFromId}')
Get Part for a given PartMadeFromId


GET
/Parts('{PartId}')/Versions('{VersionsId}')/References
Get PartReferenceLink


GET
/Parts('{PartId}')/Versions('{VersionsId}')/References('{PartReferenceLinkId}')
Get PartReferenceLink for a given PartReferenceLinkId


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Representations
Get Representation


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Representations('{RepresentationId}')
Get Representation for a given RepresentationId


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Revisions
Get Part


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Revisions('{RevisionsId}')
Get Part for a given RevisionsId


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Substitutes
Get PartSubstituteLink


POST
/Parts('{PartId}')/Versions('{VersionsId}')/Substitutes
Create PartSubstituteLink


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Substitutes('{PartSubstituteLinkId}')
Get PartSubstituteLink for a given PartSubstituteLinkId


DELETE
/Parts('{PartId}')/Versions('{VersionsId}')/Substitutes('{PartSubstituteLinkId}')
Delete an existing PartSubstituteLink


PATCH
/Parts('{PartId}')/Versions('{VersionsId}')/Substitutes('{PartSubstituteLinkId}')
Update an existing PartSubstituteLink


GET
/Parts('{PartId}')/Versions('{VersionsId}')/UpstreamEquivalanceLinks
Get EquivalenceLink


GET
/Parts('{PartId}')/Versions('{VersionsId}')/UpstreamEquivalanceLinks('{EquivalenceLinkId}')
Get EquivalenceLink for a given EquivalenceLinkId


GET
/Parts('{PartId}')/Versions('{VersionsId}')/UsedBy
Get Part


GET
/Parts('{PartId}')/Versions('{VersionsId}')/UsedBy('{UsedById}')
Get Part for a given UsedById


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Uses
Get PartUse


POST
/Parts('{PartId}')/Versions('{VersionsId}')/Uses
Create PartUse


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Uses('{PartUseId}')
Get PartUse for a given PartUseId


DELETE
/Parts('{PartId}')/Versions('{VersionsId}')/Uses('{PartUseId}')
Delete an existing PartUse


PATCH
/Parts('{PartId}')/Versions('{VersionsId}')/Uses('{PartUseId}')
Update an existing PartUse


GET
/Parts('{PartId}')/Versions('{VersionsId}')/Versions
Get Part