import { useCallback, useState } from 'react'
import { advancedSearch } from '../api/client'
import type { AdvancedSearchRequest, PartSearchResult } from '../api/types'
import MultiSelect from './MultiSelect'

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

const DATE_FIELD_OPTIONS = [
  { value: 'modified', label: 'Geändert' },
  { value: 'created', label: 'Erstellt' },
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
  const [selectedContexts, setSelectedContexts] = useState<string[]>([])
  const [state, setState] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [dateField, setDateField] = useState('modified')
  const [limit, setLimit] = useState<number | ''>('')

  const contextOptions = contexts.map((c) => ({ key: c, label: c }))

  const resetForm = useCallback(() => {
    setQuery('')
    setSelectedTypes([])
    setSelectedContexts([])
    setState('')
    setDateFrom('')
    setDateTo('')
    setDateField('modified')
    setLimit('')
  }, [])

  const handleSubmit = useCallback(async () => {
    setBusy(true)
    onError('')
    try {
      const body: AdvancedSearchRequest = {}
      if (query.trim()) body.query = query.trim()
      if (selectedTypes.length > 0) body.types = selectedTypes
      if (selectedContexts.length > 0) body.contexts = selectedContexts
      if (state.trim()) body.state = state.trim()
      if (dateFrom) body.dateFrom = dateFrom
      if (dateTo) body.dateTo = dateTo
      if (dateFrom || dateTo) body.dateField = dateField
      if (limit && limit > 0) body.limit = limit

      const items = await advancedSearch(body)
      onResults(items)
    } catch (e: unknown) {
      onError(e instanceof Error ? e.message : String(e))
    } finally {
      setBusy(false)
    }
  }, [query, selectedTypes, selectedContexts, state, dateFrom, dateTo, dateField, limit, onResults, onError])

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
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
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
          </div>

          {/* Row 2: MultiSelect dropdowns (Types + Contexts) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <MultiSelect
              label="Typen"
              options={TYPE_OPTIONS}
              selected={selectedTypes}
              onChange={setSelectedTypes}
              placeholder="Alle Typen"
            />
            <MultiSelect
              label="Kontext"
              options={contextOptions}
              selected={selectedContexts}
              onChange={setSelectedContexts}
              placeholder="Alle Kontexte"
            />
          </div>

          {/* Row 3: Date field selector + Date range + Limit */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Datumsfeld</label>
              <select
                value={dateField}
                onChange={(e) => setDateField(e.target.value)}
                className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400 bg-white"
              >
                {DATE_FIELD_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-500 mb-1 block">{dateField === 'modified' ? 'Geändert von' : 'Erstellt von'}</label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
              />
            </div>
            <div>
              <label className="text-xs text-slate-500 mb-1 block">{dateField === 'modified' ? 'Geändert bis' : 'Erstellt bis'}</label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
              />
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
