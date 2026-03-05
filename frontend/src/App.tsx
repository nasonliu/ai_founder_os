import { Dashboard } from './components/Dashboard'
import { TaskBoard } from './components/TaskBoard'
import { WorkerMonitor } from './components/WorkerMonitor'

function App() {
  return (
    <Dashboard>
      <WorkerMonitor />
    </Dashboard>
  )
}

export default App
