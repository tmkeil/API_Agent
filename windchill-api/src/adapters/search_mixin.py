"""
WRS Client — Multi-Entity-Suche (Mixin).
=========================================

Suche ueber beliebige Windchill-Objekttypen (Parts, Dokumente, CAD, Change, …).
Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Generator

from src.core.odata import extract_id, version_sort_key

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)

# Windchill ignoriert $top und liefert immer 25 Items pro Seite (fest).
_WC_PAGE_SIZE = 25
# Standard-Seitenlimit pro Entity-Typ bei der Suche.
# 200 Seiten × 25 = 5000 Items pro Typ.
_DEFAULT_SEARCH_MAX_PAGES = 200


def _odata_escape(value: str) -> str:
    """Escape single quotes for OData string literals."""
    return value.replace("'", "''")


def _wildcard_clause(field: str, value: str) -> str:
    """Build an OData $filter clause for *value* on *field*, supporting wildcards.

    OData has no native wildcard operator. We translate shell-style patterns
    into ``startswith`` / ``endswith`` / ``contains`` calls.

    Semantics (``*`` = any sequence of characters, also empty; ``?`` ignored
    because OData has no single-char wildcard — treated as literal):

    * ``"ABC"``       → ``(Field eq 'ABC' or contains(Field,'ABC'))``
    * ``"ABC*"``      → ``startswith(Field,'ABC')``
    * ``"*ABC"``      → ``endswith(Field,'ABC')``
    * ``"*ABC*"``     → ``contains(Field,'ABC')``
    * ``"A*B"``       → ``startswith(Field,'A') and endswith(Field,'B')``
    * ``"A*B*C"``     → ``startswith(Field,'A') and contains(Field,'B') and endswith(Field,'C')``
    * ``"*A*B*"``     → ``contains(Field,'A') and contains(Field,'B')``

    Empty value returns an empty string.
    """
    v = (value or "").strip()
    if not v:
        return ""

    has_star = "*" in v
    if not has_star:
        esc = _odata_escape(v)
        return f"(contains({field},'{esc}') or {field} eq '{esc}')"

    starts_any = v.startswith("*")
    ends_any = v.endswith("*")
    segments = [s for s in v.split("*") if s]
    if not segments:
        # Pattern is all wildcards (e.g. "*" or "***") — matches anything.
        return ""

    parts: list[str] = []
    n = len(segments)
    for i, seg in enumerate(segments):
        esc = _odata_escape(seg)
        if i == 0 and not starts_any:
            parts.append(f"startswith({field},'{esc}')")
        elif i == n - 1 and not ends_any:
            parts.append(f"endswith({field},'{esc}')")
        else:
            parts.append(f"contains({field},'{esc}')")
    return " and ".join(parts) if len(parts) == 1 else "(" + " and ".join(parts) + ")"


def _build_search_filter(mode: str, query: str) -> str:
    """Build OData ``$filter`` for the given search *mode* and *query*.

    Wildcards (``*``) are translated via :func:`_wildcard_clause`. For
    ``keyword`` (default) the filter matches either ``Number`` or ``Name``.
    """
    number_clause = _wildcard_clause("Number", query)
    if mode == "number":
        return number_clause or ""
    # keyword / auto — search in Number and Name.
    name_clause = _wildcard_clause("Name", query)
    if not number_clause and not name_clause:
        return ""
    if not name_clause:
        return number_clause
    if not number_clause:
        return name_clause
    return f"({number_clause} or {name_clause})"


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

    # CADDocumentMgmt und DocMgmt Fallback-Pfade.
    # Verwendet _odata_url() fuer korrekte Versionen.
    _CAD_FALLBACK_DOMAINS: list[tuple[str, str]] = [
        # CADDocumentMgmt (v5 gemaess Swagger-Spec)
        ("CADDocumentMgmt", "CADDocuments"),
        # Some installs expose EPM docs under DocMgmt
        ("DocMgmt", "Documents"),
    ]

    def _find_cad_document(self: "WRSClientBase", number: str) -> dict | None:
        """Try multiple OData endpoints to find a CAD/EPM document by number.

        CADDocumentMgmt often only exists as v5 service. Falls back to
        DocMgmt/Documents with a Number filter.
        """
        safe = number.replace("'", "''")
        filters = [f"Number eq '{safe}'", f"contains(Number,'{safe}')"]

        for domain, entity_set in self._CAD_FALLBACK_DOMAINS:
            url = f"{self._odata_url(domain)}/{entity_set}"
            for filt in filters:
                resp = self._get(url, {"$filter": filt}, suppress_errors=True)
                if resp and resp.status_code == 200:
                    items = resp.json().get("value", [])
                    if items:
                        items.sort(key=version_sort_key, reverse=True)
                        return items[0]
        return None

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

        # --- CAD documents: use dedicated fallback (v4 + DocMgmt) ---
        if type_key == "cad_document":
            result = self._find_cad_document(number)
            if result:
                result["_entity_type"] = wc_type
                result["_entity_type_key"] = type_key
                return result
            raise WRSError(
                f"{wc_type} '{number}' nicht in Windchill gefunden", status_code=404
            )

        # --- Standard path ---
        url = f"{self._odata_url(service)}/{entity_set}"
        safe = number.replace("'", "''")

        filters = [
            f"Number eq '{safe}' and Latest eq true",
            f"Number eq '{safe}'",
            f"contains(Number,'{safe}')",
        ]

        for filt in filters:
            resp = self._get(url, {"$filter": filt}, suppress_errors=True)
            if resp and resp.status_code == 200:
                items = resp.json().get("value", [])
                if items:
                    items.sort(key=version_sort_key, reverse=True)
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
        mode: str = "auto",
    ) -> list[dict]:
        """Suche ueber mehrere Windchill-Entity-Typen gleichzeitig.

        Args:
            query:        Suchbegriff (Nummer oder Name, mit Wildcard * oder ?).
            entity_types: Liste von Typ-Keys (z.B. ["part","document"]).
                          None → alle Typen durchsuchen.
            contexts:     Optional Liste von Kontexten (z.B. ['P - Design']).
                          Filter erfolgt clientseitig ueber FolderLocation.
            limit:        Max. Gesamtergebnisse (0 = kein clientseitiges Limit).
            mode:         'number' = nur Nummer (schnell), 'keyword' = Nummer+Name,
                          'auto' = automatisch (digits → number, sonst keyword).

        Returns:
            Liste von OData-Dicts, ergaenzt um '_entity_type' (z.B. 'WTPart').
        """
        import re as _re
        from concurrent.futures import ThreadPoolExecutor, as_completed

        if entity_types is None:
            targets = list(self.SEARCHABLE_ENTITIES.items())
        else:
            targets = [
                (k, v) for k, v in self.SEARCHABLE_ENTITIES.items()
                if k in entity_types
            ]

        combined_filter = _build_search_filter(mode, query)

        max_pages = _DEFAULT_SEARCH_MAX_PAGES
        if limit > 0:
            max_pages = max(max_pages, (limit // _WC_PAGE_SIZE) + 2)

        # ── Phase 1: Erste Seite pro Typ (parallel) ──────────

        def _fetch_first(type_key: str, service: str, entity_set: str, wc_type: str):
            # CADDocumentMgmt — verwende domain-spezifische URL
            if type_key == "cad_document":
                for domain, entity in self._CAD_FALLBACK_DOMAINS:
                    url = f"{self._odata_url(domain)}/{entity}"
                    params: dict[str, str] = {"$filter": combined_filter}
                    try:
                        resp = self._raw_get(url, params)
                        if resp.status_code == 200:
                            data = resp.json()
                            items = list(data.get("value", []))
                            if items:
                                next_link = data.get("@odata.nextLink")
                                for item in items:
                                    item["_entity_type"] = wc_type
                                    item["_entity_type_key"] = type_key
                                return type_key, wc_type, items, next_link
                    except Exception:
                        logger.debug("search CAD fallback failed %s/%s", domain, entity, exc_info=True)
                return type_key, wc_type, [], None

            url = f"{self._odata_url(service)}/{entity_set}"
            params: dict[str, str] = {"$filter": combined_filter}
            try:
                resp = self._raw_get(url, params)
                if resp.status_code != 200:
                    logger.warning("search %s/%s returned %s for filter: %s",
                                   service, entity_set, resp.status_code,
                                   combined_filter[:200])
                    return type_key, wc_type, [], None
                data = resp.json()
                items = list(data.get("value", []))
                next_link = data.get("@odata.nextLink")
                for item in items:
                    item["_entity_type"] = wc_type
                    item["_entity_type_key"] = type_key
                return type_key, wc_type, items, next_link
            except Exception:
                logger.debug("search first page failed %s/%s", service, entity_set, exc_info=True)
                return type_key, wc_type, [], None

        all_items: list[dict] = []
        remaining_urls: list[tuple[str, str, str]] = []  # (url, type_key, wc_type)

        with ThreadPoolExecutor(max_workers=len(targets)) as pool:
            futures = [
                pool.submit(_fetch_first, tk, svc, es, wct)
                for tk, (svc, es, wct) in targets
            ]
            for f in as_completed(futures):
                type_key, wc_type, items, next_link = f.result()
                all_items.extend(items)

                if not next_link:
                    continue

                # Skiptoken-Muster erkennen (z.B. $skiptoken=25)
                m = _re.search(r'[\?&]\$skiptoken=(\d+)', next_link)
                if not m:
                    # Unbekanntes Paging-Format → sequentiell nachladen
                    page = 1
                    nl = next_link
                    while nl and page < max_pages:
                        page += 1
                        try:
                            r = self._raw_get(nl)
                            if r.status_code != 200:
                                break
                            d = r.json()
                        except Exception:
                            break
                        for it in d.get("value", []):
                            it["_entity_type"] = wc_type
                            it["_entity_type_key"] = type_key
                            all_items.append(it)
                        nl = d.get("@odata.nextLink")
                    continue

                skip_size = int(m.group(1))
                sep = next_link[m.start()]
                base_url = next_link[:m.start()]

                # URLs fuer Seite 2..max_pages generieren
                for pg in range(1, max_pages):
                    st = skip_size * pg
                    remaining_urls.append(
                        (f"{base_url}{sep}$skiptoken={st}", type_key, wc_type)
                    )

        # ── Phase 2: Alle Rest-Seiten in einem Pool ──────────
        # Sortiere nach Skiptoken aufsteigend: niedrige Offsets (schnell) von
        # allen Typen zuerst, hohe Offsets (langsam) spaeter.
        def _skiptoken_key(item: tuple[str, str, str]) -> int:
            m = _re.search(r'\$skiptoken=(\d+)', item[0])
            return int(m.group(1)) if m else 0

        remaining_urls.sort(key=_skiptoken_key)

        if remaining_urls:
            def _fetch_page(item: tuple[str, str, str]) -> list[dict]:
                pg_url, tk, wct = item
                try:
                    r = self._raw_get(pg_url)
                    if r.status_code != 200:
                        return []
                    items = list(r.json().get("value", []))
                    for it in items:
                        it["_entity_type"] = wct
                        it["_entity_type_key"] = tk
                    return items
                except Exception:
                    return []

            workers = min(len(remaining_urls), 40)
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = [pool.submit(_fetch_page, ru) for ru in remaining_urls]
                for f in as_completed(futures):
                    result = f.result()
                    if result:
                        all_items.extend(result)

        # ── Deduplizieren + filtern ───────────────────────────

        collected: list[dict] = []
        seen_ids: set[str] = set()
        for item in all_items:
            pid = extract_id(item)
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                collected.append(item)

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

    def search_entities_stream(
        self: "WRSClientBase",
        query: str,
        entity_types: list[str] | None = None,
        contexts: list[str] | None = None,
        limit: int = 0,
        cancelled: "threading.Event | None" = None,
        mode: str = "auto",
    ) -> Generator[list[dict], None, None]:
        """Streaming-Variante von search_entities.

        Yielded Batches von Ergebnissen sobald sie verfuegbar sind,
        statt auf alle Seiten zu warten.

        Args:
            cancelled: Optional threading.Event. Wenn gesetzt, bricht die
                       Suche fruehzeitig ab (z.B. bei Client-Disconnect).
            mode:      'number' | 'keyword' | 'auto'.
        """
        import re as _re
        import threading as _threading
        from concurrent.futures import ThreadPoolExecutor, as_completed

        if cancelled is None:
            cancelled = _threading.Event()

        if entity_types is None:
            targets = list(self.SEARCHABLE_ENTITIES.items())
        else:
            targets = [
                (k, v) for k, v in self.SEARCHABLE_ENTITIES.items()
                if k in entity_types
            ]

        combined_filter = _build_search_filter(mode, query)

        max_pages = _DEFAULT_SEARCH_MAX_PAGES
        if limit > 0:
            max_pages = max(max_pages, (limit // _WC_PAGE_SIZE) + 2)

        # Helpers fuer Kontext- und Duplikat-Filter
        seen_ids: set[str] = set()
        ctx_prefixes = [f"/{ctx}/" for ctx in contexts] if contexts else None
        total_yielded = 0

        def _dedup_filter(items: list[dict]) -> list[dict]:
            nonlocal total_yielded
            out = []
            for item in items:
                pid = extract_id(item)
                if not pid or pid in seen_ids:
                    continue
                seen_ids.add(pid)
                if ctx_prefixes:
                    loc = item.get("FolderLocation") or ""
                    if not any(loc.startswith(p) for p in ctx_prefixes):
                        continue
                out.append(item)
            if limit > 0 and total_yielded + len(out) > limit:
                out = out[:limit - total_yielded]
            total_yielded += len(out)
            return out

        # ── Phase 1: Erste Seite pro Typ ─────────────────────

        def _fetch_first(type_key: str, service: str, entity_set: str, wc_type: str):
            if cancelled.is_set():
                return type_key, wc_type, [], None

            # CADDocumentMgmt — verwende domain-spezifische URL
            if type_key == "cad_document":
                for domain, entity in self._CAD_FALLBACK_DOMAINS:
                    url = f"{self._odata_url(domain)}/{entity}"
                    params: dict[str, str] = {"$filter": combined_filter}
                    try:
                        resp = self._raw_get(url, params)
                        if resp.status_code == 200:
                            data = resp.json()
                            items = list(data.get("value", []))
                            if items:
                                next_link = data.get("@odata.nextLink")
                                for item in items:
                                    item["_entity_type"] = wc_type
                                    item["_entity_type_key"] = type_key
                                return type_key, wc_type, items, next_link
                    except Exception:
                        logger.debug("stream search CAD fallback failed %s/%s", domain, entity, exc_info=True)
                return type_key, wc_type, [], None

            url = f"{self._odata_url(service)}/{entity_set}"
            params: dict[str, str] = {"$filter": combined_filter}
            try:
                resp = self._raw_get(url, params)
                if resp.status_code != 200:
                    logger.warning("stream search %s/%s returned %s for filter: %s",
                                   service, entity_set, resp.status_code,
                                   combined_filter[:200])
                    return type_key, wc_type, [], None
                data = resp.json()
                items = list(data.get("value", []))
                next_link = data.get("@odata.nextLink")
                for item in items:
                    item["_entity_type"] = wc_type
                    item["_entity_type_key"] = type_key
                return type_key, wc_type, items, next_link
            except Exception:
                return type_key, wc_type, [], None

        remaining_urls: list[tuple[str, str, str]] = []

        with ThreadPoolExecutor(max_workers=len(targets)) as pool:
            futures = [
                pool.submit(_fetch_first, tk, svc, es, wct)
                for tk, (svc, es, wct) in targets
            ]
            for f in as_completed(futures):
                if cancelled.is_set():
                    return
                type_key, wc_type, items, next_link = f.result()

                if items:
                    batch = _dedup_filter(items)
                    if batch:
                        yield batch
                    if limit > 0 and total_yielded >= limit:
                        return

                if not next_link:
                    continue

                m = _re.search(r'[\?&]\$skiptoken=(\d+)', next_link)
                if not m:
                    continue

                skip_size = int(m.group(1))
                sep = next_link[m.start()]
                base_url = next_link[:m.start()]

                for pg in range(1, max_pages):
                    remaining_urls.append(
                        (f"{base_url}{sep}$skiptoken={skip_size * pg}", type_key, wc_type)
                    )

        # ── Phase 2: Rest-Seiten parallel, yield pro Batch ───
        # Sortiere nach Skiptoken aufsteigend: schnelle Seiten zuerst.
        def _skiptoken_key(item: tuple[str, str, str]) -> int:
            m = _re.search(r'\$skiptoken=(\d+)', item[0])
            return int(m.group(1)) if m else 0

        remaining_urls.sort(key=_skiptoken_key)

        if remaining_urls and (limit == 0 or total_yielded < limit):
            def _fetch_page(item: tuple[str, str, str]) -> list[dict]:
                if cancelled.is_set():
                    return []
                pg_url, tk, wct = item
                try:
                    r = self._raw_get(pg_url)
                    if r.status_code != 200:
                        return []
                    items = list(r.json().get("value", []))
                    for it in items:
                        it["_entity_type"] = wct
                        it["_entity_type_key"] = tk
                    return items
                except Exception:
                    return []

            workers = min(len(remaining_urls), 40)
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = [pool.submit(_fetch_page, ru) for ru in remaining_urls]
                for f in as_completed(futures):
                    if cancelled.is_set():
                        # Cancel pending futures (best-effort)
                        for pf in futures:
                            pf.cancel()
                        return
                    result = f.result()
                    if result:
                        batch = _dedup_filter(result)
                        if batch:
                            yield batch
                        if limit > 0 and total_yielded >= limit:
                            return

    def advanced_search(
        self: "WRSClientBase",
        query: str = "",
        criteria: list[dict] | None = None,
        combinator: str = "and",
        entity_types: list[str] | None = None,
        contexts: list[str] | None = None,
        state: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        date_field: str = "modified",
        attributes: dict[str, str] | None = None,
        limit: int = 200,
    ) -> list[dict]:
        """Erweiterte Suche mit strukturierten OData-Filtern.

        Supports either a single free-text ``query`` (applied to ``Number`` and
        ``Name``) or a list of structured ``criteria`` (each with ``field`` and
        ``value``) joined by ``combinator`` (``and`` / ``or``). Wildcards
        (``*``) are translated via :func:`_wildcard_clause`.

        Gleiche 2-Phasen-Strategie wie search_entities (flacher Pool).
        """
        import re as _re
        from concurrent.futures import ThreadPoolExecutor, as_completed

        if entity_types is None or len(entity_types) == 0:
            targets = list(self.SEARCHABLE_ENTITIES.items())
        else:
            targets = [
                (k, v) for k, v in self.SEARCHABLE_ENTITIES.items()
                if k in entity_types
            ]

        # ── Build shared filter clauses ──────────────────────
        clauses: list[str] = []

        # Structured criteria take precedence over free-text query.
        if criteria:
            allowed_fields = {"Number", "Name"}
            criterion_clauses: list[str] = []
            for c in criteria:
                field = (c.get("field") or "Number").strip()
                if field not in allowed_fields:
                    continue
                value = (c.get("value") or "").strip()
                clause = _wildcard_clause(field, value)
                if clause:
                    criterion_clauses.append(clause)
            if criterion_clauses:
                joiner = " or " if (combinator or "and").lower() == "or" else " and "
                clauses.append("(" + joiner.join(criterion_clauses) + ")")
        elif query:
            q_clause_number = _wildcard_clause("Number", query)
            q_clause_name = _wildcard_clause("Name", query)
            if q_clause_number and q_clause_name:
                clauses.append(f"({q_clause_number} or {q_clause_name})")
            elif q_clause_number:
                clauses.append(q_clause_number)
            elif q_clause_name:
                clauses.append(q_clause_name)

        if state:
            safe_st = state.strip().replace("'", "''")
            clauses.append(f"State eq '{safe_st}'")

        # Date filter — choose OData field based on date_field param
        _date_odata_field = "CreateStamp" if date_field == "created" else "ModifyStamp"

        if date_from:
            clauses.append(f"{_date_odata_field} ge {date_from}T00:00:00Z")

        if date_to:
            clauses.append(f"{_date_odata_field} le {date_to}T23:59:59Z")

        if attributes:
            for attr_name, attr_val in attributes.items():
                safe_name = attr_name.replace("'", "''")
                safe_val = attr_val.replace("'", "''")
                clauses.append(f"{safe_name} eq '{safe_val}'")

        filter_str = " and ".join(clauses) if clauses else ""
        max_pages = max(_DEFAULT_SEARCH_MAX_PAGES, (limit // _WC_PAGE_SIZE) + 2)

        # ── Phase 1: Erste Seite pro Typ ─────────────────────

        def _fetch_first(type_key: str, service: str, entity_set: str, wc_type: str):
            url = f"{self._odata_url(service)}/{entity_set}"
            params: dict[str, str] = {}
            if filter_str:
                params["$filter"] = filter_str
            try:
                resp = self._raw_get(url, params)
                if resp.status_code != 200:
                    return type_key, wc_type, [], None
                data = resp.json()
                items = list(data.get("value", []))
                next_link = data.get("@odata.nextLink")
                for item in items:
                    item["_entity_type"] = wc_type
                    item["_entity_type_key"] = type_key
                return type_key, wc_type, items, next_link
            except Exception:
                return type_key, wc_type, [], None

        all_items: list[dict] = []
        remaining_urls: list[tuple[str, str, str]] = []

        with ThreadPoolExecutor(max_workers=len(targets)) as pool:
            futures = [
                pool.submit(_fetch_first, tk, svc, es, wct)
                for tk, (svc, es, wct) in targets
            ]
            for f in as_completed(futures):
                type_key, wc_type, items, next_link = f.result()
                all_items.extend(items)

                if not next_link:
                    continue

                m = _re.search(r'[\?&]\$skiptoken=(\d+)', next_link)
                if not m:
                    # Sequentieller Fallback
                    page = 1
                    nl = next_link
                    while nl and page < max_pages:
                        page += 1
                        try:
                            r = self._raw_get(nl)
                            if r.status_code != 200:
                                break
                            d = r.json()
                        except Exception:
                            break
                        for it in d.get("value", []):
                            it["_entity_type"] = wc_type
                            it["_entity_type_key"] = type_key
                            all_items.append(it)
                        nl = d.get("@odata.nextLink")
                    continue

                skip_size = int(m.group(1))
                sep = next_link[m.start()]
                base_url = next_link[:m.start()]

                for pg in range(1, max_pages):
                    remaining_urls.append(
                        (f"{base_url}{sep}$skiptoken={skip_size * pg}", type_key, wc_type)
                    )

        # ── Phase 2: Rest-Seiten parallel ────────────────────

        if remaining_urls:
            def _fetch_page(item: tuple[str, str, str]) -> list[dict]:
                pg_url, tk, wct = item
                try:
                    r = self._raw_get(pg_url)
                    if r.status_code != 200:
                        return []
                    items = list(r.json().get("value", []))
                    for it in items:
                        it["_entity_type"] = wct
                        it["_entity_type_key"] = tk
                    return items
                except Exception:
                    return []

            workers = min(len(remaining_urls), 20)
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = [pool.submit(_fetch_page, ru) for ru in remaining_urls]
                for f in as_completed(futures):
                    result = f.result()
                    if result:
                        all_items.extend(result)

        # ── Deduplizieren + filtern ──────────────────────────

        collected: list[dict] = []
        seen_ids: set[str] = set()
        for item in all_items:
            pid = extract_id(item)
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                collected.append(item)

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
