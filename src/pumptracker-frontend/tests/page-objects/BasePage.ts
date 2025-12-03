import { expect, Page } from '@playwright/test';
import { TestHelpers } from '../utils/helpers';

export class BasePage {
  readonly page: Page;
  readonly helpers: TestHelpers;

  constructor(page: Page) {
    this.page = page;
    this.helpers = new TestHelpers(page);
  }

  /**
   * Navigate to a specific URL
   */
  async goto(url: string = ''): Promise<void> {
    await this.page.goto(url);
    await this.helpers.waitForAppLoad();
  }

  /**
   * Get current URL
   */
  async getCurrentUrl(): Promise<string> {
    return this.page.url();
  }

  /**
   * Wait for page to be fully loaded
   */
  async waitForPageLoad(): Promise<void> {
    await this.helpers.waitForAppLoad();
    await this.helpers.waitForLoadingToComplete();
  }

  /**
   * Verify page title
   */
  async verifyPageTitle(expectedTitle: string): Promise<void> {
    await expect(this.page).toHaveTitle(new RegExp(expectedTitle, 'i'));
  }

  /**
   * Take screenshot with test context
   */
  async takeScreenshot(name: string): Promise<void> {
    await this.helpers.takeScreenshot(name);
  }

  /**
   * Check basic accessibility
   */
  async checkAccessibility(): Promise<void> {
    await this.helpers.checkAccessibility();
  }

  /**
   * Wait for and click a button
   */
  async clickButton(buttonText: string): Promise<void> {
    const button = this.page.locator(`button:has-text("${buttonText}")`);
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
    await button.click();
  }

  /**
   * Wait for and fill an input field
   */
  async fillInput(label: string, value: string): Promise<void> {
    const input = this.page.locator(`input:has-attribute(placeholder="${label}")`);
    if (await input.count() === 0) {
      // Try to find by label text
      const labelElement = this.page.locator(`label:has-text("${label}")`);
      const inputId = await labelElement.getAttribute('for');
      if (inputId) {
        await this.page.fill(`#${inputId}`, value);
        return;
      }
      throw new Error(`Input with label "${label}" not found`);
    }
    await input.fill(value);
  }

  /**
   * Verify text is visible on page
   */
  async verifyTextVisible(text: string): Promise<void> {
    await expect(this.page.locator(`text=${text}`)).toBeVisible();
  }

  /**
   * Verify text is not visible on page
   */
  async verifyTextNotVisible(text: string): Promise<void> {
    await expect(this.page.locator(`text=${text}`)).toBeHidden();
  }

  /**
   * Verify element is visible
   */
  async verifyElementVisible(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).toBeVisible();
  }

  /**
   * Verify element is hidden
   */
  async verifyElementHidden(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).toBeHidden();
  }

  /**
   * Wait for navigation to complete
   */
  async waitForNavigation(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }
}