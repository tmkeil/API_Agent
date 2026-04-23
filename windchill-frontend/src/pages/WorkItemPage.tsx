import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  getWorkItem,
  updateWorkItem,
  addWorkItemStep,
  getResultingItems,
} from '../api/client'
import type { WorkItem, ChangeItem } from '../api/types'
import { formatDate, subtypeBadgeStyle } from '../utils/labels'

const STEP_LABELS: Record<string, string> = {
  cn_selected: 'CN selected',
  parts_loaded: 'Parts loaded',
  part_selected: 'Part selected',
  bom_exported: 'BOM exported',
  bom_edited: 'BOM edited',
  csv_generated: 'CSV generated',
}

export default function WorkItemPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [wi, setWi] = useState<WorkItem | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Resulting parts
  const [parts, setParts] = useState<ChangeItem[]>([])
  const [partsLoading, setPartsLoading] = useState(false)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    getWorkItem(id)
      .then(setWi)
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false))
  }, [id])

  const handleLoadParts = async () => {
    if (!wi || !id) return
    const cnNumber = (wi.changeNotice as Record<string, string>).number
    if (!cnNumber) return

    setPartsLoading(true)
    try {
      const resp = await getResultingItems('change_notice', cnNumber)
      const partItems = resp.items.filter((i) => i.objectType === 'WTPart')
      setParts(partItems)

      // Persist in WorkItem
      const updated = await updateWorkItem(id, {
        resultingParts: partItems.map((p) => ({
          number: p.number,
          name: p.name,
          version: p.version,
          state: p.state,
          objectId: p.objectId,
          subType: p.subType,
        })),
      })
      await addWorkItemStep(id, 'parts_loaded', {
        count: partItems.length,
      })
      setWi(updated)
    } catch (e: unknown) {
      setError((e as Error).message)
    } finally {
      setPartsLoading(false)
    }
  }

  const handleSelectPart = async (part: ChangeItem) => {
    if (!id) return
    try {
      const updated = await updateWorkItem(id, {
        selectedPart: {
          number: part.number,
          name: part.name,
          version: part.version,
          state: part.state,
          objectId: part.objectId,
        },
      })
      await addWorkItemStep(id, 'part_selected', { partNumber: part.number })
      setWi(updated)
      // Navigate to BOM export for this part
      navigate(`/detail/part/${encodeURIComponent(part.number)}?workitem=${id}`)
    } catch (e: unknown) {
      setError((e as Error).message)
    }
  }

  const handleComplete = async () => {
    if (!id || !wi || wi.status === 'completed') return
    try {
      const updated = await updateWorkItem(id, { status: 'completed' })
      await addWorkItemStep(id, 'workitem_completed', {})
      setWi(updated)
    } catch (e: unknown) {
      setError((e as Error).message)
    }
  }

  const handleDownloadJson = () => {
    if (!wi) return
    const blob = new Blob([JSON.stringify(wi, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `workitem_${wi.id}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return <div className="text-sm text-slate-500 py-10 text-center animate-pulse">Loading…</div>
  }

  if (!wi) {
    return (
      <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded p-4">
        WorkItem not found. {error}
      </div>
    )
  }

  const cn = wi.changeNotice as Record<string, string>

  return (
    <div className="space-y-5 max-w-4xl">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-lg font-semibold text-slate-800">WorkItem {wi.id}</h1>
            <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
              wi.status === 'completed'
                ? 'bg-green-50 text-green-700 border border-green-300'
                : 'bg-amber-50 text-amber-700 border border-amber-300'
            }`}>
              {wi.status === 'completed' ? 'Completed' : 'In progress'}
            </span>
          </div>
          <p className="text-xs text-slate-400">Created: {formatDate(wi.createdAt)}</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleDownloadJson}
            className="text-xs px-2.5 py-1 font-medium rounded bg-slate-50 text-slate-700 border border-slate-300 hover:bg-slate-100 transition-colors"
            title="Download WorkItem as JSON file"
          >
            ⬇ JSON
          </button>
          <button
            onClick={handleComplete}
            disabled={wi.status === 'completed'}
            className="text-xs px-2.5 py-1 font-medium rounded bg-green-50 text-green-700 border border-green-300 hover:bg-green-100 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            title={wi.status === 'completed' ? 'Already completed' : 'Mark WorkItem as completed'}
          >
            ✓ Complete
          </button>
          <button
            onClick={() => navigate('/change-notices')}
            className="text-xs text-slate-500 hover:text-indigo-600 transition-colors ml-1"
          >
            ← Back
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">{error}</div>
      )}

      {/* CN Info */}
      <section className="bg-white rounded shadow-sm border border-slate-200 p-4">
        <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Change Notice</h2>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-slate-400 text-xs">Number:</span>
            <span className="ml-2 font-mono text-indigo-600 cursor-pointer hover:underline"
              onClick={() => navigate(`/detail/change_notice/${encodeURIComponent(cn.number)}`)}
            >
              {cn.number}
            </span>
          </div>
          <div>
            <span className="text-slate-400 text-xs">Type:</span>
            <span className={`ml-2 inline-block px-1.5 py-0.5 rounded border text-[10px] font-medium ${subtypeBadgeStyle(cn.subType || 'Change Notice')}`}>
              {cn.subType || 'Change Notice'}
            </span>
          </div>
          <div className="col-span-2">
            <span className="text-slate-400 text-xs">Name:</span>
            <span className="ml-2 text-slate-700">{cn.name}</span>
          </div>
          <div>
            <span className="text-slate-400 text-xs">Status:</span>
            <span className="ml-2 text-slate-600">{cn.state}</span>
          </div>
        </div>
      </section>

      {/* Steps Timeline */}
      <section className="bg-white rounded shadow-sm border border-slate-200 p-4">
        <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">Work steps</h2>
        <div className="space-y-2">
          {wi.steps.map((s, i) => (
            <div key={i} className="flex items-center gap-3 text-sm">
              <div className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                {i + 1}
              </div>
              <span className="text-slate-700">{STEP_LABELS[s.step] || s.step}</span>
              <span className="text-xs text-slate-400">{formatDate(s.timestamp)}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Resulting Parts */}
      <section className="bg-white rounded shadow-sm border border-slate-200 p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Resulting Parts (WTPart)</h2>
          <button
            onClick={handleLoadParts}
            disabled={partsLoading}
            className="px-2.5 py-1 text-[11px] font-medium rounded bg-indigo-50 text-indigo-700 border border-indigo-300 hover:bg-indigo-100 transition-colors disabled:opacity-50"
          >
            {partsLoading ? 'Loading…' : parts.length > 0 ? 'Reload' : 'Load parts'}
          </button>
        </div>

        {parts.length > 0 ? (
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200">
                <tr>
                  <th className="text-left px-3 py-1.5 font-medium">Number</th>
                  <th className="text-left px-3 py-1.5 font-medium">Name</th>
                  <th className="text-left px-3 py-1.5 font-medium">Version</th>
                  <th className="text-left px-3 py-1.5 font-medium">State</th>
                  <th className="text-left px-3 py-1.5 font-medium">Subtype</th>
                  <th className="w-16"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {parts.map((p) => (
                  <tr key={p.objectId} className="hover:bg-slate-50">
                    <td className="px-3 py-1.5 font-mono text-indigo-600">{p.number}</td>
                    <td className="px-3 py-1.5 text-slate-600 max-w-[200px] truncate">{p.name}</td>
                    <td className="px-3 py-1.5 text-slate-500">{p.version}</td>
                    <td className="px-3 py-1.5 text-slate-500">{p.state}</td>
                    <td className="px-3 py-1.5">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded border ${subtypeBadgeStyle(p.subType || 'Part')}`}>
                        {p.subType || 'Part'}
                      </span>
                    </td>
                    <td className="px-3 py-1.5">
                      <button
                        onClick={() => handleSelectPart(p)}
                        className="px-2 py-0.5 text-[10px] font-medium rounded bg-emerald-50 text-emerald-700 border border-emerald-300 hover:bg-emerald-100 transition-colors"
                      >
                        Select
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-xs text-slate-400">
            {(wi.resultingParts?.length || 0) > 0
              ? `${wi.resultingParts.length} parts saved — click "Load parts" to display.`
              : 'No parts loaded yet.'
            }
          </p>
        )}
      </section>

      {/* WorkItem JSON (collapsible) */}
      <details className="bg-white rounded shadow-sm border border-slate-200">
        <summary className="px-4 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wide cursor-pointer hover:bg-slate-50">
          WorkItem JSON
        </summary>
        <pre className="px-4 py-3 text-[11px] text-slate-600 overflow-auto max-h-96 bg-slate-50 border-t border-slate-200">
          {JSON.stringify(wi, null, 2)}
        </pre>
      </details>
    </div>
  )
}
