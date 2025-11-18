"""
Intelligent Context Pruning Service

Implements auto-checkpointing at 25% usage intervals with progressive compression
and Docker storage integration for context preservation.

Key Features:
- Auto-checkpoint at 25%, 50%, 75%, 90% usage intervals
- Progressive compression (FULL → SUMMARY → ESSENTIAL → METADATA)
- Docker storage for persistent context preservation
- Intelligent context selection based on importance
- 70-95% token reduction while maintaining critical information
"""

import json
import time
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

from ..mcp.persistent_storage import DockerPersistentStorage
from ..utils.context_compactor import ContextCompactor
from ..utils.context_compactor import ContextLevel
from ..utils.context_compactor import create_context_chunk
from ..utils.logger import get_logger
from ..utils.token_utils import estimate_tokens

logger = get_logger(__name__)


class PruningTrigger(Enum):
    """Triggers for context pruning."""

    USAGE_THRESHOLD = "usage_threshold"
    TIME_INTERVAL = "time_interval"
    MESSAGE_COUNT = "message_count"
    MANUAL_REQUEST = "manual_request"
    CONTEXT_FULL = "context_full"


@dataclass
class ContextMetrics:
    """Metrics for context usage and performance."""

    current_tokens: int = 0
    max_tokens: int = 200000
    usage_percentage: float = 0.0
    last_check_time: datetime = field(default_factory=datetime.now)
    checkpoint_count: int = 0
    total_compression_ratio: float = 1.0
    last_pruning_time: datetime | None = None


@dataclass
class PruningConfig:
    """Configuration for context pruning behavior."""

    max_tokens: int = 200000
    checkpoint_thresholds: list[float] = field(default_factory=lambda: [0.25, 0.5, 0.75, 0.9])
    time_interval_minutes: int = 30
    message_interval: int = 20
    compression_target_ratios: dict[ContextLevel, float] = field(
        default_factory=lambda: {
            ContextLevel.FULL: 0.8,
            ContextLevel.SUMMARY: 0.5,
            ContextLevel.ESSENTIAL: 0.2,
            ContextLevel.METADATA: 0.05,
        }
    )
    docker_storage_enabled: bool = True
    auto_pruning_enabled: bool = True
    importance_decay_rate: float = 0.1  # How quickly importance decays over time


@dataclass
class ContextCheckpoint:
    """A saved context checkpoint."""

    checkpoint_id: str
    timestamp: datetime
    trigger: PruningTrigger
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    compression_level: ContextLevel
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    reconstruction_hints: list[str] = field(default_factory=list)


class ContextUsageMonitor:
    """Monitors context usage and triggers pruning actions."""

    def __init__(self, config: PruningConfig):
        self.config = config
        self.metrics = ContextMetrics(max_tokens=config.max_tokens)
        self.last_checkpoint_threshold = 0.0

    def update_usage(self, current_content: str) -> float:
        """Update current usage metrics and return usage percentage."""
        self.metrics.current_tokens = estimate_tokens(current_content)
        self.metrics.usage_percentage = self.metrics.current_tokens / self.metrics.max_tokens
        self.metrics.last_check_time = datetime.now()
        return self.metrics.usage_percentage

    def should_checkpoint(self, current_usage: float, trigger_type: PruningTrigger) -> bool:
        """Determine if a checkpoint should be created."""
        if trigger_type == PruningTrigger.USAGE_THRESHOLD:
            # Check if we've crossed a threshold
            for threshold in self.config.checkpoint_thresholds:
                if current_usage >= threshold and self.last_checkpoint_threshold < threshold:
                    self.last_checkpoint_threshold = threshold
                    return True
        elif trigger_type == PruningTrigger.TIME_INTERVAL:
            # Check if enough time has passed
            if self.metrics.last_pruning_time:
                elapsed = datetime.now() - self.metrics.last_pruning_time
                return elapsed.total_seconds() >= self.config.time_interval_minutes * 60
            return True
        elif trigger_type == PruningTrigger.MANUAL_REQUEST:
            return True
        elif trigger_type == PruningTrigger.CONTEXT_FULL:
            return current_usage >= 0.95

        return False

    def get_next_threshold(self) -> float | None:
        """Get the next checkpoint threshold."""
        for threshold in self.config.checkpoint_thresholds:
            if self.metrics.usage_percentage < threshold:
                return threshold
        return None


class IntelligentContextPruner:
    """Intelligent context pruning and checkpointing service."""

    def __init__(self, config: PruningConfig | None = None):
        self.config = config or PruningConfig()
        self.usage_monitor = ContextUsageMonitor(self.config)
        self.context_compactor = ContextCompactor(self.config.max_tokens)
        self.checkpoints: list[ContextCheckpoint] = []
        self.docker_storage = DockerPersistentStorage() if self.config.docker_storage_enabled else None

        # Context chunks for current session
        self.context_chunks: list[dict[str, Any]] = []
        self.session_start_time = datetime.now()

    async def add_context_chunk(
        self,
        content: str,
        source: str,
        chunk_type: str = "message",
        importance: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Add a context chunk and check if pruning is needed."""
        # Create context chunk
        chunk = create_context_chunk(
            content=content,
            source=source,
            chunk_type=chunk_type,
            importance_score=importance,
            tags=metadata.get("tags", []) if metadata else [],
            references=metadata.get("references", []) if metadata else [],
        )

        # Add to current context
        self.context_chunks.append(
            {
                "content": content,
                "source": source,
                "chunk_type": chunk_type,
                "importance": importance,
                "timestamp": chunk.timestamp,
                "metadata": metadata or {},
            }
        )

        # Update usage
        current_content = self._get_current_content()
        usage = self.usage_monitor.update_usage(current_content)

        # Check if pruning is needed
        if self.usage_monitor.should_checkpoint(usage, PruningTrigger.USAGE_THRESHOLD):
            await self.create_checkpoint(PruningTrigger.USAGE_THRESHOLD)
            return True

        return False

    async def create_checkpoint(
        self, trigger: PruningTrigger, target_level: ContextLevel | None = None
    ) -> ContextCheckpoint:
        """Create a context checkpoint with appropriate compression level."""
        start_time = time.time()

        # Determine compression level based on usage
        if target_level is None:
            usage = self.usage_monitor.metrics.usage_percentage
            if usage < 0.5:
                target_level = ContextLevel.FULL
            elif usage < 0.75:
                target_level = ContextLevel.SUMMARY
            elif usage < 0.9:
                target_level = ContextLevel.ESSENTIAL
            else:
                target_level = ContextLevel.METADATA

        # Convert chunks to compactor format
        from ..utils.context_compactor import ContextChunk as CompactorChunk

        compactor_chunks = []
        for chunk_data in self.context_chunks:
            compactor_chunk = CompactorChunk(
                content=chunk_data["content"],
                importance_score=chunk_data["importance"],
                timestamp=chunk_data["timestamp"],
                source=chunk_data["source"],
                chunk_type=chunk_data["chunk_type"],
                tags=chunk_data["metadata"].get("tags", []),
                references=chunk_data["metadata"].get("references", []),
            )
            compactor_chunks.append(compactor_chunk)

        # Apply intelligent importance decay
        compactor_chunks = self._apply_importance_decay(compactor_chunks)

        # Compress context
        max_target_tokens = int(self.config.max_tokens * self.config.compression_target_ratios[target_level])
        compressed = self.context_compactor.compress_context(compactor_chunks, target_level, max_target_tokens)

        # Create checkpoint
        checkpoint = ContextCheckpoint(
            checkpoint_id=f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            trigger=trigger,
            original_tokens=compressed.original_tokens,
            compressed_tokens=compressed.compressed_tokens,
            compression_ratio=compressed.compression_ratio,
            compression_level=compressed.level,
            content=compressed.content,
            metadata={
                "compression_time_seconds": time.time() - start_time,
                "chunk_count": len(compactor_chunks),
                "session_duration_minutes": (datetime.now() - self.session_start_time).total_seconds() / 60,
                "target_ratio": self.config.compression_target_ratios[target_level],
                "actual_ratio": compressed.compression_ratio,
                "source_distribution": compressed.metadata.get("source_distribution", {}),
                "parallel_compression": compressed.metadata.get("parallel_compression", False),
            },
            reconstruction_hints=compressed.reconstruction_hints,
        )

        # Store checkpoint
        self.checkpoints.append(checkpoint)
        self.usage_monitor.metrics.checkpoint_count += 1
        self.usage_monitor.metrics.last_pruning_time = datetime.now()

        # Save to Docker storage if enabled
        if self.docker_storage:
            await self._save_checkpoint_to_docker(checkpoint)

        # Prune current context chunks based on compression
        await self._prune_current_context(compressed)

        logger.info(
            f"Created checkpoint {checkpoint.checkpoint_id}: "
            f"{compressed.original_tokens} → {compressed.compressed_tokens} tokens "
            f"({compressed.compression_ratio:.1%} reduction) at {target_level.value} level"
        )

        return checkpoint

    def _apply_importance_decay(self, chunks: list[Any]) -> list[Any]:
        """Apply time-based importance decay to context chunks."""
        if not chunks:
            return chunks

        current_time = datetime.now()
        decayed_chunks = []

        for chunk in chunks:
            # Calculate time-based decay
            time_diff = (current_time - chunk.timestamp).total_seconds() / 3600  # Hours
            decay_factor = max(0.1, 1.0 - (self.config.importance_decay_rate * time_diff))

            # Apply decay to importance score
            chunk.importance_score = max(0.1, chunk.importance_score * decay_factor)
            decayed_chunks.append(chunk)

        # Sort by importance after decay
        return sorted(decayed_chunks, key=lambda c: c.importance_score, reverse=True)

    async def _prune_current_context(self, compressed_context: Any) -> None:
        """Prune current context chunks based on compression results."""
        # Keep only recent and high-importance chunks
        current_time = datetime.now()

        # Remove chunks that are likely included in compressed context
        # Keep chunks from the last 15 minutes or with high importance
        recent_cutoff = current_time.timestamp() - 15 * 60  # 15 minutes ago

        self.context_chunks = [
            chunk
            for chunk in self.context_chunks
            if (chunk["timestamp"].timestamp() > recent_cutoff or chunk["importance"] > 0.8)
        ]

        # Limit to maximum number of chunks
        max_chunks = 50
        if len(self.context_chunks) > max_chunks:
            # Sort by importance and timestamp, keep the best
            self.context_chunks.sort(key=lambda c: (c["importance"], c["timestamp"].timestamp()), reverse=True)
            self.context_chunks = self.context_chunks[:max_chunks]

    async def _save_checkpoint_to_docker(self, checkpoint: ContextCheckpoint) -> bool:
        """Save checkpoint to Docker persistent storage."""
        try:
            if not self.docker_storage:
                return False

            # Create checkpoint directory
            checkpoint_dir = self.docker_storage.cache_dir / "checkpoints"
            checkpoint_dir.mkdir(exist_ok=True)

            # Save checkpoint data
            checkpoint_file = checkpoint_dir / f"{checkpoint.checkpoint_id}.json"
            checkpoint_data = {
                "checkpoint_id": checkpoint.checkpoint_id,
                "timestamp": checkpoint.timestamp.isoformat(),
                "trigger": checkpoint.trigger.value,
                "original_tokens": checkpoint.original_tokens,
                "compressed_tokens": checkpoint.compressed_tokens,
                "compression_ratio": checkpoint.compression_ratio,
                "compression_level": checkpoint.compression_level.value,
                "content": checkpoint.content,
                "metadata": checkpoint.metadata,
                "reconstruction_hints": checkpoint.reconstruction_hints,
            }

            with open(checkpoint_file, "w") as f:
                json.dump(checkpoint_data, f, indent=2)

            # Update checkpoint index
            index_file = checkpoint_dir / "checkpoint_index.json"
            index_data = {"checkpoints": []}
            if index_file.exists():
                with open(index_file) as f:
                    index_data = json.load(f)

            checkpoint_entry = {
                "checkpoint_id": checkpoint.checkpoint_id,
                "timestamp": checkpoint.timestamp.isoformat(),
                "trigger": checkpoint.trigger.value,
                "compression_ratio": checkpoint.compression_ratio,
                "compression_level": checkpoint.compression_level.value,
                "original_tokens": checkpoint.original_tokens,
                "compressed_tokens": checkpoint.compressed_tokens,
            }

            # Add or update checkpoint entry
            index_data["checkpoints"] = [
                cp for cp in index_data["checkpoints"] if cp["checkpoint_id"] != checkpoint.checkpoint_id
            ]
            index_data["checkpoints"].append(checkpoint_entry)

            # Sort by timestamp and keep last 50 checkpoints
            index_data["checkpoints"].sort(key=lambda x: x["timestamp"], reverse=True)
            index_data["checkpoints"] = index_data["checkpoints"][:50]
            # type: ignore[arg-type]
            # type: ignore[arg-type]
            index_data["last_updated"] = datetime.now().isoformat()  # type: ignore[arg-type]

            with open(index_file, "w") as f:
                json.dump(index_data, f, indent=2)

            return True

        except Exception as e:
            logger.error(f"Failed to save checkpoint to Docker: {e}")
            return False

    async def load_checkpoint_from_docker(self, checkpoint_id: str) -> ContextCheckpoint | None:
        """Load a specific checkpoint from Docker storage."""
        try:
            if not self.docker_storage:
                return None

            checkpoint_dir = self.docker_storage.cache_dir / "checkpoints"
            checkpoint_file = checkpoint_dir / f"{checkpoint_id}.json"

            if not checkpoint_file.exists():
                logger.warning(f"Checkpoint not found: {checkpoint_id}")
                return None

            with open(checkpoint_file) as f:
                checkpoint_data = json.load(f)

            checkpoint = ContextCheckpoint(
                checkpoint_id=checkpoint_data["checkpoint_id"],
                timestamp=datetime.fromisoformat(checkpoint_data["timestamp"]),
                trigger=PruningTrigger(checkpoint_data["trigger"]),
                original_tokens=checkpoint_data["original_tokens"],
                compressed_tokens=checkpoint_data["compressed_tokens"],
                compression_ratio=checkpoint_data["compression_ratio"],
                compression_level=ContextLevel(checkpoint_data["compression_level"]),
                content=checkpoint_data["content"],
                metadata=checkpoint_data["metadata"],
                reconstruction_hints=checkpoint_data["reconstruction_hints"],
            )

            return checkpoint

        except Exception as e:
            logger.error(f"Failed to load checkpoint {checkpoint_id}: {e}")
            return None

    def _get_current_content(self) -> str:
        """Get current context content."""
        if not self.context_chunks:
            return ""

        # Combine recent chunks with some structure
        content_parts = []
        for chunk in self.context_chunks[-20:]:  # Last 20 chunks
            content_parts.append(f"[{chunk['source']}] {chunk['content']}")

        return "\n\n".join(content_parts)

    async def get_pruning_recommendations(self) -> dict[str, Any]:
        """Get recommendations for context pruning."""
        usage = self.usage_monitor.metrics.usage_percentage
        next_threshold = self.usage_monitor.get_next_threshold()

        recommendations = {
            "current_usage_percentage": usage,
            "current_tokens": self.usage_monitor.metrics.current_tokens,
            "max_tokens": self.usage_monitor.metrics.max_tokens,
            "next_threshold": next_threshold,
            "should_prune_now": usage >= next_threshold if next_threshold else False,
            "recommended_action": self._get_recommended_action(usage),
            "checkpoint_count": self.usage_monitor.metrics.checkpoint_count,
            "compression_efficiency": self._calculate_compression_efficiency(),
            "recent_checkpoints": self._get_recent_checkpoints_summary(),
        }

        return recommendations

    def _get_recommended_action(self, usage: float) -> str:
        """Get recommended action based on current usage."""
        if usage < 0.25:
            return "Continue monitoring - usage is low"
        if usage < 0.5:
            return "Consider light compression (FULL level)"
        if usage < 0.75:
            return "Apply moderate compression (SUMMARY level)"
        if usage < 0.9:
            return "Apply aggressive compression (ESSENTIAL level)"
        return "Immediate pruning required (METADATA level)"

    def _calculate_compression_efficiency(self) -> float:
        """Calculate overall compression efficiency."""
        if not self.checkpoints:
            return 1.0

        total_original = sum(cp.original_tokens for cp in self.checkpoints)
        total_compressed = sum(cp.compressed_tokens for cp in self.checkpoints)

        return total_compressed / total_original if total_original > 0 else 1.0

    def _get_recent_checkpoints_summary(self) -> list[dict[str, Any]]:
        """Get summary of recent checkpoints."""
        recent_checkpoints = self.checkpoints[-5:]  # Last 5 checkpoints
        return [
            {
                "id": cp.checkpoint_id,
                "timestamp": cp.timestamp.isoformat(),
                "trigger": cp.trigger.value,
                "compression_ratio": cp.compression_ratio,
                "level": cp.compression_level.value,
            }
            for cp in recent_checkpoints
        ]

    async def manual_pruning_request(self, target_level: ContextLevel | None = None) -> ContextCheckpoint:
        """Handle manual pruning request."""
        logger.info("Manual pruning request received")
        return await self.create_checkpoint(PruningTrigger.MANUAL_REQUEST, target_level)

    def get_compression_stats(self) -> dict[str, Any]:
        """Get comprehensive compression statistics."""
        if not self.checkpoints:
            return {"message": "No checkpoints available"}

        stats = {
            "total_checkpoints": len(self.checkpoints),
            "session_duration_minutes": (datetime.now() - self.session_start_time).total_seconds() / 60,
            "compression_by_level": {},
            "average_compression_ratio": 0.0,
            "total_tokens_saved": 0,
            "most_recent_checkpoint": None,
            "pruning_triggers": {},
        }

        total_original = 0
        total_compressed = 0

        for checkpoint in self.checkpoints:
            total_original += checkpoint.original_tokens
            total_compressed += checkpoint.compressed_tokens

            # Level-specific stats
            level = checkpoint.compression_level.value
            if level not in stats["compression_by_level"]:
                stats["compression_by_level"][level] = {
                    "count": 0,
                    "total_original": 0,
                    "total_compressed": 0,
                }

            stats["compression_by_level"][level]["count"] += 1
            stats["compression_by_level"][level]["total_original"] += checkpoint.original_tokens
            stats["compression_by_level"][level]["total_compressed"] += checkpoint.compressed_tokens

            # Trigger stats
            trigger = checkpoint.trigger.value
            stats["pruning_triggers"][trigger] = stats["pruning_triggers"].get(trigger, 0) + 1

        stats["average_compression_ratio"] = total_compressed / total_original if total_original > 0 else 0
        stats["total_tokens_saved"] = total_original - total_compressed
        stats["most_recent_checkpoint"] = self.checkpoints[-1].checkpoint_id if self.checkpoints else None

        return stats


# Global pruner instance
_intelligent_pruner = IntelligentContextPruner()


def get_intelligent_pruner() -> IntelligentContextPruner:
    """Get the global intelligent context pruner instance."""
    return _intelligent_pruner


async def initialize_intelligent_pruning(config: PruningConfig | None = None) -> IntelligentContextPruner:
    """Initialize the intelligent pruning system."""
    global _intelligent_pruner

    if config:
        _intelligent_pruner = IntelligentContextPruner(config)

    # Initialize Docker storage if enabled
    if _intelligent_pruner.docker_storage:
        await _intelligent_pruner.docker_storage.initialize_docker_volume()

    logger.info("Intelligent context pruning system initialized")
    return _intelligent_pruner


# Convenience functions for common operations
async def add_context_and_check(content: str, source: str, importance: float = 0.5) -> bool:
    """Add context chunk and check if pruning is needed."""
    pruner = get_intelligent_pruner()
    return await pruner.add_context_chunk(content, source, importance=importance)


async def create_manual_checkpoint(level: ContextLevel | None = None) -> ContextCheckpoint:
    """Create a manual checkpoint."""
    pruner = get_intelligent_pruner()
    return await pruner.manual_pruning_request(level)


def get_context_status() -> dict[str, Any]:
    """Get current context status and recommendations."""
    pruner = get_intelligent_pruner()
    return pruner.get_pruning_recommendations()


def get_compression_performance() -> dict[str, Any]:
    """Get compression performance statistics."""
    pruner = get_intelligent_pruner()
    return cast(dict[str, Any], pruner.get_compression_stats())
