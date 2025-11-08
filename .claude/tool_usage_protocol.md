# Tool Usage Protocol for Claude Code

## Prime Command Optimization Workflow

### Before ANY Manual Work:
1. **STOP** - Ask: "Which specialized agent handles this?"
2. **MEMORY** - Check episodic memory for similar solutions
3. **DELEGATE** - Launch appropriate sub-agent(s)
4. **PARALLEL** - Use single message with multiple agent calls

### Tool Selection Priority:
1. **Specialized Agents** → Always first choice
2. **Serena** → For code exploration and analysis
3. **Episodic Memory** → For pattern recognition
4. **Docker Architect** → For containerization issues
5. **Manual Execution** → Only when no agent available

### Agent Delegation Triggers:
- **Code Quality Issues** → bug-hunter agent
- **Missing Infrastructure** → modular-builder agent
- **Test Problems** → test-coverage agent
- **Dependency Issues** → integration-specialist agent
- **Architecture Decisions** → zen-architect agent
- **Performance Issues** → performance-optimizer agent
- **Code Exploration** → serena agent
- **Memory Retrieval** → episodic-memory agent

### Prime Command Specific Protocol:
1. Launch prime-orchestrator agent immediately
2. Let it coordinate all tool usage
3. Focus on results, not process
4. Store learnings for next session

### Self-Correction Questions:
- Am I doing work manually that an agent could do better?
- Have I checked episodic memory for solutions?
- Am I using parallel execution effectively?
- Is Serena better suited for this code analysis?
- Should Docker be involved in this testing?

## Remember:
You are the **orchestrator**, not the **worker**. Your value is in coordinating specialized tools effectively.