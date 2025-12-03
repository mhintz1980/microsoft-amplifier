/**
 * Settings utilities for PumpTracker Lite
 * Handles settings persistence, validation, and man-hours calculations
 */

import {
  DEFAULT_DEPARTMENTS,
  DEFAULT_EMPLOYEE_COUNTS,
  SETTINGS_STORAGE_KEY
} from '../types/settings';
import type {
  DepartmentSettings,
  SettingsState,
  SettingsFormData
} from '../types/settings';

// Re-export types for component usage
export type {
  DepartmentSettings,
  SettingsState,
  SettingsFormData
};

export class SettingsManager {
  private static instance: SettingsManager;
  private settings: SettingsState;

  private constructor() {
    this.settings = this.loadSettings();
  }

  public static getInstance(): SettingsManager {
    if (!SettingsManager.instance) {
      SettingsManager.instance = new SettingsManager();
    }
    return SettingsManager.instance;
  }

  /**
   * Load settings from localStorage or initialize with defaults
   */
  private loadSettings(): SettingsState {
    try {
      // Check if localStorage is available (browser environment)
      if (typeof localStorage !== 'undefined') {
        const stored = localStorage.getItem(SETTINGS_STORAGE_KEY);
        if (stored) {
          const parsedSettings = JSON.parse(stored);
          // Validate and merge with defaults for any missing departments
          return this.validateAndMergeSettings(parsedSettings);
        }
      }
    } catch (error) {
      console.warn('Failed to load settings from localStorage:', error);
    }

    return this.getDefaultSettings();
  }

  /**
   * Validate loaded settings and merge with defaults for missing departments
   */
  private validateAndMergeSettings(settings: Partial<SettingsState>): SettingsState {
    const departments = DEFAULT_DEPARTMENTS.map(defaultDept => {
      const existingDept = settings.departments?.find(d => d.id === defaultDept.id);
      return {
        ...defaultDept,
        employeeCount: existingDept?.employeeCount ?? DEFAULT_EMPLOYEE_COUNTS[defaultDept.id] ?? 1,
        manHours: this.calculateManHours(
          existingDept?.employeeCount ?? DEFAULT_EMPLOYEE_COUNTS[defaultDept.id] ?? 1,
          existingDept?.efficiency ?? defaultDept.efficiency
        )
      };
    });

    return {
      departments,
      lastUpdated: settings.lastUpdated ?? new Date().toISOString()
    };
  }

  /**
   * Get default settings
   */
  private getDefaultSettings(): SettingsState {
    const departments = DEFAULT_DEPARTMENTS.map(dept => ({
      ...dept,
      employeeCount: DEFAULT_EMPLOYEE_COUNTS[dept.id] ?? 1,
      manHours: this.calculateManHours(DEFAULT_EMPLOYEE_COUNTS[dept.id] ?? 1, dept.efficiency)
    }));

    return {
      departments,
      lastUpdated: new Date().toISOString()
    };
  }

  /**
   * Calculate man-hours based on employee count and efficiency
   * Formula: employeeCount * 8 hours * (efficiency / 100)
   */
  public calculateManHours(employeeCount: number, efficiency: number): number {
    if (employeeCount <= 0 || efficiency <= 0) return 0;
    return Math.round(employeeCount * 8 * (efficiency / 100));
  }

  /**
   * Get current settings
   */
  public getSettings(): SettingsState {
    return { ...this.settings };
  }

  /**
   * Get settings as form data (for editing)
   */
  public getSettingsFormData(): SettingsFormData {
    const departments: Record<string, { employeeCount: number; efficiency: number }> = {};

    this.settings.departments.forEach(dept => {
      departments[dept.id] = {
        employeeCount: dept.employeeCount,
        efficiency: dept.efficiency
      };
    });

    return { departments };
  }

  /**
   * Update settings from form data
   */
  public updateSettings(formData: SettingsFormData): void {
    const departments = DEFAULT_DEPARTMENTS.map(defaultDept => {
      const formDataDept = formData.departments[defaultDept.id];
      const employeeCount = Math.max(0, formDataDept?.employeeCount ?? 1);
      const efficiency = Math.max(0, Math.min(100, formDataDept?.efficiency ?? defaultDept.efficiency));

      return {
        ...defaultDept,
        employeeCount,
        efficiency,
        manHours: this.calculateManHours(employeeCount, efficiency)
      };
    });

    this.settings = {
      departments,
      lastUpdated: new Date().toISOString()
    };

    this.saveSettings();
  }

  /**
   * Save settings to localStorage
   */
  private saveSettings(): void {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(this.settings));
      }
    } catch (error) {
      console.error('Failed to save settings to localStorage:', error);
      throw new Error('Failed to save settings');
    }
  }

  /**
   * Reset settings to defaults
   */
  public resetToDefaults(): void {
    this.settings = this.getDefaultSettings();
    this.saveSettings();
  }

  /**
   * Get total man-hours across all departments
   */
  public getTotalManHours(): number {
    return this.settings.departments.reduce((total, dept) => total + dept.manHours, 0);
  }

  /**
   * Get total employees across all departments
   */
  public getTotalEmployees(): number {
    return this.settings.departments.reduce((total, dept) => total + dept.employeeCount, 0);
  }

  /**
   * Get average efficiency across all departments
   */
  public getAverageEfficiency(): number {
    const totalEfficiency = this.settings.departments.reduce((total, dept) => total + dept.efficiency, 0);
    return Math.round(totalEfficiency / this.settings.departments.length);
  }

  /**
   * Get department by ID
   */
  public getDepartment(id: string): DepartmentSettings | undefined {
    return this.settings.departments.find(dept => dept.id === id);
  }

  /**
   * Validate form data
   */
  public validateFormData(formData: SettingsFormData): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    Object.entries(formData.departments).forEach(([deptId, data]) => {
      if (data.employeeCount < 0) {
        errors.push(`${deptId} employee count cannot be negative`);
      }
      if (data.efficiency < 0 || data.efficiency > 100) {
        errors.push(`${deptId} efficiency must be between 0 and 100`);
      }
    });

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

// Export singleton instance
export const settingsManager = SettingsManager.getInstance();

// Export convenience functions
export const getSettings = () => settingsManager.getSettings();
export const updateSettings = (formData: SettingsFormData) => settingsManager.updateSettings(formData);
export const resetSettings = () => settingsManager.resetToDefaults();