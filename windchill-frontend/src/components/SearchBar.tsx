import { useEffect, useState, type FormEvent } from 'react'

interface Props {
  onSearch: (query: string) => void
  loading?: boolean
  placeholder?: string
  initialQuery?: string
}

/**
 * Quick search field. Always performs a keyword-style search (Number OR Name),
 * with shell-style wildcards (`*`) supported on either field.
 */
export default function SearchBar({ onSearch, loading, placeholder, initialQuery }: Props) {
  const [query, setQuery] = useState(initialQuery || '')

  // Sync with external initialQuery changes (e.g. from URL params)
  useEffect(() => {
    if (initialQuery !== undefined) setQuery(initialQuery)
  }, [initialQuery])

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const q = query.trim()
    if (q) onSearch(q)
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-center">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder || 'Search — number, name or wildcard (e.g. S2200*, *287364, BES* CI*)'}
        aria-label="Search term"
        className="flex-1 border border-slate-300 rounded px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 placeholder:text-slate-400"
      />

      <button
        type="submit"
        disabled={!query.trim()}
        className="bg-indigo-600 text-white px-5 py-2 rounded text-sm font-medium hover:bg-indigo-700 disabled:opacity-40 transition-colors"
      >
        {loading ? 'Searching…' : 'Search'}
      </button>
    </form>
  )
}