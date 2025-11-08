"""
Context Compaction System for Amplifier

Implements intelligent context management based on Anthropic's context engineering research.
Provides progressive summarization, semantic compression, and just-in-time retrieval.

Key Features:
- Progressive context summarization (3-level compression)
- Semantic importance scoring
- Memory consolidation patterns
- Token-efficient context reconstruction
"""

import re
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

from .logger import get_logger
from .token_utils import estimate_tokens

logger = get_logger(__name__)


class ContextLevel(Enum):
    """Context compression levels."""

    FULL = "full"  # Complete context, high detail
    SUMMARY = "summary"  # Compressed summary, medium detail
    ESSENTIAL = "essential"  # Core points only, low detail
    METADATA = "metadata"  # Just metadata and references, minimal


@dataclass
class ContextChunk:
    """A chunk of context with metadata."""

    content: str
    importance_score: float  # 0.0 to 1.0
    timestamp: datetime
    source: str
    chunk_type: str  # "code", "explanation", "decision", "result"
    tags: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)


@dataclass
class CompactContext:
    """Compressed context representation."""

    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    level: ContextLevel
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    reconstruction_hints: list[str] = field(default_factory=list)


class ContextCompactor:
    """Intelligent context compaction and management system."""

    def __init__(self, max_context_tokens: int = 100000):
        self.max_context_tokens = max_context_tokens
        self.compression_history: list[CompactContext] = []
        self.importance_patterns: dict[str, float] = {}

    def add_context_chunk(self, chunk: ContextChunk) -> None:
        """Add a new context chunk and update importance patterns."""
        # Update importance patterns based on content
        self._update_importance_patterns(chunk)

    def _update_importance_patterns(self, chunk: ContextChunk) -> None:
        """Learn importance patterns from context chunks."""
        # Extract key terms and their importance
        terms = self._extract_key_terms(chunk.content)
        for term in terms:
            if term not in self.importance_patterns:
                self.importance_patterns[term] = 0.0
            # Update importance with exponential moving average
            self.importance_patterns[term] = 0.7 * self.importance_patterns[term] + 0.3 * chunk.importance_score

    def _extract_key_terms(self, content: str) -> list[str]:
        """Extract important terms from content."""
        # Simple term extraction - can be enhanced with NLP
        # Look for technical terms, proper nouns, and key concepts
        terms = []

        # Find capitalized words (potential proper nouns/technical terms)
        capitalized = re.findall(r"\b[A-Z][a-zA-Z]+(?:[A-Z][a-zA-Z]+)*\b", content)
        terms.extend(capitalized)

        # Find code patterns
        code_patterns = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", content)
        terms.extend(code_patterns)

        # Find file paths
        file_paths = re.findall(r"\b[\w\-\.]+/\w[\w\-\.]*\b", content)
        terms.extend(file_paths)

        return list(set(terms))  # Remove duplicates

    def compress_context(
        self, context_chunks: list[ContextChunk], target_level: ContextLevel, max_tokens: int | None = None
    ) -> CompactContext:
        """Compress context to target level."""
        if not context_chunks:
            return CompactContext(
                original_tokens=0, compressed_tokens=0, compression_ratio=1.0, level=target_level, content=""
            )

        max_tokens = max_tokens or self.max_context_tokens
        original_tokens = sum(estimate_tokens(chunk.content) for chunk in context_chunks)

        logger.info(f"Compressing {original_tokens} tokens to {target_level.value} level")

        # Sort chunks by importance
        sorted_chunks = sorted(context_chunks, key=lambda c: c.importance_score, reverse=True)

        # Apply compression based on target level
        if target_level == ContextLevel.FULL:
            compressed_content = self._compress_full(sorted_chunks, max_tokens)
        elif target_level == ContextLevel.SUMMARY:
            compressed_content = self._compress_summary(sorted_chunks, max_tokens)
        elif target_level == ContextLevel.ESSENTIAL:
            compressed_content = self._compress_essential(sorted_chunks, max_tokens)
        else:  # METADATA
            compressed_content = self._compress_metadata(sorted_chunks, max_tokens)

        compressed_tokens = estimate_tokens(compressed_content)
        compression_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0

        result = CompactContext(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compression_ratio,
            level=target_level,
            content=compressed_content,
            metadata={
                "compression_date": datetime.now().isoformat(),
                "chunk_count": len(context_chunks),
                "source_distribution": self._analyze_sources(context_chunks),
            },
            reconstruction_hints=self._generate_reconstruction_hints(sorted_chunks),
        )

        self.compression_history.append(result)
        return result

    def _compress_full(self, chunks: list[ContextChunk], max_tokens: int) -> str:
        """Full compression - keep most important content with minimal reduction."""
        content_parts = []
        current_tokens = 0

        for chunk in chunks:
            chunk_tokens = estimate_tokens(chunk.content)
            if current_tokens + chunk_tokens > max_tokens:
                # Try to include partial content
                remaining_tokens = max_tokens - current_tokens
                if remaining_tokens > 100:  # Only include if meaningful amount
                    truncated = self._truncate_content(chunk.content, remaining_tokens)
                    content_parts.append(f"[{chunk.source}] {truncated}")
                break

            content_parts.append(f"[{chunk.source}] {chunk.content}")
            current_tokens += chunk_tokens

        return "\n\n".join(content_parts)

    def _compress_summary(self, chunks: list[ContextChunk], max_tokens: int) -> str:
        """Summary compression - create summarized version of important content."""
        summaries = []
        current_tokens = 0

        for chunk in chunks:
            # Create a summary of each chunk
            summary = self._summarize_content(chunk.content, chunk.chunk_type)
            summary_tokens = estimate_tokens(summary)

            if current_tokens + summary_tokens > max_tokens:
                break

            summaries.append(f"[{chunk.source}] {summary}")
            current_tokens += summary_tokens

        return "\n\n".join(summaries)

    def _compress_essential(self, chunks: list[ContextChunk], max_tokens: int) -> str:
        """Essential compression - extract only the most critical points."""
        essential_points = []
        current_tokens = 0

        for chunk in chunks:
            # Extract essential points from each chunk
            points = self._extract_essential_points(chunk.content, chunk.chunk_type)
            points_text = "\n".join(f"• {point}" for point in points)
            points_tokens = estimate_tokens(points_text)

            if current_tokens + points_tokens > max_tokens:
                break

            if points:
                essential_points.append(f"[{chunk.source}] Critical points:\n{points_text}")
                current_tokens += points_tokens

        return "\n\n".join(essential_points)

    def _compress_metadata(self, chunks: list[ContextChunk], max_tokens: int) -> str:
        """Metadata compression - keep only references and metadata."""
        metadata_items = []
        current_tokens = 0

        for chunk in chunks:
            # Create metadata entry
            metadata = f"[{chunk.source}] {chunk.chunk_type} ({chunk.timestamp.strftime('%Y-%m-%d %H:%M')})"
            if chunk.references:
                metadata += f" | Refs: {', '.join(chunk.references[:3])}"
            if chunk.tags:
                metadata += f" | Tags: {', '.join(chunk.tags[:3])}"

            metadata_tokens = estimate_tokens(metadata)
            if current_tokens + metadata_tokens > max_tokens:
                break

            metadata_items.append(metadata)
            current_tokens += metadata_tokens

        return "\n".join(metadata_items)

    def _summarize_content(self, content: str, content_type: str) -> str:
        """Create a summary of content based on its type."""
        if content_type == "code":
            # For code, extract function signatures and key comments
            lines = content.split("\n")
            important_lines = []
            for line in lines:
                line = line.strip()
                # Keep function definitions, class definitions, and comments
                if (
                    line.startswith(("def ", "class ", "async def "))
                    or line.startswith("#")
                    or '"""' in line
                    or "'''" in line
                ):
                    important_lines.append(line)

            if len(important_lines) > 5:
                # Take first few important lines
                important_lines = important_lines[:5] + ["# ... (truncated)"]

            return "\n".join(important_lines)

        if content_type == "decision":
            # For decisions, extract the decision and key reasoning
            lines = content.split("\n")
            for line in lines:
                if any(keyword in line.lower() for keyword in ["decision:", "conclusion:", "action:"]):
                    return line.strip()
            return content[:100] + "..." if len(content) > 100 else content

        # General content summarization
        sentences = re.split(r"[.!?]+", content)
        important_sentences = []

        # Take first and last sentences, plus any with key indicators
        if sentences:
            important_sentences.append(sentences[0].strip())

            for sentence in sentences[1:-1]:
                if any(
                    keyword in sentence.lower()
                    for keyword in ["important", "critical", "key", "essential", "therefore", "because"]
                ):
                    important_sentences.append(sentence.strip())

            if len(sentences) > 1:
                important_sentences.append(sentences[-1].strip())

        return ". ".join(important_sentences[:3])

    def _extract_essential_points(self, content: str, content_type: str) -> list[str]:
        """Extract essential points from content."""
        points = []

        if content_type == "code":
            # Extract function/class names and their purposes
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith(("def ", "class ", "async def ")):
                    # Extract function signature
                    if ":" in line:
                        signature = line.split(":")[0].strip()
                        points.append(f"Function: {signature}")
        else:
            # Look for bullet points, numbered lists, or key phrases
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith(("•", "-", "*", "1.", "2.", "3.")) or any(
                    keyword in line.lower() for keyword in ["important:", "key point:", "critical:", "note:"]
                ):
                    points.append(line)

        # If no structured points found, extract key phrases
        if not points:
            # Look for sentences with important keywords
            sentences = re.split(r"[.!?]+", content)
            for sentence in sentences:
                sentence = sentence.strip()
                if any(
                    keyword in sentence.lower()
                    for keyword in ["error", "fix", "implement", "add", "remove", "update", "create"]
                ):
                    points.append(sentence)

        return points[:5]  # Limit to top 5 points

    def _truncate_content(self, content: str, max_tokens: int) -> str:
        """Truncate content to fit within token limit."""
        # Rough approximation - 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        if len(content) <= max_chars:
            return content

        # Try to truncate at sentence boundaries
        truncated = content[:max_chars]
        last_period = truncated.rfind(".")
        last_newline = truncated.rfind("\n")

        best_cut = max(last_period, last_newline)
        if best_cut > max_chars * 0.8:  # Only use if we're not cutting too much
            return truncated[: best_cut + 1] + "..."

        return truncated + "..."

    def _analyze_sources(self, chunks: list[ContextChunk]) -> dict[str, int]:
        """Analyze distribution of sources in chunks."""
        sources = {}
        for chunk in chunks:
            sources[chunk.source] = sources.get(chunk.source, 0) + 1
        return sources

    def _generate_reconstruction_hints(self, chunks: list[ContextChunk]) -> list[str]:
        """Generate hints for reconstructing full context."""
        hints = []

        # Key topics covered
        topics = set()
        for chunk in chunks:
            topics.update(chunk.tags)

        if topics:
            hints.append(f"Topics covered: {', '.join(list(topics)[:5])}")

        # Key files or components mentioned
        files = set()
        for chunk in chunks:
            for ref in chunk.references:
                if "." in ref and "/" in ref:  # Likely a file path
                    files.add(ref)

        if files:
            hints.append(f"Files referenced: {', '.join(list(files)[:3])}")

        # Time range
        if chunks:
            timestamps = [chunk.timestamp for chunk in chunks]
            earliest = min(timestamps)
            latest = max(timestamps)
            hints.append(f"Time range: {earliest.strftime('%H:%M')} - {latest.strftime('%H:%M')}")

        return hints

    def get_compression_stats(self) -> dict[str, Any]:
        """Get statistics about compression performance."""
        if not self.compression_history:
            return {"message": "No compression history available"}

        total_original = sum(c.original_tokens for c in self.compression_history)
        total_compressed = sum(c.compressed_tokens for c in self.compression_history)
        avg_ratio = total_compressed / total_original if total_original > 0 else 0

        level_stats = {}
        for level in ContextLevel:
            level_compressions = [c for c in self.compression_history if c.level == level]
            if level_compressions:
                level_stats[level.value] = {
                    "count": len(level_compressions),
                    "avg_ratio": sum(c.compression_ratio for c in level_compressions) / len(level_compressions),
                }

        return {
            "total_compressions": len(self.compression_history),
            "total_original_tokens": total_original,
            "total_compressed_tokens": total_compressed,
            "overall_compression_ratio": avg_ratio,
            "token_savings": total_original - total_compressed,
            "compression_by_level": level_stats,
            "most_recent": self.compression_history[-1].metadata if self.compression_history else None,
        }

    def reconstruct_context(self, compact_context: CompactContext) -> str:
        """Reconstruct a more detailed context from compact version."""
        # This would integrate with memory systems to retrieve full context
        # For now, return the compact content with reconstruction hints

        reconstruction = f"# Reconstructed Context ({compact_context.level.value})\n\n"
        reconstruction += compact_context.content

        if compact_context.reconstruction_hints:
            reconstruction += "\n\n# Reconstruction Hints:\n"
            for hint in compact_context.reconstruction_hints:
                reconstruction += f"- {hint}\n"

        return reconstruction


# Global compactor instance
_context_compactor = ContextCompactor()


def get_context_compactor() -> ContextCompactor:
    """Get the global context compactor instance."""
    return _context_compactor


def create_context_chunk(
    content: str,
    source: str,
    chunk_type: str = "explanation",
    importance_score: float = 0.5,
    tags: list[str] | None = None,
    references: list[str] | None = None,
) -> ContextChunk:
    """Create a new context chunk."""
    return ContextChunk(
        content=content,
        importance_score=importance_score,
        timestamp=datetime.now(),
        source=source,
        chunk_type=chunk_type,
        tags=tags or [],
        references=references or [],
    )


async def compress_session_context(
    messages: list[dict[str, Any]], target_level: ContextLevel = ContextLevel.SUMMARY, max_tokens: int = 20000
) -> CompactContext:
    """Compress a session's message context."""
    compactor = get_context_compactor()

    # Convert messages to context chunks
    chunks = []
    for msg in messages:
        content = msg.get("content", "")
        if content:
            chunk = create_context_chunk(
                content=content,
                source=msg.get("role", "unknown"),
                chunk_type="message",
                importance_score=0.7,  # Messages are generally important
                tags=["session", "conversation"],
            )
            chunks.append(chunk)

    return compactor.compress_context(chunks, target_level, max_tokens)
