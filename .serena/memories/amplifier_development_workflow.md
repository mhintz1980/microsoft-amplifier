# Amplifier Development Workflow Guide

## Environment Setup

### Prerequisites
- Python 3.11+
- uv (Python package manager)
- Node.js & pnpm
- Git
- Claude Code CLI

### Installation Commands
```bash
# Clone and setup
git clone https://github.com/microsoft/amplifier.git
cd amplifier

# Install dependencies
make install

# Activate environment
source .venv/bin/activate  # Linux/Mac/WSL
```

## Development Commands

### Basic Operations
```bash
make check            # Format, lint, type-check
make test             # Run all tests
make pytest          # Run pytest specifically
make install          # Install/update dependencies
make lock-upgrade     # Upgrade dependency lock
```

### Knowledge Management
```bash
make knowledge-update    # Extract concepts from documentation
make knowledge-query Q="query"  # Search knowledge base
make knowledge-graph-viz # Visualize knowledge connections
```

### Transcript Management
```bash
make transcript-list           # List available transcripts
make transcript-search TERM="term"  # Search conversations
make transcript-restore        # Restore full conversation history
```

### Parallel Development
```bash
make worktree feature-name     # Create isolated worktree
make worktree-list            # List all worktrees
make worktree-rm feature-name # Remove worktree
```

## Code Quality Standards

### 1. Type Checking
- Use Python type hints consistently
- Configure in pyproject.toml [tool.pyright]
- Basic mode with missing imports ignored
- Exclude patterns defined in configuration

### 2. Code Formatting
- Use ruff for formatting and linting
- Line length: 120 characters
- All files must end with newline character
- VSCode configured to format on save

### 3. Testing Strategy
- pytest framework with asyncio support
- Coverage testing available
- Integration tests prioritized over unit tests
- Test files: `test_*.py` in tests/ directory

### 4. Documentation Standards
- README.md in each module for contracts
- Docstrings for all public APIs
- Type hints throughout codebase
- Clear separation of concerns

## Specialized Agents Usage

### Core Development Agents
- **zen-architect**: Design with ruthless simplicity
- **modular-builder**: Build following modular principles  
- **bug-hunter**: Systematic debugging
- **test-coverage**: Comprehensive testing
- **api-contract-designer**: Clean API design

### Analysis & Optimization Agents
- **security-guardian**: Security analysis
- **performance-optimizer**: Performance profiling
- **database-architect**: Database design and optimization
- **integration-specialist**: External service integration

### Knowledge & Insight Agents
- **insight-synthesizer**: Find hidden connections
- **knowledge-archaeologist**: Trace idea evolution
- **concept-extractor**: Extract knowledge from documents
- **ambiguity-guardian**: Preserve productive contradictions

## AI Development Patterns

### 1. Prompt Engineering
- Use system context from ai_context/ directory
- Follow "analyze first, don't code" pattern for complex tasks
- Implement incremental processing with continuous saves
- Use defensive utilities for LLM response handling

### 2. Error Handling
- Implement graceful degradation for missing dependencies
- Use retry logic with exponential backoff
- Provide clear error messages with context
- Log detailed information for debugging

### 3. Memory Management
- Use centralized file I/O utilities with retry logic
- Store knowledge in JSON format with clear structure
- Implement access tracking and metadata
- Use Pydantic models for data validation

### 4. Parallel Processing
- Use asyncio for concurrent operations
- Implement incremental progress saving
- Support selective retry for failed operations
- Report comprehensive success/failure rates

## Common Development Scenarios

### 1. Adding a New Module
```bash
# 1. Create module directory
mkdir amplifier/new_module
cd amplifier/new_module

# 2. Create standard structure
touch __init__.py README.md core.py models.py

# 3. Define contract in README.md
# 4. Implement core functionality
# 5. Add tests
# 6. Update documentation
```

### 2. Debugging Issues
```bash
# 1. Use specialized agents
"Use bug-hunter to investigate the failing component"

# 2. Check recent changes
git log --oneline -10
git diff HEAD~1

# 3. Run targeted tests
pytest tests/test_failing_component.py -v

# 4. Check logs
tail -f .data/logs/*.log
```

### 3. Knowledge Base Development
```bash
# 1. Add content to knowledge base
cp new_document.md ai_working/content/

# 2. Update knowledge extraction
make knowledge-update

# 3. Query the knowledge base
make knowledge-query Q="relevant topic"

# 4. Verify results
```

## Performance Considerations

### 1. File I/O Operations
- Always use retry logic for cloud sync environments
- Implement incremental saves for long operations
- Use JSON format for structured data
- Compress large datasets when appropriate

### 2. AI API Usage
- Implement request batching when possible
- Use caching for repeated queries
- Handle rate limits gracefully
- Monitor token usage and costs

### 3. Memory Management
- Use generators for large datasets
- Implement cleanup for temporary resources
- Monitor memory usage in long-running processes
- Use connection pooling for external services

## Security Best Practices

### 1. API Keys and Credentials
- Use environment variables for sensitive data
- Never commit credentials to repository
- Rotate keys regularly
- Use key management services when available

### 2. Input Validation
- Use Pydantic models for data validation
- Sanitize all user inputs
- Implement proper error handling
- Log security events appropriately

### 3. Dependency Management
- Keep dependencies updated regularly
- Use uv for secure dependency resolution
- Review security advisories
- Pin critical dependencies in production

This workflow guide ensures consistent, high-quality development across the Amplifier project.