
abc1
windchill-frontend/src/api/types.ts
// TypeScript types matching backend DTOs

export interface TimingInfo {
  total_ms: number
  wrs_ms: number
  cache_hits: number
  from_cache: boolean
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
  part_id: string
  number: string
  name: string
  version: string
  state: string
  used_in_part: string | null
  used_in_name: string | null
  path_hint: string | null
}

export interface OccurrencesResponse {
  code: string
  total_found: number
  occurrences: PartOccurrence[]
  timing: TimingInfo
}

// ── Detail Page ─────────────────────────────────────────────

export interface PartDetail {
  part_id: string
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
  total_found: number
  used_in: WhereUsedEntry[]
  timing: TimingInfo
  note: string
}

export interface DocumentListResponse {
  code: string
  total_found: number
  documents: DocumentNode[]
  timing: TimingInfo
}











abc1
windchill-frontend/src/App.tsx
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import DetailPage from './pages/DetailPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen text-gray-500">Laden...</div>
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

function AppRoutes() {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen text-gray-500">Laden...</div>

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to="/" replace /> : <LoginPage />}
      />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/detail/:typeKey/:code" element={<DetailPage />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}














abc1
windchill-frontend/src/components/BomTreeNode.tsx
import { useCallback, useState } from 'react'
import { getBomChildren } from '../api/client'
import type { BomTreeNode, DocumentNode } from '../api/types'

interface Props {
  node: BomTreeNode
  depth: number
}

export default function BomTreeNodeComponent({ node, depth }: Props) {
  const hasInitialChildren = (node.children && node.children.length > 0) || node.childrenLoaded || false
  const [expanded, setExpanded] = useState(depth === 0)
  const [children, setChildren] = useState<BomTreeNode[]>(
    node.children || [],
  )
  const [documents, setDocuments] = useState<DocumentNode[]>(
    node.documents || [],
  )
  const [cadDocuments, setCadDocuments] = useState<DocumentNode[]>(
    node.cadDocuments || [],
  )
  const [loaded, setLoaded] = useState(hasInitialChildren)
  const [loading, setLoading] = useState(false)

  const toggle = useCallback(async () => {
    // Already expanded → just collapse
    if (expanded) {
      setExpanded(false)
      return
    }

    // Need to fetch children first?
    if (!loaded && node.hasChildren && node.partId) {
      setLoading(true)
      try {
        const resp = await getBomChildren(node.partId)
        setChildren(resp.children)
        setDocuments(resp.documents)
        setCadDocuments(resp.cadDocuments)
        setLoaded(true)
      } catch {
        // Fetch failed → don't expand
        setLoading(false)
        return
      }
      setLoading(false)
    }

    // Expand
    setExpanded(true)
  }, [expanded, loaded, node.hasChildren, node.partId])

  const stateColor = 'text-slate-500'

  return (
    <div style={{ marginLeft: depth > 0 ? 20 : 0 }}>
      {/* Node row */}
      <div
        className="flex items-center gap-2 py-1 group hover:bg-slate-50 rounded cursor-pointer select-none"
        onClick={toggle}
      >
        {/* Expand icon */}
        <span className="w-4 text-center text-slate-400 text-[11px] flex-shrink-0">
          {node.hasChildren ? (
            loading ? (
              <span className="animate-spin inline-block">⟳</span>
            ) : expanded ? (
              <svg className="w-3 h-3 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
            ) : (
              <svg className="w-3 h-3 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" /></svg>
            )
          ) : (
            <span className="text-slate-300">·</span>
          )}
        </span>

        {/* Type badge */}
        <span className="text-[10px] bg-slate-200 text-slate-600 px-1 rounded flex-shrink-0 font-medium">
          {node.type === 'WTPart' ? 'Part' : node.type}
        </span>

        {/* Number */}
        <span className="font-mono text-sm font-medium text-slate-800 whitespace-nowrap">
          {node.number}
        </span>

        {/* Name */}
        <span className="text-sm text-slate-500 truncate">{node.name}</span>

        {/* Version & State */}
        <span className="ml-auto flex items-center gap-2 text-xs flex-shrink-0">
          {node.quantity != null && (
            <span className="text-slate-400 font-mono">
              ×{node.quantity}
              {node.quantityUnit ? ` ${node.quantityUnit}` : ''}
            </span>
          )}
          <span className="text-slate-400">{node.version}</span>
          <span className={stateColor}>{node.state}</span>
        </span>
      </div>

      {/* Expanded content */}
      {expanded && (
        <div>
          {/* Documents */}
          {documents.length > 0 && (
            <div style={{ marginLeft: 20 }} className="mb-1">
              {documents.map((doc, i) => (
                <div
                  key={doc.docId || i}
                  className="flex items-center gap-2 py-0.5 text-xs text-slate-500"
                >
                  <span className="w-4" />
                  <span className="bg-amber-50 text-amber-700 border border-amber-200 px-1 rounded text-[10px] font-medium">
                    Doc
                  </span>
                  <span className="font-mono text-slate-600">{doc.number}</span>
                  <span className="truncate text-slate-400">{doc.name}</span>
                </div>
              ))}
            </div>
          )}

          {/* CAD Documents */}
          {cadDocuments.length > 0 && (
            <div style={{ marginLeft: 20 }} className="mb-1">
              {cadDocuments.map((doc, i) => (
                <div
                  key={doc.docId || i}
                  className="flex items-center gap-2 py-0.5 text-xs text-slate-500"
                >
                  <span className="w-4" />
                  <span className="bg-violet-50 text-violet-700 border border-violet-200 px-1 rounded text-[10px] font-medium">
                    CAD
                  </span>
                  <span className="font-mono text-slate-600">{doc.number}</span>
                  <span className="truncate text-slate-400">{doc.name}</span>
                </div>
              ))}
            </div>
          )}

          {/* Children */}
          {children.map((child) => (
            <BomTreeNodeComponent
              key={child.partId || child.number}
              node={child}
              depth={depth + 1}
            />
          ))}

          {loaded && children.length === 0 && documents.length === 0 && (
            <div
              style={{ marginLeft: 20 }}
              className="text-xs text-slate-400 italic py-1"
            >
              Keine Unterelemente
            </div>
          )}
        </div>
      )}
    </div>
  )
}














abc1
windchill-frontend/src/components/detail/CadTab.tsx
import { useCallback, useEffect, useState } from 'react'
import { getPartCadDocuments } from '../../api/client'
import type { DocumentNode } from '../../api/types'

interface Props {
  partCode: string
}

/** CAD Documents tab — EPMDocuments linked to a part. */
export default function CadTab({ partCode }: Props) {
  const [cads, setCads] = useState<DocumentNode[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const resp = await getPartCadDocuments(partCode)
      setCads(resp.documents)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [partCode])

  useEffect(() => { load() }, [load])

  if (loading) {
    return <p className="text-sm text-slate-500 animate-pulse py-4">CAD-Dokumente werden geladen…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={load} className="ml-3 underline">Erneut versuchen</button>
      </div>
    )
  }

  if (cads.length === 0) {
    return (
      <p className="text-sm text-slate-400 py-4">
        Keine CAD-Dokumente verknüpft.
      </p>
    )
  }

  return (
    <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200">
          <tr>
            <th className="text-left px-3 py-2 font-medium">Nummer</th>
            <th className="text-left px-3 py-2 font-medium">Name</th>
            <th className="text-left px-3 py-2 font-medium">Version</th>
            <th className="text-left px-3 py-2 font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {cads.map((c) => (
            <tr key={c.docId} className="hover:bg-slate-50">
              <td className="px-3 py-2 font-mono text-slate-800 whitespace-nowrap">{c.number}</td>
              <td className="px-3 py-2 text-slate-600 max-w-[300px] truncate">{c.name}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{c.version}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{c.state}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}















abc1
windchill-frontend/src/components/detail/DetailHeader.tsx
import type { ObjectDetail } from '../../api/types'

const TYPE_LABELS: Record<string, string> = {
  WTPart: 'Part',
  WTDocument: 'Dokument',
  EPMDocument: 'CAD-Dokument',
  WTChangeOrder2: 'Change Notice',
  WTChangeRequest2: 'Change Request',
  WTChangeIssue: 'Problem Report',
}

interface Props {
  detail: ObjectDetail
  onBack: () => void
}

export default function DetailHeader({ detail, onBack }: Props) {
  const typeBadge = TYPE_LABELS[detail.objectType] || detail.objectType

  return (
    <div className="flex items-start justify-between">
      <div className="min-w-0">
        <div className="flex items-center gap-3 mb-1">
          <button
            onClick={onBack}
            className="text-slate-400 hover:text-slate-600 transition-colors shrink-0"
            title="Zurück zur Suche"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 shrink-0">
            {typeBadge}
          </span>
          <h1 className="text-lg font-semibold text-slate-800 truncate">
            {detail.number}
          </h1>
          <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-500">
            {detail.state || '—'}
          </span>
        </div>
        <p className="text-sm text-slate-500 ml-8">
          {detail.name || '—'}
          <span className="mx-2 text-slate-300">|</span>
          Version {detail.version || '—'}.{detail.iteration || '—'}
          {detail.context && (
            <>
              <span className="mx-2 text-slate-300">|</span>
              {detail.context}
            </>
          )}
        </p>
      </div>
    </div>
  )
}















abc1
windchill-frontend/src/components/detail/DetailsTab.tsx
import type { ObjectDetail } from '../../api/types'

interface Props {
  detail: ObjectDetail
}

function formatDate(raw: string): string {
  if (!raw) return '—'
  try {
    const d = new Date(raw)
    if (isNaN(d.getTime())) return raw.substring(0, 10)
    return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
  } catch {
    return raw.substring(0, 10)
  }
}

const TYPE_LABELS: Record<string, string> = {
  WTPart: 'Part',
  WTDocument: 'Dokument',
  EPMDocument: 'CAD-Dokument',
  WTChangeOrder2: 'Change Notice',
  WTChangeRequest2: 'Change Request',
  WTChangeIssue: 'Problem Report',
}

/** Details tab — shows object master data. */
export default function DetailsTab({ detail }: Props) {
  const rows: [string, string][] = [
    ['Typ', TYPE_LABELS[detail.objectType] || detail.objectType],
    ['Nummer', detail.number],
    ['Name', detail.name],
    ['Version', detail.version],
    ['Iteration', detail.iteration],
    ['Status', detail.state],
    ['Identität', detail.identity],
    ['Kontext', detail.context],
    ['Zuletzt geändert', formatDate(detail.lastModified)],
    ['Erstellt', formatDate(detail.createdOn)],
    ['Objekt-ID', detail.objectId],
  ]

  return (
    <div className="bg-white rounded shadow-sm border border-slate-200">
      <table className="w-full text-sm">
        <tbody className="divide-y divide-slate-100">
          {rows.map(([label, value]) => (
            <tr key={label}>
              <td className="px-4 py-2.5 text-slate-400 font-medium w-44 whitespace-nowrap">
                {label}
              </td>
              <td className="px-4 py-2.5 text-slate-700">
                {value || '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}















abc1
windchill-frontend/src/components/detail/DocumentsTab.tsx
import { useCallback, useEffect, useState } from 'react'
import { getPartDocuments } from '../../api/client'
import type { DocumentNode } from '../../api/types'

interface Props {
  partCode: string
}

/** Documents tab — WTDocuments linked to a part. */
export default function DocumentsTab({ partCode }: Props) {
  const [docs, setDocs] = useState<DocumentNode[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const resp = await getPartDocuments(partCode)
      setDocs(resp.documents)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [partCode])

  useEffect(() => { load() }, [load])

  if (loading) {
    return <p className="text-sm text-slate-500 animate-pulse py-4">Dokumente werden geladen…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={load} className="ml-3 underline">Erneut versuchen</button>
      </div>
    )
  }

  if (docs.length === 0) {
    return (
      <p className="text-sm text-slate-400 py-4">
        Keine Dokumente verknüpft.
      </p>
    )
  }

  return (
    <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200">
          <tr>
            <th className="text-left px-3 py-2 font-medium">Nummer</th>
            <th className="text-left px-3 py-2 font-medium">Name</th>
            <th className="text-left px-3 py-2 font-medium">Version</th>
            <th className="text-left px-3 py-2 font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {docs.map((d) => (
            <tr key={d.docId} className="hover:bg-slate-50">
              <td className="px-3 py-2 font-mono text-slate-800 whitespace-nowrap">{d.number}</td>
              <td className="px-3 py-2 text-slate-600 max-w-[300px] truncate">{d.name}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{d.version}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{d.state}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}















abc1
windchill-frontend/src/components/detail/StructureTab.tsx
import { useCallback, useState } from 'react'
import { getBomRoot } from '../../api/client'
import type { BomTreeNode } from '../../api/types'
import BomTreeNodeComponent from '../BomTreeNode'

interface Props {
  partNumber: string
}

/** Structure/BOM tab — reuses existing BomTreeNode component. */
export default function StructureTab({ partNumber }: Props) {
  const [root, setRoot] = useState<BomTreeNode | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [loaded, setLoaded] = useState(false)

  const load = useCallback(async () => {
    if (loaded) return
    setLoading(true)
    setError('')
    try {
      const r = await getBomRoot(partNumber)
      setRoot(r)
      setLoaded(true)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [partNumber, loaded])

  // Auto-load on first render
  if (!loaded && !loading && !error) {
    load()
  }

  if (loading) {
    return <p className="text-sm text-slate-500 animate-pulse py-4">BOM wird geladen…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={() => { setLoaded(false); load() }} className="ml-3 underline">
          Erneut versuchen
        </button>
      </div>
    )
  }

  if (!root) return null

  return (
    <div
      className="bg-white rounded shadow-sm border border-slate-200 p-3 overflow-x-auto"
      style={{ maxHeight: '60vh', overflowY: 'auto' }}
    >
      <BomTreeNodeComponent node={root} depth={0} />
    </div>
  )
}















abc1
windchill-frontend/src/components/detail/WhereUsedTab.tsx
import { useCallback, useEffect, useState } from 'react'
import { getWhereUsed } from '../../api/client'
import type { WhereUsedEntry } from '../../api/types'
import { useNavigate } from 'react-router-dom'

interface Props {
  partCode: string
}

/** Where-Used tab — shows parent assemblies that reference this part. */
export default function WhereUsedTab({ partCode }: Props) {
  const [entries, setEntries] = useState<WhereUsedEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const resp = await getWhereUsed(partCode)
      setEntries(resp.used_in)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [partCode])

  useEffect(() => { load() }, [load])

  if (loading) {
    return <p className="text-sm text-slate-500 animate-pulse py-4">Einsatzverwendung wird geladen…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={load} className="ml-3 underline">Erneut versuchen</button>
      </div>
    )
  }

  if (entries.length === 0) {
    return (
      <p className="text-sm text-slate-400 py-4">
        Dieses Teil wird nirgends verwendet (kein Parent).
      </p>
    )
  }

  return (
    <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200">
          <tr>
            <th className="text-left px-3 py-2 font-medium">Nummer</th>
            <th className="text-left px-3 py-2 font-medium">Name</th>
            <th className="text-left px-3 py-2 font-medium">Version</th>
            <th className="text-left px-3 py-2 font-medium">Status</th>
            <th className="text-left px-3 py-2 font-medium">Menge</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {entries.map((e) => (
            <tr
              key={e.oid}
              onClick={() => navigate(`/detail/part/${encodeURIComponent(e.number)}`)}
              className="cursor-pointer hover:bg-slate-50 transition-colors"
            >
              <td className="px-3 py-2 font-mono text-indigo-600 hover:text-indigo-800 whitespace-nowrap">
                {e.number}
              </td>
              <td className="px-3 py-2 text-slate-600 max-w-[300px] truncate">{e.name}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{e.revision || '—'}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{e.state || '—'}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">
                {e.quantity != null ? `${e.quantity}${e.unit ? ' ' + e.unit : ''}` : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}















abc1
windchill-frontend/src/pages/DashboardPage.tsx
import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getApiLogs, searchParts } from '../api/client'
import type { ApiLogEntry, PartSearchResult } from '../api/types'
import SearchBar from '../components/SearchBar'

export default function DashboardPage() {
  const navigate = useNavigate()

  // Search state
  const [results, setResults] = useState<PartSearchResult[]>([])
  const [searching, setSearching] = useState(false)
  const [searchDone, setSearchDone] = useState(false)
  const [error, setError] = useState('')
  const [activeTypes, setActiveTypes] = useState<string[]>([])

  // API Log state
  const [logs, setLogs] = useState<ApiLogEntry[]>([])
  const [logOpen, setLogOpen] = useState(false)
  const logRef = useRef<HTMLDivElement>(null)

  // Poll API logs every 2.5s when the log panel is open
  useEffect(() => {
    if (!logOpen) return
    let cancelled = false
    const poll = async () => {
      try {
        const items = await getApiLogs(120)
        if (!cancelled) setLogs(items)
      } catch {
        /* ignore */
      }
    }
    poll()
    const id = setInterval(poll, 2500)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [logOpen])

  // ── Search ──────────────────────────────────────────────

  const handleSearch = useCallback(async (query: string) => {
    setError('')
    setSearching(true)
    setSearchDone(false)
    try {
      const items = await searchParts(query, 200, activeTypes.length > 0 ? activeTypes : undefined)
      setResults(items)
      // Single result → go directly to detail page
      if (items.length === 1) {
        const tk = TYPE_KEY_MAP[items[0].objectType]
        if (tk) {
          navigate(`/detail/${tk}/${encodeURIComponent(items[0].number)}`)
          return
        }
      }
    } catch (e: any) {
      setError(e.message)
      setResults([])
    } finally {
      setSearching(false)
      setSearchDone(true)
    }
  }, [activeTypes, navigate])

  function handleRowClick(r: PartSearchResult) {
    const tk = TYPE_KEY_MAP[r.objectType]
    if (tk) {
      navigate(`/detail/${tk}/${encodeURIComponent(r.number)}`)
    }
  }

  // ── Helpers ────────────────────────────────────────────

  function formatDate(raw: string): string {
    if (!raw) return '—'
    try {
      const d = new Date(raw)
      if (isNaN(d.getTime())) return raw.substring(0, 10)
      return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
    } catch {
      return raw.substring(0, 10)
    }
  }

  const TYPE_LABELS: Record<string, string> = {
    WTPart: 'Part',
    WTDocument: 'Dokument',
    EPMDocument: 'CAD',
    WTChangeOrder2: 'Change Notice',
    WTChangeRequest2: 'Change Request',
    WTChangeIssue: 'Problem Report',
  }

  /** Maps Windchill objectType → URL typeKey used for /detail/:typeKey/:code */
  const TYPE_KEY_MAP: Record<string, string> = {
    WTPart: 'part',
    WTDocument: 'document',
    EPMDocument: 'cad_document',
    WTChangeOrder2: 'change_notice',
    WTChangeRequest2: 'change_request',
    WTChangeIssue: 'problem_report',
  }

  const TYPE_FILTERS: { key: string; label: string }[] = [
    { key: 'part', label: 'Parts' },
    { key: 'document', label: 'Dokumente' },
    { key: 'cad_document', label: 'CAD' },
    { key: 'change_notice', label: 'Change Notices' },
    { key: 'change_request', label: 'Change Requests' },
    { key: 'problem_report', label: 'Problem Reports' },
  ]

  function toggleType(key: string) {
    setActiveTypes((prev) =>
      prev.includes(key) ? prev.filter((t) => t !== key) : [...prev, key],
    )
  }

  function typeLabel(raw: string): string {
    return TYPE_LABELS[raw] || raw
  }

  // ── Render ─────────────────────────────────────────────

  return (
    <div className="space-y-4">
      {/* Search */}
      <section>
        <SearchBar
          onSearch={handleSearch}
          loading={searching}
          placeholder="Suchen — Nummer, Name oder Wildcard (z.B. S2200*, Z03*, *287364)"
        />
        {/* Type filter chips */}
        <div className="flex flex-wrap gap-1.5 mt-2">
          {TYPE_FILTERS.map((tf) => (
            <button
              key={tf.key}
              onClick={() => toggleType(tf.key)}
              className={`px-2.5 py-0.5 rounded-full text-xs font-medium border transition-colors ${
                activeTypes.includes(tf.key)
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'bg-white text-slate-500 border-slate-200 hover:border-slate-400'
              }`}
            >
              {tf.label}
            </button>
          ))}
          {activeTypes.length > 0 && (
            <button
              onClick={() => setActiveTypes([])}
              className="px-2 py-0.5 text-xs text-slate-400 hover:text-slate-600"
            >
              ✕ Alle
            </button>
          )}
        </div>
      </section>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
          {error}
        </div>
      )}

      {/* Empty state */}
      {searchDone && results.length === 0 && (
        <div className="text-sm text-slate-600 bg-amber-50 border border-amber-200 rounded p-3">
          Keine Ergebnisse gefunden.
        </div>
      )}

      {/* Search results table */}
      {results.length > 0 && (
        <section>
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
            {results.length} Ergebnis{results.length !== 1 ? 'se' : ''}
          </h2>

          <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200">
                  <tr>
                    <th className="text-left px-3 py-2 font-medium">Typ</th>
                    <th className="text-left px-3 py-2 font-medium">Nummer</th>
                    <th className="text-left px-3 py-2 font-medium">Name</th>
                    <th className="text-left px-3 py-2 font-medium">Version</th>
                    <th className="text-left px-3 py-2 font-medium">Status</th>
                    <th className="text-left px-3 py-2 font-medium">Kontext</th>
                    <th className="text-left px-3 py-2 font-medium">Geändert</th>
                    <th className="text-left px-3 py-2 font-medium">Erstellt</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {results.map((r) => (
                    <tr
                      key={r.partId}
                      onClick={() => handleRowClick(r)}
                      className="cursor-pointer hover:bg-indigo-50 transition-colors"
                    >
                      <td className="px-3 py-2 whitespace-nowrap">
                        <span className="inline-block px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600">
                          {typeLabel(r.objectType)}
                        </span>
                      </td>
                      <td className="px-3 py-2 font-mono whitespace-nowrap">
                        <span className="text-indigo-600">{r.number}</span>
                      </td>
                      <td className="px-3 py-2 text-slate-600 max-w-[250px] truncate">{r.name}</td>
                      <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{r.version}</td>
                      <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{r.state}</td>
                      <td className="px-3 py-2 text-slate-400 whitespace-nowrap text-xs">{r.context || '—'}</td>
                      <td className="px-3 py-2 text-slate-400 whitespace-nowrap text-xs">{formatDate(r.lastModified)}</td>
                      <td className="px-3 py-2 text-slate-400 whitespace-nowrap text-xs">{formatDate(r.createdOn)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      )}

      {/* API Log */}
      <section className="border-t border-slate-200 pt-4">
        <button
          onClick={() => setLogOpen((o) => !o)}
          className="text-xs text-slate-400 hover:text-slate-600 font-medium transition-colors"
        >
          {logOpen ? '▾' : '▸'} API Log ({logs.length})
        </button>
        {logOpen && (
          <div
            ref={logRef}
            className="mt-2 bg-slate-900 text-green-400 text-[11px] font-mono rounded p-3 overflow-y-auto"
            style={{ maxHeight: '240px' }}
          >
            {logs.length === 0 && (
              <p className="text-slate-500">Keine API-Aufrufe protokolliert.</p>
            )}
            {logs.map((entry, i) => {
              const ts = entry.timestamp?.substring(11, 23) || ''
              const src = (entry.source || '').toUpperCase().padEnd(10)
              const method = (entry.method || '').padEnd(5)
              const status = entry.status || 0
              const ms = entry.durationMs ?? 0
              const color =
                entry.source === 'cache'
                  ? 'text-yellow-400'
                  : status >= 400
                    ? 'text-red-400'
                    : 'text-green-400'
              return (
                <div key={i} className={color}>
                  [{ts}] [{src}] {method} {status} {ms}ms {entry.url}
                  {entry.note ? ` — ${entry.note}` : ''}
                </div>
              )
            })}
          </div>
        )}
      </section>
    </div>
  )
}














abc1
windchill-frontend/src/pages/DetailPage.tsx
import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getObjectDetail } from '../api/client'
import type { ObjectDetail } from '../api/types'
import DetailHeader from '../components/detail/DetailHeader'
import DetailsTab from '../components/detail/DetailsTab'
import StructureTab from '../components/detail/StructureTab'
import DocumentsTab from '../components/detail/DocumentsTab'
import CadTab from '../components/detail/CadTab'
import WhereUsedTab from '../components/detail/WhereUsedTab'

type TabKey = 'details' | 'structure' | 'documents' | 'cad' | 'whereUsed'

interface TabDef {
  key: TabKey
  label: string
}

/** Which tabs are available per Windchill type. */
const TABS_BY_TYPE: Record<string, TabDef[]> = {
  part: [
    { key: 'details', label: 'Details' },
    { key: 'structure', label: 'Struktur (BOM)' },
    { key: 'documents', label: 'Dokumente' },
    { key: 'cad', label: 'CAD' },
    { key: 'whereUsed', label: 'Where-Used' },
  ],
  document: [
    { key: 'details', label: 'Details' },
  ],
  cad_document: [
    { key: 'details', label: 'Details' },
  ],
  change_notice: [
    { key: 'details', label: 'Details' },
  ],
  change_request: [
    { key: 'details', label: 'Details' },
  ],
  problem_report: [
    { key: 'details', label: 'Details' },
  ],
}

const DEFAULT_TABS: TabDef[] = [{ key: 'details', label: 'Details' }]

export default function DetailPage() {
  const { typeKey = 'part', code } = useParams<{ typeKey: string; code: string }>()
  const navigate = useNavigate()

  const [detail, setDetail] = useState<ObjectDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<TabKey>('details')

  const load = useCallback(async () => {
    if (!code || !typeKey) return
    setLoading(true)
    setError('')
    try {
      const resp = await getObjectDetail(typeKey, code)
      setDetail(resp.detail)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [typeKey, code])

  useEffect(() => { load() }, [load])

  // Reset tab when navigating to a different object
  useEffect(() => {
    setActiveTab('details')
  }, [typeKey, code])

  const tabs = TABS_BY_TYPE[typeKey] || DEFAULT_TABS

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-sm text-slate-500 animate-pulse">Lade Daten…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-4">
          <p className="font-medium mb-1">Fehler beim Laden von „{code}"</p>
          <p>{error}</p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="text-sm text-indigo-600 hover:underline"
        >
          ← Zurück zur Suche
        </button>
      </div>
    )
  }

  if (!detail || !code) return null

  return (
    <div className="space-y-4">
      {/* Header */}
      <DetailHeader detail={detail} onBack={() => navigate('/')} />

      {/* Tab bar */}
      <nav className="border-b border-slate-200">
        <div className="flex gap-0 -mb-px">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Tab content */}
      <div>
        {activeTab === 'details' && <DetailsTab detail={detail} />}
        {activeTab === 'structure' && <StructureTab partNumber={detail.number} />}
        {activeTab === 'documents' && <DocumentsTab partCode={code} />}
        {activeTab === 'cad' && <CadTab partCode={code} />}
        {activeTab === 'whereUsed' && <WhereUsedTab partCode={code} />}
      </div>
    </div>
  )
}















abc1
windchill-frontend/src/pages/LoginPage.tsx
import { useEffect, useState, type FormEvent } from 'react'
import { getSystems } from '../api/client'
import type { SystemInfo } from '../api/types'
import { useAuth } from '../contexts/AuthContext'

// Hardcoded fallback so the dropdown always works, even when the API is unreachable.
const FALLBACK_SYSTEMS: SystemInfo[] = [
  { key: 'dev',  label: 'DEV — Entwicklung',  url: 'https://plm-dev.neuhausen.balluff.net/Windchill' },
  { key: 'test', label: 'TEST — Test',         url: 'https://plm-test.neuhausen.balluff.net/Windchill' },
  { key: 'prod', label: 'PROD — Produktion',  url: 'https://plm-prod.neuhausen.balluff.net/Windchill' },
]

export default function LoginPage() {
  const { login, error } = useAuth()
  const [systems, setSystems] = useState<SystemInfo[]>(FALLBACK_SYSTEMS)
  const [system, setSystem] = useState('dev')         // DEV pre-selected
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    // Enrich labels from API if available; fall back silently
    getSystems()
      .then((s) => {
        if (s.length > 0) {
          setSystems(s)
          const hasdev = s.find((x) => x.key === 'dev')
          setSystem(hasdev ? 'dev' : s[0].key)
        }
      })
      .catch(() => { /* keep FALLBACK_SYSTEMS */ })
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await login(system, username, password)
    } catch {
      // error is set in context
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <form
        onSubmit={handleSubmit}
        className="bg-white shadow-lg rounded-lg p-8 w-full max-w-sm border border-slate-200"
      >
        <h1 className="text-lg font-semibold text-center text-slate-800 mb-6">
          Windchill API
        </h1>

        {error && (
          <div className="bg-red-50 text-red-700 text-sm rounded p-2 mb-4">
            {error}
          </div>
        )}

        <label className="block text-sm font-medium text-slate-700 mb-1">
          Windchill-Umgebung
        </label>
        <select
          value={system}
          onChange={(e) => setSystem(e.target.value)}
          className="w-full border border-slate-300 rounded px-3 py-2 mb-4 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          {systems.map((s) => (
            <option key={s.key} value={s.key}>
              {s.label}
            </option>
          ))}
        </select>

        <label className="block text-sm font-medium text-slate-700 mb-1">Benutzer</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full border border-slate-300 rounded px-3 py-2 mb-4 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          autoComplete="off"
          autoFocus
          required
        />

        <label className="block text-sm font-medium text-slate-700 mb-1">Passwort</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full border border-slate-300 rounded px-3 py-2 mb-6 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          autoComplete="new-password"
          required
        />

        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-indigo-600 text-white font-medium py-2 rounded hover:bg-indigo-700 disabled:opacity-40 text-sm transition-colors"
        >
          {submitting ? 'Verbinde...' : 'Anmelden'}
        </button>
      </form>
    </div>
  )
}