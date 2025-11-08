# Skills Framework Guide

A minimal, token-efficient framework for context management and skill discovery.

## Core Philosophy

- **Ruthless Simplicity**: Each skill does one thing well
- **Progressive Disclosure**: Metadata → Summary → Full content
- **Token Efficiency**: <1000 tokens per operation
- **Agent-Optimized**: Designed for AI consumption

## Quick Start

```python
from amplifier.skills import (
    SkillContext,
    compress_conversation_context,
    find_and_execute_skill
)

# Compress conversation
messages = [{"role": "user", "content": "..."}]  # Your messages
result = compress_conversation_context(messages, level="summary")

print(f"Compressed: {result['compressed_content']}")
print(f"Tokens used: {result['tokens_used']}")
```

## Architecture

```
amplifier/skills/
├── context-management/     # Context compression skills
├── skills-framework/       # Base framework
├── discovery/             # Skill discovery and matching
└── templates/             # Integration utilities
```

## Creating Skills

```python
from amplifier.skills import BaseSkill, SkillContext, SkillLevel, SkillResult

class MySkill(BaseSkill):
    @property
    def description(self) -> str:
        return "Clear description of what this skill does"

    @property
    def tags(self) -> List[str]:
        return ["tag1", "tag2"]

    def can_handle(self, context: SkillContext) -> float:
        # Return confidence score (0.0 to 1.0)
        return 0.8 if "keyword" in context.query.lower() else 0.0

    def execute(self, context: SkillContext, level: SkillLevel) -> SkillResult:
        # Execute the skill and return structured result
        return SkillResult(
            skill_name=self.skill_name,
            level=level,
            content="Result content",
            tokens_used=100,
            execution_time=0.1
        )
```

## Progressive Context Loading

```python
from amplifier.skills.templates import progressive_context_loading

# Load context progressively
results = progressive_context_loading(messages, start_level="metadata")

# Access different levels
print(results["metadata"]["compressed_content"])  # <50 tokens
print(results["summary"]["compressed_content"])   # <200 tokens
print(results["full"]["compressed_content"])     # <2000 tokens
```

## Claude Code Integration

```python
from amplifier.skills.templates import (
    auto_context_management,
    suggest_context_strategy
)

# Automatic context management
result = auto_context_management(messages, available_tokens=5000)

# Get strategy recommendations
strategy = suggest_context_strategy(
    message_count=len(messages),
    token_budget=5000,
    has_code=True
)
```

## Performance Characteristics

- **Metadata Level**: <50 tokens, ~95% compression
- **Summary Level**: <200 tokens, ~80% compression
- **Full Level**: <2000 tokens, ~30% compression
- **Discovery**: <100 tokens for skill matching
- **Execution**: Typically <100ms per operation

## Best Practices

1. **Keep skills focused** - One clear responsibility
2. **Respect token limits** - Always validate token usage
3. **Use progressive levels** - Start with metadata, expand as needed
4. **Provide clear descriptions** - Essential for discovery
5. **Handle errors gracefully** - Return useful error information

## Memory Integration

Skills automatically track usage patterns and learn from context:
- Execution frequency tracking
- Semantic importance scoring
- Usage pattern optimization
- Context relevance learning