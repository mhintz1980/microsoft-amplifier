/**
 * Denormalized Pump Data Model - Optimized for UI Consumption
 *
 * This model flattens nested structures and adds computed fields to reduce
 * data transformation overhead in the UI layer.
 */

// ===== CORE TYPES =====

/**
 * Denormalized Pump Model with flattened BOM and computed fields
 */
export interface DenormalizedPumpModel {
  id: string;
  model: string;
  description: string;

  // Pricing (flat)
  basePrice: number | null;

  // Build time (flattened from nested leadTimes)
  totalBuildDays: number;
  fabricationDays: number;
  powderCoatDays: number;
  assemblyDays: number;
  testingDays: number;

  // BOM (flattened for direct UI access)
  engineModel: string | null;
  gearboxModel: string | null;
  controlPanelModel: string | null;

  // Computed fields for UI optimization
  isEnclosed: boolean;
  pumpType: 'diaphragm' | 'rotary_lobe' | 'centrifugal' | 'piston' | 'screw_impeller' | 'vacuum_assisted';
  pumpSize: number; // Extracted from description (e.g., 4, 6, 8, 12)

  // Search/display helpers
  searchableText: string; // Concatenated search terms
  displayCategory: string; // UI-friendly category name

  // Metadata
  isActive: boolean;
  sortOrder: number;
}

/**
 * Simplified Pump entity with embedded model data
 */
export interface SimplifiedPump {
  id: string;

  // Core identifiers
  modelId: string;
  serialNumber: string | null;

  // Embedded model data (denormalized for UI performance)
  model: DenormalizedPumpModel;

  // Production tracking
  currentStage: ProductionStage;
  previousStage: ProductionStage | null;
  stageEntryTime: string; // ISO string
  estimatedCompletionDate: string | null; // ISO string
  actualCompletionDate: string | null; // ISO string

  // Priority and scheduling
  priority: Priority;
  scheduledStartDate: string | null; // ISO string
  scheduledEndDate: string | null; // ISO string

  // Purchase order info (denormalized)
  purchaseOrderNumber: string;
  customerName: string;
  purchaseOrderDate: string; // ISO string

  // Location tracking
  location: string | null;
  assignedTo: string | null;

  // Quality control
  qualityStatus: QualityStatus;
  qualityNotes: string | null;

  // Computed fields for UI
  daysInCurrentStage: number;
  isOverdue: boolean;
  buildProgress: number; // 0-100 percentage

  // Metadata
  createdAt: string; // ISO string
  updatedAt: string; // ISO string
  createdById: string | null;
  notes: string | null;
}

/**
 * Production stage with computed timing
 */
export interface ProductionStage {
  id: string;
  name: string;
  displayName: string;
  order: number;
  estimatedDays: number;
  color: string; // UI color code
  isActive: boolean;
}

/**
 * Purchase order with embedded pump count and status
 */
export interface SimplifiedPurchaseOrder {
  id: string;
  poNumber: string;
  customerName: string;
  orderDate: string; // ISO string
  requestedDeliveryDate: string | null; // ISO string
  actualDeliveryDate: string | null; // ISO string

  // Status tracking
  status: POStatus;

  // Computed fields
  totalPumps: number;
  pumpsCompleted: number;
  pumpsInProgress: number;
  completionPercentage: number;

  // Financial summary (denormalized)
  totalValue: number | null;
  paidAmount: number | null;
  balanceAmount: number | null;

  // Metadata
  createdAt: string; // ISO string
  updatedAt: string; // ISO string
  notes: string | null;
  salesRepresentative: string | null;
}

// ===== ENUMS =====

export type Priority = 'low' | 'normal' | 'high' | 'urgent';
export type QualityStatus = 'pending' | 'in_progress' | 'passed' | 'failed' | 'rework_required';
export type POStatus = 'draft' | 'confirmed' | 'in_production' | 'completed' | 'cancelled' | 'on_hold';

// ===== UI HELPER TYPES =====

/**
 * Filter configuration for UI
 */
export interface PumpFilters {
  searchText: string;
  customers: string[];
  models: string[];
  stages: string[];
  priorities: Priority[];
  dateRange: {
    start: string | null;
    end: string | null;
  };
  showOverdueOnly: boolean;
  showWithoutSerial: boolean;
}

/**
 * Dashboard metrics (computed)
 */
export interface DashboardMetrics {
  totalPumps: number;
  pumpsByStage: Record<string, number>;
  overduePumps: number;
  highPriorityPumps: number;
  completionRate: number;
  averageBuildTime: number;
  upcomingDeadlines: Array<{
    pumpId: string;
    pumpSerial: string | null;
    customer: string;
    daysRemaining: number;
  }>;
  customerSummary: Array<{
    customerName: string;
    totalPumps: number;
    completedPumps: number;
    inProgressPumps: number;
  }>;
}

// ===== DATA TRANSFORMATION UTILITIES =====

/**
 * Transforms original pumptracker-data.json into denormalized models
 */
export function transformToDenormalizedModels(originalData: any): Record<string, DenormalizedPumpModel> {
  const models: Record<string, DenormalizedPumpModel> = {};

  originalData.models.forEach((model: any, index: number) => {
    const pumpType = determinePumpType(model.model, model.description);
    const pumpSize = extractPumpSize(model.description);
    const isEnclosed = model.model.includes('SAFE');

    models[model.model] = {
      id: model.model,
      model: model.model,
      description: model.description,
      basePrice: model.price,
      totalBuildDays: model.lead_times.total_days,
      fabricationDays: model.lead_times.fabrication,
      powderCoatDays: model.lead_times.powder_coat,
      assemblyDays: model.lead_times.assembly,
      testingDays: model.lead_times.testing,
      engineModel: model.bom.engine,
      gearboxModel: model.bom.gearbox,
      controlPanelModel: model.bom.control_panel,
      isEnclosed,
      pumpType,
      pumpSize,
      searchableText: `${model.model} ${model.description} ${model.bom.engine || ''} ${model.bom.gearbox || ''}`.toLowerCase(),
      displayCategory: `${pumpSize}" ${pumpType.replace('_', ' ')}${isEnclosed ? ' (Enclosed)' : ''}`,
      isActive: true,
      sortOrder: index
    };
  });

  return models;
}

/**
 * Helper functions for data transformation
 */
function determinePumpType(model: string, description: string): DenormalizedPumpModel['pumpType'] {
  if (model.includes('DD')) return 'diaphragm';
  if (model.includes('RL')) return 'rotary_lobe';
  if (model.includes('HC')) return 'centrifugal';
  if (model.includes('PP')) return 'piston';
  if (model.includes('SIP')) return 'screw_impeller';
  if (model.includes('DV') || model.includes('DP')) return 'vacuum_assisted';
  return 'diaphragm'; // fallback
}

function extractPumpSize(description: string): number {
  const match = description.match(/(\d+)"?/);
  return match ? parseInt(match[1]) : 0;
}

/**
 * Computes derived fields for a pump
 */
export function computePumpDerivedFields(pump: SimplifiedPump): Partial<SimplifiedPump> {
  const now = new Date();
  const stageEntry = new Date(pump.stageEntryTime);
  const daysInStage = Math.floor((now.getTime() - stageEntry.getTime()) / (1000 * 60 * 60 * 24));

  let estimatedCompletionDate: string | null = null;
  let buildProgress = 0;
  let isOverdue = false;

  if (pump.scheduledEndDate) {
    const dueDate = new Date(pump.scheduledEndDate);
    isOverdue = now > dueDate && pump.currentStage !== 'completed';
    estimatedCompletionDate = pump.scheduledEndDate;
  } else {
    // Calculate from stage entry + estimated days
    const totalDays = pump.model.totalBuildDays;
    const estimated = new Date(stageEntry.getTime() + (totalDays * 24 * 60 * 60 * 1000));
    estimatedCompletionDate = estimated.toISOString();
    isOverdue = now > estimated;
  }

  // Calculate progress based on current stage
  const stages = ['not_started', 'fabrication', 'powder_coat', 'assembly', 'testing', 'shipping', 'completed'];
  const currentStageIndex = stages.indexOf(pump.currentStage as any);
  buildProgress = (currentStageIndex / (stages.length - 1)) * 100;

  return {
    daysInCurrentStage: daysInStage,
    isOverdue,
    buildProgress,
    estimatedCompletionDate
  };
}