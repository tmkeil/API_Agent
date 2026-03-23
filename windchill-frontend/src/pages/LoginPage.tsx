import { useEffect, useState, type FormEvent } from 'react'
import { getSystems } from '../api/client'
import type { SystemInfo } from '../api/types'
import { useAuth } from '../contexts/AuthContext'

// Hardcoded fallback so the dropdown always works, even when the API is unreachable.
const FALLBACK_SYSTEMS: SystemInfo[] = [
  { key: 'dev',  label: 'DEV — Entwicklung',  url: 'https://plm-dev.neuhausen.balluff.net/Windchill' },
  { key: 'test', label: 'TEST — Test',         url: 'https://plm-test.neuhausen.balluff.net/Windchill' },
  { key: 'prod', label: 'PROD — Produktion',  url: 'https://plm-prod.neuhausen.balluff.net/Windchill' },
]

export default function LoginPage() {
  const { login, error } = useAuth()
  const [systems, setSystems] = useState<SystemInfo[]>(FALLBACK_SYSTEMS)
  const [system, setSystem] = useState('dev')         // DEV pre-selected
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    // Enrich labels from API if available; fall back silently
    getSystems()
      .then((s) => {
        if (s.length > 0) {
          setSystems(s)
          const hasdev = s.find((x) => x.key === 'dev')
          setSystem(hasdev ? 'dev' : s[0].key)
        }
      })
      .catch(() => { /* keep FALLBACK_SYSTEMS */ })
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await login(system, username, password)
    } catch {
      // error is set in context
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <form
        onSubmit={handleSubmit}
        className="bg-white shadow-lg rounded-lg p-8 w-full max-w-sm border border-slate-200"
      >
        <h1 className="text-lg font-semibold text-center text-slate-800 mb-6">
          Windchill API
        </h1>

        {error && (
          <div className="bg-red-50 text-red-700 text-sm rounded p-2 mb-4">
            {error}
          </div>
        )}

        <label htmlFor="wc-system" className="block text-sm font-medium text-slate-700 mb-1">
          Windchill-Umgebung
        </label>
        <select
          id="wc-system"
          value={system}
          onChange={(e) => setSystem(e.target.value)}
          className="w-full border border-slate-300 rounded px-3 py-2 mb-4 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          {systems.map((s) => (
            <option key={s.key} value={s.key}>
              {s.label}
            </option>
          ))}
        </select>

        <label htmlFor="wc-user" className="block text-sm font-medium text-slate-700 mb-1">Benutzer</label>
        <input
          id="wc-user"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full border border-slate-300 rounded px-3 py-2 mb-4 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          autoComplete="username"
          autoFocus
          required
        />

        <label htmlFor="wc-password" className="block text-sm font-medium text-slate-700 mb-1">Passwort</label>
        <input
          id="wc-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full border border-slate-300 rounded px-3 py-2 mb-6 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          autoComplete="current-password"
          required
        />

        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-indigo-600 text-white font-medium py-2 rounded hover:bg-indigo-700 disabled:opacity-40 text-sm transition-colors"
        >
          {submitting ? 'Verbinde...' : 'Anmelden'}
        </button>
      </form>
    </div>
  )
}