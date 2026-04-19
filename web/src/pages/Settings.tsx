import { useEffect, useState } from 'react'
import { Save, RotateCcw, Settings2 } from 'lucide-react'
import { settingsApi } from '../api/client'
import Layout from '../components/Layout'

const DEFAULT_TEMPLATE = `# 用户自定义规则

## 关注领域
- 优先关注中国宏观经济和货币政策
- 对新能源、科技互联网行业保持高度敏感

## 回答风格
- 回答要简洁，控制在 3-5 段以内
- 使用专业但易懂的语言
- 遇到数据时标注来源

## 分类偏好
- 涉及"央行""利率"的文章优先归类到"货币政策"
- 涉及"财报""估值"的文章优先归类到"财报解读"
`

export default function Settings() {
  const [rules, setRules] = useState('')
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    settingsApi.getRules()
      .then((r) => setRules(r.rules || DEFAULT_TEMPLATE))
      .catch((err) => setError(err.message))
  }, [])

  const handleSave = async () => {
    setLoading(true)
    setSaved(false)
    setError(null)
    try {
      await settingsApi.updateRules(rules)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    if (confirm('确定恢复默认规则吗？')) {
      setRules(DEFAULT_TEMPLATE)
    }
  }

  return (
    <Layout>
      <main className="max-w-3xl mx-auto p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Settings2 className="w-5 h-5" /> 设置
        </h2>

        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200">
            {error}
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-gray-800">AI 助手行为规则</h3>
            <button
              onClick={handleReset}
              className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" /> 恢复默认
            </button>
          </div>

          <p className="text-sm text-gray-500 mb-3">
            以下规则会注入到 AI 的 system prompt 中，影响所有 AI 处理行为（分类、摘要、回答等）。
          </p>

          <textarea
            value={rules}
            onChange={(e) => setRules(e.target.value)}
            rows={20}
            className="w-full px-3 py-2 border rounded-lg text-sm font-mono leading-relaxed focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
          />

          <div className="flex items-center justify-between mt-4">
            <span className="text-xs text-gray-400">
              {rules.length} / 2000 字
            </span>
            <div className="flex items-center gap-3">
              {saved && <span className="text-sm text-green-600">已保存</span>}
              <button
                onClick={handleSave}
                disabled={loading}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 disabled:opacity-50 flex items-center gap-1"
              >
                <Save className="w-4 h-4" /> {loading ? '保存中' : '保存'}
              </button>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  )
}
