"""
Router: Change-Management-Endpoints.

Endpoints:
  GET /changes/{type_key}/{code}/affected  → Affected Items
  GET /changes/{type_key}/{code}/resulting → Resulting Items
"""

import logging

from fastapi import APIRouter, Depends, Request

from src.core.auth import require_auth
from src.core.dependencies import get_client
from src.models.dto import ChangeItemsResponse
from src.services import change_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/changes", tags=["changes"])


@router.get(
    "/{type_key}/{code}/affected",
    response_model=ChangeItemsResponse,
    summary="Affected Items eines Change-Objekts",
)
def affected_items(
    type_key: str,
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return change_service.get_affected_items(client, type_key, code)


@router.get(
    "/{type_key}/{code}/resulting",
    response_model=ChangeItemsResponse,
    summary="Resulting Items eines Change-Objekts",
)
def resulting_items(
    type_key: str,
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return change_service.get_resulting_items(client, type_key, code)
