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
    usageLinkId: str = ""           # OData-ID of the WTPartUsageLink to this node's parent — needed for REMOVE
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
    docAttributes: dict[str, Any] = {}


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
    subType: str = ""
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


# ── Change Notice Listing ────────────────────────────────────


class ChangeNoticeListItem(BaseModel):
    """Summary item for CN listing."""
    objectId: str = ""
    number: str = ""
    name: str = ""
    subType: str = ""
    version: str = ""
    state: str = ""
    createdBy: str = ""
    createdOn: str = ""
    lastModified: str = ""
    description: str = ""


class ChangeNoticeListResponse(BaseModel):
    """Paginated list of Change Notices."""
    totalCount: int = 0
    items: list[ChangeNoticeListItem] = []
    timing: TimingInfo = TimingInfo()


# ── Equivalence Network (Design ↔ Manufacturing) ─────────────


class EquivPartRef(BaseModel):
    """A part referenced through an Equivalence Link."""
    linkId: str = ""
    partId: str = ""
    number: str = ""
    name: str = ""
    version: str = ""
    iteration: str = ""
    state: str = ""
    view: str = ""
    organizationId: str = ""


class EquivalenceNetworkResponse(BaseModel):
    """Equivalence Network for a single Part.

    `down` lists Manufacturing pendants (this Part is the upstream/design side).
    `up`   lists Design parents (this Part is the downstream/manufacturing side).
    """
    code: str
    selfNumber: str = ""
    selfView: str = ""
    down: list[EquivPartRef] = []
    up: list[EquivPartRef] = []
    timing: TimingInfo = TimingInfo()


class BomTransformerResponse(BaseModel):
    """Combined response for the BOM Transformer dual-tree view.

    Loads the equivalence network for `code` plus the BOM root nodes for
    the Design side (left) and the Manufacturing side (right). Either
    side may be `None` if no counterpart exists yet — the frontend will
    then show an empty placeholder / Generate-action.
    """
    code: str
    selfView: str = ""
    designRoot: Optional[BomTreeNode] = None
    manufacturingRoot: Optional[BomTreeNode] = None
    equivalence: EquivalenceNetworkResponse
    timing: TimingInfo = TimingInfo()


# ── BOM Transformer — Phase 2b (DetectDiscrepancies / GenerateDownstream) ──


class TransformDetectRequest(BaseModel):
    """Detect Discrepancies zwischen Upstream- (EBOM) und Downstream-Struktur.

    Body laut Swagger-Spec (``DiscrepancyContext``: TargetPath /
    SourcePartSelection / UpstreamChangeOid). Der Live-Server verlangt
    zusätzlich ``SourceRoot`` und akzeptiert ``TargetRoot`` — beide Felder
    fehlen in der veröffentlichten Swagger-Definition.
    """
    targetPath: str = ""
    sourcePartPaths: list[str] = []
    upstreamChangeOid: str = ""
    sourceRoot: str = ""
    targetRoot: str = ""


class TransformGenerateRequest(BaseModel):
    """Generate downstream structure for the given EBOM nodes.

    `sourcePartPaths` lists the EBOM nodes the user marked as ``NEW``
    in the UI. `changeOid` is optional — provide a Change Notice OID for
    released parts (Windchill standard process).
    """
    targetPath: str
    sourcePartPaths: list[str]
    upstreamChangeOid: str = ""
    changeOid: str = ""


class TransformCopyRequest(BaseModel):
    """Per-node COPY: paste selected EBOM nodes under a MBOM target.

    Mirrors the Windchill drag&drop semantics; backend translates this to
    ``PasteSpecial``. ``sourcePartPaths`` lists the EBOM nodes the user
    marked as ``COPY`` in the UI.
    """
    targetPath: str
    sourcePartPaths: list[str]
    upstreamChangeOid: str = ""
    changeOid: str = ""


class TransformRemoveRequest(BaseModel):
    """Per-node REMOVE: delete the listed MBOM usage-links.

    ``usageLinkIds`` are OData IDs of WTPartUsageLink records (the BOM
    parent→child relationships on the MBOM side). The backend deletes
    each via ``PTC.ProdMgmt.UsageLinks('<id>')``. Fails fast on the first
    error and reports which link succeeded.
    """
    usageLinkIds: list[str]


class TransformRemoveResponse(BaseModel):
    """Per-link result of a REMOVE batch."""
    ok: bool = True
    removed: list[str] = []        # usage-link IDs successfully deleted
    failed: list[dict[str, str]] = []  # [{usageLinkId, error}]
    timing: TimingInfo = TimingInfo()


class TransformResponse(BaseModel):
    """Wraps the raw OData response from the BomTransformation domain.

    `value` is the unmodified `value` array from the Windchill response
    (typically `EquivalentUsageAssociation` entries). Returned as-is so
    the frontend can adapt without API churn while we learn the exact
    shape against plm-dev.
    """
    ok: bool = True
    action: str = ""
    value: list[dict] = []
    raw: dict = {}
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
    """Request body for adding a child to a BOM.

    Offizielle WRS-Doku: POST Parts('<parent>')/Uses
    mit Quantity, Unit, FindNumber, LineNumber, TraceCode, Occurrences.
    """
    childPartNumber: str
    quantity: float = 1.0
    unit: str = "each"
    findNumber: Optional[str] = None
    lineNumber: Optional[int] = None
    traceCode: Optional[str] = None
    occurrences: Optional[list[str]] = None


class RemoveBomChildRequest(BaseModel):
    """Request body for removing a child from a BOM."""
    usageLinkId: str


class LinkDocumentRequest(BaseModel):
    """Request body for linking a document to a part."""
    documentNumber: str
    linkType: str = "DescribedBy"   # 'DescribedBy' oder 'References'


class UnlinkDocumentRequest(BaseModel):
    """Request body for unlinking a document from a part."""
    documentNumber: str
    linkType: str = "DescribedBy"


class AddDownstreamLinkRequest(BaseModel):
    """Request body for adding a downstream/equivalence link (Design → Manufacturing)."""
    manufacturingPartNumber: str


class RemoveDownstreamLinkRequest(BaseModel):
    """Request body for removing a downstream/equivalence link."""
    manufacturingPartNumber: str


class DownstreamPartInfo(BaseModel):
    """Info about a downstream (manufacturing equivalent) part."""
    number: str
    name: str
    organization: str
    versionView: str


class DownstreamPartsResponse(BaseModel):
    """Response for downstream parts query."""
    ok: bool = True
    designPartNumber: str
    downstreamParts: list[DownstreamPartInfo] = []
    count: int = 0


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


class AdvancedSearchCriterion(BaseModel):
    """One criterion of an advanced search (field + value)."""
    field: str = "Number"   # 'Number' or 'Name'
    value: str = ""


class AdvancedSearchRequest(BaseModel):
    """Request body for advanced search with structured filters."""
    query: str = ""
    # Structured criteria (preferred over ``query``). Empty list = use ``query``.
    criteria: list[AdvancedSearchCriterion] = []
    combinator: str = "and"  # 'and' or 'or' — how to join criteria
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


# ── Balluff BOM Export ───────────────────────────────────────

class BalluffBomExportResponse(BaseModel):
    """Response fuer den Balluff BOM Export (flache Tabelle)."""
    columns: list[str] = []
    rows: list[dict[str, str]] = []
    partNumber: str = ""
    rowCount: int = 0
    view: str = ""


# ── SAP Export ───────────────────────────────────────────────

class SapExportFileEntry(BaseModel):
    """Einzelne CSV-Datei im SAP-Export."""
    filename: str = ""
    content: str = ""


class SapExportStats(BaseModel):
    """Statistiken zum SAP-Export."""
    totalInputRows: int = 0
    totalOutputRows: int = 0
    filesCount: int = 0
    skippedRows: int = 0


class SapExportResponse(BaseModel):
    """Response fuer den SAP-Export (aufbereitete CSV-Dateien)."""
    validation: list[str] = []
    files: list[SapExportFileEntry] = []
    stats: SapExportStats = SapExportStats()


class SapExportRequest(BaseModel):
    """Request-Body fuer den SAP-Export (bereits geladene Balluff-Export-Daten)."""
    columns: list[str] = []
    rows: list[dict[str, str]] = []
    partNumber: str = ""
    fromPreview: bool = False
    rules: dict[str, bool] | None = None


class SapPreviewStats(BaseModel):
    """Statistiken fuer SAP Preview (nur PartA)."""
    totalInputRows: int = 0
    totalOutputRows: int = 0
    removedRows: int = 0


class SapPreviewResponse(BaseModel):
    """Response fuer SAP Preview (PartA-Transformation + PartB-Validierung)."""
    columns: list[str] = []
    rows: list[dict[str, str]] = []
    validation: list[str] = []
    stats: SapPreviewStats = SapPreviewStats()


# ── CAD Structure (Assembly) ────────────────────────────────


class CadStructureNode(BaseModel):
    """Ein Knoten in der CAD-Assemblystruktur."""
    cadDocId: str = ""
    number: str = ""
    fileName: str = ""
    name: str = ""
    version: str = ""
    state: str = ""
    quantity: str = ""
    level: int = 0
    dependencyType: str = ""
    hasChildren: bool = False


class CadStructureResponse(BaseModel):
    """Response fuer CAD Assembly-Struktur."""
    code: str
    totalFound: int = 0
    nodes: list[CadStructureNode] = []


# ── WorkItem (Projektfortschritt-Tracking) ───────────────────


class WorkItemStep(BaseModel):
    """Ein einzelner Arbeitsschritt im WorkItem."""
    step: str           # z.B. "cn_selected", "parts_loaded", "part_selected", "bom_exported", "bom_edited", "csv_generated"
    timestamp: str = ""
    data: dict[str, Any] = {}


class WorkItemSummary(BaseModel):
    """Kurzinfo eines WorkItems fuer die Liste."""
    id: str
    cnNumber: str = ""
    cnName: str = ""
    cnSubType: str = ""
    status: str = "in_progress"  # in_progress | completed
    createdAt: str = ""
    updatedAt: str = ""
    stepCount: int = 0


class WorkItem(BaseModel):
    """Vollstaendiges WorkItem mit allen Schritten und Daten."""
    id: str
    status: str = "in_progress"
    createdAt: str = ""
    updatedAt: str = ""
    changeNotice: dict[str, Any] = {}   # CN-Metadaten (number, name, subType, state)
    resultingParts: list[dict[str, Any]] = []
    selectedPart: dict[str, Any] = {}
    bomData: list[dict[str, str]] = []
    bomColumns: list[str] = []
    steps: list[WorkItemStep] = []


class WorkItemListResponse(BaseModel):
    """Liste aller WorkItems."""
    items: list[WorkItemSummary] = []
    totalCount: int = 0
    timing: TimingInfo = TimingInfo()