import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createObject, fetchContainers } from '../api/client'
import type { ContainerItem } from '../api/types'

/* ── Windchill-Systemkonstanten (aus Part-Erstellformular) ── */

const VIEWS = [
  { value: 'Design', label: 'Design' },
  { value: 'Manufacturing', label: 'Manufacturing' },
]

const SOURCES = [
  { value: 'notapplicable', label: 'Not Applicable' },
  { value: 'make', label: 'Make' },
  { value: 'buy', label: 'Buy' },
]

const ASSEMBLY_MODES = [
  { value: 'separable', label: 'Separable' },
  { value: 'inseparable', label: 'Inseparable' },
  { value: 'component', label: 'Component' },
]

const UNITS = [
  { value: 'ea', label: 'each' },
  { value: 'as_needed', label: 'as needed' },
  { value: 'kg', label: 'kilograms' },
  { value: 'm', label: 'meters' },
  { value: 'l', label: 'liters' },
  { value: 'sq_m', label: 'square meters' },
  { value: 'cu_m', label: 'cubic meters' },
  { value: 'g', label: 'gram' },
  { value: 'mm', label: 'millimeter' },
  { value: 'fraction', label: 'partial each' },
  { value: 'ml', label: 'milliliter' },
  { value: 'KAN', label: 'can' },
  { value: 'FLA', label: 'bottle' },
  { value: 'mg', label: 'milligram' },
  { value: 'sq_mm', label: 'square millimeter' },
  { value: 'cm', label: 'centimeters' },
  { value: 'km', label: 'kilometer' },
  { value: 'sq_cm', label: 'square centimeters' },
  { value: 'FT', label: 'feed' },
  { value: 'IN', label: 'inch' },
]

const PRODUCT_FAMILIES = [
  '', 'BAE', 'BAI', 'BAM', 'BAV', 'BAW', 'BCC', 'BCM', 'BCS', 'BCW',
  'BDG', 'BEN', 'BES', 'BFB', 'BFD', 'BFF', 'BFO', 'BFS', 'BFT',
  'BGL', 'BHS', 'BIC', 'BID', 'BIL', 'BIP', 'BIR', 'BIS', 'BIU', 'BIW',
  'BKT', 'BLA', 'BLG', 'BLT', 'BMD', 'BMF', 'BML', 'BMP', 'BNI', 'BNL',
  'BNN', 'BNP', 'BNS', 'BOD', 'BOH', 'BOL', 'BOS', 'BOW', 'BPI',
  'BSE', 'BSG', 'BSI', 'BSP', 'BSS', 'BSW', 'BTL', 'BTM', 'BTS',
  'BUS', 'BVS', 'BWL', 'EQU', 'FHW', 'PIU', 'PLP', 'SET',
]

/* ── Classification Tree (Windchill Part Classification) ─── */

interface ClassificationEntry {
  name: string
  depth: number
  isGroup: boolean
}

const CLASSIFICATIONS: ClassificationEntry[] = [
  { name: 'Component', depth: 0, isGroup: true },
  { name: 'Label', depth: 1, isGroup: false },
  { name: 'TBD', depth: 1, isGroup: false },
  { name: 'Accessory', depth: 1, isGroup: true },
  { name: 'Nut Kit', depth: 2, isGroup: false },
  { name: 'Auxiliary and operating materials', depth: 1, isGroup: true },
  { name: 'Adhesive', depth: 2, isGroup: false },
  { name: 'Adhesive strip', depth: 2, isGroup: false },
  { name: 'Potting Material', depth: 2, isGroup: false },
  { name: 'Tin Solder', depth: 2, isGroup: false },
  { name: 'ECAD Electrical Component', depth: 1, isGroup: true },
  { name: 'ECAD Undefined', depth: 2, isGroup: false },
  { name: 'Pseudo Components', depth: 2, isGroup: false },
  { name: 'Circuit Protection', depth: 2, isGroup: true },
  { name: 'Fuses', depth: 3, isGroup: false },
  { name: 'Inrush Current Limiters', depth: 3, isGroup: false },
  { name: 'Power Controllers', depth: 3, isGroup: false },
  { name: 'Resettable Fuses', depth: 3, isGroup: false },
  { name: 'Reverse Polarity Protection', depth: 3, isGroup: false },
  { name: 'TVS Diodes', depth: 3, isGroup: false },
  { name: 'Varistors', depth: 3, isGroup: false },
  { name: 'Connectors', depth: 2, isGroup: true },
  { name: 'Audio_Video Connectors', depth: 3, isGroup: false },
  { name: 'Card Edge Connectors', depth: 3, isGroup: false },
  { name: 'Circular Connectors', depth: 3, isGroup: false },
  { name: 'D-Sub', depth: 3, isGroup: false },
  { name: 'FFC_FPC Connectors', depth: 3, isGroup: false },
  { name: 'Modular_Ethernet Connectors', depth: 3, isGroup: false },
  { name: 'Pin Headers', depth: 3, isGroup: false },
  { name: 'Power Connectors', depth: 3, isGroup: false },
  { name: 'RF_Coaxial Connectors', depth: 3, isGroup: false },
  { name: 'Ribbon Connectors', depth: 3, isGroup: false },
  { name: 'Terminal Blocks', depth: 3, isGroup: false },
  { name: 'Terminals', depth: 3, isGroup: false },
  { name: 'USB Connectors', depth: 3, isGroup: false },
  { name: 'Discrete Semiconductors', depth: 2, isGroup: true },
  { name: 'Diodes', depth: 3, isGroup: true },
  { name: 'Current Limiting_Regulator', depth: 4, isGroup: false },
  { name: 'General Diodes', depth: 4, isGroup: false },
  { name: 'Zener', depth: 4, isGroup: false },
  { name: 'Thyristors', depth: 3, isGroup: true },
  { name: 'DIACs & SIDACs', depth: 4, isGroup: false },
  { name: 'SCRs', depth: 4, isGroup: false },
  { name: 'Transistors', depth: 3, isGroup: true },
  { name: 'Bipolar', depth: 4, isGroup: false },
  { name: 'IGBTs', depth: 4, isGroup: false },
  { name: 'JFETs', depth: 4, isGroup: false },
  { name: 'MOSFETs', depth: 4, isGroup: false },
  { name: 'ECAD Electromechanical', depth: 2, isGroup: true },
  { name: 'Antennas', depth: 3, isGroup: false },
  { name: 'Electromagnetic Interfaces', depth: 3, isGroup: false },
  { name: 'Encoders', depth: 3, isGroup: false },
  { name: 'Heatsink', depth: 3, isGroup: false },
  { name: 'IC & Component Sockets', depth: 3, isGroup: false },
  { name: 'Relays', depth: 3, isGroup: false },
  { name: 'Shielding', depth: 3, isGroup: false },
  { name: 'Spacers', depth: 3, isGroup: false },
  { name: 'Speakers', depth: 3, isGroup: false },
  { name: 'Wire Management', depth: 3, isGroup: false },
  { name: 'Switches', depth: 3, isGroup: true },
  { name: 'DIP', depth: 4, isGroup: false },
  { name: 'Jumper', depth: 4, isGroup: false },
  { name: 'Rocker', depth: 4, isGroup: false },
  { name: 'Rotary', depth: 4, isGroup: false },
  { name: 'Slide', depth: 4, isGroup: false },
  { name: 'Snap Action', depth: 4, isGroup: false },
  { name: 'Tactile', depth: 4, isGroup: false },
  { name: 'Integrated Circuits (ICs)', depth: 2, isGroup: true },
  { name: 'Analog Switches & Multiplexers', depth: 3, isGroup: false },
  { name: 'ASICs', depth: 3, isGroup: false },
  { name: 'Audio_Video ICs', depth: 3, isGroup: false },
  { name: 'Clock & Timing', depth: 3, isGroup: false },
  { name: 'Codemeter', depth: 3, isGroup: false },
  { name: 'Solid State Relays', depth: 3, isGroup: false },
  { name: 'Data Converter ICs', depth: 3, isGroup: true },
  { name: 'Analog to Digital', depth: 4, isGroup: false },
  { name: 'Digital Potentiometers', depth: 4, isGroup: false },
  { name: 'Digital to Analog', depth: 4, isGroup: false },
  { name: 'Time to Digital', depth: 4, isGroup: false },
  { name: 'Embedded Processors & Controllers', depth: 3, isGroup: true },
  { name: 'CPLDs', depth: 4, isGroup: false },
  { name: 'Digital Signal Controllers & Processors', depth: 4, isGroup: false },
  { name: 'FPGAs', depth: 4, isGroup: false },
  { name: 'Microcontrollers', depth: 4, isGroup: false },
  { name: 'Microprocessors', depth: 4, isGroup: false },
  { name: 'Programmable System On a Chip', depth: 4, isGroup: false },
  { name: 'System On a Modul', depth: 4, isGroup: false },
  { name: 'Interface ICs', depth: 3, isGroup: true },
  { name: 'Anybus', depth: 4, isGroup: false },
  { name: 'CAN Bus', depth: 4, isGroup: false },
  { name: 'CC-Link', depth: 4, isGroup: false },
  { name: 'CLIQ', depth: 4, isGroup: false },
  { name: 'Current Limiters', depth: 4, isGroup: false },
  { name: 'Digital Isolators', depth: 4, isGroup: false },
  { name: 'Ethernet', depth: 4, isGroup: false },
  { name: 'IEEE-1394', depth: 4, isGroup: false },
  { name: 'Interbus', depth: 4, isGroup: false },
  { name: 'IO-Expander', depth: 4, isGroup: false },
  { name: 'IO-Link', depth: 4, isGroup: false },
  { name: 'LIN Bus', depth: 4, isGroup: false },
  { name: 'LVDS', depth: 4, isGroup: false },
]

/* ── Form State ───────────────────────────────────────────── */

interface FormState {
  Number: string
  Name: string
  Description: string
  View: string
  Source: string
  DefaultUnit: string
  AssemblyMode: string
  GatheringPart: string
  ConfigurableModule: string
  ProductFamily: string
  Classification: string
  ContainerBinding: string
}

const INITIAL: FormState = {
  Number: '',
  Name: '',
  Description: '',
  View: 'Design',
  Source: 'notapplicable',
  DefaultUnit: 'ea',
  AssemblyMode: 'separable',
  GatheringPart: 'no',
  ConfigurableModule: 'no',
  ProductFamily: 'PIU',
  Classification: '',
  ContainerBinding: '',
}

export default function CreatePartPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState<FormState>(INITIAL)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [containers, setContainers] = useState<ContainerItem[]>([])
  const [containersLoaded, setContainersLoaded] = useState(false)
  const [containerSearch, setContainerSearch] = useState('')

  useEffect(() => {
    fetchContainers()
      .then((resp) => {
        setContainers(resp.containers)
        setContainersLoaded(true)
        if (resp.containers.length > 0) {
          setForm((prev) => prev.ContainerBinding ? prev : { ...prev, ContainerBinding: resp.containers[0].odataBinding })
        }
      })
      .catch(() => { setContainersLoaded(true) })
  }, [])

  // Container-Liste filtern (Suchfeld)
  const filteredContainers = useMemo(() => {
    if (!containerSearch.trim()) return containers
    const q = containerSearch.toLowerCase()
    return containers.filter((c) =>
      c.name.toLowerCase().includes(q) || c.containerType.toLowerCase().includes(q)
    )
  }, [containers, containerSearch])

  const set = useCallback(
    (key: keyof FormState, val: string) =>
      setForm((prev) => ({ ...prev, [key]: val })),
    [],
  )

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()
      if (!form.Name.trim() || !form.ContainerBinding) return

      setBusy(true)
      setError('')
      setSuccess('')

      const attrs: Record<string, string> = {}
      for (const [k, v] of Object.entries(form)) {
        if (k === 'ContainerBinding') continue
        const trimmed = v.trim()
        if (trimmed) attrs[k] = trimmed
      }
      if (form.ContainerBinding) {
        attrs['Context@odata.bind'] = form.ContainerBinding
      }

      try {
        const resp = await createObject('part', attrs)
        setSuccess(resp.message || `Part '${resp.number}' erstellt`)
        setTimeout(() => {
          navigate(`/detail/part/${encodeURIComponent(resp.number)}`)
        }, 1200)
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err))
      } finally {
        setBusy(false)
      }
    },
    [form, navigate],
  )

  const canSubmit = !busy && !!form.Name.trim() && !!form.ContainerBinding

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-lg font-semibold text-slate-800">Neues Part erstellen</h1>
        <button
          onClick={() => navigate(-1)}
          className="text-xs text-slate-400 hover:text-slate-600 transition-colors"
        >
          ← Zurück
        </button>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded shadow-sm border border-slate-200 p-5 space-y-5">

        {/* ── Identity ─────────────────────────────────────── */}
        <Section title="Identity">

          {/* Container / Product */}
          {containers.length > 0 ? (
            <Field label="Product / Container" required>
              {containers.length > 20 && (
                <input
                  type="text"
                  value={containerSearch}
                  onChange={(e) => setContainerSearch(e.target.value)}
                  placeholder="Container suchen…"
                  className="input mb-1 text-xs"
                />
              )}
              <select
                value={form.ContainerBinding}
                onChange={(e) => set('ContainerBinding', e.target.value)}
                className="input"
              >
                {filteredContainers.map((c) => (
                  <option key={c.containerId} value={c.odataBinding}>
                    {c.name} ({c.containerType})
                  </option>
                ))}
              </select>
              {containers.length > 20 && (
                <span className="text-xs text-slate-400">{filteredContainers.length} von {containers.length}</span>
              )}
            </Field>
          ) : containersLoaded ? (
            <div className="bg-amber-50 border border-amber-200 text-amber-700 text-sm rounded p-3">
              Keine Container gefunden. Bitte Windchill-Verbindung prüfen.
            </div>
          ) : (
            <Field label="Product / Container" required>
              <select disabled className="input opacity-50">
                <option>Lade…</option>
              </select>
            </Field>
          )}

          {/* Number */}
          <Field label="Number">
            <input
              value={form.Number}
              onChange={(e) => set('Number', e.target.value)}
              placeholder="(Generated)"
              className="input"
            />
          </Field>

          {/* Name */}
          <Field label="Name" required>
            <input
              value={form.Name}
              onChange={(e) => set('Name', e.target.value)}
              className="input"
            />
          </Field>

          {/* Description */}
          <Field label="Description">
            <textarea
              value={form.Description}
              onChange={(e) => set('Description', e.target.value)}
              rows={2}
              className="input resize-y"
            />
          </Field>

          {/* Source */}
          <Field label="Source" required>
            <ToggleGroup
              options={SOURCES}
              value={form.Source}
              onChange={(v) => set('Source', v)}
            />
          </Field>

          {/* Associated Product Family */}
          <Field label="Associated Product Family">
            <select
              value={form.ProductFamily}
              onChange={(e) => set('ProductFamily', e.target.value)}
              className="input"
            >
              {PRODUCT_FAMILIES.map((pf) => (
                <option key={pf} value={pf}>{pf || '—'}</option>
              ))}
            </select>
          </Field>

          {/* View */}
          <Field label="View">
            <select
              value={form.View}
              onChange={(e) => set('View', e.target.value)}
              className="input"
            >
              {VIEWS.map((v) => (
                <option key={v.value} value={v.value}>{v.label}</option>
              ))}
            </select>
          </Field>

          {/* Assembly Mode */}
          <Field label="Assembly Mode" required>
            <ToggleGroup
              options={ASSEMBLY_MODES}
              value={form.AssemblyMode}
              onChange={(v) => set('AssemblyMode', v)}
            />
          </Field>

          {/* Gathering Part */}
          <Field label="Gathering Part" required>
            <ToggleGroup
              options={[{ value: 'no', label: 'No' }, { value: 'yes', label: 'Yes' }]}
              value={form.GatheringPart}
              onChange={(v) => set('GatheringPart', v)}
            />
          </Field>

          {/* Default Unit */}
          <Field label="Default Unit" required>
            <select
              value={form.DefaultUnit}
              onChange={(e) => set('DefaultUnit', e.target.value)}
              className="input"
            >
              {UNITS.map((u) => (
                <option key={u.value} value={u.value}>{u.label}</option>
              ))}
            </select>
          </Field>

          {/* Configurable Module */}
          <Field label="Configurable Module" required>
            <ToggleGroup
              options={[{ value: 'no', label: 'No' }, { value: 'yes', label: 'Yes' }]}
              value={form.ConfigurableModule}
              onChange={(v) => set('ConfigurableModule', v)}
            />
          </Field>

          {/* Classification */}
          <Field label="Classification">
            <ClassificationPicker
              value={form.Classification}
              onChange={(v) => set('Classification', v)}
            />
          </Field>
        </Section>

        {/* ── Submit ───────────────────────────────────────── */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={!canSubmit}
            className="w-full px-4 py-2.5 text-sm font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            {busy ? 'Wird erstellt…' : 'Part erstellen'}
          </button>
        </div>

        {/* Feedback */}
        {success && (
          <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm rounded p-3">
            {success}
          </div>
        )}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
            {error}
          </div>
        )}
      </form>
    </div>
  )
}

/* ── Helper Components ────────────────────────────────────── */

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <fieldset className="space-y-4">
      <legend className="text-sm font-semibold text-slate-500 uppercase tracking-wide border-b border-slate-200 pb-1 w-full">
        {title}
      </legend>
      {children}
    </fieldset>
  )
}

function Field({ label, required, children }: { label: string; required?: boolean; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {label}{required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      {children}
    </div>
  )
}

function ToggleGroup({ options, value, onChange }: {
  options: { value: string; label: string }[]
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div className="flex gap-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={`flex-1 px-3 py-2 text-sm rounded border transition-colors ${
            value === opt.value
              ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
              : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}

function ClassificationPicker({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const wrapperRef = useRef<HTMLDivElement>(null)
  const searchRef = useRef<HTMLInputElement>(null)

  // Close on outside click
  useEffect(() => {
    if (!open) return
    const handler = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  // Focus search when opened
  useEffect(() => {
    if (open) searchRef.current?.focus()
  }, [open])

  const lowerSearch = search.toLowerCase()

  // When searching: show matching leaves + their ancestor groups for context
  const filtered = useMemo(() => {
    if (!lowerSearch) return CLASSIFICATIONS

    // Find leaves that match the search
    const matchingIndices = new Set<number>()
    CLASSIFICATIONS.forEach((entry, i) => {
      if (!entry.isGroup && entry.name.toLowerCase().includes(lowerSearch)) {
        matchingIndices.add(i)
        // Include ancestor groups: walk backwards to find parents at each shallower depth
        let currentDepth = entry.depth
        for (let j = i - 1; j >= 0; j--) {
          if (CLASSIFICATIONS[j].depth < currentDepth && CLASSIFICATIONS[j].isGroup) {
            matchingIndices.add(j)
            currentDepth = CLASSIFICATIONS[j].depth
            if (currentDepth === 0) break
          }
        }
      }
    })

    return CLASSIFICATIONS.filter((_, i) => matchingIndices.has(i))
  }, [lowerSearch])

  const handleSelect = (name: string) => {
    onChange(name)
    setOpen(false)
    setSearch('')
  }

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation()
    onChange('')
    setSearch('')
  }

  return (
    <div ref={wrapperRef} className="relative">
      {/* Trigger button */}
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={`input w-full text-left flex items-center justify-between ${
          !value ? 'text-slate-400' : 'text-slate-800'
        }`}
      >
        <span className="truncate">{value || 'Classification wählen…'}</span>
        <span className="flex items-center gap-1 ml-2 shrink-0">
          {value && (
            <span
              onClick={handleClear}
              className="text-slate-400 hover:text-red-500 cursor-pointer text-base leading-none"
              title="Zurücksetzen"
            >×</span>
          )}
          <svg className={`w-4 h-4 text-slate-400 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </span>
      </button>

      {/* Dropdown panel */}
      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-slate-200 rounded shadow-lg">
          {/* Search */}
          <div className="p-2 border-b border-slate-100">
            <input
              ref={searchRef}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Suchen…"
              className="w-full text-sm px-2.5 py-1.5 border border-slate-200 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>

          {/* Tree list */}
          <div className="max-h-64 overflow-y-auto py-1">
            {filtered.length === 0 ? (
              <div className="px-3 py-2 text-sm text-slate-400">Keine Treffer</div>
            ) : (
              filtered.map((entry) => {
                if (entry.isGroup) {
                  return (
                    <div
                      key={`g-${entry.name}`}
                      className="px-3 py-1 text-xs font-semibold text-slate-400 uppercase tracking-wide select-none"
                      style={{ paddingLeft: `${12 + entry.depth * 16}px` }}
                    >
                      {entry.name}
                    </div>
                  )
                }
                const selected = value === entry.name
                return (
                  <button
                    key={entry.name}
                    type="button"
                    onClick={() => handleSelect(entry.name)}
                    className={`w-full text-left px-3 py-1.5 text-sm transition-colors ${
                      selected
                        ? 'bg-indigo-50 text-indigo-700 font-medium'
                        : 'text-slate-700 hover:bg-slate-50'
                    }`}
                    style={{ paddingLeft: `${12 + entry.depth * 16}px` }}
                  >
                    {entry.name}
                  </button>
                )
              })
            )}
          </div>
        </div>
      )}
    </div>
  )
}
