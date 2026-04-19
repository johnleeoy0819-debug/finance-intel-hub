import { Link, useLocation } from 'react-router-dom'

const NAV_ITEMS = [
  { path: '/', label: '仪表盘' },
  { path: '/library', label: '知识库' },
  { path: '/wiki', label: 'Wiki' },
  { path: '/chat', label: 'AI 助手' },
  { path: '/lint', label: '体检' },
  { path: '/upload', label: '上传' },
  { path: '/sources', label: '数据源' },
  { path: '/publications', label: '文献' },
  { path: '/settings', label: '设置' },
  { path: '/operations', label: '日志' },
]

interface Props {
  children: React.ReactNode
  extraHeader?: React.ReactNode
}

export default function Layout({ children, extraHeader }: Props) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold">Johnlee's KnowledgeBase</Link>
        <nav className="flex gap-4 text-sm">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={
                location.pathname === item.path
                  ? 'text-primary-600 font-medium'
                  : 'text-gray-600 hover:text-primary-600'
              }
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </header>
      {extraHeader && <div className="bg-white border-b px-6 py-3">{extraHeader}</div>}
      {children}
    </div>
  )
}
