# Context Management Patterns for AI Assistants

## Core Principles

### 1. Serena-First Code Analysis
**Pattern**: Always use Serena tools before direct file operations
- `get_symbols_overview` - Understand file structure first
- `find_symbol` - Locate specific functions/classes
- `search_for_pattern` - Find code patterns across files
- `find_referencing_symbols` - Understand usage context

**When to break pattern**: Only for small configuration files or when Serena tools fail

### 2. Agent Delegation Decision Tree
**Always ask before coding**:
1. Is there an existing specialized agent for this task?
2. Could this task benefit from domain-specific expertise?
3. Is this a repetitive pattern that warrants a new agent?
4. Can this be done in parallel with other tasks?

**Delegation pattern**: Use Task tool immediately when answer is YES to any

### 3. Memory Checkpoint Schedule
**Auto-checkpoint triggers**:
- After completing any major task
- Before context window gets >50% full
- After making key architectural decisions
- When switching between different work areas
- Every 30 minutes of continuous work

**Checkpoint content format**:
```
### [Task Name] - COMPLETED
- Key findings: [brief summary]
- Decisions made: [list]
- Files modified: [list]
- Next steps: [if applicable]
```

### 4. Context Pruning Rules
**What to keep in active context**:
- Current task and immediate next steps
- Recently modified files (last 2-3)
- Active agent delegations and their results
- Current working directory and immediate context

**What to move to memory**:
- Completed tasks and their outcomes
- Background research and exploration
- Failed approaches and lessons learned
- Historical context not needed for current work

### 5. Parallel Execution Strategy
**Parallelization opportunities**:
- Multiple file analysis tasks
- Agent delegations for different aspects
- Research and implementation tasks
- Testing and documentation

**Pattern**: Single message with multiple tool calls whenever possible

## Implementation Commands

### Start New Task
1. Update memory with task description
2. Use Serena tools for code analysis
3. Check for agent delegation opportunities
4. Execute in parallel where possible

### Context Reset Required
1. Checkpoint current progress to memory
2. Clear unnecessary context from conversation
3. Load relevant context from memory if needed
4. Continue with focused approach

### Agent Creation Pattern
When repetitive patterns emerge:
1. Document the pattern in memory
2. Define agent scope and whenToUse criteria
3. Create agent definition using subagent-architect
4. Test agent with sample task
5. Add to delegation decision tree