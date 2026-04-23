import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { ObjectDetail } from '../../api/types'
import { formatDate } from '../../utils/labels'

interface Props {
  detail: ObjectDetail
}

/* ── Field definition for a single row ──────────────────────── */
interface FieldDef {
  /** OData attribute key in allAttributes (or special prefix "detail." for top-level). */
  key: string
  /** Display label shown in the UI. */
  label: string
  /** Optional formatter: 'date' | 'equivNetwork'. */
  format?: 'date' | 'equivNetwork'
}

/* ── Section definition ──────────────────────────────────────── */
interface SectionDef {
  title: string
  fields: FieldDef[]
  /** Start collapsed? Default false. */
  defaultCollapsed?: boolean
}

/* ── WTPart section layout (maps OData fields → Windchill UI sections) ── */
const PART_SECTIONS: SectionDef[] = [
  {
    title: 'Visualization & Attributes',
    fields: [
      { key: 'detail.subType', label: 'Type' },
      { key: 'detail.number', label: 'Number' },
      { key: 'detail.name', label: 'Name' },
      { key: 'detail.version', label: 'Revision' },
      { key: 'detail.state', label: 'Status' },
      { key: 'CheckoutState', label: 'Checkout Status' },
      { key: 'ModifiedBy', label: 'Modified by' },
      { key: 'detail.lastModified', label: 'Last modified', format: 'date' },
    ],
  },
  {
    title: 'Identity & Classification',
    fields: [
      { key: 'BALDESCRIPTION1', label: 'Description' },
      { key: 'Source', label: 'Source' },
      { key: 'AssemblyMode', label: 'Assembly Mode' },
      { key: 'GatheringPart', label: 'Gathering Part' },
      { key: 'ConfigurableModule', label: 'Configurable Module' },
      { key: 'DefaultUnit', label: 'Default Unit' },
      { key: 'EndItem', label: 'End Item' },
      { key: '_equivNetwork', label: 'Equivalence Network', format: 'equivNetwork' },
    ],
  },
  {
    title: 'Control',
    fields: [
      { key: 'BALISVARIANT', label: 'Is Variant' },
      { key: 'BALNOTSUITABLENEWDESIGN', label: 'Not Suitable for New Design' },
      { key: 'BALDEFINEDSTORECONDITION', label: 'Special Storage Conditions' },
      { key: 'BALSPECIALOPERATIONALCONDITIONS', label: 'Special Operational Conditions' },
      { key: 'BALCONFIDENTIALITY', label: 'Confidentiality' },
    ],
  },
  {
    title: 'Specific Conformity Requirements (SCR)',
    defaultCollapsed: true,
    fields: [
      { key: 'BALDMSCRDISPLAY', label: 'SCR Display' },
      { key: 'BALDMSCREXPLFLAG', label: 'SCR Explosion Protection' },
      { key: 'BALDMSCRSAFETYFLAG', label: 'SCR Functional Safety' },
      { key: 'BALDMSCRFCMFLAG', label: 'SCR FCM Conformity' },
      { key: 'BALDMSCRRADIOFLAG', label: 'SCR Radio & Wireless' },
      { key: 'BALDMSCRCCCFLAG', label: 'SCR CCC Conformity' },
      { key: 'BALDMSCRULFLAG', label: 'SCR UL/CSA Conformity' },
      { key: 'BALDMSCR3AEHEDGFLAG', label: 'SCR 3A / EHEDG' },
      { key: 'BALDMSCRECOLABFLAG', label: 'SCR ECOLAB' },
      { key: 'BALDMSCRZULANFFLAG', label: 'SCR Certification' },
      { key: 'BALDMSCRTRACEFLAG', label: 'SCR Trace' },
      { key: 'BALDMSCRCUSTFLAG', label: 'SCR CopyExact' },
    ],
  },
  {
    title: 'SAP',
    fields: [
      { key: 'BALSAPNAME', label: 'SAP Name' },
      { key: 'BALSAPMATERIALTYPE', label: 'SAP Material Type' },
      { key: 'BALSAPMARAZZROLLUSEUAS', label: 'SAP Rollout Strategy' },
      { key: 'BALPVID', label: 'PVID' },
      { key: 'BALSAPORDERCODE', label: 'SAP Order-Code' },
      { key: 'BALSAPMSTAE', label: 'SAP Plant-Specific Material Status' },
      { key: 'BALSAPASSIGNEDPLANTS', label: 'SAP Assigned Plants' },
      { key: 'BALBINDING', label: 'Binding' },
      { key: 'BALSUFFIX', label: 'Suffix' },
    ],
  },
  {
    title: 'System',
    fields: [
      { key: 'detail.state', label: 'Status' },
      { key: 'LifeCycleTemplateName', label: 'Life-Cycle-Template' },
      { key: 'FolderLocation', label: 'Location' },
      { key: 'View', label: 'View' },
      { key: 'CreatedBy', label: 'Created by' },
      { key: 'detail.createdOn', label: 'Created on', format: 'date' },
      { key: 'ModifiedBy', label: 'Modified by' },
      { key: 'detail.lastModified', label: 'Last modified', format: 'date' },
    ],
  },
  {
    title: 'Migration Source',
    defaultCollapsed: true,
    fields: [
      { key: 'BALLegacyERPsource', label: 'Legacy ERP Source' },
      { key: 'BALLegacyERPname', label: 'Legacy ERP Name' },
      { key: 'BALLegacyERPnumber', label: 'Legacy ERP Number' },
      { key: 'BALLegacyERPversion', label: 'Legacy ERP Version' },
      { key: 'BALLegacyERPstate', label: 'Legacy ERP Status' },
      { key: 'BALERPmigrationdate', label: 'Migration Date', format: 'date' },
    ],
  },
]

/* ── All known field keys across all sections → for "Sonstige" fallback ── */
const KNOWN_KEYS = new Set<string>()
for (const section of PART_SECTIONS) {
  for (const f of section.fields) {
    if (!f.key.startsWith('detail.')) KNOWN_KEYS.add(f.key)
  }
}
// Also skip keys already shown in DetailHeader or purely internal
const SKIP_KEYS = new Set([
  'TypeIcon', 'CabinetName', 'FolderName', 'Latest', 'WorkInProgressState',
  'CheckOutStatus', 'DefaultTraceCode', 'PhantomManufacturingPart',
  'Revision', 'ObjectType', 'BALOLDDATAMODEL',
  'BALHELPLINK', 'BALINSTRUCTION', 'BALCPORDERPREFIX',
  'BALDOWNSTREAM', 'BALUPSTREAM',
])

/* ── Resolve a field value from detail + allAttributes ──── */
function resolveValue(detail: ObjectDetail, key: string): string {
  if (key.startsWith('detail.')) {
    const prop = key.slice(7) as keyof ObjectDetail
    return String(detail[prop] ?? '') || '—'
  }
  // Virtual key: merge BALDOWNSTREAM + BALUPSTREAM for Equivalence Network
  if (key === '_equivNetwork') {
    const attrs = detail.allAttributes || {}
    const down = attrs['BALDOWNSTREAM']
    const up = attrs['BALUPSTREAM']
    if (down) return String(down)
    if (up) return String(up)
    return ''
  }
  const raw = detail.allAttributes?.[key]
  if (raw === undefined || raw === null || raw === '') return ''
  return String(raw)
}

/* ── Parse Equivalence Network into Design↔Manufacturing pairs ── */
interface EquivEntry { number: string; name: string; org: string; version: string; view: string }
interface EquivPair { design: EquivEntry; manufacturing: EquivEntry }

function parseEquivEntries(value: string): EquivEntry[] {
  if (!value) return []

  // BALUPSTREAM can be just plain numbers (e.g. "1200209432")
  if (!value.includes('(')) {
    return value.split(',').map(s => s.trim()).filter(Boolean).map(num => ({
      number: num, name: '', org: '', version: '', view: 'Design',
    }))
  }

  // Full format: "NUMBER, NAME, ORG, VERSION (VIEW), …" — groups of 4
  const parts = value.split(',').map(s => s.trim())
  const all: EquivEntry[] = []
  let i = 0
  while (i + 3 < parts.length) {
    const number = parts[i]
    const name = parts[i + 1]
    const org = parts[i + 2]
    const versionView = parts[i + 3]
    const vMatch = versionView.match(/^(.+?)\s*\((.+?)\)$/)
    all.push({
      number, name, org,
      version: vMatch ? vMatch[1] : versionView,
      view: vMatch ? vMatch[2] : '',
    })
    i += 4
  }
  return all
}

function buildEquivPairs(detail: ObjectDetail): EquivPair[] {
  const attrs = detail.allAttributes || {}
  const down = String(attrs['BALDOWNSTREAM'] ?? '')
  const up = String(attrs['BALUPSTREAM'] ?? '')

  // Current part info
  const self: EquivEntry = {
    number: detail.number,
    name: detail.name,
    org: '', // not needed for display
    version: detail.version,
    view: String(attrs['View'] ?? ''),
  }

  const isDesign = self.view === 'Design'
  const pairs: EquivPair[] = []

  if (isDesign && down) {
    // Design part → BALDOWNSTREAM lists Manufacturing counterparts
    const entries = parseEquivEntries(down)
    // Deduplicate: keep latest version per number
    const latest = new Map<string, EquivEntry>()
    for (const e of entries) {
      const existing = latest.get(e.number)
      if (!existing || e.version.localeCompare(existing.version) > 0)
        latest.set(e.number, e)
    }
    for (const mfg of latest.values()) {
      pairs.push({ design: self, manufacturing: mfg })
    }
  } else if (!isDesign && up) {
    // Manufacturing part → BALUPSTREAM lists Design counterparts
    const entries = parseEquivEntries(up)
    const latest = new Map<string, EquivEntry>()
    for (const e of entries) {
      const existing = latest.get(e.number)
      if (!existing || e.version.localeCompare(existing.version) > 0)
        latest.set(e.number, e)
    }
    for (const dsn of latest.values()) {
      pairs.push({ design: dsn, manufacturing: self })
    }
  }
  return pairs
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

/* ── Equivalence Network display (Design ↔ Manufacturing pairs) ───── */
function EquivNetworkValue({ detail }: { detail: ObjectDetail }) {
  const navigate = useNavigate()
  const pairs = buildEquivPairs(detail)

  if (pairs.length === 0) return <span className="text-slate-400">—</span>

  return (
    <div className="space-y-1.5">
      {pairs.map((p, i) => (
        <div key={i} className="flex items-center gap-1.5 text-sm flex-wrap">
          {/* Design side */}
          <button
            onClick={() => navigate(`/detail/part/${p.design.number}`)}
            className="text-indigo-600 hover:text-indigo-800 hover:underline font-mono text-xs"
          >
            {p.design.number}
          </button>
          {p.design.name && <span className="text-slate-500 text-xs truncate max-w-48">{p.design.name}</span>}
          <span className="text-slate-400 text-xs">{p.design.version}</span>
          <span className="px-1 py-0.5 rounded text-[10px] font-medium bg-sky-50 text-sky-700 border border-sky-200">
            Design
          </span>

          <span className="text-slate-300 mx-1">—</span>

          {/* Manufacturing side */}
          <button
            onClick={() => navigate(`/detail/part/${p.manufacturing.number}`)}
            className="text-indigo-600 hover:text-indigo-800 hover:underline font-mono text-xs"
          >
            {p.manufacturing.number}
          </button>
          {p.manufacturing.name && <span className="text-slate-500 text-xs truncate max-w-48">{p.manufacturing.name}</span>}
          <span className="text-slate-400 text-xs">{p.manufacturing.version}</span>
          <span className="px-1 py-0.5 rounded text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
            Manufacturing
          </span>
        </div>
      ))}
    </div>
  )
}

/* ── Main Component ──────────────────────────────────────────── */
export default function PartDetailsTab({ detail }: Props) {
  const attrs = detail.allAttributes || {}

  // Collect "other" fields not covered by any section
  const otherEntries = Object.entries(attrs)
    .filter(([k]) => !KNOWN_KEYS.has(k) && !SKIP_KEYS.has(k))
    .sort((a, b) => a[0].localeCompare(b[0]))

  return (
    <div className="space-y-3">
      {PART_SECTIONS.map(section => {
        // Only show section if at least one field has a value
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
                  if (!val && !f.key.startsWith('detail.')) return null // hide empty optional fields

                  return (
                    <tr key={f.key}>
                      <td className="px-4 py-2 text-slate-400 font-medium w-56 whitespace-nowrap align-top">
                        {f.label}
                      </td>
                      <td className="px-4 py-2 text-slate-700">
                        {f.format === 'date' ? formatDate(val) :
                         f.format === 'equivNetwork' ? <EquivNetworkValue detail={detail} /> :
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

      {/* Sonstige Attribute — fields not mapped to any section */}
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
