"""
Router: Schreibende Operationen auf Windchill-Objekte.

Endpoints:
  POST   /write/create                          → Neues Objekt erstellen
  PATCH  /write/{type_key}/{code}/attributes     → Attribute aendern
  POST   /write/{type_key}/{code}/state          → Lifecycle-Status setzen
  POST   /write/{type_key}/{code}/checkout       → Auschecken
  POST   /write/{type_key}/{code}/checkin        → Einchecken  POST   /write/{type_key}/{code}/revise         → Neue Revision erstellen
  POST   /write/bom/{code}/add-child             → BOM Kind hinzufuegen
  POST   /write/bom/remove-child                 → BOM Kind entfernen"""

import logging

from fastapi import APIRouter, Depends, Query, Request

from src.core.auth import require_auth
from src.core.dependencies import get_client
from src.models.dto import (
    AddBomChildRequest,
    CreateObjectRequest,
    RemoveBomChildRequest,
    SetStateRequest,
    UpdateAttributesRequest,
    WriteResponse,
)
from src.services import write_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/write", tags=["write"])


@router.post(
    "/create",
    response_model=WriteResponse,
    summary="Neues Windchill-Objekt erstellen",
)
def create_object(
    body: CreateObjectRequest,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return write_service.create_object(client, body.typeKey, body.attributes)


@router.patch(
    "/{type_key}/{code}/attributes",
    response_model=WriteResponse,
    summary="Attribute eines Objekts aendern",
)
def update_attributes(
    type_key: str,
    code: str,
    body: UpdateAttributesRequest,
    request: Request,
    _: None = Depends(require_auth),
    objectId: str | None = Query(None, description="Direkte OData Object-ID (ueberspringt Nummernsuche)"),
):
    client = get_client(request)
    return write_service.update_attributes(client, type_key, code, body.attributes, object_id=objectId)


@router.post(
    "/{type_key}/{code}/state",
    response_model=WriteResponse,
    summary="Lifecycle-Status aendern",
)
def set_state(
    type_key: str,
    code: str,
    body: SetStateRequest,
    request: Request,
    _: None = Depends(require_auth),
    objectId: str | None = Query(None, description="Direkte OData Object-ID"),
):
    client = get_client(request)
    return write_service.set_lifecycle_state(
        client, type_key, code, body.targetState, body.comment or "",
        object_id=objectId,
    )


@router.post(
    "/{type_key}/{code}/checkout",
    response_model=WriteResponse,
    summary="Objekt auschecken",
)
def checkout_object(
    type_key: str,
    code: str,
    request: Request,
    _: None = Depends(require_auth),
    objectId: str | None = Query(None, description="Direkte OData Object-ID"),
):
    client = get_client(request)
    return write_service.checkout(client, type_key, code, object_id=objectId)


@router.post(
    "/{type_key}/{code}/checkin",
    response_model=WriteResponse,
    summary="Objekt einchecken",
)
def checkin_object(
    type_key: str,
    code: str,
    request: Request,
    _: None = Depends(require_auth),
    objectId: str | None = Query(None, description="Direkte OData Object-ID"),
):
    client = get_client(request)
    return write_service.checkin(client, type_key, code, object_id=objectId)


# ── Revise ───────────────────────────────────────────────────


@router.post(
    "/{type_key}/{code}/revise",
    response_model=WriteResponse,
    summary="Neue Revision erstellen",
)
def revise_object(
    type_key: str,
    code: str,
    request: Request,
    _: None = Depends(require_auth),
    objectId: str | None = Query(None, description="Direkte OData Object-ID"),
):
    client = get_client(request)
    return write_service.revise(client, type_key, code, object_id=objectId)


# ── BOM Children (UsageLinks) ───────────────────────────────


@router.post(
    "/bom/{code}/add-child",
    response_model=WriteResponse,
    summary="Kind-Part zur BOM hinzufuegen",
)
def add_bom_child(
    code: str,
    body: AddBomChildRequest,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return write_service.add_bom_child(
        client, code, body.childPartNumber, body.quantity, body.unit,
    )


@router.post(
    "/bom/remove-child",
    response_model=WriteResponse,
    summary="BOM-Kind-Beziehung entfernen",
)
def remove_bom_child(
    body: RemoveBomChildRequest,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return write_service.remove_bom_child(client, body.usageLinkId)
