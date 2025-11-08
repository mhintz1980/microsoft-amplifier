"""
Context Management Skill

Progressive context compression and retrieval skill converted from context_compactor.py.
Follows ruthless simplicity principles with token-efficient operations.
"""

import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ...utils.logger import get_logger
from ...utils.token_utils import estimate_tokens
from ..skills_framework.skill_template import BaseSkill
from ..skills_framework.skill_template import SkillContext
from ..skills_framework.skill_template import SkillLevel
from ..skills_framework.skill_template import SkillResult

logger = get_logger(__name__)


class ContextLevel:
    """Context compression levels matching original implementation."""

    FULL = "full"
    SUMMARY = "summary"
    ESSENTIAL = "essential"
    METADATA = "metadata"


@dataclass
class ContextChunk:
    """Simplified context chunk for skill usage."""

    content: str
    importance_score: float
    source: str
    chunk_type: str
    tags: list[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ContextCompactorSkill(BaseSkill):
    """
    Skill for intelligent context compression and retrieval.

    Converts long conversations into progressively compressed versions
    while preserving essential information and reconstruction hints.
    """

    @property
    def description(self) -> str:
        return "Compress context progressively while preserving essential information"

    @property
    def tags(self) -> list[str]:
        return ["context", "compression", "memory", "summarization"]

    def can_handle(self, context: SkillContext) -> float:
        """Determine if this skill can handle the context."""
        query_lower = context.query.lower()

        # Check for context compression keywords
        compression_keywords = [
            "compress",
            "summarize",
            "context",
            "memory",
            "history",
            "conversation",
            "session",
            "long conversation",
            "too much context",
        ]

        # Check for token limit indicators
        token_keywords = ["token", "limit", "too long", "truncate", "fit"]

        score = 0.0

        # High confidence for explicit compression requests
        if any(keyword in query_lower for keyword in compression_keywords):
            score += 0.7

        # Medium confidence for token limit concerns
        if any(keyword in query_lower for keyword in token_keywords):
            score += 0.4

        # Boost score for long conversation history
        if len(context.conversation_history) > 10:
            score += 0.3
        elif len(context.conversation_history) > 5:
            score += 0.2

        return min(score, 1.0)

    def execute(self, context: SkillContext, level: SkillLevel = SkillLevel.SUMMARY) -> SkillResult:
        """Execute context compression at specified level."""
        start_time = time.time()

        try:
            # Convert conversation history to context chunks
            chunks = self._messages_to_chunks(context.conversation_history)

            if not chunks:
                return SkillResult(
                    skill_name=self.skill_name,
                    level=level,
                    content="No context to compress.",
                    tokens_used=10,
                    execution_time=time.time() - start_time,
                    next_level_available=False,
                )

            # Compress based on level
            if level == SkillLevel.METADATA:
                compressed = self._compress_metadata(chunks, context.available_tokens)
            elif level == SkillLevel.SUMMARY:
                compressed = self._compress_summary(chunks, context.available_tokens)
            else:  # FULL
                compressed = self._compress_full(chunks, context.available_tokens)

            tokens_used = estimate_tokens(compressed)

            self.execution_count += 1
            self.last_execution = datetime.now()

            return SkillResult(
                skill_name=self.skill_name,
                level=level,
                content=compressed,
                tokens_used=tokens_used,
                execution_time=time.time() - start_time,
                metadata={
                    "original_chunks": len(chunks),
                    "compression_ratio": tokens_used / sum(estimate_tokens(c.content) for c in chunks)
                    if chunks
                    else 1.0,
                    "sources": list({c.source for c in chunks}),
                },
                next_level_available=level != SkillLevel.FULL,
            )

        except Exception as e:
            logger.error(f"Context compression failed: {e}")
            return SkillResult(
                skill_name=self.skill_name,
                level=level,
                content=f"Context compression failed: {str(e)}",
                tokens_used=50,
                execution_time=time.time() - start_time,
                next_level_available=False,
            )

    def _messages_to_chunks(self, messages: list[dict[str, Any]]) -> list[ContextChunk]:
        """Convert messages to context chunks."""
        chunks = []

        for msg in messages:
            content = msg.get("content", "")
            if not content or len(content.strip()) < 10:
                continue

            # Determine importance based on role and content
            role = msg.get("role", "unknown")
            importance = 0.5

            if role == "user":
                importance = 0.7  # User input is important
            elif role == "assistant":
                importance = 0.6  # Assistant responses are important
            elif role == "system":
                importance = 0.3  # System messages are less important

            # Boost importance for code, errors, or decisions
            content_lower = content.lower()
            if any(keyword in content_lower for keyword in ["error", "fix", "implement", "decision"]):
                importance += 0.2
            if "```" in content:  # Contains code
                importance += 0.1

            importance = min(importance, 1.0)

            chunks.append(
                ContextChunk(
                    content=content,
                    importance_score=importance,
                    source=role,
                    chunk_type="message",
                    tags=["conversation", role],
                )
            )

        return chunks

    def _compress_metadata(self, chunks: list[ContextChunk], max_tokens: int) -> str:
        """Compress to metadata level - minimal information."""
        metadata_items = []
        current_tokens = 0

        # Sort by importance
        chunks.sort(key=lambda c: c.importance_score, reverse=True)

        for chunk in chunks:
            # Create metadata entry
            metadata = f"[{chunk.source}] {chunk.chunk_type}"

            # Add timestamp
            if chunk.timestamp:
                metadata += f" ({chunk.timestamp.strftime('%H:%M')})"

            # Add key tags
            if chunk.tags:
                important_tags = chunk.tags[:2]  # Limit tags
                if important_tags:
                    metadata += f" | {', '.join(important_tags)}"

            metadata_tokens = estimate_tokens(metadata)
            if current_tokens + metadata_tokens > max_tokens:
                break

            metadata_items.append(metadata)
            current_tokens += metadata_tokens

        result = "# Context Summary (Metadata)\n\n"
        result += f"Conversation spanned {len(chunks)} messages.\n\n"
        result += "Key interactions:\n"
        result += "\n".join(f"• {item}" for item in metadata_items)

        return result

    def _compress_summary(self, chunks: list[ContextChunk], max_tokens: int) -> str:
        """Compress to summary level - key points."""
        summaries = []
        current_tokens = 0

        # Sort by importance
        chunks.sort(key=lambda c: c.importance_score, reverse=True)

        for chunk in chunks:
            summary = self._summarize_chunk(chunk)
            summary_tokens = estimate_tokens(summary)

            if current_tokens + summary_tokens > max_tokens:
                break

            summaries.append(f"[{chunk.source}] {summary}")
            current_tokens += summary_tokens

        result = "# Context Summary\n\n"
        result += "\n\n".join(summaries)

        return result

    def _compress_full(self, chunks: list[ContextChunk], max_tokens: int) -> str:
        """Compress to full level - most important content."""
        content_parts = []
        current_tokens = 0

        # Sort by importance
        chunks.sort(key=lambda c: c.importance_score, reverse=True)

        for chunk in chunks:
            content = chunk.content
            chunk_tokens = estimate_tokens(content)

            if current_tokens + chunk_tokens > max_tokens:
                # Try to include partial content
                remaining_tokens = max_tokens - current_tokens
                if remaining_tokens > 50:
                    truncated = self._truncate_content(content, remaining_tokens)
                    content_parts.append(f"[{chunk.source}] {truncated}...")
                break

            content_parts.append(f"[{chunk.source}] {content}")
            current_tokens += chunk_tokens

        result = "# Context (Compressed)\n\n"
        result += "\n\n".join(content_parts)

        return result

    def _summarize_chunk(self, chunk: ContextChunk) -> str:
        """Create a summary of a context chunk."""
        content = chunk.content

        # For code chunks, extract key elements
        if "```" in content:
            lines = content.split("\n")
            important_lines = []

            for line in lines:
                line_stripped = line.strip()
                if any(
                    pattern in line_stripped for pattern in ["def ", "class ", "import ", "from "]
                ) or line_stripped.startswith("#"):
                    important_lines.append(line_stripped)

            if important_lines:
                return f"Code: {'; '.join(important_lines[:3])}"

        # For other content, extract key sentences
        sentences = re.split(r"[.!?]+", content)
        important_sentences = []

        # Look for sentences with key indicators
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            if any(
                keyword in sentence.lower()
                for keyword in ["error", "fix", "implement", "add", "create", "decision", "important"]
            ):
                important_sentences.append(sentence)

        # Take first and last sentences if no important ones found
        if not important_sentences and sentences:
            if len(sentences) > 0:
                important_sentences.append(sentences[0].strip())
            if len(sentences) > 1:
                important_sentences.append(sentences[-1].strip())

        return ". ".join(important_sentences[:2]) if important_sentences else content[:100] + "..."

    def _truncate_content(self, content: str, max_tokens: int) -> str:
        """Truncate content to fit within token limit."""
        max_chars = max_tokens * 4  # Rough approximation

        if len(content) <= max_chars:
            return content

        # Try to truncate at sentence boundary
        truncated = content[:max_chars]
        last_period = truncated.rfind(".")

        if last_period > max_chars * 0.8:
            return truncated[: last_period + 1]

        return truncated + "..."
