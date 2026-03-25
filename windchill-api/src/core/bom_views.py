"""
BOM View Configurations.
========================

Defines which columns are shown for each BOM view.
Views correspond to Windchill BOM view concepts (Design, Manufacturing, etc.).

Column sources:
  - "part"       → field on the BomTreeNode itself (number, name, version, …)
  - "link"       → extracted usage-link standard fields (quantity, quantityUnit, lineNumber)
  - "usageLink"  → any key inside ``usageLinkAttributes`` dict (dynamic OData fields)

Each view is a dict describing the id, label, and ordered column list.
The frontend receives these configs and renders columns dynamically.
"""

from src.models.dto import BomViewColumn, BomViewConfig

# ── Column presets ───────────────────────────────────────────

_COL_LINE   = BomViewColumn(key="lineNumber",   label="Pos",       source="link")
_COL_NUM    = BomViewColumn(key="number",        label="Nummer",    source="part")
_COL_NAME   = BomViewColumn(key="name",          label="Name",      source="part")
_COL_VER    = BomViewColumn(key="version",       label="Version",   source="part")
_COL_ITER   = BomViewColumn(key="iteration",     label="Iteration", source="part")
_COL_STATE  = BomViewColumn(key="state",         label="Status",    source="part")
_COL_QTY    = BomViewColumn(key="quantity",      label="Menge",     source="link", align="right")
_COL_UNIT   = BomViewColumn(key="quantityUnit",  label="Einheit",   source="link")
_COL_ORG    = BomViewColumn(key="organizationId",label="Organisation", source="part")
_COL_TYPE   = BomViewColumn(key="type",          label="Typ",       source="part")
_COL_IDENT  = BomViewColumn(key="identity",      label="Identity",  source="part")

# Usage-link attribute columns (from usageLinkAttributes dict)
_COL_FIND_NR     = BomViewColumn(key="FindNumber",          label="Find Number",      source="usageLink")
_COL_REF_DESIG   = BomViewColumn(key="ReferenceDesignator", label="Ref Designator",   source="usageLink")
_COL_TRACE_CODE  = BomViewColumn(key="TraceCode",           label="Trace Code",       source="usageLink")
_COL_SOURCE      = BomViewColumn(key="Source",              label="Source",           source="usageLink")
_COL_SUBSTITUTE  = BomViewColumn(key="SubstituteFor",       label="Substitute For",   source="usageLink")


# ── View definitions ─────────────────────────────────────────

BOM_VIEWS: list[BomViewConfig] = [
    BomViewConfig(
        id="default",
        label="Standard",
        columns=[_COL_NUM, _COL_NAME, _COL_VER, _COL_STATE, _COL_QTY, _COL_UNIT],
    ),
    BomViewConfig(
        id="manufacturing",
        label="Manufacturing BOM",
        columns=[
            _COL_LINE, _COL_NUM, _COL_NAME, _COL_VER, _COL_STATE,
            _COL_QTY, _COL_UNIT, _COL_FIND_NR, _COL_REF_DESIG,
        ],
    ),
    BomViewConfig(
        id="detailed",
        label="Detailansicht",
        columns=[
            _COL_LINE, _COL_NUM, _COL_NAME, _COL_VER, _COL_ITER,
            _COL_STATE, _COL_QTY, _COL_UNIT, _COL_ORG,
            _COL_FIND_NR, _COL_REF_DESIG, _COL_TRACE_CODE,
            _COL_SOURCE, _COL_SUBSTITUTE,
        ],
    ),
    BomViewConfig(
        id="ai_agent",
        label="AI Agent (alle Attribute)",
        columns=[
            _COL_LINE, _COL_NUM, _COL_NAME, _COL_VER, _COL_ITER,
            _COL_STATE, _COL_IDENT, _COL_TYPE, _COL_QTY, _COL_UNIT,
            _COL_ORG, _COL_FIND_NR, _COL_REF_DESIG, _COL_TRACE_CODE,
            _COL_SOURCE, _COL_SUBSTITUTE,
        ],
    ),
]

# Quick lookup by view id
BOM_VIEWS_BY_ID: dict[str, BomViewConfig] = {v.id: v for v in BOM_VIEWS}
