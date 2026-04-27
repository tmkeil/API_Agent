"""REST endpoints for WTPart-specific operations.

Covers: Part detail, Documents, CAD-Documents, Where-Used,
Occurrences, BOM root/children.

Search, Object-Detail, Export, Benchmark, Cache and Logs
live in  routers/search.py  and  routers/admin.py.
"""

import logging
import time

from fastapi import APIRouter, Depends, Query, Request

from src.core.auth import require_auth
from src.core.bom_views import BOM_VIEWS
from src.core.dependencies import get_client, get_session
from src.core.session import log_session_event
from src.models.dto import (
    BomNodeResponse,
    BomTransformerResponse,
    BomViewConfig,
    ClassificationNodeListResponse,
    ContainerListResponse,
    DocumentListResponse,
    EquivalenceNetworkResponse,
    OccurrencesResponse,
    PartDetailResponse,
    PartSubtypeListResponse,
    WhereUsedResponse,
)
from src.services import parts_service
from src.services import bom_transformer_service

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
    return parts_service.get_part_detail(client, code)


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
    return parts_service.get_part_documents(client, code)


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
    return parts_service.get_part_cad_documents(client, code)


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
    return parts_service.get_part_where_used(client, code)


# ── Equivalence Network ──────────────────────────────────────


@router.get(
    "/parts/{code}/equivalence",
    response_model=EquivalenceNetworkResponse,
    summary="Equivalence Network (Design ↔ Manufacturing) via OData Nav",
)
def get_equivalence(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return parts_service.get_part_equivalence(client, code)


@router.get(
    "/parts/{code}/transformer",
    response_model=BomTransformerResponse,
    summary="BOM Transformer dual-tree view (Design + Manufacturing)",
)
def get_transformer(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    session = get_session(request)
    return bom_transformer_service.get_transformer_view(client, code, session=session)


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
    return parts_service.get_part_occurrences(client, code)


# ── BOM Tree (lazy) ─────────────────────────────────────────


@router.get("/bom/root", summary="BOM Root Node")
def bom_root(
    request: Request,
    partNumber: str = Query(...),
    _: None = Depends(require_auth),
) -> dict:
    client = get_client(request)
    session = get_session(request)
    node = parts_service.get_bom_root(client, partNumber, session=session)
    return {"root": node}


@router.get(
    "/bom/children",
    response_model=BomNodeResponse,
    summary="BOM-Kinder laden (ein Level)",
)
def bom_children(
    request: Request,
    partId: str = Query(...),
    _: None = Depends(require_auth),
):
    client = get_client(request)
    session = get_session(request)
    t0 = time.perf_counter()
    result = parts_service.get_bom_children(client, partId, session=session)
    duration_ms = int((time.perf_counter() - t0) * 1000)
    if session:
        log_session_event(
            session, "GET", f"/api/bom/children?partId={partId}",
            200, duration_ms, "web",
            f"children={len(result.children)} docs={len(result.documents)} cad={len(result.cadDocuments)}",
        )
    return result


@router.get(
    "/bom/views",
    response_model=list[BomViewConfig],
    summary="Verfuegbare BOM-Ansichten (Spalten-Konfigurationen)",
)
def bom_views() -> list[BomViewConfig]:
    """Return the list of available BOM view configurations.

    Each view defines which columns to display in the BOM table.
    No authentication required — view configs are static metadata.
    """
    return BOM_VIEWS


# ── Windchill Containers ─────────────────────────────────────


@router.get(
    "/containers",
    response_model=ContainerListResponse,
    summary="Windchill Container (Products / Libraries)",
)
def list_containers(
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return parts_service.get_containers(client)


# ── Part Subtypes (Soft Types) ───────────────────────────────


@router.get(
    "/part-subtypes",
    response_model=PartSubtypeListResponse,
    summary="Verfuegbare Part-Subtypes (Soft Types) aus OData Metadata",
)
def list_part_subtypes(
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return parts_service.get_part_subtypes(client)


# ── Classification Nodes ─────────────────────────────────────


@router.get(
    "/classification-nodes",
    response_model=ClassificationNodeListResponse,
    summary="Classification-Knoten aus Windchill ClfStructure",
)
def list_classification_nodes(
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return parts_service.get_classification_nodes(client)
