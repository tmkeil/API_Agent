import { useEffect, useRef, useState } from 'react'
import { clearApiLogs, getApiLogs } from '../api/client'
import type { ApiLogEntry } from '../api/types'

export default function ApiLogPanel() {
  const [logs, setLogs] = useState<ApiLogEntry[]>([])
  const [open, setOpen] = useState(false)
  const logRef = useRef<HTMLDivElement>(null)

  // Poll API logs every 2.5s when the panel is open
  useEffect(() => {
    if (!open) return
    let cancelled = false
    const poll = async () => {
      try {
        const items = await getApiLogs(120)
        if (!cancelled) setLogs(items)
      } catch {
        /* ignore */
      }
    }
    poll()
    const id = setInterval(poll, 2500)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [open])

  return (
    <section className="border-t border-slate-200 pt-4 mt-4">
      <div className="flex items-center gap-3">
        <button
          onClick={() => setOpen((o) => !o)}
          className="text-xs text-slate-400 hover:text-slate-600 font-medium transition-colors"
        >
          {open ? '▾' : '▸'} API Log ({logs.length})
        </button>
        {open && logs.length > 0 && (
          <button
            onClick={() => { setLogs([]); clearApiLogs().catch(() => {}) }}
            className="text-[10px] text-slate-400 hover:text-red-500 transition-colors"
          >
            ✕ Clear
          </button>
        )}
      </div>
      {open && (
        <div
          ref={logRef}
          className="mt-2 bg-slate-900 text-green-400 text-[11px] font-mono rounded p-3 overflow-y-auto"
          style={{ height: '240px' }}
        >
          {logs.length === 0 && (
            <p className="text-slate-500">Keine API-Aufrufe protokolliert.</p>
          )}
          {logs.map((entry, i) => {
            const ts = entry.timestamp?.substring(11, 23) || ''
            const src = (entry.source || '').toUpperCase().padEnd(10)
            const method = (entry.method || '').padEnd(5)
            const status = entry.status || 0
            const ms = entry.durationMs ?? 0
            const color =
              entry.source === 'cache'
                ? 'text-yellow-400'
                : status >= 400
                  ? 'text-red-400'
                  : 'text-green-400'
            return (
              <div key={i} className={color}>
                [{ts}] [{src}] {method} {status} {ms}ms {entry.url}
                {entry.note ? ` — ${entry.note}` : ''}
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}
