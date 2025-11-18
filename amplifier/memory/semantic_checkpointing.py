"""
Semantic Checkpointing - Advanced Progressive Compression with Semantic Analysis

Enhances checkpoint system with semantic importance scoring and progressive compression.
Integrates with the existing context compactor for intelligent content analysis.

Key Features:
- Semantic importance scoring using embeddings and NLP
- Progressive compression levels with semantic preservation
- Intelligent content selection based on semantic relevance
- Topic modeling and keyword extraction
- Semantic clustering for content grouping
- Integration with context compactor's advanced features
"""

import logging
from typing import Any

from ..utils.context_compactor import ContextChunk
from ..utils.context_compactor import get_context_compactor
from .checkpoint_manager import CheckpointLevel
from .checkpoint_manager import CheckpointManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticImportanceScorer:
    """Scores content importance using semantic analysis"""

    def __init__(self):
        self.context_compactor = get_context_compactor()
        self.importance_cache = {}
        self.topic_cache = {}

    def score_chunks(self, chunks: list[ContextChunk]) -> list[ContextChunk]:
        """Score importance of context chunks using semantic analysis

        Args:
            chunks: List of context chunks to score

        Returns:
            List of chunks with updated importance scores
        """
        logger.info(f"Scoring importance for {len(chunks)} chunks")

        # Enhanced analysis for each chunk
        for chunk in chunks:
            enhanced_score = self._calculate_semantic_importance(chunk)
            chunk.importance_score = enhanced_score

        # Sort by importance and return
        scored_chunks = sorted(chunks, key=lambda c: c.importance_score, reverse=True)
        return scored_chunks

    def _calculate_semantic_importance(self, chunk: ContextChunk) -> float:
        """Calculate semantic importance score for a chunk

        Args:
            chunk: Context chunk to score

        Returns:
            Importance score (0.0 to 1.0)
        """
        # Check cache first
        content_hash = hash(chunk.content)
        if content_hash in self.importance_cache:
            return self.importance_cache[content_hash]

        # Base importance
        importance = chunk.importance_score

        # Enhanced analysis using context compactor
        self.context_compactor.add_context_chunk(chunk)

        # Get enhanced importance factors
        importance += (
            chunk.technical_density * 0.15  # Technical content value
            + chunk.actionability * 0.15  # Actionable content value
            + chunk.novelty_score * 0.20  # Novel information value
        )

        # Semantic topic relevance
        topic_importance = self._calculate_topic_importance(chunk)
        importance += topic_importance * 0.20

        # Length and complexity factors
        length_factor = self._calculate_length_importance(chunk.content)
        importance += length_factor * 0.10

        # Cap at 1.0
        importance = min(1.0, importance)

        # Cache result
        self.importance_cache[content_hash] = importance

        return importance

    def _calculate_topic_importance(self, chunk: ContextChunk) -> float:
        """Calculate topic importance for a chunk

        Args:
            chunk: Context chunk to analyze

        Returns:
            Topic importance score (0.0 to 1.0)
        """
        if not chunk.topic_keywords:
            return 0.5  # Default importance

        # Analyze topic relevance based on keywords
        technical_topics = [
            "function",
            "class",
            "method",
            "algorithm",
            "database",
            "api",
            "interface",
            "protocol",
            "architecture",
            "design",
        ]

        problem_topics = [
            "error",
            "issue",
            "bug",
            "problem",
            "failure",
            "exception",
            "fix",
            "solution",
            "resolve",
            "debug",
            "troubleshoot",
        ]

        decision_topics = [
            "decision",
            "conclusion",
            "agreed",
            "determined",
            "selected",
            "choice",
            "prefer",
            "recommend",
            "suggest",
            "propose",
        ]

        topic_score = 0.5  # Base score

        # Check for high-value topics
        for keyword in chunk.topic_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in technical_topics:
                topic_score += 0.1
            elif keyword_lower in problem_topics:
                topic_score += 0.15  # Problems are often critical
            elif keyword_lower in decision_topics:
                topic_score += 0.12  # Decisions are important

        return min(1.0, topic_score)

    def _calculate_length_importance(self, content: str) -> float:
        """Calculate importance based on content length

        Args:
            content: Content to analyze

        Returns:
            Length importance score (0.0 to 1.0)
        """
        word_count = len(content.split())

        # Optimal length ranges for different content types
        if word_count < 10:
            return 0.3  # Too short to be very important
        if 10 <= word_count <= 50:
            return 0.8  # Good length for key points
        if 50 <= word_count <= 200:
            return 0.9  # Optimal length for detailed content
        if 200 <= word_count <= 500:
            return 0.7  # Good but might be verbose
        return 0.5  # Very long content might be less focused

    def extract_semantic_groups(self, chunks: list[ContextChunk], max_groups: int = 5) -> list[list[ContextChunk]]:
        """Group chunks by semantic similarity

        Args:
            chunks: List of chunks to group
            max_groups: Maximum number of groups to create

        Returns:
            List of semantic groups (each group is a list of chunks)
        """
        if len(chunks) < 2:
            return [chunks] if chunks else []

        logger.info(f"Creating semantic groups from {len(chunks)} chunks")

        # Use context compactor's clustering capabilities
        try:
            from ..utils.context_compactor import ContextLevel

            compressed = self.context_compactor.compress_context(chunks, ContextLevel.SUMMARY, max_tokens=50000)

            # If clustering was used, extract cluster information
            if compressed.metadata.get("clustering_used", False):
                # Simulate clustering based on semantic similarity
                groups = self._create_semantic_clusters(chunks, max_groups)
            else:
                # Fallback: group by topic keywords
                groups = self._group_by_topics(chunks, max_groups)

        except Exception as e:
            logger.warning(f"Semantic grouping failed: {e}, using simple grouping")
            groups = self._group_by_topics(chunks, max_groups)

        return groups

    def _create_semantic_clusters(self, chunks: list[ContextChunk], max_groups: int) -> list[list[ContextChunk]]:
        """Create semantic clusters using embeddings"""
        # Group chunks by topic keywords similarity
        groups = []
        remaining_chunks = chunks.copy()

        while remaining_chunks and len(groups) < max_groups:
            # Start a new group with the most important remaining chunk
            seed_chunk = max(remaining_chunks, key=lambda c: c.importance_score)
            group = [seed_chunk]
            remaining_chunks.remove(seed_chunk)

            # Find semantically similar chunks
            for chunk in remaining_chunks[:]:
                if self._are_semantically_similar(seed_chunk, chunk):
                    group.append(chunk)
                    remaining_chunks.remove(chunk)

            groups.append(group)

        # Add remaining chunks to the largest group
        if remaining_chunks:
            largest_group = max(groups, key=len) if groups else []
            largest_group.extend(remaining_chunks)

        return groups

    def _group_by_topics(self, chunks: list[ContextChunk], max_groups: int) -> list[list[ContextChunk]]:
        """Group chunks by topic keywords"""
        groups = {}
        ungrouped = []

        for chunk in chunks:
            if chunk.topic_keywords:
                # Use first topic keyword as group identifier
                primary_topic = chunk.topic_keywords[0].lower()
                if primary_topic not in groups:
                    groups[primary_topic] = []
                groups[primary_topic].append(chunk)
            else:
                ungrouped.append(chunk)

        # Limit number of groups
        topic_groups = list(groups.values())
        if len(topic_groups) > max_groups:
            # Sort groups by total importance and keep top ones
            topic_groups.sort(key=lambda g: sum(c.importance_score for c in g), reverse=True)
            topic_groups = topic_groups[:max_groups]

            # Add chunks from excluded groups to ungrouped
            for group in groups.values():
                if group not in topic_groups:
                    ungrouped.extend(group)

        # Add ungrouped chunks to the largest group or create new group
        if ungrouped:
            if topic_groups:
                largest_group = max(topic_groups, key=len)
                largest_group.extend(ungrouped)
            else:
                topic_groups = [ungrouped]

        return topic_groups

    def _are_semantically_similar(self, chunk1: ContextChunk, chunk2: ContextChunk, threshold: float = 0.7) -> bool:
        """Check if two chunks are semantically similar

        Args:
            chunk1: First chunk
            chunk2: Second chunk
            threshold: Similarity threshold

        Returns:
            True if chunks are similar
        """
        # Check topic keyword overlap
        topics1 = set(chunk1.topic_keywords) if chunk1.topic_keywords else set()
        topics2 = set(chunk2.topic_keywords) if chunk2.topic_keywords else set()

        if topics1 and topics2:
            intersection = len(topics1.intersection(topics2))
            union = len(topics1.union(topics2))
            similarity = intersection / union if union > 0 else 0

            if similarity >= threshold:
                return True

        # Check content similarity (simple approach)
        words1 = set(chunk1.content.lower().split())
        words2 = set(chunk2.content.lower().split())

        if words1 and words2:
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            similarity = intersection / union if union > 0 else 0

            return similarity >= (threshold * 0.5)  # Lower threshold for content similarity

        return False


class ProgressiveCompressor:
    """Progressive compression with semantic preservation"""

    def __init__(self):
        self.context_compactor = get_context_compactor()
        self.importance_scorer = SemanticImportanceScorer()

    def compress_progressively(
        self,
        chunks: list[ContextChunk],
        target_tokens: int,
        preserve_semantics: bool = True,
    ) -> dict[str, Any]:
        """Compress chunks progressively while preserving semantic content

        Args:
            chunks: List of context chunks to compress
            target_tokens: Target token count
            preserve_semantics: Whether to prioritize semantic preservation

        Returns:
            Dictionary with compression results
        """
        logger.info(f"Progressively compressing {len(chunks)} chunks to {target_tokens} tokens")

        if not chunks:
            return {
                "compressed_content": "",
                "chunks_used": [],
                "compression_ratio": 1.0,
                "semantic_preservation": 0.0,
            }

        # Score chunks by importance
        scored_chunks = self.importance_scorer.score_chunks(chunks)

        if preserve_semantics:
            # Use semantic grouping for better preservation
            semantic_groups = self.importance_scorer.extract_semantic_groups(scored_chunks)
            compressed_content, chunks_used = self._compress_semantically(semantic_groups, target_tokens)
            semantic_preservation = self._calculate_semantic_preservation(semantic_groups, chunks_used)
        else:
            # Simple importance-based compression
            compressed_content, chunks_used = self._compress_by_importance(scored_chunks, target_tokens)
            semantic_preservation = 0.7  # Default for non-semantic compression

        # Calculate compression metrics
        original_tokens = sum(len(chunk.content.split()) for chunk in chunks)
        compressed_tokens = len(compressed_content.split())
        compression_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0

        return {
            "compressed_content": compressed_content,
            "chunks_used": chunks_used,
            "chunks_discarded": [c for c in chunks if c not in chunks_used],
            "compression_ratio": compression_ratio,
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "semantic_preservation": semantic_preservation,
            "preservation_method": "semantic" if preserve_semantics else "importance",
        }

    def _compress_semantically(
        self, semantic_groups: list[list[ContextChunk]], target_tokens: int
    ) -> tuple[str, list[ContextChunk]]:
        """Compress using semantic grouping to preserve context relationships

        Args:
            semantic_groups: Groups of semantically related chunks
            target_tokens: Target token count

        Returns:
            Tuple of (compressed_content, used_chunks)
        """
        content_parts = []
        used_chunks = []
        current_tokens = 0

        # Sort groups by total importance
        group_importance = [(group, sum(chunk.importance_score for chunk in group)) for group in semantic_groups]
        group_importance.sort(key=lambda x: x[1], reverse=True)

        for group, _importance in group_importance:
            if current_tokens >= target_tokens:
                break

            # Compress each group
            group_content, group_chunks, group_tokens = self._compress_group(group, target_tokens - current_tokens)

            if group_content:
                content_parts.append(f"## Semantic Group: {self._get_group_topic(group)}")
                content_parts.append(group_content)
                used_chunks.extend(group_chunks)
                current_tokens += group_tokens

        compressed_content = "\n\n".join(content_parts)
        return compressed_content, used_chunks

    def _compress_by_importance(
        self, scored_chunks: list[ContextChunk], target_tokens: int
    ) -> tuple[str, list[ContextChunk]]:
        """Compress by chunk importance (simpler method)

        Args:
            scored_chunks: Chunks sorted by importance
            target_tokens: Target token count

        Returns:
            Tuple of (compressed_content, used_chunks)
        """
        content_parts = []
        used_chunks = []
        current_tokens = 0

        for chunk in scored_chunks:
            chunk_tokens = len(chunk.content.split())
            if current_tokens + chunk_tokens > target_tokens:
                # Try to include truncated version
                remaining_tokens = target_tokens - current_tokens
                if remaining_tokens > 20:  # Only if meaningful space remains
                    truncated = self._truncate_chunk(chunk, remaining_tokens)
                    if truncated:
                        content_parts.append(f"## {chunk.source}")
                        content_parts.append(truncated)
                        used_chunks.append(chunk)
                break

            content_parts.append(f"## {chunk.source}")
            content_parts.append(chunk.content)
            used_chunks.append(chunk)
            current_tokens += chunk_tokens

        compressed_content = "\n\n".join(content_parts)
        return compressed_content, used_chunks

    def _compress_group(self, group: list[ContextChunk], max_tokens: int) -> tuple[str, list[ContextChunk], int]:
        """Compress a single semantic group

        Args:
            group: Semantic group to compress
            max_tokens: Maximum tokens for this group

        Returns:
            Tuple of (group_content, used_chunks, tokens_used)
        """
        if not group:
            return "", [], 0

        # Sort chunks in group by importance
        group_sorted = sorted(group, key=lambda c: c.importance_score, reverse=True)

        content_parts = []
        used_chunks = []
        current_tokens = 0

        # Add group header
        header = f"### Group Overview ({len(group)} items)"
        header_tokens = len(header.split())
        if current_tokens + header_tokens > max_tokens:
            return "", [], 0

        content_parts.append(header)
        current_tokens += header_tokens

        # Add chunks
        for chunk in group_sorted:
            chunk_tokens = len(chunk.content.split())
            if current_tokens + chunk_tokens > max_tokens:
                break

            content_parts.append(f"#### {chunk.source} ({chunk.chunk_type})")
            content_parts.append(chunk.content)
            used_chunks.append(chunk)
            current_tokens += chunk_tokens

        group_content = "\n".join(content_parts)
        return group_content, used_chunks, current_tokens

    def _get_group_topic(self, group: list[ContextChunk]) -> str:
        """Get representative topic for a semantic group

        Args:
            group: Semantic group

        Returns:
            Topic name
        """
        if not group:
            return "Unknown"

        # Collect all topic keywords
        all_keywords = []
        for chunk in group:
            all_keywords.extend(chunk.topic_keywords)

        if not all_keywords:
            # Use source names as fallback
            sources = [chunk.source for chunk in group]
            if sources:
                return f"Sources: {', '.join(sources[:3])}"
            return "Mixed Content"

        # Find most common topic
        from collections import Counter

        keyword_counts = Counter(all_keywords)
        most_common = keyword_counts.most_common(1)[0][0]
        return most_common.title()

    def _truncate_chunk(self, chunk: ContextChunk, max_tokens: int) -> str:
        """Truncate a chunk to fit within token limit

        Args:
            chunk: Chunk to truncate
            max_tokens: Maximum tokens

        Returns:
            Truncated content or empty string if too small
        """
        words = chunk.content.split()
        if len(words) <= max_tokens:
            return chunk.content

        # Try to truncate at sentence boundaries
        truncated_words = words[:max_tokens]
        truncated_text = " ".join(truncated_words)

        # Find last sentence boundary
        last_period = truncated_text.rfind(".")
        last_question = truncated_text.rfind("?")
        last_exclamation = truncated_text.rfind("!")

        last_boundary = max(last_period, last_question, last_exclamation)
        if last_boundary > max_tokens * 0.7:  # Only use if we're not cutting too much
            return truncated_text[: last_boundary + 1]

        # Add ellipsis if we cut mid-sentence
        if len(truncated_words) > 5:  # Only if meaningful content remains
            return truncated_text + "..."
        return ""  # Too small to be useful

    def _calculate_semantic_preservation(
        self, original_groups: list[list[ContextChunk]], used_chunks: list[ContextChunk]
    ) -> float:
        """Calculate how well semantic relationships were preserved

        Args:
            original_groups: Original semantic groups
            used_chunks: Chunks that were included in compression

        Returns:
            Semantic preservation score (0.0 to 1.0)
        """
        if not original_groups:
            return 1.0

        total_groups = len(original_groups)
        preserved_groups = 0

        # Check how many groups have at least one chunk preserved
        for group in original_groups:
            if any(chunk in used_chunks for chunk in group):
                preserved_groups += 1

        # Calculate preservation ratio
        group_preservation = preserved_groups / total_groups

        # Factor in chunk preservation within groups
        total_chunks = sum(len(group) for group in original_groups)
        preserved_chunks = len(used_chunks)
        chunk_preservation = preserved_chunks / total_chunks if total_chunks > 0 else 0

        # Weighted average (group preservation is more important)
        semantic_preservation = group_preservation * 0.7 + chunk_preservation * 0.3

        return min(1.0, semantic_preservation)


class SemanticCheckpointManager:
    """Enhanced checkpoint manager with semantic analysis"""

    def __init__(self, checkpoint_manager: CheckpointManager | None = None):
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()
        self.importance_scorer = SemanticImportanceScorer()
        self.progressive_compressor = ProgressiveCompressor()

        logger.info("SemanticCheckpointManager initialized")

    def create_semantic_checkpoint(
        self,
        task_name: str,
        context_chunks: list[ContextChunk],
        task_status: str = "in_progress",
        target_tokens: int | None = None,
        preserve_semantics: bool = True,
        additional_metadata: dict[str, Any] | None = None,
    ) -> str:
        """Create a checkpoint with semantic analysis and progressive compression

        Args:
            task_name: Name of the current task
            context_chunks: Context chunks to include
            task_status: Current task status
            target_tokens: Target token count (auto-determined if None)
            preserve_semantics: Whether to prioritize semantic preservation
            additional_metadata: Additional metadata

        Returns:
            Checkpoint ID
        """
        logger.info(f"Creating semantic checkpoint for task: {task_name}")

        if not context_chunks:
            logger.warning("No context chunks provided for semantic checkpoint")
            return self.checkpoint_manager.create_checkpoint(
                task_name=task_name,
                task_status=task_status,
                additional_metadata={
                    "semantic_checkpoint": True,
                    "no_chunks": True,
                    **(additional_metadata or {}),
                },
            )

        # Score chunks by semantic importance
        scored_chunks = self.importance_scorer.score_chunks(context_chunks)

        # Determine target tokens based on content size
        if target_tokens is None:
            total_tokens = sum(len(chunk.content.split()) for chunk in context_chunks)
            if total_tokens > 50000:
                target_tokens = 5000  # Heavy compression for large content
            elif total_tokens > 20000:
                target_tokens = 10000  # Moderate compression
            else:
                target_tokens = min(15000, total_tokens)  # Light compression

        # Perform progressive compression
        compression_result = self.progressive_compressor.compress_progressively(
            scored_chunks, target_tokens, preserve_semantics
        )

        # Extract metadata from compression
        chunks_used = compression_result["chunks_used"]
        chunks_discarded = compression_result["chunks_discarded"]

        # Extract key findings and next steps from used chunks
        key_findings = self._extract_semantic_findings(chunks_used)
        next_steps = self._extract_semantic_next_steps(chunks_used)
        files_modified = self._extract_files_from_chunks(chunks_used)

        # Determine checkpoint level based on compression
        compression_ratio = compression_result["compression_ratio"]
        if compression_ratio < 0.1:
            level = CheckpointLevel.METADATA
        elif compression_ratio < 0.3:
            level = CheckpointLevel.ESSENTIAL
        elif compression_ratio < 0.6:
            level = CheckpointLevel.COMPRESSED
        else:
            level = CheckpointLevel.FULL

        # Create the checkpoint
        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            task_name=task_name,
            task_status=task_status,
            level=level,
            trigger=self.checkpoint_manager.current_task and "semantic_auto" or "manual",
            key_findings=key_findings,
            files_modified=files_modified,
            next_steps=next_steps,
            content=compression_result["compressed_content"],
            additional_metadata={
                "semantic_checkpoint": True,
                "compression_result": compression_result,
                "original_chunk_count": len(context_chunks),
                "used_chunk_count": len(chunks_used),
                "discarded_chunk_count": len(chunks_discarded),
                "semantic_preservation": compression_result["semantic_preservation"],
                "preserve_semantics": preserve_semantics,
                **(additional_metadata or {}),
            },
        )

        logger.info(f"Created semantic checkpoint {checkpoint_id}")
        logger.info(
            f"Compression: {compression_ratio:.2f}, Semantic preservation: {compression_result['semantic_preservation']:.2f}"
        )

        return checkpoint_id

    def _extract_semantic_findings(self, chunks: list[ContextChunk]) -> list[str]:
        """Extract key findings using semantic analysis"""
        findings = []

        # Sort chunks by importance
        sorted_chunks = sorted(chunks, key=lambda c: c.importance_score, reverse=True)

        for chunk in sorted_chunks[:10]:  # Top 10 most important
            # Look for decision and insight patterns
            content_lower = chunk.content.lower()

            if any(
                indicator in content_lower
                for indicator in ["decided", "conclusion", "realized", "discovered", "found", "identified"]
            ):
                findings.append(f"Insight from {chunk.source}: {chunk.content[:100]}...")

            elif any(
                indicator in content_lower
                for indicator in ["problem", "issue", "error", "bug", "challenge", "obstacle"]
            ):
                findings.append(f"Issue from {chunk.source}: {chunk.content[:100]}...")

            elif any(
                indicator in content_lower
                for indicator in ["solution", "fix", "resolve", "implement", "create", "develop"]
            ):
                findings.append(f"Solution from {chunk.source}: {chunk.content[:100]}...")

        return findings[:8]  # Limit to top 8 findings

    def _extract_semantic_next_steps(self, chunks: list[ContextChunk]) -> list[str]:
        """Extract next steps using semantic analysis"""
        next_steps = []

        # Look for action items and incomplete work
        for chunk in chunks:
            content_lower = chunk.content.lower()

            # Look for explicit next steps
            if any(
                indicator in content_lower for indicator in ["next", "following", "subsequent", "then", "after this"]
            ):
                next_steps.append(f"Next from {chunk.source}: {chunk.content[:80]}...")

            # Look for incomplete actions
            elif any(indicator in content_lower for indicator in ["need to", "should", "must", "will", "plan to"]):
                next_steps.append(f"Action item from {chunk.source}: {chunk.content[:80]}...")

        return next_steps[:6]  # Limit to top 6 next steps

    def _extract_files_from_chunks(self, chunks: list[ContextChunk]) -> list[str]:
        """Extract file references from chunks"""
        import re

        files = set()

        for chunk in chunks:
            # Look for file paths
            file_patterns = [
                r"[^\s]+\.(py|js|ts|json|md|txt|yaml|yml|html|css|sql|sh)",
                r"[a-zA-Z0-9_\-/]+\.[a-zA-Z0-9_\-/]+",
            ]

            for pattern in file_patterns:
                matches = re.findall(pattern, chunk.content)
                for match in matches:
                    if "/" in match or "." in match:  # Likely a file path
                        files.add(match)

        return list(files)[:15]  # Limit to top 15 files


# Global semantic checkpoint manager instance
_semantic_checkpoint_manager: SemanticCheckpointManager | None = None


def get_semantic_checkpoint_manager(
    checkpoint_manager: CheckpointManager | None = None,
) -> SemanticCheckpointManager:
    """Get the global semantic checkpoint manager instance"""
    global _semantic_checkpoint_manager
    if _semantic_checkpoint_manager is None:
        _semantic_checkpoint_manager = SemanticCheckpointManager(checkpoint_manager)
    return _semantic_checkpoint_manager
