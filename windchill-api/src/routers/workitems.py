"""
Router: WorkItem-Endpoints (Projektfortschritt-Tracking).

Endpoints:
  GET    /workitems                      → Alle WorkItems auflisten
  POST   /workitems                      → Neues WorkItem anlegen
  GET    /workitems/{id}                 → WorkItem laden
  PATCH  /workitems/{id}                 → WorkItem aktualisieren
  DELETE /workitems/{id}                 → WorkItem loeschen
  POST   /workitems/{id}/steps           → Arbeitsschritt hinzufuegen
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.core.auth import require_auth
from src.models.dto import WorkItem, WorkItemListResponse
from src.services import workitem_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/workitems", tags=["workitems"])


class CreateWorkItemRequest(BaseModel):
    """CN-Daten zum Erstellen eines WorkItems."""
    number: str
    name: str = ""
    subType: str = ""
    state: str = ""
    objectId: str = ""


class UpdateWorkItemRequest(BaseModel):
    """Erlaubte Felder zum Aktualisieren."""
    resultingParts: list[dict] | None = None
    selectedPart: dict | None = None
    bomData: list[dict] | None = None
    bomColumns: list[str] | None = None
    status: str | None = None


class AddStepRequest(BaseModel):
    """Arbeitsschritt hinzufuegen."""
    step: str
    data: dict = {}


@router.get(
    "",
    response_model=WorkItemListResponse,
    summary="Alle WorkItems auflisten",
)
def list_workitems(_: None = Depends(require_auth)):
    return workitem_service.list_workitems()


@router.post(
    "",
    response_model=WorkItem,
    summary="Neues WorkItem fuer eine Change Notice anlegen",
    status_code=201,
)
def create_workitem(
    body: CreateWorkItemRequest,
    _: None = Depends(require_auth),
):
    cn_data = body.model_dump()
    return workitem_service.create_workitem(cn_data)


@router.get(
    "/{workitem_id}",
    response_model=WorkItem,
    summary="WorkItem laden",
)
def get_workitem(workitem_id: str, _: None = Depends(require_auth)):
    wi = workitem_service.get_workitem(workitem_id)
    if wi is None:
        raise HTTPException(status_code=404, detail=f"WorkItem '{workitem_id}' nicht gefunden")
    return wi


@router.patch(
    "/{workitem_id}",
    response_model=WorkItem,
    summary="WorkItem aktualisieren",
)
def update_workitem(
    workitem_id: str,
    body: UpdateWorkItemRequest,
    _: None = Depends(require_auth),
):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    wi = workitem_service.update_workitem(workitem_id, updates)
    if wi is None:
        raise HTTPException(status_code=404, detail=f"WorkItem '{workitem_id}' nicht gefunden")
    return wi


@router.delete(
    "/{workitem_id}",
    summary="WorkItem loeschen",
)
def delete_workitem(workitem_id: str, _: None = Depends(require_auth)):
    if not workitem_service.delete_workitem(workitem_id):
        raise HTTPException(status_code=404, detail=f"WorkItem '{workitem_id}' nicht gefunden")
    return {"ok": True}


@router.post(
    "/{workitem_id}/steps",
    response_model=WorkItem,
    summary="Arbeitsschritt hinzufuegen",
)
def add_step(
    workitem_id: str,
    body: AddStepRequest,
    _: None = Depends(require_auth),
):
    wi = workitem_service.add_step(workitem_id, body.step, body.data)
    if wi is None:
        raise HTTPException(status_code=404, detail=f"WorkItem '{workitem_id}' nicht gefunden")
    return wi
