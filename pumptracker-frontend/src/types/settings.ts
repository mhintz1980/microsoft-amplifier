/**
 * Settings types for PumpTracker Lite
 * Defines interfaces for department configuration, employee counts, and man-hours calculations
 */

export interface DepartmentSettings {
  id: string;
  name: string;
  displayName: string;
  employeeCount: number;
  efficiency: number; // Percentage (0-100)
  manHours: number; // Calculated: employeeCount * 8 * (efficiency / 100)
  color: string; // UI color for display
}

export interface SettingsState {
  departments: DepartmentSettings[];
  lastUpdated: string;
}

export interface SettingsFormData {
  departments: Record<string, {
    employeeCount: number;
    efficiency: number;
  }>;
}

// Default department configurations
export const DEFAULT_DEPARTMENTS: Omit<DepartmentSettings, 'employeeCount' | 'manHours' | 'lastUpdated'>[] = [
  {
    id: 'fabrication',
    name: 'FABRICATION',
    displayName: 'Fabrication',
    efficiency: 85,
    color: '#3b82f6' // blue-500
  },
  {
    id: 'powder_coat',
    name: 'POWDER_COAT',
    displayName: 'Powder Coat',
    efficiency: 85,
    color: '#8b5cf6' // violet-500
  },
  {
    id: 'assembly',
    name: 'ASSEMBLY',
    displayName: 'Assembly',
    efficiency: 85,
    color: '#10b981' // emerald-500
  },
  {
    id: 'testing',
    name: 'TESTING',
    displayName: 'Testing',
    efficiency: 85,
    color: '#f59e0b' // amber-500
  }
];

// Default employee counts
export const DEFAULT_EMPLOYEE_COUNTS: Record<string, number> = {
  fabrication: 8,
  powder_coat: 6,
  assembly: 4,
  testing: 2
};

// Settings storage key
export const SETTINGS_STORAGE_KEY = 'pumptracker-settings';