import { useEffect, useState } from 'react'
import { Activity, Clock } from 'lucide-react'
import { operationsApi } from '../api/client'
import Layout from '../components/Layout'

interface LogEntry {
  id: number
  operation_type: string
  target_type?: string
  target_id?: string
  details?: string
  created_at: string
}

const TYPE_LABELS: Record<string, string> = {
  article_processed: '文章处理',
  wiki_compiled: 'Wiki 编译',
  lint_run: 'Lint 审计',
  rules_updated: '规则更新',
  file_uploaded: '文件上传',
  url_submitted: 'URL 提交',
}

const TYPE_COLORS: Record<string, string> = {
  article_processed: 'bg-blue-50 text-blue-600',
  wiki_compiled: 'bg-purple-50 text-purple-600',
  lint_run: 'bg-orange-50 text-orange-600',
  rules_updated: 'bg-gray-50 text-gray-600',
  file_uploaded: 'bg-green-50 text-green-600',
  url_submitted: 'bg-green-50 text-green-600',
}

export default function OperationLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    operationsApi.list()
      .then((res) => setLogs(res.items))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const parseDetails = (details?: string) => {
    if (!details) return null
    try {
      return JSON.parse(details)
    } catch {
      return details
    }
  }

  return (
    <Layout>
      <main className="max-w-4xl mx-auto p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5" /> 操作日志
        </h2>

        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center text-gray-500 py-10">加载中...</div>
        ) : logs.length === 0 ? (
          <div className="text-center text-gray-400 py-10">暂无操作记录</div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500">
                <tr>
                  <th className="px-4 py-3 text-left font-medium">时间</th>
                  <th className="px-4 py-3 text-left font-medium">操作</th>
                  <th className="px-4 py-3 text-left font-medium">目标</th>
                  <th className="px-4 py-3 text-left font-medium">详情</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {logs.map((log) => {
                  const details = parseDetails(log.details)
                  return (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(log.created_at).toLocaleString()}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${TYPE_COLORS[log.operation_type] || 'bg-gray-50 text-gray-600'}`}>
                          {TYPE_LABELS[log.operation_type] || log.operation_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {log.target_type || '-'}
                        {log.target_id && <span className="text-gray-400 ml-1">#{log.target_id}</span>}
                      </td>
                      <td className="px-4 py-3 text-gray-500 max-w-xs truncate">
                        {typeof details === 'object' && details !== null
                          ? Object.entries(details).map(([k, v]) => `${k}: ${v}`).join(', ')
                          : details || '-'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </Layout>
  )
}
