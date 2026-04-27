import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createObject, fetchContainers, fetchClassificationNodes, fetchPartSubtypes } from '../api/client'
import type { ClassificationNode, ContainerItem, PartSubtype } from '../api/types'
import { getSubtypeSpec, isRequired, isVisible, type FieldKey } from './createPart/subtypeFieldSpecs'

/* ── Windchill-Systemkonstanten (aus Part-Erstellformular) ── */

const VIEWS = [
  { value: 'Design', label: 'Design' },
  { value: 'Manufacturing', label: 'Manufacturing' },
]

const SOURCES = [
  { value: 'notapplicable', label: 'Not Applicable' },
  { value: 'make', label: 'Make' },
  { value: 'buy', label: 'Buy' },
]

const ASSEMBLY_MODES = [
  { value: 'separable', label: 'Separable' },
  { value: 'inseparable', label: 'Inseparable' },
  { value: 'component', label: 'Component' },
]

const UNITS = [
  { value: 'ea', label: 'each' },
  { value: 'as_needed', label: 'as needed' },
  { value: 'kg', label: 'kilograms' },
  { value: 'm', label: 'meters' },
  { value: 'l', label: 'liters' },
  { value: 'sq_m', label: 'square meters' },
  { value: 'cu_m', label: 'cubic meters' },
  { value: 'g', label: 'gram' },
  { value: 'mm', label: 'millimeter' },
  { value: 'fraction', label: 'partial each' },
  { value: 'ml', label: 'milliliter' },
  { value: 'KAN', label: 'can' },
  { value: 'FLA', label: 'bottle' },
  { value: 'mg', label: 'milligram' },
  { value: 'sq_mm', label: 'square millimeter' },
  { value: 'cm', label: 'centimeters' },
  { value: 'km', label: 'kilometer' },
  { value: 'sq_cm', label: 'square centimeters' },
  { value: 'FT', label: 'feed' },
  { value: 'IN', label: 'inch' },
]

const PRODUCT_FAMILIES = [
  '', 'BAE', 'BAI', 'BAM', 'BAV', 'BAW', 'BCC', 'BCM', 'BCS', 'BCW',
  'BDG', 'BEN', 'BES', 'BFB', 'BFD', 'BFF', 'BFO', 'BFS', 'BFT',
  'BGL', 'BHS', 'BIC', 'BID', 'BIL', 'BIP', 'BIR', 'BIS', 'BIU', 'BIW',
  'BKT', 'BLA', 'BLG', 'BLT', 'BMD', 'BMF', 'BML', 'BMP', 'BNI', 'BNL',
  'BNN', 'BNP', 'BNS', 'BOD', 'BOH', 'BOL', 'BOS', 'BOW', 'BPI',
  'BSE', 'BSG', 'BSI', 'BSP', 'BSS', 'BSW', 'BTL', 'BTM', 'BTS',
  'BUS', 'BVS', 'BWL', 'EQU', 'FHW', 'PIU', 'PLP', 'SET',
]

/* ── Classification Tree (Windchill Part Classification) ─── */

interface ClassificationEntry {
  name: string
  depth: number
  isGroup: boolean
}

const CLASSIFICATIONS: ClassificationEntry[] = [
  { name: 'Component', depth: 0, isGroup: true },
  { name: 'Label', depth: 1, isGroup: false },
  { name: 'TBD', depth: 1, isGroup: false },
  { name: 'Accessory', depth: 1, isGroup: true },
  { name: 'Nut Kit', depth: 2, isGroup: false },
  { name: 'Auxiliary and operating materials', depth: 1, isGroup: true },
  { name: 'Adhesive', depth: 2, isGroup: false },
  { name: 'Adhesive strip', depth: 2, isGroup: false },
  { name: 'Potting Material', depth: 2, isGroup: false },
  { name: 'Tin Solder', depth: 2, isGroup: false },
  { name: 'ECAD Electrical Component', depth: 1, isGroup: true },
  { name: 'ECAD Undefined', depth: 2, isGroup: false },
  { name: 'Pseudo Components', depth: 2, isGroup: false },
  { name: 'Circuit Protection', depth: 2, isGroup: true },
  { name: 'Fuses', depth: 3, isGroup: false },
  { name: 'Inrush Current Limiters', depth: 3, isGroup: false },
  { name: 'Power Controllers', depth: 3, isGroup: false },
  { name: 'Resettable Fuses', depth: 3, isGroup: false },
  { name: 'Reverse Polarity Protection', depth: 3, isGroup: false },
  { name: 'TVS Diodes', depth: 3, isGroup: false },
  { name: 'Varistors', depth: 3, isGroup: false },
  { name: 'Connectors', depth: 2, isGroup: true },
  { name: 'Audio_Video Connectors', depth: 3, isGroup: false },
  { name: 'Card Edge Connectors', depth: 3, isGroup: false },
  { name: 'Circular Connectors', depth: 3, isGroup: false },
  { name: 'D-Sub', depth: 3, isGroup: false },
  { name: 'FFC_FPC Connectors', depth: 3, isGroup: false },
  { name: 'Modular_Ethernet Connectors', depth: 3, isGroup: false },
  { name: 'Pin Headers', depth: 3, isGroup: false },
  { name: 'Power Connectors', depth: 3, isGroup: false },
  { name: 'RF_Coaxial Connectors', depth: 3, isGroup: false },
  { name: 'Ribbon Connectors', depth: 3, isGroup: false },
  { name: 'Terminal Blocks', depth: 3, isGroup: false },
  { name: 'Terminals', depth: 3, isGroup: false },
  { name: 'USB Connectors', depth: 3, isGroup: false },
  { name: 'Discrete Semiconductors', depth: 2, isGroup: true },
  { name: 'Diodes', depth: 3, isGroup: true },
  { name: 'Current Limiting_Regulator', depth: 4, isGroup: false },
  { name: 'General Diodes', depth: 4, isGroup: false },
  { name: 'Zener', depth: 4, isGroup: false },
  { name: 'Thyristors', depth: 3, isGroup: true },
  { name: 'DIACs & SIDACs', depth: 4, isGroup: false },
  { name: 'SCRs', depth: 4, isGroup: false },
  { name: 'Transistors', depth: 3, isGroup: true },
  { name: 'Bipolar', depth: 4, isGroup: false },
  { name: 'IGBTs', depth: 4, isGroup: false },
  { name: 'JFETs', depth: 4, isGroup: false },
  { name: 'MOSFETs', depth: 4, isGroup: false },
  { name: 'ECAD Electromechanical', depth: 2, isGroup: true },
  { name: 'Antennas', depth: 3, isGroup: false },
  { name: 'Electromagnetic Interfaces', depth: 3, isGroup: false },
  { name: 'Encoders', depth: 3, isGroup: false },
  { name: 'Heatsink', depth: 3, isGroup: false },
  { name: 'IC & Component Sockets', depth: 3, isGroup: false },
  { name: 'Relays', depth: 3, isGroup: false },
  { name: 'Shielding', depth: 3, isGroup: false },
  { name: 'Spacers', depth: 3, isGroup: false },
  { name: 'Speakers', depth: 3, isGroup: false },
  { name: 'Wire Management', depth: 3, isGroup: false },
  { name: 'Switches', depth: 3, isGroup: true },
  { name: 'DIP', depth: 4, isGroup: false },
  { name: 'Jumper', depth: 4, isGroup: false },
  { name: 'Rocker', depth: 4, isGroup: false },
  { name: 'Rotary', depth: 4, isGroup: false },
  { name: 'Slide', depth: 4, isGroup: false },
  { name: 'Snap Action', depth: 4, isGroup: false },
  { name: 'Tactile', depth: 4, isGroup: false },
  { name: 'Integrated Circuits (ICs)', depth: 2, isGroup: true },
  { name: 'Analog Switches & Multiplexers', depth: 3, isGroup: false },
  { name: 'ASICs', depth: 3, isGroup: false },
  { name: 'Audio_Video ICs', depth: 3, isGroup: false },
  { name: 'Clock & Timing', depth: 3, isGroup: false },
  { name: 'Codemeter', depth: 3, isGroup: false },
  { name: 'Solid State Relays', depth: 3, isGroup: false },
  { name: 'Data Converter ICs', depth: 3, isGroup: true },
  { name: 'Analog to Digital', depth: 4, isGroup: false },
  { name: 'Digital Potentiometers', depth: 4, isGroup: false },
  { name: 'Digital to Analog', depth: 4, isGroup: false },
  { name: 'Time to Digital', depth: 4, isGroup: false },
  { name: 'Embedded Processors & Controllers', depth: 3, isGroup: true },
  { name: 'CPLDs', depth: 4, isGroup: false },
  { name: 'Digital Signal Controllers & Processors', depth: 4, isGroup: false },
  { name: 'FPGAs', depth: 4, isGroup: false },
  { name: 'Microcontrollers', depth: 4, isGroup: false },
  { name: 'Microprocessors', depth: 4, isGroup: false },
  { name: 'Programmable System On a Chip', depth: 4, isGroup: false },
  { name: 'System On a Modul', depth: 4, isGroup: false },
  { name: 'Interface ICs', depth: 3, isGroup: true },
  { name: 'Anybus', depth: 4, isGroup: false },
  { name: 'CAN Bus', depth: 4, isGroup: false },
  { name: 'CC-Link', depth: 4, isGroup: false },
  { name: 'CLIQ', depth: 4, isGroup: false },
  { name: 'Current Limiters', depth: 4, isGroup: false },
  { name: 'Digital Isolators', depth: 4, isGroup: false },
  { name: 'Ethernet', depth: 4, isGroup: false },
  { name: 'IEEE-1394', depth: 4, isGroup: false },
  { name: 'Interbus', depth: 4, isGroup: false },
  { name: 'IO-Expander', depth: 4, isGroup: false },
  { name: 'IO-Link', depth: 4, isGroup: false },
  { name: 'LIN Bus', depth: 4, isGroup: false },
  { name: 'LVDS', depth: 4, isGroup: false },
]

/* ── Subtype Display-Namen (wie im Windchill UI) ─────────── */
const TYPE_DISPLAY_NAMES: Record<string, string> = {
  'PTC.ProdMgmt.BALMECHATRONICPART': 'Component',
  'PTC.ProdMgmt.BALAUXPART':         'Auxiliary Material',
  'PTC.ProdMgmt.BALENCDOCPART':      'Enclosed Document Part',
  'PTC.ProdMgmt.BALEQUIPMENTPART':   'Equipment',
  'PTC.ProdMgmt.BALPACKAGEPART':     'Package',
  'PTC.ProdMgmt.BALPRODUCTPART':     'Product',
  'PTC.ProdMgmt.BALCOLLECTIONPART':  'Collection',
  'PTC.ProdMgmt.BALRAWMATERIAL':     'Raw Material',
}

/* ── Subtype → Default-Classification Mapping ────────────── */
// Jeder Balluff-Subtype hat eine passende Default-TBD-Classification.
// Wenn der User den Subtype wechselt, wird die Classification
// automatisch angepasst (wie im Windchill UI).
const TYPE_CLASSIFICATION_MAP: Record<string, string> = {
  'PTC.ProdMgmt.BALMECHATRONICPART': 'WTPartComponentTBD',
  'PTC.ProdMgmt.BALAUXPART':         'WTPartAuxiliaryTBD',
  'PTC.ProdMgmt.BALENCDOCPART':      'WTPartEncDocTBD',
  'PTC.ProdMgmt.BALEQUIPMENTPART':   'WTPartEquipmentTBD',
  'PTC.ProdMgmt.BALPACKAGEPART':     'WTPartPackingTBD',
  'PTC.ProdMgmt.BALRAWMATERIAL':     'WTPartAuxiliaryTBD',
  'PTC.ProdMgmt.BALPRODUCTPART':     '',
  'PTC.ProdMgmt.BALCOLLECTIONPART':  '',
}

const DEFAULT_TYPE = 'PTC.ProdMgmt.BALMECHATRONICPART'

/* ── Form State ───────────────────────────────────────────── */

interface FormState {
  TypeId: string
  Number: string
  Name: string
  Description: string
  View: string
  Source: string
  DefaultUnit: string
  AssemblyMode: string
  GatheringPart: string
  ConfigurableModule: string
  ProductFamily: string
  Classification: string
  ContainerBinding: string
}

const INITIAL: FormState = {
  TypeId: DEFAULT_TYPE,
  Number: '',
  Name: '',
  Description: '',
  View: 'Design',
  Source: 'notapplicable',
  DefaultUnit: 'ea',
  AssemblyMode: 'separable',
  GatheringPart: 'no',
  ConfigurableModule: 'no',
  ProductFamily: 'PIU',
  Classification: TYPE_CLASSIFICATION_MAP[DEFAULT_TYPE] || '',
  ContainerBinding: '',
}

export default function CreatePartPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState<FormState>(INITIAL)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [containers, setContainers] = useState<ContainerItem[]>([])
  const [containersLoaded, setContainersLoaded] = useState(false)
  const [subtypes, setSubtypes] = useState<PartSubtype[]>([])
  const [subtypesLoaded, setSubtypesLoaded] = useState(false)
  const [clfNodes, setClfNodes] = useState<ClassificationNode[]>([])
  const [clfNodesLoaded, setClfNodesLoaded] = useState(false)

  useEffect(() => {
    fetchContainers()
      .then((resp) => {
        // Nur Product-Container anzeigen (PDMLinkProduct)
        const products = resp.containers.filter(
          (c) => c.containerType === 'Product' || c.containerType === 'PDMLinkProduct'
        )
        setContainers(products)
        setContainersLoaded(true)
        if (products.length > 0) {
          setForm((prev) => prev.ContainerBinding ? prev : { ...prev, ContainerBinding: products[0].odataBinding })
        }
      })
      .catch(() => { setContainersLoaded(true) })

    fetchPartSubtypes()
      .then((resp) => {
        setSubtypes(resp.subtypes)
        setSubtypesLoaded(true)
        // Default: BALMECHATRONICPART (= Component) wie im Windchill UI
        const hasMecha = resp.subtypes.some((s) => s.odataType === DEFAULT_TYPE)
        if (hasMecha) {
          setForm((prev) => prev.TypeId === DEFAULT_TYPE ? prev : {
            ...prev,
            TypeId: DEFAULT_TYPE,
            Classification: TYPE_CLASSIFICATION_MAP[DEFAULT_TYPE] || prev.Classification,
          })
        } else if (resp.subtypes.length > 0) {
          setForm((prev) => prev.TypeId ? prev : { ...prev, TypeId: resp.subtypes[0].odataType })
        }
      })
      .catch(() => { setSubtypesLoaded(true) })

    fetchClassificationNodes()
      .then((resp) => {
        setClfNodes(resp.nodes)
        setClfNodesLoaded(true)
      })
      .catch(() => { setClfNodesLoaded(true) })
  }, [])

  const set = useCallback(
    (key: keyof FormState, val: string) =>
      setForm((prev) => {
        const next = { ...prev, [key]: val }
        // Wenn der Subtype gewechselt wird, Classification automatisch anpassen
        if (key === 'TypeId') {
          const defaultClf = TYPE_CLASSIFICATION_MAP[val] || ''
          if (defaultClf) {
            next.Classification = defaultClf
          }
        }
        return next
      }),
    [],
  )

  // Welche Felder gehören aktuell zum gewählten Subtyp?
  const subtypeSpec = useMemo(() => getSubtypeSpec(form.TypeId), [form.TypeId])

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()
      if (!form.Name.trim() || !form.ContainerBinding) return

      // Prüfen, dass alle für diesen Subtyp erforderlichen Felder ausgefüllt sind
      const missingRequired: FieldKey[] = (Object.keys(form) as Array<keyof FormState>)
        .filter((k): k is FieldKey => k !== 'TypeId' && k !== 'ContainerBinding')
        .filter((k) => isRequired(subtypeSpec, k) && !form[k].trim())
      if (missingRequired.length > 0) {
        setError(`Required fields missing: ${missingRequired.join(', ')}`)
        return
      }

      setBusy(true)
      setError('')
      setSuccess('')

      const attrs: Record<string, string> = {}
      for (const [k, v] of Object.entries(form)) {
        if (k === 'ContainerBinding') continue
        // TypeId immer mitschicken (Soft-Type ist fixe Pflicht)
        if (k === 'TypeId') {
          const trimmed = v.trim()
          if (trimmed) attrs[k] = trimmed
          continue
        }
        // Felder, die für den aktuellen Subtyp ausgeblendet sind, NICHT senden.
        if (!isVisible(subtypeSpec, k as FieldKey)) continue
        const trimmed = v.trim()
        if (trimmed) attrs[k] = trimmed
      }
      if (form.ContainerBinding) {
        attrs['Context@odata.bind'] = form.ContainerBinding
      }

      try {
        const resp = await createObject('part', attrs)
        setSuccess(resp.message || `Part '${resp.number}' created`)
        setTimeout(() => {
          navigate(`/detail/part/${encodeURIComponent(resp.number)}`)
        }, 1200)
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err)
        if (msg.includes('403') || msg.toLowerCase().includes('secured action') || msg.toLowerCase().includes('authorization')) {
          const typeName = TYPE_DISPLAY_NAMES[form.TypeId] || form.TypeId
          const containerName = containers.find((c) => c.odataBinding === form.ContainerBinding)?.name || form.ContainerBinding
          setError(`No permission: type "${typeName}" cannot be created in container "${containerName}". Please choose a different type or container.`)
        } else {
          setError(msg)
        }
      } finally {
        setBusy(false)
      }
    },
    [form, navigate],
  )

  const canSubmit = !busy && !!form.Name.trim() && !!form.ContainerBinding && !!form.TypeId

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-lg font-semibold text-slate-800">Create new part</h1>
        <button
          onClick={() => navigate(-1)}
          className="text-xs text-slate-400 hover:text-slate-600 transition-colors"
        >
          ← Back
        </button>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded shadow-sm border border-slate-200 p-5 space-y-5">

        {/* ── Identity ─────────────────────────────────────── */}
        <Section title="Identity">

          {/* Container / Product */}
          {containers.length > 0 ? (
            <Field label="Product / Container" required>
              <ContainerPicker
                containers={containers}
                value={form.ContainerBinding}
                onChange={(v) => set('ContainerBinding', v)}
              />
            </Field>
          ) : containersLoaded ? (
            <div className="bg-amber-50 border border-amber-200 text-amber-700 text-sm rounded p-3">
              No containers found. Please check the Windchill connection.
            </div>
          ) : (
            <Field label="Product / Container" required>
              <select disabled className="input opacity-50">
                <option>Loading…</option>
              </select>
            </Field>
          )}

          {/* Part Type (Soft Type) */}
          {subtypes.length > 0 ? (
            <Field label="Type" required>
              <select
                value={form.TypeId}
                onChange={(e) => set('TypeId', e.target.value)}
                className="input"
              >
                {subtypes.map((st) => (
                  <option key={st.odataType} value={st.odataType}>
                    {TYPE_DISPLAY_NAMES[st.odataType] || st.name}
                  </option>
                ))}
              </select>
            </Field>
          ) : subtypesLoaded ? (
            <div className="bg-amber-50 border border-amber-200 text-amber-700 text-sm rounded p-3">
              No part subtypes found.
            </div>
          ) : (
            <Field label="Type" required>
              <select disabled className="input opacity-50">
                <option>Loading…</option>
              </select>
            </Field>
          )}

          {/* Number */}
          {isVisible(subtypeSpec, 'Number') && (
            <Field label="Number" required={isRequired(subtypeSpec, 'Number')}>
              <input
                value={form.Number}
                onChange={(e) => set('Number', e.target.value)}
                placeholder="(Generated)"
                className="input"
              />
            </Field>
          )}

          {/* Name */}
          {isVisible(subtypeSpec, 'Name') && (
            <Field label="Name" required={isRequired(subtypeSpec, 'Name')}>
              <input
                value={form.Name}
                onChange={(e) => set('Name', e.target.value)}
                className="input"
              />
            </Field>
          )}

          {/* Description */}
          {isVisible(subtypeSpec, 'Description') && (
            <Field label="Description" required={isRequired(subtypeSpec, 'Description')}>
              <textarea
                value={form.Description}
                onChange={(e) => set('Description', e.target.value)}
                rows={2}
                className="input resize-y"
              />
            </Field>
          )}

          {/* Source */}
          {isVisible(subtypeSpec, 'Source') && (
            <Field label="Source" required={isRequired(subtypeSpec, 'Source')}>
              <ToggleGroup
                options={SOURCES}
                value={form.Source}
                onChange={(v) => set('Source', v)}
              />
            </Field>
          )}

          {/* Associated Product Family */}
          {isVisible(subtypeSpec, 'ProductFamily') && (
            <Field label="Associated Product Family" required={isRequired(subtypeSpec, 'ProductFamily')}>
              <select
                value={form.ProductFamily}
                onChange={(e) => set('ProductFamily', e.target.value)}
                className="input"
              >
                {PRODUCT_FAMILIES.map((pf) => (
                  <option key={pf} value={pf}>{pf || '—'}</option>
                ))}
              </select>
            </Field>
          )}

          {/* View */}
          {isVisible(subtypeSpec, 'View') && (
            <Field label="View" required={isRequired(subtypeSpec, 'View')}>
              <select
                value={form.View}
                onChange={(e) => set('View', e.target.value)}
                className="input"
              >
                {VIEWS.map((v) => (
                  <option key={v.value} value={v.value}>{v.label}</option>
                ))}
              </select>
            </Field>
          )}

          {/* Assembly Mode */}
          {isVisible(subtypeSpec, 'AssemblyMode') && (
            <Field label="Assembly Mode" required={isRequired(subtypeSpec, 'AssemblyMode')}>
              <ToggleGroup
                options={ASSEMBLY_MODES}
                value={form.AssemblyMode}
                onChange={(v) => set('AssemblyMode', v)}
              />
            </Field>
          )}

          {/* Gathering Part */}
          {isVisible(subtypeSpec, 'GatheringPart') && (
            <Field label="Gathering Part" required={isRequired(subtypeSpec, 'GatheringPart')}>
              <ToggleGroup
                options={[{ value: 'no', label: 'No' }, { value: 'yes', label: 'Yes' }]}
                value={form.GatheringPart}
                onChange={(v) => set('GatheringPart', v)}
              />
            </Field>
          )}

          {/* Default Unit */}
          {isVisible(subtypeSpec, 'DefaultUnit') && (
            <Field label="Default Unit" required={isRequired(subtypeSpec, 'DefaultUnit')}>
              <select
                value={form.DefaultUnit}
                onChange={(e) => set('DefaultUnit', e.target.value)}
                className="input"
              >
                {UNITS.map((u) => (
                  <option key={u.value} value={u.value}>{u.label}</option>
                ))}
              </select>
            </Field>
          )}

          {/* Configurable Module */}
          {isVisible(subtypeSpec, 'ConfigurableModule') && (
            <Field label="Configurable Module" required={isRequired(subtypeSpec, 'ConfigurableModule')}>
              <ToggleGroup
                options={[{ value: 'no', label: 'No' }, { value: 'yes', label: 'Yes' }]}
                value={form.ConfigurableModule}
                onChange={(v) => set('ConfigurableModule', v)}
              />
            </Field>
          )}

          {/* Classification — automatisch vom Type bestimmt */}
          {isVisible(subtypeSpec, 'Classification') && (
            <Field label="Classification" required={isRequired(subtypeSpec, 'Classification')}>
              <div className="input bg-slate-50 text-slate-600 cursor-default flex items-center justify-between">
                <span>{form.Classification
                  ? (clfNodes.find((n) => n.internalName === form.Classification)?.displayName || form.Classification)
                  : '—'}</span>
                <span className="text-xs text-slate-400">determined automatically by type</span>
              </div>
            </Field>
          )}
        </Section>

        {/* ── Submit ───────────────────────────────────────── */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={!canSubmit}
            className="w-full px-4 py-2.5 text-sm font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            {busy ? 'Creating…' : 'Create part'}
          </button>
        </div>

        {/* Feedback */}
        {success && (
          <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm rounded p-3">
            {success}
          </div>
        )}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
            {error}
          </div>
        )}
      </form>
    </div>
  )
}

/* ── Helper Components ────────────────────────────────────── */

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <fieldset className="space-y-4">
      <legend className="text-sm font-semibold text-slate-500 uppercase tracking-wide border-b border-slate-200 pb-1 w-full">
        {title}
      </legend>
      {children}
    </fieldset>
  )
}

function Field({ label, required, children }: { label: string; required?: boolean; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {label}{required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      {children}
    </div>
  )
}

function ToggleGroup({ options, value, onChange }: {
  options: { value: string; label: string }[]
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div className="flex gap-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={`flex-1 px-3 py-2 text-sm rounded border transition-colors ${
            value === opt.value
              ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
              : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}

function ClassificationPicker({ nodes, loaded, value, onChange }: {
  nodes: ClassificationNode[]
  loaded: boolean
  value: string
  onChange: (v: string) => void
}) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const wrapperRef = useRef<HTMLDivElement>(null)
  const searchRef = useRef<HTMLInputElement>(null)

  // Close on outside click
  useEffect(() => {
    if (!open) return
    const handler = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  // Focus search when opened
  useEffect(() => {
    if (open) searchRef.current?.focus()
  }, [open])

  // Wenn API Ergebnisse liefert, nutze diese (flat list mit InternalName).
  // Sonst Fallback auf hardcoded CLASSIFICATIONS (tree mit DisplayName).
  const useApi = loaded && nodes.length > 0

  const lowerSearch = search.toLowerCase()

  // Hardcoded tree filter (mit Eltern-Kontext)
  const filteredTree = useMemo(() => {
    if (useApi) return []
    if (!lowerSearch) return CLASSIFICATIONS

    const matchingIndices = new Set<number>()
    CLASSIFICATIONS.forEach((entry, i) => {
      if (!entry.isGroup && entry.name.toLowerCase().includes(lowerSearch)) {
        matchingIndices.add(i)
        let currentDepth = entry.depth
        for (let j = i - 1; j >= 0; j--) {
          if (CLASSIFICATIONS[j].depth < currentDepth && CLASSIFICATIONS[j].isGroup) {
            matchingIndices.add(j)
            currentDepth = CLASSIFICATIONS[j].depth
            if (currentDepth === 0) break
          }
        }
      }
    })

    return CLASSIFICATIONS.filter((_, i) => matchingIndices.has(i))
  }, [lowerSearch, useApi])

  // API-basierter flat filter
  const filteredApi = useMemo(() => {
    if (!useApi) return []
    if (!lowerSearch) return nodes
    return nodes.filter((n) =>
      n.displayName.toLowerCase().includes(lowerSearch) || n.internalName.toLowerCase().includes(lowerSearch)
    )
  }, [nodes, lowerSearch, useApi])

  // Anzeigename fuer den ausgewaehlten Wert
  const selectedDisplay = useApi
    ? (nodes.find((n) => n.internalName === value)?.displayName || value)
    : value

  const handleSelect = (name: string) => {
    onChange(name)
    setOpen(false)
    setSearch('')
  }

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation()
    onChange('')
    setSearch('')
  }

  if (!loaded) {
    return (
      <select disabled className="input opacity-50">
        <option>Loading classifications…</option>
      </select>
    )
  }

  return (
    <div ref={wrapperRef} className="relative">
      {/* Trigger button */}
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={`input w-full text-left flex items-center justify-between ${
          !value ? 'text-slate-400' : 'text-slate-800'
        }`}
      >
        <span className="truncate">{value ? selectedDisplay : 'Select classification…'}</span>
        <span className="flex items-center gap-1 ml-2 shrink-0">
          {value && (
            <span
              onClick={handleClear}
              className="text-slate-400 hover:text-red-500 cursor-pointer text-base leading-none"
              title="Reset"
            >×</span>
          )}
          <svg className={`w-4 h-4 text-slate-400 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </span>
      </button>

      {/* Dropdown panel */}
      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-slate-200 rounded shadow-lg">
          {/* Search */}
          <div className="p-2 border-b border-slate-100">
            <input
              ref={searchRef}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search…"
              className="w-full text-sm px-2.5 py-1.5 border border-slate-200 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>

          {/* Tree / flat list */}
          <div className="max-h-64 overflow-y-auto py-1">
            {useApi ? (
              /* ── API-basierte flat list (InternalName) ── */
              filteredApi.length === 0 ? (
                <div className="px-3 py-2 text-sm text-slate-400">Keine Treffer</div>
              ) : (
                filteredApi.map((node) => {
                  const selected = value === node.internalName
                  return (
                    <button
                      key={node.internalName}
                      type="button"
                      onClick={() => handleSelect(node.internalName)}
                      className={`w-full text-left px-3 py-1.5 text-sm transition-colors ${
                        selected
                          ? 'bg-indigo-50 text-indigo-700 font-medium'
                          : 'text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      {node.displayName}
                      {node.displayName !== node.internalName && (
                        <span className="text-xs text-slate-400 ml-1">({node.internalName})</span>
                      )}
                    </button>
                  )
                })
              )
            ) : (
              /* ── Hardcoded tree (DisplayName) ── */
              filteredTree.length === 0 ? (
                <div className="px-3 py-2 text-sm text-slate-400">Keine Treffer</div>
              ) : (
                filteredTree.map((entry) => {
                  if (entry.isGroup) {
                    return (
                      <div
                        key={`g-${entry.name}`}
                        className="px-3 py-1 text-xs font-semibold text-slate-400 uppercase tracking-wide select-none"
                        style={{ paddingLeft: `${12 + entry.depth * 16}px` }}
                      >
                        {entry.name}
                      </div>
                    )
                  }
                  const selected = value === entry.name
                  return (
                    <button
                      key={entry.name}
                      type="button"
                      onClick={() => handleSelect(entry.name)}
                      className={`w-full text-left px-3 py-1.5 text-sm transition-colors ${
                        selected
                          ? 'bg-indigo-50 text-indigo-700 font-medium'
                          : 'text-slate-700 hover:bg-slate-50'
                      }`}
                      style={{ paddingLeft: `${12 + entry.depth * 16}px` }}
                    >
                      {entry.name}
                    </button>
                  )
                })
              )
            )}
          </div>
          <div className="px-3 py-1.5 border-t border-slate-100 text-xs text-slate-400">
            {useApi
              ? `${filteredApi.length} von ${nodes.length} (API)`
              : `${filteredTree.filter((e) => !e.isGroup).length} von ${CLASSIFICATIONS.filter((e) => !e.isGroup).length} (Fallback)`
            }
          </div>
        </div>
      )}
    </div>
  )
}

function ContainerPicker({ containers, value, onChange }: {
  containers: ContainerItem[]
  value: string
  onChange: (v: string) => void
}) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const wrapperRef = useRef<HTMLDivElement>(null)
  const searchRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!open) return
    const handler = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  useEffect(() => {
    if (open) searchRef.current?.focus()
  }, [open])

  const filtered = useMemo(() => {
    if (!search.trim()) return containers
    const q = search.toLowerCase()
    return containers.filter((c) =>
      c.name.toLowerCase().includes(q) || c.containerType.toLowerCase().includes(q)
    )
  }, [containers, search])

  const selectedName = containers.find((c) => c.odataBinding === value)?.name || ''

  return (
    <div ref={wrapperRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={`input w-full text-left flex items-center justify-between ${
          !value ? 'text-slate-400' : 'text-slate-800'
        }`}
      >
        <span className="truncate">{selectedName || 'Select container…'}</span>
        <svg className={`w-4 h-4 text-slate-400 transition-transform shrink-0 ${open ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-slate-200 rounded shadow-lg">
          <div className="p-2 border-b border-slate-100">
            <input
              ref={searchRef}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search container…"
              className="w-full text-sm px-2.5 py-1.5 border border-slate-200 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>
          <div className="max-h-64 overflow-y-auto py-1">
            {filtered.length === 0 ? (
              <div className="px-3 py-2 text-sm text-slate-400">Keine Treffer</div>
            ) : (
              filtered.map((c) => {
                const selected = value === c.odataBinding
                return (
                  <button
                    key={c.containerId}
                    type="button"
                    onClick={() => { onChange(c.odataBinding); setOpen(false); setSearch('') }}
                    className={`w-full text-left px-3 py-1.5 text-sm transition-colors ${
                      selected
                        ? 'bg-indigo-50 text-indigo-700 font-medium'
                        : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {c.name} <span className="text-xs text-slate-400">({c.containerType})</span>
                  </button>
                )
              })
            )}
          </div>
          <div className="px-3 py-1.5 border-t border-slate-100 text-xs text-slate-400">
            {filtered.length} von {containers.length}
          </div>
        </div>
      )}
    </div>
  )
}