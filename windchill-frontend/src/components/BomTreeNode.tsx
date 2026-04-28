import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getBomChildren } from '../api/client'
import type { BomTreeNode, BomViewColumn, DocumentNode } from '../api/types'
import { subtypeBadgeStyle } from '../utils/labels'

interface Props {
  node: BomTreeNode
  depth: number
  viewColumns: BomViewColumn[]
  totalCols: number
  /** Called when a row is clicked to select it (for split-view panel). */
  onSelect?: (node: BomTreeNode) => void
  /** The partId of the currently selected node (used for highlight). */
  selectedPartId?: string
  /** When provided, an explicit info button is rendered next to the
   *  number-column external-link icon. Click invokes this callback
   *  (does not toggle expansion). Used by the BOM Transformer page to
   *  open a modal with full attributes. */
  onShowDetail?: (node: BomTreeNode) => void
  /** When provided, a KEEP/NEW/REMOVE strategy chip is rendered at the
   *  start of each row. Click cycles through the three states. Used by
   *  the BOM Transformer page (Phase 2b). */
  strategyMap?: Record<string, 'KEEP' | 'NEW' | 'REMOVE'>
  onCycleStrategy?: (node: BomTreeNode) => void
}

/** Resolve a column value from a BomTreeNode based on the column config. */
/** Attribute bags for nested sources; everything else reads directly from node. */
const ATTR_BAGS: Record<string, (n: BomTreeNode) => Record<string, unknown> | undefined> = {
  usageLink: n => n.usageLinkAttributes as Record<string, unknown> | undefined,
  partAttr:  n => n.partAttributes as Record<string, unknown> | undefined,
}

const DOC_ATTR_BAGS: Record<string, (d: DocumentNode) => Record<string, unknown> | undefined> = {
  docAttr: d => d.docAttributes as Record<string, unknown> | undefined,
}

function getCellValue(node: BomTreeNode, col: BomViewColumn): string {
  const bag = ATTR_BAGS[col.source]?.(node) ?? (node as unknown as Record<string, unknown>)
  const val = bag?.[col.key]
  return val != null ? String(val) : ''
}

/** Resolve a column value from a DocumentNode — maps shared fields dynamically. */
function getDocCellValue(doc: DocumentNode, col: BomViewColumn): string {
  // Documents only have number, name, version, state as named fields.
  // Map them when the view column key matches, regardless of source.
  const docRecord: Record<string, string | undefined> = {
    number: doc.number,
    name: doc.name,
    version: doc.version,
    state: doc.state,
  }
  // "part" source keys that Documents share with Parts
  if (col.source === 'part') {
    const val = docRecord[col.key]
    return val != null ? String(val) : ''
  }
  // Document attributes (e.g. BALSAPRELEVANCE, DocTypeName)
  if (col.source === 'docAttr') {
    const bag = DOC_ATTR_BAGS.docAttr?.(doc)
    const val = bag?.[col.key]
    return val != null ? String(val) : ''
  }
  return ''
}

/**
 * BOM tree node rendered as <tr> rows inside a parent <table>.
 * Returns a React Fragment containing one or more <tr> elements.
 * Children are lazily loaded on first expand click.
 * Columns are driven by the viewColumns config (BOM view support).
 */
export default function BomTreeRow({ node, depth, viewColumns, totalCols, onSelect, selectedPartId, onShowDetail, strategyMap, onCycleStrategy }: Props) {
  const hasInitialChildren = (node.children && node.children.length > 0) || node.childrenLoaded || false
  const [expanded, setExpanded] = useState(false)
  const [children, setChildren] = useState<BomTreeNode[]>(node.children || [])
  const [documents, setDocuments] = useState<DocumentNode[]>(node.documents || [])
  const [cadDocuments, setCadDocuments] = useState<DocumentNode[]>(node.cadDocuments || [])
  const [loaded, setLoaded] = useState(hasInitialChildren)
  const [loading, setLoading] = useState(false)
  const [noChildren, setNoChildren] = useState(false)
  const navigate = useNavigate()
  const isSelected = selectedPartId === node.partId

  const toggle = useCallback(async () => {
    if (loading) return

    if (expanded) {
      setExpanded(false)
      return
    }

    // If children not loaded yet, fetch and expand in one go
    if (!loaded && node.hasChildren && node.partId) {
      setLoading(true)
      try {
        const resp = await getBomChildren(node.partId)
        // Write back to the node object so the tree sent to export is always current
        node.children = resp.children
        node.documents = resp.documents
        node.cadDocuments = resp.cadDocuments
        node.childrenLoaded = true
        setChildren(resp.children)
        setDocuments(resp.documents)
        setCadDocuments(resp.cadDocuments)
        setLoaded(true)
        setExpanded(true)
        // Only hide the expand arrow if there is truly nothing to show
        const hasAnyContent =
          resp.children.length > 0 || resp.documents.length > 0 || resp.cadDocuments.length > 0
        if (!hasAnyContent) setNoChildren(true)
      } catch {
        // Fetch failed — keep current state
      } finally {
        setLoading(false)
      }
    } else {
      setExpanded(true)
    }
  }, [expanded, loaded, loading, node.hasChildren, node.partId])

  const indent = depth * 20 + 8

  return (
    <>
      {/* Main node row */}
      <tr
        onClick={() => {
          toggle()
          onSelect?.(node)
        }}
        className={`cursor-pointer select-none transition-colors border-b border-slate-200 ${
          isSelected
            ? 'bg-indigo-100/80 hover:bg-indigo-100'
            : 'hover:bg-indigo-50/60'
        }`}
      >
        {/* Expand icon + type badge + indentation */}
        <td className="px-1 py-1.5 whitespace-nowrap" style={{ paddingLeft: indent }}>
          <span className="inline-flex items-center gap-1">
            <span className="inline-flex w-4 justify-center text-slate-400 text-[11px]">
              {node.hasChildren && !noChildren ? (
                loading ? (
                  <span className="animate-spin">⟳</span>
                ) : expanded ? (
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                ) : (
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                )
              ) : (
                <span className="w-3 h-3" />
              )}
            </span>
            <span className={`inline-block border px-1 rounded text-[10px] font-medium ${subtypeBadgeStyle(node.type || 'Part')}`}>
              {node.type || 'Part'}
            </span>
            {strategyMap && onCycleStrategy && (
              <button
                onClick={(e) => { e.stopPropagation(); onCycleStrategy(node) }}
                className={`text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded border transition-colors ${
                  (strategyMap[node.partId || ''] ?? 'KEEP') === 'NEW'
                    ? 'bg-emerald-100 border-emerald-300 text-emerald-700 hover:bg-emerald-200'
                    : (strategyMap[node.partId || ''] ?? 'KEEP') === 'REMOVE'
                    ? 'bg-rose-100 border-rose-300 text-rose-700 hover:bg-rose-200'
                    : 'bg-slate-100 border-slate-300 text-slate-600 hover:bg-slate-200'
                }`}
                title="Klick zum Wechseln: KEEP → NEW → REMOVE → KEEP"
              >
                {strategyMap[node.partId || ''] ?? 'KEEP'}
              </button>
            )}
          </span>
        </td>

        {/* Dynamic columns driven by view config */}
        {viewColumns.map((col, ci) => {
          const val = getCellValue(node, col)
          const isFirst = ci === 0
          const isNumber = col.key === 'number' && col.source === 'part'
          return (
            <td
              key={col.key}
              className={`px-2 py-1.5 text-sm whitespace-nowrap ${
                col.align === 'right' ? 'text-right font-mono' : ''
              } ${isFirst ? 'font-mono text-slate-800' : 'text-slate-500'} ${
                col.key === 'name' ? 'max-w-[280px] truncate' : ''
              }`}
            >
              {isNumber && node.number ? (
                <span className="inline-flex items-center gap-1">
                  <span>{val}</span>
                  {onShowDetail && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onShowDetail(node)
                      }}
                      className="text-slate-400 hover:text-indigo-600 transition-colors"
                      title="Quick details (Modal)"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <circle cx="12" cy="12" r="9" />
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 8h.01M11 12h1v4h1" />
                      </svg>
                    </button>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      navigate(`/detail/part/${encodeURIComponent(node.number)}`)
                    }}
                    className="text-indigo-400 hover:text-indigo-600 transition-colors"
                    title="Details öffnen"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </button>
                </span>
              ) : val}
            </td>
          )
        })}
      </tr>

      {/* Expanded content */}
      {expanded && (
        <>
          {/* Documents */}
          {documents.map((doc, i) => {
            const docTypeKey = doc.type === 'EPMDocument' || doc.type === 'CADDocument' ? 'cad_document' : 'document'
            return (
            <tr
              key={`doc-${doc.docId || i}`}
              className="text-xs border-b border-slate-100"
            >
              <td style={{ paddingLeft: indent + 20 }} className="py-0.5">
                <span className={`inline-block border px-1 rounded text-[10px] font-medium ${subtypeBadgeStyle(doc.subType || 'Dokument')}`}>
                  {doc.subType || 'Doc'}
                </span>
              </td>
              {viewColumns.map((col) => {
                const val = getDocCellValue(doc, col)
                const isNumber = col.key === 'number' && col.source === 'part'
                return (
                  <td
                    key={col.key}
                    className={`px-2 py-0.5 whitespace-nowrap ${
                      col.key === 'number' ? 'font-mono text-slate-600' : 'text-slate-400'
                    } ${col.key === 'name' ? 'max-w-[280px] truncate' : ''}`}
                  >
                    {isNumber && doc.number ? (
                      <span className="inline-flex items-center gap-1">
                        <span>{val}</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            navigate(`/detail/${docTypeKey}/${encodeURIComponent(doc.number)}`)
                          }}
                          className="text-indigo-400 hover:text-indigo-600 transition-colors"
                          title="Details öffnen"
                        >
                          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </button>
                      </span>
                    ) : val}
                  </td>
                )
              })}
            </tr>
            )
          })}

          {/* CAD Documents */}
          {cadDocuments.map((doc, i) => {
            const cadTypeKey = doc.type === 'EPMDocument' || doc.type === 'CADDocument' ? 'cad_document' : 'document'
            return (
            <tr
              key={`cad-${doc.docId || i}`}
              className="text-xs border-b border-slate-100"
            >
              <td style={{ paddingLeft: indent + 20 }} className="py-0.5">
                <span className={`inline-block border px-1 rounded text-[10px] font-medium ${subtypeBadgeStyle(doc.subType || 'CAD-Dokument')}`}>
                  {doc.subType || 'CAD'}
                </span>
              </td>
              {viewColumns.map((col) => {
                const val = getDocCellValue(doc, col)
                const isNumber = col.key === 'number' && col.source === 'part'
                return (
                  <td
                    key={col.key}
                    className={`px-2 py-0.5 whitespace-nowrap ${
                      col.key === 'number' ? 'font-mono text-slate-600' : 'text-slate-400'
                    } ${col.key === 'name' ? 'max-w-[280px] truncate' : ''}`}
                  >
                    {isNumber && doc.number ? (
                      <span className="inline-flex items-center gap-1">
                        <span>{val}</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            navigate(`/detail/${cadTypeKey}/${encodeURIComponent(doc.number)}`)
                          }}
                          className="text-indigo-400 hover:text-indigo-600 transition-colors"
                          title="Details öffnen"
                        >
                          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </button>
                      </span>
                    ) : val}
                  </td>
                )
              })}
            </tr>
            )
          })}

          {/* Children */}
          {children.map((child, idx) => (
            <BomTreeRow
              key={`${child.partId || child.number}-${idx}`}
              node={child}
              depth={depth + 1}
              viewColumns={viewColumns}
              totalCols={totalCols}
              onSelect={onSelect}
              selectedPartId={selectedPartId}
              onShowDetail={onShowDetail}
              strategyMap={strategyMap}
              onCycleStrategy={onCycleStrategy}
            />
          ))}

          {/* Empty state */}
          {loaded && children.length === 0 && documents.length === 0 && cadDocuments.length === 0 && (
            <tr>
              <td
                colSpan={totalCols}
                style={{ paddingLeft: indent + 20 }}
                className="text-xs text-slate-400 italic py-1"
              >
                Keine Unterelemente
              </td>
            </tr>
          )}
        </>
      )}
    </>
  )
}