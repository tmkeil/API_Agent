"""
Business logic: typ-uebergreifende Suche und generische Objektdetails.

Ausgelagert aus parts_service.py — hier liegt alles, was nicht
an einen einzelnen Windchill-Typ (WTPart etc.) gebunden ist.
"""

import logging
import re
import time
from typing import Optional

from src.adapters.wrs_client import WRSClient
from src.core.odata import WcType, extract_id, match_score, normalize_item
from src.core.session import UserSession, log_session_event
from src.models.dto import (
    ObjectDetail,
    ObjectDetailResponse,
    PartSearchResult,
    TimingInfo,
)

logger = logging.getLogger(__name__)


# ── Internal helpers ─────────────────────────────────────────


def _wildcard_to_regex(pattern: str) -> re.Pattern:
    escaped = re.escape(pattern)
    escaped = escaped.replace(r"\*", ".*").replace(r"\?", ".")
    return re.compile(f"^{escaped}$", re.IGNORECASE)


# ── Service Functions ────────────────────────────────────────


def search_parts(
    client: WRSClient,
    query: str,
    limit: int = 200,
    entity_types: list[str] | None = None,
    session: Optional[UserSession] = None,
    mode: str = "auto",
) -> list[PartSearchResult]:
    """Search with wildcard support, ranking, and session-level caching.

    Args:
        entity_types: Optional list of type keys to search.
                      None → all types. E.g. ["part","document","cad_document"]
        mode: 'number' = Number only (fast), 'keyword' = Number+Name, 'auto' = detect.
    """
    # Check session cache first
    types_key = ",".join(sorted(entity_types)) if entity_types else "all"
    cache_key = f"{query.lower()}|{limit}|{types_key}|{mode}"
    if session:
        with session.lock:
            cached = session.search_cache.get(cache_key)
        if cached is not None:
            log_session_event(session, "CACHE", f"search:{query}", 200, 0, "cache", "search hit")
            return cached

    # Use multi-entity search (parallel, single query per type)
    raw_items = client.search_entities(
        query, entity_types=entity_types, contexts=None, limit=limit, mode=mode,
    )

    # Wildcard-Support: zusaetzliche clientseitige Regex-Filterung
    if entity_types is None or "part" in entity_types:
        wildcard = "*" in query or "?" in query
        regex = _wildcard_to_regex(query) if wildcard else None

        if wildcard and regex:
            # Filter bestehendes Ergebnis nach Wildcard-Regex
            raw_items = [
                item for item in raw_items
                if regex.search(str(item.get("Number") or ""))
                or regex.search(str(item.get("Name") or ""))
            ]

    # Map to PartSearchResult
    matches = []
    seen_ids: set[str] = set()
    for item in raw_items:
        n = normalize_item(item)
        if not n["id"] or n["id"] in seen_ids:
            continue
        seen_ids.add(n["id"])

        obj_type = n.get("_entity_type", WcType.PART)
        sub_type = str(item.get("ObjectType") or "")

        matches.append(
            PartSearchResult(
                partId=n["id"],
                objectType=obj_type,
                subType=sub_type,
                number=n["number"],
                name=n["name"],
                version=n["version"],
                iteration=n["iteration"],
                state=n["state"],
                identity=n["identity"],
                context=n["context"],
                lastModified=n["last_modified"],
                createdOn=n["created_on"],
                isVariant=n.get("is_variant", ""),
                organizationId=n.get("organization_id", ""),
                classification=n.get("classification", ""),
            )
        )

        # Cache the part in session (only WTParts)
        if session and obj_type == WcType.PART:
            num = n["number"].strip().upper()
            with session.lock:
                if n["id"]:
                    session.part_by_id[n["id"]] = item
                if num:
                    session.part_by_number[num] = item

    matches.sort(key=lambda m: match_score(query, m.number, m.name))
    result = matches[:limit] if limit > 0 else matches

    # Store in session cache
    if session:
        with session.lock:
            session.search_cache[cache_key] = result

    return result


def get_object_detail(
    client: WRSClient, type_key: str, code: str
) -> ObjectDetailResponse:
    """Generische Detail-Abfrage fuer jeden Windchill-Objekttyp."""
    from src.services.parts_service import _flatten_value
    t0 = time.monotonic()

    raw = client.find_object(type_key, code)
    n = normalize_item(raw)

    # Capture all raw attributes (flattened for display)
    _SKIP_KEYS = {"ID", "id", "Number", "Name", "Version", "Iteration",
                  "State", "Identity", "OrganizationName", "VersionID"}
    all_attrs: dict[str, object] = {}
    for k, v in raw.items():
        if k.startswith("@") or k.startswith("odata") or k.startswith("_"):
            continue
        if k in _SKIP_KEYS:
            continue
        flat = _flatten_value(v)
        if flat is None:
            continue
        all_attrs[k] = flat

    detail = ObjectDetail(
        objectId=n["id"],
        objectType=n.get("_entity_type", ""),
        subType=str(raw.get("ObjectType") or ""),
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
        allAttributes=all_attrs,
    )

    ms = round((time.monotonic() - t0) * 1000, 1)
    return ObjectDetailResponse(
        detail=detail,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def advanced_search(
    client: WRSClient,
    query: str = "",
    types: list[str] | None = None,
    contexts: list[str] | None = None,
    state: str = "",
    date_from: str = "",
    date_to: str = "",
    date_field: str = "modified",
    attributes: dict[str, str] | None = None,
    limit: int = 200,
) -> list[PartSearchResult]:
    """Erweiterte Suche mit strukturierten Filtern.

    Delegiert an search_mixin.advanced_search und normalisiert
    die Ergebnisse zu PartSearchResult-DTOs.
    """
    from src.core.odata import WcType

    raw_items = client.advanced_search(
        query=query,
        entity_types=types if types else None,
        contexts=contexts or None,
        state=state or None,
        date_from=date_from or None,
        date_to=date_to or None,
        date_field=date_field or "modified",
        attributes=attributes or None,
        limit=limit,
    )

    results: list[PartSearchResult] = []
    for item in raw_items:
        n = normalize_item(item)
        if not n["id"]:
            continue
        obj_type = n.get("_entity_type", WcType.PART)
        sub_type = str(item.get("ObjectType") or "")
        results.append(
            PartSearchResult(
                partId=n["id"],
                objectType=obj_type,
                subType=sub_type,
                number=n["number"],
                name=n["name"],
                version=n["version"],
                iteration=n["iteration"],
                state=n["state"],
                identity=n["identity"],
                context=n["context"],
                lastModified=n["last_modified"],
                createdOn=n["created_on"],
                isVariant=n.get("is_variant", ""),
                organizationId=n.get("organization_id", ""),
                classification=n.get("classification", ""),
            )
        )
    return results[:limit]


def get_contexts(client: WRSClient) -> list[str]:
    """Get available Windchill Kontexte aus FolderLocation.

    FolderLocation enthaelt Pfade wie '/P - Design/Article'.
    Der erste Pfad-Abschnitt (z.B. 'P - Design') ist der Kontext.

    Holt nur EINE Seite (max_pages=1) — 500 Records genuegen,
    um die gaengigen Kontexte abzudecken.
    """
    url = f"{client._odata_url('ProdMgmt')}/Parts"
    contexts: set[str] = set()

    # NUR 1 Seite holen — kein Paging durch die ganze DB!
    items = client.get_all_pages(
        url, {"$select": "FolderLocation", "$top": "500"},
        max_pages=1,
        return_none_on_error=True,
    )

    # Fallback ohne $select
    if items is None:
        logger.info("get_contexts: $select=FolderLocation failed, fetching full records")
        items = client.get_all_pages(
            url, {"$top": "100"},
            max_pages=1,
            return_none_on_error=True,
        ) or []

    for item in (items or []):
        folder = item.get("FolderLocation") or ""
        if isinstance(folder, str) and folder.startswith("/"):
            # '/P - Design/Article' → 'P - Design'
            parts = folder.strip("/").split("/")
            if parts and parts[0]:
                contexts.add(parts[0])

    return sorted(contexts)
