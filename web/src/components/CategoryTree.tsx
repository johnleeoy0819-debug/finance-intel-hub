import { useState } from 'react'
import { ChevronRight, ChevronDown } from 'lucide-react'
import type { Category } from '../types'

interface Props {
  categories: Category[]
  selectedId: number | null
  onSelect: (id: number | null) => void
}

export default function CategoryTree({ categories, selectedId, onSelect }: Props) {
  const [expanded, setExpanded] = useState<Set<number>>(new Set())

  const roots = categories.filter((c) => !c.parent_id)
  const children = (parentId: number) => categories.filter((c) => c.parent_id === parentId)

  const toggle = (id: number) => {
    const next = new Set(expanded)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setExpanded(next)
  }

  return (
    <div className="space-y-1">
      {roots.map((root) => (
        <div key={root.id}>
          <button
            onClick={() => toggle(root.id)}
            className="flex items-center gap-1 w-full text-left font-medium py-1 hover:text-primary-600"
          >
            {expanded.has(root.id) ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            {root.name}
          </button>
          {expanded.has(root.id) && (
            <div className="ml-5 space-y-1">
              {children(root.id).map((child) => (
                <button
                  key={child.id}
                  onClick={() => onSelect(child.id === selectedId ? null : child.id)}
                  className={`block w-full text-left text-sm py-0.5 px-2 rounded ${
                    child.id === selectedId ? 'bg-primary-100 text-primary-700' : 'hover:bg-gray-100'
                  }`}
                >
                  {child.name}
                </button>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
