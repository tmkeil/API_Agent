abc1
windchill-api/src/core/dependencies.py
"""
Gemeinsame FastAPI-Dependencies fuer alle Router.

Eliminiert die duplizierte _get_session / _get_client Logik,
die vorher identisch in parts.py, search.py und admin.py stand.
"""

from typing import Optional

from fastapi import Request

from src.adapters.wrs_client import WRSClient, get_service_client
from src.core.session import SESSION_COOKIE, UserSession, session_store


def get_session(request: Request) -> Optional[UserSession]:
    """UserSession aus dem Session-Cookie aufloesen (falls vorhanden)."""
    token = request.cookies.get(SESSION_COOKIE)
    return session_store.get(token)


def get_client(request: Request) -> WRSClient:
    """WRSClient aufloesen: Session-Cookie zuerst, dann Service-Account."""
    session = get_session(request)
    if session:
        return session.client
    return get_service_client()














abc1
windchill-api/src/core/odata.py
"""
Zentrale OData-Normalisierung fuer Windchill WRS-Responses.

Windchill WRS liefert je nach Endpoint, $expand und OData-Version
unterschiedliche Feldnamen (z.B. "ID" vs "id", "Number" vs "PartNumber").
Dieses Modul loest alle Aliase EINMAL auf und eliminiert die 30+
.get()-Fallback-Ketten, die sich vorher durch den gesamten Code zogen.

Ausserdem: Windchill-Typ-Konstanten und Such-Ranking.
"""

from enum import IntEnum
from typing import Any


# ── OData Field Aliases ──────────────────────────────────────
#
# canonical_key → list of OData field names (tried left to right)

_FIELD_ALIASES: dict[str, list[str]] = {
    "id":            ["ID", "id"],
    "number":        ["Number", "PartNumber"],
    "name":          ["Name", "DisplayName"],
    "version":       ["Version", "VersionID"],
    "iteration":     ["Iteration", "IterationID"],
    "state":         ["State", "LifeCycleState"],
    "identity":      ["Identity", "DisplayIdentity"],
    "context":       ["ContainerName", "Context"],
    "last_modified": ["LastModified", "ModifyTimestamp"],
    "created_on":    ["CreatedOn", "CreateTimestamp"],
}


# ── Normalization helpers ────────────────────────────────────


def normalize_state(raw: Any) -> str:
    """Unwrap State-Dicts ({Value: …, Display: …}) zu einem Plain-String."""
    if isinstance(raw, dict):
        return str(raw.get("Value") or raw.get("Display") or "")
    return str(raw or "")


def extract_id(raw: dict) -> str:
    """Objekt-ID aus einem OData-Dict extrahieren (ID oder id)."""
    return str(raw.get("ID") or raw.get("id") or "")


def normalize_item(raw: dict) -> dict:
    """Alle OData-Feld-Aliase in kanonische Keys aufloesen.

    Returns:
        Dict mit den Keys: id, number, name, version, iteration,
        state (bereits entpackt), identity, context, last_modified,
        created_on.  Plus _entity_type / _entity_type_key falls vorhanden.
    """
    result: dict[str, Any] = {}

    for canonical, aliases in _FIELD_ALIASES.items():
        value = None
        for alias in aliases:
            value = raw.get(alias)
            if value is not None:
                break
        if canonical == "state":
            result[canonical] = normalize_state(value)
        else:
            result[canonical] = str(value) if value is not None else ""

    # Injizierte Metadaten beibehalten (von SearchMixin)
    for meta_key in ("_entity_type", "_entity_type_key"):
        if meta_key in raw:
            result[meta_key] = raw[meta_key]

    return result


# ── Windchill Type Constants ─────────────────────────────────


class WcType:
    """Windchill-Objekttyp-Bezeichner als Konstanten."""
    PART = "WTPart"
    DOCUMENT = "WTDocument"
    EPM_DOCUMENT = "EPMDocument"
    CAD_DOCUMENT = "CADDocument"
    CHANGE_NOTICE = "WTChangeOrder2"
    CHANGE_REQUEST = "WTChangeRequest2"
    PROBLEM_REPORT = "WTChangeIssue"


# ── Search Result Ranking ────────────────────────────────────


class MatchRank(IntEnum):
    """Prioritaetsstufen fuer Suchergebnis-Ranking (niedriger = besser)."""
    EXACT_NUMBER   = 0
    EXACT_NAME     = 1
    NUMBER_PREFIX  = 2
    NAME_PREFIX    = 3
    NUMBER_CONTAINS = 4
    NAME_CONTAINS  = 5
    NO_MATCH       = 9


def match_score(query: str, number: str, name: str) -> tuple:
    """Suchergebnis bewerten fuer Sortierung. Niedrigerer Wert = besserer Treffer.

    Returns:
        Tuple (MatchRank, number_lower, name_lower) als sort-key.
    """
    q = query.lower()
    num = (number or "").lower()
    nam = (name or "").lower()

    if num == q:
        return (MatchRank.EXACT_NUMBER, num, nam)
    if nam == q:
        return (MatchRank.EXACT_NAME, num, nam)
    if num.startswith(q):
        return (MatchRank.NUMBER_PREFIX, num, nam)
    if nam.startswith(q):
        return (MatchRank.NAME_PREFIX, num, nam)
    if q in num:
        return (MatchRank.NUMBER_CONTAINS, num, nam)
    if q in nam:
        return (MatchRank.NAME_CONTAINS, num, nam)
    return (MatchRank.NO_MATCH, num, nam)















abc1
windchill-api/src/models/dto.py
"""
DTOs (Data Transfer Objects) for the Windchill API.
Decouples the external API response from WRS internals.
"""

from typing import Any, Optional

from pydantic import BaseModel


class TimingInfo(BaseModel):
    total_ms: float = 0
    wrs_ms: float = 0
    cache_hits: int = 0
    from_cache: bool = False


# ── Part ─────────────────────────────────────────────────────


class PartDetail(BaseModel):
    part_id: str = ""
    number: str = ""
    name: str = ""
    version: str = ""
    iteration: str = ""
    state: str = ""
    identity: str = ""


class PartDetailResponse(BaseModel):
    part: PartDetail
    timing: TimingInfo


# ── Generic Object Detail ────────────────────────────────────


class ObjectDetail(BaseModel):
    """Generic detail for any Windchill object type."""
    objectId: str = ""
    objectType: str = ""       # WTPart, WTDocument, EPMDocument, ...
    typeKey: str = ""          # part, document, cad_document, ...
    number: str = ""
    name: str = ""
    version: str = ""
    iteration: str = ""
    state: str = ""
    identity: str = ""
    context: str = ""
    lastModified: str = ""
    createdOn: str = ""


class ObjectDetailResponse(BaseModel):
    detail: ObjectDetail
    timing: TimingInfo


class PartSearchResult(BaseModel):
    partId: str = ""
    objectType: str = "WTPart"
    number: str = ""
    name: str = ""
    version: str = ""
    iteration: str = ""
    state: str = ""
    identity: str = ""
    context: str = ""
    lastModified: str = ""
    createdOn: str = ""


# ── BOM Tree (lazy expand) ──────────────────────────────────


class BomTreeNode(BaseModel):
    partId: str = ""
    type: str = "WTPart"
    number: str = ""
    name: str = ""
    version: str = ""
    iteration: str = ""
    state: str = ""
    identity: str = ""
    hasChildren: bool = False
    quantity: Any = None
    quantityUnit: str = ""
    lineNumber: str = ""


class DocumentNode(BaseModel):
    docId: str = ""
    type: str = "WTDocument"
    number: str = ""
    name: str = ""
    version: str = ""
    state: str = ""


class BomNodeResponse(BaseModel):
    children: list[BomTreeNode] = []
    documents: list[DocumentNode] = []
    cadDocuments: list[DocumentNode] = []
    timing: TimingInfo = TimingInfo()


# ── Occurrences ──────────────────────────────────────────────


class PartOccurrence(BaseModel):
    part_id: str = ""
    number: str = ""
    name: str = ""
    version: str = ""
    state: str = ""
    used_in_part: Optional[str] = None
    used_in_name: Optional[str] = None
    path_hint: Optional[str] = None


class OccurrencesResponse(BaseModel):
    code: str
    total_found: int
    occurrences: list[PartOccurrence]
    timing: TimingInfo


# ── Where-Used ───────────────────────────────────────────────


class WhereUsedEntry(BaseModel):
    oid: str = ""
    number: str = ""
    name: str = ""
    revision: Optional[str] = None
    state: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None


class WhereUsedResponse(BaseModel):
    code: str
    total_found: int
    used_in: list[WhereUsedEntry]
    timing: TimingInfo
    note: str = ""


# ── Document List ────────────────────────────────────────────


class DocumentListResponse(BaseModel):
    code: str
    total_found: int
    documents: list[DocumentNode] = []
    timing: TimingInfo = TimingInfo()


# ── Cache ────────────────────────────────────────────────────


class CacheStats(BaseModel):
    entries: int
    ttl_seconds: int
    max_size: int


# ── Benchmark ────────────────────────────────────────────────


class BenchmarkResult(BaseModel):
    endpoint: str
    description: str
    api_ms: float
    estimated_ui_minutes: float
    speedup_factor: float
    note: str = ""


class BenchmarkResponse(BaseModel):
    results: list[BenchmarkResult]
    summary: str















abc1
windchill-api/src/routers/admin.py
"""
Router: Administrative / Infrastruktur-Endpoints.

Endpoints:
  GET    /logs                       → API Activity Log
  POST   /export                     → BOM als JSON exportieren
  GET    /export/download/{filename} → Export-Datei herunterladen
  GET    /benchmark                  → Performance-Benchmark
  GET    /cache/stats                → Cache-Status
  DELETE /cache                      → Cache leeren
"""

import datetime
import json
import logging
import os
import time
from collections import OrderedDict

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse

from src.core.auth import require_auth
from src.core.cache import cache
from src.core.dependencies import get_client, get_session
from src.core.odata import WcType
from src.core.session import log_session_event
from src.models.dto import (
    BenchmarkResponse,
    BenchmarkResult,
    CacheStats,
)
from src.services import parts_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ── API Logs ─────────────────────────────────────────────────


@router.get("/logs", summary="API Activity Log")
def api_logs(
    limit: int = Query(120, ge=1, le=500),
    request: Request = None,
    _: None = Depends(require_auth),
):
    session = get_session(request)
    if not session:
        return {"items": []}
    with session.lock:
        items = list(session.api_logs)[:limit]
    return {"items": items}


# ── JSON Export ──────────────────────────────────────────────


def _frontend_tree_to_export(node: dict) -> OrderedDict:
    """Convert a camelCase frontend tree node to snake_case export format."""
    children = []
    for child in node.get("children", []):
        children.append(_frontend_tree_to_export(child))

    documents = []
    for doc in node.get("documents", []):
        documents.append(OrderedDict([
            ("type", doc.get("type", WcType.DOCUMENT)),
            ("number", doc.get("number", "")),
            ("name", doc.get("name", "")),
            ("version", doc.get("version", "")),
            ("state", doc.get("state", "")),
        ]))

    cad_documents = []
    for doc in node.get("cadDocuments", []):
        cad_documents.append(OrderedDict([
            ("type", doc.get("type", WcType.CAD_DOCUMENT)),
            ("number", doc.get("number", "")),
            ("name", doc.get("name", "")),
            ("version", doc.get("version", "")),
            ("state", doc.get("state", "")),
        ]))

    has_children = len(children) > 0
    children_type = "subassembly" if has_children else "no additional children"

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
        ("children_type", children_type),
        ("children", children),
        ("documents", documents),
        ("cad_documents", cad_documents),
    ])


def _count_tree(tree: dict) -> dict:
    """Count parts, documents, CAD documents in a tree."""
    parts = 1
    docs = len(tree.get("documents", []))
    cads = len(tree.get("cad_documents", []))
    for child in tree.get("children", []):
        sub = _count_tree(child)
        parts += sub["parts"]
        docs += sub["documents"]
        cads += sub["cad_documents"]
    return {"parts": parts, "documents": docs, "cad_documents": cads}


@router.post("/export", summary="BOM als JSON exportieren")
async def export_bom(
    request: Request,
    _: None = Depends(require_auth),
):
    session = get_session(request)
    if not session:
        raise HTTPException(401, "Nicht authentifiziert")

    payload = await request.json()
    mode = str(payload.get("mode", "expandedOnly"))
    part_number = str(payload.get("partNumber", "")).strip()

    if not part_number:
        raise HTTPException(400, "partNumber fehlt")
    if mode not in ("expandedOnly", "fullTree"):
        raise HTTPException(400, "Ungültiger Exportmodus")

    if mode == "expandedOnly":
        root_tree = payload.get("tree")
        if not isinstance(root_tree, dict):
            raise HTTPException(400, "Für expandedOnly ist ein Tree-Objekt erforderlich")
        bom_tree = _frontend_tree_to_export(root_tree)
    else:
        # fullTree: not yet supported (requires recursive BOM build)
        raise HTTPException(501, "fullTree-Export wird noch nicht unterstützt")

    stats = _count_tree(bom_tree)

    export_data = OrderedDict([
        ("export_info", OrderedDict([
            ("source_system", session.system_url),
            ("odata_version", "v6"),
            ("product_number", part_number),
            ("exported_by", session.username),
            ("export_timestamp", datetime.datetime.now().isoformat()),
            ("statistics", OrderedDict([
                ("total_parts", stats["parts"]),
                ("total_documents", stats["documents"]),
                ("total_cad_documents", stats["cad_documents"]),
            ])),
        ])),
        ("bom", bom_tree),
    ])

    # Write to temp file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_number = "".join(c for c in part_number if c.isalnum() or c in "-_")
    filename = f"bom_export_{safe_number}_{timestamp}.json"
    export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "exports")
    os.makedirs(export_dir, exist_ok=True)
    filepath = os.path.join(export_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    if session:
        log_session_event(session, "POST", "/api/export", 200, 0, "web", f"export {mode}: {filename}")

    return {
        "ok": True,
        "filename": filename,
        "downloadUrl": f"/api/export/download/{filename}",
    }


@router.get("/export/download/{filename}", summary="Export-Datei herunterladen")
def export_download(
    filename: str,
    _: None = Depends(require_auth),
):
    safe_name = os.path.basename(filename)
    export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "exports")
    filepath = os.path.join(export_dir, safe_name)
    if not os.path.isfile(filepath):
        raise HTTPException(404, "Datei nicht gefunden")
    return FileResponse(filepath, filename=safe_name, media_type="application/json")


# ── Benchmark ────────────────────────────────────────────────


@router.get(
    "/benchmark",
    response_model=BenchmarkResponse,
    summary="Performance-Benchmark",
)
def benchmark(
    code: str = Query(...),
    request: Request = None,
    _: None = Depends(require_auth),
):
    client = get_client(request)
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


# ── Cache ────────────────────────────────────────────────────


@router.get(
    "/cache/stats",
    response_model=CacheStats,
    summary="Cache-Status",
)
def cache_stats(_: None = Depends(require_auth)):
    return parts_service.get_cache_stats()


@router.delete("/cache", summary="Cache leeren")
def clear_cache(_: None = Depends(require_auth)):
    cache.clear()
    return {"message": "Cache geleert."}















abc1
windchill-api/src/routers/parts.py
"""REST endpoints for WTPart-specific operations.

Covers: Part detail, Documents, CAD-Documents, Where-Used,
Occurrences, BOM root/children.

Search, Object-Detail, Export, Benchmark, Cache and Logs
live in  routers/search.py  and  routers/admin.py.
"""

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from src.adapters.wrs_client import WRSError
from src.core.auth import require_auth
from src.core.dependencies import get_client, get_session
from src.core.session import log_session_event
from src.models.dto import (
    BomNodeResponse,
    DocumentListResponse,
    OccurrencesResponse,
    PartDetailResponse,
    WhereUsedResponse,
)
from src.services import parts_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Part Detail ──────────────────────────────────────────────


@router.get(
    "/parts/{code}",
    response_model=PartDetailResponse,
    summary="Teilestammdaten",
)
def get_part(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    try:
        return parts_service.get_part_detail(client, code)
    except WRSError as e:
        raise HTTPException(
            status_code=e.status_code or 502, detail=str(e)
        )


# ── Documents ────────────────────────────────────────────────


@router.get(
    "/parts/{code}/documents",
    response_model=DocumentListResponse,
    summary="Dokumente eines Parts (DescribedBy)",
)
def get_documents(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    try:
        return parts_service.get_part_documents(client, code)
    except WRSError as e:
        raise HTTPException(
            status_code=e.status_code or 502, detail=str(e)
        )


@router.get(
    "/parts/{code}/cad-documents",
    response_model=DocumentListResponse,
    summary="CAD-Dokumente eines Parts (EPM)",
)
def get_cad_documents(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    try:
        return parts_service.get_part_cad_documents(client, code)
    except WRSError as e:
        raise HTTPException(
            status_code=e.status_code or 502, detail=str(e)
        )


# ── Where-Used ───────────────────────────────────────────────


@router.get(
    "/parts/{code}/where-used",
    response_model=WhereUsedResponse,
    summary="Einsatzverwendung (Where-Used)",
)
def get_where_used(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    try:
        return parts_service.get_part_where_used(client, code)
    except WRSError as e:
        raise HTTPException(
            status_code=e.status_code or 502, detail=str(e)
        )


# ── Occurrences ──────────────────────────────────────────────


@router.get(
    "/parts/{code}/occurrences",
    response_model=OccurrencesResponse,
    summary="Alle Vorkommen eines Part-Codes",
)
def get_occurrences(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    try:
        return parts_service.get_part_occurrences(client, code)
    except WRSError as e:
        raise HTTPException(
            status_code=e.status_code or 502, detail=str(e)
        )


# ── BOM Tree (lazy) ─────────────────────────────────────────


@router.get("/bom/root", summary="BOM Root Node")
def bom_root(
    partNumber: str = Query(...),
    request: Request = None,
    _: None = Depends(require_auth),
) -> dict:
    client = get_client(request)
    session = get_session(request)
    try:
        node = parts_service.get_bom_root(client, partNumber, session=session)
        return {"root": node}
    except WRSError as e:
        raise HTTPException(
            status_code=e.status_code or 404, detail=str(e)
        )


@router.get(
    "/bom/children",
    response_model=BomNodeResponse,
    summary="BOM-Kinder laden (ein Level)",
)
def bom_children(
    partId: str = Query(...),
    request: Request = None,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    session = get_session(request)
    t0 = time.perf_counter()
    try:
        result = parts_service.get_bom_children(client, partId, session=session)
        duration_ms = int((time.perf_counter() - t0) * 1000)
        if session:
            log_session_event(
                session, "GET", f"/api/bom/children?partId={partId}",
                200, duration_ms, "web",
                f"children={len(result.children)} docs={len(result.documents)} cad={len(result.cadDocuments)}",
            )
        return result
    except WRSError as e:
        raise HTTPException(
            status_code=e.status_code or 502, detail=str(e)
        )















abc1
windchill-api/src/routers/search.py
"""
Router: Typ-uebergreifende Suche und generische Objekt-Details.

Endpoints:
  GET /search                       → Multi-Entity-Suche
  GET /objects/{type_key}/{code}    → Detail fuer beliebigen Windchill-Typ
"""

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from src.adapters.wrs_client import WRSError
from src.core.auth import require_auth
from src.core.dependencies import get_client, get_session
from src.core.session import log_session_event
from src.models.dto import ObjectDetailResponse
from src.services import search_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Search ───────────────────────────────────────────────────


@router.get("/search", summary="Objekt-Suche (Parts, Dokumente, CAD, Change …)")
def search(
    q: str = Query(..., min_length=1, description="Suchbegriff"),
    limit: int = Query(100, ge=1, le=500),
    types: str = Query(
        None,
        description="Komma-getrennte Typ-Filter: part,document,cad_document,"
                    "change_notice,change_request,problem_report. "
                    "Leer = alle Typen.",
    ),
    request: Request = None,
    _: None = Depends(require_auth),
) -> dict:
    client = get_client(request)
    session = get_session(request)

    entity_types: list[str] | None = None
    if types:
        entity_types = [t.strip() for t in types.split(",") if t.strip()]

    t0 = time.perf_counter()
    results = search_service.search_parts(
        client, q, limit, entity_types=entity_types, session=session,
    )
    duration_ms = int((time.perf_counter() - t0) * 1000)
    if session:
        log_session_event(session, "GET", f"/api/search?q={q}&types={types}", 200, duration_ms, "web", f"{len(results)} results")
    return {"items": results}


# ── Generic Object Detail ────────────────────────────────────


@router.get(
    "/objects/{type_key}/{code}",
    response_model=ObjectDetailResponse,
    summary="Detail-Ansicht für beliebigen Windchill-Objekttyp",
)
def get_object_detail(
    type_key: str,
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    try:
        return search_service.get_object_detail(client, type_key, code)
    except WRSError as e:
        raise HTTPException(
            status_code=e.status_code or 502, detail=str(e)
        )















abc1
windchill-api/src/services/parts_service.py
"""
Business logic: WTPart-spezifische Operationen.

Part-Detail, BOM-Baum, Dokumente, CAD, Where-Used, Occurrences.
Typ-uebergreifende Suche → search_service.py
Administrative Funktionen (Export, Benchmark) → routers/admin.py

All functions accept a WRSClient instance — either the service-account
singleton or a per-session client from the frontend.
Session-level caching is used when a UserSession is provided.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from src.adapters.wrs_client import WRSClient
from src.core.cache import cache
from src.core.config import settings
from src.core.odata import WcType, extract_id, normalize_item, normalize_state
from src.core.session import UserSession, log_session_event
from src.models.dto import (
    BomNodeResponse,
    BomTreeNode,
    CacheStats,
    DocumentListResponse,
    DocumentNode,
    OccurrencesResponse,
    PartDetail,
    PartDetailResponse,
    PartOccurrence,
    TimingInfo,
    WhereUsedEntry,
    WhereUsedResponse,
)

logger = logging.getLogger(__name__)


# ── Internal mappers ─────────────────────────────────────────


def _map_part(raw: dict) -> PartDetail:
    n = normalize_item(raw)
    return PartDetail(
        part_id=n["id"],
        number=n["number"],
        name=n["name"],
        version=n["version"],
        iteration=n["iteration"],
        state=n["state"],
        identity=n["identity"],
    )


def _map_tree_node(
    raw: dict, usage_link: Optional[dict] = None
) -> BomTreeNode:
    n = normalize_item(raw)
    node = BomTreeNode(
        partId=n["id"],
        type=WcType.PART,
        number=n["number"],
        name=n["name"],
        version=n["version"],
        iteration=n["iteration"],
        state=n["state"],
        identity=n["identity"],
        hasChildren=bool(n["id"]),
    )

    if usage_link:
        qty = usage_link.get("Quantity", 1)
        unit = ""
        if isinstance(qty, dict):
            unit = str(qty.get("Unit") or "")
            qty = qty.get("Value", 1)
        if not unit:
            raw_unit = (
                usage_link.get("Unit")
                or usage_link.get("QuantityUnit")
                or ""
            )
            if isinstance(raw_unit, dict):
                raw_unit = raw_unit.get("Value") or ""
            unit = str(raw_unit)

        node.quantity = qty
        node.quantityUnit = unit
        node.lineNumber = str(
            usage_link.get("LineNumber")
            or usage_link.get("FindNumber")
            or ""
        )

    return node


def _map_document(
    raw: dict, doc_type: str = WcType.DOCUMENT
) -> DocumentNode:
    n = normalize_item(raw)
    return DocumentNode(
        docId=n["id"],
        type=doc_type,
        number=n["number"],
        name=n["name"],
        version=n["version"],
        state=n["state"],
    )



# ── Service Functions ────────────────────────────────────────


def get_part_documents(
    client: WRSClient, code: str
) -> DocumentListResponse:
    """Get WTDocuments linked to a part."""
    t0 = time.monotonic()
    raw = client.find_part(code)
    part_id = extract_id(raw)
    part_number = str(raw.get("Number") or code)
    raw_docs = client.get_described_documents(part_id, part_number)
    docs = [_map_document(d, WcType.DOCUMENT) for d in raw_docs]
    ms = round((time.monotonic() - t0) * 1000, 1)
    return DocumentListResponse(
        code=code,
        total_found=len(docs),
        documents=docs,
        timing=TimingInfo(total_ms=ms, wrs_ms=ms),
    )


def get_part_cad_documents(
    client: WRSClient, code: str
) -> DocumentListResponse:
    """Get CAD/EPM documents linked to a part."""
    t0 = time.monotonic()
    raw = client.find_part(code)
    part_id = extract_id(raw)
    raw_cads = client.get_cad_documents(part_id)
    cads = [_map_document(c, WcType.EPM_DOCUMENT) for c in raw_cads]
    ms = round((time.monotonic() - t0) * 1000, 1)
    return DocumentListResponse(
        code=code,
        total_found=len(cads),
        documents=cads,
        timing=TimingInfo(total_ms=ms, wrs_ms=ms),
    )


def get_part_where_used(
    client: WRSClient, code: str
) -> WhereUsedResponse:
    """Get where-used (parent assemblies) for a part."""
    t0 = time.monotonic()
    raw = client.find_part(code)
    part_id = extract_id(raw)
    raw_parents = client.get_where_used(part_id)
    entries = []
    for p in raw_parents:
        n = normalize_item(p)
        entries.append(WhereUsedEntry(
            oid=n["id"],
            number=n["number"],
            name=n["name"],
            revision=n["version"],
            state=n["state"],
            quantity=p.get("Quantity"),
            unit=str(p.get("Unit") or p.get("QuantityUnit") or "") or None,
        ))
    ms = round((time.monotonic() - t0) * 1000, 1)
    return WhereUsedResponse(
        code=code,
        total_found=len(entries),
        used_in=entries,
        timing=TimingInfo(total_ms=ms, wrs_ms=ms),
    )


def get_part_detail(
    client: WRSClient, code: str
) -> PartDetailResponse:
    t0 = time.monotonic()

    cache_key = f"detail:{code}"
    cached = cache.get(cache_key)
    if cached is not None:
        return PartDetailResponse(
            part=cached,
            timing=TimingInfo(
                total_ms=0, wrs_ms=0, cache_hits=1, from_cache=True
            ),
        )

    raw = client.find_part(code)
    part = _map_part(raw)
    cache.set(cache_key, part, ttl=settings.CACHE_TTL_SECONDS)

    ms = round((time.monotonic() - t0) * 1000, 1)
    return PartDetailResponse(
        part=part,
        timing=TimingInfo(total_ms=ms, wrs_ms=ms),
    )


def get_part_occurrences(
    client: WRSClient, code: str
) -> OccurrencesResponse:
    t0 = time.monotonic()

    raw = client.search_parts(code, limit=500)
    occurrences = []
    for item in raw:
        p = _map_part(item)
        occurrences.append(
            PartOccurrence(
                part_id=p.part_id,
                number=p.number,
                name=p.name,
                version=p.version,
                state=p.state,
                path_hint=p.number,
            )
        )

    ms = round((time.monotonic() - t0) * 1000, 1)
    return OccurrencesResponse(
        code=code,
        total_found=len(occurrences),
        occurrences=occurrences,
        timing=TimingInfo(total_ms=ms, wrs_ms=ms),
    )


def get_bom_root(
    client: WRSClient,
    part_number: str,
    session: Optional[UserSession] = None,
) -> BomTreeNode:
    """Load root node for lazy BOM tree, with session cache."""
    if session:
        key = part_number.strip().upper()
        with session.lock:
            cached_part = session.part_by_number.get(key)
        if cached_part:
            log_session_event(session, "CACHE", f"part:number:{part_number}", 200, 0, "cache", "part hit")
            return _map_tree_node(cached_part)

    raw = client.find_part(part_number)

    if session:
        pid = extract_id(raw).strip()
        num = str(raw.get("Number") or "").strip().upper()
        with session.lock:
            if pid:
                session.part_by_id[pid] = raw
            if num:
                session.part_by_number[num] = raw

    return _map_tree_node(raw)


def get_bom_children(
    client: WRSClient,
    part_id: str,
    session: Optional[UserSession] = None,
) -> BomNodeResponse:
    """Load one level of BOM children + documents for a part.
    Uses session-level caching and parallel loading like the prototype."""
    t0 = time.monotonic()
    _SENTINEL = object()

    # ── Check session caches ─────────────────────────────────
    links = None
    children_cached = False
    docs_cached = False
    cad_cached = False

    if session:
        with session.lock:
            cached_links = session.bom_children_by_part.get(part_id)
        if cached_links is not None:
            links = cached_links
            children_cached = True
            log_session_event(session, "CACHE", f"bom:children:{part_id}", 200, 0, "cache", "children hit")

    # Fetch links from Windchill if not cached
    if links is None:
        links = client.get_bom_children(part_id)
        if session:
            with session.lock:
                session.bom_children_by_part[part_id] = links

    # Get part info for document queries
    part = client.get_part_by_id(part_id)
    part_number = ""
    if part:
        part_number = str(part.get("Number") or part.get("PartNumber") or "")
        if session:
            with session.lock:
                session.part_by_id[part_id] = part

    # ── Check doc/cad caches ─────────────────────────────────
    documents_raw = None
    cad_raw = None

    if session:
        with session.lock:
            d = session.documents_by_part.get(part_id, _SENTINEL)
        if d is not _SENTINEL:
            documents_raw = d
            docs_cached = True
            log_session_event(session, "CACHE", f"bom:documents:{part_id}", 200, 0, "cache", "documents hit")

        with session.lock:
            c = session.cad_documents_by_part.get(part_id, _SENTINEL)
        if c is not _SENTINEL:
            cad_raw = c
            cad_cached = True
            log_session_event(session, "CACHE", f"bom:cad:{part_id}", 200, 0, "cache", "cad hit")

    # ── Parallel loading ─────────────────────────────────────
    def _resolve_child(link):
        child = client.resolve_usage_link_child(link)
        if not child:
            return None
        if session:
            cid = extract_id(child).strip()
            if cid:
                with session.lock:
                    session.part_by_id[cid] = child
        return _map_tree_node(child, usage_link=link)

    def _load_documents():
        docs = client.get_described_documents(part_id, part_number)
        if session:
            with session.lock:
                session.documents_by_part[part_id] = docs
        return docs

    def _load_cad():
        cads = client.get_cad_documents(part_id)
        if session:
            with session.lock:
                session.cad_documents_by_part[part_id] = cads
        return cads

    with ThreadPoolExecutor(max_workers=8) as executor:
        # Resolve children in parallel
        child_futures = [executor.submit(_resolve_child, link) for link in links]

        # Load docs/cad if not cached
        docs_future = None
        cad_future = None
        if documents_raw is None:
            docs_future = executor.submit(_load_documents)
        if cad_raw is None:
            cad_future = executor.submit(_load_cad)

        # Collect children
        children: list[BomTreeNode] = []
        for f in child_futures:
            node = f.result()
            if node is not None:
                children.append(node)

        if docs_future:
            documents_raw = docs_future.result()
        if cad_future:
            cad_raw = cad_future.result()

    children.sort(key=lambda n: (n.lineNumber or "", n.number or ""))

    documents = [_map_document(d, WcType.DOCUMENT) for d in (documents_raw or [])]
    cad_documents = [_map_document(d, WcType.CAD_DOCUMENT) for d in (cad_raw or [])]

    ms = round((time.monotonic() - t0) * 1000, 1)
    return BomNodeResponse(
        children=children,
        documents=documents,
        cadDocuments=cad_documents,
        timing=TimingInfo(total_ms=ms, wrs_ms=ms),
    )


def get_cache_stats() -> CacheStats:
    return CacheStats(
        entries=cache.size,
        ttl_seconds=settings.CACHE_TTL_SECONDS,
        max_size=settings.CACHE_MAX_SIZE,
    )















abc1
windchill-api/src/services/search_service.py
"""
Business logic: typ-uebergreifende Suche und generische Objektdetails.

Ausgelagert aus parts_service.py — hier liegt alles, was nicht
an einen einzelnen Windchill-Typ (WTPart etc.) gebunden ist.
"""

import logging
import re
import time
from typing import Optional

from src.adapters.wrs_client import WRSClient
from src.core.odata import WcType, extract_id, match_score, normalize_item
from src.core.session import UserSession, log_session_event
from src.models.dto import (
    ObjectDetail,
    ObjectDetailResponse,
    PartSearchResult,
    TimingInfo,
)

logger = logging.getLogger(__name__)


# ── Internal helpers ─────────────────────────────────────────


def _wildcard_to_regex(pattern: str) -> re.Pattern:
    escaped = re.escape(pattern)
    escaped = escaped.replace(r"\*", ".*").replace(r"\?", ".")
    return re.compile(f"^{escaped}$", re.IGNORECASE)


# ── Service Functions ────────────────────────────────────────


def search_parts(
    client: WRSClient,
    query: str,
    limit: int = 200,
    entity_types: list[str] | None = None,
    session: Optional[UserSession] = None,
) -> list[PartSearchResult]:
    """Search with wildcard support, ranking, and session-level caching.

    Args:
        entity_types: Optional list of type keys to search.
                      None → all types. E.g. ["part","document","cad_document"]
    """
    # Check session cache first
    types_key = ",".join(sorted(entity_types)) if entity_types else "all"
    cache_key = f"{query.lower()}|{limit}|{types_key}"
    if session:
        with session.lock:
            cached = session.search_cache.get(cache_key)
        if cached is not None:
            log_session_event(session, "CACHE", f"search:{query}", 200, 0, "cache", "search hit")
            return cached

    # Use multi-entity search
    raw_items = client.search_entities(query, entity_types=entity_types, limit=limit * 2)

    # Also do the legacy ProdMgmt/Parts search with wildcard filtering
    # if "part" is in the requested types (or all types)
    if entity_types is None or "part" in entity_types:
        url = f"{client.odata_base}/ProdMgmt/Parts"
        wildcard = "*" in query or "?" in query
        regex = _wildcard_to_regex(query)
        core = query.replace("*", "").replace("?", "").strip()
        safe = core.replace("'", "''")

        # Additional filters for wildcard patterns
        extra_collected: dict[str, dict] = {}
        seen_from_multi = {extract_id(item) for item in raw_items}

        if wildcard and core:
            extra_filters = [
                {"$filter": f"contains(Number,'{safe}')", "$top": "200"},
                {"$filter": f"contains(Name,'{safe}')", "$top": "200"},
            ]
            for params in extra_filters:
                try:
                    items = client._get_all_pages(url, params)
                    for item in items:
                        pid = extract_id(item)
                        if pid and pid not in seen_from_multi and pid not in extra_collected:
                            item["_entity_type"] = WcType.PART
                            item["_entity_type_key"] = "part"
                            extra_collected[pid] = item
                except Exception:
                    logger.debug("Wildcard filter failed: %s", params, exc_info=True)
                    continue

            # Filter by wildcard regex
            for pid, item in extra_collected.items():
                number = str(item.get("Number") or "")
                name = str(item.get("Name") or "")
                if regex.search(number) or regex.search(name):
                    raw_items.append(item)

    # Map to PartSearchResult
    matches = []
    seen_ids: set[str] = set()
    for item in raw_items:
        n = normalize_item(item)
        if not n["id"] or n["id"] in seen_ids:
            continue
        seen_ids.add(n["id"])

        obj_type = n.get("_entity_type", WcType.PART)

        matches.append(
            PartSearchResult(
                partId=n["id"],
                objectType=obj_type,
                number=n["number"],
                name=n["name"],
                version=n["version"],
                iteration=n["iteration"],
                state=n["state"],
                identity=n["identity"],
                context=n["context"],
                lastModified=n["last_modified"],
                createdOn=n["created_on"],
            )
        )

        # Cache the part in session (only WTParts)
        if session and obj_type == WcType.PART:
            num = n["number"].strip().upper()
            with session.lock:
                if n["id"]:
                    session.part_by_id[n["id"]] = item
                if num:
                    session.part_by_number[num] = item

    matches.sort(key=lambda m: match_score(query, m.number, m.name))
    result = matches[:limit]

    # Store in session cache
    if session:
        with session.lock:
            session.search_cache[cache_key] = result

    return result


def get_object_detail(
    client: WRSClient, type_key: str, code: str
) -> ObjectDetailResponse:
    """Generische Detail-Abfrage fuer jeden Windchill-Objekttyp."""
    t0 = time.monotonic()

    raw = client.find_object(type_key, code)
    n = normalize_item(raw)

    detail = ObjectDetail(
        objectId=n["id"],
        objectType=n.get("_entity_type", ""),
        typeKey=n.get("_entity_type_key", type_key),
        number=n["number"],
        name=n["name"],
        version=n["version"],
        iteration=n["iteration"],
        state=n["state"],
        identity=n["identity"],
        context=n["context"],
        lastModified=n["last_modified"],
        createdOn=n["created_on"],
    )

    ms = round((time.monotonic() - t0) * 1000, 1)
    return ObjectDetailResponse(
        detail=detail,
        timing=TimingInfo(total_ms=ms, wrs_ms=ms),
    )















abc1
windchill-frontend/src/api/client.ts
import type {
  BomNodeResponse,
  BomTreeNode,
  DocumentListResponse,
  ObjectDetailResponse,
  OccurrencesResponse,
  PartDetailResponse,
  PartSearchResult,
  SystemInfo,
  UserInfo,
  WhereUsedResponse,
  ApiLogEntry,
} from './types'

const BASE = '/api'

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(url, {
    credentials: 'include',
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}))
    throw new Error(body.error || body.detail || `HTTP ${resp.status}`)
  }
  return resp.json()
}

// Auth
export async function getSystems(): Promise<SystemInfo[]> {
  const data = await request<{ systems: SystemInfo[] }>(`${BASE}/auth/systems`)
  return data.systems
}

export async function login(
  system: string,
  username: string,
  password: string,
): Promise<UserInfo> {
  return request<UserInfo>(`${BASE}/auth/login`, {
    method: 'POST',
    body: JSON.stringify({ system, username, password }),
  })
}

export async function logout(): Promise<void> {
  await request<unknown>(`${BASE}/auth/logout`, { method: 'POST' })
}

export async function getMe(): Promise<UserInfo> {
  return request<UserInfo>(`${BASE}/auth/me`)
}

// Search
export async function searchParts(
  q: string,
  limit = 200,
  types?: string[],
): Promise<PartSearchResult[]> {
  const params = new URLSearchParams({ q, limit: String(limit) })
  if (types && types.length > 0) {
    params.set('types', types.join(','))
  }
  const data = await request<{ items: PartSearchResult[] }>(
    `${BASE}/search?${params}`,
  )
  return data.items
}

// Occurrences (Use Case: "Wo kommt Code XABC vor?")
export async function getOccurrences(code: string): Promise<OccurrencesResponse> {
  return request<OccurrencesResponse>(`${BASE}/parts/${encodeURIComponent(code)}/occurrences`)
}

// Detail Page APIs
export async function getPartDetail(code: string): Promise<PartDetailResponse> {
  return request<PartDetailResponse>(`${BASE}/parts/${encodeURIComponent(code)}`)
}

export async function getObjectDetail(typeKey: string, code: string): Promise<ObjectDetailResponse> {
  return request<ObjectDetailResponse>(
    `${BASE}/objects/${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}`,
  )
}

export async function getPartDocuments(code: string): Promise<DocumentListResponse> {
  return request<DocumentListResponse>(`${BASE}/parts/${encodeURIComponent(code)}/documents`)
}

export async function getPartCadDocuments(code: string): Promise<DocumentListResponse> {
  return request<DocumentListResponse>(`${BASE}/parts/${encodeURIComponent(code)}/cad-documents`)
}

export async function getWhereUsed(code: string): Promise<WhereUsedResponse> {
  return request<WhereUsedResponse>(`${BASE}/parts/${encodeURIComponent(code)}/where-used`)
}

// BOM
export async function getBomRoot(
  partNumber: string,
): Promise<BomTreeNode> {
  const params = new URLSearchParams({ partNumber })
  const data = await request<{ root: BomTreeNode }>(
    `${BASE}/bom/root?${params}`,
  )
  return data.root
}

export async function getBomChildren(
  partId: string,
): Promise<BomNodeResponse> {
  const params = new URLSearchParams({ partId })
  return request<BomNodeResponse>(`${BASE}/bom/children?${params}`)
}

// API Logs
export async function getApiLogs(limit = 120): Promise<ApiLogEntry[]> {
  const data = await request<{ items: ApiLogEntry[] }>(
    `${BASE}/logs?limit=${limit}`,
  )
  return data.items
}

// Export
export async function exportBom(
  mode: 'expandedOnly' | 'fullTree',
  partNumber: string,
  tree?: unknown,
): Promise<{ ok: boolean; filename: string; downloadUrl: string }> {
  return request(`${BASE}/export`, {
    method: 'POST',
    body: JSON.stringify({ mode, partNumber, tree }),
  })
}
