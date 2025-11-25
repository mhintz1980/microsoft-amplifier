/**
 * Settings Storage Layer for PumpTracker Lite
 *
 * This module provides persistent storage for department configurations,
 * vendor settings, employee data, and system settings.
 */

import {
  Department,
  Vendor,
  EmployeeConfiguration,
  SystemSettings,
  DepartmentSettings,
  ValidationResult,
  MigrationConfig,
  DEFAULT_DEPARTMENTS,
  DEFAULT_POWDER_COAT_VENDORS,
} from '../types/department-config';
import { validateDepartment, validateVendor } from './calculations';

// ===== STORAGE KEYS =====
const STORAGE_KEYS = {
  SYSTEM_SETTINGS: 'pumptracker:system-settings',
  DEPARTMENTS: 'pumptracker:departments',
  VENDORS: 'pumptracker:vendors',
  EMPLOYEES: 'pumptracker:employees',
  DEPARTMENT_SETTINGS: 'pumptracker:department-settings',
  CONFIG_VERSION: 'pumptracker:config-version',
  LAST_MIGRATION: 'pumptracker:last-migration',
} as const;

const CURRENT_CONFIG_VERSION = '1.0.0';

// ===== ERROR HANDLING =====
class SettingsStorageError extends Error {
  constructor(message: string, public readonly cause?: Error) {
    super(message);
    this.name = 'SettingsStorageError';
  }
}

// ===== SYSTEM SETTINGS =====

/**
 * Load system settings
 */
export function loadSystemSettings(): SystemSettings {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.SYSTEM_SETTINGS);
    if (!stored) {
      return createDefaultSystemSettings();
    }

    const settings = JSON.parse(stored) as SystemSettings;

    // Validate and migrate if needed
    if (settings.settingsVersion !== CURRENT_CONFIG_VERSION) {
      return migrateSystemSettings(settings);
    }

    return settings;
  } catch (error) {
    console.error('Error loading system settings:', error);
    throw new SettingsStorageError('Failed to load system settings', error instanceof Error ? error : undefined);
  }
}

/**
 * Save system settings
 */
export function saveSystemSettings(settings: Partial<SystemSettings>): void {
  try {
    const currentSettings = loadSystemSettings();
    const updatedSettings: SystemSettings = {
      ...currentSettings,
      ...settings,
      lastUpdated: new Date().toISOString(),
      settingsVersion: CURRENT_CONFIG_VERSION,
    };

    localStorage.setItem(STORAGE_KEYS.SYSTEM_SETTINGS, JSON.stringify(updatedSettings));
  } catch (error) {
    console.error('Error saving system settings:', error);
    throw new SettingsStorageError('Failed to save system settings', error instanceof Error ? error : undefined);
  }
}

// ===== DEPARTMENT MANAGEMENT =====

/**
 * Load all departments
 */
export function loadDepartments(): Department[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.DEPARTMENTS);
    if (!stored) {
      return createDefaultDepartments();
    }

    const departments = JSON.parse(stored) as Department[];

    // Validate each department
    const validDepartments = departments.filter(dept => {
      const validation = validateDepartment(dept);
      if (!validation.isValid) {
        console.warn(`Invalid department ${dept.id}:`, validation.errors);
        return false;
      }
      return true;
    });

    return validDepartments;
  } catch (error) {
    console.error('Error loading departments:', error);
    throw new SettingsStorageError('Failed to load departments', error instanceof Error ? error : undefined);
  }
}

/**
 * Save all departments
 */
export function saveDepartments(departments: Department[]): void {
  try {
    // Validate all departments before saving
    for (const dept of departments) {
      const validation = validateDepartment(dept);
      if (!validation.isValid) {
        throw new SettingsStorageError(`Invalid department ${dept.id}: ${validation.errors.map(e => e.message).join(', ')}`);
      }
    }

    localStorage.setItem(STORAGE_KEYS.DEPARTMENTS, JSON.stringify(departments));
  } catch (error) {
    console.error('Error saving departments:', error);
    throw new SettingsStorageError('Failed to save departments', error instanceof Error ? error : undefined);
  }
}

/**
 * Add or update a department
 */
export function saveDepartment(department: Department): void {
  const departments = loadDepartments();
  const existingIndex = departments.findIndex(d => d.id === department.id);

  // Validate department
  const validation = validateDepartment(department);
  if (!validation.isValid) {
    throw new SettingsStorageError(`Invalid department: ${validation.errors.map(e => e.message).join(', ')}`);
  }

  const updatedDepartment = {
    ...department,
    updatedAt: new Date().toISOString(),
  };

  if (existingIndex >= 0) {
    departments[existingIndex] = updatedDepartment;
  } else {
    departments.push(updatedDepartment);
  }

  saveDepartments(departments);
}

/**
 * Delete a department
 */
export function deleteDepartment(departmentId: string): void {
  const departments = loadDepartments();
  const filteredDepartments = departments.filter(d => d.id !== departmentId);

  if (filteredDepartments.length === departments.length) {
    throw new SettingsStorageError(`Department with ID '${departmentId}' not found`);
  }

  saveDepartments(filteredDepartments);

  // Also delete related vendors and settings
  const vendors = loadVendors().filter(v => v.departmentId !== departmentId);
  saveVendors(vendors);

  deleteDepartmentSettings(departmentId);
}

// ===== VENDOR MANAGEMENT =====

/**
 * Load all vendors
 */
export function loadVendors(): Vendor[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.VENDORS);
    if (!stored) {
      return createDefaultVendors();
    }

    const vendors = JSON.parse(stored) as Vendor[];

    // Validate each vendor
    const validVendors = vendors.filter(vendor => {
      const validation = validateVendor(vendor);
      if (!validation.isValid) {
        console.warn(`Invalid vendor ${vendor.id}:`, validation.errors);
        return false;
      }
      return true;
    });

    return validVendors;
  } catch (error) {
    console.error('Error loading vendors:', error);
    throw new SettingsStorageError('Failed to load vendors', error instanceof Error ? error : undefined);
  }
}

/**
 * Save all vendors
 */
export function saveVendors(vendors: Vendor[]): void {
  try {
    // Validate all vendors before saving
    for (const vendor of vendors) {
      const validation = validateVendor(vendor);
      if (!validation.isValid) {
        throw new SettingsStorageError(`Invalid vendor ${vendor.id}: ${validation.errors.map(e => e.message).join(', ')}`);
      }
    }

    localStorage.setItem(STORAGE_KEYS.VENDORS, JSON.stringify(vendors));
  } catch (error) {
    console.error('Error saving vendors:', error);
    throw new SettingsStorageError('Failed to save vendors', error instanceof Error ? error : undefined);
  }
}

/**
 * Add or update a vendor
 */
export function saveVendor(vendor: Vendor): void {
  const vendors = loadVendors();
  const existingIndex = vendors.findIndex(v => v.id === vendor.id);

  // Validate vendor
  const validation = validateVendor(vendor);
  if (!validation.isValid) {
    throw new SettingsStorageError(`Invalid vendor: ${validation.errors.map(e => e.message).join(', ')}`);
  }

  const updatedVendor = {
    ...vendor,
    updatedAt: new Date().toISOString(),
  };

  if (existingIndex >= 0) {
    vendors[existingIndex] = updatedVendor;
  } else {
    vendors.push(updatedVendor);
  }

  saveVendors(vendors);
}

/**
 * Delete a vendor
 */
export function deleteVendor(vendorId: string): void {
  const vendors = loadVendors();
  const filteredVendors = vendors.filter(v => v.id !== vendorId);

  if (filteredVendors.length === vendors.length) {
    throw new SettingsStorageError(`Vendor with ID '${vendorId}' not found`);
  }

  saveVendors(filteredVendors);
}

/**
 * Get vendors for a specific department
 */
export function getVendorsForDepartment(departmentId: string): Vendor[] {
  const vendors = loadVendors();
  return vendors.filter(v => v.departmentId === departmentId && v.isActive);
}

// ===== EMPLOYEE MANAGEMENT =====

/**
 * Load all employees
 */
export function loadEmployees(): EmployeeConfiguration[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.EMPLOYEES);
    return stored ? JSON.parse(stored) as EmployeeConfiguration[] : [];
  } catch (error) {
    console.error('Error loading employees:', error);
    throw new SettingsStorageError('Failed to load employees', error instanceof Error ? error : undefined);
  }
}

/**
 * Save all employees
 */
export function saveEmployees(employees: EmployeeConfiguration[]): void {
  try {
    localStorage.setItem(STORAGE_KEYS.EMPLOYEES, JSON.stringify(employees));
  } catch (error) {
    console.error('Error saving employees:', error);
    throw new SettingsStorageError('Failed to save employees', error instanceof Error ? error : undefined);
  }
}

/**
 * Add or update an employee
 */
export function saveEmployee(employee: EmployeeConfiguration): void {
  const employees = loadEmployees();
  const existingIndex = employees.findIndex(e => e.id === employee.id);

  const updatedEmployee = {
    ...employee,
    updatedAt: new Date().toISOString(),
  };

  if (existingIndex >= 0) {
    employees[existingIndex] = updatedEmployee;
  } else {
    employees.push(updatedEmployee);
  }

  saveEmployees(employees);
}

/**
 * Delete an employee
 */
export function deleteEmployee(employeeId: string): void {
  const employees = loadEmployees();
  const filteredEmployees = employees.filter(e => e.id !== employeeId);
  saveEmployees(filteredEmployees);
}

/**
 * Get employees for a specific department
 */
export function getEmployeesForDepartment(departmentId: string): EmployeeConfiguration[] {
  const employees = loadEmployees();
  return employees.filter(e => e.departmentId === departmentId && e.isActive);
}

// ===== DEPARTMENT SETTINGS =====

/**
 * Load department settings for a department
 */
export function loadDepartmentSettings(departmentId: string): DepartmentSettings | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.DEPARTMENT_SETTINGS);
    if (!stored) return null;

    const allSettings = JSON.parse(stored) as Record<string, DepartmentSettings>;
    return allSettings[departmentId] || null;
  } catch (error) {
    console.error('Error loading department settings:', error);
    return null;
  }
}

/**
 * Save department settings for a department
 */
export function saveDepartmentSettings(departmentId: string, settings: DepartmentSettings): void {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.DEPARTMENT_SETTINGS);
    const allSettings = stored ? JSON.parse(stored) as Record<string, DepartmentSettings> : {};

    const updatedSettings = {
      ...settings,
      departmentId,
      lastUpdated: new Date().toISOString(),
    };

    allSettings[departmentId] = updatedSettings;
    localStorage.setItem(STORAGE_KEYS.DEPARTMENT_SETTINGS, JSON.stringify(allSettings));
  } catch (error) {
    console.error('Error saving department settings:', error);
    throw new SettingsStorageError('Failed to save department settings', error instanceof Error ? error : undefined);
  }
}

/**
 * Delete department settings
 */
export function deleteDepartmentSettings(departmentId: string): void {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.DEPARTMENT_SETTINGS);
    if (!stored) return;

    const allSettings = JSON.parse(stored) as Record<string, DepartmentSettings>;
    delete allSettings[departmentId];
    localStorage.setItem(STORAGE_KEYS.DEPARTMENT_SETTINGS, JSON.stringify(allSettings));
  } catch (error) {
    console.error('Error deleting department settings:', error);
  }
}

// ===== CONFIGURATION MANAGEMENT =====

/**
 * Get current configuration version
 */
export function getConfigVersion(): string {
  return localStorage.getItem(STORAGE_KEYS.CONFIG_VERSION) || CURRENT_CONFIG_VERSION;
}

/**
 * Set configuration version
 */
export function setConfigVersion(version: string): void {
  localStorage.setItem(STORAGE_KEYS.CONFIG_VERSION, version);
}

/**
 * Check if first-time setup is needed
 */
export function needsFirstTimeSetup(): boolean {
  return !localStorage.getItem(STORAGE_KEYS.SYSTEM_SETTINGS);
}

/**
 * Reset all configuration data
 */
export function resetAllConfiguration(): void {
  Object.values(STORAGE_KEYS).forEach(key => {
    localStorage.removeItem(key);
  });
}

/**
 * Export all configuration data
 */
export function exportConfiguration(): string {
  const data = {
    version: CURRENT_CONFIG_VERSION,
    exportedAt: new Date().toISOString(),
    systemSettings: loadSystemSettings(),
    departments: loadDepartments(),
    vendors: loadVendors(),
    employees: loadEmployees(),
    departmentSettings: (() => {
      const stored = localStorage.getItem(STORAGE_KEYS.DEPARTMENT_SETTINGS);
      return stored ? JSON.parse(stored) : {};
    })(),
  };

  return JSON.stringify(data, null, 2);
}

/**
 * Import configuration data
 */
export function importConfiguration(configData: string): void {
  try {
    const data = JSON.parse(configData);

    // Validate structure
    if (!data.version || !data.systemSettings || !data.departments) {
      throw new SettingsStorageError('Invalid configuration data structure');
    }

    // Import data
    saveSystemSettings(data.systemSettings);
    saveDepartments(data.departments);

    if (data.vendors) {
      saveVendors(data.vendors);
    }

    if (data.employees) {
      saveEmployees(data.employees);
    }

    if (data.departmentSettings) {
      Object.entries(data.departmentSettings).forEach(([deptId, settings]) => {
        saveDepartmentSettings(deptId, settings as DepartmentSettings);
      });
    }

    setConfigVersion(data.version);
  } catch (error) {
    console.error('Error importing configuration:', error);
    throw new SettingsStorageError('Failed to import configuration', error instanceof Error ? error : undefined);
  }
}

// ===== DEFAULT FACTORIES =====

function createDefaultSystemSettings(): SystemSettings {
  return {
    organizationName: 'Pump Manufacturing Company',
    timezone: 'America/New_York',
    dateFormat: 'MM/dd/yyyy',
    currency: 'USD',
    defaultLeadTimes: {
      fabrication: 1.5,
      powder_coat: 7,
      assembly: 1,
      testing: 0.25,
    },
    capacityBuffer: 0.1,
    autoRescheduleThreshold: 7,
    defaultView: 'kanban',
    workingDaysStartHour: 8,
    workingDaysEndHour: 17,
    enableNotifications: true,
    overdueThreshold: 3,
    capacityAlertThreshold: 0.8,
    autoSave: true,
    dataRetentionDays: 365,
    enableAuditLog: true,
    settingsVersion: CURRENT_CONFIG_VERSION,
    lastUpdated: new Date().toISOString(),
    updatedBy: 'system',
  };
}

function createDefaultDepartments(): Department[] {
  return DEFAULT_DEPARTMENTS.map((dept, index) => ({
    ...dept,
    id: dept.displayName.toLowerCase().replace(/\s+/g, '_'),
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }));
}

function createDefaultVendors(): Vendor[] {
  const departments = createDefaultDepartments();
  const powderCoatDept = departments.find(d => d.id === 'powder_coat');

  if (!powderCoatDept) return [];

  return DEFAULT_POWDER_COAT_VENDORS.map((vendor, index) => ({
    ...vendor,
    id: `powder_coat_vendor_${index + 1}`,
    departmentId: powderCoatDept.id,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }));
}

// ===== MIGRATION UTILITIES =====

function migrateSystemSettings(settings: any): SystemSettings {
  // Simple migration for now - just ensure current version
  return {
    ...createDefaultSystemSettings(),
    ...settings,
    settingsVersion: CURRENT_CONFIG_VERSION,
    lastUpdated: new Date().toISOString(),
  };
}

/**
 * Check if migration is needed
 */
export function needsMigration(): boolean {
  const currentVersion = getConfigVersion();
  return currentVersion !== CURRENT_CONFIG_VERSION;
}

/**
 * Run data migration
 */
export async function runMigration(): Promise<void> {
  const currentVersion = getConfigVersion();

  if (currentVersion === CURRENT_CONFIG_VERSION) {
    return; // No migration needed
  }

  console.log(`Migrating configuration from version ${currentVersion} to ${CURRENT_CONFIG_VERSION}`);

  // For now, just re-create defaults with current version
  // In a real implementation, this would have specific migration steps

  const systemSettings = loadSystemSettings();
  if (systemSettings.settingsVersion !== CURRENT_CONFIG_VERSION) {
    saveSystemSettings(systemSettings);
  }

  setConfigVersion(CURRENT_CONFIG_VERSION);
  console.log('Migration completed successfully');
}