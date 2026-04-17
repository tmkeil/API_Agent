"""
Business logic: Change-Management-Details (Affected Items, Resulting Items).

Service-Schicht zwischen Router und Adapter. Normalisiert OData-Rohdaten
zu typisierten DTOs.
"""

import logging
import time

from src.adapters.wrs_client import WRSClient
from src.core.odata import normalize_item
from src.models.dto import (
    ChangeItem,
    ChangeItemsResponse,
    ChangeNoticeListItem,
    ChangeNoticeListResponse,
    TimingInfo,
)

logger = logging.getLogger(__name__)


def list_change_notices(
    client: WRSClient,
    *,
    state: str = "",
    sub_type: str = "",
    top: int = 50,
    skip: int = 0,
) -> ChangeNoticeListResponse:
    """Change Notices auflisten mit optionalen Filtern."""
    t0 = time.monotonic()
    raw_items, total = client.list_change_notices(
        state=state, sub_type=sub_type, top=top, skip=skip,
    )
    items = [_to_cn_list_item(raw) for raw in raw_items]
    ms = round((time.monotonic() - t0) * 1000, 1)
    return ChangeNoticeListResponse(
        totalCount=total,
        items=items,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


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

    # Windchill-Klasse aus ID: "OR:wt.part.WTPart:12345" → "WTPart"
    id_parts = n["id"].split(":")
    obj_type = id_parts[1].rsplit(".", 1)[-1] if len(id_parts) >= 3 else ""

    # Subtyp aus ObjectType (wie in bom_views): z.B. "Product", "Separable"
    sub_type = str(raw.get("ObjectType") or "")

    return ChangeItem(
        objectId=n["id"],
        objectType=obj_type,
        subType=sub_type,
        number=n["number"],
        name=n["name"],
        version=n["version"],
        iteration=n["iteration"],
        state=n["state"],
        identity=n["identity"],
    )


def has_part_resulting_items(
    client: WRSClient,
    code: str,
) -> bool:
    """Pruefen ob ein Change Notice Resulting Items vom Typ WTPart hat.

    Schneller Check ohne vollstaendige Normalisierung.
    """
    try:
        raw_items = client.get_change_resulting_items("change_notice", code)
    except Exception:
        logger.debug("has_part_resulting_items failed for %s", code, exc_info=True)
        return False

    for raw in raw_items:
        n = normalize_item(raw)
        id_parts = n["id"].split(":")
        if len(id_parts) >= 3:
            obj_type = id_parts[1].rsplit(".", 1)[-1]
            if obj_type == "WTPart":
                return True
    return False


def _to_cn_list_item(raw: dict) -> ChangeNoticeListItem:
    """Normalize a raw OData ChangeNotice dict to a list item DTO."""
    n = normalize_item(raw)
    sub_type = str(raw.get("ObjectType") or "")
    return ChangeNoticeListItem(
        objectId=n["id"],
        number=n["number"],
        name=n["name"],
        subType=sub_type,
        version=n["version"],
        state=n["state"],
        createdBy=str(raw.get("CreatedBy") or ""),
        createdOn=str(raw.get("CreatedOn") or ""),
        lastModified=str(raw.get("LastModified") or ""),
        description=str(raw.get("Description") or ""),
    )
