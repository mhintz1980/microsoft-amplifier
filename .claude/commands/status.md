# Enhanced Claude Status Display

Shows detailed context window usage, token efficiency metrics, and performance recommendations to help maintain optimal Claude Code operations.

## Usage

```bash
# Show current status once
/status

# Continuous monitoring mode (updates every 30 seconds)
/status --monitor
```

## What It Shows

### Context Window Status
- **Visual progress bar**: Percentage of context window used
- **Token count**: Exact tokens used/available
- **Efficiency status**: OPTIMAL/GOOD/WARNING/CRITICAL
- **Average tokens per operation**: Trend analysis

### Performance Metrics
- **Operations per minute**: Work throughput
- **Runtime**: Session duration
- **Efficiency score**: 0-100 based on philosophy compliance
- **Philosophy compliance**: How well we're following token efficiency principles

### Smart Recommendations
- **Context management**: When to compress or start new session
- **Token efficiency**: Reminders to use surgical investigation
- **Performance**: Suggestions for faster operations
- **Philosophy**: Review SUPERIOR_TACTICS.md when needed

### Recent Operations
- Last 5 operations with token counts
- Color coding: Green (<1k), Yellow (1k-5k), Red (>5k tokens)

## Philosophy Alignment

This tool embodies our principles:
- **Token Efficiency**: Visual feedback helps maintain <1000 tokens per operation
- **Context Engineering**: Progressive compression recommendations
- **Ruthless Simplicity**: Clear, actionable insights without complexity
- **Present-Moment Focus**: Real-time awareness of resource usage

## Examples

```
📊 CONTEXT WINDOW STATUS:
   Usage: ████                    8.0%
   Tokens: 16,000 / 200,000
   Status: OPTIMAL
   Avg per op: 2,000 tokens

⚡ PERFORMANCE METRICS:
   Operations: 8 (4.2/min)
   Runtime: 115s
   Efficiency: 80/100
   Philosophy: GOOD

💡 RECOMMENDATIONS:
   📖 PHILOSOPHY: Review SUPERIOR_TACTICS.md for token efficiency
```