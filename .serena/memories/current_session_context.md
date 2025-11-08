# Current Session Context Management

## Session Started: 2025-11-03

### Core Context Management Pattern
1. **Use Serena tools for code analysis** - Avoid reading entire files when possible
2. **Delegate to specialized agents** - Use Task tool for domain-specific work
3. **Checkpoint progress regularly** - Update this memory file after major milestones
4. **Keep context minimal** - Focus only on current task and immediate context

### Current Tasks
- [x] Set up context management system (COMPLETED)
- [ ] Establish sustainable patterns for long-running sessions

### Key Decisions Made
- Serena tools will be primary for code exploration vs direct file reads
- Memory system will serve as session state persistence
- Agent delegation pattern: identify specialized tasks and delegate immediately

### Available Specialized Agents (Key Ones for This Session)
- **zen-architect** - High-level system design and architecture
- **modular-builder** - Building modular, reusable components
- **bug-hunter** - Identifying and fixing bugs
- **integration-specialist** - System integration and API work
- **analysis-engine** - Deep code analysis and pattern detection
- **subagent-architect** - Creating new specialized agents
- **test-coverage** - Testing strategy and implementation
- **contract-spec-author** - Writing specifications and contracts

### Agent Delegations Used
- None yet - this is initial setup

### Working Patterns Established
1. **Before any code exploration**: Use Serena tools (get_symbols_overview, find_symbol, search_for_pattern)
2. **Before implementation**: Check if specialized agent exists for the task
3. **After major milestones**: Update this memory file with key findings and decisions
4. **Context pruning**: Focus only on current task, archive completed work to memory

### Session Sustainability Rules
- Never read entire codebases - use targeted searches
- Create new agents when repetitive patterns emerge
- Always ask: "Can this be delegated?" before starting work
- Use memory as external brain for persistent context

### Memory Files Created This Session
- `current_session_context` - Active session tracking
- `context_management_patterns` - Reference patterns for context management

### Last Updated: 2025-11-03 (Context management system established)