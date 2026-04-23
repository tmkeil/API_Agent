import { useNavigate } from 'react-router-dom'
import type { ObjectDetail } from '../../api/types'

interface Props {
  detail: ObjectDetail
}

interface EquivEntry {
  number: string
  name: string
  version: string
  view: string
}

interface EquivPair {
  design: EquivEntry
  manufacturing: EquivEntry
}

function parseEntries(value: string): EquivEntry[] {
  if (!value) return []
  if (!value.includes('(')) {
    return value.split(',').map(s => s.trim()).filter(Boolean).map(num => ({
      number: num, name: '', version: '', view: 'Design',
    }))
  }
  const parts = value.split(',').map(s => s.trim())
  const all: EquivEntry[] = []
  let i = 0
  while (i + 3 < parts.length) {
    const number = parts[i]
    const name = parts[i + 1]
    const versionView = parts[i + 3]
    const vMatch = versionView.match(/^(.+?)\s*\((.+?)\)$/)
    all.push({
      number, name,
      version: vMatch ? vMatch[1] : versionView,
      view: vMatch ? vMatch[2] : '',
    })
    i += 4
  }
  return all
}

function buildPairs(detail: ObjectDetail): EquivPair[] {
  const attrs = detail.allAttributes || {}
  const down = String(attrs['BALDOWNSTREAM'] ?? '')
  const up = String(attrs['BALUPSTREAM'] ?? '')
  const self: EquivEntry = {
    number: detail.number,
    name: detail.name,
    version: detail.version,
    view: String(attrs['View'] ?? ''),
  }
  const isDesign = self.view === 'Design'
  const pairs: EquivPair[] = []

  if (isDesign && down) {
    const entries = parseEntries(down)
    const latest = new Map<string, EquivEntry>()
    for (const e of entries) {
      const ex = latest.get(e.number)
      if (!ex || e.version.localeCompare(ex.version) > 0) latest.set(e.number, e)
    }
    for (const mfg of latest.values()) pairs.push({ design: self, manufacturing: mfg })
  } else if (!isDesign && up) {
    const entries = parseEntries(up)
    const latest = new Map<string, EquivEntry>()
    for (const e of entries) {
      const ex = latest.get(e.number)
      if (!ex || e.version.localeCompare(ex.version) > 0) latest.set(e.number, e)
    }
    for (const dsn of latest.values()) pairs.push({ design: dsn, manufacturing: self })
  }
  return pairs
}

export default function EquivalenceTab({ detail }: Props) {
  const navigate = useNavigate()
  const pairs = buildPairs(detail)
  const view = String(detail.allAttributes?.['View'] ?? '')

  if (pairs.length === 0) {
    return (
      <div className="bg-white rounded shadow-sm border border-slate-200 p-6 text-center text-slate-400">
        Keine Equivalence-Network-Einträge vorhanden.
      </div>
    )
  }

  return (
    <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
      <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
        <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
          Equivalence Network
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Aktuelles Part: {detail.number} ({view || '?'}) — {pairs.length} Verknüpfung{pairs.length !== 1 ? 'en' : ''}
        </p>
      </div>

      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-50 text-slate-500 text-xs uppercase">
            <th className="px-4 py-2 text-left font-medium" colSpan={3}>Design</th>
            <th className="px-2 py-2 text-center font-medium w-8"></th>
            <th className="px-4 py-2 text-left font-medium" colSpan={3}>Manufacturing</th>
          </tr>
          <tr className="border-b border-slate-200 text-xs text-slate-400">
            <th className="px-4 py-1.5 text-left font-normal">Number</th>
            <th className="px-2 py-1.5 text-left font-normal">Name</th>
            <th className="px-2 py-1.5 text-left font-normal">Version</th>
            <th className="px-2 py-1.5 text-center font-normal"></th>
            <th className="px-4 py-1.5 text-left font-normal">Number</th>
            <th className="px-2 py-1.5 text-left font-normal">Name</th>
            <th className="px-2 py-1.5 text-left font-normal">Version</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {pairs.map((p, i) => (
            <tr key={i} className="hover:bg-slate-50">
              {/* Design */}
              <td className="px-4 py-2">
                <button
                  onClick={() => navigate(`/detail/part/${p.design.number}`)}
                  className="text-indigo-600 hover:text-indigo-800 hover:underline font-mono text-xs"
                >
                  {p.design.number}
                </button>
              </td>
              <td className="px-2 py-2 text-slate-600 text-xs truncate max-w-48">
                {p.design.name}
              </td>
              <td className="px-2 py-2 text-slate-400 text-xs">
                {p.design.version}
              </td>

              {/* Separator */}
              <td className="px-2 py-2 text-center text-slate-300 font-bold">—</td>

              {/* Manufacturing */}
              <td className="px-4 py-2">
                <button
                  onClick={() => navigate(`/detail/part/${p.manufacturing.number}`)}
                  className="text-indigo-600 hover:text-indigo-800 hover:underline font-mono text-xs"
                >
                  {p.manufacturing.number}
                </button>
              </td>
              <td className="px-2 py-2 text-slate-600 text-xs truncate max-w-48">
                {p.manufacturing.name}
              </td>
              <td className="px-2 py-2 text-slate-400 text-xs">
                {p.manufacturing.version}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
