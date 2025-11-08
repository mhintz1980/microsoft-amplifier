---
description: Enhanced Claude Code status monitoring with context impact tracking and learning recommendations
category: monitoring
allowed-tools:
  - Bash
  - Read
  - mcp__serena__read_memory
  - mcp__serena__write_memory
---

# Enhanced Claude Status Display

Shows detailed context window usage, token efficiency metrics, and operation impact to help maintain optimal Claude Code performance and enable continuous learning.

## Usage

```bash
# Check current status and recent operation impact
/claude-status

# Continuous monitoring mode (updates every 30 seconds)
/claude-status --monitor

# Show impact of last operation only
/claude-status --impact
```

## What It Shows

### Context Window Status
- **Visual progress bar**: Percentage of context window used
- **Token count**: Exact tokens used/available
- **Efficiency status**: OPTIMAL/GOOD/WARNING/CRITICAL
- **Last operation impact**: Context change from previous command

### Performance & Learning Metrics
- **Operations per minute**: Work throughput
- **Runtime**: Session duration
- **Efficiency score**: 0-100 based on philosophy compliance
- **Learning recommendations**: When to stop and review for improvement

### Smart Recommendations
- **Context management**: When to compress or start new session
- **Token efficiency**: Reminders to use surgical investigation
- **Learning triggers**: Points for reflection and optimization
- **Philosophy compliance**: Review SUPERIOR_TACTICS.md when needed

### Operation Impact Analysis
- **Before/after context**: Change from last operation
- **Token efficiency rating**: How well the operation followed philosophy
- **Learning opportunity**: Suggestions for improvement

## Examples

```
📊 CONTEXT WINDOW STATUS:
   Usage: ███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 14.0%
   Tokens: 28,000 / 200,000
   Last operation: +2,000 tokens (EDIT operation)
   Status: GOOD

⚡ PERFORMANCE & LEARNING:
   Operations: 12 (4.8/min)
   Runtime: 150s
   Efficiency: 85/100
   Philosophy: GOOD

💡 LEARNING RECOMMENDATIONS:
   🎯 REFLECT: Last operation was efficient - pattern to repeat
   📈 TREND: Context usage increasing slowly - monitor pace
```

## Integration Workflow

### For Continuous Learning
1. **Run after major operations**: `/claude-status --impact`
2. **Check during complex tasks**: `/claude-status` every 5-10 operations
3. **Monitor during long sessions**: `/claude-status --monitor`
4. **Review at decision points**: Check before continuing with new approaches

### Learning Triggers
- **Context spikes > 10%**: Stop and review what caused inefficiency
- **Operations > 2000 tokens**: Consider surgical approach instead
- **Efficiency score drops**: Review SUPERIOR_TACTICS.md
- **Multiple similar failures**: Time for new approach

## Philosophy Alignment

This tool enables our core principles:
- **Token Efficiency**: Real-time feedback on context usage
- **Context Engineering**: Progressive compression recommendations
- **Ruthless Simplicity**: Identifies when operations become too complex
- **Continuous Learning**: Triggers reflection and improvement points