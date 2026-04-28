import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  getBomTransformer,
  getObjectDetail,
  postTransformerDetect,
  postTransformerGenerate,
} from '../api/client'
import type {
  BomTransformerResponse,
  BomTreeNode,
  BomViewColumn,
  ObjectDetailResponse,
} from '../api/types'
import type { TransformResponse } from '../api/client'
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
  strategyMap?: Record<string, 'KEEP' | 'SYNC' | 'REMOVE'>
  onCycleStrategy?: (node: BomTreeNode) => void
  headerExtra?: React.ReactNode
}

function BomSide({
  title,
  badge,
  badgeClass,
  root,
  columns,
  onShowDetail,
  emptyHint,
  strategyMap,
  onCycleStrategy,
  headerExtra,
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
        {headerExtra}
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
                strategyMap={strategyMap}
                onCycleStrategy={onCycleStrategy}
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
  // Phase 2b: per-node transform strategy on the MANUFACTURING side.
  // KEEP   = Knoten bleibt unangetastet (default)
  // SYNC   = beim nächsten „Sync Selection“ wird sein EBOM-Pendant in SourcePartSelection aufgenommen
  // REMOVE = visuell markiert, ausgeführt erst in Phase 2c (PTC.ProdMgmt)
  const [strategyMap, setStrategyMap] = useState<Record<string, 'KEEP' | 'SYNC' | 'REMOVE'>>({})
  const [transformBusy, setTransformBusy] = useState<null | 'detect' | 'autoSync' | 'syncSel'>(null)
  const [transformResult, setTransformResult] = useState<TransformResponse | null>(null)
  const [transformError, setTransformError] = useState<string | null>(null)
  const [confirmKind, setConfirmKind] = useState<null | 'autoSync' | 'syncSel'>(null)

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

  const cycleStrategy = useCallback((node: BomTreeNode) => {
    const id = node.partId || ''
    if (!id) return
    setStrategyMap(prev => {
      const cur = prev[id] ?? 'KEEP'
      // KEEP → SYNC → REMOVE → KEEP. REMOVE ist visuell, Phase 2c führt es aus.
      const next = cur === 'KEEP' ? 'SYNC' : cur === 'SYNC' ? 'REMOVE' : 'KEEP'
      return { ...prev, [id]: next }
    })
  }, [])

  // Build OData "Path" for an OID. BomTransformation.DiscrepancyContext expects
  // strings of the form "Parts('<oid>')" referring to the v3 Parts entity set.
  const partPath = useCallback((oid: string) => `Parts('${oid}')`, [])

  // TargetPath = MBOM-Root (downstream). Falls keine MBOM existiert, fallen wir
  // auf den Design-Root zurück (Initial-Generate-Szenario).
  const mfgRootId = data?.manufacturingRoot?.partId || ''
  const designRootId = data?.designRoot?.partId || ''
  const targetPath = mfgRootId
    ? partPath(mfgRootId)
    : designRootId ? partPath(designRootId) : ''

  const syncPartIds = useMemo(
    () => Object.entries(strategyMap)
      .filter(([, s]) => s === 'SYNC')
      .map(([id]) => id),
    [strategyMap],
  )
  const removePartIds = useMemo(
    () => Object.entries(strategyMap)
      .filter(([, s]) => s === 'REMOVE')
      .map(([id]) => id),
    [strategyMap],
  )

  async function runDetect() {
    if (!targetPath) {
      setTransformError('Kein MBOM-/Design-Root vorhanden — DetectDiscrepancies nicht möglich.')
      return
    }
    setTransformBusy('detect')
    setTransformError(null)
    setTransformResult(null)
    try {
      const r = await postTransformerDetect(code, {
        targetPath,
        // Empty selection → Windchill diff-t alle EBOM-Knoten gegen die MBOM.
        sourcePartPaths: [],
      })
      setTransformResult(r)
    } catch (e) {
      setTransformError(String((e as Error)?.message ?? e))
    } finally {
      setTransformBusy(null)
    }
  }

  /** Auto-Sync: Generate/Update mit leerer SourcePartSelection → Windchill
   *  betrachtet alle EBOM-Knoten unter dem TargetPath. Deckt 90% der Fälle. */
  async function runAutoSync() {
    if (!targetPath) {
      setTransformError('Kein MBOM-/Design-Root vorhanden.')
      setConfirmKind(null)
      return
    }
    setTransformBusy('autoSync')
    setTransformError(null)
    setTransformResult(null)
    try {
      const r = await postTransformerGenerate(code, {
        targetPath,
        sourcePartPaths: [],
      })
      setTransformResult(r)
    } catch (e) {
      setTransformError(String((e as Error)?.message ?? e))
    } finally {
      setTransformBusy(null)
      setConfirmKind(null)
    }
  }

  /** Sync Selection: nur die als SYNC markierten MBOM-Knoten triggern eine
   *  Synchronisation — wir geben deren OIDs als Filter mit. Hinweis: Windchill
   *  erwartet hier streng genommen EBOM-Pfade; für v1 senden wir die MBOM-OIDs
   *  und vertrauen auf serverseitige Auflösung via Equivalence-Map. Falls das
   *  fehlschlägt, bleibt Auto-Sync der zuverlässige Fallback. */
  async function runSyncSelection() {
    if (!targetPath) {
      setTransformError('Kein MBOM-/Design-Root vorhanden.')
      setConfirmKind(null)
      return
    }
    if (syncPartIds.length === 0) {
      setTransformError('Keine MBOM-Knoten als SYNC markiert.')
      setConfirmKind(null)
      return
    }
    setTransformBusy('syncSel')
    setTransformError(null)
    setTransformResult(null)
    try {
      const r = await postTransformerGenerate(code, {
        targetPath,
        sourcePartPaths: syncPartIds.map(partPath),
      })
      setTransformResult(r)
    } catch (e) {
      setTransformError(String((e as Error)?.message ?? e))
    } finally {
      setTransformBusy(null)
      setConfirmKind(null)
    }
  }

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
                : 'Kein Manufacturing-Pendant — nutze „Auto-Sync from EBOM“ für Initial-Generate.'
            }
            strategyMap={strategyMap}
            onCycleStrategy={cycleStrategy}
            headerExtra={
              <div className="flex items-center gap-1">
                <button
                  onClick={runDetect}
                  disabled={transformBusy !== null || !targetPath}
                  className="text-[11px] px-2 py-0.5 rounded bg-sky-600 text-white hover:bg-sky-700 disabled:opacity-50"
                  title="DetectDiscrepancies — Vorschau, was zwischen EBOM und MBOM auseinanderläuft (read-only)"
                >
                  {transformBusy === 'detect' ? '…' : 'Detect (Preview)'}
                </button>
                <button
                  onClick={() => setConfirmKind('autoSync')}
                  disabled={transformBusy !== null || !targetPath}
                  className="text-[11px] px-2 py-0.5 rounded bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50"
                  title="Generiert/aktualisiert ALLE MBOM-Knoten anhand der aktuellen EBOM (Standard-Workflow)"
                >
                  {transformBusy === 'autoSync' ? '…' : 'Auto-Sync from EBOM'}
                </button>
                <button
                  onClick={() => setConfirmKind('syncSel')}
                  disabled={transformBusy !== null || !targetPath || syncPartIds.length === 0}
                  className="text-[11px] px-2 py-0.5 rounded bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
                  title={`Synchronisiert nur die ${syncPartIds.length} als SYNC markierten Knoten`}
                >
                  {transformBusy === 'syncSel' ? '…' : `Sync Selection (${syncPartIds.length})`}
                </button>
              </div>
            }
          />
        </div>
      )}

      {modalNode && (
        <NodeDetailModal node={modalNode} onClose={() => setModalNode(null)} />
      )}

      {/* Phase 2b: BomTransformation v3 — Detect / Generate Result Panel */}
      {!loading && !error && data && (transformError || transformResult) && (
        <div className="bg-white rounded shadow-sm border border-slate-200 p-3 text-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-violet-100 text-violet-700">
              Phase 2b · BomTransformation v3
            </span>
            <button
              onClick={() => { setTransformError(null); setTransformResult(null) }}
              className="text-slate-400 hover:text-slate-700"
              title="Panel schließen"
            >×</button>
          </div>
          {transformError && (
            <div className="bg-rose-50 border border-rose-200 rounded p-2 text-rose-700 whitespace-pre-wrap">
              {transformError}
            </div>
          )}
          {transformResult && (
            <div className="space-y-2">
              <div className="flex items-center gap-3 text-slate-600">
                <span>Action: <code className="font-mono">{transformResult.action}</code></span>
                <span>Status: {transformResult.ok ? <span className="text-emerald-700">OK</span> : <span className="text-rose-700">FEHLER</span>}</span>
                <span>Result-Items: {transformResult.value.length}</span>
                {transformResult.timing?.totalMs != null && (
                  <span className="text-slate-400">{transformResult.timing.totalMs} ms</span>
                )}
              </div>
              {transformResult.value.length > 0 && (
                <details>
                  <summary className="cursor-pointer text-[10px] uppercase font-semibold text-slate-500">
                    Equivalent-Usage-Associations ({transformResult.value.length})
                  </summary>
                  <pre className="mt-1 max-h-64 overflow-auto bg-slate-50 border border-slate-200 rounded p-2 font-mono text-[11px] text-slate-700">
{JSON.stringify(transformResult.value, null, 2)}
                  </pre>
                </details>
              )}
              <details>
                <summary className="cursor-pointer text-[10px] uppercase font-semibold text-slate-500">
                  Raw Response
                </summary>
                <pre className="mt-1 max-h-64 overflow-auto bg-slate-50 border border-slate-200 rounded p-2 font-mono text-[11px] text-slate-700">
{JSON.stringify(transformResult.raw, null, 2)}
                </pre>
              </details>
            </div>
          )}
        </div>
      )}

      {/* Confirmation modal for Auto-Sync / Sync Selection */}
      {confirmKind && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40"
          onClick={() => !transformBusy && setConfirmKind(null)}
        >
          <div
            className="bg-white rounded shadow-xl border border-slate-200 w-full max-w-md p-4 space-y-3"
            onClick={e => e.stopPropagation()}
          >
            <h2 className="text-sm font-semibold text-slate-800">
              {confirmKind === 'autoSync'
                ? 'Auto-Sync from EBOM ausführen?'
                : `Sync Selection (${syncPartIds.length}) ausführen?`}
            </h2>
            {confirmKind === 'autoSync' ? (
              <p className="text-xs text-slate-600">
                Ruft <code>GenerateDownstreamStructure</code> auf <strong>plm-dev</strong>{' '}
                mit leerer <code>SourcePartSelection</code> auf. Windchill betrachtet
                damit <strong>alle</strong> EBOM-Knoten unter dem Target und
                erzeugt/aktualisiert die MBOM-Pendants entsprechend.
                Die EBOM bleibt unverändert.
              </p>
            ) : (
              <p className="text-xs text-slate-600">
                Ruft <code>GenerateDownstreamStructure</code> nur für die{' '}
                <strong>{syncPartIds.length}</strong> als{' '}
                <span className="text-indigo-700 font-semibold">SYNC</span> markierten
                MBOM-Knoten auf. Andere Knoten bleiben unverändert.
              </p>
            )}
            {removePartIds.length > 0 && (
              <p className="text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded p-2">
                Hinweis: {removePartIds.length} Knoten sind als{' '}
                <span className="font-semibold">REMOVE</span> markiert. REMOVE wird
                in dieser Phase <strong>nicht</strong> ausgeführt — kommt mit Phase 2c
                (PTC.ProdMgmt). Markierungen bleiben aber erhalten.
              </p>
            )}
            <p className="text-xs text-slate-500">
              Target: <code className="font-mono">{targetPath || '—'}</code>
            </p>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setConfirmKind(null)}
                disabled={transformBusy !== null}
                className="text-xs px-3 py-1 rounded border border-slate-300 text-slate-600 hover:bg-slate-50 disabled:opacity-50"
              >
                Abbrechen
              </button>
              <button
                onClick={confirmKind === 'autoSync' ? runAutoSync : runSyncSelection}
                disabled={transformBusy !== null}
                className="text-xs px-3 py-1 rounded bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                {transformBusy === 'autoSync' || transformBusy === 'syncSel'
                  ? 'Läuft …'
                  : 'Ja, ausführen'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

