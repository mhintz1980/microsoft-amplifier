"""
Tests for progressive context compression system
"""

import asyncio

import pytest

from amplifier.context.progressive_compression import CompressionLevel
from amplifier.context.progressive_compression import ContextChunk
from amplifier.context.progressive_compression import ContextCompressor
from amplifier.context.progressive_compression import SemanticScorer
from amplifier.context.progressive_compression import compress_context
from amplifier.context.progressive_compression import estimate_usage_percentage


class TestSemanticScorer:
    """Test semantic importance scoring"""

    def test_score_critical_content(self):
        scorer = SemanticScorer()
        chunk = ContextChunk(
            content="ERROR: Critical failure in main function", importance_score=0.0, chunk_type="text"
        )
        score = scorer.score_chunk(chunk)
        assert score > 0.7, "Critical error should have high score"

    def test_score_code_content(self):
        scorer = SemanticScorer()
        chunk = ContextChunk(content="def main_function():\n    pass", importance_score=0.0, chunk_type="code")
        score = scorer.score_chunk(chunk)
        assert score > 0.6, "Code should have medium-high score"

    def test_score_debug_content(self):
        scorer = SemanticScorer()
        chunk = ContextChunk(content="Debug trace: verbose logging output", importance_score=0.0, chunk_type="text")
        score = scorer.score_chunk(chunk)
        assert score < 0.6, "Debug content should have lower score"


class TestContextCompressor:
    """Test main compression functionality"""

    @pytest.fixture
    def compressor(self):
        return ContextCompressor()

    @pytest.fixture
    def sample_content(self):
        return """
# Main Implementation

This is the primary implementation of our system.

def main_function():
    '''Main entry point'''
    result = process_data()
    return result

def process_data():
    '''Process the data'''
    # Critical processing logic
    data = load_data()
    processed = transform(data)
    return processed

# Error Handling

def handle_errors():
    '''Handle critical errors'''
    try:
        risky_operation()
    except Exception as e:
        ERROR: Critical failure detected
        log_error(e)

# Debug Information

Debug trace: verbose logging output for testing
Temp variables for debugging
Background processing tasks

# Success Cases

SUCCESS: All tests completed successfully
Main functionality working as expected
        """.strip()

    def test_estimate_tokens(self, compressor):
        text = "This is a sample text with ten words total"
        tokens = compressor.estimate_tokens(text)
        assert tokens > 10, "Should estimate more than word count"
        assert tokens < 20, "Should be reasonable estimate"

    def test_chunk_context(self, compressor, sample_content):
        chunks = compressor.chunk_context(sample_content)
        assert len(chunks) > 1, "Should split content into multiple chunks"

        # Check that chunks have different types
        chunk_types = set(chunk.chunk_type for chunk in chunks)
        assert "code" in chunk_types, "Should identify code chunks"
        assert "text" in chunk_types, "Should identify text chunks"

    def test_full_compression(self, compressor, sample_content):
        result = asyncio.run(compressor.compress(sample_content, CompressionLevel.FULL))

        assert result.level == CompressionLevel.FULL
        assert result.compression_ratio == 1.0
        assert result.compressed_content == sample_content

    def test_summary_compression(self, compressor, sample_content):
        result = asyncio.run(compressor.compress(sample_content, CompressionLevel.SUMMARY))

        assert result.level == CompressionLevel.SUMMARY
        assert result.compression_ratio < 0.5, "Should achieve ~70% reduction"
        assert "ERROR: Critical failure" in result.compressed_content, "Should keep high-importance content"
        assert "Debug trace" not in result.compressed_content, "Should drop low-importance content"

    def test_essential_compression(self, compressor, sample_content):
        result = asyncio.run(compressor.compress(sample_content, CompressionLevel.ESSENTIAL))

        assert result.level == CompressionLevel.ESSENTIAL
        assert result.compression_ratio < 0.2, "Should achieve ~90% reduction"
        # Should keep only the most critical parts

    def test_metadata_compression(self, compressor, sample_content):
        result = asyncio.run(compressor.compress(sample_content, CompressionLevel.METADATA))

        assert result.level == CompressionLevel.METADATA
        assert result.compression_ratio < 0.1, "Should achieve ~95% reduction"
        assert "[ERROR]" in result.compressed_content, "Should show metadata for critical items"

    def test_auto_level_detection(self, compressor, sample_content):
        result = asyncio.run(compressor.compress(sample_content))

        # Should automatically choose appropriate level based on size
        assert result.level in CompressionLevel
        assert result.compression_ratio <= 1.0

    def test_compression_stats(self, compressor, sample_content):
        # Perform multiple compressions
        asyncio.run(compressor.compress(sample_content, CompressionLevel.SUMMARY))
        asyncio.run(compressor.compress(sample_content, CompressionLevel.ESSENTIAL))

        stats = compressor.get_compression_stats()

        assert stats["compressions_performed"] == 2
        assert "total_original_tokens" in stats
        assert "total_compressed_tokens" in stats
        assert "overall_compression_ratio" in stats


class TestUtilityFunctions:
    """Test convenience functions"""

    def test_compress_context_function(self):
        content = "Sample content for testing compression"
        result = asyncio.run(compress_context(content, CompressionLevel.FULL))

        assert result.level == CompressionLevel.FULL
        assert result.compressed_content == content

    def test_estimate_usage_percentage(self):
        content = "word " * 1000  # 1000 words
        usage = estimate_usage_percentage(content, max_tokens=2000)

        assert 0.4 < usage < 0.8, "Should estimate reasonable usage percentage"


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_content(self):
        compressor = ContextCompressor()
        result = asyncio.run(compressor.compress("", CompressionLevel.SUMMARY))

        assert result.compressed_content == ""
        assert result.original_tokens == 0

    def test_very_short_content(self):
        compressor = ContextCompressor()
        content = "Short"
        result = asyncio.run(compressor.compress(content, CompressionLevel.ESSENTIAL))

        # Should handle gracefully
        assert len(result.compressed_content) > 0

    def test_content_with_only_low_importance(self):
        compressor = ContextCompressor()
        content = "Debug trace 1\nDebug trace 2\nDebug trace 3"
        result = asyncio.run(compressor.compress(content, CompressionLevel.ESSENTIAL))

        # Should still keep something
        assert len(result.compressed_content) > 0

    def test_content_with_unicode_and_special_chars(self):
        compressor = ContextCompressor()
        content = "Special chars: ñáéíóú 🚀 Error: crítica"
        result = asyncio.run(compressor.compress(content, CompressionLevel.SUMMARY))

        assert result.compressed_content is not None
        assert len(result.compressed_content) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
