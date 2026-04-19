import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useStore } from '../store'
import { articlesApi } from '../api/client'
import ArticleCard from '../components/ArticleCard'
import SearchBar from '../components/SearchBar'
import CategoryTree from '../components/CategoryTree'

export default function Library() {
  const { articles, articleTotal, setArticles, selectedCategory, setSelectedCategory, categories, setCategories } = useStore()
  const [page, setPage] = useState(0)
  const limit = 20

  useEffect(() => {
    // Load categories from API (mock for now)
    setCategories([
      { id: 1, name: '宏观经济', slug: 'macro', parent_id: undefined, sort_order: 0 },
      { id: 2, name: '货币政策', slug: 'monetary', parent_id: 1, sort_order: 0 },
      { id: 3, name: '财政政策', slug: 'fiscal', parent_id: 1, sort_order: 1 },
      { id: 4, name: '金融市场', slug: 'finance', parent_id: undefined, sort_order: 1 },
      { id: 5, name: '股票市场', slug: 'stock', parent_id: 4, sort_order: 0 },
      { id: 6, name: '债券市场', slug: 'bond', parent_id: 4, sort_order: 1 },
      { id: 7, name: '行业分析', slug: 'industry', parent_id: undefined, sort_order: 2 },
      { id: 8, name: '公司研究', slug: 'company', parent_id: undefined, sort_order: 3 },
      { id: 9, name: '监管政策', slug: 'regulation', parent_id: undefined, sort_order: 4 },
      { id: 10, name: '商业模型', slug: 'business', parent_id: undefined, sort_order: 5 },
    ])

    articlesApi.list({ category_id: selectedCategory || undefined, limit, offset: page * limit })
      .then((r) => setArticles(r.items, r.total))
  }, [selectedCategory, page, setArticles, setCategories])

  const handleSearch = (q: string) => {
    // TODO: implement search
    console.log('search:', q)
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
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">全部文章 ({articleTotal})</h2>
          </div>
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
        </div>
      </main>
    </div>
  )
}
