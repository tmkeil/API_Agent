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
    """Neues Windchill-Objekt erstellen.

    Fuer Parts werden Frontend-Felder (View, Source, FolderLocation, etc.)
    in OData-konformes Format konvertiert.
    """
    t0 = time.monotonic()

    # Part-spezifische Attribut-Konvertierung
    if type_key == "part":
        attributes = _build_part_body(attributes)

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


def _build_part_body(attrs: dict[str, Any]) -> dict[str, Any]:
    """Frontend-Part-Attribute in OData-konformes Format konvertieren.

    Frontend schickt einfache Strings:
        {"Number": "...", "Name": "...", "View": "Design", "Source": "Make", ...}

    OData erwartet (PTC WRS Doku):
        {"Number": "...", "Name": "...",
         "Source": {"Value": "make"},
         "DefaultUnit": {"Value": "ea"},
         "AssemblyMode": {"Value": "separable"},
         "Context@odata.bind": "Containers('OR:...')"}

    Referenz: https://support.ptc.com/help/windchill_rest_services/r1.6/en/
              windchill_rest_services/WCCG_RESTAccessExamplesCreatePart.html
    """
    body: dict[str, Any] = {}

    # Direkte String-Properties
    for key in ("Number", "Name"):
        if key in attrs:
            body[key] = attrs[key]

    # Source: "Make" → {"Value": "make"}
    source = attrs.get("Source", "")
    if source:
        body["Source"] = {"Value": source.lower()}

    # DefaultUnit: "each" → {"Value": "ea"}
    unit = attrs.get("DefaultUnit", "")
    if unit:
        # Windchill erwartet Kurzform
        unit_map = {"each": "ea", "piece": "ea"}
        body["DefaultUnit"] = {"Value": unit_map.get(unit.lower(), unit.lower())}

    # View: "Design" → {"Value": "Design"}
    view = attrs.get("View", "")
    if view:
        body["View"] = {"Value": view}

    # AssemblyMode (Default: separable)
    body["AssemblyMode"] = {"Value": "separable"}

    # PhantomManufacturingPart: Standard false
    body["PhantomManufacturingPart"] = False

    # Context@odata.bind: Pflichtfeld — Container-Referenz
    # Wenn das Frontend eine Container-ID mitschickt, verwenden.
    # Sonst: muss der Aufrufer das Feld direkt setzen.
    context = attrs.get("Context@odata.bind", "")
    if context:
        body["Context@odata.bind"] = context

    # Falls weitere OData-Properties direkt mitgegeben werden (Power-User),
    # uebernehmen, ohne die obigen zu ueberschreiben.
    for key, val in attrs.items():
        if key not in body and key not in (
            "Source", "DefaultUnit", "View", "Number", "Name",
        ):
            body[key] = val

    return body


def _resolve_object_id(
    client: WRSClient, type_key: str, code: str, object_id: str | None,
) -> str:
    """Object-ID ermitteln: direkt verwenden oder per Suche."""
    if object_id:
        return object_id
    from src.adapters.base import WRSError
    raw_obj = client.find_object(type_key, code)
    obj_id = extract_id(raw_obj)
    if not obj_id:
        raise WRSError(f"Keine ID fuer {type_key} '{code}'", status_code=404)
    return obj_id


def update_attributes(
    client: WRSClient,
    type_key: str,
    code: str,
    attributes: dict[str, Any],
    object_id: str | None = None,
) -> WriteResponse:
    """Attribute eines bestehenden Objekts aendern."""
    t0 = time.monotonic()

    obj_id = _resolve_object_id(client, type_key, code, object_id)

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
    object_id: str | None = None,
) -> WriteResponse:
    """Lifecycle-Status aendern."""
    t0 = time.monotonic()

    obj_id = _resolve_object_id(client, type_key, code, object_id)

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
    object_id: str | None = None,
) -> WriteResponse:
    """Objekt auschecken."""
    t0 = time.monotonic()

    obj_id = _resolve_object_id(client, type_key, code, object_id)

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
    object_id: str | None = None,
) -> WriteResponse:
    """Objekt einchecken."""
    t0 = time.monotonic()

    obj_id = _resolve_object_id(client, type_key, code, object_id)

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


def revise(
    client: WRSClient,
    type_key: str,
    code: str,
    object_id: str | None = None,
) -> WriteResponse:
    """Neue Revision eines Objekts erstellen."""
    t0 = time.monotonic()

    obj_id = _resolve_object_id(client, type_key, code, object_id)

    raw = client.revise_object(type_key, obj_id)
    n = normalize_item(raw)
    ms = round((time.monotonic() - t0) * 1000, 1)
    return WriteResponse(
        ok=True,
        objectId=n["id"],
        number=n["number"],
        message=f"Neue Revision von '{n['number']}' erstellt",
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def add_bom_child(
    client: WRSClient,
    parent_code: str,
    child_code: str,
    quantity: float = 1.0,
    unit: str = "each",
) -> WriteResponse:
    """Kind-Part zur BOM hinzufuegen."""
    t0 = time.monotonic()

    parent_raw = client.find_object("part", parent_code)
    parent_id = extract_id(parent_raw)
    if not parent_id:
        from src.adapters.base import WRSError
        raise WRSError(f"Parent Part '{parent_code}' nicht gefunden", status_code=404)

    child_raw = client.find_object("part", child_code)
    child_id = extract_id(child_raw)
    if not child_id:
        from src.adapters.base import WRSError
        raise WRSError(f"Kind Part '{child_code}' nicht gefunden", status_code=404)

    client.add_bom_child(parent_id, child_id, quantity, unit)
    child_n = normalize_item(child_raw)
    ms = round((time.monotonic() - t0) * 1000, 1)
    return WriteResponse(
        ok=True,
        objectId=child_id,
        number=child_n["number"],
        message=f"'{child_n['number']}' als Kind zu '{parent_code}' hinzugefuegt",
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def remove_bom_child(
    client: WRSClient,
    usage_link_id: str,
) -> WriteResponse:
    """BOM-Kind-Beziehung (UsageLink) entfernen."""
    t0 = time.monotonic()

    client.remove_bom_child(usage_link_id)
    ms = round((time.monotonic() - t0) * 1000, 1)
    return WriteResponse(
        ok=True,
        message=f"UsageLink '{usage_link_id}' entfernt",
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )
