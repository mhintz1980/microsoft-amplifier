# Superior Tactics for Claude Code Operations

## Core Principles

### 1. Token Efficiency First
- **Target**: <1000 tokens per operation
- **Method**: Surgical investigation over comprehensive analysis
- **Tools**: Grep → find_symbol → get_symbols_overview → Read (last resort)

### 2. Progressive Context Loading
```
Level 1: Error message analysis (free)
Level 2: Targeted search (10-50 tokens)
Level 3: Symbol overview (100-200 tokens)
Level 4: Selective reading (200-500 tokens)
Level 5: Full file analysis (1000+ tokens - AVOID)
```

### 3. Memory-Based Learning
- **Before fixing**: Check memory for similar patterns
- **After fixing**: Document solution in memory
- **Result**: Never fix the same problem twice

### 4. Ruthless Simplicity
- **Question**: "What's the smallest fix that works?"
- **Avoid**: Complex architectures for simple problems
- **Focus**: Actual problem, not hypothetical scenarios

## Investigation Protocol

### When Faced With Errors:
1. **Parse error message** → Extract exact location/pattern
2. **Targeted search** → Find all instances of pattern
3. **Memory check** → "Have we fixed this before?"
4. **Apply minimal fix** → Change only what's necessary
5. **Test single case** → Verify fix works
6. **Document in memory** → Prevent future repetition

### Example Workflow:
```python
# Instead of (80,000 tokens):
"Let me analyze the entire codebase to understand the test framework issues..."

# Use (300 tokens):
"Error shows 'async fixture' issue. Search for '@pytest.fixture.*async' pattern.
Found 4 files. Memory shows this is a common pattern - change to
'@pytest_asyncio.fixture'. Fix applied and tested."
```

## Tool Usage Hierarchy

### 1. Information Gathering (Preferred order):
- `Grep` - Pattern searching
- `find_symbol` - Symbol location
- `get_symbols_overview` - Structure understanding
- `Read` - Last resort, specific sections only

### 2. Problem Solving:
- `Edit` - Minimal, targeted changes
- `Bash` - Single command verification
- `TodoWrite` - Track only complex multi-step tasks

### 3. Learning:
- `mcp__serena__write_memory` - Document solutions
- `mcp__serena__read_memory` - Check past solutions

## Anti-Patterns to Avoid

### ❌ Comprehensive Analysis
- Reading entire files "to understand the context"
- Building complex architectures for simple fixes
- Using multiple agents for straightforward problems

### ❌ Token Waste
- Duplicating information already available
- Over-explaining simple concepts
- Running parallel operations when sequential would work

### ❌ Repeated Work
- Fixing the same issues multiple times
- Not learning from previous solutions
- Ignoring memory documentation

## Success Metrics

### Good Operations:
- Token count: <1000 per task
- Time to solution: <2 minutes
- Fix durability: No regression on next run
- Learning gain: Solution documented for future

### Bad Operations:
- Token count: >10,000 per task
- Time to solution: >10 minutes
- Repeated fixes: Same problem appears again
- No documentation: Lost knowledge

## Decision Framework

Before any operation, ask:
1. **What's the minimal information needed?**
2. **Have we solved this before?** (Check memory)
3. **What's the smallest change that works?**
4. **How can we document this for future?**

If any step suggests comprehensive analysis → **STOP** → Use surgical approach instead.

## Status Monitoring Protocol

### Enhanced Status Display
Use `/status` command to monitor:
- **Context window % usage**: Visual progress bar
- **Token efficiency**: Average tokens per operation
- **Performance metrics**: Operations per minute, efficiency score
- **Smart recommendations**: When to compress, speed up, or change tactics

### Status Commands
```bash
/status              # Show current status once
/status --monitor     # Continuous monitoring (30s updates)
```

### Performance Targets
- **Context usage**: <75% before considering compression
- **Tokens per operation**: <1000 (excellent), <5000 (good)
- **Efficiency score**: >80/100 for philosophy compliance
- **Operations per minute**: >2 for active sessions

### When to Check Status
- Before starting complex tasks
- After 5+ operations in a session
- When feeling "stuck" or slow progress
- Every 30 minutes in long sessions