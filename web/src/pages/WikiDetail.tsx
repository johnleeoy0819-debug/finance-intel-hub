import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, BookOpen, Calendar } from 'lucide-react'
import { wikiApi } from '../api/client'
import Layout from '../components/Layout'
import WikiMarkdown from '../components/WikiMarkdown'
import type { WikiPage } from '../types'

export default function WikiDetail() {
  const { slug } = useParams<{ slug: string }>()
  const [page, setPage] = useState<WikiPage | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!slug) return
    setLoading(true)
    setError(null)
    wikiApi.get(slug)
      .then(setPage)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [slug])

  if (error) {
    return (
      <Layout>
        <div className="max-w-3xl mx-auto p-6">
          <div className="bg-red-50 text-red-700 p-4 rounded-lg text-sm">{error}</div>
        </div>
      </Layout>
    )
  }

  if (loading || !page) {
    return (
      <Layout>
        <div className="max-w-3xl mx-auto p-6 text-center text-gray-500">加载中...</div>
      </Layout>
    )
  }

  return (
    <Layout>
      <main className="max-w-3xl mx-auto p-6">
        <div className="mb-4">
          <Link to="/wiki" className="text-sm text-gray-500 hover:text-primary-600 flex items-center gap-1">
            <ArrowLeft className="w-4 h-4" /> 返回 Wiki 列表
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
            <BookOpen className="w-4 h-4" />
            <span>{page.topic}</span>
            <span>·</span>
            <Calendar className="w-3 h-3" />
            <span>{page.compiled_at ? new Date(page.compiled_at).toLocaleDateString() : '未编译'}</span>
          </div>

          <WikiMarkdown content={page.content || ''} />
        </div>
      </main>
    </Layout>
  )
}
