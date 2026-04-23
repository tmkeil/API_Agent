import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { DocumentListResponse, DocumentNode } from '../../api/types'

interface Props {
  /** Display label for loading/empty states */
  label: string
  partCode: string
  /** API function to fetch documents */
  fetchFn: (code: string, signal?: AbortSignal) => Promise<DocumentListResponse>
  /** Badge text shown next to each document row */
  badge: string
  /** Tailwind classes for the badge */
  badgeClass: string
}

/**
 * Shared document list tab — used by both DocumentsTab and CadTab.
 * Parameterized by fetch function and display strings to avoid duplication.
 */
export default function DocumentListTab({ label, partCode, fetchFn, badge, badgeClass }: Props) {
  const [docs, setDocs] = useState<DocumentNode[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const resp = await fetchFn(partCode, signal)
      if (signal?.aborted) return
      setDocs(resp.documents)
    } catch (e: unknown) {
      if (signal?.aborted) return
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [partCode, fetchFn])

  useEffect(() => {
    const controller = new AbortController()
    load(controller.signal)
    return () => controller.abort()
  }, [load])

  if (loading) {
    return <p className="text-sm text-slate-500 animate-pulse py-4">Loading {label}…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={() => load()} className="ml-3 underline">Retry</button>
      </div>
    )
  }

  if (docs.length === 0) {
    return (
      <p className="text-sm text-slate-400 py-4">
        Keine {label} verknüpft.
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
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {docs.map((d) => {
            // Cross-type navigation: determine the typeKey from the document type
            const typeKey = d.type === 'EPMDocument' || d.type === 'CADDocument'
              ? 'cad_document'
              : 'document'
            return (
              <tr
                key={d.docId}
                onClick={() => navigate(`/detail/${typeKey}/${encodeURIComponent(d.number)}`)}
                onKeyDown={(ev) => {
                  if (ev.key === 'Enter' || ev.key === ' ') {
                    ev.preventDefault()
                    navigate(`/detail/${typeKey}/${encodeURIComponent(d.number)}`)
                  }
                }}
                role="link"
                tabIndex={0}
                className="cursor-pointer hover:bg-indigo-50 transition-colors"
              >
                <td className="px-3 py-2 font-mono text-indigo-600 whitespace-nowrap">{d.number}</td>
                <td className="px-3 py-2 text-slate-600 max-w-[300px] truncate">{d.name}</td>
                <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{d.version}</td>
                <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{d.state}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
