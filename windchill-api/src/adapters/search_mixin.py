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
        context: str | None = None,
        limit: int = 200,
    ) -> list[dict]:
        """Suche ueber mehrere Windchill-Entity-Typen gleichzeitig.

        Args:
            query:        Suchbegriff (Nummer oder Name, mit Wildcard * oder ?).
            entity_types: Liste von Typ-Keys (z.B. ["part","document"]).
                          None → alle Typen durchsuchen.
            context:      Optional ContainerName filter (z.B. 'Balluff').
            limit:        Max. Gesamtergebnisse.

        Returns:
            Liste von OData-Dicts, ergaenzt um '_entity_type' (z.B. 'WTPart').
        """
        if entity_types is None:
            targets = list(self.SEARCHABLE_ENTITIES.items())
        else:
            targets = [
                (k, v) for k, v in self.SEARCHABLE_ENTITIES.items()
                if k in entity_types
            ]

        safe = query.replace("'", "''")
        collected: list[dict] = []
        seen_ids: set[str] = set()

        # Optional ContainerName suffix for OData $filter
        ctx_clause = ""
        if context:
            safe_ctx = context.strip().replace("'", "''")
            ctx_clause = f" and ContainerName eq '{safe_ctx}'"

        for type_key, (service, entity_set, wc_type) in targets:
            url = f"{self.odata_base}/{service}/{entity_set}"

            # OData-Filter: exakt, contains Number, contains Name
            filters = [
                {"$filter": f"Number eq '{safe}'{ctx_clause}", "$top": "20"},
                {"$filter": f"contains(Number,'{safe}'){ctx_clause}", "$top": "100"},
                {"$filter": f"contains(Name,'{safe}'){ctx_clause}", "$top": "100"},
            ]

            for params in filters:
                try:
                    items = self._get_all_pages(url, params, return_none_on_error=True)
                    if items is None:
                        # Service or entity set not available → skip remaining filters
                        break
                    for item in items:
                        pid = extract_id(item)
                        if pid and pid not in seen_ids:
                            seen_ids.add(pid)
                            item["_entity_type"] = wc_type
                            item["_entity_type_key"] = type_key
                            collected.append(item)
                except Exception:
                    logger.debug("search_entities failed for %s/%s", service, entity_set, exc_info=True)
                    continue

                if len(collected) >= limit:
                    break

            if len(collected) >= limit:
                break

        return collected[:limit]

    def advanced_search(
        self: "WRSClientBase",
        query: str = "",
        entity_types: list[str] | None = None,
        context: str | None = None,
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
            context:      ContainerName filter.
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

        if context:
            safe_ctx = context.strip().replace("'", "''")
            clauses.append(f"ContainerName eq '{safe_ctx}'")

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

            params: dict[str, str] = {"$top": str(min(limit, 200))}
            if filter_str:
                params["$filter"] = filter_str

            try:
                items = self._get_all_pages(url, params, return_none_on_error=True)
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

        return collected[:limit]
