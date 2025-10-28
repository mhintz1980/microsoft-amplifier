import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { nanoid } from 'nanoid';

import {
  Pump,
  PurchaseOrder,
  PurchaseOrderLine,
  PumpEvent,
  Model,
  Stage,
  Priority,
  StoredData,
} from '../types';
import { localStorageUtils } from '../lib/storage';

interface StoreState {
  // Data
  pumps: Pump[];
  purchaseOrders: PurchaseOrder[];
  purchaseOrderLines: PurchaseOrderLine[];
  pumpEvents: PumpEvent[];
  models: Record<string, Model>;

  // Loading state
  isLoading: boolean;
  error: string | null;

  // UI state
  filters: {
    customer?: string;
    stage?: Stage;
    priority?: Priority;
    search?: string;
  };
  collapsedStages: Set<Stage>;

  // Actions
  // Data loading
  loadData: () => Promise<void>;
  loadModels: () => Promise<void>;
  setError: (error: string | null) => void;

  // Pump actions
  addPump: (pump: Omit<Pump, 'id' | 'last_update'>) => void;
  updatePump: (id: string, updates: Partial<Pump>) => void;
  moveStage: (id: string, toStage: Stage, notes?: string) => void;
  deletePump: (id: string) => void;

  // Purchase Order actions
  addPO: (po: Omit<PurchaseOrder, 'org_id'>) => void;
  updatePO: (id: string, updates: Partial<PurchaseOrder>) => void;
  deletePO: (id: string) => void;

  // Purchase Order Line actions
  addPOLine: (line: Omit<PurchaseOrderLine, 'id' | 'org_id'>) => void;
  updatePOLine: (id: string, updates: Partial<PurchaseOrderLine>) => void;
  deletePOLine: (id: string) => void;

  // Pump Event actions
  addPumpEvent: (event: Omit<PumpEvent, 'id' | 'event_time'>) => void;

  // UI actions
  setFilters: (filters: Partial<StoreState['filters']>) => void;
  toggleStageCollapsed: (stage: Stage) => void;

  // Bulk actions
  replaceAllData: (data: StoredData) => void;
}

const defaultOrgId = 'default-org';

export const useStore = create<StoreState>()(
  devtools(
    (set, get) => ({
      // Initial state
      pumps: [],
      purchaseOrders: [],
      purchaseOrderLines: [],
      pumpEvents: [],
      models: {},
      isLoading: false,
      error: null,

      filters: {},
      collapsedStages: new Set(),

      // Data loading actions
      loadData: async () => {
        set({ isLoading: true, error: null });

        try {
          const data = localStorageUtils.storage.loadData();

          set({
            pumps: data.pumps,
            purchaseOrders: data.purchaseOrders,
            purchaseOrderLines: data.purchaseOrderLines,
            pumpEvents: data.pumpEvents,
            isLoading: false,
          });
        } catch (error) {
          console.error('Failed to load data:', error);
          set({
            error: error instanceof Error ? error.message : 'Failed to load data',
            isLoading: false,
          });
        }
      },

      loadModels: async () => {
        set({ isLoading: true, error: null });

        try {
          const models = await localStorageUtils.storage.loadModels();
          set({ models, isLoading: false });
        } catch (error) {
          console.error('Failed to load models:', error);
          set({
            error: error instanceof Error ? error.message : 'Failed to load models',
            isLoading: false,
          });
        }
      },

      setError: (error) => set({ error }),

      // Pump actions
      addPump: (pumpData) => {
        const pump: Pump = {
          ...pumpData,
          id: nanoid(),
          last_update: new Date().toISOString(),
          org_id: defaultOrgId,
        };

        // Get model defaults
        const model = get().models[pump.model_id];
        if (model) {
          pump.value = model.price || 0;
          pump.buildTime = model.defaultBuildTime;
          pump.bom = model.bom;
        }

        set({ pumps: [...get().pumps, pump] });
        localStorageUtils.pumps.save([...get().pumps, pump]);
      },

      updatePump: (id, updates) => {
        const updatedPumps = get().pumps.map(pump =>
          pump.id === id
            ? { ...pump, ...updates, last_update: new Date().toISOString() }
            : pump
        );

        set({ pumps: updatedPumps });
        localStorageUtils.pumps.save(updatedPumps);
      },

      moveStage: (id, toStage, notes) => {
        const pump = get().pumps.find(p => p.id === id);
        if (!pump) return;

        const fromStage = pump.stage;

        // Update pump stage
        get().updatePump(id, { stage: toStage });

        // Create event
        const event: PumpEvent = {
          id: nanoid(),
          pump_id: id,
          event_time: new Date().toISOString(),
          from_stage: fromStage !== toStage ? fromStage : undefined,
          to_stage: toStage,
          notes,
          org_id: defaultOrgId,
        };

        set({ pumpEvents: [...get().pumpEvents, event] });
        localStorageUtils.pumpEvents.add(event);
      },

      deletePump: (id) => {
        const updatedPumps = get().pumps.filter(p => p.id !== id);
        set({ pumps: updatedPumps });
        localStorageUtils.pumps.save(updatedPumps);
      },

      // Purchase Order actions
      addPO: (poData) => {
        const po: PurchaseOrder = {
          ...poData,
          org_id: defaultOrgId,
        };

        set({ purchaseOrders: [...get().purchaseOrders, po] });
        localStorageUtils.purchaseOrders.add(po);
      },

      updatePO: (id, updates) => {
        const updatedPOs = get().purchaseOrders.map(po =>
          po.id === id ? { ...po, ...updates } : po
        );

        set({ purchaseOrders: updatedPOs });
        localStorageUtils.purchaseOrders.save(updatedPOs);
      },

      deletePO: (id) => {
        const updatedPOs = get().purchaseOrders.filter(po => po.id !== id);
        set({ purchaseOrders: updatedPOs });
        localStorageUtils.purchaseOrders.save(updatedPOs);

        // Also delete associated lines and pumps
        const updatedLines = get().purchaseOrderLines.filter(line => line.po_id !== id);
        set({ purchaseOrderLines: updatedLines });
        localStorageUtils.purchaseOrderLines.save(updatedLines);

        const updatedPumps = get().pumps.filter(pump => pump.po_id !== id);
        set({ pumps: updatedPumps });
        localStorageUtils.pumps.save(updatedPumps);
      },

      // Purchase Order Line actions
      addPOLine: (lineData) => {
        const line: PurchaseOrderLine = {
          ...lineData,
          id: nanoid(),
          org_id: defaultOrgId,
        };

        set({ purchaseOrderLines: [...get().purchaseOrderLines, line] });
        localStorageUtils.purchaseOrderLines.add(line);
      },

      updatePOLine: (id, updates) => {
        const updatedLines = get().purchaseOrderLines.map(line =>
          line.id === id ? { ...line, ...updates } : line
        );

        set({ purchaseOrderLines: updatedLines });
        localStorageUtils.purchaseOrderLines.save(updatedLines);
      },

      deletePOLine: (id) => {
        const updatedLines = get().purchaseOrderLines.filter(line => line.id !== id);
        set({ purchaseOrderLines: updatedLines });
        localStorageUtils.purchaseOrderLines.save(updatedLines);

        // Also delete associated pumps
        const updatedPumps = get().pumps.filter(pump => pump.po_line_id !== id);
        set({ pumps: updatedPumps });
        localStorageUtils.pumps.save(updatedPumps);
      },

      // Pump Event actions
      addPumpEvent: (eventData) => {
        const event: PumpEvent = {
          ...eventData,
          id: nanoid(),
          event_time: new Date().toISOString(),
        };

        set({ pumpEvents: [...get().pumpEvents, event] });
        localStorageUtils.pumpEvents.add(event);
      },

      // UI actions
      setFilters: (filters) => {
        set({ filters: { ...get().filters, ...filters } });
      },

      toggleStageCollapsed: (stage) => {
        const collapsed = new Set(get().collapsedStages);
        if (collapsed.has(stage)) {
          collapsed.delete(stage);
        } else {
          collapsed.add(stage);
        }
        set({ collapsedStages: collapsed });
      },

      // Bulk actions
      replaceAllData: (data) => {
        set({
          pumps: data.pumps,
          purchaseOrders: data.purchaseOrders,
          purchaseOrderLines: data.purchaseOrderLines,
          pumpEvents: data.pumpEvents,
        });

        localStorageUtils.storage.saveData(data);
      },
    }),
    {
      name: 'pumptracker-store',
    }
  )
);

// Selectors for derived state
export const usePumps = () => useStore((state) => state.pumps);
export const usePurchaseOrders = () => useStore((state) => state.purchaseOrders);
export const usePurchaseOrderLines = () => useStore((state) => state.purchaseOrderLines);
export const usePumpEvents = () => useStore((state) => state.pumpEvents);
export const useModels = () => useStore((state) => state.models);
export const useFilters = () => useStore((state) => state.filters);
export const useCollapsedStages = () => useStore((state) => state.collapsedStages);
export const useIsLoading = () => useStore((state) => state.isLoading);
export const useError = () => useStore((state) => state.error);

// Derived selectors
export const useFilteredPumps = () => {
  const pumps = usePumps();
  const filters = useFilters();

  return pumps.filter(pump => {
    if (filters.customer && !pump.customer.toLowerCase().includes(filters.customer.toLowerCase())) {
      return false;
    }
    if (filters.stage && pump.stage !== filters.stage) {
      return false;
    }
    if (filters.priority && pump.priority !== filters.priority) {
      return false;
    }
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      return (
        pump.customer.toLowerCase().includes(searchLower) ||
        (pump.serial && pump.serial.toString().includes(searchLower)) ||
        pump.model_id.toLowerCase().includes(searchLower)
      );
    }
    return true;
  });
};

export const usePumpsByStage = () => {
  const filteredPumps = useFilteredPumps();
  const collapsedStages = useCollapsedStages();

  const pumpsByStage = Object.values(Stage).reduce((acc, stage) => {
    acc[stage] = filteredPumps.filter(pump => pump.stage === stage);
    return acc;
  }, {} as Record<Stage, Pump[]>);

  return { pumpsByStage, collapsedStages };
};

export const usePurchaseOrderWithLines = () => {
  const purchaseOrders = usePurchaseOrders();
  const purchaseOrderLines = usePurchaseOrderLines();

  return purchaseOrders.map(po => ({
    ...po,
    lines: purchaseOrderLines.filter(line => line.po_id === po.id),
  }));
};

export const usePumpCountByStage = () => {
  const pumpsByStage = usePumpsByStage().pumpsByStage;

  return Object.values(Stage).reduce((acc, stage) => {
    acc[stage] = pumpsByStage[stage].length;
    return acc;
  }, {} as Record<Stage, number>);
};

export default useStore;