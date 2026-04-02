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

    # ── Part Subtypes (Soft Types) ──────────────────────────

    def get_part_subtypes(self: "WRSClientBase") -> list[dict]:
        """Verfuegbare Part-Subtypes aus bestehenden Parts ermitteln.

        Laedt eine Stichprobe existierender Parts und sammelt die
        distinct ``@odata.type``-Werte. Diese sind immer in der
        OData-Response enthalten (z.B. ``#PTC.ProdMgmt.BALMECHATRONICPART``).

        Returns:
            Liste von Dicts: [{"name": "BALMECHATRONICPART",
                               "odataType": "PTC.ProdMgmt.BALMECHATRONICPART"}, ...]
        """
        url = f"{self.odata_base}/ProdMgmt/Parts"
        params = {"$select": "Number", "$top": "200"}

        try:
            items = self._get_all_pages(url, params, return_none_on_error=True)
            if not items:
                logger.warning("get_part_subtypes: Keine Parts geladen")
                return []
        except Exception:
            logger.warning("get_part_subtypes request failed", exc_info=True)
            return []

        # Distinct @odata.type sammeln
        type_set: set[str] = set()
        for item in items:
            odata_type = item.get("@odata.type", "")
            if odata_type:
                type_set.add(odata_type)

        subtypes: list[dict] = []
        for raw_type in sorted(type_set):
            # "#PTC.ProdMgmt.BALMECHATRONICPART" → name="BALMECHATRONICPART", odataType="PTC.ProdMgmt.BALMECHATRONICPART"
            clean = raw_type.lstrip("#")
            name = clean.rsplit(".", 1)[-1] if "." in clean else clean
            subtypes.append({"name": name, "odataType": clean})

        logger.info("Found %d Part subtypes from %d parts: %s",
                    len(subtypes), len(items),
                    [s["name"] for s in subtypes])
        return subtypes

    # ── Classification Nodes ─────────────────────────────────

    def get_classification_nodes(self: "WRSClientBase") -> list[dict]:
        """Classification-Knoten aus ClfStructure/ClfNodes laden.

        Die ClfStructure-API ist hierarchisch: der Wurzelaufruf liefert
        nur Root-Knoten. Kinder muessen ueber ``$expand=Children``
        oder rekursive Navigation geladen werden.

        Versucht mehrere URL-Varianten (versioniert + unversioniert),
        da ClfStructure bei manchen Windchill-Konfigurationen nur
        ohne OData-Version erreichbar ist.

        Returns:
            Flache Liste aller ClfNode-Dicts (OData raw).
        """
        base_urls = [
            f"{self.base_url}/servlet/odata/ClfStructure/ClfNodes",
            f"{self.odata_base}/ClfStructure/ClfNodes",
            f"{self.base_url}/servlet/odata/v4/ClfStructure/ClfNodes",
        ]

        root_items: list[dict] = []
        working_base: str = ""

        # ── Schritt 1: Root-Knoten laden (mit $expand=Children versuch) ──
        for base in base_urls:
            logger.info("Trying ClfNodes at: %s", base)
            try:
                # Versuch mit $expand=Children($levels=max) — liefert ggf. den ganzen Baum
                resp = self._raw_get(base, params={"$expand": "Children($levels=max)"}, timeout=30)
                logger.info("ClfNodes %s ($expand) → HTTP %d", base, resp.status_code)
                if resp.status_code == 200:
                    data = resp.json()
                    root_items = data.get("value", [])
                    working_base = base
                    break

                # Fallback: ohne $expand
                resp = self._raw_get(base, timeout=15)
                logger.info("ClfNodes %s (plain) → HTTP %d", base, resp.status_code)
                if resp.status_code == 200:
                    data = resp.json()
                    root_items = data.get("value", [])
                    working_base = base
                    break
            except Exception:
                logger.info("ClfNodes failed at %s", base, exc_info=True)
                continue

        if not root_items:
            logger.warning("ClfStructure/ClfNodes: Keine der URLs war erfolgreich")
            return []

        logger.info("ClfNodes root: %d items from %s", len(root_items), working_base)

        # ── Schritt 2: Baum flach machen ──
        all_nodes: list[dict] = []
        self._flatten_clf_tree(all_nodes, root_items, working_base)
        logger.info("ClfNodes total (flat): %d Knoten", len(all_nodes))
        if all_nodes:
            logger.info("ClfNode sample keys: %s", list(all_nodes[0].keys()))
            for i, node in enumerate(all_nodes[:5]):
                logger.info("ClfNode[%d]: %s", i, {k: v for k, v in node.items()
                            if k not in ("@odata.type", "@odata.id", "@odata.editLink",
                                         "Children", "ClfNodeAttributes")})
        return all_nodes

    def _flatten_clf_tree(
        self: "WRSClientBase",
        result: list[dict],
        nodes: list[dict],
        working_base: str,
        depth: int = 0,
    ) -> None:
        """Rekursiv ClfNode-Baum flach machen.

        Wenn ``Children`` schon inline sind ($expand hat funktioniert),
        werden sie direkt verarbeitet. Sonst werden Children pro Knoten
        via Navigation-Property nachgeladen.
        """
        if depth > 20:  # Schutz gegen Endlosrekursion
            return
        for node in nodes:
            result.append(node)
            children = node.get("Children")

            if isinstance(children, list) and children:
                # Children waren inline ($expand hat funktioniert)
                self._flatten_clf_tree(result, children, working_base, depth + 1)
            elif children is None or (isinstance(children, list) and not children):
                # Kein $expand oder Blattknoten — versuche Navigation nachladen
                internal = node.get("InternalName") or node.get("ID") or ""
                if not internal:
                    continue
                # Nur nachladen wenn kein Blattknoten
                if node.get("Instantiable") is True and not node.get("Children"):
                    continue  # Blattknoten ohne Kinder — ueberspringen

                child_url = f"{working_base}('{internal}')/Children"
                try:
                    resp = self._raw_get(child_url, timeout=15)
                    if resp.status_code == 200:
                        child_data = resp.json().get("value", [])
                        if child_data:
                            logger.debug("ClfNode '%s' → %d children", internal, len(child_data))
                            self._flatten_clf_tree(result, child_data, working_base, depth + 1)
                except Exception:
                    logger.debug("ClfNode children load failed for '%s'", internal, exc_info=True)

    # ── Container-Liste ──────────────────────────────────────

    def get_containers(self: "WRSClientBase") -> list[dict]:
        """Windchill Container (Products/Libraries) auflisten.

        ``Containers`` ist ein Entity Set der **DataAdmin**-Domain,
        nicht der ProdMgmt-Domain. Ermittelt via:
        ``GET /servlet/odata/v6/DataAdmin/Containers``

        Versucht verschiedene Strategien um nur Product-Container
        zu laden und das Paginieren von 1000+ Containern zu vermeiden:
          1. OData Type-Cast: /Containers/PTC.DataAdmin.PDMLinkProduct
          2. $filter auf @odata.type
          3. Ungefiltert mit $select um Payload zu reduzieren

        Returns:
            Liste von Container-Dicts mit ID, Name, @odata.type etc.
        """
        url = f"{self.odata_base}/DataAdmin/Containers"

        # Strategie 1: OData Type-Cast (nur Product-Container)
        type_cast_url = f"{url}/PTC.DataAdmin.PDMLinkProduct"
        items = self._get_all_pages(type_cast_url, {}, return_none_on_error=True)
        if items:
            logger.info("Container type-cast lieferte %d Product-Container", len(items))
            return items

        # Strategie 2: $filter auf ContainerType
        items = self._get_all_pages(
            url, {"$filter": "ContainerType eq 'Product'"}, return_none_on_error=True
        )
        if items:
            logger.info("Container $filter lieferte %d Container", len(items))
            return items

        # Strategie 3: Ungefiltert aber mit $select um Payload zu reduzieren
        logger.info("Container-Filter fehlgeschlagen – lade alle mit $select")
        items = self._get_all_pages(url, {"$select": "ID,Name"})

        if items is None:
            return []
        return items
