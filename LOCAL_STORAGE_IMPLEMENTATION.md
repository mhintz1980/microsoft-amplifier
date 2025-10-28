# PumpTracker Lite - Simplified Storage Implementation

This is the simplified storage implementation for PumpTracker Lite that replaces the over-engineered DataAdapter pattern with direct localStorage utilities.

## Key Changes

### ❌ Removed: Over-Engineered DataAdapter Pattern
- Complex adapter interface with multiple implementations
- Unnecessary abstraction layers
- Complex state management for data persistence

### ✅ Added: Simple localStorage Utilities
- Direct, straightforward functions for each data type
- Robust error handling with detailed error messages
- Built-in retry logic and quota management
- Simple API that's easy to understand and maintain

## Architecture

### Direct Storage Functions

Instead of going through a complex adapter interface, components now use direct functions:

```typescript
// Before (DataAdapter pattern)
const data = await dataAdapter.load();
await dataAdapter.upsertPumps(pumps);
await dataAdapter.addPumpEvent(event);

// After (Direct functions)
const pumps = localStorageUtils.pumps.load();
localStorageUtils.pumps.save(pumps);
localStorageUtils.pumpEvents.add(event);
```

### Available Functions

#### General Storage
- `storage.loadData()` - Load all stored data
- `storage.saveData(data)` - Save all data
- `storage.loadModels()` - Load models from JSON
- `storage.clearData()` - Clear all data
- `storage.isAvailable()` - Check localStorage availability

#### Pump Operations
- `pumps.save(pumps)` - Save pumps array
- `pumps.load()` - Load pumps array
- `pumps.add(pump)` - Add single pump
- `pumps.update(id, updates)` - Update pump by ID
- `pumps.delete(id)` - Delete pump by ID

#### Purchase Order Operations
- `purchaseOrders.save(orders)` - Save orders array
- `purchaseOrders.load()` - Load orders array
- `purchaseOrders.add(order)` - Add single order
- `purchaseOrders.update(id, updates)` - Update order by ID
- `purchaseOrders.delete(id)` - Delete order by ID

#### Purchase Order Line Operations
- `purchaseOrderLines.save(lines)` - Save lines array
- `purchaseOrderLines.load()` - Load lines array
- `purchaseOrderLines.add(line)` - Add single line
- `purchaseOrderLines.update(id, updates)` - Update line by ID
- `purchaseOrderLines.delete(id)` - Delete line by ID

#### Pump Event Operations
- `pumpEvents.save(events)` - Save events array
- `pumpEvents.load()` - Load events array
- `pumpEvents.add(event)` - Add single event
- `pumpEvents.delete(id)` - Delete event by ID

## Error Handling

The implementation includes robust error handling:

1. **StorageError Class** - Custom error class with detailed messages
2. **Quota Management** - Handles localStorage quota exceeded errors
3. **Validation** - Validates data structure on load
4. **Fallbacks** - Caches models and provides fallbacks when network fails

## Example Usage

```typescript
import { localStorageUtils } from './lib/storage';
import { useStore } from './store';

// In a component:
function AddPumpButton() {
  const addPump = useStore((state) => state.addPump);

  const handleAdd = () => {
    addPump({
      po_id: 'PO-001',
      customer: 'Test Customer',
      model_id: 'DD-4S',
      stage: Stage.NOT_STARTED,
      priority: Priority.NORMAL,
      // ... other fields
    });
    // Automatically saves to localStorage!
  };

  return <button onClick={handleAdd}>Add Pump</button>;
}
```

## Data Structure

All data is stored in a single localStorage key with the following structure:

```typescript
{
  schemaVersion: "2.0.0",
  lastSavedAt: "2024-01-01T00:00:00.000Z",
  orgId: "default-org",
  purchaseOrders: PurchaseOrder[],
  purchaseOrderLines: PurchaseOrderLine[],
  pumps: Pump[],
  pumpEvents: PumpEvent[]
}
```

## Testing

Run the test file to verify functionality:

```typescript
import { testStorage } from './test-storage';

// Run tests in development
testStorage();
```

## Benefits

1. **Simplicity** - Easy to understand and maintain
2. **Performance** - No unnecessary abstraction layers
3. **Reliability** - Robust error handling and validation
4. **Type Safety** - Full TypeScript support
5. **Developer Experience** - Clear, predictable API

## Migration from DataAdapter

If migrating from the DataAdapter pattern:

1. Replace `dataAdapter.load()` calls with specific type loaders
2. Replace `dataAdapter.upsertX()` calls with direct save functions
3. Replace `dataAdapter.addX()` calls with direct add functions
4. Remove adapter interface and implementations
5. Update imports to use `localStorageUtils`

The new implementation maintains the same external interface for components while simplifying the internal implementation significantly.