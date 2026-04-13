"""
Router: Administrative / Infrastruktur-Endpoints.

Endpoints:
  GET    /logs                               → API Activity Log
  POST   /export                             → BOM als JSON exportieren
  GET    /export/download/{filename}         → Export-Datei herunterladen
  GET    /export/balluff/{part_number}       → Balluff BOM Export (flat table)
  GET    /benchmark                          → Performance-Benchmark
  GET    /cache/stats                        → Cache-Status
  DELETE /cache                              → Cache leeren
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse

from src.core.auth import require_auth
from src.core.cache import cache
from src.core.dependencies import get_client, get_session
from src.core.session import log_session_event
from src.models.dto import BalluffBomExportResponse, BenchmarkResponse, CacheStats, SapExportResponse
from src.services import admin_service, bom_export_service, parts_service, sap_export_service

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
    if mode not in ("expandedOnly", "fullTree", "extended"):
        raise HTTPException(400, "Ungültiger Exportmodus")

    if mode == "extended":
        # Extended: Design + Manufacturing Equivalents + their BOMs
        client = get_client(request)
        try:
            _, filename = admin_service.build_extended_export(
                client, part_number, session.system_url, session.username,
            )
        except Exception as e:
            raise HTTPException(500, f"Extended-Export fehlgeschlagen: {e}")
    elif mode == "fullTree":
        # Server-side full BOM explosion
        client = get_client(request)
        try:
            _, filename = admin_service.build_full_tree_export(
                client, part_number, session.system_url, session.username,
            )
        except Exception as e:
            raise HTTPException(500, f"Full-Tree-Export fehlgeschlagen: {e}")
    else:
        # expandedOnly — uses frontend-provided tree
        root_tree = payload.get("tree")
        if not isinstance(root_tree, dict):
            raise HTTPException(400, "Für expandedOnly ist ein Tree-Objekt erforderlich")
        client = get_client(request)
        try:
            _, filename = admin_service.build_export(
                root_tree, part_number, session.system_url, session.username,
                client=client,
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


# ── Balluff BOM Export (flat table) ──────────────────────────


@router.get(
    "/export/balluff/{part_number}",
    response_model=BalluffBomExportResponse,
    summary="Balluff BOM Export als flache Tabelle",
)
def balluff_bom_export(
    part_number: str,
    request: Request = None,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    session = get_session(request)
    try:
        result = bom_export_service.balluff_bom_export(client, part_number)
    except Exception as e:
        raise HTTPException(500, f"Balluff-Export fehlgeschlagen: {e}")

    if session:
        log_session_event(
            session, "GET", f"/api/export/balluff/{part_number}", 200, 0, "web",
            f"balluff export: {part_number} ({result['rowCount']} rows)",
        )
    return result


# ── SAP Export (aufbereitete CSVs) ───────────────────────────


@router.get(
    "/export/sap/{part_number}",
    response_model=SapExportResponse,
    summary="SAP Export — aufbereitete CSV-Dateien fuer SAP-Import",
)
def sap_export(
    part_number: str,
    request: Request = None,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    session = get_session(request)
    try:
        raw_export = bom_export_service.balluff_bom_export(client, part_number)
        result = sap_export_service.sap_export(raw_export)
    except Exception as e:
        raise HTTPException(500, f"SAP-Export fehlgeschlagen: {e}")

    if session:
        log_session_event(
            session, "GET", f"/api/export/sap/{part_number}", 200, 0, "web",
            f"sap export: {part_number} ({result['stats']['filesCount']} files)",
        )
    return result


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
    # Domain aus Entity-Pfad extrahieren (z.B. "ProdMgmt/Parts" -> "ProdMgmt")
    domain = entity.split("/")[0] if "/" in entity else entity
    entity_path = entity.split("/", 1)[1] if "/" in entity else ""
    if entity_path:
        url = f"{client._odata_url(domain)}/{entity_path}"
    else:
        url = client._odata_url(domain)
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


@router.get("/diagnose/service-doc", summary="OData Service-Dokument — zeigt alle Entity Sets")
def diagnose_service_doc(
    request: Request,
    _: None = Depends(require_auth),
    domain: str = Query("ProdMgmt", description="OData Domain, z.B. ProdMgmt, DocMgmt"),
):
    """Ruft das OData Service-Dokument ab und listet alle Entity Sets.

    Testet sowohl den versionierten (z.B. /odata/v6/ProdMgmt)
    als auch den unversionierten Pfad (/odata/ProdMgmt).
    """
    client = get_client(request)
    results = {}

    for label, base in [
        ("versioned", client._odata_url(domain)),
        ("unversioned", f"{client.base_url}/servlet/odata/{domain}"),
    ]:
        url = base
        try:
            resp = client._raw_get(url, timeout=15)
            results[label] = {
                "url": url,
                "status": resp.status_code,
                "entity_sets": [],
            }
            if resp.status_code == 200:
                data = resp.json()
                # OData service doc: {"value": [{"name": "Parts", "url": "Parts"}, ...]}
                entity_sets = [item.get("name", item.get("url", "")) for item in data.get("value", [])]
                results[label]["entity_sets"] = sorted(entity_sets)
        except Exception as e:
            results[label] = {"url": url, "error": str(e)}

    return {"domain": domain, "results": results}


@router.get(
    "/diagnose/classifications",
    summary="Classification-Werte fuer Part-Erstellung entdecken",
)
def diagnose_classifications(
    request: Request,
    _: None = Depends(require_auth),
    type_path: str = Query(
        "ProdMgmt/Parts",
        description="OData Type-Pfad",
    ),
):
    """Versucht, die verfuegbaren Classifications zu ermitteln.

    Testet mehrere Ansaetze:
    1. OData $metadata fuer den Type (Enum-Definitionen)
    2. Bekannte Entity Sets: ClassificationNodes, Classifications
    3. Distinct-Werte aus existierenden Parts
    """
    client = get_client(request)
    results: dict = {}

    # 1) $metadata pruefen
    for label, base in [("versioned", client._odata_url(type_path.split('/')[0])), ("unversioned", f"{client.base_url}/servlet/odata")]:
        meta_url = f"{base}/{type_path.split('/')[0]}/$metadata"
        try:
            resp = client._raw_get(meta_url, timeout=15)
            results[f"metadata_{label}"] = {
                "url": meta_url,
                "status": resp.status_code,
                "contentType": resp.headers.get("content-type", ""),
                "snippet": resp.text[:2000] if resp.status_code == 200 else None,
            }
        except Exception as e:
            results[f"metadata_{label}"] = {"url": meta_url, "error": str(e)}

    # 2) Bekannte Classification Entity Sets testen
    for domain_entity in [
        "ProdMgmt/ClassificationNodes",
        "ProdMgmt/Classifications",
        "DataAdmin/ClassificationNodes",
        "DataAdmin/Classifications",
        "Classification/Nodes",
        "Classification/ClassificationNodes",
    ]:
        url = f"{client._odata_url(domain_entity.split('/')[0])}/{domain_entity.split('/', 1)[1]}"
        try:
            resp = client._raw_get(url, timeout=10)
            entry: dict = {"url": url, "status": resp.status_code}
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("value", [])
                entry["count"] = len(items)
                if items:
                    entry["sampleFields"] = sorted(items[0].keys())
                    entry["sample"] = items[0]
            results[domain_entity] = entry
        except Exception as e:
            results[domain_entity] = {"url": url, "error": str(e)}

    # 3) Distinct Classification-Werte aus echten Parts (Top 50)
    try:
        url = f"{client._odata_url('ProdMgmt')}/Parts"
        params = {
            "$select": "Number,Name,BAL_CLASSIFICATION_BINDING_WTPART",
            "$top": "50",
        }
        items = client.get_all_pages(url, params, return_none_on_error=True)
        if items:
            values = set()
            for it in items:
                val = it.get("BAL_CLASSIFICATION_BINDING_WTPART", "")
                if val:
                    values.add(str(val) if not isinstance(val, dict) else str(val.get("Value", val)))
            results["distinctFromParts"] = {
                "sampleSize": len(items),
                "distinctValues": sorted(values),
            }
        else:
            results["distinctFromParts"] = {"error": "Keine Parts geladen"}
    except Exception as e:
        results["distinctFromParts"] = {"error": str(e)}

    return {"typePath": type_path, "results": results}
