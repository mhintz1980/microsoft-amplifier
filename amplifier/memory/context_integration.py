"""
Context Integration - Unified Context Management with Checkpointing

Integrates the checkpoint system with existing context management utilities.
Provides a unified interface for context compression, checkpointing, and restoration.

Key Features:
- Integration with context compactor
- Semantic importance scoring
- Progressive compression support
- Automatic context restoration
- Context analysis and optimization
- Memory system integration
"""

import logging
import re
from datetime import datetime
from typing import Any

from ..utils.context_compactor import ContextChunk
from ..utils.context_compactor import ContextLevel as CompactorLevel
from ..utils.context_compactor import create_context_chunk
from ..utils.context_compactor import get_context_compactor
from .checkpoint_manager import CheckpointLevel
from .checkpoint_manager import CheckpointManager
from .checkpoint_manager import get_checkpoint_manager
from .checkpoint_triggers import get_trigger_system

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextIntegration:
    """Integrates checkpoint system with context management"""

    def __init__(self, checkpoint_manager: CheckpointManager | None = None):
        """Initialize context integration

        Args:
            checkpoint_manager: Checkpoint manager instance, creates one if None
        """
        self.checkpoint_manager = checkpoint_manager or get_checkpoint_manager()
        self.trigger_system = get_trigger_system(self.checkpoint_manager)
        self.context_compactor = get_context_compactor()

        logger.info("ContextIntegration initialized")

    def create_context_checkpoint(
        self,
        context_chunks: list[ContextChunk],
        task_name: str,
        task_status: str = "in_progress",
        level: CheckpointLevel | None = None,
        additional_metadata: dict[str, Any] | None = None,
    ) -> str:
        """Create a checkpoint from context chunks with intelligent compression

        Args:
            context_chunks: List of context chunks to include
            task_name: Name of the current task
            task_status: Current task status
            level: Checkpoint detail level (auto-determined if None)
            additional_metadata: Additional metadata to include

        Returns:
            Checkpoint ID
        """
        # Determine appropriate checkpoint level based on context size
        if level is None:
            total_tokens = sum(len(chunk.content.split()) for chunk in context_chunks)
            if total_tokens > 50000:
                level = CheckpointLevel.COMPRESSED
            elif total_tokens > 20000:
                level = CheckpointLevel.ESSENTIAL
            else:
                level = CheckpointLevel.FULL

        # Create checkpoint content
        if level == CheckpointLevel.FULL:
            content = self._create_full_content(context_chunks)
        elif level == CheckpointLevel.COMPRESSED:
            content = self._create_compressed_content(context_chunks)
        elif level == CheckpointLevel.ESSENTIAL:
            content = self._create_essential_content(context_chunks)
        else:  # METADATA
            content = self._create_metadata_content(context_chunks)

        # Extract key findings from chunks
        key_findings = self._extract_key_findings(context_chunks)

        # Extract files mentioned in chunks
        files_modified = self._extract_file_references(context_chunks)

        # Generate next steps based on context
        next_steps = self._generate_next_steps(context_chunks)

        # Create the checkpoint
        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            task_name=task_name,
            task_status=task_status,
            level=level,
            trigger=self.checkpoint_manager.current_task and "auto_context" or "manual",
            key_findings=key_findings,
            files_modified=files_modified,
            next_steps=next_steps,
            content=content,
            additional_metadata={
                "context_integration": True,
                "chunk_count": len(context_chunks),
                "total_tokens": sum(len(chunk.content.split()) for chunk in context_chunks),
                "compression_level": level.value,
                **(additional_metadata or {}),
            },
        )

        logger.info(f"Created context checkpoint {checkpoint_id} with {len(context_chunks)} chunks")
        return checkpoint_id

    def restore_context_from_checkpoint(self, checkpoint_id: str) -> dict[str, Any]:
        """Restore context from a checkpoint with intelligent reconstruction

        Args:
            checkpoint_id: ID of checkpoint to restore

        Returns:
            Dictionary with restored context and metadata
        """
        # Restore basic checkpoint
        restored = self.checkpoint_manager.restore_checkpoint(checkpoint_id)
        if not restored:
            return {}

        checkpoint = restored["checkpoint"]

        # Enhance restoration with context reconstruction
        reconstructed_context = self._reconstruct_context(checkpoint)

        # Create context chunks from restored content
        context_chunks = self._create_chunks_from_restored(checkpoint, reconstructed_context)

        # Store restoration information
        restoration_metadata = {
            "restored_at": datetime.now().isoformat(),
            "checkpoint_age": datetime.now() - datetime.fromisoformat(checkpoint["timestamp"]),
            "chunks_reconstructed": len(context_chunks),
            "reconstruction_method": "context_integration",
        }

        return {
            "checkpoint": checkpoint,
            "context_chunks": [chunk.__dict__ for chunk in context_chunks],
            "reconstructed_context": reconstructed_context,
            "restoration_metadata": restoration_metadata,
            "task_context": restored["context"],
        }

    def analyze_and_optimize_context(self, context_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze context and provide optimization recommendations

        Args:
            context_data: Current context data

        Returns:
            Analysis results and recommendations
        """
        # Estimate current usage
        usage_percent = self.trigger_system.context_monitor.estimate_usage(context_data)
        usage_trend = self.trigger_system.context_monitor.get_usage_trend()

        # Analyze content patterns
        messages = context_data.get("messages", [])
        files = context_data.get("files", {})

        # Create context chunks for analysis
        context_chunks = []
        for i, msg in enumerate(messages):
            chunk = create_context_chunk(
                content=msg.get("content", ""),
                source=f"message_{i}",
                chunk_type="message",
                importance_score=0.7,  # Messages are generally important
                tags=["conversation", msg.get("role", "unknown")],
            )
            context_chunks.append(chunk)

        for file_path, file_content in files.items():
            if isinstance(file_content, str):
                chunk = create_context_chunk(
                    content=file_content,
                    source=file_path,
                    chunk_type="code",
                    importance_score=0.8,  # Files are typically important
                    tags=["file", "code"],
                    references=[file_path],
                )
                context_chunks.append(chunk)

        # Analyze chunks with context compactor
        analysis_results = {}
        if context_chunks:
            # Add chunks to compactor for analysis
            for chunk in context_chunks:
                self.context_compactor.add_context_chunk(chunk)

            # Get compression stats
            analysis_results["compression_stats"] = self.context_compactor.get_compression_stats()
            analysis_results["context_analytics"] = self.context_compactor.get_context_analytics()

        # Generate recommendations
        recommendations = self._generate_recommendations(usage_percent, usage_trend, analysis_results)

        return {
            "current_usage": usage_percent,
            "usage_trend": usage_trend,
            "analysis_results": analysis_results,
            "recommendations": recommendations,
            "checkpoint_suggestion": self._suggest_checkpoint_action(usage_percent, usage_trend),
        }

    def create_smart_checkpoint(
        self,
        task_name: str,
        context_data: dict[str, Any] | None = None,
        importance_threshold: float = 0.5,
    ) -> str | None:
        """Create an intelligent checkpoint based on current context

        Args:
            task_name: Name of the current task
            context_data: Current context data
            importance_threshold: Minimum importance for content inclusion

        Returns:
            Checkpoint ID or None if no significant content
        """
        if not context_data:
            return None

        # Create context chunks from current context
        context_chunks = self._create_chunks_from_context_data(context_data, importance_threshold)

        if not context_chunks:
            logger.info("No significant content for checkpoint")
            return None

        # Analyze and determine best checkpoint strategy
        analysis = self.analyze_and_optimize_context(context_data)

        # Choose checkpoint level based on analysis
        if analysis["current_usage"] > 75:
            level = CheckpointLevel.COMPRESSED
        elif analysis["current_usage"] > 50:
            level = CheckpointLevel.ESSENTIAL
        else:
            level = CheckpointLevel.FULL

        # Create the checkpoint
        checkpoint_id = self.create_context_checkpoint(
            context_chunks=context_chunks,
            task_name=task_name,
            level=level,
            additional_metadata={
                "smart_checkpoint": True,
                "importance_threshold": importance_threshold,
                "context_analysis": analysis,
            },
        )

        return checkpoint_id

    # Private methods

    def _create_full_content(self, context_chunks: list[ContextChunk]) -> str:
        """Create full content from context chunks"""
        content_parts = ["# Full Context Checkpoint\n"]

        # Group chunks by source
        sources = {}
        for chunk in context_chunks:
            source = chunk.source
            if source not in sources:
                sources[source] = []
            sources[source].append(chunk)

        # Organize by source
        for source, chunks in sources.items():
            content_parts.append(f"## {source}\n")
            for chunk in chunks:
                content_parts.append(f"### {chunk.chunk_type}\n")
                content_parts.append(f"{chunk.content}\n")
                if chunk.tags:
                    content_parts.append(f"Tags: {', '.join(chunk.tags)}\n")
                content_parts.append("---\n")

        return "\n".join(content_parts)

    def _create_compressed_content(self, context_chunks: list[ContextChunk]) -> str:
        """Create compressed content using context compactor"""
        try:
            # Use context compactor for intelligent compression
            compact_context = self.context_compactor.compress_context(
                context_chunks,
                CompactorLevel.SUMMARY,
                max_tokens=20000,
            )
            return f"# Compressed Context Checkpoint\n\n{compact_context.content}"
        except Exception as e:
            logger.warning(f"Context compression failed: {e}, using simple compression")
            return self._create_simple_compressed_content(context_chunks)

    def _create_essential_content(self, context_chunks: list[ContextChunk]) -> str:
        """Create essential content (critical points only)"""
        content_parts = ["# Essential Points Checkpoint\n"]

        # Sort by importance
        sorted_chunks = sorted(context_chunks, key=lambda c: c.importance_score, reverse=True)

        # Extract essential points from top chunks
        for chunk in sorted_chunks[:10]:  # Top 10 most important
            content_parts.append(f"## {chunk.source} ({chunk.chunk_type})\n")

            # Extract key points
            sentences = chunk.content.split(".")
            important_sentences = []

            for sentence in sentences[:5]:  # Top 5 sentences
                sentence = sentence.strip()
                if sentence and any(
                    keyword in sentence.lower()
                    for keyword in ["important", "critical", "key", "error", "fix", "implement"]
                ):
                    important_sentences.append(sentence)

            if important_sentences:
                content_parts.extend(f"- {s}." for s in important_sentences)
            else:
                # Include first sentence if no important ones found
                first_sentence = sentences[0].strip() if sentences else ""
                if first_sentence:
                    content_parts.append(f"- {first_sentence}.")

            content_parts.append("\n")

        return "\n".join(content_parts)

    def _create_metadata_content(self, context_chunks: list[ContextChunk]) -> str:
        """Create metadata-only content"""
        content_parts = ["# Metadata Checkpoint\n"]

        # Summary statistics
        content_parts.append("## Summary\n")
        content_parts.append(f"- Total chunks: {len(context_chunks)}")
        content_parts.append(f"- Sources: {len(set(c.source for c in context_chunks))}")
        content_parts.append(
            f"- Average importance: {sum(c.importance_score for c in context_chunks) / len(context_chunks):.2f}"
        )
        content_parts.append("\n")

        # Sources breakdown
        sources = {}
        for chunk in context_chunks:
            sources[chunk.source] = sources.get(chunk.source, 0) + 1

        content_parts.append("## Sources\n")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            content_parts.append(f"- {source}: {count} chunks")
        content_parts.append("\n")

        # Tags summary
        all_tags = []
        for chunk in context_chunks:
            all_tags.extend(chunk.tags)

        if all_tags:
            from collections import Counter

            tag_counts = Counter(all_tags)
            content_parts.append("## Top Tags\n")
            for tag, count in tag_counts.most_common(10):
                content_parts.append(f"- {tag}: {count}")
            content_parts.append("\n")

        return "\n".join(content_parts)

    def _create_simple_compressed_content(self, context_chunks: list[ContextChunk]) -> str:
        """Fallback simple compression"""
        content_parts = ["# Compressed Context (Simple)\n"]

        # Sort by importance and include top content
        sorted_chunks = sorted(context_chunks, key=lambda c: c.importance_score, reverse=True)

        for chunk in sorted_chunks[:20]:  # Top 20 chunks
            content_parts.append(f"## {chunk.source}\n")
            # Include first 200 characters
            content = chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
            content_parts.append(f"{content}\n")

        return "\n".join(content_parts)

    def _extract_key_findings(self, context_chunks: list[ContextChunk]) -> list[str]:
        """Extract key findings from context chunks"""
        findings = []

        # Look for high-importance chunks with decision indicators
        decision_keywords = ["decided", "conclusion", "agreed", "determined", "selected"]
        error_keywords = ["error", "issue", "problem", "bug", "failure"]
        solution_keywords = ["fix", "solution", "implement", "create", "resolve"]

        for chunk in context_chunks:
            if chunk.importance_score > 0.7:
                content_lower = chunk.content.lower()

                # Check for decisions
                if any(keyword in content_lower for keyword in decision_keywords):
                    findings.append(f"Decision: {chunk.source} - {chunk.content[:100]}...")

                # Check for errors/solutions
                if any(keyword in content_lower for keyword in error_keywords):
                    findings.append(f"Issue: {chunk.source} - {chunk.content[:100]}...")

                if any(keyword in content_lower for keyword in solution_keywords):
                    findings.append(f"Solution: {chunk.source} - {chunk.content[:100]}...")

        return findings[:10]  # Limit to top 10 findings

    def _extract_file_references(self, context_chunks: list[ContextChunk]) -> list[str]:
        """Extract file references from context chunks"""
        import re

        file_patterns = [
            r"[^\s]+\.(py|js|ts|json|md|txt|yaml|yml|html|css)",
            r"[^\s]+/[^\s]+",  # General path pattern
        ]

        files = set()
        for chunk in context_chunks:
            for pattern in file_patterns:
                matches = re.findall(pattern, chunk.content)
                files.update(matches)

        return list(files)[:20]  # Limit to top 20 files

    def _generate_next_steps(self, context_chunks: list[ContextChunk]) -> list[str]:
        """Generate next steps based on context"""
        next_steps = []

        # Look for incomplete work or TODO items
        todo_patterns = [
            r"(?i)(?:TODO|FIXME|XXX):\s*(.+)",
            r"(?i)need\s+to\s+(.+)",
            r"(?i)should\s+(.+)",
            r"(?i)(?:implement|create|add|fix)\s+(.+)",
        ]

        for chunk in context_chunks:
            for pattern in todo_patterns:
                matches = re.findall(pattern, chunk.content)
                for match in matches:
                    if len(match.strip()) > 5:  # Filter out very short matches
                        next_steps.append(f"{match.strip()} (from {chunk.source})")

        return next_steps[:10]  # Limit to top 10 next steps

    def _reconstruct_context(self, checkpoint: dict[str, Any]) -> str:
        """Reconstruct detailed context from checkpoint"""
        content_parts = [f"# Reconstructed Context from {checkpoint['timestamp']}"]
        content_parts.append(f"Task: {checkpoint['task_name']}")
        content_parts.append(f"Status: {checkpoint['task_status']}")
        content_parts.append("")

        # Include key findings
        if checkpoint["key_findings"]:
            content_parts.append("## Key Findings\n")
            for finding in checkpoint["key_findings"]:
                content_parts.append(f"- {finding}")
            content_parts.append("")

        # Include next steps
        if checkpoint["next_steps"]:
            content_parts.append("## Next Steps\n")
            for step in checkpoint["next_steps"]:
                content_parts.append(f"- {step}")
            content_parts.append("")

        # Include files modified
        if checkpoint["files_modified"]:
            content_parts.append("## Files Modified\n")
            for file_path in checkpoint["files_modified"]:
                content_parts.append(f"- {file_path}")
            content_parts.append("")

        # Include original content
        if checkpoint["content"]:
            content_parts.append("## Original Content\n")
            content_parts.append(checkpoint["content"])

        return "\n".join(content_parts)

    def _create_chunks_from_restored(
        self, checkpoint: dict[str, Any], reconstructed_context: str
    ) -> list[ContextChunk]:
        """Create context chunks from restored checkpoint"""
        chunks = []

        # Create main content chunk
        main_chunk = create_context_chunk(
            content=reconstructed_context,
            source=f"checkpoint_{checkpoint['checkpoint_id']}",
            chunk_type="restored_context",
            importance_score=0.9,  # Restored content is highly important
            tags=["restored", "checkpoint", checkpoint["task_name"]],
            references=checkpoint["files_modified"],
        )
        chunks.append(main_chunk)

        # Create separate chunks for key findings
        for finding in checkpoint["key_findings"]:
            finding_chunk = create_context_chunk(
                content=finding,
                source=f"checkpoint_{checkpoint['checkpoint_id']}",
                chunk_type="key_finding",
                importance_score=0.8,
                tags=["key_finding", checkpoint["task_name"]],
            )
            chunks.append(finding_chunk)

        # Create chunks for next steps
        for step in checkpoint["next_steps"]:
            step_chunk = create_context_chunk(
                content=step,
                source=f"checkpoint_{checkpoint['checkpoint_id']}",
                chunk_type="next_step",
                importance_score=0.7,
                tags=["next_step", checkpoint["task_name"]],
            )
            chunks.append(step_chunk)

        return chunks

    def _create_chunks_from_context_data(
        self, context_data: dict[str, Any], importance_threshold: float
    ) -> list[ContextChunk]:
        """Create context chunks from general context data"""
        chunks = []

        # Process messages
        messages = context_data.get("messages", [])
        for i, msg in enumerate(messages):
            content = msg.get("content", "")
            if not content:
                continue

            # Calculate importance based on content
            importance = self._calculate_content_importance(content)
            if importance < importance_threshold:
                continue

            chunk = create_context_chunk(
                content=content,
                source=f"message_{i}",
                chunk_type="message",
                importance_score=importance,
                tags=["conversation", msg.get("role", "unknown")],
            )
            chunks.append(chunk)

        # Process files
        files = context_data.get("files", {})
        for file_path, file_content in files.items():
            if not isinstance(file_content, str) or not file_content:
                continue

            # Files are typically important
            importance = self._calculate_content_importance(file_content, boost=0.2)
            if importance < importance_threshold:
                continue

            chunk = create_context_chunk(
                content=file_content,
                source=file_path,
                chunk_type="code",
                importance_score=importance,
                tags=["file", "code"],
                references=[file_path],
            )
            chunks.append(chunk)

        return chunks

    def _calculate_content_importance(self, content: str, boost: float = 0.0) -> float:
        """Calculate importance score for content"""
        if not content:
            return 0.0

        importance = 0.5 + boost  # Base importance

        # Boost for technical content
        technical_keywords = ["function", "class", "import", "error", "fix", "implement", "create"]
        tech_count = sum(1 for keyword in technical_keywords if keyword in content.lower())
        importance += min(0.3, tech_count * 0.05)

        # Boost for important indicators
        important_keywords = ["critical", "important", "key", "essential", "error", "fix", "solution"]
        imp_count = sum(1 for keyword in important_keywords if keyword in content.lower())
        importance += min(0.2, imp_count * 0.04)

        # Length factor (moderate length is more important)
        word_count = len(content.split())
        if 50 <= word_count <= 500:
            importance += 0.1
        elif word_count > 1000:
            importance -= 0.1  # Very long content might be less relevant

        return min(1.0, importance)

    def _generate_recommendations(
        self, usage_percent: int, usage_trend: str, analysis_results: dict[str, Any]
    ) -> list[str]:
        """Generate optimization recommendations"""
        recommendations = []

        if usage_percent > 80:
            recommendations.append("High context usage detected - consider creating a compressed checkpoint")
        elif usage_percent > 60:
            recommendations.append("Moderate context usage - monitor for further increases")

        if usage_trend == "increasing":
            recommendations.append("Context usage is trending upward - plan for checkpointing")
        elif usage_trend == "decreasing":
            recommendations.append("Context usage is decreasing - good optimization")

        # Add analysis-based recommendations
        if "compression_stats" in analysis_results:
            stats = analysis_results["compression_stats"]
            if stats.get("overall_compression_ratio", 1.0) > 0.5:
                recommendations.append("Good compression potential - consider using compressed checkpoints")

        if not recommendations:
            recommendations.append("Context usage is optimal - continue current approach")

        return recommendations

    def _suggest_checkpoint_action(self, usage_percent: int, usage_trend: str) -> dict[str, Any]:
        """Suggest appropriate checkpoint action"""
        if usage_percent > 80:
            return {
                "action": "create_compressed_checkpoint",
                "urgency": "high",
                "reason": "Very high context usage",
                "level": CheckpointLevel.COMPRESSED.value,
            }
        if usage_percent > 60 or usage_trend == "increasing":
            return {
                "action": "create_essential_checkpoint",
                "urgency": "medium",
                "reason": "Moderate usage or increasing trend",
                "level": CheckpointLevel.ESSENTIAL.value,
            }
        return {
            "action": "monitor",
            "urgency": "low",
            "reason": "Context usage is manageable",
            "level": CheckpointLevel.FULL.value,
        }


# Global context integration instance
_context_integration: ContextIntegration | None = None


def get_context_integration(checkpoint_manager: CheckpointManager | None = None) -> ContextIntegration:
    """Get the global context integration instance"""
    global _context_integration
    if _context_integration is None:
        _context_integration = ContextIntegration(checkpoint_manager)
    return _context_integration
