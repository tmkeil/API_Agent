import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getOccurrences } from '../../api/client'
import type { PartOccurrence } from '../../api/types'

interface Props {
  partCode: string
}

/** Occurrences tab — shows all occurrences of a part number (same code, different versions/contexts). */
export default function OccurrencesTab({ partCode }: Props) {
  const [items, setItems] = useState<PartOccurrence[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const resp = await getOccurrences(partCode)
      if (signal?.aborted) return
      setItems(resp.occurrences)
    } catch (e: unknown) {
      if (signal?.aborted) return
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [partCode])

  useEffect(() => {
    const controller = new AbortController()
    load(controller.signal)
    return () => controller.abort()
  }, [load])

  if (loading) {
    return <p className="text-sm text-slate-500 animate-pulse py-4">Loading occurrences…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={() => load()} className="ml-3 underline">Retry</button>
      </div>
    )
  }

  if (items.length === 0) {
    return <p className="text-sm text-slate-400 py-4">No occurrences found.</p>
  }

  return (
    <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200">
          <tr>
            <th className="text-left px-3 py-2 font-medium">Number</th>
            <th className="text-left px-3 py-2 font-medium">Name</th>
            <th className="text-left px-3 py-2 font-medium">Version</th>
            <th className="text-left px-3 py-2 font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.map((o) => (
            <tr
              key={o.partId}
              onClick={() => navigate(`/detail/part/${encodeURIComponent(o.number)}`)}
              onKeyDown={(ev) => {
                if (ev.key === 'Enter' || ev.key === ' ') {
                  ev.preventDefault()
                  navigate(`/detail/part/${encodeURIComponent(o.number)}`)
                }
              }}
              role="link"
              tabIndex={0}
              className="cursor-pointer hover:bg-indigo-50 transition-colors"
            >
              <td className="px-3 py-2 font-mono text-indigo-600 whitespace-nowrap">{o.number}</td>
              <td className="px-3 py-2 text-slate-600 max-w-[300px] truncate">{o.name}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{o.version || '—'}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{o.state || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
