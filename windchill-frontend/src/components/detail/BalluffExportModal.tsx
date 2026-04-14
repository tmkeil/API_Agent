import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { fetchBalluffBomExport, fetchSapExport, fetchSapPreview } from '../../api/client'
import type { BalluffBomExportResponse, SapExportResponse, SapExportRequest, SapPreviewResponse } from '../../api/types'

// ── Types ───────────────────────────────────────────────────

type ExportRow = Record<string, string>

interface TabData {
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

function downloadBlob(content: string, filename: string) {
  const bom = '\uFEFF'
  const blob = new Blob([bom + content], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

// ── Column widths ───────────────────────────────────────────

const NARROW_COLS = new Set([
  'Structure Level', 'LvL', 'MatScr', 'MatDest', 'Plant', 'PTp',
  'DocPart', 'Version', 'Assembly', 'Pos', 'Quantity',
])

function colWidth(col: string): string {
  if (NARROW_COLS.has(col)) return 'w-16'
  if (col === 'Description' || col === 'ERP Position Text' || col === 'PosText') return 'w-64'
  if (col === 'Mat/Doc Number' || col === 'Reference Designator') return 'w-40'
  return 'w-28'
}

// ── Row type colors ─────────────────────────────────────────

function rowBg(row: ExportRow): string {
  if (row['PTp'] === 'L') return 'bg-white'
  if (row['PTp'] === 'D') return 'bg-blue-50/60'
  return 'bg-amber-50/50'
}

// ── Component ───────────────────────────────────────────────

interface Props {
  partNumber: string
  onClose: () => void
}

export default function BalluffExportModal({ partNumber, onClose }: Props) {
  const [activeTab, setActiveTab] = useState<'raw' | 'sap'>('raw')

  // ── Raw data state ────────────────────────────────────
  const [rawLoading, setRawLoading] = useState(true)
  const [rawData, setRawData] = useState<TabData | null>(null)
  const [rawError, setRawError] = useState('')

  // ── SAP Preview state ─────────────────────────────────
  const [sapLoading, setSapLoading] = useState(false)
  const [sapData, setSapData] = useState<TabData | null>(null)
  const [sapValidation, setSapValidation] = useState<string[]>([])
  const [sapPreviewStats, setSapPreviewStats] = useState<{
    totalInputRows: number; totalOutputRows: number; removedRows: number
  } | null>(null)
  const [sapError, setSapError] = useState('')

  // ── SAP Export (final) state ──────────────────────────
  const [exportLoading, setExportLoading] = useState(false)
  const [exportResult, setExportResult] = useState<SapExportResponse | null>(null)
  const [exportError, setExportError] = useState('')

  // ── Edit state ────────────────────────────────────────
  const [editCell, setEditCell] = useState<{ tab: string; row: number; col: string } | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // ── Collapse state (raw tab) ──────────────────────────
  const [collapsed, setCollapsed] = useState<Set<number>>(new Set())

  // ── Load raw data on mount ────────────────────────────
  useEffect(() => {
    const ctrl = new AbortController()
    setRawLoading(true)
    setRawError('')
    fetchBalluffBomExport(partNumber, ctrl.signal)
      .then((resp: BalluffBomExportResponse) => {
        setRawData({
          columns: resp.columns,
          rows: resp.rows.map(r => ({ ...r })),
          partNumber: resp.partNumber,
        })
      })
      .catch(e => {
        if (e.name !== 'AbortError') setRawError(e instanceof Error ? e.message : String(e))
      })
      .finally(() => setRawLoading(false))
    return () => ctrl.abort()
  }, [partNumber])

  // ── SAP Preview trigger ───────────────────────────────
  const triggerSapPreview = useCallback((data: TabData) => {
    const ctrl = new AbortController()
    setSapLoading(true)
    setSapError('')
    setSapData(null)
    setSapValidation([])
    setSapPreviewStats(null)
    setExportResult(null)
    setExportError('')
    fetchSapPreview(
      { columns: data.columns, rows: data.rows, partNumber: data.partNumber },
      ctrl.signal,
    )
      .then((resp: SapPreviewResponse) => {
        setSapData({
          columns: resp.columns,
          rows: resp.rows.map(r => ({ ...r })),
          partNumber: data.partNumber,
        })
        setSapValidation(resp.validation)
        setSapPreviewStats(resp.stats)
      })
      .catch(e => {
        if (e.name !== 'AbortError') setSapError(e instanceof Error ? e.message : String(e))
      })
      .finally(() => setSapLoading(false))
    return ctrl
  }, [])

  // Auto-trigger SAP preview when raw data first loads
  const sapPreviewTriggered = useRef(false)
  useEffect(() => {
    if (!rawData || sapPreviewTriggered.current) return
    sapPreviewTriggered.current = true
    const ctrl = triggerSapPreview(rawData)
    return () => ctrl.abort()
  }, [rawData, triggerSapPreview])

  // ── Collapse logic (raw tab) ──────────────────────────
  const toggleCollapse = useCallback((rowIdx: number) => {
    setCollapsed(prev => {
      const next = new Set(prev)
      if (next.has(rowIdx)) next.delete(rowIdx)
      else next.add(rowIdx)
      return next
    })
  }, [])

  const rowHasChildren = useMemo(() => {
    if (!rawData) return new Set<number>()
    const result = new Set<number>()
    const rows = rawData.rows
    for (let i = 0; i < rows.length - 1; i++) {
      if (rows[i]['PTp'] !== 'L') continue
      const level = parseInt(rows[i]['Structure Level'] || '0', 10)
      const nextLevel = parseInt(rows[i + 1]?.['Structure Level'] || '0', 10)
      if (nextLevel > level) result.add(i)
    }
    return result
  }, [rawData])

  const visibleRows = useMemo(() => {
    if (!rawData) return []
    const rows = rawData.rows
    const visible: number[] = []
    let skipUntilLevel = -1
    for (let i = 0; i < rows.length; i++) {
      const level = parseInt(rows[i]['Structure Level'] || '0', 10)
      if (skipUntilLevel >= 0) {
        if (level > skipUntilLevel) continue
        skipUntilLevel = -1
      }
      visible.push(i)
      if (collapsed.has(i) && rows[i]['PTp'] === 'L') {
        skipUntilLevel = level
      }
    }
    return visible
  }, [rawData, collapsed])

  // ── Edit handlers ─────────────────────────────────────
  const startEdit = useCallback((tab: string, rowIdx: number, col: string) => {
    setEditCell({ tab, row: rowIdx, col })
    setTimeout(() => inputRef.current?.focus(), 0)
  }, [])

  const commitEdit = useCallback((value: string) => {
    if (!editCell) return
    const setter = editCell.tab === 'raw' ? setRawData : setSapData
    setter((prev: TabData | null) => {
      if (!prev) return prev
      const rows = [...prev.rows]
      rows[editCell.row] = { ...rows[editCell.row], [editCell.col]: value }
      return { ...prev, rows }
    })
    setEditCell(null)
  }, [editCell])

  // ── Row operations (raw tab) ──────────────────────────
  const addRowAfter = useCallback((idx: number) => {
    if (!rawData) return
    const empty: ExportRow = {}
    for (const c of rawData.columns) empty[c] = ''
    setRawData((prev: TabData | null) => {
      if (!prev) return prev
      const rows = [...prev.rows]
      rows.splice(idx + 1, 0, empty)
      return { ...prev, rows }
    })
  }, [rawData])

  const removeRow = useCallback((idx: number) => {
    setRawData((prev: TabData | null) => {
      if (!prev) return prev
      const rows = prev.rows.filter((_: ExportRow, i: number) => i !== idx)
      return { ...prev, rows }
    })
  }, [])

  // ── CSV downloads ─────────────────────────────────────
  const handleDownloadRaw = useCallback(() => {
    if (!rawData) return
    const csv = toCsv(rawData.columns, rawData.rows)
    downloadBlob(csv, `BalluffBOM_${rawData.partNumber}_${new Date().toISOString().slice(0, 10)}.csv`)
  }, [rawData])

  const handleDownloadSap = useCallback(() => {
    if (!sapData) return
    const csv = toCsv(sapData.columns, sapData.rows)
    downloadBlob(csv, `SAP_Preview_${sapData.partNumber}_${new Date().toISOString().slice(0, 10)}.csv`)
  }, [sapData])

  // ── SAP Export (final: PartB→C→D) ────────────────────
  const handleSapExport = useCallback(async () => {
    if (!sapData) return
    setExportLoading(true)
    setExportError('')
    setExportResult(null)
    try {
      const body: SapExportRequest = {
        columns: sapData.columns,
        rows: sapData.rows,
        partNumber: sapData.partNumber,
        fromPreview: true,
      }
      const resp = await fetchSapExport(body)
      setExportResult(resp)
    } catch (e: unknown) {
      setExportError(e instanceof Error ? e.message : String(e))
    } finally {
      setExportLoading(false)
    }
  }, [sapData])

  const handleDownloadSapFile = useCallback((idx: number) => {
    if (!exportResult) return
    const file = exportResult.files[idx]
    downloadBlob(file.content, file.filename)
  }, [exportResult])

  const handleDownloadAllSapFiles = useCallback(() => {
    if (!exportResult) return
    for (const file of exportResult.files) {
      downloadBlob(file.content, file.filename)
    }
  }, [exportResult])

  // ── Reload ────────────────────────────────────────────
  const handleReload = useCallback(() => {
    setRawData(null)
    setRawLoading(true)
    setRawError('')
    setSapData(null)
    setSapError('')
    setSapValidation([])
    setSapPreviewStats(null)
    setExportResult(null)
    setExportError('')
    setCollapsed(new Set())
    sapPreviewTriggered.current = false
    fetchBalluffBomExport(partNumber)
      .then((resp: BalluffBomExportResponse) => {
        setRawData({
          columns: resp.columns,
          rows: resp.rows.map(r => ({ ...r })),
          partNumber: resp.partNumber,
        })
      })
      .catch(e => setRawError(e instanceof Error ? e.message : String(e)))
      .finally(() => setRawLoading(false))
  }, [partNumber])

  // ── Recalculate SAP preview ───────────────────────────
  const handleRefreshPreview = useCallback(() => {
    if (!rawData) return
    triggerSapPreview(rawData)
  }, [rawData, triggerSapPreview])

  // ── Close on Escape ───────────────────────────────────
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !editCell) onClose()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose, editCell])

  // ── Shared table renderer ─────────────────────────────
  function renderTable(
    tab: 'raw' | 'sap',
    data: TabData,
    options: {
      visibleRowIndices?: number[]
      showCollapse?: boolean
      showRowOps?: boolean
    } = {},
  ) {
    const {
      visibleRowIndices,
      showCollapse = false,
      showRowOps = false,
    } = options
    const indices = visibleRowIndices ?? data.rows.map((_, i) => i)

    return (
      <div className="border border-slate-200 rounded-lg overflow-auto flex-1">
        <table className="text-xs border-collapse min-w-max">
          <thead className="sticky top-0 z-10">
            <tr className="bg-slate-100">
              <th className="px-1 py-1.5 text-center text-slate-400 font-normal border-b border-slate-200 sticky left-0 bg-slate-100 z-20 w-16">
                #
              </th>
              {data.columns.map(col => (
                <th
                  key={col}
                  className={`px-2 py-1.5 text-left text-slate-600 font-medium border-b border-slate-200 whitespace-nowrap ${colWidth(col)}`}
                  title={col}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {indices.map(ri => {
              const row = data.rows[ri]
              if (!row) return null
              const canCollapse = showCollapse && rowHasChildren.has(ri)
              const isCollapsed = collapsed.has(ri)
              const level = parseInt(row['Structure Level'] || '0', 10)
              return (
                <tr
                  key={ri}
                  className={`${rowBg(row)} hover:bg-yellow-50/50 group border-b border-slate-100`}
                >
                  <td className="px-1 py-0.5 text-center sticky left-0 bg-inherit z-10 border-r border-slate-100">
                    <div className="flex items-center gap-0.5">
                      {canCollapse ? (
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
                      {showRowOps && (
                        <span className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-0.5">
                          <button
                            onClick={() => addRowAfter(ri)}
                            className="text-emerald-500 hover:text-emerald-700 text-[10px] leading-none"
                            title="Zeile darunter einfügen"
                          >+</button>
                          <button
                            onClick={() => removeRow(ri)}
                            className="text-red-400 hover:text-red-600 text-[10px] leading-none"
                            title="Zeile entfernen"
                          >×</button>
                        </span>
                      )}
                    </div>
                  </td>
                  {data.columns.map(col => {
                    const isEditing = editCell?.tab === tab && editCell?.row === ri && editCell?.col === col
                    const val = row[col] ?? ''
                    const indent = col === 'Structure Level' && level > 0
                      ? { paddingLeft: `${level * 8 + 8}px` }
                      : undefined
                    return (
                      <td
                        key={col}
                        className={`px-2 py-0.5 whitespace-nowrap cursor-text ${isEditing ? 'p-0' : ''} ${colWidth(col)}`}
                        style={indent}
                        onDoubleClick={() => startEdit(tab, ri, col)}
                      >
                        {isEditing ? (
                          <input
                            ref={inputRef}
                            defaultValue={val}
                            className="w-full px-1 py-0.5 text-xs border border-indigo-400 rounded outline-none bg-white"
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
              )
            })}
          </tbody>
        </table>
      </div>
    )
  }

  // ── Render ────────────────────────────────────────────
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-xl shadow-2xl border border-slate-200 w-[95vw] h-[90vh] flex flex-col">
        {/* ── Modal Header ── */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-slate-200 shrink-0">
          <div className="flex items-center gap-4">
            <h2 className="text-sm font-semibold text-slate-800">
              Balluff BOM Export — {partNumber}
            </h2>
            {/* Tabs */}
            <div className="flex gap-1 bg-slate-100 rounded-lg p-0.5">
              <button
                onClick={() => setActiveTab('raw')}
                className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                  activeTab === 'raw'
                    ? 'bg-white text-slate-800 shadow-sm'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                Ausgangsdaten
                {rawData && (
                  <span className="ml-1.5 text-slate-400">{rawData.rows.length}</span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('sap')}
                className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                  activeTab === 'sap'
                    ? 'bg-white text-slate-800 shadow-sm'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                SAP Vorschau
                {sapLoading && (
                  <span className="ml-1.5 animate-pulse text-slate-400">…</span>
                )}
                {!sapLoading && sapValidation.length > 0 && (
                  <span className="ml-1.5 text-amber-600 font-normal">⚠ {sapValidation.length}</span>
                )}
                {!sapLoading && sapData && sapValidation.length === 0 && (
                  <span className="ml-1.5 text-emerald-600">✓</span>
                )}
              </button>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 text-lg leading-none px-2"
          >
            ✕
          </button>
        </div>

        {/* ── Tab Content ── */}
        <div className="flex-1 flex flex-col overflow-hidden px-5 py-3">

          {/* ── Ausgangsdaten Tab ── */}
          {activeTab === 'raw' && (
            <>
              {rawLoading && (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-sm text-slate-500 animate-pulse">
                    BOM wird geladen und aufbereitet…
                  </div>
                </div>
              )}
              {rawError && !rawLoading && (
                <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2 rounded-md">
                  {rawError}
                  <button onClick={handleReload} className="ml-3 underline">Erneut versuchen</button>
                </div>
              )}
              {rawData && (
                <>
                  <div className="flex items-center gap-3 mb-2 shrink-0">
                    <span className="text-xs text-slate-500">
                      {rawData.rows.length} Zeilen ·{' '}
                      {rawData.rows.filter(r => r['PTp'] === 'L').length} Parts ·{' '}
                      {rawData.rows.filter(r => r['PTp'] === 'D').length} Docs ·{' '}
                      {rawData.rows.filter(r => r['PTp'] !== 'L' && r['PTp'] !== 'D').length} CAD
                    </span>
                    <button
                      onClick={handleDownloadRaw}
                      className="px-3 py-1 text-xs font-medium rounded bg-emerald-600 text-white hover:bg-emerald-700 transition-colors"
                    >
                      CSV herunterladen
                    </button>
                    <button
                      onClick={handleReload}
                      disabled={rawLoading}
                      className="px-2 py-1 text-xs font-medium rounded border border-slate-300 text-slate-500 hover:bg-slate-100 transition-colors disabled:opacity-40"
                    >
                      ↻ Neu laden
                    </button>
                  </div>
                  {renderTable('raw', rawData, {
                    visibleRowIndices: visibleRows,
                    showCollapse: true,
                    showRowOps: true,
                  })}
                </>
              )}
            </>
          )}

          {/* ── SAP Vorschau Tab ── */}
          {activeTab === 'sap' && (
            <>
              {sapLoading && (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-sm text-slate-500 animate-pulse">
                    SAP-Vorschau wird berechnet (PartA + Validierung)…
                  </div>
                </div>
              )}
              {sapError && !sapLoading && (
                <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2 rounded-md mb-2">
                  {sapError}
                  <button onClick={handleRefreshPreview} className="ml-3 underline">Erneut versuchen</button>
                </div>
              )}
              {sapData && (
                <>
                  {/* Validation */}
                  {sapValidation.length > 0 && (
                    <div className="bg-amber-50 border border-amber-200 rounded-md px-4 py-2 mb-2 shrink-0">
                      <div className="text-xs font-semibold text-amber-800 mb-1">
                        Validierung — {sapValidation.length} Hinweis{sapValidation.length !== 1 ? 'e' : ''}
                      </div>
                      <ul className="text-xs text-amber-700 space-y-0.5 max-h-24 overflow-auto">
                        {sapValidation.map((msg, i) => (
                          <li key={i} className="flex gap-1.5">
                            <span className="text-amber-500 shrink-0">•</span>
                            <span>{msg}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {sapValidation.length === 0 && (
                    <div className="bg-emerald-50 border border-emerald-200 rounded-md px-4 py-1.5 mb-2 text-xs text-emerald-700 shrink-0">
                      ✓ Keine Validierungsfehler gefunden
                    </div>
                  )}

                  {/* Stats + actions */}
                  <div className="flex items-center gap-3 mb-2 shrink-0">
                    <span className="text-xs text-slate-500">
                      {sapData.rows.length} Zeilen
                      {sapPreviewStats && sapPreviewStats.removedRows > 0 && (
                        <> · {sapPreviewStats.removedRows} entfernt (PG-Regel)</>
                      )}
                    </span>
                    <button
                      onClick={handleRefreshPreview}
                      disabled={sapLoading}
                      className="px-2 py-1 text-xs font-medium rounded border border-slate-300 text-slate-500 hover:bg-slate-100 transition-colors disabled:opacity-40"
                    >
                      ↻ Vorschau aktualisieren
                    </button>
                    <button
                      onClick={handleDownloadSap}
                      className="px-3 py-1 text-xs font-medium rounded bg-emerald-600 text-white hover:bg-emerald-700 transition-colors"
                    >
                      CSV herunterladen
                    </button>
                    <button
                      onClick={handleSapExport}
                      disabled={exportLoading}
                      className="px-3 py-1 text-xs font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700 transition-colors disabled:opacity-40"
                    >
                      {exportLoading ? 'SAP Export…' : 'SAP Export'}
                    </button>
                  </div>

                  {/* SAP Export Result */}
                  {exportError && (
                    <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2 rounded-md mb-2 shrink-0">
                      {exportError}
                    </div>
                  )}
                  {exportResult && (
                    <div className="border border-slate-200 rounded-md mb-2 shrink-0">
                      <div className="flex items-center justify-between px-3 py-2 bg-slate-50 border-b border-slate-200">
                        <span className="text-xs font-semibold text-slate-700">
                          SAP CSV-Dateien ({exportResult.files.length})
                        </span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-slate-500">
                            {exportResult.stats.totalOutputRows} SAP-Zeilen · {exportResult.stats.skippedRows} übersprungen
                          </span>
                          {exportResult.files.length > 0 && (
                            <button
                              onClick={handleDownloadAllSapFiles}
                              className="px-2 py-0.5 text-xs font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700"
                            >
                              Alle herunterladen
                            </button>
                          )}
                        </div>
                      </div>
                      {exportResult.validation.length > 0 && (
                        <div className="px-3 py-2 bg-amber-50 border-b border-amber-200">
                          <div className="text-xs font-semibold text-amber-800 mb-1">
                            Validierung nach Bearbeitung — {exportResult.validation.length} Hinweis{exportResult.validation.length !== 1 ? 'e' : ''}
                          </div>
                          <ul className="text-xs text-amber-700 space-y-0.5 max-h-20 overflow-auto">
                            {exportResult.validation.map((msg, i) => (
                              <li key={i}>• {msg}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      <div className="divide-y divide-slate-100 max-h-32 overflow-auto">
                        {exportResult.files.map((file, i) => (
                          <div key={i} className="flex items-center justify-between px-3 py-1.5 hover:bg-slate-50">
                            <span className="text-xs text-slate-700 font-mono">{file.filename}</span>
                            <button
                              onClick={() => handleDownloadSapFile(i)}
                              className="text-xs text-indigo-600 hover:text-indigo-800"
                            >↓</button>
                          </div>
                        ))}
                      </div>
                      {exportResult.files.length === 0 && (
                        <div className="text-xs text-slate-500 py-3 text-center">
                          Keine SAP-Dateien erzeugt (keine Zeilen mit gesetzter Pos).
                        </div>
                      )}
                    </div>
                  )}

                  {renderTable('sap', sapData)}
                </>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
