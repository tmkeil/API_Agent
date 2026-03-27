import { useEffect, useState, type FormEvent } from 'react'

export type SearchMode = 'auto' | 'number' | 'keyword'

interface Props {
  onSearch: (query: string, mode: SearchMode) => void
  loading?: boolean
  placeholder?: string
  initialQuery?: string
}

export default function SearchBar({ onSearch, loading, placeholder, initialQuery }: Props) {
  const [query, setQuery] = useState(initialQuery || '')
  const [mode, setMode] = useState<SearchMode>('auto')

  // Sync with external initialQuery changes (e.g. from URL params)
  useEffect(() => {
    if (initialQuery !== undefined) setQuery(initialQuery)
  }, [initialQuery])

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const q = query.trim()
    if (q) onSearch(q, mode)
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-center">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder || "Produktnummer eingeben, z.B. S2200287364"}
        aria-label="Suchbegriff eingeben"
        className="flex-1 border border-slate-300 rounded px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 placeholder:text-slate-400"
      />

      {/* Mode toggle */}
      <div className="flex rounded border border-slate-300 overflow-hidden text-xs">
        {([['auto', 'Auto'], ['number', 'Nummer'], ['keyword', 'Keyword']] as const).map(([m, label]) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            className={`px-2.5 py-2 transition-colors ${
              mode === m
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-slate-500 hover:bg-slate-50'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <button
        type="submit"
        disabled={!query.trim()}
        className="bg-indigo-600 text-white px-5 py-2 rounded text-sm font-medium hover:bg-indigo-700 disabled:opacity-40 transition-colors"
      >
        {loading ? 'Suche…' : 'Suchen'}
      </button>
    </form>
  )
}