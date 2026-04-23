import { useAuth } from '../contexts/AuthContext'
import type { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import ApiLogPanel from './ApiLogPanel'

export default function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

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
              <button
                onClick={() => navigate('/')}
                className="px-2.5 py-1 text-xs font-medium rounded text-slate-300 hover:text-white transition-colors"
              >
                Search
              </button>
              <button
                onClick={() => navigate('/?mode=cn')}
                className="px-2.5 py-1 text-xs font-medium rounded text-slate-300 hover:text-white transition-colors"
              >
                Change Notices
              </button>
              <button
                onClick={() => navigate('/create/part')}
                className="px-2.5 py-1 text-xs font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
              >
                + New Part
              </button>
              <span className="text-slate-300 text-xs">{user.username}</span>
              <button
                onClick={logout}
                className="text-slate-400 hover:text-white text-xs transition-colors"
              >
                Sign out
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