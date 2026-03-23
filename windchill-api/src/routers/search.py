"""
Router: Typ-uebergreifende Suche und generische Objekt-Details.

Endpoints:
  GET /search                       → Multi-Entity-Suche
  GET /objects/{type_key}/{code}    → Detail fuer beliebigen Windchill-Typ
"""

import logging
import time

from fastapi import APIRouter, Depends, Query, Request

from src.core.auth import require_auth
from src.core.dependencies import get_client, get_session
from src.core.session import log_session_event
from src.models.dto import AdvancedSearchRequest, ObjectDetailResponse, SearchResponse
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
    limit: int = Query(100, ge=1, le=500),
    types: str = Query(
        None,
        description="Komma-getrennte Typ-Filter: part,document,cad_document,"
                    "change_notice,change_request,problem_report. "
                    "Leer = alle Typen.",
    ),
    context: str = Query(
        None,
        description="Windchill ContainerName Filter (z.B. 'Balluff'). "
                    "Leer = kein Kontext-Filter.",
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
        client, q, limit, entity_types=entity_types, context=context, session=session,
    )
    duration_ms = int((time.perf_counter() - t0) * 1000)
    if session:
        log_session_event(session, "GET", f"/api/search?q={q}&types={types}", 200, duration_ms, "web", f"{len(results)} results")
    return SearchResponse(items=results)


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
        context=body.context,
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
