import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ChevronDown, ChevronUp, Maximize2, Minimize2 } from 'lucide-react'
import { KanbanCard } from './KanbanCard'
import { mockPumps, mockDepartments, updatePumpsWithCapacityAwareScheduling, getCapacityStatus } from '@/lib/dataAdapter'

interface KanbanColumnProps {
  title: string
  stage: string
  isCollapsed: boolean
  onToggleCollapse: () => void
  pumps?: any[]
  vendors?: any[]
}

export function KanbanColumn({ title, stage, isCollapsed, onToggleCollapse, pumps = [], vendors = [] }: KanbanColumnProps) {
  const [cardsCollapsed, setCardsCollapsed] = useState(false)

  // Special handling for powder coat stage with 3-vendor swimlanes
  const isPowderCoat = stage === 'POWDER_COAT'

  const displayPumps = pumps.filter(pump => pump.stage === stage)

  return (
    <Card className={`kanban-column ${isCollapsed ? 'h-16' : 'min-h-[500px]'} transition-all duration-300`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-gray-700">
            {title}
          </CardTitle>
          <div className="flex items-center gap-1">
            <span className="bg-gray-200 text-gray-700 text-xs px-2 py-1 rounded-full">
              {displayPumps.length}
            </span>
            <button
              onClick={onToggleCollapse}
              className="p-1 hover:bg-gray-200 rounded"
            >
              {isCollapsed ? (
                <ChevronDown className="h-3 w-3" />
              ) : (
                <ChevronUp className="h-3 w-3" />
              )}
            </button>
          </div>
        </div>

        {/* Expand/Collapse Cards Toggle */}
        {!isCollapsed && (
          <button
            onClick={() => setCardsCollapsed(!cardsCollapsed)}
            className="mt-2 w-full justify-start text-xs flex items-center gap-1 text-gray-600 hover:text-gray-800"
          >
            {cardsCollapsed ? (
              <>
                <Maximize2 className="h-3 w-3" />
                Expand Cards
              </>
            ) : (
              <>
                <Minimize2 className="h-3 w-3" />
                Collapse Cards
              </>
            )}
          </button>
        )}
      </CardHeader>

      {!isCollapsed && (
        <CardContent className="pt-0">
          {/* 3-Vendor Powder Coat Swimlanes */}
          {isPowderCoat && vendors.length > 0 ? (
            <div className="space-y-3">
              {vendors.map((vendor) => (
                <div key={vendor.id} className="border rounded-lg p-2 bg-gray-50">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-xs font-medium text-gray-700">
                      {vendor.name}
                    </h4>
                    <span className="text-xs text-gray-500">
                      {vendor.currentLoad}/{vendor.weeklyCapacity}
                    </span>
                  </div>
                  <div className="space-y-1">
                    {/* Vendor-specific pumps would go here */}
                    {displayPumps.slice(0, 2).map((pump) => (
                      <KanbanCard
                        key={pump.id}
                        pump={pump}
                        isCollapsed={cardsCollapsed}
                        vendorName={vendor.name}
                      />
                    ))}
                  </div>
                  <div className="h-px bg-gray-300 my-2"></div>
                  <div className="text-center">
                    <span className="text-xs text-gray-500">Capacity: {vendor.weeklyCapacity - vendor.currentLoad} available</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {displayPumps.map((pump) => (
                <KanbanCard
                  key={pump.id}
                  pump={pump}
                  isCollapsed={cardsCollapsed}
                />
              ))}
            </div>
          )}

          {/* Add new pump button */}
          <button className="w-full h-12 border-2 border-dashed border-gray-300 text-gray-500 hover:border-gray-400 hover:text-gray-600 rounded-lg mt-3 flex items-center justify-center text-sm">
            + Add Pump
          </button>
        </CardContent>
      )}
    </Card>
  )
}

export function KanbanBoard() {
  // Get capacity-aware pump data
  const [pumpData, setPumpData] = useState(() => updatePumpsWithCapacityAwareScheduling());
  const [capacityStatus, setCapacityStatus] = useState(() => getCapacityStatus());

  // Mock vendors for powder coat (3 vendors)
  const powderCoatVendors = [
    { id: 'vendor-1', name: 'Vendor A - Premium', weeklyCapacity: 7, currentLoad: 5, isPreferred: true },
    { id: 'vendor-2', name: 'Vendor B - Standard', weeklyCapacity: 7, currentLoad: 4, isPreferred: false },
    { id: 'vendor-3', name: 'Vendor C - Economy', weeklyCapacity: 7, currentLoad: 6, isPreferred: false }
  ]

  const [columns, setColumns] = useState([
    { id: 'NOT_STARTED', title: 'Not Started', isCollapsed: false },
    { id: 'FABRICATION', title: 'Fabrication', isCollapsed: false },
    { id: 'POWDER_COAT', title: 'Powder Coat', isCollapsed: false },
    { id: 'ASSEMBLY', title: 'Assembly', isCollapsed: false },
    { id: 'TESTING', title: 'Testing', isCollapsed: false },
    { id: 'SHIPPING', title: 'Shipping', isCollapsed: false },
    { id: 'QA_COMPLETE', title: 'QA Complete', isCollapsed: false }
  ])

  // Refresh data when settings change
  const refreshData = () => {
    setPumpData(updatePumpsWithCapacityAwareScheduling());
    setCapacityStatus(getCapacityStatus());
  };

  const toggleColumnCollapse = (columnId: string) => {
    setColumns(prev => prev.map(col =>
      col.id === columnId
        ? { ...col, isCollapsed: !col.isCollapsed }
        : col
    ))
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Production Board</h2>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-600">
            Drag and drop pumps to move between stages
          </div>
          <button
            onClick={refreshData}
            className="text-sm bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
          >
            Refresh Schedules
          </button>
        </div>
      </div>

      {/* Capacity Status Summary */}
      <div className="mb-6 p-4 bg-green-50 rounded-lg">
        <h3 className="text-sm font-medium text-green-900 mb-3">Department Capacity Status</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {capacityStatus.map((dept) => (
            <div key={dept.departmentId} className="text-center">
              <div className="text-sm font-medium text-green-800 capitalize">
                {dept.departmentId.replace('_', ' ')}
              </div>
              <div className="text-xs text-green-600">
                {dept.dailyManHours} man-hours/day
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {dept.queuedJobs} jobs queued
              </div>
            </div>
          ))}
        </div>
        {pumpData.conflicts.length > 0 && (
          <div className="mt-3 p-2 bg-yellow-100 rounded text-xs text-yellow-800">
            ⚠️ {pumpData.conflicts.length} capacity conflicts detected
          </div>
        )}
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 xl:grid-cols-7 gap-4">
        {columns.map((column) => (
          <KanbanColumn
            key={column.id}
            title={column.title}
            stage={column.id}
            isCollapsed={column.isCollapsed}
            onToggleCollapse={() => toggleColumnCollapse(column.id)}
            pumps={pumpData.pumps}
            vendors={column.id === 'POWDER_COAT' ? powderCoatVendors : []}
          />
        ))}
      </div>

      {/* Powder Coat Capacity Summary */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="text-sm font-medium text-blue-900 mb-2">Powder Coat Capacity Summary</h3>
        <div className="grid grid-cols-3 gap-4">
          {powderCoatVendors.map((vendor) => (
            <div key={vendor.id} className="text-center">
              <div className="text-sm font-medium text-blue-800">{vendor.name}</div>
              <div className="text-xs text-blue-600">
                {vendor.currentLoad} / {vendor.weeklyCapacity} pumps
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2 mt-1">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${(vendor.currentLoad / vendor.weeklyCapacity) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
        <div className="mt-3 text-center text-xs text-blue-700">
          Total Capacity: {powderCoatVendors.reduce((sum, v) => sum + v.weeklyCapacity, 0)} pumps per week
        </div>
      </div>
    </div>
  )
}