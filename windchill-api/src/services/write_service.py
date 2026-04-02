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

    Fuer Parts zweistufig:
      1. POST /ProdMgmt/Parts mit Standard-OData-Feldern
      2. PATCH /ProdMgmt/Parts('<id>') mit IBAs / Soft-Attributes
    Windchill erlaubt IBAs (z.B. BAL_CP_ORDER_PREFIX) nicht im Create-Body.
    """
    t0 = time.monotonic()

    post_create_attrs: dict[str, Any] = {}

    # Part-spezifische Attribut-Konvertierung
    if type_key == "part":
        attributes, post_create_attrs = _build_part_body(attributes)
        logger.info("Create Part body: %s", attributes)
        if post_create_attrs:
            logger.info("Post-create PATCH body: %s", post_create_attrs)

    raw = client.create_object(type_key, attributes)
    n = normalize_item(raw)
    obj_id = n["id"]

    # Schritt 2: IBAs / Soft-Attributes per PATCH nachsetzen
    if post_create_attrs and obj_id:
        try:
            client.update_object_attributes(type_key, obj_id, post_create_attrs)
            logger.info("Post-create PATCH fuer %s '%s': %s",
                        type_key, n["number"], list(post_create_attrs.keys()))
        except Exception:
            logger.warning("Post-create PATCH fehlgeschlagen fuer %s '%s': %s",
                           type_key, n["number"], list(post_create_attrs.keys()),
                           exc_info=True)

    ms = round((time.monotonic() - t0) * 1000, 1)
    return WriteResponse(
        ok=True,
        objectId=obj_id,
        number=n["number"],
        message=f"{type_key} '{n['number']}' erstellt",
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def _build_part_body(attrs: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Frontend-Part-Attribute in OData-konformes Format konvertieren.

    Gibt zwei Dicts zurueck:
      1. create_body — Felder fuer POST /ProdMgmt/Parts (Standard-OData-Properties)
      2. patch_body  — IBAs/Soft-Attributes, die per PATCH nach Create gesetzt werden

    Windchill akzeptiert beim Create nur Standard-Properties.
    IBAs (BAL_*, Custom Attributes) muessen per PATCH nachgesetzt werden.
    """
    create_body: dict[str, Any] = {}
    patch_body: dict[str, Any] = {}

    # --- @odata.type (Soft Type / Subtype) ---
    # Windchill verlangt einen konkreten Subtype, Base WTPart ist nicht instantiierbar.
    # Format: "PTC.ProdMgmt.BALMECHATRONICPART" (ohne #-Prefix)
    odata_type = attrs.get("TypeId", "")
    if odata_type:
        create_body["@odata.type"] = odata_type

    # --- Direkte String-Properties (Create) ---
    for key in ("Number", "Name", "Description"):
        if key in attrs and attrs[key]:
            create_body[key] = attrs[key]

    # --- Enum-Properties (Create, OData: {"Value": "..."}) ---

    # Source: "make" | "buy" | "notapplicable"
    source = attrs.get("Source", "")
    if source:
        create_body["Source"] = {"Value": source.lower()}

    # DefaultUnit: z.B. "ea", "kg", "m", "l", ...
    unit = attrs.get("DefaultUnit", "")
    if unit:
        create_body["DefaultUnit"] = {"Value": unit}

    # View: Wird beim Create nicht akzeptiert (HTTP 400 egal welches Format).
    # Muss per PATCH nach Create gesetzt werden.
    view = attrs.get("View", "")
    if view:
        patch_body["View"] = view

    # AssemblyMode: "separable" | "inseparable" | "component"
    assembly = attrs.get("AssemblyMode", "separable")
    create_body["AssemblyMode"] = {"Value": assembly.lower()}

    # --- Boolean-Properties (Windchill verlangt diese explizit, auch wenn false) ---

    gathering = attrs.get("GatheringPart", "no").lower() == "yes"
    create_body["GatheringPart"] = gathering

    phantom = attrs.get("PhantomManufacturingPart", "no").lower() in ("yes", "true")
    create_body["PhantomManufacturingPart"] = phantom

    # ConfigurableModule: Wird beim Create nicht akzeptiert ("Invalid JSON type").
    # Muss per PATCH nach Create gesetzt werden.
    configurable = attrs.get("ConfigurableModule", "no").lower() == "yes"
    if configurable:
        patch_body["ConfigurableModule"] = True

    # EndItem: Nicht bei allen Subtypes erlaubt ("cannot be changed").
    # Nur senden wenn explizit gesetzt.
    end_item_raw = attrs.get("EndItem", "no").lower()
    if end_item_raw in ("yes", "true"):
        create_body["EndItem"] = True

    # DefaultTraceCode: Pflichtfeld, Enum {"Value": "..."}
    # Werte: "0" (Untraced), "L" (Lot Traced), "S" (Serial Traced), "X" (By Trace Code)
    trace_code = attrs.get("DefaultTraceCode", "0")
    create_body["DefaultTraceCode"] = {"Value": trace_code}

    # --- Container-Referenz (Create, Pflicht) ---
    context = attrs.get("Context@odata.bind", "")
    if context:
        create_body["Context@odata.bind"] = context

    # --- IBAs / Soft Attributes ---
    # OData-Feldnamen sind OHNE Unterstriche (z.B. BALCPORDERPREFIX statt BAL_CP_ORDER_PREFIX)
    product_family = attrs.get("ProductFamily", "")
    if product_family:
        patch_body["BALCPORDERPREFIX"] = product_family

    # Classification: Pflicht beim Create.
    # Balluff-spezifischer Feldname: BALCLASSIFICATIONBINDINGWTPART
    # Format: Objekt mit ClfNodeInternalName (wie bei PTC Classification).
    classification = attrs.get("Classification", "")
    if classification:
        create_body["BALCLASSIFICATIONBINDINGWTPART"] = {
            "ClfNodeInternalName": classification,
        }

    # Falls weitere OData-Properties direkt mitgegeben werden (Power-User),
    # uebernehmen in create_body, ohne die obigen zu ueberschreiben.
    _handled = {
        "Source", "DefaultUnit", "View", "Number", "Name", "Description",
        "AssemblyMode", "GatheringPart", "ConfigurableModule",
        "PhantomManufacturingPart", "ProductFamily", "Classification",
        "EndItem", "DefaultTraceCode", "TypeId",
    }
    for key, val in attrs.items():
        if key not in create_body and key not in patch_body and key not in _handled:
            create_body[key] = val

    return create_body, patch_body


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
