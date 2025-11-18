# Context Management

This module provides context management and compression capabilities for the Microsoft Amplifier framework.

## Progressive Context Compression

The `progressive_compression.py` module implements a sophisticated context compression system that helps manage large conversational contexts efficiently.

### Features

- **Multi-level compression**: FULL → SUMMARY → ESSENTIAL → METADATA
- **Semantic importance scoring**: Intelligently preserves critical information
- **Real-time token monitoring**: Tracks context usage automatically
- **Docker storage integration**: Preserves compressed context for later retrieval
- **Automatic level selection**: Chooses appropriate compression based on content size

### Compression Levels

| Level | Usage Range | Reduction | Description |
|-------|-------------|-----------|-------------|
| FULL | 0-25% | 0% | No compression, complete context |
| SUMMARY | 25-50% | 70% | Key points only, preserves important sections |
| ESSENTIAL | 50-75% | 90% | Critical info only, high-value content |
| METADATA | 75-100% | 95% | Just pointers and metadata for storage |

### Quick Start

```python
from amplifier.context.progressive_compression import ContextCompressor, CompressionLevel

# Create compressor
compressor = ContextCompressor()

# Compress context
result = await compressor.compress(context_text, CompressionLevel.SUMMARY)

print(f"Compression ratio: {result.compression_ratio:.2f}")
print(f"Compressed content: {result.compressed_content}")

# Get compression statistics
stats = compressor.get_compression_stats()
print(f"Overall reduction: {stats['token_reduction']}")
```

### Automatic Usage

For automatic compression based on content size:

```python
from amplifier.context.progressive_compression import compress_context

# Automatic level selection
result = await compress_context(context_text)
print(f"Selected level: {result.level.value}")
```

### Semantic Scoring

The system uses semantic importance scoring to determine what content to preserve:

- **Critical patterns**: errors, exceptions, critical, main functions
- **Medium patterns**: examples, tests, notes, comments
- **Low patterns**: debug, verbose, temporary, background

### Integration with MCP

When available, the system integrates with the MCP persistent storage for saving compressed context:

```python
# Store compressed context in Docker storage
storage_key = result.storage_key

# Restore original content later
original = await compressor.restore_from_storage(storage_key)
```

### Performance Characteristics

- **Token estimation**: ~1.3 tokens per word (rough estimate)
- **Compression speed**: O(n log n) for chunking and sorting
- **Memory usage**: Minimal, chunks processed in streaming fashion
- **Storage efficiency**: Compressed data stored in Docker volumes

## Files

- `progressive_compression.py` - Main compression system
- `tests/test_progressive_compression.py` - Comprehensive test suite
- `examples/compression_demo.py` - Demonstration script
- `intelligent_pruning_service.py` - Existing context pruning service