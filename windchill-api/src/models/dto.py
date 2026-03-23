"""
DTOs (Data Transfer Objects) for the Windchill API.
Decouples the external API response from WRS internals.
"""

from typing import Any, Optional

from pydantic import BaseModel


class TimingInfo(BaseModel):
    totalMs: float = 0
    wrsMs: float = 0
    cacheHits: int = 0
    fromCache: bool = False


# ── Part ─────────────────────────────────────────────────────


class PartDetail(BaseModel):
    partId: str = ""
    number: str = ""
    name: str = ""
    version: str = ""
    iteration: str = ""
    state: str = ""
    identity: str = ""


class PartDetailResponse(BaseModel):
    part: PartDetail
    timing: TimingInfo


# ── Generic Object Detail ────────────────────────────────────


class ObjectDetail(BaseModel):
    """Generic detail for any Windchill object type."""
    objectId: str = ""
    objectType: str = ""       # WTPart, WTDocument, EPMDocument, ...
    typeKey: str = ""          # part, document, cad_document, ...
    number: str = ""
    name: str = ""
    version: str = ""
    iteration: str = ""
    state: str = ""
    identity: str = ""
    context: str = ""
    lastModified: str = ""
    createdOn: str = ""


class ObjectDetailResponse(BaseModel):
    detail: ObjectDetail
    timing: TimingInfo


class PartSearchResult(BaseModel):
    partId: str = ""
    objectType: str = "WTPart"
    number: str = ""
    name: str = ""
    version: str = ""
    iteration: str = ""
    state: str = ""
    identity: str = ""
    context: str = ""
    lastModified: str = ""
    createdOn: str = ""


# ── BOM Tree (lazy expand) ──────────────────────────────────


class BomTreeNode(BaseModel):
    partId: str = ""
    type: str = "WTPart"
    number: str = ""
    name: str = ""
    version: str = ""
    iteration: str = ""
    state: str = ""
    identity: str = ""
    hasChildren: bool = False
    quantity: Any = None
    quantityUnit: str = ""
    lineNumber: str = ""


class DocumentNode(BaseModel):
    docId: str = ""
    type: str = "WTDocument"
    number: str = ""
    name: str = ""
    version: str = ""
    state: str = ""


class BomNodeResponse(BaseModel):
    children: list[BomTreeNode] = []
    documents: list[DocumentNode] = []
    cadDocuments: list[DocumentNode] = []
    timing: TimingInfo = TimingInfo()


# ── Occurrences ──────────────────────────────────────────────


class PartOccurrence(BaseModel):
    partId: str = ""
    number: str = ""
    name: str = ""
    version: str = ""
    state: str = ""
    usedInPart: Optional[str] = None
    usedInName: Optional[str] = None
    pathHint: Optional[str] = None


class OccurrencesResponse(BaseModel):
    code: str
    totalFound: int
    occurrences: list[PartOccurrence]
    timing: TimingInfo


# ── Where-Used ───────────────────────────────────────────────


class WhereUsedEntry(BaseModel):
    oid: str = ""
    number: str = ""
    name: str = ""
    revision: Optional[str] = None
    state: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None


class WhereUsedResponse(BaseModel):
    code: str
    totalFound: int
    usedIn: list[WhereUsedEntry]
    timing: TimingInfo
    note: str = ""


# ── Document List ────────────────────────────────────────────


class DocumentListResponse(BaseModel):
    code: str
    totalFound: int
    documents: list[DocumentNode] = []
    timing: TimingInfo = TimingInfo()


# ── Cache ────────────────────────────────────────────────────


class CacheStats(BaseModel):
    entries: int
    ttl_seconds: int
    max_size: int


# ── Benchmark ────────────────────────────────────────────────


class BenchmarkResult(BaseModel):
    endpoint: str
    description: str
    api_ms: float
    estimated_ui_minutes: float
    speedup_factor: float
    note: str = ""


class BenchmarkResponse(BaseModel):
    results: list[BenchmarkResult]
    summary: str


# ── Search ───────────────────────────────────────────────────


class SearchResponse(BaseModel):
    items: list[PartSearchResult] = []


# ── Change Items (Affected / Resulting) ──────────────────────


class ChangeItem(BaseModel):
    """An item affected by or resulting from a Change object."""
    objectId: str = ""
    objectType: str = ""
    number: str = ""
    name: str = ""
    version: str = ""
    iteration: str = ""
    state: str = ""
    identity: str = ""


class ChangeItemsResponse(BaseModel):
    """Response for affected/resulting items of a change object."""
    code: str
    relation: str = ""  # "affected" or "resulting"
    totalFound: int = 0
    items: list[ChangeItem] = []
    timing: TimingInfo = TimingInfo()


# ── Document Details (Referencing Parts, File Info) ──────────


class ReferencingPart(BaseModel):
    """A part that references a specific document."""
    partId: str = ""
    number: str = ""
    name: str = ""
    version: str = ""
    iteration: str = ""
    state: str = ""
    identity: str = ""


class ReferencingPartsResponse(BaseModel):
    """Response for parts referencing a document."""
    code: str
    totalFound: int = 0
    parts: list[ReferencingPart] = []
    timing: TimingInfo = TimingInfo()


class FileInfo(BaseModel):
    """File/content attachment of a document."""
    fileId: str = ""
    fileName: str = ""
    fileSize: str = ""
    mimeType: str = ""
    role: str = ""
    created: str = ""
    modified: str = ""


class FileInfoResponse(BaseModel):
    """Response for document file info."""
    code: str
    totalFound: int = 0
    files: list[FileInfo] = []
    timing: TimingInfo = TimingInfo()


# ── Versions / Iterations ───────────────────────────────────


class VersionEntry(BaseModel):
    """A single version/iteration of a Windchill object."""
    objectId: str = ""
    number: str = ""
    name: str = ""
    version: str = ""
    iteration: str = ""
    state: str = ""
    identity: str = ""
    context: str = ""
    lastModified: str = ""
    createdOn: str = ""
    isCurrent: bool = False


class VersionsResponse(BaseModel):
    """Response for version/iteration history."""
    code: str
    totalFound: int = 0
    versions: list[VersionEntry] = []
    timing: TimingInfo = TimingInfo()


# ── Lifecycle History ────────────────────────────────────────


class LifecycleEntry(BaseModel):
    """A lifecycle state transition event."""
    fromState: str = ""
    toState: str = ""
    timestamp: str = ""
    user: str = ""
    comment: str = ""


class LifecycleResponse(BaseModel):
    """Response for lifecycle history."""
    code: str
    totalFound: int = 0
    events: list[LifecycleEntry] = []
    timing: TimingInfo = TimingInfo()
