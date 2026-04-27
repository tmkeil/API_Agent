/**
 * Subtype-spezifische Feld-Spezifikationen für die CreatePart-Page.
 *
 * Quelle: ../../../part_creation_html/aatest.md (Zusammenfassung der
 * Windchill-Native-UI-Felder pro Subtyp). Erforderliche Felder sind dort
 * mit `*` markiert.
 *
 * Hinweis: Die hier aufgeführten Feld-Keys entsprechen den OData-Properties,
 * die der WRSClient akzeptiert. Subtyp-spezifische Soft-Attribute (z. B.
 * BAL_HARDWARE_VERSION, BAL_TYPE_OF_DOCUMENTATION) sind aktuell nicht
 * ausgeliefert — sobald die OData-Keys bekannt sind, können sie hier
 * deklarativ ergänzt werden, ohne die Page-Logik zu ändern.
 */

/** Form-Feld-Keys, die die CreatePart-Page derzeit kennt. */
export type FieldKey =
  | 'Number'
  | 'Name'
  | 'Description'
  | 'View'
  | 'Source'
  | 'DefaultUnit'
  | 'AssemblyMode'
  | 'GatheringPart'
  | 'ConfigurableModule'
  | 'ProductFamily'
  | 'Classification'

/** Sichtbarkeit + Pflicht-Status eines Feldes für einen bestimmten Subtyp. */
export interface FieldRule {
  visible: boolean
  required: boolean
}

/** Komplette Spezifikation eines Subtyps. */
export type SubtypeSpec = Record<FieldKey, FieldRule>

const SHOW_REQUIRED: FieldRule = { visible: true, required: true }
const SHOW_OPTIONAL: FieldRule = { visible: true, required: false }
const HIDDEN: FieldRule = { visible: false, required: false }

/** Defaults für Felder, die in fast allen Subtypen vorkommen. */
const COMMON: SubtypeSpec = {
  Number:             SHOW_OPTIONAL,
  Name:               SHOW_REQUIRED,
  Description:        SHOW_OPTIONAL,
  View:               SHOW_OPTIONAL,
  Source:             SHOW_REQUIRED,
  DefaultUnit:        SHOW_REQUIRED,
  AssemblyMode:       SHOW_REQUIRED,
  GatheringPart:      SHOW_REQUIRED,
  ConfigurableModule: SHOW_REQUIRED,
  ProductFamily:      SHOW_OPTIONAL,
  Classification:     SHOW_REQUIRED,
}

/** Auxiliary Material — alle Standardfelder erforderlich. */
const SPEC_AUXILIARY: SubtypeSpec = { ...COMMON }

/** Basic Material — wie Aux, ohne Classification-Pflicht? Nein, mit. */
const SPEC_BASIC: SubtypeSpec = { ...COMMON }

/**
 * Collection — kein AssemblyMode, kein DefaultUnit, keine Classification.
 * (laut aatest.md hat Collection nur Identity ohne Classification-Sektion)
 */
const SPEC_COLLECTION: SubtypeSpec = {
  ...COMMON,
  AssemblyMode:   HIDDEN,
  DefaultUnit:    HIDDEN,
  Classification: HIDDEN,
}

/** Component — alle Standardfelder erforderlich. */
const SPEC_COMPONENT: SubtypeSpec = { ...COMMON }

/**
 * DMY — minimaler Dummy-Eintrag, kein AssemblyMode/DefaultUnit/Classification.
 */
const SPEC_DMY: SubtypeSpec = {
  ...COMMON,
  AssemblyMode:   HIDDEN,
  DefaultUnit:    HIDDEN,
  Classification: HIDDEN,
}

/**
 * Enclosed Documentation — kein AssemblyMode/DefaultUnit, Classification erforderlich.
 */
const SPEC_ENCLOSED_DOC: SubtypeSpec = {
  ...COMMON,
  AssemblyMode: HIDDEN,
  DefaultUnit:  HIDDEN,
}

/** Equipment — alle Standardfelder erforderlich. */
const SPEC_EQUIPMENT: SubtypeSpec = { ...COMMON }

/** Packing Material — alle Standardfelder erforderlich. */
const SPEC_PACKING: SubtypeSpec = { ...COMMON }

/**
 * Product — kein DefaultUnit, **keine Classification** (in aatest.md
 * fehlt die ganze Classification-Sektion bei Product).
 */
const SPEC_PRODUCT: SubtypeSpec = {
  ...COMMON,
  DefaultUnit:    HIDDEN,
  Classification: HIDDEN,
}

/** Fallback, wenn ein unbekannter Subtyp-Code kommt. */
const SPEC_DEFAULT: SubtypeSpec = { ...COMMON }

/**
 * Mapping: OData-Subtyp → SubtypeSpec.
 *
 * Die OData-Codes stammen aus `fetchPartSubtypes()` und entsprechen dem
 * `odataType`-Feld der Subtyp-Liste.
 */
const SUBTYPE_SPECS: Record<string, SubtypeSpec> = {
  'PTC.ProdMgmt.BALAUXPART':         SPEC_AUXILIARY,
  'PTC.ProdMgmt.BALRAWMATERIAL':     SPEC_BASIC,
  'PTC.ProdMgmt.BALCOLLECTIONPART':  SPEC_COLLECTION,
  'PTC.ProdMgmt.BALMECHATRONICPART': SPEC_COMPONENT,
  'PTC.ProdMgmt.BALDUMMYPART':       SPEC_DMY,
  'PTC.ProdMgmt.BALENCDOCPART':      SPEC_ENCLOSED_DOC,
  'PTC.ProdMgmt.BALEQUIPMENTPART':   SPEC_EQUIPMENT,
  'PTC.ProdMgmt.BALPACKAGEPART':     SPEC_PACKING,
  'PTC.ProdMgmt.BALPRODUCTPART':     SPEC_PRODUCT,
}

/**
 * Liefert die Spec für einen Subtyp; fällt auf einen sicheren Default
 * zurück, wenn der Subtyp nicht im Mapping steht.
 */
export function getSubtypeSpec(odataType: string): SubtypeSpec {
  return SUBTYPE_SPECS[odataType] ?? SPEC_DEFAULT
}

/** Convenience-Helper für die Page. */
export function isVisible(spec: SubtypeSpec, key: FieldKey): boolean {
  return spec[key].visible
}

export function isRequired(spec: SubtypeSpec, key: FieldKey): boolean {
  return spec[key].visible && spec[key].required
}
