import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Library from './pages/Library'
import ArticleDetail from './pages/ArticleDetail'
import Sources from './pages/Sources'
import Upload from './pages/Upload'

function App() {
  return (
    <div className="min-h-screen">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/library" element={<Library />} />
        <Route path="/article/:id" element={<ArticleDetail />} />
        <Route path="/sources" element={<Sources />} />
        <Route path="/upload" element={<Upload />} />
      </Routes>
    </div>
  )
}

export default App
