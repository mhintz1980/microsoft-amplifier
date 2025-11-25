/**
 * Data Migration Utilities for PumpTracker Lite
 *
 * This module handles data migrations between different versions of the
 * department configuration system.
 */

import {
  Department,
  Vendor,
  EmployeeConfiguration,
  SystemSettings,
  MigrationConfig,
  MigrationStep,
} from '../types/department-config';

// ===== MIGRATION REGISTRY =====

interface MigrationRegistry {
  [fromVersion: string]: {
    [toVersion: string]: MigrationStep[];
  };
}

/**
 * Migration registry for all supported version transitions
 */
const MIGRATION_REGISTRY: MigrationRegistry = {
  // Placeholder for future migrations
  // '0.9.0': { '1.0.0': [/* migration steps */] }
};

// ===== CURRENT MIGRATIONS =====

/**
 * Get available migrations for a version
 */
export function getAvailableMigrations(fromVersion: string, toVersion: string): MigrationStep[] {
  return MIGRATION_REGISTRY[fromVersion]?.[toVersion] || [];
}

/**
 * Check if a migration path exists
 */
export function canMigrate(fromVersion: string, toVersion: string): boolean {
  const migrations = getAvailableMigrations(fromVersion, toVersion);
  return migrations.length > 0;
}

// ===== SPECIFIC MIGRATIONS =====

/**
 * Migrate from old stage-based system to new department system
 * This handles the transition from the original pump tracker data model
 */
export const MIGRATE_TO_V1: MigrationStep[] = [
  {
    id: 'migrate_departments',
    description: 'Migrate department data from legacy format',
    forwardMigration: async (data: any) => {
      // Handle legacy data that might have old department structure
      if (data.departments && Array.isArray(data.departments)) {
        const migratedDepartments = data.departments.map((dept: any) => {
          // Convert old department format to new format
          if (dept.id && typeof dept.id === 'string' && dept.id.match(/^[a-f0-9-]{36}$/)) {
            // Convert UUID to human-readable ID
            const humanReadableId = generateHumanReadableId(dept.displayName || dept.name || 'unknown');
            return {
              ...dept,
              id: humanReadableId,
              // Ensure all required fields are present
              childDepartmentIds: dept.childDepartmentIds || [],
              isActive: dept.isActive !== undefined ? dept.isActive : true,
              sortOrder: dept.sortOrder !== undefined ? dept.sortOrder : 999,
              minCapacity: dept.minCapacity !== undefined ? dept.minCapacity : 1,
              maxCapacity: dept.maxCapacity !== undefined ? dept.maxCapacity : 20,
              workDays: dept.workDays || [1, 2, 3, 4, 5],
              shiftsPerDay: dept.shiftsPerDay || 1,
              hoursPerShift: dept.hoursPerShift || 8,
              defaultProcessingDays: dept.defaultProcessingDays || 1,
              createdAt: dept.createdAt || new Date().toISOString(),
              updatedAt: dept.updatedAt || new Date().toISOString(),
            };
          }
          return dept;
        });

        data.departments = migratedDepartments;
      }

      return data;
    },
    dependencies: [],
  },
  {
    id: 'migrate_vendors',
    description: 'Migrate vendor data and establish powder coat vendors',
    forwardMigration: async (data: any) => {
      // If no vendors exist, create default powder coat vendors
      if (!data.vendors || data.vendors.length === 0) {
        const powderCoatDept = data.departments?.find((d: any) =>
          d.id === 'powder_coat' || d.displayName?.toLowerCase().includes('powder')
        );

        if (powderCoatDept) {
          data.vendors = [
            {
              id: 'powder_coat_vendor_1',
              departmentId: powderCoatDept.id,
              name: 'vendor_1',
              displayName: 'Vendor A - Primary',
              contactInfo: {
                email: 'vendor-a@example.com',
                phone: '555-0101',
              },
              weeklyCapacity: 21,
              currentLoad: 0,
              qualityRating: 5,
              averageLeadTime: 7,
              leadTimeDays: 7,
              bufferDays: 2,
              preferredLoad: 15,
              isActive: true,
              isPreferred: true,
              swimlaneColor: '#8b5cf6',
              swimlanePosition: 1,
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
            },
            {
              id: 'powder_coat_vendor_2',
              departmentId: powderCoatDept.id,
              name: 'vendor_2',
              displayName: 'Vendor B - Secondary',
              contactInfo: {
                email: 'vendor-b@example.com',
                phone: '555-0102',
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
              swimlaneColor: '#a78bfa',
              swimlanePosition: 2,
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
            },
            {
              id: 'powder_coat_vendor_3',
              departmentId: powderCoatDept.id,
              name: 'vendor_3',
              displayName: 'Vendor C - Backup',
              contactInfo: {
                email: 'vendor-c@example.com',
                phone: '555-0103',
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
              swimlaneColor: '#c4b5fd',
              swimlanePosition: 3,
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
            },
          ];
        }
      }

      return data;
    },
    dependencies: ['migrate_departments'],
  },
  {
    id: 'migrate_system_settings',
    description: 'Create system settings with default values',
    forwardMigration: async (data: any) => {
      if (!data.systemSettings) {
        data.systemSettings = {
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
          settingsVersion: '1.0.0',
          lastUpdated: new Date().toISOString(),
          updatedBy: 'migration',
        };
      } else {
        // Ensure version is updated
        data.systemSettings.settingsVersion = '1.0.0';
        data.systemSettings.lastUpdated = new Date().toISOString();
        data.systemSettings.updatedBy = 'migration';
      }

      return data;
    },
    dependencies: [],
  },
  {
    id: 'update_department_capacity',
    description: 'Update department capacity based on new vendor system',
    forwardMigration: async (data: any) => {
      if (data.departments && data.vendors) {
        const powderCoatVendors = data.vendors.filter((v: any) =>
          v.departmentId === 'powder_coat' || v.departmentId?.includes('powder')
        );

        if (powderCoatVendors.length > 0) {
          const powderCoatDept = data.departments.find((d: any) =>
            d.id === 'powder_coat' || d.displayName?.toLowerCase().includes('powder')
          );

          if (powderCoatDept) {
            // Update powder coat department capacity based on vendors
            const totalVendorCapacity = powderCoatVendors.reduce((sum: number, v: any) =>
              sum + v.weeklyCapacity, 0
            );

            powderCoatDept.defaultDailyCapacity = Math.floor(totalVendorCapacity / 7);
            powderCoatDept.maxCapacity = Math.floor(totalVendorCapacity / 5); // Assume 5 working days
          }
        }
      }

      return data;
    },
    dependencies: ['migrate_vendors'],
  },
];

// Add the migration to registry
MIGRATION_REGISTRY['0.9.0'] = { '1.0.0': MIGRATE_TO_V1 };

// ===== UTILITY FUNCTIONS =====

/**
 * Generate human-readable ID from display name
 */
function generateHumanReadableId(displayName: string): string {
  return displayName
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '') // Remove special characters
    .replace(/\s+/g, '_') // Replace spaces with underscores
    .replace(/_+/g, '_') // Remove duplicate underscores
    .replace(/^_|_$/g, '') // Remove leading/trailing underscores
    .substring(0, 50); // Limit length
}

/**
 * Validate migration dependencies
 */
function validateDependencies(migrations: MigrationStep[]): string[] {
  const errors: string[] = [];
  const stepIds = new Set(migrations.map(m => m.id));

  migrations.forEach(migration => {
    migration.dependencies.forEach(dep => {
      if (!stepIds.has(dep)) {
        errors.push(`Migration '${migration.id}' depends on '${dep}' which is not included`);
      }
    });
  });

  return errors;
}

/**
 * Sort migrations based on dependencies
 */
function sortMigrationsByDependencies(migrations: MigrationStep[]): MigrationStep[] {
  const sorted: MigrationStep[] = [];
  const remaining = [...migrations];
  let iterations = 0;
  const maxIterations = migrations.length * 2;

  while (remaining.length > 0 && iterations < maxIterations) {
    let progress = false;

    for (let i = remaining.length - 1; i >= 0; i--) {
      const migration = remaining[i];

      // Check if all dependencies are satisfied
      const dependenciesSatisfied = migration.dependencies.every(dep =>
        sorted.some(s => s.id === dep)
      );

      if (dependenciesSatisfied) {
        sorted.push(migration);
        remaining.splice(i, 1);
        progress = true;
      }
    }

    if (!progress) {
      // Circular dependency or missing dependency
      throw new Error(`Cannot resolve migration dependencies. Remaining: ${remaining.map(m => m.id).join(', ')}`);
    }

    iterations++;
  }

  if (remaining.length > 0) {
    throw new Error(`Migration resolution failed. Remaining: ${remaining.map(m => m.id).join(', ')}`);
  }

  return sorted;
}

// ===== MAIN MIGRATION FUNCTIONS =====

/**
 * Run migration from one version to another
 */
export async function runMigration(
  data: any,
  fromVersion: string,
  toVersion: string
): Promise<any> {
  console.log(`Starting migration from ${fromVersion} to ${toVersion}`);

  const migrations = getAvailableMigrations(fromVersion, toVersion);

  if (migrations.length === 0) {
    console.log('No migrations found, data is already at target version');
    return data;
  }

  // Validate dependencies
  const dependencyErrors = validateDependencies(migrations);
  if (dependencyErrors.length > 0) {
    throw new Error(`Migration dependency errors: ${dependencyErrors.join(', ')}`);
  }

  // Sort migrations by dependencies
  const sortedMigrations = sortMigrationsByDependencies(migrations);

  let migratedData = { ...data };
  let migrationCount = 0;

  try {
    for (const migration of sortedMigrations) {
      console.log(`Running migration: ${migration.description}`);
      migratedData = await migration.forwardMigration(migratedData);
      migrationCount++;
    }

    console.log(`Successfully completed ${migrationCount} migrations`);
    return migratedData;
  } catch (error) {
    console.error(`Migration failed at step ${migrationCount}:`, error);
    throw new Error(`Migration failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Check if data needs migration
 */
export function needsMigration(data: any, targetVersion: string): boolean {
  const currentVersion = data.systemSettings?.settingsVersion || data.schemaVersion || '0.9.0';

  if (currentVersion === targetVersion) {
    return false;
  }

  return canMigrate(currentVersion, targetVersion);
}

/**
 * Get migration plan without executing it
 */
export function getMigrationPlan(fromVersion: string, toVersion: string): MigrationConfig | null {
  const migrations = getAvailableMigrations(fromVersion, toVersion);

  if (migrations.length === 0) {
    return null;
  }

  return {
    fromVersion,
    toVersion,
    migrations,
  };
}

/**
 * Auto-detect current version from data
 */
export function detectCurrentVersion(data: any): string {
  // Try different version indicators
  if (data.systemSettings?.settingsVersion) {
    return data.systemSettings.settingsVersion;
  }

  if (data.schemaVersion) {
    return data.schemaVersion;
  }

  if (data.configVersion) {
    return data.configVersion;
  }

  // Check for legacy indicators
  if (data.departments && Array.isArray(data.departments)) {
    const hasHumanReadableIds = data.departments.some((dept: any) =>
      typeof dept.id === 'string' && !dept.id.match(/^[a-f0-9-]{36}$/)
    );

    if (hasHumanReadableIds) {
      return '1.0.0'; // Already has human-readable IDs
    }
  }

  // Default to legacy version
  return '0.9.0';
}

// ===== BACKUP AND RESTORE =====

/**
 * Create backup before migration
 */
export function createMigrationBackup(data: any): string {
  const backup = {
    timestamp: new Date().toISOString(),
    version: detectCurrentVersion(data),
    data: JSON.parse(JSON.stringify(data)), // Deep clone
  };

  return JSON.stringify(backup, null, 2);
}

/**
 * Restore from backup
 */
export function restoreFromBackup(backupJson: string): any {
  try {
    const backup = JSON.parse(backupJson);
    return backup.data;
  } catch (error) {
    throw new Error(`Failed to restore from backup: ${error instanceof Error ? error.message : 'Invalid backup format'}`);
  }
}

export default {
  runMigration,
  needsMigration,
  getMigrationPlan,
  detectCurrentVersion,
  createMigrationBackup,
  restoreFromBackup,
  getAvailableMigrations,
  canMigrate,
};