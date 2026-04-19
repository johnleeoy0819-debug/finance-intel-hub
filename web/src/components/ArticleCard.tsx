import { Link } from 'react-router-dom'
import type { Article } from '../types'

interface Props {
  article: Article
}

export default function ArticleCard({ article }: Props) {
  const sentimentEmoji = {
    positive: '😊',
    neutral: '😐',
    negative: '😞',
  }[article.sentiment || 'neutral']

  const importanceStars = {
    high: '⭐⭐⭐',
    medium: '⭐⭐',
    low: '⭐',
  }[article.importance || 'low']

  return (
    <Link
      to={`/article/${article.id}`}
      className="block p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
    >
      <h3 className="font-semibold text-lg mb-2">{article.title}</h3>
      <div className="flex flex-wrap gap-2 mb-2">
        {article.tags?.map((tag) => (
          <span key={tag} className="px-2 py-0.5 bg-gray-100 text-xs rounded-full text-gray-600">
            #{tag}
          </span>
        ))}
      </div>
      <p className="text-gray-600 text-sm line-clamp-2 mb-2">{article.summary}</p>
      <div className="flex items-center gap-3 text-xs text-gray-500">
        <span>{article.primary_category} / {article.secondary_category}</span>
        <span>{sentimentEmoji} {article.sentiment}</span>
        <span>{importanceStars}</span>
        <span>{new Date(article.created_at).toLocaleDateString()}</span>
      </div>
    </Link>
  )
}
