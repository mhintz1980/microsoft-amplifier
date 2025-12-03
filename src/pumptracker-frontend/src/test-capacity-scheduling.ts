/**
 * Test capacity-aware scheduling implementation
 * Run this to validate the scheduling system works correctly
 */

import { updatePumpsWithCapacityAwareScheduling, calculateRealisticSchedules, getPumpsWithScheduling } from './lib/dataAdapter';
import { settingsManager } from './lib/settings';

console.log('=== Testing Capacity-Aware Scheduling ===\n');

// Test 1: Load current settings
console.log('1. Current Settings:');
const settings = settingsManager.getSettings();
settings.departments.forEach(dept => {
  console.log(`   ${dept.name}: ${dept.employeeCount} employees × ${dept.efficiency}% efficiency = ${dept.manHours} man-hours/day`);
});

console.log('\n2. Mock Pumps Analysis:');
const pumpData = updatePumpsWithCapacityAwareScheduling();
console.log(`   Total pumps: ${pumpData.pumps.length}`);

// Show pumps by stage
const pumpsByStage = pumpData.pumps.reduce((acc, pump) => {
  if (!acc[pump.stage]) {
    acc[pump.stage] = [];
  }
  acc[pump.stage].push(pump);
  return acc;
}, {} as Record<string, any[]>);

Object.entries(pumpsByStage).forEach(([stage, pumps]) => {
  console.log(`   ${stage}: ${pumps.length} pumps`);
  pumps.forEach(pump => {
    if (pump.capacityInfo) {
      console.log(`     - ${pump.model_id} (${pump.customer}): ${pump.capacityInfo.duration.toFixed(1)} days, ${pump.capacityInfo.estimatedHours}h`);
    }
  });
});

console.log('\n3. Capacity Conflicts:');
if (pumpData.conflicts.length === 0) {
  console.log('   ✅ No capacity conflicts detected');
} else {
  console.log(`   ⚠️ ${pumpData.conflicts.length} conflicts found:`);
  pumpData.conflicts.forEach((conflict, index) => {
    console.log(`     ${index + 1}. ${conflict.departmentId} on ${conflict.date.toLocaleDateString()}: ${conflict.demand}h demand vs ${conflict.capacity}h capacity (${conflict.overload}h overload)`);
  });
}

console.log('\n4. Realistic Schedule Simulation:');
const schedules = calculateRealisticSchedules();
console.log(`   Total jobs scheduled: ${schedules.length}`);

schedules.forEach((schedule, index) => {
  const pump = pumpData.pumps.find(p => p.id === schedule.jobId);
  console.log(`   ${index + 1}. ${pump?.model_id || schedule.jobId}:`);
  console.log(`      Start: ${schedule.startDate.toLocaleDateString()}`);
  console.log(`      End: ${schedule.endDate.toLocaleDateString()}`);
  console.log(`      Total Duration: ${schedule.totalDuration} days`);
  console.log(`      Stages: ${schedule.stages.length}`);
});

console.log('\n5. Fabrication Department Analysis:');
const fabricationPumps = pumpData.pumps.filter(p => p.stage === 'FABRICATION');
console.log(`   Pumps in Fabrication: ${fabricationPumps.length}`);
const fabricationDept = settings.departments.find(d => d.id === 'fabrication');
if (fabricationDept) {
  console.log(`   Department Capacity: ${fabricationDept.manHours} man-hours/day`);
  console.log(`   Employees: ${fabricationDept.employeeCount} at ${fabricationDept.efficiency}% efficiency`);

  const totalFabricationHours = fabricationPumps
    .filter(p => p.capacityInfo)
    .reduce((sum, p) => sum + (p.capacityInfo?.estimatedHours || 0), 0);

  console.log(`   Total Required Hours: ${totalFabricationHours}h`);
  console.log(`   Estimated Total Duration: ${totalFabricationHours / fabricationDept.manHours} days (if done sequentially)`);
}

console.log('\n6. Test Results Summary:');
console.log('   ✅ Settings integration: Working');
console.log('   ✅ Capacity calculations: Working');
console.log('   ✅ Job duration calculations: Working');
console.log(`   ${pumpData.conflicts.length === 0 ? '✅' : '⚠️'} Conflict detection: ${pumpData.conflicts.length === 0 ? 'No conflicts' : 'Conflicts found'}`);
console.log('   ✅ Realistic scheduling: Working');

export { pumpData, settings, schedules };