export interface TestData {
  departments: {
    id: string;
    displayName: string;
    employeeCount: number;
    efficiency: number;
    dailyManHours: number;
  }[];
  vendors: {
    id: string;
    name: string;
    weeklyCapacity: number;
    currentLoad: number;
    isPreferred: boolean;
  }[];
  pumps: {
    id: string;
    name: string;
    stage: string;
    status: string;
    priority: number;
    estimatedCompletionDate: string;
    vendor?: string;
  }[];
}

export const defaultTestData: TestData = {
  departments: [
    {
      id: 'FABRICATION',
      displayName: 'Fabrication',
      employeeCount: 8,
      efficiency: 85,
      dailyManHours: 54.4
    },
    {
      id: 'POWDER_COAT',
      displayName: 'Powder Coat',
      employeeCount: 4,
      efficiency: 90,
      dailyManHours: 28.8
    },
    {
      id: 'ASSEMBLY',
      displayName: 'Assembly',
      employeeCount: 6,
      efficiency: 88,
      dailyManHours: 42.24
    },
    {
      id: 'TESTING',
      displayName: 'Testing',
      employeeCount: 2,
      efficiency: 95,
      dailyManHours: 15.2
    },
    {
      id: 'SHIPPING',
      displayName: 'Shipping',
      employeeCount: 2,
      efficiency: 92,
      dailyManHours: 14.72
    },
    {
      id: 'QA_COMPLETE',
      displayName: 'QA Complete',
      employeeCount: 1,
      efficiency: 98,
      dailyManHours: 7.84
    }
  ],
  vendors: [
    {
      id: 'vendor-1',
      name: 'Vendor A - Premium',
      weeklyCapacity: 7,
      currentLoad: 5,
      isPreferred: true
    },
    {
      id: 'vendor-2',
      name: 'Vendor B - Standard',
      weeklyCapacity: 7,
      currentLoad: 4,
      isPreferred: false
    },
    {
      id: 'vendor-3',
      name: 'Vendor C - Economy',
      weeklyCapacity: 7,
      currentLoad: 6,
      isPreferred: false
    }
  ],
  pumps: [
    {
      id: 'pump-001',
      name: 'Industrial Pump A',
      stage: 'FABRICATION',
      status: 'IN_PROGRESS',
      priority: 1,
      estimatedCompletionDate: '2024-12-15',
    },
    {
      id: 'pump-002',
      name: 'Commercial Pump B',
      stage: 'POWDER_COAT',
      status: 'IN_PROGRESS',
      priority: 2,
      estimatedCompletionDate: '2024-12-18',
      vendor: 'Vendor A - Premium'
    },
    {
      id: 'pump-003',
      name: 'Residential Pump C',
      stage: 'ASSEMBLY',
      status: 'IN_PROGRESS',
      priority: 3,
      estimatedCompletionDate: '2024-12-20',
    }
  ]
};

export class TestDataManager {
  private static instance: TestDataManager;
  private data: TestData;

  private constructor() {
    this.data = { ...defaultTestData };
  }

  static getInstance(): TestDataManager {
    if (!TestDataManager.instance) {
      TestDataManager.instance = new TestDataManager();
    }
    return TestDataManager.instance;
  }

  getData(): TestData {
    return { ...this.data };
  }

  updateDepartment(departmentId: string, updates: Partial<TestData['departments'][0]>): void {
    const deptIndex = this.data.departments.findIndex(d => d.id === departmentId);
    if (deptIndex !== -1) {
      this.data.departments[deptIndex] = {
        ...this.data.departments[deptIndex],
        ...updates
      };
      // Recalculate man-hours if efficiency or employee count changed
      if (updates.employeeCount !== undefined || updates.efficiency !== undefined) {
        const dept = this.data.departments[deptIndex];
        dept.dailyManHours = (dept.employeeCount * 8 * dept.efficiency) / 100;
      }
    }
  }

  addPump(pump: Omit<TestData['pumps'][0], 'id'>): string {
    const id = `pump-${Date.now()}`;
    this.data.pumps.push({ id, ...pump });
    return id;
  }

  movePump(pumpId: string, newStage: string, vendor?: string): void {
    const pump = this.data.pumps.find(p => p.id === pumpId);
    if (pump) {
      pump.stage = newStage;
      if (vendor) {
        pump.vendor = vendor;
      }
    }
  }

  updateVendorLoad(vendorId: string, newLoad: number): void {
    const vendor = this.data.vendors.find(v => v.id === vendorId);
    if (vendor) {
      vendor.currentLoad = newLoad;
    }
  }

  reset(): void {
    this.data = { ...defaultTestData };
  }
}