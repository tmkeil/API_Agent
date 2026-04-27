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
from src.models.dto import BalluffBomExportResponse, BenchmarkResponse, CacheStats, SapExportRequest, SapExportResponse, SapPreviewResponse
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
    max_depth: int | None = None,
    request: Request = None,
    _: None = Depends(require_auth),
):
    from src.core.cache import cache as bom_cache
    cache_key = f"balluff_bom:{part_number}:depth={max_depth}"
    cached = bom_cache.get(cache_key)
    if cached:
        return cached

    client = get_client(request)
    session = get_session(request)
    try:
        result = bom_export_service.balluff_bom_export(client, part_number, max_depth=max_depth)
    except Exception as e:
        raise HTTPException(500, f"Balluff-Export fehlgeschlagen: {e}")

    # Cache for 10 minutes (BOM data changes infrequently)
    bom_cache.set(cache_key, result, ttl=600)

    if session:
        log_session_event(
            session, "GET", f"/api/export/balluff/{part_number}", 200, 0, "web",
            f"balluff export: {part_number} ({result['rowCount']} rows)",
        )
    return result


# ── SAP Preview (nur PartA + PartB) ──────────────────────────


@router.post(
    "/export/sap/preview",
    response_model=SapPreviewResponse,
    summary="SAP Preview — PartA-Transformation + PartB-Validierung",
)
def sap_preview(
    body: SapExportRequest,
    request: Request = None,
    _: None = Depends(require_auth),
):
    session = get_session(request)
    try:
        raw_export = {
            "columns": body.columns,
            "rows": body.rows,
            "partNumber": body.partNumber,
        }
        result = sap_export_service.sap_preview(raw_export, rules=body.rules)
    except Exception as e:
        raise HTTPException(500, f"SAP-Preview fehlgeschlagen: {e}")

    if session:
        log_session_event(
            session, "POST", "/api/export/sap/preview", 200, 0, "web",
            f"sap preview: {body.partNumber} ({result['stats']['totalOutputRows']} rows)",
        )
    return result


# ── SAP Export (aufbereitete CSVs) ───────────────────────────


@router.post(
    "/export/sap",
    response_model=SapExportResponse,
    summary="SAP Export — aufbereitete CSV-Dateien fuer SAP-Import",
)
def sap_export(
    body: SapExportRequest,
    request: Request = None,
    _: None = Depends(require_auth),
):
    session = get_session(request)
    try:
        raw_export = {
            "columns": body.columns,
            "rows": body.rows,
            "partNumber": body.partNumber,
            "fromPreview": body.fromPreview,
        }
        result = sap_export_service.sap_export(raw_export, rules=body.rules)
    except Exception as e:
        raise HTTPException(500, f"SAP-Export fehlgeschlagen: {e}")

    if session:
        log_session_event(
            session, "POST", "/api/export/sap", 200, 0, "web",
            f"sap export: {body.partNumber} ({result['stats']['filesCount']} files)",
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


@router.get(
    "/diagnose/equivalence",
    summary="Equivalence Network — prueft welche OData-Pfade auf diesem Windchill funktionieren",
)
def diagnose_equivalence(
    request: Request,
    _: None = Depends(require_auth),
    partNumber: str = Query(..., description="Part-Nummer (Code)"),
):
    """Probiert mehrere OData-Pfade fuer Equivalence-Links und meldet,
    welche tatsaechlich antworten. Zur Verifikation auf dem echten System
    bevor wir uns auf einen Pfad festlegen.

    Probierte Pfade (jeweils relativ zum Part):
      A) /Parts('{id}')/DownstreamEquivalanceLinks?$expand=Downstream
      B) /Parts('{id}')/DownstreamEquivalanceLinks
      C) /Parts('{id}')/UpstreamEquivalanceLinks?$expand=Upstream
      D) /Parts('{id}')/UpstreamEquivalanceLinks
      E) /Parts('{id}')/BAL_DOWNSTREAMNav
      F) BomTransformation /GetEquivalenceNetworkForParts (Action)
      G) BalluffCustom /GetEquivalence(ProductNumber=...)
    """
    from src.core.odata import extract_id

    client = get_client(request)

    # Resolve part
    try:
        raw_part = client.find_part(partNumber)
    except Exception as e:
        return {"error": f"Part nicht gefunden: {e}", "partNumber": partNumber}

    part_id = extract_id(raw_part)
    base_part = f"{client._odata_url('ProdMgmt')}/Parts('{part_id}')"

    results: list[dict] = []

    def probe(label: str, url: str, params: dict | None = None, method: str = "GET", body: dict | None = None):
        entry: dict = {"label": label, "url": url, "params": params or {}, "method": method}
        try:
            if method == "GET":
                resp = client._get(url, params, suppress_errors=True)
            else:
                resp = client._http.post(url, json=body, timeout=client._timeout)
            if resp is None:
                entry.update(ok=False, status=0, error="no response")
            else:
                entry["status"] = resp.status_code
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        if isinstance(data, dict) and "value" in data:
                            val = data["value"]
                            entry.update(
                                ok=True,
                                count=len(val) if isinstance(val, list) else None,
                                sample=val[:2] if isinstance(val, list) else val,
                            )
                        else:
                            entry.update(ok=True, sample=data)
                    except Exception as je:
                        entry.update(ok=True, parseError=str(je), text=resp.text[:300])
                else:
                    entry.update(ok=False, text=resp.text[:300])
        except Exception as ex:
            entry.update(ok=False, error=str(ex))
        return entry

    # A / B
    results.append(probe(
        "A: WTPart Downstream + $expand=Downstream",
        f"{base_part}/DownstreamEquivalanceLinks",
        {"$expand": "Downstream"},
    ))
    results.append(probe(
        "B: WTPart Downstream (no expand)",
        f"{base_part}/DownstreamEquivalanceLinks",
    ))
    # C / D
    results.append(probe(
        "C: WTPart Upstream + $expand=Upstream",
        f"{base_part}/UpstreamEquivalanceLinks",
        {"$expand": "Upstream"},
    ))
    results.append(probe(
        "D: WTPart Upstream (no expand)",
        f"{base_part}/UpstreamEquivalanceLinks",
    ))
    # E
    results.append(probe(
        "E: WTPart BAL_DOWNSTREAMNav (object refs)",
        f"{base_part}/BAL_DOWNSTREAMNav",
    ))
    # F: BomTransformation action (versioned base path from swagger: v3/BomTransformation)
    bt_url = f"{client.base_url}/servlet/odata/v3/BomTransformation/GetEquivalenceNetworkForParts"
    results.append(probe(
        "F: BomTransformation/GetEquivalenceNetworkForParts",
        bt_url,
        method="POST",
        body={"Parts": [{"ID": part_id}]},
    ))
    # G: BalluffCustom GetEquivalence (basePath: v1/BalluffCustom)
    bc_url = (
        f"{client.base_url}/servlet/odata/v1/BalluffCustom"
        f"/GetEquivalence(ProductNumber=@ProductNumber)"
    )
    results.append(probe(
        "G: BalluffCustom/GetEquivalence(ProductNumber=...)",
        bc_url,
        {"@ProductNumber": f"'{partNumber}'"},
    ))

    summary = [
        {"label": r["label"], "ok": r.get("ok"), "status": r.get("status"),
         "count": r.get("count")}
        for r in results
    ]
    return {
        "partNumber": partNumber,
        "partId": part_id,
        "summary": summary,
        "details": results,
    }


# ── Phase 2a: Branch / Path / SaveAs Action Discovery ───────


@router.get(
    "/diagnose/branch-actions",
    summary="Phase 2a: prueft welche Branch/Path/SaveAs-Actions auf diesem Windchill verfuegbar sind",
)
def diagnose_branch_actions(
    request: Request,
    _: None = Depends(require_auth),
    partNumber: str = Query(..., description="Part-Nummer (Code) eines existierenden Parts"),
):
    """Ermittelt, welche OData-Actions fuer 'New Downstream Branch' / 'Save As' /
    'Revise' / 'CheckOut' auf plm-prod tatsaechlich deployt sind.

    Zwei Probe-Strategien (beide nebenwirkungsfrei):
      1) $metadata (XML) der relevanten Domains laden und nach Action-Namen
         grep'en. Liefert die definitive Liste der bound Actions.
      2) GET auf die Action-URL. 405 'Method Not Allowed' beweist, dass die
         Action existiert (sie erwartet POST). 404 'Not Found' beweist, dass
         sie nicht deployt ist.

    POST-Proben werden BEWUSST NICHT ausgefuehrt, weil sie reale Objekte
    erzeugen wuerden (NewBranch, SaveAs, Revise haben Seiteneffekte!).
    """
    from src.core.odata import extract_id

    client = get_client(request)

    # 1) Part aufloesen
    try:
        raw_part = client.find_part(partNumber)
    except Exception as e:
        return {"error": f"Part nicht gefunden: {e}", "partNumber": partNumber}
    part_id = extract_id(raw_part)

    # 2) Action-Kandidaten (PTC-Standard + Balluff-Custom + bekannte v3-Pfade)
    #    Format: (label, namespace, action_name)
    candidates: list[tuple[str, str, str]] = [
        # PTC ProdMgmt Standard-Actions
        ("PTC.ProdMgmt.NewBranch",                    "PTC.ProdMgmt", "NewBranch"),
        ("PTC.ProdMgmt.SaveAs",                       "PTC.ProdMgmt", "SaveAs"),
        ("PTC.ProdMgmt.Revise",                       "PTC.ProdMgmt", "Revise"),
        ("PTC.ProdMgmt.CheckOut",                     "PTC.ProdMgmt", "CheckOut"),
        ("PTC.ProdMgmt.CheckIn",                      "PTC.ProdMgmt", "CheckIn"),
        ("PTC.ProdMgmt.UndoCheckOut",                 "PTC.ProdMgmt", "UndoCheckOut"),
        ("PTC.ProdMgmt.CreateAlternate",              "PTC.ProdMgmt", "CreateAlternate"),
        ("PTC.ProdMgmt.AssignAlternate",              "PTC.ProdMgmt", "AssignAlternate"),
        ("PTC.ProdMgmt.NewVersion",                   "PTC.ProdMgmt", "NewVersion"),
        ("PTC.ProdMgmt.GenerateStructuredAppearance", "PTC.ProdMgmt", "GenerateStructuredAppearance"),
        # Balluff-Custom (vermutet, von der Diagnose her wahrscheinlich nicht da)
        ("PTC.BalluffCustom.NewDownstreamBranch",     "PTC.BalluffCustom", "NewDownstreamBranch"),
        ("PTC.BalluffCustom.GenerateDownstreamStructure", "PTC.BalluffCustom", "GenerateDownstreamStructure"),
        # v3 BomTransformation (per Diagnose schon als 404 bekannt — als Referenz)
        ("PTC.BomTransformation.GenerateDownstreamStructure",
         "PTC.BomTransformation", "GenerateDownstreamStructure"),
    ]

    base_part = f"{client._odata_url('ProdMgmt')}/Parts('{part_id}')"

    # ── Schritt 1: $metadata grep ────────────────────────────
    metadata_findings: dict[str, dict] = {}
    domains_to_check = ["ProdMgmt", "ChangeMgmt"]
    # Optionale custom Domains (vermutlich 404)
    optional_domains = [
        ("BalluffCustom_v1", f"{client.base_url}/servlet/odata/v1/BalluffCustom/$metadata"),
        ("BalluffCustom_v6", f"{client._odata_url('BalluffCustom')}/$metadata"),
        ("BomTransformation_v3", f"{client.base_url}/servlet/odata/v3/BomTransformation/$metadata"),
    ]

    metadata_blobs: dict[str, str] = {}
    for dom in domains_to_check:
        url = f"{client._odata_url(dom)}/$metadata"
        try:
            resp = client._raw_get(url, timeout=15)
            entry: dict = {"url": url, "status": resp.status_code,
                           "contentType": resp.headers.get("content-type", "")}
            if resp.status_code == 200:
                txt = resp.text or ""
                metadata_blobs[dom] = txt
                entry["sizeBytes"] = len(txt)
            else:
                entry["snippet"] = (resp.text or "")[:300]
            metadata_findings[dom] = entry
        except Exception as e:
            metadata_findings[dom] = {"url": url, "error": str(e)}

    for label, url in optional_domains:
        try:
            resp = client._raw_get(url, timeout=10)
            entry = {"url": url, "status": resp.status_code}
            if resp.status_code == 200:
                txt = resp.text or ""
                metadata_blobs[label] = txt
                entry["sizeBytes"] = len(txt)
            metadata_findings[label] = entry
        except Exception as e:
            metadata_findings[label] = {"url": url, "error": str(e)}

    # In den geladenen Metadata-Blobs nach Action-Namen suchen.
    # Korrektes XML-Parsing — die EDM-Schemas listen <Action Name="..."> Elemente.
    import xml.etree.ElementTree as ET
    EDM_NS = "{http://docs.oasis-open.org/odata/ns/edm}"

    actions_per_domain: dict[str, list[dict]] = {}
    functions_per_domain: dict[str, list[dict]] = {}

    for dom, blob in metadata_blobs.items():
        try:
            root = ET.fromstring(blob)
        except ET.ParseError as pe:
            actions_per_domain[dom] = [{"_parseError": str(pe)}]
            continue
        actions: list[dict] = []
        functions: list[dict] = []
        for sch in root.iter(f"{EDM_NS}Schema"):
            ns = sch.get("Namespace") or ""
            for act in sch.findall(f"{EDM_NS}Action"):
                actions.append({
                    "namespace": ns,
                    "name": act.get("Name") or "",
                    "isBound": (act.get("IsBound") or "").lower() == "true",
                    "fullName": f"{ns}.{act.get('Name')}",
                })
            for fn in sch.findall(f"{EDM_NS}Function"):
                functions.append({
                    "namespace": ns,
                    "name": fn.get("Name") or "",
                    "isBound": (fn.get("IsBound") or "").lower() == "true",
                    "fullName": f"{ns}.{fn.get('Name')}",
                })
        actions_per_domain[dom] = actions
        functions_per_domain[dom] = functions

    # Index: alle bekannten Action-FullNames ueber alle geladenen Metadata-Domains
    known_action_full_names: set[str] = set()
    for acts in actions_per_domain.values():
        for a in acts:
            if "_parseError" not in a:
                known_action_full_names.add(a["fullName"])

    # ── Schritt 2: GET-Probe pro Kandidat ────────────────────
    # WICHTIG: 400 alleine ist KEIN Beweis, dass die Action existiert — der
    # OData-URL-Parser kann fuer beliebige unbekannte Action-Namen 400
    # zurueckgeben. Verdict ist daher die Kombination aus HTTP-Status UND
    # Metadata-Treffer.
    action_probes: list[dict] = []
    for label, namespace, action in candidates:
        url = f"{base_part}/{namespace}.{action}"
        full_name = f"{namespace}.{action}"
        in_metadata = full_name in known_action_full_names
        entry: dict = {"label": label, "url": url, "method": "GET",
                       "inMetadata": in_metadata}
        try:
            resp = client._get(url, None, suppress_errors=True)
            if resp is None:
                entry.update(verdict="unknown", error="no response")
            else:
                entry["status"] = resp.status_code
                status = resp.status_code
                if status == 405:
                    # Action existiert definitiv (erwartet POST)
                    entry.update(verdict="EXISTS",
                                 hint="405 Method Not Allowed → Action ist deployt, erwartet POST")
                elif status == 404:
                    entry.update(verdict="MISSING", hint="404 Not Found")
                elif status in (200, 204):
                    entry.update(verdict="UNEXPECTED_GET_OK",
                                 hint="GET hat geklappt — moeglicherweise Function statt Action",
                                 sample=(resp.text or "")[:200])
                elif status in (400, 422):
                    # Hier brauchen wir Metadata-Bestaetigung
                    if in_metadata:
                        entry.update(verdict="EXISTS",
                                     hint=f"{status} + Metadata-Hit → Action ist deployt")
                    else:
                        entry.update(verdict="MISSING",
                                     hint=f"{status} ohne Metadata-Hit → Action vermutlich nicht deployt (OData parst unbekannte Action-Names oft als 400)",
                                     sample=(resp.text or "")[:200])
                elif status in (401, 403):
                    entry.update(verdict="AUTH",
                                 hint=f"{status} → Auth-Problem oder fehlende Rechte")
                else:
                    entry.update(verdict="OTHER",
                                 sample=(resp.text or "")[:200])
        except Exception as ex:
            entry.update(verdict="ERROR", error=str(ex))
        action_probes.append(entry)

    # ── Zusammenfassung ──────────────────────────────────────
    summary = {
        "exists": [p["label"] for p in action_probes if p.get("verdict") == "EXISTS"],
        "missing": [p["label"] for p in action_probes if p.get("verdict") == "MISSING"],
        "auth": [p["label"] for p in action_probes if p.get("verdict") == "AUTH"],
        "metadataActionsByDomain": {
            dom: sorted([a["fullName"] for a in acts if "_parseError" not in a])
            for dom, acts in actions_per_domain.items()
        },
        "metadataFunctionsByDomain": {
            dom: sorted([f["fullName"] for f in fns if "_parseError" not in f])
            for dom, fns in functions_per_domain.items()
        },
    }

    return {
        "partNumber": partNumber,
        "partId": part_id,
        "summary": summary,
        "metadata": metadata_findings,
        "actionProbes": action_probes,
        "note": (
            "Verdict-Logik: 405 oder (400 + Metadata-Hit) = EXISTS. "
            "400 ohne Metadata-Hit = MISSING (OData liefert oft 400 statt 404 fuer "
            "unbekannte Action-Names). 401/403 = AUTH (z.B. fehlende Rechte auf prod). "
            "POST-Probes wurden bewusst nicht ausgefuehrt, weil sie persistente "
            "Objekte erzeugen wuerden."
        ),
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