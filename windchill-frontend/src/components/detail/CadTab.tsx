import { getPartCadDocuments } from '../../api/client'
import DocumentListTab from './DocumentListTab'

interface Props {
  partCode: string
}

/** CAD Documents tab — EPMDocuments linked to a part. */
export default function CadTab({ partCode }: Props) {
  return (
    <DocumentListTab
      label="CAD-Dokumente"
      partCode={partCode}
      fetchFn={getPartCadDocuments}
      badge="CAD"
      badgeClass="bg-violet-50 text-violet-700 border-violet-200"
    />
  )
}
