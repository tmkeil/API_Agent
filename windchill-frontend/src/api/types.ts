// TypeScript types matching backend DTOs

export interface TimingInfo {
  totalMs: number
  wrsMs: number
  cacheHits: number
  fromCache: boolean
}

export interface PartSearchResult {
  partId: string
  objectType: string
  subType?: string
  number: string
  name: string
  version: string
  iteration: string
  state: string
  identity: string
  context: string
  lastModified: string
  createdOn: string
  isVariant: string
  organizationId: string
  classification: string
}

export interface BomTreeNode {
  partId: string
  type: string
  number: string
  name: string
  version: string
  iteration: string
  state: string
  identity: string
  hasChildren: boolean
  quantity?: number | null
  quantityUnit?: string
  lineNumber?: string
  organizationId?: string
  usageLinkAttributes?: Record<string, unknown>
  partAttributes?: Record<string, unknown>
  // Frontend-only state
  children?: BomTreeNode[]
  documents?: DocumentNode[]
  cadDocuments?: DocumentNode[]
  expanded?: boolean
  childrenLoaded?: boolean
}

export interface DocumentNode {
  docId: string
  type: string
  subType?: string
  number: string
  name: string
  version: string
  state: string
  docAttributes?: Record<string, unknown>
}

export interface BomNodeResponse {
  children: BomTreeNode[]
  documents: DocumentNode[]
  cadDocuments: DocumentNode[]
  timing: TimingInfo
}

// ── BOM View Configuration ──────────────────────────────────

export interface BomViewColumn {
  key: string
  label: string
  source: 'part' | 'link' | 'usageLink' | 'partAttr' | 'docAttr'
  align: 'left' | 'right'
}

export interface BomViewConfig {
  id: string
  label: string
  columns: BomViewColumn[]
}

export interface SystemInfo {
  key: string
  label: string
  url: string
}

export interface UserInfo {
  ok: boolean
  username: string
  system: string
  systemUrl: string
}

export interface ApiLogEntry {
  timestamp: string
  source: string
  method: string
  url: string
  status: number
  durationMs: number
  note: string
}

// ── Occurrences ("Wo kommt Code XABC vor?") ────────────────

export interface PartOccurrence {
  partId: string
  number: string
  name: string
  version: string
  state: string
  usedInPart: string | null
  usedInName: string | null
  pathHint: string | null
}

export interface OccurrencesResponse {
  code: string
  totalFound: number
  occurrences: PartOccurrence[]
  timing: TimingInfo
}

// ── Detail Page ─────────────────────────────────────────────

export interface PartDetail {
  partId: string
  number: string
  name: string
  version: string
  iteration: string
  state: string
  identity: string
}

export interface PartDetailResponse {
  part: PartDetail
  timing: TimingInfo
}

export interface ObjectDetail {
  objectId: string
  objectType: string
  subType?: string
  typeKey: string
  number: string
  name: string
  version: string
  iteration: string
  state: string
  identity: string
  context: string
  lastModified: string
  createdOn: string
  allAttributes?: Record<string, unknown>
}

export interface ObjectDetailResponse {
  detail: ObjectDetail
  timing: TimingInfo
}

export interface WhereUsedEntry {
  oid: string
  number: string
  name: string
  revision: string | null
  state: string | null
  quantity: number | null
  unit: string | null
}

export interface WhereUsedResponse {
  code: string
  totalFound: number
  usedIn: WhereUsedEntry[]
  timing: TimingInfo
  note: string
}

export interface DocumentListResponse {
  code: string
  totalFound: number
  documents: DocumentNode[]
  timing: TimingInfo
}

// ── Change Items (Affected / Resulting) ─────────────────────

export interface ChangeItem {
  objectId: string
  objectType: string
  subType: string
  number: string
  name: string
  version: string
  iteration: string
  state: string
  identity: string
}

export interface ChangeItemsResponse {
  code: string
  relation: string
  totalFound: number
  items: ChangeItem[]
  timing: TimingInfo
}

// ── Document Details (Referencing Parts, File Info) ─────────

export interface ReferencingPart {
  partId: string
  number: string
  name: string
  version: string
  iteration: string
  state: string
  identity: string
}

export interface ReferencingPartsResponse {
  code: string
  totalFound: number
  parts: ReferencingPart[]
  timing: TimingInfo
}

export interface FileInfo {
  fileId: string
  fileName: string
  fileSize: string
  mimeType: string
  role: string
  created: string
  modified: string
}

export interface FileInfoResponse {
  code: string
  totalFound: number
  files: FileInfo[]
  timing: TimingInfo
}

// ── Versions / Iterations ───────────────────────────────────

export interface VersionEntry {
  objectId: string
  number: string
  name: string
  version: string
  iteration: string
  state: string
  identity: string
  context: string
  lastModified: string
  createdOn: string
  isCurrent: boolean
}

export interface VersionsResponse {
  code: string
  totalFound: number
  versions: VersionEntry[]
  timing: TimingInfo
}

// ── Lifecycle History ───────────────────────────────────────

export interface LifecycleEntry {
  fromState: string
  toState: string
  timestamp: string
  user: string
  comment: string
}

export interface LifecycleResponse {
  code: string
  totalFound: number
  events: LifecycleEntry[]
  timing: TimingInfo
}

// ── Write Operations ────────────────────────────────────────

export interface CreateObjectRequest {
  typeKey: string
  attributes: Record<string, string>
}

export interface UpdateAttributesRequest {
  attributes: Record<string, string>
}

export interface SetStateRequest {
  targetState: string
  comment?: string
}

export interface AddBomChildRequest {
  childPartNumber: string
  quantity?: number
  unit?: string
  findNumber?: string
  lineNumber?: number
  traceCode?: string
  occurrences?: string[]
}

export interface RemoveBomChildRequest {
  usageLinkId: string
}

export interface LinkDocumentRequest {
  documentNumber: string
  linkType?: string  // 'DescribedBy' | 'References'
}

export interface UnlinkDocumentRequest {
  documentNumber: string
  linkType?: string
}

export interface AddDownstreamLinkRequest {
  manufacturingPartNumber: string
}

export interface RemoveDownstreamLinkRequest {
  manufacturingPartNumber: string
}

export interface DownstreamPartInfo {
  number: string
  name: string
  organization: string
  versionView: string
}

export interface DownstreamPartsResponse {
  ok: boolean
  designPartNumber: string
  downstreamParts: DownstreamPartInfo[]
  count: number
}

export interface WriteResponse {
  ok: boolean
  objectId: string
  number: string
  message: string
  timing: TimingInfo
}

// ── Bulk / Batch ────────────────────────────────────────────

export interface BulkItem {
  typeKey: string
  code: string
}

export interface BulkDetailResult {
  typeKey: string
  code: string
  ok: boolean
  error?: string
  detail?: ObjectDetail
}

export interface BulkResponse {
  totalRequested: number
  totalFound: number
  totalErrors: number
  results: BulkDetailResult[]
  timing: TimingInfo
}

// ── Containers ──────────────────────────────────────────────

export interface ContainerItem {
  containerId: string
  name: string
  containerType: string
  odataBinding: string
}

export interface ContainerListResponse {
  containers: ContainerItem[]
}

// ── Part Subtypes ───────────────────────────────────────────

export interface PartSubtype {
  name: string
  odataType: string
}

export interface PartSubtypeListResponse {
  subtypes: PartSubtype[]
}

// ── Classification Nodes ────────────────────────────────────

export interface ClassificationNode {
  internalName: string
  displayName: string
  parentInternalName: string
  isLeaf: boolean
}

export interface ClassificationNodeListResponse {
  nodes: ClassificationNode[]
}

// ── Advanced Search ─────────────────────────────────────────

export interface AdvancedSearchRequest {
  query?: string
  types?: string[]
  contexts?: string[]
  state?: string
  dateFrom?: string
  dateTo?: string
  dateField?: string
  attributes?: Record<string, string>
  limit?: number
}

// ── Balluff BOM Export ──────────────────────────────────────

export interface BalluffBomExportResponse {
  columns: string[]
  rows: Record<string, string>[]
  partNumber: string
  rowCount: number
}

// ── SAP Export ──────────────────────────────────────────────

export interface SapExportFileEntry {
  filename: string
  content: string
}

export interface SapExportStats {
  totalInputRows: number
  totalOutputRows: number
  filesCount: number
  skippedRows: number
}

export interface SapExportResponse {
  validation: string[]
  files: SapExportFileEntry[]
  stats: SapExportStats
}

export interface SapExportRequest {
  columns: string[]
  rows: Record<string, string>[]
  partNumber: string
  fromPreview?: boolean
  rules?: Record<string, boolean>
}

// ── SAP Preview ────────────────────────────────────────────

export interface SapPreviewStats {
  totalInputRows: number
  totalOutputRows: number
  removedRows: number
}

export interface SapPreviewResponse {
  columns: string[]
  rows: Record<string, string>[]
  validation: string[]
  stats: SapPreviewStats
}

// ── CAD Structure (Assembly) ────────────────────────────────

export interface CadStructureNode {
  cadDocId: string
  number: string
  fileName: string
  name: string
  version: string
  state: string
  quantity: string
  level: number
  dependencyType: string
  hasChildren: boolean
}

export interface CadStructureResponse {
  code: string
  totalFound: number
  nodes: CadStructureNode[]
  timing: TimingInfo
}

// ── CN Part Results Check ───────────────────────────────────

export interface CheckPartResultsResponse {
  withParts: string[]
}

// ── Change Notice Listing ───────────────────────────────────

export interface ChangeNoticeListItem {
  objectId: string
  number: string
  name: string
  subType: string
  version: string
  state: string
  createdBy: string
  createdOn: string
  lastModified: string
  description: string
}

export interface ChangeNoticeListResponse {
  totalCount: number
  items: ChangeNoticeListItem[]
  timing: TimingInfo
}

// ── WorkItem (Projekt-Tracking) ─────────────────────────────

export interface WorkItemStep {
  step: string
  timestamp: string
  data: Record<string, unknown>
}

export interface WorkItemSummary {
  id: string
  cnNumber: string
  cnName: string
  cnSubType: string
  status: string
  createdAt: string
  updatedAt: string
  stepCount: number
}

export interface WorkItem {
  id: string
  status: string
  createdAt: string
  updatedAt: string
  changeNotice: Record<string, unknown>
  resultingParts: Record<string, unknown>[]
  selectedPart: Record<string, unknown>
  bomData: Record<string, string>[]
  bomColumns: string[]
  steps: WorkItemStep[]
}

export interface WorkItemListResponse {
  items: WorkItemSummary[]
  totalCount: number
}