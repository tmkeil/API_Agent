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
    context: Optional[str] = None,
    session: Optional[UserSession] = None,
) -> list[PartSearchResult]:
    """Search with wildcard support, ranking, and session-level caching.

    Args:
        entity_types: Optional list of type keys to search.
                      None → all types. E.g. ["part","document","cad_document"]
        context: Optional Windchill ContainerName to filter results.
    """
    # Check session cache first
    types_key = ",".join(sorted(entity_types)) if entity_types else "all"
    ctx_key = (context or "").strip().lower()
    cache_key = f"{query.lower()}|{limit}|{types_key}|{ctx_key}"
    if session:
        with session.lock:
            cached = session.search_cache.get(cache_key)
        if cached is not None:
            log_session_event(session, "CACHE", f"search:{query}", 200, 0, "cache", "search hit")
            return cached

    # Use multi-entity search
    raw_items = client.search_entities(
        query, entity_types=entity_types, context=context, limit=limit * 2,
    )

    # Also do the legacy ProdMgmt/Parts search with wildcard filtering
    # if "part" is in the requested types (or all types)
    if entity_types is None or "part" in entity_types:
        url = f"{client.odata_base}/ProdMgmt/Parts"
        wildcard = "*" in query or "?" in query
        regex = _wildcard_to_regex(query)
        core = query.replace("*", "").replace("?", "").strip()
        safe = core.replace("'", "''")

        # Additional filters for wildcard patterns
        extra_collected: dict[str, dict] = {}
        seen_from_multi = {extract_id(item) for item in raw_items}

        if wildcard and core:
            extra_filters = [
                {"$filter": f"contains(Number,'{safe}')", "$top": "200"},
                {"$filter": f"contains(Name,'{safe}')", "$top": "200"},
            ]
            for params in extra_filters:
                try:
                    items = client.get_all_pages(url, params)
                    for item in items:
                        pid = extract_id(item)
                        if pid and pid not in seen_from_multi and pid not in extra_collected:
                            item["_entity_type"] = WcType.PART
                            item["_entity_type_key"] = "part"
                            extra_collected[pid] = item
                except Exception:
                    logger.debug("Wildcard filter failed: %s", params, exc_info=True)
                    continue

            # Filter by wildcard regex
            for pid, item in extra_collected.items():
                number = str(item.get("Number") or "")
                name = str(item.get("Name") or "")
                if regex.search(number) or regex.search(name):
                    raw_items.append(item)

    # Map to PartSearchResult
    matches = []
    seen_ids: set[str] = set()
    for item in raw_items:
        n = normalize_item(item)
        if not n["id"] or n["id"] in seen_ids:
            continue
        seen_ids.add(n["id"])

        obj_type = n.get("_entity_type", WcType.PART)

        matches.append(
            PartSearchResult(
                partId=n["id"],
                objectType=obj_type,
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
    result = matches[:limit]

    # Store in session cache
    if session:
        with session.lock:
            session.search_cache[cache_key] = result

    return result


def get_object_detail(
    client: WRSClient, type_key: str, code: str
) -> ObjectDetailResponse:
    """Generische Detail-Abfrage fuer jeden Windchill-Objekttyp."""
    t0 = time.monotonic()

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

    ms = round((time.monotonic() - t0) * 1000, 1)
    return ObjectDetailResponse(
        detail=detail,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def get_contexts(client: WRSClient) -> list[str]:
    """Get available Windchill container names for context filtering.

    Queries ProdMgmt/Parts for a small sample and extracts unique ContainerName values.
    """
    url = f"{client.odata_base}/ProdMgmt/Parts"
    # Fetch a decent sample to discover containers
    items = client.get_all_pages(url, {"$select": "ContainerName", "$top": "500"}) or []
    containers: set[str] = set()
    for item in items:
        cn = item.get("ContainerName") or item.get("Context")
        if cn:
            containers.add(str(cn))
    return sorted(containers)
