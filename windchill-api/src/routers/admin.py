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


@router.delete("/logs", summary="API Log leeren")
def clear_api_logs(
    request: Request = None,
    _: None = Depends(require_auth),
):
    session = get_session(request)
    if session:
        with session.lock:
            session.api_logs.clear()
    return {"cleared": True}


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


# ── Diagnose (OData-Feld-Inspektion) ────────────────────────


@router.get("/diagnose/fields", summary="Zeigt alle OData-Felder eines echten WRS-Records")
def diagnose_fields(
    request: Request,
    _: None = Depends(require_auth),
    entity: str = Query("ProdMgmt/Parts", description="OData-Pfad, z.B. ProdMgmt/Parts"),
    top: int = Query(1, ge=1, le=5),
):
    """Holt 1-5 Records aus dem WRS und zeigt alle Felder + Werte.

    Damit kann man pruefen, welche Felder Windchill tatsaechlich liefert.
    """
    client = get_client(request)
    url = f"{client.odata_base}/{entity}"
    items = client.get_all_pages(url, {"$top": str(top)}, return_none_on_error=True)
    if items is None:
        return {"error": f"Entity '{entity}' nicht erreichbar", "fields": [], "records": []}
    fields = sorted(items[0].keys()) if items else []
    return {
        "entity": entity,
        "recordCount": len(items),
        "fields": fields,
        "records": items[:top],
    }


@router.get(
    "/diagnose/bom-fields",
    summary="BOM Raw Fields — zeigt alle Part- und UsageLink-Felder fuer ein echtes Part",
)
def diagnose_bom_fields(
    request: Request,
    _: None = Depends(require_auth),
    partNumber: str = Query(..., description="Part-Nummer"),
):
    """Holt ein Part + seine BOM Usage-Links und gibt alle Rohfelder zurueck.

    Damit kann man ermitteln, welche Spalten (IBAs) Windchill tatsaechlich
    fuer die Stueckliste liefert.  Nuetzlich fuer BOM-View-Konfiguration.
    """
    import time

    t0 = time.monotonic()
    client = get_client(request)

    # 1) Part laden
    try:
        part_raw = client.find_part(partNumber)
    except Exception as exc:
        return {"error": str(exc), "partFields": [], "usageLinkFields": []}

    part_fields = sorted(part_raw.keys())

    # Filter out nested dicts/lists for display, but keep OData values
    def _simplify(val):
        if isinstance(val, dict):
            # OData enum pattern {Value, Display}
            if "Value" in val:
                return val.get("Display") or val.get("Value")
            if "ID" in val:
                return f"<ref:{val.get('ID', '')[:20]}>"
            return str(val)[:200]
        if isinstance(val, list):
            return f"<list:{len(val)} items>"
        return val

    part_simple = {k: _simplify(v) for k, v in part_raw.items() if not k.startswith("@")}

    # 2) Usage-Links (BOM children) laden
    from src.core.odata import extract_id

    part_id = extract_id(part_raw)
    usage_links_raw = client.get_bom_children(part_id)

    link_fields: list[str] = []
    links_simple: list[dict] = []
    for link in usage_links_raw[:5]:  # max 5 links for overview
        link_fields_set = set(link_fields)
        for k in link.keys():
            if not k.startswith("@") and k not in link_fields_set:
                link_fields.append(k)
                link_fields_set.add(k)
        links_simple.append({k: _simplify(v) for k, v in link.items() if not k.startswith("@")})

    # 3) Try resolving one child for child-Part field overview
    child_raw = None
    child_fields: list[str] = []
    child_simple: dict = {}
    if usage_links_raw:
        child_raw = client.resolve_usage_link_child(usage_links_raw[0])
        if child_raw:
            child_fields = sorted(child_raw.keys())
            child_simple = {k: _simplify(v) for k, v in child_raw.items() if not k.startswith("@")}

    ms = round((time.monotonic() - t0) * 1000, 1)

    return {
        "partNumber": partNumber,
        "durationMs": ms,
        "part": {
            "fieldCount": len(part_fields),
            "fields": part_fields,
            "sample": part_simple,
        },
        "usageLinks": {
            "totalCount": len(usage_links_raw),
            "shownCount": len(links_simple),
            "fieldCount": len(link_fields),
            "fields": link_fields,
            "samples": links_simple,
        },
        "childPart": {
            "fieldCount": len(child_fields),
            "fields": child_fields,
            "sample": child_simple,
        } if child_raw else None,
    }
