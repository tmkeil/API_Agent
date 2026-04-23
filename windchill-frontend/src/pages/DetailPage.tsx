import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getAffectedItems, getObjectDetail, getResultingItems, createWorkItem } from '../api/client'
import type { ObjectDetail } from '../api/types'
import DetailHeader from '../components/detail/DetailHeader'
import DetailsTab from '../components/detail/DetailsTab'
import PartDetailsTab from '../components/detail/PartDetailsTab'
import DocDetailsTab from '../components/detail/DocDetailsTab'
import CadDetailsTab from '../components/detail/CadDetailsTab'
import AttributesTab from '../components/detail/AttributesTab'
import StructureTab from '../components/detail/StructureTab'
import CadStructureTab from '../components/detail/CadStructureTab'
import DocumentsTab from '../components/detail/DocumentsTab'
import CadTab from '../components/detail/CadTab'
import AllDocumentsTab from '../components/detail/AllDocumentsTab'
import WhereUsedTab from '../components/detail/WhereUsedTab'
import OccurrencesTab from '../components/detail/OccurrencesTab'
import ChangeItemsTab from '../components/detail/ChangeItemsTab'
import ReferencingPartsTab from '../components/detail/ReferencingPartsTab'
import FileInfoTab from '../components/detail/FileInfoTab'
import VersionsTab from '../components/detail/VersionsTab'
import LifecycleTab from '../components/detail/LifecycleTab'
import EquivalenceTab from '../components/detail/EquivalenceTab'
import WriteActionsPanel from '../components/detail/WriteActionsPanel'

type TabKey = 'details' | 'attributes' | 'structure' | 'cadStructure' | 'documents' | 'cad' | 'allDocuments'
  | 'whereUsed' | 'occurrences' | 'equivalence'
  | 'affected' | 'resulting' | 'referencingParts' | 'files' | 'versions' | 'lifecycle' | 'actions'

interface TabDef {
  key: TabKey
  label: string
}

/** Which tabs are available per Windchill type. */
const TABS_BY_TYPE: Record<string, TabDef[]> = {
  part: [
    { key: 'details', label: 'Details' },
    { key: 'attributes', label: 'Attributes' },
    { key: 'structure', label: 'Structure (BOM)' },
    { key: 'allDocuments', label: 'Documents' },
    { key: 'whereUsed', label: 'Where-Used' },
    { key: 'occurrences', label: 'Occurrences' },
    { key: 'equivalence', label: 'Equivalence Network' },
    { key: 'versions', label: 'Versions' },
    { key: 'lifecycle', label: 'Lifecycle' },
    { key: 'actions', label: 'Actions' },
  ],
  document: [
    { key: 'details', label: 'Details' },
    { key: 'attributes', label: 'Attributes' },
    { key: 'referencingParts', label: 'Referencing Parts' },
    { key: 'files', label: 'Files' },
    { key: 'versions', label: 'Versions' },
    { key: 'lifecycle', label: 'Lifecycle' },
    { key: 'actions', label: 'Actions' },
  ],
  cad_document: [
    { key: 'details', label: 'Details' },
    { key: 'attributes', label: 'Attributes' },
    { key: 'cadStructure', label: 'Structure' },
    { key: 'referencingParts', label: 'Linked Part' },
    { key: 'files', label: 'Files' },
    { key: 'versions', label: 'Versions' },
    { key: 'lifecycle', label: 'Lifecycle' },
    { key: 'actions', label: 'Actions' },
  ],
  change_notice: [
    { key: 'details', label: 'Details' },
    { key: 'attributes', label: 'Attributes' },
    { key: 'affected', label: 'Affected Items' },
    { key: 'resulting', label: 'Resulting Items' },
    { key: 'versions', label: 'Versions' },
    { key: 'lifecycle', label: 'Lifecycle' },
    { key: 'actions', label: 'Actions' },
  ],
  change_request: [
    { key: 'details', label: 'Details' },
    { key: 'attributes', label: 'Attributes' },
    { key: 'affected', label: 'Affected Items' },
    { key: 'versions', label: 'Versions' },
    { key: 'lifecycle', label: 'Lifecycle' },
    { key: 'actions', label: 'Actions' },
  ],
  problem_report: [
    { key: 'details', label: 'Details' },
    { key: 'attributes', label: 'Attributes' },
    { key: 'affected', label: 'Affected Items' },
    { key: 'versions', label: 'Versions' },
    { key: 'lifecycle', label: 'Lifecycle' },
    { key: 'actions', label: 'Actions' },
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
        <p className="text-sm text-slate-500 animate-pulse">Loading data…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-4">
          <p className="font-medium mb-1">Failed to load „{code}"</p>
          <p>{error}</p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="text-sm text-indigo-600 hover:underline"
        >
          ← Back to search
        </button>
      </div>
    )
  }

  if (!detail || !code) return null

  const isChangeNotice = typeKey === 'change_notice'

  const handleStartWorkItem = async () => {
    if (!detail) return
    try {
      const wi = await createWorkItem({
        number: detail.number,
        name: detail.name,
        subType: detail.subType,
        state: detail.state,
        objectId: detail.objectId,
      })
      navigate(`/workitem/${wi.id}`)
    } catch (e: unknown) {
      setError((e as Error).message || 'Failed to create WorkItem')
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <DetailHeader detail={detail} onBack={() => navigate('/')} />
        {isChangeNotice && (
          <button
            onClick={handleStartWorkItem}
            className="shrink-0 ml-4 px-3 py-1.5 text-xs font-medium rounded bg-emerald-50 text-emerald-700 border border-emerald-300 hover:bg-emerald-100 transition-colors"
            title="Create WorkItem for this Change Notice"
          >
            ▶ Start WorkItem
          </button>
        )}
      </div>

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
        {activeTab === 'details' && (
          typeKey === 'part' ? <PartDetailsTab detail={detail} /> :
          typeKey === 'cad_document' ? <CadDetailsTab detail={detail} /> :
          typeKey === 'document' ? <DocDetailsTab detail={detail} /> :
          <DetailsTab detail={detail} />
        )}
        {activeTab === 'attributes' && <AttributesTab detail={detail} />}
        {activeTab === 'structure' && <StructureTab partNumber={detail.number} />}
        {activeTab === 'cadStructure' && <CadStructureTab cadCode={detail.number} />}
        {activeTab === 'documents' && <DocumentsTab partCode={code} />}
        {activeTab === 'cad' && <CadTab partCode={code} />}
        {activeTab === 'allDocuments' && <AllDocumentsTab partCode={code} />}
        {activeTab === 'whereUsed' && <WhereUsedTab partCode={code} />}
        {activeTab === 'occurrences' && <OccurrencesTab partCode={code} />}
        {activeTab === 'equivalence' && <EquivalenceTab detail={detail} />}
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
          <WriteActionsPanel typeKey={typeKey} code={code} objectId={detail?.objectId} onSuccess={load} />
        )}
      </div>
    </div>
  )
}
