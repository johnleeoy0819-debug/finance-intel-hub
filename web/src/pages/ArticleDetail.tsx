import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, ThumbsUp, ThumbsDown } from 'lucide-react'
import { articlesApi, graphApi, skillApi } from '../api/client'
import KnowledgeGraph from '../components/KnowledgeGraph'
import type { Article, GraphData } from '../types'

export default function ArticleDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [article, setArticle] = useState<Article | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'summary' | 'original' | 'mindmap' | 'graph'>('summary')
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [graphLoading, setGraphLoading] = useState(false)
  const [feedbackSent, setFeedbackSent] = useState(false)
  const [showFeedbackForm, setShowFeedbackForm] = useState(false)
  const [feedbackComment, setFeedbackComment] = useState('')

  useEffect(() => {
    if (!id) return
    setError(null)
    setActiveTab('summary')
    setGraphData(null)
    setFeedbackSent(false)
    articlesApi.get(Number(id))
      .then(setArticle)
      .catch((err) => setError(err.message))
  }, [id])

  useEffect(() => {
    if (activeTab === 'graph' && id && !graphData) {
      setGraphLoading(true)
      graphApi.article(Number(id), 1)
        .then(setGraphData)
        .catch((err) => setError(err.message))
        .finally(() => setGraphLoading(false))
    }
  }, [activeTab, id, graphData])

  const handleThumbsUp = async () => {
    if (!article || feedbackSent) return
    try {
      await skillApi.feedback({
        query: article.title,
        response_summary: article.summary,
        rating: 5,
      })
      setFeedbackSent(true)
    } catch (err: any) {
      setError(err.message)
    }
  }

  const handleThumbsDown = async () => {
    if (!article || feedbackSent) return
    if (!showFeedbackForm) {
      setShowFeedbackForm(true)
      return
    }
    try {
      await skillApi.feedback({
        query: article.title,
        response_summary: article.summary,
        rating: 1,
        comment: feedbackComment,
      })
      setFeedbackSent(true)
      setShowFeedbackForm(false)
      setFeedbackComment('')
    } catch (err: any) {
      setError(err.message)
    }
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-red-600 mb-2">加载失败</p>
          <p className="text-gray-500 text-sm mb-4">{error}</p>
          <Link to="/library" className="text-primary-600 hover:underline text-sm">返回知识库</Link>
        </div>
      </div>
    )
  }

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
        <h1 className="text-lg font-semibold truncate flex-1">{article.title}</h1>
        <nav className="flex gap-4 text-sm">
          <Link to="/publications" className="text-gray-600 hover:text-primary-600">文献</Link>
        </nav>
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
            {([
              { key: 'summary' as const, label: 'AI摘要' },
              { key: 'original' as const, label: '原文' },
              { key: 'mindmap' as const, label: '思维导图' },
              { key: 'graph' as const, label: '知识图谱' },
            ]).map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${
                  activeTab === tab.key ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500'
                }`}
              >
                {tab.label}
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

          {activeTab === 'graph' && (
            <div>
              {graphLoading ? (
                <div className="py-10 text-center text-gray-500">加载知识图谱...</div>
              ) : graphData ? (
                <KnowledgeGraph
                  data={graphData}
                  width={720}
                  height={420}
                  onNodeClick={(nid) => navigate(`/articles/${nid}`)}
                />
              ) : (
                <div className="text-center text-gray-400 py-10">暂无知识图谱数据</div>
              )}
            </div>
          )}
        </div>

        <div className="flex flex-col items-center gap-3">
          {feedbackSent && (
            <span className="text-sm text-green-600">反馈已提交，感谢！</span>
          )}
          {showFeedbackForm && (
            <div className="w-full max-w-md bg-white rounded-lg shadow p-3">
              <textarea
                value={feedbackComment}
                onChange={(e) => setFeedbackComment(e.target.value)}
                placeholder="请告诉我们哪里不准确..."
                className="w-full px-3 py-2 border rounded-lg text-sm resize-none"
                rows={2}
              />
            </div>
          )}
          <div className="flex gap-3">
            <button
              onClick={handleThumbsUp}
              disabled={feedbackSent}
              className="flex items-center gap-1 px-4 py-2 bg-white rounded-lg shadow text-sm hover:bg-gray-50 disabled:opacity-50"
            >
              <ThumbsUp className="w-4 h-4" /> 有用
            </button>
            <button
              onClick={handleThumbsDown}
              disabled={feedbackSent}
              className="flex items-center gap-1 px-4 py-2 bg-white rounded-lg shadow text-sm hover:bg-gray-50 disabled:opacity-50"
            >
              <ThumbsDown className="w-4 h-4" /> 不准确
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
