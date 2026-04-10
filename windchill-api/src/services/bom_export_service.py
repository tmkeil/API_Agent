"""
Balluff BOM Export — Flache Tabelle fuer SAP-Transfer.
========================================================

Erzeugt den "Balluff BOM Export" als flache Zeilenliste (JSON),
identisch zum CSV-Export der Windchill "Balluff BOM Export"-Funktion.

Jede Zeile ist ein Dict mit den Spalten als Keys, alle Werte als Strings.
Parts (PTp=L) und Dokumente (PTp=D) werden abwechselnd ausgegeben:
  - Fuer jeden Part-Knoten: zuerst der Part, dann seine Dokumente,
    dann rekursiv die BOM-Kinder.
"""

from __future__ import annotations

import logging
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from src.core.odata import extract_id, normalize_item

logger = logging.getLogger(__name__)

_MAX_DEPTH = 50

# ═════════════════════════════════════════════════════════════
# Spalten-Reihenfolge (identisch zum Windchill Balluff BOM Export)
# ═════════════════════════════════════════════════════════════

COLUMNS: list[str] = [
    "Structure Level",
    "LvL",
    "MatScr",
    "MatDest",
    "Plant",
    "DisconType",
    "DisconDate",
    "Subtyp",
    "Made From",
    "Mat/Doc Number",
    "DocType",
    "Version",
    "Description",
    "DocPart",
    "PTp",
    "Formula Key",
    "SAP Downstream",
    "Printing Good",
    "State",
    "Raw Dimension 1",
    "Raw Dimension 2",
    "Raw Dimension 3",
    "Raw Dimension Unit",
    "Raw Material Amount",
    "Raw Material Amount Unit",
    "Raw Material Quantity",
    "Raw Material Quantity Unit",
    "Assembly",
    "Pos",
    "DisconGrp",
    "SuccessGrp",
    "Quantity",
    "Quantity Unit",
    "Reference Designator",
    "ERP Position Text",
    "Parent",
]

# Subtypes die als Collection gelten (werden im Export uebersprungen,
# Kinder werden zum Eltern-Level hochgezogen)
_COLLECTION_SUBTYPES = {"Collection", "BALCOLLECTIONPART"}


# ═════════════════════════════════════════════════════════════
# OData-Value Helper
# ═════════════════════════════════════════════════════════════

def _flat(val: Any) -> str:
    """OData-Wert als flachen String aufloesen."""
    if val is None:
        return ""
    if isinstance(val, dict):
        return str(val.get("Display") or val.get("Value") or "")
    if isinstance(val, list):
        parts = []
        for item in val:
            if isinstance(item, dict):
                parts.append(str(item.get("Value") or item.get("Display") or item))
            else:
                parts.append(str(item))
        return ", ".join(parts) if parts else ""
    if isinstance(val, bool):
        return "true" if val else "false"
    return str(val) if val else ""


def _empty_row() -> dict[str, str]:
    """Leere Zeile mit allen Spalten."""
    return {col: "" for col in COLUMNS}


# ── Version-Formatierung ─────────────────────────────────────
# Windchill Version: "00.1 (Manufacturing)" → nur Major: "00"
# Dokument-Version:  "AB.3" → nur Revision: "AB"

_VERSION_RE = re.compile(r"^([A-Za-z0-9]+)")


def _format_version(raw: dict) -> str:
    """Major-Version extrahieren (ohne Iteration und View-Label)."""
    ver = str(raw.get("Version") or raw.get("VersionID") or "")
    # Alles vor dem ersten Punkt oder Leerzeichen
    m = _VERSION_RE.match(ver.split(".")[0].split("(")[0].strip())
    return m.group(1) if m else ver


# ── Mengeneinheiten-Abkuerzungen ─────────────────────────────
# Windchill OData liefert volle Namen, Balluff-Export nutzt ISO-Kuerzel

_UNIT_MAP: dict[str, str] = {
    "each": "ea",
    "meters": "m",
    "meter": "m",
    "millimeters": "mm",
    "millimeter": "mm",
    "centimeters": "cm",
    "centimeter": "cm",
    "kilograms": "kg",
    "kilogram": "kg",
    "grams": "g",
    "gram": "g",
    "liters": "l",
    "liter": "l",
    "pieces": "pc",
    "piece": "pc",
}


def _abbreviate_unit(unit_str: str) -> str:
    """OData-Einheit in Windchill-Export-Kuerzel umwandeln."""
    return _UNIT_MAP.get(unit_str.lower().strip(), unit_str)


def _format_quantity(val: str) -> str:
    """Menge formatieren: '1.0' → '1', '2.554' bleibt."""
    if not val:
        return val
    try:
        f = float(val)
        if f == int(f):
            return str(int(f))
        return val
    except (ValueError, TypeError):
        return val


# ═════════════════════════════════════════════════════════════
# Made-From / Raw-Dimensions
# ═════════════════════════════════════════════════════════════

_RAW_IBA_MAP = [
    ("BALSAPSTPOROMS1", "Raw Dimension 1"),
    ("BALSAPSTPOROMS2", "Raw Dimension 2"),
    ("BALSAPSTPOROMS3", "Raw Dimension 3"),
    ("BALSAPSTPOROMEI", "Raw Dimension Unit"),
    ("BALSAPSTPOROMEN", "Raw Material Amount"),
    ("BALSAPSTPOROAME", "Raw Material Amount Unit"),
    ("BALSAPSTPOROANZ", "Raw Material Quantity"),
    ("BALSAPSTPOROKME", "Raw Material Quantity Unit"),
]


def _apply_raw_dimensions(row: dict[str, str], part_raw: dict) -> None:
    """Raw-Dimensions-IBAs aus Part-Attributen in die Zeile uebernehmen."""
    for iba_key, col_name in _RAW_IBA_MAP:
        val = part_raw.get(iba_key)
        if val is not None and val != "" and val != []:
            row[col_name] = _flat(val)


# ═════════════════════════════════════════════════════════════
# Zeilen-Builder
# ═════════════════════════════════════════════════════════════

def _build_part_row(
    part_raw: dict,
    depth: int,
    parent_number: str,
    usage_link: dict | None,
    has_children: bool,
) -> dict[str, str]:
    """Eine Part-Zeile (PTp=L) bauen."""
    n = normalize_item(part_raw)
    row = _empty_row()

    row["Structure Level"] = str(depth)
    row["Subtyp"] = _flat(part_raw.get("ObjectType") or part_raw.get("TypeName") or "")
    row["Made From"] = _flat(part_raw.get("BALMADEFROMNUMBER") or "")
    row["Mat/Doc Number"] = n["number"]
    row["Version"] = _format_version(part_raw)
    row["Description"] = n["name"]
    row["DocPart"] = "000"
    row["PTp"] = "L"
    # SAP Downstream ist im Balluff-Export nur fuer Dokumente relevant
    # (BALSAPRELEVANCE = boolean). Parts haben hier keinen Wert.
    row["State"] = n["state"]
    row["Assembly"] = "Yes" if has_children else "No"
    row["Parent"] = parent_number

    # Raw-Dimensions aus Part-IBAs
    _apply_raw_dimensions(row, part_raw)

    # DisconType ist ein PART-Attribut (BAL_SAP_MARA_ZZROLLUSEUAS), kein UsageLink-Attribut
    row["DisconType"] = _flat(part_raw.get("BALSAPMARAZZROLLUSEUAS") or "")

    # Usage-Link-Attribute (nur bei Kindern, nicht Root)
    if usage_link:
        row["Pos"] = _flat(
            usage_link.get("FindNumber")
            or usage_link.get("LineNumber")
            or ""
        )
        qty_raw = _flat(usage_link.get("Quantity") or "")
        row["Quantity"] = _format_quantity(qty_raw)
        unit_raw = _flat(
            usage_link.get("QuantityUnit")
            or usage_link.get("Unit")
            or ""
        )
        row["Quantity Unit"] = _abbreviate_unit(unit_raw)
        # OData-Schema: ReferenceDesignatorRange (nicht ReferenceDesignator)
        row["Reference Designator"] = _flat(
            usage_link.get("ReferenceDesignatorRange")
            or usage_link.get("ReferenceDesignator")
            or ""
        )
        row["Formula Key"] = _flat(usage_link.get("BALSAPFORMULAKEY") or "")
        # OData-Schema: BAL_SAP_STPO_NFEAG → BALSAPSTPONFEAG
        row["DisconDate"] = _flat(usage_link.get("BALSAPSTPONFEAG") or "")
        # OData-Schema: BAL_SAP_STPO_NFGRP → BALSAPSTPONFGRP
        row["DisconGrp"] = _flat(usage_link.get("BALSAPSTPONFGRP") or "")
        row["SuccessGrp"] = _flat(usage_link.get("BALSAPSUCCGRP") or "")
        # OData-Schema: BAL_ERP_BOM_POSITION_TEXT → BALERPBOMPOSITIONTEXT
        row["ERP Position Text"] = _flat(usage_link.get("BALERPBOMPOSITIONTEXT") or "")

    return row


def _build_doc_row(
    doc_raw: dict,
    depth: int,
    parent_number: str,
    *,
    is_cad: bool = False,
) -> dict[str, str]:
    """Eine Dokument-Zeile bauen.

    WTDocuments erhalten PTp='D', CAD-Drawings (EPMDocuments) erhalten leeres PTp.
    """
    n = normalize_item(doc_raw)
    row = _empty_row()

    row["Structure Level"] = str(depth)
    # CAD-Dokumente: "CAD-Document " Prefix fuer den Subtyp (wie Windchill)
    subtyp = _flat(doc_raw.get("ObjectType") or doc_raw.get("TypeName") or "")
    if is_cad and subtyp and not subtyp.startswith("CAD"):
        subtyp = f"CAD-Document {subtyp}"
    row["Subtyp"] = subtyp
    row["Mat/Doc Number"] = n["number"]
    # DocTypeName = Standard-WTDocument-Feld, BAL_DOCUMENT_DOCTYPE = Balluff-IBA
    row["DocType"] = _flat(
        doc_raw.get("DocTypeName")
        or doc_raw.get("BAL_DOCUMENT_DOCTYPE")
        or doc_raw.get("DocType")
        or ""
    )
    row["Version"] = _format_version(doc_raw)
    row["Description"] = n["name"]
    row["DocPart"] = "000"
    row["PTp"] = "" if is_cad else "D"
    # SAP Downstream fuer Dokumente = BAL_SAP_RELEVANCE (boolean)
    row["SAP Downstream"] = _flat(doc_raw.get("BALSAPRELEVANCE") or "")
    # Printing Good existiert nur auf BAL_ENC_DOC_PART (nicht auf WTDocument/EPMDocument)
    # Wird via DescribedBy nicht geladen, daher Fallback auf BALPRINTINGGOOD
    row["Printing Good"] = _flat(doc_raw.get("BALPRINTINGGOOD") or "")
    row["State"] = n["state"]
    row["Parent"] = parent_number

    return row


# ═════════════════════════════════════════════════════════════
# Rekursive BOM-Traversierung
# ═════════════════════════════════════════════════════════════

def _export_node(
    client,
    part_raw: dict,
    depth: int,
    parent_number: str,
    usage_link: dict | None,
    rows: list[dict[str, str]],
    seen: set[str],
) -> None:
    """Part-Knoten + Dokumente + Kinder rekursiv flach exportieren."""
    part_id = extract_id(part_raw)
    number = part_raw.get("Number") or normalize_item(part_raw)["number"]

    # Collection-Parts pruefen (ObjectType oder TypeName)
    obj_type = str(
        part_raw.get("ObjectType")
        or part_raw.get("TypeName")
        or ""
    )
    is_collection = obj_type in _COLLECTION_SUBTYPES

    # ── Daten laden (Dokumente + Kinder parallel) ─────────
    docs: list[dict] = []
    cad_docs: list[dict] = []
    children_links: list = []

    def _load_docs():
        if is_collection:
            return []
        try:
            return client.get_described_documents(part_id, number)
        except Exception:
            return []

    def _load_cad():
        if is_collection:
            return []
        try:
            return client.get_cad_documents(part_id)
        except Exception:
            return []

    def _load_children():
        if depth >= _MAX_DEPTH:
            return []
        if part_id in seen:
            return []
        try:
            return client.get_bom_children(part_id)
        except Exception:
            return []

    with ThreadPoolExecutor(max_workers=3) as pool:
        f_docs = pool.submit(_load_docs)
        f_cad = pool.submit(_load_cad)
        f_children = pool.submit(_load_children)
        docs = f_docs.result()
        cad_docs = f_cad.result()
        children_links = f_children.result()

    # Dokumente deduplizieren — WTDocs und CAD zusammen, nach Nummer sortiert
    seen_doc_ids: set[str] = set()
    all_docs: list[tuple[dict, bool]] = []  # (doc_raw, is_cad)
    for d in (docs or []):
        did = d.get("ID", "")
        if did and did not in seen_doc_ids:
            seen_doc_ids.add(did)
            all_docs.append((d, False))
    for d in (cad_docs or []):
        did = d.get("ID", "")
        if did and did not in seen_doc_ids:
            seen_doc_ids.add(did)
            all_docs.append((d, True))
    # Sortierung nach Dokumentnummer (wie Windchill-Export)
    all_docs.sort(key=lambda x: x[0].get("Number") or normalize_item(x[0])["number"])

    # Kinder aufloesen
    resolved_children: list[tuple[dict, dict]] = []  # (link, child_part)
    if part_id and part_id not in seen:
        seen.add(part_id)
        for link in children_links:
            child = client.resolve_usage_link_child(link)
            if child:
                child_id = extract_id(child)
                if child_id:
                    resolved_children.append((link, child))

    has_children = len(resolved_children) > 0

    if is_collection:
        # ── Collection Part: Zeile UND Dokumente ueberspringen,
        #    Kinder werden auf gleicher Tiefe (depth) weitergefuehrt
        logger.debug(
            "Collection Part %s uebersprungen (Kinder: %d)",
            number, len(resolved_children),
        )
        # Kinder sortieren
        resolved_children.sort(
            key=lambda x: (
                _flat(x[0].get("FindNumber") or x[0].get("LineNumber") or ""),
                x[1].get("Number", ""),
            )
        )
        for link, child in resolved_children:
            _export_node(client, child, depth, number, link, rows, seen)
    else:
        # ── 1. Part-Zeile ────────────────────────────────
        rows.append(_build_part_row(part_raw, depth, parent_number, usage_link, has_children))

        # ── 2. Dokument-Zeilen (alle nach Nummer sortiert) ──
        for doc, cad_flag in all_docs:
            rows.append(_build_doc_row(doc, depth + 1, number, is_cad=cad_flag))

        # ── 3. Kinder rekursiv ───────────────────────────
        resolved_children.sort(
            key=lambda x: (
                _flat(x[0].get("FindNumber") or x[0].get("LineNumber") or ""),
                x[1].get("Number", ""),
            )
        )
        for link, child in resolved_children:
            _export_node(client, child, depth + 1, number, link, rows, seen)

    # Part-ID wieder freigeben (darf in anderen Zweigen nochmal vorkommen)
    if part_id:
        seen.discard(part_id)


# ═════════════════════════════════════════════════════════════
# Public API
# ═════════════════════════════════════════════════════════════

def balluff_bom_export(client, part_number: str) -> dict:
    """Balluff BOM Export fuer ein Part als flache Tabelle.

    Returns:
        Dict mit columns, rows, partNumber, rowCount.
    """
    from src.adapters.base import WRSError

    raw_part = client.find_part(part_number)
    part_id = extract_id(raw_part)
    if not part_id:
        raise WRSError(
            f"Part '{part_number}' nicht gefunden oder ohne ID",
            status_code=404,
        )

    rows: list[dict[str, str]] = []
    seen: set[str] = set()

    _export_node(client, raw_part, 0, "", None, rows, seen)

    n_parts = sum(1 for r in rows if r["PTp"] == "L")
    n_wt_docs = sum(1 for r in rows if r["PTp"] == "D")
    n_cad = len(rows) - n_parts - n_wt_docs
    logger.info(
        "Balluff BOM Export fuer %s: %d Zeilen (%d Parts, %d WTDocs, %d CAD)",
        part_number,
        len(rows),
        n_parts,
        n_wt_docs,
        n_cad,
    )

    return {
        "columns": COLUMNS,
        "rows": rows,
        "partNumber": part_number,
        "rowCount": len(rows),
    }
