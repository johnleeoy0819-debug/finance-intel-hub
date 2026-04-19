import { useEffect, useState } from 'react'
import { Plus, Trash2, ExternalLink } from 'lucide-react'
import { publicationsApi } from '../api/client'
import Layout from '../components/Layout'
import type { Publication } from '../types'

export default function Publications() {
  const [items, setItems] = useState<Publication[]>([])
  const [total, setTotal] = useState(0)
  const [q, setQ] = useState('')
  const [pubType, setPubType] = useState('')
  const [showImport, setShowImport] = useState(false)
  const [importUrl, setImportUrl] = useState('')
  const [error, setError] = useState<string | null>(null)

  const load = () => {
    setError(null)
    publicationsApi.list({ q: q || undefined, pub_type: pubType || undefined, limit: 50 })
      .then((r) => { setItems(r.items); setTotal(r.total) })
      .catch((err) => setError(err.message))
  }

  useEffect(() => { load() }, [q, pubType])  // eslint-disable-line react-hooks/exhaustive-deps

  const handleImport = async () => {
    setError(null)
    try {
      await publicationsApi.import(importUrl)
      setImportUrl('')
      setShowImport(false)
      load()
    } catch (err: any) {
      setError(err.message)
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await publicationsApi.delete(id)
      setItems(items.filter((p) => p.id !== id))
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <Layout>
      <main className="max-w-5xl mx-auto p-6">
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200">{error}</div>
        )}

        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold">文献管理 ({total})</h2>
          <button onClick={() => setShowImport(!showImport)} className="flex items-center gap-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
            <Plus className="w-4 h-4" /> 导入文献
          </button>
        </div>

        <div className="flex gap-3 mb-6">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="搜索标题、作者、摘要..."
            className="flex-1 px-3 py-2 border rounded-lg"
          />
          <select value={pubType} onChange={(e) => setPubType(e.target.value)} className="px-3 py-2 border rounded-lg">
            <option value="">全部类型</option>
            <option value="arxiv">arXiv</option>
            <option value="journal">期刊</option>
            <option value="book">书籍</option>
          </select>
        </div>

        {showImport && (
          <div className="bg-white rounded-lg shadow p-4 mb-6 space-y-3">
            <p className="text-sm text-gray-500">支持 arXiv URL 或 DOI</p>
            <input
              value={importUrl}
              onChange={(e) => setImportUrl(e.target.value)}
              placeholder="https://arxiv.org/abs/2401.00001 或 10.1234/example"
              className="w-full px-3 py-2 border rounded-lg"
            />
            <div className="flex gap-2">
              <button onClick={handleImport} className="px-4 py-2 bg-primary-600 text-white rounded-lg">导入</button>
              <button onClick={() => setShowImport(false)} className="px-4 py-2 border rounded-lg">取消</button>
            </div>
          </div>
        )}

        <div className="space-y-3">
          {items.map((pub) => (
            <div key={pub.id} className="bg-white rounded-lg shadow p-4 flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs px-2 py-0.5 bg-gray-100 rounded-full uppercase">{pub.pub_type}</span>
                  {pub.citation_count > 0 && (
                    <span className="text-xs text-gray-500">被引 {pub.citation_count} 次</span>
                  )}
                </div>
                <h3 className="font-medium truncate">{pub.title}</h3>
                <p className="text-sm text-gray-500 truncate">{pub.authors}</p>
                {pub.abstract && (
                  <p className="text-sm text-gray-400 mt-1 line-clamp-2">{pub.abstract.slice(0, 200)}...</p>
                )}
              </div>
              <div className="flex gap-2 shrink-0">
                {pub.url && (
                  <a href={pub.url} target="_blank" rel="noreferrer" className="p-2 text-gray-400 hover:text-primary-600">
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
                <button onClick={() => handleDelete(pub.id)} className="p-2 text-red-600 hover:bg-red-50 rounded">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </main>
    </Layout>
  )
}
