"""
Business logic: Bulk/Batch-Abfragen.

Holt Details fuer mehrere Objekte parallel (ThreadPoolExecutor).
Nutzt die bestehende find_object-Logik des Adapters.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.adapters.wrs_client import WRSClient
from src.core.odata import normalize_item
from src.models.dto import (
    BulkDetailResult,
    BulkResponse,
    ObjectDetail,
    TimingInfo,
)

logger = logging.getLogger(__name__)

_BULK_EXECUTOR = ThreadPoolExecutor(max_workers=8)


def _fetch_one(client: WRSClient, type_key: str, code: str) -> BulkDetailResult:
    """Einzelnes Objekt holen — laeuft im Thread."""
    try:
        raw = client.find_object(type_key, code)
        n = normalize_item(raw)
        detail = ObjectDetail(
            objectId=n["id"],
            objectType=n.get("_entity_type", ""),
            typeKey=n.get("_entity_type_key", type_key),
            number=n["number"],
            name=n["name"],
            version=n["version"],
            iteration=n["iteration"],
            state=n["state"],
            identity=n["identity"],
            context=n["context"],
            lastModified=n["last_modified"],
            createdOn=n["created_on"],
        )
        return BulkDetailResult(
            typeKey=type_key, code=code, ok=True, detail=detail,
        )
    except Exception as exc:
        return BulkDetailResult(
            typeKey=type_key, code=code, ok=False, error=str(exc),
        )


def bulk_details(
    client: WRSClient,
    items: list[dict],
    *,
    max_concurrent: int = 8,
) -> BulkResponse:
    """Details fuer eine Liste von (typeKey, code)-Paaren parallel abrufen.

    Args:
        items: Liste von {"typeKey": "part", "code": "123"}.
        max_concurrent: Max. Thread-Parallelitaet.
    """
    t0 = time.monotonic()
    results: list[BulkDetailResult] = []

    futures = {
        _BULK_EXECUTOR.submit(
            _fetch_one, client, it["typeKey"], it["code"]
        ): idx
        for idx, it in enumerate(items)
    }

    # Collect in submission order
    ordered: dict[int, BulkDetailResult] = {}
    for future in as_completed(futures):
        idx = futures[future]
        ordered[idx] = future.result()

    results = [ordered[i] for i in range(len(items))]

    total_ok = sum(1 for r in results if r.ok)
    total_err = sum(1 for r in results if not r.ok)
    ms = round((time.monotonic() - t0) * 1000, 1)

    return BulkResponse(
        totalRequested=len(items),
        totalFound=total_ok,
        totalErrors=total_err,
        results=results,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )
