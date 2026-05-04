"""REST endpoints for WTPart-specific operations.

Covers: Part detail, Documents, CAD-Documents, Where-Used,
Occurrences, BOM root/children.

Search, Object-Detail, Export, Benchmark, Cache and Logs
live in  routers/search.py  and  routers/admin.py.
"""

import logging
import time

from fastapi import APIRouter, Depends, Query, Request

from src.core.auth import require_auth
from src.core.bom_views import BOM_VIEWS
from src.core.dependencies import get_client, get_session
from src.core.session import log_session_event
from src.models.dto import (
    BomNodeResponse,
    BomTransformerResponse,
    BomViewConfig,
    ClassificationNodeListResponse,
    ContainerListResponse,
    DocumentListResponse,
    EquivalenceNetworkResponse,
    OccurrencesResponse,
    PartDetailResponse,
    PartSubtypeListResponse,
    TransformDetectRequest,
    TransformGenerateRequest,
    TransformCopyRequest,
    TransformRemoveRequest,
    TransformRemoveResponse,
    TransformResponse,
    WhereUsedResponse,
)
from src.services import parts_service
from src.services import bom_transformer_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Part Detail ──────────────────────────────────────────────


@router.get(
    "/parts/{code}",
    response_model=PartDetailResponse,
    summary="Teilestammdaten",
)
def get_part(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return parts_service.get_part_detail(client, code)


# ── Documents ────────────────────────────────────────────────


@router.get(
    "/parts/{code}/documents",
    response_model=DocumentListResponse,
    summary="Dokumente eines Parts (DescribedBy)",
)
def get_documents(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return parts_service.get_part_documents(client, code)


@router.get(
    "/parts/{code}/cad-documents",
    response_model=DocumentListResponse,
    summary="CAD-Dokumente eines Parts (EPM)",
)
def get_cad_documents(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return parts_service.get_part_cad_documents(client, code)


# ── Where-Used ───────────────────────────────────────────────


@router.get(
    "/parts/{code}/where-used",
    response_model=WhereUsedResponse,
    summary="Einsatzverwendung (Where-Used)",
)
def get_where_used(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return parts_service.get_part_where_used(client, code)


# ── Equivalence Network ──────────────────────────────────────


@router.get(
    "/parts/{code}/equivalence",
    response_model=EquivalenceNetworkResponse,
    summary="Equivalence Network (Design ↔ Manufacturing) via OData Nav",
)
def get_equivalence(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return parts_service.get_part_equivalence(client, code)


@router.get(
    "/parts/{code}/transformer",
    response_model=BomTransformerResponse,
    summary="BOM Transformer dual-tree view (Design + Manufacturing)",
)
def get_transformer(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    session = get_session(request)
    return bom_transformer_service.get_transformer_view(client, code, session=session)


@router.get(
    "/_debug/part/{part_id:path}",
    summary="DEV: dump raw Part JSON + master-lookup attempts",
)
def debug_part(
    part_id: str,
    request: Request,
    _: None = Depends(require_auth),
):
    """Diagnostic only: returns the raw Part dict + tries common 'Master' lookup
    forms, so we can see which navigation/property/$expand actually exists.
    """
    import logging as _logging
    log = _logging.getLogger("debug_part")
    client = get_client(request)
    base = f"{client._odata_url('ProdMgmt')}/Parts('{part_id}')"
    out: dict = {"part_id": part_id, "base": base}
    # 1) plain
    r = client._get(base, None, suppress_errors=True)
    out["plain"] = {"status": r.status_code if r is not None else None,
                    "keys": sorted([k for k in (r.json() or {}).keys()])[:60] if r and r.status_code == 200 else None,
                    "body": (r.text[:1500] if r is not None else None) if (r is None or r.status_code != 200) else None}
    # 2) $expand=Master
    r = client._get(base, {"$expand": "Master"}, suppress_errors=True)
    out["expand_Master"] = {"status": r.status_code if r is not None else None,
                            "body": r.text[:1500] if r is not None else None}
    # 3) /Master nav
    r = client._get(base + "/Master", None, suppress_errors=True)
    out["nav_Master"] = {"status": r.status_code if r is not None else None,
                         "body": r.text[:1500] if r is not None else None}
    # 4) $select=Identity (Identity often holds master-style "Number, Name, Version")
    r = client._get(base, {"$select": "Identity,Number,Name"}, suppress_errors=True)
    out["select_Identity"] = {"status": r.status_code if r is not None else None,
                              "body": r.text[:1500] if r is not None else None}
    log.info("debug_part(%s): %s", part_id, out)
    return out


@router.get(
    "/_debug/detect_variants",
    summary="DEV: try multiple DetectDiscrepancies body permutations",
)
def debug_detect_variants(
    request: Request,
    source_oid: str,
    target_oid: str,
    source_path: str = "/",
    target_path: str = "/",
    _: None = Depends(require_auth),
):
    """Feuert serielle DetectDiscrepancies-Calls mit verschiedenen Body-Formen
    gegen den Live-Server und liefert pro Variante {status, body_snippet}.

    URL-Beispiel (im eingeloggten Browser-Tab in die Adressleiste):
        /api/_debug/detect_variants?source_oid=OR:wt.part.WTPart:396451183
            &target_oid=OR:wt.part.WTPart:396671366
            &source_path=/0:396451183-392173008-060c64e0-5635-4faf-b652-87faed00c444
    """
    import logging as _logging
    log = _logging.getLogger("debug_detect_variants")
    client = get_client(request)
    url = f"{client.base_url}/servlet/odata/v3/BomTransformation/DetectDiscrepancies"

    def _try(label: str, body: dict) -> dict:
        client._refresh_csrf()
        r = client._post(url, json_body=body, suppress_errors=True)
        snippet = r.text[:1200] if r is not None else None
        status = r.status_code if r is not None else None
        log.info("variant=%s status=%s body=%s", label, status, snippet)
        return {"status": status, "request": body, "response": snippet}

    src_parts = f"Parts('{source_oid}')"
    tgt_parts = f"Parts('{target_oid}')"

    variants: dict = {}

    variants["A_odata_id_root_path"] = _try("A", {"DiscrepancyContext": {
        "SourceRoot": {"@odata.id": src_parts},
        "TargetRoot": {"@odata.id": tgt_parts},
        "TargetPath": "/",
        "SourcePartSelection": [{"Path": "/"}],
        "UpstreamChangeOid": "",
    }})

    variants["B_odata_id_real_path"] = _try("B", {"DiscrepancyContext": {
        "SourceRoot": {"@odata.id": src_parts},
        "TargetRoot": {"@odata.id": tgt_parts},
        "TargetPath": target_path,
        "SourcePartSelection": [{"Path": source_path}],
        "UpstreamChangeOid": "",
    }})

    variants["C_id_field"] = _try("C", {"DiscrepancyContext": {
        "SourceRoot": {"ID": source_oid},
        "TargetRoot": {"ID": target_oid},
        "TargetPath": target_path,
        "SourcePartSelection": [{"Path": source_path}],
        "UpstreamChangeOid": "",
    }})

    variants["D_odata_bind_outside"] = _try("D", {"DiscrepancyContext": {
        "SourceRoot@odata.bind": src_parts,
        "TargetRoot@odata.bind": tgt_parts,
        "TargetPath": target_path,
        "SourcePartSelection": [{"Path": source_path}],
        "UpstreamChangeOid": "",
    }})

    variants["E_only_source_root"] = _try("E", {"DiscrepancyContext": {
        "SourceRoot": {"@odata.id": src_parts},
        "TargetPath": target_path,
        "SourcePartSelection": [{"Path": source_path}],
        "UpstreamChangeOid": "",
    }})

    variants["F_oid_only_string"] = _try("F", {"DiscrepancyContext": {
        "SourceRoot": {"@odata.id": source_oid},
        "TargetRoot": {"@odata.id": target_oid},
        "TargetPath": target_path,
        "SourcePartSelection": [{"Path": source_path}],
        "UpstreamChangeOid": "",
    }})

    return {"url": url, "variants": variants}


@router.post(
    "/_debug/detect_raw",
    summary="DEV: send a raw DetectDiscrepancies body and return Windchill's response",
)
def debug_detect_raw(
    body: dict,
    request: Request,
    _: None = Depends(require_auth),
):
    """Send an arbitrary body straight to BomTransformation/DetectDiscrepancies.

    Body shape: ``{"DiscrepancyContext": {...}}`` — passed through verbatim.
    Returns ``{status, body}`` so we can inspect 4xx/5xx error messages.
    """
    import logging as _logging
    log = _logging.getLogger("debug_detect_raw")
    client = get_client(request)
    url = f"{client.base_url}/servlet/odata/v3/BomTransformation/DetectDiscrepancies"
    client._refresh_csrf()
    log.info("debug_detect_raw payload: %s", body)
    resp = client._post(url, json_body=body, suppress_errors=True)
    return {
        "status": resp.status_code if resp is not None else None,
        "body": (resp.text if resp is not None else None),
    }


@router.post(
    "/parts/{code}/transformer/detect",
    response_model=TransformResponse,
    summary="Detect EBOM nodes without Manufacturing pendant (BomTransformation v3)",
)
def post_transformer_detect(
    code: str,
    body: TransformDetectRequest,
    request: Request,
    _: None = Depends(require_auth),
):
    """Wraps ``BomTransformation/DetectDiscrepancies``.

    Requires the v3/BomTransformation domain to be deployed (dev only on
    plm-dev; not on plm-prod). Returns 404 from Windchill if missing —
    the adapter raises ``WRSError(status=404)`` which surfaces as HTTP 404.
    """
    client = get_client(request)
    session = get_session(request)
    return bom_transformer_service.detect_discrepancies(
        client,
        target_path=body.targetPath,
        source_part_paths=body.sourcePartPaths or None,
        upstream_change_oid=body.upstreamChangeOid,
        source_root=body.sourceRoot,
        target_root=body.targetRoot,
        session=session,
    )


@router.post(
    "/parts/{code}/transformer/generate",
    response_model=TransformResponse,
    summary="Generate Manufacturing-side downstream structure (BomTransformation v3)",
)
def post_transformer_generate(
    code: str,
    body: TransformGenerateRequest,
    request: Request,
    _: None = Depends(require_auth),
):
    """Wraps ``BomTransformation/GenerateDownstreamStructure``.

    `body.sourcePartPaths` is the list of EBOM nodes the user marked as
    NEW. `body.changeOid` is optional — provide a Change Notice OID for
    released parts (Windchill standard process).
    """
    client = get_client(request)
    session = get_session(request)
    return bom_transformer_service.generate_downstream(
        client,
        target_path=body.targetPath,
        source_part_paths=body.sourcePartPaths,
        upstream_change_oid=body.upstreamChangeOid,
        change_oid=body.changeOid,
        session=session,
    )


@router.post(
    "/parts/{code}/transformer/copy",
    response_model=TransformResponse,
    summary="Per-node COPY (PasteSpecial) — paste EBOM nodes under MBOM target",
)
def post_transformer_copy(
    code: str,
    body: TransformCopyRequest,
    request: Request,
    _: None = Depends(require_auth),
):
    """Wraps ``BomTransformation/PasteSpecial`` — OData-Equivalent zum
    Drag&Drop in der Windchill-GUI. Kopiert die in ``sourcePartPaths``
    angegebenen EBOM-Knoten unter den ``targetPath`` MBOM-Knoten.
    """
    client = get_client(request)
    session = get_session(request)
    return bom_transformer_service.paste_special(
        client,
        target_path=body.targetPath,
        source_part_paths=body.sourcePartPaths,
        upstream_change_oid=body.upstreamChangeOid,
        change_oid=body.changeOid,
        session=session,
    )


@router.post(
    "/parts/{code}/transformer/remove",
    response_model=TransformRemoveResponse,
    summary="Per-node REMOVE — delete the listed MBOM UsageLinks",
)
def post_transformer_remove(
    code: str,  # noqa: ARG001 — accepted for URL symmetry; not used server-side
    body: TransformRemoveRequest,
    request: Request,
    _: None = Depends(require_auth),
):
    """Phase 2c: löscht die übergebenen ``WTPartUsageLink``-IDs auf der
    MBOM-Seite via ``PTC.ProdMgmt.UsageLinks('<id>')``. Die EBOM bleibt
    unverändert; nur die Parent→Child-Beziehung in der MBOM wird gekappt.
    """
    client = get_client(request)
    session = get_session(request)
    return bom_transformer_service.remove_usage_links(
        client,
        usage_link_ids=body.usageLinkIds,
        session=session,
    )


# ── Occurrences ──────────────────────────────────────────────


@router.get(
    "/parts/{code}/occurrences",
    response_model=OccurrencesResponse,
    summary="Alle Vorkommen eines Part-Codes",
)
def get_occurrences(
    code: str,
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return parts_service.get_part_occurrences(client, code)


# ── BOM Tree (lazy) ─────────────────────────────────────────


@router.get("/bom/root", summary="BOM Root Node")
def bom_root(
    request: Request,
    partNumber: str = Query(...),
    _: None = Depends(require_auth),
) -> dict:
    client = get_client(request)
    session = get_session(request)
    node = parts_service.get_bom_root(client, partNumber, session=session)
    return {"root": node}


@router.get(
    "/bom/children",
    response_model=BomNodeResponse,
    summary="BOM-Kinder laden (ein Level)",
)
def bom_children(
    request: Request,
    partId: str = Query(...),
    _: None = Depends(require_auth),
):
    client = get_client(request)
    session = get_session(request)
    t0 = time.perf_counter()
    result = parts_service.get_bom_children(client, partId, session=session)
    duration_ms = int((time.perf_counter() - t0) * 1000)
    if session:
        log_session_event(
            session, "GET", f"/api/bom/children?partId={partId}",
            200, duration_ms, "web",
            f"children={len(result.children)} docs={len(result.documents)} cad={len(result.cadDocuments)}",
        )
    return result


@router.get(
    "/bom/views",
    response_model=list[BomViewConfig],
    summary="Verfuegbare BOM-Ansichten (Spalten-Konfigurationen)",
)
def bom_views() -> list[BomViewConfig]:
    """Return the list of available BOM view configurations.

    Each view defines which columns to display in the BOM table.
    No authentication required — view configs are static metadata.
    """
    return BOM_VIEWS


# ── Windchill Containers ─────────────────────────────────────


@router.get(
    "/containers",
    response_model=ContainerListResponse,
    summary="Windchill Container (Products / Libraries)",
)
def list_containers(
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return parts_service.get_containers(client)


# ── Part Subtypes (Soft Types) ───────────────────────────────


@router.get(
    "/part-subtypes",
    response_model=PartSubtypeListResponse,
    summary="Verfuegbare Part-Subtypes (Soft Types) aus OData Metadata",
)
def list_part_subtypes(
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return parts_service.get_part_subtypes(client)


# ── Classification Nodes ─────────────────────────────────────


@router.get(
    "/classification-nodes",
    response_model=ClassificationNodeListResponse,
    summary="Classification-Knoten aus Windchill ClfStructure",
)
def list_classification_nodes(
    request: Request,
    _: None = Depends(require_auth),
):
    client = get_client(request)
    return parts_service.get_classification_nodes(client)
