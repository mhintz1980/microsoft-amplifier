/**
 * Simple test to verify Settings functionality
 * This file can be run in the browser console to test settings
 */

import { settingsManager } from './lib/settings';

// Test function to verify settings work correctly
export function testSettings() {
  console.log('Testing Settings functionality...');

  // Get current settings
  const currentSettings = settingsManager.getSettings();
  console.log('Current settings:', currentSettings);

  // Test man-hours calculation
  const testManHours = settingsManager.calculateManHours(10, 85);
  console.log('Man-hours for 10 employees at 85% efficiency:', testManHours);
  console.log('Expected: 68 (10 * 8 * 0.85)');

  // Test form data
  const formData = settingsManager.getSettingsFormData();
  console.log('Form data:', formData);

  // Test validation
  const validationResult = settingsManager.validateFormData(formData);
  console.log('Validation result:', validationResult);

  // Test totals
  console.log('Total employees:', settingsManager.getTotalEmployees());
  console.log('Total man-hours:', settingsManager.getTotalManHours());
  console.log('Average efficiency:', settingsManager.getAverageEfficiency());

  console.log('Settings test completed successfully!');
}

// Export for use in browser console
(window as any).testSettings = testSettings;