import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { searchPartsStream, checkCnPartResults } from '../api/client'
import type { PartSearchResult } from '../api/types'
import SearchBar, { type SearchMode } from '../components/SearchBar'
import AdvancedSearchPanel from '../components/AdvancedSearchPanel'
import { TYPE_KEY_MAP, formatDate, typeLabel, subtypeBadgeStyle } from '../utils/labels'

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
                className={`px-2.5 py-1 text-[11px] font-medium rounded border transition-colors ${
                  cnPartsFilter
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                    : 'bg-slate-50 text-slate-600 border-slate-300 hover:bg-slate-100'
                }`}
                title="Nur Change Notices anzeigen, die Part Resulting Items enthalten"
              >
                {cnCheckLoading ? (
                  <span className="animate-pulse">Prüfe CNs…</span>
                ) : cnPartsFilter ? (
                  '✓ Nur CNs mit Parts'
                ) : (
                  'Nur CNs mit Parts'
                )}
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
    </div>
  )
}