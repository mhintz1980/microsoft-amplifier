import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Cleaning up Playwright test environment...');

  // Perform any global cleanup
  // Clear local storage, reset test data, etc.

  console.log('✅ Playwright test environment teardown complete');
}

export default globalTeardown;