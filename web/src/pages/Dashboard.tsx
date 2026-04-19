import Layout from '../components/Layout'

export default function Dashboard() {
  return (
    <Layout>
      <main className="max-w-6xl mx-auto p-6">
        <h2 className="text-lg font-semibold mb-4">仪表盘</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500">今日新增</div>
            <div className="text-2xl font-bold mt-1">--</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500">本周新增</div>
            <div className="text-2xl font-bold mt-1">--</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500">知识图谱关系数</div>
            <div className="text-2xl font-bold mt-1">--</div>
          </div>
        </div>
      </main>
    </Layout>
  )
}
