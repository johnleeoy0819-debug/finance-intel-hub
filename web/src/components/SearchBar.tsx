import { Search } from 'lucide-react'
import { useState } from 'react'

export type SearchMode = 'fulltext' | 'semantic' | 'hybrid'

interface Props {
  onSearch: (q: string, mode: SearchMode) => void
  placeholder?: string
}

export default function SearchBar({ onSearch, placeholder = '搜索文章、标签...' }: Props) {
  const [q, setQ] = useState('')
  const [mode, setMode] = useState<SearchMode>('fulltext')

  const handleSubmit = () => {
    if (q.trim()) onSearch(q.trim(), mode)
  }

  const modes: { key: SearchMode; label: string }[] = [
    { key: 'fulltext', label: '全文' },
    { key: 'semantic', label: '语义' },
    { key: 'hybrid', label: '混合' },
  ]

  return (
    <div className="flex items-center gap-2">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          placeholder={placeholder}
          className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>
      <div className="flex bg-gray-100 rounded-lg p-0.5 text-xs">
        {modes.map((m) => (
          <button
            key={m.key}
            onClick={() => { setMode(m.key); if (q.trim()) onSearch(q.trim(), m.key) }}
            className={`px-2 py-1.5 rounded-md transition ${
              mode === m.key ? 'bg-white shadow text-primary-700 font-medium' : 'text-gray-500'
            }`}
          >
            {m.label}
          </button>
        ))}
      </div>
    </div>
  )
}
