import { getPartDocuments } from '../../api/client'
import DocumentListTab from './DocumentListTab'

interface Props {
  partCode: string
}

/** Documents tab — WTDocuments linked to a part. */
export default function DocumentsTab({ partCode }: Props) {
  return (
    <DocumentListTab
      label="Documents"
      partCode={partCode}
      fetchFn={getPartDocuments}
      badge="Doc"
      badgeClass="bg-amber-50 text-amber-700 border-amber-200"
    />
  )
}
