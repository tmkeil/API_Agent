"""
SAP Export Service — Aufbereitung des Balluff BOM Exports fuer SAP-Import.
==========================================================================

Portiert die VBA-Tool-Logik (PartA → PartB → PartC → PartD) in Python:

  PartA: Daten-Transformation (Printing-Good-Regel, Prefix-Entfernung,
         Reference-Designator-Expansion, PosText-Bildung)
  PartB: Validierung (Geschaeftsregeln pruefen)
  PartC: SAP-Schema-Transformation (nur Pos-Zeilen, Spaltenumbenennung,
         Einheiten-Konvertierung)
  PartD: Split nach Parent+StructureLevel in separate CSV-Dateien

Input:  Rohdaten aus balluff_bom_export() (columns + rows)
Output: Validierungsmeldungen + aufbereitete CSV-Dateien
"""

from __future__ import annotations

import csv
import io
import logging
import re
from collections import OrderedDict
from typing import Any

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════

def _norm(x: Any) -> str:
    """Wert normalisieren: None/NaN/leer → ''."""
    if x is None:
        return ""
    s = str(x).strip()
    if s.lower() in ("", "none", "nan", "#nv", "<na>", "nat"):
        return ""
    return s


def _filled(x: Any) -> bool:
    return _norm(x) != ""


# ═════════════════════════════════════════════════════════════
# PartA: Daten-Transformation
# ═════════════════════════════════════════════════════════════

# ── Reference Designator Expansion ───────────────────────────
# z.B. "A1-A5" → "A1,A2,A3,A4,A5"
# z.B. "A1,B3-B5" → "A1,B3,B4,B5"

_RANGE_RE = re.compile(
    r"([A-Za-z]+)\s*(\d+)\s*-\s*([A-Za-z]+)\s*(\d+)"
)
_SINGLE_RE = re.compile(r"([A-Za-z]+)\s*(\d+)")
_BRACKET_NUM_RE = re.compile(r"\[\s*\d+\s*-\s*\d+\s*\]")


def _expand_token(token: str) -> list[str]:
    """Einzelnen RD-Token expandieren (z.B. 'A1-A5' → ['A1','A2','A3','A4','A5'])."""
    token = token.strip()
    if not token:
        return []
    m = _RANGE_RE.fullmatch(token)
    if m:
        prefix1, start_s, prefix2, end_s = m.groups()
        if prefix1.upper() != prefix2.upper():
            return [token]
        start, end = int(start_s), int(end_s)
        r = range(start, end + 1) if start <= end else range(start, end - 1, -1)
        return [f"{prefix1.upper()}{i}" for i in r]
    m2 = _SINGLE_RE.fullmatch(token)
    if m2:
        prefix, num = m2.groups()
        return [f"{prefix.upper()}{int(num)}"]
    return [token]


def _expand_reference_designator(rd: str) -> str:
    """Reference Designator vollstaendig expandieren und deduplizieren."""
    if not _filled(rd):
        return ""
    # Semikolons durch Kommas ersetzen
    rd = rd.replace(";", ",")
    tokens = [t.strip() for t in rd.split(",") if t.strip()]
    expanded: list[str] = []
    for tok in tokens:
        expanded.extend(_expand_token(tok))
    # Normalisieren und deduplizieren (Reihenfolge beibehalten)
    normalized = [_norm(x).replace(" ", "") for x in expanded if _norm(x)]
    deduped = list(OrderedDict.fromkeys(normalized))
    return ",".join(deduped)


def _strip_bracket_numbers(text: str) -> str:
    """[12345-1] Pattern aus String entfernen."""
    if not _filled(text):
        return ""
    s = _BRACKET_NUM_RE.sub("", str(text))
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s*,\s*", ",", s)
    return s.strip(", ")


def _strip_7000_prefix(number: str) -> str:
    """'7000'-Prefix und 'S+4 alphanumerische Zeichen'-Prefix entfernen."""
    s = _norm(number)
    if not s:
        return ""
    # 7000-Prefix entfernen
    s = re.sub(r"^7000", "", s)
    # S + 4 alphanumerische Zeichen Prefix entfernen
    s = re.sub(r"^S[A-Za-z0-9]{4}", "", s)
    return s.strip()


# ── Printing Good Normalisierung ─────────────────────────────

_PG_MAP = {
    "yes": "YES", "no": "NO", "true": "YES", "false": "NO",
    "1": "YES", "0": "NO", "ja": "YES", "nein": "NO",
}


def _normalize_printing_good(val: str) -> str:
    return _PG_MAP.get(_norm(val).lower(), _norm(val).upper())


def part_a(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """PartA: Daten-Transformation.

    - Mat/Doc Number: 7000/S+4-Prefix entfernen
    - Parent auf Level 0 leeren
    - Printing Good Regel: Enclosed Documentation mit PG=NO entfernen,
      erstes 'Customer related document' Kind hochziehen
    - PosText bilden (Reference Designator + ERP Position Text)
    - Reference Designator expandieren
    - [12345-1] aus Reference Designator entfernen
    """
    result = [dict(r) for r in rows]  # Deep copy

    # 1) Mat/Doc Number: Prefixe entfernen
    for r in result:
        if _filled(r.get("Mat/Doc Number")):
            r["Mat/Doc Number"] = _strip_7000_prefix(r["Mat/Doc Number"])

    # 2) Parent auf Level 0 leeren
    for r in result:
        if _norm(r.get("Structure Level")) == "0":
            r["Parent"] = ""

    # 3) Printing Good Regel
    # Printing Good Werte normalisieren
    for r in result:
        if "Printing Good" in r:
            r["Printing Good"] = _normalize_printing_good(r.get("Printing Good", ""))

    # Enclosed Documentation mit PG=NO: Zeile entfernen + erstes Customer
    # Related Document Kind auf gleiche Ebene hochziehen
    rows_to_drop: list[int] = []
    for i in range(len(result)):
        subtyp = _norm(result[i].get("Subtyp"))
        pg = _norm(result[i].get("Printing Good"))
        if subtyp == "Enclosed Documentation" and pg == "NO":
            parent_val = _norm(result[i].get("Parent"))
            sl = _norm(result[i].get("Structure Level"))
            try:
                ed_level = int(sl)
            except (ValueError, TypeError):
                ed_level = 0
            first_found = False
            for ni in range(i + 1, len(result)):
                next_subtyp = _norm(result[ni].get("Subtyp"))
                next_sl = _norm(result[ni].get("Structure Level"))
                try:
                    next_level = int(next_sl)
                except (ValueError, TypeError):
                    continue
                if next_level <= ed_level:
                    break
                if next_subtyp == "Customer related document" and next_level > ed_level:
                    if not first_found:
                        result[ni]["Parent"] = parent_val
                        result[ni]["Structure Level"] = sl
                        first_found = True
                    else:
                        result[ni]["Parent"] = parent_val
            rows_to_drop.append(i)

    # Zeilen entfernen (von hinten nach vorne)
    for idx in reversed(rows_to_drop):
        result.pop(idx)

    # Printing Good Spalte entfernen (nicht mehr benoetigt)
    for r in result:
        r.pop("Printing Good", None)

    # 4) PosText bilden + Reference Designator expandieren
    for r in result:
        rd = _norm(r.get("Reference Designator"))
        erp = _norm(r.get("ERP Position Text"))
        # Bracket Numbers entfernen
        rd = _strip_bracket_numbers(rd)
        # Expandieren
        rd_expanded = _expand_reference_designator(rd)
        r["Reference Designator"] = rd_expanded
        # PosText = expandierter RD + ERP Position Text
        parts = [rd_expanded, erp]
        r["PosText"] = " ".join(p for p in parts if p).strip()

    return result


# ═════════════════════════════════════════════════════════════
# PartB: Validierung
# ═════════════════════════════════════════════════════════════

_RAW_FIELDS = [
    "Raw Dimension 1", "Raw Dimension 2", "Raw Dimension 3",
    "Raw Dimension Unit",
]

_OK_STATES = {"RELEASED", "PUBLISHED"}


def part_b(rows: list[dict[str, str]]) -> list[str]:
    """PartB: Validierungsregeln pruefen.

    Prueft NUR Zeilen mit Structure Level >= 1.
    Returns: Liste von Validierungs-Fehlermeldungen (leer = alles OK).
    """
    issues: list[str] = []

    for i, r in enumerate(rows):
        row_num = i + 2  # +1 fuer 0-Index, +1 fuer Header
        sl = _norm(r.get("Structure Level"))
        if sl == "" or sl == "0":
            continue  # Level 0 nicht validieren

        # [Regel] Made From → mind. ein RAW-Feld muss befuellt sein
        if _filled(r.get("Made From")):
            has_raw = any(_filled(r.get(f)) for f in _RAW_FIELDS)
            if not has_raw:
                issues.append(
                    f"Zeile {row_num}: 'Made From' ist gesetzt, aber kein "
                    f"RAW-Dimension-Feld/Einheit ist befuellt."
                )

        # [Regel] Pos gesetzt → State muss RELEASED oder PUBLISHED sein
        if _filled(r.get("Pos")):
            state = _norm(r.get("State")).upper()
            if state not in _OK_STATES:
                issues.append(
                    f"Zeile {row_num}: Pos gesetzt, aber State='{r.get('State')}' "
                    f"(nicht RELEASED/PUBLISHED)."
                )

        # [Regel] Kein Collection-Eintrag mit gesetzter Pos
        if _filled(r.get("Pos")):
            subtyp = _norm(r.get("Subtyp")).lower()
            if "collection" in subtyp:
                issues.append(
                    f"Zeile {row_num}: 'Collection'-Eintrag mit gesetzter Pos "
                    f"ist nicht erlaubt."
                )

        # [Regel] PTp=D → DocPart/DocType/Version muessen vollstaendig sein
        if _norm(r.get("PTp")).upper() == "D":
            doc_fields = ["DocPart", "DocType", "Version"]
            if not all(_filled(r.get(f)) for f in doc_fields):
                issues.append(
                    f"Zeile {row_num}: PTp='D', aber DocPart/DocType/Version "
                    f"unvollstaendig."
                )

        # [Regel] PTp=L oder R → Quantity und Quantity Unit muessen befuellt sein
        ptp = _norm(r.get("PTp")).upper()
        if ptp in ("L", "R"):
            qty_fields = ["Quantity", "Quantity Unit"]
            if not all(_filled(r.get(f)) for f in qty_fields):
                issues.append(
                    f"Zeile {row_num}: PTp='{r.get('PTp')}', aber "
                    f"'Quantity' und/oder 'Quantity Unit' fehlt."
                )

    return issues


# ═════════════════════════════════════════════════════════════
# PartC: SAP-Schema-Transformation
# ═════════════════════════════════════════════════════════════

# SAP-Spaltennamen-Mapping (Export-Header → SAP-technischer Name)
_SAP_HEADER_MAP = {
    "Raw Material Amount": "ROMEN_BI",
    "Raw Material Quantity": "ROANZ_BI",
    "Raw Dimension 1": "ROMS1_BI",
    "Raw Dimension 2": "ROMS2_BI",
    "Raw Dimension 3": "ROMS3_BI",
    "Raw Dimension Unit": "ROMEI",
    "Formular Key": "RFORM",
    "Raw Material Amount Unit": "ROKME",
    "Version": "DocVersion",
    "Quantity Unit": "MEINS",
}

# SAP Ziel-Spaltenreihenfolge
_SAP_TARGET_COLUMNS = [
    "MatScr", "MatDest", "Plant", "DisconType", "DisconDate",
    "DisconGrp", "SuccessGrp", "Pos", "PTp", "Mat/Doc Number",
    "DocType", "DocPart", "DocVersion", "Description", "Quantity",
    "MEINS", "PosText", "ROMEN_BI", "ROANZ_BI", "ROMS1_BI",
    "ROMS2_BI", "ROMS3_BI", "ROMEI", "RFORM", "ROKME",
]

# Einheiten-Spalten die UPPERCASE sein muessen
_UNIT_COLUMNS = {
    "MEINS", "ROMEI", "ROMEN_BI", "ROANZ_BI", "ROMS1_BI",
    "ROMS2_BI", "ROMS3_BI", "RFORM", "ROKME",
}


def part_c(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """PartC: SAP-Schema-Transformation.

    - Nur Zeilen mit gesetzter Pos behalten
    - DocType leer → DocPart/Version leeren
    - Made From → Mat/Doc Number ueberschreiben
    - 'ea' → 'ST' (Einheiten-Konvertierung)
    - Spalten umbenennen (SAP-technische Namen)
    - SAP-Zielschema anwenden (Spaltenreihenfolge)
    - Einheiten in GROSSBUCHSTABEN
    """
    result: list[dict[str, str]] = []

    for r in rows:
        # Nur Zeilen mit Pos behalten
        if not _filled(r.get("Pos")):
            continue

        row = dict(r)

        # DocType leer → DocPart/Version leeren
        if not _filled(row.get("DocType")):
            row["DocPart"] = ""
            row["Version"] = ""

        # DocType auf 3 Zeichen kuerzen (z.B. "DOK - xyz" → "DOK")
        doc_type = _norm(row.get("DocType"))
        if len(doc_type) > 3:
            row["DocType"] = doc_type[:3]

        # Made From → Mat/Doc Number ueberschreiben
        if _filled(row.get("Made From")):
            row["Mat/Doc Number"] = _norm(row["Made From"])

        # Einheiten: 'ea' → 'ST'
        for col in ("Quantity Unit", "Raw Material Amount Unit",
                     "Raw Material Quantity Unit"):
            if _norm(row.get(col, "")).lower() == "ea":
                row[col] = "ST"

        # Spalten umbenennen
        renamed: dict[str, str] = {}
        for old_key, val in row.items():
            new_key = _SAP_HEADER_MAP.get(old_key, old_key)
            renamed[new_key] = val

        # SAP-Zielschema: nur Zielspalten, in der richtigen Reihenfolge
        sap_row: dict[str, str] = {}
        for col in _SAP_TARGET_COLUMNS:
            sap_row[col] = _norm(renamed.get(col, ""))

        # Einheiten UPPERCASE
        for col in _UNIT_COLUMNS:
            if col in sap_row and sap_row[col]:
                sap_row[col] = sap_row[col].upper()

        # Structure Level und Parent mitspeichern (fuer PartD-Split)
        sap_row["_structure_level"] = _norm(row.get("Structure Level", "0"))
        sap_row["_parent"] = _norm(row.get("Parent", ""))

        result.append(sap_row)

    return result


# ═════════════════════════════════════════════════════════════
# PartD: Split nach Parent + Structure Level → CSV-Dateien
# ═════════════════════════════════════════════════════════════

_S4_PREFIX_RE = re.compile(r"^S[A-Za-z0-9]{4}")
_BAD_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|]')


def _strip_s4_prefix(name: str) -> str:
    """S + 4 alphanumerische Zeichen Prefix aus Dateinamen entfernen."""
    name = name.strip()
    if len(name) >= 5 and name[0].upper() == "S":
        four = name[1:5].upper()
        if all(c.isalnum() for c in four):
            return name[5:]
    return name


def _sanitize_filename(name: str) -> str:
    """Ungueltige Zeichen aus Dateinamen ersetzen."""
    result = _BAD_FILENAME_CHARS.sub("_", name.strip())
    return result[:200] if result else "UNKNOWN"


def part_d(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """PartD: Split in separate CSV-Dateien pro Parent + Structure Level.

    Returns:
        Liste von Dicts mit 'filename' und 'content' (CSV als String).
    """
    # Gruppen ermitteln: Parent + Structure Level
    groups: dict[str, list[dict[str, str]]] = {}

    for r in rows:
        parent = r.get("_parent", "")
        sl = r.get("_structure_level", "0")

        # Zeilen ohne Parent oder mit Level 0 ueberspringen
        if not parent or sl == "0":
            continue

        key = f"{parent}|LEVEL{sl}"
        if key not in groups:
            groups[key] = []
        groups[key].append(r)

    # CSV-Spalten (ohne interne Felder)
    csv_columns = [c for c in _SAP_TARGET_COLUMNS]

    files: list[dict[str, str]] = []
    for key, group_rows in sorted(groups.items()):
        parent_part, level_part = key.split("|", 1)

        # CSV generieren
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(csv_columns)
        for r in group_rows:
            writer.writerow([r.get(c, "") for c in csv_columns])
        csv_content = output.getvalue()

        # Dateiname: Parent (ohne S4-Prefix) + Level
        base_name = _strip_s4_prefix(parent_part)
        safe_name = _sanitize_filename(base_name)
        if not safe_name:
            safe_name = "UNKNOWN_PARENT"
        filename = f"{safe_name}_{level_part}.csv"

        files.append({
            "filename": filename,
            "content": csv_content,
        })

    return files


# ═════════════════════════════════════════════════════════════
# Public API: Kompletter SAP-Export
# ═════════════════════════════════════════════════════════════

def sap_preview(raw_export: dict) -> dict:
    """SAP Preview — nur PartA (Transformation) + PartB (Validierung).

    Wird beim Oeffnen des Modals automatisch im Hintergrund aufgerufen.
    Liefert die transformierten Daten fuer den "SAP Vorschau"-Tab.

    Args:
        raw_export: Ergebnis von balluff_bom_export() mit columns + rows.

    Returns:
        Dict mit columns, rows, validation, stats.
    """
    raw_rows = raw_export.get("rows", [])
    part_number = raw_export.get("partNumber", "")

    # ── PartA: Transformation ────────────────────────────
    transformed = part_a(raw_rows)
    logger.info("SAP Preview %s: PartA fertig — %d → %d Zeilen",
                part_number, len(raw_rows), len(transformed))

    # ── PartB: Validierung ───────────────────────────────
    validation = part_b(transformed)
    logger.info("SAP Preview %s: PartB fertig — %d Validierungsmeldungen",
                part_number, len(validation))

    # Spalten aus erster Zeile ableiten
    columns = list(transformed[0].keys()) if transformed else []

    return {
        "columns": columns,
        "rows": transformed,
        "validation": validation,
        "stats": {
            "totalInputRows": len(raw_rows),
            "totalOutputRows": len(transformed),
            "removedRows": len(raw_rows) - len(transformed),
        },
    }


def sap_export(raw_export: dict) -> dict:
    """Kompletter SAP-Export-Workflow.

    Args:
        raw_export: Ergebnis von balluff_bom_export() mit columns + rows.
                    Wenn fromPreview=True, wird PartA uebersprungen (Daten
                    sind bereits transformiert/editiert).

    Returns:
        Dict mit:
          - validation: Liste von Validierungs-Fehlermeldungen
          - files: Liste von {filename, content} Dicts
          - stats: {totalInputRows, totalOutputRows, filesCount, skippedRows}
    """
    raw_rows = raw_export.get("rows", [])
    part_number = raw_export.get("partNumber", "")
    from_preview = raw_export.get("fromPreview", False)

    # ── PartA: Transformation (ggf. ueberspringen) ──────
    if from_preview:
        transformed = raw_rows
        logger.info("SAP Export %s: PartA uebersprungen (fromPreview)",
                    part_number)
    else:
        transformed = part_a(raw_rows)
        logger.info("SAP Export %s: PartA fertig — %d → %d Zeilen",
                    part_number, len(raw_rows), len(transformed))

    # ── PartB: Validierung ───────────────────────────────
    validation = part_b(transformed)
    logger.info("SAP Export %s: PartB fertig — %d Validierungsmeldungen",
                part_number, len(validation))

    # ── PartC: SAP-Schema ────────────────────────────────
    sap_rows = part_c(transformed)
    logger.info("SAP Export %s: PartC fertig — %d → %d SAP-Zeilen",
                part_number, len(transformed), len(sap_rows))

    # ── PartD: Split in CSV-Dateien ──────────────────────
    files = part_d(sap_rows)
    logger.info("SAP Export %s: PartD fertig — %d CSV-Dateien",
                part_number, len(files))

    return {
        "validation": validation,
        "files": files,
        "stats": {
            "totalInputRows": len(raw_rows),
            "totalOutputRows": len(sap_rows),
            "filesCount": len(files),
            "skippedRows": len(transformed) - len(sap_rows),
        },
    }
