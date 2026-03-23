import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getObjectVersions } from '../../api/client'
import type { VersionEntry } from '../../api/types'
import { formatDate } from '../../utils/labels'

interface Props {
  typeKey: string
  code: string
}

/** Tab showing all versions/iterations of a Windchill object. */
export default function VersionsTab({ typeKey, code }: Props) {
  const [versions, setVersions] = useState<VersionEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const resp = await getObjectVersions(typeKey, code, signal)
      if (signal?.aborted) return
      setVersions(resp.versions)
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
    return <p className="text-sm text-slate-500 animate-pulse py-4">Versionsverlauf wird geladen…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={() => load()} className="ml-3 underline">Erneut versuchen</button>
      </div>
    )
  }

  if (versions.length === 0) {
    return (
      <p className="text-sm text-slate-400 py-4">
        Kein Versionsverlauf verfügbar.
      </p>
    )
  }

  return (
    <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200">
          <tr>
            <th className="text-left px-3 py-2 font-medium">Version</th>
            <th className="text-left px-3 py-2 font-medium">Iteration</th>
            <th className="text-left px-3 py-2 font-medium">Status</th>
            <th className="text-left px-3 py-2 font-medium">Name</th>
            <th className="text-left px-3 py-2 font-medium">Geändert</th>
            <th className="text-left px-3 py-2 font-medium">Erstellt</th>
            <th className="text-left px-3 py-2 font-medium w-16"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {versions.map((v) => (
            <tr
              key={v.objectId || `${v.version}.${v.iteration}`}
              className={`hover:bg-slate-50 ${v.isCurrent ? 'bg-indigo-50/50' : ''}`}
            >
              <td className="px-3 py-2 font-mono text-slate-700 whitespace-nowrap">
                {v.version}
              </td>
              <td className="px-3 py-2 font-mono text-slate-700 whitespace-nowrap">
                {v.iteration}
              </td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">
                {v.state || '—'}
              </td>
              <td className="px-3 py-2 text-slate-600 max-w-[250px] truncate">
                {v.name}
              </td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">
                {formatDate(v.lastModified)}
              </td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">
                {formatDate(v.createdOn)}
              </td>
              <td className="px-3 py-2 whitespace-nowrap">
                {v.isCurrent && (
                  <span className="inline-block px-1.5 py-0.5 rounded text-[10px] font-medium bg-indigo-100 text-indigo-700">
                    Aktuell
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
