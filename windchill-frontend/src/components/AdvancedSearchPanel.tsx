import { useCallback, useState } from 'react'
import { advancedSearch } from '../api/client'
import type { AdvancedSearchRequest, PartSearchResult } from '../api/types'

interface Props {
  contexts: string[]
  onResults: (items: PartSearchResult[]) => void
  onError: (msg: string) => void
}

const TYPE_OPTIONS = [
  { key: 'part', label: 'Part' },
  { key: 'document', label: 'Dokument' },
  { key: 'cad_document', label: 'CAD' },
  { key: 'change_notice', label: 'Change Notice' },
  { key: 'change_request', label: 'Change Request' },
  { key: 'problem_report', label: 'Problem Report' },
]

/**
 * Collapsible advanced search form with structured filters.
 * Renders below the quick search on the dashboard.
 */
export default function AdvancedSearchPanel({ contexts, onResults, onError }: Props) {
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(false)

  // Form fields
  const [query, setQuery] = useState('')
  const [selectedTypes, setSelectedTypes] = useState<string[]>([])
  const [context, setContext] = useState('')
  const [state, setState] = useState('')
  const [description, setDescription] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [limit, setLimit] = useState<number | ''>('')

  const toggleType = (key: string) => {
    setSelectedTypes((prev) =>
      prev.includes(key) ? prev.filter((t) => t !== key) : [...prev, key],
    )
  }

  const resetForm = useCallback(() => {
    setQuery('')
    setSelectedTypes([])
    setContext('')
    setState('')
    setDescription('')
    setDateFrom('')
    setDateTo('')
    setLimit('')
  }, [])

  const handleSubmit = useCallback(async () => {
    setBusy(true)
    onError('')
    try {
      const body: AdvancedSearchRequest = {}
      if (query.trim()) body.query = query.trim()
      if (selectedTypes.length > 0) body.types = selectedTypes
      if (context) body.context = context
      if (state.trim()) body.state = state.trim()
      if (description.trim()) body.description = description.trim()
      if (dateFrom) body.dateFrom = dateFrom
      if (dateTo) body.dateTo = dateTo
      if (limit && limit > 0) body.limit = limit

      const items = await advancedSearch(body)
      onResults(items)
    } catch (e: unknown) {
      onError(e instanceof Error ? e.message : String(e))
    } finally {
      setBusy(false)
    }
  }, [query, selectedTypes, context, state, description, dateFrom, dateTo, limit, onResults, onError])

  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen((o) => !o)}
        className="text-xs text-indigo-500 hover:text-indigo-700 font-medium transition-colors"
      >
        {open ? '▾ Erweiterte Suche ausblenden' : '▸ Erweiterte Suche'}
      </button>

      {open && (
        <div className="mt-2 bg-slate-50 border border-slate-200 rounded p-4 space-y-3">
          {/* Row 1: Query + State */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Nummer / Name</label>
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Suchbegriff"
                className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
              />
            </div>
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Status</label>
              <input
                value={state}
                onChange={(e) => setState(e.target.value)}
                placeholder="z.B. INWORK, RELEASED"
                className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
              />
            </div>
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Beschreibung</label>
              <input
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Substring"
                className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
              />
            </div>
          </div>

          {/* Row 2: Date range + Context + Limit */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Datum von</label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
              />
            </div>
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Datum bis</label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
              />
            </div>
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Kontext</label>
              <select
                value={context}
                onChange={(e) => setContext(e.target.value)}
                className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded bg-white focus:outline-none focus:ring-1 focus:ring-indigo-400"
              >
                <option value="">Alle</option>
                {contexts.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Limit</label>
              <input
                type="number"
                min={0}
                max={10000}
                value={limit}
                placeholder="kein Limit"
                onChange={(e) => {
                  const v = e.target.value
                  setLimit(v === '' ? '' : Math.max(0, Number(v)))
                }}
                className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
              />
            </div>
          </div>

          {/* Type chips */}
          <div>
            <label className="text-xs text-slate-500 mb-1 block">Typen</label>
            <div className="flex flex-wrap gap-1.5">
              {TYPE_OPTIONS.map((t) => (
                <button
                  key={t.key}
                  onClick={() => toggleType(t.key)}
                  className={`px-2.5 py-0.5 rounded-full text-xs font-medium border transition-colors ${
                    selectedTypes.includes(t.key)
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : 'bg-white text-slate-500 border-slate-200 hover:border-slate-400'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3 pt-1">
            <button
              onClick={handleSubmit}
              disabled={busy}
              className="px-4 py-1.5 text-sm font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {busy ? 'Suche…' : 'Erweiterte Suche starten'}
            </button>
            <button
              onClick={resetForm}
              className="text-xs text-slate-400 hover:text-slate-600"
            >
              Zurücksetzen
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
