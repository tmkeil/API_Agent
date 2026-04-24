import { useEffect, useRef, useState, type ReactNode } from 'react'

export interface RowAction {
  /** Stable key for React list rendering. */
  key: string
  /** Menu label. */
  label: string
  /** Optional hint (shown as muted subtext). */
  description?: string
  /** Called when the item is clicked. The menu closes afterwards. */
  onSelect: () => void
  /** When true, item is rendered but not clickable. */
  disabled?: boolean
  /** Optional leading icon / glyph. */
  icon?: ReactNode
}

interface Props {
  /** Tooltip / aria-label for the trigger button. */
  title?: string
  /** Menu action items. If empty, the button is not rendered. */
  actions: RowAction[]
}

/**
 * Generic row-action menu: a compact "⋯" trigger that opens a dropdown of
 * actions. Designed to be embedded in table rows (e.g. search results). New
 * actions for additional object types can be added by the caller — the menu
 * itself does not know about specific object types.
 */
export default function RowActionsMenu({ title = 'Actions', actions }: Props) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    function onDocClick(ev: MouseEvent) {
      if (ref.current && !ref.current.contains(ev.target as Node)) {
        setOpen(false)
      }
    }
    function onEsc(ev: KeyboardEvent) {
      if (ev.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', onDocClick)
    document.addEventListener('keydown', onEsc)
    return () => {
      document.removeEventListener('mousedown', onDocClick)
      document.removeEventListener('keydown', onEsc)
    }
  }, [open])

  return (
    <div ref={ref} className="relative inline-block" onClick={(e) => e.stopPropagation()}>
      <button
        type="button"
        onClick={(e) => { e.stopPropagation(); setOpen((o) => !o) }}
        title={title}
        aria-label={title}
        aria-haspopup="menu"
        aria-expanded={open}
        className={`w-7 h-7 inline-flex items-center justify-center rounded text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors ${
          open ? 'text-slate-700 bg-slate-100' : ''
        }`}
      >
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <circle cx="4" cy="10" r="1.6" />
          <circle cx="10" cy="10" r="1.6" />
          <circle cx="16" cy="10" r="1.6" />
        </svg>
      </button>
      {open && (
        <div
          role="menu"
          className="absolute left-0 mt-1 z-20 min-w-[220px] bg-white border border-slate-200 rounded shadow-lg py-1 text-sm"
        >
          {actions.length === 0 && (
            <div className="px-3 py-1.5 text-xs text-slate-400 italic">No actions available</div>
          )}
          {actions.map((a) => (
            <button
              key={a.key}
              type="button"
              role="menuitem"
              disabled={a.disabled}
              onClick={() => { if (!a.disabled) { a.onSelect(); setOpen(false) } }}
              className="w-full text-left px-3 py-1.5 flex items-start gap-2 hover:bg-indigo-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {a.icon && <span className="mt-0.5 text-slate-400">{a.icon}</span>}
              <span className="flex-1">
                <span className="block text-slate-700">{a.label}</span>
                {a.description && (
                  <span className="block text-[11px] text-slate-400">{a.description}</span>
                )}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
