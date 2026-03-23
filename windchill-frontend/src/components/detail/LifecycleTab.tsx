import { useCallback, useEffect, useState } from 'react'
import { getLifecycleHistory } from '../../api/client'
import type { LifecycleEntry } from '../../api/types'
import { formatDate } from '../../utils/labels'

interface Props {
  typeKey: string
  code: string
}

/** Tab showing lifecycle history (state transitions) of a Windchill object. */
export default function LifecycleTab({ typeKey, code }: Props) {
  const [events, setEvents] = useState<LifecycleEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const resp = await getLifecycleHistory(typeKey, code, signal)
      if (signal?.aborted) return
      setEvents(resp.events)
    } catch (e: unknown) {
      if (signal?.aborted) return
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [typeKey, code])

  useEffect(() => {
    const controller = new AbortController()
    load(controller.signal)
    return () => controller.abort()
  }, [load])

  if (loading) {
    return <p className="text-sm text-slate-500 animate-pulse py-4">Lifecycle-History wird geladen…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={() => load()} className="ml-3 underline">Erneut versuchen</button>
      </div>
    )
  }

  if (events.length === 0) {
    return (
      <p className="text-sm text-slate-400 py-4">
        Keine Lifecycle-Events verfügbar.
      </p>
    )
  }

  return (
    <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
      {/* Timeline visualization */}
      <div className="p-4 space-y-0">
        {events.map((ev, idx) => (
          <div key={idx} className="flex gap-4 relative">
            {/* Timeline line */}
            <div className="flex flex-col items-center">
              <div className={`w-3 h-3 rounded-full border-2 z-10 ${
                idx === events.length - 1
                  ? 'border-indigo-500 bg-indigo-500'
                  : 'border-slate-300 bg-white'
              }`} />
              {idx < events.length - 1 && (
                <div className="w-0.5 h-full bg-slate-200 -mt-px" />
              )}
            </div>

            {/* Event content */}
            <div className="pb-6 -mt-0.5 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                {ev.fromState && (
                  <>
                    <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-500">
                      {ev.fromState}
                    </span>
                    <svg className="w-3 h-3 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </>
                )}
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  idx === events.length - 1
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'bg-slate-100 text-slate-600'
                }`}>
                  {ev.toState}
                </span>
              </div>
              <div className="text-xs text-slate-400 mt-1 flex gap-3">
                {ev.timestamp && <span>{formatDate(ev.timestamp)}</span>}
                {ev.user && <span>{ev.user}</span>}
                {ev.comment && <span className="text-slate-500">{ev.comment}</span>}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
