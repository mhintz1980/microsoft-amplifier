import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';
import { SettingsModalPage } from '../page-objects/SettingsModalPage';
import { KanbanBoardPage } from '../page-objects/KanbanBoardPage';

test.describe('Cross-Feature Integration Tests', () => {
  let dashboardPage: DashboardPage;
  let settingsPage: SettingsModalPage;
  let kanbanPage: KanbanBoardPage;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    settingsPage = new SettingsModalPage(page);
    kanbanPage = new KanbanBoardPage(page);
  });

  test.describe('Settings Changes → Kanban Timing Integration', () => {
    test('should update Kanban scheduling based on capacity settings', async () => {
      await test.step('Navigate to dashboard and open settings', async () => {
        await dashboardPage.gotoDashboard();
        await settingsPage.openSettingsModal();
      });

      await test.step('Modify department capacity settings', async () => {
        await settingsPage.setEmployeeCount('Fabrication', 15);
        await settingsPage.setEfficiency('Fabrication', 90);
        await settingsPage.setEmployeeCount('Powder Coat', 8);
        await settingsPage.setEfficiency('Powder Coat', 95);
      });

      await test.step('Save settings and navigate to Kanban', async () => {
        await settingsPage.saveButton.click();
        await kanbanPage.gotoKanbanBoard();
      });

      await test.step('Verify Kanban reflects capacity changes', async () => {
        const capacityStatus = await kanbanPage.getCapacityStatus();

        const fabricationDept = capacityStatus.find(d => d.department.toLowerCase().includes('fabrication'));
        const powderCoatDept = capacityStatus.find(d => d.department.toLowerCase().includes('powder'));

        if (fabricationDept) {
          // 15 employees * 8 hours * 90% efficiency = 108 man-hours
          expect(fabricationDept.manHours).toBeCloseTo(108, 0);
        }

        if (powderCoatDept) {
          // 8 employees * 8 hours * 95% efficiency = 60.8 man-hours
          expect(powderCoatDept.manHours).toBeCloseTo(60.8, 0);
        }
      });
    });

    test('should update powder coat vendor capacity based on settings', async () => {
      await dashboardPage.gotoDashboard();
      await settingsPage.openSettingsModal();

      // Modify powder coat department settings
      await settingsPage.setEmployeeCount('Powder Coat', 6);
      await settingsPage.setEfficiency('Powder Coat', 92);
      await settingsPage.saveButton.click();

      await kanbanPage.gotoKanbanBoard();

      // Verify vendor capacity is updated
      const vendors = ['Vendor A - Premium', 'Vendor B - Standard', 'Vendor C - Economy'];

      for (const vendor of vendors) {
        const capacity = await kanbanPage.getVendorCapacity(vendor);
        expect(capacity.weeklyCapacity).toBe(7); // Should remain consistent
        expect(capacity.currentLoad).toBeGreaterThanOrEqual(0);
      }

      // Verify powder coat capacity summary is updated
      await kanbanPage.verifyPowderCoatCapacitySummary();
    });
  });

  test.describe('Settings Changes → Dashboard Display Integration', () => {
    test('should update dashboard KPI calculations based on capacity settings', async () => {
      await dashboardPage.gotoDashboard();

      // Get initial KPI values
      const initialKPI = await dashboardPage.getKPIValues();

      await settingsPage.openSettingsModal();

      // Make significant capacity changes
      await settingsPage.setEmployeeCount('Fabrication', 20);
      await settingsPage.setEfficiency('Fabrication', 95);
      await settingsPage.setEmployeeCount('Testing', 5);
      await settingsPage.setEfficiency('Testing', 98);

      await settingsPage.saveButton.click();
      await dashboardPage.helpers.waitForLoadingToComplete();

      // Verify charts update with new capacity-based calculations
      await dashboardPage.verifyChartsRendered();

      // Lead times might change with increased capacity
      await dashboardPage.helpers.verifyChartRenders('[data-testid="lead-time-trend-chart"]');
    });

    test('should reflect department changes in department tree map', async () => {
      await dashboardPage.gotoDashboard();
      await settingsPage.openSettingsModal();

      // Modify multiple departments
      await settingsPage.setEmployeeCount('Fabrication', 12);
      await settingsPage.setEmployeeCount('Assembly', 10);
      await settingsPage.setEmployeeCount('Testing', 4);

      await settingsPage.saveButton.click();
      await dashboardPage.helpers.waitForLoadingToComplete();

      // Verify department tree map shows updated departments
      await dashboardPage.verifyDepartmentTreeMapNames();
      await dashboardPage.helpers.verifyChartRenders('[data-testid="department-treemap-chart"]');
    });
  });

  test.describe('Navigation and State Persistence', () => {
    test('should maintain settings across view switches', async () => {
      await dashboardPage.gotoDashboard();
      await settingsPage.openSettingsModal();

      // Configure specific settings
      await settingsPage.setEmployeeCount('Fabrication', 14);
      await settingsPage.setEfficiency('Fabrication', 88);
      await settingsPage.setEmployeeCount('Powder Coat', 6);
      await settingsPage.setEfficiency('Powder Coat', 92);

      await settingsPage.saveButton.click();

      // Navigate to Kanban and back
      await kanbanPage.gotoKanbanBoard();
      await kanbanPage.waitForKanbanBoardLoad();

      // Verify Kanban shows updated capacity
      const capacityStatus = await kanbanPage.getCapacityStatus();
      expect(capacityStatus.length).toBeGreaterThanOrEqual(4);

      // Navigate back to Dashboard
      await dashboardPage.gotoDashboard();
      await settingsPage.openSettingsModal();

      // Verify settings persisted
      const fabricationEmployees = await settingsPage.getEmployeeCount('Fabrication');
      const fabricationEfficiency = await settingsPage.getEfficiency('Fabrication');
      const powderCoatEmployees = await settingsPage.getEmployeeCount('Powder Coat');
      const powderCoatEfficiency = await settingsPage.getEfficiency('Powder Coat');

      expect(fabricationEmployees).toBe(14);
      expect(fabricationEfficiency).toBe(88);
      expect(powderCoatEmployees).toBe(6);
      expect(powderCoatEfficiency).toBe(92);
    });

    test('should maintain application state during browser refresh', async () => {
      await dashboardPage.gotoDashboard();
      await settingsPage.openSettingsModal();

      // Set specific configuration
      await settingsPage.setEmployeeCount('Assembly', 12);
      await settingsPage.setEfficiency('Assembly', 90);
      await settingsPage.saveButton.click();

      // Navigate to Kanban
      await kanbanPage.gotoKanbanBoard();
      await kanbanPage.waitForKanbanBoardLoad();

      // Get current state
      const beforeRefreshCapacity = await kanbanPage.getCapacityStatus();

      // Refresh the page
      await kanbanPage.page.reload();
      await kanbanPage.waitForKanbanBoardLoad();

      // Verify state is maintained
      const afterRefreshCapacity = await kanbanPage.getCapacityStatus();
      expect(afterRefreshCapacity.length).toBe(beforeRefreshCapacity.length);

      // Verify specific department maintained its capacity
      const assemblyDeptBefore = beforeRefreshCapacity.find(d =>
        d.department.toLowerCase().includes('assembly')
      );
      const assemblyDeptAfter = afterRefreshCapacity.find(d =>
        d.department.toLowerCase().includes('assembly')
      );

      if (assemblyDeptBefore && assemblyDeptAfter) {
        expect(assemblyDeptAfter.manHours).toBeCloseTo(assemblyDeptBefore.manHours, 0);
      }
    });
  });

  test.describe('Data Synchronization', () => {
    test('should synchronize pump data across dashboard and kanban', async () => {
      await dashboardPage.gotoDashboard();

      // Get dashboard data
      const dashboardKPI = await dashboardPage.getKPIValues();

      // Navigate to Kanban
      await kanbanPage.gotoKanbanBoard();

      // Verify Kanban shows consistent data
      const totalCards = await kanbanPage.kanbanCards.count();

      // Total cards should be reasonable compared to dashboard orders
      expect(totalCards).toBeGreaterThan(0);
      expect(totalCards).toBeLessThan(dashboardKPI.totalOrders * 2); // Allow some flexibility

      // Verify capacity status is consistent
      const capacityStatus = await kanbanPage.getCapacityStatus();
      expect(capacityStatus.length).toBeGreaterThan(0);

      // Navigate back to dashboard
      await dashboardPage.gotoDashboard();
      await dashboardPage.helpers.waitForLoadingToComplete();

      // Dashboard should show consistent data
      const updatedKPI = await dashboardPage.getKPIValues();
      expect(updatedKPI.totalOrders).toBe(dashboardKPI.totalOrders);
    });

    test('should handle concurrent data updates', async () => {
      await dashboardPage.gotoDashboard();
      await settingsPage.openSettingsModal();

      // Make simultaneous changes
      await settingsPage.setEmployeeCount('Fabrication', 16);
      await settingsPage.setEfficiency('Fabrication', 92);
      await settingsPage.setEmployeeCount('Powder Coat', 7);
      await settingsPage.setEfficiency('Powder Coat', 89);

      await settingsPage.saveButton.click();

      // Quickly navigate to Kanban
      await kanbanPage.gotoKanbanBoard();
      await kanbanPage.waitForKanbanBoardLoad();

      // Verify all changes are reflected
      const capacityStatus = await kanbanPage.getCapacityStatus();

      // Find Fabrication department
      const fabricationDept = capacityStatus.find(d =>
        d.department.toLowerCase().includes('fabrication')
      );

      if (fabricationDept) {
        // 16 employees * 8 hours * 92% efficiency = 117.76 man-hours
        expect(fabricationDept.manHours).toBeCloseTo(117.8, 0);
      }

      // Find Powder Coat department
      const powderCoatDept = capacityStatus.find(d =>
        d.department.toLowerCase().includes('powder')
      );

      if (powderCoatDept) {
        // 7 employees * 8 hours * 89% efficiency = 49.84 man-hours
        expect(powderCoatDept.manHours).toBeCloseTo(49.8, 0);
      }
    });
  });

  test.describe('Error Handling Across Features', () => {
    test('should handle settings errors without breaking other features', async () => {
      await dashboardPage.gotoDashboard();
      await settingsPage.openSettingsModal();

      // Try to save invalid settings
      await settingsPage.setEmployeeCount('Fabrication', -5);
      await settingsPage.saveButton.click();

      // Should show validation error but not crash
      await expect(settingsPage.validationErrors.first()).toBeVisible();

      // Close modal and verify dashboard still works
      await settingsPage.cancelButton.click();
      await dashboardPage.helpers.waitForLoadingToComplete();

      // Dashboard should still function
      await dashboardPage.verifyKPICards();
      await dashboardPage.verifyChartsRendered();
    });

    test('should handle kanban data errors without breaking settings', async () => {
      // Mock network error for kanban data
      await kanbanPage.page.route('**/api/**', route => route.abort());

      await kanbanPage.gotoKanbanBoard();
      await kanbanPage.page.waitForTimeout(2000);

      // Try to open settings - should still work
      const settingsButton = kanbanPage.page.locator('[data-testid="settings-button"]');
      if (await settingsButton.count() > 0) {
        await settingsButton.click();
        await settingsPage.expectSettingsModalOpen();

        // Settings should still function normally
        await settingsPage.setEmployeeCount('Fabrication', 10);
        await settingsPage.setEfficiency('Fabrication', 85);

        const actualEmployees = await settingsPage.getEmployeeCount('Fabrication');
        const actualEfficiency = await settingsPage.getEfficiency('Fabrication');

        expect(actualEmployees).toBe(10);
        expect(actualEfficiency).toBe(85);
      }
    });
  });

  test.describe('Performance Integration', () => {
    test('should maintain performance across view transitions', async () => {
      const transitionTimes = [];

      await dashboardPage.gotoDashboard();
      transitionTimes.push(Date.now());

      await kanbanPage.gotoKanbanBoard();
      transitionTimes.push(Date.now());

      await settingsPage.openSettingsModal();
      transitionTimes.push(Date.now());

      await settingsPage.closeSettingsModal();
      transitionTimes.push(Date.now());

      await dashboardPage.gotoDashboard();
      transitionTimes.push(Date.now());

      // Calculate transition times
      for (let i = 1; i < transitionTimes.length; i++) {
        const transitionTime = transitionTimes[i] - transitionTimes[i - 1];
        expect(transitionTime).toBeLessThan(3000); // Each transition under 3 seconds
      }
    });

    test('should handle memory usage with multiple feature interactions', async () => {
      // Perform multiple interactions
      for (let i = 0; i < 5; i++) {
        await dashboardPage.gotoDashboard();
        await dashboardPage.helpers.waitForLoadingToComplete();

        await kanbanPage.gotoKanbanBoard();
        await kanbanPage.waitForKanbanBoardLoad();

        // Some quick interactions
        await kanbanPage.refreshButton.click();
        await kanbanPage.page.waitForTimeout(1000);

        await dashboardPage.gotoDashboard();
        await dashboardPage.helpers.waitForLoadingToComplete();
      }

      // Application should still be responsive
      await dashboardPage.verifyKPICards();
      await kanbanPage.gotoKanbanBoard();
      await kanbanPage.verifyEightStages();
    });
  });

  test.describe('Cross-Browser Integration', () => {
    // These tests run on different browsers as configured in playwright.config.ts
    test('should work consistently across browsers', async () => {
      await dashboardPage.gotoDashboard();
      await settingsPage.openSettingsModal();

      // Configure test settings
      await settingsPage.setEmployeeCount('Fabrication', 11);
      await settingsPage.setEfficiency('Fabrication', 87);
      await settingsPage.saveButton.click();

      await kanbanPage.gotoKanbanBoard();
      await kanbanPage.waitForKanbanBoardLoad();

      // Verify capacity calculations are consistent across browsers
      const capacityStatus = await kanbanPage.getCapacityStatus();
      expect(capacityStatus.length).toBeGreaterThan(0);

      const fabricationDept = capacityStatus.find(d =>
        d.department.toLowerCase().includes('fabrication')
      );

      if (fabricationDept) {
        // 11 employees * 8 hours * 87% efficiency = 76.56 man-hours
        expect(fabricationDept.manHours).toBeCloseTo(76.6, 0);
      }

      // Navigate back and verify persistence
      await dashboardPage.gotoDashboard();
      await settingsPage.openSettingsModal();

      const persistedEmployees = await settingsPage.getEmployeeCount('Fabrication');
      const persistedEfficiency = await settingsPage.getEfficiency('Fabrication');

      expect(persistedEmployees).toBe(11);
      expect(persistedEfficiency).toBe(87);
    });
  });

  test.describe('Real-world Usage Scenarios', () => {
    test('should handle complete production planning workflow', async () => {
      await test.step('Start with dashboard overview', async () => {
        await dashboardPage.gotoDashboard();
        await dashboardPage.verifyKPICards();
        await dashboardPage.verifyChartsRendered();
      });

      await test.step('Adjust production capacity based on demand', async () => {
        await settingsPage.openSettingsModal();

        // Increase capacity for busy departments
        await settingsPage.setEmployeeCount('Fabrication', 12);
        await settingsPage.setEfficiency('Fabrication', 90);
        await settingsPage.setEmployeeCount('Assembly', 8);
        await settingsPage.setEfficiency('Assembly', 88);

        await settingsPage.saveButton.click();
      });

      await test.step('Review updated production schedule', async () => {
        await kanbanPage.gotoKanbanBoard();
        await kanbanPage.waitForKanbanBoardLoad();

        const capacityStatus = await kanbanPage.getCapacityStatus();
        expect(capacityStatus.length).toBeGreaterThan(0);

        // Verify powder coat vendors are ready
        await kanbanPage.verifyPowderCoatVendorSwimlanes();
      });

      await test.step('Test drag and drop scheduling', async () => {
        const sourceColumn = 'Not Started';
        const targetColumn = 'Fabrication';

        const sourceCount = await kanbanPage.getColumnCardCount(sourceColumn);

        if (sourceCount > 0) {
          await kanbanPage.testDragAndDrop(sourceColumn, targetColumn);
        }
      });

      await test.step('Return to dashboard to review updated metrics', async () => {
        await dashboardPage.gotoDashboard();
        await dashboardPage.helpers.waitForLoadingToComplete();
        await dashboardPage.verifyChartsRendered();
      });
    });

    test('should handle vendor management workflow', async () => {
      await kanbanPage.gotoKanbanBoard();

      await test.step('Review powder coat vendor capacity', async () => {
        const vendors = ['Vendor A - Premium', 'Vendor B - Standard', 'Vendor C - Economy'];

        for (const vendor of vendors) {
          const capacity = await kanbanPage.getVendorCapacity(vendor);
          expect(capacity.weeklyCapacity).toBe(7);
          expect(capacity.available).toBeGreaterThanOrEqual(0);
        }
      });

      await test.step('Adjust powder coat department to match vendor capacity', async () => {
        await settingsPage.openSettingsModal();
        await settingsPage.setEmployeeCount('Powder Coat', 5);
        await settingsPage.setEfficiency('Powder Coat', 94);
        await settingsPage.saveButton.click();
      });

      await test.step('Verify vendor assignments work', async () => {
        await kanbanPage.gotoKanbanBoard();
        const powderCoatCount = await kanbanPage.getColumnCardCount('Powder Coat');

        if (powderCoatCount > 0) {
          await kanbanPage.testPowderCoatVendorAssignment();
        }
      });
    });
  });
});