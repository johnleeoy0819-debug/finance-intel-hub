import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import FileUploader from '../components/FileUploader'
import { uploadApi } from '../api/client'
import type { UploadTask } from '../types'

export default function Upload() {
  const [tasks, setTasks] = useState<UploadTask[]>([])
  const [error, setError] = useState<string | null>(null)

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
        // Media uploads return {task, result}; doc uploads return task directly
        const task = resp.task || resp
        newTasks.push(task)
      } catch (err: any) {
        setError(err.message)
        break
      }
    }
    setTasks((prev) => [...newTasks, ...prev])
  }

  const statusLabel: Record<string, string> = { pending: '待处理', processing: '处理中', completed: '已完成', failed: '失败' }
  const statusColor: Record<string, string> = { pending: 'text-gray-500', processing: 'text-primary-600', completed: 'text-green-600', failed: 'text-red-600' }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold">FinanceIntel Hub</Link>
        <nav className="flex gap-4 text-sm">
          <Link to="/" className="text-gray-600 hover:text-primary-600">仪表盘</Link>
          <Link to="/library" className="text-gray-600 hover:text-primary-600">知识库</Link>
          <Link to="/upload" className="text-primary-600 font-medium">上传</Link>
          <Link to="/sources" className="text-gray-600 hover:text-primary-600">数据源</Link>
          <Link to="/publications" className="text-gray-600 hover:text-primary-600">文献</Link>
        </nav>
      </header>

      <main className="max-w-4xl mx-auto p-6">
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200">
            {error}
          </div>
        )}

        <h2 className="text-lg font-semibold mb-4">上传中心</h2>
        <FileUploader onUpload={handleUpload} />

        <div className="mt-8 bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b"><tr><th className="text-left px-4 py-3 font-medium">文件名</th><th className="text-left px-4 py-3 font-medium">类型</th><th className="text-left px-4 py-3 font-medium">状态</th><th className="text-left px-4 py-3 font-medium">时间</th></tr></thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.id} className="border-b last:border-0">
                  <td className="px-4 py-3">{task.original_filename}</td>
                  <td className="px-4 py-3 uppercase">{task.file_type}</td>
                  <td className={`px-4 py-3 ${statusColor[task.status] || 'text-gray-500'}`}>{statusLabel[task.status] || task.status}</td>
                  <td className="px-4 py-3 text-gray-500">{new Date(task.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  )
}
