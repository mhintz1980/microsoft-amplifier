# Amplifier Project Overview

**Project Type**: AI Development Environment & Supercharged Workspace
**Primary Language**: Python 3.11+
**Key Framework**: Claude Code SDK integration
**Architecture**: Modular "bricks and studs" design

## Core Purpose
Amplifier is a coordinated development system that supercharges AI coding assistants with:
- 20+ specialized agents for different tasks
- Persistent knowledge that compounds over time
- Workflows that execute complex methodologies
- Parallel development capabilities

## Key Architectural Patterns

### 1. Modular Design Philosophy
- Each module is self-contained ("brick") with clear interfaces ("studs")
- Regeneratable from specifications without breaking dependencies
- Follows ruthless simplicity principle
- Clear contracts between modules

### 2. Project Structure
```
amplifier/
├── memory/              # Memory storage system (JSON-based)
├── extraction/          # AI-powered memory extraction from conversations
├── search/             # Semantic search capabilities
├── validation/         # Claim validation against stored memories
├── knowledge_synthesis/ # Advanced knowledge processing
├── ccsdk_toolkit/      # Claude Code SDK integration toolkit
├── utils/              # Utility functions (file I/O with retry logic)
└── config/             # Configuration management
```

### 3. Key Dependencies
- **Claude Code SDK**: Core AI integration (claude-code-sdk>=0.0.20)
- **AI/ML**: anthropic, openai, pydantic-ai, langchain
- **Data Processing**: pydantic, networkx, pyvis
- **Web**: aiohttp, httpx, beautifulsoup4, requests
- **Development**: pytest, ruff, pyright

## Critical Implementation Details

### File I/O with Retry Logic
Location: `amplifier/utils/file_io.py`
- Purpose: Handles cloud sync issues (OneDrive, Dropbox, etc.)
- Key functions: `write_json_with_retry`, `read_json_with_retry`
- Includes exponential backoff and cloud sync warnings

### Memory System Core
Location: `amplifier/memory/core.py`
- MemoryStore class with MAX_MEMORIES limit
- JSON-based storage in `.data/memory.json`
- Pydantic models for validation
- Access count tracking

### Claude Code SDK Integration
Location: `amplifier/ccsdk_toolkit/core/session.py`
- ClaudeSession class for AI interactions
- Error handling for SDK availability
- Session management utilities

## Development Workflow
1. **Installation**: `make install` (uses uv package manager)
2. **Testing**: `make test` or `make check` (format, lint, type-check)
3. **Knowledge Building**: `make knowledge-update`
4. **Parallel Development**: `make worktree feature-name`

## Important Files
- `pyproject.toml`: Dependencies and project configuration
- `CLAUDE.md`: Claude Code specific instructions
- `AGENTS.md`: Agent guidance and development patterns
- `DISCOVERIES.md`: Non-obvious problems and solutions discovered
- `amplifier/README.md`: Memory system architecture details

## Key Features
1. **Specialized Agents**: 20+ experts for different tasks (zen-architect, bug-hunter, etc.)
2. **Knowledge Extraction**: Transforms documentation into queryable knowledge
3. **Conversation Transcripts**: Automatic export/restore before compaction
4. **Parallel Worktrees**: Build multiple solutions simultaneously
5. **Modular Builder Lite**: One-command workflow from idea to module

## Development Philosophy
- Ruthless simplicity (KISS principle)
- Trust in emergence over control
- Present-moment focus (build for now, not hypothetical futures)
- Direct integration with minimal abstractions
- Fail fast and visibly during development

## Known Issues & Solutions
- **Cloud Sync I/O Errors**: Handled with retry logic in file_io.py
- **LLM Response Format Issues**: Defensive utilities in ccsdk_toolkit/defensive/
- **Tool Generation Pattern Failures**: Standard patterns enforced for reliability

This overview serves as the foundation for understanding the Amplifier project architecture and key implementation patterns.