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
        url = f"{self._odata_url('ProdMgmt')}/Parts('{part_id}')/DescribedBy"
        _collect(self._get_all_pages(url, return_none_on_error=True))

        # Quelle 2: DocMgmt mit Balluff-spezifischem Filter
        if part_number and self._doc_service_available:
            safe = part_number.replace("'", "''")
            url = f"{self._odata_url('DocMgmt')}/Documents"
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
            url = f"{self._odata_url('ProdMgmt')}/Parts('{part_id}')/References"
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
        url = f"{self._odata_url('ProdMgmt')}/Parts('{part_id}')/PartDocAssociations"
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
            url = f"{self._odata_url('ProdMgmt')}/Parts('{part_id}')/Representations"
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

        url = f"{self._odata_url('ProdMgmt')}/Parts('{part_id}')/References"
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
        # Domain-spezifische URL verwenden
        odata_base = self._odata_url(service)

        results: list[dict] = []
        seen: set[str] = set()

        # Try verschiedene Nav-Properties
        nav_props = ["Describes", "DescribesObjects", "DescribedByParts", "AssociatedParts"]
        for nav in nav_props:
            url = f"{odata_base}/{entity_set}('{doc_id}')/{nav}"
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
        # Domain-spezifische URL verwenden
        odata_base = self._odata_url(service)

        results: list[dict] = []
        seen: set[str] = set()

        # Strategie 1: ContentHolders (gibt alle Dateien)
        nav_props = ["ContentHolders", "PrimaryContent", "Attachments", "ContentItems"]
        for nav in nav_props:
            url = f"{odata_base}/{entity_set}('{doc_id}')/{nav}"
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

        # Domain-spezifische URL verwenden
        odata_base = self._odata_url(service)

        urls: list[str] = []
        if file_id:
            urls.append(
                f"{odata_base}/{entity_set}('{doc_id}')"
                f"/ContentHolders('{file_id}')/$value"
            )
        urls.extend([
            f"{odata_base}/{entity_set}('{doc_id}')/PrimaryContent/$value",
            f"{odata_base}/{entity_set}('{doc_id}')/Content/$value",
            f"{odata_base}/{entity_set}('{doc_id}')/$value",
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

    # ── CAD Structure (Assembly) ─────────────────────────────

    def get_cad_structure(
        self: "WRSClientBase",
        cad_doc_id: str,
        *,
        recursive: bool = True,
        _level: int = 1,
        _seen: set | None = None,
    ) -> list[dict]:
        """CAD-Struktur (Assembly-Baum) eines CAD-Dokuments laden.

        Zweischritt-Ansatz:
          1. GET /CADDocuments('{id}')/Uses  → Usage-Links (Quantity, DepType, FileName)
          2. GET /CADDocuments?$filter=...   → Child-Details (Number, Version, State)
        Ergebnis wird gemergt und bei ``recursive=True`` rekursiv aufgeloest.

        Returns:
            Flache Liste von Dicts mit allen Feldern (level, fileName, number,
            version, state, quantity, dependencyType, hasChildren, cadDocId).
        """
        if _seen is None:
            _seen = set()

        # Schritt 1: Usage-Links laden
        base = self._odata_url("CADDocumentMgmt")
        uses_url = f"{base}/CADDocuments('{cad_doc_id}')/Uses"
        uses = self._get_all_pages(uses_url, return_none_on_error=True)
        if not uses:
            logger.debug("Uses lieferte keine Eintraege fuer %s", cad_doc_id)
            return []

        # ComponentName / UseInfo.FileName sammeln
        file_names: list[str] = []
        uses_by_file: dict[str, dict] = {}
        for u in uses:
            fn = (
                u.get("ComponentName")
                or (u.get("UseInfo") or {}).get("FileName")
                or ""
            )
            if fn:
                file_names.append(fn)
                uses_by_file[fn] = u

        # Schritt 2: Child-CADDocuments per Batch-Filter aufloesen
        child_docs_by_file: dict[str, dict] = {}
        if file_names:
            child_docs_by_file = self._resolve_cad_docs_by_filenames(file_names)

        # Zusammenfuehren
        result: list[dict] = []
        for fn in file_names:
            use = uses_by_file.get(fn, {})
            doc = child_docs_by_file.get(fn, {})

            dep_type_raw = use.get("DepType") or ""
            # DepType kann ein dict mit Value sein (PTC.EnumType)
            dep_type = dep_type_raw.get("Value", "") if isinstance(dep_type_raw, dict) else str(dep_type_raw)

            quantity = use.get("Quantity")
            quantity_str = str(int(quantity)) if isinstance(quantity, (int, float)) and quantity == int(quantity) else str(quantity or "1")

            # Version aus OData-Feldern
            version = str(doc.get("Version") or doc.get("VersionID") or "")
            # State (PTC.EnumType)
            state_raw = doc.get("State")
            state = state_raw.get("Value", "") if isinstance(state_raw, dict) else str(state_raw or "")

            child_id = str(doc.get("ID") or "")
            has_children = bool(doc.get("HasChildren", False))

            # HasChildren aus Uses pruefen: Kind hat selbst Uses?
            # Falls doc keinen HasChildren-Hint hat, merken wir die ID
            # und pruefen per Rekursion.

            node = {
                "level": _level,
                "fileName": fn,
                "number": str(doc.get("Number") or ""),
                "name": str(doc.get("Name") or ""),
                "version": version,
                "state": state,
                "quantity": quantity_str,
                "dependencyType": dep_type,
                "hasChildren": has_children,
                "cadDocId": child_id,
            }
            result.append(node)

            # Rekursiv Kinder laden
            if recursive and child_id and child_id not in _seen:
                _seen.add(child_id)
                children = self.get_cad_structure(
                    child_id,
                    recursive=True,
                    _level=_level + 1,
                    _seen=_seen,
                )
                result.extend(children)

        logger.debug(
            "Uses lieferte %d direkte Kinder (gesamt %d) fuer %s",
            len(file_names), len(result), cad_doc_id,
        )
        return result

    def _resolve_cad_docs_by_filenames(
        self: "WRSClientBase",
        file_names: list[str],
    ) -> dict[str, dict]:
        """CADDocuments per FileName-Filter batch-weise aufloesen.

        Teilt grosse Listen in Chunks auf (OData-URL-Laenge begrenzt).
        Returns: Mapping FileName → CADDocument-Dict
        """
        base = self._odata_url("CADDocumentMgmt")
        result: dict[str, dict] = {}
        chunk_size = 10  # Max 10 OR-Klauseln pro Request

        for i in range(0, len(file_names), chunk_size):
            chunk = file_names[i : i + chunk_size]
            clauses = [f"FileName eq '{fn.replace(chr(39), chr(39)*2)}'" for fn in chunk]
            filt = " or ".join(clauses)
            url = f"{base}/CADDocuments"
            items = self._get_all_pages(
                url,
                {"$filter": filt, "$select": "Number,Name,FileName,Version,State,ID"},
                return_none_on_error=True,
            )
            if items:
                # Nimm jeweils die neueste Version pro FileName
                from src.core.odata import version_sort_key
                for item in sorted(items, key=version_sort_key, reverse=True):
                    fn = str(item.get("FileName") or "")
                    if fn and fn not in result:
                        result[fn] = item

        return result