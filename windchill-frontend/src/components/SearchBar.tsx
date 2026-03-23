import { useState, type FormEvent } from 'react'

interface Props {
  onSearch: (query: string) => void
  loading?: boolean
  placeholder?: string
}

export default function SearchBar({ onSearch, loading, placeholder }: Props) {
  const [query, setQuery] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const q = query.trim()
    if (q) onSearch(q)
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder || "Produktnummer eingeben, z.B. S2200287364"}
        aria-label="Suchbegriff eingeben"
        className="flex-1 border border-slate-300 rounded px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 placeholder:text-slate-400"
      />
      <button
        type="submit"
        disabled={loading || !query.trim()}
        className="bg-indigo-600 text-white px-5 py-2 rounded text-sm font-medium hover:bg-indigo-700 disabled:opacity-40 transition-colors"
      >
        {loading ? 'Suche...' : 'Suchen'}
      </button>
    </form>
  )
}