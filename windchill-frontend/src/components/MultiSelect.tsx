import { useEffect, useRef, useState } from 'react'

interface Option {
  key: string
  label: string
}

interface Props {
  label: string
  options: Option[]
  selected: string[]
  onChange: (selected: string[]) => void
  placeholder?: string
}

/**
 * Multi-select dropdown with checkboxes.
 * Shows a summary of selected items in the trigger button.
 */
export default function MultiSelect({ label, options, selected, onChange, placeholder = 'Alle' }: Props) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  // Close on outside click
  useEffect(() => {
    if (!open) return
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  function toggle(key: string) {
    onChange(
      selected.includes(key)
        ? selected.filter((k) => k !== key)
        : [...selected, key],
    )
  }

  const displayText = selected.length === 0
    ? placeholder
    : selected.length <= 2
      ? selected.map((k) => options.find((o) => o.key === k)?.label ?? k).join(', ')
      : `${selected.length} ausgewählt`

  return (
    <div ref={ref} className="relative">
      <label className="text-xs text-slate-500 mb-1 block">{label}</label>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={`w-full flex items-center justify-between px-2 py-1.5 text-sm border rounded focus:outline-none focus:ring-1 focus:ring-indigo-400 transition-colors ${
          selected.length > 0
            ? 'border-indigo-400 bg-indigo-50 text-indigo-700'
            : 'border-slate-300 bg-white text-slate-500'
        }`}
      >
        <span className="truncate">{displayText}</span>
        <svg className={`w-3.5 h-3.5 ml-1 flex-shrink-0 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-slate-200 rounded shadow-lg max-h-48 overflow-auto">
          {/* Select all / clear */}
          <div className="flex items-center justify-between px-2 py-1 border-b border-slate-100 text-[11px] text-slate-400">
            <button
              type="button"
              onClick={() => onChange(options.map((o) => o.key))}
              className="hover:text-indigo-600"
            >
              Alle
            </button>
            <button
              type="button"
              onClick={() => onChange([])}
              className="hover:text-red-500"
            >
              Keine
            </button>
          </div>
          {options.map((opt) => (
            <label
              key={opt.key}
              className="flex items-center gap-2 px-2 py-1.5 text-sm hover:bg-slate-50 cursor-pointer select-none"
            >
              <input
                type="checkbox"
                checked={selected.includes(opt.key)}
                onChange={() => toggle(opt.key)}
                className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 h-3.5 w-3.5"
              />
              <span className="text-slate-700">{opt.label}</span>
            </label>
          ))}
        </div>
      )}
    </div>
  )
}
