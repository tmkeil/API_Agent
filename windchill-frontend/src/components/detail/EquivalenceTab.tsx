import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getPartEquivalence } from '../../api/client'
import type { EquivPartRef, EquivalenceNetworkResponse, ObjectDetail } from '../../api/types'

interface Props {
  detail: ObjectDetail
}

interface EquivPair {
  design: EquivPartRef | SelfRef
  manufacturing: EquivPartRef | SelfRef
}

interface SelfRef {
  partId: string
  number: string
  name: string
  version: string
  view: string
  state: string
  organizationId: string
}

function selfFromDetail(detail: ObjectDetail): SelfRef {
  return {
    partId: detail.objectId,
    number: detail.number,
    name: detail.name,
    version: detail.version,
    view: String(detail.allAttributes?.['View'] ?? ''),
    state: detail.state,
    organizationId: '',
  }
}

function buildPairs(detail: ObjectDetail, data: EquivalenceNetworkResponse): EquivPair[] {
  const self = selfFromDetail(detail)
  const isDesign = (data.selfView || self.view) === 'Design'
  const pairs: EquivPair[] = []
  if (isDesign) {
    for (const m of data.down) pairs.push({ design: self, manufacturing: m })
  } else {
    for (const d of data.up) pairs.push({ design: d, manufacturing: self })
  }
  return pairs
}

export default function EquivalenceTab({ detail }: Props) {
  const navigate = useNavigate()
  const [data, setData] = useState<EquivalenceNetworkResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const ctrl = new AbortController()
    setLoading(true)
    setError(null)
    getPartEquivalence(detail.number, ctrl.signal)
      .then(setData)
      .catch(e => {
        if (e?.name !== 'AbortError') setError(String(e?.message ?? e))
      })
      .finally(() => setLoading(false))
    return () => ctrl.abort()
  }, [detail.number])

  if (loading) {
    return (
      <div className="bg-white rounded shadow-sm border border-slate-200 p-6 text-center text-slate-400 text-sm">
        Lade Equivalence Network …
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded shadow-sm border border-rose-200 p-6 text-center text-rose-600 text-sm">
        Fehler beim Laden: {error}
      </div>
    )
  }

  const pairs = data ? buildPairs(detail, data) : []
  const view = data?.selfView || String(detail.allAttributes?.['View'] ?? '')

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

