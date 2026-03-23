"""
Router: Administrative / Infrastruktur-Endpoints.

Endpoints:
  GET    /logs                       → API Activity Log
  POST   /export                     → BOM als JSON exportieren
  GET    /export/download/{filename} → Export-Datei herunterladen
  GET    /benchmark                  → Performance-Benchmark
  GET    /cache/stats                → Cache-Status
  DELETE /cache                      → Cache leeren
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse

from src.core.auth import require_auth
from src.core.cache import cache
from src.core.dependencies import get_client, get_session
from src.core.session import log_session_event
from src.models.dto import BenchmarkResponse, CacheStats
from src.services import admin_service, parts_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ── API Logs ─────────────────────────────────────────────────


@router.get("/logs", summary="API Activity Log")
def api_logs(
    limit: int = Query(120, ge=1, le=500),
    request: Request = None,
    _: None = Depends(require_auth),
):
    session = get_session(request)
    if not session:
        return {"items": []}
    with session.lock:
        items = list(session.api_logs)[:limit]
    return {"items": items}


# ── JSON Export ──────────────────────────────────────────────


@router.post("/export", summary="BOM als JSON exportieren")
async def export_bom(
    request: Request,
    _: None = Depends(require_auth),
):
    session = get_session(request)
    if not session:
        raise HTTPException(401, "Nicht authentifiziert")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(400, "Ungültiger JSON-Body")

    mode = str(payload.get("mode", "expandedOnly"))
    part_number = str(payload.get("partNumber", "")).strip()

    if not part_number:
        raise HTTPException(400, "partNumber fehlt")
    if mode not in ("expandedOnly", "fullTree"):
        raise HTTPException(400, "Ungültiger Exportmodus")
    if mode != "expandedOnly":
        raise HTTPException(501, "fullTree-Export wird noch nicht unterstützt")

    root_tree = payload.get("tree")
    if not isinstance(root_tree, dict):
        raise HTTPException(400, "Für expandedOnly ist ein Tree-Objekt erforderlich")

    try:
        _, filename = admin_service.build_export(
            root_tree, part_number, session.system_url, session.username,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    log_session_event(
        session, "POST", "/api/export", 200, 0, "web",
        f"export {mode}: {filename}",
    )
    return {
        "ok": True,
        "filename": filename,
        "downloadUrl": f"/api/export/download/{filename}",
    }


@router.get("/export/download/{filename}", summary="Export-Datei herunterladen")
def export_download(
    filename: str,
    _: None = Depends(require_auth),
):
    filepath = admin_service.get_export_filepath(filename)
    if not filepath:
        raise HTTPException(404, "Datei nicht gefunden")
    return FileResponse(filepath, filename=filename, media_type="application/json")


# ── Benchmark ────────────────────────────────────────────────


@router.get(
    "/benchmark",
    response_model=BenchmarkResponse,
    summary="Performance-Benchmark",
)
def benchmark(
    code: str = Query(...),
    request: Request = None,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return admin_service.run_benchmark(client, code)


# ── Cache ────────────────────────────────────────────────────


@router.get(
    "/cache/stats",
    response_model=CacheStats,
    summary="Cache-Status",
)
def cache_stats(_: None = Depends(require_auth)):
    return parts_service.get_cache_stats()


@router.delete("/cache", summary="Cache leeren")
def clear_cache(_: None = Depends(require_auth)):
    cache.clear()
    return {"message": "Cache geleert."}
