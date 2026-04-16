"""
Router: Change-Management-Endpoints.

Endpoints:
  GET  /changes/{type_key}/{code}/affected        → Affected Items
  GET  /changes/{type_key}/{code}/resulting        → Resulting Items
  POST /changes/check-part-results                 → Batch-Check: welche CNs haben Part Resulting Items
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

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


# ── Batch Check: CNs mit Part Resulting Items ────────────────


class CheckPartResultsRequest(BaseModel):
    """Liste von CN-Nummern zum Pruefen."""
    numbers: list[str]


class CheckPartResultsResponse(BaseModel):
    """Ergebnis: Welche CNs haben Part Resulting Items."""
    withParts: list[str] = []


@router.post(
    "/check-part-results",
    response_model=CheckPartResultsResponse,
    summary="Batch-Check: welche Change Notices haben Part Resulting Items",
)
def check_part_results(
    body: CheckPartResultsRequest,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    with_parts: list[str] = []

    def _check(code: str) -> tuple[str, bool]:
        return code, change_service.has_part_resulting_items(client, code)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(_check, code) for code in body.numbers[:50]]
        for f in as_completed(futures):
            code, has = f.result()
            if has:
                with_parts.append(code)

    return CheckPartResultsResponse(withParts=with_parts)
