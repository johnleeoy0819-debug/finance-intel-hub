import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, FileText, List } from 'lucide-react'
import { wikiApi } from '../api/client'
import Layout from '../components/Layout'
import type { WikiPage } from '../types'

export default function WikiList() {
  const [pages, setPages] = useState<WikiPage[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    wikiApi.list()
      .then(setPages)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <Layout>
      <main className="max-w-4xl mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <BookOpen className="w-5 h-5" /> 知识 Wiki
          </h2>
          <div className="flex items-center gap-3">
            <Link
              to="/wiki/index"
              className="text-sm text-primary-600 hover:underline flex items-center gap-1"
            >
              <List className="w-4 h-4" /> 索引
            </Link>
            <span className="text-sm text-gray-500">{pages.length} 个主题</span>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200">
            {error}
          </div>
        )}

        {loading ? (
          <div className="py-10 text-center text-gray-500">加载中...</div>
        ) : pages.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 mb-2">暂无 Wiki 页面</p>
            <p className="text-sm text-gray-400">
              Wiki 页面由系统自动编译生成。当某个主题积累足够文章后，系统会自动生成综述。
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {pages.map((page) => (
              <Link
                key={page.id}
                to={`/wiki/${page.slug}`}
                className="block bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900 mb-1">{page.title}</h3>
                    <p className="text-sm text-gray-500">
                      主题: {page.topic} · 引用 {page.article_count} 篇文章
                    </p>
                  </div>
                  <span className="text-xs text-gray-400 shrink-0">
                    {page.updated_at ? new Date(page.updated_at).toLocaleDateString() : ''}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </Layout>
  )
}
