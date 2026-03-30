"""
WRS Client — BOM-Operationen (Mixin).
======================================

Stuecklistenstruktur laden: Usage-Links, Kind-Parts aufloesen.
Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)


class BomMixin:
    """BOM / Stuecklisten-Operationen (Mixin fuer WRSClientBase)."""

    def get_bom_children(self: "WRSClientBase", part_id: str) -> list:
        """BOM-Kinder (Usage Links) eines Parts laden.

        Windchill bietet mehrere OData-Navigations-Properties fuer die
        Stuecklistenstruktur. Welche verfuegbar ist, haengt von der
        WRS/OData-Version ab:
          - Uses           (Standard, v5+)
          - UsesInterface  (alternative Struktur)
          - BOMComponents  (aeltere Versionen)
          - PartStructure  (Fallback)

        Die erste funktionierende Strategie wird gecacht und fuer
        alle weiteren Abfragen dieser Session wiederverwendet.
        """
        nav_options = ["Uses", "UsesInterface", "BOMComponents", "PartStructure"]

        # Gecachte Strategie aus vorherigem Aufruf verwenden
        if self._bom_nav_strategy:
            nav, use_expand = self._bom_nav_strategy
            url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/{nav}"
            params = {"$expand": "Uses"} if use_expand else None
            result = self._get_all_pages(url, params, return_none_on_error=True)
            if result is not None:
                return result
            # Strategie hat nicht funktioniert → neu discovern
            self._bom_nav_strategy = None

        # Alle Strategien durchprobieren
        for nav in nav_options:
            url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/{nav}"

            # Zuerst mit $expand=Uses (liefert Kind-Parts inline mit)
            result = self._get_all_pages(url, {"$expand": "Uses"}, return_none_on_error=True)
            if result is not None:
                self._bom_nav_strategy = (nav, True)
                return result

            # Ohne $expand (Kind-Parts muessen einzeln aufgeloest werden)
            result = self._get_all_pages(url, return_none_on_error=True)
            if result is not None:
                self._bom_nav_strategy = (nav, False)
                return result

        return []

    def resolve_usage_link_child(self: "WRSClientBase", link: dict) -> Optional[dict]:
        """Kind-Part aus einem BOM Usage-Link aufloesen.

        Ein Usage-Link beschreibt die Beziehung Parent→Child in der Stueckliste.
        Das Kind-Part-Objekt kann entweder:
          a) Bereits inline im Link enthalten sein ($expand hat funktioniert)
          b) Per Navigation-Property nachgeladen werden muessen

        Probiert die Keys: Uses, RoleBObject, Child, Part.
        """
        # Pruefen ob das Kind bereits inline vorhanden ist
        for key in ["Uses", "RoleBObject", "Child", "Part"]:
            child = link.get(key)
            if isinstance(child, dict) and ("Number" in child or "ID" in child):
                return child
            # $expand kann eine Liste liefern (z.B. "Uses": [{...}])
            if isinstance(child, list) and child:
                first = child[0]
                if isinstance(first, dict) and ("Number" in first or "ID" in first):
                    return first

        # Kind per Navigation-Property nachladen
        link_id = link.get("ID", "")
        if not link_id:
            return None

        # Gecachte Navigation verwenden
        if self._usage_link_nav:
            child = self._resolve_link_via_nav(link_id, self._usage_link_nav)
            if child:
                return child
            self._usage_link_nav = None  # Funktioniert nicht mehr → neu discovern

        # Alle Navigation-Properties durchprobieren
        for nav in ["Uses", "RoleBObject", "Child"]:
            child = self._resolve_link_via_nav(link_id, nav)
            if child:
                self._usage_link_nav = nav
                return child

        return None

    def _resolve_link_via_nav(self: "WRSClientBase", link_id: str, nav: str) -> Optional[dict]:
        """Hilfsmethode: Kind-Part ueber ein bestimmtes Navigation-Property laden."""
        url = f"{self.odata_base}/ProdMgmt/UsageLinks('{link_id}')/{nav}"
        try:
            data = self._get_json(url)
            # OData kann Collection oder einzelnes Objekt liefern
            if "value" in data and data["value"]:
                return data["value"][0]
            if "ID" in data or "Number" in data:
                return data
        except Exception:
            logger.debug("_resolve_link_via_nav(%s, %s) failed", link_id, nav, exc_info=True)
        return None
