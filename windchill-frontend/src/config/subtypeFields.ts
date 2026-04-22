/**
 * Subtype-specific field definitions for the Create Part form.
 *
 * Derived from OData $metadata (ProdMgmt v6).
 * Only writable fields are included (no ReadOnly, no via-action, no Collection types).
 * BALCLASSIFICATIONBINDINGWTPART is excluded (already handled in the main form).
 */

export type FieldType = 'text' | 'boolean' | 'number' | 'date'

export type FieldGroup = 'attributes' | 'dimensions' | 'sap' | 'legacy'

export interface FieldDef {
  label: string
  type: FieldType
  group: FieldGroup
}

/* ── Global field registry ─────────────────────────────────── */

export const FIELD_REGISTRY: Record<string, FieldDef> = {
  // ── Attributes ──
  BALADDITIV1:                          { label: 'Additive 1',                          type: 'text',    group: 'attributes' },
  BALADDITIV1PERCENTAGE:                { label: 'Additive 1 (%)',                      type: 'text',    group: 'attributes' },
  BALADDITIV2:                          { label: 'Additive 2',                          type: 'text',    group: 'attributes' },
  BALADDITIV2PERCENTAGE:                { label: 'Additive 2 (%)',                      type: 'text',    group: 'attributes' },
  BALADDITIV3:                          { label: 'Additive 3',                          type: 'text',    group: 'attributes' },
  BALADDITIV3PERCENTAGE:                { label: 'Additive 3 (%)',                      type: 'text',    group: 'attributes' },
  BALALTIUMCATEGORY:                    { label: 'Altium Category',                     type: 'text',    group: 'attributes' },
  BALALTIUMCLEANUP:                     { label: 'Altium Cleanup',                      type: 'text',    group: 'attributes' },
  BALAUTOMATICEXCHANGE:                 { label: 'Automatic Exchange',                  type: 'text',    group: 'attributes' },
  BALAUTOMATICPACKING:                  { label: 'Automatic Packing',                   type: 'boolean', group: 'attributes' },
  BALAZUREMESSAGE:                      { label: 'Azure Message',                       type: 'text',    group: 'attributes' },
  BALBYAPPROVALLIMITEDCHARACTERISTICS:  { label: 'By Approval Limited Characteristics', type: 'text',    group: 'attributes' },
  BALCUSTOMERPROVIDEDPART:              { label: 'Customer Provided Part',               type: 'boolean', group: 'attributes' },
  BALCUSTOMERSPECIFIC:                  { label: 'Customer Specific',                    type: 'text',    group: 'attributes' },
  BALDEFINEDSTORECONDITION:             { label: 'Defined Store Condition',              type: 'boolean', group: 'attributes' },
  BALDOCUMENTATIONTYPE:                 { label: 'Documentation Type',                   type: 'text',    group: 'attributes' },
  BALDOCUMENTDOCTYPE:                   { label: 'Document Doc Type',                    type: 'text',    group: 'attributes' },
  BALDOCUMENTSUBTYPE:                   { label: 'Document Subtype',                     type: 'text',    group: 'attributes' },
  BALERPmigrationdate:                  { label: 'ERP Migration Date',                   type: 'date',    group: 'legacy' },
  BALFORMATCHCODE:                      { label: 'Format/CH Code',                       type: 'text',    group: 'attributes' },
  BALINTERNALTRANSPORTPACKING:          { label: 'Internal Transport Packing',           type: 'boolean', group: 'attributes' },
  BALISVARIANT:                         { label: 'Is Variant',                           type: 'boolean', group: 'attributes' },
  BALLegacyERPname:                     { label: 'Legacy ERP Name',                      type: 'text',    group: 'legacy' },
  BALLegacyERPnumber:                   { label: 'Legacy ERP Number',                    type: 'text',    group: 'legacy' },
  BALLegacyERPsource:                   { label: 'Legacy ERP Source',                    type: 'text',    group: 'legacy' },
  BALLegacyERPstate:                    { label: 'Legacy ERP State',                     type: 'text',    group: 'legacy' },
  BALLegacyERPversion:                  { label: 'Legacy ERP Version',                   type: 'text',    group: 'legacy' },
  BALMATERIAL:                          { label: 'Material',                             type: 'text',    group: 'attributes' },
  BALNOEXPIRATION:                      { label: 'No Expiration',                        type: 'boolean', group: 'attributes' },
  BALNOTSUITABLENEWDESIGN:              { label: 'Not Suitable for New Design',          type: 'boolean', group: 'attributes' },
  BALPRINTINGGOOD:                      { label: 'Printing Good',                        type: 'boolean', group: 'attributes' },
  BALPROCESSTOKEN:                      { label: 'Process Token',                        type: 'text',    group: 'attributes' },
  BALQAAPPROVED:                        { label: 'QA Approved',                          type: 'boolean', group: 'attributes' },
  BALREVIEWTILL:                        { label: 'Review Till',                          type: 'date',    group: 'attributes' },
  BALSERIALNUMBER:                      { label: 'Serial Number',                        type: 'text',    group: 'attributes' },
  BALSOFTWAREGUID:                      { label: 'Software GUID',                        type: 'text',    group: 'attributes' },
  BALSPECIALOPERATIONALCONDITIONS:      { label: 'Special Operational Conditions',       type: 'boolean', group: 'attributes' },
  BALSPECIALOPERATIONALCONDITIONSTEXT:  { label: 'Special Operational Conditions Text',  type: 'text',    group: 'attributes' },
  BALSTORAGECONDITIONTEXT:              { label: 'Storage Condition Text',               type: 'text',    group: 'attributes' },
  BALSURFACECOLOUR:                     { label: 'Surface Colour',                       type: 'text',    group: 'attributes' },
  BALSURFACEFINISH:                     { label: 'Surface Finish',                       type: 'text',    group: 'attributes' },
  BALSURFACEHARDNESS:                   { label: 'Surface Hardness',                     type: 'text',    group: 'attributes' },
  BALSURFACEOTHER:                      { label: 'Surface Other',                        type: 'text',    group: 'attributes' },
  BALSURFACETHICKNESS:                  { label: 'Surface Thickness',                    type: 'text',    group: 'attributes' },
  BALUNIQUESOFTWAREIDENTIFIER:          { label: 'Unique Software Identifier',           type: 'text',    group: 'attributes' },
  BALUPSTREAMSOURCE:                    { label: 'Upstream Source',                       type: 'text',    group: 'attributes' },
  BALVALIDFROM:                         { label: 'Valid From',                            type: 'date',    group: 'attributes' },
  BALVALIDITYPERIOD:                    { label: 'Validity Period',                       type: 'date',    group: 'attributes' },
  BALVERSION:                           { label: 'Version',                              type: 'text',    group: 'attributes' },

  // ── Dimensions & Weight ──
  BALOBJECTDIMENSION1:                  { label: 'Object Dimension 1',                   type: 'number',  group: 'dimensions' },
  BALOBJECTDIMENSION2:                  { label: 'Object Dimension 2',                   type: 'number',  group: 'dimensions' },
  BALOBJECTDIMENSION3:                  { label: 'Object Dimension 3',                   type: 'number',  group: 'dimensions' },
  BALOBJECTDIMENSION4:                  { label: 'Object Dimension 4',                   type: 'number',  group: 'dimensions' },
  BALWEIGHTBRUTTO:                      { label: 'Weight Brutto',                        type: 'number',  group: 'dimensions' },
  BALWEIGHTMODELED:                     { label: 'Weight Modeled',                       type: 'number',  group: 'dimensions' },
  BALWEIGHTNETTO:                       { label: 'Weight Netto',                         type: 'number',  group: 'dimensions' },

  // ── SAP ──
  BALSAPALLOCATEDPLANT:                 { label: 'SAP Allocated Plant',                  type: 'text',    group: 'sap' },
  BALSAPMATCOMPLIANCESTATUS:            { label: 'SAP Mat Compliance Status',             type: 'text',    group: 'sap' },
  BALSAPMSTAV:                          { label: 'SAP MSTAV',                            type: 'text',    group: 'sap' },
}

/* ── Group display metadata ───────────────────────────────── */

export const GROUP_LABELS: Record<FieldGroup, string> = {
  attributes: 'Subtype Attributes',
  dimensions: 'Dimensions & Weight',
  sap:        'SAP',
  legacy:     'Legacy ERP',
}

export const GROUP_ORDER: FieldGroup[] = ['attributes', 'dimensions', 'sap', 'legacy']

/* ── Per-subtype field lists ──────────────────────────────── */
// Only the OData property names that belong to each subtype (own properties, writable).

export const SUBTYPE_FIELDS: Record<string, string[]> = {
  'PTC.ProdMgmt.BALMECHATRONICPART': [
    'BALADDITIV1', 'BALADDITIV1PERCENTAGE', 'BALADDITIV2', 'BALADDITIV2PERCENTAGE',
    'BALADDITIV3', 'BALADDITIV3PERCENTAGE', 'BALALTIUMCATEGORY', 'BALALTIUMCLEANUP',
    'BALAUTOMATICEXCHANGE', 'BALBYAPPROVALLIMITEDCHARACTERISTICS',
    'BALCUSTOMERPROVIDEDPART', 'BALCUSTOMERSPECIFIC', 'BALDEFINEDSTORECONDITION',
    'BALERPmigrationdate', 'BALISVARIANT',
    'BALLegacyERPname', 'BALLegacyERPnumber', 'BALLegacyERPsource',
    'BALLegacyERPstate', 'BALLegacyERPversion',
    'BALMATERIAL', 'BALNOTSUITABLENEWDESIGN',
    'BALOBJECTDIMENSION1', 'BALOBJECTDIMENSION2', 'BALOBJECTDIMENSION3', 'BALOBJECTDIMENSION4',
    'BALSAPALLOCATEDPLANT', 'BALSAPMATCOMPLIANCESTATUS', 'BALSAPMSTAV',
    'BALSPECIALOPERATIONALCONDITIONS', 'BALSPECIALOPERATIONALCONDITIONSTEXT',
    'BALSTORAGECONDITIONTEXT',
    'BALSURFACECOLOUR', 'BALSURFACEFINISH', 'BALSURFACEHARDNESS',
    'BALSURFACEOTHER', 'BALSURFACETHICKNESS',
    'BALUPSTREAMSOURCE', 'BALVERSION',
    'BALWEIGHTBRUTTO', 'BALWEIGHTMODELED', 'BALWEIGHTNETTO',
  ],

  'PTC.ProdMgmt.BALAUXPART': [
    'BALBYAPPROVALLIMITEDCHARACTERISTICS', 'BALDEFINEDSTORECONDITION',
    'BALERPmigrationdate',
    'BALLegacyERPname', 'BALLegacyERPnumber', 'BALLegacyERPsource',
    'BALLegacyERPstate', 'BALLegacyERPversion',
    'BALNOTSUITABLENEWDESIGN',
    'BALSAPALLOCATEDPLANT', 'BALSAPMATCOMPLIANCESTATUS', 'BALSAPMSTAV',
    'BALSPECIALOPERATIONALCONDITIONS', 'BALSPECIALOPERATIONALCONDITIONSTEXT',
    'BALSTORAGECONDITIONTEXT', 'BALUPSTREAMSOURCE', 'BALVERSION',
  ],

  'PTC.ProdMgmt.BALENCDOCPART': [
    'BALBYAPPROVALLIMITEDCHARACTERISTICS', 'BALCUSTOMERSPECIFIC',
    'BALDOCUMENTATIONTYPE', 'BALDOCUMENTDOCTYPE', 'BALDOCUMENTSUBTYPE',
    'BALERPmigrationdate',
    'BALLegacyERPname', 'BALLegacyERPnumber', 'BALLegacyERPsource',
    'BALLegacyERPstate', 'BALLegacyERPversion',
    'BALNOTSUITABLENEWDESIGN', 'BALPRINTINGGOOD',
    'BALSAPALLOCATEDPLANT', 'BALSAPMATCOMPLIANCESTATUS', 'BALSAPMSTAV',
    'BALVERSION',
  ],

  'PTC.ProdMgmt.BALEQUIPMENTPART': [
    'BALBYAPPROVALLIMITEDCHARACTERISTICS', 'BALDEFINEDSTORECONDITION',
    'BALOBJECTDIMENSION1', 'BALOBJECTDIMENSION2', 'BALOBJECTDIMENSION3',
    'BALSAPALLOCATEDPLANT', 'BALSAPMATCOMPLIANCESTATUS', 'BALSAPMSTAV',
    'BALSERIALNUMBER',
    'BALSPECIALOPERATIONALCONDITIONS', 'BALSPECIALOPERATIONALCONDITIONSTEXT',
    'BALSTORAGECONDITIONTEXT', 'BALUPSTREAMSOURCE', 'BALVERSION',
    'BALWEIGHTBRUTTO', 'BALWEIGHTMODELED', 'BALWEIGHTNETTO',
  ],

  'PTC.ProdMgmt.BALPACKAGEPART': [
    'BALAUTOMATICPACKING', 'BALBYAPPROVALLIMITEDCHARACTERISTICS',
    'BALCUSTOMERPROVIDEDPART', 'BALCUSTOMERSPECIFIC', 'BALDEFINEDSTORECONDITION',
    'BALERPmigrationdate', 'BALINTERNALTRANSPORTPACKING',
    'BALLegacyERPname', 'BALLegacyERPnumber', 'BALLegacyERPsource',
    'BALLegacyERPstate', 'BALLegacyERPversion',
    'BALNOTSUITABLENEWDESIGN',
    'BALOBJECTDIMENSION1', 'BALOBJECTDIMENSION2', 'BALOBJECTDIMENSION3', 'BALOBJECTDIMENSION4',
    'BALSAPALLOCATEDPLANT', 'BALSAPMATCOMPLIANCESTATUS', 'BALSAPMSTAV',
    'BALSPECIALOPERATIONALCONDITIONS', 'BALSPECIALOPERATIONALCONDITIONSTEXT',
    'BALSTORAGECONDITIONTEXT', 'BALUPSTREAMSOURCE', 'BALVERSION',
    'BALWEIGHTBRUTTO', 'BALWEIGHTMODELED', 'BALWEIGHTNETTO',
  ],

  'PTC.ProdMgmt.BALPRODUCTPART': [
    'BALBYAPPROVALLIMITEDCHARACTERISTICS', 'BALCUSTOMERSPECIFIC',
    'BALDEFINEDSTORECONDITION', 'BALERPmigrationdate', 'BALFORMATCHCODE',
    'BALISVARIANT',
    'BALLegacyERPname', 'BALLegacyERPnumber', 'BALLegacyERPsource',
    'BALLegacyERPstate', 'BALLegacyERPversion',
    'BALNOTSUITABLENEWDESIGN',
    'BALOBJECTDIMENSION1', 'BALOBJECTDIMENSION2', 'BALOBJECTDIMENSION3', 'BALOBJECTDIMENSION4',
    'BALSAPALLOCATEDPLANT', 'BALSAPMATCOMPLIANCESTATUS', 'BALSAPMSTAV',
    'BALSPECIALOPERATIONALCONDITIONS', 'BALSPECIALOPERATIONALCONDITIONSTEXT',
    'BALSTORAGECONDITIONTEXT', 'BALVERSION',
    'BALWEIGHTBRUTTO', 'BALWEIGHTMODELED', 'BALWEIGHTNETTO',
  ],

  'PTC.ProdMgmt.BALCOLLECTIONPART': [
    // No writable subtype-specific fields
  ],

  'PTC.ProdMgmt.BALRAWMATERIAL': [
    'BALBYAPPROVALLIMITEDCHARACTERISTICS', 'BALNOTSUITABLENEWDESIGN',
  ],

  'PTC.ProdMgmt.BALSOFTWAREPART': [
    'BALAZUREMESSAGE', 'BALBYAPPROVALLIMITEDCHARACTERISTICS',
    'BALCUSTOMERSPECIFIC', 'BALERPmigrationdate',
    'BALLegacyERPname', 'BALLegacyERPnumber', 'BALLegacyERPsource',
    'BALLegacyERPstate', 'BALLegacyERPversion',
    'BALNOTSUITABLENEWDESIGN', 'BALPROCESSTOKEN', 'BALQAAPPROVED',
    'BALSAPALLOCATEDPLANT', 'BALSAPMATCOMPLIANCESTATUS', 'BALSAPMSTAV',
    'BALSOFTWAREGUID', 'BALUNIQUESOFTWAREIDENTIFIER', 'BALUPSTREAMSOURCE',
  ],

  'PTC.ProdMgmt.BALDMYPART': [
    'BALERPmigrationdate',
    'BALLegacyERPname', 'BALLegacyERPnumber', 'BALLegacyERPsource',
    'BALLegacyERPstate', 'BALLegacyERPversion',
    'BALSAPALLOCATEDPLANT',
  ],

  'PTC.ProdMgmt.BALINTDOCPART': [
    'BALBYAPPROVALLIMITEDCHARACTERISTICS', 'BALNOTSUITABLENEWDESIGN',
    'BALSAPMSTAV', 'BALVERSION',
  ],

  'PTC.ProdMgmt.BALCERTPART': [
    'BALNOEXPIRATION', 'BALNOTSUITABLENEWDESIGN',
    'BALREVIEWTILL', 'BALVALIDFROM', 'BALVALIDITYPERIOD',
  ],
}

/* ── Helper: get grouped fields for a subtype ─────────────── */

export interface GroupedFields {
  group: FieldGroup
  label: string
  fields: { name: string; def: FieldDef }[]
}

export function getGroupedFieldsForSubtype(odataType: string): GroupedFields[] {
  const fieldNames = SUBTYPE_FIELDS[odataType] || []
  if (fieldNames.length === 0) return []

  const byGroup = new Map<FieldGroup, { name: string; def: FieldDef }[]>()
  for (const name of fieldNames) {
    const def = FIELD_REGISTRY[name]
    if (!def) continue
    const list = byGroup.get(def.group) || []
    list.push({ name, def })
    byGroup.set(def.group, list)
  }

  return GROUP_ORDER
    .filter((g) => byGroup.has(g))
    .map((g) => ({
      group: g,
      label: GROUP_LABELS[g],
      fields: byGroup.get(g)!,
    }))
}
