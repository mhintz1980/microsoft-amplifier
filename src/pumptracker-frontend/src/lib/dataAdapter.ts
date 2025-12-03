// Import from the existing data layer
import { scheduleJob, calculateJobDuration, type JobStage, scheduler } from './scheduling'

// Mock some data for now since we can't directly import from the parent directory
// In a real implementation, this would connect to the actual data layer

export interface Department {
  id: string;
  name: string;
  isActive: boolean;
  sortOrder: number;
}

export const mockDepartments: Department[] = [
  { id: 'FABRICATION', name: 'Fabrication', isActive: true, sortOrder: 1 },
  { id: 'POWDER_COAT', name: 'Powder Coat', isActive: true, sortOrder: 2 },
  { id: 'ASSEMBLY', name: 'Assembly', isActive: true, sortOrder: 3 },
  { id: 'TESTING', name: 'Testing', isActive: true, sortOrder: 4 },
  { id: 'SHIPPING', name: 'Shipping', isActive: true, sortOrder: 5 }
];

export const mockPumps = [
  {
    id: 'pump-001',
    po_id: 'PO-2025-001',
    customer: 'Water Corporation',
    model_id: 'SAFE-RL-1000',
    stage: 'FABRICATION',
    priority: 'HIGH',
    value: 45000,
    buildTime: 15,
    last_update: new Date().toISOString(),
    powder_color: 'Safety Red',
    estimatedCompletionDate: null,
    actualDuration: null
  },
  {
    id: 'pump-002',
    po_id: 'PO-2025-002',
    customer: 'Mining Co Ltd',
    model_id: 'SAFE-HC-500',
    stage: 'POWDER_COAT',
    priority: 'MEDIUM',
    value: 32000,
    buildTime: 12,
    last_update: new Date().toISOString(),
    powder_color: 'Industrial Yellow',
    estimatedCompletionDate: null,
    actualDuration: null
  },
  {
    id: 'pump-003',
    po_id: 'PO-2025-003',
    customer: 'Civic Municipal',
    model_id: 'STANDARD-RL-800',
    stage: 'ASSEMBLY',
    priority: 'LOW',
    value: 28000,
    buildTime: 10,
    last_update: new Date().toISOString(),
    powder_color: 'Municipal Blue',
    estimatedCompletionDate: null,
    actualDuration: null
  },
  {
    id: 'pump-004',
    po_id: 'PO-2025-004',
    customer: 'Industrial Plant',
    model_id: 'SAFE-RL-1200',
    stage: 'FABRICATION',
    priority: 'HIGH',
    value: 52000,
    buildTime: 18,
    last_update: new Date().toISOString(),
    powder_color: 'Industrial Gray',
    estimatedCompletionDate: null,
    actualDuration: null
  }
];

export const mockPurchaseOrders = [
  {
    id: 'PO-2025-001',
    customer: 'Water Corporation',
    dateReceived: '2025-01-15',
    promiseDate: '2025-02-28'
  },
  {
    id: 'PO-2025-002',
    customer: 'Mining Co Ltd',
    dateReceived: '2025-01-18',
    promiseDate: '2025-03-10'
  }
];

export function getDepartmentName(departmentId: string): string {
  const dept = mockDepartments.find(d => d.id === departmentId);
  return dept?.name || departmentId;
}

export function getPumpsByStage() {
  const pumpsByStage = mockPumps.reduce((acc, pump) => {
    if (!acc[pump.stage]) {
      acc[pump.stage] = [];
    }
    acc[pump.stage].push(pump);
    return acc;
  }, {} as Record<string, typeof mockPumps>);

  return pumpsByStage;
}

export function getCustomerValueData() {
  const customerValue = mockPumps.reduce((acc, pump) => {
    if (!acc[pump.customer]) {
      acc[pump.customer] = 0;
    }
    acc[pump.customer] += pump.value;
    return acc;
  }, {} as Record<string, number>);

  return Object.entries(customerValue).map(([name, value]) => ({
    name,
    value,
    color: '#10b981' // Default green, could be made dynamic
  }));
}

export function getStageDistribution() {
  const stageCounts = mockPumps.reduce((acc, pump) => {
    if (!acc[pump.stage]) {
      acc[pump.stage] = 0;
    }
    acc[pump.stage] += 1;
    return acc;
  }, {} as Record<string, number>);

  const colors = {
    'FABRICATION': '#8b5cf6',
    'POWDER_COAT': '#f59e0b',
    'ASSEMBLY': '#06b6d4',
    'TESTING': '#3b82f6',
    'SHIPPING': '#10b981'
  };

  return Object.entries(stageCounts).map(([name, value]) => ({
    name: getDepartmentName(name),
    value,
    color: colors[name as keyof typeof colors] || '#6b7280'
  }));
}

export function getLateOrdersData() {
  // Mock late orders data
  return [
    { name: 'On Time', value: 89, color: '#10b981' },
    { name: 'Late', value: 23, color: '#ef4444' }
  ];
}

export function getPriorityDistribution() {
  const priorityCounts = mockPumps.reduce((acc, pump) => {
    if (!acc[pump.priority]) {
      acc[pump.priority] = 0;
    }
    acc[pump.priority] += 1;
    return acc;
  }, {} as Record<string, number>);

  const colors = {
    'HIGH': '#ef4444',
    'MEDIUM': '#f59e0b',
    'LOW': '#10b981'
  };

  return Object.entries(priorityCounts).map(([name, value]) => ({
    name,
    value,
    color: colors[name as keyof typeof colors] || '#6b7280'
  }));
}

// Capacity-aware scheduling functions

/**
 * Define the standard stages and their estimated hours for pump jobs
 */
export const PUMP_JOB_STAGES: JobStage[] = [
  { departmentId: 'fabrication', estimatedHours: 40, priority: 'HIGH' },
  { departmentId: 'powder_coat', estimatedHours: 8, priority: 'MEDIUM' },
  { departmentId: 'assembly', estimatedHours: 24, priority: 'HIGH' },
  { departmentId: 'testing', estimatedHours: 16, priority: 'HIGH' },
  { departmentId: 'shipping', estimatedHours: 4, priority: 'LOW' }
];

/**
 * Calculate realistic completion dates for all pumps
 */
export function calculateRealisticSchedules() {
  const jobs = mockPumps.map(pump => ({
    jobId: pump.id,
    stages: PUMP_JOB_STAGES.map(stage => ({
      ...stage,
      priority: pump.priority as 'HIGH' | 'MEDIUM' | 'LOW'
    }))
  }));

  return scheduler.simulateMultipleJobs(jobs);
}

/**
 * Get current capacity status for all departments
 */
export function getCapacityStatus() {
  return scheduler.getCapacityStatus();
}

/**
 * Calculate estimated completion date for a single pump
 */
export function calculatePumpCompletionDate(pumpId: string) {
  const pump = mockPumps.find(p => p.id === pumpId);
  if (!pump) return null;

  const stages = PUMP_JOB_STAGES.map(stage => ({
    ...stage,
    priority: pump.priority as 'HIGH' | 'MEDIUM' | 'LOW'
  }));

  // Calculate duration for current stage only
  const currentStage = stages.find(s =>
    s.departmentId.toLowerCase() === pump.stage.toLowerCase()
  );

  if (!currentStage) return null;

  // Find competing jobs in same stage
  const competingJobs = mockPumps
    .filter(p => p.id !== pumpId && p.stage === pump.stage)
    .map(p => {
      const pumpStages = PUMP_JOB_STAGES.map(stage => ({
        ...stage,
        priority: p.priority as 'HIGH' | 'MEDIUM' | 'LOW'
      }));
      return pumpStages.find(s =>
        s.departmentId.toLowerCase() === p.stage.toLowerCase()
      );
    })
    .filter(Boolean) as JobStage[];

  const duration = calculateJobDuration(currentStage, competingJobs);
  const completionDate = new Date();
  completionDate.setDate(completionDate.getDate() + Math.ceil(duration));

  return {
    completionDate,
    duration,
    department: getDepartmentName(pump.stage),
    estimatedHours: currentStage.estimatedHours
  };
}

/**
 * Get pumps with realistic completion dates
 */
export function getPumpsWithScheduling() {
  return mockPumps.map(pump => {
    const scheduling = calculatePumpCompletionDate(pump.id);
    return {
      ...pump,
      estimatedCompletionDate: scheduling?.completionDate || null,
      estimatedDuration: scheduling?.duration || null,
      currentDepartment: getDepartmentName(pump.stage),
      capacityInfo: scheduling || null
    };
  });
}

/**
 * Detect capacity conflicts in current schedule
 */
export function getSchedulingConflicts() {
  const schedules = calculateRealisticSchedules();
  return scheduler.detectConflicts(schedules);
}

/**
 * Update pump data with capacity-aware scheduling
 */
export function updatePumpsWithCapacityAwareScheduling() {
  const pumpsWithScheduling = getPumpsWithScheduling();
  const conflicts = getSchedulingConflicts();

  return {
    pumps: pumpsWithScheduling,
    conflicts,
    capacityStatus: getCapacityStatus(),
    schedules: calculateRealisticSchedules()
  };
}