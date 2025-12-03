# E2E Testing Guide for PumpTracker Lite

This guide provides comprehensive documentation for running, writing, and maintaining end-to-end tests for the PumpTracker Lite application using Playwright.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- Application running at `http://localhost:5175`
- Dependencies installed (`npm install`)

### Running Tests

```bash
# Run all tests
npm run test:e2e

# Run tests with visible browser
npm run test:e2e:headed

# Run tests with Playwright Test Runner UI
npm run test:e2e:ui

# Run tests in debug mode
npm run test:e2e:debug

# Run specific browser tests
npm run test:e2e:chromium
npm run test:e2e:firefox
npm run test:e2e:webkit

# Run mobile tests
npm run test:e2e:mobile

# Run smoke tests only
npm run test:e2e:smoke

# Run with specific grep pattern
npm run test:e2e -- --grep "settings"

# Update visual snapshots
npm run test:e2e:update-snapshots
```

## 📁 Test Structure

```
tests/
├── dashboard/
│   └── dashboard.spec.ts        # Dashboard-specific tests
├── settings/
│   └── settings.spec.ts         # Settings modal tests
├── kanban/
│   └── kanban-board.spec.ts     # Kanban board tests
├── integration/
│   └── cross-feature.spec.ts    # Cross-feature integration tests
├── smoke/
│   └── smoke.spec.ts            # Critical path smoke tests
├── page-objects/
│   ├── BasePage.ts              # Base page object with common utilities
│   ├── DashboardPage.ts         # Dashboard page object
│   ├── SettingsModalPage.ts     # Settings modal page object
│   └── KanbanBoardPage.ts       # Kanban board page object
├── utils/
│   ├── test-data.ts             # Test data management
│   └── helpers.ts               # Test helper utilities
├── global-setup.ts              # Global test setup
├── global-teardown.ts           # Global test teardown
└── screenshots/                 # Generated screenshots (auto-created)
```

## 🎯 Test Categories

### 1. Dashboard Tests (`tests/dashboard/`)

**Coverage:**
- KPI card rendering and interaction
- Chart functionality (Late Orders, Value By Customer, Lead Time Trend, Department Tree Map)
- Category cycling functionality
- Favorites toggle
- Date range filtering
- Order details expansion
- Responsive design

**Example:**
```typescript
test('should display correct KPI metrics', async () => {
  const kpiValues = await dashboardPage.getKPIValues();
  expect(kpiValues.lateOrders).toBeGreaterThanOrEqual(0);
  expect(kpiValues.totalOrders).toBeGreaterThan(0);
});
```

### 2. Settings Modal Tests (`tests/settings/`)

**Coverage:**
- Modal open/close functionality
- Department settings display and modification
- Employee count and efficiency inputs
- Man-hours calculation verification
- Input validation
- Settings persistence
- Reset to defaults functionality

**Example:**
```typescript
test('should calculate man-hours correctly', async () => {
  await settingsPage.setEmployeeCount('Fabrication', 10);
  await settingsPage.setEfficiency('Fabrication', 85);
  await settingsPage.verifyManHoursCalculation('Fabrication');
  // 10 * 8 * 0.85 = 68 man-hours
});
```

### 3. Kanban Board Tests (`tests/kanban/`)

**Coverage:**
- 8-stage production pipeline display
- 3-vendor powder coat swimlanes
- Drag and drop functionality
- Column collapse/expand
- Card collapse/expand
- Capacity-aware scheduling
- Vendor assignment
- Refresh schedules functionality

**Example:**
```typescript
test('should display 3-vendor swimlanes for powder coat', async () => {
  await kanbanPage.verifyPowderCoatVendorSwimlanes();
  const vendorCapacity = await kanbanPage.getVendorCapacity('Vendor A - Premium');
  expect(vendorCapacity.weeklyCapacity).toBe(7);
});
```

### 4. Integration Tests (`tests/integration/`)

**Coverage:**
- Settings changes → Kanban timing integration
- Settings changes → Dashboard display integration
- Navigation and state persistence
- Data synchronization
- Error handling across features
- Performance integration
- Cross-browser consistency

**Example:**
```typescript
test('should update Kanban scheduling based on capacity settings', async () => {
  await settingsPage.setEmployeeCount('Fabrication', 15);
  await settingsPage.saveButton.click();

  const capacityStatus = await kanbanPage.getCapacityStatus();
  const fabricationDept = capacityStatus.find(d =>
    d.department.toLowerCase().includes('fabrication')
  );
  expect(fabricationDept.manHours).toBeCloseTo(108, 0); // 15 * 8 * 0.9
});
```

### 5. Smoke Tests (`tests/smoke/`)

**Coverage:**
- Core application loading
- Basic functionality verification
- Performance expectations
- Critical path testing
- Accessibility basics

**Usage:**
```bash
npm run test:e2e:smoke
```

## 🏗️ Page Object Model

### BasePage
Provides common utilities and methods for all pages:
- Navigation
- Element interactions
- Screenshot capture
- Accessibility checks
- Form validation helpers

### Specialized Page Objects
- **DashboardPage**: Dashboard-specific methods and locators
- **SettingsModalPage**: Settings modal interactions
- **KanbanBoardPage**: Kanban board functionality

### Example Usage:
```typescript
const dashboardPage = new DashboardPage(page);
await dashboardPage.gotoDashboard();
await dashboardPage.verifyKPICards();
await dashboardPage.testCategoryCycling();
```

## 📊 Test Data Management

### TestDataManager
Located in `tests/utils/test-data.ts`, provides:
- Default test data for departments, vendors, and pumps
- Data modification methods
- Reset functionality
- Centralized test data source

### Example:
```typescript
const testDataManager = TestDataManager.getInstance();
testDataManager.updateDepartment('FABRICATION', { employeeCount: 12 });
const data = testDataManager.getData();
```

## 🔧 Test Helpers

### TestHelpers Class
Located in `tests/utils/helpers.ts`, provides:
- Wait utilities
- Screenshot management
- Accessibility checks
- Form interactions
- Modal handling
- Drag and drop helpers

### Example:
```typescript
const helpers = new TestHelpers(page);
await helpers.waitForAppLoad();
await helpers.takeScreenshot('dashboard-loaded');
await helpers.checkAccessibility();
```

## 🎨 Visual Testing

### Screenshots
Screenshots are automatically captured:
- On test failure
- Manually via `takeScreenshot()`
- For visual regression testing

### Visual Regression Tests
Mark tests with `@visual` tag for visual regression:
```typescript
test('dashboard visual regression @visual', async () => {
  await dashboardPage.gotoDashboard();
  await expect(page).toHaveScreenshot('dashboard.png');
});
```

## 🚦 CI/CD Integration

### GitHub Actions
- **E2E Tests**: Full test suite across multiple browsers
- **Visual Regression**: Automated visual testing
- **Cross-browser**: Chrome, Firefox, Safari testing
- **Mobile**: Mobile viewport testing
- **Performance**: Performance regression testing

### Test Reports
- HTML reports with artifacts
- JUnit XML for CI integration
- JSON results for automation
- Coverage reports

### Environment Variables
- `BASE_URL`: Application base URL (default: http://localhost:5175)
- `CI`: CI mode flag for headless execution
- `UPDATE_SNAPSHOTS`: Visual snapshot update flag

## 🐛 Debugging Tests

### Playwright Inspector
```bash
npm run test:e2e:debug
# or
npx playwright test --debug
```

### Trace Viewer
```bash
npm run test:e2e:report
# or
npx playwright show-report
```

### Headed Mode
```bash
npm run test:e2e:headed
```

### Code Generation
```bash
npm run test:e2e:codegen
```

## 📋 Best Practices

### 1. Test Organization
- Use descriptive test names
- Group related tests with `describe`
- Use `test.step` for logical test divisions
- Add appropriate tags (`@smoke`, `@regression`, `@visual`)

### 2. Selectors
- Use data-testid attributes for test-specific elements
- Prefer semantic selectors over CSS classes
- Avoid brittle selectors that depend on DOM structure

### 3. Waits and Timing
- Use explicit waits over fixed timeouts
- Leverage Playwright's auto-waiting capabilities
- Handle loading states and animations

### 4. Data Management
- Use TestDataManager for consistent test data
- Clean up test data after tests
- Avoid dependencies between tests

### 5. Error Handling
- Test error scenarios and edge cases
- Verify graceful degradation
- Test network failures and invalid inputs

### 6. Performance
- Set reasonable timeouts
- Test with realistic data volumes
- Monitor test execution times

## 🔍 Test Coverage Areas

### Functional Coverage
- ✅ Dashboard KPI cards and charts
- ✅ Settings modal with capacity management
- ✅ Kanban board with drag-and-drop
- ✅ Powder coat vendor management
- ✅ Cross-feature integration
- ✅ Data persistence

### Non-Functional Coverage
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Accessibility compliance
- ✅ Performance benchmarks
- ✅ Error handling
- ✅ Cross-browser compatibility

### Integration Coverage
- ✅ Settings → Kanban timing integration
- ✅ Settings → Dashboard calculations
- ✅ Data synchronization across views
- ✅ Navigation and state persistence

## 📝 Writing New Tests

### 1. Create Test File
```typescript
import { test, expect } from '@playwright/test';
import { DashboardPage } from '../page-objects/DashboardPage';

test.describe('New Feature Tests', () => {
  test('should demonstrate new functionality', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    // Test implementation
  });
});
```

### 2. Use Page Objects
```typescript
const pageObject = new FeaturePage(page);
await pageObject.goto();
await pageObject.performAction();
await expect(pageObject.resultElement).toBeVisible();
```

### 3. Add Test Steps
```typescript
await test.step('Setup test conditions', async () => {
  // Setup code
});

await test.step('Execute main functionality', async () => {
  // Test code
});

await test.step('Verify results', async () => {
  // Assertions
});
```

### 4. Add Appropriate Tags
```typescript
test('new feature test @smoke @regression', async () => {
  // Test implementation
});
```

## 🚨 Troubleshooting

### Common Issues

1. **Tests Flaking**
   - Increase wait times for dynamic content
   - Use more specific selectors
   - Check for race conditions

2. **Timeout Failures**
   - Increase specific test timeouts
   - Verify application is running correctly
   - Check network conditions

3. **Element Not Found**
   - Verify selectors are correct
   - Check if element exists in current state
   - Use waitForElement() instead of direct access

4. **Visual Differences**
   - Update snapshots if changes are intentional
   - Check for font rendering differences
   - Verify consistent test environments

### Debug Commands
```bash
# Run specific test file
npx playwright test tests/dashboard/dashboard.spec.ts

# Run with specific line numbers
npx playwright test tests/dashboard/dashboard.spec.ts:15-25

# Run with trace
npx playwright test --trace on

# Generate HTML report
npx playwright test --reporter=html
```

## 📈 Performance Metrics

### Target Performance
- **Page Load**: < 3 seconds
- **Category Change**: < 2 seconds
- **Drag and Drop**: < 1 second
- **Modal Open**: < 500ms

### Monitoring
- Test execution times are tracked
- Performance regressions are flagged
- CI includes performance benchmarks

## 🔗 Additional Resources

- [Playwright Documentation](https://playwright.dev/)
- [Page Object Model Pattern](https://playwright.dev/docs/pom)
- [Test Best Practices](https://playwright.dev/docs/best-practices)
- [Debugging Tests](https://playwright.dev/docs/debug)
- [Visual Testing](https://playwright.dev/docs/test-snapshots)