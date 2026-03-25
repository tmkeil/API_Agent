import { useCallback, useState } from 'react'
import { getBomChildren } from '../api/client'
import type { BomTreeNode, DocumentNode } from '../api/types'

interface Props {
  node: BomTreeNode
  depth: number
}

/**
 * BOM tree node rendered as <tr> rows inside a parent <table>.
 * Returns a React Fragment containing one or more <tr> elements.
 * Children are lazily loaded on first expand click.
 */
export default function BomTreeRow({ node, depth }: Props) {
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
        {/* Expand icon + indentation */}
        <td className="px-1 py-1.5 whitespace-nowrap" style={{ paddingLeft: indent }}>
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
              <span className="text-slate-300">·</span>
            )}
          </span>
        </td>

        {/* Nummer */}
        <td className="px-2 py-1.5 font-mono text-sm text-slate-800 whitespace-nowrap">
          {node.number}
        </td>

        {/* Name */}
        <td className="px-2 py-1.5 text-sm text-slate-600 max-w-[280px] truncate">
          {node.name}
        </td>

        {/* Version */}
        <td className="px-2 py-1.5 text-sm text-slate-500 whitespace-nowrap">
          {node.version}
        </td>

        {/* Status */}
        <td className="px-2 py-1.5 text-sm text-slate-500 whitespace-nowrap">
          {node.state}
        </td>

        {/* Menge */}
        <td className="px-2 py-1.5 text-sm text-slate-500 font-mono whitespace-nowrap text-right">
          {node.quantity != null ? node.quantity : ''}
        </td>

        {/* Einheit */}
        <td className="px-2 py-1.5 text-sm text-slate-500 whitespace-nowrap">
          {node.quantityUnit || ''}
        </td>
      </tr>

      {/* Expanded content */}
      {expanded && (
        <>
          {/* Documents */}
          {documents.map((doc, i) => (
            <tr key={`doc-${doc.docId || i}`} className="text-xs border-b border-slate-100">
              <td style={{ paddingLeft: indent + 20 }} className="py-0.5" />
              <td className="px-2 py-0.5 whitespace-nowrap">
                <span className="inline-block bg-amber-50 text-amber-700 border border-amber-200 px-1 rounded text-[10px] font-medium mr-1">
                  Doc
                </span>
                <span className="font-mono text-slate-600">{doc.number}</span>
              </td>
              <td className="px-2 py-0.5 text-slate-400 truncate">{doc.name}</td>
              <td className="px-2 py-0.5 text-slate-400">{doc.version}</td>
              <td className="px-2 py-0.5 text-slate-400">{doc.state}</td>
              <td colSpan={2} />
            </tr>
          ))}

          {/* CAD Documents */}
          {cadDocuments.map((doc, i) => (
            <tr key={`cad-${doc.docId || i}`} className="text-xs border-b border-slate-100">
              <td style={{ paddingLeft: indent + 20 }} className="py-0.5" />
              <td className="px-2 py-0.5 whitespace-nowrap">
                <span className="inline-block bg-violet-50 text-violet-700 border border-violet-200 px-1 rounded text-[10px] font-medium mr-1">
                  CAD
                </span>
                <span className="font-mono text-slate-600">{doc.number}</span>
              </td>
              <td className="px-2 py-0.5 text-slate-400 truncate">{doc.name}</td>
              <td className="px-2 py-0.5 text-slate-400">{doc.version}</td>
              <td className="px-2 py-0.5 text-slate-400">{doc.state}</td>
              <td colSpan={2} />
            </tr>
          ))}

          {/* Children */}
          {children.map((child, idx) => (
            <BomTreeRow
              key={`${child.partId || child.number}-${idx}`}
              node={child}
              depth={depth + 1}
            />
          ))}

          {/* Empty state */}
          {loaded && children.length === 0 && documents.length === 0 && cadDocuments.length === 0 && (
            <tr>
              <td
                colSpan={7}
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