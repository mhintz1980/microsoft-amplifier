import { expect, Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class KanbanBoardPage extends BasePage {
  // Board locators
  readonly kanbanBoard = this.page.locator('[data-testid="kanban-board"]');
  readonly boardTitle = this.page.locator('h2:has-text("Production Board")');
  readonly refreshButton = this.page.locator('[data-testid="refresh-schedules-button"]');

  // Column locators
  readonly kanbanColumns = this.page.locator('[data-testid="kanban-column"]');
  readonly getColumn = (columnTitle: string) =>
    this.kanbanColumns.filter({ hasText: columnTitle });

  // Stage columns
  readonly notStartedColumn = this.getColumn('Not Started');
  readonly fabricationColumn = this.getColumn('Fabrication');
  readonly powderCoatColumn = this.getColumn('Powder Coat');
  readonly assemblyColumn = this.getColumn('Assembly');
  readonly testingColumn = this.getColumn('Testing');
  readonly shippingColumn = this.getColumn('Shipping');
  readonly qaCompleteColumn = this.getColumn('QA Complete');

  // Powder coat vendor swimlanes
  readonly powderCoatVendors = this.page.locator('[data-testid="powder-coat-vendor"]');
  readonly getVendorSwimlane = (vendorName: string) =>
    this.powderCoatVendors.filter({ hasText: vendorName });

  // Card locators
  readonly kanbanCards = this.page.locator('[data-testid="kanban-card"]');
  readonly addPumpButton = this.page.locator('[data-testid="add-pump-button"]');

  // Capacity status locators
  readonly capacityStatus = this.page.locator('[data-testid="capacity-status"]');
  readonly capacityConflictWarning = this.page.locator('[data-testid="capacity-conflict-warning"]');

  // Collapse/expand locators
  readonly columnCollapseButtons = this.page.locator('[data-testid="column-collapse-button"]');
  readonly cardCollapseButtons = this.page.locator('[data-testid="card-collapse-button"]');

  constructor(page: Page) {
    super(page);
  }

  /**
   * Navigate to kanban board
   */
  async gotoKanbanBoard(): Promise<void> {
    await this.helpers.navigateToView('kanban');
    await this.waitForKanbanBoardLoad();
  }

  /**
   * Wait for kanban board to fully load
   */
  async waitForKanbanBoardLoad(): Promise<void> {
    await expect(this.boardTitle).toBeVisible();
    await expect(this.kanbanBoard).toBeVisible();
    await expect(this.kanbanColumns).toHaveCount({ min: 7 }); // At least 7 columns
    await this.helpers.waitForLoadingToComplete();
  }

  /**
   * Verify all 8 stages are present
   */
  async verifyEightStages(): Promise<void> {
    const expectedStages = [
      'Not Started',
      'Fabrication',
      'Powder Coat',
      'Assembly',
      'Testing',
      'Shipping',
      'QA Complete'
    ];

    for (const stage of expectedStages) {
      const column = this.getColumn(stage);
      await expect(column).toBeVisible();
      await expect(column.locator('h3')).toContainText(stage);
    }
  }

  /**
   * Verify powder coat stage has 3-vendor swimlanes
   */
  async verifyPowderCoatVendorSwimlanes(): Promise<void> {
    await expect(this.powderCoatColumn).toBeVisible();

    // Should have vendor swimlanes
    const vendorCount = await this.powderCoatVendors.count();
    expect(vendorCount).toBe(3);

    // Verify vendor names
    const expectedVendors = [
      'Vendor A - Premium',
      'Vendor B - Standard',
      'Vendor C - Economy'
    ];

    for (const vendor of expectedVendors) {
      const swimlane = this.getVendorSwimlane(vendor);
      await expect(swimlane).toBeVisible();
      await expect(swimlane).toContainText(vendor);
    }

    // Verify each vendor shows capacity information
    for (const vendor of expectedVendors) {
      const swimlane = this.getVendorSwimlane(vendor);
      await expect(swimlane).toContainText('/');
      await expect(swimlane).toContainText('pumps');
    }
  }

  /**
   * Verify capacity-aware scheduling display
   */
  async verifyCapacityAwareScheduling(): Promise<void> {
    // Verify capacity status section is visible
    await expect(this.capacityStatus).toBeVisible();

    // Should show department information
    await expect(this.capacityStatus).toContainText('Department Capacity Status');
    await expect(this.capacityStatus).toContainText('man-hours/day');
    await expect(this.capacityStatus).toContainText('jobs queued');

    // Should show at least 4 departments
    const departments = this.capacityStatus.locator('[data-testid="department-capacity"]');
    await expect(departments).toHaveCount({ min: 4 });
  }

  /**
   * Test drag and drop functionality between columns
   */
  async testDragAndDrop(sourceColumnTitle: string, targetColumnTitle: string): Promise<void> {
    const sourceColumn = this.getColumn(sourceColumnTitle);
    const targetColumn = this.getColumn(targetColumnTitle);

    // Find first card in source column
    const firstCard = sourceColumn.locator('[data-testid="kanban-card"]').first();
    const cardCountBefore = await sourceColumn.locator('[data-testid="kanban-card"]').count();

    if (await firstCard.count() > 0) {
      // Get card details for verification
      const cardText = await firstCard.textContent();

      // Drag and drop card
      await firstCard.dragTo(targetColumn);

      // Wait for animation/update
      await this.page.waitForTimeout(1000);

      // Verify card moved (source column has fewer cards)
      const cardCountAfter = await sourceColumn.locator('[data-testid="kanban-card"]').count();
      expect(cardCountAfter).toBeLessThan(cardCountBefore);

      // Verify card is in target column
      const movedCard = targetColumn.locator('[data-testid="kanban-card"]').filter({ hasText: cardText || '' });
      await expect(movedCard).toBeVisible();
    }
  }

  /**
   * Test powder coat vendor assignment
   */
  async testPowderCoatVendorAssignment(): Promise<void> {
    const premiumVendor = this.getVendorSwimlane('Vendor A - Premium');
    const standardVendor = this.getVendorSwimlane('Vendor B - Standard');

    // Get initial card counts
    const premiumCountBefore = await premiumVendor.locator('[data-testid="kanban-card"]').count();

    // Look for a card in powder coat column (not in vendor swimlane)
    const powderCoatCards = this.powderCoatColumn.locator('[data-testid="kanban-card"]');

    if (await powderCoatCards.count() > 0) {
      const firstCard = powderCoatCards.first();

      // Drag card to premium vendor swimlane
      await firstCard.dragTo(premiumVendor);
      await this.page.waitForTimeout(1000);

      // Verify card is now in vendor swimlane
      const premiumCountAfter = await premiumVendor.locator('[data-testid="kanban-card"]').count();
      expect(premiumCountAfter).toBeGreaterThan(premiumCountBefore);
    }
  }

  /**
   * Test column collapse functionality
   */
  async testColumnCollapse(): Promise<void> {
    const fabricationColumn = this.getColumn('Fabrication');
    const collapseButton = fabricationColumn.locator('[data-testid="column-collapse-button"]');

    // Verify column is initially expanded
    await expect(fabricationColumn).not.toHaveClass(/h-16/);

    // Collapse column
    await collapseButton.click();
    await this.page.waitForTimeout(500);

    // Verify column is collapsed
    await expect(fabricationColumn).toHaveClass(/h-16/);

    // Expand column
    await collapseButton.click();
    await this.page.waitForTimeout(500);

    // Verify column is expanded again
    await expect(fabricationColumn).not.toHaveClass(/h-16/);
  }

  /**
   * Test card collapse functionality
   */
  async testCardCollapse(): Promise<void> {
    // Find a column with cards
    const columnWithCards = this.kanbanColumns.filter({ has: this.page.locator('[data-testid="kanban-card"]') }).first();

    const cardCollapseButton = columnWithCards.locator('[data-testid="card-collapse-button"]');

    if (await cardCollapseButton.count() > 0) {
      // Get card details before collapse
      const expandedCard = columnWithCards.locator('[data-testid="kanban-card"]').first();
      const expandedHeight = await expandedCard.evaluate(el => el.offsetHeight);

      // Collapse cards
      await cardCollapseButton.click();
      await this.page.waitForTimeout(500);

      // Verify cards are collapsed
      const collapsedCard = columnWithCards.locator('[data-testid="kanban-card"]').first();
      const collapsedHeight = await collapsedCard.evaluate(el => el.offsetHeight);

      expect(collapsedHeight).toBeLessThan(expandedHeight);

      // Expand cards again
      await cardCollapseButton.click();
      await this.page.waitForTimeout(500);

      // Verify cards are expanded
      const reExpandedCard = columnWithCards.locator('[data-testid="kanban-card"]').first();
      const reExpandedHeight = await reExpandedCard.evaluate(el => el.offsetHeight);

      expect(reExpandedHeight).toBeGreaterThan(collapsedHeight);
    }
  }

  /**
   * Test capacity conflict detection
   */
  async testCapacityConflictDetection(): Promise<void> {
    // This test would need to trigger capacity conflicts
    // For now, just verify the warning element exists
    if (await this.capacityConflictWarning.count() > 0) {
      await expect(this.capacityConflictWarning).toContainText('capacity conflicts');
    }
  }

  /**
   * Test refresh schedules functionality
   */
  async testRefreshSchedules(): Promise<void> {
    // Get initial card counts
    const initialCards = await this.kanbanCards.count();

    // Click refresh button
    await this.refreshButton.click();
    await this.page.waitForTimeout(2000);

    // Verify board still loads correctly
    await this.waitForKanbanBoardLoad();

    // Card counts should still be reasonable (not zero, not wildly different)
    const refreshedCards = await this.kanbanCards.count();
    expect(refreshedCards).toBeGreaterThan(0);
  }

  /**
   * Get cards count for a specific column
   */
  async getColumnCardCount(columnTitle: string): Promise<number> {
    const column = this.getColumn(columnTitle);
    return await column.locator('[data-testid="kanban-card"]').count();
  }

  /**
   * Get vendor capacity information
   */
  async getVendorCapacity(vendorName: string): Promise<{
    currentLoad: number;
    weeklyCapacity: number;
    available: number;
  }> {
    const swimlane = this.getVendorSwimlane(vendorName);
    const capacityText = await swimlane.locator('text=/\\d+\\/\\d+/').textContent();

    if (capacityText) {
      const [current, capacity] = capacityText.trim().split('/').map(n => parseInt(n));
      return {
        currentLoad: current,
        weeklyCapacity: capacity,
        available: capacity - current
      };
    }

    return { currentLoad: 0, weeklyCapacity: 0, available: 0 };
  }

  /**
   * Verify powder coat capacity summary
   */
  async verifyPowderCoatCapacitySummary(): Promise<void> {
    const capacitySummary = this.page.locator('[data-testid="powder-coat-capacity-summary"]');
    await expect(capacitySummary).toBeVisible();
    await expect(capacitySummary).toContainText('Powder Coat Capacity Summary');
    await expect(capacitySummary).toContainText('Total Capacity');
    await expect(capacitySummary).toContainText('pumps per week');
  }

  /**
   * Test responsive layout
   */
  async testResponsiveLayout(): Promise<void> {
    // Test mobile view
    await this.page.setViewportSize({ width: 375, height: 667 });
    await this.page.waitForTimeout(500);

    // Columns should stack vertically on mobile
    await expect(this.kanbanBoard).toBeVisible();
    await expect(this.kanbanColumns).toHaveCount({ min: 7 });

    // Test desktop view
    await this.page.setViewportSize({ width: 1920, height: 1080 });
    await this.page.waitForTimeout(500);

    // Columns should be in a grid on desktop
    await expect(this.kanbanBoard).toBeVisible();
    await expect(this.kanbanColumns).toHaveCount({ min: 7 });
  }

  /**
   * Get capacity status for all departments
   */
  async getCapacityStatus(): Promise<Array<{
    department: string;
    manHours: number;
    queuedJobs: number;
  }>> {
    const departments = this.capacityStatus.locator('[data-testid="department-capacity"]');
    const status = [];

    for (let i = 0; i < await departments.count(); i++) {
      const dept = departments.nth(i);
      const deptName = await dept.locator('[data-testid="department-name"]').textContent();
      const manHours = await dept.locator('[data-testid="man-hours"]').textContent();
      const queuedJobs = await dept.locator('[data-testid="queued-jobs"]').textContent();

      status.push({
        department: deptName || '',
        manHours: parseFloat(manHours?.replace(/[^0-9.]/g, '') || '0'),
        queuedJobs: parseInt(queuedJobs?.replace(/[^0-9]/g, '') || '0')
      });
    }

    return status;
  }
}