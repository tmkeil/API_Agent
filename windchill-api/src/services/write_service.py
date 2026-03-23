"""
Business logic: Schreibende Operationen (Create, Update, State, Checkout/Checkin).

Service-Schicht zwischen Router und Adapter. Normalisiert OData-Rohdaten
zu typisierten DTOs. Stellt sicher, dass alle Schreiboperationen
ueber einen einzigen Service laufen (Single Responsibility).
"""

import logging
import time
from typing import Any

from src.adapters.wrs_client import WRSClient
from src.core.odata import extract_id, normalize_item
from src.models.dto import TimingInfo, WriteResponse

logger = logging.getLogger(__name__)


def create_object(
    client: WRSClient,
    type_key: str,
    attributes: dict[str, Any],
) -> WriteResponse:
    """Neues Windchill-Objekt erstellen."""
    t0 = time.monotonic()
    raw = client.create_object(type_key, attributes)
    n = normalize_item(raw)
    ms = round((time.monotonic() - t0) * 1000, 1)
    return WriteResponse(
        ok=True,
        objectId=n["id"],
        number=n["number"],
        message=f"{type_key} '{n['number']}' erstellt",
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def update_attributes(
    client: WRSClient,
    type_key: str,
    code: str,
    attributes: dict[str, Any],
) -> WriteResponse:
    """Attribute eines bestehenden Objekts aendern."""
    t0 = time.monotonic()

    # Objekt finden → ID ermitteln
    raw_obj = client.find_object(type_key, code)
    obj_id = extract_id(raw_obj)
    if not obj_id:
        from src.adapters.base import WRSError
        raise WRSError(f"Keine ID fuer {type_key} '{code}'", status_code=404)

    raw = client.update_object_attributes(type_key, obj_id, attributes)
    n = normalize_item(raw)
    ms = round((time.monotonic() - t0) * 1000, 1)
    return WriteResponse(
        ok=True,
        objectId=n["id"],
        number=n["number"],
        message=f"Attribute aktualisiert fuer '{n['number']}'",
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def set_lifecycle_state(
    client: WRSClient,
    type_key: str,
    code: str,
    target_state: str,
    comment: str = "",
) -> WriteResponse:
    """Lifecycle-Status aendern."""
    t0 = time.monotonic()

    raw_obj = client.find_object(type_key, code)
    obj_id = extract_id(raw_obj)
    if not obj_id:
        from src.adapters.base import WRSError
        raise WRSError(f"Keine ID fuer {type_key} '{code}'", status_code=404)

    raw = client.set_lifecycle_state(type_key, obj_id, target_state, comment)
    n = normalize_item(raw)
    ms = round((time.monotonic() - t0) * 1000, 1)
    return WriteResponse(
        ok=True,
        objectId=n["id"],
        number=n["number"],
        message=f"Status von '{n['number']}' auf '{target_state}' gesetzt",
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def checkout(
    client: WRSClient,
    type_key: str,
    code: str,
) -> WriteResponse:
    """Objekt auschecken."""
    t0 = time.monotonic()

    raw_obj = client.find_object(type_key, code)
    obj_id = extract_id(raw_obj)
    if not obj_id:
        from src.adapters.base import WRSError
        raise WRSError(f"Keine ID fuer {type_key} '{code}'", status_code=404)

    raw = client.checkout_object(type_key, obj_id)
    n = normalize_item(raw)
    ms = round((time.monotonic() - t0) * 1000, 1)
    return WriteResponse(
        ok=True,
        objectId=n["id"],
        number=n["number"],
        message=f"'{n['number']}' ausgecheckt",
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def checkin(
    client: WRSClient,
    type_key: str,
    code: str,
    comment: str = "",
) -> WriteResponse:
    """Objekt einchecken."""
    t0 = time.monotonic()

    raw_obj = client.find_object(type_key, code)
    obj_id = extract_id(raw_obj)
    if not obj_id:
        from src.adapters.base import WRSError
        raise WRSError(f"Keine ID fuer {type_key} '{code}'", status_code=404)

    raw = client.checkin_object(type_key, obj_id, comment)
    n = normalize_item(raw)
    ms = round((time.monotonic() - t0) * 1000, 1)
    return WriteResponse(
        ok=True,
        objectId=n["id"],
        number=n["number"],
        message=f"'{n['number']}' eingecheckt",
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )
