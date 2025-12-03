import React, { useState } from 'react'
import { Settings } from 'lucide-react'
import { SettingsModal } from './settings'
import { Button } from './ui/button'

interface NavigationProps {
  activeView: string
  onViewChange: (view: string) => void
}

export function Navigation({ activeView, onViewChange }: NavigationProps) {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)

  return (
    <>
      <nav className="industrial-card border-b bg-card/95 backdrop-blur-sm shadow-sm animate-scale-in">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-8">
              <h1 className="text-2xl font-display font-bold text-primary tracking-tight">
                PumpTracker Lite
              </h1>
              <div className="flex space-x-2">
                <button
                  onClick={() => onViewChange('dashboard')}
                  className={`
                    px-4 py-2 text-sm font-display font-medium rounded-lg transition-all duration-200
                    ${activeView === 'dashboard'
                      ? 'bg-primary text-primary-foreground shadow-sm hover:shadow-md'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                    }
                  `}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => onViewChange('kanban')}
                  className={`
                    px-4 py-2 text-sm font-display font-medium rounded-lg transition-all duration-200
                    ${activeView === 'kanban'
                      ? 'bg-primary text-primary-foreground shadow-sm hover:shadow-md'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                    }
                  `}
                >
                  Kanban Board
                </button>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm font-body text-muted-foreground font-medium">
                Manufacturing Excellence Platform
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsSettingsOpen(true)}
                className="flex items-center space-x-2 font-display"
              >
                <Settings className="h-4 w-4" />
                <span>Settings</span>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </>
  )
}