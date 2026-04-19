import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Library from './pages/Library'
import ArticleDetail from './pages/ArticleDetail'
import Sources from './pages/Sources'
import Upload from './pages/Upload'
import Publications from './pages/Publications'
import Chat from './pages/Chat'
import WikiList from './pages/WikiList'
import WikiDetail from './pages/WikiDetail'
import LintReports from './pages/LintReports'
import Settings from './pages/Settings'
import OperationLogs from './pages/OperationLogs'

function App() {
  return (
    <div className="min-h-screen">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/library" element={<Library />} />
        <Route path="/article/:id" element={<ArticleDetail />} />
        <Route path="/sources" element={<Sources />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/publications" element={<Publications />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/wiki" element={<WikiList />} />
        <Route path="/wiki/:slug" element={<WikiDetail />} />
        <Route path="/lint" element={<LintReports />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/operations" element={<OperationLogs />} />
      </Routes>
    </div>
  )
}

export default App
