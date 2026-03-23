"""
Router: Versions- und Lifecycle-Endpoints.

Endpoints:
  GET /objects/{type_key}/{code}/versions  → Alle Versionen/Iterationen
  GET /objects/{type_key}/{code}/lifecycle → Lifecycle-History (Status-Uebergaenge)
"""

import logging

from fastapi import APIRouter, Depends, Request

from src.core.auth import require_auth
from src.core.dependencies import get_client
from src.models.dto import LifecycleResponse, VersionsResponse
from src.services import version_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["versions"])


@router.get(
    "/objects/{type_key}/{code}/versions",
    response_model=VersionsResponse,
    summary="Alle Versionen/Iterationen eines Objekts",
)
def object_versions(
    type_key: str,
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return version_service.get_all_versions(client, type_key, code)


@router.get(
    "/objects/{type_key}/{code}/lifecycle",
    response_model=LifecycleResponse,
    summary="Lifecycle-History (Status-Uebergaenge)",
)
def lifecycle_history(
    type_key: str,
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return version_service.get_lifecycle_history(client, type_key, code)
