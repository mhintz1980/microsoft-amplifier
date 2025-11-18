"""
Context Reconstruction and Retrieval System

Provides intelligent reconstruction and retrieval of compressed context
with semantic search, similarity matching, and progressive detail recovery.

Key Features:
- Progressive context reconstruction from compressed levels
- Semantic search and similarity matching
- Context expansion and detail recovery
- Multi-level reconstruction hints
- Intelligent chunk retrieval based on queries
"""

import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .context_compactor import CompactContext
from .context_compactor import ContextChunk
from .context_compactor import ContextLevel
from .context_compactor import get_context_compactor
from .logger import get_logger
from .token_utils import estimate_tokens

logger = get_logger(__name__)


class RetrievalMode(Enum):
    """Context retrieval modes."""

    EXACT = "exact"  # Retrieve exact chunks
    SEMANTIC = "semantic"  # Semantic similarity matching
    HYBRID = "hybrid"  # Combination of exact and semantic
    PROGRESSIVE = "progressive"  # Progressive detail loading


class ReconstructionLevel(Enum):
    """Levels of context reconstruction detail."""

    METADATA_ONLY = "metadata_only"  # Just metadata and references
    KEY_POINTS = "key_points"  # Essential points and summaries
    DETAILED = "detailed"  # Full details with context
    COMPLETE = "complete"  # Full reconstruction with all details


@dataclass
class RetrievalQuery:
    """Query for context retrieval."""

    query_id: str
    query_text: str
    retrieval_mode: RetrievalMode = RetrievalMode.SEMANTIC
    max_results: int = 10
    similarity_threshold: float = 0.5
    context_types: list[str] = field(default_factory=list)
    time_range: tuple[datetime, datetime] | None = None
    required_topics: list[str] = field(default_factory=list)


@dataclass
class RetrievalResult:
    """Result of context retrieval."""

    query_id: str
    matched_chunks: list[ContextChunk]
    similarity_scores: list[float]
    reconstruction_level: ReconstructionLevel
    retrieval_time: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReconstructionRequest:
    """Request for context reconstruction."""

    request_id: str
    compact_context: CompactContext
    target_level: ReconstructionLevel
    expansion_queries: list[str] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)


@dataclass
class ReconstructionResult:
    """Result of context reconstruction."""

    request_id: str
    reconstructed_content: str
    original_level: ContextLevel
    reconstructed_level: ReconstructionLevel
    expansion_ratio: float
    detail_added: str
    confidence_score: float
    reconstruction_time: float


class ContextRetriever:
    """Intelligent context retrieval and reconstruction system."""

    def __init__(self, embedding_model: str | None = None):
        self.compactor = get_context_compactor()

        # Sentence transformer for semantic search
        try:
            self.sentence_model = SentenceTransformer(embedding_model or "all-MiniLM-L6-v2")
            logger.info("Sentence transformer model loaded for retrieval")
        except Exception as e:
            logger.warning(f"Failed to load sentence transformer: {e}")
            self.sentence_model = None

        # Storage for context chunks and indices
        self.context_storage: list[ContextChunk] = []
        self.semantic_index: dict[str, np.ndarray] = {}
        self.keyword_index: dict[str, list[str]] = defaultdict(list)
        self.temporal_index: dict[str, list[ContextChunk]] = defaultdict(list)

        # Performance tracking
        self.retrieval_stats = {
            "total_queries": 0,
            "avg_retrieval_time": 0.0,
            "cache_hits": 0,
            "semantic_queries": 0,
            "exact_queries": 0,
        }

    def add_context_chunk(self, chunk: ContextChunk) -> None:
        """Add a context chunk to the retrieval system."""
        self.context_storage.append(chunk)

        # Create semantic embedding
        if self.sentence_model and chunk.content:
            try:
                embedding = self.sentence_model.encode(chunk.content)
                # type: ignore[arg-type]
                # type: ignore[arg-type]
                self.semantic_index[chunk.content] = embedding  # type: ignore[arg-type]
            except Exception as e:
                logger.warning(f"Failed to create embedding: {e}")

        # Update keyword index
        for keyword in chunk.topic_keywords:
            self.keyword_index[keyword.lower()].append(chunk.content)

        # Update temporal index
        date_key = chunk.timestamp.strftime("%Y-%m-%d")
        self.temporal_index[date_key].append(chunk)

    async def retrieve_context(self, query: RetrievalQuery) -> RetrievalResult:
        """Retrieve context chunks based on query."""
        start_time = asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0
        self.retrieval_stats["total_queries"] += 1

        if query.retrieval_mode == RetrievalMode.SEMANTIC:
            self.retrieval_stats["semantic_queries"] += 1
            matched_chunks, scores = await self._semantic_retrieval(query)
        elif query.retrieval_mode == RetrievalMode.EXACT:
            self.retrieval_stats["exact_queries"] += 1
            matched_chunks, scores = await self._exact_retrieval(query)
        elif query.retrieval_mode == RetrievalMode.HYBRID:
            matched_chunks, scores = await self._hybrid_retrieval(query)
        else:  # PROGRESSIVE
            matched_chunks, scores = await self._progressive_retrieval(query)

        retrieval_time = (asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0) - start_time

        # Update performance stats
        self.retrieval_stats["avg_retrieval_time"] = (
            self.retrieval_stats["avg_retrieval_time"] * (self.retrieval_stats["total_queries"] - 1) + retrieval_time
        ) / self.retrieval_stats["total_queries"]

        # Determine reconstruction level based on query complexity
        reconstruction_level = self._determine_reconstruction_level(query, matched_chunks)

        return RetrievalResult(
            query_id=query.query_id,
            matched_chunks=matched_chunks,
            similarity_scores=scores,
            reconstruction_level=reconstruction_level,
            retrieval_time=retrieval_time,
            metadata={
                "query_mode": query.retrieval_mode.value,
                "chunks_evaluated": len(self.context_storage),
                "avg_similarity": np.mean(scores) if scores else 0,
                "max_similarity": max(scores) if scores else 0,
            },
        )

    async def _semantic_retrieval(self, query: RetrievalQuery) -> tuple[list[ContextChunk], list[float]]:
        """Perform semantic similarity retrieval."""
        if not self.sentence_model:
            return await self._exact_retrieval(query)

        # Create query embedding
        query_embedding = self.sentence_model.encode(query.query_text)

        # Calculate similarities
        similarities = []
        for chunk in self.context_storage:
            if chunk.content in self.semantic_index:
                chunk_embedding = self.semantic_index[chunk.content]
                similarity = cosine_similarity(query_embedding.reshape(1, -1), chunk_embedding.reshape(1, -1))[0][0]
                similarities.append((chunk, similarity))

        # Filter by threshold and sort
        filtered = [(chunk, sim) for chunk, sim in similarities if sim >= query.similarity_threshold]
        filtered.sort(key=lambda x: x[1], reverse=True)

        # Apply additional filters
        matched_chunks, scores = [], []
        for chunk, similarity in filtered[: query.max_results]:
            if self._passes_chunk_filters(chunk, query):
                matched_chunks.append(chunk)
                scores.append(similarity)

        return matched_chunks, scores

    async def _exact_retrieval(self, query: RetrievalQuery) -> tuple[list[ContextChunk], list[float]]:
        """Perform exact keyword matching retrieval."""
        query_terms = query.query_text.lower().split()
        matched_chunks = []
        scores = []

        for chunk in self.context_storage:
            score = 0.0
            chunk_text = (chunk.content + " " + " ".join(chunk.topic_keywords)).lower()

            # Calculate exact match score
            for term in query_terms:
                if term in chunk_text:
                    score += 1.0

            # Normalize score
            if query_terms:
                score = score / len(query_terms)

            if score > 0 and self._passes_chunk_filters(chunk, query):
                matched_chunks.append(chunk)
                scores.append(score)

        # Sort by score
        sorted_results = sorted(zip(matched_chunks, scores, strict=False), key=lambda x: x[1], reverse=True)
        matched_chunks, scores = zip(*sorted_results[: query.max_results], strict=False) if sorted_results else ([], [])

        return list(matched_chunks), list(scores)

    async def _hybrid_retrieval(self, query: RetrievalQuery) -> tuple[list[ContextChunk], list[float]]:
        """Perform hybrid retrieval combining semantic and exact matching."""
        # Get semantic results
        semantic_chunks, semantic_scores = await self._semantic_retrieval(query)

        # Get exact results
        exact_chunks, exact_scores = await self._exact_retrieval(query)

        # Combine results with weighted scores
        combined_scores = defaultdict(float)
        chunk_mapping = {}

        # Add semantic scores (weight: 0.7)
        for chunk, score in zip(semantic_chunks, semantic_scores, strict=False):
            combined_scores[id(chunk)] += score * 0.7
            chunk_mapping[id(chunk)] = chunk

        # Add exact scores (weight: 0.3)
        for chunk, score in zip(exact_chunks, exact_scores, strict=False):
            combined_scores[id(chunk)] += score * 0.3
            chunk_mapping[id(chunk)] = chunk

        # Sort by combined score
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        # Return top results
        matched_chunks = [chunk_mapping[chunk_id] for chunk_id, _ in sorted_results[: query.max_results]]
        scores = [score for _, score in sorted_results[: query.max_results]]

        return matched_chunks, scores

    async def _progressive_retrieval(self, query: RetrievalQuery) -> tuple[list[ContextChunk], list[float]]:
        """Perform progressive retrieval with increasing detail."""
        # Start with exact retrieval for immediate results
        exact_chunks, exact_scores = await self._exact_retrieval(query)

        # If need more results, add semantic
        if len(exact_chunks) < query.max_results:
            semantic_chunks, semantic_scores = await self._semantic_retrieval(query)

            # Combine, avoiding duplicates
            seen_ids = {id(chunk) for chunk in exact_chunks}
            for chunk, score in zip(semantic_chunks, semantic_scores, strict=False):
                if id(chunk) not in seen_ids and len(exact_chunks) < query.max_results:
                    exact_chunks.append(chunk)
                    exact_scores.append(score)
                    seen_ids.add(id(chunk))

        return exact_chunks, exact_scores

    def _passes_chunk_filters(self, chunk: ContextChunk, query: RetrievalQuery) -> bool:
        """Check if chunk passes query filters."""
        # Context type filter
        if query.context_types and chunk.chunk_type not in query.context_types:
            return False

        # Time range filter
        if query.time_range:
            start_time, end_time = query.time_range
            if not (start_time <= chunk.timestamp <= end_time):
                return False

        # Required topics filter
        if query.required_topics:
            chunk_topics = set(chunk.topic_keywords)
            required_topics = set(query.required_topics)
            if not chunk_topics & required_topics:  # No overlap
                return False

        return True

    def _determine_reconstruction_level(self, query: RetrievalQuery, chunks: list[ContextChunk]) -> ReconstructionLevel:
        """Determine appropriate reconstruction level based on query and results."""
        # Progressive based on query complexity and result count
        query_complexity = len(query.query_text.split())
        result_count = len(chunks)

        if query_complexity <= 3 and result_count <= 5:
            return ReconstructionLevel.KEY_POINTS
        if query_complexity <= 5 or result_count <= 10:
            return ReconstructionLevel.DETAILED
        return ReconstructionLevel.COMPLETE

    async def reconstruct_context(self, request: ReconstructionRequest) -> ReconstructionResult:
        """Reconstruct detailed context from compact version."""
        start_time = asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0

        original_tokens = request.compact_context.compressed_tokens
        original_level = request.compact_context.level

        # Base reconstruction
        if request.target_level == ReconstructionLevel.METADATA_ONLY:
            reconstructed = self._reconstruct_metadata_only(request.compact_context)
        elif request.target_level == ReconstructionLevel.KEY_POINTS:
            reconstructed = await self._reconstruct_key_points(request.compact_context, request)
        elif request.target_level == ReconstructionLevel.DETAILED:
            reconstructed = await self._reconstruct_detailed(request.compact_context, request)
        else:  # COMPLETE
            reconstructed = await self._reconstruct_complete(request.compact_context, request)

        reconstruction_time = (
            asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0
        ) - start_time

        final_tokens = estimate_tokens(reconstructed)
        expansion_ratio = final_tokens / original_tokens if original_tokens > 0 else 1

        # Calculate confidence based on reconstruction quality
        confidence_score = self._calculate_reconstruction_confidence(
            original_level, request.target_level, reconstructed
        )

        return ReconstructionResult(
            request_id=request.request_id,
            reconstructed_content=reconstructed,
            original_level=original_level,
            reconstructed_level=request.target_level,
            expansion_ratio=expansion_ratio,
            detail_added=self._describe_detail_added(original_level, request.target_level),
            confidence_score=confidence_score,
            reconstruction_time=reconstruction_time,
        )

    def _reconstruct_metadata_only(self, compact_context: CompactContext) -> str:
        """Reconstruct with metadata only."""
        reconstruction = f"# Context Metadata ({compact_context.level.value.upper()})\n\n"

        # Add basic metadata
        reconstruction += f"**Compression Level:** {compact_context.level.value}\n"
        reconstruction += f"**Original Tokens:** {compact_context.original_tokens}\n"
        reconstruction += f"**Compressed Tokens:** {compact_context.compressed_tokens}\n"
        reconstruction += f"**Compression Ratio:** {compact_context.compression_ratio:.2f}\n"

        # Add reconstruction hints
        if compact_context.reconstruction_hints:
            reconstruction += "\n**Reconstruction Hints:**\n"
            for hint in compact_context.reconstruction_hints:
                reconstruction += f"- {hint}\n"

        # Add metadata from compact context
        if compact_context.metadata:
            reconstruction += "\n**Additional Metadata:**\n"
            for key, value in compact_context.metadata.items():
                if isinstance(value, list | dict):
                    value = json.dumps(value, indent=2)
                reconstruction += f"- {key}: {value}\n"

        return reconstruction

    async def _reconstruct_key_points(self, compact_context: CompactContext, request: ReconstructionRequest) -> str:
        """Reconstruct with key points and essential information."""
        base_reconstruction = self._reconstruct_metadata_only(compact_context)

        # Add the compressed content as key points
        reconstruction = base_reconstruction + f"\n\n# Key Points\n\n{compact_context.content}\n"

        # Add expansion based on focus areas if provided
        if request.focus_areas:
            expansion_text = await self._expand_focus_areas(compact_context, request.focus_areas, "key_points")
            reconstruction += f"\n\n# Focus Area Expansion\n\n{expansion_text}"

        return reconstruction

    async def _reconstruct_detailed(self, compact_context: CompactContext, request: ReconstructionRequest) -> str:
        """Reconstruct with detailed information."""
        base_reconstruction = await self._reconstruct_key_points(compact_context, request)

        # Add semantic expansion
        if request.expansion_queries:
            expanded_details = await self._semantic_expansion(compact_context, request.expansion_queries)
            base_reconstruction += f"\n\n# Expanded Details\n\n{expanded_details}"

        # Add related context chunks if available
        related_chunks = await self._find_related_chunks(compact_context)
        if related_chunks:
            base_reconstruction += "\n\n# Related Context\n\n"
            for i, chunk in enumerate(related_chunks[:3]):  # Limit to 3 related chunks
                base_reconstruction += f"**Related {i + 1}:** [{chunk.source}] {chunk.content[:200]}...\n"

        return base_reconstruction

    async def _reconstruct_complete(self, compact_context: CompactContext, request: ReconstructionRequest) -> str:
        """Reconstruct with complete detail including full related context."""
        detailed_reconstruction = await self._reconstruct_detailed(compact_context, request)

        # Add comprehensive related context
        related_chunks = await self._find_related_chunks(compact_context)
        if related_chunks:
            detailed_reconstruction += "\n\n# Complete Related Context\n\n"
            for chunk in related_chunks:
                detailed_reconstruction += (
                    f"**Source: {chunk.source}** ({chunk.timestamp.strftime('%Y-%m-%d %H:%M')})\n"
                )
                detailed_reconstruction += f"{chunk.content}\n\n"

        # Add context relationships and patterns
        patterns = self._analyze_context_patterns(compact_context)
        if patterns:
            detailed_reconstruction += "\n\n# Context Patterns\n\n"
            for pattern in patterns:
                detailed_reconstruction += f"- {pattern}\n"

        return detailed_reconstruction

    async def _expand_focus_areas(
        self, compact_context: CompactContext, focus_areas: list[str], detail_level: str
    ) -> str:
        """Expand context based on specific focus areas."""
        if not self.sentence_model:
            return "Semantic expansion not available"

        expanded_content = []

        for area in focus_areas:
            # Find related chunks using semantic search
            query = RetrievalQuery(
                query_id=f"expand_{area}",
                query_text=area,
                retrieval_mode=RetrievalMode.SEMANTIC,
                max_results=5,
                similarity_threshold=0.3,
            )

            result = await self.retrieve_context(query)

            if result.matched_chunks:
                expanded_content.append(f"**{area.title()} Expansion:**")
                for chunk in result.matched_chunks[:3]:
                    if detail_level == "key_points":
                        # Add just key points from chunk
                        summary = chunk.content[:150] + "..." if len(chunk.content) > 150 else chunk.content
                        expanded_content.append(f"- {summary}")
                    else:
                        # Add more detail
                        expanded_content.append(f"- [{chunk.source}] {chunk.content}")

        return "\n".join(expanded_content)

    async def _semantic_expansion(self, compact_context: CompactContext, queries: list[str]) -> str:
        """Perform semantic expansion based on queries."""
        if not self.sentence_model:
            return "Semantic expansion not available"

        expansions = []

        for query_text in queries:
            # Find semantically related content
            query = RetrievalQuery(
                query_id=f"semantic_{query_text[:20]}",
                query_text=query_text,
                retrieval_mode=RetrievalMode.SEMANTIC,
                max_results=3,
                similarity_threshold=0.4,
            )

            result = await self.retrieve_context(query)

            if result.matched_chunks:
                expansions.append(f"**Expansion for '{query_text}':**")
                for chunk, similarity in zip(result.matched_chunks, result.similarity_scores, strict=False):
                    expansions.append(f"- [{chunk.source}] (similarity: {similarity:.2f}) {chunk.content[:200]}...")

        return "\n".join(expansions)

    async def _find_related_chunks(self, compact_context: CompactContext) -> list[ContextChunk]:
        """Find context chunks related to the compact context."""
        if not self.sentence_model or not compact_context.content:
            return []

        # Create embedding for the compact context
        try:
            context_embedding = self.sentence_model.encode(compact_context.content)
        except Exception as e:
            logger.warning(f"Failed to create context embedding: {e}")
            return []

        # Find similar chunks
        similarities = []
        for chunk in self.context_storage:
            if chunk.content in self.semantic_index:
                chunk_embedding = self.semantic_index[chunk.content]
                similarity = cosine_similarity(context_embedding.reshape(1, -1), chunk_embedding.reshape(1, -1))[0][0]
                similarities.append((chunk, similarity))

        # Return top similar chunks
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in similarities[:5]]  # Top 5 related chunks

    def _analyze_context_patterns(self, compact_context: CompactContext) -> list[str]:
        """Analyze patterns in the context for reconstruction hints."""
        patterns = []

        # Analyze reconstruction hints for patterns
        for hint in compact_context.reconstruction_hints:
            if "Topics covered:" in hint:
                topics = hint.split("Topics covered:")[1].strip()
                patterns.append(f"Main topics: {topics}")
            elif "Files referenced:" in hint:
                files = hint.split("Files referenced:")[1].strip()
                patterns.append(f"Related files: {files}")
            elif "Time range:" in hint:
                time_range = hint.split("Time range:")[1].strip()
                patterns.append(f"Time context: {time_range}")

        # Add compression analysis
        if compact_context.compression_ratio < 0.1:
            patterns.append("Highly compressed content - aggressive summarization applied")
        elif compact_context.compression_ratio > 0.5:
            patterns.append("Lightly compressed content - most details preserved")

        return patterns

    def _calculate_reconstruction_confidence(
        self, original: ContextLevel, target: ReconstructionLevel, content: str
    ) -> float:
        """Calculate confidence score for reconstruction quality."""
        # Base confidence based on level difference
        level_mapping = {
            ContextLevel.METADATA: ReconstructionLevel.METADATA_ONLY,
            ContextLevel.ESSENTIAL: ReconstructionLevel.KEY_POINTS,
            ContextLevel.SUMMARY: ReconstructionLevel.DETAILED,
            ContextLevel.FULL: ReconstructionLevel.COMPLETE,
        }

        target_depth = list(ReconstructionLevel).index(target)
        original_depth = list(ReconstructionLevel).index(level_mapping.get(original, ReconstructionLevel.METADATA_ONLY))

        depth_confidence = max(0, 1 - abs(target_depth - original_depth) / 3)

        # Content quality factors
        content_length = len(content)
        length_confidence = min(1, content_length / 1000)  # Prefer longer reconstructions

        # Check for reconstruction quality indicators
        quality_indicators = [
            "###" in content,  # Has headers
            "**" in content,  # Has bold text (emphasis)
            "-" in content,  # Has lists
            content.count("\n") > 5,  # Has multiple lines
        ]

        quality_confidence = sum(quality_indicators) / len(quality_indicators)

        # Combine confidence factors
        overall_confidence = depth_confidence * 0.4 + length_confidence * 0.3 + quality_confidence * 0.3

        return min(1.0, max(0.0, overall_confidence))

    def _describe_detail_added(self, original: ContextLevel, target: ReconstructionLevel) -> str:
        """Describe the level of detail added during reconstruction."""
        descriptions = {
            (ContextLevel.METADATA, ReconstructionLevel.KEY_POINTS): "Added key points and essential information",
            (ContextLevel.METADATA, ReconstructionLevel.DETAILED): "Added detailed information with semantic expansion",
            (
                ContextLevel.METADATA,
                ReconstructionLevel.COMPLETE,
            ): "Added complete context with full related information",
            (
                ContextLevel.ESSENTIAL,
                ReconstructionLevel.DETAILED,
            ): "Enhanced with detailed explanations and related context",
            (
                ContextLevel.ESSENTIAL,
                ReconstructionLevel.COMPLETE,
            ): "Expanded to full detail with comprehensive related context",
            (
                ContextLevel.SUMMARY,
                ReconstructionLevel.COMPLETE,
            ): "Expanded from summary to complete context with related information",
        }

        return descriptions.get((original, target), "Standard reconstruction applied")

    def get_retrieval_stats(self) -> dict[str, Any]:
        """Get comprehensive statistics about retrieval performance."""
        return {
            "performance_stats": self.retrieval_stats,
            "storage_stats": {
                "total_chunks_stored": len(self.context_storage),
                "semantic_index_size": len(self.semantic_index),
                "keyword_index_size": len(self.keyword_index),
                "temporal_index_size": len(self.temporal_index),
            },
            "model_info": {
                "semantic_model_available": self.sentence_model is not None,
                "model_name": getattr(self.sentence_model, "name", "unknown") if self.sentence_model else None,
            },
        }


# Global context retriever instance
_context_retriever: ContextRetriever | None = None


def get_context_retriever() -> ContextRetriever:
    """Get the global context retriever instance."""
    global _context_retriever
    if _context_retriever is None:
        _context_retriever = ContextRetriever()
    return _context_retriever
