import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createObject, fetchContainers } from '../api/client'
import type { ContainerItem } from '../api/types'

const SOURCES = ['Make', 'Buy'] as const
const UNITS = ['each', 'kg', 'm', 'l', 'piece'] as const

interface FormState {
  Number: string
  Name: string
  Source: string
  DefaultUnit: string
  ContainerBinding: string
}

const INITIAL: FormState = {
  Number: '',
  Name: '',
  Source: 'Make',
  DefaultUnit: 'each',
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
      if (!form.Number.trim() || !form.Name.trim()) return

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
        <Field label="Nummer *">
          <input
            value={form.Number}
            onChange={(e) => set('Number', e.target.value)}
            placeholder="z.B. S2200287364"
            required
            className="input"
          />
        </Field>

        {/* Name */}
        <Field label="Name *">
          <input
            value={form.Name}
            onChange={(e) => set('Name', e.target.value)}
            placeholder="z.B. BES M18ZI-PSC80B-S04G"
            required
            className="input"
          />
        </Field>

        {/* Container */}
        {containers.length > 0 ? (
          <Field label="Container">
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
          <Field label="Container">
            <input
              value={form.ContainerBinding}
              onChange={(e) => set('ContainerBinding', e.target.value)}
              placeholder="z.B. Containers('OR:wt.pdmlink.PDMLinkProduct:12345')"
              className="input"
            />
          </Field>
        ) : (
          <Field label="Container">
            <select disabled className="input opacity-50">
              <option>Lade…</option>
            </select>
          </Field>
        )}

        {/* Source */}
        <Field label="Source">
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
        <Field label="Einheit">
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
    </div>
  )
}

/** Reusable form field wrapper */
function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {label}
      </label>
      {children}
    </div>
  )
}
