import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getPartDocuments, getPartCadDocuments } from '../../api/client'
import type { DocumentNode } from '../../api/types'
import { subtypeBadgeStyle } from '../../utils/labels'

interface Props {
  partCode: string
}

/**
 * Combined documents tab — shows all documents grouped by category:
 *   1. Described By Documents (WTDocuments)
 *   2. CAD / Dynamic Documents (EPMDocuments)
 *
 * Replaces the separate "Dokumente" and "CAD" tabs with a single unified view.
 */
export default function AllDocumentsTab({ partCode }: Props) {
  const [describedDocs, setDescribedDocs] = useState<DocumentNode[]>([])
  const [cadDocs, setCadDocs] = useState<DocumentNode[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const [docsResp, cadResp] = await Promise.all([
        getPartDocuments(partCode, signal),
        getPartCadDocuments(partCode, signal),
      ])
      if (signal?.aborted) return
      setDescribedDocs(docsResp.documents)
      setCadDocs(cadResp.documents)
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
    return <p className="text-sm text-slate-500 animate-pulse py-4">Loading documents…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={() => load()} className="ml-3 underline">Retry</button>
      </div>
    )
  }

  const totalCount = describedDocs.length + cadDocs.length

  if (totalCount === 0) {
    return <p className="text-sm text-slate-400 py-4">No documents linked.</p>
  }

  return (
    <div className="space-y-4">
      {/* Described By Documents */}
      {describedDocs.length > 0 && (
        <DocSection
          title="Described By Documents"
          subtitle={`${describedDocs.length} Dokument${describedDocs.length !== 1 ? 'e' : ''}`}
          docs={describedDocs}
          navigate={navigate}
        />
      )}

      {/* CAD / Dynamic Documents */}
      {cadDocs.length > 0 && (
        <DocSection
          title="CAD / Dynamic Documents"
          subtitle={`${cadDocs.length} Dokument${cadDocs.length !== 1 ? 'e' : ''}`}
          docs={cadDocs}
          navigate={navigate}
        />
      )}
    </div>
  )
}

/** Reusable section showing a list of documents with a section header. */
function DocSection({
  title,
  subtitle,
  docs,
  navigate,
}: {
  title: string
  subtitle: string
  docs: DocumentNode[]
  navigate: ReturnType<typeof useNavigate>
}) {
  return (
    <div>
      <div className="flex items-baseline gap-2 mb-1.5">
        <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wide">{title}</h3>
        <span className="text-[10px] text-slate-400">{subtitle}</span>
      </div>
      <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200">
            <tr>
              <th className="text-left px-3 py-2 font-medium w-10">Typ</th>
              <th className="text-left px-3 py-2 font-medium">Number</th>
              <th className="text-left px-3 py-2 font-medium">Name</th>
              <th className="text-left px-3 py-2 font-medium">Version</th>
              <th className="text-left px-3 py-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {docs.map((d) => {
              const typeKey =
                d.type === 'EPMDocument' || d.type === 'CADDocument'
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
                  <td className="px-3 py-2 whitespace-nowrap">
                    <span className={`inline-block border px-1 rounded text-[10px] font-medium ${subtypeBadgeStyle(d.subType || d.type)}`}>
                      {d.subType || (d.type === 'EPMDocument' ? 'CAD' : 'Doc')}
                    </span>
                  </td>
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
    </div>
  )
}
