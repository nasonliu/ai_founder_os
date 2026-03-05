import { useState } from 'react'
import { 
  LayoutDashboard, 
  Users, 
  GitBranch, 
  Zap, 
  Shield,
  Settings
} from 'lucide-react'

interface DashboardProps {
  children?: React.ReactNode
}

export function Dashboard({ children }: DashboardProps) {
  const [activeTab, setActiveTab] = useState('overview')

  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'projects', label: 'Projects', icon: GitBranch },
    { id: 'workers', label: 'Workers', icon: Users },
    { id: 'tasks', label: 'Tasks', icon: Zap },
    { id: 'reviews', label: 'Reviews', icon: Shield },
    { id: 'settings', label: 'Settings', icon: Settings },
  ]

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">AI Founder OS</h1>
          <p className="text-sm text-gray-500">Dashboard</p>
        </div>
        
        <nav className="p-2">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left ${
                  activeTab === tab.id
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{tab.label}</span>
              </button>
            )
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="p-6">
          {children || <OverviewPanel />}
        </div>
      </main>
    </div>
  )
}

function OverviewPanel() {
  const stats = [
    { label: 'Active Projects', value: '3', color: 'bg-blue-500' },
    { label: 'Running Workers', value: '5', color: 'bg-green-500' },
    { label: 'Pending Reviews', value: '2', color: 'bg-yellow-500' },
    { label: 'Completed Tasks', value: '28', color: 'bg-purple-500' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">System Overview</h2>
        <p className="text-gray-500">Monitor your AI engineering organization</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center mb-4`}>
              <span className="text-2xl font-bold text-white">{stat.value}</span>
            </div>
            <p className="text-gray-600">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-gray-700">Task completed: Implement Planner Loop</span>
            <span className="text-gray-400 text-sm ml-auto">2m ago</span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-gray-700">Worker assigned: builder_01</span>
            <span className="text-gray-400 text-sm ml-auto">5m ago</span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <span className="text-gray-700">Review requested: Skill Installation</span>
            <span className="text-gray-400 text-sm ml-auto">10m ago</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
