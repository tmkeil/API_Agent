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
    subType: str = ""          # OData ObjectType (Product, Component, Production Document, …)
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
    allAttributes: dict[str, Any] = {}  # all raw OData attributes (flattened)


class ObjectDetailResponse(BaseModel):
    detail: ObjectDetail
    timing: TimingInfo


class PartSearchResult(BaseModel):
    partId: str = ""
    objectType: str = "WTPart"
    subType: str = ""           # OData ObjectType (Product, Component, Auxiliary Material, …)
    number: str = ""
    name: str = ""
    version: str = ""
    iteration: str = ""
    state: str = ""
    identity: str = ""
    context: str = ""
    lastModified: str = ""
    createdOn: str = ""
    isVariant: str = ""
    organizationId: str = ""
    classification: str = ""


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
    organizationId: str = ""
    usageLinkAttributes: dict[str, Any] = {}
    partAttributes: dict[str, Any] = {}


class DocumentNode(BaseModel):
    docId: str = ""
    type: str = "WTDocument"       # Windchill class (WTDocument, EPMDocument)
    subType: str = ""              # OData ObjectType (Production Document, Approval Document, …)
    number: str = ""
    name: str = ""
    version: str = ""
    state: str = ""


class BomNodeResponse(BaseModel):
    children: list[BomTreeNode] = []
    documents: list[DocumentNode] = []
    cadDocuments: list[DocumentNode] = []
    timing: TimingInfo = TimingInfo()


# ── BOM View Configuration ──────────────────────────────────


class BomViewColumn(BaseModel):
    """Describes a single column in a BOM view."""
    key: str                       # field key to display
    label: str                     # column header label
    source: str = "part"           # "part" | "link" | "usageLink"
    align: str = "left"            # "left" | "right"


class BomViewConfig(BaseModel):
    """A named BOM view with its column set."""
    id: str
    label: str
    columns: list[BomViewColumn]


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


# ── Write Operations ────────────────────────────────────────


class CreateObjectRequest(BaseModel):
    """Request body for creating a Windchill object."""
    typeKey: str
    attributes: dict[str, Any]


class UpdateAttributesRequest(BaseModel):
    """Request body for updating object attributes."""
    attributes: dict[str, Any]


class SetStateRequest(BaseModel):
    """Request body for changing lifecycle state."""
    targetState: str
    comment: str = ""


class AddBomChildRequest(BaseModel):
    """Request body for adding a child to a BOM."""
    childPartNumber: str
    quantity: float = 1.0
    unit: str = "each"


class RemoveBomChildRequest(BaseModel):
    """Request body for removing a child from a BOM."""
    usageLinkId: str


class WriteResponse(BaseModel):
    """Generic response for write operations."""
    ok: bool = True
    objectId: str = ""
    number: str = ""
    message: str = ""
    timing: TimingInfo = TimingInfo()


# ── Bulk / Batch Queries ────────────────────────────────────


class BulkItem(BaseModel):
    """A single item in a bulk query request."""
    typeKey: str
    code: str


class BulkRequest(BaseModel):
    """Request body for bulk detail queries."""
    items: list[BulkItem]


class BulkDetailResult(BaseModel):
    """Result for a single item in a bulk query."""
    typeKey: str
    code: str
    ok: bool = True
    error: str = ""
    detail: Optional[ObjectDetail] = None


class BulkResponse(BaseModel):
    """Response for bulk detail queries."""
    totalRequested: int = 0
    totalFound: int = 0
    totalErrors: int = 0
    results: list[BulkDetailResult] = []
    timing: TimingInfo = TimingInfo()


# ── Advanced Search ─────────────────────────────────────────


class AdvancedSearchRequest(BaseModel):
    """Request body for advanced search with structured filters."""
    query: str = ""
    types: list[str] = []
    contexts: list[str] = []
    state: str = ""
    dateFrom: str = ""
    dateTo: str = ""
    dateField: str = "modified"  # "modified" or "created"
    attributes: dict[str, str] = {}
    limit: int = 200


# ── Containers ───────────────────────────────────────────────


class ContainerItem(BaseModel):
    """A Windchill Container (Product / Library)."""
    containerId: str = ""
    name: str = ""
    containerType: str = ""
    odataBinding: str = ""


class ContainerListResponse(BaseModel):
    """Response for container listing."""
    containers: list[ContainerItem] = []
    timing: TimingInfo = TimingInfo()


class PartSubtype(BaseModel):
    """Ein verfuegbarer Part-Subtype (Soft Type) in Windchill."""
    name: str = ""
    odataType: str = ""


class PartSubtypeListResponse(BaseModel):
    """Response fuer Part-Subtype-Listing."""
    subtypes: list[PartSubtype] = []


class ClassificationNode(BaseModel):
    """Ein Knoten im Windchill Classification-Baum."""
    internalName: str = ""
    displayName: str = ""
    parentInternalName: str = ""
    isLeaf: bool = False


class ClassificationNodeListResponse(BaseModel):
    """Response fuer Classification-Node-Listing."""
    nodes: list[ClassificationNode] = []
