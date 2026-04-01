import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createObject, fetchContainers, fetchPartFormConfig } from '../api/client'
import type { PartFormOption } from '../api/client'
import type { ContainerItem } from '../api/types'

/* ── Fallback-Optionen (falls Config-API nicht erreichbar) ── */

const FB_VIEWS: PartFormOption[] = [
  { value: 'Design', label: 'Design' },
  { value: 'Manufacturing', label: 'Manufacturing' },
]
const FB_SOURCES: PartFormOption[] = [
  { value: 'notapplicable', label: 'Not Applicable' },
  { value: 'make', label: 'Make' },
  { value: 'buy', label: 'Buy' },
]
const FB_ASSEMBLY: PartFormOption[] = [
  { value: 'separable', label: 'Separable' },
  { value: 'inseparable', label: 'Inseparable' },
  { value: 'component', label: 'Component' },
]
const FB_UNITS: PartFormOption[] = [
  { value: 'ea', label: 'each' },
  { value: 'kg', label: 'kilograms' },
  { value: 'm', label: 'meters' },
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
  ContainerBinding: '',
}

export default function CreatePartPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState<FormState>(INITIAL)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Dynamic option lists (from backend)
  const [views, setViews] = useState<PartFormOption[]>(FB_VIEWS)
  const [sources, setSources] = useState<PartFormOption[]>(FB_SOURCES)
  const [assemblyModes, setAssemblyModes] = useState<PartFormOption[]>(FB_ASSEMBLY)
  const [units, setUnits] = useState<PartFormOption[]>(FB_UNITS)
  const [productFamilies, setProductFamilies] = useState<string[]>([])

  const [containers, setContainers] = useState<ContainerItem[]>([])
  const [containersLoaded, setContainersLoaded] = useState(false)
  const [configLoaded, setConfigLoaded] = useState(false)

  // Load form config + containers in parallel
  useEffect(() => {
    fetchPartFormConfig()
      .then((cfg) => {
        if (cfg.views?.length) setViews(cfg.views)
        if (cfg.sources?.length) setSources(cfg.sources)
        if (cfg.assemblyModes?.length) setAssemblyModes(cfg.assemblyModes)
        if (cfg.units?.length) setUnits(cfg.units)
        if (cfg.productFamilies?.length) setProductFamilies(cfg.productFamilies)
        setConfigLoaded(true)
      })
      .catch(() => { setConfigLoaded(true) })

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
  const loading = !containersLoaded || !configLoaded

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

      {loading ? (
        <div className="bg-white rounded shadow-sm border border-slate-200 p-8 text-center text-slate-400 text-sm">
          Lade Formularkonfiguration…
        </div>
      ) : (
      <form onSubmit={handleSubmit} className="bg-white rounded shadow-sm border border-slate-200 p-5 space-y-5">

        {/* ── Identity ─────────────────────────────────────── */}
        <Section title="Identity">

          {/* Container / Product */}
          {containers.length > 0 ? (
            <Field label="Product / Container" required>
              <select
                value={form.ContainerBinding}
                onChange={(e) => set('ContainerBinding', e.target.value)}
                className="input"
              >
                {containers.map((c) => (
                  <option key={c.containerId} value={c.odataBinding}>
                    {c.name} ({c.containerType})
                  </option>
                ))}
              </select>
            </Field>
          ) : (
            <div className="bg-amber-50 border border-amber-200 text-amber-700 text-sm rounded p-3">
              Keine Container gefunden. Bitte Windchill-Verbindung prüfen.
            </div>
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
              options={sources}
              value={form.Source}
              onChange={(v) => set('Source', v)}
            />
          </Field>

          {/* Associated Product Family */}
          {productFamilies.length > 0 && (
            <Field label="Associated Product Family">
              <select
                value={form.ProductFamily}
                onChange={(e) => set('ProductFamily', e.target.value)}
                className="input"
              >
                {productFamilies.map((pf) => (
                  <option key={pf} value={pf}>{pf || '—'}</option>
                ))}
              </select>
            </Field>
          )}

          {/* View */}
          <Field label="View" required>
            <select
              value={form.View}
              onChange={(e) => set('View', e.target.value)}
              className="input"
            >
              {views.map((v) => (
                <option key={v.value} value={v.value}>{v.label}</option>
              ))}
            </select>
          </Field>

          {/* Assembly Mode */}
          <Field label="Assembly Mode" required>
            <ToggleGroup
              options={assemblyModes}
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
              {units.map((u) => (
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
      )}
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
