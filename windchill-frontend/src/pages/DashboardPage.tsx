import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { searchPartsStream, checkCnPartResults, streamChangeNotices } from '../api/client'
import type { PartSearchResult, ChangeNoticeListItem } from '../api/types'
import SearchBar from '../components/SearchBar'
import AdvancedSearchPanel from '../components/AdvancedSearchPanel'
import RowActionsMenu, { type RowAction } from '../components/RowActionsMenu'
import BalluffExportModal from '../components/detail/BalluffExportModal'
import { TYPE_KEY_MAP, formatDate, typeLabel, subtypeBadgeStyle } from '../utils/labels'

const CN_STATES = ['OPEN', 'RESOLVED', 'CANCELLED', 'IMPLEMENTATION'] as const

// Bekannte Windchill-Kontexte (Folder-Toplevel)
const WINDCHILL_CONTEXTS = [
  'P - Design',
  'P - Electronical Components - Design',
  'P - Electronical Components - Manufacturing',
  'P - Manufacturing',
  'P - Mechanical Components',
  'P - Compliance and Conformity',
  'P - Enclosed Documentation',
]

// ── Background Search Store ────────────────────────────
// Der Stream läuft im Hintergrund weiter, auch wenn die Komponente
// unmounted wird (z.B. beim Wechsel zur Detailseite).

interface SearchStore {
  query: string
  results: PartSearchResult[]
  searching: boolean
  done: boolean
  error: string
  durationMs: number
}

let _store: SearchStore = {
  query: '', results: [], searching: false, done: false, error: '', durationMs: 0,
}
let _abortCtrl: AbortController | null = null
const _listeners = new Set<() => void>()

function _notify() {
  _listeners.forEach((fn) => fn())
}

function getStoreSnapshot(): SearchStore {
  return _store
}

function subscribeStore(cb: () => void): () => void {
  _listeners.add(cb)
  return () => { _listeners.delete(cb) }
}

function startSearch(query: string, types?: string[]) {
  // Abort previous stream
  _abortCtrl?.abort()

  _store = { query, results: [], searching: true, done: false, error: '', durationMs: 0 }
  _notify()

  const ctrl = searchPartsStream(
    query,
    (batch) => {
      _store = { ..._store, results: [..._store.results, ...batch] }
      _notify()
    },
    (info) => {
      _store = { ..._store, searching: false, done: true, durationMs: info.durationMs }
      _notify()
    },
    (msg) => {
      _store = { ..._store, searching: false, done: true, error: msg }
      _notify()
    },
    { types },
  )
  _abortCtrl = ctrl
}

function abortSearch() {
  _abortCtrl?.abort()
  _abortCtrl = null
  if (_store.searching) {
    _store = { ..._store, searching: false, done: true }
    _notify()
  }
}

// ── Background CN Store ────────────────────────────────
// Module-level singleton — persists across component mounts/unmounts
// (tab switches, navigation to detail page and back).
// Each unique (state, subType) filter combination is cached independently.
// The SSE stream continues even if the user navigates away.

interface CnStore {
  items: ChangeNoticeListItem[]
  loading: boolean
  done: boolean
  error: string
  durationMs: number
  /** Cache key = "state|subType" */
  filterKey: string
}

let _cnStore: CnStore = {
  items: [], loading: false, done: false, error: '', durationMs: 0, filterKey: '',
}
let _cnAbortCtrl: AbortController | null = null
const _cnListeners = new Set<() => void>()
// Per-filter-key cache: keeps completed results for instant tab switching
const _cnCache = new Map<string, ChangeNoticeListItem[]>()

function _cnNotify() {
  _cnListeners.forEach((fn) => fn())
}

function getCnSnapshot(): CnStore {
  return _cnStore
}

function subscribeCn(cb: () => void): () => void {
  _cnListeners.add(cb)
  return () => { _cnListeners.delete(cb) }
}

function startCnStream(state: string, subType: string) {
  const filterKey = `${state}|${subType}`

  // If the same filter is already loading/loaded, skip
  if (_cnStore.filterKey === filterKey && (_cnStore.loading || _cnStore.done)) {
    return
  }

  // Check cache
  const cached = _cnCache.get(filterKey)
  if (cached) {
    _cnStore = { items: cached, loading: false, done: true, error: '', durationMs: 0, filterKey }
    _cnNotify()
    return
  }

  // Abort any in-flight stream (different filter)
  _cnAbortCtrl?.abort()

  _cnStore = { items: [], loading: true, done: false, error: '', durationMs: 0, filterKey }
  _cnNotify()

  const ctrl = streamChangeNotices(
    (batch) => {
      _cnStore = { ..._cnStore, items: [..._cnStore.items, ...batch] }
      _cnNotify()
    },
    (info) => {
      _cnStore = { ..._cnStore, loading: false, done: true, durationMs: info.durationMs }
      // Cache completed results
      _cnCache.set(filterKey, _cnStore.items)
      _cnNotify()
    },
    (msg) => {
      _cnStore = { ..._cnStore, loading: false, done: true, error: msg }
      _cnNotify()
    },
    { state: state || undefined, subType: subType || undefined, top: 1000 },
  )
  _cnAbortCtrl = ctrl
}

function invalidateCnCache() {
  _cnCache.clear()
}

// ── Component ──

export default function DashboardPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()

  // Dashboard mode: 'search' or 'cn'
  const mode = searchParams.get('mode') === 'cn' ? 'cn' : 'search'

  // Restore query from URL (e.g. after navigating back from detail page)
  const urlQuery = searchParams.get('q') || ''

  // Subscribe to the background search store
  const searchState = useSyncExternalStore(subscribeStore, getStoreSnapshot)
  const { results, searching, done: searchDone, error } = searchState

  const [activeTypes] = useState<string[]>([])
  const hasRestoredRef = useRef(false)

  // Row-level action: open Balluff BOM export modal for a WTPart.
  const [balluffPart, setBalluffPart] = useState<string | null>(null)

  // CN "has Part results" filter state (for search results containing CNs)
  const [cnPartsFilter, setCnPartsFilter] = useState(false)
  const [cnWithParts, setCnWithParts] = useState<Set<string>>(new Set())
  const [cnCheckLoading, setCnCheckLoading] = useState(false)
  const cnCheckRef = useRef<AbortController | null>(null)

  // ── CN Store (module-level, streaming, cached) ──────────
  const cnState = useSyncExternalStore(subscribeCn, getCnSnapshot)
  const [cnStateFilter, setCnStateFilter] = useState('')
  const [cnErpOnly, setCnErpOnly] = useState(false)
  const [cnOnlyWithParts, setCnOnlyWithParts] = useState(false)
  const [cnWithPartsSet, setCnWithPartsSet] = useState<Set<string>>(new Set())
  const [cnPartsCheckLoading, setCnPartsCheckLoading] = useState(false)

  // Start/resume CN stream when entering CN mode or when filters change
  useEffect(() => {
    if (mode === 'cn') {
      startCnStream(cnStateFilter, cnErpOnly ? 'ERP Transfer' : '')
    }
  }, [mode, cnStateFilter, cnErpOnly])

  // Client-side filter for "mit Parts" only
  const cnFilteredItems = cnOnlyWithParts
    ? cnState.items.filter((cn) => cnWithPartsSet.has(cn.number))
    : cnState.items

  // Check which CNs have Part resulting items
  const handleCnPartsToggle = useCallback(async () => {
    if (cnOnlyWithParts) {
      setCnOnlyWithParts(false)
      return
    }
    setCnPartsCheckLoading(true)
    try {
      const numbers = cnState.items.map((cn) => cn.number)
      const resp = await checkCnPartResults(numbers)
      setCnWithPartsSet(new Set(resp.withParts))
      setCnOnlyWithParts(true)
    } catch {
      // silently fail
    } finally {
      setCnPartsCheckLoading(false)
    }
  }, [cnOnlyWithParts, cnState.items])

  // Reset client-side "with parts" filter when server-side filters change
  useEffect(() => {
    setCnOnlyWithParts(false)
    setCnWithPartsSet(new Set())
  }, [cnStateFilter, cnErpOnly])

  // ── Search ──────────────────────────────────────────────

  const handleSearch = useCallback((query: string) => {
    // Persist query in URL so "Back" restores state
    setSearchParams(query ? { q: query } : {}, { replace: true })
    startSearch(query, activeTypes.length > 0 ? activeTypes : undefined)
  }, [activeTypes, setSearchParams])

  // Restore search from URL params (e.g. after navigating back from detail page)
  // If the store already has results for this query, nothing happens.
  useEffect(() => {
    if (urlQuery && !hasRestoredRef.current) {
      hasRestoredRef.current = true
      if (searchState.query !== urlQuery || searchState.results.length === 0) {
        startSearch(urlQuery, activeTypes.length > 0 ? activeTypes : undefined)
      }
    }
  }, [urlQuery]) // eslint-disable-line react-hooks/exhaustive-deps

  function handleRowClick(r: PartSearchResult) {
    const tk = TYPE_KEY_MAP[r.objectType]
    if (tk) {
      navigate(`/detail/${tk}/${encodeURIComponent(r.number)}`)
    }
  }

  // ── Helpers ────────────────────────────────────────────

  // Show Part-only columns only when all results are Parts
  const allParts = results.length > 0 && results.every((r) => r.objectType === 'WTPart')

  // Check if results contain Change Notices
  const hasCns = results.some((r) => r.objectType === 'WTChangeOrder2')

  // Handle CN Part filter toggle
  const handleCnFilterToggle = useCallback(async () => {
    if (cnPartsFilter) {
      setCnPartsFilter(false)
      return
    }
    // Check which CNs have Part resulting items
    setCnCheckLoading(true)
    cnCheckRef.current?.abort()
    const ctrl = new AbortController()
    cnCheckRef.current = ctrl
    try {
      const cnNumbers = results
        .filter((r) => r.objectType === 'WTChangeOrder2')
        .map((r) => r.number)
      const resp = await checkCnPartResults(cnNumbers, ctrl.signal)
      setCnWithParts(new Set(resp.withParts))
      setCnPartsFilter(true)
    } catch (e: unknown) {
      if ((e as Error).name !== 'AbortError') {
        console.error('CN part check failed:', e)
      }
    } finally {
      setCnCheckLoading(false)
    }
  }, [cnPartsFilter, results])

  // Reset filter when results change
  useEffect(() => {
    setCnPartsFilter(false)
    setCnWithParts(new Set())
  }, [searchState.query])

  // Apply CN filter to results
  const displayResults = cnPartsFilter
    ? results.filter((r) => r.objectType !== 'WTChangeOrder2' || cnWithParts.has(r.number))
    : results

  // Build the per-row action list. Kept local to DashboardPage so actions can
  // depend on component state (modals, navigation). Actions which do not
  // apply to a given row are simply omitted — RowActionsMenu hides the
  // trigger when the list is empty.
  const buildRowActions = useCallback((r: PartSearchResult): RowAction[] => {
    const list: RowAction[] = []
    const typeKey = TYPE_KEY_MAP[r.objectType]
    const isPart = r.objectType === 'WTPart' || typeKey === 'part'
    if (isPart) {
      list.push({
        key: 'bom-transformer',
        label: 'Open BOM Transformer',
        description: 'Design ↔ Manufacturing dual tree view',
        onSelect: () => navigate(`/parts/${encodeURIComponent(r.number)}/transformer`),
      })
      list.push({
        key: 'balluff-bom',
        label: 'Balluff BOM export…',
        description: 'Open the BOM export modal for this part',
        onSelect: () => setBalluffPart(r.number),
      })
    }
    return list
  }, [navigate])

  // ── Render ─────────────────────────────────────────────

  return (
    <div className="space-y-4">
      {/* Mode Toggle */}
      {/* <div className="flex items-center gap-1 bg-slate-100 rounded-lg p-0.5 w-fit">
        <button
          onClick={() => setSearchParams(mode === 'search' ? {} : {}, { replace: true })}
          className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
            mode === 'search'
              ? 'bg-white text-slate-800 shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Search
        </button>
        <button
          onClick={() => setSearchParams({ mode: 'cn' }, { replace: true })}
          className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
            mode === 'cn'
              ? 'bg-white text-slate-800 shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Change Notices
        </button>
      </div> */}

      {/* ── Search Mode ─────────────────────────────────── */}
      {mode === 'search' && (
        <>
      {/* Search */}
      <section>
        <SearchBar
          onSearch={handleSearch}
          loading={searching}
          initialQuery={urlQuery}
          placeholder="Search — number, name or wildcard (e.g. S2200*, Z03*, *287364)"
        />
        {/* Advanced Search Panel */}
        <AdvancedSearchPanel
          contexts={WINDCHILL_CONTEXTS}
          onStart={() => {
            // Reset the result store for streaming advanced search
            abortSearch()
            _store = { query: '', results: [], searching: true, done: false, error: '', durationMs: 0 }
            _notify()
          }}
          onResults={(items) => {
            // Append each streamed batch
            _store = { ..._store, results: [..._store.results, ...items] }
            _notify()
          }}
          onDone={(info) => {
            _store = { ..._store, searching: false, done: true, durationMs: info.durationMs }
            _notify()
          }}
          onError={(msg) => {
            _store = { ..._store, searching: false, done: true, error: msg }
            _notify()
          }}
        />
      </section>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
          {error}
        </div>
      )}

      {/* Empty state */}
      {searchDone && results.length === 0 && (
        <div className="text-sm text-slate-600 bg-amber-50 border border-amber-200 rounded p-3">
          No results found.
        </div>
      )}

      {/* Search results table */}
      {results.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
              {displayResults.length} result{displayResults.length !== 1 ? 's' : ''}
              {cnPartsFilter && displayResults.length !== results.length && (
                <span className="ml-1 text-emerald-500">(filtered from {results.length})</span>
              )}
              {searching && (
                <span className="ml-2 text-indigo-500 animate-pulse">
                  — loading more…
                </span>
              )}
            </h2>
            {hasCns && !searching && (
              <button
                onClick={handleCnFilterToggle}
                disabled={cnCheckLoading}
                className={`px-2 py-1 text-[11px] font-medium rounded border transition-colors disabled:opacity-40 ${
                  cnPartsFilter
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                    : 'bg-white text-slate-500 border-slate-300 hover:bg-slate-50'
                }`}
              >
                {cnCheckLoading ? '…' : cnPartsFilter ? '✓ with parts' : 'with parts'}
              </button>
            )}
          </div>

          <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
            <div className="overflow-auto" style={{ maxHeight: 'calc(100vh - 300px)' }}>
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200 sticky top-0 z-10">
                  <tr>
                    <th className="px-2 py-2 font-medium w-10" aria-label="Actions"></th>
                    <th className="text-left px-3 py-2 font-medium">Type</th>
                    <th className="text-left px-3 py-2 font-medium">Number</th>
                    <th className="text-left px-3 py-2 font-medium">Name</th>
                    <th className="text-left px-3 py-2 font-medium">Version</th>
                    <th className="text-left px-3 py-2 font-medium">State</th>
                    <th className="text-left px-3 py-2 font-medium">Context</th>
                    <th className="text-left px-3 py-2 font-medium">Organization ID</th>
                    {allParts && <th className="text-left px-3 py-2 font-medium">Is Variant</th>}
                    {allParts && <th className="text-left px-3 py-2 font-medium">Classification</th>}
                    <th className="text-left px-3 py-2 font-medium">Modified</th>
                    <th className="text-left px-3 py-2 font-medium">Created</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {displayResults.map((r) => (
                    <tr
                      key={r.partId}
                      onClick={() => handleRowClick(r)}
                      className="cursor-pointer hover:bg-indigo-50 transition-colors"
                    >
                      <td className="px-1 py-1 whitespace-nowrap">
                        <RowActionsMenu actions={buildRowActions(r)} />
                      </td>
                      <td className="px-3 py-2 whitespace-nowrap">
                        <span className={`inline-block px-1.5 py-0.5 rounded border text-[10px] font-medium ${subtypeBadgeStyle(r.subType || typeLabel(r.objectType))}`}>
                          {typeLabel(r.objectType, r.subType)}
                        </span>
                      </td>
                      <td className="px-3 py-2 font-mono whitespace-nowrap">
                        <span className="text-indigo-600">{r.number}</span>
                      </td>
                      <td className="px-3 py-2 text-slate-600 max-w-[250px] truncate">{r.name}</td>
                      <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{r.version}</td>
                      <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{r.state}</td>
                      <td className="px-3 py-2 text-slate-400 whitespace-nowrap text-xs">{r.context || '—'}</td>
                      <td className="px-3 py-2 text-slate-500 whitespace-nowrap text-xs">{r.organizationId || '—'}</td>
                      {allParts && <td className="px-3 py-2 text-slate-500 whitespace-nowrap text-xs">{r.isVariant || '—'}</td>}
                      {allParts && <td className="px-3 py-2 text-slate-500 whitespace-nowrap text-xs">{r.classification || '—'}</td>}
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
        </>
      )}

      {/* ── Change Notices Mode ─────────────────────────── */}
      {mode === 'cn' && (
        <>
          {/* CN Header — progressive count */}
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
            {cnFilteredItems.length !== cnState.items.length
              ? `${cnFilteredItems.length} of ${cnState.items.length} Change Notices (filtered)`
              : `${cnState.items.length} Change Notice${cnState.items.length !== 1 ? 's' : ''}`
            }
            {cnState.loading && (
              <span className="ml-2 text-indigo-500 animate-pulse">
                — loading more…
              </span>
            )}
            {cnState.done && cnState.durationMs > 0 && (
              <span className="ml-2 text-slate-300 font-normal">
                ({Math.round(cnState.durationMs)}ms)
              </span>
            )}
          </h2>

          {cnState.error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
              {cnState.error}
            </div>
          )}

          {/* CN Table — renders progressively as data arrives;
              filter controls are always visible (fixes reset bug) */}
          <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
            <div className="overflow-auto" style={{ maxHeight: 'calc(100vh - 240px)' }}>
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200 sticky top-0 z-10">
                  <tr>
                    {/* Typ — click to toggle ERP filter */}
                    <th className="text-left px-3 py-2 font-medium">
                      <button
                        onClick={() => setCnErpOnly(!cnErpOnly)}
                        className={`flex items-center gap-1 transition-colors ${
                          cnErpOnly ? 'text-indigo-600' : 'text-slate-500 hover:text-slate-700'
                        }`}
                        title={cnErpOnly ? 'Clear filter' : 'Show only ERP Transfer'}
                      >
                        Type
                        {cnErpOnly && <span className="text-[9px]">✕</span>}
                        <svg className="w-3 h-3 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                        </svg>
                      </button>
                    </th>
                    <th className="text-left px-3 py-2 font-medium">Number</th>
                    <th className="text-left px-3 py-2 font-medium">Name</th>
                    <th className="text-left px-3 py-2 font-medium">Version</th>
                    {/* Status — dropdown filter */}
                    <th className="text-left px-3 py-2 font-medium">
                      <div className="relative inline-block">
                        <select
                          value={cnStateFilter}
                          onChange={(e) => setCnStateFilter(e.target.value)}
                          className={`appearance-none bg-transparent pr-4 cursor-pointer font-medium focus:outline-none ${
                            cnStateFilter ? 'text-indigo-600' : 'text-slate-500'
                          }`}
                        >
                          <option value="">State ▾</option>
                          {CN_STATES.map((s) => (
                            <option key={s} value={s}>{s}</option>
                          ))}
                        </select>
                        {cnStateFilter && (
                          <button
                            onClick={(e) => { e.stopPropagation(); setCnStateFilter('') }}
                            className="absolute right-0 top-1/2 -translate-y-1/2 text-[9px] text-indigo-400 hover:text-indigo-600"
                            title="Clear filter"
                          >✕</button>
                        )}
                      </div>
                    </th>
                    <th className="text-left px-3 py-2 font-medium">Creator</th>
                    <th className="text-left px-3 py-2 font-medium">Modified</th>
                    {/* Resulting Parts — click to filter */}
                    <th className="text-center px-3 py-2 font-medium w-10">
                      <button
                        onClick={handleCnPartsToggle}
                        disabled={cnPartsCheckLoading || cnState.items.length === 0}
                        className={`transition-colors disabled:opacity-30 ${
                          cnOnlyWithParts ? 'text-emerald-600' : 'text-slate-400 hover:text-slate-600'
                        }`}
                        title={cnOnlyWithParts ? 'Clear filter' : 'Only CNs with Part Resulting Items'}
                      >
                        {cnPartsCheckLoading ? (
                          <span className="animate-pulse text-[10px]">…</span>
                        ) : (
                          <svg className="w-3.5 h-3.5 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                          </svg>
                        )}
                      </button>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {cnFilteredItems.map((cn) => (
                    <tr
                      key={cn.objectId}
                      onClick={() => navigate(`/detail/change_notice/${encodeURIComponent(cn.number)}`)}
                      className="cursor-pointer hover:bg-indigo-50 transition-colors"
                    >
                      <td className="px-3 py-2 whitespace-nowrap">
                        <span className={`inline-block px-1.5 py-0.5 rounded border text-[10px] font-medium ${subtypeBadgeStyle(cn.subType || 'Change Notice')}`}>
                          {cn.subType || 'Change Notice'}
                        </span>
                      </td>
                      <td className="px-3 py-2 font-mono whitespace-nowrap">
                        <span className="text-indigo-600">{cn.number}</span>
                      </td>
                      <td className="px-3 py-2 text-slate-600 max-w-[300px] truncate" title={cn.name}>
                        {cn.name}
                      </td>
                      <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{cn.version}</td>
                      <td className="px-3 py-2 whitespace-nowrap">
                        <span className={`text-xs px-1.5 py-0.5 rounded ${
                          cn.state === 'OPEN' ? 'bg-green-50 text-green-700' :
                          cn.state === 'RESOLVED' ? 'bg-blue-50 text-blue-700' :
                          cn.state === 'CANCELLED' ? 'bg-red-50 text-red-700' :
                          'bg-slate-100 text-slate-600'
                        }`}>
                          {cn.state}
                        </span>
                      </td>
                      <td className="px-3 py-2 text-slate-400 whitespace-nowrap text-xs">{cn.createdBy}</td>
                      <td className="px-3 py-2 text-slate-400 whitespace-nowrap text-xs">{formatDate(cn.lastModified)}</td>
                      <td className="px-3 py-2 text-center">
                        {cnWithPartsSet.size > 0 && (
                          cnWithPartsSet.has(cn.number)
                            ? <span className="text-emerald-500 text-[10px]">●</span>
                            : <span className="text-slate-300 text-[10px]">○</span>
                        )}
                      </td>
                    </tr>
                  ))}
                  {cnFilteredItems.length === 0 && !cnState.loading && (
                    <tr>
                      <td colSpan={8} className="px-3 py-8 text-center text-sm text-slate-400">
                        No Change Notices found.
                        {(cnStateFilter || cnErpOnly) && (
                          <button
                            onClick={() => { setCnStateFilter(''); setCnErpOnly(false) }}
                            className="ml-2 text-indigo-500 hover:text-indigo-700 underline"
                          >
                            Clear filters
                          </button>
                        )}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* ── Balluff BOM Export Modal (triggered from row actions) ── */}
      {balluffPart && (
        <BalluffExportModal
          partNumber={balluffPart}
          onClose={() => setBalluffPart(null)}
        />
      )}
    </div>
  )
}
