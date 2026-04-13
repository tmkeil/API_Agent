import { useCallback, useMemo, useRef, useState } from 'react'
import { fetchBalluffBomExport, fetchSapExport } from '../../api/client'
import type { BalluffBomExportResponse, SapExportResponse, SapExportRequest } from '../../api/types'

// ── State ───────────────────────────────────────────────────

type ExportRow = Record<string, string>

interface ExportState {
  columns: string[]
  rows: ExportRow[]
  partNumber: string
}

// ── CSV helper ──────────────────────────────────────────────

function escCsv(v: string): string {
  if (v.includes(';') || v.includes('"') || v.includes('\n')) {
    return `"${v.replace(/"/g, '""')}"`
  }
  return v
}

function toCsv(columns: string[], rows: ExportRow[]): string {
  const header = columns.map(escCsv).join(';')
  const lines = rows.map(r => columns.map(c => escCsv(r[c] ?? '')).join(';'))
  return [header, ...lines].join('\r\n')
}

function downloadCsv(csv: string, filename: string) {
  const bom = '\uFEFF'
  const blob = new Blob([bom + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

// ── Column widths (compact) ─────────────────────────────────

const NARROW_COLS = new Set([
  'Structure Level', 'LvL', 'MatScr', 'MatDest', 'Plant', 'PTp',
  'DocPart', 'Version', 'Assembly', 'Pos', 'Quantity',
])

function colWidth(col: string): string {
  if (NARROW_COLS.has(col)) return 'w-16'
  if (col === 'Description' || col === 'ERP Position Text') return 'w-64'
  if (col === 'Mat/Doc Number' || col === 'Reference Designator') return 'w-40'
  return 'w-28'
}

// ── Row type colors ─────────────────────────────────────────

function rowBg(row: ExportRow): string {
  if (row['PTp'] === 'L') return 'bg-white'
  if (row['PTp'] === 'D') return 'bg-blue-50/60'
  return 'bg-amber-50/50'     // CAD Drawings (empty PTp)
}

// ── Component ───────────────────────────────────────────────

interface Props {
  partNumber: string
  onClose: () => void
}

export default function BalluffExportTable({ partNumber, onClose }: Props) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState<ExportState | null>(null)
  const [editCell, setEditCell] = useState<{ row: number; col: string } | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // ── Collapse state ──────────────────────────────────────
  // Set of row indices that are collapsed (their children are hidden)
  const [collapsed, setCollapsed] = useState<Set<number>>(new Set())

  const toggleCollapse = useCallback((rowIdx: number) => {
    setCollapsed(prev => {
      const next = new Set(prev)
      if (next.has(rowIdx)) next.delete(rowIdx)
      else next.add(rowIdx)
      return next
    })
  }, [])

  // Compute visible rows based on collapse state
  const visibleRows = useMemo(() => {
    if (!data) return []
    const rows = data.rows
    const visible: number[] = []
    let skipUntilLevel = -1

    for (let i = 0; i < rows.length; i++) {
      const level = parseInt(rows[i]['Structure Level'] || '0', 10)

      // If we're skipping (a parent is collapsed), check if we've exited the subtree
      if (skipUntilLevel >= 0) {
        if (level > skipUntilLevel) continue  // still inside collapsed subtree
        skipUntilLevel = -1  // exited subtree
      }

      visible.push(i)

      // If this row is collapsed and is a Part with children, skip its subtree
      if (collapsed.has(i) && rows[i]['PTp'] === 'L' && rows[i]['Assembly'] === 'Yes') {
        skipUntilLevel = level
      }
    }
    return visible
  }, [data, collapsed])

  // ── Load ────────────────────────────────────────────────

  const handleLoad = useCallback(async () => {
    setLoading(true)
    setError('')
    setData(null)
    setCollapsed(new Set())
    try {
      const resp: BalluffBomExportResponse = await fetchBalluffBomExport(partNumber)
      setData({
        columns: resp.columns,
        rows: resp.rows.map(r => ({ ...r })),
        partNumber: resp.partNumber,
      })
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }, [partNumber])

  // ── Edit cell ───────────────────────────────────────────

  const startEdit = useCallback((rowIdx: number, col: string) => {
    setEditCell({ row: rowIdx, col })
    setTimeout(() => inputRef.current?.focus(), 0)
  }, [])

  const commitEdit = useCallback((value: string) => {
    if (!editCell || !data) return
    setData((prev: ExportState | null) => {
      if (!prev) return prev
      const rows = [...prev.rows]
      rows[editCell.row] = { ...rows[editCell.row], [editCell.col]: value }
      return { ...prev, rows }
    })
    setEditCell(null)
  }, [editCell, data])

  // ── Row operations ──────────────────────────────────────

  const addRowAfter = useCallback((idx: number) => {
    if (!data) return
    const empty: ExportRow = {}
    for (const c of data.columns) empty[c] = ''
    setData((prev: ExportState | null) => {
      if (!prev) return prev
      const rows = [...prev.rows]
      rows.splice(idx + 1, 0, empty)
      return { ...prev, rows }
    })
  }, [data])

  const removeRow = useCallback((idx: number) => {
    if (!data) return
    setData((prev: ExportState | null) => {
      if (!prev) return prev
      const rows = prev.rows.filter((_: ExportRow, i: number) => i !== idx)
      return { ...prev, rows }
    })
  }, [data])

  // ── CSV export ──────────────────────────────────────────

  const handleDownload = useCallback(() => {
    if (!data) return
    const csv = toCsv(data.columns, data.rows)
    const filename = `BalluffBOM_${data.partNumber}_${new Date().toISOString().slice(0, 10)}.csv`
    downloadCsv(csv, filename)
  }, [data])

  // ── SAP Export ──────────────────────────────────────────

  const [sapLoading, setSapLoading] = useState(false)
  const [sapResult, setSapResult] = useState<SapExportResponse | null>(null)
  const [sapError, setSapError] = useState('')
  const [showSapDialog, setShowSapDialog] = useState(false)

  const handleSapExport = useCallback(async () => {
    if (!data) return
    setSapLoading(true)
    setSapError('')
    setSapResult(null)
    setShowSapDialog(true)
    try {
      const body: SapExportRequest = {
        columns: data.columns,
        rows: data.rows,
        partNumber: data.partNumber,
      }
      const resp = await fetchSapExport(body)
      setSapResult(resp)
    } catch (e: unknown) {
      setSapError(e instanceof Error ? e.message : String(e))
    } finally {
      setSapLoading(false)
    }
  }, [data])

  const handleSapDownloadAll = useCallback(() => {
    if (!sapResult || sapResult.files.length === 0) return
    const bom = '\uFEFF'
    for (const file of sapResult.files) {
      const blob = new Blob([bom + file.content], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.filename
      a.click()
      URL.revokeObjectURL(url)
    }
  }, [sapResult])

  const handleSapDownloadSingle = useCallback((idx: number) => {
    if (!sapResult) return
    const file = sapResult.files[idx]
    const bom = '\uFEFF'
    const blob = new Blob([bom + file.content], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = file.filename
    a.click()
    URL.revokeObjectURL(url)
  }, [sapResult])

  // ── Initial state: show load button ─────────────────────

  if (!data && !loading && !error) {
    return (
      <div className="border-t border-slate-200 mt-3 pt-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h3 className="text-sm font-semibold text-slate-700">Balluff BOM Export</h3>
            <button
              onClick={handleLoad}
              className="px-3 py-1 text-xs font-medium rounded bg-emerald-600 text-white hover:bg-emerald-700 transition-colors"
            >
              Export laden
            </button>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 text-xs"
          >
            Schließen ✕
          </button>
        </div>
      </div>
    )
  }

  // ── Render ──────────────────────────────────────────────

  return (
    <div className="border-t border-slate-200 mt-3 pt-3 space-y-2">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-semibold text-slate-700">Balluff BOM Export</h3>
          {data && (
            <>
              <span className="text-xs text-slate-500">{data.rows.length} Zeilen · {data.rows.filter(r => r['PTp'] === 'L').length} Parts · {data.rows.filter(r => r['PTp'] === 'D').length} Docs · {data.rows.filter(r => r['PTp'] !== 'L' && r['PTp'] !== 'D').length} CAD</span>
              <button
                onClick={handleDownload}
                className="px-3 py-1 text-xs font-medium rounded bg-emerald-600 text-white hover:bg-emerald-700 transition-colors"
              >
                CSV herunterladen
              </button>
              <button
                onClick={handleSapExport}
                disabled={sapLoading}
                className="px-3 py-1 text-xs font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700 transition-colors disabled:opacity-40"
              >
                {sapLoading ? 'SAP Export…' : 'SAP Export'}
              </button>
              <button
                onClick={handleLoad}
                disabled={loading}
                className="px-2 py-1 text-xs font-medium rounded border border-slate-300 text-slate-500 hover:bg-slate-100 transition-colors disabled:opacity-40"
              >
                ↻ Neu laden
              </button>
            </>
          )}
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-600 text-xs"
        >
          Schließen ✕
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2 rounded-md">
          {error}
          <button onClick={handleLoad} className="ml-3 underline">Erneut versuchen</button>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-sm text-slate-500 animate-pulse py-4">
          BOM wird geladen und aufbereitet…
        </div>
      )}

      {/* Table */}
      {data && (
        <div className="border border-slate-200 rounded-lg overflow-auto max-h-[50vh]">
          <table className="text-xs border-collapse min-w-max">
            <thead className="sticky top-0 z-10">
              <tr className="bg-slate-100">
                <th className="px-1 py-1.5 text-center text-slate-400 font-normal border-b border-slate-200 sticky left-0 bg-slate-100 z-20 w-16">
                  #
                </th>
                {data.columns.map(col => (
                  <th
                    key={col}
                    className={`px-2 py-1.5 text-left text-slate-600 font-medium border-b border-slate-200
                                whitespace-nowrap ${colWidth(col)}`}
                    title={col}
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {visibleRows.map(ri => {
                const row = data.rows[ri]
                const isAssembly = row['PTp'] === 'L' && row['Assembly'] === 'Yes'
                const isCollapsed = collapsed.has(ri)
                const level = parseInt(row['Structure Level'] || '0', 10)
                return (
                <tr
                  key={ri}
                  className={`${rowBg(row)} hover:bg-yellow-50/50 group border-b border-slate-100`}
                >
                  {/* Row controls */}
                  <td className="px-1 py-0.5 text-center sticky left-0 bg-inherit z-10 border-r border-slate-100">
                    <div className="flex items-center gap-0.5">
                      {isAssembly ? (
                        <button
                          onClick={() => toggleCollapse(ri)}
                          className="text-slate-500 hover:text-slate-700 text-[10px] leading-none w-3"
                          title={isCollapsed ? 'Aufklappen' : 'Zuklappen'}
                        >
                          {isCollapsed ? '▸' : '▾'}
                        </button>
                      ) : (
                        <span className="w-3" />
                      )}
                      <span className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-0.5">
                        <button
                          onClick={() => addRowAfter(ri)}
                          className="text-emerald-500 hover:text-emerald-700 text-[10px] leading-none"
                          title="Zeile darunter einfügen"
                        >
                          +
                        </button>
                        <button
                          onClick={() => removeRow(ri)}
                          className="text-red-400 hover:text-red-600 text-[10px] leading-none"
                          title="Zeile entfernen"
                        >
                          ×
                        </button>
                      </span>
                    </div>
                  </td>
                  {data.columns.map(col => {
                    const isEditing = editCell?.row === ri && editCell?.col === col
                    const val = row[col] ?? ''
                    // Indent the first data column by structure level
                    const indent = col === 'Structure Level' && level > 0
                      ? { paddingLeft: `${level * 8 + 8}px` }
                      : undefined
                    return (
                      <td
                        key={col}
                        className={`px-2 py-0.5 whitespace-nowrap cursor-text
                                    ${isEditing ? 'p-0' : ''} ${colWidth(col)}`}
                        style={indent}
                        onDoubleClick={() => startEdit(ri, col)}
                      >
                        {isEditing ? (
                          <input
                            ref={inputRef}
                            defaultValue={val}
                            className="w-full px-1 py-0.5 text-xs border border-indigo-400 rounded
                                      outline-none bg-white"
                            onBlur={e => commitEdit(e.target.value)}
                            onKeyDown={e => {
                              if (e.key === 'Enter') commitEdit((e.target as HTMLInputElement).value)
                              if (e.key === 'Escape') setEditCell(null)
                            }}
                          />
                        ) : (
                          <span className={val ? 'text-slate-700' : 'text-slate-300'}>
                            {val || '–'}
                          </span>
                        )}
                      </td>
                    )
                  })}
                </tr>
              )})}
            </tbody>
          </table>
        </div>
      )}

      {/* ── SAP Export Dialog ── */}
      {showSapDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
          <div className="bg-white rounded-lg shadow-xl border border-slate-200 w-[600px] max-h-[80vh] flex flex-col">
            {/* Dialog header */}
            <div className="flex items-center justify-between px-5 py-3 border-b border-slate-200">
              <h3 className="text-sm font-semibold text-slate-800">SAP Export</h3>
              <button
                onClick={() => setShowSapDialog(false)}
                className="text-slate-400 hover:text-slate-600 text-sm"
              >
                ✕
              </button>
            </div>

            {/* Dialog body */}
            <div className="flex-1 overflow-auto px-5 py-4 space-y-4">
              {sapLoading && (
                <div className="text-sm text-slate-500 animate-pulse py-8 text-center">
                  Daten werden für SAP aufbereitet…
                </div>
              )}

              {sapError && (
                <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2 rounded-md">
                  {sapError}
                </div>
              )}

              {sapResult && (
                <>
                  {/* Stats */}
                  <div className="text-xs text-slate-500 flex gap-4">
                    <span>Input: {sapResult.stats.totalInputRows} Zeilen</span>
                    <span>Output: {sapResult.stats.totalOutputRows} SAP-Zeilen</span>
                    <span>Dateien: {sapResult.stats.filesCount}</span>
                    <span>Übersprungen: {sapResult.stats.skippedRows}</span>
                  </div>

                  {/* Validation */}
                  {sapResult.validation.length > 0 && (
                    <div className="bg-amber-50 border border-amber-200 rounded-md px-4 py-3">
                      <div className="text-xs font-semibold text-amber-800 mb-2">
                        Validierung — {sapResult.validation.length} Hinweis{sapResult.validation.length !== 1 ? 'e' : ''}
                      </div>
                      <ul className="text-xs text-amber-700 space-y-1 max-h-40 overflow-auto">
                        {sapResult.validation.map((msg, i) => (
                          <li key={i} className="flex gap-1.5">
                            <span className="text-amber-500 shrink-0">•</span>
                            <span>{msg}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {sapResult.validation.length === 0 && (
                    <div className="bg-emerald-50 border border-emerald-200 rounded-md px-4 py-2 text-xs text-emerald-700">
                      Keine Validierungsfehler gefunden.
                    </div>
                  )}

                  {/* Files list */}
                  {sapResult.files.length > 0 && (
                    <div>
                      <div className="text-xs font-semibold text-slate-700 mb-2">
                        CSV-Dateien ({sapResult.files.length})
                      </div>
                      <div className="border border-slate-200 rounded-md divide-y divide-slate-100 max-h-48 overflow-auto">
                        {sapResult.files.map((file, i) => (
                          <div key={i} className="flex items-center justify-between px-3 py-1.5 hover:bg-slate-50">
                            <span className="text-xs text-slate-700 font-mono">{file.filename}</span>
                            <button
                              onClick={() => handleSapDownloadSingle(i)}
                              className="text-xs text-indigo-600 hover:text-indigo-800"
                            >
                              ↓
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {sapResult.files.length === 0 && !sapError && (
                    <div className="text-xs text-slate-500 py-4 text-center">
                      Keine SAP-Dateien erzeugt (keine Zeilen mit gesetzter Pos).
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Dialog footer */}
            {sapResult && sapResult.files.length > 0 && (
              <div className="flex justify-end gap-2 px-5 py-3 border-t border-slate-200">
                <button
                  onClick={() => setShowSapDialog(false)}
                  className="px-3 py-1.5 text-xs font-medium rounded border border-slate-300 text-slate-600 hover:bg-slate-100"
                >
                  Schließen
                </button>
                <button
                  onClick={handleSapDownloadAll}
                  className="px-4 py-1.5 text-xs font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700"
                >
                  Alle {sapResult.files.length} CSVs herunterladen
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
