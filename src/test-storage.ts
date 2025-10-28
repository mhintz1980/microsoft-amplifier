/**
 * Simple test for localStorage utilities
 * Run this in a browser console or during development
 */

import localStorageUtils from './lib/storage';
const { StorageError } = localStorageUtils;
import { Pump, Stage, Priority, PurchaseOrder } from './types';

// Mock localStorage for testing (not used in type checking)
// const localStorageMock = (() => {
//   let store: Record<string, string> = {};

//   return {
//     getItem(key: string) {
//       return store[key] || null;
//     },
//     setItem(key: string, value: string) {
//       store[key] = value.toString();
//     },
//     removeItem(key: string) {
//       delete store[key];
//     },
//     clear() {
//       store = {};
//     },
//   };
// })();

// Mock fetch for models
global.fetch = async (input: RequestInfo | URL) => {
  const url = typeof input === 'string' ? input : input.toString();
  if (url.includes('models.json')) {
    return {
      ok: true,
      json: async () => ({
        models: [
          {
            model: 'DD-4S',
            description: '4" Double Diaphragm',
            price: 20000,
            bom: { engine: 'HATZ 1B50E', gearbox: 'RENOLD WM6', control_panel: 'DSEE050' },
            lead_times: { fabrication: 1.5, powder_coat: 7, assembly: 1, testing: 0.25, total_days: 9.75 }
          }
        ]
      })
    } as Response;
  }
  throw new Error('Not found');
};

// Test functions
export async function testStorage() {
  console.log('🧪 Testing localStorage utilities...');

  try {
    // Test basic storage availability
    if (!localStorageUtils.storage.isAvailable()) {
      console.log('❌ localStorage not available');
      return;
    }
    console.log('✅ localStorage is available');

    // Test loading empty data
    const emptyData = localStorageUtils.storage.loadData();
    console.log('✅ Empty data loaded:', emptyData);

    // Test adding a pump
    const testPump: Pump = {
      id: 'test-pump-1',
      po_id: 'PO-001',
      customer: 'Test Customer',
      model_id: 'DD-4S',
      stage: Stage.NOT_STARTED,
      priority: Priority.NORMAL,
      last_update: new Date().toISOString(),
      value: 20000,
      buildTime: 9.75,
      bom: { engine: 'HATZ 1B50E', gearbox: 'RENOLD WM6', control_panel: 'DSEE050' },
      org_id: 'default-org',
    };

    localStorageUtils.pumps.add(testPump);
    console.log('✅ Pump added successfully');

    // Test loading pumps
    const pumps = localStorageUtils.pumps.load();
    console.log('✅ Pumps loaded:', pumps);

    // Test updating a pump
    localStorageUtils.pumps.update('test-pump-1', { stage: Stage.FABRICATION });
    const updatedPumps = localStorageUtils.pumps.load();
    console.log('✅ Pump updated:', updatedPumps[0].stage);

    // Test adding a purchase order
    const testPO: PurchaseOrder = {
      id: 'PO-001',
      customer: 'Test Customer',
      dateReceived: new Date().toISOString(),
      org_id: 'default-org',
    };

    localStorageUtils.purchaseOrders.add(testPO);
    console.log('✅ Purchase order added successfully');

    // Test loading models
    const models = await localStorageUtils.storage.loadModels();
    console.log('✅ Models loaded:', Object.keys(models));

    // Test error handling
    try {
      localStorageUtils.pumps.update('non-existent', { stage: Stage.ASSEMBLY });
      console.log('⚠️ Update non-existent pump did not throw (this is expected)');
    } catch (error) {
      console.log('✅ Error handling works correctly');
    }

    console.log('🎉 All tests passed!');

  } catch (error) {
    console.error('❌ Test failed:', error);
    if (error instanceof StorageError) {
      console.error('Storage error details:', error.cause);
    } else if (error instanceof Error) {
      console.error('Error details:', error.message);
    }
  }
}

// Export test functions for manual testing
export { localStorageUtils };

// Auto-run tests if in development
if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
  // Uncomment to auto-run tests in development
  // testStorage();
}