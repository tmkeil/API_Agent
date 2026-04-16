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

type RuleConfig = Record<string, boolean>

// ── Rule definitions ────────────────────────────────────────

const RULE_DEFS: { key: string; label: string; description: string; defaultValue: boolean }[] = [
  {
    key: 'ApplyPrintingGoodRule',
    label: 'Printing-Good-Regel',
    description: 'Enclosed Documentation mit Printing Good = NO entfernen',
    defaultValue: true,
  },
  {
    key: 'FilterQepDrwDocTypes',
    label: 'QEP/DRW Filter',
    description: 'Zeilen mit DocType QEP oder DRW entfernen',
    defaultValue: false,
  },
]

function defaultRules(): RuleConfig {
  const r: RuleConfig = {}
  for (const d of RULE_DEFS) r[d.key] = d.defaultValue
  return r
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

// ── Collapse helpers ────────────────────────────────────────

function computeRowHasChildren(data: TabData | null): Set<number> {
  if (!data) return new Set()
  const result = new Set<number>()
  const rows = data.rows
  for (let i = 0; i < rows.length - 1; i++) {
    if (rows[i]['PTp'] !== 'L') continue
    const level = parseInt(rows[i]['Structure Level'] || '0', 10)
    const nextLevel = parseInt(rows[i + 1]?.['Structure Level'] || '0', 10)
    if (nextLevel > level) result.add(i)
  }
  return result
}

function computeVisibleRows(data: TabData | null, collapsedSet: Set<number>): number[] {
  if (!data) return []
  const rows = data.rows
  const visible: number[] = []
  let skipUntilLevel = -1
  for (let i = 0; i < rows.length; i++) {
    const level = parseInt(rows[i]['Structure Level'] || '0', 10)
    if (skipUntilLevel >= 0) {
      if (level > skipUntilLevel) continue
      skipUntilLevel = -1
    }
    visible.push(i)
    if (collapsedSet.has(i) && rows[i]['PTp'] === 'L') {
      skipUntilLevel = level
    }
  }
  return visible
}

// ── Component ───────────────────────────────────────────────

interface Props {
  partNumber: string
  onClose: () => void
}

export default function BalluffExportModal({ partNumber, onClose }: Props) {
  const [activeTab, setActiveTab] = useState<'raw' | 'sap' | 'config'>('raw')

  // ── Level picker state ────────────────────────────────
  const [maxDepth, setMaxDepth] = useState<number | null>(null)
  const [depthInput, setDepthInput] = useState('')
  const [bomLoaded, setBomLoaded] = useState(false)

  // ── Rules state ───────────────────────────────────────
  const [rules, setRules] = useState<RuleConfig>(defaultRules)

  // ── Raw data state ────────────────────────────────────
  const [rawLoading, setRawLoading] = useState(false)
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
  const [validationStale, setValidationStale] = useState(false)

  // ── SAP Export (final) state ──────────────────────────
  const [exportLoading, setExportLoading] = useState(false)
  const [exportResult, setExportResult] = useState<SapExportResponse | null>(null)
  const [exportError, setExportError] = useState('')

  // ── Edit state ────────────────────────────────────────
  const [editCell, setEditCell] = useState<{ tab: string; row: number; col: string } | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // ── Collapse state ────────────────────────────────────
  const [rawCollapsed, setRawCollapsed] = useState<Set<number>>(new Set())
  const [sapCollapsed, setSapCollapsed] = useState<Set<number>>(new Set())

  // ── Depth input handler ───────────────────────────────
  const handleDepthInputChange = useCallback((val: string) => {
    setDepthInput(val)
    if (val === '') {
      setMaxDepth(null)
    } else {
      const n = parseInt(val, 10)
      if (!isNaN(n) && n >= 1) setMaxDepth(n)
    }
  }, [])

  // ── Load BOM (triggered by user) ──────────────────────
  const sapPreviewTriggered = useRef(false)

  const loadBom = useCallback((depth: number | null) => {
    const ctrl = new AbortController()
    setRawLoading(true)
    setRawError('')
    setRawData(null)
    setSapData(null)
    setSapError('')
    setSapValidation([])
    setSapPreviewStats(null)
    setExportResult(null)
    setExportError('')
    setRawCollapsed(new Set())
    setSapCollapsed(new Set())
    setValidationStale(false)
    sapPreviewTriggered.current = false
    fetchBalluffBomExport(partNumber, ctrl.signal, depth ?? undefined)
      .then((resp: BalluffBomExportResponse) => {
        setRawData({
          columns: resp.columns,
          rows: resp.rows.map(r => ({ ...r })),
          partNumber: resp.partNumber,
        })
        setBomLoaded(true)
      })
      .catch(e => {
        if (e.name !== 'AbortError') setRawError(e instanceof Error ? e.message : String(e))
      })
      .finally(() => setRawLoading(false))
    return ctrl
  }, [partNumber])

  // ── SAP Preview trigger ───────────────────────────────
  const triggerSapPreview = useCallback((data: TabData, r?: RuleConfig) => {
    const ctrl = new AbortController()
    setSapLoading(true)
    setSapError('')
    setSapData(null)
    setSapValidation([])
    setSapPreviewStats(null)
    setExportResult(null)
    setExportError('')
    setValidationStale(false)
    setSapCollapsed(new Set())
    fetchSapPreview(
      { columns: data.columns, rows: data.rows, partNumber: data.partNumber, rules: r ?? rules },
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
  }, [rules])

  // Auto-trigger SAP preview when raw data first loads
  useEffect(() => {
    if (!rawData || sapPreviewTriggered.current) return
    sapPreviewTriggered.current = true
    const ctrl = triggerSapPreview(rawData)
    return () => ctrl.abort()
  }, [rawData, triggerSapPreview])

  // ── Collapse logic ────────────────────────────────────
  const toggleCollapse = useCallback((tab: 'raw' | 'sap', rowIdx: number) => {
    const setter = tab === 'raw' ? setRawCollapsed : setSapCollapsed
    setter(prev => {
      const next = new Set(prev)
      if (next.has(rowIdx)) next.delete(rowIdx)
      else next.add(rowIdx)
      return next
    })
  }, [])

  const rawHasChildren = useMemo(() => computeRowHasChildren(rawData), [rawData])
  const rawVisibleRows = useMemo(() => computeVisibleRows(rawData, rawCollapsed), [rawData, rawCollapsed])
  const sapHasChildren = useMemo(() => computeRowHasChildren(sapData), [sapData])
  const sapVisibleRows = useMemo(() => computeVisibleRows(sapData, sapCollapsed), [sapData, sapCollapsed])

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
    if (editCell.tab === 'sap') setValidationStale(true)
    setEditCell(null)
  }, [editCell])

  // ── Row operations (both tabs) ────────────────────────
  const addRowAfter = useCallback((tab: 'raw' | 'sap', idx: number) => {
    const data = tab === 'raw' ? rawData : sapData
    if (!data) return
    const empty: ExportRow = {}
    for (const c of data.columns) empty[c] = ''
    const setter = tab === 'raw' ? setRawData : setSapData
    setter((prev: TabData | null) => {
      if (!prev) return prev
      const rows = [...prev.rows]
      rows.splice(idx + 1, 0, empty)
      return { ...prev, rows }
    })
    if (tab === 'sap') setValidationStale(true)
  }, [rawData, sapData])

  const removeRow = useCallback((tab: 'raw' | 'sap', idx: number) => {
    const setter = tab === 'raw' ? setRawData : setSapData
    setter((prev: TabData | null) => {
      if (!prev) return prev
      const rows = prev.rows.filter((_: ExportRow, i: number) => i !== idx)
      return { ...prev, rows }
    })
    if (tab === 'sap') setValidationStale(true)
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
        rules,
      }
      const resp = await fetchSapExport(body)
      setExportResult(resp)
    } catch (e: unknown) {
      setExportError(e instanceof Error ? e.message : String(e))
    } finally {
      setExportLoading(false)
    }
  }, [sapData, rules])

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
    loadBom(maxDepth)
  }, [loadBom, maxDepth])

  // ── Recalculate SAP preview ───────────────────────────
  const handleRefreshPreview = useCallback(() => {
    if (!rawData) return
    triggerSapPreview(rawData)
  }, [rawData, triggerSapPreview])

  // ── Re-validate SAP data after edits ──────────────────
  const handleRevalidate = useCallback(() => {
    if (!sapData) return
    setValidationStale(false)
    const ctrl = new AbortController()
    setSapLoading(true)
    setSapError('')
    setSapValidation([])
    setExportResult(null)
    setExportError('')
    fetchSapPreview(
      { columns: sapData.columns, rows: sapData.rows, partNumber: sapData.partNumber, rules },
      ctrl.signal,
    )
      .then((resp: SapPreviewResponse) => {
        setSapData({
          columns: resp.columns,
          rows: resp.rows.map(r => ({ ...r })),
          partNumber: sapData.partNumber,
        })
        setSapValidation(resp.validation)
        setSapPreviewStats(resp.stats)
      })
      .catch(e => {
        if (e.name !== 'AbortError') setSapError(e instanceof Error ? e.message : String(e))
      })
      .finally(() => setSapLoading(false))
  }, [sapData, rules])

  // ── Close on Escape ───────────────────────────────────
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !editCell) onClose()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose, editCell])

  // ── Can export? ───────────────────────────────────────
  const exportBlocked = sapValidation.length > 0 || validationStale

  // ── Shared table renderer ─────────────────────────────
  function renderTable(
    tab: 'raw' | 'sap',
    data: TabData,
  ) {
    const hasChildren = tab === 'raw' ? rawHasChildren : sapHasChildren
    const visibleRowIndices = tab === 'raw' ? rawVisibleRows : sapVisibleRows
    const collapsedSet = tab === 'raw' ? rawCollapsed : sapCollapsed

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
            {visibleRowIndices.map(ri => {
              const row = data.rows[ri]
              if (!row) return null
              const canCollapse = hasChildren.has(ri)
              const isCollapsed = collapsedSet.has(ri)
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
                          onClick={() => toggleCollapse(tab, ri)}
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
                          onClick={() => addRowAfter(tab, ri)}
                          className="text-emerald-500 hover:text-emerald-700 text-[10px] leading-none"
                          title="Zeile einfügen"
                        >+</button>
                        <button
                          onClick={() => removeRow(tab, ri)}
                          className="text-red-400 hover:text-red-600 text-[10px] leading-none"
                          title="Zeile entfernen"
                        >×</button>
                      </span>
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
                        className={`px-2 py-0.5 whitespace-nowrap ${isEditing ? 'p-0' : 'shadow-[inset_0_1px_3px_rgba(0,0,0,0.08)] bg-white/80 hover:shadow-[inset_0_1px_4px_rgba(0,0,0,0.15)] hover:bg-white cursor-text rounded-sm'} ${colWidth(col)}`}
                        style={indent}
                        onClick={() => !isEditing && startEdit(tab, ri, col)}
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
                {!sapLoading && sapData && sapValidation.length === 0 && !validationStale && (
                  <span className="ml-1.5 text-emerald-600">✓</span>
                )}
                {validationStale && (
                  <span className="ml-1.5 text-orange-500 font-normal">◌</span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('config')}
                className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                  activeTab === 'config'
                    ? 'bg-white text-slate-800 shadow-sm'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                Regeln
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
            !bomLoaded && !rawLoading && !rawError ? (
              <div className="flex-1 flex flex-col items-center justify-center gap-5">
                <div className="flex items-center gap-3">
                  <label className="text-xs text-slate-500">Tiefe:</label>
                  <input
                    type="number"
                    min={1}
                    placeholder="Alle"
                    value={depthInput}
                    onChange={e => handleDepthInputChange(e.target.value)}
                    className="w-20 px-2 py-1.5 text-sm border border-slate-300 rounded-lg text-center focus:border-indigo-400 focus:outline-none"
                  />
                  <button
                    onClick={() => { setMaxDepth(null); setDepthInput('') }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                      maxDepth === null
                        ? 'bg-indigo-600 text-white shadow-sm'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    Alle
                  </button>
                </div>
                <button
                  onClick={() => loadBom(maxDepth)}
                  className="px-6 py-2 text-sm font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 shadow transition-colors"
                >
                  BOM laden
                </button>
              </div>
            ) : rawLoading ? (
              <div className="flex-1 flex flex-col items-center justify-center gap-3">
                <svg className="animate-spin h-8 w-8 text-indigo-500" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span className="text-sm text-slate-600">
                  Lade BOM{maxDepth !== null ? ` (${maxDepth} Ebenen)` : ''}…
                </span>
              </div>
            ) : rawError ? (
                <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2 rounded-md">
                  {rawError}
                  <button onClick={handleReload} className="ml-3 underline">Erneut versuchen</button>
                </div>
              ) : rawData ? (
                <>
                  <div className="flex items-center gap-3 mb-2 shrink-0">
                    <span className="text-xs text-slate-500">
                      {rawData.rows.length} Zeilen · {rawData.rows.filter(r => r['PTp'] === 'L').length} Parts · {rawData.rows.filter(r => r['PTp'] === 'D').length} Docs
                      {maxDepth !== null && <> · Tiefe: {maxDepth}</>}
                    </span>
                    <button onClick={handleDownloadRaw} className="px-3 py-1 text-xs font-medium rounded bg-emerald-600 text-white hover:bg-emerald-700 transition-colors disabled:bg-emerald-300 disabled:text-white/70 disabled:cursor-not-allowed disabled:hover:bg-emerald-300">
                      CSV
                    </button>
                    <button onClick={handleReload} disabled={rawLoading} className="px-2 py-1 text-xs font-medium rounded border border-slate-300 text-slate-500 hover:bg-slate-100 transition-colors disabled:opacity-40 disabled:bg-emerald-300">
                      Neu laden
                    </button>
                    <button
                      onClick={() => { setBomLoaded(false); setRawData(null); setSapData(null); setSapValidation([]); setSapPreviewStats(null); setExportResult(null); setExportError(''); setValidationStale(false); sapPreviewTriggered.current = false }}
                      className="px-2 py-1 text-xs font-medium rounded border border-slate-300 text-slate-500 hover:bg-slate-100 transition-colors"
                    >
                      Tiefe ändern
                    </button>
                  </div>
                  {renderTable('raw', rawData)}
                </>
              ) : null
          )}

          {/* ── SAP Vorschau Tab ── */}
          {activeTab === 'sap' && (
            sapLoading ? (
              <div className="flex-1 flex flex-col items-center justify-center gap-3">
                <svg className="animate-spin h-8 w-8 text-indigo-500" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span className="text-sm text-slate-600">SAP-Vorschau wird berechnet…</span>
              </div>
            ) : sapError ? (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2 rounded-md mb-2">
                {sapError}
                <button onClick={handleRefreshPreview} className="ml-3 underline">Erneut versuchen</button>
              </div>
            ) : sapData ? (
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
                  {sapValidation.length === 0 && !validationStale && (
                    <div className="bg-emerald-50 border border-emerald-200 rounded-md px-4 py-1.5 mb-2 text-xs text-emerald-700 shrink-0">
                      ✓ Keine Validierungsfehler
                    </div>
                  )}
                  {validationStale && (
                    <div className="bg-orange-50 border border-orange-200 rounded-md px-4 py-1.5 mb-2 text-xs text-orange-700 shrink-0">
                      Validierung veraltet — vor Export erneut prüfen
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex items-center gap-3 mb-2 shrink-0">
                    <span className="text-xs text-slate-500">
                      {sapData.rows.length} Zeilen
                      {sapPreviewStats && sapPreviewStats.removedRows > 0 && (
                        <> · {sapPreviewStats.removedRows} entfernt</>
                      )}
                    </span>
                    <button onClick={handleRefreshPreview} disabled={sapLoading} className="px-2 py-1 text-xs font-medium rounded border border-slate-300 text-slate-500 hover:bg-slate-100 transition-colors disabled:opacity-40">
                      Vorschau aktualisieren
                    </button>
                    <button
                      onClick={handleRevalidate}
                      className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
                        validationStale
                          ? 'border border-amber-400 bg-amber-50 text-amber-700 hover:bg-amber-100'
                          : 'border border-slate-300 text-slate-500 hover:bg-slate-100'
                      }`}
                    >
                      Validierung prüfen
                    </button>
                    <button onClick={handleDownloadSap} className="px-3 py-1 text-xs font-medium rounded bg-emerald-600 text-white hover:bg-emerald-700 transition-colors disabled:bg-emerald-300 disabled:text-white/70 disabled:cursor-not-allowed disabled:hover:bg-emerald-300">
                      CSV
                    </button>
                    <button
                      onClick={handleSapExport}
                      disabled={exportLoading || exportBlocked}
                      className={`px-3 py-1 text-xs font-medium rounded transition-colors disabled:opacity-40 ${
                        exportBlocked
                          ? 'bg-slate-400 text-white cursor-not-allowed'
                          : 'bg-indigo-600 text-white hover:bg-indigo-700'
                      }`}
                      title={exportBlocked ? (validationStale ? 'Validierung veraltet' : 'Validierungsfehler beheben') : undefined}
                    >
                      {exportLoading ? 'Export…' : 'SAP Export'}
                    </button>
                    {exportBlocked && (
                      <span className="text-xs text-amber-600">
                        {validationStale ? 'Validierung prüfen' : 'Fehler beheben'}
                      </span>
                    )}
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
                            {exportResult.stats.totalOutputRows} Zeilen · {exportResult.stats.skippedRows} übersprungen
                          </span>
                          {exportResult.files.length > 0 && (
                            <button onClick={handleDownloadAllSapFiles} className="px-2 py-0.5 text-xs font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700">
                              Alle herunterladen
                            </button>
                          )}
                        </div>
                      </div>
                      {exportResult.validation.length > 0 && (
                        <div className="px-3 py-2 bg-amber-50 border-b border-amber-200">
                          <div className="text-xs font-semibold text-amber-800 mb-1">
                            Validierung — {exportResult.validation.length} Hinweis{exportResult.validation.length !== 1 ? 'e' : ''}
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
                            <button onClick={() => handleDownloadSapFile(i)} className="text-xs text-indigo-600 hover:text-indigo-800">↓</button>
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
              ) : !rawData ? (
                <div className="flex-1 flex items-center justify-center text-sm text-slate-400">
                  Zuerst BOM im Tab "Ausgangsdaten" laden
                </div>
              ) : null
          )}

          {/* ── Regeln Tab ── */}
          {activeTab === 'config' && (
            <div className="flex-1 flex flex-col gap-4 max-w-lg mx-auto py-6">
              <h3 className="text-sm font-semibold text-slate-700">Transformationsregeln</h3>
              <p className="text-xs text-slate-400">
                Regeln steuern die SAP-Vorschau-Transformation. Änderungen werden beim nächsten "Vorschau aktualisieren" angewendet.
              </p>
              <div className="space-y-3">
                {RULE_DEFS.map(def => (
                  <label key={def.key} className="flex items-start gap-3 p-3 rounded-lg border border-slate-200 hover:border-slate-300 cursor-pointer transition-colors">
                    <input
                      type="checkbox"
                      checked={rules[def.key] ?? def.defaultValue}
                      onChange={e => setRules(prev => ({ ...prev, [def.key]: e.target.checked }))}
                      className="mt-0.5 h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                    />
                    <div>
                      <div className="text-xs font-medium text-slate-700">{def.label}</div>
                      <div className="text-xs text-slate-400">{def.description}</div>
                    </div>
                  </label>
                ))}
              </div>
              <button
                onClick={() => setRules(defaultRules())}
                className="self-start px-3 py-1 text-xs font-medium rounded border border-slate-300 text-slate-500 hover:bg-slate-100 transition-colors"
              >
                Standardwerte zurücksetzen
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
