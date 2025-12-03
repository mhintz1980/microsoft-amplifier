import React from 'react'
import { KPICards } from './KPICards'
import { ChartsSection } from './ChartsSection'
import { OrderDetails } from './OrderDetails'
import { UniversalFilters } from './UniversalFilters'

export function Dashboard() {
  return (
    <div data-testid="dashboard" className="min-h-screen bg-background">
      {/* Header with filters - scroll locked */}
      <div className="scroll-locked industrial-card border-b bg-card/95 backdrop-blur-sm shadow-sm animate-fade-in">
        <div className="px-6 py-4">
          <UniversalFilters />
        </div>
      </div>

      {/* Main content */}
      <div className="p-6 space-y-8 animate-fade-in-delay-2">
        {/* KPI Cards */}
        <div className="animate-fade-in-delay-1">
          <KPICards />
        </div>

        {/* Charts Section - Fixed the non-rendering charts */}
        <div className="animate-fade-in-delay-2">
          <ChartsSection />
        </div>

        {/* Order Details - Expandable PO lines */}
        <div className="animate-fade-in-delay-3">
          <OrderDetails />
        </div>
      </div>
    </div>
  )
}