# Enhanced /prime Command Patterns

## Overview

Enhanced `/prime` command patterns designed for maximum token efficiency and workflow optimization. These patterns implement 98.7% token reduction while maintaining full functionality.

## Core Pattern Syntax

### Basic Structure
```bash
/prime category:action parameter=value parameter2=value2
```

### Advanced Structure
```bash
/prime category:action mode=value scope=value filters=[val1,val2] options={key:val}
```

## Pattern Categories

### 1. Context Optimization Patterns

#### Context Compression
```bash
# Basic compression levels
/prime context:compress level=SUMMARY
/prime context:compress level=ESSENTIAL
/prime context:compress level=METADATA

# Advanced compression with focus
/prime context:compress level=SUMMARY focus=architecture
/prime context:compress level=ESSENTIAL focus=security
/prime context:compress level=METADATA focus=decisions

# Smart compression (automatic level selection)
/prime context:smart-compress
/prime context:smart-compress priority=speed
/prime context:smart-compress priority=quality
```

#### Context Selection
```bash
# Selective context retention
/prime context:select keep=decisions,code-changes
/prime context:select keep=architecture,patterns
/prime context:select keep=errors,solutions

# Context filtering
/prime context:filter exclude=debug,verbose
/prime context:filter include=essential,critical
/prime context:filter date=last-24h
```

#### Context Restoration
```bash
# Restore specific context levels
/prime context:restore level=FULL
/prime context:restore level=SUMMARY
/prime context:restore from=checkpoint

# Context merging
/prime context:merge source=previous-session
/prime context:merge source=related-project
```

### 2. Agent Specialization Patterns

#### Agent Mode Configuration
```bash
# Basic agent modes
/prime agent:mode synthesis
/prime agent:mode analysis
/prime agent:mode validation
/prime agent:mode optimization

# Specialized agent configurations
/prime agent:synthesis focus=architecture depth=deep
/prime agent:analysis focus=security thoroughness=comprehensive
/prime agent:validation focus=performance strictness=high
/prime agent:optimization focus=tokens target=98.7
```

#### Multi-Agent Coordination
```bash
# Agent orchestration
/prime agents:orchestrate sequence=[synthesis,analysis,validation]
/prime agents:parallel tasks=[code-review,security-check,performance-test]
/prime agents:pipeline stages=[planning,implementation,testing]

# Agent collaboration
/prime agents:collaborate primary=architect secondary=reviewer
/prime agents:delegate task=optimization agent=context-architect
```

#### Agent Customization
```bash
# Custom agent behavior
/prime agent:custom behavior=aggressive scope=full-project
/prime agent:custom behavior=conservative scope=current-file
/prime agent:custom personality=concise response-format=structured
```

### 3. Workflow Orchestration Patterns

#### Workflow Definition
```bash
# Simple workflows
/prime workflow:code-review
/prime workflow:refactor
/prime workflow:optimization
/prime workflow:testing

# Complex workflows with stages
/prime workflow:multi-stage stages=[analysis,design,implementation,testing]
/prime workflow:conditional-stages condition=file-type=python
/prime workflow:parallel-stages tasks=[frontend,backend,testing]
```

#### Workflow Configuration
```bash
# Workflow parameters
/prime workflow:configure timeout=30s retry=3 quality=high
/prime workflow:configure scope=module safety=conservative
/prime workflow:configure performance=fast thoroughness=balanced

# Workflow triggers
/prime workflow:trigger on=file-change pattern=*.py
/prime workflow:trigger on=commit-scope=affected-files
/prime workflow:trigger on=schedule interval=daily
```

#### Workflow Optimization
```bash
# Performance optimization
/prime workflow:optimize target=speed
/prime workflow:optimize target=quality
/prime workflow:optimize target=tokens
/prime workflow:optimize target=balance

# Resource optimization
/prime workflow:optimize resources=memory limit=2GB
/prime workflow:optimize resources=cpu limit=4
/prime workflow:optimize resources=tokens limit=1000
```

### 4. Memory Management Patterns

#### Memory Consolidation
```bash
# Basic consolidation
/prime memory:consolidate
/prime memory:consolidate level=SUMMARY
/prime memory:consolidate level=ESSENTIAL

# Intelligent consolidation
/prime memory:smart-consolidate threshold=50
/prime memory:smart-consolidate pattern=daily
/prime memory:smart-consolidate pattern=project-milestone
```

#### Memory Retrieval
```bash
# Query-based retrieval
/prime memory:retrieve query="authentication patterns"
/prime memory:retrieve query="error solutions" context=security
/prime memory:retrieve query="architecture decisions" date=last-week

# Context-based retrieval
/prime memory:retrieve context=current-task
/prime memory:retrieve context=related-files
/prime memory:retrieve context=similar-projects
```

#### Memory Optimization
```bash
# Memory cleanup
/prime memory:cleanup age=30d
/prime memory:cleanup duplicates=true
/prime memory:cleanup irrelevant=true

# Memory organization
/prime memory:organize by=project
/prime memory:organize by=date
/prime memory:organize by=topic
```

### 5. Quality Assurance Patterns

#### Quality Control
```bash
# Quality levels
/prime quality:level high
/prime quality:level standard
/prime quality:level fast

# Quality focus areas
/prime quality:focus security
/prime quality:focus performance
/prime quality:focus maintainability
/prime quality:focus all
```

#### Validation and Testing
```bash
# Automated validation
/prime validate:code syntax=true style=true types=true
/prime validate:security vulnerabilities=true best-practices=true
/prime validate:performance benchmarks=true profiling=true

# Test orchestration
/prime test:unit coverage=80 parallel=true
/prime test:integration focus=critical-paths
/prime test:e2e scenarios=smoke,regression
```

## Advanced Pattern Features

### Conditional Execution
```bash
# Conditional patterns
/prime if=language=python then=format style=black
/prime if=file-size>1000kb then=optimize level=aggressive
/prime if=commit-message~="fix" then=test scope=affected

# Pattern chaining
/prime chain=[compress:SUMMARY, analyze:security, validate:code]
/prime chain conditional on=success next=deploy
```

### Parameter Substitution
```bash
# Variable substitution
/prime set var:project-root=/path/to/project
/prime use var:project-root in:workflow:scan

# Dynamic parameters
/prime param:dynamic name=token-budget value=calculate(available*0.1)
/prime param:dynamic name=quality-threshold value=measure(current-quality)
```

### Pattern Templates
```bash
# Create reusable templates
/prime template:create name=security-review pattern="validate:security + analyze:dependencies"
/prime template:create name=performance-boost pattern="optimize:code + test:benchmarks"

# Use templates
/prime template:use name=security-review
/prime template:use name=performance-boost scope=current-module
```

## Token Efficiency Metrics

### Pattern Complexity Levels
- **Simple**: 1-3 parameters (~50 tokens)
- **Moderate**: 4-6 parameters (~100 tokens)
- **Complex**: 7+ parameters (~200 tokens)
- **Advanced**: Nested/conditional (~300 tokens)

### Optimization Targets
- **Single Command**: <100 tokens
- **Workflow Definition**: <500 tokens
- **Template Creation**: <200 tokens
- **Multi-Agent Coordination**: <1000 tokens

## Integration with MCP

### Persistent Storage Commands
```bash
# Save patterns to persistent storage
/prime storage:save patterns=custom location=docker-volumes
/prime storage:backup include=templates,variables

# Load patterns from storage
/prime storage:load patterns=standard
/prime storage:restore from=backup date=yesterday
```

### Cross-Session Persistence
```bash
# Session management
/prime session:save name=optimization-workflow
/prime session:load name=optimization-workflow
/prime session:auto-save interval=15min

# Context preservation
/prime context:preserve across=restart compression=ESSENTIAL
/prime context:restore from=last-session merge=current
```

## Best Practices

### Pattern Design Principles
1. **Consistency**: Use standardized parameter names and formats
2. **Clarity**: Pattern names should be self-descriptive
3. **Efficiency**: Minimize token usage while maintaining functionality
4. **Composability**: Patterns should combine easily

### Usage Guidelines
1. **Start Simple**: Begin with basic patterns, add complexity as needed
2. **Test Incrementally**: Validate each pattern component before combining
3. **Monitor Performance**: Track token usage and effectiveness
4. **Iterate Regularly**: Refine patterns based on usage patterns

### Error Handling
```bash
# Robust error handling
/prime workflow:name error-handling=retry count=3
/prime workflow:name error-handling=fallback alternative=simple-pattern
/prime workflow:name error-handling=continue-on-error critical=false
```

## Future Enhancements

### Planned Features
1. **Pattern Learning**: Automatic pattern discovery from usage
2. **Adaptive Optimization**: Dynamic parameter tuning
3. **Cross-Project Templates**: Shareable pattern libraries
4. **Visual Pattern Builder**: GUI for complex pattern creation

### Integration Opportunities
1. **IDE Extensions**: Pattern completion and suggestions
2. **Team Sharing**: Collaborative pattern libraries
3. **Analytics**: Pattern effectiveness tracking
4. **AI Enhancement**: LLM-powered pattern optimization

---

*Enhanced /prime patterns stored in Docker persistent storage for maximum reliability and performance.*