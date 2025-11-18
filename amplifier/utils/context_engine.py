"""
Intelligent Context Management Engine

Provides intelligent context management based on conversation patterns,
user behavior, and system performance metrics.

Key Features:
- Just-in-time context retrieval
- Progressive context loading
- Memory consolidation patterns
- Performance-aware context management
- Automatic context pruning and consolidation
"""

import asyncio
import json
import time
from collections import defaultdict
from collections import deque
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from .context_compactor import CompactContext
from .context_compactor import ContextChunk
from .context_compactor import ContextLevel
from .context_compactor import get_context_compactor
from .logger import get_logger

logger = get_logger(__name__)


class ContextStrategy(Enum):
    """Context management strategies."""

    PROGRESSIVE = "progressive"  # Load progressively as needed
    PREDICTIVE = "predictive"  # Preload likely relevant context
    CONSERVATIVE = "conservative"  # Keep more context, less aggressive pruning
    AGGRESSIVE = "aggressive"  # Aggressive pruning for minimal context


@dataclass
class ContextRequest:
    """A request for context with specific requirements."""

    request_id: str
    query: str
    max_tokens: int
    priority: int = 1  # 1-5, 5 being highest
    topics: list[str] = field(default_factory=list)
    time_range: tuple[datetime, datetime] | None = None
    required_sources: list[str] = field(default_factory=list)
    context_types: list[str] = field(default_factory=list)
    strategy: ContextStrategy = ContextStrategy.PROGRESSIVE


@dataclass
class ContextResponse:
    """Response to a context request."""

    request_id: str
    content: str
    tokens_used: int
    chunks_included: int
    chunks_skipped: int
    compression_level: ContextLevel
    retrieval_time: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryConsolidation:
    """Represents a memory consolidation event."""

    timestamp: datetime
    original_chunks: int
    consolidated_chunks: int
    compression_ratio: float
    key_topics: list[str]
    importance_score: float
    compact_context: CompactContext


class ContextEngine:
    """Intelligent context management engine."""

    def __init__(
        self,
        max_working_memory: int = 50000,
        consolidation_threshold: int = 100,
        strategy: ContextStrategy = ContextStrategy.PROGRESSIVE,
    ):
        self.max_working_memory = max_working_memory
        self.consolidation_threshold = consolidation_threshold
        self.strategy = strategy

        # Context storage
        self.working_memory: deque[ContextChunk] = deque(maxlen=1000)
        self.consolidated_memory: list[MemoryConsolidation] = []
        self.context_index: dict[str, list[ContextChunk]] = defaultdict(list)

        # Performance tracking
        self.request_history: deque[ContextRequest] = deque(maxlen=1000)
        self.response_history: deque[ContextResponse] = deque(maxlen=1000)
        self.access_patterns: dict[str, int] = defaultdict(int)
        self.topic_popularity: dict[str, int] = defaultdict(int)

        # Context compactor
        self.compactor = get_context_compactor()

        # Background tasks
        self.consolidation_task: asyncio.Task | None = None
        self.cleanup_task: asyncio.Task | None = None

    async def initialize(self):
        """Initialize the context engine and start background tasks."""
        logger.info("Initializing context engine")

        # Start background consolidation task
        self.consolidation_task = asyncio.create_task(self._periodic_consolidation())
        self.cleanup_task = asyncio.create_task(self._periodic_cleanup())

        logger.info("Context engine initialized successfully")

    async def shutdown(self):
        """Shutdown the context engine and cleanup resources."""
        logger.info("Shutting down context engine")

        if self.consolidation_task:
            self.consolidation_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()

        # Perform final consolidation
        await self._consolidate_if_needed()

        logger.info("Context engine shutdown complete")

    async def add_context_chunk(self, chunk: ContextChunk) -> None:
        """Add a new context chunk to working memory."""
        # Add to working memory
        self.working_memory.append(chunk)

        # Update indices
        for topic in chunk.topic_keywords:
            self.context_index[topic].append(chunk)

        # Update access patterns
        for tag in chunk.tags:
            self.access_patterns[tag] += 1

        # Check if consolidation is needed
        await self._consolidate_if_needed()

    async def get_context(self, request: ContextRequest) -> ContextResponse:
        """Get context based on request requirements."""
        start_time = time.time()

        # Record request
        self.request_history.append(request)

        # Update topic popularity
        for topic in request.topics:
            self.topic_popularity[topic] += 1

        # Select appropriate chunks based on strategy
        chunks = await self._select_chunks(request)

        # Compress context based on token constraints
        compression_level = self._determine_compression_level(request)
        compact_context = self.compactor.compress_context(chunks, compression_level, request.max_tokens)

        retrieval_time = time.time() - start_time

        # Create response
        response = ContextResponse(
            request_id=request.request_id,
            content=compact_context.content,
            tokens_used=compact_context.compressed_tokens,
            chunks_included=len(chunks),
            chunks_skipped=len(self.working_memory) - len(chunks),
            compression_level=compression_level,
            retrieval_time=retrieval_time,
            metadata={
                "compression_ratio": compact_context.compression_ratio,
                "original_tokens": compact_context.original_tokens,
                "strategy_used": request.strategy.value,
                "reconstruction_hints": compact_context.reconstruction_hints,
            },
        )

        # Record response
        self.response_history.append(response)

        logger.info(
            f"Context retrieved: {response.tokens_used}/{request.max_tokens} tokens, "
            f"{response.chunks_included} chunks, {retrieval_time:.3f}s"
        )

        return response

    async def _select_chunks(self, request: ContextRequest) -> list[ContextChunk]:
        """Select relevant chunks based on request and strategy."""
        if request.strategy == ContextStrategy.PROGRESSIVE:
            return await self._progressive_selection(request)
        if request.strategy == ContextStrategy.PREDICTIVE:
            return await self._predictive_selection(request)
        if request.strategy == ContextStrategy.CONSERVATIVE:
            return await self._conservative_selection(request)
        # AGGRESSIVE
        return await self._aggressive_selection(request)

    async def _progressive_selection(self, request: ContextRequest) -> list[ContextChunk]:
        """Progressive context selection - start with most important, add as needed."""
        # Sort by enhanced importance score
        sorted_chunks = sorted(
            self.working_memory, key=lambda c: self._calculate_request_relevance(c, request), reverse=True
        )

        selected = []
        current_tokens = 0

        for chunk in sorted_chunks:
            # Estimate tokens for this chunk
            chunk_tokens = self.compactor.encoding.encode(chunk.content)
            chunk_token_count = len(chunk_tokens)

            # Check if adding this chunk would exceed limit
            if current_tokens + chunk_token_count > request.max_tokens * 0.8:  # Leave room for compression
                break

            # Apply filters
            if not self._passes_filters(chunk, request):
                continue

            selected.append(chunk)
            current_tokens += chunk_token_count

        return selected

    async def _predictive_selection(self, request: ContextRequest) -> list[ContextChunk]:
        """Predictive selection - preload likely relevant context based on patterns."""
        # Analyze request to predict relevant topics
        predicted_topics = self._predict_relevant_topics(request)

        # Boost chunks with predicted topics
        scored_chunks = []
        for chunk in self.working_memory:
            base_score = self._calculate_request_relevance(chunk, request)

            # Boost for predicted topics
            topic_boost = sum(1 for topic in chunk.topic_keywords if topic in predicted_topics)

            # Boost for frequently accessed sources
            access_boost = sum(self.access_patterns.get(tag, 0) for tag in chunk.tags)

            final_score = base_score + (topic_boost * 0.2) + (access_boost * 0.1)
            scored_chunks.append((chunk, final_score))

        # Sort by final score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        # Select top chunks within token limit
        selected = []
        current_tokens = 0

        for chunk, _score in scored_chunks:
            chunk_tokens = len(self.compactor.encoding.encode(chunk.content))

            if current_tokens + chunk_tokens > request.max_tokens * 0.8:
                break

            if self._passes_filters(chunk, request):
                selected.append(chunk)
                current_tokens += chunk_tokens

        return selected

    async def _conservative_selection(self, request: ContextRequest) -> list[ContextChunk]:
        """Conservative selection - keep more context, less aggressive filtering."""
        # Use larger token budget (90% instead of 80%)
        token_budget = int(request.max_tokens * 0.9)

        # Sort by importance but be less aggressive about filtering
        sorted_chunks = sorted(
            self.working_memory, key=lambda c: self._calculate_request_relevance(c, request), reverse=True
        )

        selected = []
        current_tokens = 0

        for chunk in sorted_chunks:
            chunk_tokens = len(self.compactor.encoding.encode(chunk.content))

            if current_tokens + chunk_tokens > token_budget:
                break

            # Apply minimal filters for conservative approach
            if self._passes_basic_filters(chunk, request):
                selected.append(chunk)
                current_tokens += chunk_tokens

        return selected

    async def _aggressive_selection(self, request: ContextRequest) -> list[ContextChunk]:
        """Aggressive selection - minimal context, strict filtering."""
        # Use smaller token budget (60% for aggressive compression)
        token_budget = int(request.max_tokens * 0.6)

        # Very strict importance threshold
        min_importance = 0.7

        # Sort by enhanced importance
        sorted_chunks = sorted(
            self.working_memory, key=lambda c: self._calculate_request_relevance(c, request), reverse=True
        )

        selected = []
        current_tokens = 0

        for chunk in sorted_chunks:
            # Apply strict importance threshold
            if chunk.importance_score < min_importance:
                continue

            chunk_tokens = len(self.compactor.encoding.encode(chunk.content))

            if current_tokens + chunk_tokens > token_budget:
                break

            # Apply all filters strictly
            if self._passes_strict_filters(chunk, request):
                selected.append(chunk)
                current_tokens += chunk_tokens

        return selected

    def _calculate_request_relevance(self, chunk: ContextChunk, request: ContextRequest) -> float:
        """Calculate relevance score of chunk for specific request."""
        relevance = chunk.importance_score

        # Topic relevance
        topic_matches = len(set(chunk.topic_keywords) & set(request.topics))
        relevance += topic_matches * 0.2

        # Source relevance
        if chunk.source in request.required_sources:
            relevance += 0.3

        # Type relevance
        if chunk.chunk_type in request.context_types:
            relevance += 0.2

        # Time range relevance
        if request.time_range:
            start_time, end_time = request.time_range
            if start_time <= chunk.timestamp <= end_time:
                relevance += 0.2

        # Recency boost
        hours_old = (datetime.now() - chunk.timestamp).total_seconds() / 3600
        recency_boost = max(0, 1 - hours_old / 168)  # Decay over 1 week
        relevance += recency_boost * 0.1

        # Technical content boost for technical requests
        if chunk.technical_density > 0.5:
            relevance += chunk.technical_density * 0.15

        return relevance

    def _predict_relevant_topics(self, request: ContextRequest) -> list[str]:
        """Predict relevant topics based on request and historical patterns."""
        # Extract topics from request
        request_topics = set(request.topics)

        # Find related topics based on co-occurrence in working memory
        topic_cooccurrence = defaultdict(int)

        for chunk in self.working_memory:
            chunk_topics = set(chunk.topic_keywords)
            if request_topics & chunk_topics:
                # This chunk has some of the request topics
                for topic in chunk_topics - request_topics:
                    topic_cooccurrence[topic] += 1

        # Sort by co-occurrence frequency
        related_topics = sorted(topic_cooccurrence.items(), key=lambda x: x[1], reverse=True)

        # Add popular topics
        popular_topics = sorted(self.topic_popularity.items(), key=lambda x: x[1], reverse=True)

        # Combine and return top predictions
        predicted = [topic for topic, _ in related_topics[:10]]
        predicted.extend([topic for topic, _ in popular_topics[:5] if topic not in predicted])

        return predicted[:15]  # Return top 15 predictions

    def _passes_filters(self, chunk: ContextChunk, request: ContextRequest) -> bool:
        """Check if chunk passes all applicable filters."""
        return self._passes_basic_filters(chunk, request) and self._passes_strict_filters(chunk, request)

    def _passes_basic_filters(self, chunk: ContextChunk, request: ContextRequest) -> bool:
        """Apply basic filters to chunk selection."""
        # Time range filter
        if request.time_range:
            start_time, end_time = request.time_range
            if not (start_time <= chunk.timestamp <= end_time):
                return False

        # Required sources filter
        return not (request.required_sources and chunk.source not in request.required_sources)

    def _passes_strict_filters(self, chunk: ContextChunk, request: ContextRequest) -> bool:
        """Apply strict filters for aggressive selection."""
        # Context types filter
        if request.context_types and chunk.chunk_type not in request.context_types:
            return False

        # Minimum importance threshold
        return not chunk.importance_score < 0.3

    def _determine_compression_level(self, request: ContextRequest) -> ContextLevel:
        """Determine appropriate compression level based on request."""
        # Higher priority requests get better compression levels
        if request.priority >= 4:
            return ContextLevel.SUMMARY
        if request.priority >= 3:
            return ContextLevel.ESSENTIAL
        return ContextLevel.METADATA

    async def _consolidate_if_needed(self) -> None:
        """Consolidate working memory if it exceeds threshold."""
        if len(self.working_memory) >= self.consolidation_threshold:
            await self._consolidate_memory()

    async def _consolidate_memory(self) -> None:
        """Consolidate working memory into long-term storage."""
        if len(self.working_memory) < 10:
            return

        logger.info(f"Consolidating {len(self.working_memory)} context chunks")

        # Take oldest chunks for consolidation
        chunks_to_consolidate = list(self.working_memory)[:50]  # Consolidate oldest 50

        # Remove from working memory
        for chunk in chunks_to_consolidate:
            try:
                self.working_memory.remove(chunk)
            except ValueError:
                continue  # Chunk already removed

        # Create compact context
        compact_context = self.compactor.compress_context(chunks_to_consolidate, ContextLevel.SUMMARY)

        # Extract key topics
        all_topics = []
        for chunk in chunks_to_consolidate:
            all_topics.extend(chunk.topic_keywords)
        key_topics = list(set(all_topics))[:10]

        # Calculate average importance
        avg_importance = sum(chunk.importance_score for chunk in chunks_to_consolidate) / len(chunks_to_consolidate)

        # Create consolidation record
        consolidation = MemoryConsolidation(
            timestamp=datetime.now(),
            original_chunks=len(chunks_to_consolidate),
            consolidated_chunks=1,  # Single compact context
            compression_ratio=compact_context.compression_ratio,
            key_topics=key_topics,
            importance_score=avg_importance,
            compact_context=compact_context,
        )

        self.consolidated_memory.append(consolidation)

        # Update indices
        for topic in key_topics:
            self.context_index[topic].extend(chunks_to_consolidate)

        logger.info(
            f"Memory consolidation complete: {consolidation.original_chunks} -> {consolidation.consolidated_chunks} "
            f"chunks, {consolidation.compression_ratio:.2f} ratio"
        )

    async def _periodic_consolidation(self) -> None:
        """Background task for periodic memory consolidation."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                await self._consolidate_if_needed()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic consolidation: {e}")

    async def _periodic_cleanup(self) -> None:
        """Background task for periodic cleanup of old data."""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                await self._cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")

    async def _cleanup_old_data(self) -> None:
        """Clean up old data to prevent memory leaks."""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(days=7)

        # Clean old consolidated memory (keep only recent)
        old_consolidations = [c for c in self.consolidated_memory if c.timestamp < cutoff_time]

        for consolidation in old_consolidations:
            self.consolidated_memory.remove(consolidation)

        if old_consolidations:
            logger.info(f"Cleaned up {len(old_consolidations)} old memory consolidations")

    def get_engine_stats(self) -> dict[str, Any]:
        """Get comprehensive statistics about the context engine."""
        return {
            "memory_stats": {
                "working_memory_size": len(self.working_memory),
                "consolidated_memory_size": len(self.consolidated_memory),
                "max_working_memory": self.working_memory.maxlen,
                "total_chunks_processed": len(self.working_memory)
                + sum(c.original_chunks for c in self.consolidated_memory),
            },
            "performance_stats": {
                "requests_processed": len(self.request_history),
                "avg_response_time": sum(r.retrieval_time for r in self.response_history) / len(self.response_history)
                if self.response_history
                else 0,
                "avg_tokens_used": sum(r.tokens_used for r in self.response_history) / len(self.response_history)
                if self.response_history
                else 0,
                "compression_efficiency": self.compactor.get_compression_stats(),
            },
            "pattern_analysis": {
                "top_topics": dict(sorted(self.topic_popularity.items(), key=lambda x: x[1], reverse=True)[:10]),
                "access_patterns": dict(sorted(self.access_patterns.items(), key=lambda x: x[1], reverse=True)[:10]),
                "context_index_size": len(self.context_index),
            },
            "consolidation_stats": {
                "total_consolidations": len(self.consolidated_memory),
                "avg_compression_ratio": sum(c.compression_ratio for c in self.consolidated_memory)
                / len(self.consolidated_memory)
                if self.consolidated_memory
                else 0,
                "total_original_chunks": sum(c.original_chunks for c in self.consolidated_memory),
                "total_consolidated_chunks": sum(c.consolidated_chunks for c in self.consolidated_memory),
            },
        }

    def save_state(self, file_path: Path) -> None:
        """Save engine state to file for persistence."""
        state = {
            "working_memory": [asdict(chunk) for chunk in self.working_memory],
            "consolidated_memory": [asdict(consolidation) for consolidation in self.consolidated_memory],
            "access_patterns": dict(self.access_patterns),
            "topic_popularity": dict(self.topic_popularity),
            "timestamp": datetime.now().isoformat(),
        }

        with open(file_path, "w") as f:
            json.dump(state, f, indent=2, default=str)

        logger.info(f"Context engine state saved to {file_path}")

    def load_state(self, file_path: Path) -> None:
        """Load engine state from file."""
        if not file_path.exists():
            logger.warning(f"State file {file_path} does not exist")
            return

        with open(file_path) as f:
            state = json.load(f)

        # Restore working memory (simplified restoration)
        self.working_memory.clear()
        for chunk_data in state.get("working_memory", []):
            # Convert timestamp back to datetime
            if isinstance(chunk_data.get("timestamp"), str):
                chunk_data["timestamp"] = datetime.fromisoformat(chunk_data["timestamp"])
            # Create ContextChunk (simplified)
            chunk = ContextChunk(**chunk_data)
            self.working_memory.append(chunk)

        # Restore other state
        self.access_patterns = defaultdict(int, state.get("access_patterns", {}))
        self.topic_popularity = defaultdict(int, state.get("topic_popularity", {}))

        logger.info(f"Context engine state loaded from {file_path}")


# Global context engine instance
_context_engine: ContextEngine | None = None


def get_context_engine() -> ContextEngine:
    """Get the global context engine instance."""
    global _context_engine
    if _context_engine is None:
        _context_engine = ContextEngine()
    return _context_engine


async def initialize_context_engine() -> ContextEngine:
    """Initialize the global context engine."""
    engine = get_context_engine()
    await engine.initialize()
    return engine


async def shutdown_context_engine() -> None:
    """Shutdown the global context engine."""
    global _context_engine
    if _context_engine:
        await _context_engine.shutdown()
        _context_engine = None
