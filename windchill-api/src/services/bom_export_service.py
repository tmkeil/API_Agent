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
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from src.core.odata import extract_id, normalize_item
from src.core.odata_fields import F

logger = logging.getLogger(__name__)

_MAX_DEPTH = 50

# ═════════════════════════════════════════════════════════════
# Spalten-Reihenfolge (identisch zum Windchill Balluff BOM Export)
# ═════════════════════════════════════════════════════════════

COLUMNS: list[str] = [
    "Structure Level",
    "LvL",
    "Pos",
    "PTp",
    "Mat/Doc Number",
    "Description",
    "State",
    "Subtyp",
    "SAP Downstream",
    "Assembly",
    "Parent",
    "Made From",
    "MatScr",
    "MatDest",
    "Plant",
    "DisconType",
    "DisconDate",
    "DisconGrp",
    "SuccessGrp",
    "DocPart",
    "DocType",
    "Version",
    "Quantity",
    "Quantity Unit",
    "Reference Designator",
    "ERP Position Text",
    "Raw Dimension 1",
    "Raw Dimension 2",
    "Raw Dimension 3",
    "Raw Dimension Unit",
    "Raw Material Amount",
    "Raw Material Amount Unit",
    "Raw Material Quantity",
    "Raw Material Quantity Unit",
    "Formular Key",
    "Printing Good",
]

# Subtypes die als Collection gelten (werden im Export uebersprungen,
# Kinder werden zum Eltern-Level hochgezogen)
_COLLECTION_SUBTYPES = {"Collection", F.PartSubtype.COLLECTION}


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
    (F.RawMaterialLink.RAW_DIM_1, "Raw Dimension 1"),
    (F.RawMaterialLink.RAW_DIM_2, "Raw Dimension 2"),
    (F.RawMaterialLink.RAW_DIM_3, "Raw Dimension 3"),
    (F.RawMaterialLink.RAW_DIM_UNIT, "Raw Dimension Unit"),
    (F.RawMaterialLink.RAW_AMOUNT, "Raw Material Amount"),
    # Balluff/SAP-Konvention: ROAME (RAW_AMOUNT_UNIT) ist die Einheit der
    # Anzahl (ROANZ), ROKME (RAW_QUANTITY_UNIT) ist die Einheit der Menge
    # (ROMEN) — die Label-Zuordnung wird entsprechend getauscht.
    (F.RawMaterialLink.RAW_QUANTITY_UNIT, "Raw Material Amount Unit"),
    (F.RawMaterialLink.RAW_QUANTITY, "Raw Material Quantity"),
    (F.RawMaterialLink.RAW_AMOUNT_UNIT, "Raw Material Quantity Unit"),
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
    made_from_link: dict | None = None,
) -> dict[str, str]:
    """Eine Part-Zeile (PTp=L) bauen.

    Datenquellen:
      part_raw        → WTPart OData-Record (Part-Attribute)
      usage_link      → PTC.ProdMgmt.PartUse (BOM-Beziehung Parent→Child)
      made_from_link  → PTC.BomTransformation.RawMaterialLink (Made-From-Beziehung)
      normalize_item  → Standard-Felder (number, name, state)
    """
    n = normalize_item(part_raw)
    row = _empty_row()

    # ── Struktur / Metadaten ──────────────────────────────
    row["Structure Level"] = str(depth)
    row["PTp"] = "L"
    row["DocPart"] = "000"
    row["Assembly"] = "Yes" if has_children else "No"
    row["Parent"] = parent_number

    # ── Quelle: WTPart (part_raw) ─────────────────────────
    row["Subtyp"] = _flat(part_raw.get("ObjectType") or part_raw.get("TypeName") or "")
    row["Made From"] = _flat(part_raw.get(F.Part.MADE_FROM_NUMBER) or "")
    row["Mat/Doc Number"] = n["number"]
    row["Version"] = _format_version(part_raw)
    row["Description"] = n["name"]
    row["State"] = n["state"]
    row["DisconType"] = _flat(part_raw.get(F.Part.DISCON_TYPE) or "")
    # Printing Good liegt auf dem Part-Subtyp "Enclosed Documentation" (BALENCDOCPART),
    # nicht auf dem Dokument. Wir lesen es daher auch aus part_raw.
    row["Printing Good"] = _flat(part_raw.get(F.Part.PRINTING_GOOD) or "")

    # ── Quelle: WTPart — Raw-Dimensions (Part-IBAs) ──────
    _apply_raw_dimensions(row, part_raw)

    # ── Quelle: PartUse / UsageLink (nur bei Kindern) ────
    if usage_link:
        row["Pos"] = _flat(
            usage_link.get(F.UsageLink.FIND_NUMBER)
            or usage_link.get(F.UsageLink.LINE_NUMBER)
            or ""
        )
        qty_raw = _flat(usage_link.get(F.UsageLink.QUANTITY) or "")
        row["Quantity"] = _format_quantity(qty_raw)
        unit_raw = _flat(
            usage_link.get(F.UsageLink.QUANTITY_UNIT)
            or usage_link.get(F.UsageLink.UNIT)
            or ""
        )
        row["Quantity Unit"] = _abbreviate_unit(unit_raw)
        row["Reference Designator"] = _flat(
            usage_link.get(F.UsageLink.REF_DESIGNATOR_RANGE)
            or usage_link.get(F.UsageLink.REF_DESIGNATOR)
            or ""
        )
        row["DisconDate"] = _flat(usage_link.get(F.UsageLink.DISCON_DATE) or "")
        row["DisconGrp"] = _flat(usage_link.get(F.UsageLink.DISCON_GRP) or "")
        row["SuccessGrp"] = ""  # Existiert nicht im OData-Schema
        row["ERP Position Text"] = _flat(usage_link.get(F.UsageLink.ERP_POSITION_TEXT) or "")

    # ── Quelle: RawMaterialLink (Made-From-Beziehung) ────
    if made_from_link:
        row["Formular Key"] = _flat(made_from_link.get(F.RawMaterialLink.FORMULA_KEY) or "")

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

    Datenquelle: Ausschliesslich doc_raw (WTDocument/EPMDocument OData-Record).
    """
    n = normalize_item(doc_raw)
    row = _empty_row()

    # ── Struktur / Metadaten ──────────────────────────────
    row["Structure Level"] = str(depth)
    row["DocPart"] = "000"
    row["Parent"] = parent_number

    # ── Quelle: WTDocument / EPMDocument (doc_raw) ────────
    subtyp = _flat(doc_raw.get("ObjectType") or doc_raw.get("TypeName") or "")
    if is_cad and subtyp and not subtyp.startswith("CAD"):
        subtyp = f"CAD-Document {subtyp}"
    row["Subtyp"] = subtyp
    row["Mat/Doc Number"] = n["number"]
    # DocType: BALDOCUMENTTYPE EnumType → kurzer Value-Code (DOK, QEP, DRW, DRF, ...)
    # WTDocuments liefern EnumType-Dict {"Value": "DOK", "Display": "DOK - Technical documents"}
    # CAD EPMDocuments liefern oft nur den Display-String ("DRW - Material documents")
    doc_type_raw = doc_raw.get(F.Doc.DOC_TYPE)
    if isinstance(doc_type_raw, dict):
        row["DocType"] = str(doc_type_raw.get("Value") or "")
    elif doc_type_raw:
        # Plain-String: Short-Code vor " - " extrahieren (z.B. "DRW - Material documents" → "DRW")
        s = str(doc_type_raw).strip()
        row["DocType"] = s.split(" - ")[0].strip() if " - " in s else s
    else:
        row["DocType"] = ""

    row["PTp"] = "D"
    row["Version"] = _format_version(doc_raw)
    row["Description"] = n["name"]
    row["SAP Downstream"] = _flat(doc_raw.get(F.Doc.SAP_RELEVANCE) or "")
    row["Printing Good"] = _flat(doc_raw.get(F.Doc.PRINTING_GOOD) or "")
    row["State"] = n["state"]

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
    max_depth: int = _MAX_DEPTH,
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

    # ── Daten laden (Dokumente + Kinder + MadeFrom parallel) ──
    docs: list[dict] = []
    cad_docs: list[dict] = []
    children_links: list = []
    made_from_links: list[dict] = []

    # Made-From nur laden wenn Part ein BALMADEFROMNUMBER hat
    has_made_from = bool(part_raw.get(F.Part.MADE_FROM_NUMBER))

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
        if part_id in seen:
            return []
        try:
            return client.get_bom_children(part_id)
        except Exception:
            return []

    def _load_made_from():
        if not has_made_from or is_collection:
            return []
        try:
            return client.get_made_from_links(part_id)
        except Exception:
            return []

    with ThreadPoolExecutor(max_workers=4) as pool:
        f_docs = pool.submit(_load_docs)
        f_cad = pool.submit(_load_cad)
        f_children = pool.submit(_load_children)
        f_mf = pool.submit(_load_made_from)
        docs = f_docs.result()
        cad_docs = f_cad.result()
        children_links = f_children.result()
        made_from_links = f_mf.result()

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

    # Kinder aufloesen (parallel — resolve_usage_link_child ist 1 OData-Call pro Kind)
    resolved_children: list[tuple[dict, dict]] = []  # (link, child_part)
    if part_id and part_id not in seen:
        seen.add(part_id)
        if children_links:
            def _resolve(link: dict) -> tuple[dict, dict | None]:
                try:
                    return link, client.resolve_usage_link_child(link)
                except Exception:
                    return link, None

            # Reihenfolge der Kinder beibehalten → results_by_index
            results_by_index: dict[int, tuple[dict, dict | None]] = {}
            with ThreadPoolExecutor(max_workers=8) as pool:
                futures = {
                    pool.submit(_resolve, lk): idx
                    for idx, lk in enumerate(children_links)
                }
                for fut in as_completed(futures):
                    idx = futures[fut]
                    results_by_index[idx] = fut.result()

            for idx in sorted(results_by_index.keys()):
                link, child = results_by_index[idx]
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
            _export_node(client, child, depth, number, link, rows, seen, max_depth)
    else:
        # ── 1. Part-Zeile ────────────────────────────────
        # Erstes RawMaterialLink-Objekt (fuer Formular Key + ggf. Raw Dimensions)
        mf_link = made_from_links[0] if made_from_links else None
        rows.append(_build_part_row(part_raw, depth, parent_number, usage_link, has_children, mf_link))

        # ── 2. Dokument-Zeilen (nur unterhalb max_depth, da Docs bei depth+1 liegen)
        if depth < max_depth:
            for doc, cad_flag in all_docs:
                rows.append(_build_doc_row(doc, depth + 1, number, is_cad=cad_flag))

        # ── 3. Kinder rekursiv (nur unterhalb max_depth) ──
        if depth < max_depth:
            resolved_children.sort(
                key=lambda x: (
                    _flat(x[0].get("FindNumber") or x[0].get("LineNumber") or ""),
                    x[1].get("Number", ""),
                )
            )
            for link, child in resolved_children:
                _export_node(client, child, depth + 1, number, link, rows, seen, max_depth)

    # Part-ID wieder freigeben (darf in anderen Zweigen nochmal vorkommen)
    if part_id:
        seen.discard(part_id)


# ═════════════════════════════════════════════════════════════
# Public API
# ═════════════════════════════════════════════════════════════

def balluff_bom_export(client, part_number: str, max_depth: int | None = None) -> dict:
    """Balluff BOM Export fuer ein Part als flache Tabelle.

    Args:
        client: WRS Client.
        part_number: Windchill Part-Nummer.
        max_depth: Maximale BOM-Tiefe (None = unbegrenzt, Standard: 50).

    Returns:
        Dict mit columns, rows, partNumber, rowCount.
    """
    from src.adapters.base import WRSError

    effective_depth = max_depth if max_depth is not None else _MAX_DEPTH

    raw_part = client.find_part(part_number)
    part_id = extract_id(raw_part)
    if not part_id:
        raise WRSError(
            f"Part '{part_number}' nicht gefunden oder ohne ID",
            status_code=404,
        )

    rows: list[dict[str, str]] = []
    seen: set[str] = set()

    _export_node(client, raw_part, 0, "", None, rows, seen, effective_depth)

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
