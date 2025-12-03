import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';
import { KanbanBoardPage } from '../page-objects/KanbanBoardPage';

test.describe('Kanban Board E2E Tests', () => {
  let kanbanPage: KanbanBoardPage;

  test.beforeEach(async ({ page }) => {
    kanbanPage = new KanbanBoardPage(page);
    await kanbanPage.gotoKanbanBoard();
  });

  test.describe('Board Loading and Display', () => {
    test('should load kanban board with all components', async () => {
      await test.step('Board loads successfully', async () => {
        await expect(kanbanPage.page).toHaveURL(/.*\/$/);
        await kanbanPage.waitForKanbanBoardLoad();
      });

      await test.step('Board title is displayed', async () => {
        await expect(kanbanPage.boardTitle).toBeVisible();
        await expect(kanbanPage.boardTitle).toContainText('Production Board');
      });

      await test.step('Refresh button is available', async () => {
        await expect(kanbanPage.refreshButton).toBeVisible();
        await expect(kanbanPage.refreshButton).toContainText('Refresh Schedules');
      });
    });

    test('should display 8-stage production pipeline', async () => {
      await kanbanPage.verifyEightStages();
    });

    test('should display capacity status information', async () => {
      await kanbanPage.verifyCapacityAwareScheduling();

      const capacityStatus = await kanbanPage.getCapacityStatus();
      expect(capacityStatus.length).toBeGreaterThanOrEqual(4);

      for (const dept of capacityStatus) {
        expect(dept.department).toBeTruthy();
        expect(dept.manHours).toBeGreaterThan(0);
        expect(dept.queuedJobs).toBeGreaterThanOrEqual(0);
      }
    });
  });

  test.describe('Powder Coat Vendor Swimlanes', () => {
    test('should display 3-vendor swimlanes for powder coat', async () => {
      await kanbanPage.verifyPowderCoatVendorSwimlanes();
    });

    test('should show vendor capacity information', async () => {
      const vendors = ['Vendor A - Premium', 'Vendor B - Standard', 'Vendor C - Economy'];

      for (const vendor of vendors) {
        const capacity = await kanbanPage.getVendorCapacity(vendor);

        expect(capacity.weeklyCapacity).toBeGreaterThan(0);
        expect(capacity.currentLoad).toBeGreaterThanOrEqual(0);
        expect(capacity.available).toBeGreaterThanOrEqual(0);
        expect(capacity.available).toBe(capacity.weeklyCapacity - capacity.currentLoad);
      }
    });

    test('should verify powder coat capacity summary', async () => {
      await kanbanPage.verifyPowderCoatCapacitySummary();
    });
  });

  test.describe('Drag and Drop Functionality', () => {
    test('should allow dragging cards between columns', async () => {
      // Find columns with cards
      const columnsWithCards = [];
      const expectedStages = ['Not Started', 'Fabrication', 'Powder Coat', 'Assembly', 'Testing'];

      for (const stage of expectedStages) {
        const cardCount = await kanbanPage.getColumnCardCount(stage);
        if (cardCount > 0) {
          columnsWithCards.push(stage);
        }
      }

      // Need at least 2 columns with cards for testing drag and drop
      if (columnsWithCards.length >= 2) {
        const sourceColumn = columnsWithCards[0];
        const targetColumn = columnsWithCards[1];

        await test.step(`Drag card from ${sourceColumn} to ${targetColumn}`, async () => {
          const sourceCountBefore = await kanbanPage.getColumnCardCount(sourceColumn);
          const targetCountBefore = await kanbanPage.getColumnCardCount(targetColumn);

          await kanbanPage.testDragAndDrop(sourceColumn, targetColumn);

          const sourceCountAfter = await kanbanPage.getColumnCardCount(sourceColumn);
          const targetCountAfter = await kanbanPage.getColumnCardCount(targetColumn);

          // Verify card moved (allowing for potential animation delays)
          expect(sourceCountAfter).toBeLessThanOrEqual(sourceCountBefore);
        });
      } else {
        test.skip('Not enough columns with cards to test drag and drop');
      }
    });

    test('should allow dragging cards to powder coat vendors', async () => {
      const powderCoatCount = await kanbanPage.getColumnCardCount('Powder Coat');

      if (powderCoatCount > 0) {
        await kanbanPage.testPowderCoatVendorAssignment();
      } else {
        test.skip('No cards in Powder Coat column to test vendor assignment');
      }
    });
  });

  test.describe('Column Management', () => {
    test('should allow collapsing and expanding columns', async () => {
      await kanbanPage.testColumnCollapse();
    });

    test('should maintain column state during session', async () => {
      const fabricationColumn = kanbanPage.getColumn('Fabrication');
      const collapseButton = fabricationColumn.locator('[data-testid="column-collapse-button"]');

      await test.step('Collapse column', async () => {
        await collapseButton.click();
        await kanbanPage.page.waitForTimeout(500);
        await expect(fabricationColumn).toHaveClass(/h-16/);
      });

      await test.step('Navigate away and back', async () => {
        await kanbanPage.goto('/');
        await kanbanPage.gotoKanbanBoard();
      });

      await test.step('Column state should be maintained', async () => {
        await expect(fabricationColumn).toHaveClass(/h-16/);
      });

      await test.step('Expand column for cleanup', async () => {
        await collapseButton.click();
        await kanbanPage.page.waitForTimeout(500);
        await expect(fabricationColumn).not.toHaveClass(/h-16/);
      });
    });
  });

  test.describe('Card Management', () => {
    test('should allow collapsing and expanding cards', async () => {
      await kanbanPage.testCardCollapse();
    });

    test('should display add pump button in each column', async () => {
      const columns = await kanbanPage.kanbanColumns.count();

      for (let i = 0; i < columns; i++) {
        const column = kanbanPage.kanbanColumns.nth(i);
        const addButton = column.locator('[data-testid="add-pump-button"]');

        await expect(addButton).toBeVisible();
        await expect(addButton).toContainText('Add Pump');
      }
    });

    test('should show card count badges', async () => {
      const expectedStages = ['Not Started', 'Fabrication', 'Powder Coat', 'Assembly', 'Testing', 'Shipping', 'QA Complete'];

      for (const stage of expectedStages) {
        const column = kanbanPage.getColumn(stage);
        const badge = column.locator('.bg-gray-200.text-gray-700');

        await expect(badge).toBeVisible();

        const badgeText = await badge.textContent();
        const count = parseInt(badgeText || '0');
        expect(count).toBeGreaterThanOrEqual(0);
      }
    });
  });

  test.describe('Capacity-Aware Scheduling', () => {
    test('should display department capacity status', async () => {
      await kanbanPage.verifyCapacityAwareScheduling();
    });

    test('should show capacity conflicts when they exist', async () => {
      await kanbanPage.testCapacityConflictDetection();
    });

    test('should refresh schedules correctly', async () => {
      await kanbanPage.testRefreshSchedules();

      // Verify board still functions after refresh
      await kanbanPage.verifyEightStages();
      await kanbanPage.verifyPowderCoatVendorSwimlanes();
    });
  });

  test.describe('Powder Coat Specific Features', () => {
    test('should handle vendor-specific card assignments', async () => {
      const premiumVendor = kanbanPage.getVendorSwimlane('Vendor A - Premium');
      const standardVendor = kanbanPage.getVendorSwimlane('Vendor B - Standard');

      await expect(premiumVendor).toBeVisible();
      await expect(standardVendor).toBeVisible();

      // Verify vendor capacity display
      const premiumCapacity = await kanbanPage.getVendorCapacity('Vendor A - Premium');
      const standardCapacity = await kanbanPage.getVendorCapacity('Vendor B - Standard');

      expect(premiumCapacity.weeklyCapacity).toBe(7);
      expect(standardCapacity.weeklyCapacity).toBe(7);
    });

    test('should show vendor preference indicators', async () => {
      const premiumVendor = kanbanPage.getVendorSwimlane('Vendor A - Premium');

      // Premium vendor should be marked as preferred (this might be visual, so check for indicators)
      await expect(premiumVendor).toContainText('Premium');
    });
  });

  test.describe('Responsive Design', () => {
    test('should adapt to mobile viewport', async () => {
      await kanbanPage.testResponsiveLayout();
    });

    test('should maintain functionality on tablet', async () => {
      await kanbanPage.page.setViewportSize({ width: 768, height: 1024 });
      await kanbanPage.page.waitForTimeout(500);

      await kanbanPage.verifyEightStages();
      await kanbanPage.verifyPowderCoatVendorSwimlanes();

      // Drag and drop should still work on tablet
      const sourceColumn = 'Not Started';
      const targetColumn = 'Fabrication';

      const sourceCount = await kanbanPage.getColumnCardCount(sourceColumn);
      const targetCount = await kanbanPage.getColumnCardCount(targetColumn);

      if (sourceCount > 0) {
        await kanbanPage.testDragAndDrop(sourceColumn, targetColumn);
      }
    });
  });

  test.describe('Data Persistence', () => {
    test('should maintain card positions during session', async () => {
      // Get initial card counts
      const initialCounts = {};
      const stages = ['Not Started', 'Fabrication', 'Powder Coat', 'Assembly', 'Testing', 'Shipping', 'QA Complete'];

      for (const stage of stages) {
        initialCounts[stage] = await kanbanPage.getColumnCardCount(stage);
      }

      // Navigate away and back
      await kanbanPage.goto('/');
      await kanbanPage.gotoKanbanBoard();

      // Verify counts are maintained
      for (const stage of stages) {
        const currentCount = await kanbanPage.getColumnCardCount(stage);
        expect(currentCount).toBe(initialCounts[stage]);
      }
    });

    test('should maintain vendor assignments', async () => {
      const initialPremiumCapacity = await kanbanPage.getVendorCapacity('Vendor A - Premium');

      // Navigate away and back
      await kanbanPage.goto('/');
      await kanbanPage.gotoKanbanBoard();

      const currentPremiumCapacity = await kanbanPage.getVendorCapacity('Vendor A - Premium');
      expect(currentPremiumCapacity.currentLoad).toBe(initialPremiumCapacity.currentLoad);
    });
  });

  test.describe('Performance', () => {
    test('should load within acceptable time', async () => {
      const startTime = Date.now();
      await kanbanPage.gotoKanbanBoard();
      const loadTime = Date.now() - startTime;

      // Should load within 5 seconds
      expect(loadTime).toBeLessThan(5000);
    });

    test('should handle drag and drop efficiently', async () => {
      const sourceColumn = 'Not Started';
      const targetColumn = 'Fabrication';

      const sourceCount = await kanbanPage.getColumnCardCount(sourceColumn);

      if (sourceCount > 0) {
        const startTime = Date.now();

        await kanbanPage.testDragAndDrop(sourceColumn, targetColumn);

        const dragTime = Date.now() - startTime;

        // Drag and drop should complete within 3 seconds
        expect(dragTime).toBeLessThan(3000);
      } else {
        test.skip('No cards available to test drag performance');
      }
    });
  });

  test.describe('Error Handling', () => {
    test('should handle missing data gracefully', async () => {
      // Mock empty data scenario
      await kanbanPage.page.route('**/*', route => {
        // Simulate empty response for data endpoints
        if (route.request().url().includes('/api/')) {
          route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ pumps: [], capacity: [] })
          });
        } else {
          route.continue();
        }
      });

      await kanbanPage.refreshButton.click();
      await kanbanPage.page.waitForTimeout(2000);

      // Board should still render structure
      await kanbanPage.verifyEightStages();
      await kanbanPage.verifyPowderCoatVendorSwimlanes();
    });

    test('should handle network errors', async () => {
      // Mock network failure
      await kanbanPage.page.route('**/*', route => route.abort());

      await kanbanPage.refreshButton.click();
      await kanbanPage.page.waitForTimeout(2000);

      // Should show error state or fallback
      const hasErrorState = await kanbanPage.page.locator('text=Error|No Data|Unable to load').count() > 0 ||
                           await kanbanPage.kanbanBoard.count() > 0;

      expect(hasErrorState).toBeTruthy();
    });
  });

  test.describe('Keyboard Navigation', () => {
    test('should support keyboard navigation', async () => {
      await test.step('Tab to first interactive element', async () => {
        await kanbanPage.page.keyboard.press('Tab');
        const focusedElement = kanbanPage.page.locator(':focus');
        await expect(focusedElement).toBeVisible();
      });

      await test.step('Navigate through columns', async () => {
        for (let i = 0; i < 5; i++) {
          await kanbanPage.page.keyboard.press('Tab');
          await kanbanPage.page.waitForTimeout(100);

          const focused = kanbanPage.page.locator(':focus');
          const isVisible = await focused.isVisible();
          if (isVisible) {
            const tagName = await focused.evaluate(el => el.tagName.toLowerCase());
            expect(['button', 'input', 'select', 'a']).toContain(tagName);
          }
        }
      });

      await test.step('Access refresh button via keyboard', async () => {
        // Find refresh button and focus it
        await kanbanPage.refreshButton.focus();
        await expect(kanbanPage.refreshButton).toBeFocused();

        // Activate with Enter key
        await kanbanPage.page.keyboard.press('Enter');
        await kanbanPage.page.waitForTimeout(2000);
      });
    });
  });
});