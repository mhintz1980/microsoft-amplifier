import React, { useState } from 'react'
import { Dashboard } from './components/Dashboard'
import { KanbanBoard } from './components/KanbanBoard'
import { Navigation } from './components/Navigation'

function App() {
  const [activeView, setActiveView] = useState('dashboard')

  return (
    <div className="min-h-screen bg-background font-body animate-fade-in">
      <Navigation activeView={activeView} onViewChange={setActiveView} />
      <main className="animate-fade-in-delay-1">
        {activeView === 'dashboard' ? <Dashboard /> : <KanbanBoard />}
      </main>
    </div>
  )
}

export default App