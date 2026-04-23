import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { ChangeItem, ChangeItemsResponse } from '../../api/types'
import { TYPE_KEY_MAP, typeLabel } from '../../utils/labels'
import BalluffExportModal from './BalluffExportModal'

interface Props {
  /** Display label for loading/empty states */
  label: string
  /** API function to fetch change items */
  fetchFn: (signal?: AbortSignal) => Promise<ChangeItemsResponse>
}

/**
 * Shared tab component for Affected Items and Resulting Items.
 * Parameterized by fetch function and display label.
 */
export default function ChangeItemsTab({ label, fetchFn }: Props) {
  const [items, setItems] = useState<ChangeItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [exportPartNumber, setExportPartNumber] = useState<string | null>(null)
  const navigate = useNavigate()

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const resp = await fetchFn(signal)
      if (signal?.aborted) return
      setItems(resp.items)
    } catch (e: unknown) {
      if (signal?.aborted) return
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [fetchFn])

  useEffect(() => {
    const controller = new AbortController()
    load(controller.signal)
    return () => controller.abort()
  }, [load])

  function handleRowClick(item: ChangeItem) {
    const tk = TYPE_KEY_MAP[item.objectType]
    if (tk) {
      navigate(`/detail/${tk}/${encodeURIComponent(item.number)}`)
    }
  }

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

  if (items.length === 0) {
    return (
      <p className="text-sm text-slate-400 py-4">
        Keine {label} vorhanden.
      </p>
    )
  }

  return (
    <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200">
          <tr>
            <th className="text-left px-3 py-2 font-medium">Typ</th>
            <th className="text-left px-3 py-2 font-medium">Number</th>
            <th className="text-left px-3 py-2 font-medium">Name</th>
            <th className="text-left px-3 py-2 font-medium">Version</th>
            <th className="text-left px-3 py-2 font-medium">Status</th>
            <th className="w-10" />
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.map((item) => {
            const tk = TYPE_KEY_MAP[item.objectType]
            const isPart = tk === 'part'
            return (
              <tr
                key={item.objectId || item.number}
                onClick={() => handleRowClick(item)}
                onKeyDown={(ev) => {
                  if (ev.key === 'Enter' || ev.key === ' ') {
                    ev.preventDefault()
                    handleRowClick(item)
                  }
                }}
                role={tk ? 'link' : undefined}
                tabIndex={tk ? 0 : undefined}
                className={tk ? 'cursor-pointer hover:bg-indigo-50 transition-colors' : 'hover:bg-slate-50'}
              >
                <td className="px-3 py-2 whitespace-nowrap">
                  <span className="inline-block px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600">
                    {typeLabel(item.objectType, item.subType)}
                  </span>
                </td>
                <td className="px-3 py-2 font-mono text-indigo-600 whitespace-nowrap">
                  {item.number}
                </td>
                <td className="px-3 py-2 text-slate-600 max-w-[300px] truncate">{item.name}</td>
                <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{item.version}</td>
                <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{item.state}</td>
                <td className="px-1 py-2 text-center">
                  {isPart && (
                    <button
                      onClick={(e) => { e.stopPropagation(); setExportPartNumber(item.number) }}
                      className="px-2 py-0.5 text-[10px] font-medium rounded bg-emerald-600 text-white hover:bg-emerald-700 transition-colors"
                      title={`Balluff BOM Export für ${item.number}`}
                    >
                      Export
                    </button>
                  )}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>

      {/* Balluff BOM Export Modal */}
      {exportPartNumber && (
        <BalluffExportModal
          partNumber={exportPartNumber}
          onClose={() => setExportPartNumber(null)}
        />
      )}
    </div>
  )
}
