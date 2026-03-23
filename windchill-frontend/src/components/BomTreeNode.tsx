import { useCallback, useEffect, useState } from 'react'
import { getBomChildren } from '../api/client'
import type { BomTreeNode, DocumentNode } from '../api/types'

interface Props {
  node: BomTreeNode
  depth: number
}

export default function BomTreeNodeComponent({ node, depth }: Props) {
  const hasInitialChildren = (node.children && node.children.length > 0) || node.childrenLoaded || false
  const [expanded, setExpanded] = useState(depth === 0)
  const [children, setChildren] = useState<BomTreeNode[]>(
    node.children || [],
  )
  const [documents, setDocuments] = useState<DocumentNode[]>(
    node.documents || [],
  )
  const [cadDocuments, setCadDocuments] = useState<DocumentNode[]>(
    node.cadDocuments || [],
  )
  const [loaded, setLoaded] = useState(hasInitialChildren)
  const [loading, setLoading] = useState(false)
  const [noChildren, setNoChildren] = useState(false)

  // Auto-load children for root node so the expanded state matches reality
  const loadChildren = useCallback(async () => {
    if (loaded || loading || !node.hasChildren || !node.partId) return
    setLoading(true)
    try {
      const resp = await getBomChildren(node.partId)
      setChildren(resp.children)
      setDocuments(resp.documents)
      setCadDocuments(resp.cadDocuments)
      setLoaded(true)
      if (resp.children.length === 0) {
        setNoChildren(true)
      }
    } catch {
      // Fetch failed — keep current state
    } finally {
      setLoading(false)
    }
  }, [loaded, loading, node.hasChildren, node.partId])

  // Root node starts expanded → fetch children immediately
  useEffect(() => {
    if (depth === 0 && expanded && !loaded) {
      loadChildren()
    }
  }, [depth, expanded, loaded, loadChildren])

  const toggle = useCallback(async () => {
    if (expanded) {
      setExpanded(false)
      return
    }

    // Prevent double-clicks while loading
    if (loading) return

    // Need to fetch children first?
    if (!loaded) {
      await loadChildren()
    }

    // Expand
    setExpanded(true)
  }, [expanded, loaded, loading, loadChildren])

  return (
    <div style={{ marginLeft: depth > 0 ? 20 : 0 }}>
      {/* Node row */}
      <div
        className="flex items-center gap-2 py-1 group hover:bg-slate-50 rounded cursor-pointer select-none"
        onClick={toggle}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle() } }}
        role="button"
        tabIndex={0}
        aria-expanded={expanded}
        aria-label={`${node.number} ${node.name}`}
      >
        {/* Expand icon */}
        <span className="w-4 text-center text-slate-400 text-[11px] flex-shrink-0">
          {node.hasChildren && !noChildren ? (
            loading ? (
              <span className="animate-spin inline-block">⟳</span>
            ) : expanded ? (
              <svg className="w-3 h-3 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
            ) : (
              <svg className="w-3 h-3 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" /></svg>
            )
          ) : (
            <span className="text-slate-300">·</span>
          )}
        </span>

        {/* Type badge */}
        <span className="text-[10px] bg-slate-200 text-slate-600 px-1 rounded flex-shrink-0 font-medium">
          {node.type === 'WTPart' ? 'Part' : node.type}
        </span>

        {/* Identity: Number, Name, OrgID, Version, State */}
        <span className="text-sm text-slate-800 truncate">
          <span className="font-mono font-medium">{node.number}</span>
          {node.name && <span className="text-slate-500">, {node.name}</span>}
          {node.organizationId && <span className="text-slate-400">, {node.organizationId}</span>}
          <span className="text-slate-400">, {node.version}</span>
          {node.state && <span className="text-slate-500">, {node.state}</span>}
        </span>

        {/* Quantity | Unit */}
        {node.quantity != null && (
          <span className="ml-auto flex items-center gap-1 text-xs flex-shrink-0 font-mono text-slate-400">
            <span className="text-slate-300">|</span>
            <span>{node.quantity}</span>
            {node.quantityUnit && (
              <>
                <span className="text-slate-300">|</span>
                <span>{node.quantityUnit}</span>
              </>
            )}
          </span>
        )}
      </div>

      {/* Expanded content */}
      {expanded && (
        <div>
          {/* Documents */}
          {documents.length > 0 && (
            <div style={{ marginLeft: 20 }} className="mb-1">
              {documents.map((doc, i) => (
                <div
                  key={doc.docId || i}
                  className="flex items-center gap-2 py-0.5 text-xs text-slate-500"
                >
                  <span className="w-4" />
                  <span className="bg-amber-50 text-amber-700 border border-amber-200 px-1 rounded text-[10px] font-medium">
                    Doc
                  </span>
                  <span className="font-mono text-slate-600">{doc.number}</span>
                  <span className="truncate text-slate-400">{doc.name}</span>
                </div>
              ))}
            </div>
          )}

          {/* CAD Documents */}
          {cadDocuments.length > 0 && (
            <div style={{ marginLeft: 20 }} className="mb-1">
              {cadDocuments.map((doc, i) => (
                <div
                  key={doc.docId || i}
                  className="flex items-center gap-2 py-0.5 text-xs text-slate-500"
                >
                  <span className="w-4" />
                  <span className="bg-violet-50 text-violet-700 border border-violet-200 px-1 rounded text-[10px] font-medium">
                    CAD
                  </span>
                  <span className="font-mono text-slate-600">{doc.number}</span>
                  <span className="truncate text-slate-400">{doc.name}</span>
                </div>
              ))}
            </div>
          )}

          {/* Children */}
          {children.map((child, idx) => (
            <BomTreeNodeComponent
              key={`${child.partId || child.number}-${idx}`}
              node={child}
              depth={depth + 1}
            />
          ))}

          {loaded && children.length === 0 && documents.length === 0 && cadDocuments.length === 0 && (
            <div
              style={{ marginLeft: 20 }}
              className="text-xs text-slate-400 italic py-1"
            >
              Keine Unterelemente
            </div>
          )}
        </div>
      )}
    </div>
  )
}