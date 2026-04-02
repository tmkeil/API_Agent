import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createObject, fetchContainers, fetchClassificationNodes, fetchPartSubtypes } from '../api/client'
import type { ClassificationNode, ContainerItem, PartSubtype } from '../api/types'

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

/* ── Form State ───────────────────────────────────────────── */

interface FormState {
  TypeId: string
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
  TypeId: '',
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
  const [subtypes, setSubtypes] = useState<PartSubtype[]>([])
  const [subtypesLoaded, setSubtypesLoaded] = useState(false)
  const [clfNodes, setClfNodes] = useState<ClassificationNode[]>([])
  const [clfNodesLoaded, setClfNodesLoaded] = useState(false)

  useEffect(() => {
    fetchContainers()
      .then((resp) => {
        // Nur Product-Container anzeigen (PDMLinkProduct)
        const products = resp.containers.filter(
          (c) => c.containerType === 'Product' || c.containerType === 'PDMLinkProduct'
        )
        setContainers(products)
        setContainersLoaded(true)
        if (products.length > 0) {
          setForm((prev) => prev.ContainerBinding ? prev : { ...prev, ContainerBinding: products[0].odataBinding })
        }
      })
      .catch(() => { setContainersLoaded(true) })

    fetchPartSubtypes()
      .then((resp) => {
        setSubtypes(resp.subtypes)
        setSubtypesLoaded(true)
        if (resp.subtypes.length > 0) {
          setForm((prev) => prev.TypeId ? prev : { ...prev, TypeId: resp.subtypes[0].odataType })
        }
      })
      .catch(() => { setSubtypesLoaded(true) })

    fetchClassificationNodes()
      .then((resp) => {
        setClfNodes(resp.nodes)
        setClfNodesLoaded(true)
      })
      .catch(() => { setClfNodesLoaded(true) })
  }, [])

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

  const canSubmit = !busy && !!form.Name.trim() && !!form.ContainerBinding && !!form.TypeId

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
              <ContainerPicker
                containers={containers}
                value={form.ContainerBinding}
                onChange={(v) => set('ContainerBinding', v)}
              />
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

          {/* Part Type (Soft Type) */}
          {subtypes.length > 0 ? (
            <Field label="Type" required>
              <select
                value={form.TypeId}
                onChange={(e) => set('TypeId', e.target.value)}
                className="input"
              >
                {subtypes.map((st) => (
                  <option key={st.odataType} value={st.odataType}>{st.name}</option>
                ))}
              </select>
            </Field>
          ) : subtypesLoaded ? (
            <div className="bg-amber-50 border border-amber-200 text-amber-700 text-sm rounded p-3">
              Keine Part-Subtypes gefunden.
            </div>
          ) : (
            <Field label="Type" required>
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
          <Field label="Classification" required>
            <ClassificationPicker
              nodes={clfNodes}
              loaded={clfNodesLoaded}
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

function ClassificationPicker({ nodes, loaded, value, onChange }: {
  nodes: ClassificationNode[]
  loaded: boolean
  value: string
  onChange: (v: string) => void
}) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const wrapperRef = useRef<HTMLDivElement>(null)
  const searchRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!open) return
    const handler = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  useEffect(() => {
    if (open) searchRef.current?.focus()
  }, [open])

  const filtered = useMemo(() => {
    if (!search.trim()) return nodes
    const q = search.toLowerCase()
    return nodes.filter((n) =>
      n.displayName.toLowerCase().includes(q) || n.internalName.toLowerCase().includes(q)
    )
  }, [nodes, search])

  const selectedDisplay = nodes.find((n) => n.internalName === value)?.displayName || value

  const handleSelect = (internalName: string) => {
    onChange(internalName)
    setOpen(false)
    setSearch('')
  }

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation()
    onChange('')
    setSearch('')
  }

  if (!loaded) {
    return (
      <select disabled className="input opacity-50">
        <option>Lade Classifications…</option>
      </select>
    )
  }

  return (
    <div ref={wrapperRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={`input w-full text-left flex items-center justify-between ${
          !value ? 'text-slate-400' : 'text-slate-800'
        }`}
      >
        <span className="truncate">{value ? selectedDisplay : 'Classification wählen…'}</span>
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

      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-slate-200 rounded shadow-lg">
          <div className="p-2 border-b border-slate-100">
            <input
              ref={searchRef}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Suchen…"
              className="w-full text-sm px-2.5 py-1.5 border border-slate-200 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>
          <div className="max-h-64 overflow-y-auto py-1">
            {filtered.length === 0 ? (
              <div className="px-3 py-2 text-sm text-slate-400">Keine Treffer</div>
            ) : (
              filtered.map((node) => {
                const selected = value === node.internalName
                return (
                  <button
                    key={node.internalName}
                    type="button"
                    onClick={() => handleSelect(node.internalName)}
                    className={`w-full text-left px-3 py-1.5 text-sm transition-colors ${
                      selected
                        ? 'bg-indigo-50 text-indigo-700 font-medium'
                        : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {node.displayName}
                    {node.displayName !== node.internalName && (
                      <span className="text-xs text-slate-400 ml-1">({node.internalName})</span>
                    )}
                  </button>
                )
              })
            )}
          </div>
          <div className="px-3 py-1.5 border-t border-slate-100 text-xs text-slate-400">
            {filtered.length} von {nodes.length}
          </div>
        </div>
      )}
    </div>
  )
}

function ContainerPicker({ containers, value, onChange }: {
  containers: ContainerItem[]
  value: string
  onChange: (v: string) => void
}) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const wrapperRef = useRef<HTMLDivElement>(null)
  const searchRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!open) return
    const handler = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  useEffect(() => {
    if (open) searchRef.current?.focus()
  }, [open])

  const filtered = useMemo(() => {
    if (!search.trim()) return containers
    const q = search.toLowerCase()
    return containers.filter((c) =>
      c.name.toLowerCase().includes(q) || c.containerType.toLowerCase().includes(q)
    )
  }, [containers, search])

  const selectedName = containers.find((c) => c.odataBinding === value)?.name || ''

  return (
    <div ref={wrapperRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={`input w-full text-left flex items-center justify-between ${
          !value ? 'text-slate-400' : 'text-slate-800'
        }`}
      >
        <span className="truncate">{selectedName || 'Container wählen…'}</span>
        <svg className={`w-4 h-4 text-slate-400 transition-transform shrink-0 ${open ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-slate-200 rounded shadow-lg">
          <div className="p-2 border-b border-slate-100">
            <input
              ref={searchRef}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Container suchen…"
              className="w-full text-sm px-2.5 py-1.5 border border-slate-200 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>
          <div className="max-h-64 overflow-y-auto py-1">
            {filtered.length === 0 ? (
              <div className="px-3 py-2 text-sm text-slate-400">Keine Treffer</div>
            ) : (
              filtered.map((c) => {
                const selected = value === c.odataBinding
                return (
                  <button
                    key={c.containerId}
                    type="button"
                    onClick={() => { onChange(c.odataBinding); setOpen(false); setSearch('') }}
                    className={`w-full text-left px-3 py-1.5 text-sm transition-colors ${
                      selected
                        ? 'bg-indigo-50 text-indigo-700 font-medium'
                        : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {c.name} <span className="text-xs text-slate-400">({c.containerType})</span>
                  </button>
                )
              })
            )}
          </div>
          <div className="px-3 py-1.5 border-t border-slate-100 text-xs text-slate-400">
            {filtered.length} von {containers.length}
          </div>
        </div>
      )}
    </div>
  )
}
