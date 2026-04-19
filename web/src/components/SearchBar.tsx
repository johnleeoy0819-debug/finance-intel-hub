import { Search } from 'lucide-react'
import { useState } from 'react'

interface Props {
  onSearch: (q: string) => void
  placeholder?: string
}

export default function SearchBar({ onSearch, placeholder = '搜索文章、标签...' }: Props) {
  const [q, setQ] = useState('')

  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
      <input
        type="text"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && onSearch(q)}
        placeholder={placeholder}
        className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
      />
    </div>
  )
}
