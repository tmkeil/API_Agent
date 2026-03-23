"""
Router: Typ-uebergreifende Suche und generische Objekt-Details.

Endpoints:
  GET /search                       → Multi-Entity-Suche
  GET /search/stream                → Streaming-Suche (SSE)
  GET /objects/{type_key}/{code}    → Detail fuer beliebigen Windchill-Typ
"""

import json
import logging
import time

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse

from src.core.auth import require_auth
from src.core.dependencies import get_client, get_session
from src.core.odata import WcType, normalize_item, match_score
from src.core.session import log_session_event
from src.models.dto import AdvancedSearchRequest, ObjectDetailResponse, PartSearchResult, SearchResponse
from src.services import search_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Search ───────────────────────────────────────────────────


@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Objekt-Suche (Parts, Dokumente, CAD, Change \u2026)",
)
def search(
    q: str = Query(..., min_length=1, description="Suchbegriff"),
    limit: int = Query(0, ge=0, le=10000, description="Max Ergebnisse. 0 = kein clientseitiges Limit, Windchill-Serverlimit greift."),
    types: str = Query(
        None,
        description="Komma-getrennte Typ-Filter: part,document,cad_document,"
                    "change_notice,change_request,problem_report. "
                    "Leer = alle Typen.",
    ),
    request: Request = None,
    _: None = Depends(require_auth),
) -> SearchResponse:
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
    return SearchResponse(items=results)


# ── Streaming Search (SSE) ───────────────────────────────────


@router.get(
    "/search/stream",
    summary="Streaming-Suche via Server-Sent Events",
)
def search_stream(
    q: str = Query(..., min_length=1, description="Suchbegriff"),
    limit: int = Query(0, ge=0, le=10000),
    types: str = Query(None),
    request: Request = None,
    _: None = Depends(require_auth),
):
    """SSE-Endpoint: Liefert Ergebnis-Batches als `data:` Events.

    Jedes Event enthaelt ein JSON-Array von PartSearchResult-Objekten.
    Am Ende kommt ein `event: done` mit Zusammenfassung.
    """
    client = get_client(request)

    entity_types: list[str] | None = None
    if types:
        entity_types = [t.strip() for t in types.split(",") if t.strip()]

    def _to_search_result(item: dict) -> dict:
        n = normalize_item(item)
        if not n["id"]:
            return None
        obj_type = n.get("_entity_type", WcType.PART)
        return {
            "partId": n["id"],
            "objectType": obj_type,
            "number": n["number"],
            "name": n["name"],
            "version": n["version"],
            "iteration": n["iteration"],
            "state": n["state"],
            "identity": n["identity"],
            "context": n["context"],
            "lastModified": n["last_modified"],
            "createdOn": n["created_on"],
        }

    def _generate():
        total = 0
        t0 = time.perf_counter()
        for batch in client.search_entities_stream(
            q, entity_types=entity_types, limit=limit,
        ):
            results = [r for item in batch if (r := _to_search_result(item)) is not None]
            if results:
                total += len(results)
                yield f"data: {json.dumps(results, ensure_ascii=False)}\n\n"

        duration_ms = int((time.perf_counter() - t0) * 1000)
        yield f"event: done\ndata: {json.dumps({'total': total, 'durationMs': duration_ms})}\n\n"

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── Advanced Search ──────────────────────────────────────────


@router.post(
    "/search/advanced",
    response_model=SearchResponse,
    summary="Erweiterte Suche mit strukturierten Filtern",
)
def advanced_search(
    body: AdvancedSearchRequest,
    request: Request,
    _: None = Depends(require_auth),
) -> SearchResponse:
    client = get_client(request)
    results = search_service.advanced_search(
        client,
        query=body.query,
        types=body.types or None,
        contexts=body.contexts or None,
        state=body.state,
        description=body.description,
        date_from=body.dateFrom,
        date_to=body.dateTo,
        attributes=body.attributes or None,
        limit=body.limit,
    )
    return SearchResponse(items=results)


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
    return search_service.get_object_detail(client, type_key, code)


# ── Contexts ─────────────────────────────────────────────────


@router.get(
    "/contexts",
    summary="Verfügbare Windchill-Kontexte (Container) auflisten",
)
def list_contexts(
    request: Request,
    _: None = Depends(require_auth),
) -> dict:
    client = get_client(request)
    return {"contexts": search_service.get_contexts(client)}
