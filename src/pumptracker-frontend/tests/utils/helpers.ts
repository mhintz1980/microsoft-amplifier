import { expect, Page } from '@playwright/test';

export class TestHelpers {
  constructor(private page: Page) {}

  /**
   * Wait for the application to be fully loaded
   */
  async waitForAppLoad(): Promise<void> {
    // Wait for either dashboard or kanban view to be visible
    await Promise.race([
      this.page.waitForSelector('[data-testid="dashboard"]'),
      this.page.waitForSelector('[data-testid="kanban-board"]'),
      this.page.waitForSelector('h2:has-text("Dashboard")'),
      this.page.waitForSelector('h2:has-text("Production Board")')
    ]);
  }

  /**
   * Navigate between Dashboard and Kanban views
   */
  async navigateToView(view: 'dashboard' | 'kanban'): Promise<void> {
    const navigationButton = this.page.locator(`button:has-text("${view === 'dashboard' ? 'Dashboard' : 'Production Board'}")`);
    await navigationButton.click();

    // Wait for view to load
    if (view === 'dashboard') {
      await this.page.waitForSelector('[data-testid="kpi-cards"]');
    } else {
      await this.page.waitForSelector('[data-testid="kanban-board"]');
    }
  }

  /**
   * Wait for and handle loading states
   */
  async waitForLoadingToComplete(): Promise<void> {
    // Wait for any loading spinners to disappear
    await this.page.waitForSelector('.animate-spin', { state: 'detached' }).catch(() => {});

    // Wait for charts to render (look for SVG elements)
    await this.page.waitForSelector('svg', { state: 'attached' }).catch(() => {});

    // Small delay to ensure all animations complete
    await this.page.waitForTimeout(500);
  }

  /**
   * Take screenshot with descriptive name
   */
  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({
      path: `test-results/screenshots/${name}-${Date.now()}.png`,
      fullPage: true
    });
  }

  /**
   * Verify accessibility of current page
   */
  async checkAccessibility(): Promise<void> {
    // Basic accessibility checks
    await expect(this.page.locator('h1, h2')).toHaveCount({ min: 1 });

    // Check for proper ARIA labels on interactive elements
    const buttons = this.page.locator('button:not([aria-label]):not([aria-labelledby])');
    const buttonCount = await buttons.count();

    if (buttonCount > 0) {
      console.warn(`⚠️ Found ${buttonCount} buttons without ARIA labels`);
    }
  }

  /**
   * Mock localStorage for testing
   */
  async mockLocalStorage(data: Record<string, string>): Promise<void> {
    await this.page.evaluate((storageData) => {
      Object.entries(storageData).forEach(([key, value]) => {
        localStorage.setItem(key, value);
      });
    }, data);
  }

  /**
   * Clear localStorage
   */
  async clearLocalStorage(): Promise<void> {
    await this.page.evaluate(() => {
      localStorage.clear();
    });
  }

  /**
   * Check if element is visible and enabled
   */
  async isElementVisibleAndEnabled(selector: string): Promise<boolean> {
    const element = this.page.locator(selector);
    const isVisible = await element.isVisible();
    const isEnabled = await element.isEnabled();
    return isVisible && isEnabled;
  }

  /**
   * Wait for network idle (no network requests for 500ms)
   */
  async waitForNetworkIdle(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Get element text content safely
   */
  async getTextContent(selector: string): Promise<string> {
    const element = this.page.locator(selector);
    return await element.textContent() || '';
  }

  /**
   * Verify chart renders correctly
   */
  async verifyChartRenders(chartSelector: string): Promise<void> {
    const chart = this.page.locator(chartSelector);

    // Check if chart container exists
    await expect(chart).toBeVisible();

    // Check for SVG element (Recharts uses SVG)
    await expect(chart.locator('svg')).toBeVisible();

    // Check for at least one chart element
    await expect(chart.locator('svg').first()).toBeVisible();
  }

  /**
   * Handle modal/dialog interactions
   */
  async waitForModal(modalSelector: string): Promise<void> {
    await this.page.waitForSelector(modalSelector);
    await expect(this.page.locator(modalSelector)).toBeVisible();
  }

  async closeModal(closeButtonSelector: string): Promise<void> {
    await this.page.click(closeButtonSelector);
    await expect(this.page.locator(closeButtonSelector).closest('.fixed')).toBeHidden();
  }

  /**
   * Drag and drop helper
   */
  async dragAndDrop(sourceSelector: string, targetSelector: string): Promise<void> {
    const source = this.page.locator(sourceSelector);
    const target = this.page.locator(targetSelector);

    await source.dragTo(target);
  }

  /**
   * Fill form with validation
   */
  async fillForm(fields: Record<string, string>): Promise<void> {
    for (const [selector, value] of Object.entries(fields)) {
      const field = this.page.locator(selector);
      await expect(field).toBeVisible();
      await field.fill(value);
    }
  }

  /**
   * Verify form validation errors
   */
  async verifyValidationErrors(errors: Record<string, string>): Promise<void> {
    for (const [fieldSelector, expectedError] of Object.entries(errors)) {
      const field = this.page.locator(fieldSelector);
      const errorElement = field.locator('..').locator('text=' + expectedError);
      await expect(errorElement).toBeVisible();
    }
  }
}