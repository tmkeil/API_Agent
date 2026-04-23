import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { ObjectDetail } from '../../api/types'
import { formatDate } from '../../utils/labels'

interface Props {
  detail: ObjectDetail
}

/* ── Field definition ──────────────────────────────────────── */
interface FieldDef {
  key: string
  label: string
  format?: 'date' | 'refParts'
}

interface SectionDef {
  title: string
  fields: FieldDef[]
  defaultCollapsed?: boolean
}

/* ── WTDocument section layout (based on Windchill UI sections) ── */
const DOC_SECTIONS: SectionDef[] = [
  {
    title: 'Zusammenfassung',
    fields: [
      { key: 'DocTypeName', label: 'Typ' },
      { key: 'BALDOCUMENTSUBTYPE', label: 'Dokument-Subtyp' },
      { key: 'detail.number', label: 'Nummer' },
      { key: 'detail.name', label: 'Name' },
      { key: 'detail.version', label: 'Revision' },
      { key: 'detail.state', label: 'Status' },
      { key: 'CheckoutState', label: 'Checkout Status' },
      { key: 'ModifiedBy', label: 'Modified by' },
      { key: 'detail.lastModified', label: 'Last modified', format: 'date' },
    ],
  },
  {
    title: 'Identität',
    fields: [
      { key: 'Description', label: 'Beschreibung' },
      { key: 'BALDESCRIPTION1', label: 'BAL Beschreibung 1' },
      { key: 'BALDESCRIPTION2', label: 'BAL Beschreibung 2' },
      { key: 'BALDOCUMENTLANG', label: 'Sprache' },
      { key: 'FolderLocation', label: 'Location' },
      { key: 'BALREFERENCEPART', label: 'Referenz-Parts', format: 'refParts' },
    ],
  },
  {
    title: 'Steuerung (Control)',
    fields: [
      { key: 'BALSAPRELEVANCE', label: 'SAP Downstream erlaubt' },
      { key: 'BALFORMICARELEVANCE', label: 'Formica Downstream erlaubt' },
      { key: 'BALTIMELINERELEVANCE', label: 'Timeline Downstream erlaubt' },
      { key: 'BALPIMRELEVANCE', label: 'PIM Downstream erlaubt' },
      { key: 'BALWEBRELEVANCE', label: 'WEB Downstream erlaubt' },
      { key: 'BALARCHIVEREQUIRED', label: 'Archivierung erforderlich' },
      { key: 'BALCONFIDENTIALITY', label: 'Vertraulichkeit' },
      { key: 'BALSTATUSINFORMATION', label: 'Statusinformation' },
    ],
  },
  {
    title: 'Spezifische Konformitätsanforderungen (SCR)',
    defaultCollapsed: true,
    fields: [
      { key: 'BALDMSCRDISPLAY', label: 'SCR Display' },
      { key: 'BALDMSCREXPLFLAG', label: 'SCR Explosionsschutz' },
      { key: 'BALDMSCRSAFETYFLAG', label: 'SCR Funktionale Sicherheit' },
      { key: 'BALDMSCRFCMFLAG', label: 'SCR FCM Konformität' },
      { key: 'BALDMSCRRADIOFLAG', label: 'SCR Funk & Wireless' },
      { key: 'BALDMSCRCCCFLAG', label: 'SCR CCC Konformität' },
      { key: 'BALDMSCRULFLAG', label: 'SCR UL/CSA Konformität' },
      { key: 'BALDMSCR3AEHEDGFLAG', label: 'SCR 3A / EHEDG' },
      { key: 'BALDMSCRECOLABFLAG', label: 'SCR ECOLAB' },
      { key: 'BALDMSCRZULANFFLAG', label: 'SCR Zertifizierung' },
      { key: 'BALDMSCRTRACEFLAG', label: 'SCR Trace' },
      { key: 'BALDMSCRCUSTFLAG', label: 'SCR CopyExact' },
      { key: 'BALBYAPPROVALLIMITEDCHARACTERISTICS', label: 'Zulassungsbegrenzende Merkmale' },
    ],
  },
  {
    title: 'SAP',
    fields: [
      { key: 'BALSAPNAME', label: 'SAP Name' },
      { key: 'BALDOCUMENTTYPE', label: 'SAP Dokumenttyp' },
      { key: 'BALGROUPNUMBER', label: 'SAP Gruppennummer' },
    ],
  },
  {
    title: 'System',
    fields: [
      { key: 'detail.state', label: 'Status' },
      { key: 'LifeCycleTemplateName', label: 'Life-Cycle-Template' },
      { key: 'detail.context', label: 'Kontext' },
      { key: 'FolderLocation', label: 'Location' },
      { key: 'BALCREATEDBY', label: 'Created by (login)' },
      { key: 'CreatedBy', label: 'Created by' },
      { key: 'detail.createdOn', label: 'Created on', format: 'date' },
      { key: 'BALMODIFIEDBY', label: 'Modified by (login)' },
      { key: 'ModifiedBy', label: 'Modified by' },
      { key: 'detail.lastModified', label: 'Last modified', format: 'date' },
      { key: 'BALRELEASEDAT', label: 'Freigegeben am' },
      { key: 'BALRELEASEDBY', label: 'Freigegeben von' },
    ],
  },
  {
    title: 'Migration',
    defaultCollapsed: true,
    fields: [
      { key: 'BALLEGACYID', label: 'Legacy ID' },
      { key: 'BALOLDDATAMODEL', label: 'Altes Datenmodell' },
    ],
  },
]

/* ── All known field keys → for "Sonstige" fallback ── */
const KNOWN_KEYS = new Set<string>()
for (const section of DOC_SECTIONS) {
  for (const f of section.fields) {
    if (!f.key.startsWith('detail.')) KNOWN_KEYS.add(f.key)
  }
}
const SKIP_KEYS = new Set([
  'TypeIcon', 'CabinetName', 'FolderName', 'Latest', 'WorkInProgressState',
  'CheckOutStatus', 'ObjectType', 'Revision', 'Comments', 'Title',
  'BALHELPLINK', 'BALINSTRUCTIONS', 'BALSCRDISPLAY',
  'BALCLASSIFICATIONBINDINGWTDOC',
])

/* ── Resolve a field value ──────────────────────────────────── */
function resolveValue(detail: ObjectDetail, key: string): string {
  if (key.startsWith('detail.')) {
    const prop = key.slice(7) as keyof ObjectDetail
    return String(detail[prop] ?? '') || '—'
  }
  const raw = detail.allAttributes?.[key]
  if (raw === undefined || raw === null || raw === '') return ''
  return String(raw)
}

/* ── Reference Parts display (comma-separated numbers → clickable links) ── */
function RefPartsValue({ value }: { value: string }) {
  const navigate = useNavigate()
  if (!value) return <span className="text-slate-400">—</span>

  const numbers = value.split(',').map(s => s.trim()).filter(Boolean)
  if (numbers.length === 0) return <span className="text-slate-400">—</span>

  return (
    <div className="flex flex-wrap gap-1.5">
      {numbers.map((num, i) => (
        <button
          key={i}
          onClick={() => navigate(`/detail/part/${num}`)}
          className="text-indigo-600 hover:text-indigo-800 hover:underline font-mono text-xs"
        >
          {num}
        </button>
      ))}
    </div>
  )
}

/* ── Collapsible section component ──────────────────────────── */
function Section({ title, children, defaultCollapsed = false }: {
  title: string
  children: React.ReactNode
  defaultCollapsed?: boolean
}) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed)

  return (
    <div className="bg-white rounded shadow-sm border border-slate-200 overflow-hidden">
      <button
        onClick={() => setCollapsed(c => !c)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 hover:bg-slate-100 transition-colors border-b border-slate-200"
      >
        <span className="text-xs font-semibold text-slate-600 uppercase tracking-wider">{title}</span>
        <svg
          className={`w-4 h-4 text-slate-400 transition-transform ${collapsed ? '' : 'rotate-180'}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {!collapsed && children}
    </div>
  )
}

/* ── Main Component ──────────────────────────────────────────── */
export default function DocDetailsTab({ detail }: Props) {
  const attrs = detail.allAttributes || {}

  const otherEntries = Object.entries(attrs)
    .filter(([k]) => !KNOWN_KEYS.has(k) && !SKIP_KEYS.has(k))
    .sort((a, b) => a[0].localeCompare(b[0]))

  return (
    <div className="space-y-3">
      {DOC_SECTIONS.map(section => {
        const hasValues = section.fields.some(f => {
          const val = resolveValue(detail, f.key)
          return val && val !== '—'
        })
        if (!hasValues) return null

        return (
          <Section key={section.title} title={section.title} defaultCollapsed={section.defaultCollapsed}>
            <table className="w-full text-sm">
              <tbody className="divide-y divide-slate-100">
                {section.fields.map(f => {
                  const val = resolveValue(detail, f.key)
                  if (!val && !f.key.startsWith('detail.')) return null

                  return (
                    <tr key={f.key}>
                      <td className="px-4 py-2 text-slate-400 font-medium w-56 whitespace-nowrap align-top">
                        {f.label}
                      </td>
                      <td className="px-4 py-2 text-slate-700">
                        {f.format === 'date' ? formatDate(val) :
                         f.format === 'refParts' ? <RefPartsValue value={val} /> :
                         val || '—'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </Section>
        )
      })}

      {otherEntries.length > 0 && (
        <Section title={`Sonstige Attribute (${otherEntries.length})`} defaultCollapsed>
          <table className="w-full text-sm">
            <tbody className="divide-y divide-slate-100">
              {otherEntries.map(([key, value]) => (
                <tr key={key}>
                  <td className="px-4 py-2 text-slate-400 font-mono text-xs w-56 whitespace-nowrap align-top">
                    {key}
                  </td>
                  <td className="px-4 py-2 text-slate-700 break-all">
                    {String(value)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>
      )}
    </div>
  )
}
