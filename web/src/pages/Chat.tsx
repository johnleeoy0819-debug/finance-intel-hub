import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, ThumbsUp, ThumbsDown, BookOpen, Save } from 'lucide-react'
import { Link } from 'react-router-dom'
import { skillApi, wikiApi } from '../api/client'
import Layout from '../components/Layout'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: { id: number; title: string }[]
  strategy?: string
  wikiSlug?: string
  feedbackSent?: boolean
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: '你好！我是"经济大师"，你的财经知识库助手。\n\n你可以问我任何问题，比如：\n• "最近央行降息的影响是什么？"\n• "分析一下新能源行业的趋势"\n• "特斯拉最新财报怎么看？"\n\n我会基于你的知识库文章给出回答。',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [savedToWiki, setSavedToWiki] = useState<Set<string>>(new Set())
  const [errorToast, setErrorToast] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input.trim() }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await skillApi.chat(userMsg.content)
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.answer,
        sources: res.sources,
        strategy: res.strategy,
        wikiSlug: res.wiki_slug,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { id: (Date.now() + 1).toString(), role: 'assistant', content: `请求失败：${err.message}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleFeedback = async (msgId: string, rating: number) => {
    const msg = messages.find((m) => m.id === msgId)
    if (!msg || msg.feedbackSent) return
    try {
      await skillApi.feedback({
        query: msg.content.slice(0, 200),
        response_summary: msg.content.slice(0, 500),
        rating,
      })
      setMessages((prev) =>
        prev.map((m) => (m.id === msgId ? { ...m, feedbackSent: true } : m))
      )
    } catch {
      setErrorToast('反馈提交失败，请稍后重试')
      setTimeout(() => setErrorToast(null), 3000)
    }
  }

  const handleSaveToWiki = async (msgId: string) => {
    const msg = messages.find((m) => m.id === msgId)
    if (!msg || savedToWiki.has(msgId)) return
    const title = msg.content.split('\n')[0].slice(0, 50) || 'Chat 笔记'
    try {
      await wikiApi.writeback(title, msg.content)
      setSavedToWiki((prev) => new Set(prev).add(msgId))
    } catch {
      setErrorToast('保存到 Wiki 失败，请稍后重试')
      setTimeout(() => setErrorToast(null), 3000)
    }
  }

  return (
    <Layout>
      <div className="max-w-3xl mx-auto h-[calc(100vh-64px)] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                msg.role === 'user' ? 'bg-primary-100 text-primary-600' : 'bg-gray-100 text-gray-600'
              }`}>
                {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>
              <div className={`max-w-[80%] rounded-lg p-3 text-sm ${
                msg.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white shadow text-gray-700'
              }`}>
                <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                {msg.strategy && msg.id !== 'welcome' && (
                  <div className="mt-1.5 mb-1">
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                      msg.strategy === 'wiki'
                        ? 'bg-purple-50 text-purple-600'
                        : msg.strategy === 'fulltext'
                        ? 'bg-blue-50 text-blue-600'
                        : 'bg-gray-50 text-gray-500'
                    }`}>
                      {msg.strategy === 'wiki' ? 'Wiki' : msg.strategy === 'fulltext' ? '全文' : 'RAG'}
                    </span>
                    {msg.wikiSlug && (
                      <Link to={`/wiki/${msg.wikiSlug}`} className="text-[10px] text-primary-600 hover:underline ml-1.5">
                        查看综述
                      </Link>
                    )}
                  </div>
                )}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-100">
                    <div className="text-xs text-gray-400 mb-1 flex items-center gap-1">
                      <BookOpen className="w-3 h-3" /> 引用来源
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {msg.sources.map((s) => (
                        <Link
                          key={s.id}
                          to={`/article/${s.id}`}
                          className="text-xs px-2 py-0.5 bg-gray-50 text-primary-600 rounded hover:underline"
                        >
                          {s.title}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
                {msg.role === 'assistant' && msg.id !== 'welcome' && (
                  <div className="mt-2 flex gap-2">
                    <button
                      onClick={() => handleFeedback(msg.id, 1)}
                      disabled={msg.feedbackSent}
                      className="text-xs flex items-center gap-0.5 text-gray-400 hover:text-green-600 disabled:opacity-50"
                    >
                      <ThumbsUp className="w-3 h-3" /> 有用
                    </button>
                    <button
                      onClick={() => handleFeedback(msg.id, -1)}
                      disabled={msg.feedbackSent}
                      className="text-xs flex items-center gap-0.5 text-gray-400 hover:text-red-600 disabled:opacity-50"
                    >
                      <ThumbsDown className="w-3 h-3" /> 不准确
                    </button>
                    <button
                      onClick={() => handleSaveToWiki(msg.id)}
                      disabled={savedToWiki.has(msg.id)}
                      className="text-xs flex items-center gap-0.5 text-gray-400 hover:text-blue-600 disabled:opacity-50"
                    >
                      <Save className="w-3 h-3" /> {savedToWiki.has(msg.id) ? '已保存' : '保存到 Wiki'}
                    </button>
                    {msg.feedbackSent && <span className="text-xs text-green-500">已反馈</span>}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                <Bot className="w-4 h-4 text-gray-600 animate-pulse" />
              </div>
              <div className="bg-white shadow rounded-lg p-3 text-sm text-gray-400">思考中...</div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t bg-white p-4">
          <div className="max-w-3xl mx-auto flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="输入你的问题..."
              className="flex-1 px-4 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 disabled:opacity-50 flex items-center gap-1"
            >
              <Send className="w-4 h-4" /> 发送
            </button>
          </div>
        </div>
      </div>
      {errorToast && (
        <div className="fixed bottom-20 left-1/2 -translate-x-1/2 bg-red-600 text-white text-sm px-4 py-2 rounded-lg shadow-lg z-50">
          {errorToast}
        </div>
      )}
    </Layout>
  )
}
