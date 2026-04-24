import type {
  AddBomChildRequest,
  AdvancedSearchRequest,
  BalluffBomExportResponse,
  BomNodeResponse,
  BomTreeNode,
  BomViewConfig,
  BulkItem,
  BulkResponse,
  CadStructureResponse,
  ChangeItemsResponse,
  CheckPartResultsResponse,
  ContainerListResponse,
  DocumentListResponse,
  FileInfoResponse,
  LifecycleResponse,
  ObjectDetailResponse,
  OccurrencesResponse,
  PartDetailResponse,
  PartSearchResult,
  PartSubtypeListResponse,
  ClassificationNodeListResponse,
  ReferencingPartsResponse,
  SetStateRequest,
  SystemInfo,
  UserInfo,
  VersionsResponse,
  WhereUsedResponse,
  WriteResponse,
  ApiLogEntry,
  SapExportResponse,
  SapExportRequest,
  SapPreviewResponse,
  ChangeNoticeListResponse,
  WorkItem,
  WorkItemListResponse,
  ChangeNoticeListItem,
} from './types'

const BASE = '/api'

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { ...init?.headers as Record<string, string> }
  // Only set Content-Type for requests with a body (POST, PUT, PATCH)
  const method = (init?.method || 'GET').toUpperCase()
  if (['POST', 'PUT', 'PATCH'].includes(method)) {
    if (!headers['Content-Type']) {
      headers['Content-Type'] = 'application/json'
    }
  }
  const resp = await fetch(url, {
    credentials: 'include',
    ...init,
    headers,
    // Forward AbortController signal so callers can cancel in-flight requests
    signal: init?.signal,
  })
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}))
    throw new Error(body.error || body.detail || `HTTP ${resp.status}`)
  }
  // Guard against empty or non-JSON responses (e.g. 204 No Content)
  const ct = resp.headers.get('content-type') || ''
  if (resp.status === 204 || !ct.includes('application/json')) {
    return undefined as unknown as T
  }
  return resp.json()
}

// Auth
export async function getSystems(): Promise<SystemInfo[]> {
  const data = await request<{ systems: SystemInfo[] }>(`${BASE}/auth/systems`)
  return data.systems
}

export async function login(
  system: string,
  username: string,
  password: string,
): Promise<UserInfo> {
  return request<UserInfo>(`${BASE}/auth/login`, {
    method: 'POST',
    body: JSON.stringify({ system, username, password }),
  })
}

export async function logout(): Promise<void> {
  await request<unknown>(`${BASE}/auth/logout`, { method: 'POST' })
}

export async function getMe(): Promise<UserInfo> {
  return request<UserInfo>(`${BASE}/auth/me`)
}

// Search
export async function searchParts(
  q: string,
  limit?: number,
  types?: string[],
  context?: string,
): Promise<PartSearchResult[]> {
  const params = new URLSearchParams({ q })
  if (limit && limit > 0) params.set('limit', String(limit))
  if (types && types.length > 0) {
    params.set('types', types.join(','))
  }
  if (context) {
    params.set('context', context)
  }
  const data = await request<{ items: PartSearchResult[] }>(
    `${BASE}/search?${params}`,
  )
  return data.items
}

/**
 * Streaming search via Server-Sent Events.
 * Calls `onBatch` with each batch of results as they arrive.
 * Returns an AbortController to cancel the stream.
 */
export function searchPartsStream(
  q: string,
  onBatch: (items: PartSearchResult[]) => void,
  onDone: (info: { total: number; durationMs: number }) => void,
  onError: (err: string) => void,
  opts?: { limit?: number; types?: string[] },
): AbortController {
  const params = new URLSearchParams({ q })
  if (opts?.limit && opts.limit > 0) params.set('limit', String(opts.limit))
  if (opts?.types && opts.types.length > 0) {
    params.set('types', opts.types.join(','))
  }
  // Always use keyword mode on the backend (Number OR Name with wildcards).
  params.set('mode', 'keyword')

  const controller = new AbortController()

  fetch(`${BASE}/search/stream?${params}`, {
    credentials: 'include',
    signal: controller.signal,
    headers: { Accept: 'text/event-stream' },
  })
    .then(async (resp) => {
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}))
        throw new Error(body.error || body.detail || `HTTP ${resp.status}`)
      }
      const reader = resp.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''
      let doneReceived = false

      const parseEvent = (raw: string) => {
        const lines = raw.trim().split('\n')
        let eventType = 'message'
        let data = ''
        for (const line of lines) {
          if (line.startsWith('event: ')) eventType = line.slice(7)
          else if (line.startsWith('data: ')) data += line.slice(6)
        }
        if (!data) return
        if (eventType === 'done') {
          doneReceived = true
          try { onDone(JSON.parse(data)) } catch { /* ignore */ }
        } else {
          try {
            const items = JSON.parse(data) as PartSearchResult[]
            if (items.length > 0) onBatch(items)
          } catch { /* ignore */ }
        }
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        // Extract complete SSE events (separated by \n\n)
        const segments = buffer.split('\n\n')
        buffer = segments.pop() || '' // keep incomplete tail
        for (const seg of segments) {
          if (seg.trim()) parseEvent(seg)
        }
      }

      // Flush any remaining data in buffer
      if (buffer.trim()) parseEvent(buffer)

      // Guarantee onDone fires even if server didn't send event:done
      if (!doneReceived) {
        onDone({ total: 0, durationMs: 0 })
      }
    })
    .catch((err) => {
      if (err?.name !== 'AbortError') {
        onError(err instanceof Error ? err.message : String(err))
      }
    })

  return controller
}

// Contexts (Windchill Container names)
export async function getContexts(): Promise<string[]> {
  const data = await request<{ contexts: string[] }>(`${BASE}/contexts`)
  return data.contexts
}

// Containers (Products / Libraries — for Context@odata.bind)
export async function fetchContainers(): Promise<ContainerListResponse> {
  return request<ContainerListResponse>(`${BASE}/containers`)
}

// Part Subtypes (Soft Types — for @odata.type)
export async function fetchPartSubtypes(): Promise<PartSubtypeListResponse> {
  return request<PartSubtypeListResponse>(`${BASE}/part-subtypes`)
}

// Classification Nodes (from ClfStructure)
export async function fetchClassificationNodes(): Promise<ClassificationNodeListResponse> {
  return request<ClassificationNodeListResponse>(`${BASE}/classification-nodes`)
}

// Occurrences (Use Case: "Wo kommt Code XABC vor?")
export async function getOccurrences(code: string): Promise<OccurrencesResponse> {
  return request<OccurrencesResponse>(`${BASE}/parts/${encodeURIComponent(code)}/occurrences`)
}

// Detail Page APIs
export async function getPartDetail(code: string, signal?: AbortSignal): Promise<PartDetailResponse> {
  return request<PartDetailResponse>(`${BASE}/parts/${encodeURIComponent(code)}`, { signal })
}

export async function getObjectDetail(typeKey: string, code: string, signal?: AbortSignal): Promise<ObjectDetailResponse> {
  return request<ObjectDetailResponse>(
    `${BASE}/objects/${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}`,
    { signal },
  )
}

export async function getPartDocuments(code: string, signal?: AbortSignal): Promise<DocumentListResponse> {
  return request<DocumentListResponse>(`${BASE}/parts/${encodeURIComponent(code)}/documents`, { signal })
}

export async function getPartCadDocuments(code: string, signal?: AbortSignal): Promise<DocumentListResponse> {
  return request<DocumentListResponse>(`${BASE}/parts/${encodeURIComponent(code)}/cad-documents`, { signal })
}

export async function getWhereUsed(code: string, signal?: AbortSignal): Promise<WhereUsedResponse> {
  return request<WhereUsedResponse>(`${BASE}/parts/${encodeURIComponent(code)}/where-used`, { signal })
}

// Change Items (Affected / Resulting)
export async function getAffectedItems(typeKey: string, code: string, signal?: AbortSignal): Promise<ChangeItemsResponse> {
  return request<ChangeItemsResponse>(
    `${BASE}/changes/${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}/affected`,
    { signal },
  )
}

export async function getResultingItems(typeKey: string, code: string, signal?: AbortSignal): Promise<ChangeItemsResponse> {
  return request<ChangeItemsResponse>(
    `${BASE}/changes/${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}/resulting`,
    { signal },
  )
}

// Document Details (Referencing Parts, File Info)
export async function getReferencingParts(typeKey: string, code: string, signal?: AbortSignal): Promise<ReferencingPartsResponse> {
  return request<ReferencingPartsResponse>(
    `${BASE}/documents/${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}/referencing-parts`,
    { signal },
  )
}

export async function getDocumentFiles(typeKey: string, code: string, signal?: AbortSignal): Promise<FileInfoResponse> {
  return request<FileInfoResponse>(
    `${BASE}/documents/${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}/files`,
    { signal },
  )
}

// Versions / Iterations
export async function getObjectVersions(typeKey: string, code: string, signal?: AbortSignal): Promise<VersionsResponse> {
  return request<VersionsResponse>(
    `${BASE}/objects/${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}/versions`,
    { signal },
  )
}

// Lifecycle History
export async function getLifecycleHistory(typeKey: string, code: string, signal?: AbortSignal): Promise<LifecycleResponse> {
  return request<LifecycleResponse>(
    `${BASE}/objects/${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}/lifecycle`,
    { signal },
  )
}

// BOM
export async function getBomRoot(
  partNumber: string,
  signal?: AbortSignal,
): Promise<BomTreeNode> {
  const params = new URLSearchParams({ partNumber })
  const data = await request<{ root: BomTreeNode }>(
    `${BASE}/bom/root?${params}`,
    { signal },
  )
  return data.root
}

export async function getBomChildren(
  partId: string,
): Promise<BomNodeResponse> {
  const params = new URLSearchParams({ partId })
  return request<BomNodeResponse>(`${BASE}/bom/children?${params}`)
}

export async function getBomViews(): Promise<BomViewConfig[]> {
  return request<BomViewConfig[]>(`${BASE}/bom/views`)
}

// BOM raw field diagnostics
export async function diagnoseBomFields(partNumber: string): Promise<Record<string, unknown>> {
  const params = new URLSearchParams({ partNumber })
  return request<Record<string, unknown>>(`${BASE}/diagnose/bom-fields?${params}`)
}

// API Logs
export async function getApiLogs(limit = 120): Promise<ApiLogEntry[]> {
  const data = await request<{ items: ApiLogEntry[] }>(
    `${BASE}/logs?limit=${limit}`,
  )
  return data.items
}

export async function clearApiLogs(): Promise<void> {
  await request<{ cleared: boolean }>(`${BASE}/logs`, {
    method: 'DELETE',
  })
}

// Export
export async function exportBom(
  mode: 'expandedOnly' | 'fullTree' | 'extended',
  partNumber: string,
  tree?: unknown,
): Promise<{ ok: boolean; filename: string; downloadUrl: string }> {
  return request(`${BASE}/export`, {
    method: 'POST',
    body: JSON.stringify({ mode, partNumber, tree }),
  })
}

// Balluff BOM Export (flat table)
export async function fetchBalluffBomExport(
  partNumber: string,
  signal?: AbortSignal,
  maxDepth?: number,
): Promise<BalluffBomExportResponse> {
  const params = maxDepth != null ? `?max_depth=${maxDepth}` : ''
  return request<BalluffBomExportResponse>(
    `${BASE}/export/balluff/${encodeURIComponent(partNumber)}${params}`,
    { signal },
  )
}
// SAP Preview (PartA-Transformation + PartB-Validierung)
export async function fetchSapPreview(
  body: SapExportRequest,
  signal?: AbortSignal,
): Promise<SapPreviewResponse> {
  return request<SapPreviewResponse>(
    `${BASE}/export/sap/preview`,
    { method: 'POST', body: JSON.stringify(body), signal },
  )
}
// SAP Export (aufbereitete CSV-Dateien — nutzt bereits geladene Daten via POST)
export async function fetchSapExport(
  body: SapExportRequest,
  signal?: AbortSignal,
): Promise<SapExportResponse> {
  return request<SapExportResponse>(
    `${BASE}/export/sap`,
    { method: 'POST', body: JSON.stringify(body), signal },
  )
}
// ── Write Operations ────────────────────────────────────────

export async function createObject(
  typeKey: string,
  attributes: Record<string, string>,
): Promise<WriteResponse> {
  return request<WriteResponse>(`${BASE}/write/create`, {
    method: 'POST',
    body: JSON.stringify({ typeKey, attributes }),
  })
}

/** Build URL with optional objectId query param. */
function writeUrl(path: string, objectId?: string): string {
  const base = `${BASE}/write/${path}`
  return objectId ? `${base}?objectId=${encodeURIComponent(objectId)}` : base
}

export async function updateAttributes(
  typeKey: string,
  code: string,
  attributes: Record<string, string>,
  objectId?: string,
): Promise<WriteResponse> {
  return request<WriteResponse>(
    writeUrl(`${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}/attributes`, objectId),
    {
      method: 'PATCH',
      body: JSON.stringify({ attributes }),
    },
  )
}

export async function setLifecycleState(
  typeKey: string,
  code: string,
  body: SetStateRequest,
  objectId?: string,
): Promise<WriteResponse> {
  return request<WriteResponse>(
    writeUrl(`${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}/state`, objectId),
    {
      method: 'POST',
      body: JSON.stringify(body),
    },
  )
}

export async function checkoutObject(
  typeKey: string,
  code: string,
  objectId?: string,
): Promise<WriteResponse> {
  return request<WriteResponse>(
    writeUrl(`${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}/checkout`, objectId),
    { method: 'POST' },
  )
}

export async function checkinObject(
  typeKey: string,
  code: string,
  objectId?: string,
): Promise<WriteResponse> {
  return request<WriteResponse>(
    writeUrl(`${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}/checkin`, objectId),
    { method: 'POST' },
  )
}

export async function reviseObject(
  typeKey: string,
  code: string,
  objectId?: string,
): Promise<WriteResponse> {
  return request<WriteResponse>(
    writeUrl(`${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}/revise`, objectId),
    { method: 'POST' },
  )
}

export async function addBomChild(
  parentCode: string,
  body: AddBomChildRequest,
): Promise<WriteResponse> {
  return request<WriteResponse>(
    `${BASE}/write/bom/${encodeURIComponent(parentCode)}/add-child`,
    {
      method: 'POST',
      body: JSON.stringify(body),
    },
  )
}

export async function removeBomChild(
  usageLinkId: string,
): Promise<WriteResponse> {
  return request<WriteResponse>(
    `${BASE}/write/bom/remove-child`,
    {
      method: 'POST',
      body: JSON.stringify({ usageLinkId }),
    },
  )
}

// ── Bulk / Batch ────────────────────────────────────────────

export async function bulkDetails(items: BulkItem[]): Promise<BulkResponse> {
  return request<BulkResponse>(`${BASE}/bulk/details`, {
    method: 'POST',
    body: JSON.stringify({ items }),
  })
}

// ── Advanced Search ─────────────────────────────────────────

export async function advancedSearch(body: AdvancedSearchRequest): Promise<PartSearchResult[]> {
  const data = await request<{ items: PartSearchResult[] }>(
    `${BASE}/search/advanced`,
    {
      method: 'POST',
      body: JSON.stringify(body),
    },
  )
  return data.items
}

/**
 * Streaming advanced search via Server-Sent Events.
 * Mirrors :func:`searchPartsStream` but posts the structured request body.
 */
export function advancedSearchStream(
  body: AdvancedSearchRequest,
  onBatch: (items: PartSearchResult[]) => void,
  onDone: (info: { total: number; durationMs: number }) => void,
  onError: (err: string) => void,
): AbortController {
  const controller = new AbortController()

  fetch(`${BASE}/search/advanced/stream`, {
    method: 'POST',
    credentials: 'include',
    signal: controller.signal,
    headers: {
      Accept: 'text/event-stream',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
    .then(async (resp) => {
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}))
        throw new Error(err.error || err.detail || `HTTP ${resp.status}`)
      }
      const reader = resp.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''
      let doneReceived = false

      const parseEvent = (raw: string) => {
        const lines = raw.trim().split('\n')
        let eventType = 'message'
        let data = ''
        for (const line of lines) {
          if (line.startsWith('event: ')) eventType = line.slice(7)
          else if (line.startsWith('data: ')) data += line.slice(6)
        }
        if (!data) return
        if (eventType === 'done') {
          doneReceived = true
          try { onDone(JSON.parse(data)) } catch { /* ignore */ }
        } else {
          try {
            const items = JSON.parse(data) as PartSearchResult[]
            if (items.length > 0) onBatch(items)
          } catch { /* ignore */ }
        }
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const segments = buffer.split('\n\n')
        buffer = segments.pop() || ''
        for (const seg of segments) {
          if (seg.trim()) parseEvent(seg)
        }
      }
      if (buffer.trim()) parseEvent(buffer)
      if (!doneReceived) onDone({ total: 0, durationMs: 0 })
    })
    .catch((err) => {
      if (err?.name !== 'AbortError') {
        onError(err instanceof Error ? err.message : String(err))
      }
    })

  return controller
}

// ── Document Download ───────────────────────────────────────

export function getDocumentDownloadUrl(typeKey: string, code: string): string {
  return `${BASE}/documents/${encodeURIComponent(typeKey)}/${encodeURIComponent(code)}/download`
}

// ── CAD Structure (Assembly) ────────────────────────────────

export async function getCadStructure(code: string, signal?: AbortSignal): Promise<CadStructureResponse> {
  return request<CadStructureResponse>(
    `${BASE}/documents/cad/${encodeURIComponent(code)}/structure`,
    { signal },
  )
}

export function getCadStructureCsvUrl(code: string): string {
  return `${BASE}/documents/cad/${encodeURIComponent(code)}/structure/csv`
}

// ── CN Part Results Check ───────────────────────────────────

export async function checkCnPartResults(numbers: string[], signal?: AbortSignal): Promise<CheckPartResultsResponse> {
  return request<CheckPartResultsResponse>(
    `${BASE}/changes/check-part-results`,
    {
      method: 'POST',
      body: JSON.stringify({ numbers }),
      signal,
    },
  )
}

// ── Change Notice Listing ───────────────────────────────────

export async function listChangeNotices(
  params?: { state?: string; subType?: string; top?: number; skip?: number },
  signal?: AbortSignal,
): Promise<ChangeNoticeListResponse> {
  const qs = new URLSearchParams()
  if (params?.state) qs.set('state', params.state)
  if (params?.subType) qs.set('sub_type', params.subType)
  if (params?.top) qs.set('top', String(params.top))
  if (params?.skip) qs.set('skip', String(params.skip))
  const q = qs.toString()
  return request<ChangeNoticeListResponse>(
    `${BASE}/changes/change_notices${q ? '?' + q : ''}`,
    { signal },
  )
}


// ── Change Notice Stream ────────────────────────────────────

export function streamChangeNotices(
  onBatch: (items: ChangeNoticeListItem[]) => void,
  onDone: (info: { durationMs: number }) => void,
  onError: (err: string) => void,
  opts?: { state?: string; subType?: string; top?: number },
): AbortController {
  const params = new URLSearchParams()
  if (opts?.state) params.set('state', opts.state)
  if (opts?.subType) params.set('sub_type', opts.subType)
  if (opts?.top) params.set('top', String(opts.top))

  const controller = new AbortController()

  fetch(`${BASE}/changes/change_notices/stream?${params}`, {
    credentials: 'include',
    signal: controller.signal,
    headers: { Accept: 'text/event-stream' },
  })
    .then(async (resp) => {
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}))
        throw new Error(body.error || body.detail || `HTTP ${resp.status}`)
      }
      const reader = resp.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''
      let doneReceived = false

      const parseEvent = (raw: string) => {
        const lines = raw.trim().split('\n')
        let eventType = 'message'
        let data = ''
        for (const line of lines) {
          if (line.startsWith('event: ')) eventType = line.slice(7)
          else if (line.startsWith('data: ')) data += line.slice(6)
        }
        if (!data) return
        if (eventType === 'done') {
          doneReceived = true
          try { onDone(JSON.parse(data)) } catch { /* ignore */ }
        } else {
          try {
            const items = JSON.parse(data) as ChangeNoticeListItem[]
            if (items.length > 0) onBatch(items)
          } catch { /* ignore */ }
        }
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const segments = buffer.split('\n\n')
        buffer = segments.pop() || ''
        for (const seg of segments) {
          if (seg.trim()) parseEvent(seg)
        }
      }

      if (buffer.trim()) parseEvent(buffer)
      if (!doneReceived) onDone({ durationMs: 0 })
    })
    .catch((err) => {
      if (err?.name !== 'AbortError') {
        onError(err instanceof Error ? err.message : String(err))
      }
    })

  return controller
}

// ── WorkItems ───────────────────────────────────────────────

export async function listWorkItems(): Promise<WorkItemListResponse> {
  return request<WorkItemListResponse>(`${BASE}/workitems`)
}

export async function createWorkItem(cnData: {
  number: string
  name?: string
  subType?: string
  state?: string
  objectId?: string
}): Promise<WorkItem> {
  return request<WorkItem>(`${BASE}/workitems`, {
    method: 'POST',
    body: JSON.stringify(cnData),
  })
}

export async function getWorkItem(id: string): Promise<WorkItem> {
  return request<WorkItem>(`${BASE}/workitems/${encodeURIComponent(id)}`)
}

export async function updateWorkItem(
  id: string,
  updates: Partial<Pick<WorkItem, 'resultingParts' | 'selectedPart' | 'bomData' | 'bomColumns' | 'status'>>,
): Promise<WorkItem> {
  return request<WorkItem>(`${BASE}/workitems/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  })
}

export async function deleteWorkItem(id: string): Promise<void> {
  await request<{ ok: boolean }>(`${BASE}/workitems/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  })
}

export async function addWorkItemStep(
  id: string,
  step: string,
  data?: Record<string, unknown>,
): Promise<WorkItem> {
  return request<WorkItem>(`${BASE}/workitems/${encodeURIComponent(id)}/steps`, {
    method: 'POST',
    body: JSON.stringify({ step, data: data || {} }),
  })
}
