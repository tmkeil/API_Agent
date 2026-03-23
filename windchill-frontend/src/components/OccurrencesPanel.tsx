import { useCallback, useState, type FormEvent } from 'react'
import { getOccurrences } from '../api/client'
import type { OccurrencesResponse } from '../api/types'

/**
 * OccurrencesPanel — "Wo kommt Code XABC vor?"
 *
 * Standalone-Suchkomponente die alle Vorkommen eines Codes in Windchill anzeigt.
 * Nutzt den /api/parts/{code}/occurrences Endpoint.
 * Geplant als Tab oder Panel auf der Detailseite und als Baustein fuer den AI Agent.
 */
export default function OccurrencesPanel() {
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<OccurrencesResponse | null>(null)
  const [error, setError] = useState('')

  const handleSubmit = useCallback(
    async (e: FormEvent) => {
      e.preventDefault()
      const q = code.trim()
      if (!q) return
      setLoading(true)
      setError('')
      setResult(null)
      try {
        const data = await getOccurrences(q)
        setResult(data)
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err)
        setError(msg || 'Fehler bei der Suche')
      } finally {
        setLoading(false)
      }
    },
    [code],
  )

  return (
    <div className="space-y-3">
      <h2 className="text-sm font-semibold text-gray-500">
        Code-Suche: „Wo kommt Code XABC vor?"
      </h2>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Code eingeben, z.B. XABC, BAL-1234, S2200*"
          aria-label="Code-Suche"
          className="flex-1 border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="submit"
          disabled={loading || !code.trim()}
          className="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Suche...' : 'Vorkommen suchen'}
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">{error}</div>
      )}

      {result && (
        <div className="space-y-2">
          {/* Summary */}
          <div className="flex items-center gap-3 text-sm">
            <span className="font-mono font-semibold">{result.code}</span>
            <span className="text-gray-500">
              {result.totalFound} Vorkommen gefunden
            </span>
            <span className="text-gray-400 text-xs">
              ({result.timing.totalMs.toFixed(0)} ms
              {result.timing.fromCache ? ', Cache' : ''})
            </span>
          </div>

          {/* Results table */}
          {result.occurrences.length > 0 ? (
            <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-slate-500 text-xs">
                  <tr>
                    <th className="text-left px-4 py-2 font-medium">Nummer</th>
                    <th className="text-left px-4 py-2 font-medium">Name</th>
                    <th className="text-left px-4 py-2 font-medium">Version</th>
                    <th className="text-left px-4 py-2 font-medium">Status</th>
                    <th className="text-left px-4 py-2 font-medium">Verwendet in</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {result.occurrences.map((occ, i) => (
                    <tr key={occ.partId || i} className="hover:bg-slate-50">
                      <td className="px-4 py-2 font-mono text-slate-800">{occ.number}</td>
                      <td className="px-4 py-2 text-slate-500 truncate max-w-[200px]">
                        {occ.name}
                      </td>
                      <td className="px-4 py-2 text-slate-400">{occ.version}</td>
                      <td className="px-4 py-2">
                        <span
                          className={
                            occ.state === 'RELEASED'
                              ? 'text-emerald-600 font-medium'
                              : 'text-slate-500'
                          }
                        >
                          {occ.state}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-slate-500 text-xs">
                        {occ.usedInPart ? (
                          <span>
                            <span className="font-mono">{occ.usedInPart}</span>
                            {occ.usedInName && (
                              <span className="text-slate-400 ml-1">
                                ({occ.usedInName})
                              </span>
                            )}
                          </span>
                        ) : occ.pathHint ? (
                          <span className="text-slate-400">{occ.pathHint}</span>
                        ) : (
                          <span className="text-slate-300">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-sm text-slate-500 bg-amber-50 border border-amber-200 rounded p-3">
              Keine Vorkommen gefunden.
            </div>
          )}
        </div>
      )}
    </div>
  )
}
