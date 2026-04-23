import { useCallback, useEffect, useState } from 'react'
import { getCadStructure, getCadStructureCsvUrl } from '../../api/client'
import type { CadStructureNode } from '../../api/types'

interface Props {
  cadCode: string
}

/**
 * CAD Assembly Structure tab — shows the hierarchical structure of a CAD document
 * with CSV export functionality.
 */
export default function CadStructureTab({ cadCode }: Props) {
  const [nodes, setNodes] = useState<CadStructureNode[]>([])
  const [loading, setLoading] = useState(false)
  const [loaded, setLoaded] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async (signal?: AbortSignal) => {
    if (loaded || loading) return
    setLoading(true)
    setError('')
    try {
      const resp = await getCadStructure(cadCode, signal)
      if (signal?.aborted) return
      setNodes(resp.nodes)
      setLoaded(true)
    } catch (e: unknown) {
      if (signal?.aborted) return
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [cadCode, loaded, loading])

  // Auto-load on mount
  useEffect(() => {
    const controller = new AbortController()
    load(controller.signal)
    return () => controller.abort()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  function handleCsvExport() {
    window.open(getCadStructureCsvUrl(cadCode), '_blank')
  }

  if (!loaded && !loading && !error) {
    return (
      <div className="py-6 text-center">
        <button
          onClick={() => load()}
          className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded hover:bg-indigo-700"
        >
          Load structure
        </button>
      </div>
    )
  }

  if (loading) {
    return <p className="text-sm text-slate-500 animate-pulse py-4">Loading CAD structure…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={() => { setLoaded(false); load() }} className="ml-3 underline">
          Retry
        </button>
      </div>
    )
  }

  if (nodes.length === 0) {
    return <p className="text-sm text-slate-400 py-4">No CAD structure available.</p>
  }

  return (
    <div className="space-y-3">
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
          {nodes.length} Eintr{nodes.length !== 1 ? 'äge' : 'ag'}
        </h3>
        <button
          onClick={handleCsvExport}
          className="px-3 py-1.5 text-xs font-medium text-white bg-emerald-600 rounded hover:bg-emerald-700 transition-colors"
          title="CAD-Struktur als CSV exportieren"
        >
          CSV Export
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
        <div className="overflow-auto" style={{ maxHeight: 'calc(100vh - 350px)' }}>
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200 sticky top-0 z-10">
              <tr>
                <th className="text-left px-3 py-2 font-medium">Level</th>
                <th className="text-left px-3 py-2 font-medium">File Name</th>
                <th className="text-left px-3 py-2 font-medium">Version</th>
                <th className="text-right px-3 py-2 font-medium">Quantity</th>
                <th className="text-left px-3 py-2 font-medium">Number</th>
                <th className="text-left px-3 py-2 font-medium">Dependency Type</th>
                <th className="text-left px-3 py-2 font-medium">State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {nodes.map((node, idx) => (
                <tr key={`${node.cadDocId || node.number}-${idx}`} className="hover:bg-slate-50">
                  <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{node.level}</td>
                  <td className="px-3 py-2 whitespace-nowrap">
                    <span style={{ paddingLeft: `${node.level * 16}px` }} className="inline-flex items-center gap-1">
                      {node.hasChildren && (
                        <span className="text-slate-400 text-[10px]">▶</span>
                      )}
                      <span className="text-slate-700">{node.fileName || '—'}</span>
                    </span>
                  </td>
                  <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{node.version || '—'}</td>
                  <td className="px-3 py-2 text-right text-slate-500 whitespace-nowrap">{node.quantity || '—'}</td>
                  <td className="px-3 py-2 font-mono text-indigo-600 whitespace-nowrap">{node.number || '—'}</td>
                  <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{node.dependencyType || '—'}</td>
                  <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{node.state || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
