# Amplifier Module Development Guide

## Module Structure Patterns

### Standard Module Organization
Each module follows the "bricks and studs" philosophy:
```
module_name/
├── __init__.py          # Public API exports
├── README.md           # Module purpose and contract
├── core.py             # Main implementation
├── models.py           # Data models (if needed)
├── cli.py              # Command-line interface (optional)
└── tests/              # Module tests
```

### Core Modules Analysis

#### 1. Memory System (`amplifier/memory/`)
**Purpose**: Persist and retrieve memories with JSON storage
**Key Classes**:
- `MemoryStore` (core.py) - Main storage with MAX_MEMORIES limit
- Memory models in models.py - Pydantic validation

**Contract**: Add, search, and retrieve memories
**Storage**: `.data/memory.json` with access tracking

#### 2. Knowledge Synthesis (`amplifier/knowledge_synthesis/`)
**Purpose**: Advanced knowledge processing and synthesis
**Key Classes**:
- `SynthesisEngine` (synthesis_engine.py) - Core synthesis logic
- Multiple extractors and processors

**Features**:
- Article processing
- Event handling
- Stream reading
- Tension detection
- Focused extraction

#### 3. CCSDK Toolkit (`amplifier/ccsdk_toolkit/`)
**Purpose**: Claude Code SDK integration toolkit
**Key Classes**:
- `ClaudeSession` (core/session.py) - AI session management
- `SessionError`, `SDKNotAvailableError` - Error handling

**Structure**:
- core/ - Session management and utilities
- defensive/ - LLM response handling utilities
- templates/ - Code generation templates
- config/ - Configuration management
- cli/ - Command-line tools

#### 4. Utils (`amplifier/utils/`)
**Purpose**: Shared utility functions
**Key Files**:
- `file_io.py` - File I/O with retry logic for cloud sync
- `token_utils.py` - Token counting utilities
- `logger.py` - Logging configuration
- `logging_utils.py` - Additional logging utilities

**Critical Functions** (file_io.py):
- `write_json_with_retry` / `read_json_with_retry`
- `write_text_with_retry` / `read_text_with_retry`
- `append_line_with_retry`
- `_handle_io_error` - Cloud sync error handling

## Development Patterns

### 1. Symbol Discovery
Use Serena tools to explore modules efficiently:
```bash
# Get overview of symbols in a file
mcp__serena__get_symbols_overview(relative_path="amplifier/module/core.py")

# Find specific symbols
mcp__serena__find_symbol(name_path="ClassName", relative_path="amplifier/module/")
```

### 2. File I/O Best Practices
Always use the centralized file I/O utilities:
```python
from amplifier.utils.file_io import write_json, read_json

# Instead of direct file operations
write_json(data, filepath)  # Handles retries automatically
```

### 3. Error Handling Patterns
- Use defensive utilities for LLM responses
- Implement retry logic with exponential backoff
- Provide clear error messages with context

### 4. Memory System Integration
```python
from amplifier.memory import MemoryStore, Memory

store = MemoryStore()
memory = Memory(
    content="User preference",
    category="preference", 
    metadata={"source": "conversation"}
)
stored = store.add_memory(memory)
```

## Module Creation Guidelines

### 1. Contract First
Always start with a clear README defining:
- Purpose and scope
- Public API (inputs/outputs)
- Dependencies and requirements
- Usage examples

### 2. Self-Contained Design
- All code, tests, and data within module directory
- No external dependencies beyond what's in pyproject.toml
- Clear separation between public and private APIs

### 3. Test Coverage
- Focus on behavior at contract level
- Integration tests at module level
- Use pytest framework

### 4. Documentation
- README.md for user-facing documentation
- Docstrings for all public APIs
- Type hints throughout

## Integration Points

### 1. Claude Code SDK
Use the ccsdk_toolkit for AI interactions:
```python
from amplifier.ccsdk_toolkit.core.session import ClaudeSession

session = ClaudeSession()
response = await session.generate_response(prompt)
```

### 2. Knowledge Base
Integrate with knowledge synthesis for content processing:
```python
from amplifier.knowledge_synthesis import SynthesisEngine

engine = SynthesisEngine()
results = await engine.process_content(content)
```

### 3. Memory Storage
Utilize the memory system for persistent storage:
```python
from amplifier.memory import MemoryStore

store = MemoryStore()
memories = store.search(query)
```

This guide serves as a reference for understanding existing modules and creating new ones that follow the established patterns.