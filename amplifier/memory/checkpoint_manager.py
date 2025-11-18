"""
Memory Checkpoint Manager - Automatic Context Saving and Restoration

Implements intelligent checkpointing system for context management.
Provides automatic triggering, smart storage, and restoration capabilities.

Key Features:
- Auto-checkpoint triggers (task completion, context window usage, time-based, work area switching)
- Progressive compression integration
- Semantic importance scoring for checkpoint content
- Memory system integration for persistence
- Context restoration capabilities
- Integration with hook system
- Follows ruthless simplicity principles
"""

import json
import logging
import uuid
from datetime import datetime
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from .core import MemoryStore
from .models import Memory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CheckpointTrigger(Enum):
    """Types of checkpoint triggers"""

    TASK_COMPLETION = "task_completion"
    CONTEXT_THRESHOLD = "context_threshold"
    TIME_INTERVAL = "time_interval"
    WORK_AREA_SWITCH = "work_area_switch"
    MANUAL = "manual"


class CheckpointLevel(Enum):
    """Checkpoint detail levels"""

    FULL = "full"  # Complete context
    COMPRESSED = "compressed"  # Compressed summary
    ESSENTIAL = "essential"  # Critical points only
    METADATA = "metadata"  # Just references


class Checkpoint:
    """A memory checkpoint with metadata"""

    def __init__(
        self,
        checkpoint_id: str,
        timestamp: datetime,
        level: CheckpointLevel,
        trigger: CheckpointTrigger,
        task_name: str,
        task_status: str,
        key_findings: list[str],
        files_modified: list[str],
        next_steps: list[str],
        content: str,
        metadata: dict[str, Any],
    ):
        self.checkpoint_id = checkpoint_id
        self.timestamp = timestamp
        self.level = level
        self.trigger = trigger
        self.task_name = task_name
        self.task_status = task_status
        self.key_findings = key_findings
        self.files_modified = files_modified
        self.next_steps = next_steps
        self.content = content
        self.metadata = metadata

    @property
    def work_area(self) -> str:
        """Get the work area from metadata"""
        return self.metadata.get("work_area", "unknown")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "checkpoint_id": self.checkpoint_id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value if hasattr(self.level, "value") else self.level,
            "trigger": self.trigger.value if hasattr(self.trigger, "value") else self.trigger,
            "task_name": self.task_name,
            "task_status": self.task_status,
            "key_findings": self.key_findings,
            "files_modified": self.files_modified,
            "next_steps": self.next_steps,
            "content": self.content,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Checkpoint":
        """Create from dictionary"""
        return cls(
            checkpoint_id=data["checkpoint_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            level=CheckpointLevel(data["level"]),
            trigger=CheckpointTrigger(data["trigger"]),
            task_name=data["task_name"],
            task_status=data["task_status"],
            key_findings=data["key_findings"],
            files_modified=data["files_modified"],
            next_steps=data["next_steps"],
            content=data["content"],
            metadata=data["metadata"],
        )


class CheckpointManager:
    """Manages memory checkpoints with automatic triggering and restoration"""

    def __init__(
        self,
        data_dir: Path | None = None,
        max_checkpoints: int = 50,
        checkpoint_interval_minutes: int = 30,
        context_threshold_percent: int = 50,
    ):
        """Initialize checkpoint manager

        Args:
            data_dir: Directory for checkpoint storage
            max_checkpoints: Maximum checkpoints to keep
            checkpoint_interval_minutes: Auto-checkpoint interval
            context_threshold_percent: Context usage threshold for auto-checkpoint
        """
        self.data_dir = data_dir or Path(".data")
        self.checkpoint_file = self.data_dir / "checkpoints.json"
        self.max_checkpoints = max_checkpoints
        self.checkpoint_interval = timedelta(minutes=checkpoint_interval_minutes)
        self.context_threshold = context_threshold_percent

        # Initialize memory store for integration
        self.memory_store = MemoryStore(self.data_dir)

        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load existing checkpoints
        self.checkpoints: dict[str, Checkpoint] = self._load_checkpoints()

        # Track last checkpoint time for interval triggering
        self.last_checkpoint_time = self._get_latest_checkpoint_time()

        # Track current task state
        self.current_task: dict[str, Any] | None = None
        self.work_area: str | None = None

        logger.info(f"CheckpointManager initialized with {len(self.checkpoints)} checkpoints")

    def create_checkpoint(
        self,
        task_name: str,
        task_status: str = "in_progress",
        level: CheckpointLevel = CheckpointLevel.FULL,
        trigger: CheckpointTrigger = CheckpointTrigger.MANUAL,
        key_findings: list[str] | None = None,
        files_modified: list[str] | None = None,
        next_steps: list[str] | None = None,
        content: str | None = None,
        additional_metadata: dict[str, Any] | None = None,
    ) -> str:
        """Create a new checkpoint

        Args:
            task_name: Name of the current task
            task_status: Current task status
            level: Checkpoint detail level
            trigger: What triggered this checkpoint
            key_findings: List of key findings/decisions
            files_modified: List of files that were modified
            next_steps: Next steps to continue work
            content: Optional content to include
            additional_metadata: Additional metadata

        Returns:
            Checkpoint ID
        """
        checkpoint_id = str(uuid.uuid4())
        timestamp = datetime.now()

        # Generate content if not provided
        if content is None:
            content = self._generate_checkpoint_content(level, trigger)

        # Create checkpoint
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            timestamp=timestamp,
            level=level,
            trigger=trigger,
            task_name=task_name,
            task_status=task_status,
            key_findings=key_findings or [],
            files_modified=files_modified or [],
            next_steps=next_steps or [],
            content=content,
            metadata={
                "work_area": self.work_area,
                "context_usage": self._estimate_context_usage(),
                "checkpoint_version": "1.0",
                **(additional_metadata or {}),
            },
        )

        # Store checkpoint
        self.checkpoints[checkpoint_id] = checkpoint
        self.last_checkpoint_time = timestamp

        # Save to persistent storage
        self._save_checkpoints()

        # Store in memory system for additional persistence
        self._store_checkpoint_in_memory(checkpoint)

        # Clean up old checkpoints
        self._cleanup_old_checkpoints()

        # Handle both enum and string triggers for robustness
        trigger_value = trigger.value if hasattr(trigger, "value") else trigger
        logger.info(f"Created checkpoint {checkpoint_id}: {task_name} ({trigger_value})")
        return checkpoint_id

    def should_checkpoint(self, trigger: CheckpointTrigger) -> bool:
        """Check if a checkpoint should be created for the given trigger

        Args:
            trigger: Type of trigger to check

        Returns:
            True if checkpoint should be created
        """
        if trigger == CheckpointTrigger.TIME_INTERVAL:
            if self.last_checkpoint_time is None:
                return True
            return datetime.now() - self.last_checkpoint_time >= self.checkpoint_interval

        if trigger == CheckpointTrigger.CONTEXT_THRESHOLD:
            return self._estimate_context_usage() >= self.context_threshold

        if trigger == CheckpointTrigger.WORK_AREA_SWITCH:
            # Always checkpoint when switching work areas
            return True

        if trigger == CheckpointTrigger.TASK_COMPLETION:
            # Always checkpoint when completing major tasks
            return True

        # Default to no checkpoint for manual triggers
        return False

    def restore_checkpoint(self, checkpoint_id: str) -> dict[str, Any] | None:
        """Restore a checkpoint to continue work

        Args:
            checkpoint_id: ID of checkpoint to restore

        Returns:
            Dictionary with restored context or None if not found
        """
        checkpoint = self.checkpoints.get(checkpoint_id)
        if not checkpoint:
            logger.warning(f"Checkpoint {checkpoint_id} not found")
            return None

        # Update current task state
        self.current_task = {
            "name": checkpoint.task_name,
            "status": checkpoint.task_status,
            "restored_from": checkpoint_id,
            "restored_at": datetime.now().isoformat(),
        }
        self.work_area = checkpoint.metadata.get("work_area")

        # Store restoration in memory system
        self.memory_store.add_memory(
            Memory(
                content=f"Restored checkpoint: {checkpoint.task_name} from {checkpoint.timestamp}",
                category="learning",
                metadata={
                    "type": "checkpoint_restoration",
                    "checkpoint_id": checkpoint_id,
                    "original_timestamp": checkpoint.timestamp.isoformat(),
                },
            )
        )

        logger.info(f"Restored checkpoint {checkpoint_id}: {checkpoint.task_name}")

        return {
            "checkpoint": checkpoint.to_dict(),
            "context": {
                "task_name": checkpoint.task_name,
                "task_status": checkpoint.task_status,
                "key_findings": checkpoint.key_findings,
                "files_modified": checkpoint.files_modified,
                "next_steps": checkpoint.next_steps,
                "content": checkpoint.content,
                "work_area": checkpoint.metadata.get("work_area"),
            },
            "restoration_metadata": {
                "restored_at": datetime.now().isoformat(),
                "checkpoint_age": datetime.now() - checkpoint.timestamp,
            },
        }

    def get_recent_checkpoints(self, limit: int = 10) -> list[Checkpoint]:
        """Get recent checkpoints

        Args:
            limit: Maximum number of checkpoints to return

        Returns:
            List of checkpoints sorted by timestamp (newest first)
        """
        checkpoints = list(self.checkpoints.values())
        checkpoints.sort(key=lambda c: c.timestamp, reverse=True)
        return checkpoints[:limit]

    def get_checkpoints_by_task(self, task_name: str) -> list[Checkpoint]:
        """Get all checkpoints for a specific task

        Args:
            task_name: Name of the task

        Returns:
            List of checkpoints for the task
        """
        return [c for c in self.checkpoints.values() if c.task_name == task_name]

    def update_current_task(
        self,
        task_name: str,
        task_status: str = "in_progress",
        work_area: str | None = None,
    ):
        """Update the current task state

        Args:
            task_name: Name of the current task
            task_status: Current task status
            work_area: Current work area
        """
        old_work_area = self.work_area
        self.current_task = {"name": task_name, "status": task_status}
        self.work_area = work_area

        # Check if work area switched
        if old_work_area and old_work_area != self.work_area:
            if self.should_checkpoint(CheckpointTrigger.WORK_AREA_SWITCH):
                self.create_checkpoint(
                    task_name=task_name,
                    task_status=task_status,
                    trigger=CheckpointTrigger.WORK_AREA_SWITCH,
                    additional_metadata={
                        "old_work_area": old_work_area,
                        "new_work_area": self.work_area,
                    },
                )

    def check_auto_triggers(self) -> list[str]:
        """Check all automatic triggers and create checkpoints if needed

        Returns:
            List of created checkpoint IDs
        """
        created_checkpoint_ids = []

        if not self.current_task:
            return created_checkpoint_ids

        # Check time interval trigger
        if self.should_checkpoint(CheckpointTrigger.TIME_INTERVAL):
            checkpoint_id = self.create_checkpoint(
                task_name=self.current_task["name"],
                task_status=self.current_task["status"],
                trigger=CheckpointTrigger.TIME_INTERVAL,
            )
            created_checkpoint_ids.append(checkpoint_id)

        # Check context threshold trigger
        if self.should_checkpoint(CheckpointTrigger.CONTEXT_THRESHOLD):
            checkpoint_id = self.create_checkpoint(
                task_name=self.current_task["name"],
                task_status=self.current_task["status"],
                trigger=CheckpointTrigger.CONTEXT_THRESHOLD,
                level=CheckpointLevel.COMPRESSED,  # Compress for threshold triggers
            )
            created_checkpoint_ids.append(checkpoint_id)

        return created_checkpoint_ids

    def complete_task(
        self,
        task_name: str,
        key_findings: list[str] | None = None,
        files_modified: list[str] | None = None,
        next_steps: list[str] | None = None,
    ) -> str:
        """Create a completion checkpoint for a task

        Args:
            task_name: Name of the completed task
            key_findings: Key findings/decisions made
            files_modified: Files that were modified
            next_steps: Next steps for continuing work

        Returns:
            Checkpoint ID
        """
        checkpoint_id = self.create_checkpoint(
            task_name=task_name,
            task_status="completed",
            trigger=CheckpointTrigger.TASK_COMPLETION,
            level=CheckpointLevel.FULL,
            key_findings=key_findings,
            files_modified=files_modified,
            next_steps=next_steps,
        )

        # Clear current task
        self.current_task = None

        logger.info(f"Task completed: {task_name}")
        return checkpoint_id

    def get_checkpoint_statistics(self) -> dict[str, Any]:
        """Get statistics about checkpoints

        Returns:
            Dictionary with checkpoint statistics
        """
        if not self.checkpoints:
            return {"total_checkpoints": 0}

        # Analyze checkpoints
        total_checkpoints = len(self.checkpoints)
        triggers = {}
        levels = {}
        tasks = {}

        for checkpoint in self.checkpoints.values():
            # Count triggers
            trigger_val = checkpoint.trigger.value if hasattr(checkpoint.trigger, "value") else checkpoint.trigger
            triggers[trigger_val] = triggers.get(trigger_val, 0) + 1
            # Count levels
            level_val = checkpoint.level.value if hasattr(checkpoint.level, "value") else checkpoint.level
            levels[level_val] = levels.get(level_val, 0) + 1
            # Count tasks
            tasks[checkpoint.task_name] = tasks.get(checkpoint.task_name, 0) + 1

        # Most common task
        most_common_task = max(tasks.items(), key=lambda x: x[1]) if tasks else None

        # Recent activity (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_checkpoints = [c for c in self.checkpoints.values() if c.timestamp >= recent_cutoff]

        return {
            "total_checkpoints": total_checkpoints,
            "triggers": triggers,
            "levels": levels,
            "unique_tasks": len(tasks),
            "most_common_task": most_common_task[0] if most_common_task else None,
            "recent_24h": len(recent_checkpoints),
            "current_task": self.current_task,
            "current_work_area": self.work_area,
            "last_checkpoint_time": self.last_checkpoint_time.isoformat() if self.last_checkpoint_time else None,
        }

    # Private methods

    def _load_checkpoints(self) -> dict[str, Checkpoint]:
        """Load checkpoints from storage"""
        if not self.checkpoint_file.exists():
            return {}

        try:
            with open(self.checkpoint_file) as f:
                data = json.load(f)
                checkpoints = {}
                for checkpoint_data in data.get("checkpoints", []):
                    checkpoint = Checkpoint.from_dict(checkpoint_data)
                    checkpoints[checkpoint.checkpoint_id] = checkpoint
                return checkpoints
        except Exception as e:
            logger.error(f"Failed to load checkpoints: {e}")
            return {}

    def _save_checkpoints(self):
        """Save checkpoints to storage"""
        try:
            data = {
                "checkpoints": [c.to_dict() for c in self.checkpoints.values()],
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "total_checkpoints": len(self.checkpoints),
                    "version": "1.0",
                },
            }

            with open(self.checkpoint_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save checkpoints: {e}")

    def _store_checkpoint_in_memory(self, checkpoint: Checkpoint):
        """Store checkpoint in memory system for additional persistence"""
        try:
            self.memory_store.add_memory(
                Memory(
                    content=f"Checkpoint: {checkpoint.task_name} - {checkpoint.task_status}",
                    category="learning",
                    metadata={
                        "type": "checkpoint",
                        "checkpoint_id": checkpoint.checkpoint_id,
                        "trigger": checkpoint.trigger.value
                        if hasattr(checkpoint.trigger, "value")
                        else checkpoint.trigger,
                        "level": checkpoint.level.value if hasattr(checkpoint.level, "value") else checkpoint.level,
                        "timestamp": checkpoint.timestamp.isoformat(),
                    },
                )
            )
        except Exception as e:
            logger.warning(f"Failed to store checkpoint in memory: {e}")

    def _cleanup_old_checkpoints(self):
        """Remove old checkpoints if exceeded limit"""
        if len(self.checkpoints) <= self.max_checkpoints:
            return

        # Sort by timestamp, keep most recent
        checkpoints = list(self.checkpoints.values())
        checkpoints.sort(key=lambda c: c.timestamp, reverse=True)

        # Remove oldest checkpoints
        to_remove = checkpoints[self.max_checkpoints :]
        for checkpoint in to_remove:
            del self.checkpoints[checkpoint.checkpoint_id]

        logger.info(f"Cleaned up {len(to_remove)} old checkpoints")
        self._save_checkpoints()

    def _get_latest_checkpoint_time(self) -> datetime | None:
        """Get timestamp of most recent checkpoint"""
        if not self.checkpoints:
            return None

        return max(c.timestamp for c in self.checkpoints.values())

    def _estimate_context_usage(self) -> int:
        """Estimate current context usage percentage

        This is a simplified estimation - in a real implementation,
        this would integrate with the actual context window management
        """
        # For now, use a simple heuristic based on recent activity
        recent_checkpoints = self.get_recent_checkpoints(limit=5)
        if not recent_checkpoints:
            return 0

        # Estimate based on checkpoint frequency and content size
        avg_content_size = sum(len(c.content) for c in recent_checkpoints) / len(recent_checkpoints)

        # Simple heuristic: larger content and more frequent checkpoints = higher usage
        usage = min(95, int((avg_content_size / 10000) * 100))
        return usage

    def _generate_checkpoint_content(self, level: CheckpointLevel, trigger: CheckpointTrigger) -> str:
        """Generate checkpoint content based on level and trigger

        Args:
            level: Checkpoint detail level
            trigger: What triggered the checkpoint

        Returns:
            Generated content
        """
        content_parts = []

        # Header
        trigger_val = trigger.value if hasattr(trigger, "value") else trigger
        content_parts.append(f"# Checkpoint - {str(trigger_val).replace('_', ' ').title()}")
        content_parts.append(f"Created: {datetime.now().isoformat()}")
        level_val = level.value if hasattr(level, "value") else level
        content_parts.append(f"Level: {level_val}")

        if self.current_task:
            content_parts.append(f"Task: {self.current_task['name']}")
            content_parts.append(f"Status: {self.current_task['status']}")

        if self.work_area:
            content_parts.append(f"Work Area: {self.work_area}")

        content_parts.append("")

        # Recent activity summary
        if level in [CheckpointLevel.FULL, CheckpointLevel.COMPRESSED]:
            content_parts.append("## Recent Activity")
            recent_memories = self.memory_store.search_recent(limit=5)
            for memory in recent_memories:
                content_parts.append(f"- {memory.content[:100]}...")
            content_parts.append("")

        # Key information based on level
        if level == CheckpointLevel.FULL:
            content_parts.append("## Full Context")
            content_parts.append("(Full context content would be included here)")
            content_parts.append("")
        elif level == CheckpointLevel.COMPRESSED:
            content_parts.append("## Summary")
            content_parts.append("(Compressed summary of current work)")
            content_parts.append("")
        elif level == CheckpointLevel.ESSENTIAL:
            content_parts.append("## Essential Points")
            content_parts.append("- Critical points only")
            content_parts.append("")
        elif level == CheckpointLevel.METADATA:
            content_parts.append("## Metadata")
            content_parts.append(f"- Total checkpoints: {len(self.checkpoints)}")
            content_parts.append(f"- Current work area: {self.work_area}")
            content_parts.append("")

        return "\n".join(content_parts)


# Global checkpoint manager instance
_checkpoint_manager: CheckpointManager | None = None


def get_checkpoint_manager() -> CheckpointManager:
    """Get the global checkpoint manager instance"""
    global _checkpoint_manager
    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager()
    return _checkpoint_manager
