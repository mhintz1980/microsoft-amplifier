export interface BOM {
  engine: string;
  gearbox: string;
  control_panel: string;
}

export interface LeadTimes {
  fabrication: number;
  powder_coat: number;
  assembly: number;
  testing: number;
  total_days: number;
}

export interface Model {
  id: string;
  description: string;
  price: number | null;
  defaultBuildTime: number;
  bom: BOM;
  leadTimes: LeadTimes;
}

export interface Pump {
  id: string; // UUID
  serial?: number;
  po_id: string;
  po_line_id?: string; // UUID
  customer: string;
  model_id: string;
  stage: Stage;
  priority: Priority;
  powder_color?: string;
  last_update: string; // ISO
  value: number;
  buildTime: number;
  bom: BOM;
  scheduled_start?: string; // ISO
  scheduled_end?: string; // ISO
  promise_date?: string; // ISO
  org_id: string; // UUID
}

export interface PurchaseOrder {
  id: string; // PO number
  customer: string;
  dateReceived?: string; // ISO
  promiseDate?: string; // ISO default
  notes?: string;
  org_id: string; // UUID
}

export interface PurchaseOrderLine {
  id: string; // UUID
  po_id: string;
  line_no: number;
  model_id: string;
  quantity: number;
  priority: Priority;
  color?: string;
  promise_date?: string; // ISO override
  value_each: number;
  org_id: string; // UUID
}

export interface PumpEvent {
  id: string; // UUID
  pump_id: string; // UUID
  event_time: string; // ISO
  from_stage?: Stage;
  to_stage?: Stage;
  notes?: string;
  meta?: Record<string, any>;
  org_id: string; // UUID
}

export enum Stage {
  NOT_STARTED = 'NOT_STARTED',
  FABRICATION = 'FABRICATION',
  POWDER_COAT = 'POWDER_COAT',
  ASSEMBLY = 'ASSEMBLY',
  TESTING = 'TESTING',
  QA_COMPLETE = 'QA_COMPLETE',
  SHIPPED = 'SHIPPED'
}

export enum Priority {
  LOW = 'LOW',
  NORMAL = 'NORMAL',
  HIGH = 'HIGH',
  URGENT = 'URGENT'
}

export interface StoredData {
  schemaVersion: string;
  lastSavedAt: string;
  orgId: string;
  purchaseOrders: PurchaseOrder[];
  purchaseOrderLines: PurchaseOrderLine[];
  pumps: Pump[];
  pumpEvents: PumpEvent[];
}

export interface ModelsData {
  models: ModelData[];
}

export interface ModelData {
  model: string;
  description: string;
  price: number;
  bom: BOM;
  lead_times: LeadTimes;
}