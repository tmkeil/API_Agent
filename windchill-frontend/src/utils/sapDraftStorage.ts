/**
 * Persistent draft storage for the SAP preview table.
 *
 * Drafts let the user resume their edits across navigations, page reloads,
 * logouts and browser restarts. Storage uses ``localStorage`` and is keyed
 * per ``(system, username, partNumber)`` so that multiple users on the same
 * machine never see each other's drafts.
 *
 * The serialized draft is wrapped with a schema version so future column
 * changes can drop or migrate stale drafts safely. An LRU index keeps the
 * total number of drafts bounded.
 */

export interface SapPreviewDraftRow {
  [col: string]: string
}

export interface SapPreviewDraft {
  schemaVersion: 1
  partNumber: string
  /** ISO timestamp of the last save. */
  savedAt: string
  /** Column order at save time — used to detect incompatible drafts. */
  columns: string[]
  rows: SapPreviewDraftRow[]
}

const SCHEMA_VERSION = 1
const MAX_DRAFTS = 50
const KEY_PREFIX = 'sap-draft'
const INDEX_KEY = `${KEY_PREFIX}:index`

interface IndexEntry {
  key: string
  /** ms epoch — last accessed (load or save). */
  touchedAt: number
}

interface UserScope {
  system: string
  username: string
}

/* ── Key helpers ───────────────────────────────────────────── */

function _scopeKey(s: UserScope): string {
  // Encode to keep ':' a safe separator.
  const u = encodeURIComponent(s.username)
  const sys = encodeURIComponent(s.system)
  return `${sys}|${u}`
}

function _draftKey(s: UserScope, partNumber: string): string {
  return `${KEY_PREFIX}:${_scopeKey(s)}:${encodeURIComponent(partNumber)}`
}

/* ── Index ─────────────────────────────────────────────────── */

function _readIndex(): IndexEntry[] {
  try {
    const raw = localStorage.getItem(INDEX_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function _writeIndex(idx: IndexEntry[]): void {
  try {
    localStorage.setItem(INDEX_KEY, JSON.stringify(idx))
  } catch {
    /* ignore quota / private mode */
  }
}

function _touchIndex(key: string): void {
  const idx = _readIndex().filter((e) => e.key !== key)
  idx.unshift({ key, touchedAt: Date.now() })
  // LRU evict
  while (idx.length > MAX_DRAFTS) {
    const drop = idx.pop()
    if (drop) {
      try { localStorage.removeItem(drop.key) } catch { /* ignore */ }
    }
  }
  _writeIndex(idx)
}

function _removeFromIndex(key: string): void {
  const idx = _readIndex().filter((e) => e.key !== key)
  _writeIndex(idx)
}

/* ── Public API ────────────────────────────────────────────── */

/** Load a draft for the given user + part number. Returns ``null`` if none. */
export function loadDraft(scope: UserScope, partNumber: string): SapPreviewDraft | null {
  if (!scope.username || !partNumber) return null
  const key = _draftKey(scope, partNumber)
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return null
    const parsed = JSON.parse(raw) as SapPreviewDraft
    if (parsed?.schemaVersion !== SCHEMA_VERSION) {
      // Incompatible — drop silently.
      localStorage.removeItem(key)
      _removeFromIndex(key)
      return null
    }
    _touchIndex(key)
    return parsed
  } catch {
    return null
  }
}

/** Persist a draft (overwriting any previous). Best-effort — quota errors are swallowed. */
export function saveDraft(
  scope: UserScope,
  partNumber: string,
  columns: string[],
  rows: SapPreviewDraftRow[],
): SapPreviewDraft | null {
  if (!scope.username || !partNumber) return null
  const draft: SapPreviewDraft = {
    schemaVersion: SCHEMA_VERSION,
    partNumber,
    savedAt: new Date().toISOString(),
    columns: [...columns],
    rows: rows.map((r) => ({ ...r })),
  }
  const key = _draftKey(scope, partNumber)
  try {
    localStorage.setItem(key, JSON.stringify(draft))
    _touchIndex(key)
    return draft
  } catch {
    // Likely QuotaExceededError. Drop the oldest draft and retry once.
    const idx = _readIndex()
    const tail = idx.pop()
    if (tail) {
      try { localStorage.removeItem(tail.key) } catch { /* ignore */ }
      _writeIndex(idx)
      try {
        localStorage.setItem(key, JSON.stringify(draft))
        _touchIndex(key)
        return draft
      } catch {
        return null
      }
    }
    return null
  }
}

/** Delete the draft for the given user + part number, if any. */
export function deleteDraft(scope: UserScope, partNumber: string): void {
  if (!scope.username || !partNumber) return
  const key = _draftKey(scope, partNumber)
  try { localStorage.removeItem(key) } catch { /* ignore */ }
  _removeFromIndex(key)
}
