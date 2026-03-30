import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createObject } from '../api/client'

// Windchill Views (Part-Kontext)
const VIEWS = ['Design', 'Manufacturing'] as const

// Folder-Kontexte (Toplevel)
const FOLDER_LOCATIONS = [
  '/P - Design',
  '/P - Manufacturing',
  '/P - Electronical Components - Design',
  '/P - Electronical Components - Manufacturing',
  '/P - Mechanical Components',
  '/P - Compliance and Conformity',
  '/P - Enclosed Documentation',
] as const

const SOURCES = ['Make', 'Buy'] as const
const UNITS = ['each', 'kg', 'm', 'l', 'piece'] as const

interface FormState {
  Number: string
  Name: string
  View: string
  FolderLocation: string
  Source: string
  DefaultUnit: string
}

const INITIAL: FormState = {
  Number: '',
  Name: '',
  View: 'Design',
  FolderLocation: '/P - Design',
  Source: 'Make',
  DefaultUnit: 'each',
}

export default function CreatePartPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState<FormState>(INITIAL)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const set = useCallback(
    (key: keyof FormState, val: string) =>
      setForm((prev) => ({ ...prev, [key]: val })),
    [],
  )

  // Auto-sync View ↔ FolderLocation
  const setView = useCallback((view: string) => {
    setForm((prev) => ({
      ...prev,
      View: view,
      FolderLocation: view === 'Manufacturing' ? '/P - Manufacturing' : '/P - Design',
    }))
  }, [])

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()
      if (!form.Number.trim() || !form.Name.trim()) return

      setBusy(true)
      setError('')
      setSuccess('')

      // Build attributes — only send non-empty values
      const attrs: Record<string, string> = {}
      for (const [k, v] of Object.entries(form)) {
        const trimmed = v.trim()
        if (trimmed) attrs[k] = trimmed
      }

      try {
        const resp = await createObject('part', attrs)
        setSuccess(resp.message || `Part '${resp.number}' erstellt`)
        // Navigate to detail page after short delay
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

  return (
    <div className="max-w-xl mx-auto">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-lg font-semibold text-slate-800">Neues Part erstellen</h1>
        <button
          onClick={() => navigate(-1)}
          className="text-xs text-slate-400 hover:text-slate-600 transition-colors"
        >
          ← Zurück
        </button>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded shadow-sm border border-slate-200 p-5 space-y-4">
        {/* Number */}
        <Field label="Nummer *" hint="Windchill Part Number">
          <input
            value={form.Number}
            onChange={(e) => set('Number', e.target.value)}
            placeholder="z.B. S2200287364"
            required
            className="input"
          />
        </Field>

        {/* Name */}
        <Field label="Name *" hint="Bezeichnung / Beschreibung">
          <input
            value={form.Name}
            onChange={(e) => set('Name', e.target.value)}
            placeholder="z.B. BES M18ZI-PSC80B-S04G"
            required
            className="input"
          />
        </Field>

        {/* View (Design / Manufacturing) */}
        <Field label="View" hint="Design oder Manufacturing Part?">
          <div className="flex gap-2">
            {VIEWS.map((v) => (
              <button
                key={v}
                type="button"
                onClick={() => setView(v)}
                className={`flex-1 px-3 py-2 text-sm rounded border transition-colors ${
                  form.View === v
                    ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                    : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
                }`}
              >
                {v}
              </button>
            ))}
          </div>
        </Field>

        {/* Folder Location */}
        <Field label="Ablageort" hint="Windchill Folder / Kontext">
          <select
            value={form.FolderLocation}
            onChange={(e) => set('FolderLocation', e.target.value)}
            className="input"
          >
            {FOLDER_LOCATIONS.map((f) => (
              <option key={f} value={f}>{f}</option>
            ))}
          </select>
        </Field>

        {/* Source */}
        <Field label="Source" hint="Make = Eigenproduktion, Buy = Zukauf">
          <div className="flex gap-2">
            {SOURCES.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => set('Source', s)}
                className={`flex-1 px-3 py-2 text-sm rounded border transition-colors ${
                  form.Source === s
                    ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                    : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </Field>

        {/* Default Unit */}
        <Field label="Einheit" hint="Mengeneinheit">
          <select
            value={form.DefaultUnit}
            onChange={(e) => set('DefaultUnit', e.target.value)}
            className="input"
          >
            {UNITS.map((u) => (
              <option key={u} value={u}>{u}</option>
            ))}
          </select>
        </Field>

        {/* Submit */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={busy || !form.Number.trim() || !form.Name.trim()}
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

      {/* Info box */}
      <div className="mt-4 bg-slate-50 border border-slate-200 rounded p-4 text-xs text-slate-500 space-y-1">
        <p><strong>Hinweis:</strong> Windchill vergibt Revision, Version und Lifecycle automatisch anhand des konfigurierten Templates.</p>
        <p>Die <strong>View</strong> bestimmt, ob das Part unter "P - Design" oder "P - Manufacturing" angelegt wird.</p>
        <p>Weitere Attribute können nach dem Erstellen über den Aktionen-Tab bearbeitet werden.</p>
      </div>
    </div>
  )
}

/** Reusable form field wrapper */
function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {label}
        {hint && <span className="ml-2 text-xs font-normal text-slate-400">{hint}</span>}
      </label>
      {children}
    </div>
  )
}
