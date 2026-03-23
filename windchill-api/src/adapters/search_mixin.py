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

from src.core.odata import extract_id

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)

# Windchill ignoriert $top und liefert immer 25 Items pro Seite (fest).
_WC_PAGE_SIZE = 25
# Standard-Seitenlimit pro Entity-Typ bei der Suche.
# 200 Seiten × 25 = 5000 Items pro Typ.
_DEFAULT_SEARCH_MAX_PAGES = 200


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

        Strategie (2-Phasen, flacher Thread-Pool):

        Phase 1 — Erste Seite pro Typ parallel abrufen.
                  Liefert Ergebnisse + Skiptoken-Muster.
        Phase 2 — Alle verbleibenden Seiten aller Typen in einem
                  einzigen Thread-Pool parallel abrufen.

        Kein verschachtelter Thread-Pool, kein $count.

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
        import re as _re
        from concurrent.futures import ThreadPoolExecutor, as_completed

        if entity_types is None:
            targets = list(self.SEARCHABLE_ENTITIES.items())
        else:
            targets = [
                (k, v) for k, v in self.SEARCHABLE_ENTITIES.items()
                if k in entity_types
            ]

        safe = query.replace("'", "''")

        # Query-Intelligenz: den OData-Filter an die Art des Suchbegriffs anpassen.
        #
        # 1. Exakte Nummer (Ziffern + >= 5 Zeichen + keine Wildcards):
        #    → Nur "Number eq" (Index-Lookup, ~0.5s statt ~7s).
        #      Beispiel: S2200287364, BCC0812-P-A051-004
        #
        # 2. Kurze/partielle Nummer (Ziffern, aber < 5 Zeichen oder Wildcards):
        #    → "Number eq" + "contains(Number,...)"
        #      Beispiel: BCC08, Z03
        #
        # 3. Reiner Text (keine Ziffern):
        #    → "contains(Number,...) or contains(Name,...)"
        #      Beispiel: BCC, Sensor
        _has_digits = any(c.isdigit() for c in query)
        _has_wildcards = "*" in query or "?" in query
        _is_exact_number = _has_digits and len(query) >= 5 and not _has_wildcards

        if _is_exact_number:
            combined_filter = f"Number eq '{safe}'"
        elif _has_digits:
            combined_filter = (
                f"(Number eq '{safe}' or contains(Number,'{safe}'))"
            )
        else:
            combined_filter = (
                f"(Number eq '{safe}' or contains(Number,'{safe}') "
                f"or contains(Name,'{safe}'))"
            )

        max_pages = _DEFAULT_SEARCH_MAX_PAGES
        if limit > 0:
            max_pages = max(max_pages, (limit // _WC_PAGE_SIZE) + 2)

        # ── Phase 1: Erste Seite pro Typ (parallel) ──────────

        def _fetch_first(type_key: str, service: str, entity_set: str, wc_type: str):
            url = f"{self.odata_base}/{service}/{entity_set}"
            params: dict[str, str] = {"$filter": combined_filter}
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
    ) -> Generator[list[dict], None, None]:
        """Streaming-Variante von search_entities.

        Yielded Batches von Ergebnissen sobald sie verfuegbar sind,
        statt auf alle Seiten zu warten. Jeder Batch ist eine Liste
        von OData-Dicts (dedupliziert, kontextgefiltert).

        Phase 1 — Erste Seite pro Typ parallel → yield sofort.
        Phase 2 — Restliche Seiten parallel → yield pro fertigem Batch.

        Args:
            cancelled: Optional threading.Event. Wenn gesetzt, bricht die
                       Suche fruehzeitig ab (z.B. bei Client-Disconnect).
        """
        import re as _re
        import threading as _threading
        from concurrent.futures import ThreadPoolExecutor, as_completed

        if cancelled is None:
            cancelled = _threading.Event()  # Dummy, wird nie gesetzt

        if entity_types is None:
            targets = list(self.SEARCHABLE_ENTITIES.items())
        else:
            targets = [
                (k, v) for k, v in self.SEARCHABLE_ENTITIES.items()
                if k in entity_types
            ]

        safe = query.replace("'", "''")
        _has_digits = any(c.isdigit() for c in query)
        _has_wildcards = "*" in query or "?" in query
        _is_exact_number = _has_digits and len(query) >= 5 and not _has_wildcards

        if _is_exact_number:
            combined_filter = f"Number eq '{safe}'"
        elif _has_digits:
            combined_filter = f"(Number eq '{safe}' or contains(Number,'{safe}'))"
        else:
            combined_filter = (
                f"(Number eq '{safe}' or contains(Number,'{safe}') "
                f"or contains(Name,'{safe}'))"
            )

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
            url = f"{self.odata_base}/{service}/{entity_set}"
            params: dict[str, str] = {"$filter": combined_filter}
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

        if query:
            safe_q = query.replace("'", "''")
            _has_digits = any(c.isdigit() for c in query)
            _has_wildcards = "*" in query or "?" in query
            _is_exact_number = _has_digits and len(query) >= 5 and not _has_wildcards
            if _is_exact_number:
                clauses.append(f"Number eq '{safe_q}'")
            elif _has_digits:
                clauses.append(
                    f"(contains(Number,'{safe_q}'))"
                )
            else:
                clauses.append(
                    f"(contains(Number,'{safe_q}') or contains(Name,'{safe_q}'))"
                )

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
        max_pages = max(_DEFAULT_SEARCH_MAX_PAGES, (limit // _WC_PAGE_SIZE) + 2)

        # ── Phase 1: Erste Seite pro Typ ─────────────────────

        def _fetch_first(type_key: str, service: str, entity_set: str, wc_type: str):
            url = f"{self.odata_base}/{service}/{entity_set}"
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
