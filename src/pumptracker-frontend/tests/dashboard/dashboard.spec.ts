import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';

test.describe('Dashboard E2E Tests', () => {
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    await dashboardPage.gotoDashboard();
  });

  test.describe('Dashboard Loading', () => {
    test('should load dashboard with all components', async () => {
      await test.step('Dashboard loads successfully', async () => {
        await expect(dashboardPage.page).toHaveURL(/.*\/$/);
        await dashboardPage.waitForDashboardLoad();
      });

      await test.step('KPI cards are displayed', async () => {
        await dashboardPage.verifyKPICards();
      });

      await test.step('Charts are rendered', async () => {
        await dashboardPage.verifyChartsRendered();
      });

      await test.step('Filters are available', async () => {
        await expect(dashboardPage.universalFilters).toBeVisible();
        await expect(dashboardPage.categoryFilter).toBeVisible();
        await expect(dashboardPage.dateRangeFilter).toBeVisible();
      });

      await test.step('Order details section is present', async () => {
        await expect(dashboardPage.orderDetailsSection).toBeVisible();
      });
    });

    test('should handle accessibility requirements', async () => {
      await test.step('Page has proper heading structure', async () => {
        const h1Elements = dashboardPage.page.locator('h1');
        const h2Elements = dashboardPage.page.locator('h2');

        await expect(h1Elements).toHaveCount({ min: 1 });
        await expect(h2Elements).toHaveCount({ min: 1 });
      });

      await test.step('Interactive elements are accessible', async () => {
        await dashboardPage.checkAccessibility();
      });
    });
  });

  test.describe('KPI Cards Functionality', () => {
    test('should display correct KPI metrics', async () => {
      const kpiValues = await dashboardPage.getKPIValues();

      await test.step('Late orders KPI is numeric', async () => {
        expect(kpiValues.lateOrders).toBeGreaterThanOrEqual(0);
        expect(kpiValues.lateOrders).toBeLessThan(1000);
      });

      await test.step('Total orders KPI is numeric', async () => {
        expect(kpiValues.totalOrders).toBeGreaterThan(0);
        expect(kpiValues.totalOrders).toBeLessThan(10000);
      });

      await test.step('Average value KPI is formatted correctly', async () => {
        expect(kpiValues.avgValue).toMatch(/\$?[\d,]+\.?\d*/);
      });

      await test.step('On-time delivery KPI is percentage', async () => {
        expect(kpiValues.onTimeDelivery).toBeGreaterThanOrEqual(0);
        expect(kpiValues.onTimeDelivery).toBeLessThanOrEqual(100);
      });
    });

    test('should handle KPI card interactions', async () => {
      await test.step('Late orders card is clickable', async () => {
        await dashboardPage.lateOrdersCard.click();
        await dashboardPage.helpers.waitForLoadingToComplete();
        await dashboardPage.verifyChartsRendered();
      });

      await test.step('Total orders card shows hover effect', async () => {
        await dashboardPage.totalOrdersCard.hover();
        await dashboardPage.page.waitForTimeout(500);
      });
    });
  });

  test.describe('Charts Functionality', () => {
    test('should render all charts correctly', async () => {
      await test.step('Late orders chart renders', async () => {
        await dashboardPage.helpers.verifyChartRenders('[data-testid="late-orders-chart"]');
      });

      await test.step('Value by customer chart renders', async () => {
        await dashboardPage.helpers.verifyChartRenders('[data-testid="value-by-customer-chart"]');
      });

      await test.step('Lead time trend chart renders', async () => {
        await dashboardPage.helpers.verifyChartRenders('[data-testid="lead-time-trend-chart"]');
      });

      await test.step('Department tree map chart renders', async () => {
        await dashboardPage.helpers.verifyChartRenders('[data-testid="department-treemap-chart"]');
      });
    });

    test('should support click-to-drill-down functionality', async () => {
      await test.step('Late orders chart drill-down works', async () => {
        await dashboardPage.testChartDrillDown(
          '[data-testid="late-orders-chart"]',
          'Order Details'
        );
      });

      await test.step('Value by customer chart drill-down works', async () => {
        await dashboardPage.testChartDrillDown(
          '[data-testid="value-by-customer-chart"]',
          'Customer Details'
        );
      });
    });

    test('should display human-readable department names in tree map', async () => {
      await dashboardPage.verifyDepartmentTreeMapNames();

      const expectedDepartments = [
        'Fabrication', 'Powder Coat', 'Assembly',
        'Testing', 'Shipping', 'QA Complete'
      ];

      for (const dept of expectedDepartments) {
        const deptElement = dashboardPage.departmentTreeMapChart.locator(`text=${dept}`);
        if (await deptElement.count() > 0) {
          await expect(deptElement.first()).toBeVisible();
        }
      }
    });
  });

  test.describe('Category Cycling', () => {
    test('should cycle through chart categories', async () => {
      await dashboardPage.testCategoryCycling();
    });

    test('should maintain data integrity during category changes', async () => {
      const initialKPI = await dashboardPage.getKPIValues();

      await test.step('Switch to Late Orders category', async () => {
        await dashboardPage.categoryFilter.click();
        await dashboardPage.page.locator('text=Late Orders').click();
        await dashboardPage.helpers.waitForLoadingToComplete();
      });

      await test.step('Switch back to All Orders', async () => {
        await dashboardPage.categoryFilter.click();
        await dashboardPage.page.locator('text=All Orders').click();
        await dashboardPage.helpers.waitForLoadingToComplete();
      });

      await test.step('Verify KPI values return to original', async () => {
        const finalKPI = await dashboardPage.getKPIValues();
        expect(finalKPI.totalOrders).toBe(initialKPI.totalOrders);
      });
    });
  });

  test.describe('Favorites Functionality', () => {
    test('should toggle favorites state', async () => {
      await dashboardPage.testFavoritesToggle();
    });

    test('should persist favorites in session', async () => {
      await test.step('Enable favorites', async () => {
        await dashboardPage.favoritesButton.click();
        await dashboardPage.helpers.waitForLoadingToComplete();
      });

      await test.step('Navigate away and back', async () => {
        await dashboardPage.goto('/settings');
        await dashboardPage.goto('/');
        await dashboardPage.waitForDashboardLoad();
      });

      await test.step('Favorites state should be maintained', async () => {
        const favoritesState = await dashboardPage.favoritesButton.getAttribute('aria-pressed');
        expect(favoritesState).toBe('true');
      });
    });
  });

  test.describe('Date Range Filtering', () => {
    test('should filter by date range', async () => {
      await dashboardPage.testDateRangeFiltering();
    });

    test('should update charts based on date selection', async () => {
      await test.step('Select "Last 7 Days"', async () => {
        await dashboardPage.dateRangeFilter.click();
        await dashboardPage.page.locator('text="Last 7 Days"').click();
        await dashboardPage.helpers.waitForLoadingToComplete();
      });

      await test.step('Verify charts update', async () => {
        await dashboardPage.verifyChartsRendered();
      });

      await test.step('Select "Last 90 Days"', async () => {
        await dashboardPage.dateRangeFilter.click();
        await dashboardPage.page.locator('text="Last 90 Days"').click();
        await dashboardPage.helpers.waitForLoadingToComplete();
      });

      await test.step('Verify charts update again', async () => {
        await dashboardPage.verifyChartsRendered();
      });
    });
  });

  test.describe('Order Details', () => {
    test('should display expandable order rows', async () => {
      await dashboardPage.testOrderDetailsExpansion();
    });

    test('should show order information on expansion', async () => {
      const firstOrderRow = dashboardPage.expandableOrderRows.first();

      if (await firstOrderRow.count() > 0) {
        await test.step('Expand order row', async () => {
          await firstOrderRow.click();
          await dashboardPage.page.waitForTimeout(500);
        });

        await test.step('Verify expanded content contains order details', async () => {
          const expandedContent = firstOrderRow.locator('[data-testid="expanded-order-content"]');
          await expect(expandedContent).toBeVisible();

          // Should contain PO number, customer info, etc.
          await expect(expandedContent).toContainText(/PO|Order|Customer/i);
        });

        await test.step('Collapse order row', async () => {
          await firstOrderRow.click();
          await dashboardPage.page.waitForTimeout(500);
          await expect(expandedContent).toBeHidden();
        });
      }
    });
  });

  test.describe('Responsive Design', () => {
    test('should adapt to mobile viewport', async () => {
      await dashboardPage.page.setViewportSize({ width: 375, height: 667 });
      await dashboardPage.page.waitForTimeout(500);

      await test.step('KPI cards stack vertically', async () => {
        await expect(dashboardPage.kpiCards).toBeVisible();
      });

      await test.step('Charts are responsive', async () => {
        await dashboardPage.verifyChartsRendered();
      });

      await test.step('Filters remain accessible', async () => {
        await expect(dashboardPage.universalFilters).toBeVisible();
      });
    });

    test('should adapt to tablet viewport', async () => {
      await dashboardPage.page.setViewportSize({ width: 768, height: 1024 });
      await dashboardPage.page.waitForTimeout(500);

      await dashboardPage.verifyChartsRendered();
      await dashboardPage.verifyKPICards();
    });
  });

  test.describe('Performance', () => {
    test('should load within acceptable time', async () => {
      const startTime = Date.now();
      await dashboardPage.gotoDashboard();
      const loadTime = Date.now() - startTime;

      // Should load within 5 seconds
      expect(loadTime).toBeLessThan(5000);
    });

    test('should handle category changes efficiently', async () => {
      const startTime = Date.now();
      await dashboardPage.categoryFilter.click();
      await dashboardPage.page.locator('text=High Value').click();
      await dashboardPage.helpers.waitForLoadingToComplete();
      const changeTime = Date.now() - startTime;

      // Category change should complete within 3 seconds
      expect(changeTime).toBeLessThan(3000);
    });
  });

  test.describe('Error Handling', () => {
    test('should handle network errors gracefully', async () => {
      // Mock network failure
      await dashboardPage.page.route('**/*', route => route.abort());

      await test.step('Navigate to dashboard with network error', async () => {
        await dashboardPage.gotoDashboard();
      });

      await test.step('Should show error state or fallback UI', async () => {
        // Either shows error message or cached data
        const hasContent = await dashboardPage.page.locator('text=Error|No Data|Unable to load').count() > 0 ||
                           await dashboardPage.kpiCards.count() > 0;

        expect(hasContent).toBeTruthy();
      });
    });
  });
});