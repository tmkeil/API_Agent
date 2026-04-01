import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createObject, fetchContainers } from '../api/client'
import type { ContainerItem } from '../api/types'

/* ── Option-Listen (aus Windchill Part-Erstellung) ────────── */

const VIEWS = [
  { value: 'Design', label: 'Design' },
  { value: 'Manufacturing', label: 'Manufacturing' },
  { value: '0002', label: '0002' },
  { value: 'CN01', label: 'CN01' },
  { value: 'MX02', label: 'MX02' },
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
  Location: string
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
  Location: '/Default/Article',
  ProductFamily: 'PIU',
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

  useEffect(() => {
    fetchContainers()
      .then((resp) => {
        setContainers(resp.containers)
        setContainersLoaded(true)
        if (resp.containers.length > 0 && !form.ContainerBinding) {
          setForm((prev) => ({ ...prev, ContainerBinding: resp.containers[0].odataBinding }))
        }
      })
      .catch(() => { setContainersLoaded(true) })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

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
            <div className="flex gap-2">
              {SOURCES.map((s) => (
                <button
                  key={s.value}
                  type="button"
                  onClick={() => set('Source', s.value)}
                  className={`flex-1 px-3 py-2 text-sm rounded border transition-colors ${
                    form.Source === s.value
                      ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                      : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
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
          <Field label="View" required>
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
            <div className="flex gap-2">
              {ASSEMBLY_MODES.map((am) => (
                <button
                  key={am.value}
                  type="button"
                  onClick={() => set('AssemblyMode', am.value)}
                  className={`flex-1 px-3 py-2 text-sm rounded border transition-colors ${
                    form.AssemblyMode === am.value
                      ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                      : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
                  }`}
                >
                  {am.label}
                </button>
              ))}
            </div>
          </Field>

          {/* Gathering Part */}
          <Field label="Gathering Part" required>
            <div className="flex gap-2">
              {[{ value: 'no', label: 'No' }, { value: 'yes', label: 'Yes' }].map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => set('GatheringPart', opt.value)}
                  className={`flex-1 px-3 py-2 text-sm rounded border transition-colors ${
                    form.GatheringPart === opt.value
                      ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                      : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
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

          {/* Location */}
          <Field label="Location" required>
            <input
              value={form.Location}
              onChange={(e) => set('Location', e.target.value)}
              className="input"
            />
          </Field>

          {/* Configurable Module */}
          <Field label="Configurable Module" required>
            <div className="flex gap-2">
              {[{ value: 'no', label: 'No' }, { value: 'yes', label: 'Yes' }].map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => set('ConfigurableModule', opt.value)}
                  className={`flex-1 px-3 py-2 text-sm rounded border transition-colors ${
                    form.ConfigurableModule === opt.value
                      ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                      : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
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
