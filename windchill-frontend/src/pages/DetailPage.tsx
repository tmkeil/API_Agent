import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getAffectedItems, getObjectDetail, getResultingItems } from '../api/client'
import type { ObjectDetail } from '../api/types'
import DetailHeader from '../components/detail/DetailHeader'
import DetailsTab from '../components/detail/DetailsTab'
import StructureTab from '../components/detail/StructureTab'
import DocumentsTab from '../components/detail/DocumentsTab'
import CadTab from '../components/detail/CadTab'
import WhereUsedTab from '../components/detail/WhereUsedTab'
import ChangeItemsTab from '../components/detail/ChangeItemsTab'
import ReferencingPartsTab from '../components/detail/ReferencingPartsTab'
import FileInfoTab from '../components/detail/FileInfoTab'
import VersionsTab from '../components/detail/VersionsTab'
import LifecycleTab from '../components/detail/LifecycleTab'
import WriteActionsPanel from '../components/detail/WriteActionsPanel'

type TabKey = 'details' | 'structure' | 'documents' | 'cad' | 'whereUsed'
  | 'affected' | 'resulting' | 'referencingParts' | 'files' | 'versions' | 'lifecycle' | 'actions'

interface TabDef {
  key: TabKey
  label: string
}

/** Which tabs are available per Windchill type. */
const TABS_BY_TYPE: Record<string, TabDef[]> = {
  part: [
    { key: 'details', label: 'Details' },
    { key: 'structure', label: 'Struktur (BOM)' },
    { key: 'documents', label: 'Dokumente' },
    { key: 'cad', label: 'CAD' },
    { key: 'whereUsed', label: 'Where-Used' },
    { key: 'versions', label: 'Versionen' },
    { key: 'lifecycle', label: 'Lifecycle' },
    { key: 'actions', label: 'Aktionen' },
  ],
  document: [
    { key: 'details', label: 'Details' },
    { key: 'referencingParts', label: 'Referenzierende Parts' },
    { key: 'files', label: 'Dateien' },
    { key: 'versions', label: 'Versionen' },
    { key: 'lifecycle', label: 'Lifecycle' },
    { key: 'actions', label: 'Aktionen' },
  ],
  cad_document: [
    { key: 'details', label: 'Details' },
    { key: 'referencingParts', label: 'Verknüpftes Part' },
    { key: 'files', label: 'Dateien' },
    { key: 'versions', label: 'Versionen' },
    { key: 'lifecycle', label: 'Lifecycle' },
    { key: 'actions', label: 'Aktionen' },
  ],
  change_notice: [
    { key: 'details', label: 'Details' },
    { key: 'affected', label: 'Affected Items' },
    { key: 'resulting', label: 'Resulting Items' },
    { key: 'versions', label: 'Versionen' },
    { key: 'lifecycle', label: 'Lifecycle' },
    { key: 'actions', label: 'Aktionen' },
  ],
  change_request: [
    { key: 'details', label: 'Details' },
    { key: 'affected', label: 'Affected Items' },
    { key: 'versions', label: 'Versionen' },
    { key: 'lifecycle', label: 'Lifecycle' },
    { key: 'actions', label: 'Aktionen' },
  ],
  problem_report: [
    { key: 'details', label: 'Details' },
    { key: 'affected', label: 'Affected Items' },
    { key: 'versions', label: 'Versionen' },
    { key: 'lifecycle', label: 'Lifecycle' },
    { key: 'actions', label: 'Aktionen' },
  ],
}

const DEFAULT_TABS: TabDef[] = [{ key: 'details', label: 'Details' }]

export default function DetailPage() {
  const { typeKey = 'part', code } = useParams<{ typeKey: string; code: string }>()
  const navigate = useNavigate()

  const [detail, setDetail] = useState<ObjectDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<TabKey>('details')

  const load = useCallback(async () => {
    if (!code || !typeKey) return
    setLoading(true)
    setError('')
    try {
      const resp = await getObjectDetail(typeKey, code)
      setDetail(resp.detail)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)
    } finally {
      setLoading(false)
    }
  }, [typeKey, code])

  useEffect(() => { load() }, [load])

  // Reset tab when navigating to a different object
  useEffect(() => {
    setActiveTab('details')
  }, [typeKey, code])

  const tabs = TABS_BY_TYPE[typeKey] || DEFAULT_TABS

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-sm text-slate-500 animate-pulse">Lade Daten…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-4">
          <p className="font-medium mb-1">Fehler beim Laden von „{code}"</p>
          <p>{error}</p>
        </div>
        <button
          onClick={() => navigate(-1)}
          className="text-sm text-indigo-600 hover:underline"
        >
          ← Zurück zur Suche
        </button>
      </div>
    )
  }

  if (!detail || !code) return null

  return (
    <div className="space-y-4">
      {/* Header */}
      <DetailHeader detail={detail} onBack={() => navigate(-1)} />

      {/* Tab bar */}
      <nav className="border-b border-slate-200">
        <div className="flex gap-0 -mb-px">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Tab content */}
      <div>
        {activeTab === 'details' && <DetailsTab detail={detail} />}
        {activeTab === 'structure' && <StructureTab partNumber={detail.number} />}
        {activeTab === 'documents' && <DocumentsTab partCode={code} />}
        {activeTab === 'cad' && <CadTab partCode={code} />}
        {activeTab === 'whereUsed' && <WhereUsedTab partCode={code} />}
        {activeTab === 'affected' && (
          <ChangeItemsTab
            label="Affected Items"
            fetchFn={(signal) => getAffectedItems(typeKey, code, signal)}
          />
        )}
        {activeTab === 'resulting' && (
          <ChangeItemsTab
            label="Resulting Items"
            fetchFn={(signal) => getResultingItems(typeKey, code, signal)}
          />
        )}
        {activeTab === 'referencingParts' && (
          <ReferencingPartsTab typeKey={typeKey} code={code} />
        )}
        {activeTab === 'files' && (
          <FileInfoTab typeKey={typeKey} code={code} />
        )}
        {activeTab === 'versions' && (
          <VersionsTab typeKey={typeKey} code={code} />
        )}
        {activeTab === 'lifecycle' && (
          <LifecycleTab typeKey={typeKey} code={code} />
        )}
        {activeTab === 'actions' && (
          <WriteActionsPanel typeKey={typeKey} code={code} onSuccess={load} />
        )}
      </div>
    </div>
  )
}
