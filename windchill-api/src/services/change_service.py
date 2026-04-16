"""
Business logic: Change-Management-Details (Affected Items, Resulting Items).

Service-Schicht zwischen Router und Adapter. Normalisiert OData-Rohdaten
zu typisierten DTOs.
"""

import time

from src.adapters.wrs_client import WRSClient
from src.core.odata import normalize_item
from src.models.dto import ChangeItem, ChangeItemsResponse, TimingInfo


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
