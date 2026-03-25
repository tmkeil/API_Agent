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
  number: string
  name: string
  version: string
  state: string
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
  source: 'part' | 'link' | 'usageLink'
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
