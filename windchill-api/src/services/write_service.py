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

    Frontend schickt einfache Strings (z.B. Source='make', View='Design').
    OData erwartet komplexe Typen (z.B. Source={"Value":"make"}).

    Felder basierend auf Windchill Part-Erstellformular (wpe.md):
        Number, Name, Description,
        Source, View, AssemblyMode, DefaultUnit,
        GatheringPart, ConfigurableModule,
        Location (FolderPath), ProductFamily (IBA),
        Context@odata.bind (Container)
    """
    body: dict[str, Any] = {}

    # --- Direkte String-Properties ---
    for key in ("Number", "Name", "Description"):
        if key in attrs and attrs[key]:
            body[key] = attrs[key]

    # --- Enum-Properties (OData: {"Value": "..."}  ) ---

    # Source: "make" | "buy" | "notapplicable"
    source = attrs.get("Source", "")
    if source:
        body["Source"] = {"Value": source.lower()}

    # DefaultUnit: z.B. "ea", "kg", "m", "l", ...
    unit = attrs.get("DefaultUnit", "")
    if unit:
        body["DefaultUnit"] = {"Value": unit}

    # View: "Design" | "Manufacturing"
    # Hinweis: {"Value": "Design"} gibt HTTP 400 "Invalid JSON type for property 'View'".
    # Deshalb als einfachen String senden. Falls das auch scheitert, muss View
    # über einen anderen Mechanismus gesetzt werden (z.B. Container-Kontext).
    view = attrs.get("View", "")
    if view:
        body["View"] = view

    # AssemblyMode: "separable" | "inseparable" | "component"
    assembly = attrs.get("AssemblyMode", "separable")
    body["AssemblyMode"] = {"Value": assembly.lower()}

    # --- Boolean-Properties (nur senden wenn true, false ist Windchill-Default) ---

    # GatheringPart: "yes"/"no" → boolean
    if attrs.get("GatheringPart", "no").lower() == "yes":
        body["GatheringPart"] = True

    # PhantomManufacturingPart: nur wenn explizit true
    if attrs.get("PhantomManufacturingPart", "no").lower() in ("yes", "true"):
        body["PhantomManufacturingPart"] = True

    # ConfigurableModule: "yes"/"no" → boolean
    if attrs.get("ConfigurableModule", "no").lower() == "yes":
        body["ConfigurableModule"] = True

    # --- Container-Referenz (Pflicht) ---
    context = attrs.get("Context@odata.bind", "")
    if context:
        body["Context@odata.bind"] = context

    # --- IBA / Soft Attributes ---
    product_family = attrs.get("ProductFamily", "")
    if product_family:
        body["BAL_CP_ORDER_PREFIX"] = product_family

    # Classification (IBA): z.B. "Fuses", "MOSFETs", etc.
    classification = attrs.get("Classification", "")
    if classification:
        body["BAL_CLASSIFICATION_BINDING_WTPART"] = classification

    # Falls weitere OData-Properties direkt mitgegeben werden (Power-User),
    # uebernehmen, ohne die obigen zu ueberschreiben.
    _handled = {
        "Source", "DefaultUnit", "View", "Number", "Name", "Description",
        "AssemblyMode", "GatheringPart", "ConfigurableModule",
        "PhantomManufacturingPart", "ProductFamily", "Classification",
    }
    for key, val in attrs.items():
        if key not in body and key not in _handled:
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
