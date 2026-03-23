"""
Router: Dokument-Detail-Endpoints.

Endpoints:
  GET /documents/{type_key}/{code}/referencing-parts → Parts die dieses Dokument referenzieren
  GET /documents/{type_key}/{code}/files             → Datei-Info (ContentHolders)
"""

import logging

from fastapi import APIRouter, Depends, Request

from src.core.auth import require_auth
from src.core.dependencies import get_client
from src.models.dto import FileInfoResponse, ReferencingPartsResponse
from src.services import document_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


@router.get(
    "/{type_key}/{code}/referencing-parts",
    response_model=ReferencingPartsResponse,
    summary="Parts die dieses Dokument referenzieren",
)
def referencing_parts(
    type_key: str,
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return document_service.get_referencing_parts(client, type_key, code)


@router.get(
    "/{type_key}/{code}/files",
    response_model=FileInfoResponse,
    summary="Datei-Info / ContentHolders eines Dokuments",
)
def document_files(
    type_key: str,
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return document_service.get_document_files(client, type_key, code)
