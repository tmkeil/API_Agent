"""
Business logic: WTPart-spezifische Operationen.

Part-Detail, BOM-Baum, Dokumente, CAD, Where-Used, Occurrences.
Typ-uebergreifende Suche → search_service.py
Administrative Funktionen (Export, Benchmark) → routers/admin.py

All functions accept a WRSClient instance — either the service-account
singleton or a per-session client from the frontend.
Session-level caching is used when a UserSession is provided.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from src.adapters.wrs_client import WRSClient
from src.core.cache import cache
from src.core.config import settings
from src.core.odata import WcType, extract_id, normalize_item, normalize_state
from src.core.session import UserSession, log_session_event
from src.models.dto import (
    BomNodeResponse,
    BomTreeNode,
    CacheStats,
    DocumentListResponse,
    DocumentNode,
    OccurrencesResponse,
    PartDetail,
    PartDetailResponse,
    PartOccurrence,
    TimingInfo,
    WhereUsedEntry,
    WhereUsedResponse,
)

logger = logging.getLogger(__name__)

# Module-level thread pool — reused across all get_bom_children calls
_bom_executor = ThreadPoolExecutor(max_workers=16, thread_name_prefix="bom")


# ── Internal mappers ─────────────────────────────────────────


def _map_part(raw: dict) -> PartDetail:
    n = normalize_item(raw)
    return PartDetail(
        partId=n["id"],
        number=n["number"],
        name=n["name"],
        version=n["version"],
        iteration=n["iteration"],
        state=n["state"],
        identity=n["identity"],
    )


def _has_children(raw: dict) -> bool:
    """Heuristik: Hat dieses Part Kinder in der Stueckliste?

    Windchill liefert je nach OData-Version und $expand
    unterschiedliche Hinweise. Wir pruefen mehrere Indikatoren.
    Im Zweifel geben wir True zurueck — die UI laedt dann
    einfach eine leere Children-Liste.
    """
    for key in ("UsesPartList", "PartListMember", "Uses", "UsesInterface",
                "BOMComponents", "PartStructure"):
        val = raw.get(key)
        if val is not None:
            if isinstance(val, list) and len(val) > 0:
                return True
            if isinstance(val, str) and val:
                return True
    # odata.navigationLink Hinweis
    for key in raw:
        if key.endswith("@odata.navigationLink") and "Uses" in key:
            return True
    # Fallback: Immer True — die UI laedt dann leere Kinder und
    # klappt den Pfeil weg falls keine Ergebnisse kommen
    return True


def _flatten_value(val: object) -> object:
    """Flatten OData values for BOM column display.

    - dict with Value/Display → Display or Value
    - list → join first values with ', '
    - None → skip
    - scalar → as-is
    """
    if val is None:
        return None
    if isinstance(val, dict):
        return str(val.get("Display") or val.get("Value") or val)
    if isinstance(val, list):
        if len(val) == 0:
            return None
        parts = []
        for item in val:
            if isinstance(item, dict):
                parts.append(str(item.get("Value") or item.get("Display") or item))
            else:
                parts.append(str(item))
        return ", ".join(parts)
    return val


def _map_tree_node(
    raw: dict, usage_link: Optional[dict] = None
) -> BomTreeNode:
    n = normalize_item(raw)
    node = BomTreeNode(
        partId=n["id"],
        type=raw.get("ObjectType") or WcType.PART,
        number=n["number"],
        name=n["name"],
        version=n["version"],
        iteration=n["iteration"],
        state=n["state"],
        identity=n["identity"],
        hasChildren=_has_children(raw),
        organizationId=n.get("organization_id", ""),
    )

    # ── Capture ALL part-level attributes (for BOM view columns) ──
    # Skip fields already extracted into named BomTreeNode fields
    # (includes ALL aliases from odata._FIELD_ALIASES to prevent duplicates)
    _SKIP_PART_KEYS = {
        "ID", "id",
        "Number", "PartNumber",
        "Name", "DisplayName",
        "Version", "VersionID",
        "Iteration", "IterationID",
        "State", "LifeCycleState",
        "Identity", "DisplayIdentity",
        "OrganizationName",
    }
    part_attrs: dict[str, object] = {}
    for k, v in raw.items():
        if k.startswith("@") or k.startswith("odata"):
            continue
        if k in _SKIP_PART_KEYS:
            continue
        flat = _flatten_value(v)
        if flat is None:
            continue
        part_attrs[k] = flat
    node.partAttributes = part_attrs

    if usage_link:
        qty = usage_link.get("Quantity", 1)
        unit = ""
        if isinstance(qty, dict):
            unit = str(qty.get("Unit") or "")
            qty = qty.get("Value", 1)
        if not unit:
            raw_unit = (
                usage_link.get("Unit")
                or usage_link.get("QuantityUnit")
                or ""
            )
            if isinstance(raw_unit, dict):
                raw_unit = raw_unit.get("Value") or ""
            unit = str(raw_unit)

        node.quantity = qty
        node.quantityUnit = unit
        node.lineNumber = str(
            usage_link.get("LineNumber")
            or usage_link.get("FindNumber")
            or ""
        )

        # Capture ALL remaining usage-link attributes
        # (for BOM view column support and AI Agent access)
        _SKIP_LINK_KEYS = {
            "Quantity", "Unit", "QuantityUnit", "LineNumber", "FindNumber",
            "Uses", "RoleBObject", "Child", "Part", "ID",
            "UsesInterface", "BOMComponents", "PartStructure",
        }
        extra: dict[str, object] = {}
        for k, v in usage_link.items():
            if k.startswith("@") or k.startswith("odata"):
                continue
            if k in _SKIP_LINK_KEYS:
                continue
            flat = _flatten_value(v)
            if flat is None:
                continue
            extra[k] = flat
        node.usageLinkAttributes = extra

    return node


def _map_document(
    raw: dict, doc_type: str = WcType.DOCUMENT
) -> DocumentNode:
    n = normalize_item(raw)
    return DocumentNode(
        docId=n["id"],
        type=doc_type,
        number=n["number"],
        name=n["name"],
        version=n["version"],
        state=n["state"],
    )



# ── Service Functions ────────────────────────────────────────


def get_part_documents(
    client: WRSClient, code: str
) -> DocumentListResponse:
    """Get WTDocuments linked to a part."""
    t0 = time.monotonic()
    raw = client.find_part(code)
    part_id = extract_id(raw)
    part_number = str(raw.get("Number") or code)
    raw_docs = client.get_described_documents(part_id, part_number)
    docs = [_map_document(d, WcType.DOCUMENT) for d in raw_docs]
    ms = round((time.monotonic() - t0) * 1000, 1)
    return DocumentListResponse(
        code=code,
        totalFound=len(docs),
        documents=docs,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def get_part_cad_documents(
    client: WRSClient, code: str
) -> DocumentListResponse:
    """Get CAD/EPM documents linked to a part."""
    t0 = time.monotonic()
    raw = client.find_part(code)
    part_id = extract_id(raw)
    raw_cads = client.get_cad_documents(part_id)
    cads = [_map_document(c, WcType.EPM_DOCUMENT) for c in raw_cads]
    ms = round((time.monotonic() - t0) * 1000, 1)
    return DocumentListResponse(
        code=code,
        totalFound=len(cads),
        documents=cads,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def get_part_where_used(
    client: WRSClient, code: str
) -> WhereUsedResponse:
    """Get where-used (parent assemblies) for a part."""
    t0 = time.monotonic()
    raw = client.find_part(code)
    part_id = extract_id(raw)
    raw_parents = client.get_where_used(part_id)
    entries = []
    for p in raw_parents:
        n = normalize_item(p)
        qty = p.get("Quantity")
        unit_str = str(p.get("Unit") or p.get("QuantityUnit") or "") or None
        if isinstance(qty, dict):
            unit_str = str(qty.get("Unit") or unit_str or "")
            qty = qty.get("Value", qty)
        entries.append(WhereUsedEntry(
            oid=n["id"],
            number=n["number"],
            name=n["name"],
            revision=n["version"],
            state=n["state"],
            quantity=qty,
            unit=unit_str or None,
        ))
    ms = round((time.monotonic() - t0) * 1000, 1)
    return WhereUsedResponse(
        code=code,
        totalFound=len(entries),
        usedIn=entries,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def get_part_detail(
    client: WRSClient, code: str
) -> PartDetailResponse:
    t0 = time.monotonic()

    cache_key = f"detail:{code}"
    cached = cache.get(cache_key)
    if cached is not None:
        return PartDetailResponse(
            part=cached,
            timing=TimingInfo(
                totalMs=0, wrsMs=0, cacheHits=1, fromCache=True
            ),
        )

    raw = client.find_part(code)
    part = _map_part(raw)
    cache.set(cache_key, part, ttl=settings.CACHE_TTL_SECONDS)

    ms = round((time.monotonic() - t0) * 1000, 1)
    return PartDetailResponse(
        part=part,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def get_part_occurrences(
    client: WRSClient, code: str
) -> OccurrencesResponse:
    t0 = time.monotonic()

    raw = client.search_parts(code, limit=500)
    occurrences = []
    for item in raw:
        p = _map_part(item)
        occurrences.append(
            PartOccurrence(
                partId=p.partId,
                number=p.number,
                name=p.name,
                version=p.version,
                state=p.state,
                pathHint=p.number,
            )
        )

    ms = round((time.monotonic() - t0) * 1000, 1)
    return OccurrencesResponse(
        code=code,
        totalFound=len(occurrences),
        occurrences=occurrences,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def get_bom_root(
    client: WRSClient,
    part_number: str,
    session: Optional[UserSession] = None,
) -> BomTreeNode:
    """Load root node for lazy BOM tree, with session cache."""
    if session:
        key = part_number.strip().upper()
        with session.lock:
            cached_part = session.part_by_number.get(key)
        if cached_part:
            log_session_event(session, "CACHE", f"part:number:{part_number}", 200, 0, "cache", "part hit")
            return _map_tree_node(cached_part)

    raw = client.find_part(part_number)

    if session:
        pid = extract_id(raw).strip()
        num = str(raw.get("Number") or "").strip().upper()
        with session.lock:
            if pid:
                session.part_by_id[pid] = raw
            if num:
                session.part_by_number[num] = raw

    return _map_tree_node(raw)


def get_bom_children(
    client: WRSClient,
    part_id: str,
    session: Optional[UserSession] = None,
) -> BomNodeResponse:
    """Load one level of BOM children + documents for a part.
    Uses session-level caching and parallel loading like the prototype."""
    t0 = time.monotonic()
    _SENTINEL = object()

    # ── Check session caches ─────────────────────────────────
    links = None
    children_cached = False
    docs_cached = False
    cad_cached = False

    if session:
        with session.lock:
            cached_links = session.bom_children_by_part.get(part_id)
        if cached_links is not None:
            links = cached_links
            children_cached = True
            log_session_event(session, "CACHE", f"bom:children:{part_id}", 200, 0, "cache", "children hit")

    # Fetch links from Windchill if not cached
    if links is None:
        links = client.get_bom_children(part_id)
        if session:
            with session.lock:
                session.bom_children_by_part[part_id] = links

    # Get part info for document queries (use session cache first)
    part = None
    if session:
        with session.lock:
            part = session.part_by_id.get(part_id)
    if not part:
        part = client.get_part_by_id(part_id)
    part_number = ""
    if part:
        part_number = str(part.get("Number") or part.get("PartNumber") or "")
        if session:
            with session.lock:
                session.part_by_id[part_id] = part

    # ── Check doc/cad caches ─────────────────────────────────
    documents_raw = None
    cad_raw = None

    if session:
        with session.lock:
            d = session.documents_by_part.get(part_id, _SENTINEL)
        if d is not _SENTINEL:
            documents_raw = d
            docs_cached = True
            log_session_event(session, "CACHE", f"bom:documents:{part_id}", 200, 0, "cache", "documents hit")

        with session.lock:
            c = session.cad_documents_by_part.get(part_id, _SENTINEL)
        if c is not _SENTINEL:
            cad_raw = c
            cad_cached = True
            log_session_event(session, "CACHE", f"bom:cad:{part_id}", 200, 0, "cache", "cad hit")

    # ── Parallel loading ─────────────────────────────────────
    def _resolve_child(link):
        child = client.resolve_usage_link_child(link)
        if not child:
            return None
        if session:
            cid = extract_id(child).strip()
            if cid:
                with session.lock:
                    session.part_by_id[cid] = child
        return _map_tree_node(child, usage_link=link)

    def _load_documents():
        docs = client.get_described_documents(part_id, part_number)
        if session:
            with session.lock:
                session.documents_by_part[part_id] = docs
        return docs

    def _load_cad():
        cads = client.get_cad_documents(part_id)
        if session:
            with session.lock:
                session.cad_documents_by_part[part_id] = cads
        return cads

    # ── Parallel loading (reuses module-level thread pool) ──
    child_futures = [_bom_executor.submit(_resolve_child, link) for link in links]

    docs_future = None
    cad_future = None
    if documents_raw is None:
        docs_future = _bom_executor.submit(_load_documents)
    if cad_raw is None:
        cad_future = _bom_executor.submit(_load_cad)

    children: list[BomTreeNode] = []
    for f in child_futures:
        node = f.result()
        if node is not None:
            children.append(node)

    if docs_future:
        documents_raw = docs_future.result()
    if cad_future:
        cad_raw = cad_future.result()

    children.sort(key=lambda n: (n.lineNumber or "", n.number or ""))

    documents = [_map_document(d, WcType.DOCUMENT) for d in (documents_raw or [])]
    cad_documents = [_map_document(d, WcType.CAD_DOCUMENT) for d in (cad_raw or [])]

    ms = round((time.monotonic() - t0) * 1000, 1)
    return BomNodeResponse(
        children=children,
        documents=documents,
        cadDocuments=cad_documents,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def get_cache_stats() -> CacheStats:
    return CacheStats(
        entries=cache.size,
        ttl_seconds=settings.CACHE_TTL_SECONDS,
        max_size=settings.CACHE_MAX_SIZE,
    )
