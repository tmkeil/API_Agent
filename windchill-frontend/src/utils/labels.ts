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

/** Get a human-readable label for a Windchill objectType. Falls back to the raw type string. */
export function typeLabel(raw: string): string {
  return TYPE_LABELS[raw] || raw
}
