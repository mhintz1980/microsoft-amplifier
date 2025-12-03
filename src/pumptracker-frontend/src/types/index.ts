// Import types from the core types
import type { Pump, PurchaseOrder, PurchaseOrderLine, Stage, Priority } from './core'

export interface KPIData {
  totalOrders: number
  onTimeDelivery: number
  avgProductionTime: number
  activeJobs: number
}

export interface ChartData {
  name: string
  value: number
  color?: string
}

export interface FilterState {
  customer: string
  stage: string
  priority: string
  dateRange: {
    start: Date | null
    end: Date | null
  }
  model: string
}

export interface KanbanColumn {
  id: string
  title: string
  pumps: Pump[]
  isCollapsed: boolean
}

export type SortableItem = {
  id: string
  pump: Pump
}

// Re-export from existing types
export type { Pump, PurchaseOrder, PurchaseOrderLine, Stage, Priority }