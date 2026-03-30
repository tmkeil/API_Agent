"""
WRS Client — Write-Operationen (Mixin).
=========================================

Schreibende Operationen gegen Windchill WRS OData:
  - Part erstellen
  - Attribute ändern (PATCH)
  - Lifecycle-Status setzen
  - Change-Objekte erstellen

Windchill WRS benötigt CSRF_NONCE fuer alle Schreiboperationen.
Der Nonce wird in base.py automatisch bei jedem Response aktualisiert.

Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from src.core.odata import extract_id, normalize_item

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)


class WriteMixin:
    """Schreibende Operationen (Mixin fuer WRSClientBase)."""

    # Mapping: type_key → (OData service, entity set)
    _WRITABLE_ENTITIES: dict[str, tuple[str, str]] = {
        "part":            ("ProdMgmt",        "Parts"),
        "document":        ("DocMgmt",         "Documents"),
        "cad_document":    ("CADDocumentMgmt", "CADDocuments"),
        "change_notice":   ("ChangeMgmt",      "ChangeNotices"),
        "change_request":  ("ChangeMgmt",      "ChangeRequests"),
        "problem_report":  ("ChangeMgmt",      "ProblemReports"),
    }

    def create_object(
        self: "WRSClientBase",
        type_key: str,
        attributes: dict[str, Any],
    ) -> dict:
        """Neues Windchill-Objekt erstellen via POST.

        Args:
            type_key: Typ-Schluessel (z.B. 'part', 'change_notice').
            attributes: OData-Properties, z.B. {"Number": "...", "Name": "..."}.

        Returns:
            Das erstellte Objekt als OData-Dict.

        Raises:
            WRSError: Bei Fehlern (400 Validation, 403 Permission, etc.)
        """
        from src.adapters.base import WRSError

        if type_key not in self._WRITABLE_ENTITIES:
            raise WRSError(f"Unbekannter Objekttyp: '{type_key}'", status_code=400)

        service, entity_set = self._WRITABLE_ENTITIES[type_key]
        # CADDocumentMgmt only exists in v4
        odata_base = f"{self.base_url}/servlet/odata/v4" if type_key == "cad_document" else self.odata_base
        url = f"{odata_base}/{service}/{entity_set}"

        resp = self._post(url, json_body=attributes)
        if resp is None:
            raise WRSError(f"Erstellen von {entity_set} fehlgeschlagen", status_code=502)

        if resp.status_code in (200, 201):
            return resp.json()

        # Windchill Fehler-Details extrahieren
        detail = _extract_error_detail(resp)
        raise WRSError(
            f"Erstellen fehlgeschlagen (HTTP {resp.status_code}): {detail}",
            status_code=resp.status_code,
        )

    def update_object_attributes(
        self: "WRSClientBase",
        type_key: str,
        obj_id: str,
        attributes: dict[str, Any],
    ) -> dict:
        """Attribute eines bestehenden Objekts aendern via PATCH.

        Args:
            type_key:   Typ-Schluessel.
            obj_id:     OData-ID des Objekts.
            attributes: Nur die zu aendernden Properties.

        Returns:
            Das aktualisierte Objekt als OData-Dict.
        """
        from src.adapters.base import WRSError

        if type_key not in self._WRITABLE_ENTITIES:
            raise WRSError(f"Unbekannter Objekttyp: '{type_key}'", status_code=400)

        service, entity_set = self._WRITABLE_ENTITIES[type_key]
        # CADDocumentMgmt only exists in v4
        odata_base = f"{self.base_url}/servlet/odata/v4" if type_key == "cad_document" else self.odata_base
        url = f"{odata_base}/{service}/{entity_set}('{obj_id}')"

        resp = self._patch(url, json_body=attributes)
        if resp is None:
            raise WRSError(f"Update von {entity_set}('{obj_id}') fehlgeschlagen", status_code=502)

        if resp.status_code in (200, 204):
            if resp.status_code == 204:
                # PATCH mit 204 → kein Body, Objekt neu laden
                return self._get_json(url)
            return resp.json()

        detail = _extract_error_detail(resp)
        raise WRSError(
            f"Update fehlgeschlagen (HTTP {resp.status_code}): {detail}",
            status_code=resp.status_code,
        )

    def set_lifecycle_state(
        self: "WRSClientBase",
        type_key: str,
        obj_id: str,
        target_state: str,
        comment: str = "",
    ) -> dict:
        """Lifecycle-Status eines Objekts aendern.

        Nutzt die OData Action PTC.ProdMgmt.SetLifeCycleState bzw.
        den aequivalenten Endpoint des jeweiligen Dienstes.

        Args:
            type_key:     Typ-Schluessel.
            obj_id:       OData-ID des Objekts.
            target_state: Ziel-Status (z.B. 'RELEASED', 'INWORK').
            comment:      Optionaler Kommentar fuer den Statuswechsel.
        """
        from src.adapters.base import WRSError

        if type_key not in self._WRITABLE_ENTITIES:
            raise WRSError(f"Unbekannter Objekttyp: '{type_key}'", status_code=400)

        service, entity_set = self._WRITABLE_ENTITIES[type_key]

        # CADDocumentMgmt only exists in v4
        odata_base = f"{self.base_url}/servlet/odata/v4" if type_key == "cad_document" else self.odata_base

        # Strategie 1: OData Action (Windchill 12+)
        action_url = (
            f"{odata_base}/{service}/{entity_set}('{obj_id}')"
            f"/PTC.{service}.SetLifeCycleState"
        )
        body: dict[str, Any] = {"State": target_state}
        if comment:
            body["Comment"] = comment

        resp = self._post(action_url, json_body=body, suppress_errors=True)
        if resp and resp.status_code in (200, 204):
            if resp.status_code == 200:
                try:
                    return resp.json()
                except Exception:
                    pass
            # Erfolg — Objekt neu laden
            obj_url = f"{odata_base}/{service}/{entity_set}('{obj_id}')"
            return self._get_json(obj_url)

        # Strategie 2: Generischer LifeCycleState Patch (Fallback)
        patch_url = f"{odata_base}/{service}/{entity_set}('{obj_id}')"
        state_body: dict[str, Any] = {"State": target_state}
        resp = self._patch(patch_url, json_body=state_body, suppress_errors=True)
        if resp and resp.status_code in (200, 204):
            if resp.status_code == 200:
                try:
                    return resp.json()
                except Exception:
                    pass
            return self._get_json(patch_url)

        # Fehler
        detail = _extract_error_detail(resp) if resp else "Keine Antwort"
        raise WRSError(
            f"Status-Wechsel fehlgeschlagen (→ {target_state}): {detail}",
            status_code=resp.status_code if resp else 502,
        )

    def checkout_object(
        self: "WRSClientBase",
        type_key: str,
        obj_id: str,
    ) -> dict:
        """Checkout (Auschecken) eines Objekts fuer Bearbeitung.

        Nutzt OData Action PTC.{service}.CheckOut.
        """
        from src.adapters.base import WRSError

        if type_key not in self._WRITABLE_ENTITIES:
            raise WRSError(f"Unbekannter Objekttyp: '{type_key}'", status_code=400)

        service, entity_set = self._WRITABLE_ENTITIES[type_key]
        # CADDocumentMgmt only exists in v4
        odata_base = f"{self.base_url}/servlet/odata/v4" if type_key == "cad_document" else self.odata_base
        url = f"{odata_base}/{service}/{entity_set}('{obj_id}')/PTC.{service}.CheckOut"

        resp = self._post(url, json_body={})
        if resp is None:
            raise WRSError("Checkout fehlgeschlagen", status_code=502)

        if resp.status_code in (200, 201):
            return resp.json()

        detail = _extract_error_detail(resp)
        raise WRSError(
            f"Checkout fehlgeschlagen (HTTP {resp.status_code}): {detail}",
            status_code=resp.status_code,
        )

    def checkin_object(
        self: "WRSClientBase",
        type_key: str,
        obj_id: str,
        comment: str = "",
    ) -> dict:
        """Checkin (Einchecken) eines ausgecheckten Objekts.

        Nutzt OData Action PTC.{service}.CheckIn.
        """
        from src.adapters.base import WRSError

        if type_key not in self._WRITABLE_ENTITIES:
            raise WRSError(f"Unbekannter Objekttyp: '{type_key}'", status_code=400)

        service, entity_set = self._WRITABLE_ENTITIES[type_key]
        # CADDocumentMgmt only exists in v4
        odata_base = f"{self.base_url}/servlet/odata/v4" if type_key == "cad_document" else self.odata_base
        url = f"{odata_base}/{service}/{entity_set}('{obj_id}')/PTC.{service}.CheckIn"

        body: dict[str, Any] = {}
        if comment:
            body["Comment"] = comment

        resp = self._post(url, json_body=body)
        if resp is None:
            raise WRSError("Checkin fehlgeschlagen", status_code=502)

        if resp.status_code in (200, 201):
            return resp.json()

        detail = _extract_error_detail(resp)
        raise WRSError(
            f"Checkin fehlgeschlagen (HTTP {resp.status_code}): {detail}",
            status_code=resp.status_code,
        )


    # ── Revise ───────────────────────────────────────────────

    def revise_object(
        self: "WRSClientBase",
        type_key: str,
        obj_id: str,
    ) -> dict:
        """Neue Revision eines Objekts erstellen.

        Nutzt OData Action PTC.{service}.Revise.
        Windchill erstellt eine neue Revision und gibt das neue Objekt zurueck.
        """
        from src.adapters.base import WRSError

        if type_key not in self._WRITABLE_ENTITIES:
            raise WRSError(f"Unbekannter Objekttyp: '{type_key}'", status_code=400)

        service, entity_set = self._WRITABLE_ENTITIES[type_key]
        odata_base = (
            f"{self.base_url}/servlet/odata/v4"
            if type_key == "cad_document"
            else self.odata_base
        )
        url = (
            f"{odata_base}/{service}/{entity_set}('{obj_id}')"
            f"/PTC.{service}.Revise"
        )

        resp = self._post(url, json_body={})
        if resp is None:
            raise WRSError("Revise fehlgeschlagen", status_code=502)

        if resp.status_code in (200, 201):
            return resp.json()

        detail = _extract_error_detail(resp)
        raise WRSError(
            f"Revise fehlgeschlagen (HTTP {resp.status_code}): {detail}",
            status_code=resp.status_code,
        )

    # ── BOM Usage Links (Kinder hinzufuegen / entfernen) ─────

    def add_bom_child(
        self: "WRSClientBase",
        parent_part_id: str,
        child_part_id: str,
        quantity: float = 1.0,
        unit: str = "each",
    ) -> dict:
        """Kind-Part ueber einen neuen UsageLink zur BOM hinzufuegen.

        Args:
            parent_part_id: OData-ID des Eltern-Parts.
            child_part_id:  OData-ID des Kind-Parts.
            quantity:       Menge (Default: 1).
            unit:           Mengeneinheit (Default: 'each').

        Returns:
            Der erstellte UsageLink als OData-Dict.
        """
        from src.adapters.base import WRSError

        url = f"{self.odata_base}/ProdMgmt/Parts('{parent_part_id}')/Uses"
        body: dict = {
            "Uses@odata.bind": f"Parts('{child_part_id}')",
            "Quantity": quantity,
            "Unit": unit,
        }

        resp = self._post(url, json_body=body)
        if resp is None:
            raise WRSError("BOM Kind hinzufuegen fehlgeschlagen", status_code=502)

        if resp.status_code in (200, 201):
            return resp.json()

        detail = _extract_error_detail(resp)
        raise WRSError(
            f"BOM Kind hinzufuegen fehlgeschlagen (HTTP {resp.status_code}): {detail}",
            status_code=resp.status_code,
        )

    def remove_bom_child(
        self: "WRSClientBase",
        usage_link_id: str,
    ) -> None:
        """Einen UsageLink (BOM-Kind-Beziehung) entfernen.

        Args:
            usage_link_id: OData-ID des UsageLinks.
        """
        from src.adapters.base import WRSError

        url = f"{self.odata_base}/ProdMgmt/UsageLinks('{usage_link_id}')"

        resp = self._delete(url)
        if resp is None:
            raise WRSError("BOM Kind entfernen fehlgeschlagen", status_code=502)

        if resp.status_code in (200, 204):
            return

        detail = _extract_error_detail(resp)
        raise WRSError(
            f"BOM Kind entfernen fehlgeschlagen (HTTP {resp.status_code}): {detail}",
            status_code=resp.status_code,
        )


def _extract_error_detail(resp) -> str:
    """Windchill-OData-Fehlermeldung aus der Response extrahieren."""
    try:
        data = resp.json()
        err = data.get("error", {})
        msg = err.get("message", "")
        if isinstance(msg, dict):
            msg = msg.get("value", str(msg))
        return str(msg) if msg else f"HTTP {resp.status_code}"
    except Exception:
        return f"HTTP {resp.status_code}"
