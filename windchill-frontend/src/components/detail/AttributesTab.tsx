import { useState } from 'react'
import type { ObjectDetail } from '../../api/types'

interface Props {
  detail: ObjectDetail
}

/** Attributes tab — shows all OData attributes from Windchill as a searchable key-value table. */
export default function AttributesTab({ detail }: Props) {
  const [filter, setFilter] = useState('')
  const attrs = detail.allAttributes || {}
  const entries = Object.entries(attrs)

  const filtered = filter
    ? entries.filter(([k, v]) => {
        const q = filter.toLowerCase()
        return k.toLowerCase().includes(q) || String(v).toLowerCase().includes(q)
      })
    : entries

  // Sort: alphabetically by key
  filtered.sort((a, b) => a[0].localeCompare(b[0]))

  if (entries.length === 0) {
    return <p className="text-sm text-slate-400 py-4">Keine zusätzlichen Attribute verfügbar.</p>
  }

  return (
    <div className="space-y-2">
      {/* Search filter */}
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Attribut filtern…"
          className="px-3 py-1.5 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 w-72"
        />
        <span className="text-xs text-slate-400">
          {filtered.length} / {entries.length} Attribute
        </span>
      </div>

      {/* Key-value table */}
      <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
        <div className="overflow-auto" style={{ maxHeight: '60vh' }}>
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200 sticky top-0 z-10">
              <tr>
                <th className="text-left px-3 py-2 font-medium w-72">Attribute</th>
                <th className="text-left px-3 py-2 font-medium">Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map(([key, value]) => (
                <tr key={key} className="hover:bg-slate-50/50">
                  <td className="px-3 py-2 text-slate-500 font-mono text-xs whitespace-nowrap">
                    {key}
                  </td>
                  <td className="px-3 py-2 text-slate-700">
                    {renderValue(value)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

/** Render attribute value with appropriate formatting. */
function renderValue(val: unknown): string {
  if (val === null || val === undefined) return '—'
  if (typeof val === 'boolean') return val ? 'Yes' : 'No'
  return String(val)
}
