"""
Business logic: Dokument-Details (referenzierende Parts, Datei-Info).

Service-Schicht zwischen Router und Adapter. Normalisiert OData-Rohdaten
zu typisierten DTOs.
"""

import logging
import time

from src.adapters.wrs_client import WRSClient
from src.core.odata import extract_id, normalize_item
from src.models.dto import (
    FileInfo,
    FileInfoResponse,
    ReferencingPart,
    ReferencingPartsResponse,
    TimingInfo,
)

logger = logging.getLogger(__name__)

# Mapping: type_key → (OData service section, entity set)
_DOC_ENTITIES: dict[str, tuple[str, str]] = {
    "document":     ("DocMgmt",         "Documents"),
    "cad_document": ("CADDocumentMgmt", "CADDocuments"),
}


def get_referencing_parts(
    client: WRSClient,
    type_key: str,
    code: str,
) -> ReferencingPartsResponse:
    """Welche Parts verweisen auf dieses Dokument?"""
    from src.adapters.base import WRSError

    if type_key not in _DOC_ENTITIES:
        raise WRSError(f"Kein Dokument-Typ: '{type_key}'", status_code=400)

    t0 = time.monotonic()

    # Erst das Dokument finden
    raw_doc = client.find_object(type_key, code)
    doc_id = extract_id(raw_doc)
    if not doc_id:
        raise WRSError(f"Keine ID fuer {type_key} '{code}'", status_code=404)

    service, entity_set = _DOC_ENTITIES[type_key]
    raw_parts = client.get_document_referencing_parts(service, entity_set, doc_id)

    parts = [_to_referencing_part(raw) for raw in raw_parts]
    ms = round((time.monotonic() - t0) * 1000, 1)

    return ReferencingPartsResponse(
        code=code,
        totalFound=len(parts),
        parts=parts,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def get_document_files(
    client: WRSClient,
    type_key: str,
    code: str,
) -> FileInfoResponse:
    """Datei-Info (ContentHolders) eines Dokuments laden."""
    from src.adapters.base import WRSError

    if type_key not in _DOC_ENTITIES:
        raise WRSError(f"Kein Dokument-Typ: '{type_key}'", status_code=400)

    t0 = time.monotonic()

    raw_doc = client.find_object(type_key, code)
    doc_id = extract_id(raw_doc)
    if not doc_id:
        raise WRSError(f"Keine ID fuer {type_key} '{code}'", status_code=404)

    service, entity_set = _DOC_ENTITIES[type_key]
    raw_files = client.get_document_content_info(service, entity_set, doc_id)

    files = [_to_file_info(raw) for raw in raw_files]
    ms = round((time.monotonic() - t0) * 1000, 1)

    return FileInfoResponse(
        code=code,
        totalFound=len(files),
        files=files,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def _to_referencing_part(raw: dict) -> ReferencingPart:
    """Normalize a raw OData dict to a ReferencingPart DTO."""
    n = normalize_item(raw)
    return ReferencingPart(
        partId=n["id"],
        number=n["number"],
        name=n["name"],
        version=n["version"],
        iteration=n["iteration"],
        state=n["state"],
        identity=n["identity"],
    )


def _to_file_info(raw: dict) -> FileInfo:
    """Normalize a raw OData dict to a FileInfo DTO."""
    file_id = extract_id(raw) or str(raw.get("ContentId", ""))
    file_name = str(
        raw.get("FileName") or raw.get("Name") or raw.get("DisplayName") or ""
    )
    file_size = str(raw.get("FileSize") or raw.get("ContentLength") or "")
    mime_type = str(
        raw.get("FormatName") or raw.get("MimeType") or raw.get("ContentType") or ""
    )
    role = str(raw.get("Role") or raw.get("ContentRole") or "")
    created = str(raw.get("CreatedOn") or raw.get("CreateTimestamp") or "")
    modified = str(raw.get("LastModified") or raw.get("ModifyTimestamp") or "")

    return FileInfo(
        fileId=file_id,
        fileName=file_name,
        fileSize=file_size,
        mimeType=mime_type,
        role=role,
        created=created,
        modified=modified,
    )


def download_file(
    client: WRSClient,
    type_key: str,
    code: str,
) -> tuple[bytes, str, str]:
    """Primaerdatei eines Dokuments herunterladen.

    Returns:
        (content_bytes, filename, content_type)
    """
    from src.adapters.base import WRSError

    if type_key not in _DOC_ENTITIES:
        raise WRSError(f"Kein Dokument-Typ: '{type_key}'", status_code=400)

    raw_doc = client.find_object(type_key, code)
    doc_id = extract_id(raw_doc)
    if not doc_id:
        raise WRSError(f"Keine ID fuer {type_key} '{code}'", status_code=404)

    service, entity_set = _DOC_ENTITIES[type_key]
    return client.download_document_content(service, entity_set, doc_id)
