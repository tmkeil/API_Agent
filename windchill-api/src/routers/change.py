"""
Router: Change-Management-Endpoints.

Endpoints:
  GET  /changes/change_notices                     → Change Notices auflisten
  GET  /changes/change_notices/stream              → Streaming-Auflistung (SSE)
  GET  /changes/{type_key}/{code}/affected        → Affected Items
  GET  /changes/{type_key}/{code}/resulting        → Resulting Items
  POST /changes/check-part-results                 → Batch-Check: welche CNs haben Part Resulting Items
"""

import asyncio
import json
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.core.auth import require_auth
from src.core.dependencies import get_client
from src.core.odata import normalize_item
from src.models.dto import ChangeItemsResponse, ChangeNoticeListResponse
from src.services import change_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/changes", tags=["changes"])


@router.get(
    "/change_notices",
    response_model=ChangeNoticeListResponse,
    summary="Change Notices auflisten (optional gefiltert nach State/SubType)",
)
def list_change_notices(
    request: Request,
    state: str = "",
    sub_type: str = "",
    top: int = 50,
    skip: int = 0,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return change_service.list_change_notices(
        client, state=state, sub_type=sub_type, top=min(top, 1000), skip=skip,
    )


# ── Streaming CN List (SSE) ─────────────────────────────────


def _to_cn_item(raw: dict) -> dict:
    """Convert raw OData dict to a CN list item dict for SSE."""
    n = normalize_item(raw)
    return {
        "objectId": n["id"],
        "number": n["number"],
        "name": n["name"],
        "subType": str(raw.get("ObjectType") or ""),
        "version": n["version"],
        "state": n["state"],
        "createdBy": str(raw.get("CreatedBy") or n.get("created_by", "")),
        "createdOn": n.get("created_on", ""),
        "lastModified": n.get("last_modified", ""),
        "description": str(raw.get("Description") or ""),
    }


@router.get(
    "/change_notices/stream",
    summary="Change Notices als SSE-Stream (progressive Darstellung)",
)
async def stream_change_notices(
    request: Request,
    state: str = "",
    sub_type: str = "",
    top: int = Query(1000, ge=1, le=5000),
    _: None = Depends(require_auth),
):
    """SSE-Endpoint: Liefert CN-Batches als `data:` Events.

    Jedes Event enthaelt ein JSON-Array von CN-Items.
    Am Ende kommt ein `event: done` mit Zusammenfassung.
    Erkennt Client-Disconnect und bricht ab.
    """
    client = get_client(request)

    async def _generate():
        total = 0
        t0 = time.perf_counter()

        queue: asyncio.Queue[list[dict] | None] = asyncio.Queue()
        cancelled = threading.Event()
        loop = asyncio.get_event_loop()

        def _producer():
            try:
                for batch in client.list_change_notices_stream(
                    state=state,
                    sub_type=sub_type,
                    top=top,
                    cancelled=cancelled,
                ):
                    if cancelled.is_set():
                        break
                    items = [_to_cn_item(raw) for raw in batch]
                    if items:
                        loop.call_soon_threadsafe(queue.put_nowait, items)
            except Exception:
                logger.debug("CN SSE producer error", exc_info=True)
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, None)

        thread = threading.Thread(target=_producer, daemon=True)
        thread.start()

        try:
            while True:
                while True:
                    if await request.is_disconnected():
                        logger.info("CN SSE client disconnected, cancelling")
                        cancelled.set()
                        return
                    try:
                        batch = await asyncio.wait_for(queue.get(), timeout=0.5)
                        break
                    except asyncio.TimeoutError:
                        continue

                if batch is None:
                    break

                total += len(batch)
                yield f"data: {json.dumps(batch, ensure_ascii=False)}\n\n"

            duration_ms = int((time.perf_counter() - t0) * 1000)
            yield f"event: done\ndata: {json.dumps({'total': total, 'durationMs': duration_ms})}\n\n"
        finally:
            cancelled.set()
            thread.join(timeout=5)

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


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
