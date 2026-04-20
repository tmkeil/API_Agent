"""
WRS Client — Change Management Mixin.
=======================================

Affected Items und Resulting Items fuer Change-Objekte
(WTChangeOrder2, WTChangeRequest2, WTChangeIssue).

Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from src.core.odata import extract_id, normalize_item

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)


# Mapping von WRS-Feldern in Change-Objekten:
# ChangeMgmt/ChangeNotices  → AffectedObjects, ResultingObjects
# ChangeMgmt/ChangeRequests → AffectedObjects
# ChangeMgmt/ProblemReports → AffectedObjects


class ChangeMixin:
    """Change-Management-Operationen (Mixin fuer WRSClientBase)."""

    # Mapping: type_key → (OData service section, entity set)
    _CHANGE_ENTITIES: dict[str, tuple[str, str]] = {
        "change_notice":  ("ChangeMgmt", "ChangeNotices"),
        "change_request": ("ChangeMgmt", "ChangeRequests"),
        "problem_report": ("ChangeMgmt", "ProblemReports"),
    }

    def list_change_notices(
        self: "WRSClientBase",
        *,
        state: str = "",
        sub_type: str = "",
        top: int = 50,
        skip: int = 0,
    ) -> tuple[list[dict], int]:
        """Change Notices auflisten mit optionalen Filtern.

        Args:
            state:    State-Filter (z.B. 'OPEN', 'RESOLVED', 'CANCELLED').
            sub_type: ObjectType-Filter (z.B. 'ERP Transfer').
            top:      Max Ergebnisse pro Seite.
            skip:     Offset fuer Paging.

        Returns:
            Tuple (items, total_count).
        """
        service, entity_set = self._CHANGE_ENTITIES["change_notice"]
        url = f"{self._odata_url(service)}/{entity_set}"

        filters: list[str] = []
        if state:
            safe = state.replace("'", "''")
            filters.append(f"State/Value eq '{safe}'")
        if sub_type:
            safe = sub_type.replace("'", "''")
            filters.append(f"contains(ObjectType,'{safe}')")

        params: dict = {
            "$count": True,
            "$orderby": "LastModified desc",
        }
        if filters:
            params["$filter"] = " and ".join(filters)

        # Erste Seite holen (fuer Total-Count)
        first_resp = self._get(url, {**params, "$top": min(top, 25), "$skip": skip}, suppress_errors=True)
        if not first_resp or first_resp.status_code != 200:
            return [], 0

        first_data = first_resp.json()
        first_items = list(first_data.get("value", []))
        total = first_data.get("@odata.count", len(first_items))

        # Windchill cappt pro Request auf 25 → weitere Seiten parallel nachladen
        if top > 25 and len(first_items) == 25 and total > 25:
            import math
            from concurrent.futures import ThreadPoolExecutor, as_completed

            needed_remaining = min(top, int(total)) - 25
            needed_pages = math.ceil(needed_remaining / 25)

            page_skips = [skip + 25 * (i + 1) for i in range(needed_pages)]

            def _fetch_page(page_skip: int) -> tuple[int, list[dict]]:
                r = self._get(
                    url,
                    {**params, "$top": 25, "$skip": page_skip},
                    suppress_errors=True,
                )
                if not r or r.status_code != 200:
                    return page_skip, []
                return page_skip, list(r.json().get("value", []))

            results_by_skip: dict[int, list[dict]] = {skip: first_items}
            with ThreadPoolExecutor(max_workers=10) as pool:
                futures = {pool.submit(_fetch_page, ps): ps for ps in page_skips}
                for fut in as_completed(futures):
                    ps, items_pg = fut.result()
                    results_by_skip[ps] = items_pg

            all_items: list[dict] = []
            for ps in sorted(results_by_skip.keys()):
                all_items.extend(results_by_skip[ps])
            items = all_items[:top]
        else:
            items = first_items[:top]

        return items, total

    def get_change_affected_items(
        self: "WRSClientBase",
        type_key: str,
        number: str,
    ) -> list[dict]:
        """Affected Items eines Change-Objekts abfragen.

        Windchill OData: ChangeNotices('ID')/AffectedObjects
        oder Expand auf ChangeNotices?$filter=Number eq '...'&$expand=AffectedObjects

        Returns:
            List of normalized item dicts with cross-reference info.
        """
        from src.adapters.base import WRSError

        if type_key not in self._CHANGE_ENTITIES:
            raise WRSError(f"Kein Change-Typ: '{type_key}'", status_code=400)

        service, entity_set = self._CHANGE_ENTITIES[type_key]

        # Step 1: Find the change object
        change_obj = self._find_change_by_number(service, entity_set, number)
        if not change_obj:
            raise WRSError(
                f"{entity_set} '{number}' nicht gefunden", status_code=404
            )

        change_id = extract_id(change_obj)
        if not change_id:
            raise WRSError(
                f"Keine ID fuer {entity_set} '{number}'", status_code=404
            )

        # Step 2: Query AffectedObjects navigation property
        url = f"{self._odata_url(service)}/{entity_set}('{change_id}')/AffectedObjects"
        items = self._get_all_pages(url, return_none_on_error=True)
        if items is None:
            # Fallback: try $expand approach
            items = self._expand_change_nav(service, entity_set, number, "AffectedObjects")

        return items or []

    def get_change_resulting_items(
        self: "WRSClientBase",
        type_key: str,
        number: str,
    ) -> list[dict]:
        """Resulting Items eines Change-Objekts abfragen (nur Change Notices).

        Returns:
            List of normalized item dicts.
        """
        from src.adapters.base import WRSError

        if type_key not in self._CHANGE_ENTITIES:
            raise WRSError(f"Kein Change-Typ: '{type_key}'", status_code=400)

        service, entity_set = self._CHANGE_ENTITIES[type_key]

        change_obj = self._find_change_by_number(service, entity_set, number)
        if not change_obj:
            raise WRSError(
                f"{entity_set} '{number}' nicht gefunden", status_code=404
            )

        change_id = extract_id(change_obj)
        if not change_id:
            raise WRSError(
                f"Keine ID fuer {entity_set} '{number}'", status_code=404
            )

        # ResultingObjects nav property
        url = f"{self._odata_url(service)}/{entity_set}('{change_id}')/ResultingObjects"
        items = self._get_all_pages(url, return_none_on_error=True)
        if items is None:
            items = self._expand_change_nav(service, entity_set, number, "ResultingObjects")

        return items or []

    # ── Internal helpers ─────────────────────────────────────

    def _find_change_by_number(
        self: "WRSClientBase",
        service: str,
        entity_set: str,
        number: str,
    ) -> dict | None:
        """Find a change object by Number, returning the latest version."""
        url = f"{self._odata_url(service)}/{entity_set}"
        safe = number.replace("'", "''")

        resp = self._get(
            url,
            {"$filter": f"Number eq '{safe}'"},
            suppress_errors=True,
        )
        if resp and resp.status_code == 200:
            items = resp.json().get("value", [])
            if items:
                # Latest version first
                items.sort(
                    key=lambda p: (p.get("Version", ""), p.get("Iteration", "")),
                    reverse=True,
                )
                return items[0]
        return None

    def _expand_change_nav(
        self: "WRSClientBase",
        service: str,
        entity_set: str,
        number: str,
        nav_property: str,
    ) -> list[dict]:
        """Fallback: $expand on the entity set to get navigation property inline."""
        url = f"{self._odata_url(service)}/{entity_set}"
        safe = number.replace("'", "''")
        resp = self._get(
            url,
            {"$filter": f"Number eq '{safe}'", "$expand": nav_property},
            suppress_errors=True,
        )
        if resp and resp.status_code == 200:
            items = resp.json().get("value", [])
            if items:
                return items[0].get(nav_property, [])
        return []
