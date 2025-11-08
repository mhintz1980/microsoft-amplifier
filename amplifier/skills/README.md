# Skills Framework

A minimal, token-efficient framework for context management and skill discovery.

## Philosophy

- **Ruthless simplicity**: Each skill does one thing well
- **Progressive disclosure**: Metadata → Summary → Full content
- **Token efficiency**: <1000 tokens per operation
- **Agent-optimized**: Designed for AI consumption

## Structure

```
amplifier/skills/
├── context-management/    # Context compression and retrieval
├── skills-framework/      # Core framework utilities
├── templates/            # Skill templates and patterns
└── discovery/            # Skill discovery and matching
```

## Usage

Skills are self-contained modules with standardized contracts:

1. **Skill Definition**: Clear purpose, inputs, outputs
2. **Progressive Loading**: Multiple detail levels
3. **Semantic Scoring**: Importance-based retrieval
4. **Memory Integration**: Learning and adaptation

## Integration

Skills integrate with Claude Code through standardized hooks and can be discovered automatically based on context needs.