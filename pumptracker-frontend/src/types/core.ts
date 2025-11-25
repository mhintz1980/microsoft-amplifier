// Core data types for PumpTracker Lite

export interface Pump {
  id: string;
  po_id: string;
  customer: string;
  model_id: string;
  stage: Stage;
  priority: Priority;
  value: number;
  buildTime: number;
  last_update: string;
  powder_color?: string;
  estimatedCompletionDate?: string;
  actualDuration?: number;
  scheduledStartDate?: string;
  scheduledEndDate?: string;
  assignedDepartment?: string;
  currentDepartment?: string;
  capacityInfo?: {
    realisticDuration: number;
    requiredManHours: number;
    estimatedHours: number;
    duration: number;
    startDate: string;
    endDate: string;
    completionDate: string;
    conflicts: Array<{
      jobId: string;
      conflictType: string;
      severity: string;
    }>;
  };
}

export interface PurchaseOrder {
  id: string;
  customer: string;
  orderDate: string;
  requestedDeliveryDate: string;
  status: string;
  totalValue: number;
  pumps: Pump[];
}

export interface PurchaseOrderLine {
  id: string;
  pumpId: string;
  quantity: number;
  unitPrice: number;
  stage: Stage;
  priority: Priority;
}

export type Stage =
  | 'NOT_STARTED'
  | 'FABRICATION'
  | 'POWDER_COAT'
  | 'ASSEMBLY'
  | 'TESTING'
  | 'SHIPPING'
  | 'QA_COMPLETE'
  | 'SHIPPED';

export type Priority = 'HIGH' | 'MEDIUM' | 'LOW';

export interface Department {
  id: string;
  name: string;
  isActive: boolean;
  sortOrder: number;
}