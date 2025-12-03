import { expect, Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class SettingsModalPage extends BasePage {
  // Modal locators
  readonly settingsModal = this.page.locator('[data-testid="settings-modal"]');
  readonly settingsButton = this.page.locator('[data-testid="settings-button"]');
  readonly closeButton = this.page.locator('[data-testid="settings-close-button"]');
  readonly saveButton = this.page.locator('[data-testid="settings-save-button"]');
  readonly cancelButton = this.page.locator('[data-testid="settings-cancel-button"]');
  readonly resetButton = this.page.locator('[data-testid="settings-reset-button"]');

  // Department settings locators
  readonly departmentCards = this.page.locator('[data-testid="department-card"]');
  readonly employeeInputs = this.page.locator('[data-testid="employee-count-input"]');
  readonly efficiencyInputs = this.page.locator('[data-testid="efficiency-input"]');
  readonly manHoursDisplays = this.page.locator('[data-testid="man-hours-display"]');

  // Summary locators
  readonly totalEmployeesDisplay = this.page.locator('[data-testid="total-employees"]');
  readonly averageEfficiencyDisplay = this.page.locator('[data-testid="average-efficiency"]');
  readonly totalManHoursDisplay = this.page.locator('[data-testid="total-man-hours"]');

  // Validation locators
  readonly validationErrors = this.page.locator('[data-testid="validation-error"]');

  constructor(page: Page) {
    super(page);
  }

  /**
   * Open settings modal
   */
  async openSettingsModal(): Promise<void> {
    await this.settingsButton.click();
    await this.expectSettingsModalOpen();
  }

  /**
   * Close settings modal
   */
  async closeSettingsModal(): Promise<void> {
    await this.closeButton.click();
    await this.expectSettingsModalClosed();
  }

  /**
   * Expect settings modal to be open
   */
  async expectSettingsModalOpen(): Promise<void> {
    await this.helpers.waitForModal('[data-testid="settings-modal"]');
    await expect(this.settingsModal).toBeVisible();
  }

  /**
   * Expect settings modal to be closed
   */
  async expectSettingsModalClosed(): Promise<void> {
    await expect(this.settingsModal).toBeHidden();
  }

  /**
   * Get department card by department name
   */
  getDepartmentCard(departmentName: string) {
    return this.departmentCards.filter({ hasText: departmentName });
  }

  /**
   * Get employee count input for a department
   */
  getEmployeeInput(departmentName: string) {
    const card = this.getDepartmentCard(departmentName);
    return card.locator('[data-testid="employee-count-input"]');
  }

  /**
   * Get efficiency input for a department
   */
  getEfficiencyInput(departmentName: string) {
    const card = this.getDepartmentCard(departmentName);
    return card.locator('[data-testid="efficiency-input"]');
  }

  /**
   * Get man-hours display for a department
   */
  getManHoursDisplay(departmentName: string) {
    const card = this.getDepartmentCard(departmentName);
    return card.locator('[data-testid="man-hours-display"]');
  }

  /**
   * Set department employee count
   */
  async setEmployeeCount(departmentName: string, count: number): Promise<void> {
    const input = this.getEmployeeInput(departmentName);
    await expect(input).toBeVisible();
    await input.fill(count.toString());
  }

  /**
   * Set department efficiency
   */
  async setEfficiency(departmentName: string, efficiency: number): Promise<void> {
    const input = this.getEfficiencyInput(departmentName);
    await expect(input).toBeVisible();
    await input.fill(efficiency.toString());
  }

  /**
   * Get current employee count for a department
   */
  async getEmployeeCount(departmentName: string): Promise<number> {
    const input = this.getEmployeeInput(departmentName);
    const value = await input.inputValue();
    return parseInt(value) || 0;
  }

  /**
   * Get current efficiency for a department
   */
  async getEfficiency(departmentName: string): Promise<number> {
    const input = this.getEfficiencyInput(departmentName);
    const value = await input.inputValue();
    return parseInt(value) || 0;
  }

  /**
   * Get current man-hours for a department
   */
  async getManHours(departmentName: string): Promise<number> {
    const display = this.getManHoursDisplay(departmentName);
    const text = await display.textContent();
    return parseFloat(text?.replace(/[^0-9.]/g, '') || '0');
  }

  /**
   * Verify man-hours calculation
   */
  async verifyManHoursCalculation(departmentName: string): Promise<void> {
    const employeeCount = await this.getEmployeeCount(departmentName);
    const efficiency = await this.getEfficiency(departmentName);
    const expectedManHours = (employeeCount * 8 * efficiency) / 100;
    const actualManHours = await this.getManHours(departmentName);

    expect(actualManHours).toBeCloseTo(expectedManHours, 1);
  }

  /**
   * Test department settings modification
   */
  async testDepartmentSettingsModification(): Promise<void> {
    const testCases = [
      { department: 'Fabrication', employees: 10, efficiency: 90 },
      { department: 'Powder Coat', employees: 5, efficiency: 95 },
      { department: 'Assembly', employees: 8, efficiency: 85 },
    ];

    for (const testCase of testCases) {
      // Set new values
      await this.setEmployeeCount(testCase.department, testCase.employees);
      await this.setEfficiency(testCase.department, testCase.efficiency);

      // Verify values were set
      expect(await this.getEmployeeCount(testCase.department)).toBe(testCase.employees);
      expect(await this.getEfficiency(testCase.department)).toBe(testCase.efficiency);

      // Verify man-hours calculation
      await this.verifyManHoursCalculation(testCase.department);

      console.log(`✅ ${testCase.department} settings verified`);
    }
  }

  /**
   * Test settings persistence
   */
  async testSettingsPersistence(): Promise<void> {
    // Set initial values
    await this.setEmployeeCount('Fabrication', 15);
    await this.setEfficiency('Fabrication', 88);

    // Save settings
    await this.saveButton.click();
    await this.expectSettingsModalClosed();

    // Reopen settings
    await this.openSettingsModal();

    // Verify values persisted
    expect(await this.getEmployeeCount('Fabrication')).toBe(15);
    expect(await this.getEfficiency('Fabrication')).toBe(88);
  }

  /**
   * Test settings reset to defaults
   */
  async testSettingsReset(): Promise<void> {
    // Modify some settings
    await this.setEmployeeCount('Fabrication', 20);
    await this.setEfficiency('Fabrication', 75);

    // Reset to defaults
    await this.resetButton.click();

    // Handle confirmation dialog
    await this.page.locator('button:has-text("OK")').click();

    // Verify values were reset
    // These should match the default values from the application
    expect(await this.getEmployeeCount('Fabrication')).toBe(8); // Default value
    expect(await this.getEfficiency('Fabrication')).toBe(85); // Default value
  }

  /**
   * Test capacity calculation verification
   */
  async testCapacityCalculation(): Promise<void> {
    // Get summary values before changes
    const beforeTotal = await this.getTotalEmployees();
    const beforeManHours = await this.getTotalManHours();

    // Modify department settings
    await this.setEmployeeCount('Fabrication', 12);
    await this.setEfficiency('Fabrication', 90);

    // Verify individual department calculation
    await this.verifyManHoursCalculation('Fabrication');

    // Verify summary updates
    const afterTotal = await this.getTotalEmployees();
    const afterManHours = await this.getTotalManHours();

    expect(afterTotal).toBeGreaterThan(beforeTotal);
    expect(afterManHours).toBeGreaterThan(beforeManHours);
  }

  /**
   * Get total employees count
   */
  async getTotalEmployees(): Promise<number> {
    const text = await this.totalEmployeesDisplay.textContent();
    return parseInt(text?.replace(/[^0-9]/g, '') || '0');
  }

  /**
   * Get average efficiency
   */
  async getAverageEfficiency(): Promise<number> {
    const text = await this.averageEfficiencyDisplay.textContent();
    return parseInt(text?.replace(/[^0-9]/g, '') || '0');
  }

  /**
   * Get total man-hours
   */
  async getTotalManHours(): Promise<number> {
    const text = await this.totalManHoursDisplay.textContent();
    return parseFloat(text?.replace(/[^0-9.]/g, '') || '0');
  }

  /**
   * Test input validation
   */
  async testInputValidation(): Promise<void> {
    // Test negative values
    await this.setEmployeeCount('Fabrication', -5);
    await this.saveButton.click();

    // Should show validation error
    await expect(this.validationErrors.first()).toBeVisible();

    // Clear error and test valid values
    await this.setEmployeeCount('Fabrication', 10);
    await this.saveButton.click();

    // Should save successfully
    await this.expectSettingsModalClosed();
  }

  /**
   * Test efficiency limits
   */
  async testEfficiencyLimits(): Promise<void> {
    // Test efficiency > 100
    await this.setEfficiency('Fabrication', 150);

    // Should be capped at 100
    const efficiency = await this.getEfficiency('Fabrication');
    expect(efficiency).toBeLessThanOrEqual(100);

    // Test negative efficiency
    await this.setEfficiency('Fabrication', -10);

    // Should be capped at 0
    const negativeEfficiency = await this.getEfficiency('Fabrication');
    expect(negativeEfficiency).toBeGreaterThanOrEqual(0);
  }

  /**
   * Cancel changes test
   */
  async testCancelChanges(): Promise<void> {
    // Get initial values
    const initialEmployees = await this.getEmployeeCount('Fabrication');
    const initialEfficiency = await this.getEfficiency('Fabrication');

    // Modify values
    await this.setEmployeeCount('Fabrication', 25);
    await this.setEfficiency('Fabrication', 65);

    // Cancel instead of saving
    await this.cancelButton.click();
    await this.expectSettingsModalClosed();

    // Reopen and verify values were not saved
    await this.openSettingsModal();
    expect(await this.getEmployeeCount('Fabrication')).toBe(initialEmployees);
    expect(await this.getEfficiency('Fabrication')).toBe(initialEfficiency);
  }
}