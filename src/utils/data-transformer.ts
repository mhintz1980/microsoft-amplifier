/**
 * Data Transformation Utilities
 *
 * Converts between original and denormalized pump data models
 * Provides utilities for data migration and validation
 */

import {
  DenormalizedPumpModel,
  SimplifiedPump,
  SimplifiedPurchaseOrder,
  transformToDenormalizedModels,
  computePumpDerivedFields
} from '../types/denormalized-pump-model';

// ===== DATA MIGRATION =====

/**
 * Complete data migration from original format to denormalized format
 */
export interface MigratedData {
  models: Record<string, DenormalizedPumpModel>;
  pumps: SimplifiedPump[];
  purchaseOrders: SimplifiedPurchaseOrder[];
  productionStages: ProductionStage[];
  migrationMetadata: {
    migratedAt: string;
    version: string;
    originalDataChecksum: string;
    recordsMigrated: {
      models: number;
      pumps: number;
      purchaseOrders: number;
    };
  };
}

export interface ProductionStage {
  id: string;
  name: string;
  displayName: string;
  order: number;
  estimatedDays: number;
  color: string;
  isActive: boolean;
}

/**
 * Migrates original pumptracker data to denormalized format
 */
export function migrateOriginalData(originalData: any): MigratedData {
  const models = transformToDenormalizedModels(originalData);
  const productionStages = createProductionStages();

  // Create empty arrays for pumps and POs (they'll be created from user data)
  const pumps: SimplifiedPump[] = [];
  const purchaseOrders: SimplifiedPurchaseOrder[] = [];

  return {
    models,
    pumps,
    purchaseOrders,
    productionStages,
    migrationMetadata: {
      migratedAt: new Date().toISOString(),
      version: '1.0.0',
      originalDataChecksum: calculateChecksum(JSON.stringify(originalData)),
      recordsMigrated: {
        models: Object.keys(models).length,
        pumps: 0,
        purchaseOrders: 0
      }
    }
  };
}

/**
 * Creates standard production stages configuration
 */
export function createProductionStages(): ProductionStage[] {
  return [
    {
      id: 'not_started',
      name: 'not_started',
      displayName: 'Not Started',
      order: 0,
      estimatedDays: 0,
      color: '#94a3b8', // slate-500
      isActive: true
    },
    {
      id: 'fabrication',
      name: 'fabrication',
      displayName: 'Fabrication',
      order: 1,
      estimatedDays: 2, // Average from models
      color: '#3b82f6', // blue-500
      isActive: true
    },
    {
      id: 'powder_coat',
      name: 'powder_coat',
      displayName: 'Powder Coat',
      order: 2,
      estimatedDays: 7,
      color: '#a855f7', // purple-500
      isActive: true
    },
    {
      id: 'assembly',
      name: 'assembly',
      displayName: 'Assembly',
      order: 3,
      estimatedDays: 1.5,
      color: '#f59e0b', // amber-500
      isActive: true
    },
    {
      id: 'testing',
      name: 'testing',
      displayName: 'Testing',
      order: 4,
      estimatedDays: 0.5,
      color: '#10b981', // emerald-500
      isActive: true
    },
    {
      id: 'shipping',
      name: 'shipping',
      displayName: 'Shipping',
      order: 5,
      estimatedDays: 1,
      color: '#06b6d4', // cyan-500
      isActive: true
    },
    {
      id: 'completed',
      name: 'completed',
      displayName: 'Completed',
      order: 6,
      estimatedDays: 0,
      color: '#22c55e', // green-500
      isActive: true
    }
  ];
}

// ===== DATA VALIDATION =====

/**
 * Validates denormalized pump model data structure
 */
export function validateDenormalizedModel(model: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!model.id || typeof model.id !== 'string') {
    errors.push('Model must have a valid id');
  }

  if (!model.model || typeof model.model !== 'string') {
    errors.push('Model must have a valid model name');
  }

  if (!model.description || typeof model.description !== 'string') {
    errors.push('Model must have a valid description');
  }

  if (typeof model.totalBuildDays !== 'number' || model.totalBuildDays < 0) {
    errors.push('Model must have a valid totalBuildDays (non-negative number)');
  }

  if (!['diaphragm', 'rotary_lobe', 'centrifugal', 'piston', 'screw_impeller', 'vacuum_assisted'].includes(model.pumpType)) {
    errors.push('Model must have a valid pumpType');
  }

  if (typeof model.pumpSize !== 'number' || model.pumpSize < 1) {
    errors.push('Model must have a valid pumpSize (positive number)');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Validates simplified pump data structure
 */
export function validateSimplifiedPump(pump: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!pump.id || typeof pump.id !== 'string') {
    errors.push('Pump must have a valid id');
  }

  if (!pump.modelId || typeof pump.modelId !== 'string') {
    errors.push('Pump must have a valid modelId');
  }

  if (!pump.currentStage || typeof pump.currentStage !== 'string') {
    errors.push('Pump must have a valid currentStage');
  }

  if (!pump.stageEntryTime || isNaN(new Date(pump.stageEntryTime).getTime())) {
    errors.push('Pump must have a valid stageEntryTime (ISO date string)');
  }

  if (!['low', 'normal', 'high', 'urgent'].includes(pump.priority)) {
    errors.push('Pump must have a valid priority');
  }

  if (!pump.model || typeof pump.model !== 'object') {
    errors.push('Pump must have embedded model data');
  } else {
    const modelValidation = validateDenormalizedModel(pump.model);
    if (!modelValidation.isValid) {
      errors.push(`Invalid embedded model: ${modelValidation.errors.join(', ')}`);
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

// ===== DATA HELPERS =====

/**
 * Calculates checksum for data integrity verification
 */
export function calculateChecksum(data: string): string {
  // Simple hash function for checksum
  let hash = 0;
  for (let i = 0; i < data.length; i++) {
    const char = data.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(16);
}

/**
 * Generates a unique pump ID
 */
export function generatePumpId(): string {
  return `pump_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Generates a unique PO ID
 */
export function generatePurchaseOrderId(): string {
  return `po_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Calculates estimated completion date based on model and current stage
 */
export function calculateEstimatedCompletionDate(
  model: DenormalizedPumpModel,
  currentStage: string,
  stageEntryTime: string
): string {
  const stages = createProductionStages();
  const currentStageIndex = stages.findIndex(s => s.id === currentStage);

  if (currentStageIndex === -1) {
    return stageEntryTime;
  }

  let totalRemainingDays = 0;
  for (let i = currentStageIndex + 1; i < stages.length; i++) {
    totalRemainingDays += stages[i].estimatedDays;
  }

  const entryDate = new Date(stageEntryTime);
  const completionDate = new Date(entryDate.getTime() + (totalRemainingDays * 24 * 60 * 60 * 1000));

  return completionDate.toISOString();
}

/**
 * Creates a new pump with derived fields calculated
 */
export function createSimplifiedPump(
  model: DenormalizedPumpModel,
  purchaseOrderData: {
    poNumber: string;
    customerName: string;
    orderDate: string;
  },
  overrides: Partial<SimplifiedPump> = {}
): SimplifiedPump {
  const now = new Date().toISOString();
  const pump: SimplifiedPump = {
    id: generatePumpId(),
    modelId: model.id,
    serialNumber: null,
    model,
    currentStage: 'not_started',
    previousStage: null,
    stageEntryTime: now,
    estimatedCompletionDate: null,
    actualCompletionDate: null,
    priority: 'normal',
    scheduledStartDate: null,
    scheduledEndDate: null,
    purchaseOrderNumber: purchaseOrderData.poNumber,
    customerName: purchaseOrderData.customerName,
    purchaseOrderDate: purchaseOrderData.orderDate,
    location: null,
    assignedTo: null,
    qualityStatus: 'pending',
    qualityNotes: null,
    daysInCurrentStage: 0,
    isOverdue: false,
    buildProgress: 0,
    createdAt: now,
    updatedAt: now,
    createdById: null,
    notes: null,
    ...overrides
  };

  // Calculate derived fields
  const derived = computePumpDerivedFields(pump);
  return { ...pump, ...derived };
}

/**
 * Updates pump stage and recalculates derived fields
 */
export function updatePumpStage(
  pump: SimplifiedPump,
  newStage: string,
  notes?: string
): SimplifiedPump {
  const now = new Date().toISOString();
  const updatedPump: SimplifiedPump = {
    ...pump,
    previousStage: pump.currentStage,
    currentStage: newStage as any,
    stageEntryTime: now,
    updatedAt: now,
    notes: notes || pump.notes
  };

  // Calculate estimated completion date
  updatedPump.estimatedCompletionDate = calculateEstimatedCompletionDate(
    updatedPump.model,
    newStage,
    now
  );

  // Recalculate derived fields
  const derived = computePumpDerivedFields(updatedPump);
  return { ...updatedPump, ...derived };
}

// ===== DATA EXPORT =====

/**
 * Exports denormalized data back to original format (for compatibility)
 */
export function exportToOriginalFormat(denormalizedData: {
  models: Record<string, DenormalizedPumpModel>;
}): any {
  const models = Object.values(denormalizedData.models).map(model => ({
    model: model.model,
    description: model.description,
    price: model.basePrice,
    bom: {
      engine: model.engineModel,
      gearbox: model.gearboxModel,
      control_panel: model.controlPanelModel
    },
    lead_times: {
      fabrication: model.fabricationDays,
      powder_coat: model.powderCoatDays,
      assembly: model.assemblyDays,
      testing: model.testingDays,
      total_days: model.totalBuildDays
    }
  }));

  return { models };
}

/**
 * Generates data summary report
 */
export function generateDataSummary(data: {
  models: Record<string, DenormalizedPumpModel>;
  pumps: SimplifiedPump[];
  purchaseOrders: SimplifiedPurchaseOrder[];
}): any {
  const { models, pumps, purchaseOrders } = data;

  return {
    summary: {
      totalModels: Object.keys(models).length,
      totalPumps: pumps.length,
      totalPurchaseOrders: purchaseOrders.length,
      generatedAt: new Date().toISOString()
    },
    models: {
      byType: Object.values(models).reduce((acc, model) => {
        acc[model.pumpType] = (acc[model.pumpType] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      bySize: Object.values(models).reduce((acc, model) => {
        const size = `${model.pumpSize}"`;
        acc[size] = (acc[size] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      enclosed: Object.values(models).filter(m => m.isEnclosed).length
    },
    pumps: {
      byStage: pumps.reduce((acc, pump) => {
        acc[pump.currentStage] = (acc[pump.currentStage] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      overdue: pumps.filter(p => p.isOverdue).length,
      withoutSerial: pumps.filter(p => !pump.serialNumber).length,
      highPriority: pumps.filter(p => p.priority === 'high' || p.priority === 'urgent').length
    },
    purchaseOrders: {
      byStatus: purchaseOrders.reduce((acc, po) => {
        acc[po.status] = (acc[po.status] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      totalValue: purchaseOrders.reduce((sum, po) => sum + (po.totalValue || 0), 0)
    }
  };
}