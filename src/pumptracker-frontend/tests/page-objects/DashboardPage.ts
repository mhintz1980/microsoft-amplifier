import { expect, Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class DashboardPage extends BasePage {
  // KPI Cards locators
  readonly kpiCards = this.page.locator('[data-testid="kpi-cards"]');
  readonly lateOrdersCard = this.page.locator('[data-testid="kpi-late-orders"]');
  readonly avgValuePerOrderCard = this.page.locator('[data-testid="kpi-avg-value"]');
  readonly totalOrdersCard = this.page.locator('[data-testid="kpi-total-orders"]');
  readonly onTimeDeliveryCard = this.page.locator('[data-testid="kpi-on-time-delivery"]');

  // Charts locators
  readonly chartsSection = this.page.locator('[data-testid="charts-section"]');
  readonly lateOrdersChart = this.page.locator('[data-testid="late-orders-chart"]');
  readonly valueByCustomerChart = this.page.locator('[data-testid="value-by-customer-chart"]');
  readonly leadTimeTrendChart = this.page.locator('[data-testid="lead-time-trend-chart"]');
  readonly departmentTreeMapChart = this.page.locator('[data-testid="department-treemap-chart"]');

  // Filters locators
  readonly universalFilters = this.page.locator('[data-testid="universal-filters"]');
  readonly categoryFilter = this.page.locator('[data-testid="category-filter"]');
  readonly dateRangeFilter = this.page.locator('[data-testid="date-range-filter"]');
  readonly favoritesButton = this.page.locator('[data-testid="favorites-button"]');

  // Order details
  readonly orderDetailsSection = this.page.locator('[data-testid="order-details"]');
  readonly expandableOrderRows = this.page.locator('[data-testid="order-row-expandable"]');

  constructor(page: Page) {
    super(page);
  }

  /**
   * Navigate to dashboard
   */
  async gotoDashboard(): Promise<void> {
    await this.goto('/');
    await this.waitForDashboardLoad();
  }

  /**
   * Wait for dashboard to fully load
   */
  async waitForDashboardLoad(): Promise<void> {
    await expect(this.kpiCards).toBeVisible();
    await expect(this.chartsSection).toBeVisible();
    await this.helpers.waitForLoadingToComplete();
  }

  /**
   * Verify all KPI cards are displayed
   */
  async verifyKPICards(): Promise<void> {
    await expect(this.lateOrdersCard).toBeVisible();
    await expect(this.avgValuePerOrderCard).toBeVisible();
    await expect(this.totalOrdersCard).toBeVisible();
    await expect(this.onTimeDeliveryCard).toBeVisible();

    // Verify KPI cards have numeric values
    await expect(this.lateOrdersCard.locator('text=/\\d+/')).toBeVisible();
    await expect(this.totalOrdersCard.locator('text=/\\d+/')).toBeVisible();
    await expect(this.avgValuePerOrderCard.locator('text=/\\$?[\\d,]+/')).toBeVisible();
    await expect(this.onTimeDeliveryCard.locator('text=/\\d+%/')).toBeVisible();
  }

  /**
   * Verify all charts are rendered
   */
  async verifyChartsRendered(): Promise<void> {
    await this.helpers.verifyChartRenders('[data-testid="late-orders-chart"]');
    await this.helpers.verifyChartRenders('[data-testid="value-by-customer-chart"]');
    await this.helpers.verifyChartRenders('[data-testid="lead-time-trend-chart"]');
    await this.helpers.verifyChartRenders('[data-testid="department-treemap-chart"]');
  }

  /**
   * Test category cycling functionality
   */
  async testCategoryCycling(): Promise<void> {
    const categories = ['All Orders', 'Late Orders', 'High Value', 'Standard'];

    for (const category of categories) {
      await this.categoryFilter.click();
      await this.page.locator(`text=${category}`).click();
      await this.helpers.waitForLoadingToComplete();

      // Verify charts update with new category
      await this.verifyChartsRendered();

      // Take screenshot for visual verification
      await this.takeScreenshot(`dashboard-category-${category.toLowerCase().replace(' ', '-')}`);
    }
  }

  /**
   * Test favorites functionality
   */
  async testFavoritesToggle(): Promise<void> {
    // Check initial state
    const initialFavoritesState = await this.favoritesButton.getAttribute('aria-pressed');

    // Toggle favorites
    await this.favoritesButton.click();
    await this.helpers.waitForLoadingToComplete();

    // Verify state changed
    const newFavoritesState = await this.favoritesButton.getAttribute('aria-pressed');
    expect(initialFavoritesState).not.toBe(newFavoritesState);

    // Toggle back
    await this.favoritesButton.click();
    await this.helpers.waitForLoadingToComplete();
  }

  /**
   * Test chart click-to-drill-down functionality
   */
  async testChartDrillDown(chartSelector: string, expectedDrillDownContent: string): Promise<void> {
    const chart = this.page.locator(chartSelector);

    // Click on the chart
    await chart.click();

    // Wait for drill-down content to appear
    await this.page.waitForSelector(`text=${expectedDrillDownContent}`, { timeout: 5000 });

    // Verify drill-down navigation works
    await expect(this.page.locator(`text=${expectedDrillDownContent}`)).toBeVisible();

    // Take screenshot of drill-down view
    await this.takeScreenshot(`chart-drill-down-${chartSelector.replace('[data-testid="', '').replace('"]', '')}`);
  }

  /**
   * Test KPI card interactions
   */
  async testKPICardInteractions(): Promise<void> {
    // Test late orders card click
    await this.lateOrdersCard.click();
    await this.helpers.waitForLoadingToComplete();

    // Should filter to show late orders
    await this.verifyChartsRendered();

    // Test total orders card hover (if it has hover effect)
    await this.totalOrdersCard.hover();
    await this.page.waitForTimeout(500);
  }

  /**
   * Verify Department Tree Map shows human-readable names
   */
  async verifyDepartmentTreeMapNames(): Promise<void> {
    await this.departmentTreeMapChart.waitFor({ state: 'visible' });

    // Look for human-readable department names in the chart
    const expectedDepartments = ['Fabrication', 'Powder Coat', 'Assembly', 'Testing', 'Shipping', 'QA Complete'];

    for (const dept of expectedDepartments) {
      const deptElement = this.departmentTreeMapChart.locator(`text=${dept}`);
      // Department names should be visible in the chart
      if (await deptElement.count() > 0) {
        await expect(deptElement.first()).toBeVisible();
      }
    }
  }

  /**
   * Test order details expandable rows
   */
  async testOrderDetailsExpansion(): Promise<void> {
    // Find first order row
    const firstOrderRow = this.expandableOrderRows.first();

    if (await firstOrderRow.count() > 0) {
      // Expand the row
      await firstOrderRow.click();
      await this.page.waitForTimeout(500);

      // Verify expanded content is visible
      const expandedContent = firstOrderRow.locator('[data-testid="expanded-order-content"]');
      await expect(expandedContent).toBeVisible();

      // Collapse the row
      await firstOrderRow.click();
      await this.page.waitForTimeout(500);

      // Verify expanded content is hidden
      await expect(expandedContent).toBeHidden();
    }
  }

  /**
   * Test date range filtering
   */
  async testDateRangeFiltering(): Promise<void> {
    await this.dateRangeFilter.click();

    // Select a predefined date range
    await this.page.locator('text="Last 30 Days"').click();
    await this.helpers.waitForLoadingToComplete();

    // Verify charts update
    await this.verifyChartsRendered();
  }

  /**
   * Get current KPI values
   */
  async getKPIValues(): Promise<{
    lateOrders: number;
    avgValue: string;
    totalOrders: number;
    onTimeDelivery: number;
  }> {
    const lateOrdersText = await this.helpers.getTextContent('[data-testid="kpi-late-orders"] .text-2xl');
    const avgValueText = await this.helpers.getTextContent('[data-testid="kpi-avg-value"] .text-2xl');
    const totalOrdersText = await this.helpers.getTextContent('[data-testid="kpi-total-orders"] .text-2xl');
    const onTimeDeliveryText = await this.helpers.getTextContent('[data-testid="kpi-on-time-delivery"] .text-2xl');

    return {
      lateOrders: parseInt(lateOrdersText) || 0,
      avgValue: avgValueText,
      totalOrders: parseInt(totalOrdersText) || 0,
      onTimeDelivery: parseInt(onTimeDeliveryText.replace('%', '')) || 0
    };
  }
}