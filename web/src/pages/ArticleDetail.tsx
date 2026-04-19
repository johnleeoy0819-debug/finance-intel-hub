import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ThumbsUp, ThumbsDown } from 'lucide-react'
import { articlesApi } from '../api/client'
import type { Article } from '../types'

export default function ArticleDetail() {
  const { id } = useParams<{ id: string }>()
  const [article, setArticle] = useState<Article | null>(null)
  const [activeTab, setActiveTab] = useState<'summary' | 'original' | 'mindmap'>('summary')

  useEffect(() => {
    if (id) articlesApi.get(Number(id)).then(setArticle)
  }, [id])

  if (!article) return <div className="p-10 text-center">加载中...</div>

  const keyPoints = article.key_points
    ? (typeof article.key_points === 'string' ? JSON.parse(article.key_points) : article.key_points)
    : []

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex items-center gap-4">
        <Link to="/library" className="text-gray-600 hover:text-primary-600">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h1 className="text-lg font-semibold truncate">{article.title}</h1>
      </header>

      <main className="max-w-4xl mx-auto p-6">
        <div className="bg-white rounded-lg shadow p-6 mb-4">
          <div className="flex flex-wrap gap-2 mb-3">
            {article.tags?.map((tag: string) => (
              <span key={tag} className="px-2 py-0.5 bg-gray-100 text-xs rounded-full">#{tag}</span>
            ))}
          </div>
          <div className="text-sm text-gray-500 mb-4">
            {article.primary_category} / {article.secondary_category} · {article.source} · {new Date(article.created_at).toLocaleDateString()}
          </div>

          <div className="flex gap-2 border-b mb-4">
            {(['summary', 'original', 'mindmap'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${
                  activeTab === tab ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500'
                }`}
              >
                {tab === 'summary' ? 'AI摘要' : tab === 'original' ? '原文' : '思维导图'}
              </button>
            ))}
          </div>

          {activeTab === 'summary' && (
            <div>
              <p className="text-gray-700 mb-4">{article.summary}</p>
              <h3 className="font-semibold mb-2">关键要点</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-700 mb-4">
                {keyPoints.map((point: string, i: number) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>情感: {article.sentiment === 'positive' ? '😊 正面' : article.sentiment === 'negative' ? '😞 负面' : '😐 中性'}</span>
                <span>重要度: {article.importance === 'high' ? '⭐⭐⭐ 高' : article.importance === 'medium' ? '⭐⭐ 中' : '⭐ 低'}</span>
              </div>
            </div>
          )}

          {activeTab === 'original' && (
            <div className="prose max-w-none whitespace-pre-wrap text-gray-700">
              {article.clean_content || '暂无原文'}
            </div>
          )}

          {activeTab === 'mindmap' && (
            <div className="prose max-w-none whitespace-pre-wrap text-gray-700 font-mono bg-gray-50 p-4 rounded">
              {article.mindmap || '暂无思维导图'}
            </div>
          )}
        </div>

        <div className="flex gap-3 justify-center">
          <button className="flex items-center gap-1 px-4 py-2 bg-white rounded-lg shadow text-sm hover:bg-gray-50">
            <ThumbsUp className="w-4 h-4" /> 有用
          </button>
          <button className="flex items-center gap-1 px-4 py-2 bg-white rounded-lg shadow text-sm hover:bg-gray-50">
            <ThumbsDown className="w-4 h-4" /> 不准确
          </button>
        </div>
      </main>
    </div>
  )
}
