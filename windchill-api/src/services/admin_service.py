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

from src.core.odata import WcType
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
