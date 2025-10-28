# Amplifier Troubleshooting Guide

## Common Issues and Solutions

### 1. File I/O Errors (Cloud Sync Issues)

**Symptoms**: 
- OSError errno 5 during file operations
- Random I/O failures in WSL2 environment
- Files becoming temporarily unavailable

**Root Cause**: OneDrive/Dropbox cloud sync delays with symlinked directories

**Solutions**:
```python
# Use centralized file I/O utilities with retry logic
from amplifier.utils.file_io import write_json, read_json

# This automatically handles cloud sync issues
write_json(data, filepath)
```

**Prevention**:
- Enable "Always keep on this device" for cloud-synced folders
- Use local directories for critical development data
- Implement retry logic proactively

### 2. LLM Response Format Issues

**Symptoms**:
- JSON parsing errors from LLM responses
- Context contamination in responses
- Transient failures without retry

**Solutions**:
```python
from amplifier.ccsdk_toolkit.defensive import parse_llm_json, retry_with_feedback

# Extract JSON from any LLM response format
result = parse_llm_json(llm_response)

# Intelligent retry with error correction
result = await retry_with_feedback(async_func=generate_response, prompt=prompt)
```

**Prevention**:
- Always use defensive utilities for LLM responses
- Implement context isolation to prevent contamination
- Add comprehensive error handling

### 3. Tool Generation Failures

**Symptoms**:
- Non-recursive file discovery
- Silent failures without feedback
- Poor visibility into processing

**Solutions**:
```python
# Use recursive glob patterns
files = list(Path(dir).glob("**/*.md"))  # NOT "*.md"

# Validate minimum inputs
if len(files) < required_min:
    logger.error(f"Need at least {required_min} files, found {len(files)}")
    sys.exit(1)

# Show clear progress
logger.info(f"Processing {len(files)} files:")
for f in files[:5]:
    logger.info(f"  • {f.name}")
```

**Prevention**:
- Use standard tool patterns checklist
- Test with edge cases (empty dirs, single file)
- Validate against philosophy compliance

### 4. Memory System Issues

**Symptoms**:
- Memory storage failures
- Search not returning results
- Access count tracking issues

**Solutions**:
```python
# Check memory store initialization
from amplifier.memory import MemoryStore

store = MemoryStore()
all_memories = store.get_all()
print(f"Found {len(all_memories)} memories")

# Verify memory structure
for memory_id, memory in all_memories.items():
    assert hasattr(memory, 'content')
    assert hasattr(memory, 'category')
    assert hasattr(memory, 'timestamp')
```

**Prevention**:
- Use Pydantic models for validation
- Implement proper error handling
- Test memory operations regularly

### 5. Claude Code SDK Integration Issues

**Symptoms**:
- SDK not available errors
- Session management failures
- Unexpected API responses

**Solutions**:
```python
from amplifier.ccsdk_toolkit.core.session import ClaudeSession, SDKNotAvailableError

try:
    session = ClaudeSession()
    response = await session.generate_response(prompt)
except SDKNotAvailableError:
    logger.error("Claude Code SDK not available")
    # Implement fallback behavior
```

**Prevention**:
- Check SDK availability before use
- Implement graceful fallbacks
- Monitor API usage and limits

## Environment-Specific Issues

### WSL2 Specific Problems

**Symptoms**:
- Path compatibility issues
- Permission errors
- Performance degradation

**Solutions**:
```bash
# Check WSL2 configuration
wsl --status
wsl --list --verbose

# Fix path issues
export PATH="/usr/local/bin:$PATH"

# Check permissions
ls -la /mnt/c/
```

**Prevention**:
- Use Windows paths for cross-platform compatibility
- Configure proper permissions
- Monitor system resources

### Python Environment Issues

**Symptoms**:
- Import errors
- Version conflicts
- Virtual environment problems

**Solutions**:
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Verify uv installation
uv --version

# Recreate virtual environment
rm -rf .venv
make install

# Check dependencies
uv pip list
```

**Prevention**:
- Use uv for dependency management
- Pin critical dependencies
- Regular environment updates

## Performance Issues

### Slow Knowledge Processing

**Symptoms**:
- Knowledge extraction taking >30 seconds per document
- High memory usage during processing
- Timeouts during synthesis

**Solutions**:
```python
# Implement incremental processing
from amplifier.utils.file_io import write_json

# Save progress after each item
for i, item in enumerate(items):
    result = process_item(item)
    write_json(result, f"results_{i}.json")  # Incremental save
```

**Prevention**:
- Process documents in batches
- Implement progress checkpoints
- Monitor memory usage

### API Rate Limiting

**Symptoms**:
- HTTP 429 errors
- Slow response times
- Request timeouts

**Solutions**:
```python
import time
import asyncio

async def rate_limited_request(url, delay=1.0):
    await asyncio.sleep(delay)  # Rate limiting
    async with aiohttp.ClientSession() as session:
        return await session.get(url)
```

**Prevention**:
- Implement request batching
- Use exponential backoff
- Monitor API usage metrics

## Debugging Tools and Techniques

### 1. Logging Configuration

```python
import logging
from amplifier.utils.logger import setup_logger

logger = setup_logger(__name__)
logger.info("Debug information")
```

### 2. Memory and Performance Profiling

```bash
# Profile memory usage
python -m memory_profiler script.py

# Profile performance
python -m cProfile -o profile.stats script.py
```

### 3. File System Monitoring

```bash
# Monitor file operations
inotifywatch -v /path/to/directory

# Check disk usage
df -h
du -sh .data/
```

### 4. Network Diagnostics

```bash
# Check connectivity
curl -I https://api.anthropic.com

# Test DNS resolution
nslookup api.anthropic.com

# Monitor network traffic
netstat -an | grep :443
```

## Recovery Procedures

### 1. Corrupted Memory Store

```bash
# Backup current data
cp .data/memory.json .data/memory.json.backup

# Rebuild from source
make knowledge-update
```

### 2. Failed Knowledge Extraction

```bash
# Clear partial results
rm -rf .data/knowledge_synthesis/

# Restart extraction
make knowledge-update
```

### 3. Broken Worktree

```bash
# Remove corrupted worktree
make worktree-rm feature-name

# Create fresh worktree
make worktree feature-name
```

## Prevention Checklist

Before starting development work:

- [ ] Check that all dependencies are installed (`make check`)
- [ ] Verify cloud sync settings for development directories
- [ ] Ensure sufficient disk space available
- [ ] Check network connectivity for external APIs
- [ ] Verify Claude Code SDK installation
- [ ] Backup important data (.data/ directory)
- [ ] Check system resources (memory, CPU)

During development:

- [ ] Use centralized utilities for file operations
- [ ] Implement proper error handling
- [ ] Save progress incrementally for long operations
- [ ] Monitor log files for unusual activity
- [ ] Test changes in isolated worktrees

After development:

- [ ] Run full test suite (`make test`)
- [ ] Check code quality (`make check`)
- [ ] Update documentation
- [ ] Commit changes with clear messages
- [ ] Clean up temporary files and worktrees

This troubleshooting guide helps identify and resolve common issues in the Amplifier development environment.