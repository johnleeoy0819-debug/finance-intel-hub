import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar, CartesianGrid,
} from 'recharts'
import { BookOpen, Calendar, Database, GitBranch, Layers, TrendingUp } from 'lucide-react'
import { statsApi } from '../api/client'
import Layout from '../components/Layout'
import type { DashboardStats } from '../types'
// eslint-disable-next-line @typescript-eslint/no-explicit-any

const SENTIMENT_COLORS: Record<string, string> = {
  positive: '#22c55e',
  neutral: '#6b7280',
  negative: '#ef4444',
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    statsApi.dashboard()
      .then(setStats)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <Layout>
      <main className="max-w-6xl mx-auto p-6">
        <h2 className="text-lg font-semibold mb-4">仪表盘</h2>

        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200">{error}</div>
        )}

        {!stats ? (
          <div className="py-10 text-center text-gray-500">加载中...</div>
        ) : (
          <>
            {/* Stat Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
              <StatCard icon={<Layers className="w-5 h-5 text-primary-600" />} label="文章总数" value={stats.total_count} />
              <StatCard icon={<TrendingUp className="w-5 h-5 text-green-600" />} label="今日新增" value={stats.today_count} />
              <StatCard icon={<Calendar className="w-5 h-5 text-blue-600" />} label="本周新增" value={stats.week_count} />
              <StatCard icon={<Database className="w-5 h-5 text-orange-600" />} label="活跃数据源" value={stats.source_count} />
              <StatCard icon={<GitBranch className="w-5 h-5 text-purple-600" />} label="知识关系" value={stats.edge_count} />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
              {/* 7-Day Trend */}
              <div className="bg-white rounded-lg shadow p-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3">7天文章趋势</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={stats.trend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                    <XAxis dataKey="date" tickFormatter={(d) => d.slice(5)} tick={{ fontSize: 12 }} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                    <Tooltip formatter={(v: any) => [`${v} 篇`, '新增']} />
                    <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Sentiment Pie */}
              <div className="bg-white rounded-lg shadow p-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3">情感分布</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={stats.sentiment_distribution}
                      dataKey="count"
                      nameKey="sentiment"
                      cx="50%"
                      cy="50%"
                      outerRadius={70}
                      label={(props: any) => `${props.sentiment}: ${props.count}`}
                    >
                      {stats.sentiment_distribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[entry.sentiment] || '#9ca3af'} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Category Bar + Recent Articles */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Category Distribution */}
              <div className="bg-white rounded-lg shadow p-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3">分类分布</h3>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={stats.category_distribution} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                    <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} />
                    <YAxis dataKey="name" type="category" width={80} tick={{ fontSize: 11 }} />
                    <Tooltip formatter={(v: any) => [`${v} 篇`, '数量']} />
                    <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Recent Articles */}
              <div className="bg-white rounded-lg shadow p-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3">最近新增</h3>
                <div className="space-y-2">
                  {stats.recent_articles.map((a) => (
                    <Link
                      key={a.id}
                      to={`/article/${a.id}`}
                      className="flex items-center gap-3 p-2 rounded hover:bg-gray-50 transition"
                    >
                      <BookOpen className="w-4 h-4 text-gray-400 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm truncate">{a.title}</div>
                        <div className="text-xs text-gray-400">{new Date(a.created_at).toLocaleDateString()}</div>
                      </div>
                      <span className={`text-xs px-1.5 py-0.5 rounded ${
                        a.sentiment === 'positive' ? 'bg-green-50 text-green-700' :
                        a.sentiment === 'negative' ? 'bg-red-50 text-red-700' :
                        'bg-gray-50 text-gray-600'
                      }`}>
                        {a.sentiment === 'positive' ? '正面' : a.sentiment === 'negative' ? '负面' : '中性'}
                      </span>
                    </Link>
                  ))}
                  {stats.recent_articles.length === 0 && (
                    <div className="text-sm text-gray-400 py-4 text-center">暂无文章</div>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </main>
    </Layout>
  )
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="bg-white rounded-lg shadow p-4 flex items-center gap-3">
      <div className="p-2 bg-gray-50 rounded-lg">{icon}</div>
      <div>
        <div className="text-2xl font-bold">{value}</div>
        <div className="text-xs text-gray-500">{label}</div>
      </div>
    </div>
  )
}
