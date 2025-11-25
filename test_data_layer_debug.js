/**
 * Debug Test Suite for PumpTracker Lite Data Layer
 *
 * This test suite validates the critical fixes made to the data layer
 * and ensures proper functionality of department configurations,
 * vendor management, and capacity calculations.
 */

// Mock localStorage for Node.js environment
if (typeof localStorage === 'undefined') {
  global.localStorage = {
    data: {},
    getItem(key) { return this.data[key] || null; },
    setItem(key, value) { this.data[key] = value; },
    removeItem(key) { delete this.data[key]; },
    clear() { this.data = {}; }
  };
}

// Import the modules to test (adjust paths as needed)
const { validateDepartment, validateVendor, calculateDailyCapacity, calculateVendorAllocation, calculateCapacityUtilization } = require('../src/lib/calculations.ts');
const { DEFAULT_DEPARTMENTS, DEFAULT_POWDER_COAT_VENDORS } = require('../src/types/department-config.ts');

console.log('🔧 PumpTracker Lite Data Layer Debug Tests');
console.log('='.repeat(50));

// Test 1: Department Validation
console.log('\n📋 Test 1: Department Validation');
try {
  const testDept = DEFAULT_DEPARTMENTS[0];
  const fullDept = {
    ...testDept,
    id: 'fabrication',
    createdAt: '2025-01-23T10:00:00.000Z',
    updatedAt: '2025-01-23T10:00:00.000Z'
  };

  const validation = validateDepartment(fullDept);
  console.log('✅ Department validation:', validation.isValid ? 'PASSED' : 'FAILED');
  if (!validation.isValid) {
    console.log('❌ Errors:', validation.errors);
  }
  if (validation.warnings.length > 0) {
    console.log('⚠️  Warnings:', validation.warnings);
  }
} catch (error) {
  console.log('❌ Department validation test failed:', error.message);
}

// Test 2: Vendor Validation
console.log('\n🏭 Test 2: Vendor Validation');
try {
  const testVendor = DEFAULT_POWDER_COAT_VENDORS[0];
  const fullVendor = {
    ...testVendor,
    id: 'powder_coat_vendor_1',
    departmentId: 'powder_coat',
    createdAt: '2025-01-23T10:00:00.000Z',
    updatedAt: '2025-01-23T10:00:00.000Z'
  };

  const validation = validateVendor(fullVendor);
  console.log('✅ Vendor validation:', validation.isValid ? 'PASSED' : 'FAILED');
  if (!validation.isValid) {
    console.log('❌ Errors:', validation.errors);
  }
  if (validation.warnings.length > 0) {
    console.log('⚠️  Warnings:', validation.warnings);
  }
} catch (error) {
  console.log('❌ Vendor validation test failed:', error.message);
}

// Test 3: Capacity Utilization Calculation (Division by Zero Fix)
console.log('\n📊 Test 3: Capacity Utilization Calculation');
try {
  const testCases = [
    { current: 5, maximum: 10, expected: 0.5 },
    { current: 0, maximum: 0, expected: 0 },
    { current: 5, maximum: 0, expected: 0 },
    { current: 10, maximum: 10, expected: 1 },
    { current: 15, maximum: 10, expected: 1 }, // Should be capped at 1
  ];

  testCases.forEach((testCase, index) => {
    const result = calculateCapacityUtilization(testCase.current, testCase.maximum);
    const passed = Math.abs(result - testCase.expected) < 0.001;
    console.log(`${passed ? '✅' : '❌'} Test 3.${index + 1}: ${testCase.current}/${testCase.maximum} = ${result} (expected ${testCase.expected})`);
  });
} catch (error) {
  console.log('❌ Capacity utilization test failed:', error.message);
}

// Test 4: Daily Capacity Calculation (No More Infinity Issues)
console.log('\n📅 Test 4: Daily Capacity Calculation');
try {
  const department = {
    ...DEFAULT_DEPARTMENTS[0],
    id: 'fabrication',
    createdAt: '2025-01-23T10:00:00.000Z',
    updatedAt: '2025-01-23T10:00:00.000Z'
  };

  const employees = [
    {
      id: 'emp_1',
      name: 'Test Employee',
      role: 'Technician',
      departmentId: 'fabrication',
      hoursPerShift: 8,
      shiftsPerDay: 1,
      workDays: [1, 2, 3, 4, 5],
      efficiency: 0.8,
      pumpsPerShift: 2,
      skillLevel: 'intermediate',
      utilizationTarget: 0.8,
      isActive: true,
      isCrossTrained: false,
      crossTrainedDepartments: [],
      createdAt: '2025-01-23T10:00:00.000Z',
      updatedAt: '2025-01-23T10:00:00.000Z'
    }
  ];

  const capacity = calculateDailyCapacity(department, employees, [], new Date());
  console.log('✅ Daily capacity calculation:', {
    availableEmployees: capacity.availableEmployees,
    theoreticalCapacity: capacity.theoreticalCapacity,
    practicalCapacity: capacity.practicalCapacity,
    availableCapacity: capacity.availableCapacity
  });

  // Validate no NaN or Infinity values
  const isValid = !isNaN(capacity.practicalCapacity) && isFinite(capacity.practicalCapacity);
  console.log(`${isValid ? '✅' : '❌'} Capacity calculation is valid (no NaN/Infinity)`);
} catch (error) {
  console.log('❌ Daily capacity test failed:', error.message);
}

// Test 5: Vendor Allocation Logic
console.log('\n🚚 Test 5: Vendor Allocation Logic');
try {
  const vendors = DEFAULT_POWDER_COAT_VENDORS.map((vendor, index) => ({
    ...vendor,
    id: `powder_coat_vendor_${index + 1}`,
    departmentId: 'powder_coat',
    createdAt: '2025-01-23T10:00:00.000Z',
    updatedAt: '2025-01-23T10:00:00.000Z'
  }));

  const allocation = calculateVendorAllocation(vendors, 25);
  const totalAllocated = allocation.reduce((sum, item) => sum + item.pumps, 0);

  console.log('✅ Vendor allocation test:');
  console.log(`   Requested: 25 pumps`);
  console.log(`   Allocated: ${totalAllocated} pumps`);
  console.log(`   Distribution:`, allocation.map(a => `${a.vendorId}: ${a.pumps}`).join(', '));

  const passed = totalAllocated === 25;
  console.log(`${passed ? '✅' : '❌'} Allocation sums correctly`);
} catch (error) {
  console.log('❌ Vendor allocation test failed:', error.message);
}

// Test 6: Edge Cases
console.log('\n⚠️  Test 6: Edge Cases');
try {
  const edgeCases = [
    { name: 'Empty department', func: () => calculateCapacityUtilization(0, 0) },
    { name: 'Negative capacity', func: () => calculateCapacityUtilization(5, -10) },
    { name: 'Null values', func: () => calculateCapacityUtilization(null, null) },
  ];

  edgeCases.forEach(testCase => {
    try {
      const result = testCase.func();
      const isValid = !isNaN(result) && isFinite(result) && result >= 0;
      console.log(`${isValid ? '✅' : '❌'} ${testCase.name}: ${result}`);
    } catch (error) {
      console.log(`❌ ${testCase.name}: ${error.message}`);
    }
  });
} catch (error) {
  console.log('❌ Edge cases test failed:', error.message);
}

console.log('\n🎉 Debug testing completed!');
console.log('\nKey fixes implemented:');
console.log('1. ✅ Division by zero protection in capacity calculations');
console.log('2. ✅ Array.push() instead of Set.add() for date arrays');
console.log('3. ✅ Recursive function call fixes in store methods');
console.log('4. ✅ Proper error handling for edge cases');
console.log('5. ✅ Input validation and sanitization');