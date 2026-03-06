import { useState } from 'react'

export function Dashboard({ children }: { children?: React.ReactNode }) {
  const [activeTab, setActiveTab] = useState('overview')

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r border-gray-200 p-4">
        <h1 className="text-xl font-bold text-gray-900">AI Founder OS</h1>
        <p className="text-sm text-gray-500 mb-4">Dashboard</p>
        <nav className="space-y-2">
          <button onClick={() => setActiveTab('overview')} className="w-full text-left px-3 py-2 rounded-lg bg-blue-50 text-blue-700">Overview</button>
          <button onClick={() => setActiveTab('projects')} className="w-full text-left px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100">Projects</button>
          <button onClick={() => setActiveTab('workers')} className="w-full text-left px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100">Workers</button>
          <button onClick={() => setActiveTab('tasks')} className="w-full text-left px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100">Tasks</button>
        </nav>
      </aside>
      <main className="flex-1 p-6">
        <h2 className="text-2xl font-bold text-gray-900">System Overview</h2>
        <div className="grid grid-cols-4 gap-4 mt-4">
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="text-3xl font-bold text-blue-500">3</div>
            <div className="text-gray-600">Active Projects</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="text-3xl font-bold text-green-500">5</div>
            <div className="text-gray-600">Running Workers</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="text-3xl font-bold text-yellow-500">2</div>
            <div className="text-gray-600">Pending Reviews</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="text-3xl font-bold text-purple-500">28</div>
            <div className="text-gray-600">Completed Tasks</div>
          </div>
        </div>
      </main>
    </div>
  )
}

function App() {
  return <Dashboard />
}

export default App
