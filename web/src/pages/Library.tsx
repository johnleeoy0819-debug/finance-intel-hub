import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useStore } from '../store'
import { articlesApi, searchApi } from '../api/client'
import ArticleCard from '../components/ArticleCard'
import SearchBar, { type SearchMode } from '../components/SearchBar'
import CategoryTree from '../components/CategoryTree'
import type { Article } from '../types'

interface SearchResult {
  article: Article
  score?: number
}

export default function Library() {
  const { articles, articleTotal, setArticles, selectedCategory, setSelectedCategory, categories } = useStore()
  const [page, setPage] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [, setSearchMode] = useState<SearchMode>('fulltext')
  const [searchResults, setSearchResults] = useState<SearchResult[] | null>(null)
  const limit = 20

  useEffect(() => {
    setError(null)
    setLoading(true)
    setSearchResults(null)
    articlesApi.list({ category_id: selectedCategory || undefined, limit, offset: page * limit })
      .then((r) => setArticles(r.items, r.total))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [selectedCategory, page, setArticles])

  const handleSearch = (q: string, mode: SearchMode) => {
    setError(null)
    setLoading(true)
    setSearchMode(mode)
    setPage(0)

    if (mode === 'fulltext') {
      searchApi.search(q)
        .then((r: any) => { setSearchResults(null); setArticles(r.items || [], r.items?.length || 0) })
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false))
    } else if (mode === 'semantic') {
      searchApi.semantic(q)
        .then((r: any) => {
          const items: SearchResult[] = (r.items || []).map((item: any) => ({
            article: item.article,
            score: item.score,
          }))
          setSearchResults(items)
          setArticles([], items.length)
        })
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false))
    } else {
      searchApi.hybrid(q)
        .then((r: any) => { setSearchResults(null); setArticles(r.items || [], r.items?.length || 0) })
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false))
    }
  }

  const displayItems = searchResults
    ? searchResults.map((r) => r.article)
    : articles

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold">FinanceIntel Hub</Link>
        <div className="flex-1 max-w-xl mx-6">
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
              onSelect={(id) => { setSelectedCategory(id); setSearchResults(null); setPage(0) }}
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
            <h2 className="text-lg font-semibold">
              {searchResults ? `语义搜索结果 (${articleTotal})` : `全部文章 (${articleTotal})`}
            </h2>
          </div>

          {loading ? (
            <div className="py-10 text-center text-gray-500">加载中...</div>
          ) : (
            <>
              <div className="space-y-3">
                {displayItems.map((article, idx) => (
                  <div key={article.id} className="relative">
                    {searchResults && searchResults[idx]?.score !== undefined && (
                      <div className="absolute right-2 top-2 text-xs text-gray-400 bg-white/80 px-1.5 py-0.5 rounded">
                        相似度: {searchResults[idx].score}
                      </div>
                    )}
                    <ArticleCard article={article} />
                  </div>
                ))}
              </div>
              {!searchResults && articleTotal > limit && (
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
