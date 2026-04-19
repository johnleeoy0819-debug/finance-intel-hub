import { useEffect, useState } from 'react'
import { AlertTriangle, CheckCircle, Clock, ShieldAlert, FileSearch } from 'lucide-react'
import { lintApi } from '../api/client'
import Layout from '../components/Layout'
import type { LintReport } from '../types'

const TYPE_LABELS: Record<string, string> = {
  orphan: '孤儿文章',
  duplicate: '重复内容',
  contradiction: '观点矛盾',
  outdated: '信息过时',
}

const TYPE_ICONS: Record<string, React.ReactNode> = {
  orphan: <FileSearch className="w-4 h-4" />,
  duplicate: <ShieldAlert className="w-4 h-4" />,
  contradiction: <AlertTriangle className="w-4 h-4" />,
  outdated: <Clock className="w-4 h-4" />,
}

const SEVERITY_COLOR: Record<string, string> = {
  high: 'text-red-600 bg-red-50 border-red-200',
  medium: 'text-orange-600 bg-orange-50 border-orange-200',
  warning: 'text-yellow-600 bg-yellow-50 border-yellow-200',
}

export default function LintReports() {
  const [reports, setReports] = useState<LintReport[]>([])
  const [summary, setSummary] = useState<{ total_open: number; by_type: Record<string, number> } | null>(null)
  const [loading, setLoading] = useState(false)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchData = () => {
    setLoading(true)
    Promise.all([lintApi.list(), lintApi.summary()])
      .then(([r, s]) => {
        setReports(r)
        setSummary(s)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleRun = async () => {
    setRunning(true)
    try {
      await lintApi.run()
      setTimeout(fetchData, 3000) // Wait for async lint to complete
    } catch (err: any) {
      setError(err.message)
    } finally {
      setRunning(false)
    }
  }

  const handleResolve = async (id: number) => {
    try {
      await lintApi.update(id, 'resolved')
      fetchData()
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <Layout>
      <main className="max-w-4xl mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <ShieldAlert className="w-5 h-5" /> 知识体检
          </h2>
          <button
            onClick={handleRun}
            disabled={running}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 disabled:opacity-50"
          >
            {running ? '审计中...' : '立即审计'}
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200">
            {error}
          </div>
        )}

        {summary && (
          <div className="grid grid-cols-4 gap-3 mb-6">
            {Object.entries(summary.by_type).map(([type, count]) => (
              <div key={type} className="bg-white rounded-lg shadow p-3 text-center">
                <div className="text-2xl font-bold text-gray-800">{count}</div>
                <div className="text-xs text-gray-500">{TYPE_LABELS[type] || type}</div>
              </div>
            ))}
            <div className="bg-white rounded-lg shadow p-3 text-center">
              <div className="text-2xl font-bold text-primary-600">{summary.total_open}</div>
              <div className="text-xs text-gray-500">待处理</div>
            </div>
          </div>
        )}

        {loading ? (
          <div className="py-10 text-center text-gray-500">加载中...</div>
        ) : reports.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <CheckCircle className="w-12 h-12 text-green-300 mx-auto mb-3" />
            <p className="text-gray-500">知识库状态良好，未发现异常</p>
          </div>
        ) : (
          <div className="space-y-3">
            {reports.map((r) => {
              let details: any = {}
              if (r.details) {
                try {
                  details = JSON.parse(r.details)
                } catch {
                  details = { raw: r.details }
                }
              }
              return (
                <div
                  key={r.id}
                  className={`bg-white rounded-lg shadow p-4 border-l-4 ${
                    SEVERITY_COLOR[r.severity || 'warning'] || 'border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {TYPE_ICONS[r.lint_type]}
                      <span className="font-medium text-sm">
                        {TYPE_LABELS[r.lint_type] || r.lint_type}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded ${SEVERITY_COLOR[r.severity || 'warning']}`}>
                        {r.severity === 'high' ? '严重' : r.severity === 'medium' ? '中等' : '提醒'}
                      </span>
                    </div>
                    {r.status === 'open' && (
                      <button
                        onClick={() => handleResolve(r.id)}
                        className="text-xs text-primary-600 hover:underline"
                      >
                        标记已解决
                      </button>
                    )}
                  </div>
                  <div className="text-sm text-gray-600">
                    {details.title || details.article_1 || details.issue || JSON.stringify(details)}
                  </div>
                  {details.suggestion && (
                    <div className="text-xs text-gray-400 mt-1">建议: {details.suggestion}</div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </main>
    </Layout>
  )
}
