"""
Business logic: Change-Management-Details (Affected Items, Resulting Items).

Service-Schicht zwischen Router und Adapter. Normalisiert OData-Rohdaten
zu typisierten DTOs.
"""

import logging
import time

from src.adapters.wrs_client import WRSClient
from src.core.odata import normalize_item
from src.models.dto import ChangeItem, ChangeItemsResponse, TimingInfo

logger = logging.getLogger(__name__)


def get_affected_items(
    client: WRSClient,
    type_key: str,
    code: str,
) -> ChangeItemsResponse:
    """Affected Items eines Change-Objekts abfragen."""
    t0 = time.monotonic()
    raw_items = client.get_change_affected_items(type_key, code)
    items = [_to_change_item(raw) for raw in raw_items]
    ms = round((time.monotonic() - t0) * 1000, 1)
    return ChangeItemsResponse(
        code=code,
        relation="affected",
        totalFound=len(items),
        items=items,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def get_resulting_items(
    client: WRSClient,
    type_key: str,
    code: str,
) -> ChangeItemsResponse:
    """Resulting Items eines Change-Objekts abfragen."""
    t0 = time.monotonic()
    raw_items = client.get_change_resulting_items(type_key, code)
    items = [_to_change_item(raw) for raw in raw_items]
    ms = round((time.monotonic() - t0) * 1000, 1)
    return ChangeItemsResponse(
        code=code,
        relation="resulting",
        totalFound=len(items),
        items=items,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def _to_change_item(raw: dict) -> ChangeItem:
    """Normalize a raw OData dict to a ChangeItem DTO."""
    n = normalize_item(raw)

    # ── Object Type erkennen ─────────────────────────────
    # OData liefert @odata.type z.B. "#PTC.ProdMgmt.BAL_PRODUCT_PART"
    # oder "#PTC.DocMgmt.WTDocument", "#PTC.ProdMgmt.WTPart" etc.
    obj_type = ""
    odata_type = str(raw.get("@odata.type", ""))
    if odata_type:
        # "#PTC.ProdMgmt.BAL_PRODUCT_PART" → Windchill-Klasse ableiten
        segment = odata_type.rsplit(".", 1)[-1]  # "BAL_PRODUCT_PART"
        if "ProdMgmt" in odata_type:
            obj_type = "WTPart"
        elif "DocMgmt" in odata_type:
            obj_type = "WTDocument"
        elif "EPM" in odata_type or "CadMgmt" in odata_type:
            obj_type = "EPMDocument"
        elif "ChangeMgmt" in odata_type:
            if "ChangeNotice" in odata_type or "ChangeOrder" in odata_type:
                obj_type = "WTChangeOrder2"
            elif "ChangeRequest" in odata_type:
                obj_type = "WTChangeRequest2"
            elif "ProblemReport" in odata_type or "ChangeIssue" in odata_type:
                obj_type = "WTChangeIssue"
        if not obj_type:
            obj_type = segment  # Fallback: letztes Segment
    if not obj_type:
        obj_type = raw.get("Type") or raw.get("SubType") or raw.get("_entity_type") or ""

    # ── Subtype (Part-Untertyp) ──────────────────────────
    sub_type = ""
    if odata_type and "ProdMgmt" in odata_type:
        segment = odata_type.rsplit(".", 1)[-1]
        if segment != "WTPart":
            sub_type = segment  # z.B. "BAL_PRODUCT_PART"
    if not sub_type:
        sub_type = str(raw.get("ObjectType") or raw.get("SubType") or "")

    return ChangeItem(
        objectId=n["id"],
        objectType=str(obj_type),
        subType=sub_type,
        number=n["number"],
        name=n["name"],
        version=n["version"],
        iteration=n["iteration"],
        state=n["state"],
        identity=n["identity"],
    )
