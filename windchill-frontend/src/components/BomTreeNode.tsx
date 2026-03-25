import { useCallback, useState } from 'react'
import { getBomChildren } from '../api/client'
import type { BomTreeNode, BomViewColumn, DocumentNode } from '../api/types'
import { subtypeBadgeStyle } from '../utils/labels'

interface Props {
  node: BomTreeNode
  depth: number
  viewColumns: BomViewColumn[]
  totalCols: number
}

/** Resolve a column value from a BomTreeNode based on the column config. */
function getCellValue(node: BomTreeNode, col: BomViewColumn): string {
  const nodeRecord = node as unknown as Record<string, unknown>
  // "part" source: direct field on node
  if (col.source === 'part') {
    const val = nodeRecord[col.key]
    return val != null ? String(val) : ''
  }
  // "link" source: standard extracted usage-link fields
  if (col.source === 'link') {
    const val = nodeRecord[col.key]
    return val != null ? String(val) : ''
  }
  // "usageLink" source: dynamic key inside usageLinkAttributes
  if (col.source === 'usageLink') {
    const attrs = node.usageLinkAttributes
    if (!attrs) return ''
    const val = attrs[col.key]
    return val != null ? String(val) : ''
  }
  // "partAttr" source: dynamic key inside partAttributes
  if (col.source === 'partAttr') {
    const attrs = node.partAttributes
    if (!attrs) return ''
    const val = attrs[col.key]
    return val != null ? String(val) : ''
  }
  return ''
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
  return ''
}

/**
 * BOM tree node rendered as <tr> rows inside a parent <table>.
 * Returns a React Fragment containing one or more <tr> elements.
 * Children are lazily loaded on first expand click.
 * Columns are driven by the viewColumns config (BOM view support).
 */
export default function BomTreeRow({ node, depth, viewColumns, totalCols }: Props) {
  const hasInitialChildren = (node.children && node.children.length > 0) || node.childrenLoaded || false
  const [expanded, setExpanded] = useState(false)
  const [children, setChildren] = useState<BomTreeNode[]>(node.children || [])
  const [documents, setDocuments] = useState<DocumentNode[]>(node.documents || [])
  const [cadDocuments, setCadDocuments] = useState<DocumentNode[]>(node.cadDocuments || [])
  const [loaded, setLoaded] = useState(hasInitialChildren)
  const [loading, setLoading] = useState(false)
  const [noChildren, setNoChildren] = useState(false)

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
        setChildren(resp.children)
        setDocuments(resp.documents)
        setCadDocuments(resp.cadDocuments)
        setLoaded(true)
        setExpanded(true)
        if (resp.children.length === 0) setNoChildren(true)
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
        onClick={toggle}
        className="cursor-pointer select-none hover:bg-indigo-50/60 transition-colors border-b border-slate-200"
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
          </span>
        </td>

        {/* Dynamic columns driven by view config */}
        {viewColumns.map((col, ci) => {
          const val = getCellValue(node, col)
          const isFirst = ci === 0
          return (
            <td
              key={col.key}
              className={`px-2 py-1.5 text-sm whitespace-nowrap ${
                col.align === 'right' ? 'text-right font-mono' : ''
              } ${isFirst ? 'font-mono text-slate-800' : 'text-slate-500'} ${
                col.key === 'name' ? 'max-w-[280px] truncate' : ''
              }`}
            >
              {val}
            </td>
          )
        })}
      </tr>

      {/* Expanded content */}
      {expanded && (
        <>
          {/* Documents */}
          {documents.map((doc, i) => (
            <tr key={`doc-${doc.docId || i}`} className="text-xs border-b border-slate-100">
              <td style={{ paddingLeft: indent + 20 }} className="py-0.5">
                <span className={`inline-block border px-1 rounded text-[10px] font-medium ${subtypeBadgeStyle(doc.subType || 'Dokument')}`}>
                  {doc.subType || 'Doc'}
                </span>
              </td>
              {viewColumns.map((col) => {
                const val = getDocCellValue(doc, col)
                return (
                  <td
                    key={col.key}
                    className={`px-2 py-0.5 whitespace-nowrap ${
                      col.key === 'number' ? 'font-mono text-slate-600' : 'text-slate-400'
                    } ${col.key === 'name' ? 'max-w-[280px] truncate' : ''}`}
                  >
                    {val}
                  </td>
                )
              })}
            </tr>
          ))}

          {/* CAD Documents */}
          {cadDocuments.map((doc, i) => (
            <tr key={`cad-${doc.docId || i}`} className="text-xs border-b border-slate-100">
              <td style={{ paddingLeft: indent + 20 }} className="py-0.5">
                <span className={`inline-block border px-1 rounded text-[10px] font-medium ${subtypeBadgeStyle(doc.subType || 'CAD-Dokument')}`}>
                  {doc.subType || 'CAD'}
                </span>
              </td>
              {viewColumns.map((col) => {
                const val = getDocCellValue(doc, col)
                return (
                  <td
                    key={col.key}
                    className={`px-2 py-0.5 whitespace-nowrap ${
                      col.key === 'number' ? 'font-mono text-slate-600' : 'text-slate-400'
                    } ${col.key === 'name' ? 'max-w-[280px] truncate' : ''}`}
                  >
                    {val}
                  </td>
                )
              })}
            </tr>
          ))}

          {/* Children */}
          {children.map((child, idx) => (
            <BomTreeRow
              key={`${child.partId || child.number}-${idx}`}
              node={child}
              depth={depth + 1}
              viewColumns={viewColumns}
              totalCols={totalCols}
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