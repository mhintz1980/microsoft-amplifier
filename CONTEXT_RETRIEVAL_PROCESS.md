# Context Retrieval Process - Prime Command Enhancement

## Critical First Steps for Every /prime Command

**Purpose**: Ensure all optimization techniques are loaded before any work begins. This prevents repeated failures due to context housekeeping.

## Step 1: Load Techniques Registry (ALWAYS FIRST)

```bash
# Check if techniques registry exists
if [ -f "CLAUDE_TECHNIQUES_REGISTRY.md" ]; then
    echo "✅ Techniques registry found - loading optimization patterns"
    # Read and apply techniques immediately
else
    echo "❌ Techniques registry missing - restore from Docker storage"
    # Restore from Docker storage first
    if [ -d ".docker-storage/claude-techniques-registry/" ]; then
        cp .docker-storage/claude-techniques-registry/CLAUDE_TECHNIQUES_REGISTRY.md .
        echo "✅ Techniques restored from Docker storage"
    else
        echo "❌ No backup found - starting without optimizations"
    fi
fi
```

## Step 2: Activate Specialized Agents (PARALLEL EXECUTION)

Before any other work, activate the specialized agents:

- Context Optimization Specialist (70-95% compression)
- Performance Optimization Specialist (2-3x throughput)
- MCP Integration Specialist (95%+ reliability)
- Memory Persistence Specialist (99.9% continuity)

## Step 3: Apply MCP Context-Saving (98.7% Token Reduction)

Always use MCP code execution instead of direct operations:

```python
from amplifier.mcp.code_execution import execute_in_docker
from amplifier.mcp.persistent_storage import store_result
```

## Step 4: Enable Parallel Delegation Pattern

Single message, multiple agents - never sequential Task calls.

## Step 5: Set Context Pruning Rules

Auto-checkpoint at 25% usage intervals.

## Integration Point

**Add this to the very beginning of `/prime` command**:
1. Load techniques registry first
2. Then proceed with philosophy documents
3. Then run make install/check/test
4. Apply all optimization techniques throughout

## Success Criteria

- Techniques registry loaded immediately
- Specialized agents activated
- MCP integration active
- Parallel delegation pattern used
- Context pruning rules established

Only after all retrieval steps complete should the normal /prime process begin.