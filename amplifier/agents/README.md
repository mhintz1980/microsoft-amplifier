# Dynamic Agent Loading Framework

A progressive agent discovery and on-demand loading system that minimizes context usage while maintaining fast access to specialized agents.

## Overview

The framework implements the progressive agent discovery pattern from the techniques registry:

- **96% memory reduction**: Load only metadata (5,632 tokens) instead of full definitions (136,709 tokens)
- **On-demand loading**: Load full agent definitions only when needed
- **Tag-based discovery**: Find agents by capabilities and expertise
- **Context management**: Automatic unloading to manage memory efficiently
- **Task tool integration**: Seamless integration with existing workflows

## Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Agent Registry    │    │   Dynamic Loader     │    │  Task Integration   │
│                     │    │                      │    │                     │
│ • 33 agents         │◄──►│ • Metadata cache      │◄──►│ • Smart discovery    │
│ • 5,632 metadata    │    │ • On-demand loading   │    │ • Agent resolution   │
│ • 136,709 tokens    │    │ • Context management  │    │ • Alternative agents │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
          │                           │                           │
          ▼                           ▼                           ▼
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│  agent_registry.json│    │  .claude/agents/     │    │   Task Tool         │
│                     │    │                      │    │                     │
│ • Lightweight cache │    │ • zen-architect.md   │    │ • Automatic agent   │
│ • Tag distribution  │    │ • security-guard.md  │    │   selection         │
│ • Usage statistics  │    │ • *.md/*.json files   │    │ • Content loading   │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

## Quick Start

### Basic Usage

```python
from amplifier.agents import find_agents_by_tags, load_agent

# Find architecture agents
agents = find_agents_by_tags(['architecture'])
print(f"Found {len(agents)} architecture agents")

# Load a specific agent
result = load_agent('zen-architect')
if result.success:
    print(f"Loaded agent with {len(result.content)} characters")
```

### Task Integration

```python
from amplifier.agents import resolve_agent_for_task, get_agent_content

# Automatically find the best agent for a task
agent_id = resolve_agent_for_task(
    "Design a modular authentication system",
    required_tags=['architecture'],
    preferred_tags=['security']
)

if agent_id:
    # Get the agent's content for Task tool
    content = get_agent_content(agent_id)
```

### Building Registry

```bash
# Build agent registry with statistics
python3 amplifier/agents/build_registry.py --stats

# Force rebuild registry
python3 amplifier/agents/build_registry.py --force
```

## Features

### 1. Progressive Discovery

Load only essential metadata first, then full definitions on-demand:

```python
# Metadata loaded instantly (5,632 tokens total)
agents = find_agents_by_tags(['security'])  # Returns in <1ms

# Full content loaded only when needed
result = load_agent('security-guardian')   # 4,831 tokens loaded
```

### 2. Tag-Based Discovery

Find agents by capabilities using intelligent tagging:

```python
# Find agents with specific capabilities
security_agents = find_agents_by_tags(['security'])
architects = find_agents_by_tags(['architecture', 'design'])

# Require all tags vs any tag
specialized = find_agents_by_tags(['security', 'analysis'], require_all=True)
```

### 3. Intelligent Agent Resolution

Automatically select the best agent for any task:

```python
from amplifier.agents import resolve_agent_for_task

# Smart agent selection based on task description
agent_id = resolve_agent_for_task(
    "Optimize database performance",
    required_tags=['optimization'],
    preferred_tags=['database']
)

# Get alternative suggestions
from amplifier.agents import get_task_resolver
resolver = get_task_resolver()
alternatives = resolver.suggest_alternatives(
    "Optimize database performance",
    excluded_agent_id=agent_id
)
```

### 4. Context Management

Automatic memory management with configurable limits:

```python
from amplifier.agents import get_agent_loader

loader = get_agent_loader()
print(f"Loaded agents: {len(loader.loaded_agents)}/{loader.max_loaded_agents}")

# Manual unloading
loader.unload_agent('zen-architect')

# Statistics
stats = loader.get_registry_stats()
print(f"Memory efficiency: {stats['memory_efficiency']:.1f}%")
```

## Performance

### Memory Efficiency

- **96% reduction**: 5,632 tokens metadata vs 136,709 tokens full definitions
- **On-demand loading**: Only load agents when actually used
- **Context management**: Automatic unloading of least recently used agents

### Speed

- **Discovery**: <1ms for tag-based searches
- **Loading**: <1ms for agent content loading
- **Throughput**: 150M+ characters per second loading rate

### Scalability

- **33 agents** currently supported
- **Configurable capacity**: Default 10 concurrent loaded agents
- **Progressive loading**: Scales to hundreds of agents

## Agent Registry

The registry stores lightweight metadata for all agents:

```json
{
  "version": "1.0.0",
  "total_agents": 33,
  "agents": [
    {
      "identifier": "zen-architect",
      "name": "Zen Architect",
      "description": "Master designer for code planning...",
      "tags": ["architecture", "development", "analysis"],
      "when_to_use": "Use for architecture design tasks...",
      "file_path": ".claude/agents/zen-architect.md",
      "file_type": "md",
      "size_tokens": 5276,
      "load_count": 0
    }
  ]
}
```

### Tag Distribution

Current tag distribution across agents:

- **architecture**: 33 agents
- **integration**: 32 agents
- **optimization**: 32 agents
- **testing**: 32 agents
- **cleanup**: 31 agents
- **development**: 31 agents
- **security**: 31 agents
- **analysis**: 30 agents
- **specialist**: 28 agents

## Testing

Run the comprehensive test suite:

```bash
# Test all functionality
python3 amplifier/agents/test_dynamic_loading.py

# Expected output:
# 🎉 All tests passed! Dynamic agent loading is working correctly.
```

Test coverage includes:
- ✅ Registry building and metadata extraction
- ✅ Tag-based discovery and search
- ✅ On-demand loading and context management
- ✅ Task tool integration
- ✅ Performance metrics
- ✅ Error handling and edge cases

## Integration with Task Tool

The framework integrates seamlessly with the existing Task tool workflow:

### Manual Agent Specification

```python
# Use specific agent
agent_id = resolve_agent_for_task(
    "My task description",
    manual_agent_id='zen-architect'
)
```

### Automatic Agent Discovery

```python
# Let system find best agent
agent_id = resolve_agent_for_task(
    "Design a secure authentication system",
    required_tags=['security', 'architecture']
)
```

### Alternative Agents

Get suggestions when the primary agent isn't suitable:

```python
resolver = get_task_resolver()
alternatives = resolver.suggest_alternatives(
    "Design a secure authentication system",
    excluded_agent_id='previous-agent-id'
)
```

## Configuration

### Environment Variables

```bash
# Optional: Custom agents directory
export AMPLIFIER_AGENTS_DIR="/path/to/agents"

# Optional: Registry location
export AMPLIFIER_REGISTRY_PATH="/path/to/registry.json"
```

### Runtime Configuration

```python
from amplifier.agents import DynamicAgentLoader

# Custom configuration
loader = DynamicAgentLoader(
    agents_dir=".claude/agents",
    registry_file="custom_registry.json"
)

# Adjust context management
loader.max_loaded_agents = 20  # Default: 10
```

## File Structure

```
amplifier/agents/
├── __init__.py              # Public API and exports
├── dynamic_loader.py        # Core loading framework
├── task_integration.py      # Task tool integration
├── build_registry.py        # Registry building script
├── test_dynamic_loading.py  # Comprehensive test suite
├── agent_registry.json      # Lightweight metadata cache
└── README.md               # This documentation
```

## API Reference

### Core Functions

#### `find_agents_by_tags(tags, require_all=False)`
Find agents by capability tags.

**Parameters:**
- `tags`: List of tags to search for
- `require_all`: If True, agent must have ALL tags

**Returns:**
- List of `AgentMetadata` objects

#### `find_agents_by_description(query)`
Find agents by searching descriptions.

**Parameters:**
- `query`: Search query string

**Returns:**
- List of matching `AgentMetadata` objects

#### `load_agent(agent_id)`
Load full agent definition.

**Parameters:**
- `agent_id`: Agent identifier

**Returns:**
- `AgentLoadResult` with content or error

#### `resolve_agent_for_task(description, required_tags=None, preferred_tags=None, manual_agent_id=None)`
Intelligently select agent for task.

**Parameters:**
- `description`: Task description
- `required_tags`: Must-have tags
- `preferred_tags`: Nice-to-have tags
- `manual_agent_id`: Override with specific agent

**Returns:**
- Agent identifier string or None

### Data Classes

#### `AgentMetadata`
Lightweight agent information:
- `identifier`: Unique agent ID
- `name`: Human-readable name
- `description`: Agent description
- `tags`: Capability tags
- `when_to_use`: Usage guidance
- `file_path`: Path to agent file
- `file_type`: 'md' or 'json'
- `size_tokens`: Estimated token count
- `last_loaded`: Last load timestamp
- `load_count`: Usage frequency

#### `AgentLoadResult`
Result of loading operation:
- `success`: Loading succeeded
- `agent_id`: Agent identifier
- `content`: Full agent content (if successful)
- `error`: Error message (if failed)
- `load_time`: Loading duration in seconds

## Troubleshooting

### Registry Not Found

If you get "No agents found" errors:

```bash
# Rebuild registry
python3 amplifier/agents/build_registry.py --force
```

### Agent Loading Failed

Check agent file format and accessibility:

```python
from amplifier.agents import load_agent
result = load_agent('agent-id')
if not result.success:
    print(f"Error: {result.error}")
```

### Performance Issues

Monitor memory usage and loading statistics:

```python
from amplifier.agents import get_agent_loader
loader = get_agent_loader()
stats = loader.get_registry_stats()
print(f"Loaded agents: {stats['loaded_agents']}")
print(f"Memory efficiency: {stats['memory_efficiency']:.1f}%")
```

## Contributing

### Adding New Agents

1. Create agent file in `.claude/agents/`
2. Use descriptive frontmatter with tags
3. Rebuild registry: `python3 amplifier/agents/build_registry.py --force`

### Agent File Format

#### Markdown (.md)
```yaml
---
name: my-specialist
description: Use this agent for...
---
You are a specialist agent...
```

#### JSON (.json)
```json
{
  "identifier": "my-specialist",
  "whenToUse": "Use this agent for...",
  "systemPrompt": "You are a specialist agent..."
}
```

### Testing Changes

```bash
# Run test suite
python3 amplifier/agents/test_dynamic_loading.py

# Run specific tests
python3 -m pytest tests/test_agents.py -v
```

## License

This framework is part of the Microsoft Amplifier project.