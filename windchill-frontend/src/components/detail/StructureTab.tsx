import { useCallback, useEffect, useState } from 'react'
import { getBomRoot } from '../../api/client'
import type { BomTreeNode } from '../../api/types'
import BomTreeRow from '../BomTreeNode'

interface Props {
  partNumber: string
}

/** Structure/BOM tab — renders a tree-table with proper column headers. */
export default function StructureTab({ partNumber }: Props) {
  const [root, setRoot] = useState<BomTreeNode | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [loaded, setLoaded] = useState(false)

  const load = useCallback(async (signal?: AbortSignal) => {
    if (loaded) return
    setLoading(true)
    setError('')
    try {
      const r = await getBomRoot(partNumber, signal)
      if (signal?.aborted) return
      setRoot(r)
      setLoaded(true)
    } catch (e: unknown) {
      if (signal?.aborted) return
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [partNumber, loaded])

  // Auto-load via useEffect instead of during render
  useEffect(() => {
    const controller = new AbortController()
    load(controller.signal)
    return () => controller.abort()
  }, [load])

  if (loading) {
    return <p className="text-sm text-slate-500 animate-pulse py-4">BOM wird geladen…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={() => { setLoaded(false) }} className="ml-3 underline">
          Erneut versuchen
        </button>
      </div>
    )
  }

  if (!root) return null

  return (
    <div
      className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden"
      style={{ maxHeight: '60vh', overflowY: 'auto' }}
    >
      <table className="w-full text-sm border-collapse">
        <thead className="bg-slate-100 text-slate-600 text-xs border-b border-slate-200 sticky top-0 z-10">
          <tr>
            <th className="text-left px-1 py-2 font-medium w-8" />
            <th className="text-left px-2 py-2 font-medium">Nummer</th>
            <th className="text-left px-2 py-2 font-medium">Name</th>
            <th className="text-left px-2 py-2 font-medium">Version</th>
            <th className="text-left px-2 py-2 font-medium">Status</th>
            <th className="text-right px-2 py-2 font-medium">Menge</th>
            <th className="text-left px-2 py-2 font-medium">Einheit</th>
          </tr>
        </thead>
        <tbody className="[&>tr:nth-child(even)]:bg-slate-50/70">
          <BomTreeRow node={root} depth={0} />
        </tbody>
      </table>
    </div>
  )
}
