"""
WRS Client — Multi-Entity-Suche (Mixin).
=========================================

Suche ueber beliebige Windchill-Objekttypen (Parts, Dokumente, CAD, Change, …).
Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from src.core.odata import extract_id

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)

# Windchill ignoriert $top und liefert immer 25 Items pro Seite (fest).
_WC_PAGE_SIZE = 25
# Standard-Seitenlimit pro Entity-Typ bei der Suche.
# 40 Seiten × 25 = 1000 Items pro Typ.
# Dank parallelem Paging (alle Seiten gleichzeitig) dauert das nur
# so lang wie ein einzelner Request (~3s Parts, ~10s Documents).
_DEFAULT_SEARCH_MAX_PAGES = 40


class SearchMixin:
    """Multi-Entity-Suche (Mixin fuer WRSClientBase)."""

    # Mapping: type_key → (OData service, entity set, Windchill type label)
    SEARCHABLE_ENTITIES: dict[str, tuple[str, str, str]] = {
        "part":            ("ProdMgmt",          "Parts",           "WTPart"),
        "document":        ("DocMgmt",           "Documents",       "WTDocument"),
        "cad_document":    ("CADDocumentMgmt",   "CADDocuments",    "EPMDocument"),
        "change_notice":   ("ChangeMgmt",        "ChangeNotices",   "WTChangeOrder2"),
        "change_request":  ("ChangeMgmt",        "ChangeRequests",  "WTChangeRequest2"),
        "problem_report":  ("ChangeMgmt",        "ProblemReports",  "WTChangeIssue"),
    }

    def find_object(self: "WRSClientBase", type_key: str, number: str) -> dict:
        """Ein Windchill-Objekt beliebigen Typs anhand seiner Nummer finden.

        Args:
            type_key: Schluessel aus SEARCHABLE_ENTITIES (z.B. 'part', 'document').
            number:   Objektnummer (z.B. '2200500023').

        Returns:
            OData-Dict des Objekts, ergaenzt um '_entity_type' und '_entity_type_key'.

        Raises:
            WRSError 404 wenn nicht gefunden, 400 wenn Typ unbekannt.
        """
        from src.adapters.base import WRSError

        if type_key not in self.SEARCHABLE_ENTITIES:
            raise WRSError(f"Unbekannter Objekttyp: '{type_key}'", status_code=400)

        service, entity_set, wc_type = self.SEARCHABLE_ENTITIES[type_key]
        url = f"{self.odata_base}/{service}/{entity_set}"
        safe = number.replace("'", "''")

        filters = [
            f"Number eq '{safe}'",
            f"contains(Number,'{safe}')",
        ]

        for filt in filters:
            resp = self._get(url, {"$filter": filt}, suppress_errors=True)
            if resp and resp.status_code == 200:
                items = resp.json().get("value", [])
                if items:
                    items.sort(
                        key=lambda p: (p.get("Version", ""), p.get("Iteration", "")),
                        reverse=True,
                    )
                    result = items[0]
                    result["_entity_type"] = wc_type
                    result["_entity_type_key"] = type_key
                    return result

        raise WRSError(
            f"{wc_type} '{number}' nicht in Windchill gefunden", status_code=404
        )

    def search_entities(
        self: "WRSClientBase",
        query: str,
        entity_types: list[str] | None = None,
        contexts: list[str] | None = None,
        limit: int = 0,
    ) -> list[dict]:
        """Suche ueber mehrere Windchill-Entity-Typen gleichzeitig.

        Strategie: Ein einzelner OData-Filter pro Typ
        (Number/Name mit OR), parallel ueber ThreadPoolExecutor.
        Windchill's eigenes serverseitiges Limit greift automatisch.

        Kontext-Filter (P - Design etc.) erfolgt clientseitig anhand
        von FolderLocation, da dieses Feld nicht OData-filterbar ist.

        Args:
            query:        Suchbegriff (Nummer oder Name, mit Wildcard * oder ?).
            entity_types: Liste von Typ-Keys (z.B. ["part","document"]).
                          None → alle Typen durchsuchen.
            contexts:     Optional Liste von Kontexten (z.B. ['P - Design']).
                          Filter erfolgt clientseitig ueber FolderLocation.
            limit:        Max. Gesamtergebnisse (0 = kein clientseitiges Limit).

        Returns:
            Liste von OData-Dicts, ergaenzt um '_entity_type' (z.B. 'WTPart').
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        if entity_types is None:
            targets = list(self.SEARCHABLE_ENTITIES.items())
        else:
            targets = [
                (k, v) for k, v in self.SEARCHABLE_ENTITIES.items()
                if k in entity_types
            ]

        safe = query.replace("'", "''")

        # OData-Filter: nur Number/Name (FolderLocation ist NICHT filterbar)
        combined_filter = (
            f"(Number eq '{safe}' or contains(Number,'{safe}') "
            f"or contains(Name,'{safe}'))"
        )

        def _search_one_type(type_key: str, service: str, entity_set: str, wc_type: str) -> list[dict]:
            url = f"{self.odata_base}/{service}/{entity_set}"
            params: dict[str, str] = {"$filter": combined_filter}

            # Seitenlimit berechnen
            if limit > 0:
                pages = max(_DEFAULT_SEARCH_MAX_PAGES, (limit // _WC_PAGE_SIZE) + 2)
            else:
                pages = _DEFAULT_SEARCH_MAX_PAGES

            try:
                items = self._get_all_pages_parallel(
                    url, params, max_pages=pages,
                    return_none_on_error=True,
                )
                if items is None:
                    return []
                for item in items:
                    item["_entity_type"] = wc_type
                    item["_entity_type_key"] = type_key
                if items:
                    logger.debug(
                        "search_entities %s/%s fields: %s",
                        service, entity_set, list(items[0].keys()),
                    )
                return items
            except Exception:
                logger.debug("search_entities failed for %s/%s", service, entity_set, exc_info=True)
                return []

        # Parallele Abfrage aller Entity-Typen
        collected: list[dict] = []
        seen_ids: set[str] = set()

        with ThreadPoolExecutor(max_workers=len(targets)) as pool:
            futures = {
                pool.submit(_search_one_type, tk, svc, es, wct): tk
                for tk, (svc, es, wct) in targets
            }
            for future in as_completed(futures):
                for item in future.result():
                    pid = extract_id(item)
                    if pid and pid not in seen_ids:
                        seen_ids.add(pid)
                        collected.append(item)

        # Clientseitiger Kontext-Filter (FolderLocation)
        if contexts:
            prefixes = [f"/{ctx}/" for ctx in contexts]
            collected = [
                item for item in collected
                if any(
                    (item.get("FolderLocation") or "").startswith(p)
                    for p in prefixes
                )
            ]

        return collected[:limit] if limit > 0 else collected

    def advanced_search(
        self: "WRSClientBase",
        query: str = "",
        entity_types: list[str] | None = None,
        contexts: list[str] | None = None,
        state: str | None = None,
        description: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        attributes: dict[str, str] | None = None,
        limit: int = 200,
    ) -> list[dict]:
        """Erweiterte Suche mit strukturierten OData-Filtern.

        Args:
            query:        Nummer oder Name (optional, kann leer sein).
            entity_types: Typ-Keys (None → alle).
            contexts:     Liste von Kontexten (clientseitiger Filter via FolderLocation).
            state:        Lifecycle-State filter (z.B. 'INWORK', 'RELEASED').
            description:  Beschreibungs-Substring filter.
            date_from:    ISO-Datum (>= ModifyStamp).
            date_to:      ISO-Datum (<= ModifyStamp).
            attributes:   Zusaetzliche Name=Value-Filter auf OData-Felder.
            limit:        Max. Gesamtergebnisse.
        """
        if entity_types is None or len(entity_types) == 0:
            targets = list(self.SEARCHABLE_ENTITIES.items())
        else:
            targets = [
                (k, v) for k, v in self.SEARCHABLE_ENTITIES.items()
                if k in entity_types
            ]

        # ── Build shared filter clauses ──────────────────────
        clauses: list[str] = []

        if query:
            safe_q = query.replace("'", "''")
            clauses.append(
                f"(contains(Number,'{safe_q}') or contains(Name,'{safe_q}'))"
            )

        # FolderLocation ist NICHT OData-filterbar → kein OData-Clause

        if state:
            safe_st = state.strip().replace("'", "''")
            clauses.append(f"State eq '{safe_st}'")

        if description:
            safe_desc = description.replace("'", "''")
            clauses.append(f"contains(Description,'{safe_desc}')")

        if date_from:
            clauses.append(f"ModifyStamp ge {date_from}T00:00:00Z")

        if date_to:
            clauses.append(f"ModifyStamp le {date_to}T23:59:59Z")

        if attributes:
            for attr_name, attr_val in attributes.items():
                safe_name = attr_name.replace("'", "''")
                safe_val = attr_val.replace("'", "''")
                clauses.append(f"{safe_name} eq '{safe_val}'")

        filter_str = " and ".join(clauses) if clauses else ""

        collected: list[dict] = []
        seen_ids: set[str] = set()

        for type_key, (service, entity_set, wc_type) in targets:
            url = f"{self.odata_base}/{service}/{entity_set}"

            # Seitenlimit: genuegend Seiten um 'limit' Items zu finden
            pages = max(_DEFAULT_SEARCH_MAX_PAGES, (limit // _WC_PAGE_SIZE) + 2)

            params: dict[str, str] = {}
            if filter_str:
                params["$filter"] = filter_str

            try:
                items = self._get_all_pages_parallel(
                    url, params, max_pages=pages,
                    return_none_on_error=True,
                )
                if items is None:
                    continue
                for item in items:
                    pid = extract_id(item)
                    if pid and pid not in seen_ids:
                        seen_ids.add(pid)
                        item["_entity_type"] = wc_type
                        item["_entity_type_key"] = type_key
                        collected.append(item)
            except Exception:
                logger.debug(
                    "advanced_search failed for %s/%s",
                    service, entity_set,
                    exc_info=True,
                )
                continue

            if len(collected) >= limit:
                break

        # Clientseitiger Kontext-Filter (FolderLocation)
        if contexts:
            prefixes = [f"/{ctx}/" for ctx in contexts]
            collected = [
                item for item in collected
                if any(
                    (item.get("FolderLocation") or "").startswith(p)
                    for p in prefixes
                )
            ]

        return collected[:limit]
