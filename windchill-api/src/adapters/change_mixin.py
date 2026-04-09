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
