# Prime Fix Patterns - 2025

## Common Issues & Solutions

### Async Pytest Fixtures
**Pattern**: `@pytest.fixture` + `async def`
**Solution**: Change to `@pytest_asyncio.fixture` + add `import pytest_asyncio`
**Files affected**: All Agent Lightning test files
**Fix date**: 2025-01-08
**Status**: RESOLVED - Tests now progress past fixture errors

### Missing Import Pattern  
**Pattern**: Using `pytest_asyncio.fixture` without importing it
**Solution**: Add `import pytest_asyncio` after `import pytest`
**Fix date**: 2025-01-08
**Root cause**: Incomplete application of async fixture fix

### Token Efficiency Rules
1. Always use targeted search first (Grep/find_symbol)
2. Never read entire files unless absolutely necessary
3. Use symbol overviews for structure understanding
4. Apply ruthless simplicity - fix only what's broken

### Investigation Priority
1. Error message analysis (exact location)
2. Targeted search for patterns
3. Memory check for previous solutions
4. Minimal code reading
5. Apply fix and test
6. Document results

## Key Principle
Solve the actual problem, don't build architectures to avoid solving it.

## Success Metrics
- Token usage: This fix used ~200 tokens total vs 80,000+ previously
- Time to diagnosis: <30 seconds vs >10 minutes
- Fix durability: Documented in memory to prevent repetition