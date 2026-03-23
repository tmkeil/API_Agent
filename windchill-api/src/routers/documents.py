"""
Router: Dokument-Detail-Endpoints.

Endpoints:
  GET /documents/{type_key}/{code}/referencing-parts → Parts die dieses Dokument referenzieren
  GET /documents/{type_key}/{code}/files             → Datei-Info (ContentHolders)
  GET /documents/{type_key}/{code}/download          → Primaerdatei herunterladen
"""

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

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


@router.get(
    "/{type_key}/{code}/download",
    summary="Primaerdatei eines Dokuments herunterladen",
    responses={
        200: {
            "description": "Datei-Inhalt (Stream)",
            "content": {"application/octet-stream": {}},
        },
    },
)
def download_document(
    type_key: str,
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    """Download der Primaerdatei eines Dokuments.

    Gibt den binaeren File-Content zurueck mit korrektem
    Content-Type und Content-Disposition Header.
    """
    client = get_client(request)
    content_bytes, filename, content_type = document_service.download_file(
        client, type_key, code,
    )

    return Response(
        content=content_bytes,
        media_type=content_type or "application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(content_bytes)),
        },
    )
