"""
WRS Client — BOM Transformation (Mixin).
=========================================

Wrappers fuer die OData v3 ``BomTransformation``-Domain (PTC Standard).

Auf welchen Systemen verfuegbar:
  * plm-dev  — Domain ist deployt, alle Actions nutzbar.
  * plm-prod — Domain ist NICHT deployt (404 auf $metadata).

Alle Methoden geben dem Aufrufer rohe OData-Antworten zurueck.
``WRSError`` wird bei nicht-2xx-Responses gehoben.

Quellen:
  - service_endpoints/PTC.BOMTransformation.json (Swagger v3)
  - service_endpoints/definitions.json
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)

# OData base path for the BomTransformation domain. v3 ist auf plm-dev der
# einzige bekannte deployte Major-Version (Swagger schreibt v3 fest).
_BT_BASE_PATH = "/servlet/odata/v3/BomTransformation"


class BomTransformationMixin:
    """Bound to ``WRSClient`` via Mehrfachvererbung."""

    # ── Helpers ──────────────────────────────────────────────

    def _bt_url(self: "WRSClientBase", action: str) -> str:
        """Liefert die volle URL fuer eine BomTransformation-Action."""
        return f"{self.base_url}{_BT_BASE_PATH}/{action.lstrip('/')}"

    def _bt_post(
        self: "WRSClientBase",
        action: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """POST gegen eine unbound BomTransformation-Action.

        Hebt ``WRSError`` bei Fehlern. Liefert das geparste JSON oder ``{}``
        bei 204 No Content.
        """
        from src.adapters.base import WRSError
        from src.adapters.write_mixin import _extract_error_detail  # type: ignore

        url = self._bt_url(action)
        self._refresh_csrf()
        resp = self._post(url, json_body=body, suppress_errors=True)
        if resp is None:
            raise WRSError(
                f"BomTransformation/{action}: keine Antwort", status_code=502
            )
        if resp.status_code == 404:
            raise WRSError(
                f"BomTransformation/{action}: nicht deployt auf diesem Windchill (404). "
                "Diese Domain ist nur auf dev verfuegbar.",
                status_code=404,
            )
        if resp.status_code in (200, 201):
            try:
                return resp.json()
            except Exception:
                return {}
        if resp.status_code == 204:
            return {}
        detail = _extract_error_detail(resp)
        raise WRSError(
            f"BomTransformation/{action} fehlgeschlagen (HTTP {resp.status_code}): {detail}",
            status_code=resp.status_code,
        )

    # ── Actions (unbound) ────────────────────────────────────

    def detect_discrepancies(
        self: "WRSClientBase",
        source_root: str,
        source_part_paths: list[str] | None = None,
        upstream_change_oid: str | None = None,
    ) -> dict[str, Any]:
        """``POST /BomTransformation/DetectDiscrepancies``.

        Findet Discrepancies zwischen Upstream- und Downstream-Struktur,
        ausgehend vom Upstream-Root-Part ``source_root``.

        Args:
            source_root: OID des EBOM-Root-Parts (Pflicht laut wt_down.md /
                DetectAndResolveDiscrepancies-Schema, das auf Detect übertragbar
                ist — der Server lehnt den Call sonst mit
                ``"SourceRoot param is required"`` ab).
            source_part_paths: Optionale Einschraenkung auf bestimmte
                EBOM-Knoten (Liste von Windchill-Pfaden).
            upstream_change_oid: Optionaler Change-Kontext fuer den Upstream.

        Returns:
            Rohes OData-JSON. Schluessel ``value`` enthaelt die Discrepancies
            als ``PTC.BomTransformation.DiscrepancyItem``-Eintraege.
        """
        body: dict[str, Any] = {
            "DiscrepancyContext": _build_discrepancy_context(
                target_path="",
                source_part_paths=source_part_paths,
                upstream_change_oid=upstream_change_oid,
                source_root=source_root,
            ),
        }
        return self._bt_post("DetectDiscrepancies", body)

    def detect_and_resolve_discrepancies(
        self: "WRSClientBase",
        target_path: str,
        source_part_paths: list[str] | None = None,
        upstream_change_oid: str | None = None,
        change_oid: str | None = None,
    ) -> dict[str, Any]:
        """``POST /BomTransformation/DetectAndResolveDiscrepancies``."""
        body: dict[str, Any] = {
            "DiscrepancyContext": _build_discrepancy_context(
                target_path, source_part_paths, upstream_change_oid
            ),
        }
        if change_oid:
            body["ChangeOid"] = change_oid
        return self._bt_post("DetectAndResolveDiscrepancies", body)

    def generate_downstream_structure(
        self: "WRSClientBase",
        target_path: str,
        source_part_paths: list[str],
        upstream_change_oid: str | None = None,
        change_oid: str | None = None,
    ) -> dict[str, Any]:
        """``POST /BomTransformation/GenerateDownstreamStructure``.

        Erzeugt die Downstream-Struktur (MBOM-Pendants + Equivalence-Links)
        fuer die in ``source_part_paths`` angegebenen EBOM-Knoten.

        Args:
            target_path: Windchill-Pfad zum Manufacturing-Root.
            source_part_paths: Liste der zu transformierenden EBOM-Knoten-Pfade.
            upstream_change_oid: Optionaler Change-Kontext fuer den Upstream.
            change_oid: Optionale Change Notice / Change Task fuer das
                Resultat (entspricht dem Windchill-Standardprozess fuer
                released Parts).

        Returns:
            Rohes OData-JSON. ``value`` enthaelt
            ``EquivalentUsageAssociation``-Eintraege mit den neuen
            Downstream-Parts und ihren Equivalence-Links.
        """
        body: dict[str, Any] = {
            "DiscrepancyContext": _build_discrepancy_context(
                target_path, source_part_paths, upstream_change_oid
            ),
        }
        if change_oid:
            body["ChangeOid"] = change_oid
        return self._bt_post("GenerateDownstreamStructure", body)

    def update_to_current_upstream_equivalents(
        self: "WRSClientBase",
        target_path: str,
        source_part_paths: list[str] | None = None,
        upstream_change_oid: str | None = None,
        change_oid: str | None = None,
    ) -> dict[str, Any]:
        """``POST /BomTransformation/UpdateToCurrentUpstreamEquivalents``."""
        body: dict[str, Any] = {
            "DiscrepancyContext": _build_discrepancy_context(
                target_path, source_part_paths, upstream_change_oid
            ),
        }
        if change_oid:
            body["ChangeOid"] = change_oid
        return self._bt_post("UpdateToCurrentUpstreamEquivalents", body)

    def paste_special(
        self: "WRSClientBase",
        target_path: str,
        source_part_paths: list[str],
        upstream_change_oid: str | None = None,
        change_oid: str | None = None,
    ) -> dict[str, Any]:
        """``POST /BomTransformation/PasteSpecial``.

        Per-Knoten COPY: nimmt die in ``source_part_paths`` angegebenen
        EBOM-Knoten und fuegt sie als neue Downstream-Equivalents unter
        ``target_path`` (MBOM-Knoten) ein. Dies ist die OData-Entsprechung
        des Drag&Drop-Vorgangs in der Windchill-GUI.

        Args:
            target_path: Windchill-Pfad zum Ziel-MBOM-Knoten (Eltern).
            source_part_paths: Liste der EBOM-Knoten-Pfade, die kopiert
                werden sollen.
            upstream_change_oid: Optionaler Change-Kontext fuer den Upstream.
            change_oid: Optionale Change Notice / Change Task.

        Returns:
            Rohes OData-JSON. ``value`` enthaelt
            ``EquivalentUsageAssociation``-Eintraege.
        """
        body: dict[str, Any] = {
            "DiscrepancyContext": _build_discrepancy_context(
                target_path, source_part_paths, upstream_change_oid
            ),
        }
        if change_oid:
            body["ChangeOid"] = change_oid
        return self._bt_post("PasteSpecial", body)

    def get_equivalence_network_for_parts(
        self: "WRSClientBase",
        part_ids: list[str],
    ) -> dict[str, Any]:
        """``POST /BomTransformation/GetEquivalenceNetworkForParts``.

        Liefert das Equivalence-Netzwerk fuer eine Liste von Part-IDs.
        """
        body = {"Parts": [{"ID": pid} for pid in part_ids]}
        return self._bt_post("GetEquivalenceNetworkForParts", body)


# ── Module-level helpers ─────────────────────────────────────


def _build_discrepancy_context(
    target_path: str,
    source_part_paths: list[str] | None,
    upstream_change_oid: str | None,
    source_root: str | None = None,
    target_root: str | None = None,
) -> dict[str, Any]:
    """Baut den ``PTC.BomTransformation.DiscrepancyContext``-Body.

    Vollständiges Schema laut Windchill REST Services Domain Capabilities
    (wt_down.md, DetectAndResolveDiscrepancies / GenerateDownstreamStructure):

        {
          "SourceRoot": str,                 # OID des Upstream-Root-Parts (Pflicht
                                              # für Detect / Generate / DetectAndResolve)
          "TargetRoot": str,                 # OID des Downstream-Root-Parts
          "TargetPart": str,                 # OID des Downstream-Parents (alt. zu TargetPath)
          "TargetPath": str,                 # Path-String — bei Detect verboten
                                              # ("TargetPath should not be included.")
          "SourcePartSelection": [ { "Path": str }, ... ],
          "UpstreamChangeOid": str
        }

    Die in ``definitions.json`` veröffentlichte Form ist unvollständig
    (es fehlen ``SourceRoot``, ``TargetRoot``, ``TargetPart``).
    ``wt_down.md`` aus der Windchill-Helpcenter-Doku ist maßgeblich.
    """
    ctx: dict[str, Any] = {}
    if source_root:
        # SourceRoot ist im EDM eine Navigation-Property auf ObjectReferenceable.
        # Das Java-Backend von BomTransformation erwartet jedoch intern eine
        # ``wt.fc.ObjectReference`` (Leichtgewicht-Reference), keine voll
        # materialisierte WTPart-Entity. Mit Inline-Object ``{"ID": ...}`` oder
        # einfachem String resolved Windchill ueber die Parts-EntitySet zu einer
        # WTPart-Entity, was zu einem ClassCastException fuehrt:
        #   "class wt.part.WTPart cannot be cast to class wt.fc.ObjectReference"
        # Der OData-v4-konforme Weg, eine reine Reference (nicht Entity) zu
        # uebergeben, ist die ``@odata.bind``-Annotation am Property-Namen:
        ctx["SourceRoot@odata.bind"] = f"Parts('{source_root}')"
    if target_root:
        ctx["TargetRoot@odata.bind"] = f"Parts('{target_root}')"
    if target_path:
        ctx["TargetPath"] = target_path
    if source_part_paths:
        ctx["SourcePartSelection"] = [{"Path": p} for p in source_part_paths]
    if upstream_change_oid:
        ctx["UpstreamChangeOid"] = upstream_change_oid
    return ctx
