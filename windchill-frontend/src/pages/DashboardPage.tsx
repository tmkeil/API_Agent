import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { searchPartsStream, checkCnPartResults, listChangeNotices } from '../api/client'
import type { PartSearchResult, ChangeNoticeListItem } from '../api/types'
import SearchBar, { type SearchMode } from '../components/SearchBar'
import AdvancedSearchPanel from '../components/AdvancedSearchPanel'
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

function startSearch(query: string, types?: string[], mode?: SearchMode) {
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
    { types, mode },
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

  // CN "has Part results" filter state
  const [cnPartsFilter, setCnPartsFilter] = useState(false)
  const [cnWithParts, setCnWithParts] = useState<Set<string>>(new Set())
  const [cnCheckLoading, setCnCheckLoading] = useState(false)
  const cnCheckRef = useRef<AbortController | null>(null)

  // ── CN Listing state ────────────────────────────────────
  const CN_PAGE_SIZE = 50
  const [cnItems, setCnItems] = useState<ChangeNoticeListItem[]>([])
  const [cnTotal, setCnTotal] = useState(0)
  const [cnLoading, setCnLoading] = useState(false)
  const [cnError, setCnError] = useState('')
  const [cnPage, setCnPage] = useState(0)
  const [cnStateFilter, setCnStateFilter] = useState('')
  const [cnErpOnly, setCnErpOnly] = useState(false)
  const [cnOnlyWithParts, setCnOnlyWithParts] = useState(false)
  const [cnWithPartsSet, setCnWithPartsSet] = useState<Set<string>>(new Set())
  const [cnPartsCheckLoading, setCnPartsCheckLoading] = useState(false)

  const loadCns = useCallback(async (p: number) => {
    setCnLoading(true)
    setCnError('')
    try {
      const resp = await listChangeNotices({
        state: cnStateFilter,
        subType: cnErpOnly ? 'ERP Transfer' : '',
        top: CN_PAGE_SIZE,
        skip: p * CN_PAGE_SIZE,
      })
      setCnItems(resp.items)
      setCnTotal(resp.totalCount)
      setCnPage(p)
    } catch (e: unknown) {
      setCnError((e as Error).message || 'Fehler beim Laden')
    } finally {
      setCnLoading(false)
    }
  }, [cnStateFilter, cnErpOnly])

  // Load CNs when switching to CN mode or when filters change
  useEffect(() => {
    if (mode === 'cn') loadCns(0)
  }, [mode, loadCns])

  const cnTotalPages = Math.ceil(cnTotal / CN_PAGE_SIZE)

  // Check which CNs (on current page) have Part resulting items
  const handleCnPartsToggle = useCallback(async () => {
    if (cnOnlyWithParts) {
      setCnOnlyWithParts(false)
      return
    }
    setCnPartsCheckLoading(true)
    try {
      const numbers = cnItems.map((cn) => cn.number)
      const resp = await checkCnPartResults(numbers)
      setCnWithPartsSet(new Set(resp.withParts))
      setCnOnlyWithParts(true)
    } catch {
      // silently fail
    } finally {
      setCnPartsCheckLoading(false)
    }
  }, [cnOnlyWithParts, cnItems])

  // Reset "mit Parts" filter when CN data changes
  useEffect(() => {
    setCnOnlyWithParts(false)
    setCnWithPartsSet(new Set())
  }, [cnItems])

  const cnDisplayItems = cnOnlyWithParts
    ? cnItems.filter((cn) => cnWithPartsSet.has(cn.number))
    : cnItems

  // ── Search ──────────────────────────────────────────────

  const handleSearch = useCallback((query: string, mode?: SearchMode) => {
    // Persist query in URL so "Back" restores state
    setSearchParams(query ? { q: query } : {}, { replace: true })
    startSearch(query, activeTypes.length > 0 ? activeTypes : undefined, mode)
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

  // ── Render ─────────────────────────────────────────────

  return (
    <div className="space-y-4">
      {/* Mode Toggle */}
      <div className="flex items-center gap-1 bg-slate-100 rounded-lg p-0.5 w-fit">
        <button
          onClick={() => setSearchParams(mode === 'search' ? {} : {}, { replace: true })}
          className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
            mode === 'search'
              ? 'bg-white text-slate-800 shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Suche
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
      </div>

      {/* ── Search Mode ─────────────────────────────────── */}
      {mode === 'search' && (
        <>
      {/* Search */}
      <section>
        <SearchBar
          onSearch={handleSearch}
          loading={searching}
          initialQuery={urlQuery}
          placeholder="Suchen — Nummer, Name oder Wildcard (z.B. S2200*, Z03*, *287364)"
        />
        {/* Advanced Search Panel */}
        <AdvancedSearchPanel
          contexts={WINDCHILL_CONTEXTS}
          onResults={(items) => {
            // Inject advanced search results into the store
            abortSearch()
            _store = { query: _store.query, results: items, searching: false, done: true, error: '', durationMs: 0 }
            _notify()
          }}
          onError={(msg) => {
            abortSearch()
            _store = { query: _store.query, results: [], searching: false, done: true, error: msg, durationMs: 0 }
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
          Keine Ergebnisse gefunden.
        </div>
      )}

      {/* Search results table */}
      {results.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
              {displayResults.length} Ergebnis{displayResults.length !== 1 ? 'se' : ''}
              {cnPartsFilter && displayResults.length !== results.length && (
                <span className="ml-1 text-emerald-500">(gefiltert von {results.length})</span>
              )}
              {searching && (
                <span className="ml-2 text-indigo-500 animate-pulse">
                  — Lade weitere…
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
                {cnCheckLoading ? '…' : cnPartsFilter ? '✓ mit Parts' : 'mit Parts'}
              </button>
            )}
          </div>

          <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
            <div className="overflow-auto" style={{ maxHeight: 'calc(100vh - 300px)' }}>
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200 sticky top-0 z-10">
                  <tr>
                    <th className="text-left px-3 py-2 font-medium">Typ</th>
                    <th className="text-left px-3 py-2 font-medium">Nummer</th>
                    <th className="text-left px-3 py-2 font-medium">Name</th>
                    <th className="text-left px-3 py-2 font-medium">Version</th>
                    <th className="text-left px-3 py-2 font-medium">Status</th>
                    <th className="text-left px-3 py-2 font-medium">Kontext</th>
                    <th className="text-left px-3 py-2 font-medium">Organization ID</th>
                    {allParts && <th className="text-left px-3 py-2 font-medium">Is Variant</th>}
                    {allParts && <th className="text-left px-3 py-2 font-medium">Classification</th>}
                    <th className="text-left px-3 py-2 font-medium">Geändert</th>
                    <th className="text-left px-3 py-2 font-medium">Erstellt</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {displayResults.map((r) => (
                    <tr
                      key={r.partId}
                      onClick={() => handleRowClick(r)}
                      className="cursor-pointer hover:bg-indigo-50 transition-colors"
                    >
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
          {/* CN Header */}
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
              {cnOnlyWithParts
                ? `${cnDisplayItems.length} von ${cnTotal} Change Notices (mit Parts)`
                : `${cnTotal} Change Notice${cnTotal !== 1 ? 's' : ''}`
              }
              {cnLoading && <span className="ml-2 text-indigo-500 animate-pulse">Lade…</span>}
            </h2>
            <div className="flex items-center gap-2">
              <button
                onClick={handleCnPartsToggle}
                disabled={cnPartsCheckLoading || cnItems.length === 0}
                className={`px-2 py-1 text-[11px] font-medium rounded border transition-colors disabled:opacity-40 ${
                  cnOnlyWithParts
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                    : 'bg-white text-slate-500 border-slate-300 hover:bg-slate-50'
                }`}
              >
                {cnPartsCheckLoading ? '…' : cnOnlyWithParts ? '✓ mit Parts' : 'mit Parts'}
              </button>
            </div>
          </div>

          {cnError && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
              {cnError}
            </div>
          )}

          {/* CN Table */}
          {cnItems.length > 0 && (
            <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
              <div className="overflow-auto" style={{ maxHeight: 'calc(100vh - 280px)' }}>
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200 sticky top-0 z-10">
                    <tr>
                      {/* Typ column with ERP filter */}
                      <th className="text-left px-3 py-2 font-medium">
                        <button
                          onClick={() => setCnErpOnly(!cnErpOnly)}
                          className={`flex items-center gap-1 transition-colors ${
                            cnErpOnly ? 'text-indigo-600' : 'text-slate-500 hover:text-slate-700'
                          }`}
                          title={cnErpOnly ? 'Alle Typen anzeigen' : 'Nur ERP Transfer'}
                        >
                          Typ
                          {cnErpOnly && <span className="text-[9px]">✕</span>}
                          <svg className="w-3 h-3 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                          </svg>
                        </button>
                      </th>
                      <th className="text-left px-3 py-2 font-medium">Nummer</th>
                      <th className="text-left px-3 py-2 font-medium">Name</th>
                      <th className="text-left px-3 py-2 font-medium">Version</th>
                      {/* Status column with filter */}
                      <th className="text-left px-3 py-2 font-medium">
                        <div className="relative inline-block">
                          <select
                            value={cnStateFilter}
                            onChange={(e) => setCnStateFilter(e.target.value)}
                            className={`appearance-none bg-transparent pr-4 cursor-pointer font-medium focus:outline-none ${
                              cnStateFilter ? 'text-indigo-600' : 'text-slate-500'
                            }`}
                          >
                            <option value="">Status ▾</option>
                            {CN_STATES.map((s) => (
                              <option key={s} value={s}>{s}</option>
                            ))}
                          </select>
                          {cnStateFilter && (
                            <button
                              onClick={(e) => { e.stopPropagation(); setCnStateFilter('') }}
                              className="absolute right-0 top-1/2 -translate-y-1/2 text-[9px] text-indigo-400 hover:text-indigo-600"
                              title="Filter zurücksetzen"
                            >✕</button>
                          )}
                        </div>
                      </th>
                      <th className="text-left px-3 py-2 font-medium">Ersteller</th>
                      <th className="text-left px-3 py-2 font-medium">Geändert</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {cnDisplayItems.map((cn) => (
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
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {!cnLoading && cnItems.length === 0 && !cnError && (
            <div className="text-sm text-slate-600 bg-amber-50 border border-amber-200 rounded p-3">
              Keine Change Notices gefunden.
            </div>
          )}

          {/* CN Paging */}
          {cnTotalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => loadCns(cnPage - 1)}
                disabled={cnPage === 0}
                className="px-2 py-1 text-xs rounded border border-slate-300 disabled:opacity-30 hover:bg-slate-100"
              >
                ←
              </button>
              <span className="text-xs text-slate-500">
                Seite {cnPage + 1} von {cnTotalPages}
              </span>
              <button
                onClick={() => loadCns(cnPage + 1)}
                disabled={cnPage >= cnTotalPages - 1}
                className="px-2 py-1 text-xs rounded border border-slate-300 disabled:opacity-30 hover:bg-slate-100"
              >
                →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}