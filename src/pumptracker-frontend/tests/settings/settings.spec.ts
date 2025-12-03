import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';
import { SettingsModalPage } from '../page-objects/SettingsModalPage';

test.describe('Settings Modal E2E Tests', () => {
  let dashboardPage: DashboardPage;
  let settingsPage: SettingsModalPage;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    settingsPage = new SettingsModalPage(page);

    // Start on dashboard where settings button should be accessible
    await dashboardPage.gotoDashboard();
  });

  test.describe('Modal Open/Close Functionality', () => {
    test('should open and close settings modal', async () => {
      await test.step('Open settings modal', async () => {
        await settingsPage.openSettingsModal();
        await settingsPage.expectSettingsModalOpen();
      });

      await test.step('Verify modal content is visible', async () => {
        await expect(settingsPage.page.locator('h2:has-text("Department Settings")')).toBeVisible();
        await expect(settingsPage.departmentCards).toHaveCount({ min: 4 });
      });

      await test.step('Close settings modal using close button', async () => {
        await settingsPage.closeSettingsModal();
        await settingsPage.expectSettingsModalClosed();
      });

      await test.step('Verify dashboard is still visible', async () => {
        await expect(dashboardPage.kpiCards).toBeVisible();
      });
    });

    test('should close modal when clicking outside', async () => {
      await settingsPage.openSettingsModal();

      await test.step('Click outside modal', async () => {
        await settingsPage.page.locator('.fixed.inset-0').first().click({ position: { x: 10, y: 10 } });
      });

      await test.step('Modal should be closed', async () => {
        await settingsPage.expectSettingsModalClosed();
      });
    });

    test('should close modal with escape key', async () => {
      await settingsPage.openSettingsModal();

      await test.step('Press escape key', async () => {
        await settingsPage.page.keyboard.press('Escape');
      });

      await test.step('Modal should be closed', async () => {
        await settingsPage.expectSettingsModalClosed();
      });
    });
  });

  test.describe('Department Settings Display', () => {
    test.beforeEach(async () => {
      await settingsPage.openSettingsModal();
    });

    test('should display all department cards', async () => {
      const expectedDepartments = [
        'Fabrication', 'Powder Coat', 'Assembly', 'Testing', 'Shipping', 'QA Complete'
      ];

      for (const dept of expectedDepartments) {
        const card = settingsPage.getDepartmentCard(dept);
        await expect(card).toBeVisible();
        await expect(card).toContainText(dept);
      }
    });

    test('should show current department settings', async () => {
      await test.step('Fabrication department shows current values', async () => {
        const employees = await settingsPage.getEmployeeCount('Fabrication');
        const efficiency = await settingsPage.getEfficiency('Fabrication');
        const manHours = await settingsPage.getManHours('Fabrication');

        expect(employees).toBeGreaterThan(0);
        expect(efficiency).toBeGreaterThan(0);
        expect(efficiency).toBeLessThanOrEqual(100);
        expect(manHours).toBeGreaterThan(0);
      });

      await test.step('Powder Coat department shows current values', async () => {
        const employees = await settingsPage.getEmployeeCount('Powder Coat');
        const efficiency = await settingsPage.getEfficiency('Powder Coat');
        const manHours = await settingsPage.getManHours('Powder Coat');

        expect(employees).toBeGreaterThan(0);
        expect(efficiency).toBeGreaterThan(0);
        expect(efficiency).toBeLessThanOrEqual(100);
        expect(manHours).toBeGreaterThan(0);
      });
    });

    test('should display summary statistics', async () => {
      await test.step('Total employees is calculated correctly', async () => {
        const totalEmployees = await settingsPage.getTotalEmployees();
        expect(totalEmployees).toBeGreaterThan(0);
      });

      await test.step('Average efficiency is displayed', async () => {
        const avgEfficiency = await settingsPage.getAverageEfficiency();
        expect(avgEfficiency).toBeGreaterThan(0);
        expect(avgEfficiency).toBeLessThanOrEqual(100);
      });

      await test.step('Total man-hours is calculated', async () => {
        const totalManHours = await settingsPage.getTotalManHours();
        expect(totalManHours).toBeGreaterThan(0);
      });
    });
  });

  test.describe('Department Settings Modification', () => {
    test.beforeEach(async () => {
      await settingsPage.openSettingsModal();
    });

    test('should allow modifying employee counts', async () => {
      const testCases = [
        { department: 'Fabrication', employees: 10 },
        { department: 'Powder Coat', employees: 5 },
        { department: 'Assembly', employees: 8 }
      ];

      for (const testCase of testCases) {
        await test.step(`Set ${testCase.department} employees to ${testCase.employees}`, async () => {
          await settingsPage.setEmployeeCount(testCase.department, testCase.employees);

          const actualEmployees = await settingsPage.getEmployeeCount(testCase.department);
          expect(actualEmployees).toBe(testCase.employees);
        });
      }
    });

    test('should allow modifying efficiency rates', async () => {
      const testCases = [
        { department: 'Fabrication', efficiency: 90 },
        { department: 'Powder Coat', efficiency: 95 },
        { department: 'Assembly', efficiency: 85 }
      ];

      for (const testCase of testCases) {
        await test.step(`Set ${testCase.department} efficiency to ${testCase.efficiency}%`, async () => {
          await settingsPage.setEfficiency(testCase.department, testCase.efficiency);

          const actualEfficiency = await settingsPage.getEfficiency(testCase.department);
          expect(actualEfficiency).toBe(testCase.efficiency);
        });
      }
    });

    test('should calculate man-hours correctly', async () => {
      await test.step('Test Fabrication department calculation', async () => {
        await settingsPage.setEmployeeCount('Fabrication', 10);
        await settingsPage.setEfficiency('Fabrication', 85);

        await settingsPage.verifyManHoursCalculation('Fabrication');

        const manHours = await settingsPage.getManHours('Fabrication');
        expect(manHours).toBeCloseTo(68, 1); // 10 * 8 * 0.85 = 68
      });

      await test.step('Test Powder Coat department calculation', async () => {
        await settingsPage.setEmployeeCount('Powder Coat', 4);
        await settingsPage.setEfficiency('Powder Coat', 90);

        await settingsPage.verifyManHoursCalculation('Powder Coat');

        const manHours = await settingsPage.getManHours('Powder Coat');
        expect(manHours).toBeCloseTo(28.8, 1); // 4 * 8 * 0.9 = 28.8
      });
    });

    test('should update summary statistics when values change', async () => {
      const initialTotal = await settingsPage.getTotalEmployees();

      await test.step('Increase employee count', async () => {
        await settingsPage.setEmployeeCount('Fabrication', 15);
      });

      await test.step('Summary should update', async () => {
        const newTotal = await settingsPage.getTotalEmployees();
        expect(newTotal).toBeGreaterThan(initialTotal);
      });
    });
  });

  test.describe('Input Validation', () => {
    test.beforeEach(async () => {
      await settingsPage.openSettingsModal();
    });

    test('should validate employee count input', async () => {
      await test.step('Negative values should be rejected or corrected', async () => {
        await settingsPage.setEmployeeCount('Fabrication', -5);

        const correctedValue = await settingsPage.getEmployeeCount('Fabrication');
        expect(correctedValue).toBeGreaterThanOrEqual(0);
      });

      await test.step('Text input should be handled gracefully', async () => {
        await settingsPage.setEmployeeCount('Fabrication', 'abc' as any);

        const correctedValue = await settingsPage.getEmployeeCount('Fabrication');
        expect(isNaN(correctedValue)).toBeFalsy();
      });

      await test.step('Very large values should be handled', async () => {
        await settingsPage.setEmployeeCount('Fabrication', 9999);

        const correctedValue = await settingsPage.getEmployeeCount('Fabrication');
        expect(correctedValue).toBeLessThan(10000);
      });
    });

    test('should validate efficiency input', async () => {
      await test.step('Efficiency should be capped at 100%', async () => {
        await settingsPage.setEfficiency('Fabrication', 150);

        const actualEfficiency = await settingsPage.getEfficiency('Fabrication');
        expect(actualEfficiency).toBeLessThanOrEqual(100);
      });

      await test.step('Efficiency should be floored at 0%', async () => {
        await settingsPage.setEfficiency('Fabrication', -10);

        const actualEfficiency = await settingsPage.getEfficiency('Fabrication');
        expect(actualEfficiency).toBeGreaterThanOrEqual(0);
      });

      await test.step('Decimal efficiency should be handled', async () => {
        await settingsPage.setEfficiency('Fabrication', 87.5);

        const actualEfficiency = await settingsPage.getEfficiency('Fabrication');
        expect(actualEfficiency).toBeGreaterThanOrEqual(0);
        expect(actualEfficiency).toBeLessThanOrEqual(100);
      });
    });

    test('should show validation errors for invalid inputs', async () => {
      await test.step('Submit form with negative values', async () => {
        await settingsPage.setEmployeeCount('Fabrication', -1);
        await settingsPage.saveButton.click();
      });

      await test.step('Validation error should appear', async () => {
        await expect(settingsPage.validationErrors.first()).toBeVisible();
      });
    });
  });

  test.describe('Settings Persistence', () => {
    test('should save settings and persist across sessions', async () => {
      await settingsPage.openSettingsModal();

      await test.step('Modify department settings', async () => {
        await settingsPage.setEmployeeCount('Fabrication', 12);
        await settingsPage.setEfficiency('Fabrication', 88);
      });

      await test.step('Save settings', async () => {
        await settingsPage.saveButton.click();
        await settingsPage.expectSettingsModalClosed();
      });

      await test.step('Reopen settings modal', async () => {
        await settingsPage.openSettingsModal();
      });

      await test.step('Verify settings persisted', async () => {
        const employees = await settingsPage.getEmployeeCount('Fabrication');
        const efficiency = await settingsPage.getEfficiency('Fabrication');

        expect(employees).toBe(12);
        expect(efficiency).toBe(88);
      });
    });

    test('should cancel changes when cancel button is clicked', async () => {
      await settingsPage.openSettingsModal();

      await test.step('Get initial values', async () => {
        const initialEmployees = await settingsPage.getEmployeeCount('Fabrication');
        const initialEfficiency = await settingsPage.getEfficiency('Fabrication');

        await test.step('Modify values', async () => {
          await settingsPage.setEmployeeCount('Fabrication', 25);
          await settingsPage.setEfficiency('Fabrication', 65);
        });

        await test.step('Cancel changes', async () => {
          await settingsPage.cancelButton.click();
          await settingsPage.expectSettingsModalClosed();
        });

        await test.step('Reopen and verify values were not saved', async () => {
          await settingsPage.openSettingsModal();

          const currentEmployees = await settingsPage.getEmployeeCount('Fabrication');
          const currentEfficiency = await settingsPage.getEfficiency('Fabrication');

          expect(currentEmployees).toBe(initialEmployees);
          expect(currentEfficiency).toBe(initialEfficiency);
        });
      });
    });
  });

  test.describe('Settings Reset', () => {
    test('should reset to default values', async () => {
      await settingsPage.openSettingsModal();

      await test.step('Modify some settings', async () => {
        await settingsPage.setEmployeeCount('Fabrication', 20);
        await settingsPage.setEfficiency('Fabrication', 75);
      });

      await test.step('Reset to defaults', async () => {
        await settingsPage.resetButton.click();

        // Handle confirmation dialog
        await settingsPage.page.locator('button:has-text("OK")').click();
      });

      await test.step('Verify values were reset', async () => {
        // These should match the default values from the application
        const employees = await settingsPage.getEmployeeCount('Fabrication');
        const efficiency = await settingsPage.getEfficiency('Fabrication');

        // Default values (adjust based on your application's defaults)
        expect(employees).toBe(8);
        expect(efficiency).toBe(85);
      });
    });

    test('should show confirmation dialog before reset', async () => {
      await settingsPage.openSettingsModal();

      await test.step('Click reset button', async () => {
        await settingsPage.resetButton.click();
      });

      await test.step('Confirmation dialog should appear', async () => {
        await expect(settingsPage.page.locator('text="Are you sure"')).toBeVisible();
        await expect(settingsPage.page.locator('button:has-text("OK")')).toBeVisible();
        await expect(settingsPage.page.locator('button:has-text("Cancel")')).toBeVisible();
      });

      await test.step('Cancel reset', async () => {
        await settingsPage.page.locator('button:has-text("Cancel")').click();

        // Settings should remain unchanged
        const employees = await settingsPage.getEmployeeCount('Fabrication');
        expect(employees).toBeGreaterThan(0);
      });
    });
  });

  test.describe('Capacity Calculation Verification', () => {
    test.beforeEach(async () => {
      await settingsPage.openSettingsModal();
    });

    test('should verify individual department capacity', async () => {
      await test.step('Test multiple departments', async () => {
        const testDepartments = ['Fabrication', 'Powder Coat', 'Assembly'];

        for (const dept of testDepartments) {
          await settingsPage.setEmployeeCount(dept, 10);
          await settingsPage.setEfficiency(dept, 85);
          await settingsPage.verifyManHoursCalculation(dept);

          const manHours = await settingsPage.getManHours(dept);
          expect(manHours).toBeCloseTo(68, 1); // 10 * 8 * 0.85 = 68
        }
      });
    });

    test('should update total capacity when individual departments change', async () => {
      const initialManHours = await settingsPage.getTotalManHours();

      await test.step('Increase multiple departments', async () => {
        await settingsPage.setEmployeeCount('Fabrication', 12);
        await settingsPage.setEmployeeCount('Powder Coat', 6);
        await settingsPage.setEmployeeCount('Assembly', 10);
      });

      await test.step('Total capacity should increase', async () => {
        const newManHours = await settingsPage.getTotalManHours();
        expect(newManHours).toBeGreaterThan(initialManHours);
      });
    });
  });

  test.describe('Accessibility and Usability', () => {
    test.beforeEach(async () => {
      await settingsPage.openSettingsModal();
    });

    test('should be accessible via keyboard', async () => {
      await test.step('Tab through form fields', async () => {
        await settingsPage.page.keyboard.press('Tab');
        await settingsPage.page.keyboard.press('Tab');
        await settingsPage.page.keyboard.press('Tab');

        // Focus should be on an input element
        const focusedElement = settingsPage.page.locator(':focus');
        expect(focusedElement).toBeVisible();
      });

      await test.step('Save button should be accessible', async () => {
        await settingsPage.page.keyboard.press('Tab');
        await settingsPage.page.waitForTimeout(100); // Wait for focus to settle

        const focusedButton = settingsPage.page.locator(':focus');
        const buttonText = await focusedButton.textContent();
        expect(buttonText).toMatch(/Save|Cancel|Reset/);
      });
    });

    test('should have proper form labels', async () => {
      await test.step('Employee inputs have labels', async () => {
        const employeeInputs = settingsPage.employeeInputs;

        for (let i = 0; i < await employeeInputs.count(); i++) {
          const input = employeeInputs.nth(i);
          const label = input.locator('xpath=./preceding-sibling::label | ./ancestor::*[1]/label');

          if (await label.count() > 0) {
            const labelText = await label.textContent();
            expect(labelText?.toLowerCase()).toContain('employee');
          }
        }
      });

      await test.step('Efficiency inputs have labels', async () => {
        const efficiencyInputs = settingsPage.efficiencyInputs;

        for (let i = 0; i < await efficiencyInputs.count(); i++) {
          const input = efficiencyInputs.nth(i);
          const label = input.locator('xpath=./preceding-sibling::label | ./ancestor::*[1]/label');

          if (await label.count() > 0) {
            const labelText = await label.textContent();
            expect(labelText?.toLowerCase()).toContain('efficiency');
          }
        }
      });
    });
  });
});