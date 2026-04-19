import { useEffect, useState } from 'react'
import { Send } from 'lucide-react'
import { Link } from 'react-router-dom'
import FileUploader from '../components/FileUploader'
import { uploadApi } from '../api/client'
import Layout from '../components/Layout'
import type { UploadTask } from '../types'

export default function Upload() {
  const [tasks, setTasks] = useState<UploadTask[]>([])
  const [error, setError] = useState<string | null>(null)
  const [url, setUrl] = useState('')
  const [urlLoading, setUrlLoading] = useState(false)

  useEffect(() => {
    uploadApi.tasks()
      .then(setTasks)
      .catch((err) => setError(err.message))
  }, [])

  const handleUpload = async (files: FileList) => {
    setError(null)
    const newTasks: UploadTask[] = []
    for (const file of Array.from(files)) {
      try {
        const resp = await uploadApi.upload(file)
        const task = resp.task || resp
        newTasks.push(task)
      } catch (err: any) {
        setError(err.message)
        break
      }
    }
    setTasks((prev) => [...newTasks, ...prev])
  }

  const handleUrlSubmit = async () => {
    if (!url.trim() || urlLoading) return
    setError(null)
    setUrlLoading(true)
    try {
      const resp = await uploadApi.uploadUrl(url.trim())
      const newTask: UploadTask = {
        id: resp.task_id,
        original_filename: url.trim(),
        file_type: resp.type,
        status: resp.status,
        created_at: new Date().toISOString(),
      }
      setTasks((prev) => [newTask, ...prev])
      setUrl('')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setUrlLoading(false)
    }
  }

  const statusLabel: Record<string, string> = { pending: '待处理', processing: '处理中', completed: '已完成', failed: '失败' }
  const statusColor: Record<string, string> = { pending: 'text-gray-500', processing: 'text-primary-600', completed: 'text-green-600', failed: 'text-red-600' }

  return (
    <Layout>
      <main className="max-w-4xl mx-auto p-6">
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200">
            {error}
          </div>
        )}

        <h2 className="text-lg font-semibold mb-4">上传中心</h2>

        {/* URL Input */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2">粘贴链接</h3>
          <div className="flex gap-2">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleUrlSubmit()}
              placeholder="https://...  支持文章链接和 YouTube/Bilibili 等视频链接"
              className="flex-1 px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              onClick={handleUrlSubmit}
              disabled={urlLoading || !url.trim()}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 disabled:opacity-50 flex items-center gap-1"
            >
              <Send className="w-4 h-4" /> {urlLoading ? '提交中' : '提交'}
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2">
            支持：网页文章、YouTube、Bilibili、抖音等视频链接。文章直接清洗入库，视频自动下载音频并转录。
          </p>
        </div>

        {/* File Upload */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2">上传文件</h3>
          <FileUploader onUpload={handleUpload} />
        </div>

        {/* Task List */}
        <div className="mt-8 bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b"><tr><th className="text-left px-4 py-3 font-medium">文件名/链接</th><th className="text-left px-4 py-3 font-medium">类型</th><th className="text-left px-4 py-3 font-medium">状态</th><th className="text-left px-4 py-3 font-medium">时间</th></tr></thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.id} className="border-b last:border-0">
                  <td className="px-4 py-3 max-w-xs truncate">
                    {task.article_id ? (
                      <Link to={`/article/${task.article_id}`} className="text-primary-600 hover:underline truncate block">
                        {task.original_filename}
                      </Link>
                    ) : (
                      <span className="truncate block">{task.original_filename}</span>
                    )}
                  </td>
                  <td className="px-4 py-3 uppercase">{task.file_type}</td>
                  <td className={`px-4 py-3 ${statusColor[task.status] || 'text-gray-500'}`}>{statusLabel[task.status] || task.status}</td>
                  <td className="px-4 py-3 text-gray-500">{new Date(task.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {tasks.length === 0 && (
            <div className="p-8 text-center text-gray-400 text-sm">暂无上传记录</div>
          )}
        </div>
      </main>
    </Layout>
  )
}
