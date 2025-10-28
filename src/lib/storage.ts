import { StoredData, Model, ModelsData, Pump, PurchaseOrder, PurchaseOrderLine, PumpEvent } from '../types';

const STORAGE_KEY = 'pumptracker:v2:data';
const MODELS_KEY = 'pumptracker:models';
const SCHEMA_VERSION = '2.0.0';
const DEFAULT_ORG_ID = 'default-org';

class StorageError extends Error {
  constructor(message: string, public readonly cause?: Error) {
    super(message);
    this.name = 'StorageError';
  }
}

/**
 * Simple localStorage utilities with robust error handling
 */
export const storage = {
  /**
   * Load all stored data from localStorage
   */
  loadData(): StoredData {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) {
        return createEmptyData();
      }

      const data = JSON.parse(stored) as StoredData;

      // Basic validation
      if (!data.schemaVersion || !Array.isArray(data.purchaseOrders)) {
        console.warn('Invalid data format, creating empty data');
        return createEmptyData();
      }

      return data;
    } catch (error) {
      console.error('Error loading data from localStorage:', error);
      throw new StorageError('Failed to load data from localStorage', error instanceof Error ? error : undefined);
    }
  },

  /**
   * Save all data to localStorage
   */
  saveData(data: StoredData): void {
    try {
      const dataToSave: StoredData = {
        ...data,
        schemaVersion: SCHEMA_VERSION,
        lastSavedAt: new Date().toISOString(),
        orgId: data.orgId || DEFAULT_ORG_ID,
      };

      localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToSave));
    } catch (error) {
      console.error('Error saving data to localStorage:', error);

      if (error instanceof Error && error.name === 'QuotaExceededError') {
        throw new StorageError('Storage quota exceeded. Please clear some data.', error);
      }

      throw new StorageError('Failed to save data to localStorage', error instanceof Error ? error : undefined);
    }
  },

  /**
   * Load models from static JSON file
   */
  async loadModels(): Promise<Record<string, Model>> {
    try {
      const response = await fetch('/src/data/models.json');
      if (!response.ok) {
        throw new Error(`Failed to load models: ${response.statusText}`);
      }

      const modelsData: ModelsData = await response.json();

      // Transform array to record and map to our Model interface
      const models: Record<string, Model> = {};
      for (const modelData of modelsData.models) {
        models[modelData.model] = {
          id: modelData.model,
          description: modelData.description,
          price: modelData.price,
          defaultBuildTime: modelData.lead_times.total_days,
          bom: modelData.bom,
          leadTimes: modelData.lead_times,
        };
      }

      // Cache models in localStorage for faster access
      try {
        localStorage.setItem(MODELS_KEY, JSON.stringify(models));
      } catch (error) {
        console.warn('Failed to cache models in localStorage:', error);
      }

      return models;
    } catch (error) {
      console.error('Error loading models:', error);

      // Try to load from cache if network fails
      try {
        const cached = localStorage.getItem(MODELS_KEY);
        if (cached) {
          const models = JSON.parse(cached) as Record<string, Model>;
          console.warn('Using cached models due to network failure');
          return models;
        }
      } catch (cacheError) {
        console.error('Failed to load cached models:', cacheError);
      }

      throw new StorageError('Failed to load models', error instanceof Error ? error : undefined);
    }
  },

  /**
   * Clear all stored data
   */
  clearData(): void {
    try {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(MODELS_KEY);
    } catch (error) {
      console.error('Error clearing localStorage:', error);
      throw new StorageError('Failed to clear localStorage', error instanceof Error ? error : undefined);
    }
  },

  /**
   * Check if localStorage is available
   */
  isAvailable(): boolean {
    try {
      const test = '__storage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch {
      return false;
    }
  },
};

/**
 * Specific save/load functions for each data type
 */
export const pumps = {
  save: (pumps: Pump[]): void => {
    const data = storage.loadData();
    data.pumps = pumps;
    storage.saveData(data);
  },

  load: (): Pump[] => {
    return storage.loadData().pumps;
  },

  add: (pump: Pump): void => {
    const data = storage.loadData();
    data.pumps.push(pump);
    storage.saveData(data);
  },

  update: (id: string, updates: Partial<Pump>): void => {
    const data = storage.loadData();
    const index = data.pumps.findIndex(p => p.id === id);
    if (index !== -1) {
      data.pumps[index] = { ...data.pumps[index], ...updates };
      storage.saveData(data);
    }
  },

  delete: (id: string): void => {
    const data = storage.loadData();
    data.pumps = data.pumps.filter(p => p.id !== id);
    storage.saveData(data);
  },
};

export const purchaseOrders = {
  save: (orders: PurchaseOrder[]): void => {
    const data = storage.loadData();
    data.purchaseOrders = orders;
    storage.saveData(data);
  },

  load: (): PurchaseOrder[] => {
    return storage.loadData().purchaseOrders;
  },

  add: (order: PurchaseOrder): void => {
    const data = storage.loadData();
    data.purchaseOrders.push(order);
    storage.saveData(data);
  },

  update: (id: string, updates: Partial<PurchaseOrder>): void => {
    const data = storage.loadData();
    const index = data.purchaseOrders.findIndex(o => o.id === id);
    if (index !== -1) {
      data.purchaseOrders[index] = { ...data.purchaseOrders[index], ...updates };
      storage.saveData(data);
    }
  },

  delete: (id: string): void => {
    const data = storage.loadData();
    data.purchaseOrders = data.purchaseOrders.filter(o => o.id !== id);
    storage.saveData(data);
  },
};

export const purchaseOrderLines = {
  save: (lines: PurchaseOrderLine[]): void => {
    const data = storage.loadData();
    data.purchaseOrderLines = lines;
    storage.saveData(data);
  },

  load: (): PurchaseOrderLine[] => {
    return storage.loadData().purchaseOrderLines;
  },

  add: (line: PurchaseOrderLine): void => {
    const data = storage.loadData();
    data.purchaseOrderLines.push(line);
    storage.saveData(data);
  },

  update: (id: string, updates: Partial<PurchaseOrderLine>): void => {
    const data = storage.loadData();
    const index = data.purchaseOrderLines.findIndex(l => l.id === id);
    if (index !== -1) {
      data.purchaseOrderLines[index] = { ...data.purchaseOrderLines[index], ...updates };
      storage.saveData(data);
    }
  },

  delete: (id: string): void => {
    const data = storage.loadData();
    data.purchaseOrderLines = data.purchaseOrderLines.filter(l => l.id !== id);
    storage.saveData(data);
  },
};

export const pumpEvents = {
  save: (events: PumpEvent[]): void => {
    const data = storage.loadData();
    data.pumpEvents = events;
    storage.saveData(data);
  },

  load: (): PumpEvent[] => {
    return storage.loadData().pumpEvents;
  },

  add: (event: PumpEvent): void => {
    const data = storage.loadData();
    data.pumpEvents.push(event);
    storage.saveData(data);
  },

  delete: (id: string): void => {
    const data = storage.loadData();
    data.pumpEvents = data.pumpEvents.filter(e => e.id !== id);
    storage.saveData(data);
  },
};

/**
 * Helper function to create empty data structure
 */
function createEmptyData(): StoredData {
  return {
    schemaVersion: SCHEMA_VERSION,
    lastSavedAt: new Date().toISOString(),
    orgId: DEFAULT_ORG_ID,
    purchaseOrders: [],
    purchaseOrderLines: [],
    pumps: [],
    pumpEvents: [],
  };
}

/**
 * Export storage utilities for use in components
 */
export const localStorageUtils = {
  storage,
  pumps,
  purchaseOrders,
  purchaseOrderLines,
  pumpEvents,
  StorageError,
};

export default localStorageUtils;