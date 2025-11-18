"""
Context Memory Integration Module

Connects context optimization with memory systems for persistent
context management and cross-session continuity.

Implements ruthless simplicity while providing powerful
context persistence and retrieval capabilities.
"""

import json
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Any

from ..memory.core import MemoryStore
from ..memory.models import Memory
from ..utils.logger import get_logger
from .context_optimization import ContextChunk
from .context_optimization import ContextMetrics
from .context_optimization import ConversationType

logger = get_logger(__name__)


class ContextMemoryIntegration:
    """
    Integration layer between context optimization and memory systems.

    Provides persistent storage for optimized contexts, metrics tracking,
    and cross-session context continuity.
    """

    def __init__(self, memory_store: MemoryStore | None = None, data_dir: Path | None = None):
        """Initialize context memory integration.

        Args:
            memory_store: Existing memory store instance, creates new if None
            data_dir: Data directory for context-specific storage
        """
        self.memory_store = memory_store or MemoryStore(data_dir=data_dir)
        self.data_dir = data_dir or Path(".data")
        self.context_data_file = self.data_dir / "context_sessions.json"

        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Context memory integration initialized")

    def save_optimized_context(
        self,
        chunks: list[ContextChunk],
        optimized_content: str,
        metrics: ContextMetrics,
        conversation_type: ConversationType,
        session_id: str | None = None,
    ) -> str:
        """Save optimized context to memory with metadata.

        Args:
            chunks: Original context chunks
            optimized_content: Compressed/optimized content
            metrics: Performance metrics from optimization
            conversation_type: Type of conversation
            session_id: Optional session identifier

        Returns:
            Memory ID for the saved context
        """
        # Create comprehensive memory entry
        memory_data = {
            "type": "optimized_context",
            "content": optimized_content,
            "metadata": {
                "conversation_type": conversation_type.value,
                "original_chunks": len(chunks),
                "compression_ratio": metrics.compression_ratio,
                "processing_time": metrics.processing_time,
                "information_retention": metrics.information_retention_score,
                "semantic_coherence": metrics.semantic_coherence_score,
                "original_tokens": metrics.original_tokens,
                "compressed_tokens": metrics.compressed_tokens,
                "session_id": session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "chunk_summary": self._create_chunk_summary(chunks),
                "optimization_level": self._determine_optimization_level(metrics.compression_ratio),
                "tags": self._extract_context_tags(chunks),
            },
        }

        # Store in memory system
        memory = Memory(
            content=f"Optimized Context ({conversation_type.value}): {len(chunks)} chunks compressed",
            category="preference",  # Use preference category for context optimizations
            metadata=memory_data["metadata"],
        )

        stored_memory = self.memory_store.add_memory(memory)

        # Also save detailed context data for reconstruction
        self._save_detailed_context(session_id, chunks, optimized_content, metrics, conversation_type)

        logger.info(
            f"Saved optimized context with {len(chunks)} chunks, compression ratio: {metrics.compression_ratio:.2%}"
        )

        return stored_memory.id

    def retrieve_relevant_context(
        self,
        query: str,
        conversation_type: ConversationType | None = None,
        max_contexts: int = 5,
        time_range_hours: int | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant optimized contexts based on query and criteria.

        Args:
            query: Search query for relevance matching
            conversation_type: Filter by conversation type
            max_contexts: Maximum number of contexts to return
            time_range_hours: Only return contexts within this time range

        Returns:
            List of relevant context entries with metadata
        """
        # Get recent memories that might contain context optimizations
        recent_memories = self.memory_store.search_recent(limit=50)

        relevant_contexts = []
        current_time = datetime.now()

        for memory in recent_memories:
            # Check if this is an optimized context
            if memory.metadata.get("type") != "optimized_context":
                continue

            # Check conversation type filter
            if conversation_type and memory.metadata.get("conversation_type") != conversation_type.value:
                continue

            # Check time range filter
            if time_range_hours:
                context_age = (current_time - memory.timestamp).total_seconds() / 3600
                if context_age > time_range_hours:
                    continue

            # Calculate relevance score based on query
            relevance_score = self._calculate_relevance(query, memory.content, memory.metadata)

            if relevance_score > 0.3:  # Minimum relevance threshold
                relevant_contexts.append(
                    {
                        "memory_id": memory.id,
                        "content": memory.content,
                        "metadata": memory.metadata,
                        "relevance_score": relevance_score,
                        "timestamp": memory.timestamp,
                        "accessed_count": memory.accessed_count,
                    }
                )

        # Sort by relevance and return top results
        relevant_contexts.sort(key=lambda c: c["relevance_score"], reverse=True)

        return relevant_contexts[:max_contexts]

    def get_context_metrics_history(self, session_id: str | None = None, days_back: int = 7) -> list[ContextMetrics]:
        """Get historical context optimization metrics.

        Args:
            session_id: Filter by specific session
            days_back: Number of days to look back

        Returns:
            List of context metrics
        """
        # Load detailed context data
        detailed_data = self._load_detailed_context_data()

        metrics_list = []
        cutoff_time = datetime.now() - timedelta(days=days_back)

        for context_entry in detailed_data.get("contexts", []):
            # Check session filter
            if session_id and context_entry.get("session_id") != session_id:
                continue

            # Check time filter
            try:
                entry_time = datetime.fromisoformat(context_entry.get("timestamp", ""))
                if entry_time < cutoff_time:
                    continue
            except:
                continue

            # Extract metrics
            metrics = ContextMetrics(
                original_tokens=context_entry.get("original_tokens", 0),
                compressed_tokens=context_entry.get("compressed_tokens", 0),
                compression_ratio=context_entry.get("compression_ratio", 0.0),
                processing_time=context_entry.get("processing_time", 0.0),
                information_retention_score=context_entry.get("information_retention", 0.0),
                semantic_coherence_score=context_entry.get("semantic_coherence", 0.0),
            )

            metrics_list.append(metrics)

        return metrics_list

    def generate_context_insights(self, days_back: int = 7) -> dict[str, Any]:
        """Generate insights from context optimization history.

        Args:
            days_back: Number of days to analyze

        Returns:
            Dictionary with insights and recommendations
        """
        metrics_history = self.get_context_metrics_history(days_back=days_back)

        if not metrics_history:
            return {
                "insights": ["No context optimization history available"],
                "recommendations": ["Start using context optimization to gather insights"],
                "statistics": {},
            }

        # Calculate statistics
        avg_compression = sum(m.compression_ratio for m in metrics_history) / len(metrics_history)
        avg_processing_time = sum(m.processing_time for m in metrics_history) / len(metrics_history)
        avg_retention = sum(m.information_retention_score for m in metrics_history) / len(metrics_history)

        total_original_tokens = sum(m.original_tokens for m in metrics_history)
        total_compressed_tokens = sum(m.compressed_tokens for m in metrics_history)
        total_tokens_saved = total_original_tokens - total_compressed_tokens

        # Generate insights
        insights = []
        recommendations = []

        if avg_compression > 0.7:
            insights.append(f"Excellent compression performance: {avg_compression:.1%} average reduction")
        elif avg_compression > 0.5:
            insights.append(f"Good compression performance: {avg_compression:.1%} average reduction")
        else:
            insights.append(f"Moderate compression performance: {avg_compression:.1%} average reduction")
            recommendations.append("Consider using higher compression levels for better token efficiency")

        if avg_retention > 0.8:
            insights.append(f"High information retention: {avg_retention:.1%} average")
        elif avg_retention < 0.6:
            insights.append(f"Low information retention: {avg_retention:.1%} average")
            recommendations.append("Review compression settings to preserve more critical information")

        if avg_processing_time > 2.0:
            insights.append(f"Processing time is high: {avg_processing_time:.2f}s average")
            recommendations.append("Consider optimizing context processing for better performance")

        if total_tokens_saved > 10000:
            insights.append(f"Significant token savings: {total_tokens_saved:,} tokens saved in {days_back} days")

        # Analyze conversation types
        detailed_data = self._load_detailed_context_data()
        conversation_types = defaultdict(int)

        for context_entry in detailed_data.get("contexts", []):
            conv_type = context_entry.get("conversation_type", "unknown")
            conversation_types[conv_type] += 1

        if conversation_types:
            most_common_type = max(conversation_types, key=conversation_types.get)
            insights.append(f"Most common conversation type: {most_common_type.replace('_', ' ').title()}")

        return {
            "insights": insights,
            "recommendations": recommendations,
            "statistics": {
                "total_optimizations": len(metrics_history),
                "average_compression": avg_compression,
                "average_processing_time": avg_processing_time,
                "average_information_retention": avg_retention,
                "total_tokens_saved": total_tokens_saved,
                "conversation_types": dict(conversation_types),
                "period_days": days_back,
            },
        }

    def create_context_checkpoint(
        self, session_id: str, chunks: list[ContextChunk], checkpoint_name: str | None = None
    ) -> str:
        """Create a checkpoint of current context state.

        Args:
            session_id: Session identifier
            chunks: Current context chunks
            checkpoint_name: Optional descriptive name

        Returns:
            Checkpoint ID
        """
        checkpoint_data = {
            "session_id": session_id,
            "name": checkpoint_name or f"checkpoint_{datetime.now().strftime('%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "chunks": [
                {
                    "content": chunk.content,
                    "importance_score": chunk.importance_score,
                    "source": chunk.source,
                    "semantic_tags": chunk.semantic_tags,
                    "timestamp": chunk.timestamp.isoformat(),
                }
                for chunk in chunks
            ],
            "total_chunks": len(chunks),
            "total_tokens": sum(chunk.token_count for chunk in chunks),
        }

        # Save checkpoint
        checkpoints_file = self.data_dir / "context_checkpoints.json"

        try:
            if checkpoints_file.exists():
                with open(checkpoints_file) as f:
                    checkpoints_data = json.load(f)
            else:
                checkpoints_data = {"checkpoints": []}
        except:
            checkpoints_data = {"checkpoints": []}

        checkpoints_data["checkpoints"].append(checkpoint_data)

        # Keep only last 20 checkpoints
        checkpoints_data["checkpoints"] = checkpoints_data["checkpoints"][-20:]

        with open(checkpoints_file, "w") as f:
            json.dump(checkpoints_data, f, indent=2)

        checkpoint_id = f"{session_id}_{len(checkpoints_data['checkpoints'])}"
        logger.info(f"Created context checkpoint: {checkpoint_id}")

        return checkpoint_id

    def restore_context_checkpoint(self, checkpoint_id: str) -> list[ContextChunk] | None:
        """Restore context chunks from checkpoint.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            List of restored context chunks, None if not found
        """
        checkpoints_file = self.data_dir / "context_checkpoints.json"

        if not checkpoints_file.exists():
            return None

        try:
            with open(checkpoints_file) as f:
                checkpoints_data = json.load(f)
        except:
            return None

        # Find checkpoint
        for checkpoint in checkpoints_data.get("checkpoints", []):
            current_id = f"{checkpoint['session_id']}_{len([c for c in checkpoints_data['checkpoints'] if c['timestamp'] <= checkpoint['timestamp']])}"
            if current_id == checkpoint_id:
                # Restore chunks
                chunks = []
                for chunk_data in checkpoint.get("chunks", []):
                    chunk = ContextChunk(
                        content=chunk_data["content"],
                        importance_score=chunk_data["importance_score"],
                        source=chunk_data["source"],
                        chunk_type="message",
                        semantic_tags=chunk_data.get("semantic_tags", []),
                        timestamp=datetime.fromisoformat(chunk_data["timestamp"]),
                    )
                    chunks.append(chunk)

                logger.info(f"Restored {len(chunks)} chunks from checkpoint: {checkpoint_id}")
                return chunks

        return None

    # Private helper methods

    def _create_chunk_summary(self, chunks: list[ContextChunk]) -> dict[str, Any]:
        """Create summary of chunks for metadata."""
        sources = defaultdict(int)
        semantic_tags = defaultdict(int)
        total_importance = 0

        for chunk in chunks:
            sources[chunk.source] += 1
            for tag in chunk.semantic_tags:
                semantic_tags[tag] += 1
            total_importance += chunk.importance_score

        return {
            "sources": dict(sources),
            "semantic_tags": dict(semantic_tags),
            "total_chunks": len(chunks),
            "average_importance": total_importance / len(chunks) if chunks else 0,
            "total_tokens": sum(chunk.token_count for chunk in chunks),
        }

    def _extract_context_tags(self, chunks: list[ContextChunk]) -> list[str]:
        """Extract key tags from context chunks."""
        all_tags = []
        for chunk in chunks:
            all_tags.extend(chunk.semantic_tags)

        # Return most common tags
        tag_counts = defaultdict(int)
        for tag in all_tags:
            tag_counts[tag] += 1

        return [tag for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

    def _determine_optimization_level(self, compression_ratio: float) -> str:
        """Determine optimization level based on compression ratio."""
        if compression_ratio >= 0.9:
            return "metadata"
        if compression_ratio >= 0.6:
            return "essential"
        if compression_ratio >= 0.3:
            return "summary"
        return "full"

    def _save_detailed_context(
        self,
        session_id: str | None,
        chunks: list[ContextChunk],
        optimized_content: str,
        metrics: ContextMetrics,
        conversation_type: ConversationType,
    ):
        """Save detailed context data for reconstruction."""
        try:
            if self.context_data_file.exists():
                with open(self.context_data_file) as f:
                    data = json.load(f)
            else:
                data = {"contexts": [], "metadata": {"version": "1.0"}}
        except:
            data = {"contexts": [], "metadata": {"version": "1.0"}}

        context_entry = {
            "session_id": session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "conversation_type": conversation_type.value,
            "optimized_content": optimized_content,
            "original_chunks": len(chunks),
            "original_tokens": metrics.original_tokens,
            "compressed_tokens": metrics.compressed_tokens,
            "compression_ratio": metrics.compression_ratio,
            "processing_time": metrics.processing_time,
            "information_retention": metrics.information_retention_score,
            "semantic_coherence": metrics.semantic_coherence_score,
            "chunk_summary": self._create_chunk_summary(chunks),
        }

        data["contexts"].append(context_entry)

        # Keep only last 100 contexts
        data["contexts"] = data["contexts"][-100:]

        with open(self.context_data_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load_detailed_context_data(self) -> dict[str, Any]:
        """Load detailed context data."""
        try:
            if self.context_data_file.exists():
                with open(self.context_data_file) as f:
                    return json.load(f)
        except:
            pass

        return {"contexts": [], "metadata": {"version": "1.0"}}

    def _calculate_relevance(self, query: str, content: str, metadata: dict[str, Any]) -> float:
        """Calculate relevance score for context matching."""
        query_lower = query.lower()
        content_lower = content.lower()

        score = 0.0

        # Exact phrase matches
        if query_lower in content_lower:
            score += 0.8

        # Word matches
        query_words = query_lower.split()
        content_words = content_lower.split()

        matching_words = set(query_words) & set(content_words)
        if query_words:
            score += len(matching_words) / len(query_words) * 0.5

        # Conversation type matching
        conv_type = metadata.get("conversation_type", "")
        if conv_type and conv_type in query_lower:
            score += 0.3

        # Tag matching
        tags = metadata.get("tags", [])
        for tag in tags:
            if tag.lower() in query_lower:
                score += 0.2

        return min(score, 1.0)
