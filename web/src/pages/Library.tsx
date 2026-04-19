import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useStore } from '../store'
import { articlesApi } from '../api/client'
import ArticleCard from '../components/ArticleCard'
import SearchBar from '../components/SearchBar'
import CategoryTree from '../components/CategoryTree'

export default function Library() {
  const { articles, articleTotal, setArticles, selectedCategory, setSelectedCategory, categories } = useStore()
  const [page, setPage] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const limit = 20

  useEffect(() => {
    setError(null)
    setLoading(true)
    articlesApi.list({ category_id: selectedCategory || undefined, limit, offset: page * limit })
      .then((r) => setArticles(r.items, r.total))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [selectedCategory, page, setArticles])

  const handleSearch = (q: string) => {
    setError(null)
    setLoading(true)
    articlesApi.list({ tag: q, limit, offset: 0 })
      .then((r) => { setPage(0); setArticles(r.items, r.total) })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold">FinanceIntel Hub</Link>
        <div className="flex-1 max-w-md mx-6">
          <SearchBar onSearch={handleSearch} />
        </div>
        <nav className="flex gap-4 text-sm">
          <Link to="/" className="text-gray-600 hover:text-primary-600">仪表盘</Link>
          <Link to="/library" className="text-primary-600 font-medium">知识库</Link>
          <Link to="/upload" className="text-gray-600 hover:text-primary-600">上传</Link>
          <Link to="/sources" className="text-gray-600 hover:text-primary-600">数据源</Link>
        </nav>
      </header>

      <main className="max-w-6xl mx-auto p-6 flex gap-6">
        <aside className="w-56 shrink-0">
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold mb-3">分类</h3>
            <CategoryTree
              categories={categories}
              selectedId={selectedCategory}
              onSelect={setSelectedCategory}
            />
          </div>
        </aside>

        <div className="flex-1">
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200">
              {error}
            </div>
          )}

          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">全部文章 ({articleTotal})</h2>
          </div>

          {loading ? (
            <div className="py-10 text-center text-gray-500">加载中...</div>
          ) : (
            <>
              <div className="space-y-3">
                {articles.map((article) => (
                  <ArticleCard key={article.id} article={article} />
                ))}
              </div>
              {articleTotal > limit && (
                <div className="flex justify-center gap-2 mt-6">
                  <button
                    onClick={() => setPage((p) => Math.max(0, p - 1))}
                    disabled={page === 0}
                    className="px-3 py-1 border rounded hover:bg-gray-100 disabled:opacity-50"
                  >
                    上一页
                  </button>
                  <span className="px-3 py-1">{page + 1}</span>
                  <button
                    onClick={() => setPage((p) => p + 1)}
                    disabled={(page + 1) * limit >= articleTotal}
                    className="px-3 py-1 border rounded hover:bg-gray-100 disabled:opacity-50"
                  >
                    下一页
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  )
}
