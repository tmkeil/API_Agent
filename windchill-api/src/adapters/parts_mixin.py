"""
WRS Client — Part-Operationen (Mixin).
=======================================

Methoden fuer Einzel-Part-Suche, ID-Lookup, Freitextsuche und Soft-Attributes.
Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from src.core.odata import extract_id, version_sort_key

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)


class PartsMixin:
    """Part-spezifische Operationen (Mixin fuer WRSClientBase)."""

    # ── Part-Suche ───────────────────────────────────────────

    def find_part(self: "WRSClientBase", part_number: str) -> dict:
        """Part nach Nummer suchen (neuste Version/Iteration).

        Versucht exakte OData-Filter — KEINE Fuzzy-Fallbacks (contains/startswith),
        da diese stillschweigend ein anderes Part liefern koennten.
        Fuer Freitextsuche → search_parts() verwenden.

        Returns:
            Dict mit allen Part-Properties.
        Raises:
            WRSError(404): Part nicht gefunden.
        """
        from src.adapters.base import WRSError

        url = f"{self.odata_base}/ProdMgmt/Parts"
        safe = part_number.replace("'", "''")

        # Nur exakte Filter — kein contains/startswith, um Falsch-Treffer zu vermeiden
        filters = [
            f"Number eq '{safe}'",
            f"Number eq '{safe}' and LatestIteration eq true",
        ]

        for filt in filters:
            resp = self._get(url, {"$filter": filt}, suppress_errors=True)
            if resp and resp.status_code == 200:
                items = resp.json().get("value", [])
                if items:
                    # Neuste Version zuerst; bei Gleichstand Manufacturing bevorzugen
                    items.sort(key=version_sort_key, reverse=True)
                    return items[0]

        raise WRSError(f"Part '{part_number}' nicht in Windchill gefunden", 404)

    def get_part_by_id(self: "WRSClientBase", part_id: str) -> Optional[dict]:
        """Part nach interner OData-ID laden."""
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')"
        try:
            return self._get_json(url)
        except Exception:
            logger.debug("get_part_by_id(%s) failed", part_id, exc_info=True)
            return None

    def search_parts(self: "WRSClientBase", query: str, limit: int = 25) -> list[dict]:
        """Freitextsuche nach Parts (Nummer oder Name).

        Kombiniert mehrere OData-Filter um moeglichst viele Treffer zu finden:
          1. Exakte Nummer    (schnell, hoechste Relevanz)
          2. Nummer enthaelt  (breit)
          3. Name enthaelt    (breit)
        """
        url = f"{self.odata_base}/ProdMgmt/Parts"
        collected: dict[str, dict] = {}
        safe = query.replace("'", "''")

        strategies = [
            {"$filter": f"Number eq '{safe}'", "$top": "20"},
            {"$filter": f"contains(Number,'{safe}')", "$top": "100"},
            {"$filter": f"contains(Name,'{safe}')", "$top": "100"},
        ]

        for params in strategies:
            try:
                items = self._get_all_pages(url, params)
                for item in items:
                    pid = extract_id(item)
                    if pid:
                        collected[str(pid)] = item
                if len(collected) >= 250:
                    break
            except Exception:
                logger.debug("search_parts filter failed: %s", params, exc_info=True)
                continue

        return list(collected.values())[:limit]

    # ── Soft Attributes ──────────────────────────────────────

    def get_soft_attributes(self: "WRSClientBase", part_id: str, attr_names: list[str]) -> dict:
        """Custom-Attribute (IBAs / Soft Attributes) eines Parts laden.

        IBAs sind firmenspezifische Attribute (z.B. BALMADEFROMNUMBER),
        die ueber $select abgefragt werden koennen.
        Fallback: Gesamten Part laden falls $select nicht unterstuetzt wird.
        """
        result = {name: "" for name in attr_names}
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')"

        # Versuch 1: Gezieltes $select (schneller, weniger Daten)
        try:
            resp = self._get(url, {"$select": ",".join(attr_names)}, suppress_errors=True)
            if resp and resp.status_code == 200:
                data = resp.json()
                for name in attr_names:
                    val = data.get(name, "")
                    if isinstance(val, dict):
                        val = val.get("Value", val.get("Display", ""))
                    if val:
                        result[name] = str(val)
                if any(result.values()):
                    return result
        except Exception:
            logger.debug("get_soft_attributes $select failed for %s", part_id, exc_info=True)

        # Versuch 2: Alle Properties laden (Fallback)
        try:
            data = self._get_json(url)
            for name in attr_names:
                val = data.get(name, "")
                if isinstance(val, dict):
                    val = val.get("Value", val.get("Display", ""))
                if val:
                    result[name] = str(val)
        except Exception:
            logger.debug("get_soft_attributes full-load failed for %s", part_id, exc_info=True)

        return result

    # ── Container-Liste ──────────────────────────────────────

    def get_containers(self: "WRSClientBase") -> list[dict]:
        """Windchill Container (Products/Libraries) auflisten.

        ``Containers`` ist ein Entity Set der **DataAdmin**-Domain,
        nicht der ProdMgmt-Domain. Ermittelt via:
        ``GET /servlet/odata/v6/DataAdmin/Containers``

        Returns:
            Liste von Container-Dicts mit ID, Name, ContainerType etc.
        """
        url = f"{self.odata_base}/DataAdmin/Containers"

        # Versuche zuerst mit Server-seitigem Filter …
        items = self._get_all_pages(
            url, {"$filter": "ContainerType eq 'Product'"}, return_none_on_error=True
        )

        # Fallback: kein Filter (manche Windchill-Versionen unterstützen $filter nicht)
        if items is None:
            logger.info("Container $filter fehlgeschlagen – lade alle Container ungefiltert")
            items = self._get_all_pages(url)

        if items is None:
            return []
        return items
