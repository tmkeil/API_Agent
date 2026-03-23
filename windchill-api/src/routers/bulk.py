"""
Router: Bulk/Batch-Abfragen.

Endpoints:
  POST /bulk/details → Details fuer mehrere Objekte auf einmal
"""

import logging

from fastapi import APIRouter, Depends, Request

from src.core.auth import require_auth
from src.core.dependencies import get_client
from src.models.dto import BulkRequest, BulkResponse

from src.services import bulk_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bulk", tags=["bulk"])


@router.post(
    "/details",
    response_model=BulkResponse,
    summary="Details fuer mehrere Objekte parallel abrufen",
)
def bulk_details(
    body: BulkRequest,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    items = [{"typeKey": it.typeKey, "code": it.code} for it in body.items]
    return bulk_service.bulk_details(client, items)
