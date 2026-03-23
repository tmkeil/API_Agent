"""
WRS Client — Dokument-Operationen (Mixin).
============================================

Beschriebene Dokumente und CAD-Dokumente eines Parts laden.
Reverse-Navigation: Welche Parts verweisen auf dieses Dokument?
Datei-Info: ContentHolders eines Dokuments.
Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from src.core.odata import extract_id

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)


class DocumentsMixin:
    """Dokument-spezifische Operationen (Mixin fuer WRSClientBase)."""

    def get_described_documents(self: "WRSClientBase", part_id: str, part_number: str = "") -> list:
        """Dokumente laden, die mit einem Part verknuepft sind.

        Drei Quellen in Prioritaetsreihenfolge:
          1. DescribedBy-Navigation    (Standard-Verknuepfung Part → Dokument)
          2. DocMgmt + BALREFERENCEPART (firmenspezifischer Balluff-Filter)
          3. References-Navigation     (Fallback fuer aeltere WRS-Versionen)
        """
        all_docs: list[dict] = []
        seen: set[str] = set()

        def _collect(items: Optional[list]) -> None:
            if not items:
                return
            for item in items:
                doc_id = item.get("ID", "")
                if doc_id and doc_id not in seen:
                    seen.add(doc_id)
                    all_docs.append(item)

        # Quelle 1: DescribedBy
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/DescribedBy"
        _collect(self._get_all_pages(url, return_none_on_error=True))

        # Quelle 2: DocMgmt mit Balluff-spezifischem Filter
        if part_number and self._doc_service_available:
            safe = part_number.replace("'", "''")
            url = f"{self.odata_base}/DocMgmt/Documents"
            result = self._get_all_pages(
                url,
                {"$filter": f"BALREFERENCEPART/any(s:s eq '{safe}')"},
                return_none_on_error=True,
            )
            if result is not None:
                _collect(result)
            else:
                # DocMgmt-Service nicht verfuegbar → nicht nochmal versuchen
                self._doc_service_available = False

        # Quelle 3: Fallback — References
        if not all_docs:
            url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/References"
            _collect(self._get_all_pages(url, return_none_on_error=True))

        return all_docs

    def get_cad_documents(self: "WRSClientBase", part_id: str) -> list:
        """CAD-Dokumente (EPM/CAD) eines Parts laden.

        Zwei Quellen:
          1. PartDocAssociations + $expand=RelatedCADDoc (bevorzugt)
          2. Representations (Fallback)
        """
        all_cads: list[dict] = []
        seen: set[str] = set()

        # Quelle 1: PartDocAssociations mit inline-Expand
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/PartDocAssociations"
        result = self._get_all_pages(url, {"$expand": "RelatedCADDoc"}, return_none_on_error=True)
        if result:
            for assoc in result:
                cad = assoc.get("RelatedCADDoc") or {}
                cad_id = cad.get("ID", "")
                if cad_id and cad_id not in seen and (cad.get("Number") or cad.get("Name")):
                    seen.add(cad_id)
                    all_cads.append(cad)

        # Quelle 2: Fallback — Representations
        if not all_cads:
            url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/Representations"
            result = self._get_all_pages(url, return_none_on_error=True)
            if result:
                for cad in result:
                    cad_id = cad.get("ID", "")
                    if cad_id and cad_id not in seen:
                        seen.add(cad_id)
                        all_cads.append(cad)

        return all_cads
    # ── Reverse Navigation: Document → Parts ─────────────────

    def get_document_referencing_parts(
        self: "WRSClientBase",
        service: str,
        entity_set: str,
        doc_id: str,
    ) -> list[dict]:
        """Welche Parts verweisen auf dieses Dokument (Reverse-Navigation)?

        Mehrere Strategien:
          1. Describes / DescribesObjects Navigation
          2. DescribedByParts Navigation (CAD-Dokumente)
          3. AssociatedParts Navigation
        """
        results: list[dict] = []
        seen: set[str] = set()

        # Try verschiedene Nav-Properties
        nav_props = ["Describes", "DescribesObjects", "DescribedByParts", "AssociatedParts"]
        for nav in nav_props:
            url = f"{self.odata_base}/{service}/{entity_set}('{doc_id}')/{nav}"
            items = self._get_all_pages(url, return_none_on_error=True)
            if items:
                for item in items:
                    pid = extract_id(item)
                    if pid and pid not in seen:
                        seen.add(pid)
                        results.append(item)
                if results:
                    return results

        return results

    def get_document_content_info(
        self: "WRSClientBase",
        service: str,
        entity_set: str,
        doc_id: str,
    ) -> list[dict]:
        """Content/Datei-Info eines Dokuments laden.

        Mehrere Strategien:
          1. ContentHolders Navigation (Standard)
          2. PrimaryContent Navigation
          3. Attachments / ContentItems Fallback
        """
        results: list[dict] = []
        seen: set[str] = set()

        # Strategie 1: ContentHolders (gibt alle Dateien)
        nav_props = ["ContentHolders", "PrimaryContent", "Attachments", "ContentItems"]
        for nav in nav_props:
            url = f"{self.odata_base}/{service}/{entity_set}('{doc_id}')/{nav}"
            items = self._get_all_pages(url, return_none_on_error=True)
            if items:
                for item in items:
                    fid = extract_id(item) or item.get("FileName", "")
                    if fid and fid not in seen:
                        seen.add(fid)
                        results.append(item)
                if results:
                    return results

        return results