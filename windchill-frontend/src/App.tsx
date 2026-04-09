import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import ErrorBoundary from './components/ErrorBoundary'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import DetailPage from './pages/DetailPage'
import CreatePartPage from './pages/CreatePartPage'
import BomExportPage from './pages/BomExportPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen text-gray-500">Laden...</div>
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-slate-500">
      <h1 className="text-2xl font-bold mb-2">404</h1>
      <p className="text-sm">Seite nicht gefunden.</p>
      <a href="/" className="mt-4 text-indigo-600 hover:underline text-sm">← Zur Startseite</a>
    </div>
  )
}

function AppRoutes() {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen text-gray-500">Laden...</div>

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to="/" replace /> : <LoginPage />}
      />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/create/part" element={<CreatePartPage />} />              <Route path="/export/balluff" element={<BomExportPage />} />                <Route path="/detail/:typeKey/:code" element={<DetailPage />} />
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  )
}