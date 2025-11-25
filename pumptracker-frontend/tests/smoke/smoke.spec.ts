import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';
import { SettingsModalPage } from '../page-objects/SettingsModalPage';
import { KanbanBoardPage } from '../page-objects/KanbanBoardPage';

/**
 * Smoke Tests @smoke
 *
 * These tests verify the core functionality of the PumpTracker Lite application.
 * They should run quickly and provide confidence that the main features are working.
 */
test.describe('Smoke Tests @smoke', () => {
  test('should load dashboard and display core components', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await test.step('Dashboard loads successfully', async () => {
      await dashboardPage.gotoDashboard();
      await expect(dashboardPage.page).toHaveURL(/.*\/$/);
    });

    await test.step('KPI cards are visible', async () => {
      await expect(dashboardPage.kpiCards).toBeVisible();
    });

    await test.step('Charts are rendered', async () => {
      await dashboardPage.helpers.verifyChartRenders('[data-testid="late-orders-chart"]');
    });

    await test.step('Navigation works', async () => {
      await dashboardPage.helpers.navigateToView('kanban');
    });
  });

  test('should load kanban board and display core functionality', async ({ page }) => {
    const kanbanPage = new KanbanBoardPage(page);

    await test.step('Kanban board loads', async () => {
      await kanbanPage.gotoKanbanBoard();
      await kanbanPage.waitForKanbanBoardLoad();
    });

    await test.step('All 8 stages are displayed', async () => {
      await kanbanPage.verifyEightStages();
    });

    await test.step('Capacity status is shown', async () => {
      await kanbanPage.verifyCapacityAwareScheduling();
    });

    await test.step('Powder coat vendors are displayed', async () => {
      await kanbanPage.verifyPowderCoatVendorSwimlanes();
    });
  });

  test('should open and close settings modal', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    const settingsPage = new SettingsModalPage(page);

    await test.step('Navigate to dashboard', async () => {
      await dashboardPage.gotoDashboard();
    });

    await test.step('Open settings modal', async () => {
      await settingsPage.openSettingsModal();
      await settingsPage.expectSettingsModalOpen();
    });

    await test.step('Verify department cards are visible', async () => {
      await expect(settingsPage.departmentCards).toHaveCount({ min: 4 });
    });

    await test.step('Close settings modal', async () => {
      await settingsPage.closeSettingsModal();
      await settingsPage.expectSettingsModalClosed();
    });
  });

  test('should allow basic department settings modification', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    const settingsPage = new SettingsModalPage(page);

    await dashboardPage.gotoDashboard();
    await settingsPage.openSettingsModal();

    await test.step('Modify Fabrication department', async () => {
      await settingsPage.setEmployeeCount('Fabrication', 10);
      await settingsPage.setEfficiency('Fabrication', 90);

      const employees = await settingsPage.getEmployeeCount('Fabrication');
      const efficiency = await settingsPage.getEfficiency('Fabrication');

      expect(employees).toBe(10);
      expect(efficiency).toBe(90);
    });

    await test.step('Verify man-hours calculation', async () => {
      await settingsPage.verifyManHoursCalculation('Fabrication');
    });

    await test.step('Save settings', async () => {
      await settingsPage.saveButton.click();
      await settingsPage.expectSettingsModalClosed();
    });
  });

  test('should handle basic kanban interactions', async ({ page }) => {
    const kanbanPage = new KanbanBoardPage(page);

    await kanbanPage.gotoKanbanBoard();

    await test.step('Column collapse works', async () => {
      const fabricationColumn = kanbanPage.getColumn('Fabrication');
      const collapseButton = fabricationColumn.locator('[data-testid="column-collapse-button"]');

      await collapseButton.click();
      await kanbanPage.page.waitForTimeout(500);

      await expect(fabricationColumn).toHaveClass(/h-16/);

      // Expand back
      await collapseButton.click();
      await kanbanPage.page.waitForTimeout(500);

      await expect(fabricationColumn).not.toHaveClass(/h-16/);
    });

    await test.step('Refresh schedules works', async () => {
      await kanbanPage.refreshButton.click();
      await kanbanPage.page.waitForTimeout(2000);

      await kanbanPage.waitForKanbanBoardLoad();
    });
  });

  test('should support responsive design', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await test.step('Desktop view works', async () => {
      await page.setViewportSize({ width: 1920, height: 1080 });
      await dashboardPage.gotoDashboard();
      await dashboardPage.verifyKPICards();
      await dashboardPage.verifyChartsRendered();
    });

    await test.step('Mobile view works', async () => {
      await page.setViewportSize({ width: 375, height: 667 });
      await dashboardPage.helpers.waitForLoadingToComplete();

      await expect(dashboardPage.kpiCards).toBeVisible();
    });

    await test.step('Tablet view works', async () => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await dashboardPage.helpers.waitForLoadingToComplete();

      await expect(dashboardPage.kpiCards).toBeVisible();
    });
  });

  test('should handle navigation between views', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    const kanbanPage = new KanbanBoardPage(page);

    await test.step('Start on dashboard', async () => {
      await dashboardPage.gotoDashboard();
      await dashboardPage.verifyKPICards();
    });

    await test.step('Navigate to kanban', async () => {
      await dashboardPage.helpers.navigateToView('kanban');
      await kanbanPage.waitForKanbanBoardLoad();
    });

    await test.step('Navigate back to dashboard', async () => {
      await dashboardPage.helpers.navigateToView('dashboard');
      await dashboardPage.helpers.waitForLoadingToComplete();
      await dashboardPage.verifyKPICards();
    });
  });

  test('should load within performance expectations', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    const startTime = Date.now();
    await dashboardPage.gotoDashboard();
    const loadTime = Date.now() - startTime;

    // Should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
  });

  test('should handle category filtering', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await dashboardPage.gotoDashboard();
    await dashboardPage.helpers.waitForLoadingToComplete();

    await test.step('Switch to Late Orders category', async () => {
      await dashboardPage.categoryFilter.click();
      await dashboardPage.page.locator('text=Late Orders').click();
      await dashboardPage.helpers.waitForLoadingToComplete();
    });

    await test.step('Charts update with new category', async () => {
      await dashboardPage.verifyChartsRendered();
    });

    await test.step('Switch back to All Orders', async () => {
      await dashboardPage.categoryFilter.click();
      await dashboardPage.page.locator('text=All Orders').click();
      await dashboardPage.helpers.waitForLoadingToComplete();
    });
  });

  test('should verify basic accessibility', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await dashboardPage.gotoDashboard();

    await test.step('Page has proper heading structure', async () => {
      const h1Elements = page.locator('h1');
      const h2Elements = page.locator('h2');

      await expect(h1Elements).toHaveCount({ min: 1 });
      await expect(h2Elements).toHaveCount({ min: 1 });
    });

    await test.step('Interactive elements are accessible', async () => {
      await dashboardPage.checkAccessibility();
    });
  });
});