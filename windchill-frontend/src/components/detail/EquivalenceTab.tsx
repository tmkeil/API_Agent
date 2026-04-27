import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { diagnoseEquivalence, getPartEquivalence } from '../../api/client'
import type { EquivDiagnosticResponse } from '../../api/client'
import type {
  EquivPartRef,
  EquivalenceNetworkResponse,
  ObjectDetail,
} from '../../api/types'

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
  const [diag, setDiag] = useState<EquivDiagnosticResponse | null>(null)
  const [diagLoading, setDiagLoading] = useState(false)
  const [diagError, setDiagError] = useState<string | null>(null)

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

  async function runDiagnose() {
    setDiagLoading(true)
    setDiagError(null)
    setDiag(null)
    try {
      const r = await diagnoseEquivalence(detail.number)
      setDiag(r)
    } catch (e) {
      setDiagError(String((e as Error)?.message ?? e))
    } finally {
      setDiagLoading(false)
    }
  }

  const diagPanel = (
    <div className="bg-white rounded shadow-sm border border-amber-200 overflow-hidden">
      <div className="px-4 py-2.5 bg-amber-50 border-b border-amber-200 flex items-center justify-between gap-3">
        <div>
          <h3 className="text-xs font-semibold text-amber-700 uppercase tracking-wider">
            Equivalence-Pfad-Diagnose
          </h3>
          <p className="text-xs text-amber-600 mt-0.5">
            Probiert mehrere OData-Pfade und meldet Status / Treffer.
          </p>
        </div>
        <button
          onClick={runDiagnose}
          disabled={diagLoading}
          className="px-3 py-1.5 text-xs rounded border border-amber-300 bg-white hover:bg-amber-100 text-amber-800 disabled:opacity-50"
        >
          {diagLoading ? 'Prüfe …' : 'Pfade prüfen'}
        </button>
      </div>
      {diagError && (
        <div className="px-4 py-2 text-xs text-rose-600 bg-rose-50 border-b border-rose-200">
          {diagError}
        </div>
      )}
      {diag && (
        <div className="px-4 py-3 text-xs space-y-2">
          <div className="text-slate-500">
            partId: <span className="font-mono">{diag.partId}</span>
          </div>
          <table className="w-full">
            <thead>
              <tr className="text-slate-500">
                <th className="text-left font-medium py-1">Pfad</th>
                <th className="text-left font-medium py-1 w-20">HTTP</th>
                <th className="text-left font-medium py-1 w-20">OK</th>
                <th className="text-left font-medium py-1 w-20">Anzahl</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {diag.summary.map((r, i) => (
                <tr key={i}>
                  <td className="py-1 pr-2">{r.label}</td>
                  <td className="py-1 font-mono">{r.status ?? '—'}</td>
                  <td className="py-1">
                    {r.ok
                      ? <span className="text-emerald-600">✓</span>
                      : <span className="text-rose-600">✗</span>}
                  </td>
                  <td className="py-1">{r.count ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <details className="mt-2">
            <summary className="cursor-pointer text-slate-500 hover:text-slate-700">
              Roh-Antworten anzeigen
            </summary>
            <pre className="mt-2 p-2 bg-slate-50 border border-slate-200 rounded text-[10px] overflow-x-auto max-h-96">
              {JSON.stringify(diag.details, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  )

  if (loading) {
    return (
      <div className="space-y-3">
        {diagPanel}
        <div className="bg-white rounded shadow-sm border border-slate-200 p-6 text-center text-slate-400 text-sm">
          Lade Equivalence Network …
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-3">
        {diagPanel}
        <div className="bg-white rounded shadow-sm border border-rose-200 p-6 text-center text-rose-600 text-sm">
          Fehler beim Laden: {error}
        </div>
      </div>
    )
  }

  const pairs = data ? buildPairs(detail, data) : []
  const view = data?.selfView || String(detail.allAttributes?.['View'] ?? '')

  if (pairs.length === 0) {
    return (
      <div className="space-y-3">
        {diagPanel}
        <div className="bg-white rounded shadow-sm border border-slate-200 p-6 text-center text-slate-400">
          Keine Equivalence-Network-Einträge vorhanden.
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {diagPanel}
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
    </div>
  )
}

