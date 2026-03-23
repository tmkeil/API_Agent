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
    # Detect object type from raw data (Type property or Subtype)
    obj_type = raw.get("Type") or raw.get("SubType") or raw.get("_entity_type") or ""
    return ChangeItem(
        objectId=n["id"],
        objectType=str(obj_type),
        number=n["number"],
        name=n["name"],
        version=n["version"],
        iteration=n["iteration"],
        state=n["state"],
        identity=n["identity"],
    )
