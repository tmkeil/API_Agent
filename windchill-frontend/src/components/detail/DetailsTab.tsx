import type { ObjectDetail } from '../../api/types'
import { TYPE_LABELS, formatDate } from '../../utils/labels'

interface Props {
  detail: ObjectDetail
}

/** Details tab — shows object master data. */
export default function DetailsTab({ detail }: Props) {
  const rows: [string, string][] = [
    ['Typ', TYPE_LABELS[detail.objectType] || detail.objectType],
    ['Subtyp', detail.subType || '—'],
    ['Nummer', detail.number],
    ['Name', detail.name],
    ['Version', detail.version],
    ['Iteration', detail.iteration],
    ['Status', detail.state],
    ['Identität', detail.identity],
    ['Kontext', detail.context],
    ['Zuletzt geändert', formatDate(detail.lastModified)],
    ['Erstellt', formatDate(detail.createdOn)],
    ['Objekt-ID', detail.objectId],
  ]

  return (
    <div className="bg-white rounded shadow-sm border border-slate-200">
      <table className="w-full text-sm">
        <tbody className="divide-y divide-slate-100">
          {rows.map(([label, value]) => (
            <tr key={label}>
              <td className="px-4 py-2.5 text-slate-400 font-medium w-44 whitespace-nowrap">
                {label}
              </td>
              <td className="px-4 py-2.5 text-slate-700">
                {value || '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
