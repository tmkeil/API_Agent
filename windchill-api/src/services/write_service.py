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
      1. create_body — Minimale Felder fuer POST /ProdMgmt/Parts
         (nur die von der offiziellen WRS-Doku erlaubten Standard-Properties)
      2. patch_body  — Alles andere per PATCH nach Create setzen

    Windchill akzeptiert beim Create nur wenige Standard-Properties.
    IBAs, Enums und Custom-Felder muessen per PATCH nachgesetzt werden.
    Referenz: PTC WRS Doku "Creating a Part".
    """
    create_body: dict[str, Any] = {}
    patch_body: dict[str, Any] = {}

    # ── CREATE-Body: Nur das Minimum (wie offizielle WRS-Doku) ──

    # @odata.type (Soft Type / Subtype) — noetig damit Windchill den
    # richtigen Subtype instantiiert (z.B. BALMECHATRONICPART).
    # HINWEIS: 403 "Secured Action" bedeutet fehlende Berechtigung
    # fuer den Subtype im gewaehlten Container, NICHT falscher Payload.
    odata_type = attrs.get("TypeId", "")
    if odata_type:
        if not odata_type.startswith("#"):
            odata_type = f"#{odata_type}"
        create_body["@odata.type"] = odata_type

    # Name (Pflicht)
    if attrs.get("Name"):
        create_body["Name"] = attrs["Name"]

    # Number (optional — Windchill generiert sonst automatisch)
    if attrs.get("Number"):
        create_body["Number"] = attrs["Number"]

    # Context@odata.bind (Pflicht — Container-Referenz)
    context = attrs.get("Context@odata.bind", "")
    if context:
        create_body["Context@odata.bind"] = context

    # PhantomManufacturingPart (in offizieller Doku enthalten)
    phantom = attrs.get("PhantomManufacturingPart", "no").lower() in ("yes", "true")
    create_body["PhantomManufacturingPart"] = phantom

    # AssemblyMode (in offizieller Doku enthalten)
    assembly = attrs.get("AssemblyMode", "separable")
    create_body["AssemblyMode"] = {
        "Value": assembly.lower(),
        "Display": assembly.capitalize(),
    }

    # ── PATCH-Body: Alles andere nach Create setzen ──

    # Source
    source = attrs.get("Source", "")
    if source:
        patch_body["Source"] = {"Value": source.lower()}

    # DefaultUnit
    unit = attrs.get("DefaultUnit", "")
    if unit:
        patch_body["DefaultUnit"] = {"Value": unit}

    # View
    view = attrs.get("View", "")
    if view:
        patch_body["View"] = view

    # GatheringPart
    gathering = attrs.get("GatheringPart", "no").lower() == "yes"
    if gathering:
        patch_body["GatheringPart"] = True

    # ConfigurableModule
    configurable = attrs.get("ConfigurableModule", "no").lower() == "yes"
    if configurable:
        patch_body["ConfigurableModule"] = True

    # EndItem
    end_item_raw = attrs.get("EndItem", "no").lower()
    if end_item_raw in ("yes", "true"):
        patch_body["EndItem"] = True

    # DefaultTraceCode
    trace_code = attrs.get("DefaultTraceCode", "")
    if trace_code:
        patch_body["DefaultTraceCode"] = {"Value": trace_code}

    # ProductFamily (IBA: BALCPORDERPREFIX)
    product_family = attrs.get("ProductFamily", "")
    if product_family:
        patch_body["BALCPORDERPREFIX"] = product_family

    # Classification (IBA: BALCLASSIFICATIONBINDINGWTPART)
    # Balluff-Pflichtfeld beim Create (nicht in Standard-PTC-Doku, aber vom System verlangt)
    classification = attrs.get("Classification", "")
    if classification:
        create_body["BALCLASSIFICATIONBINDINGWTPART"] = {
            "ClfNodeInternalName": classification,
        }

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
    find_number: str | None = None,
    line_number: int | None = None,
    trace_code: str | None = None,
    occurrences: list[str] | None = None,
) -> WriteResponse:
    """Kind-Part zur BOM hinzufuegen (mit optionalen BOM-Feldern)."""
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

    client.add_bom_child(
        parent_id, child_id, quantity, unit,
        find_number=find_number,
        line_number=line_number,
        trace_code=trace_code,
        occurrences=occurrences,
    )
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


# ── Dokument-Verknuepfung ───────────────────────────────────


def link_document_to_part(
    client: WRSClient,
    part_code: str,
    doc_code: str,
    link_type: str = "DescribedBy",
) -> WriteResponse:
    """Dokument mit einem Part verknuepfen.

    Args:
        part_code: Teilenummer des Parts.
        doc_code:  Dokumentnummer.
        link_type: 'DescribedBy' (beschreibend) oder 'References' (Referenz).
    """
    t0 = time.monotonic()

    part_raw = client.find_object("part", part_code)
    part_id = extract_id(part_raw)
    if not part_id:
        from src.adapters.base import WRSError
        raise WRSError(f"Part '{part_code}' nicht gefunden", status_code=404)

    doc_raw = client.find_object("document", doc_code)
    doc_id = extract_id(doc_raw)
    if not doc_id:
        from src.adapters.base import WRSError
        raise WRSError(f"Dokument '{doc_code}' nicht gefunden", status_code=404)

    client.link_document_to_part(part_id, doc_id, link_type)
    ms = round((time.monotonic() - t0) * 1000, 1)
    return WriteResponse(
        ok=True,
        objectId=doc_id,
        number=doc_code,
        message=f"Dokument '{doc_code}' mit Part '{part_code}' verknuepft ({link_type})",
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def unlink_document_from_part(
    client: WRSClient,
    part_code: str,
    doc_code: str,
    link_type: str = "DescribedBy",
) -> WriteResponse:
    """Dokument-Verknuepfung von einem Part entfernen."""
    t0 = time.monotonic()

    part_raw = client.find_object("part", part_code)
    part_id = extract_id(part_raw)
    if not part_id:
        from src.adapters.base import WRSError
        raise WRSError(f"Part '{part_code}' nicht gefunden", status_code=404)

    doc_raw = client.find_object("document", doc_code)
    doc_id = extract_id(doc_raw)
    if not doc_id:
        from src.adapters.base import WRSError
        raise WRSError(f"Dokument '{doc_code}' nicht gefunden", status_code=404)

    client.unlink_document_from_part(part_id, doc_id, link_type)
    ms = round((time.monotonic() - t0) * 1000, 1)
    return WriteResponse(
        ok=True,
        objectId=doc_id,
        number=doc_code,
        message=f"Verknuepfung von '{doc_code}' zu '{part_code}' entfernt ({link_type})",
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


# ── Downstream / Equivalence Links (BALDOWNSTREAM IBA) ──────


def _parse_downstream_entries(value: str) -> list[dict[str, str]]:
    """Parse BALDOWNSTREAM into structured entries.

    BALDOWNSTREAM format:
      "NUMBER, NAME, ORG, VERSION (VIEW), NUMBER, NAME, ORG, VERSION (VIEW), ..."
    Each entry is a group of 4 comma-separated tokens.
    Returns list of dicts with keys: number, name, organization, versionView.
    """
    if not value or value.startswith("<list:0"):
        return []

    parts = [s.strip() for s in value.split(",")]
    entries: list[dict[str, str]] = []
    i = 0
    while i + 3 < len(parts):
        entries.append({
            "number": parts[i],
            "name": parts[i + 1],
            "organization": parts[i + 2],
            "versionView": parts[i + 3],
        })
        i += 4
    return entries


def _build_downstream_string(entries: list[dict[str, str]]) -> str:
    """Build BALDOWNSTREAM string from structured entries."""
    tokens: list[str] = []
    for e in entries:
        tokens.extend([e["number"], e["name"], e["organization"], e["versionView"]])
    return ", ".join(tokens)


def _extract_downstream_raw(raw_part: dict) -> str:
    """Extract BALDOWNSTREAM string from a raw OData part response."""
    val = raw_part.get("BALDOWNSTREAM", "")
    if isinstance(val, list):
        val = ", ".join(str(v) for v in val)
    return str(val) if val else ""


def get_downstream_parts(
    client: WRSClient,
    part_code: str,
) -> list[dict[str, str]]:
    """Get downstream (manufacturing equivalent) parts for a design part.

    Reads the BALDOWNSTREAM IBA and parses it into structured entries.
    """
    raw_part = client.find_object("part", part_code)
    downstream_raw = _extract_downstream_raw(raw_part)
    return _parse_downstream_entries(downstream_raw)


def add_downstream_link(
    client: WRSClient,
    design_part_code: str,
    mfg_part_code: str,
) -> WriteResponse:
    """Add a downstream/equivalence link (Design → Manufacturing).

    Updates the BALDOWNSTREAM IBA on the design part by appending the
    manufacturing part reference in Windchill's format:
      "NUMBER, NAME, ORG, VERSION (VIEW)"
    """
    t0 = time.monotonic()
    from src.adapters.base import WRSError

    # 1. Load design part
    design_raw = client.find_object("part", design_part_code)
    design_id = extract_id(design_raw)
    if not design_id:
        raise WRSError(f"Design Part '{design_part_code}' nicht gefunden", status_code=404)

    # 2. Load manufacturing part
    mfg_raw = client.find_object("part", mfg_part_code)
    mfg_id = extract_id(mfg_raw)
    if not mfg_id:
        raise WRSError(f"Manufacturing Part '{mfg_part_code}' nicht gefunden", status_code=404)

    # 3. Parse current BALDOWNSTREAM
    downstream_raw = _extract_downstream_raw(design_raw)
    entries = _parse_downstream_entries(downstream_raw)

    # 4. Check if already linked
    mfg_number = str(mfg_raw.get("Number", ""))
    if any(e["number"] == mfg_number for e in entries):
        ms = round((time.monotonic() - t0) * 1000, 1)
        return WriteResponse(
            ok=True,
            objectId=mfg_id,
            number=mfg_number,
            message=f"Downstream Link '{mfg_number}' existiert bereits",
            timing=TimingInfo(totalMs=ms, wrsMs=ms),
        )

    # 5. Build new entry from manufacturing part's OData data
    mfg_name = str(mfg_raw.get("Name", ""))
    mfg_org = str(mfg_raw.get("OrganizationName", ""))
    mfg_version = str(mfg_raw.get("Version", ""))
    mfg_view = str(mfg_raw.get("View", ""))
    version_view = f"{mfg_version} ({mfg_view})" if mfg_view else mfg_version

    entries.append({
        "number": mfg_number,
        "name": mfg_name,
        "organization": mfg_org,
        "versionView": version_view,
    })

    # 6. PATCH design part with updated BALDOWNSTREAM
    new_value = _build_downstream_string(entries)
    client.update_object_attributes("part", design_id, {"BALDOWNSTREAM": new_value})

    ms = round((time.monotonic() - t0) * 1000, 1)
    return WriteResponse(
        ok=True,
        objectId=mfg_id,
        number=mfg_number,
        message=f"Downstream Link '{mfg_number}' zu '{design_part_code}' hinzugefuegt",
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def remove_downstream_link(
    client: WRSClient,
    design_part_code: str,
    mfg_part_code: str,
) -> WriteResponse:
    """Remove a downstream/equivalence link from a design part.

    Removes the manufacturing part reference from the BALDOWNSTREAM IBA.
    """
    t0 = time.monotonic()
    from src.adapters.base import WRSError

    # 1. Load design part
    design_raw = client.find_object("part", design_part_code)
    design_id = extract_id(design_raw)
    if not design_id:
        raise WRSError(f"Design Part '{design_part_code}' nicht gefunden", status_code=404)

    # 2. Parse current BALDOWNSTREAM
    downstream_raw = _extract_downstream_raw(design_raw)
    entries = _parse_downstream_entries(downstream_raw)

    # 3. Remove entry matching mfg_part_code
    original_count = len(entries)
    entries = [e for e in entries if e["number"] != mfg_part_code]

    if len(entries) == original_count:
        raise WRSError(
            f"Downstream Link '{mfg_part_code}' nicht gefunden in '{design_part_code}'",
            status_code=404,
        )

    # 4. PATCH design part with updated BALDOWNSTREAM
    new_value = _build_downstream_string(entries)
    client.update_object_attributes("part", design_id, {"BALDOWNSTREAM": new_value})

    ms = round((time.monotonic() - t0) * 1000, 1)
    return WriteResponse(
        ok=True,
        number=mfg_part_code,
        message=f"Downstream Link '{mfg_part_code}' von '{design_part_code}' entfernt",
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )
