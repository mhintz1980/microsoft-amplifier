import { test, expect } from '@playwright/test';

test('Setup verification - application loads', async ({ page }) => {
  await page.goto('/');

  // Verify the page loads without errors
  await expect(page).toHaveTitle(/PumpTracker|React App/);

  // Look for key application elements
  const hasDashboard = await page.locator('[data-testid="dashboard"], h2:has-text("Dashboard")').count() > 0;
  const hasKanban = await page.locator('[data-testid="kanban-board"], h2:has-text("Production Board")').count() > 0;

  expect(hasDashboard || hasKanban).toBeTruthy();

  // Take a screenshot for verification
  await page.screenshot({ path: 'test-results/setup-verification.png', fullPage: true });
});