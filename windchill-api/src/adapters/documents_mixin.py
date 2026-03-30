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

    def get_referenced_by_documents(
        self: "WRSClientBase",
        part_id: str,
        exclude_ids: set[str] | None = None,
    ) -> list:
        """Dokumente laden, die dieses Part per References-Navigation referenzieren.

        Anders als ``get_described_documents`` (DescribedBy) liefert dies die
        umgekehrte Richtung: Dokumente, die das Part in ihrer References-Liste
        haben.  Wird als eigene Kategorie im Export gefuehrt.

        Args:
            part_id: OData-ID des Parts.
            exclude_ids: Bereits bekannte Dokument-IDs (z.B. aus DescribedBy),
                         die hier nicht nochmal aufgefuehrt werden sollen.
        """
        if exclude_ids is None:
            exclude_ids = set()

        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/References"
        items = self._get_all_pages(url, return_none_on_error=True)
        if not items:
            return []

        result: list[dict] = []
        seen: set[str] = set()
        for item in items:
            doc_id = item.get("ID", "")
            if doc_id and doc_id not in seen and doc_id not in exclude_ids:
                seen.add(doc_id)
                result.append(item)
        return result
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
        # CADDocumentMgmt only exists in v4
        if service == "CADDocumentMgmt":
            odata_base = f"{self.base_url}/servlet/odata/v4"
        else:
            odata_base = self.odata_base

        results: list[dict] = []
        seen: set[str] = set()

        # Try verschiedene Nav-Properties
        nav_props = ["Describes", "DescribesObjects", "DescribedByParts", "AssociatedParts"]
        for nav in nav_props:
            url = f"{odata_base}/{service}/{entity_set}('{doc_id}')/{nav}"
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
        # CADDocumentMgmt only exists in v4
        if service == "CADDocumentMgmt":
            odata_base = f"{self.base_url}/servlet/odata/v4"
        else:
            odata_base = self.odata_base

        results: list[dict] = []
        seen: set[str] = set()

        # Strategie 1: ContentHolders (gibt alle Dateien)
        nav_props = ["ContentHolders", "PrimaryContent", "Attachments", "ContentItems"]
        for nav in nav_props:
            url = f"{odata_base}/{service}/{entity_set}('{doc_id}')/{nav}"
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

    def download_document_content(
        self: "WRSClientBase",
        service: str,
        entity_set: str,
        doc_id: str,
        file_id: str = "",
    ) -> tuple[bytes, str, str]:
        """Datei-Inhalt aus dem Windchill Vault herunterladen.

        Mehrere Strategien:
          1. ContentHolders('file_id')/$value  (direkt per Content-ID)
          2. PrimaryContent/$value             (Hauptdatei)
          3. Content/$value                    (Generisch)

        Returns:
            Tuple (content_bytes, filename, content_type).

        Raises:
            WRSError 404 wenn kein Content vorhanden.
        """
        from src.adapters.base import WRSError

        # CADDocumentMgmt only exists in v4
        if service == "CADDocumentMgmt":
            odata_base = f"{self.base_url}/servlet/odata/v4"
        else:
            odata_base = self.odata_base

        urls: list[str] = []
        if file_id:
            urls.append(
                f"{odata_base}/{service}/{entity_set}('{doc_id}')"
                f"/ContentHolders('{file_id}')/$value"
            )
        urls.extend([
            f"{odata_base}/{service}/{entity_set}('{doc_id}')/PrimaryContent/$value",
            f"{odata_base}/{service}/{entity_set}('{doc_id}')/Content/$value",
            f"{odata_base}/{service}/{entity_set}('{doc_id}')/$value",
        ])

        for url in urls:
            resp = self._get(url, suppress_errors=True)
            if resp and resp.status_code == 200:
                ct = resp.headers.get("content-type", "application/octet-stream")
                # Dateinamen aus Content-Disposition extrahieren
                disp = resp.headers.get("content-disposition", "")
                filename = ""
                if "filename=" in disp:
                    parts = disp.split("filename=")
                    if len(parts) > 1:
                        filename = parts[1].strip().strip('"').strip("'")
                if not filename:
                    filename = f"download_{doc_id}"
                return resp.content, filename, ct

        raise WRSError(
            f"Kein downloadbarer Content fuer {entity_set}('{doc_id}')",
            status_code=404,
        )