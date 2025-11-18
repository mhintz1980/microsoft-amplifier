"""
Progressive Context Compression System

Implements multi-level context compression with semantic importance scoring.
Follows ruthless simplicity philosophy - clean, focused, effective.

Usage:
    from amplifier.context.progressive_compression import ContextCompressor

    compressor = ContextCompressor()
    compressed = compressor.compress(context_text, target_level="SUMMARY")
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

try:
    from amplifier.mcp.persistent_storage import retrieve_result
    from amplifier.mcp.persistent_storage import store_result

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP persistent_storage not available, using file-based fallback")


class CompressionLevel(Enum):
    """Context compression levels with target reduction ratios"""

    FULL = "FULL"  # 0-25% usage, no compression
    SUMMARY = "SUMMARY"  # 25-50% usage, 70% reduction
    ESSENTIAL = "ESSENTIAL"  # 50-75% usage, 90% reduction
    METADATA = "METADATA"  # 75-100% usage, 95% reduction


@dataclass
class ContextChunk:
    """A piece of context with metadata for compression decisions"""

    content: str
    importance_score: float
    chunk_type: str  # "code", "text", "list", "error", "success"
    source_location: str | None = None
    timestamp: datetime | None = None
    tokens_estimated: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.tokens_estimated == 0:
            self.tokens_estimated = len(self.content.split()) * 1.3  # Rough estimate


@dataclass
class CompressionResult:
    """Result of context compression operation"""

    compressed_content: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    level: CompressionLevel
    metadata: dict[str, Any]
    storage_key: str | None = None
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class SemanticScorer:
    """Scores context chunks by semantic importance"""

    def __init__(self):
        # High-importance patterns
        self.critical_patterns = [
            r"error",
            r"exception",
            r"failure",
            r"bug",
            r"issue",
            r"critical",
            r"urgent",
            r"important",
            r"key",
            r"main",
            r"todo",
            r"fixme",
            r"hack",
            r"warning",
            r"define",
            r"class ",
            r"def ",
            r"function",
            r"method",
            r"import ",
            r"from ",
            r"require",
            r"export",
        ]

        # Medium-importance patterns
        self.medium_patterns = [
            r"example",
            r"test",
            r"demo",
            r"sample",
            r"note",
            r"comment",
            r"remark",
            r"observation",
            r"secondary",
            r"optional",
            r"additional",
        ]

        # Low-importance patterns
        self.low_patterns = [
            r"debug",
            r"verbose",
            r"trace",
            r"log",
            r"temp",
            r"temporary",
            r"scratch",
            r"background",
            r"history",
            r"archive",
        ]

    def score_chunk(self, chunk: ContextChunk) -> float:
        """Score a context chunk from 0.0 (low) to 1.0 (critical)"""
        content_lower = chunk.content.lower()
        score = 0.5  # Base score

        # Check for critical patterns
        for pattern in self.critical_patterns:
            if re.search(pattern, content_lower):
                score += 0.2

        # Check for medium patterns
        for pattern in self.medium_patterns:
            if re.search(pattern, content_lower):
                score += 0.1

        # Check for low patterns (reduce score)
        for pattern in self.low_patterns:
            if re.search(pattern, content_lower):
                score -= 0.1

        # Adjust based on content type
        type_scores = {"error": 0.9, "code": 0.8, "success": 0.7, "text": 0.5, "list": 0.4}
        score = type_scores.get(chunk.chunk_type, score) * 0.7 + score * 0.3

        # Ensure score is in valid range
        return max(0.0, min(1.0, score))


class ContextCompressor:
    """Main context compression system"""

    def __init__(
        self, compression_thresholds: list[float] = None, storage_path: str = ".docker-storage/context-compression/"
    ):
        self.scorer = SemanticScorer()
        self.compression_thresholds = compression_thresholds or [0.5, 0.7, 0.9]
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Track compression history
        self.compression_history: list[CompressionResult] = []

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation for context monitoring"""
        return int(len(text.split()) * 1.3)

    def chunk_context(self, content: str) -> list[ContextChunk]:
        """Break content into chunks for analysis"""
        chunks = []

        # Split by logical sections
        sections = re.split(r"\n\s*\n", content)

        for i, section in enumerate(sections):
            if not section.strip():
                continue

            # Determine chunk type
            chunk_type = "text"
            if "error" in section.lower() or "exception" in section.lower():
                chunk_type = "error"
            elif "success" in section.lower() or "completed" in section.lower():
                chunk_type = "success"
            elif re.search(r"def |class |function|import ", section):
                chunk_type = "code"
            elif re.search(r"^\s*[-*+]\s", section, re.MULTILINE):
                chunk_type = "list"

            chunk = ContextChunk(
                content=section.strip(),
                importance_score=0.0,  # Will be scored later
                chunk_type=chunk_type,
                source_location=f"section_{i}",
            )

            # Score the chunk
            chunk.importance_score = self.scorer.score_chunk(chunk)
            chunks.append(chunk)

        return chunks

    def compress_to_level(
        self, chunks: list[ContextChunk], target_level: CompressionLevel
    ) -> tuple[str, dict[str, Any]]:
        """Compress chunks to target level"""

        if target_level == CompressionLevel.FULL:
            # No compression, return everything
            content = "\n\n".join(chunk.content for chunk in chunks)
            metadata = {"chunks_count": len(chunks), "compression": "none"}
            return content, metadata

        # Sort chunks by importance
        sorted_chunks = sorted(chunks, key=lambda x: x.importance_score, reverse=True)

        # Calculate how many chunks to keep based on level
        retention_rates = {
            CompressionLevel.SUMMARY: 0.3,  # Keep 30% (70% reduction)
            CompressionLevel.ESSENTIAL: 0.1,  # Keep 10% (90% reduction)
            CompressionLevel.METADATA: 0.05,  # Keep 5% (95% reduction)
        }

        retention_rate = retention_rates[target_level]
        keep_count = max(1, int(len(sorted_chunks) * retention_rate))
        kept_chunks = sorted_chunks[:keep_count]

        if target_level == CompressionLevel.METADATA:
            # For metadata level, just keep summaries
            compressed_sections = []
            for chunk in kept_chunks:
                summary = f"[{chunk.chunk_type.upper()}] Score: {chunk.importance_score:.2f}"
                if chunk.source_location:
                    summary += f" | {chunk.source_location}"
                compressed_sections.append(summary)
            content = "\n".join(compressed_sections)
        else:
            # For other levels, keep full content of selected chunks
            content = "\n\n".join(chunk.content for chunk in kept_chunks)

        metadata = {
            "chunks_kept": len(kept_chunks),
            "chunks_total": len(sorted_chunks),
            "retention_rate": retention_rate,
            "compression": target_level.value,
            "avg_importance": sum(c.importance_score for c in kept_chunks) / len(kept_chunks),
        }

        return content, metadata

    async def compress(
        self, content: str, target_level: CompressionLevel = None, force_compress: bool = False
    ) -> CompressionResult:
        """
        Compress content to target level

        Args:
            content: The context to compress
            target_level: Target compression level (auto-determined if None)
            force_compress: Force compression even if under threshold

        Returns:
            CompressionResult with compressed content and metadata
        """

        # Estimate original tokens
        original_tokens = self.estimate_tokens(content)

        # Determine if compression is needed
        if target_level is None:
            # Simple heuristic based on content size
            if original_tokens < 1000:
                target_level = CompressionLevel.FULL
            elif original_tokens < 3000:
                target_level = CompressionLevel.SUMMARY
            elif original_tokens < 6000:
                target_level = CompressionLevel.ESSENTIAL
            else:
                target_level = CompressionLevel.METADATA

        # Skip compression if already at FULL level and under threshold
        if target_level == CompressionLevel.FULL and not force_compress:
            return CompressionResult(
                compressed_content=content,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                compression_ratio=1.0,
                level=CompressionLevel.FULL,
                metadata={"compression": "skipped", "reason": "under_threshold"},
            )

        # Chunk and compress
        chunks = self.chunk_context(content)
        compressed_content, metadata = self.compress_to_level(chunks, target_level)

        compressed_tokens = self.estimate_tokens(compressed_content)
        compression_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0

        # Store in persistent storage if available
        storage_key = None
        if MCP_AVAILABLE and target_level != CompressionLevel.FULL:
            storage_key = f"compressed_context_{hashlib.md5(content.encode()).hexdigest()[:8]}"
            await store_result(
                storage_key,
                {
                    "original": content,
                    "compressed": compressed_content,
                    "metadata": metadata,
                    "level": target_level.value,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        result = CompressionResult(
            compressed_content=compressed_content,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compression_ratio,
            level=target_level,
            metadata=metadata,
            storage_key=storage_key,
        )

        # Track compression history
        self.compression_history.append(result)

        return result

    async def restore_from_storage(self, storage_key: str) -> str | None:
        """Restore original content from storage"""
        if not MCP_AVAILABLE:
            return None

        try:
            result = await retrieve_result(storage_key)
            if result and isinstance(result, dict):
                return result.get("original")
        except Exception as e:
            print(f"Failed to restore from storage: {e}")

        return None

    def get_compression_stats(self) -> dict[str, Any]:
        """Get statistics on compression performance"""
        if not self.compression_history:
            return {"message": "No compression history"}

        total_original = sum(r.original_tokens for r in self.compression_history)
        total_compressed = sum(r.compressed_tokens for r in self.compression_history)
        avg_ratio = total_compressed / total_original if total_original > 0 else 1.0

        level_counts = {}
        for result in self.compression_history:
            level_counts[result.level.value] = level_counts.get(result.level.value, 0) + 1

        return {
            "compressions_performed": len(self.compression_history),
            "total_original_tokens": total_original,
            "total_compressed_tokens": total_compressed,
            "overall_compression_ratio": avg_ratio,
            "token_reduction": f"{(1 - avg_ratio) * 100:.1f}%",
            "compression_levels_used": level_counts,
            "last_compression": self.compression_history[-1].timestamp.isoformat()
            if self.compression_history
            else None,
        }


# Global instance for easy use
_default_compressor: ContextCompressor | None = None


def get_compressor() -> ContextCompressor:
    """Get or create default compressor instance"""
    global _default_compressor
    if _default_compressor is None:
        _default_compressor = ContextCompressor()
    return _default_compressor


async def compress_context(content: str, level: CompressionLevel = None) -> CompressionResult:
    """Convenient function to compress context"""
    compressor = get_compressor()
    return await compressor.compress(content, level)


def estimate_usage_percentage(content: str, max_tokens: int = 8000) -> float:
    """Estimate context usage percentage"""
    tokens = len(content.split()) * 1.3  # Rough estimate
    return min(1.0, tokens / max_tokens)
