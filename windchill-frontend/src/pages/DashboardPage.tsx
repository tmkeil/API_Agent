import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { clearApiLogs, getApiLogs, searchPartsStream } from '../api/client'
import type { ApiLogEntry, PartSearchResult } from '../api/types'
import SearchBar from '../components/SearchBar'
import AdvancedSearchPanel from '../components/AdvancedSearchPanel'
import { TYPE_FILTERS, TYPE_KEY_MAP, formatDate, typeLabel } from '../utils/labels'

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

// ── Component ──

export default function DashboardPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()

  // Restore query from URL (e.g. after navigating back from detail page)
  const urlQuery = searchParams.get('q') || ''

  // Subscribe to the background search store
  const searchState = useSyncExternalStore(subscribeStore, getStoreSnapshot)
  const { results, searching, done: searchDone, error } = searchState

  const [activeTypes, setActiveTypes] = useState<string[]>([])
  const hasRestoredRef = useRef(false)
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

  function toggleType(key: string) {
    setActiveTypes((prev) =>
      prev.includes(key) ? prev.filter((t) => t !== key) : [...prev, key],
    )
  }

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
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
            {results.length} Ergebnis{results.length !== 1 ? 'se' : ''}
            {searching && (
              <span className="ml-2 text-indigo-500 animate-pulse">
                — Lade weitere…
              </span>
            )}
          </h2>

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
        <div className="flex items-center gap-3">
          <button
            onClick={() => setLogOpen((o) => !o)}
            className="text-xs text-slate-400 hover:text-slate-600 font-medium transition-colors"
          >
            {logOpen ? '▾' : '▸'} API Log ({logs.length})
          </button>
          {logOpen && logs.length > 0 && (
            <button
              onClick={() => { setLogs([]); clearApiLogs().catch(() => {}) }}
              className="text-[10px] text-slate-400 hover:text-red-500 transition-colors"
            >
              ✕ Clear
            </button>
          )}
        </div>
        {logOpen && (
          <div
            ref={logRef}
            className="mt-2 bg-slate-900 text-green-400 text-[11px] font-mono rounded p-3 overflow-y-auto"
            style={{ height: '240px' }}
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