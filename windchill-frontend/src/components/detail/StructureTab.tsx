import { useCallback, useEffect, useState } from 'react'
import { diagnoseBomFields, getBomRoot, getBomViews } from '../../api/client'
import type { BomTreeNode, BomViewConfig } from '../../api/types'
import BomTreeRow from '../BomTreeNode'
import BomDetailPanel from './BomDetailPanel'

interface Props {
  partNumber: string
}

/** Default view config used while views are loading or if fetch fails. */
const FALLBACK_VIEW: BomViewConfig = {
  id: 'default',
  label: 'Standard',
  columns: [
    { key: 'number', label: 'Nummer', source: 'part', align: 'left' },
    { key: 'name', label: 'Name', source: 'part', align: 'left' },
    { key: 'version', label: 'Version', source: 'part', align: 'left' },
    { key: 'state', label: 'Status', source: 'part', align: 'left' },
    { key: 'quantity', label: 'Menge', source: 'link', align: 'right' },
    { key: 'quantityUnit', label: 'Einheit', source: 'link', align: 'left' },
  ],
}

/** Structure/BOM tab — loads root on first user interaction, not automatically. */
export default function StructureTab({ partNumber }: Props) {
  const [root, setRoot] = useState<BomTreeNode | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [loaded, setLoaded] = useState(false)

  // BOM view state
  const [views, setViews] = useState<BomViewConfig[]>([FALLBACK_VIEW])
  const [activeViewId, setActiveViewId] = useState('default')

  // Raw fields diagnostic
  const [rawFields, setRawFields] = useState<Record<string, unknown> | null>(null)
  const [rawFieldsLoading, setRawFieldsLoading] = useState(false)
  const [showRawFields, setShowRawFields] = useState(false)

  // Selection for split-view detail panel
  const [selectedNode, setSelectedNode] = useState<BomTreeNode | null>(null)

  const activeView = views.find(v => v.id === activeViewId) ?? views[0]

  // Load available views once on mount
  useEffect(() => {
    let cancelled = false
    getBomViews()
      .then(v => {
        if (!cancelled && v.length > 0) setViews(v)
      })
      .catch(() => { /* keep fallback */ })
    return () => { cancelled = true }
  }, [])

  const load = useCallback(async (signal?: AbortSignal) => {
    if (loaded || loading) return
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
  }, [partNumber, loaded, loading])

  const loadRawFields = useCallback(async () => {
    if (rawFields || rawFieldsLoading) {
      setShowRawFields(!showRawFields)
      return
    }
    setRawFieldsLoading(true)
    try {
      const data = await diagnoseBomFields(partNumber)
      setRawFields(data)
      setShowRawFields(true)
    } catch {
      // ignore
    } finally {
      setRawFieldsLoading(false)
    }
  }, [partNumber, rawFields, rawFieldsLoading, showRawFields])

  // NO auto-load — user must click the load button

  if (!loaded && !loading) {
    return (
      <div className="text-center py-6">
        <button
          onClick={() => load()}
          className="px-4 py-2 text-sm font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
        >
          Stückliste laden
        </button>
      </div>
    )
  }

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

  // Total column count = 1 (expand+type) + view columns
  const totalCols = 1 + activeView.columns.length

  return (
    <div className="space-y-2">
      {/* View selector bar */}
      <div className="flex items-center justify-between gap-3 px-1">
        <div className="flex items-center gap-3">
          <label className="text-xs font-medium text-slate-500">BOM-Ansicht:</label>
          <div className="flex gap-1">
            {views.map(v => (
              <button
                key={v.id}
                onClick={() => setActiveViewId(v.id)}
                className={`px-2.5 py-1 text-xs rounded-md transition-colors ${
                  v.id === activeViewId
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {v.label}
              </button>
            ))}
          </div>
        </div>
        <button
          onClick={loadRawFields}
          className="px-2 py-1 text-[10px] font-medium rounded border border-slate-300 text-slate-500 hover:bg-slate-100 transition-colors"
          title="Rohfelder von Windchill anzeigen (Diagnose)"
        >
          {rawFieldsLoading ? '…' : showRawFields ? 'Raw Fields ✕' : 'Raw Fields'}
        </button>
      </div>

      {/* Raw fields diagnostic panel */}
      {showRawFields && rawFields && (
        <div className="bg-slate-50 border border-slate-200 rounded p-3 text-xs font-mono max-h-[50vh] overflow-auto">
          <div className="mb-2 font-sans text-[11px] font-semibold text-slate-600">
            Windchill OData Raw Fields — {partNumber}
          </div>
          <RawFieldsSection title="Part Fields" data={(rawFields as Record<string, unknown>).part as Record<string, unknown> | undefined} />
          <RawFieldsSection title="Usage Link Fields" data={(rawFields as Record<string, unknown>).usageLinks as Record<string, unknown> | undefined} />
          <RawFieldsSection title="Child Part Fields" data={(rawFields as Record<string, unknown>).childPart as Record<string, unknown> | undefined} />
        </div>
      )}

      {/* ── Split layout: BOM table + detail panel ── */}
      <div className="flex gap-0" style={{ height: '65vh' }}>
        {/* LEFT — BOM table */}
        <div
          className={`bg-white rounded-l shadow-sm border border-slate-200 overflow-hidden flex flex-col transition-all ${
            selectedNode ? 'w-[55%] min-w-[400px]' : 'w-full'
          }`}
        >
          <div className="flex-1 overflow-auto">
            <table className="w-full text-sm border-collapse">
              <thead className="bg-slate-100 text-slate-600 text-xs border-b border-slate-200 sticky top-0 z-10">
                <tr>
                  <th className="text-left px-1 py-2 font-medium w-16" />
                  {activeView.columns.map(col => (
                    <th
                      key={col.key}
                      className={`px-2 py-2 font-medium whitespace-nowrap ${
                        col.align === 'right' ? 'text-right' : 'text-left'
                      }`}
                    >
                      {col.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="[&>tr:nth-child(even)]:bg-slate-50/70">
                <BomTreeRow
                  node={root}
                  depth={0}
                  viewColumns={activeView.columns}
                  totalCols={totalCols}
                  onSelect={setSelectedNode}
                  selectedPartId={selectedNode?.partId}
                />
              </tbody>
            </table>
          </div>
        </div>

        {/* RIGHT — Detail panel (shown when a node is selected) */}
        {selectedNode && (
          <div className="w-[45%] min-w-[320px] rounded-r shadow-sm border border-l-0 border-slate-200 overflow-hidden">
            <BomDetailPanel
              node={selectedNode}
              onClose={() => setSelectedNode(null)}
            />
          </div>
        )}
      </div>
    </div>
  )
}

/** Collapsible section showing raw fields from the diagnostic endpoint. */
function RawFieldsSection({ title, data }: { title: string; data?: Record<string, unknown> | null }) {
  const [open, setOpen] = useState(true)
  if (!data) return null

  const fields = (data.fields as string[] | undefined) ?? []
  const sample = (data.sample ?? data.samples) as Record<string, unknown> | Record<string, unknown>[] | undefined

  return (
    <div className="mb-3">
      <button
        onClick={() => setOpen(!open)}
        className="text-[11px] font-semibold text-indigo-600 hover:text-indigo-800 mb-1"
      >
        {open ? '▾' : '▸'} {title} ({fields.length} Felder)
      </button>
      {open && (
        <div className="ml-2">
          <div className="text-slate-500 mb-1">Felder: {fields.join(', ')}</div>
          {sample && (
            <pre className="bg-white border border-slate-200 rounded p-2 text-[10px] overflow-x-auto whitespace-pre-wrap max-h-[30vh]">
              {JSON.stringify(sample, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}