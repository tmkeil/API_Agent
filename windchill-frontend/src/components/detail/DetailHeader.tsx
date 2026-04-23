import type { ObjectDetail } from '../../api/types'
import { typeLabel } from '../../utils/labels'

interface Props {
  detail: ObjectDetail
  onBack: () => void
}

export default function DetailHeader({ detail, onBack }: Props) {
  const typeBadge = typeLabel(detail.objectType, detail.subType)

  return (
    <div className="flex items-start justify-between">
      <div className="min-w-0">
        <div className="flex items-center gap-3 mb-1">
          <button
            onClick={onBack}
            className="text-slate-400 hover:text-slate-600 transition-colors shrink-0"
            title="Back to search"
            aria-label="Back to search"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 shrink-0">
            {typeBadge}
          </span>
          <h1 className="text-lg font-semibold text-slate-800 truncate">
            {detail.number}
          </h1>
          <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-500">
            {detail.state || '—'}
          </span>
        </div>
        <p className="text-sm text-slate-500 ml-8">
          {detail.name || '—'}
          <span className="mx-2 text-slate-300">|</span>
          Version {detail.version || '—'}.{detail.iteration || '—'}
          {detail.context && (
            <>
              <span className="mx-2 text-slate-300">|</span>
              {detail.context}
            </>
          )}
        </p>
      </div>
    </div>
  )
}
