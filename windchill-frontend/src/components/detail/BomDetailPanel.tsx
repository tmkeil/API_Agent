import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getObjectDetail, getPartDocuments, getPartCadDocuments } from '../../api/client'
import type { BomTreeNode, DocumentNode, ObjectDetail } from '../../api/types'
import { subtypeBadgeStyle } from '../../utils/labels'

/* ────────────────────── public interface ───────────────────── */

interface Props {
  /** The currently selected BOM node. */
  node: BomTreeNode
  /** Called when the user clicks the close button. */
  onClose: () => void
}

type PanelTab = 'summary' | 'attributes' | 'documents'

/* ════════════════════════════════════════════════════════════ */

export default function BomDetailPanel({ node, onClose }: Props) {
  const [detail, setDetail] = useState<ObjectDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<PanelTab>('summary')
  const navigate = useNavigate()

  // Fetch ObjectDetail whenever the selected node changes
  const load = useCallback(async (signal: AbortSignal) => {
    if (!node.number) return
    setLoading(true)
    setError('')
    setDetail(null)
    try {
      const resp = await getObjectDetail('part', node.number, signal)
      if (signal.aborted) return
      setDetail(resp.detail)
    } catch (e: unknown) {
      if (signal.aborted) return
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)
    } finally {
      if (!signal.aborted) setLoading(false)
    }
  }, [node.number])

  useEffect(() => {
    const ctrl = new AbortController()
    load(ctrl.signal)
    return () => ctrl.abort()
  }, [load])

  const tabs: { key: PanelTab; label: string }[] = [
    { key: 'summary', label: 'Übersicht' },
    { key: 'attributes', label: 'Attribute' },
    { key: 'documents', label: 'Documents' },
  ]

  return (
    <div className="flex flex-col h-full border-l border-slate-200 bg-white">
      {/* ── Panel header ── */}
      <div className="flex items-center justify-between gap-2 px-3 py-2 border-b border-slate-200 bg-slate-50 shrink-0">
        <div className="min-w-0 flex items-center gap-2">
          <span className={`shrink-0 inline-block border px-1 rounded text-[10px] font-medium ${subtypeBadgeStyle(node.type || 'Part')}`}>
            {node.type || 'Part'}
          </span>
          <span className="font-mono text-sm font-semibold text-slate-800 truncate">
            {node.number}
          </span>
          <button
            onClick={() => navigate(`/detail/part/${encodeURIComponent(node.number)}`)}
            className="shrink-0 text-indigo-400 hover:text-indigo-600 transition-colors"
            title="Detailseite öffnen"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </button>
        </div>
        <button
          onClick={onClose}
          className="shrink-0 text-slate-400 hover:text-slate-600 transition-colors"
          title="Close panel"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* ── Sub-tab bar ── */}
      <nav className="flex border-b border-slate-200 bg-white shrink-0">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`px-3 py-1.5 text-xs font-medium border-b-2 transition-colors ${
              activeTab === t.key
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {/* ── Content area ── */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden p-3">
        {loading && (
          <p className="text-xs text-slate-400 animate-pulse py-4">Loading details…</p>
        )}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-xs rounded p-2">
            {error}
          </div>
        )}
        {!loading && !error && (
          <>
            {activeTab === 'summary' && <SummaryContent node={node} detail={detail} />}
            {activeTab === 'attributes' && <AttributesContent detail={detail} />}
            {activeTab === 'documents' && <DocumentsContent partCode={node.number} />}
          </>
        )}
      </div>
    </div>
  )
}

/* ═══════════════════  Sub-tab content  ═══════════════════ */

/** Summary — Windchill-style grouped key-value display. */
function SummaryContent({ node, detail }: { node: BomTreeNode; detail: ObjectDetail | null }) {
  // Build sections from ObjectDetail if available, fall back to BomTreeNode fields
  const summaryRows: [string, string][] = [
    ['Typ', node.type || '—'],
    ['Nummer', node.number],
    ['Name', node.name || '—'],
    ['Version', node.version || '—'],
    ['Status', node.state || '—'],
  ]

  if (detail) {
    summaryRows.push(
      ['Iteration', detail.iteration || '—'],
      ['Kontext', detail.context || '—'],
      ['Last modified', detail.lastModified || '—'],
      ['Created on', detail.createdOn || '—'],
    )
  }

  // Extract Balluff-specific or "Identity" fields from allAttributes
  const identityKeys = [
    'Description', 'Source', 'AssociatedProductFamily',
    'AssemblyMode', 'GatheringPart', 'DefaultUnit', 'EndItem',
  ]
  const identityRows: [string, string][] = []
  if (detail?.allAttributes) {
    for (const k of identityKeys) {
      const v = detail.allAttributes[k]
      if (v != null && v !== '') identityRows.push([k, String(v)])
    }
  }

  // SAP fields
  const sapKeys = [
    'BALSAPNAME', 'BALSAPRolloutStrategy', 'BALSAPOrderCode',
    'BALSAPCrossPlantMaterialState', 'BALSAPAssignedPlants',
    'BALSAPMaterialType', 'BALPVID',
  ]
  const sapRows: [string, string][] = []
  if (detail?.allAttributes) {
    for (const k of sapKeys) {
      const v = detail.allAttributes[k]
      if (v != null && v !== '') sapRows.push([k.replace(/^BAL/, ''), String(v)])
    }
  }

  return (
    <div className="space-y-3">
      <FieldsetSection title="Zusammenfassung" rows={summaryRows} />
      {identityRows.length > 0 && <FieldsetSection title="Identity" rows={identityRows} />}
      {sapRows.length > 0 && <FieldsetSection title="SAP" rows={sapRows} />}
    </div>
  )
}

/** Grouped fieldset like Windchill's grouped attribute sections. */
function FieldsetSection({ title, rows }: { title: string; rows: [string, string][] }) {
  return (
    <fieldset className="border border-slate-200 rounded px-3 py-2">
      <legend className="text-[10px] font-semibold text-slate-500 uppercase tracking-wide px-1">
        {title}
      </legend>
      <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-xs">
        {rows.map(([label, value], i) => (
          <Fragment key={`${label}-${i}`}>
            <dt className="text-slate-500 font-medium whitespace-nowrap">{label}:</dt>
            <dd className="text-slate-700 break-words">{value}</dd>
          </Fragment>
        ))}
      </dl>
    </fieldset>
  )
}

import { Fragment } from 'react'

/** All attributes — compact searchable table. */
function AttributesContent({ detail }: { detail: ObjectDetail | null }) {
  const [filter, setFilter] = useState('')
  const attrs = detail?.allAttributes || {}
  const entries = Object.entries(attrs)

  const filtered = filter
    ? entries.filter(([k, v]) => {
        const q = filter.toLowerCase()
        return k.toLowerCase().includes(q) || String(v).toLowerCase().includes(q)
      })
    : entries

  filtered.sort((a, b) => a[0].localeCompare(b[0]))

  if (entries.length === 0) {
    return <p className="text-xs text-slate-400 py-2">Keine Attribute verfügbar.</p>
  }

  return (
    <div className="space-y-2">
      <input
        type="text"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Attribut filtern…"
        className="w-full px-2 py-1 text-xs border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-500"
      />
      <div className="text-[10px] text-slate-400">
        {filtered.length} / {entries.length}
      </div>
      <div className="overflow-auto" style={{ maxHeight: '50vh' }}>
        <table className="w-full text-xs">
          <tbody className="divide-y divide-slate-100">
            {filtered.map(([key, value]) => (
              <tr key={key} className="hover:bg-slate-50/50">
                <td className="py-1 pr-2 text-slate-500 font-mono text-[10px] whitespace-nowrap align-top">{key}</td>
                <td className="py-1 text-slate-700 break-words">{fmtVal(value)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function fmtVal(v: unknown): string {
  if (v === null || v === undefined) return '—'
  if (typeof v === 'boolean') return v ? 'Yes' : 'No'
  return String(v)
}

/** Compact combined documents list for the panel. */
function DocumentsContent({ partCode }: { partCode: string }) {
  const [docs, setDocs] = useState<DocumentNode[]>([])
  const [cadDocs, setCadDocs] = useState<DocumentNode[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const ctrl = new AbortController()
    setLoading(true)
    setError('')
    Promise.all([
      getPartDocuments(partCode, ctrl.signal),
      getPartCadDocuments(partCode, ctrl.signal),
    ])
      .then(([d, c]) => {
        if (ctrl.signal.aborted) return
        setDocs(d.documents)
        setCadDocs(c.documents)
      })
      .catch((e) => {
        if (ctrl.signal.aborted) return
        setError(e instanceof Error ? e.message : String(e))
      })
      .finally(() => {
        if (!ctrl.signal.aborted) setLoading(false)
      })
    return () => ctrl.abort()
  }, [partCode])

  if (loading) return <p className="text-xs text-slate-400 animate-pulse py-2">Loading…</p>
  if (error) return <p className="text-xs text-red-600 py-2">{error}</p>

  const all = [
    ...docs.map((d) => ({ ...d, cat: 'Doc' as const })),
    ...cadDocs.map((d) => ({ ...d, cat: 'CAD' as const })),
  ]

  if (all.length === 0) {
    return <p className="text-xs text-slate-400 py-2">No documents linked.</p>
  }

  return (
    <div className="space-y-1">
      <div className="text-[10px] text-slate-400">{all.length} Dokument{all.length !== 1 ? 'e' : ''}</div>
      <div className="divide-y divide-slate-100">
        {all.map((d) => {
          const typeKey = d.cat === 'CAD' ? 'cad_document' : 'document'
          return (
            <div
              key={d.docId}
              className="flex items-center gap-2 py-1 text-xs group"
            >
              <span className={`shrink-0 inline-block border px-1 rounded text-[9px] font-medium ${subtypeBadgeStyle(d.subType || (d.cat === 'CAD' ? 'CAD-Dokument' : 'Dokument'))}`}>
                {d.subType || d.cat}
              </span>
              <span className="font-mono text-slate-600 truncate">{d.number}</span>
              <span className="text-slate-400 truncate flex-1">{d.name}</span>
              <button
                onClick={() => navigate(`/detail/${typeKey}/${encodeURIComponent(d.number)}`)}
                className="shrink-0 text-indigo-400 hover:text-indigo-600 opacity-0 group-hover:opacity-100 transition-all"
                title="Detailseite öffnen"
              >
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
