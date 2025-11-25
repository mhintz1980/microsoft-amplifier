import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Clock, User, Package, AlertTriangle, GripVertical, Users, TrendingUp } from 'lucide-react'
import { formatDate, getStageColor, getPriorityColor } from '@/lib/utils'

interface KanbanCardProps {
  pump: {
    id: string
    model_id: string
    customer: string
    stage: string
    priority: string
    value: number
    buildTime: number
    last_update: string
    powder_color?: string
    estimatedCompletionDate?: string | null
    estimatedDuration?: number | null
    currentDepartment?: string
    capacityInfo?: {
      completionDate: Date
      duration: number
      department: string
      estimatedHours: number
    } | null
  }
  isCollapsed: boolean
  vendorName?: string
}

export function KanbanCard({ pump, isCollapsed, vendorName }: KanbanCardProps) {
  const priorityColors = {
    HIGH: 'bg-red-100 border-red-300',
    MEDIUM: 'bg-yellow-100 border-yellow-300',
    LOW: 'bg-green-100 border-green-300'
  }

  const priorityIndicator = pump.priority === 'HIGH' ? (
    <AlertTriangle className="h-3 w-3 text-red-600" />
  ) : null

  if (isCollapsed) {
    // Collapsed view - only essential info
    return (
      <Card className={`kanban-card p-3 border-l-4 ${priorityColors[pump.priority as keyof typeof priorityColors]} hover:shadow-md cursor-move`}>
        <CardContent className="p-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <GripVertical className="h-4 w-4 text-gray-400" />
              {priorityIndicator}
              <span className="text-sm font-medium truncate">{pump.model_id}</span>
            </div>
            <div className="text-xs text-gray-500">
              ${pump.value.toLocaleString()}
            </div>
          </div>
          <div className="text-xs text-gray-600 mt-1 truncate">
            {pump.customer}
          </div>
          {pump.estimatedDuration && (
            <div className="flex items-center gap-1 mt-1">
              <Clock className="h-3 w-3 text-blue-500" />
              <span className="text-xs text-blue-600 font-medium">
                {pump.estimatedDuration.toFixed(1)}d
              </span>
            </div>
          )}
          {vendorName && (
            <div className="text-xs text-blue-600 mt-1">
              {vendorName}
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  // Expanded view - full details
  return (
    <Card className={`kanban-card border-l-4 ${priorityColors[pump.priority as keyof typeof priorityColors]} hover:shadow-lg cursor-move`}>
      <CardContent className="p-4">
        {/* Header with drag handle and model */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2 min-w-0 flex-1">
            <GripVertical className="h-4 w-4 text-gray-400" />
            {priorityIndicator}
            <h4 className="font-semibold text-sm truncate">{pump.model_id}</h4>
          </div>
          <div className="text-xs text-gray-500 font-medium">
            ${(pump.value / 1000).toFixed(1)}k
          </div>
        </div>

        {/* Customer and details */}
        <div className="space-y-2 mb-3">
          <div className="flex items-center gap-2">
            <User className="h-3 w-3 text-gray-400" />
            <span className="text-sm text-gray-700 truncate">{pump.customer}</span>
          </div>

          {/* Capacity-aware duration display */}
          {pump.capacityInfo ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-3 w-3 text-blue-500" />
                <span className="text-sm text-blue-700 font-medium">
                  {pump.capacityInfo.duration.toFixed(1)} days
                </span>
              </div>
              <span className="text-xs text-gray-500">
                {pump.capacityInfo.estimatedHours}h
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Package className="h-3 w-3 text-gray-400" />
              <span className="text-sm text-gray-700">{pump.buildTime} days</span>
            </div>
          )}

          {/* Department info */}
          {pump.currentDepartment && (
            <div className="flex items-center gap-2">
              <Users className="h-3 w-3 text-green-500" />
              <span className="text-sm text-green-700">{pump.currentDepartment}</span>
            </div>
          )}

          {vendorName && (
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 bg-blue-500 rounded-full"></div>
              <span className="text-sm text-blue-700">{vendorName}</span>
            </div>
          )}
        </div>

        {/* Stage and priority */}
        <div className="flex items-center justify-between mb-3">
          <span className={`text-xs px-2 py-1 rounded ${getStageColor(pump.stage)}`}>
            {pump.stage.replace('_', ' ')}
          </span>
          <span className={`text-xs px-2 py-1 rounded font-medium ${getPriorityColor(pump.priority)}`}>
            {pump.priority}
          </span>
        </div>

        {/* Additional details */}
        {pump.powder_color && (
          <div className="mb-3">
            <div className="text-xs text-gray-500 mb-1">Color:</div>
            <div className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded border border-gray-300"
                style={{ backgroundColor: getTextColor(pump.powder_color) }}
              ></div>
              <span className="text-xs text-gray-700">{pump.powder_color}</span>
            </div>
          </div>
        )}

        {/* Footer with date and completion estimate */}
        <div className="flex flex-col gap-2">
          {pump.capacityInfo?.completionDate && (
            <div className="flex items-center justify-between text-xs bg-blue-50 p-2 rounded">
              <div className="flex items-center gap-1 text-blue-700">
                <Clock className="h-3 w-3" />
                <span>Est. completion</span>
              </div>
              <span className="font-medium text-blue-800">
                {formatDate(pump.capacityInfo.completionDate.toISOString())}
              </span>
            </div>
          )}

          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {formatDate(pump.last_update)}
            </div>
            <span className="font-medium">#{pump.id.slice(-6)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Helper function to convert color names to approximate colors
function getTextColor(colorName: string): string {
  const colorMap: Record<string, string> = {
    'Safety Red': '#dc2626',
    'Industrial Yellow': '#f59e0b',
    'Municipal Blue': '#2563eb',
    'Forest Green': '#16a34a',
    'Standard Gray': '#6b7280',
    'Corporate White': '#f9fafb',
    'Marine Blue': '#1e40af',
    'Construction Orange': '#ea580c'
  }
  return colorMap[colorName] || '#6b7280'
}