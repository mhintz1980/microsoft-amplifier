/**
 * Denormalized PumpTracker Store
 *
 * Zustand store optimized for denormalized pump data model.
 * Provides efficient state management with minimal data transformation.
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { nanoid } from 'nanoid';

// Types
import {
  DenormalizedPumpModel,
  SimplifiedPump,
  SimplifiedPurchaseOrder,
  ProductionStage,
  PumpFilters,
  DashboardMetrics,
  Priority,
  QualityStatus,
  POStatus,
  computePumpDerivedFields
} from '../types/denormalized-pump-model';

// Import catalog data for lead times
import pumptrackerData from '../../pumptracker-manus/src/data/pumptracker-data.json';

// Catalog data types
interface CatalogModel {
  model: string;
  description: string;
  price: number | null;
  bom: {
    engine: string | null;
    gearbox: string | null;
    control_panel: string | null;
  };
  lead_times: {
    fabrication: number;
    powder_coat: number;
    assembly: number;
    testing: number;
    total_days: number;
  };
}

interface CatalogData {
  models: CatalogModel[];
  customers: string[];
  productionStages: string[];
}

// ===== CATALOG DATA ACCESS UTILITIES =====

/**
 * Get model lead times from catalog data
 * @param modelId - The model identifier (e.g., "DD-4S", "RL200")
 * @returns Lead times object or null if model not found
 */
export function getModelLeadTimes(modelId: string): CatalogModel['lead_times'] | null {
  try {
    const catalog = pumptrackerData as CatalogData;
    const model = catalog.models.find(m => m.model === modelId);
    return model ? model.lead_times : null;
  } catch (error) {
    console.error(`Error getting lead times for model ${modelId}:`, error);
    return null;
  }
}

/**
 * Get all models from catalog data
 * @returns Array of catalog models
 */
export function getCatalogModels(): CatalogModel[] {
  try {
    const catalog = pumptrackerData as CatalogData;
    return catalog.models || [];
  } catch (error) {
    console.error('Error getting catalog models:', error);
    return [];
  }
}

/**
 * Get a specific model from catalog data
 * @param modelId - The model identifier
 * @returns Catalog model or null if not found
 */
export function getCatalogModel(modelId: string): CatalogModel | null {
  try {
    const catalog = pumptrackerData as CatalogData;
    return catalog.models.find(m => m.model === modelId) || null;
  } catch (error) {
    console.error(`Error getting catalog model ${modelId}:`, error);
    return null;
  }
}

/**
 * Convert catalog model to denormalized pump model format
 * @param catalogModel - Catalog model to convert
 * @returns DenormalizedPumpModel
 */
export function catalogModelToDenormalized(catalogModel: CatalogModel): DenormalizedPumpModel {
  return {
    id: catalogModel.model,
    modelId: catalogModel.model,
    name: catalogModel.description,
    description: catalogModel.description,
    category: 'Standard', // Default category
    specifications: {
      flowRate: null,
      pressure: null,
      power: null,
      speed: null,
      material: null,
      weight: null,
      dimensions: null
    },
    bom: {
      engine: catalogModel.bom.engine || null,
      gearbox: catalogModel.bom.gearbox || null,
      controlPanel: catalogModel.bom.control_panel || null,
      additionalComponents: []
    },
    pricing: {
      basePrice: catalogModel.price || 0,
      laborCost: 0,
      materialCost: 0,
      totalPrice: catalogModel.price || 0,
      currency: 'USD'
    },
    leadTimes: {
      fabrication: catalogModel.lead_times.fabrication,
      assembly: catalogModel.lead_times.assembly,
      testing: catalogModel.lead_times.testing,
      finishing: catalogModel.lead_times.powder_coat,
      totalDays: catalogModel.lead_times.total_days
    },
    qualityRequirements: {
      minQualityScore: 80,
      requiredTests: ['performance', 'safety'],
      passCriteria: {}
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    isActive: true
  };
}

/**
 * Load all catalog models as denormalized pump models
 * @returns Record of denormalized pump models keyed by model ID
 */
export function loadCatalogModelsAsDenormalized(): Record<string, DenormalizedPumpModel> {
  const catalogModels = getCatalogModels();
  return catalogModels.reduce((acc, catalogModel) => {
    const denormalizedModel = catalogModelToDenormalized(catalogModel);
    acc[denormalizedModel.id] = denormalizedModel;
    return acc;
  }, {} as Record<string, DenormalizedPumpModel>);
}

// ===== UTILITY FUNCTIONS FOR STORE OPERATIONS =====

/**
 * Create a simplified pump from a model and order data
 */
function createSimplifiedPump(
  model: DenormalizedPumpModel,
  orderData: {
    poNumber: string;
    customerName: string;
    orderDate: string;
  },
  overrides?: Partial<SimplifiedPump>
): SimplifiedPump {
  const pumpId = nanoid();
  const now = new Date().toISOString();

  const basePump: SimplifiedPump = {
    id: pumpId,
    modelId: model.id,
    purchaseOrderNumber: orderData.poNumber,
    customerName: orderData.customerName,
    serialNumber: null,
    currentStage: 'not_started',
    priority: 'normal',
    status: 'on_track',
    notes: null,

    // Model data (embedded)
    model: {
      id: model.id,
      modelId: model.id,
      name: model.name,
      description: model.description,
      category: model.category,
      specifications: model.specifications,
      bom: model.bom,
      pricing: model.pricing,
      leadTimes: model.leadTimes,
      qualityRequirements: model.qualityRequirements,
      searchableText: `${model.id} ${model.name} ${model.description}`.toLowerCase()
    },

    // Dates
    createdAt: now,
    updatedAt: now,
    estimatedCompletionDate: null,
    actualCompletionDate: null,

    // Computed fields (will be calculated by computePumpDerivedFields)
    isOverdue: false,
    completionPercentage: 0,
    timeInCurrentStage: 0
  };

  // Apply any overrides
  const pumpWithOverrides = { ...basePump, ...overrides };

  // Calculate derived fields
  const derivedFields = computePumpDerivedFields(pumpWithOverrides);

  return { ...pumpWithOverrides, ...derivedFields };
}

/**
 * Update pump stage and related fields
 */
function updatePumpStage(
  pump: SimplifiedPump,
  newStage: string,
  notes?: string
): SimplifiedPump {
  const now = new Date().toISOString();

  return {
    ...pump,
    currentStage: newStage,
    notes: notes || pump.notes,
    updatedAt: now,
    // Update derived fields
    ...computePumpDerivedFields({
      ...pump,
      currentStage: newStage,
      updatedAt: now
    })
  };
}

// Store State Interface
interface PumpTrackerState {
  // Data
  models: Record<string, DenormalizedPumpModel>;
  pumps: Record<string, SimplifiedPump>; // Changed from array to object for O(1) lookups
  purchaseOrders: Record<string, SimplifiedPurchaseOrder>; // Changed from array to object
  productionStages: ProductionStage[];

  // UI State
  filters: PumpFilters;
  selectedPumpIds: string[];
  selectedPurchaseOrderId: string | null;
  viewMode: 'dashboard' | 'kanban';
  collapsedStages: string[];

  // Loading state
  isLoading: boolean;
  lastSavedAt: string | null;
  error: string | null;
}

// Store Actions Interface
interface PumpTrackerActions {
  // Data loading
  loadModels: (models: Record<string, DenormalizedPumpModel>) => void;
  loadCatalogModels: () => void;
  loadData: (data: {
    pumps?: SimplifiedPump[];
    purchaseOrders?: SimplifiedPurchaseOrder[];
  }) => void;

  // Pump management
  addPump: (pumpData: {
    modelId: string;
    purchaseOrderNumber: string;
    customerName: string;
    purchaseOrderDate: string;
    overrides?: Partial<SimplifiedPump>;
  }) => string;
  updatePump: (pumpId: string, updates: Partial<SimplifiedPump>) => void;
  movePumpStage: (pumpId: string, newStage: string, notes?: string) => void;
  deletePump: (pumpId: string) => void;
  assignSerialNumber: (pumpId: string, serialNumber: string) => void;
  updatePumpPriority: (pumpId: string, priority: Priority) => void;

  // Purchase order management
  addPurchaseOrder: (poData: {
    poNumber: string;
    customerName: string;
    orderDate: string;
    pumps?: Array<{
      modelId: string;
      quantity: number;
      overrides?: Partial<SimplifiedPump>;
    }>;
  }) => string;
  updatePurchaseOrder: (poId: string, updates: Partial<SimplifiedPurchaseOrder>) => void;
  deletePurchaseOrder: (poId: string) => void;

  // Selection and UI
  selectPump: (pumpId: string, multiSelect?: boolean) => void;
  deselectPump: (pumpId: string) => void;
  selectAllPumps: () => void;
  clearSelection: () => void;
  setSelectedPurchaseOrder: (poId: string | null) => void;

  // Filtering
  updateFilters: (filters: Partial<PumpFilters>) => void;
  clearFilters: () => void;
  setViewMode: (mode: 'dashboard' | 'kanban') => void;
  toggleStageCollapsed: (stageId: string) => void;

  // Utility
  refreshDerivedFields: () => void;
  exportData: () => string;
  resetStore: () => void;
}

// Store Definition
export const usePumpTrackerStore = create<PumpTrackerState & PumpTrackerActions>()(
  persist(
    (set, get) => ({
      // Initial State
      models: {},
      pumps: {},
      purchaseOrders: {},
      productionStages: [],

      // UI State
      filters: {
        searchText: '',
        customers: [],
        models: [],
        stages: [],
        priorities: [],
        dateRange: { start: null, end: null },
        showOverdueOnly: false,
        showWithoutSerial: false
      },
      selectedPumpIds: [],
      selectedPurchaseOrderId: null,
      viewMode: 'dashboard',
      collapsedStages: [],

      // Loading state
      isLoading: false,
      lastSavedAt: null,
      error: null,

      // Actions
      loadModels: (models) => set({ models }),

      loadCatalogModels: () => {
        try {
          const catalogModels = loadCatalogModelsAsDenormalized();
          const catalog = pumptrackerData as CatalogData;

          // Convert catalog production stages to the expected format
          const productionStages: ProductionStage[] = catalog.productionStages.map((stageName, index) => ({
            id: stageName.toUpperCase(),
            name: stageName,
            displayName: stageName,
            description: `${stageName} production stage`,
            order: index,
            color: `hsl(${index * 60}, 70%, 50%)`, // Generate different colors for each stage
            isActive: true,
            estimatedDays: null,
            requirements: {
              skills: [],
              tools: [],
              materials: [],
              qualityChecks: []
            }
          }));

          set({
            models: catalogModels,
            productionStages
          });
        } catch (error) {
          console.error('Failed to load catalog models:', error);
          set({ error: error instanceof Error ? error.message : 'Failed to load catalog models' });
        }
      },

      loadData: (data) => set((state) => {
        const newState = { ...state };

        if (data.pumps) {
          const pumpsObject = data.pumps.reduce((acc, pump) => {
            acc[pump.id] = pump;
            return acc;
          }, {} as Record<string, SimplifiedPump>);
          newState.pumps = { ...state.pumps, ...pumpsObject };
        }

        if (data.purchaseOrders) {
          const poObject = data.purchaseOrders.reduce((acc, po) => {
            acc[po.id] = po;
            return acc;
          }, {} as Record<string, SimplifiedPurchaseOrder>);
          newState.purchaseOrders = { ...state.purchaseOrders, ...poObject };
        }

        return newState;
      }),

      addPump: (pumpData) => {
        const state = get();
        const model = state.models[pumpData.modelId];
        if (!model) {
          throw new Error(`Model not found: ${pumpData.modelId}`);
        }

        const pump = createSimplifiedPump(model, {
          poNumber: pumpData.purchaseOrderNumber,
          customerName: pumpData.customerName,
          orderDate: pumpData.purchaseOrderDate
        }, pumpData.overrides);

        set((prevState) => ({
          pumps: { ...prevState.pumps, [pump.id]: pump },
          lastSavedAt: new Date().toISOString()
        }));

        return pump.id;
      },

      updatePump: (pumpId, updates) => set((state) => {
        const pump = state.pumps[pumpId];
        if (!pump) return state;

        const updatedPump = { ...pump, ...updates, updatedAt: new Date().toISOString() };
        const withDerivedFields = { ...updatedPump, ...computePumpDerivedFields(updatedPump) };

        return {
          pumps: { ...state.pumps, [pumpId]: withDerivedFields },
          lastSavedAt: new Date().toISOString()
        };
      }),

      movePumpStage: (pumpId, newStage, notes) => set((state) => {
        const pump = state.pumps[pumpId];
        if (!pump) return state;

        const updatedPump = updatePumpStage(pump, newStage, notes);

        return {
          pumps: { ...state.pumps, [pumpId]: updatedPump },
          lastSavedAt: new Date().toISOString()
        };
      }),

      deletePump: (pumpId) => set((state) => {
        const newPumps = { ...state.pumps };
        delete newPumps[pumpId];

        return {
          pumps: newPumps,
          selectedPumpIds: state.selectedPumpIds.filter(id => id !== pumpId),
          lastSavedAt: new Date().toISOString()
        };
      }),

      assignSerialNumber: (pumpId, serialNumber) => set((state) => {
        const pump = state.pumps[pumpId];
        if (!pump) return state;

        return {
          pumps: {
            ...state.pumps,
            [pumpId]: {
              ...pump,
              serialNumber,
              updatedAt: new Date().toISOString()
            }
          },
          lastSavedAt: new Date().toISOString()
        };
      }),

      updatePumpPriority: (pumpId, priority) => set((state) => {
        const pump = state.pumps[pumpId];
        if (!pump) return state;

        const updatedPump = { ...pump, priority, updatedAt: new Date().toISOString() };
        const withDerivedFields = { ...updatedPump, ...computePumpDerivedFields(updatedPump) };

        return {
          pumps: { ...state.pumps, [pumpId]: withDerivedFields },
          lastSavedAt: new Date().toISOString()
        };
      }),

      addPurchaseOrder: (poData) => {
        const poId = nanoid();
        const now = new Date().toISOString();

        const newPO: SimplifiedPurchaseOrder = {
          id: poId,
          poNumber: poData.poNumber,
          customerName: poData.customerName,
          orderDate: poData.orderDate,
          requestedDeliveryDate: null,
          actualDeliveryDate: null,
          status: 'confirmed',
          totalPumps: poData.pumps?.length || 0,
          pumpsCompleted: 0,
          pumpsInProgress: 0,
          completionPercentage: 0,
          totalValue: null,
          paidAmount: null,
          balanceAmount: null,
          createdAt: now,
          updatedAt: now,
          notes: null,
          salesRepresentative: null
        };

        set((state) => ({
          purchaseOrders: { ...state.purchaseOrders, [poId]: newPO },
          lastSavedAt: now
        }));

        // Add pumps if provided
        if (poData.pumps) {
          poData.pumps.forEach(pumpSpec => {
            for (let i = 0; i < pumpSpec.quantity; i++) {
              get().addPump({
                modelId: pumpSpec.modelId,
                purchaseOrderNumber: poData.poNumber,
                customerName: poData.customerName,
                purchaseOrderDate: poData.orderDate,
                overrides: pumpSpec.overrides
              });
            }
          });
        }

        return poId;
      },

      updatePurchaseOrder: (poId, updates) => set((state) => {
        const po = state.purchaseOrders[poId];
        if (!po) return state;

        const updatedPO = { ...po, ...updates, updatedAt: new Date().toISOString() };

        return {
          purchaseOrders: { ...state.purchaseOrders, [poId]: updatedPO },
          lastSavedAt: new Date().toISOString()
        };
      }),

      deletePurchaseOrder: (poId) => set((state) => {
        const newPOs = { ...state.purchaseOrders };
        delete newPOs[poId];

        // Remove pumps associated with this PO
        const newPumps = { ...state.pumps };
        Object.keys(newPumps).forEach(pumpId => {
          if (newPumps[pumpId].purchaseOrderNumber === state.purchaseOrders[poId]?.poNumber) {
            delete newPumps[pumpId];
          }
        });

        return {
          purchaseOrders: newPOs,
          pumps: newPumps,
          selectedPurchaseOrderId: state.selectedPurchaseOrderId === poId ? null : state.selectedPurchaseOrderId,
          lastSavedAt: new Date().toISOString()
        };
      }),

      selectPump: (pumpId, multiSelect = false) => set((state) => {
        if (multiSelect) {
          const isSelected = state.selectedPumpIds.includes(pumpId);
          return {
            selectedPumpIds: isSelected
              ? state.selectedPumpIds.filter(id => id !== pumpId)
              : [...state.selectedPumpIds, pumpId]
          };
        } else {
          return { selectedPumpIds: [pumpId] };
        }
      }),

      deselectPump: (pumpId) => set((state) => ({
        selectedPumpIds: state.selectedPumpIds.filter(id => id !== pumpId)
      })),

      selectAllPumps: () => set((state) => {
        const filteredPumpIds = getFilteredPumpIds(state);
        return { selectedPumpIds: filteredPumpIds };
      }),

      clearSelection: () => set({ selectedPumpIds: [] }),

      setSelectedPurchaseOrder: (poId) => set({ selectedPurchaseOrderId: poId }),

      updateFilters: (filters) => set((state) => ({
        filters: { ...state.filters, ...filters }
      })),

      clearFilters: () => set({
        filters: {
          searchText: '',
          customers: [],
          models: [],
          stages: [],
          priorities: [],
          dateRange: { start: null, end: null },
          showOverdueOnly: false,
          showWithoutSerial: false
        }
      }),

      setViewMode: (mode) => set({ viewMode: mode }),

      toggleStageCollapsed: (stageId) => set((state) => ({
        collapsedStages: state.collapsedStages.includes(stageId)
          ? state.collapsedStages.filter(id => id !== stageId)
          : [...state.collapsedStages, stageId]
      })),

      refreshDerivedFields: () => set((state) => {
        const updatedPumps = { ...state.pumps };
        Object.keys(updatedPumps).forEach(pumpId => {
          const derived = computePumpDerivedFields(updatedPumps[pumpId]);
          updatedPumps[pumpId] = { ...updatedPumps[pumpId], ...derived };
        });
        return { pumps: updatedPumps };
      }),

      exportData: () => {
        const state = get();
        return JSON.stringify({
          models: state.models,
          pumps: Object.values(state.pumps),
          purchaseOrders: Object.values(state.purchaseOrders),
          productionStages: state.productionStages,
          exportedAt: new Date().toISOString()
        }, null, 2);
      },

      resetStore: () => set({
        pumps: {},
        purchaseOrders: {},
        selectedPumpIds: [],
        selectedPurchaseOrderId: null,
        filters: {
          searchText: '',
          customers: [],
          models: [],
          stages: [],
          priorities: [],
          dateRange: { start: null, end: null },
          showOverdueOnly: false,
          showWithoutSerial: false
        },
        lastSavedAt: new Date().toISOString()
      })
    }),
    {
      name: 'pumptracker-denormalized-v2-catalog-integrated',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        pumps: state.pumps,
        purchaseOrders: state.purchaseOrders,
        selectedPumpIds: state.selectedPumpIds,
        selectedPurchaseOrderId: state.selectedPurchaseOrderId,
        filters: state.filters,
        viewMode: state.viewMode,
        collapsedStages: state.collapsedStages,
        lastSavedAt: state.lastSavedAt
      })
    }
  )
);

// ===== SELECTORS (Optimized for Denormalized Data) =====

/**
 * Get filtered pump IDs based on current filters
 */
function getFilteredPumpIds(state: PumpTrackerState): string[] {
  const { pumps, filters } = state;
  let pumpIds = Object.keys(pumps);

  // Text search (uses pre-computed searchableText)
  if (filters.searchText) {
    const searchLower = filters.searchText.toLowerCase();
    pumpIds = pumpIds.filter(id => {
      const pump = pumps[id];
      return (
        pump.model.searchableText.includes(searchLower) ||
        pump.serialNumber?.toLowerCase().includes(searchLower) ||
        pump.customerName.toLowerCase().includes(searchLower) ||
        pump.notes?.toLowerCase().includes(searchLower)
      );
    });
  }

  // Customer filter
  if (filters.customers.length > 0) {
    pumpIds = pumpIds.filter(id => filters.customers.includes(pumps[id].customerName));
  }

  // Model filter
  if (filters.models.length > 0) {
    pumpIds = pumpIds.filter(id => filters.models.includes(pumps[id].modelId));
  }

  // Stage filter
  if (filters.stages.length > 0) {
    pumpIds = pumpIds.filter(id => filters.stages.includes(pumps[id].currentStage));
  }

  // Priority filter
  if (filters.priorities.length > 0) {
    pumpIds = pumpIds.filter(id => filters.priorities.includes(pumps[id].priority));
  }

  // Overdue filter
  if (filters.showOverdueOnly) {
    pumpIds = pumpIds.filter(id => pumps[id].isOverdue);
  }

  // Without serial filter
  if (filters.showWithoutSerial) {
    pumpIds = pumpIds.filter(id => !pumps[id].serialNumber);
  }

  // Date range filter
  if (filters.dateRange.start || filters.dateRange.end) {
    pumpIds = pumpIds.filter(id => {
      const pumpDate = new Date(pumps[id].createdAt);
      const start = filters.dateRange.start ? new Date(filters.dateRange.start) : null;
      const end = filters.dateRange.end ? new Date(filters.dateRange.end) : null;

      if (start && pumpDate < start) return false;
      if (end && pumpDate > end) return false;
      return true;
    });
  }

  return pumpIds;
}

/**
 * Get pumps grouped by stage (optimized for Kanban view)
 */
export const usePumpsByStage = () => {
  const pumps = usePumpTrackerStore(state => state.pumps);
  const filters = usePumpTrackerStore(state => state.filters);
  const productionStages = usePumpTrackerStore(state => state.productionStages);

  const filteredPumpIds = getFilteredPumpIds({ pumps, filters } as PumpTrackerState);

  return productionStages.reduce((acc, stage) => {
    const stagePumps = filteredPumpIds
      .map(id => pumps[id])
      .filter(pump => pump.currentStage === stage.id)
      .sort((a, b) => {
        // Sort by priority first, then by creation date
        const priorityOrder = { urgent: 0, high: 1, normal: 2, low: 3 };
        const aPriority = priorityOrder[a.priority];
        const bPriority = priorityOrder[b.priority];

        if (aPriority !== bPriority) {
          return aPriority - bPriority;
        }

        return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
      });

    acc[stage.id] = stagePumps;
    return acc;
  }, {} as Record<string, SimplifiedPump[]>);
};

/**
 * Get dashboard metrics
 */
export const useDashboardMetrics = (): DashboardMetrics => {
  const pumps = usePumpTrackerStore(state => state.pumps);
  const purchaseOrders = usePumpTrackerStore(state => state.purchaseOrders);
  const productionStages = usePumpTrackerStore(state => state.productionStages);

  const allPumps = Object.values(pumps);
  const allPOs = Object.values(purchaseOrders);

  // Calculate metrics
  const pumpsByStage = productionStages.reduce((acc, stage) => {
    acc[stage.displayName] = allPumps.filter(pump => pump.currentStage === stage.id).length;
    return acc;
  }, {} as Record<string, number>);

  const overduePumps = allPumps.filter(pump => pump.isOverdue).length;
  const highPriorityPumps = allPumps.filter(pump => pump.priority === 'high' || pump.priority === 'urgent').length;

  const completedPumps = allPumps.filter(pump => pump.currentStage === 'completed').length;
  const completionRate = allPumps.length > 0 ? (completedPumps / allPumps.length) * 100 : 0;

  // Calculate average build time for completed pumps
  const completedPumpsWithTime = allPumps.filter(pump =>
    pump.currentStage === 'completed' && pump.actualCompletionDate
  );
  const averageBuildTime = completedPumpsWithTime.length > 0
    ? completedPumpsWithTime.reduce((sum, pump) => {
        const start = new Date(pump.createdAt).getTime();
        const end = new Date(pump.actualCompletionDate!).getTime();
        return sum + (end - start) / (1000 * 60 * 60 * 24); // Convert to days
      }, 0) / completedPumpsWithTime.length
    : 0;

  // Upcoming deadlines (next 7 days)
  const sevenDaysFromNow = new Date();
  sevenDaysFromNow.setDate(sevenDaysFromNow.getDate() + 7);

  const upcomingDeadlines = allPumps
    .filter(pump =>
      pump.estimatedCompletionDate &&
      new Date(pump.estimatedCompletionDate) <= sevenDaysFromNow &&
      pump.currentStage !== 'completed'
    )
    .map(pump => ({
      pumpId: pump.id,
      pumpSerial: pump.serialNumber,
      customer: pump.customerName,
      daysRemaining: Math.ceil(
        (new Date(pump.estimatedCompletionDate!).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
      )
    }))
    .sort((a, b) => a.daysRemaining - b.daysRemaining)
    .slice(0, 10);

  // Customer summary
  const customerSummary = Object.values(
    allPumps.reduce((acc, pump) => {
      if (!acc[pump.customerName]) {
        acc[pump.customerName] = {
          customerName: pump.customerName,
          totalPumps: 0,
          completedPumps: 0,
          inProgressPumps: 0
        };
      }
      acc[pump.customerName].totalPumps++;
      if (pump.currentStage === 'completed') {
        acc[pump.customerName].completedPumps++;
      } else if (pump.currentStage !== 'not_started') {
        acc[pump.customerName].inProgressPumps++;
      }
      return acc;
    }, {} as Record<string, any>)
  );

  return {
    totalPumps: allPumps.length,
    pumpsByStage,
    overduePumps,
    highPriorityPumps,
    completionRate,
    averageBuildTime,
    upcomingDeadlines,
    customerSummary
  };
};