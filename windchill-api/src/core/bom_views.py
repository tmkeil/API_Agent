"""
BOM View Configurations.
========================

Defines which columns are shown for each BOM view.
Based on real Windchill OData field names from Balluff PLM.

Column sources:
  - "part"       → named field on BomTreeNode itself (number, name, version, …)
  - "link"       → extracted usage-link standard fields (quantity, quantityUnit, lineNumber)
  - "usageLink"  → key inside ``usageLinkAttributes`` dict (from WTPartUsageLink)
  - "partAttr"   → key inside ``partAttributes`` dict (from WTPart OData record)

Each view defines an id, label, and ordered column list.
The frontend receives these configs and renders columns dynamically.
"""

from src.models.dto import BomViewColumn, BomViewConfig
from src.core.odata_fields import F

# ═══════════════════════════════════════════════════════════════
# Part-level columns (from BomTreeNode named fields)
# ═══════════════════════════════════════════════════════════════
_COL_NUM    = BomViewColumn(key="number",        label="Nummer",       source="part")
_COL_NAME   = BomViewColumn(key="name",          label="Name",         source="part")
_COL_VER    = BomViewColumn(key="version",       label="Version",      source="part")
_COL_ITER   = BomViewColumn(key="iteration",     label="Iteration",    source="part")
_COL_STATE  = BomViewColumn(key="state",         label="Status",       source="part")
_COL_ORG    = BomViewColumn(key="organizationId",label="Organisation", source="part")
_COL_IDENT  = BomViewColumn(key="identity",      label="Identity",     source="part")

# ═══════════════════════════════════════════════════════════════
# Usage-link columns (standard extracted fields)
# ═══════════════════════════════════════════════════════════════
_COL_LINE   = BomViewColumn(key="lineNumber",    label="Pos",          source="link")
_COL_QTY    = BomViewColumn(key="quantity",      label="Menge",        source="link", align="right")
_COL_UNIT   = BomViewColumn(key="quantityUnit",  label="Einheit",      source="link")

# ═══════════════════════════════════════════════════════════════
# Part attributes (from partAttributes dict — real Balluff OData fields)
# ═══════════════════════════════════════════════════════════════
_COL_OBJ_TYPE       = BomViewColumn(key="ObjectType",               label="Object Type",       source="partAttr")
_COL_SOURCE         = BomViewColumn(key="Source",                   label="Source",            source="partAttr")
_COL_LATEST         = BomViewColumn(key="Latest",                   label="Latest",            source="partAttr")
_COL_VIEW           = BomViewColumn(key="View",                     label="View",              source="partAttr")
_COL_SAP_NAME       = BomViewColumn(key=F.Part.SAP_NAME,           label="SAP Name",          source="partAttr")
_COL_BINDING        = BomViewColumn(key=F.Part.BINDING,             label="Binding",           source="partAttr")
_COL_SUFFIX         = BomViewColumn(key=F.Part.SUFFIX,              label="Suffix",            source="partAttr")
_COL_CONF_MOD       = BomViewColumn(key="ConfigurableModule",      label="Conf. Module",      source="partAttr")
_COL_SAP_PLANTS     = BomViewColumn(key=F.Part.SAP_ASSIGNED_PLANTS, label="SAP Assigned Plants", source="partAttr")
_COL_SAP_DOWNSTREAM = BomViewColumn(key=F.Doc.SAP_RELEVANCE,       label="SAP Downstream",    source="docAttr")
_COL_SAP_UPSTREAM   = BomViewColumn(key=F.Part.UPSTREAM,            label="SAP Upstream",      source="partAttr")
_COL_IS_VARIANT     = BomViewColumn(key=F.Part.IS_VARIANT,          label="Is Variant",        source="partAttr")
_COL_CN_APPROVER    = BomViewColumn(key="ECNAPPROVER",             label="CN Approver",       source="partAttr")
_COL_CN_APPR_DATE   = BomViewColumn(key="ECNAPPROVERDATE",         label="CN Approver Date",  source="partAttr")
_COL_MADE_FROM      = BomViewColumn(key=F.Part.MADE_FROM_NUMBER,    label="Made From Number",  source="partAttr")
_COL_VAR_DERIVED    = BomViewColumn(key=F.Part.VARIANT_DERIVED_FROM, label="Variant Derived From", source="partAttr")
_COL_DESCRIPTION    = BomViewColumn(key=F.Part.DESCRIPTION_1,       label="Beschreibung",      source="partAttr")
_COL_END_ITEM       = BomViewColumn(key="EndItem",                 label="End Item",          source="partAttr")
_COL_SAP_MAT_TYPE   = BomViewColumn(key=F.Part.MATERIAL_TYPE,       label="SAP Material Type", source="partAttr")
_COL_SAP_ORDER      = BomViewColumn(key=F.Part.SAP_ORDER_CODE,      label="SAP Order Code",    source="partAttr")
_COL_REVISION       = BomViewColumn(key="Revision",                label="Revision",          source="partAttr")
_COL_DEF_TRACE      = BomViewColumn(key="DefaultTraceCode",        label="Default Trace",     source="partAttr")
_COL_DEF_UNIT       = BomViewColumn(key="DefaultUnit",             label="Default Unit",      source="partAttr")

# Raw material fields (on child parts)
_COL_RAW_DIM1       = BomViewColumn(key=F.RawMaterialLink.RAW_DIM_1,       label="Raw Dim 1",         source="partAttr")
_COL_RAW_DIM2       = BomViewColumn(key=F.RawMaterialLink.RAW_DIM_2,       label="Raw Dim 2",         source="partAttr")
_COL_RAW_DIM3       = BomViewColumn(key=F.RawMaterialLink.RAW_DIM_3,       label="Raw Dim 3",         source="partAttr")
_COL_RAW_DIM_UNIT   = BomViewColumn(key=F.RawMaterialLink.RAW_DIM_UNIT,    label="Raw Dim Unit",      source="partAttr")
_COL_RAW_MAT_AMT    = BomViewColumn(key=F.RawMaterialLink.RAW_AMOUNT,      label="Raw Mat Amount",    source="partAttr")
_COL_RAW_MAT_UNIT   = BomViewColumn(key=F.RawMaterialLink.RAW_AMOUNT_UNIT, label="Raw Mat Amt Unit",  source="partAttr")
_COL_RAW_MAT_QTY    = BomViewColumn(key=F.RawMaterialLink.RAW_QUANTITY,    label="Raw Mat Qty",       source="partAttr")
_COL_RAW_MAT_QUNIT  = BomViewColumn(key=F.RawMaterialLink.RAW_QUANTITY_UNIT, label="Raw Mat Qty Unit",  source="partAttr")

# ═══════════════════════════════════════════════════════════════
# Usage-link attributes (from usageLinkAttributes dict — WTPartUsageLink)
# ═══════════════════════════════════════════════════════════════
_COL_FIND_NR        = BomViewColumn(key="FindNumber",              label="Find Number",       source="usageLink")
_COL_TRACE_CODE     = BomViewColumn(key="TraceCode",               label="Trace Code",        source="usageLink")
_COL_REF_DESIG      = BomViewColumn(key="ReferenceDesignatorRange",label="Ref Designator",    source="usageLink")
_COL_LINK_OBJ_TYPE  = BomViewColumn(key="ObjectType",             label="Link Type",          source="usageLink")
_COL_BY_PRODUCT     = BomViewColumn(key=F.UsageLink.BY_PRODUCT,     label="By-Product",        source="usageLink")
_COL_BOM_POS_TEXT   = BomViewColumn(key=F.UsageLink.ERP_POSITION_TEXT, label="BOM Pos Text",      source="usageLink")
_COL_SAP_ALT_GRP    = BomViewColumn(key=F.UsageLink.ALT_GROUP,      label="SAP Alt Group",     source="usageLink")
_COL_SAP_ALT_PRI    = BomViewColumn(key=F.UsageLink.ALT_PRIORITY,   label="SAP Alt Priority",  source="usageLink")
_COL_SAP_ALT_ST     = BomViewColumn(key=F.UsageLink.ALT_STRATEGY,   label="SAP Alt Status",    source="usageLink")
_COL_SAP_PROB       = BomViewColumn(key=F.UsageLink.USAGE_PROBABILITY, label="SAP Probability",   source="usageLink")
_COL_SAP_DISC_GRP   = BomViewColumn(key=F.UsageLink.DISCON_GRP,     label="SAP Disc. Group",   source="usageLink")
_COL_SAP_DISC_DATE  = BomViewColumn(key=F.UsageLink.DISCON_DATE,    label="SAP Disc. Date",    source="usageLink")


# ═══════════════════════════════════════════════════════════════
# View definitions
# ═══════════════════════════════════════════════════════════════

BOM_VIEWS: list[BomViewConfig] = [
    BomViewConfig(
        id="default",
        label="Standard",
        columns=[
            _COL_LINE, _COL_NUM, _COL_NAME, _COL_VER, _COL_STATE,
            _COL_QTY, _COL_UNIT,
        ],
    ),
    BomViewConfig(
        id="extended",
        label="Erweitert",
        columns=[
            _COL_LINE, _COL_NUM, _COL_NAME, _COL_VER, _COL_STATE,
            _COL_QTY, _COL_UNIT, _COL_OBJ_TYPE, _COL_SOURCE,
            _COL_VIEW, _COL_LATEST, _COL_BINDING,
        ],
    ),
    BomViewConfig(
        id="sap",
        label="SAP / Manufacturing",
        columns=[
            _COL_LINE, _COL_NUM, _COL_NAME, _COL_SAP_NAME, _COL_STATE,
            _COL_QTY, _COL_UNIT, _COL_SOURCE,
            _COL_SAP_PLANTS, _COL_SAP_MAT_TYPE, _COL_SAP_DOWNSTREAM,
            _COL_BOM_POS_TEXT, _COL_SAP_ALT_GRP, _COL_SAP_ALT_PRI,
            _COL_SAP_DISC_GRP,
        ],
    ),
    BomViewConfig(
        id="raw_material",
        label="Rohmaterial",
        columns=[
            _COL_LINE, _COL_NUM, _COL_NAME, _COL_STATE,
            _COL_QTY, _COL_UNIT, _COL_MADE_FROM,
            _COL_RAW_DIM1, _COL_RAW_DIM2, _COL_RAW_DIM3, _COL_RAW_DIM_UNIT,
            _COL_RAW_MAT_AMT, _COL_RAW_MAT_UNIT,
            _COL_RAW_MAT_QTY, _COL_RAW_MAT_QUNIT,
        ],
    ),
    BomViewConfig(
        id="all_fields",
        label="Alle Felder",
        columns=[
            _COL_LINE, _COL_NUM, _COL_NAME, _COL_VER, _COL_ITER,
            _COL_STATE, _COL_IDENT, _COL_OBJ_TYPE, _COL_SOURCE,
            _COL_VIEW, _COL_LATEST, _COL_QTY, _COL_UNIT, _COL_ORG,
            _COL_BINDING, _COL_SUFFIX, _COL_SAP_NAME, _COL_CONF_MOD,
            _COL_IS_VARIANT, _COL_SAP_PLANTS, _COL_SAP_DOWNSTREAM,
            _COL_CN_APPROVER, _COL_CN_APPR_DATE,
            _COL_MADE_FROM, _COL_VAR_DERIVED,
            _COL_END_ITEM, _COL_DEF_TRACE, _COL_REVISION,
            _COL_FIND_NR, _COL_TRACE_CODE, _COL_REF_DESIG,
            _COL_BOM_POS_TEXT, _COL_BY_PRODUCT,
            _COL_SAP_ALT_GRP, _COL_SAP_ALT_PRI, _COL_SAP_DISC_GRP,
            _COL_RAW_DIM1, _COL_RAW_DIM2, _COL_RAW_DIM3, _COL_RAW_DIM_UNIT,
            _COL_RAW_MAT_AMT, _COL_RAW_MAT_UNIT,
            _COL_RAW_MAT_QTY, _COL_RAW_MAT_QUNIT,
        ],
    ),
]

# Quick lookup by view id
BOM_VIEWS_BY_ID: dict[str, BomViewConfig] = {v.id: v for v in BOM_VIEWS}
