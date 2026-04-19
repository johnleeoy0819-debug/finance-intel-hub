import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Play, Trash2 } from 'lucide-react'
import { sourcesApi } from '../api/client'
import type { Source } from '../types'

export default function Sources() {
  const [sources, setSources] = useState<Source[]>([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', url: '', driver: 'firecrawl', schedule: '0 */2 * * *' })

  useEffect(() => { sourcesApi.list().then(setSources) }, [])

  const handleCreate = async () => {
    const created = await sourcesApi.create(form)
    setSources([...sources, created])
    setShowForm(false)
    setForm({ name: '', url: '', driver: 'firecrawl', schedule: '0 */2 * * *' })
  }

  const handleDelete = async (id: number) => {
    await sourcesApi.delete(id)
    setSources(sources.filter((s) => s.id !== id))
  }

  const handleTrigger = async (id: number) => {
    const result = await sourcesApi.trigger(id)
    alert(`采集完成，新增 ${result.article_ids.length} 篇文章`)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold">FinanceIntel Hub</Link>
        <nav className="flex gap-4 text-sm">
          <Link to="/" className="text-gray-600 hover:text-primary-600">仪表盘</Link>
          <Link to="/library" className="text-gray-600 hover:text-primary-600">知识库</Link>
          <Link to="/upload" className="text-gray-600 hover:text-primary-600">上传</Link>
          <Link to="/sources" className="text-primary-600 font-medium">数据源</Link>
        </nav>
      </header>

      <main className="max-w-4xl mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold">数据源管理</h2>
          <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
            <Plus className="w-4 h-4" /> 新增数据源
          </button>
        </div>

        {showForm && (
          <div className="bg-white rounded-lg shadow p-4 mb-6 space-y-3">
            <input placeholder="名称（如：新浪财经）" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full px-3 py-2 border rounded-lg" />
            <input placeholder="URL" value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} className="w-full px-3 py-2 border rounded-lg" />
            <input placeholder="Cron 表达式" value={form.schedule} onChange={(e) => setForm({ ...form, schedule: e.target.value })} className="w-full px-3 py-2 border rounded-lg" />
            <div className="flex gap-2">
              <button onClick={handleCreate} className="px-4 py-2 bg-primary-600 text-white rounded-lg">保存</button>
              <button onClick={() => setShowForm(false)} className="px-4 py-2 border rounded-lg">取消</button>
            </div>
          </div>
        )}

        <div className="space-y-3">
          {sources.map((source) => (
            <div key={source.id} className="bg-white rounded-lg shadow p-4 flex items-center justify-between">
              <div>
                <div className="font-medium">{source.name}</div>
                <div className="text-sm text-gray-500">{source.url} · {source.driver} · {source.schedule}</div>
                <div className="text-xs text-gray-400">上次采集: {source.last_crawled_at ? new Date(source.last_crawled_at).toLocaleString() : '从未'}</div>
              </div>
              <div className="flex gap-2">
                <button onClick={() => handleTrigger(source.id)} className="p-2 text-primary-600 hover:bg-primary-50 rounded"><Play className="w-4 h-4" /></button>
                <button onClick={() => handleDelete(source.id)} className="p-2 text-red-600 hover:bg-red-50 rounded"><Trash2 className="w-4 h-4" /></button>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
