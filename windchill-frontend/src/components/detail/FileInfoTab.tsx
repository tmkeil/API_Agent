import { useCallback, useEffect, useState } from 'react'
import { getDocumentFiles, getDocumentDownloadUrl } from '../../api/client'
import type { FileInfo } from '../../api/types'
import { formatDate } from '../../utils/labels'

interface Props {
  typeKey: string
  code: string
}

/** Tab showing file/content attachments of a document. */
export default function FileInfoTab({ typeKey, code }: Props) {
  const [files, setFiles] = useState<FileInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const resp = await getDocumentFiles(typeKey, code, signal)
      if (signal?.aborted) return
      setFiles(resp.files)
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

  function formatFileSize(raw: string): string {
    if (!raw) return '—'
    const bytes = parseInt(raw, 10)
    if (isNaN(bytes)) return raw
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const downloadUrl = getDocumentDownloadUrl(typeKey, code)

  if (loading) {
    return <p className="text-sm text-slate-500 animate-pulse py-4">Dateien werden geladen…</p>
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
        {error}
        <button onClick={() => load()} className="ml-3 underline">Erneut versuchen</button>
      </div>
    )
  }

  if (files.length === 0) {
    return (
      <p className="text-sm text-slate-400 py-4">
        Keine Dateien vorhanden.
      </p>
    )
  }

  return (
    <div className="space-y-2">
      {/* Download button */}
      <div className="flex items-center gap-2">
        <a
          href={downloadUrl}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
          download
        >
          ↓ Primärdatei herunterladen
        </a>
      </div>

      <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-slate-500 text-xs border-b border-slate-200">
          <tr>
            <th className="text-left px-3 py-2 font-medium">Dateiname</th>
            <th className="text-left px-3 py-2 font-medium">Größe</th>
            <th className="text-left px-3 py-2 font-medium">Typ</th>
            <th className="text-left px-3 py-2 font-medium">Rolle</th>
            <th className="text-left px-3 py-2 font-medium">Geändert</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {files.map((f) => (
            <tr key={f.fileId || f.fileName} className="hover:bg-slate-50">
              <td className="px-3 py-2 font-mono text-slate-700 whitespace-nowrap">
                {f.fileName || '—'}
              </td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">
                {formatFileSize(f.fileSize)}
              </td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">
                {f.mimeType || '—'}
              </td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">
                {f.role || '—'}
              </td>
              <td className="px-3 py-2 text-slate-500 whitespace-nowrap">
                {formatDate(f.modified)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    </div>
  )
}
