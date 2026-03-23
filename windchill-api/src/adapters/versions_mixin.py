"""
WRS Client — Versions- und Lifecycle-Operationen (Mixin).
==========================================================

Alle Versionen/Iterationen eines Objekts laden.
Lifecycle-History (Status-Uebergaenge) laden.
Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from src.core.odata import extract_id

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)


class VersionsMixin:
    """Versions- und Lifecycle-Operationen (Mixin fuer WRSClientBase)."""

    # Mapping: type_key → (OData service, entity set)
    _VERSION_ENTITIES: dict[str, tuple[str, str]] = {
        "part":            ("ProdMgmt",        "Parts"),
        "document":        ("DocMgmt",         "Documents"),
        "cad_document":    ("CADDocumentMgmt", "CADDocuments"),
        "change_notice":   ("ChangeMgmt",      "ChangeNotices"),
        "change_request":  ("ChangeMgmt",      "ChangeRequests"),
        "problem_report":  ("ChangeMgmt",      "ProblemReports"),
    }

    def get_all_versions(
        self: "WRSClientBase",
        type_key: str,
        number: str,
    ) -> list[dict]:
        """Alle Versionen/Iterationen eines Objekts laden.

        Sucht nach Number ohne LatestIteration-Filter, um alle
        Versionen zurueckzubekommen.

        Returns:
            Liste aller Versionen, sortiert absteigend (neueste zuerst).
        """
        from src.adapters.base import WRSError

        if type_key not in self._VERSION_ENTITIES:
            raise WRSError(f"Unbekannter Objekttyp fuer Versionen: '{type_key}'", status_code=400)

        service, entity_set = self._VERSION_ENTITIES[type_key]
        url = f"{self.odata_base}/{service}/{entity_set}"
        safe = number.replace("'", "''")

        # Alle Versionen/Iterationen fuer diese Nummer
        items = self._get_all_pages(
            url,
            {"$filter": f"Number eq '{safe}'", "$orderby": "Version desc,Iteration desc"},
            return_none_on_error=True,
        )

        # Fallback ohne $orderby (nicht alle Windchill-Versionen unterstuetzen das)
        if items is None:
            items = self._get_all_pages(
                url,
                {"$filter": f"Number eq '{safe}'"},
                return_none_on_error=True,
            )

        if not items:
            return []

        # Manuell sortieren fuer den Fall dass $orderby ignoriert wurde
        def _sort_key(item: dict) -> tuple[int, int]:
            try:
                v = int(item.get("Version", "0") or 0)
            except (ValueError, TypeError):
                v = 0
            try:
                i = int(item.get("Iteration", "0") or 0)
            except (ValueError, TypeError):
                i = 0
            return (v, i)

        items.sort(key=_sort_key, reverse=True)
        return items

    def get_lifecycle_history(
        self: "WRSClientBase",
        type_key: str,
        obj_id: str,
    ) -> list[dict]:
        """Lifecycle-History (Status-Uebergaenge) eines Objekts laden.

        Mehrere Strategien:
          1. LifeCycleHistory Navigation Property
          2. LifeCycleEvents Navigation Property
          3. StateHistory Navigation Property

        Falls keiner dieser Endpunkte verfuegbar ist, wird eine leere
        Liste zurueckgegeben — der Aufrufer kann dann stattdessen die
        Versionsliste als Proxy verwenden.
        """
        from src.adapters.base import WRSError

        if type_key not in self._VERSION_ENTITIES:
            raise WRSError(f"Unbekannter Objekttyp fuer Lifecycle: '{type_key}'", status_code=400)

        service, entity_set = self._VERSION_ENTITIES[type_key]

        nav_props = ["LifeCycleHistory", "LifeCycleEvents", "StateHistory"]
        for nav in nav_props:
            url = f"{self.odata_base}/{service}/{entity_set}('{obj_id}')/{nav}"
            items = self._get_all_pages(url, return_none_on_error=True)
            if items:
                return items

        return []
