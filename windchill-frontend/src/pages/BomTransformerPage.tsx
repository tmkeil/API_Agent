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

/** Fixed table height — keeps both panes at full size from the start so the
 *  layout doesn't jump when the user expands the root. */
const TABLE_HEIGHT = '75vh'

interface SideProps {
  title: string
  badge: string
  badgeClass: string
  root: BomTreeNode | null
  columns: BomViewColumn[]
  onShowDetail: (node: BomTreeNode) => void
  emptyHint: string
}

function BomSide({
  title,
  badge,
  badgeClass,
  root,
  columns,
  onShowDetail,
  emptyHint,
}: SideProps) {
  const totalCols = columns.length + 1
  return (
    <div
      className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden flex flex-col min-w-0"
      style={{ height: TABLE_HEIGHT }}
    >
      <div className="px-3 py-2 border-b border-slate-200 bg-slate-50 flex items-center justify-between gap-2 flex-shrink-0">
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
      <div className="flex-1 min-h-0 overflow-auto">
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
                onShowDetail={onShowDetail}
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

interface DetailModalProps {
  node: BomTreeNode
  onClose: () => void
}

function NodeDetailModal({ node, onClose }: DetailModalProps) {
  const [detail, setDetail] = useState<ObjectDetailResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!node.number) return
    const ctrl = new AbortController()
    setDetail(null)
    setError(null)
    setLoading(true)
    getObjectDetail('part', node.number, ctrl.signal)
      .then(setDetail)
      .catch(e => {
        if (e?.name !== 'AbortError') setError(String(e?.message ?? e))
      })
      .finally(() => setLoading(false))
    return () => ctrl.abort()
  }, [node.number])

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40"
      onClick={onClose}
    >
      <div
        className="bg-white rounded shadow-xl border border-slate-200 w-full max-w-3xl flex flex-col"
        style={{ maxHeight: '85vh' }}
        onClick={e => e.stopPropagation()}
      >
        <div className="px-4 py-3 border-b border-slate-200 bg-slate-50 flex items-center justify-between gap-3 flex-shrink-0">
          <div className="min-w-0">
            <div className="text-[10px] uppercase text-slate-500 tracking-wider">Node Details</div>
            <div className="text-sm font-medium text-slate-800 truncate font-mono" title={node.number}>
              {node.number || '—'}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Link
              to={`/detail/part/${encodeURIComponent(node.number)}`}
              className="text-xs px-2.5 py-1 rounded border border-indigo-200 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 whitespace-nowrap"
            >
              Open full detail page →
            </Link>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 text-xl px-2"
              aria-label="Schließen"
            >
              ×
            </button>
          </div>
        </div>
        <div className="flex-1 min-h-0 overflow-auto p-4 text-xs space-y-3">
          <section>
            <div className="text-[10px] uppercase text-slate-500 mb-2 tracking-wider">Basis</div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
              <Row label="Name">{node.name || '—'}</Row>
              <Row label="Subtype">{node.type || '—'}</Row>
              <Row label="Version">{node.version || '—'}</Row>
              <Row label="Iteration">{node.iteration || '—'}</Row>
              <Row label="State">{node.state || '—'}</Row>
              <Row label="Identity">{node.identity || '—'}</Row>
              {node.quantity != null && (
                <Row label="Quantity">
                  {String(node.quantity)} {node.quantityUnit ?? ''}
                </Row>
              )}
              {node.lineNumber && <Row label="Line #">{node.lineNumber}</Row>}
              {node.organizationId && <Row label="Org">{node.organizationId}</Row>}
            </div>
          </section>

          <section className="pt-3 border-t border-slate-100">
            <div className="text-[10px] uppercase text-slate-500 mb-2 tracking-wider">
              Volle Attribute
            </div>
            {loading && <div className="text-slate-400 italic">Lädt …</div>}
            {error && <div className="text-rose-600">{error}</div>}
            {detail && (
              <table className="w-full">
                <tbody className="divide-y divide-slate-100">
                  {Object.entries(detail.detail.allAttributes ?? {})
                    .filter(([, v]) => v != null && v !== '')
                    .map(([k, v]) => (
                      <tr key={k}>
                        <td className="py-0.5 pr-3 text-slate-500 align-top whitespace-nowrap font-mono">
                          {k}
                        </td>
                        <td className="py-0.5 text-slate-800 break-all">
                          {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            )}
          </section>
        </div>
      </div>
    </div>
  )
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex gap-2 min-w-0">
      <div className="text-slate-500 w-24 flex-shrink-0">{label}</div>
      <div className="text-slate-800 break-all min-w-0">{children}</div>
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
  const [modalNode, setModalNode] = useState<BomTreeNode | null>(null)

  useEffect(() => {
    if (!code) return
    const ctrl = new AbortController()
    setLoading(true)
    setError(null)
    setModalNode(null)
    getBomTransformer(code, ctrl.signal)
      .then(setData)
      .catch(e => {
        if (e?.name !== 'AbortError') setError(String(e?.message ?? e))
      })
      .finally(() => setLoading(false))
    return () => ctrl.abort()
  }, [code])

  const columns = compact ? COMPACT_COLUMNS : FULL_COLUMNS

  const handleShowDetail = useCallback((node: BomTreeNode) => {
    setModalNode(node)
  }, [])

  const designNumber = data?.designRoot?.number ?? '—'
  const mfgNumber = data?.manufacturingRoot?.number ?? '—'

  const links = data?.equivalence
  const linkCount = useMemo(() => {
    if (!links) return 0
    return (links.down?.length ?? 0) + (links.up?.length ?? 0)
  }, [links])

  /** Break out of Layout's `max-w-7xl + px-6` so the two trees use the full
   *  viewport width. A small 0.75rem inner gutter keeps content off the
   *  scrollbar/edge. */
  const fullBleed: React.CSSProperties = {
    marginLeft: 'calc(50% - 50vw + 0.75rem)',
    marginRight: 'calc(50% - 50vw + 0.75rem)',
  }

  return (
    <div className="space-y-3" style={fullBleed}>
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

      {/* Dual tree — full viewport width, fixed height */}
      {!loading && !error && data && (
        <div
          className="grid gap-3"
          style={{ gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)' }}
        >
          <BomSide
            title={designNumber}
            badge="Design"
            badgeClass="bg-sky-100 text-sky-700"
            root={data.designRoot}
            columns={columns}
            onShowDetail={handleShowDetail}
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
            onShowDetail={handleShowDetail}
            emptyHint={
              data.selfView.toLowerCase().startsWith('manuf')
                ? 'Manufacturing-BOM nicht verfügbar.'
                : 'Kein Manufacturing-Pendant — Phase 2: „Generate Downstream".'
            }
          />
        </div>
      )}

      {modalNode && (
        <NodeDetailModal node={modalNode} onClose={() => setModalNode(null)} />
      )}
    </div>
  )
}
