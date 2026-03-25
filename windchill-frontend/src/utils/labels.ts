/**
 * Shared constants and utility functions used across multiple components.
 * Centralised here to avoid duplication (DRY).
 */

// ── Windchill object type labels ────────────────────────────

/** Human-readable labels for Windchill objectType values. */
export const TYPE_LABELS: Record<string, string> = {
  WTPart: 'Part',
  WTDocument: 'Dokument',
  EPMDocument: 'CAD-Dokument',
  WTChangeOrder2: 'Change Notice',
  WTChangeRequest2: 'Change Request',
  WTChangeIssue: 'Problem Report',
}

/** Badge color styles for Windchill subtype (OData ObjectType).
 *  Covers WTPart subtypes, WTDocument subtypes, and EPMDocument subtypes.
 */
export const SUBTYPE_BADGE_STYLES: Record<string, string> = {
  // ── WTPart subtypes ──
  Product:                'bg-sky-50 text-sky-700 border-sky-200',
  Component:              'bg-slate-100 text-slate-600 border-slate-300',
  'Auxiliary Material':   'bg-amber-50 text-amber-700 border-amber-200',
  'Raw Material':         'bg-orange-50 text-orange-700 border-orange-200',
  Inseparable:            'bg-emerald-50 text-emerald-700 border-emerald-200',
  'Packing Material':     'bg-lime-50 text-lime-700 border-lime-200',
  'Package Material':     'bg-lime-50 text-lime-700 border-lime-200',
  Bulk:                   'bg-cyan-50 text-cyan-700 border-cyan-200',
  Separable:              'bg-teal-50 text-teal-700 border-teal-200',
  // ── WTDocument subtypes ──
  'Production Document':  'bg-amber-50 text-amber-700 border-amber-200',
  'Approval Document':    'bg-rose-50 text-rose-700 border-rose-200',
  'Specification':        'bg-blue-50 text-blue-700 border-blue-200',
  'Reference Document':   'bg-indigo-50 text-indigo-700 border-indigo-200',
  'Drawing':              'bg-purple-50 text-purple-700 border-purple-200',
  'Technical Document':   'bg-fuchsia-50 text-fuchsia-700 border-fuchsia-200',
  // ── EPMDocument subtypes ──
  'CAD Document':         'bg-violet-50 text-violet-700 border-violet-200',
  'CADDocument':          'bg-violet-50 text-violet-700 border-violet-200',
  // ── Fallback type-class badges ──
  Part:                   'bg-sky-50 text-sky-700 border-sky-200',
  Dokument:               'bg-amber-50 text-amber-700 border-amber-200',
  'CAD-Dokument':         'bg-violet-50 text-violet-700 border-violet-200',
}

/** Default badge style for unknown subtypes. */
const _DEFAULT_BADGE = 'bg-slate-100 text-slate-600 border-slate-300'

/** Get badge CSS classes for a subtype/type string. */
export function subtypeBadgeStyle(subType: string): string {
  return SUBTYPE_BADGE_STYLES[subType] || _DEFAULT_BADGE
}

/** Maps Windchill objectType → URL typeKey used for /detail/:typeKey/:code */
export const TYPE_KEY_MAP: Record<string, string> = {
  WTPart: 'part',
  WTDocument: 'document',
  EPMDocument: 'cad_document',
  WTChangeOrder2: 'change_notice',
  WTChangeRequest2: 'change_request',
  WTChangeIssue: 'problem_report',
}

/** Filter chip definitions for the search UI. */
export const TYPE_FILTERS: { key: string; label: string }[] = [
  { key: 'part', label: 'Parts' },
  { key: 'document', label: 'Dokumente' },
  { key: 'cad_document', label: 'CAD' },
  { key: 'change_notice', label: 'Change Notices' },
  { key: 'change_request', label: 'Change Requests' },
  { key: 'problem_report', label: 'Problem Reports' },
]

// ── Utility functions ───────────────────────────────────────

/** Format an ISO date string to dd.MM.yyyy (German locale). Returns '—' for empty/invalid input. */
export function formatDate(raw: string): string {
  if (!raw) return '—'
  try {
    const d = new Date(raw)
    if (isNaN(d.getTime())) return raw.substring(0, 10)
    return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
  } catch {
    return raw.substring(0, 10)
  }
}

/** Get a human-readable label for a Windchill objectType.
 *  If a subType (OData ObjectType like "Product", "Auxiliary Material") is provided,
 *  use it directly. Otherwise fall back to TYPE_LABELS or the raw string.
 */
export function typeLabel(objectType: string, subType?: string): string {
  if (subType) return subType
  return TYPE_LABELS[objectType] || objectType
}
