import { useCallback, useState } from 'react'
import { advancedSearch } from '../api/client'
import type { AdvancedSearchCriterion, AdvancedSearchRequest, PartSearchResult } from '../api/types'
import MultiSelect from './MultiSelect'

interface Props {
  contexts: string[]
  onResults: (items: PartSearchResult[]) => void
  onError: (msg: string) => void
}

const TYPE_OPTIONS = [
  { key: 'part', label: 'Part' },
  { key: 'document', label: 'Document' },
  { key: 'cad_document', label: 'CAD' },
  { key: 'change_notice', label: 'Change Notice' },
  { key: 'change_request', label: 'Change Request' },
  { key: 'problem_report', label: 'Problem Report' },
]

const DATE_FIELD_OPTIONS = [
  { value: 'modified', label: 'Modified' },
  { value: 'created', label: 'Created' },
]

type Criterion = AdvancedSearchCriterion & { id: number }

let _critIdSeq = 0
function _newCriterion(field: 'Number' | 'Name' = 'Number', value = ''): Criterion {
  _critIdSeq += 1
  return { id: _critIdSeq, field, value }
}

/**
 * Collapsible advanced search form with structured filters.
 * Renders below the quick search on the dashboard.
 */
export default function AdvancedSearchPanel({ contexts, onResults, onError }: Props) {
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(false)

  // Criteria list — at least one row, each with field + value.
  const [criteria, setCriteria] = useState<Criterion[]>([_newCriterion('Number', '')])
  const [combinator, setCombinator] = useState<'and' | 'or'>('and')

  const [selectedTypes, setSelectedTypes] = useState<string[]>([])
  const [selectedContexts, setSelectedContexts] = useState<string[]>([])
  const [state, setState] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [dateField, setDateField] = useState('modified')
  const [limit, setLimit] = useState<number | ''>('')

  const contextOptions = contexts.map((c) => ({ key: c, label: c }))

  const addCriterion = useCallback(() => {
    setCriteria((prev) => [...prev, _newCriterion('Number', '')])
  }, [])

  const removeCriterion = useCallback((id: number) => {
    setCriteria((prev) => (prev.length <= 1 ? prev : prev.filter((c) => c.id !== id)))
  }, [])

  const updateCriterion = useCallback((id: number, patch: Partial<AdvancedSearchCriterion>) => {
    setCriteria((prev) => prev.map((c) => (c.id === id ? { ...c, ...patch } : c)))
  }, [])

  const resetForm = useCallback(() => {
    setCriteria([_newCriterion('Number', '')])
    setCombinator('and')
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
      const cleaned = criteria
        .map((c) => ({ field: c.field, value: c.value.trim() }))
        .filter((c) => c.value.length > 0)
      if (cleaned.length > 0) {
        body.criteria = cleaned
        body.combinator = combinator
      }
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
  }, [criteria, combinator, selectedTypes, selectedContexts, state, dateFrom, dateTo, dateField, limit, onResults, onError])

  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen((o) => !o)}
        className="text-xs text-indigo-500 hover:text-indigo-700 font-medium transition-colors"
      >
        {open ? '▾ Hide advanced search' : '▸ Advanced search'}
      </button>

      {open && (
        <div className="mt-2 bg-slate-50 border border-slate-200 rounded p-4 space-y-3">
          {/* Criteria list */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs text-slate-500">Criteria</label>
              {criteria.length > 1 && (
                <div className="inline-flex rounded border border-slate-300 overflow-hidden text-[11px]">
                  {(['and', 'or'] as const).map((op) => (
                    <button
                      key={op}
                      type="button"
                      onClick={() => setCombinator(op)}
                      className={`px-2 py-0.5 transition-colors ${
                        combinator === op
                          ? 'bg-indigo-600 text-white'
                          : 'bg-white text-slate-500 hover:bg-slate-100'
                      }`}
                    >
                      {op.toUpperCase()}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <div className="space-y-1.5">
              {criteria.map((c, i) => (
                <div key={c.id} className="flex items-center gap-1.5">
                  <span className="text-[10px] text-slate-400 w-7 text-right select-none">
                    {i === 0 ? 'WHERE' : combinator.toUpperCase()}
                  </span>
                  <select
                    value={c.field}
                    onChange={(e) => updateCriterion(c.id, { field: e.target.value as 'Number' | 'Name' })}
                    className="px-2 py-1.5 text-sm border border-slate-300 rounded bg-white focus:outline-none focus:ring-1 focus:ring-indigo-400"
                  >
                    <option value="Number">Number</option>
                    <option value="Name">Name</option>
                  </select>
                  <input
                    value={c.value}
                    onChange={(e) => updateCriterion(c.id, { value: e.target.value })}
                    placeholder={
                      c.field === 'Number'
                        ? 'e.g. S2200*, *287364, BES* CI*'
                        : 'e.g. sensor, *connector*'
                    }
                    className="flex-1 px-2 py-1.5 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
                  />
                  <button
                    type="button"
                    onClick={() => removeCriterion(c.id)}
                    disabled={criteria.length <= 1}
                    title="Remove criterion"
                    className="w-7 h-7 flex items-center justify-center text-slate-400 hover:text-red-600 hover:bg-red-50 rounded disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-slate-400 transition-colors"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={addCriterion}
              className="mt-1.5 text-xs text-indigo-500 hover:text-indigo-700 font-medium"
            >
              + Add criterion
            </button>
          </div>

          {/* State */}
          <div>
            <label className="text-xs text-slate-500 mb-1 block">Status</label>
            <input
              value={state}
              onChange={(e) => setState(e.target.value)}
              placeholder="e.g. INWORK, RELEASED"
              className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>

          {/* Row 2: MultiSelect dropdowns (Types + Contexts) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <MultiSelect
              label="Types"
              options={TYPE_OPTIONS}
              selected={selectedTypes}
              onChange={setSelectedTypes}
              placeholder="All types"
            />
            <MultiSelect
              label="Context"
              options={contextOptions}
              selected={selectedContexts}
              onChange={setSelectedContexts}
              placeholder="All contexts"
            />
          </div>

          {/* Row 3: Date field selector + Date range + Limit */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Date field</label>
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
              <label className="text-xs text-slate-500 mb-1 block">{dateField === 'modified' ? 'Modified from' : 'Created from'}</label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
              />
            </div>
            <div>
              <label className="text-xs text-slate-500 mb-1 block">{dateField === 'modified' ? 'Modified to' : 'Created to'}</label>
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
                placeholder="no limit"
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
              {busy ? 'Searching…' : 'Run advanced search'}
            </button>
            <button
              onClick={resetForm}
              className="text-xs text-slate-400 hover:text-slate-600"
            >
              Reset
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
