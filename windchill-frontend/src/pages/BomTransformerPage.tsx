import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { getBomTransformer, getObjectDetail } from '../api/client'
import type {
  BomTransformerResponse,
  BomTreeNode,
  BomViewColumn,
  ObjectDetailResponse,
} from '../api/types'
import BomTreeRow from '../components/BomTreeNode'

/** Compact column set used by both trees — matches StructureTab's defaults
 *  but trimmed for a side-by-side layout. */
const COMPACT_COLUMNS: BomViewColumn[] = [
  { key: 'number', label: 'Nummer', source: 'part', align: 'left' },
  { key: 'name', label: 'Name', source: 'part', align: 'left' },
  { key: 'version', label: 'Ver.', source: 'part', align: 'left' },
  { key: 'state', label: 'Status', source: 'part', align: 'left' },
  { key: 'quantity', label: 'Qty', source: 'link', align: 'right' },
]

const FULL_COLUMNS: BomViewColumn[] = [
  { key: 'number', label: 'Nummer', source: 'part', align: 'left' },
  { key: 'name', label: 'Name', source: 'part', align: 'left' },
  { key: 'version', label: 'Version', source: 'part', align: 'left' },
  { key: 'iteration', label: 'Iter.', source: 'part', align: 'left' },
  { key: 'state', label: 'Status', source: 'part', align: 'left' },
  { key: 'quantity', label: 'Qty', source: 'link', align: 'right' },
  { key: 'quantityUnit', label: 'Unit', source: 'link', align: 'left' },
]

interface SideProps {
  title: string
  badge: string
  badgeClass: string
  root: BomTreeNode | null
  columns: BomViewColumn[]
  onSelect: (node: BomTreeNode) => void
  selectedPartId?: string
  emptyHint: string
}

function BomSide({
  title,
  badge,
  badgeClass,
  root,
  columns,
  onSelect,
  selectedPartId,
  emptyHint,
}: SideProps) {
  const totalCols = columns.length + 1
  return (
    <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden flex flex-col min-w-0">
      <div className="px-3 py-2 border-b border-slate-200 bg-slate-50 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className={`text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded ${badgeClass}`}>
            {badge}
          </span>
          <span className="text-sm font-medium text-slate-700 truncate" title={title}>
            {title}
          </span>
        </div>
        {root?.number && (
          <Link
            to={`/detail/part/${encodeURIComponent(root.number)}`}
            className="text-[11px] text-indigo-600 hover:text-indigo-800 hover:underline whitespace-nowrap"
            title="Open detail page"
          >
            Details →
          </Link>
        )}
      </div>
      <div className="flex-1 overflow-auto" style={{ maxHeight: '70vh' }}>
        {root ? (
          <table className="w-full text-sm border-collapse">
            <thead className="bg-slate-100 text-slate-600 text-xs border-b border-slate-200 sticky top-0 z-10">
              <tr>
                <th className="text-left px-1 py-2 font-medium w-12" />
                {columns.map(col => (
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
                viewColumns={columns}
                totalCols={totalCols}
                onSelect={onSelect}
                selectedPartId={selectedPartId}
              />
            </tbody>
          </table>
        ) : (
          <div className="p-6 text-sm text-slate-500 italic">{emptyHint}</div>
        )}
      </div>
    </div>
  )
}

interface DetailPanelProps {
  selected: BomTreeNode | null
  onClose: () => void
}

function NodeDetailPanel({ selected, onClose }: DetailPanelProps) {
  const [detail, setDetail] = useState<ObjectDetailResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setDetail(null)
    setError(null)
    if (!selected?.number) return
    const ctrl = new AbortController()
    setLoading(true)
    getObjectDetail('part', selected.number, ctrl.signal)
      .then(setDetail)
      .catch(e => {
        if (e?.name !== 'AbortError') setError(String(e?.message ?? e))
      })
      .finally(() => setLoading(false))
    return () => ctrl.abort()
  }, [selected?.number])

  if (!selected) {
    return (
      <div className="bg-white rounded shadow-sm border border-slate-200 p-4 text-xs text-slate-500 italic">
        Klick auf einen Knoten, um Details zu sehen.
      </div>
    )
  }

  return (
    <div className="bg-white rounded shadow-sm border border-slate-200 flex flex-col" style={{ maxHeight: '70vh' }}>
      <div className="px-3 py-2 border-b border-slate-200 bg-slate-50 flex items-center justify-between gap-2">
        <div className="min-w-0">
          <div className="text-[10px] uppercase text-slate-500 tracking-wider">Selected node</div>
          <div className="text-sm font-medium text-slate-700 truncate" title={selected.number}>
            {selected.number || '—'}
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-600 text-sm px-2"
          aria-label="Schließen"
        >
          ×
        </button>
      </div>
      <div className="flex-1 overflow-auto p-3 text-xs space-y-2">
        <Row label="Name">{selected.name || '—'}</Row>
        <Row label="Version">{selected.version || '—'}</Row>
        <Row label="Iteration">{selected.iteration || '—'}</Row>
        <Row label="State">{selected.state || '—'}</Row>
        <Row label="Subtype">{selected.type || '—'}</Row>
        {selected.quantity != null && (
          <Row label="Quantity">
            {String(selected.quantity)} {selected.quantityUnit ?? ''}
          </Row>
        )}
        {selected.lineNumber && <Row label="Line #">{selected.lineNumber}</Row>}

        <div className="pt-2 border-t border-slate-100">
          <div className="text-[10px] uppercase text-slate-500 mb-1">Volle Attribute</div>
          {loading && <div className="text-slate-400 italic">Lädt …</div>}
          {error && <div className="text-rose-600">{error}</div>}
          {detail && (
            <table className="w-full">
              <tbody className="divide-y divide-slate-100">
                {Object.entries(detail.detail.allAttributes ?? {})
                  .filter(([, v]) => v != null && v !== '')
                  .slice(0, 80)
                  .map(([k, v]) => (
                    <tr key={k}>
                      <td className="py-0.5 pr-2 text-slate-500 align-top whitespace-nowrap">{k}</td>
                      <td className="py-0.5 text-slate-800 break-all">
                        {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="pt-2 border-t border-slate-100">
          <Link
            to={`/detail/part/${encodeURIComponent(selected.number)}`}
            className="text-indigo-600 hover:text-indigo-800 hover:underline"
          >
            Open full detail page →
          </Link>
        </div>
      </div>
    </div>
  )
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex gap-2">
      <div className="text-slate-500 w-20 flex-shrink-0">{label}</div>
      <div className="text-slate-800 break-all">{children}</div>
    </div>
  )
}

export default function BomTransformerPage() {
  const { code = '' } = useParams<{ code: string }>()
  const navigate = useNavigate()
  const [data, setData] = useState<BomTransformerResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [compact, setCompact] = useState(true)
  const [selected, setSelected] = useState<BomTreeNode | null>(null)

  useEffect(() => {
    if (!code) return
    const ctrl = new AbortController()
    setLoading(true)
    setError(null)
    setSelected(null)
    getBomTransformer(code, ctrl.signal)
      .then(setData)
      .catch(e => {
        if (e?.name !== 'AbortError') setError(String(e?.message ?? e))
      })
      .finally(() => setLoading(false))
    return () => ctrl.abort()
  }, [code])

  const columns = compact ? COMPACT_COLUMNS : FULL_COLUMNS

  const handleSelect = useCallback((node: BomTreeNode) => {
    setSelected(node)
  }, [])

  const designNumber = data?.designRoot?.number ?? '—'
  const mfgNumber = data?.manufacturingRoot?.number ?? '—'

  const links = data?.equivalence
  const linkCount = useMemo(() => {
    if (!links) return 0
    return (links.down?.length ?? 0) + (links.up?.length ?? 0)
  }, [links])

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-3 min-w-0">
          <button
            onClick={() => navigate(-1)}
            className="text-xs text-slate-500 hover:text-slate-800"
          >
            ← Zurück
          </button>
          <h1 className="text-lg font-semibold text-slate-800 truncate">
            BOM Transformer
          </h1>
          <span className="text-sm text-slate-500 font-mono">{code}</span>
          {data?.selfView && (
            <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
              self: {data.selfView}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500">
            {linkCount > 0 ? `${linkCount} Equivalence Link(s)` : 'Keine Equivalence Links'}
          </span>
          <label className="flex items-center gap-1.5 text-xs text-slate-600 cursor-pointer">
            <input
              type="checkbox"
              checked={compact}
              onChange={e => setCompact(e.target.checked)}
              className="accent-indigo-600"
            />
            Kompakt
          </label>
        </div>
      </div>

      {/* Loading / error */}
      {loading && (
        <div className="bg-white rounded shadow-sm border border-slate-200 p-6 text-sm text-slate-500">
          Lädt Transformer-Ansicht …
        </div>
      )}
      {error && (
        <div className="bg-rose-50 border border-rose-200 rounded p-3 text-sm text-rose-700">
          {error}
        </div>
      )}

      {/* Dual tree + side panel */}
      {!loading && !error && data && (
        <div className="grid gap-3" style={{ gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr) 320px' }}>
          <BomSide
            title={designNumber}
            badge="Design"
            badgeClass="bg-sky-100 text-sky-700"
            root={data.designRoot}
            columns={columns}
            onSelect={handleSelect}
            selectedPartId={selected?.partId}
            emptyHint={
              data.selfView.toLowerCase().startsWith('manuf')
                ? 'Kein Design-Pendant verknüpft.'
                : 'Design-BOM nicht verfügbar.'
            }
          />
          <BomSide
            title={mfgNumber}
            badge="Manufacturing"
            badgeClass="bg-amber-100 text-amber-700"
            root={data.manufacturingRoot}
            columns={columns}
            onSelect={handleSelect}
            selectedPartId={selected?.partId}
            emptyHint={
              data.selfView.toLowerCase().startsWith('manuf')
                ? 'Manufacturing-BOM nicht verfügbar.'
                : 'Kein Manufacturing-Pendant — Phase 2: „Generate Downstream".'
            }
          />
          <NodeDetailPanel
            selected={selected}
            onClose={() => setSelected(null)}
          />
        </div>
      )}
    </div>
  )
}
