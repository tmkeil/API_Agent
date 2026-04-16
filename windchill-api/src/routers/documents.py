"""
Router: Dokument-Detail-Endpoints.

Endpoints:
  GET /documents/{type_key}/{code}/referencing-parts → Parts die dieses Dokument referenzieren
  GET /documents/{type_key}/{code}/files             → Datei-Info (ContentHolders)
  GET /documents/{type_key}/{code}/download          → Primaerdatei herunterladen
  GET /documents/cad/{code}/structure                → CAD Assembly-Struktur
  GET /documents/cad/{code}/structure/csv            → CAD Assembly-Struktur als CSV
"""

import csv
import io
import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from src.core.auth import require_auth
from src.core.dependencies import get_client
from src.models.dto import CadStructureResponse, FileInfoResponse, ReferencingPartsResponse
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


# ── CAD Assembly Structure ───────────────────────────────────


@router.get(
    "/cad/{code}/structure",
    response_model=CadStructureResponse,
    summary="CAD Assembly-Struktur eines CAD-Dokuments",
)
def cad_structure(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return document_service.get_cad_structure(client, code)


@router.get(
    "/cad/{code}/structure/csv",
    summary="CAD Assembly-Struktur als CSV-Download",
    responses={200: {"content": {"text/csv": {}}}},
)
def cad_structure_csv(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    """CSV-Export der CAD Assembly-Struktur.

    Spalten: Level, File Name, Version, Quantity, Number, Dependency Type, State
    """
    client = get_client(request)
    result = document_service.get_cad_structure(client, code)

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Level", "File Name", "Version", "Quantity", "Number", "Dependency Type", "State"])
    for node in result.nodes:
        writer.writerow([
            node.level,
            node.fileName,
            node.version,
            node.quantity,
            node.number,
            node.dependencyType,
            node.state,
        ])

    csv_content = output.getvalue()
    filename = f"CAD_Structure_{code}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
