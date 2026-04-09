"""
WRS Client — BOM-Operationen (Mixin).
======================================

Stuecklistenstruktur laden: Usage-Links, Kind-Parts aufloesen.
Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.

Offizieller Weg (WRS 1.6 Doku):
  POST Parts('<id>')/PTC.ProdMgmt.GetPartStructure
      ?$expand=Components($expand=Part,PartUse)
  → liefert Components[] mit Part (Kind) und PartUse (Usage-Link-Infos)

Fallback (aeltere WRS-Versionen):
  GET Parts('<id>')/Uses?$expand=Uses
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)


class BomMixin:
    """BOM / Stuecklisten-Operationen (Mixin fuer WRSClientBase)."""

    # ── Offizielle Methode: GetPartStructure (POST Action) ──

    def get_part_structure(
        self: "WRSClientBase",
        part_id: str,
    ) -> Optional[list[dict[str, Any]]]:
        """BOM-Kinder via offiziellem GetPartStructure-Action laden.

        Offizieller Weg laut WRS 1.6 Doku:
          POST /ProdMgmt/Parts('<id>')/PTC.ProdMgmt.GetPartStructure
              ?$expand=Components($expand=Part,PartUse)

        Returns:
            Liste von Component-Dicts mit 'Part' und 'PartUse' Unter-Objekten,
            oder None falls die Action nicht verfuegbar ist (Fallback noetig).
        """
        url = (
            f"{self._odata_url('ProdMgmt')}/Parts('{part_id}')"
            f"/PTC.ProdMgmt.GetPartStructure"
            f"?$expand=Components($expand=Part,PartUse)"
        )
        self._refresh_csrf()
        resp = self._post(url, json_body={}, suppress_errors=True)

        if resp is None or resp.status_code not in (200, 201):
            status = resp.status_code if resp else "no response"
            logger.info("GetPartStructure nicht verfuegbar (HTTP %s) — verwende Fallback", status)
            return None

        data = resp.json()

        # Response kann direkt Components enthalten oder in 'value'
        components = data.get("Components") or data.get("value") or []

        # Wenn die Response ein einzelnes Part-Objekt ist (mit Components darin)
        if not components and isinstance(data, dict):
            # GetPartStructure liefert manchmal {... , "Components": [...]}
            for key in ("Components", "BOMComponents", "PartStructure"):
                if key in data and isinstance(data[key], list):
                    components = data[key]
                    break

        if not isinstance(components, list):
            logger.warning("GetPartStructure: unerwartetes Format — components=%s", type(components))
            return None

        logger.debug("GetPartStructure lieferte %d Components fuer %s", len(components), part_id)
        return components

    # ── Fallback: alte Methode (GET /Uses) ───────────────────

    def get_bom_children(self: "WRSClientBase", part_id: str) -> list:
        """BOM-Kinder (Usage Links) eines Parts laden.

        Versucht zuerst den offiziellen GetPartStructure-Weg (POST Action).
        Falls das fehlschlaegt, Fallback auf GET /Uses mit Strategie-Discovery.
        """
        # 1. Offizieller Weg: GetPartStructure
        if not getattr(self, "_bom_use_legacy", False):
            components = self.get_part_structure(part_id)
            if components is not None:
                # Erfolg → in usage-link-kompatibles Format transformieren
                return self._components_to_usage_links(components)
            # GetPartStructure nicht verfuegbar → dauerhaft auf Legacy wechseln
            self._bom_use_legacy = True
            logger.info("Wechsle dauerhaft auf Legacy-BOM-Methode (GET /Uses)")

        # 2. Fallback: alte Methode
        return self._get_bom_children_legacy(part_id)

    def _components_to_usage_links(
        self: "WRSClientBase", components: list[dict]
    ) -> list[dict]:
        """GetPartStructure-Components in das alte usage-link-Format konvertieren.

        Jedes Component hat 'Part' (Kind-Part) und 'PartUse' (Link-Infos).
        Wir fuegen das Kind-Part direkt unter dem Key 'Uses' ein,
        sodass resolve_usage_link_child() es sofort findet.
        """
        result = []
        for comp in components:
            part_use = comp.get("PartUse") or {}
            child_part = comp.get("Part") or {}

            if not child_part and not part_use:
                continue

            # Baue ein usage-link-aehnliches Dict:
            # part_use enthält Quantity, Unit, LineNumber, FindNumber, etc.
            # Wir haengen das Kind-Part unter 'Uses' an (gleicher Key wie $expand=Uses)
            link = dict(part_use)
            if child_part:
                link["Uses"] = child_part

            # Uebernehme auch Component-Level Attribute (z.B. Occurrence)
            for k, v in comp.items():
                if k not in ("Part", "PartUse", "@odata.type") and k not in link:
                    link[k] = v

            result.append(link)

        return result

    def _get_bom_children_legacy(self: "WRSClientBase", part_id: str) -> list:
        """Legacy-Fallback: BOM-Kinder via GET /Uses laden.

        Probiert verschiedene OData-Navigations-Properties:
          - Uses           (Standard, v5+)
          - UsesInterface  (alternative Struktur)
          - BOMComponents  (aeltere Versionen)
          - PartStructure  (Fallback)
        """
        nav_options = ["Uses", "UsesInterface", "BOMComponents", "PartStructure"]

        # Gecachte Strategie aus vorherigem Aufruf verwenden
        if self._bom_nav_strategy:
            nav, use_expand = self._bom_nav_strategy
            url = f"{self._odata_url('ProdMgmt')}/Parts('{part_id}')/{nav}"
            params = {"$expand": "Uses"} if use_expand else None
            result = self._get_all_pages(url, params, return_none_on_error=True)
            if result is not None:
                return result
            self._bom_nav_strategy = None

        # Alle Strategien durchprobieren
        for nav in nav_options:
            url = f"{self._odata_url('ProdMgmt')}/Parts('{part_id}')/{nav}"

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
          a) Bereits inline im Link enthalten sein ($expand oder GetPartStructure)
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
            self._usage_link_nav = None

        # Alle Navigation-Properties durchprobieren
        for nav in ["Uses", "RoleBObject", "Child"]:
            child = self._resolve_link_via_nav(link_id, nav)
            if child:
                self._usage_link_nav = nav
                return child

        return None

    def _resolve_link_via_nav(self: "WRSClientBase", link_id: str, nav: str) -> Optional[dict]:
        """Hilfsmethode: Kind-Part ueber ein bestimmtes Navigation-Property laden."""
        url = f"{self._odata_url('ProdMgmt')}/UsageLinks('{link_id}')/{nav}"
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
