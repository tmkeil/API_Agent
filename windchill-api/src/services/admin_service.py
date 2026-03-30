"""
Business logic for administrative endpoints: BOM export & performance benchmark.

Extracted from routers/admin.py so that the router only handles HTTP concerns
(request parsing, auth, response formatting) while this module owns the logic.
"""

import copy
import datetime
import json
import logging
import os
import time
from collections import OrderedDict

from src.core.odata import WcType, extract_id, normalize_item
from src.models.dto import BenchmarkResponse, BenchmarkResult
from src.services import parts_service

logger = logging.getLogger(__name__)

# ── Export directory (sibling to the project root) ───────────

_EXPORT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "exports",
)


# ── BOM Export ───────────────────────────────────────────────


def _export_doc_node(doc: dict, doc_type: str = WcType.DOCUMENT) -> OrderedDict:
    """Export a document/CAD node with ALL its attributes."""
    result = OrderedDict()
    result["type"] = doc.get("type", doc_type)
    result["number"] = doc.get("number", "")
    result["name"] = doc.get("name", "")
    result["version"] = doc.get("version", "")
    result["state"] = doc.get("state", "")
    # Include any extra attributes the doc may carry
    for k, v in doc.items():
        if k in ("type", "number", "name", "version", "state", "docId"):
            continue
        if v is not None and v != "" and v != []:
            result[k] = v
    return result


def _build_made_from(part_attrs: dict) -> OrderedDict | None:
    """Extract Made From relationship data from part attributes."""
    mf_number = part_attrs.get("BALMADEFROMNUMBER", "")
    if not mf_number or mf_number == "<list:0 items>":
        return None
    raw_fields = OrderedDict()
    raw_fields["made_from_number"] = mf_number
    # Raw dimension fields
    _RAW_KEYS = [
        ("BALSAPSTPOROMS1", "raw_dimension_1"),
        ("BALSAPSTPOROMS2", "raw_dimension_2"),
        ("BALSAPSTPOROMS3", "raw_dimension_3"),
        ("BALSAPSTPOROMEI", "raw_dimension_unit"),
        ("BALSAPSTPOROMEN", "raw_material_amount"),
        ("BALSAPSTPOROAME", "raw_material_amount_unit"),
        ("BALSAPSTPOROANZ", "raw_material_quantity"),
        ("BALSAPSTPOROKME", "raw_material_quantity_unit"),
    ]
    for odata_key, export_key in _RAW_KEYS:
        val = part_attrs.get(odata_key)
        if val is not None and val != "" and val != []:
            raw_fields[export_key] = val
    return raw_fields


def frontend_tree_to_export(node: dict, _depth: int = 0) -> OrderedDict:
    """Convert a camelCase frontend BOM tree node to export format with ALL attributes.

    Raises:
        ValueError: If tree depth exceeds 200 levels (cycle protection).
    """
    if _depth > 200:
        raise ValueError("Baumstruktur ist zu tief verschachtelt (max. 200 Ebenen)")

    children = [frontend_tree_to_export(child, _depth + 1) for child in node.get("children", [])]

    documents = [_export_doc_node(doc, WcType.DOCUMENT) for doc in node.get("documents", [])]
    cad_documents = [_export_doc_node(doc, WcType.CAD_DOCUMENT) for doc in node.get("cadDocuments", [])]

    has_children = len(children) > 0 or bool(node.get("hasChildren"))
    part_attrs = node.get("partAttributes") or {}
    usage_attrs = node.get("usageLinkAttributes") or {}

    result = OrderedDict()
    result["type"] = node.get("type", WcType.PART)
    result["number"] = node.get("number", "")
    result["name"] = node.get("name", "")
    result["version"] = node.get("version", "")
    result["iteration"] = node.get("iteration", "")
    result["state"] = node.get("state", "")
    result["identity"] = node.get("identity", "")

    # Part attributes (SAP, Description, View, Source, etc.)
    if part_attrs:
        result["part_attributes"] = part_attrs

    # Usage link / BOM position data
    result["line_number"] = node.get("lineNumber", "")
    result["quantity"] = node.get("quantity")
    result["quantity_unit"] = node.get("quantityUnit", "")
    if usage_attrs:
        result["usage_link_attributes"] = usage_attrs

    # Made From relationship
    made_from = _build_made_from(part_attrs)
    if made_from:
        result["made_from"] = made_from

    result["children_type"] = "subassembly" if has_children else "leaf part"
    result["documents"] = documents
    result["cad_documents"] = cad_documents
    result["children"] = children

    return result


def count_tree_stats(tree: dict) -> dict:
    """Count parts, documents, CAD documents, referenced-by, made-from in an export tree."""
    parts = 1
    docs = len(tree.get("documents", []))
    cads = len(tree.get("cad_documents", []))
    refs = len(tree.get("referenced_by_documents", []))
    mf = 1 if tree.get("made_from") else 0
    for child in tree.get("children", []):
        sub = count_tree_stats(child)
        parts += sub["parts"]
        docs += sub["documents"]
        cads += sub["cad_documents"]
        refs += sub["referenced_by_documents"]
        mf += sub["made_from"]
    return {
        "parts": parts,
        "documents": docs,
        "cad_documents": cads,
        "referenced_by_documents": refs,
        "made_from": mf,
    }


def build_export(
    root_tree: dict,
    part_number: str,
    system_url: str,
    username: str,
) -> tuple[OrderedDict, str]:
    """Build BOM export data and write to JSON file.

    Returns:
        Tuple of (export_data, filename).

    Raises:
        ValueError: If tree is too deep.
    """
    bom_tree = frontend_tree_to_export(root_tree)
    stats = count_tree_stats(bom_tree)

    export_data = OrderedDict([
        ("export_info", OrderedDict([
            ("source_system", system_url),
            ("odata_version", "v6"),
            ("product_number", part_number),
            ("exported_by", username),
            ("export_timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat()),
            ("statistics", OrderedDict([
                ("total_parts", stats["parts"]),
                ("total_documents", stats["documents"]),
                ("total_cad_documents", stats["cad_documents"]),
                ("total_referenced_by_documents", stats["referenced_by_documents"]),
                ("total_made_from", stats["made_from"]),
            ])),
        ])),
        ("bom", bom_tree),
    ])

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_number = "".join(c for c in part_number if c.isalnum() or c in "-_")
    filename = f"bom_export_{safe_number}_{timestamp}.json"

    os.makedirs(_EXPORT_DIR, exist_ok=True)
    filepath = os.path.join(_EXPORT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    return export_data, filename


def get_export_filepath(filename: str) -> str | None:
    """Resolve an export filename to its full path, or None if not found."""
    safe_name = os.path.basename(filename)
    filepath = os.path.join(_EXPORT_DIR, safe_name)
    return filepath if os.path.isfile(filepath) else None


# ── Full-Tree BOM Export (server-side recursive) ─────────────

_MAX_DEPTH = 50   # safety limit against infinite recursion
_flatten = parts_service._flatten_value  # reuse existing utility


def _export_raw_doc(d: dict, doc_type: str) -> OrderedDict:
    """Export a raw OData document dict with ALL its attributes."""
    _SKIP = {"@odata.type", "@odata.context", "@odata.editLink", "@odata.id"}
    result = OrderedDict()
    result["type"] = doc_type
    result["number"] = _flatten(d.get("Number", ""))
    result["name"] = _flatten(d.get("Name", ""))
    result["version"] = f'{_flatten(d.get("Version", ""))}.{_flatten(d.get("Iteration", ""))}'
    result["state"] = _flatten(d.get("State") or d.get("LifeCycleState") or "")
    # Include ALL remaining attributes
    for k, v in d.items():
        if k in ("Number", "Name", "Version", "Iteration", "State",
                 "LifeCycleState", "ID", "id") or k in _SKIP or k.startswith("@"):
            continue
        flat = _flatten(v)
        if flat is not None and flat != "" and flat != []:
            result[k] = flat
    return result


def _export_part_node(
    client,
    part_id: str,
    part_dict: dict,
    usage_link: dict | None,
    depth: int,
    seen_ids: set[str],
    part_cache: dict[str, OrderedDict] | None = None,
) -> OrderedDict:
    """Recursively export a part with its BOM, documents and CAD documents.

    Includes ALL part attributes, ALL usage link attributes, Made From
    relationships, and raw dimension data — matching the stakeholder spec.

    Caching: When the same part_id has been fully expanded before, the cached
    template is reused (deep-copied) and only usage-link-specific fields
    (line_number, quantity, quantity_unit, usage_link_attributes) are updated.
    This avoids redundant Windchill API calls for duplicate sub-assemblies.
    """
    if part_cache is None:
        part_cache = {}

    n = normalize_item(part_dict)
    number = n["number"]

    # ── Check cache for this part ─────────────────────────
    cached = part_cache.get(part_id)
    if cached is not None:
        result = copy.deepcopy(cached)
        # Overlay usage-link-specific fields for this BOM position
        if usage_link:
            result["line_number"] = _flatten(usage_link.get("LineNumber") or usage_link.get("FindNumber") or "")
            result["quantity"] = _flatten(usage_link.get("Quantity"))
            result["quantity_unit"] = _flatten(usage_link.get("QuantityUnit") or usage_link.get("Unit") or "")
            _SKIP_LINK = {"ID", "id", "Quantity", "QuantityUnit", "Unit",
                          "LineNumber", "FindNumber"}
            u_attrs = OrderedDict()
            for k, v in usage_link.items():
                if k.startswith("@") or k.startswith("odata") or k in _SKIP_LINK:
                    continue
                flat = _flatten(v)
                if flat is not None and flat != "" and flat != []:
                    u_attrs[k] = flat
            if u_attrs:
                result["usage_link_attributes"] = u_attrs
            else:
                result.pop("usage_link_attributes", None)
        return result

    # ── ALL part attributes (skip OData noise) ────────────
    _SKIP_PART = {"ID", "id", "Number", "Name", "Version", "Iteration",
                  "State", "LifeCycleState", "Identity", "OrganizationName",
                  "VersionID"}
    part_attrs = OrderedDict()
    for k, v in part_dict.items():
        if k.startswith("@") or k.startswith("odata") or k.startswith("_"):
            continue
        if k in _SKIP_PART:
            continue
        flat = _flatten(v)
        if flat is not None and flat != "" and flat != []:
            part_attrs[k] = flat

    # ── Usage link attributes ─────────────────────────────
    qty = None
    qty_unit = ""
    line_number = ""
    usage_attrs = OrderedDict()
    if usage_link:
        qty = _flatten(usage_link.get("Quantity"))
        qty_unit = _flatten(usage_link.get("QuantityUnit") or usage_link.get("Unit") or "")
        line_number = _flatten(usage_link.get("LineNumber") or usage_link.get("FindNumber") or "")
        # ALL usage link attributes
        _SKIP_LINK = {"ID", "id", "Quantity", "QuantityUnit", "Unit",
                      "LineNumber", "FindNumber"}
        for k, v in usage_link.items():
            if k.startswith("@") or k.startswith("odata") or k in _SKIP_LINK:
                continue
            flat = _flatten(v)
            if flat is not None and flat != "" and flat != []:
                usage_attrs[k] = flat

    # ── Documents + CAD documents + Referenced By (parallel) ─
    part_number = number
    documents_raw: list[dict] = []
    cad_raw: list[dict] = []
    referenced_by_raw: list[dict] = []
    children_links: list = []

    from concurrent.futures import ThreadPoolExecutor

    def _load_docs():
        try:
            return client.get_described_documents(part_id, part_number)
        except Exception:
            return []

    def _load_cad():
        try:
            return client.get_cad_documents(part_id)
        except Exception:
            return []

    def _load_children():
        if depth >= _MAX_DEPTH:
            return []
        try:
            return client.get_bom_children(part_id)
        except Exception:
            return []

    with ThreadPoolExecutor(max_workers=3) as pool:
        f_docs = pool.submit(_load_docs)
        f_cad = pool.submit(_load_cad)
        f_children = pool.submit(_load_children)
        documents_raw = f_docs.result()
        cad_raw = f_cad.result()
        children_links = f_children.result()

    # Load Referenced By as own category, excluding already-known doc IDs
    described_ids = {d.get("ID", "") for d in (documents_raw or []) if d.get("ID")}
    try:
        referenced_by_raw = client.get_referenced_by_documents(part_id, described_ids)
    except Exception:
        referenced_by_raw = []

    # ── Format documents with ALL attributes ───────────────
    documents = [_export_raw_doc(d, WcType.DOCUMENT) for d in (documents_raw or [])]
    cad_documents = [_export_raw_doc(d, WcType.CAD_DOCUMENT) for d in (cad_raw or [])]
    referenced_by = [_export_raw_doc(d, WcType.DOCUMENT) for d in (referenced_by_raw or [])]

    # ── Made From relationship ─────────────────────────────
    made_from = _build_made_from(part_attrs)

    # ── Recurse into children ──────────────────────────────
    children: list[OrderedDict] = []
    if depth < _MAX_DEPTH:
        for link in children_links:
            child_part = client.resolve_usage_link_child(link)
            if not child_part:
                continue
            child_id = extract_id(child_part)
            if not child_id or child_id in seen_ids:
                continue
            seen_ids.add(child_id)
            children.append(
                _export_part_node(client, child_id, child_part, link, depth + 1, seen_ids, part_cache)
            )
            seen_ids.discard(child_id)  # allow same part in different branches

    children.sort(key=lambda c: (c.get("line_number", ""), c.get("number", "")))

    has_children = len(children) > 0

    result = OrderedDict()
    result["type"] = WcType.PART
    result["number"] = number
    result["name"] = n["name"]
    result["version"] = n["version"]
    result["iteration"] = n["iteration"]
    result["state"] = n["state"]
    result["identity"] = n["identity"]

    # All part-level attributes
    if part_attrs:
        result["part_attributes"] = part_attrs

    # BOM position data
    result["line_number"] = line_number
    result["quantity"] = qty
    result["quantity_unit"] = qty_unit
    if usage_attrs:
        result["usage_link_attributes"] = usage_attrs

    # Made From
    if made_from:
        result["made_from"] = made_from

    result["children_type"] = "subassembly" if has_children else "leaf part"
    result["documents"] = documents
    result["cad_documents"] = cad_documents
    if referenced_by:
        result["referenced_by_documents"] = referenced_by
    result["children"] = children

    # ── Store in cache (without usage-link-specific data) ──
    part_cache[part_id] = copy.deepcopy(result)

    return result


def build_full_tree_export(
    client,
    part_number: str,
    system_url: str,
    username: str,
) -> tuple[OrderedDict, str]:
    """Server-side full BOM explosion export.

    Recursively fetches the entire BOM tree from Windchill,
    including documents and CAD documents at each level.

    Returns:
        Tuple of (export_data, filename).
    """
    from src.adapters.base import WRSError

    # Find root part
    raw_part = client.find_object("part", part_number)
    part_id = extract_id(raw_part)
    if not part_id:
        raise WRSError(f"Part '{part_number}' nicht gefunden oder hat keine ID", status_code=404)

    seen_ids: set[str] = {part_id}
    part_cache: dict[str, OrderedDict] = {}
    bom_tree = _export_part_node(client, part_id, raw_part, None, 0, seen_ids, part_cache)
    stats = count_tree_stats(bom_tree)

    logger.info(
        "Full tree export for %s: %d parts, %d cached reuses",
        part_number, stats["parts"], len(part_cache),
    )

    export_data = OrderedDict([
        ("export_info", OrderedDict([
            ("source_system", system_url),
            ("odata_version", "v6"),
            ("product_number", part_number),
            ("exported_by", username),
            ("export_timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat()),
            ("export_mode", "fullTree"),
            ("statistics", OrderedDict([
                ("total_parts", stats["parts"]),
                ("total_documents", stats["documents"]),
                ("total_cad_documents", stats["cad_documents"]),
                ("total_referenced_by_documents", stats["referenced_by_documents"]),
                ("total_made_from", stats["made_from"]),
                ("cached_part_reuses", len(part_cache)),
            ])),
        ])),
        ("bom", bom_tree),
    ])

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_number = "".join(c for c in part_number if c.isalnum() or c in "-_")
    filename = f"bom_full_export_{safe_number}_{timestamp}.json"

    os.makedirs(_EXPORT_DIR, exist_ok=True)
    filepath = os.path.join(_EXPORT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    return export_data, filename


# ── Extended Export (Design → Manufacturing Equivalence → BOMs) ──


def _parse_equiv_downstream(value: str) -> list[str]:
    """Parse BALDOWNSTREAM into deduplicated manufacturing part numbers.

    BALDOWNSTREAM format:
      "NUMBER, NAME, ORG, VERSION (VIEW), NUMBER, NAME, ORG, VERSION (VIEW), ..."
    Each entry is a group of 4 comma-separated tokens.
    We extract unique part numbers, keeping only the latest version per number.
    """
    if not value or value.startswith("<list:0"):
        return []

    parts = [s.strip() for s in value.split(",")]
    # Groups of 4: number, name, org, version(view)
    latest: dict[str, str] = {}  # number → version
    i = 0
    while i + 3 < len(parts):
        number = parts[i]
        version_view = parts[i + 3]
        # Extract version from "AA.5 (Manufacturing)"
        version = version_view.split("(")[0].strip() if "(" in version_view else version_view
        existing = latest.get(number, "")
        if not existing or version > existing:
            latest[number] = version
        i += 4

    return list(latest.keys())


def build_extended_export(
    client,
    part_number: str,
    system_url: str,
    username: str,
) -> tuple[OrderedDict, str]:
    """Extended export: Design part + Manufacturing equivalents + their BOMs.

    Workflow:
      1. Load the Design part and export its BOM tree.
      2. Parse BALDOWNSTREAM to find Manufacturing equivalent part numbers.
      3. For each Manufacturing part, export its full BOM tree.
      4. GATH (Gathering Parts, Suffix=GATH) are included but their BOMs
         are NOT recursively expanded (only the top-level part data).

    Returns:
        Tuple of (export_data, filename).
    """
    from src.adapters.base import WRSError

    # ── 1. Export Design part BOM ──────────────────────────
    raw_part = client.find_object("part", part_number)
    part_id = extract_id(raw_part)
    if not part_id:
        raise WRSError(f"Part '{part_number}' nicht gefunden", status_code=404)

    # Shared cache across all trees in this export
    part_cache: dict[str, OrderedDict] = {}
    seen_ids: set[str] = {part_id}
    design_tree = _export_part_node(client, part_id, raw_part, None, 0, seen_ids, part_cache)

    # ── 2. Find Manufacturing equivalents ──────────────────
    downstream_raw = _flatten(raw_part.get("BALDOWNSTREAM", ""))
    mfg_numbers = _parse_equiv_downstream(str(downstream_raw) if downstream_raw else "")
    logger.info(
        "Extended export for %s: found %d Manufacturing equivalents: %s",
        part_number, len(mfg_numbers), mfg_numbers,
    )

    # ── 3. Export each Manufacturing part's BOM ────────────
    manufacturing_trees: list[OrderedDict] = []
    for mfg_number in mfg_numbers:
        try:
            mfg_raw = client.find_object("part", mfg_number)
            mfg_id = extract_id(mfg_raw)
            if not mfg_id:
                continue

            mfg_n = normalize_item(mfg_raw)

            # Check if this is a Gathering Part (Suffix=GATH)
            # Gathering parts are included but their BOMs are not expanded
            suffix = _flatten(mfg_raw.get("BALSAPSUFFIX", "")) or ""
            is_gathering = str(suffix).upper() == "GATH"

            if is_gathering:
                # Export only top-level data, no BOM recursion
                logger.info("Skipping BOM expansion for Gathering Part %s", mfg_number)
                mfg_seen: set[str] = {mfg_id}
                # Use depth=_MAX_DEPTH to prevent child loading
                mfg_tree = _export_part_node(
                    client, mfg_id, mfg_raw, None, _MAX_DEPTH, mfg_seen, part_cache,
                )
                mfg_tree["_gathering_part"] = True
            else:
                mfg_seen = {mfg_id}
                mfg_tree = _export_part_node(
                    client, mfg_id, mfg_raw, None, 0, mfg_seen, part_cache,
                )

            manufacturing_trees.append(mfg_tree)
        except Exception as exc:
            logger.warning("Could not export Manufacturing part %s: %s", mfg_number, exc)
            manufacturing_trees.append(OrderedDict([
                ("number", mfg_number),
                ("error", str(exc)),
            ]))

    # ── 4. Combine into export structure ───────────────────
    design_stats = count_tree_stats(design_tree)
    total_stats = {k: v for k, v in design_stats.items()}
    for mt in manufacturing_trees:
        if "error" not in mt:
            ms = count_tree_stats(mt)
            for k in total_stats:
                total_stats[k] += ms[k]

    export_data = OrderedDict([
        ("export_info", OrderedDict([
            ("source_system", system_url),
            ("odata_version", "v6"),
            ("product_number", part_number),
            ("exported_by", username),
            ("export_timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat()),
            ("export_mode", "extended"),
            ("design_part", part_number),
            ("manufacturing_equivalents", mfg_numbers),
            ("statistics", OrderedDict([
                ("total_parts", total_stats["parts"]),
                ("total_documents", total_stats["documents"]),
                ("total_cad_documents", total_stats["cad_documents"]),
                ("total_referenced_by_documents", total_stats["referenced_by_documents"]),
                ("total_made_from", total_stats["made_from"]),
                ("cached_part_reuses", len(part_cache)),
            ])),
        ])),
        ("design_bom", design_tree),
        ("manufacturing_boms", manufacturing_trees),
    ])

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_number = "".join(c for c in part_number if c.isalnum() or c in "-_")
    filename = f"bom_extended_export_{safe_number}_{timestamp}.json"

    os.makedirs(_EXPORT_DIR, exist_ok=True)
    filepath = os.path.join(_EXPORT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    return export_data, filename


# ── Benchmark ────────────────────────────────────────────────


def run_benchmark(client, code: str) -> BenchmarkResponse:
    """Execute a performance benchmark for a given part number."""
    results: list[BenchmarkResult] = []

    t0 = time.monotonic()
    try:
        parts_service.get_part_detail(client, code)
        ms = (time.monotonic() - t0) * 1000
        results.append(
            BenchmarkResult(
                endpoint=f"GET /parts/{code}",
                description="Part suchen & Stammdaten anzeigen",
                api_ms=round(ms, 1),
                estimated_ui_minutes=1.0,
                speedup_factor=round(60_000 / max(ms, 1)),
                note="UI: Suche → öffnen → laden ≈ 1 Min.",
            )
        )
    except Exception as e:
        results.append(
            BenchmarkResult(
                endpoint=f"GET /parts/{code}",
                description="Part suchen",
                api_ms=-1,
                estimated_ui_minutes=1.0,
                speedup_factor=0,
                note=f"Fehler: {e}",
            )
        )

    best = max(
        (r for r in results if r.speedup_factor > 0),
        key=lambda r: r.speedup_factor,
        default=None,
    )
    summary = (
        f"API bis zu {int(best.speedup_factor)}× schneller für '{code}'."
        if best
        else "Benchmark fehlgeschlagen."
    )
    return BenchmarkResponse(results=results, summary=summary)
