import { useAuth } from '../contexts/AuthContext'
import type { ReactNode } from 'react'
import ApiLogPanel from './ApiLogPanel'

export default function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-slate-900 text-white shadow-md">
        <div className="max-w-7xl mx-auto px-6 h-12 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-base font-semibold tracking-tight">Windchill API</span>
            <span className="text-slate-400 text-xs font-normal">Explorer</span>
            {user && (
              <span className="text-[10px] bg-slate-700 text-slate-300 px-2 py-0.5 rounded font-mono">
                {user.system.toUpperCase()}
              </span>
            )}
          </div>
          {user && (
            <div className="flex items-center gap-4 text-sm">
              <span className="text-slate-300 text-xs">{user.username}</span>
              <button
                onClick={logout}
                className="text-slate-400 hover:text-white text-xs transition-colors"
              >
                Abmelden
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-5">
        {children}
        {user && <ApiLogPanel />}
      </main>
    </div>
  )
}