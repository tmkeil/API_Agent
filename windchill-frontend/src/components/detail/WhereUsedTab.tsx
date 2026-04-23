import { useCallback, useEffect, useState } from 'react'
import { getWhereUsed } from '../../api/client'
import type { WhereUsedEntry } from '../../api/types'
import { useNavigate } from 'react-router-dom'

interface Props {
  partCode: string
}

/** Where-Used tab — shows parent assemblies that reference this part. */
export default function WhereUsedTab({ partCode }: Props) {
  const [entries, setEntries] = useState<WhereUsedEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const resp = await getWhereUsed(partCode, signal)
      if (signal?.aborted) return
      setEntries(resp.usedIn)
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
    return <p className="text-sm text-slate-500 animate-pulse py-4">Loading where-used…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={() => load()} className="ml-3 underline">Retry</button>
      </div>
    )
  }

  if (entries.length === 0) {
    return (
      <p className="text-sm text-slate-400 py-4">
        Dieses Teil wird nirgends verwendet (kein Parent).
      </p>
    )
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
            <th className="text-left px-3 py-2 font-medium">Quantity</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {entries.map((e) => (
            <tr
              key={e.oid}
              onClick={() => navigate(`/detail/part/${encodeURIComponent(e.number)}`)}
              onKeyDown={(ev) => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); navigate(`/detail/part/${encodeURIComponent(e.number)}`) } }}
              role="link"
              tabIndex={0}
              className="cursor-pointer hover:bg-slate-50 transition-colors"
            >
              <td className="px-3 py-2 font-mono text-indigo-600 hover:text-indigo-800 whitespace-nowrap">
                {e.number}
              </td>
              <td className="px-3 py-2 text-slate-600 max-w-[300px] truncate">{e.name}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{e.revision || '—'}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{e.state || '—'}</td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">
                {e.quantity != null ? `${e.quantity}${e.unit ? ' ' + e.unit : ''}` : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
