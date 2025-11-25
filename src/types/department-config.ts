/**
 * Department Configuration Types for PumpTracker Lite
 *
 * This module defines the data structures for managing departments,
 * vendors, man-hours calculations, and system settings.
 */

// ===== CORE DEPARTMENT TYPES =====

/**
 * Department configuration with human-readable identifiers
 */
export interface Department {
  id: string; // Human-readable ID like 'fabrication', 'powder_coat'
  displayName: string; // User-friendly name like "Fabrication"
  description?: string;
  color: string; // UI color code for swimlanes

  // Hierarchy support
  parentDepartmentId?: string; // For nested departments
  childDepartmentIds: string[]; // Sub-departments

  // Capacity and scheduling
  isActive: boolean;
  sortOrder: number; // Display order in UI

  // Production configuration
  defaultDailyCapacity: number; // Default pumps per day
  minCapacity: number; // Minimum capacity constraint
  maxCapacity: number; // Maximum capacity constraint

  // Operating schedule
  workDays: number[]; // Days of week (0-6, Sunday=0)
  shiftsPerDay: number;
  hoursPerShift: number;

  // Processing time defaults
  defaultProcessingDays: number; // Default time per pump

  // Metadata
  createdAt: string; // ISO timestamp
  updatedAt: string; // ISO timestamp
}

/**
 * Vendor configuration for departments with multiple vendors
 */
export interface Vendor {
  id: string; // Human-readable ID like 'powder_coat_vendor_1'
  departmentId: string; // Reference to department

  // Basic info
  name: string; // Vendor name
  displayName: string; // Display name
  contactInfo?: {
    email?: string;
    phone?: string;
    address?: string;
  };

  // Capacity and performance
  weeklyCapacity: number; // Pumps per week
  currentLoad: number; // Currently assigned pumps
  qualityRating: number; // 1-5 rating
  averageLeadTime: number; // Days

  // Scheduling
  leadTimeDays: number; // Standard lead time
  bufferDays: number; // Buffer for scheduling
  preferredLoad: number; // Optimal workload

  // Status
  isActive: boolean;
  isPreferred: boolean; // Preferred vendor

  // Swimlane configuration
  swimlaneColor: string; // UI color for this vendor's swimlane
  swimlanePosition: number; // Position in department

  // Metadata
  createdAt: string;
  updatedAt: string;
}

/**
 * Employee configuration for man-hours calculations
 */
export interface EmployeeConfiguration {
  id: string; // Human-readable ID like 'fab_lead_tech'

  // Basic info
  name: string;
  role: string;
  departmentId: string;

  // Schedule
  hoursPerShift: number; // Hours worked per shift
  shiftsPerDay: number; // Number of shifts per day
  workDays: number[]; // Days of week (0-6)

  // Productivity
  efficiency: number; // 0.1 to 1.0 (10% to 100% efficiency)
  pumpsPerShift: number; // Pumps completed per shift
  skillLevel: 'junior' | 'intermediate' | 'senior' | 'lead';

  // Cost and utilization
  hourlyRate?: number; // For cost calculations
  utilizationTarget: number; // Target utilization (0-1)

  // Status
  isActive: boolean;
  isCrossTrained: boolean; // Can work in other departments
  crossTrainedDepartments: string[]; // IDs of other departments

  // Metadata
  createdAt: string;
  updatedAt: string;
}

// ===== CALCULATION RESULT TYPES =====

/**
 * Daily capacity calculation result
 */
export interface DailyCapacity {
  date: string; // ISO date
  departmentId: string;

  // Input values
  availableEmployees: number;
  employeeHours: number;
  operatingHours: number;

  // Calculated values
  theoreticalCapacity: number; // Based on employee hours
  practicalCapacity: number; // Considering efficiency
  scheduledLoad: number; // Currently scheduled
  availableCapacity: number; // practicalCapacity - scheduledLoad

  // Vendor breakdown (for departments with vendors)
  vendorCapacities: Array<{
    vendorId: string;
    vendorName: string;
    capacity: number;
    currentLoad: number;
    availableCapacity: number;
  }>;
}

/**
 * Man-hours calculation result
 */
export interface ManHoursCalculation {
  departmentId: string;
  dateRange: {
    startDate: string;
    endDate: string;
  };

  // Employee breakdown
  totalEmployees: number;
  totalScheduledHours: number;
  totalAvailableHours: number;

  // Capacity metrics
  totalManHours: number; // Available man-hours
  averageEfficiency: number; // Weighted average
  effectiveManHours: number; // After efficiency adjustment

  // Production capacity
  maxPumpCapacity: number;
  currentScheduledPumps: number;
  availableCapacity: number;

  // Daily breakdown
  dailyCapacities: DailyCapacity[];
}

// ===== CONFIGURATION SETTINGS =====

/**
 * System-wide configuration settings
 */
export interface SystemSettings {
  // General settings
  organizationName: string;
  timezone: string;
  dateFormat: string;
  currency: string;

  // Scheduling settings
  defaultLeadTimes: Record<string, number>; // Department ID -> days
  capacityBuffer: number; // Percentage buffer (0-1)
  autoRescheduleThreshold: number; // Days to look ahead

  // UI settings
  defaultView: 'kanban' | 'calendar' | 'list';
  workingDaysStartHour: number; // 0-23
  workingDaysEndHour: number; // 0-23

  // Notification settings
  enableNotifications: boolean;
  overdueThreshold: number; // Days before marking as overdue
  capacityAlertThreshold: number; // Percentage (0-1)

  // Data settings
  autoSave: boolean;
  dataRetentionDays: number;
  enableAuditLog: boolean;

  // Version and metadata
  settingsVersion: string;
  lastUpdated: string;
  updatedBy: string;
}

/**
 * Department-specific settings override
 */
export interface DepartmentSettings {
  departmentId: string;

  // Override system defaults
  workingDaysStartHour?: number;
  workingDaysEndHour?: number;
  defaultLeadTime?: number;
  capacityBuffer?: number;

  // Department-specific settings
  enableVendorAllocation: boolean;
  requireLeadAssignment: boolean;
  qualityCheckRequired: boolean;

  // Scheduling rules
  maxConcurrentJobs?: number;
  minTimeBetweenJobs?: number; // Hours
  setupTimeRequired?: number; // Hours

  // Quality settings
  qualityStandards: string[];
  inspectionCheckpoints: string[];

  // Metadata
  lastUpdated: string;
  updatedBy: string;
}

// ===== VALIDATION TYPES =====

/**
 * Configuration validation result
 */
export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationWarning {
  field: string;
  message: string;
  code: string;
}

// ===== MIGRATION TYPES =====

/**
 * Data migration configuration
 */
export interface MigrationConfig {
  fromVersion: string;
  toVersion: string;
  migrations: MigrationStep[];
}

export interface MigrationStep {
  id: string;
  description: string;
  forwardMigration: (data: any) => Promise<any>;
  rollbackMigration?: (data: any) => Promise<any>;
  dependencies: string[]; // Other step IDs that must run first
}

// ===== ENUMS =====

export type DepartmentStatus = 'active' | 'inactive' | 'maintenance';
export type VendorStatus = 'active' | 'inactive' | 'on_hold';
export type EmployeeStatus = 'active' | 'on_leave' | 'training' | 'inactive';

// ===== DEFAULT CONFIGURATIONS =====

/**
 * Default department configurations
 */
export const DEFAULT_DEPARTMENTS: Omit<Department, 'id' | 'createdAt' | 'updatedAt'>[] = [
  {
    displayName: "Fabrication",
    description: "Metal fabrication and structural assembly",
    color: "#3b82f6", // blue-500
    childDepartmentIds: [],
    isActive: true,
    sortOrder: 1,
    defaultDailyCapacity: 8,
    minCapacity: 2,
    maxCapacity: 12,
    workDays: [1, 2, 3, 4, 5], // Monday-Friday
    shiftsPerDay: 1,
    hoursPerShift: 8,
    defaultProcessingDays: 1.5,
  },
  {
    displayName: "Powder Coat",
    description: "Surface preparation and powder coating",
    color: "#8b5cf6", // violet-500
    childDepartmentIds: [],
    isActive: true,
    sortOrder: 2,
    defaultDailyCapacity: 21, // 3 vendors × 7 pumps each
    minCapacity: 7,
    maxCapacity: 30,
    workDays: [1, 2, 3, 4, 5],
    shiftsPerDay: 1,
    hoursPerShift: 8,
    defaultProcessingDays: 7,
  },
  {
    displayName: "Assembly",
    description: "Final assembly and integration",
    color: "#10b981", // emerald-500
    childDepartmentIds: [],
    isActive: true,
    sortOrder: 3,
    defaultDailyCapacity: 6,
    minCapacity: 1,
    maxCapacity: 10,
    workDays: [1, 2, 3, 4, 5],
    shiftsPerDay: 1,
    hoursPerShift: 8,
    defaultProcessingDays: 1,
  },
  {
    displayName: "Testing",
    description: "Quality testing and performance verification",
    color: "#f59e0b", // amber-500
    childDepartmentIds: [],
    isActive: true,
    sortOrder: 4,
    defaultDailyCapacity: 4,
    minCapacity: 1,
    maxCapacity: 8,
    workDays: [1, 2, 3, 4, 5],
    shiftsPerDay: 1,
    hoursPerShift: 8,
    defaultProcessingDays: 0.25,
  },
];

/**
 * Default powder coat vendors
 */
export const DEFAULT_POWDER_COAT_VENDORS: Omit<Vendor, 'id' | 'departmentId' | 'createdAt' | 'updatedAt'>[] = [
  {
    name: "vendor_1",
    displayName: "Vendor A - Primary",
    contactInfo: {
      email: "vendor-a@example.com",
      phone: "555-0101",
    },
    weeklyCapacity: 21, // 3 pumps per day × 7 days
    currentLoad: 0,
    qualityRating: 5,
    averageLeadTime: 7,
    leadTimeDays: 7,
    bufferDays: 2,
    preferredLoad: 15,
    isActive: true,
    isPreferred: true,
    swimlaneColor: "#8b5cf6", // violet-500
    swimlanePosition: 1,
  },
  {
    name: "vendor_2",
    displayName: "Vendor B - Secondary",
    contactInfo: {
      email: "vendor-b@example.com",
      phone: "555-0102",
    },
    weeklyCapacity: 21,
    currentLoad: 0,
    qualityRating: 4,
    averageLeadTime: 8,
    leadTimeDays: 8,
    bufferDays: 3,
    preferredLoad: 12,
    isActive: true,
    isPreferred: false,
    swimlaneColor: "#a78bfa", // violet-400
    swimlanePosition: 2,
  },
  {
    name: "vendor_3",
    displayName: "Vendor C - Backup",
    contactInfo: {
      email: "vendor-c@example.com",
      phone: "555-0103",
    },
    weeklyCapacity: 21,
    currentLoad: 0,
    qualityRating: 3,
    averageLeadTime: 10,
    leadTimeDays: 10,
    bufferDays: 4,
    preferredLoad: 10,
    isActive: true,
    isPreferred: false,
    swimlaneColor: "#c4b5fd", // violet-300
    swimlanePosition: 3,
  },
];