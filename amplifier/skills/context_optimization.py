"""
Context Optimization Specialist Skill

Advanced context management with progressive loading, token efficiency,
and semantic importance scoring for AI systems.

Implements ruthless simplicity while achieving 70-95% compression targets
and maintaining conversation coherence across context management operations.
"""

import re
import time
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

from ..utils.logger import get_logger
from ..utils.token_utils import estimate_tokens
from .skills_framework.skill_template import BaseSkill
from .skills_framework.skill_template import SkillContext
from .skills_framework.skill_template import SkillLevel
from .skills_framework.skill_template import SkillResult

logger = get_logger(__name__)


class ContextLevel(Enum):
    """Context compression levels with target reduction ratios."""

    FULL = "full"  # 0% reduction - complete content
    SUMMARY = "summary"  # 70% reduction - key points
    ESSENTIAL = "essential"  # 90% reduction - critical info
    METADATA = "metadata"  # 95% reduction - minimal metadata


class ConversationType(Enum):
    """Conversation types for specialized optimization strategies."""

    CODE_DEVELOPMENT = "code_development"
    PROBLEM_SOLVING = "problem_solving"
    PLANNING = "planning"
    DISCUSSION = "discussion"
    MIXED = "mixed"


@dataclass
class ContextMetrics:
    """Performance metrics for context optimization operations."""

    original_tokens: int = 0
    compressed_tokens: int = 0
    compression_ratio: float = 0.0
    processing_time: float = 0.0
    information_retention_score: float = 0.0
    semantic_coherence_score: float = 0.0


@dataclass
class ContextChunk:
    """Enhanced context chunk with semantic features."""

    content: str
    importance_score: float
    source: str
    chunk_type: str
    semantic_tags: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    token_count: int = 0
    references: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.token_count == 0:
            self.token_count = estimate_tokens(self.content)
        if not self.semantic_tags:
            self.semantic_tags = self._extract_semantic_tags()

    def _extract_semantic_tags(self) -> list[str]:
        """Extract semantic tags from content for better classification."""
        content_lower = self.content.lower()
        tags = []

        # Content type detection
        if "```" in self.content:
            tags.append("code")
        if any(url in self.content for url in ["http://", "https://", "www."]):
            tags.append("has_url")
        if any(pattern in content_lower for pattern in ["error", "fix", "bug", "issue"]):
            tags.append("error_resolution")
        if any(pattern in content_lower for pattern in ["implement", "add", "create", "build"]):
            tags.append("implementation")
        if any(pattern in content_lower for pattern in ["decision", "choose", "select"]):
            tags.append("decision")
        if any(pattern in content_lower for pattern in ["question", "why", "how", "what"]):
            tags.append("question")

        return tags


@dataclass
class ContextBudget:
    """Context budget management for token allocation."""

    total_budget: int
    current_usage: int = 0
    reserved_tokens: int = 0
    compression_threshold: float = 0.8  # Start compression at 80% usage

    @property
    def available_tokens(self) -> int:
        return max(0, self.total_budget - self.current_usage - self.reserved_tokens)

    @property
    def usage_percentage(self) -> float:
        return self.current_usage / self.total_budget if self.total_budget > 0 else 0

    def needs_compression(self) -> bool:
        return self.usage_percentage > self.compression_threshold


class ContextOptimizationSkill(BaseSkill):
    """
    Advanced context optimization specialist skill.

    Provides progressive context loading, token efficiency optimization,
    semantic importance scoring, and context engineering patterns.
    """

    def __init__(self):
        super().__init__()
        self.metrics_history: list[ContextMetrics] = []
        self.conversation_patterns: dict[str, float] = defaultdict(float)

    @property
    def description(self) -> str:
        return "Advanced context optimization with progressive loading and semantic scoring"

    @property
    def tags(self) -> list[str]:
        return ["context", "optimization", "compression", "token-efficiency", "semantic"]

    def can_handle(self, context: SkillContext) -> float:
        """Determine if this skill can handle the context."""
        query_lower = context.query.lower()

        # High-confidence keywords
        optimization_keywords = [
            "optimize",
            "optimization",
            "compress",
            "compression",
            "context",
            "token",
            "efficiency",
            "summarize",
            "memory",
        ]

        # Context management indicators
        context_keywords = [
            "too much context",
            "long conversation",
            "token limit",
            "context window",
            "conversation history",
            "session",
        ]

        score = 0.0

        # High confidence for explicit optimization requests
        if any(keyword in query_lower for keyword in optimization_keywords):
            score += 0.8

        # Medium confidence for context management concerns
        if any(keyword in query_lower for keyword in context_keywords):
            score += 0.5

        # Boost based on conversation length
        if len(context.conversation_history) > 20:
            score += 0.3
        elif len(context.conversation_history) > 10:
            score += 0.2

        # Boost for low token availability
        if context.available_tokens < 2000:
            score += 0.3

        return min(score, 1.0)

    def execute(self, context: SkillContext, level: SkillLevel = SkillLevel.SUMMARY) -> SkillResult:
        """Execute context optimization at specified level."""
        start_time = time.time()

        try:
            # Analyze conversation characteristics
            conversation_type = self._detect_conversation_type(context.conversation_history)

            # Convert to context chunks with semantic analysis
            chunks = self._create_context_chunks(context.conversation_history)

            if not chunks:
                return self._empty_result(level, start_time)

            # Apply semantic importance scoring
            chunks = self._score_semantic_importance(chunks, conversation_type)

            # Create context budget
            budget = ContextBudget(
                total_budget=context.available_tokens, current_usage=sum(c.token_count for c in chunks)
            )

            # Compress based on level and budget
            if level == SkillLevel.METADATA:
                compressed = self._compress_metadata(chunks, budget)
            elif level == SkillLevel.SUMMARY:
                compressed = self._compress_summary(chunks, budget, conversation_type)
            else:  # FULL
                compressed = self._compress_full(chunks, budget)

            # Calculate metrics
            metrics = self._calculate_metrics(chunks, compressed, start_time)
            self.metrics_history.append(metrics)

            return SkillResult(
                skill_name=self.skill_name,
                level=level,
                content=compressed,
                tokens_used=estimate_tokens(compressed),
                execution_time=time.time() - start_time,
                metadata={
                    "conversation_type": conversation_type.value,
                    "original_chunks": len(chunks),
                    "compression_ratio": metrics.compression_ratio,
                    "information_retention": metrics.information_retention_score,
                    "semantic_coherence": metrics.semantic_coherence_score,
                    "budget_usage": budget.usage_percentage,
                },
                next_level_available=level != SkillLevel.FULL,
            )

        except Exception as e:
            logger.error(f"Context optimization failed: {e}")
            return SkillResult(
                skill_name=self.skill_name,
                level=level,
                content=f"Context optimization failed: {str(e)}",
                tokens_used=50,
                execution_time=time.time() - start_time,
                next_level_available=False,
            )

    def _detect_conversation_type(self, messages: list[dict[str, Any]]) -> ConversationType:
        """Detect conversation type for specialized optimization."""
        code_indicators = ["```", "def ", "class ", "import ", "function"]
        problem_indicators = ["error", "issue", "fix", "debug", "problem"]
        planning_indicators = ["plan", "implement", "create", "build", "design"]

        scores = {
            ConversationType.CODE_DEVELOPMENT: 0,
            ConversationType.PROBLEM_SOLVING: 0,
            ConversationType.PLANNING: 0,
            ConversationType.DISCUSSION: 0,
        }

        content = " ".join(msg.get("content", "").lower() for msg in messages)

        for indicator in code_indicators:
            if indicator in content:
                scores[ConversationType.CODE_DEVELOPMENT] += 1

        for indicator in problem_indicators:
            if indicator in content:
                scores[ConversationType.PROBLEM_SOLVING] += 1

        for indicator in planning_indicators:
            if indicator in content:
                scores[ConversationType.PLANNING] += 1

        # Default to discussion if no strong signals
        scores[ConversationType.DISCUSSION] = 0.5

        max_score = max(scores.values())
        if max_score < 1.0:
            return ConversationType.MIXED

        return max(scores, key=scores.get)

    def _create_context_chunks(self, messages: list[dict[str, Any]]) -> list[ContextChunk]:
        """Create enhanced context chunks with semantic analysis."""
        chunks = []

        for msg in messages:
            content = msg.get("content", "")
            if not content or len(content.strip()) < 10:
                continue

            role = msg.get("role", "unknown")
            timestamp_str = msg.get("timestamp", "")

            # Parse timestamp if available
            timestamp = datetime.now()
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except:
                    pass

            chunk = ContextChunk(
                content=content,
                importance_score=self._calculate_base_importance(content, role),
                source=role,
                chunk_type="message",
                timestamp=timestamp,
                references=self._extract_references(content),
            )

            chunks.append(chunk)

        return chunks

    def _calculate_base_importance(self, content: str, role: str) -> float:
        """Calculate base importance score for content."""
        score = 0.5  # Base score

        # Role-based importance
        if role == "user":
            score += 0.2  # User input is most important
        elif role == "assistant":
            score += 0.1  # Assistant responses are important
        elif role == "system":
            score -= 0.1  # System messages are less important

        # Content-based importance
        content_lower = content.lower()

        # High importance indicators
        high_importance = ["error", "fix", "implement", "decision", "important", "critical"]
        if any(indicator in content_lower for indicator in high_importance):
            score += 0.3

        # Code presence
        if "```" in content:
            score += 0.2

        # Question indicators (high importance for context)
        if any(q in content_lower for q in ["?", "question", "how", "why", "what"]):
            score += 0.1

        # Length-based adjustment (longer content may be more important)
        if len(content) > 500:
            score += 0.1
        elif len(content) < 50:
            score -= 0.1

        return min(max(score, 0.0), 1.0)

    def _extract_references(self, content: str) -> list[str]:
        """Extract references to previous messages or entities."""
        references = []

        # File references
        file_pattern = r"\b[\w\-_\.]+\.(py|js|ts|md|json|yaml|yml)\b"
        references.extend(re.findall(file_pattern, content))

        # URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        references.extend(re.findall(url_pattern, content))

        return list(set(references))

    def _score_semantic_importance(
        self, chunks: list[ContextChunk], conversation_type: ConversationType
    ) -> list[ContextChunk]:
        """Apply semantic importance scoring based on conversation type."""
        for chunk in chunks:
            # Type-specific importance adjustments
            if conversation_type == ConversationType.CODE_DEVELOPMENT:
                if "code" in chunk.semantic_tags:
                    chunk.importance_score += 0.3
                if "implementation" in chunk.semantic_tags:
                    chunk.importance_score += 0.2

            elif conversation_type == ConversationType.PROBLEM_SOLVING:
                if "error_resolution" in chunk.semantic_tags:
                    chunk.importance_score += 0.4
                if "question" in chunk.semantic_tags:
                    chunk.importance_score += 0.2

            elif conversation_type == ConversationType.PLANNING:
                if "decision" in chunk.semantic_tags:
                    chunk.importance_score += 0.3
                if "implementation" in chunk.semantic_tags:
                    chunk.importance_score += 0.1

            # Recency boost for recent messages
            hours_ago = (datetime.now() - chunk.timestamp).total_seconds() / 3600
            if hours_ago < 1:
                chunk.importance_score += 0.1
            elif hours_ago > 24:
                chunk.importance_score -= 0.1

            # Normalize importance score
            chunk.importance_score = min(max(chunk.importance_score, 0.0), 1.0)

        return chunks

    def _compress_metadata(self, chunks: list[ContextChunk], budget: ContextBudget) -> str:
        """Compress to metadata level - 95% reduction target."""
        # Sort by importance and take top chunks
        chunks.sort(key=lambda c: c.importance_score, reverse=True)

        metadata_items = []
        current_tokens = 0

        for chunk in chunks:
            # Create minimal metadata entry
            metadata = f"[{chunk.source}]"

            # Add key semantic tags
            if chunk.semantic_tags:
                important_tags = [
                    tag
                    for tag in chunk.semantic_tags[:2]
                    if tag in ["code", "error_resolution", "decision", "implementation"]
                ]
                if important_tags:
                    metadata += f" {', '.join(important_tags)}"

            # Add timestamp if recent
            hours_ago = (datetime.now() - chunk.timestamp).total_seconds() / 3600
            if hours_ago < 6:
                metadata += f" ({int(hours_ago)}h ago)"

            # Add reference count if any
            if chunk.references:
                metadata += f" [{len(chunk.references)} refs]"

            metadata_tokens = estimate_tokens(metadata)
            if current_tokens + metadata_tokens > budget.available_tokens:
                break

            metadata_items.append(metadata)
            current_tokens += metadata_tokens

        result = "# Context Summary (Metadata)\n\n"
        result += f"Conversation: {len(chunks)} messages spanning {(chunks[-1].timestamp - chunks[0].timestamp).total_seconds() / 3600:.1f}h\n\n"
        result += "Key interactions:\n"
        result += "\n".join(f"• {item}" for item in metadata_items)

        return result

    def _compress_summary(
        self, chunks: list[ContextChunk], budget: ContextBudget, conversation_type: ConversationType
    ) -> str:
        """Compress to summary level - 70% reduction target."""
        chunks.sort(key=lambda c: c.importance_score, reverse=True)

        summaries = []
        current_tokens = 0

        # Group chunks by semantic similarity
        semantic_groups = self._group_by_semantics(chunks)

        for group in semantic_groups:
            if not group:
                continue

            # Create summary for group
            group_summary = self._summarize_group(group, conversation_type)
            summary_tokens = estimate_tokens(group_summary)

            if current_tokens + summary_tokens > budget.available_tokens:
                break

            summaries.append(group_summary)
            current_tokens += summary_tokens

        result = "# Context Summary\n\n"
        result += f"Type: {conversation_type.value.replace('_', ' ').title()}\n"
        result += f"Messages: {len(chunks)} | Groups: {len(semantic_groups)}\n\n"
        result += "\n\n".join(summaries)

        return result

    def _compress_full(self, chunks: list[ContextChunk], budget: ContextBudget) -> str:
        """Compress to full level - most important content preserved."""
        chunks.sort(key=lambda c: c.importance_score, reverse=True)

        content_parts = []
        current_tokens = 0

        for chunk in chunks:
            content = chunk.content
            chunk_tokens = chunk.token_count

            if current_tokens + chunk_tokens > budget.available_tokens:
                # Try to include truncated version
                remaining_tokens = budget.available_tokens - current_tokens
                if remaining_tokens > 50:
                    truncated = self._smart_truncate(content, remaining_tokens)
                    content_parts.append(f"[{chunk.source}] {truncated}...")
                break

            content_parts.append(f"[{chunk.source}] {content}")
            current_tokens += chunk_tokens

        result = "# Context (Optimized)\n\n"
        result += "\n\n".join(content_parts)

        return result

    def _group_by_semantics(self, chunks: list[ContextChunk]) -> list[list[ContextChunk]]:
        """Group chunks by semantic similarity."""
        groups = defaultdict(list)

        for chunk in chunks:
            # Primary grouping by source and key tags
            primary_tag = chunk.source
            if chunk.semantic_tags:
                # Use most important semantic tag as primary grouping
                important_tags = ["code", "error_resolution", "decision", "implementation", "question"]
                for tag in important_tags:
                    if tag in chunk.semantic_tags:
                        primary_tag = tag
                        break

            groups[primary_tag].append(chunk)

        # Convert to list and sort groups by total importance
        sorted_groups = sorted(groups.values(), key=lambda g: sum(c.importance_score for c in g), reverse=True)

        return sorted_groups

    def _summarize_group(self, chunks: list[ContextChunk], conversation_type: ConversationType) -> str:
        """Create summary for a group of related chunks."""
        if not chunks:
            return ""

        # Take the most important chunk from the group
        main_chunk = max(chunks, key=lambda c: c.importance_score)

        # Create contextual summary
        summary = f"**{main_chunk.source.title()}**"

        # Add semantic context
        if main_chunk.semantic_tags:
            summary += f" ({', '.join(main_chunk.semantic_tags[:2])})"

        # Add core content summary
        content_summary = self._extract_key_points(main_chunk.content, conversation_type)
        summary += f": {content_summary}"

        # Add group size if multiple chunks
        if len(chunks) > 1:
            summary += f" [+{len(chunks) - 1} related]"

        return summary

    def _extract_key_points(self, content: str, conversation_type: ConversationType) -> str:
        """Extract key points based on conversation type."""
        if conversation_type == ConversationType.CODE_DEVELOPMENT:
            return self._extract_code_points(content)
        if conversation_type == ConversationType.PROBLEM_SOLVING:
            return self._extract_problem_points(content)
        if conversation_type == ConversationType.PLANNING:
            return self._extract_planning_points(content)
        return self._extract_general_points(content)

    def _extract_code_points(self, content: str) -> str:
        """Extract key points from code-related content."""
        lines = content.split("\n")
        key_lines = []

        for line in lines:
            line_stripped = line.strip()
            # Look for definitions, imports, and important comments
            if (
                any(pattern in line_stripped for pattern in ["def ", "class ", "import ", "from "])
                or line_stripped.startswith("#")
                and any(word in line_stripped.lower() for word in ["fix", "implement", "add", "todo"])
            ):
                key_lines.append(line_stripped)

        return "; ".join(key_lines[:3]) if key_lines else content[:100] + "..."

    def _extract_problem_points(self, content: str) -> str:
        """Extract key points from problem-solving content."""
        content_lower = content.lower()

        # Look for problem, solution, and error patterns
        problem_patterns = ["error:", "issue:", "problem:", "failed"]
        solution_patterns = ["fix:", "solution:", "resolved:", "implemented"]

        sentences = re.split(r"[.!?]+", content)
        key_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            sentence_lower = sentence.lower()
            if any(pattern in sentence_lower for pattern in problem_patterns + solution_patterns):
                key_sentences.append(sentence)

        return ". ".join(key_sentences[:2]) if key_sentences else content[:100] + "..."

    def _extract_planning_points(self, content: str) -> str:
        """Extract key points from planning content."""
        planning_patterns = ["plan:", "implement", "create", "build", "design", "decision:"]

        sentences = re.split(r"[.!?]+", content)
        key_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            if any(pattern in sentence.lower() for pattern in planning_patterns):
                key_sentences.append(sentence)

        return ". ".join(key_sentences[:2]) if key_sentences else content[:100] + "..."

    def _extract_general_points(self, content: str) -> str:
        """Extract key points from general content."""
        # Take first and last sentences, or first 100 chars
        sentences = re.split(r"[.!?]+", content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if len(sentences) >= 2:
            return f"{sentences[0]} [...] {sentences[-1]}"
        if sentences:
            return sentences[0]
        return content[:100] + "..."

    def _smart_truncate(self, content: str, max_tokens: int) -> str:
        """Intelligently truncate content to preserve meaning."""
        max_chars = max_tokens * 4  # Rough approximation

        if len(content) <= max_chars:
            return content

        # Try to truncate at sentence boundary
        truncated = content[:max_chars]
        last_period = truncated.rfind(".")

        if last_period > max_chars * 0.7:
            return truncated[: last_period + 1]

        # Try to truncate at word boundary
        last_space = truncated.rfind(" ")
        if last_space > max_chars * 0.8:
            return truncated[:last_space] + "..."

        return truncated + "..."

    def _calculate_metrics(
        self, original_chunks: list[ContextChunk], compressed: str, start_time: float
    ) -> ContextMetrics:
        """Calculate performance metrics for the optimization."""
        original_tokens = sum(c.token_count for c in original_chunks)
        compressed_tokens = estimate_tokens(compressed)

        compression_ratio = (original_tokens - compressed_tokens) / original_tokens if original_tokens > 0 else 0

        # Estimate information retention based on importance preservation
        total_importance = sum(c.importance_score for c in original_chunks)
        preserved_importance = 0  # This would need more sophisticated analysis

        # Simple coherence score based on structure preservation
        coherence_score = 1.0 - (compression_ratio * 0.2)  # Rough estimate

        return ContextMetrics(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compression_ratio,
            processing_time=time.time() - start_time,
            information_retention_score=min(preserved_importance / total_importance, 1.0)
            if total_importance > 0
            else 0.8,
            semantic_coherence_score=coherence_score,
        )

    def _empty_result(self, level: SkillLevel, start_time: float) -> SkillResult:
        """Return result for empty context."""
        return SkillResult(
            skill_name=self.skill_name,
            level=level,
            content="No context available for optimization.",
            tokens_used=10,
            execution_time=time.time() - start_time,
            next_level_available=False,
        )

    def get_optimization_recommendations(self, context: SkillContext) -> dict[str, Any]:
        """Provide optimization recommendations based on context analysis."""
        if not context.conversation_history:
            return {"recommendations": ["No conversation history to analyze"]}

        chunks = self._create_context_chunks(context.conversation_history)
        conversation_type = self._detect_conversation_type(context.conversation_history)

        recommendations = []

        # Analyze token usage
        total_tokens = sum(c.token_count for c in chunks)
        if total_tokens > 4000:
            recommendations.append("Consider aggressive compression for long conversations")

        # Analyze conversation patterns
        if conversation_type == ConversationType.CODE_DEVELOPMENT:
            recommendations.append("Preserve code blocks and implementation details")
        elif conversation_type == ConversationType.PROBLEM_SOLVING:
            recommendations.append("Focus on error messages and resolution steps")

        # Analyze semantic distribution
        semantic_counts = defaultdict(int)
        for chunk in chunks:
            for tag in chunk.semantic_tags:
                semantic_counts[tag] += 1

        if semantic_counts["code"] > len(chunks) * 0.5:
            recommendations.append("Heavy code content - prioritize syntax and structure")

        return {
            "conversation_type": conversation_type.value,
            "total_chunks": len(chunks),
            "total_tokens": total_tokens,
            "semantic_distribution": dict(semantic_counts),
            "recommendations": recommendations,
            "average_importance": sum(c.importance_score for c in chunks) / len(chunks) if chunks else 0,
        }
