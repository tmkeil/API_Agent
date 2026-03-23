import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getReferencingParts } from '../../api/client'
import type { ReferencingPart } from '../../api/types'

interface Props {
  typeKey: string
  code: string
}

/** Tab showing parts that reference this document. */
export default function ReferencingPartsTab({ typeKey, code }: Props) {
  const [parts, setParts] = useState<ReferencingPart[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const resp = await getReferencingParts(typeKey, code, signal)
      if (signal?.aborted) return
      setParts(resp.parts)
    } catch (e: unknown) {
      if (signal?.aborted) return
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [typeKey, code])

  useEffect(() => {
    const controller = new AbortController()
    load(controller.signal)
    return () => controller.abort()
  }, [load])

  if (loading) {
    return <p className="text-sm text-slate-500 animate-pulse py-4">Referenzierende Parts werden geladen…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={() => load()} className="ml-3 underline">Erneut versuchen</button>
      </div>
    )
  }

  if (parts.length === 0) {
    return (
      <p className="text-sm text-slate-400 py-4">
        Keine Parts verweisen auf dieses Dokument.
      </p>
    )
  }

  return (
    <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200">
          <tr>
            <th className="text-left px-3 py-2 font-medium">Nummer</th>
            <th className="text-left px-3 py-2 font-medium">Name</th>
            <th className="text-left px-3 py-2 font-medium">Version</th>
            <th className="text-left px-3 py-2 font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {parts.map((p) => (
            <tr
              key={p.partId}
              onClick={() => navigate(`/detail/part/${encodeURIComponent(p.number)}`)}
              onKeyDown={(ev) => {
                if (ev.key === 'Enter' || ev.key === ' ') {
                  ev.preventDefault()
                  navigate(`/detail/part/${encodeURIComponent(p.number)}`)
                }
              }}
              role="link"
              tabIndex={0}
              className="cursor-pointer hover:bg-indigo-50 transition-colors"
            >
              <td className="px-3 py-2 font-mono text-indigo-600 whitespace-nowrap">{p.number}</td>
              <td className="px-3 py-2 text-slate-600 max-w-[300px] truncate">{p.name}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{p.version}.{p.iteration}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{p.state || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
