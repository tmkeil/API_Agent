"""
Business logic for administrative endpoints: BOM export & performance benchmark.

Extracted from routers/admin.py so that the router only handles HTTP concerns
(request parsing, auth, response formatting) while this module owns the logic.
"""

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


def frontend_tree_to_export(node: dict, _depth: int = 0) -> OrderedDict:
    """Convert a camelCase frontend BOM tree node to snake_case export format.

    Raises:
        ValueError: If tree depth exceeds 200 levels (cycle protection).
    """
    if _depth > 200:
        raise ValueError("Baumstruktur ist zu tief verschachtelt (max. 200 Ebenen)")

    children = [frontend_tree_to_export(child, _depth + 1) for child in node.get("children", [])]

    documents = [
        OrderedDict([
            ("type", doc.get("type", WcType.DOCUMENT)),
            ("number", doc.get("number", "")),
            ("name", doc.get("name", "")),
            ("version", doc.get("version", "")),
            ("state", doc.get("state", "")),
        ])
        for doc in node.get("documents", [])
    ]

    cad_documents = [
        OrderedDict([
            ("type", doc.get("type", WcType.CAD_DOCUMENT)),
            ("number", doc.get("number", "")),
            ("name", doc.get("name", "")),
            ("version", doc.get("version", "")),
            ("state", doc.get("state", "")),
        ])
        for doc in node.get("cadDocuments", [])
    ]

    has_children = len(children) > 0 or bool(node.get("hasChildren"))

    return OrderedDict([
        ("type", node.get("type", WcType.PART)),
        ("number", node.get("number", "")),
        ("name", node.get("name", "")),
        ("version", node.get("version", "")),
        ("iteration", node.get("iteration", "")),
        ("state", node.get("state", "")),
        ("identity", node.get("identity", "")),
        ("quantity", node.get("quantity")),
        ("quantity_unit", node.get("quantityUnit", "")),
        ("line_number", node.get("lineNumber", "")),
        ("children_type", "subassembly" if has_children else "leaf part"),
        ("children", children),
        ("documents", documents),
        ("cad_documents", cad_documents),
    ])


def count_tree_stats(tree: dict) -> dict:
    """Count parts, documents, CAD documents in an export tree (recursive)."""
    parts = 1
    docs = len(tree.get("documents", []))
    cads = len(tree.get("cad_documents", []))
    for child in tree.get("children", []):
        sub = count_tree_stats(child)
        parts += sub["parts"]
        docs += sub["documents"]
        cads += sub["cad_documents"]
    return {"parts": parts, "documents": docs, "cad_documents": cads}


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
_FLATTEN = parts_service._flatten_value  # reuse existing utility


def _export_part_node(
    client,
    part_id: str,
    part_dict: dict,
    usage_link: dict | None,
    depth: int,
    seen_ids: set[str],
) -> OrderedDict:
    """Recursively export a part with its BOM, documents and CAD documents.

    Args:
        client:     Authenticated WRSClient.
        part_dict:  OData dict of the part.
        usage_link: BOM usage link (for qty/line number), or None for root.
        depth:      Current depth (for cycle protection).
        seen_ids:   Set of already-visited part IDs (cycle protection).
    """
    n = normalize_item(part_dict)
    number = n["number"]

    # ── Usage link attributes (quantity, line number) ─────
    qty = None
    qty_unit = ""
    line_number = ""
    if usage_link:
        qty = _flatten(usage_link.get("Quantity"))
        qty_unit = _flatten(usage_link.get("QuantityUnit") or usage_link.get("Unit") or "")
        line_number = _flatten(usage_link.get("LineNumber") or usage_link.get("FindNumber") or "")

    # ── Documents + CAD documents (parallel) ──────────────
    part_number = number
    documents_raw: list[dict] = []
    cad_raw: list[dict] = []
    children_links: list = []

    from concurrent.futures import ThreadPoolExecutor, as_completed

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

    # ── Format documents ───────────────────────────────────
    documents = [
        OrderedDict([
            ("type", WcType.DOCUMENT),
            ("number", _flatten(d.get("Number", ""))),
            ("name", _flatten(d.get("Name", ""))),
            ("version", f'{_flatten(d.get("Version", ""))}.{_flatten(d.get("Iteration", ""))}'),
            ("state", _flatten(d.get("State") or d.get("LifeCycleState") or "")),
        ])
        for d in (documents_raw or [])
    ]

    cad_documents = [
        OrderedDict([
            ("type", WcType.CAD_DOCUMENT),
            ("number", _flatten(d.get("Number", ""))),
            ("name", _flatten(d.get("Name", ""))),
            ("version", f'{_flatten(d.get("Version", ""))}.{_flatten(d.get("Iteration", ""))}'),
            ("state", _flatten(d.get("State") or d.get("LifeCycleState") or "")),
        ])
        for d in (cad_raw or [])
    ]

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
                _export_part_node(client, child_id, child_part, link, depth + 1, seen_ids)
            )
            seen_ids.discard(child_id)  # allow same part in different branches

    children.sort(key=lambda c: (c.get("line_number", ""), c.get("number", "")))

    has_children = len(children) > 0

    return OrderedDict([
        ("type", WcType.PART),
        ("number", number),
        ("name", n["name"]),
        ("version", n["version"]),
        ("iteration", n["iteration"]),
        ("state", n["state"]),
        ("identity", n["identity"]),
        ("quantity", qty),
        ("quantity_unit", qty_unit),
        ("line_number", line_number),
        ("children_type", "subassembly" if has_children else "leaf part"),
        ("children", children),
        ("documents", documents),
        ("cad_documents", cad_documents),
    ])


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
    bom_tree = _export_part_node(client, part_id, raw_part, None, 0, seen_ids)
    stats = count_tree_stats(bom_tree)

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
