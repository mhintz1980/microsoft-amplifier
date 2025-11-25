/**
 * Capacity and Man-Hours Calculation Utilities
 *
 * This module provides calculation functions for department capacities,
 * man-hours, and scheduling logic for PumpTracker Lite.
 */

import {
  Department,
  Vendor,
  EmployeeConfiguration,
  DailyCapacity,
  ManHoursCalculation,
  ValidationResult,
  ValidationError,
  ValidationWarning,
} from '../types/department-config';

// ===== VALIDATION UTILITIES =====

/**
 * Validate department configuration
 */
export function validateDepartment(department: Department): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationWarning[] = [];

  // Required fields
  if (!department.id || department.id.trim() === '') {
    errors.push({
      field: 'id',
      message: 'Department ID is required',
      code: 'REQUIRED_FIELD'
    });
  }

  if (!department.displayName || department.displayName.trim() === '') {
    errors.push({
      field: 'displayName',
      message: 'Display name is required',
      code: 'REQUIRED_FIELD'
    });
  }

  // Logical constraints
  if (department.minCapacity > department.maxCapacity) {
    errors.push({
      field: 'minCapacity',
      message: 'Minimum capacity cannot be greater than maximum capacity',
      code: 'INVALID_RANGE'
    });
  }

  if (department.defaultDailyCapacity < department.minCapacity ||
      department.defaultDailyCapacity > department.maxCapacity) {
    warnings.push({
      field: 'defaultDailyCapacity',
      message: 'Default capacity is outside min-max range',
      code: 'OUT_OF_RANGE'
    });
  }

  if (department.hoursPerShift <= 0 || department.hoursPerShift > 24) {
    errors.push({
      field: 'hoursPerShift',
      message: 'Hours per shift must be between 1 and 24',
      code: 'INVALID_RANGE'
    });
  }

  if (department.shiftsPerDay <= 0 || department.shiftsPerDay > 3) {
    warnings.push({
      field: 'shiftsPerDay',
      message: 'Unusual number of shifts per day',
      code: 'UNUSUAL_VALUE'
    });
  }

  // Work days validation
  if (department.workDays.length === 0) {
    errors.push({
      field: 'workDays',
      message: 'At least one work day must be specified',
      code: 'REQUIRED_FIELD'
    });
  }

  department.workDays.forEach(day => {
    if (day < 0 || day > 6) {
      errors.push({
        field: 'workDays',
        message: `Invalid work day: ${day}. Must be 0-6 (Sunday=0)`,
        code: 'INVALID_VALUE'
      });
    }
  });

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * Validate vendor configuration
 */
export function validateVendor(vendor: Vendor): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationWarning[] = [];

  // Required fields
  if (!vendor.id || vendor.id.trim() === '') {
    errors.push({
      field: 'id',
      message: 'Vendor ID is required',
      code: 'REQUIRED_FIELD'
    });
  }

  if (!vendor.name || vendor.name.trim() === '') {
    errors.push({
      field: 'name',
      message: 'Vendor name is required',
      code: 'REQUIRED_FIELD'
    });
  }

  if (!vendor.departmentId || vendor.departmentId.trim() === '') {
    errors.push({
      field: 'departmentId',
      message: 'Department ID is required',
      code: 'REQUIRED_FIELD'
    });
  }

  // Logical constraints
  if (vendor.weeklyCapacity <= 0) {
    errors.push({
      field: 'weeklyCapacity',
      message: 'Weekly capacity must be greater than 0',
      code: 'INVALID_RANGE'
    });
  }

  if (vendor.currentLoad < 0) {
    errors.push({
      field: 'currentLoad',
      message: 'Current load cannot be negative',
      code: 'INVALID_RANGE'
    });
  }

  if (vendor.currentLoad > vendor.weeklyCapacity) {
    warnings.push({
      field: 'currentLoad',
      message: 'Current load exceeds weekly capacity',
      code: 'CAPACITY_EXCEEDED'
    });
  }

  if (vendor.qualityRating < 1 || vendor.qualityRating > 5) {
    errors.push({
      field: 'qualityRating',
      message: 'Quality rating must be between 1 and 5',
      code: 'INVALID_RANGE'
    });
  }

  if (vendor.leadTimeDays <= 0) {
    errors.push({
      field: 'leadTimeDays',
      message: 'Lead time must be greater than 0',
      code: 'INVALID_RANGE'
    });
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
}

// ===== CAPACITY CALCULATIONS =====

/**
 * Calculate daily capacity for a department
 */
export function calculateDailyCapacity(
  department: Department,
  employees: EmployeeConfiguration[],
  vendors: Vendor[] = [],
  date: Date = new Date()
): DailyCapacity {
  const dateStr = date.toISOString().split('T')[0];
  const dayOfWeek = date.getDay();

  // Check if this is a work day
  const isWorkDay = department.workDays.includes(dayOfWeek);
  if (!isWorkDay) {
    return {
      date: dateStr,
      departmentId: department.id,
      availableEmployees: 0,
      employeeHours: 0,
      operatingHours: 0,
      theoreticalCapacity: 0,
      practicalCapacity: 0,
      scheduledLoad: 0,
      availableCapacity: 0,
      vendorCapacities: []
    };
  }

  // Filter active employees for this department
  const activeEmployees = employees.filter(emp =>
    emp.departmentId === department.id &&
    emp.isActive &&
    emp.workDays.includes(dayOfWeek)
  );

  // Calculate employee hours
  const employeeHours = activeEmployees.reduce((total, emp) => {
    return total + (emp.hoursPerShift * emp.shiftsPerDay);
  }, 0);

  // Calculate operating hours
  const operatingHours = department.hoursPerShift * department.shiftsPerDay;

  // Calculate capacity based on employees
  const totalEfficiency = activeEmployees.reduce((sum, emp) => sum + emp.efficiency, 0);
  const avgEfficiency = activeEmployees.length > 0 ? totalEfficiency / activeEmployees.length : 0;

  // Theoretical capacity based on employee hours
  const theoreticalCapacity = activeEmployees.reduce((total, emp) => {
    return total + (emp.pumpsPerShift * emp.shiftsPerDay);
  }, 0);

  // Practical capacity considering efficiency
  const practicalCapacity = Math.floor(theoreticalCapacity * avgEfficiency);

  // Get current scheduled load (this would typically come from the pump data)
  const scheduledLoad = 0; // Placeholder - would query actual scheduled pumps

  // Calculate vendor capacities if this department uses vendors
  const vendorCapacities = vendors
    .filter(v => v.departmentId === department.id && v.isActive)
    .map(vendor => ({
      vendorId: vendor.id,
      vendorName: vendor.displayName,
      capacity: Math.floor(vendor.weeklyCapacity / 7), // Daily capacity
      currentLoad: vendor.currentLoad,
      availableCapacity: Math.floor(vendor.weeklyCapacity / 7) - vendor.currentLoad
    }));

  // Total capacity includes both internal and vendor capacity
  const totalVendorCapacity = vendorCapacities.reduce((sum, v) => sum + v.capacity, 0);
  const totalCapacity = Math.max(practicalCapacity, totalVendorCapacity, 0);

  return {
    date: dateStr,
    departmentId: department.id,
    availableEmployees: activeEmployees.length,
    employeeHours,
    operatingHours,
    theoreticalCapacity,
    practicalCapacity,
    scheduledLoad,
    availableCapacity: totalCapacity - scheduledLoad,
    vendorCapacities
  };
}

/**
 * Calculate man-hours for a date range
 */
export function calculateManHours(
  department: Department,
  employees: EmployeeConfiguration[],
  startDate: Date,
  endDate: Date
): ManHoursCalculation {
  const dateRange = {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0]
  };

  // Filter active employees for this department
  const activeEmployees = employees.filter(emp =>
    emp.departmentId === department.id && emp.isActive
  );

  // Calculate total work days in range
  const workDays = getWorkDaysInRange(department.workDays, startDate, endDate);
  const totalWorkDays = workDays.length;

  // Calculate total available hours
  const totalAvailableHours = activeEmployees.reduce((total, emp) => {
    const employeeWorkDays = workDays.filter(day => emp.workDays.includes(day));
    return total + (employeeWorkDays.length * emp.hoursPerShift * emp.shiftsPerDay);
  }, 0);

  // Calculate scheduled hours (considering shifts)
  const totalScheduledHours = activeEmployees.reduce((total, emp) => {
    return total + (totalWorkDays * emp.hoursPerShift * emp.shiftsPerDay);
  }, 0);

  // Calculate efficiency metrics
  const totalEfficiency = activeEmployees.reduce((sum, emp) => sum + emp.efficiency, 0);
  const averageEfficiency = activeEmployees.length > 0 ? totalEfficiency / activeEmployees.length : 0;

  // Calculate effective man-hours
  const effectiveManHours = totalAvailableHours * averageEfficiency;

  // Calculate production capacity
  const maxPumpCapacity = activeEmployees.reduce((total, emp) => {
    const employeeWorkDays = workDays.filter(day => emp.workDays.includes(day));
    return total + (employeeWorkDays.length * emp.pumpsPerShift * emp.shiftsPerDay);
  }, 0);

  // Calculate daily capacities
  const dailyCapacities = workDays.map(date =>
    calculateDailyCapacity(department, employees, [], date)
  );

  const currentScheduledPumps = 0; // Placeholder - would query actual scheduled pumps

  return {
    departmentId: department.id,
    dateRange,
    totalEmployees: activeEmployees.length,
    totalScheduledHours,
    totalAvailableHours,
    totalManHours: totalAvailableHours,
    averageEfficiency,
    effectiveManHours,
    maxPumpCapacity,
    currentScheduledPumps,
    availableCapacity: maxPumpCapacity - currentScheduledPumps,
    dailyCapacities
  };
}

/**
 * Calculate optimal vendor allocation for pumps
 */
export function calculateVendorAllocation(
  vendors: Vendor[],
  pumpsToAllocate: number,
  priorityVendorId?: string
): Array<{ vendorId: string; pumps: number; vendor: Vendor }> {
  const activeVendors = vendors
    .filter(v => v.isActive)
    .sort((a, b) => {
      // Sort by priority first, then by capacity
      if (a.isPreferred && !b.isPreferred) return -1;
      if (!a.isPreferred && b.isPreferred) return 1;
      return (b.weeklyCapacity - b.currentLoad) - (a.weeklyCapacity - a.currentLoad);
    });

  const allocation: Array<{ vendorId: string; pumps: number; vendor: Vendor }> = [];
  let remainingPumps = pumpsToAllocate;

  // If priority vendor specified, allocate to them first
  if (priorityVendorId) {
    const priorityVendor = activeVendors.find(v => v.id === priorityVendorId);
    if (priorityVendor) {
      const availableCapacity = priorityVendor.weeklyCapacity - priorityVendor.currentLoad;
      const allocateToPriority = Math.min(remainingPumps, availableCapacity);

      if (allocateToPriority > 0) {
        allocation.push({
          vendorId: priorityVendor.id,
          pumps: allocateToPriority,
          vendor: priorityVendor
        });
        remainingPumps -= allocateToPriority;
      }
    }
  }

  // Allocate remaining pumps to other vendors
  for (const vendor of activeVendors) {
    if (remainingPumps <= 0) break;
    if (vendor.id === priorityVendorId) continue; // Already allocated

    const availableCapacity = vendor.weeklyCapacity - vendor.currentLoad;
    const allocateToVendor = Math.min(remainingPumps, availableCapacity);

    if (allocateToVendor > 0) {
      allocation.push({
        vendorId: vendor.id,
        pumps: allocateToVendor,
        vendor
      });
      remainingPumps -= allocateToVendor;
    }
  }

  return allocation;
}

// ===== UTILITY FUNCTIONS =====

/**
 * Get work days within a date range for a department
 */
function getWorkDaysInRange(workDays: number[], startDate: Date, endDate: Date): Date[] {
  const workDates: Date[] = [];
  const current = new Date(startDate);

  while (current <= endDate) {
    if (workDays.includes(current.getDay())) {
      workDates.push(new Date(current));
    }
    current.setDate(current.getDate() + 1);
  }

  return workDates;
}

/**
 * Calculate days between two dates
 */
export function daysBetween(startDate: Date, endDate: Date): number {
  const timeDiff = endDate.getTime() - startDate.getTime();
  return Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
}

/**
 * Add work days to a date, skipping non-work days
 */
export function addWorkDays(
  startDate: Date,
  daysToAdd: number,
  workDays: number[]
): Date {
  const result = new Date(startDate);
  let daysAdded = 0;

  while (daysAdded < daysToAdd) {
    result.setDate(result.getDate() + 1);
    if (workDays.includes(result.getDay())) {
      daysAdded++;
    }
  }

  return result;
}

/**
 * Format capacity for display
 */
export function formatCapacity(capacity: number): string {
  if (capacity === 0) return '0';
  if (capacity < 1) return '< 1';
  return capacity.toString();
}

/**
 * Get capacity utilization color
 */
export function getCapacityUtilizationColor(utilization: number): string {
  if (utilization >= 0.9) return '#ef4444'; // red-500 (critical)
  if (utilization >= 0.8) return '#f59e0b'; // amber-500 (warning)
  if (utilization >= 0.6) return '#eab308'; // yellow-500 (moderate)
  return '#10b981'; // emerald-500 (good)
}

/**
 * Calculate capacity utilization percentage
 */
export function calculateCapacityUtilization(current: number, maximum: number): number {
  if (!maximum || maximum <= 0) return 0;
  return Math.min(current / maximum, 1);
}

// ===== SCHEDULING UTILITIES =====

/**
 * Calculate estimated completion date for a pump
 */
export function calculateEstimatedCompletion(
  currentStage: string,
  departmentConfigs: Department[],
  vendorConfigs: Vendor[] = [],
  startDate: Date = new Date()
): Date {
  // Define stage order and lead times
  const stageOrder = ['FABRICATION', 'POWDER_COAT', 'ASSEMBLY', 'TESTING'];
  const currentStageIndex = stageOrder.indexOf(currentStage);

  if (currentStageIndex === -1 || currentStageIndex === stageOrder.length - 1) {
    return startDate; // Already at final stage or invalid stage
  }

  let completionDate = new Date(startDate);

  // Add lead times for remaining stages
  for (let i = currentStageIndex + 1; i < stageOrder.length; i++) {
    const stageName = stageOrder[i];
    const department = departmentConfigs.find(d =>
      d.id.toLowerCase() === stageName.toLowerCase()
    );

    if (department) {
      // Check if department uses vendors
      const vendors = vendorConfigs.filter(v => v.departmentId === department.id);
      if (vendors.length > 0) {
        // Use average vendor lead time
        const avgLeadTime = vendors.reduce((sum, v) => sum + v.leadTimeDays, 0) / vendors.length;
        completionDate = addWorkDays(completionDate, Math.ceil(avgLeadTime), department.workDays);
      } else {
        // Use department default processing time
        completionDate = addWorkDays(
          completionDate,
          Math.ceil(department.defaultProcessingDays),
          department.workDays
        );
      }
    }
  }

  return completionDate;
}

/**
 * Get critical path for pump completion
 */
export function getCriticalPath(
  currentStage: string,
  departmentConfigs: Department[],
  vendorConfigs: Vendor[] = []
): Array<{ stage: string; days: number; department: string; vendor?: string }> {
  const stageOrder = ['FABRICATION', 'POWDER_COAT', 'ASSEMBLY', 'TESTING'];
  const currentStageIndex = stageOrder.indexOf(currentStage);

  if (currentStageIndex === -1 || currentStageIndex === stageOrder.length - 1) {
    return [];
  }

  const criticalPath: Array<{ stage: string; days: number; department: string; vendor?: string }> = [];

  for (let i = currentStageIndex + 1; i < stageOrder.length; i++) {
    const stageName = stageOrder[i];
    const department = departmentConfigs.find(d =>
      d.id.toLowerCase() === stageName.toLowerCase()
    );

    if (department) {
      const vendors = vendorConfigs.filter(v => v.departmentId === department.id);
      let days: number;
      let vendor: string | undefined;

      if (vendors.length > 0) {
        // Use preferred vendor or best available
        const preferredVendor = vendors.find(v => v.isPreferred) || vendors[0];
        days = preferredVendor.leadTimeDays;
        vendor = preferredVendor.displayName;
      } else {
        days = department.defaultProcessingDays;
      }

      criticalPath.push({
        stage: stageName,
        days: Math.ceil(days),
        department: department.displayName,
        vendor
      });
    }
  }

  return criticalPath;
}