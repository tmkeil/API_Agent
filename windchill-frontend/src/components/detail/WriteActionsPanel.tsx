import { useCallback, useState } from 'react'
import {
  addBomChild,
  checkinObject,
  checkoutObject,
  removeBomChild,
  reviseObject,
  setLifecycleState,
  updateAttributes,
} from '../../api/client'
import type { WriteResponse } from '../../api/types'

interface Props {
  typeKey: string
  code: string
  objectId?: string
  onSuccess?: () => void
}

type Action = 'checkout' | 'checkin' | 'state' | 'attributes' | 'addChild' | 'removeChild' | null

/**
 * Write-operations panel on the detail page.
 *
 * Provides buttons for checkout, checkin, set-state, and attribute-update.
 * Each opens an inline mini-form where needed.
 */
export default function WriteActionsPanel({ typeKey, code, objectId, onSuccess }: Props) {
  const [action, setAction] = useState<Action>(null)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<WriteResponse | null>(null)
  const [error, setError] = useState('')

  // Form state
  const [targetState, setTargetState] = useState('')
  const [stateComment, setStateComment] = useState('')
  const [attrKey, setAttrKey] = useState('')
  const [attrVal, setAttrVal] = useState('')
  const [childNumber, setChildNumber] = useState('')
  const [childQty, setChildQty] = useState('1')
  const [childUnit, setChildUnit] = useState('each')
  const [linkId, setLinkId] = useState('')

  const reset = useCallback(() => {
    setAction(null)
    setError('')
    setResult(null)
    setTargetState('')
    setStateComment('')
    setAttrKey('')
    setAttrVal('')
    setChildNumber('')
    setChildQty('1')
    setChildUnit('each')
    setLinkId('')
  }, [])

  const exec = useCallback(async (fn: () => Promise<WriteResponse>) => {
    setBusy(true)
    setError('')
    setResult(null)
    try {
      const resp = await fn()
      setResult(resp)
      onSuccess?.()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setBusy(false)
    }
  }, [onSuccess])

  const handleCheckout = () => exec(() => checkoutObject(typeKey, code, objectId))
  const handleCheckin = () => exec(() => checkinObject(typeKey, code, objectId))
  const handleSetState = () => {
    if (!targetState.trim()) return
    exec(() =>
      setLifecycleState(typeKey, code, {
        targetState: targetState.trim(),
        comment: stateComment.trim() || undefined,
      }, objectId),
    )
  }
  const handleUpdateAttrs = () => {
    if (!attrKey.trim()) return
    exec(() => updateAttributes(typeKey, code, { [attrKey.trim()]: attrVal }, objectId))
  }
  const handleRevise = () => exec(() => reviseObject(typeKey, code, objectId))
  const handleAddChild = () => {
    if (!childNumber.trim()) return
    exec(() =>
      addBomChild(code, {
        childPartNumber: childNumber.trim(),
        quantity: parseFloat(childQty) || 1,
        unit: childUnit.trim() || 'each',
      }),
    )
  }
  const handleRemoveChild = () => {
    if (!linkId.trim()) return
    exec(() => removeBomChild(linkId.trim()))
  }

  return (
    <div className="space-y-3">
      {/* Action buttons */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={handleCheckout}
          disabled={busy}
          className="px-3 py-1.5 text-xs font-medium rounded bg-amber-500 text-white hover:bg-amber-600 disabled:opacity-50 transition-colors"
        >
          Auschecken
        </button>
        <button
          onClick={handleCheckin}
          disabled={busy}
          className="px-3 py-1.5 text-xs font-medium rounded bg-emerald-500 text-white hover:bg-emerald-600 disabled:opacity-50 transition-colors"
        >
          Einchecken
        </button>
        <button
          onClick={() => setAction(action === 'state' ? null : 'state')}
          className={`px-3 py-1.5 text-xs font-medium rounded border transition-colors ${
            action === 'state'
              ? 'bg-indigo-600 text-white border-indigo-600'
              : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
          }`}
        >
          Status ändern
        </button>
        <button
          onClick={() => setAction(action === 'attributes' ? null : 'attributes')}
          className={`px-3 py-1.5 text-xs font-medium rounded border transition-colors ${
            action === 'attributes'
              ? 'bg-indigo-600 text-white border-indigo-600'
              : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
          }`}
        >
          Attribut ändern
        </button>
        <button
          onClick={handleRevise}
          disabled={busy}
          className="px-3 py-1.5 text-xs font-medium rounded bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 transition-colors"
        >
          Revisionieren
        </button>
        {typeKey === 'part' && (
          <>
            <button
              onClick={() => setAction(action === 'addChild' ? null : 'addChild')}
              className={`px-3 py-1.5 text-xs font-medium rounded border transition-colors ${
                action === 'addChild'
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
              }`}
            >
              + BOM Kind
            </button>
            <button
              onClick={() => setAction(action === 'removeChild' ? null : 'removeChild')}
              className={`px-3 py-1.5 text-xs font-medium rounded border transition-colors ${
                action === 'removeChild'
                  ? 'bg-red-600 text-white border-red-600'
                  : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
              }`}
            >
              − BOM Kind
            </button>
          </>
        )}
      </div>

      {/* Inline forms */}
      {action === 'state' && (
        <div className="flex items-end gap-2 bg-slate-50 rounded p-3 border border-slate-200">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-500">Zielstatus</label>
            <input
              value={targetState}
              onChange={(e) => setTargetState(e.target.value)}
              placeholder="z.B. RELEASED"
              className="px-2 py-1 text-sm border border-slate-300 rounded w-40 focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-500">Kommentar (optional)</label>
            <input
              value={stateComment}
              onChange={(e) => setStateComment(e.target.value)}
              placeholder="Kommentar"
              className="px-2 py-1 text-sm border border-slate-300 rounded w-48 focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>
          <button
            onClick={handleSetState}
            disabled={busy || !targetState.trim()}
            className="px-3 py-1.5 text-xs font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            Anwenden
          </button>
          <button onClick={reset} className="px-2 py-1.5 text-xs text-slate-400 hover:text-slate-600">
            Abbrechen
          </button>
        </div>
      )}

      {action === 'attributes' && (
        <div className="flex items-end gap-2 bg-slate-50 rounded p-3 border border-slate-200">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-500">Attribut-Name</label>
            <input
              value={attrKey}
              onChange={(e) => setAttrKey(e.target.value)}
              placeholder="z.B. Name"
              className="px-2 py-1 text-sm border border-slate-300 rounded w-40 focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-500">Neuer Wert</label>
            <input
              value={attrVal}
              onChange={(e) => setAttrVal(e.target.value)}
              placeholder="Wert"
              className="px-2 py-1 text-sm border border-slate-300 rounded w-48 focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>
          <button
            onClick={handleUpdateAttrs}
            disabled={busy || !attrKey.trim()}
            className="px-3 py-1.5 text-xs font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            Speichern
          </button>
          <button onClick={reset} className="px-2 py-1.5 text-xs text-slate-400 hover:text-slate-600">
            Abbrechen
          </button>
        </div>
      )}

      {action === 'addChild' && (
        <div className="flex items-end gap-2 bg-slate-50 rounded p-3 border border-slate-200">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-500">Kind-Teilenummer</label>
            <input
              value={childNumber}
              onChange={(e) => setChildNumber(e.target.value)}
              placeholder="z.B. 000001234"
              className="px-2 py-1 text-sm border border-slate-300 rounded w-40 focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-500">Menge</label>
            <input
              type="number"
              min="0"
              step="any"
              value={childQty}
              onChange={(e) => setChildQty(e.target.value)}
              className="px-2 py-1 text-sm border border-slate-300 rounded w-20 focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-500">Einheit</label>
            <input
              value={childUnit}
              onChange={(e) => setChildUnit(e.target.value)}
              className="px-2 py-1 text-sm border border-slate-300 rounded w-20 focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>
          <button
            onClick={handleAddChild}
            disabled={busy || !childNumber.trim()}
            className="px-3 py-1.5 text-xs font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            Hinzufügen
          </button>
          <button onClick={reset} className="px-2 py-1.5 text-xs text-slate-400 hover:text-slate-600">
            Abbrechen
          </button>
        </div>
      )}

      {action === 'removeChild' && (
        <div className="flex items-end gap-2 bg-slate-50 rounded p-3 border border-slate-200">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-500">UsageLink-ID</label>
            <input
              value={linkId}
              onChange={(e) => setLinkId(e.target.value)}
              placeholder="z.B. OR:wt.part.WTPartUsageLink:12345"
              className="px-2 py-1 text-sm border border-slate-300 rounded w-72 focus:outline-none focus:ring-1 focus:ring-indigo-400"
            />
          </div>
          <button
            onClick={handleRemoveChild}
            disabled={busy || !linkId.trim()}
            className="px-3 py-1.5 text-xs font-medium rounded bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 transition-colors"
          >
            Entfernen
          </button>
          <button onClick={reset} className="px-2 py-1.5 text-xs text-slate-400 hover:text-slate-600">
            Abbrechen
          </button>
        </div>
      )}

      {/* Result / Error feedback */}
      {busy && (
        <p className="text-xs text-slate-500 animate-pulse">Wird ausgeführt…</p>
      )}
      {result && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm rounded p-2">
          {result.message}
        </div>
      )}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-2">
          {error}
        </div>
      )}
    </div>
  )
}
