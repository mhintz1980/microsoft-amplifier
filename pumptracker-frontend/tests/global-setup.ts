import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Setting up Playwright test environment...');

  // Set up test data or perform any global initialization
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Wait for the app to be ready
    await page.goto(config.webServer?.url || 'http://localhost:5175');

    // Wait for the app to load
    await page.waitForSelector('[data-testid="app-loaded"]', { timeout: 30000 });

    console.log('✅ Application is ready for testing');
  } catch (error) {
    console.log('⚠️  Application not immediately ready, tests will wait for it');
  } finally {
    await context.close();
    await browser.close();
  }

  console.log('✅ Playwright test environment setup complete');
}

export default globalSetup;