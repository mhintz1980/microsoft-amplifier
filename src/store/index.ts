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
  Department,
  Vendor,
  EmployeeConfiguration,
  SystemSettings,
  DepartmentSettings,
  DailyCapacity,
  ManHoursCalculation,
} from '../types';
import { localStorageUtils } from '../lib/storage';
import {
  loadSystemSettings as loadSystemSettingsFromStorage,
  saveSystemSettings as saveSystemSettingsToStorage,
  loadDepartments as loadDepartmentsFromStorage,
  saveDepartment as saveDepartmentToStorage,
  deleteDepartment as deleteDepartmentFromStorage,
  loadVendors as loadVendorsFromStorage,
  saveVendor as saveVendorToStorage,
  deleteVendor as deleteVendorFromStorage,
  loadEmployees as loadEmployeesFromStorage,
  saveEmployee as saveEmployeeToStorage,
  deleteEmployee as deleteEmployeeFromStorage,
  getVendorsForDepartment as getVendorsForDepartmentFromStorage,
  getEmployeesForDepartment as getEmployeesForDepartmentFromStorage,
  loadDepartmentSettings as loadDepartmentSettingsFromStorage,
  saveDepartmentSettings as saveDepartmentSettingsToStorage,
  needsFirstTimeSetup,
  needsMigration,
  runMigration,
} from '../lib/settings-storage';
import {
  calculateDailyCapacity,
  calculateManHours,
  calculateVendorAllocation,
} from '../lib/calculations';

interface StoreState {
  // Core Data
  pumps: Pump[];
  purchaseOrders: PurchaseOrder[];
  purchaseOrderLines: PurchaseOrderLine[];
  pumpEvents: PumpEvent[];
  models: Record<string, Model>;

  // Department Configuration Data
  departments: Department[];
  vendors: Vendor[];
  employees: EmployeeConfiguration[];
  systemSettings: SystemSettings;
  departmentSettings: Record<string, DepartmentSettings>;

  // Computed Capacity Data
  dailyCapacities: Record<string, DailyCapacity[]>; // departmentId -> array of daily capacities
  manHoursCalculations: Record<string, ManHoursCalculation>; // departmentId -> calculation

  // Loading state
  isLoading: boolean;
  error: string | null;
  isConfigurationLoading: boolean;

  // UI state
  filters: {
    customer?: string;
    stage?: Stage;
    priority?: Priority;
    search?: string;
  };
  collapsedStages: Set<Stage>;

  // Actions
  // Core Data loading
  loadData: () => Promise<void>;
  loadModels: () => Promise<void>;
  setError: (error: string | null) => void;

  // Configuration loading and initialization
  loadConfiguration: () => Promise<void>;
  initializeConfiguration: () => Promise<void>;
  isFirstTimeSetup: () => boolean;
  checkAndRunMigration: () => Promise<void>;

  // Department Management
  loadDepartments: () => void;
  saveDepartment: (department: Department) => void;
  deleteDepartment: (departmentId: string) => void;
  getDepartmentById: (id: string) => Department | undefined;

  // Vendor Management
  loadVendors: () => void;
  saveVendor: (vendor: Vendor) => void;
  deleteVendor: (vendorId: string) => void;
  getVendorsForDepartment: (departmentId: string) => Vendor[];
  allocatePumpsToVendors: (departmentId: string, pumpsCount: number, priorityVendorId?: string) => Array<{vendorId: string; pumps: number}>;

  // Employee Management
  loadEmployees: () => void;
  saveEmployee: (employee: EmployeeConfiguration) => void;
  deleteEmployee: (employeeId: string) => void;
  getEmployeesForDepartment: (departmentId: string) => EmployeeConfiguration[];

  // System Settings Management
  saveSystemSettings: (settings: Partial<SystemSettings>) => void;
  loadSystemSettings: () => void;

  // Department Settings Management
  saveDepartmentSettings: (departmentId: string, settings: DepartmentSettings) => void;
  getDepartmentSettings: (departmentId: string) => DepartmentSettings | null;

  // Capacity Calculations
  calculateDailyCapacity: (departmentId: string, date?: Date) => DailyCapacity;
  calculateWeeklyCapacity: (departmentId: string, startDate?: Date) => DailyCapacity[];
  calculateManHours: (departmentId: string, startDate: Date, endDate: Date) => ManHoursCalculation;
  refreshCapacityData: () => void;

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

      // Department configuration state
      departments: [],
      vendors: [],
      employees: [],
      systemSettings: {} as SystemSettings,
      departmentSettings: {},

      // Computed capacity data
      dailyCapacities: {},
      manHoursCalculations: {},

      // Loading state
      isLoading: false,
      isConfigurationLoading: false,
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

      // Configuration loading and initialization
      loadConfiguration: async () => {
        set({ isConfigurationLoading: true, error: null });

        try {
          // Check if first-time setup is needed
          if (needsFirstTimeSetup()) {
            await get().initializeConfiguration();
          } else {
            // Check if migration is needed
            if (needsMigration()) {
              await get().checkAndRunMigration();
            }

            // Load existing configuration
            get().loadSystemSettings();
            get().loadDepartments();
            get().loadVendors();
            get().loadEmployees();
          }

          set({ isConfigurationLoading: false });
        } catch (error) {
          console.error('Failed to load configuration:', error);
          set({
            error: error instanceof Error ? error.message : 'Failed to load configuration',
            isConfigurationLoading: false,
          });
        }
      },

      initializeConfiguration: async () => {
        console.log('Initializing first-time configuration...');
        // The storage layer will create defaults automatically
        get().loadSystemSettings();
        get().loadDepartments();
        get().loadVendors();
        get().loadEmployees();
        console.log('First-time configuration completed');
      },

      isFirstTimeSetup: () => needsFirstTimeSetup(),

      checkAndRunMigration: async () => {
        console.log('Running configuration migration...');
        await runMigration();
        get().loadConfiguration(); // Reload after migration
      },

      // Department Management
      loadDepartments: () => {
        try {
          const depts = loadDepartmentsFromStorage();
          set({ departments: depts });
        } catch (error) {
          console.error('Failed to load departments:', error);
          set({ error: 'Failed to load departments' });
        }
      },

      saveDepartment: (department) => {
        try {
          saveDepartmentToStorage(department);
          const departments = loadDepartmentsFromStorage();
          set({ departments });
        } catch (error) {
          console.error('Failed to save department:', error);
          set({ error: error instanceof Error ? error.message : 'Failed to save department' });
        }
      },

      deleteDepartment: (departmentId) => {
        try {
          deleteDepartmentFromStorage(departmentId);
          const departments = loadDepartmentsFromStorage();
          set({ departments });
        } catch (error) {
          console.error('Failed to delete department:', error);
          set({ error: error instanceof Error ? error.message : 'Failed to delete department' });
        }
      },

      getDepartmentById: (id) => {
        return get().departments.find(dept => dept.id === id);
      },

      // Vendor Management
      loadVendors: () => {
        try {
          const vendors = loadVendorsFromStorage();
          set({ vendors });
        } catch (error) {
          console.error('Failed to load vendors:', error);
          set({ error: 'Failed to load vendors' });
        }
      },

      saveVendor: (vendor) => {
        try {
          saveVendorToStorage(vendor);
          const vendors = loadVendorsFromStorage();
          set({ vendors });
        } catch (error) {
          console.error('Failed to save vendor:', error);
          set({ error: error instanceof Error ? error.message : 'Failed to save vendor' });
        }
      },

      deleteVendor: (vendorId) => {
        try {
          deleteVendorFromStorage(vendorId);
          const vendors = loadVendorsFromStorage();
          set({ vendors });
        } catch (error) {
          console.error('Failed to delete vendor:', error);
          set({ error: error instanceof Error ? error.message : 'Failed to delete vendor' });
        }
      },

      getVendorsForDepartment: (departmentId) => {
        return getVendorsForDepartmentFromStorage(departmentId);
      },

      allocatePumpsToVendors: (departmentId, pumpsCount, priorityVendorId) => {
        const departmentVendors = get().getVendorsForDepartment(departmentId);
        const allocation = calculateVendorAllocation(departmentVendors, pumpsCount, priorityVendorId);

        // Update vendor current loads
        allocation.forEach(({ vendorId, pumps }) => {
          const vendor = get().vendors.find(v => v.id === vendorId);
          if (vendor) {
            get().saveVendor({
              ...vendor,
              currentLoad: vendor.currentLoad + pumps,
            });
          }
        });

        return allocation;
      },

      // Employee Management
      loadEmployees: () => {
        try {
          const employees = loadEmployeesFromStorage();
          set({ employees });
        } catch (error) {
          console.error('Failed to load employees:', error);
          set({ error: 'Failed to load employees' });
        }
      },

      saveEmployee: (employee) => {
        try {
          saveEmployeeToStorage(employee);
          const employees = loadEmployeesFromStorage();
          set({ employees });
        } catch (error) {
          console.error('Failed to save employee:', error);
          set({ error: error instanceof Error ? error.message : 'Failed to save employee' });
        }
      },

      deleteEmployee: (employeeId) => {
        try {
          deleteEmployeeFromStorage(employeeId);
          const employees = loadEmployeesFromStorage();
          set({ employees });
        } catch (error) {
          console.error('Failed to delete employee:', error);
          set({ error: error instanceof Error ? error.message : 'Failed to delete employee' });
        }
      },

      getEmployeesForDepartment: (departmentId) => {
        return getEmployeesForDepartmentFromStorage(departmentId);
      },

      // System Settings Management
      saveSystemSettings: (settings) => {
        try {
          saveSystemSettingsToStorage(settings);
          const systemSettings = loadSystemSettingsFromStorage();
          set({ systemSettings });
        } catch (error) {
          console.error('Failed to save system settings:', error);
          set({ error: error instanceof Error ? error.message : 'Failed to save system settings' });
        }
      },

      loadSystemSettings: () => {
        try {
          const settings = loadSystemSettingsFromStorage();
          set({ systemSettings: settings });
        } catch (error) {
          console.error('Failed to load system settings:', error);
          set({ error: 'Failed to load system settings' });
        }
      },

      // Department Settings Management
      saveDepartmentSettings: (departmentId, settings) => {
        try {
          saveDepartmentSettingsToStorage(departmentId, settings);
          const currentSettings = get().departmentSettings;
          set({
            departmentSettings: {
              ...currentSettings,
              [departmentId]: settings,
            },
          });
        } catch (error) {
          console.error('Failed to save department settings:', error);
          set({ error: error instanceof Error ? error.message : 'Failed to save department settings' });
        }
      },

      getDepartmentSettings: (departmentId) => {
        const cached = get().departmentSettings[departmentId];
        if (cached) return cached;

        const settings = loadDepartmentSettingsFromStorage(departmentId);
        if (settings) {
          const currentSettings = get().departmentSettings;
          set({
            departmentSettings: {
              ...currentSettings,
              [departmentId]: settings,
            },
          });
        }

        return settings;
      },

      // Capacity Calculations
      calculateDailyCapacity: (departmentId, date = new Date()) => {
        const department = get().getDepartmentById(departmentId);
        const employees = get().getEmployeesForDepartment(departmentId);
        const vendors = get().getVendorsForDepartment(departmentId);

        if (!department) {
          throw new Error(`Department with ID '${departmentId}' not found`);
        }

        return calculateDailyCapacity(department, employees, vendors, date);
      },

      calculateWeeklyCapacity: (departmentId, startDate = new Date()) => {
        const endDate = new Date(startDate);
        endDate.setDate(endDate.getDate() + 6); // 7 days total

        const department = get().getDepartmentById(departmentId);
        const employees = get().getEmployeesForDepartment(departmentId);
        const vendors = get().getVendorsForDepartment(departmentId);

        if (!department) {
          throw new Error(`Department with ID '${departmentId}' not found`);
        }

        const dailyCapacities: DailyCapacity[] = [];
        const current = new Date(startDate);

        while (current <= endDate) {
          dailyCapacities.push(
            calculateDailyCapacity(department, employees, vendors, new Date(current))
          );
          current.setDate(current.getDate() + 1);
        }

        return dailyCapacities;
      },

      calculateManHours: (departmentId, startDate, endDate) => {
        const department = get().getDepartmentById(departmentId);
        const employees = get().getEmployeesForDepartment(departmentId);

        if (!department) {
          throw new Error(`Department with ID '${departmentId}' not found`);
        }

        return calculateManHours(department, employees, startDate, endDate);
      },

      refreshCapacityData: () => {
        const departments = get().departments;
        const dailyCapacities: Record<string, DailyCapacity[]> = {};
        const manHoursCalculations: Record<string, ManHoursCalculation> = {};

        departments.forEach(department => {
          // Calculate weekly capacity
          const startDate = new Date();
          startDate.setDate(startDate.getDate() - startDate.getDay()); // Start of week
          const weeklyCapacity = get().calculateWeeklyCapacity(department.id, startDate);

          dailyCapacities[department.id] = weeklyCapacity;

          // Calculate man-hours for current week
          const endDate = new Date(startDate);
          endDate.setDate(endDate.getDate() + 6);

          try {
            const manHours = get().calculateManHours(department.id, startDate, endDate);
            manHoursCalculations[department.id] = manHours;
          } catch (error) {
            console.error(`Failed to calculate man-hours for ${department.id}:`, error);
          }
        });

        set({ dailyCapacities, manHoursCalculations });
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

// Department Configuration Selectors
export const useDepartments = () => useStore((state) => state.departments);
export const useVendors = () => useStore((state) => state.vendors);
export const useEmployees = () => useStore((state) => state.employees);
export const useSystemSettings = () => useStore((state) => state.systemSettings);
export const useDepartmentSettings = () => useStore((state) => state.departmentSettings);
export const useDailyCapacities = () => useStore((state) => state.dailyCapacities);
export const useManHoursCalculations = () => useStore((state) => state.manHoursCalculations);
export const useIsConfigurationLoading = () => useStore((state) => state.isConfigurationLoading);

// Derived selectors for departments
export const useActiveDepartments = () => {
  const departments = useDepartments();
  return departments.filter(dept => dept.isActive).sort((a, b) => a.sortOrder - b.sortOrder);
};

export const useDepartmentById = (id: string) => {
  const departments = useDepartments();
  return departments.find(dept => dept.id === id);
};

export const useVendorsForDepartment = (departmentId: string) => {
  const vendors = useVendors();
  return vendors
    .filter(vendor => vendor.departmentId === departmentId && vendor.isActive)
    .sort((a, b) => {
      if (a.isPreferred && !b.isPreferred) return -1;
      if (!a.isPreferred && b.isPreferred) return 1;
      return a.swimlanePosition - b.swimlanePosition;
    });
};

export const useEmployeesForDepartment = (departmentId: string) => {
  const employees = useEmployees();
  return employees.filter(emp => emp.departmentId === departmentId && emp.isActive);
};

export const useDepartmentCapacity = (departmentId: string) => {
  const store = useStore();
  const dailyCapacities = useDailyCapacities();
  const manHoursCalculations = useManHoursCalculations();

  return {
    dailyCapacity: dailyCapacities[departmentId] || [],
    manHoursCalculation: manHoursCalculations[departmentId] || null,
    refreshData: () => store.refreshCapacityData(),
  };
};

export const useSystemHealth = () => {
  const departments = useActiveDepartments();
  const vendors = useVendors();
  const employees = useEmployees();

  // Calculate health metrics
  const activeVendorCount = vendors.filter(v => v.isActive).length;
  const activeEmployeeCount = employees.filter(e => e.isActive).length;
  const vendorsWithHighLoad = vendors.filter(v => v.currentLoad > v.weeklyCapacity * 0.8).length;

  return {
    departmentCount: departments.length,
    vendorCount: activeVendorCount,
    employeeCount: activeEmployeeCount,
    vendorsAtCapacity: vendorsWithHighLoad,
    systemStatus: activeVendorCount > 0 && activeEmployeeCount > 0 ? 'healthy' : 'warning',
  };
};

export default useStore;