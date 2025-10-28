#!/usr/bin/env tsx

/**
 * Migration Script: Original Data -> Denormalized Format
 *
 * This script transforms the original pumptracker-data.json into the
 * optimized denormalized format for better UI performance.
 */

import fs from 'fs';
import path from 'path';
import { migrateOriginalData, generateDataSummary } from '../utils/data-transformer';

// Configuration
const CONFIG = {
  originalDataPath: path.join(__dirname, '../../content/pumptracker-lite/pumptracker-data.json'),
  outputPath: path.join(__dirname, '../../src/data/denormalized-models.json'),
  summaryPath: path.join(__dirname, '../../src/data/migration-summary.json'),
  backupOriginal: true
};

/**
 * Main migration function
 */
async function migrateData(): Promise<void> {
  console.log('🚀 Starting data migration to denormalized format...\n');

  try {
    // 1. Load original data
    console.log('📖 Loading original data...');
    const originalData = loadOriginalData();
    console.log(`✅ Loaded ${originalData.models.length} pump models`);

    // 2. Create backup if enabled
    if (CONFIG.backupOriginal) {
      await createBackup();
      console.log('💾 Created backup of original data');
    }

    // 3. Migrate to denormalized format
    console.log('\n🔄 Transforming data to denormalized format...');
    const migratedData = migrateOriginalData(originalData);
    console.log(`✅ Migrated ${Object.keys(migratedData.models).length} models`);

    // 4. Generate summary
    console.log('\n📊 Generating migration summary...');
    const summary = generateDataSummary({
      models: migratedData.models,
      pumps: migratedData.pumps,
      purchaseOrders: migratedData.purchaseOrders
    });

    // 5. Write output files
    console.log('\n💾 Writing output files...');
    await writeOutputFiles(migratedData, summary);

    // 6. Display migration results
    displayMigrationResults(migratedData, summary);

    console.log('\n🎉 Migration completed successfully!');

  } catch (error) {
    console.error('\n❌ Migration failed:', error);
    process.exit(1);
  }
}

/**
 * Load original pump data
 */
function loadOriginalData(): any {
  const filePath = CONFIG.originalDataPath;

  if (!fs.existsSync(filePath)) {
    throw new Error(`Original data file not found: ${filePath}`);
  }

  try {
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(fileContent);
  } catch (error) {
    throw new Error(`Failed to parse original data: ${error}`);
  }
}

/**
 * Create backup of original data
 */
async function createBackup(): Promise<void> {
  const originalPath = CONFIG.originalDataPath;
  const backupPath = originalPath.replace('.json', '.backup.json');

  fs.copyFileSync(originalPath, backupPath);
  console.log(`💾 Backup created: ${backupPath}`);
}

/**
 * Write output files
 */
async function writeOutputFiles(migratedData: any, summary: any): Promise<void> {
  // Write denormalized models
  fs.writeFileSync(
    CONFIG.outputPath,
    JSON.stringify({
      models: migratedData.models,
      productionStages: migratedData.productionStages,
      customers: migrateData.customers || [], // Keep original customers if they exist
      metadata: {
        version: '1.0.0',
        createdAt: new Date().toISOString(),
        description: 'Denormalized pump models optimized for UI consumption with flattened BOM and computed fields',
        lastUpdated: new Date().toISOString(),
        migration: migratedData.migrationMetadata
      }
    }, null, 2),
    'utf-8'
  );

  // Write migration summary
  fs.writeFileSync(
    CONFIG.summaryPath,
    JSON.stringify(summary, null, 2),
    'utf-8'
  );

  console.log(`✅ Denormalized models: ${CONFIG.outputPath}`);
  console.log(`✅ Migration summary: ${CONFIG.summaryPath}`);
}

/**
 * Display migration results
 */
function displayMigrationResults(migratedData: any, summary: any): void {
  console.log('\n📈 Migration Results:');
  console.log('─'.repeat(50));

  console.log(`Models migrated: ${summary.summary.totalModels}`);
  console.log(`Total build time range: ${getBuildTimeRange(migratedData.models)}`);
  console.log(`Price range: ${getPriceRange(migratedData.models)}`);
  console.log(`Pump types: ${Object.keys(summary.models.byType).join(', ')}`);
  console.log(`Pump sizes: ${Object.keys(summary.models.bySize).sort().join(', ')}`);
  console.log(`Enclosed models: ${summary.models.enclosed}`);

  console.log('\n🔧 Data Structure Improvements:');
  console.log('• Flattened BOM data for direct UI access');
  console.log('• Pre-computed pump categories and search terms');
  console.log('• Individual timing fields per production stage');
  console.log('• Added display categories for better UX');
  console.log('• Optimized for filtering and search operations');

  console.log('\n📊 Model Distribution:');
  Object.entries(summary.models.byType).forEach(([type, count]) => {
    console.log(`  ${type.replace('_', ' ')}: ${count}`);
  });

  console.log('\n💡 Next Steps:');
  console.log('1. Update TypeScript imports to use new data structure');
  console.log('2. Modify UI components to leverage flattened fields');
  console.log('3. Update data access patterns in store/services');
  console.log('4. Test all UI functionality with new data format');
  console.log('5. Remove old data transformation logic');
}

/**
 * Calculate build time range from models
 */
function getBuildTimeRange(models: Record<string, any>): string {
  const times = Object.values(models).map((model: any) => model.totalBuildDays);
  const min = Math.min(...times);
  const max = Math.max(...times);
  return `${min} - ${max} days`;
}

/**
 * Calculate price range from models
 */
function getPriceRange(models: Record<string, any>): string {
  const prices = Object.values(models)
    .map((model: any) => model.basePrice)
    .filter(price => price !== null) as number[];

  if (prices.length === 0) return 'No pricing data';

  const min = Math.min(...prices);
  const max = Math.max(...prices);
  return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
}

/**
 * Validate migration integrity
 */
function validateMigration(migratedData: any): boolean {
  try {
    // Basic structure validation
    if (!migratedData.models || typeof migratedData.models !== 'object') {
      throw new Error('Invalid models structure');
    }

    if (!migratedData.productionStages || !Array.isArray(migratedData.productionStages)) {
      throw new Error('Invalid production stages structure');
    }

    // Validate each model
    Object.values(migratedData.models).forEach((model: any) => {
      const requiredFields = ['id', 'model', 'description', 'pumpType', 'pumpSize'];
      for (const field of requiredFields) {
        if (!model[field]) {
          throw new Error(`Model ${model.id} missing required field: ${field}`);
        }
      }
    });

    return true;
  } catch (error) {
    console.error('❌ Migration validation failed:', error);
    return false;
  }
}

// Run migration if this file is executed directly
if (require.main === module) {
  migrateData()
    .then(() => {
      console.log('\n✨ All done!');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n💥 Fatal error:', error);
      process.exit(1);
    });
}

export { migrateData, validateMigration };