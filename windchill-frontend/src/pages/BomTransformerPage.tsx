import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  getBomTransformer,
  getObjectDetail,
  postTransformerDetect,
  postTransformerGenerate,
  postTransformerCopy,
  postTransformerRemove,
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
  getStrategy?: (node: BomTreeNode) => 'KEEP' | 'COPY' | 'REMOVE'
  onCycleStrategy?: (node: BomTreeNode) => void
  chipMode?: 'source' | 'target'
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
  getStrategy,
  onCycleStrategy,
  chipMode,
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
        {headerExtra}
      </div>
      <div className="flex-1 min-h-0 overflow-auto">
        {root ? (
          <table className="w-full text-sm border-collapse">
            <thead className="bg-slate-100 text-slate-600 text-xs border-b border-slate-200 sticky top-0 z-10">
              <tr>
                {getStrategy && (
                  <th className="text-left px-1 py-2 font-medium w-20 text-[10px] uppercase tracking-wider">
                    Action
                  </th>
                )}
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
                getStrategy={getStrategy}
                onCycleStrategy={onCycleStrategy}
                chipMode={chipMode}
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
  const [modalNode, setModalNode] = useState<BomTreeNode | null>(null)
  // Phase 2b: per-node transform strategy.
  // KEEP   = Knoten bleibt unangetastet (default)
  // COPY   = nur auf EBOM-Seite sinnvoll → wird via PasteSpecial in MBOM kopiert
  // REMOVE = nur auf MBOM-Seite sinnvoll → visuell, Ausführung in Phase 2c (PTC.ProdMgmt)
  // Phase 2b/2c: per-side, per-node strategy overrides. Maps store ONLY user
  // overrides. The effective strategy is computed by `getEbomStrategy` /
  // `getMfgStrategy` below (which fall back to a context-aware default).
  // Two separate maps are required: a Part can appear in both trees with the
  // same partId (shared part without manufacturing-specific variant), and a
  // single map would entangle the two sides.
  const [ebomOverride, setEbomOverride] = useState<Record<string, 'KEEP' | 'COPY'>>({})
  const [mfgOverride, setMfgOverride] = useState<Record<string, 'KEEP' | 'REMOVE'>>({})
  const [transformBusy, setTransformBusy] = useState<null | 'detect' | 'autoSync' | 'copy' | 'remove'>(null)
  const [transformResult, setTransformResult] = useState<TransformResponse | null>(null)
  const [transformError, setTransformError] = useState<string | null>(null)
  const [confirmKind, setConfirmKind] = useState<null | 'autoSync' | 'copy' | 'remove'>(null)
  // Auto-Detect: rohe DiscrepancyItems aus ``BomTransformation/DetectDiscrepancies``.
  // Sobald die Page lädt und ein TargetPath bekannt ist, fragen wir Windchill
  // einmalig nach den Discrepancies. Diese werden dann zum Pre-Marken der
  // EBOM-Knoten genutzt (Status NEW/MODIFIED → Default COPY) — semantisch
  // korrekt, server-seitig aufgelöst, ein einziger Roundtrip.
  const [detectItems, setDetectItems] = useState<Array<Record<string, unknown>> | null>(null)
  const [detectAutoBusy, setDetectAutoBusy] = useState(false)
  const [detectAutoError, setDetectAutoError] = useState<string | null>(null)

  useEffect(() => {
    if (!code) return
    const ctrl = new AbortController()
    setLoading(true)
    setError(null)
    setModalNode(null)
    setEbomOverride({})
    setMfgOverride({})
    setDetectItems(null)
    setDetectAutoError(null)
    getBomTransformer(code, ctrl.signal)
      .then(setData)
      .catch(e => {
        if (e?.name !== 'AbortError') setError(String(e?.message ?? e))
      })
      .finally(() => setLoading(false))
    return () => ctrl.abort()
  }, [code])

  const columns = COMPACT_COLUMNS

  const handleShowDetail = useCallback((node: BomTreeNode) => {
    setModalNode(node)
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
  // SourceRoot/TargetRoot sind im Detect-Body nicht vorgesehen — laut Swagger
  // hat der DiscrepancyContext nur UpstreamChangeOid / SourcePartSelection /
  // TargetPath. Wir senden den Body daher ohne weitere Felder.

  // Fire-and-forget DetectDiscrepancies as soon as a sourceRoot is available.
  // Wir fragen einmal pro geladener Page — der Aufruf ist read-only und
  // liefert in einem Roundtrip die Identität-aufgelöste Diff-Liste, die wir
  // sonst per Heuristik (Number-Match) nur ungenau approximieren könnten.
  // 404 (Domain nicht deployed — z. B. plm-prod) wird stillschweigend
  // ignoriert; die Page funktioniert dann ohne Pre-Marking weiter.
  useEffect(() => {
    if (!code) return
    const ctrl = new AbortController()
    setDetectAutoBusy(true)
    setDetectAutoError(null)
    postTransformerDetect(code, {})
      .then(r => {
        if (ctrl.signal.aborted) return
        setDetectItems(Array.isArray(r.value) ? r.value : [])
      })
      .catch(e => {
        if (e?.name === 'AbortError') return
        const msg = String(e?.message ?? e)
        // 404 = Domain auf diesem Windchill nicht deployed (prod). Kein Fehler-Indikator.
        if (/\b404\b|nicht deploy/i.test(msg)) {
          setDetectItems([])
        } else {
          setDetectAutoError(msg)
          setDetectItems([])
        }
      })
      .finally(() => {
        if (!ctrl.signal.aborted) setDetectAutoBusy(false)
      })
    return () => ctrl.abort()
  }, [code])

  // Tree-walker: collect partIds + Numbers + (partId → usageLinkId) for a subtree.
  // The usageLinkId is the ID of the WTPartUsageLink that connects each node
  // to its parent — only that link can be deleted (Phase 2c REMOVE). The root
  // node has no incoming link and is therefore not removable.
  const walkTree = useCallback(
    (root: BomTreeNode | null): {
      ids: Set<string>
      numbers: Set<string>
      linkByPart: Map<string, string>
    } => {
      const ids = new Set<string>()
      const numbers = new Set<string>()
      const linkByPart = new Map<string, string>()
      const stack: BomTreeNode[] = root ? [root] : []
      while (stack.length) {
        const n = stack.pop()!
        if (n.partId) {
          ids.add(n.partId)
          if (n.usageLinkId) linkByPart.set(n.partId, n.usageLinkId)
        }
        if (n.number) numbers.add(n.number)
        if (n.children) for (const c of n.children) stack.push(c)
      }
      return { ids, numbers, linkByPart }
    },
    [],
  )

  const ebomWalk = useMemo(() => walkTree(data?.designRoot ?? null), [data, walkTree])
  const mfgWalk = useMemo(() => walkTree(data?.manufacturingRoot ?? null), [data, walkTree])
  const mfgIds = mfgWalk.ids

  // Discrepancy-Item-Index: Set von ``Number`` aller Items, die DetectDiscrepancies
  // für diese Page geliefert hat. Solche Numbers entsprechen EBOM-Knoten, die
  // *nicht identisch* in der MBOM stehen (NEW oder MODIFIED) — also exakt die
  // Kandidaten für PasteSpecial → Default COPY. Die Status-Differenzierung
  // ist hier nicht nötig: alle non-identical Items wollen kopiert werden.
  // Falls Detect (noch) nicht geladen ist, fällt der Default auf einen sicheren
  // Wert zurück — siehe getEbomStrategy.
  const discrepancyNumbers = useMemo(() => {
    const s = new Set<string>()
    if (!detectItems) return s
    for (const it of detectItems) {
      const num = (it.Number ?? it.number ?? it.PartNumber ?? it.partNumber) as
        | string
        | undefined
      if (typeof num === 'string' && num) s.add(num)
    }
    return s
  }, [detectItems])

  // Effective strategy resolvers.
  //   EBOM: COPY wenn der Knoten in der DetectDiscrepancy-Antwort vorkommt
  //         (Status NEW/MODIFIED — kein Pendant oder abweichendes Pendant).
  //         Solange Detect noch lädt, defaulten wir konservativ auf KEEP, damit
  //         keine Übergangs-Chips aufpoppen, die der Server gleich widerruft.
  //         Schlägt Detect fehl, bleiben alle EBOM-Defaults KEEP — der User
  //         kann immer noch manuell COPY setzen oder den Detect-Button benutzen.
  //   MBOM: immer KEEP — REMOVE ist destruktiv und muss opt-in sein.
  const getEbomStrategy = useCallback(
    (node: BomTreeNode): 'KEEP' | 'COPY' | 'REMOVE' => {
      const id = node.partId || ''
      if (id && id in ebomOverride) return ebomOverride[id]
      if (!detectItems) return 'KEEP'
      return node.number && discrepancyNumbers.has(node.number) ? 'COPY' : 'KEEP'
    },
    [ebomOverride, detectItems, discrepancyNumbers],
  )
  const getMfgStrategy = useCallback(
    (node: BomTreeNode): 'KEEP' | 'COPY' | 'REMOVE' => {
      const id = node.partId || ''
      return (id && mfgOverride[id]) || 'KEEP'
    },
    [mfgOverride],
  )

  // Side-aware chip cycle. Initialize from default before flipping so the
  // first click on an auto-COPY node does the intuitive thing (COPY → KEEP).
  const cycleEbomStrategy = useCallback((node: BomTreeNode) => {
    const id = node.partId || ''
    if (!id) return
    const cur = getEbomStrategy(node)
    const next: 'KEEP' | 'COPY' = cur === 'COPY' ? 'KEEP' : 'COPY'
    setEbomOverride(prev => ({ ...prev, [id]: next }))
  }, [getEbomStrategy])
  const cycleMfgStrategy = useCallback((node: BomTreeNode) => {
    const id = node.partId || ''
    if (!id) return
    const cur = getMfgStrategy(node)
    const next: 'KEEP' | 'REMOVE' = cur === 'REMOVE' ? 'KEEP' : 'REMOVE'
    setMfgOverride(prev => ({ ...prev, [id]: next }))
  }, [getMfgStrategy])

  // Collect effective COPY partIds across the whole loaded EBOM tree.
  const copyPartIds = useMemo(() => {
    const out: string[] = []
    const stack: BomTreeNode[] = data?.designRoot ? [data.designRoot] : []
    while (stack.length) {
      const n = stack.pop()!
      if (n.partId && getEbomStrategy(n) === 'COPY') out.push(n.partId)
      if (n.children) for (const c of n.children) stack.push(c)
    }
    return out
  }, [data, getEbomStrategy])

  const removePartIds = useMemo(
    () => Object.entries(mfgOverride)
      .filter(([id, s]) => s === 'REMOVE' && mfgIds.has(id))
      .map(([id]) => id),
    [mfgOverride, mfgIds],
  )
  // Resolve REMOVE-marked partIds to their UsageLink IDs. Root is excluded
  // automatically (no incoming link). Nodes whose link wasn't loaded yet
  // are dropped — user must expand them first.
  const removeLinkIds = useMemo(
    () => removePartIds
      .map(id => mfgWalk.linkByPart.get(id))
      .filter((v): v is string => !!v),
    [removePartIds, mfgWalk],
  )
  const removeUnresolved = removePartIds.length - removeLinkIds.length

  async function runDetect() {
    setTransformBusy('detect')
    setTransformError(null)
    setTransformResult(null)
    try {
      const r = await postTransformerDetect(code, {})
      setTransformResult(r)
    } catch (e) {
      setTransformError(String((e as Error)?.message ?? e))
    } finally {
      setTransformBusy(null)
    }
  }

  /** Auto-Sync: GenerateDownstreamStructure mit leerer SourcePartSelection.
   *  Windchill betrachtet alle EBOM-Knoten unter dem TargetPath und erzeugt /
   *  aktualisiert die MBOM-Pendants. Standard-Workflow für „komplett übernehmen". */
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

  /** Apply COPY: PasteSpecial mit den als COPY markierten EBOM-Knoten unter
   *  den MBOM-Target. OData-Equivalent zum Drag&Drop in der Windchill-GUI. */
  async function runApplyCopy() {
    if (!targetPath) {
      setTransformError('Kein MBOM-/Design-Root vorhanden.')
      setConfirmKind(null)
      return
    }
    if (copyPartIds.length === 0) {
      setTransformError('Keine EBOM-Knoten als COPY markiert.')
      setConfirmKind(null)
      return
    }
    setTransformBusy('copy')
    setTransformError(null)
    setTransformResult(null)
    try {
      const r = await postTransformerCopy(code, {
        targetPath,
        sourcePartPaths: copyPartIds.map(partPath),
      })
      setTransformResult(r)
    } catch (e) {
      setTransformError(String((e as Error)?.message ?? e))
    } finally {
      setTransformBusy(null)
      setConfirmKind(null)
    }
  }

  /** Apply REMOVE: löscht die UsageLinks der als REMOVE markierten MBOM-Knoten
   *  via PTC.ProdMgmt.UsageLinks('<id>'). Liefert per-Link Erfolg/Fehler zurück. */
  async function runApplyRemove() {
    if (removeLinkIds.length === 0) {
      setTransformError('Keine MBOM-UsageLinks zum Entfernen aufgelöst.')
      setConfirmKind(null)
      return
    }
    setTransformBusy('remove')
    setTransformError(null)
    setTransformResult(null)
    try {
      const r = await postTransformerRemove(code, { usageLinkIds: removeLinkIds })
      // Wrap the per-link response into a TransformResponse-shaped object so
      // the existing result panel can show it without a second renderer.
      setTransformResult({
        ok: r.ok,
        action: 'RemoveUsageLinks',
        value: [
          ...r.removed.map(id => ({ usageLinkId: id, status: 'removed' })),
          ...r.failed.map(f => ({ usageLinkId: f.usageLinkId, status: 'failed', error: f.error })),
        ],
        raw: r as unknown as Record<string, unknown>,
        timing: r.timing ?? {},
      } as TransformResponse)
      // Drop strategies for successfully removed nodes — the tree will re-load
      // on next refresh; until then the chips would be stale.
      if (r.removed.length > 0) {
        const removedPartIds = new Set(
          removePartIds.filter(pid => {
            const lid = mfgWalk.linkByPart.get(pid)
            return lid && r.removed.includes(lid)
          }),
        )
        setMfgOverride(prev => {
          const next = { ...prev }
          for (const pid of removedPartIds) delete next[pid]
          return next
        })
      }
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
            getStrategy={getEbomStrategy}
            onCycleStrategy={cycleEbomStrategy}
            chipMode="source"
            headerExtra={
              <div className="flex items-center gap-2">
                <span
                  className="text-[10px] text-slate-500 italic"
                  title="EBOM wird nie geschrieben — COPY markiert nur, was per PasteSpecial in die MBOM übernommen wird"
                >
                  read-only
                </span>
                {detectAutoBusy ? (
                  <span className="text-[10px] text-slate-400" title="DetectDiscrepancies läuft …">
                    scanning…
                  </span>
                ) : detectAutoError ? (
                  <span
                    className="text-[10px] text-rose-600"
                    title={`Auto-Detect fehlgeschlagen: ${detectAutoError}`}
                  >
                    detect err
                  </span>
                ) : detectItems ? (
                  <span
                    className="text-[10px] text-emerald-600"
                    title={`${discrepancyNumbers.size} Discrepancy-Item(s) — als COPY vorgemarkt`}
                  >
                    {discrepancyNumbers.size} diff
                  </span>
                ) : null}
              </div>
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
            getStrategy={getMfgStrategy}
            onCycleStrategy={cycleMfgStrategy}
            chipMode="target"
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
                  title="GenerateDownstreamStructure — alle EBOM-Knoten in die MBOM übernehmen (Initial-Generate / Bulk-Update)"
                >
                  {transformBusy === 'autoSync' ? '…' : 'Auto-Sync from EBOM'}
                </button>
                <button
                  onClick={() => setConfirmKind('copy')}
                  disabled={transformBusy !== null || !targetPath || copyPartIds.length === 0}
                  className="text-[11px] px-2 py-0.5 rounded bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
                  title={`PasteSpecial — kopiert nur die ${copyPartIds.length} als COPY markierten EBOM-Knoten`}
                >
                  {transformBusy === 'copy' ? '…' : `Apply COPY (${copyPartIds.length})`}
                </button>
                <button
                  onClick={() => setConfirmKind('remove')}
                  disabled={transformBusy !== null || removeLinkIds.length === 0}
                  className="text-[11px] px-2 py-0.5 rounded bg-rose-600 text-white hover:bg-rose-700 disabled:opacity-50"
                  title={
                    removeUnresolved > 0
                      ? `${removeLinkIds.length} resolvable / ${removeUnresolved} not yet expanded`
                      : `Löscht die ${removeLinkIds.length} markierten MBOM-UsageLinks via PTC.ProdMgmt`
                  }
                >
                  {transformBusy === 'remove' ? '…' : `Apply REMOVE (${removeLinkIds.length})`}
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
                : confirmKind === 'copy'
                  ? `Apply COPY (${copyPartIds.length}) ausführen?`
                  : `Apply REMOVE (${removeLinkIds.length}) ausführen?`}
            </h2>
            {confirmKind === 'autoSync' ? (
              <p className="text-xs text-slate-600">
                Ruft <code>GenerateDownstreamStructure</code> auf <strong>plm-dev</strong>{' '}
                mit leerer <code>SourcePartSelection</code> auf. Windchill betrachtet
                damit <strong>alle</strong> EBOM-Knoten unter dem Target und
                erzeugt/aktualisiert die MBOM-Pendants entsprechend.
                Die EBOM bleibt unverändert.
              </p>
            ) : confirmKind === 'copy' ? (
              <p className="text-xs text-slate-600">
                Ruft <code>PasteSpecial</code> auf <strong>plm-dev</strong> auf und
                kopiert die <strong>{copyPartIds.length}</strong> als{' '}
                <span className="text-emerald-700 font-semibold">COPY</span> markierten
                EBOM-Knoten unter den MBOM-Target. Andere Knoten bleiben unverändert.
                Die EBOM bleibt unverändert.
              </p>
            ) : (
              <>
                <p className="text-xs text-slate-600">
                  Löscht die <strong>{removeLinkIds.length}</strong> als{' '}
                  <span className="text-rose-700 font-semibold">REMOVE</span> markierten
                  MBOM-UsageLinks via <code>PTC.ProdMgmt.UsageLinks('&lt;id&gt;')</code>.
                  Nur die Parent→Child-Beziehung wird gekappt — die referenzierten Parts
                  selbst bleiben in Windchill bestehen. Die EBOM bleibt unverändert.
                </p>
                {removeUnresolved > 0 && (
                  <p className="text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded p-2">
                    {removeUnresolved} markierte Knoten konnten nicht aufgelöst werden
                    (UsageLink unbekannt — Knoten ggf. erst aufklappen oder Root-Knoten markiert).
                    Diese werden übersprungen.
                  </p>
                )}
              </>
            )}
            {confirmKind !== 'remove' && removePartIds.length > 0 && (
              <p className="text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded p-2">
                Hinweis: {removePartIds.length} Knoten sind als{' '}
                <span className="font-semibold">REMOVE</span> markiert — sie werden
                durch diese Aktion <strong>nicht</strong> entfernt. Nutze
                „Apply REMOVE" separat.
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
                onClick={
                  confirmKind === 'autoSync'
                    ? runAutoSync
                    : confirmKind === 'copy'
                      ? runApplyCopy
                      : runApplyRemove
                }
                disabled={transformBusy !== null}
                className={
                  'text-xs px-3 py-1 rounded text-white disabled:opacity-50 ' +
                  (confirmKind === 'remove'
                    ? 'bg-rose-600 hover:bg-rose-700'
                    : 'bg-emerald-600 hover:bg-emerald-700')
                }
              >
                {transformBusy === 'autoSync'
                  || transformBusy === 'copy'
                  || transformBusy === 'remove'
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

