"""
Checkpoint Triggers - Auto-Detection System for Context Checkpointing

Implements intelligent triggering mechanisms for automatic checkpoint creation.
Monitors various signals to determine optimal checkpointing moments.

Key Features:
- Auto-detection of task completion
- Context window usage monitoring
- Time-based interval triggering
- Work area switching detection
- Semantic importance analysis
- Integration with file system monitoring
- Hook system integration
"""

import logging
import re
from datetime import datetime
from datetime import timedelta
from typing import Any

from ..utils.logger import get_logger
from .checkpoint_manager import CheckpointLevel
from .checkpoint_manager import CheckpointManager
from .checkpoint_manager import CheckpointTrigger


# Hook logger fallback
class HookLogger:
    """Simple logger for hook integration"""

    def __init__(self, name: str):
        self.logger = get_logger(name)

    def info(self, message: str):
        self.logger.info(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def error(self, message: str):
        self.logger.error(message)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskCompletionDetector:
    """Detects task completion patterns in conversation and file changes"""

    def __init__(self):
        self.completion_patterns = [
            r"(?i)(done|complete[d]?|finished|success|implement|fix|create|add|remove|update).*\.",
            r"(?i)(all|everything).*is.*(done|complete|finished|ready)",
            r"(?i)task.*complete|project.*finish|goal.*achiev",
            r"(?i)(test|check|verify).*pass|succeed",
            r"(?i)(no|nothing).*more.*need|require|left",
        ]

        self.high_completion_indicators = [
            "successfully completed",
            "implementation complete",
            "all tests passing",
            "fully functional",
            "mission accomplished",
        ]

    def detect_completion(self, message: str, confidence_threshold: float = 0.7) -> tuple[bool, float]:
        """Detect if a message indicates task completion

        Args:
            message: Message content to analyze
            confidence_threshold: Minimum confidence to consider completion

        Returns:
            Tuple of (is_completion, confidence_score)
        """
        if not message:
            return False, 0.0

        message_lower = message.lower()
        confidence = 0.0

        # Check for high-confidence indicators
        for indicator in self.high_completion_indicators:
            if indicator in message_lower:
                confidence += 0.4
                logger.debug(f"High completion indicator found: {indicator}")

        # Check for completion patterns
        for pattern in self.completion_patterns:
            matches = re.findall(pattern, message)
            if matches:
                confidence += 0.2 * len(matches)
                logger.debug(f"Completion pattern matches: {matches}")

        # Check for completion verbs
        completion_verbs = ["completed", "finished", "done", "implemented", "fixed", "created"]
        verb_count = sum(1 for verb in completion_verbs if f" {verb} " in f" {message_lower} ")
        confidence += min(0.3, verb_count * 0.1)

        # Check for finality indicators
        finality_words = ["finally", "ultimately", "at last", "in conclusion"]
        for word in finality_words:
            if word in message_lower:
                confidence += 0.1

        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)

        logger.debug(f"Task completion detection: confidence={confidence:.2f}, threshold={confidence_threshold}")
        return confidence >= confidence_threshold, confidence


class ContextUsageMonitor:
    """Monitors context window usage and triggers checkpoints when needed"""

    def __init__(self, max_tokens: int = 100000, threshold_percent: int = 50):
        self.max_tokens = max_tokens
        self.threshold_percent = threshold_percent
        self.current_usage = 0
        self.usage_history = []

    def estimate_usage(self, context_data: dict[str, Any]) -> int:
        """Estimate current context usage percentage

        Args:
            context_data: Dictionary with context information

        Returns:
            Usage percentage (0-100)
        """
        # Simple heuristic based on context data size
        if not context_data:
            return 0

        # Count approximate tokens from various sources
        estimated_tokens = 0

        # Messages content
        messages = context_data.get("messages", [])
        for msg in messages:
            content = msg.get("content", "")
            estimated_tokens += len(content.split()) * 1.3  # Rough token estimate

        # File contents
        files = context_data.get("files", {})
        for file_content in files.values():
            if isinstance(file_content, str):
                estimated_tokens += len(file_content.split()) * 1.3

        # Tools and other context
        tools = context_data.get("tools", [])
        estimated_tokens += len(tools) * 100  # Estimate per tool

        # Calculate percentage
        usage_percent = min(100, int((estimated_tokens / self.max_tokens) * 100))

        # Update history
        self.usage_history.append(
            {
                "timestamp": datetime.now(),
                "usage_percent": usage_percent,
                "estimated_tokens": estimated_tokens,
            }
        )

        # Keep only last 100 entries
        self.usage_history = self.usage_history[-100:]

        self.current_usage = usage_percent
        return usage_percent

    def should_checkpoint(self, usage_percent: int) -> bool:
        """Determine if checkpoint should be triggered based on usage

        Args:
            usage_percent: Current usage percentage

        Returns:
            True if checkpoint should be triggered
        """
        return usage_percent >= self.threshold_percent

    def get_usage_trend(self) -> str:
        """Get usage trend analysis

        Returns:
            Trend description: "increasing", "decreasing", or "stable"
        """
        if len(self.usage_history) < 5:
            return "insufficient_data"

        recent = self.usage_history[-5:]
        changes = []

        for i in range(1, len(recent)):
            change = recent[i]["usage_percent"] - recent[i - 1]["usage_percent"]
            changes.append(change)

        avg_change = sum(changes) / len(changes)

        if avg_change > 5:
            return "increasing"
        if avg_change < -5:
            return "decreasing"
        return "stable"


class WorkAreaMonitor:
    """Monitors work area changes and detects switches"""

    def __init__(self):
        self.current_work_area: str | None = None
        self.work_area_patterns = [
            r".*/([^/]+)/.*\.py$",  # Python file paths
            r".*/([^/]+)/.*\.md$",  # Markdown file paths
            r".*/([^/]+)/.*\.json$",  # JSON file paths
        ]

        # Project indicators
        self.project_indicators = {
            "frontend": ["frontend", "ui", "components", "templates"],
            "backend": ["backend", "api", "server", "services"],
            "data": ["data", "database", "storage", "cache"],
            "tests": ["test", "spec", "e2e", "integration"],
            "docs": ["docs", "documentation", "readme"],
        }

    def detect_work_area(self, file_paths: list[str]) -> str | None:
        """Detect current work area from file paths

        Args:
            file_paths: List of file paths being worked on

        Returns:
            Detected work area or None
        """
        if not file_paths:
            return None

        # Extract directory patterns
        areas = []
        for file_path in file_paths:
            for pattern in self.work_area_patterns:
                match = re.search(pattern, file_path)
                if match:
                    areas.append(match.group(1))
                    break

        if not areas:
            return None

        # Find most common area
        from collections import Counter

        area_counter = Counter(areas)
        most_common_area = area_counter.most_common(1)[0][0]

        # Check if it matches any project indicators
        for project_type, indicators in self.project_indicators.items():
            if any(indicator in most_common_area.lower() for indicator in indicators):
                return project_type

        return most_common_area

    def has_switched(self, new_work_area: str | None) -> bool:
        """Check if work area has switched

        Args:
            new_work_area: Newly detected work area

        Returns:
            True if work area has switched
        """
        if self.current_work_area is None:
            self.current_work_area = new_work_area
            return False

        switched = self.current_work_area != new_work_area
        if switched:
            logger.info(f"Work area switched from '{self.current_work_area}' to '{new_work_area}'")
            self.current_work_area = new_work_area

        return switched


class CheckpointTriggerSystem:
    """Main trigger system that coordinates all detection mechanisms"""

    def __init__(self, checkpoint_manager: CheckpointManager):
        self.checkpoint_manager = checkpoint_manager
        self.task_detector = TaskCompletionDetector()
        self.context_monitor = ContextUsageMonitor()
        self.work_area_monitor = WorkAreaMonitor()

        # Hook logger for debugging
        self.hook_logger = HookLogger("checkpoint_triggers")

        # State tracking
        self.last_trigger_time: datetime | None = None
        self.trigger_history = []
        self.active_files: set[str] = set()

        # Configuration
        self.min_interval_minutes = 2  # Minimum time between auto-triggers
        self.enable_task_completion = True
        self.enable_context_monitoring = True
        self.enable_work_area_switching = True

    def check_task_completion(self, message: str) -> str | None:
        """Check if message indicates task completion and create checkpoint

        Args:
            message: Message content to analyze

        Returns:
            Checkpoint ID if created, None otherwise
        """
        if not self.enable_task_completion:
            return None

        if not self._can_trigger():
            return None

        is_completion, confidence = self.task_detector.detect_completion(message)
        if not is_completion:
            return None

        self.hook_logger.info(f"Task completion detected with confidence {confidence:.2f}")

        # Extract task name from message or use current task
        task_name = self._extract_task_name(message) or "Completed Task"

        # Create completion checkpoint
        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            task_name=task_name,
            task_status="completed",
            trigger=CheckpointTrigger.TASK_COMPLETION,
            level=CheckpointLevel.FULL,
            key_findings=[f"Task completion detected with confidence {confidence:.2f}"],
            content=message,
            additional_metadata={
                "completion_confidence": confidence,
                "trigger_message": message,
            },
        )

        self._record_trigger(CheckpointTrigger.TASK_COMPLETION, checkpoint_id)
        return checkpoint_id

    def check_context_usage(self, context_data: dict[str, Any]) -> str | None:
        """Check context usage and create checkpoint if needed

        Args:
            context_data: Current context data

        Returns:
            Checkpoint ID if created, None otherwise
        """
        if not self.enable_context_monitoring:
            return None

        if not self._can_trigger():
            return None

        usage_percent = self.context_monitor.estimate_usage(context_data)
        trend = self.context_monitor.get_usage_trend()

        self.hook_logger.info(f"Context usage: {usage_percent}% (trend: {trend})")

        if not self.context_monitor.should_checkpoint(usage_percent):
            return None

        # Determine compression level based on usage
        if usage_percent > 80:
            level = CheckpointLevel.METADATA
        elif usage_percent > 65:
            level = CheckpointLevel.ESSENTIAL
        else:
            level = CheckpointLevel.COMPRESSED

        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            task_name=self.checkpoint_manager.current_task.get("name", "Unknown Task")
            if self.checkpoint_manager.current_task
            else "Context Management",
            task_status=self.checkpoint_manager.current_task.get("status", "in_progress")
            if self.checkpoint_manager.current_task
            else "in_progress",
            trigger=CheckpointTrigger.CONTEXT_THRESHOLD,
            level=level,
            key_findings=[
                f"Context usage reached {usage_percent}%",
                f"Usage trend: {trend}",
            ],
            additional_metadata={
                "context_usage_percent": usage_percent,
                "usage_trend": trend,
                "estimated_tokens": int(usage_percent * 1000),  # Rough estimate
            },
        )

        self._record_trigger(CheckpointTrigger.CONTEXT_THRESHOLD, checkpoint_id)
        return checkpoint_id

    def check_work_area_switch(self, file_paths: list[str]) -> str | None:
        """Check for work area switches and create checkpoint

        Args:
            file_paths: List of currently active file paths

        Returns:
            Checkpoint ID if created, None otherwise
        """
        if not self.enable_work_area_switching:
            return None

        if not self._can_trigger():
            return None

        # Update active files
        new_files = set(file_paths)
        files_added = new_files - self.active_files
        self.active_files = new_files

        if not files_added:
            return None  # No new files to analyze

        new_work_area = self.work_area_monitor.detect_work_area(file_paths)

        if not self.work_area_monitor.has_switched(new_work_area):
            return None

        self.hook_logger.info(f"Work area switched to: {new_work_area}")

        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            task_name=self.checkpoint_manager.current_task.get("name", "Unknown Task")
            if self.checkpoint_manager.current_task
            else "Work Area Switch",
            task_status=self.checkpoint_manager.current_task.get("status", "in_progress")
            if self.checkpoint_manager.current_task
            else "in_progress",
            trigger=CheckpointTrigger.WORK_AREA_SWITCH,
            level=CheckpointLevel.COMPRESSED,
            key_findings=[
                f"Work area switched to: {new_work_area}",
                f"Active files: {len(file_paths)}",
            ],
            files_modified=list(files_added),
            additional_metadata={
                "new_work_area": new_work_area,
                "active_file_count": len(file_paths),
                "files_added": list(files_added),
            },
        )

        self._record_trigger(CheckpointTrigger.WORK_AREA_SWITCH, checkpoint_id)
        return checkpoint_id

    def check_time_interval(self) -> str | None:
        """Check if time interval trigger should fire

        Returns:
            Checkpoint ID if created, None otherwise
        """
        if not self.checkpoint_manager.should_checkpoint(CheckpointTrigger.TIME_INTERVAL):
            return None

        if not self._can_trigger():
            return None

        self.hook_logger.info("Time interval checkpoint triggered")

        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            task_name=self.checkpoint_manager.current_task.get("name", "Unknown Task")
            if self.checkpoint_manager.current_task
            else "Periodic Checkpoint",
            task_status=self.checkpoint_manager.current_task.get("status", "in_progress")
            if self.checkpoint_manager.current_task
            else "in_progress",
            trigger=CheckpointTrigger.TIME_INTERVAL,
            level=CheckpointLevel.COMPRESSED,
            key_findings=[
                "Periodic checkpoint - time interval reached",
                f"Active for {datetime.now() - self.checkpoint_manager.last_checkpoint_time if self.checkpoint_manager.last_checkpoint_time else 'unknown'}",
            ],
            additional_metadata={
                "interval_minutes": self.checkpoint_manager.checkpoint_interval.total_seconds() / 60,
                "current_work_area": self.checkpoint_manager.work_area,
            },
        )

        self._record_trigger(CheckpointTrigger.TIME_INTERVAL, checkpoint_id)
        return checkpoint_id

    def process_hook_data(self, hook_name: str, data: dict[str, Any]) -> str | None:
        """Process data from hook system and create checkpoints if needed

        Args:
            hook_name: Name of the hook that triggered
            data: Hook data

        Returns:
            Checkpoint ID if created, None otherwise
        """
        self.hook_logger.info(f"Processing hook: {hook_name}")

        checkpoint_id = None

        # Handle different hook types
        if hook_name == "pre_tool_use":
            # Check for task completion in tool input
            input_data = data.get("input", {})
            if isinstance(input_data, str):
                checkpoint_id = self.check_task_completion(input_data)

        elif hook_name == "post_tool_use":
            # Check for work area changes from tool output
            output_data = data.get("output", {})
            files_created = output_data.get("files_created", [])
            if files_created:
                checkpoint_id = self.check_work_area_switch(files_created)

        elif hook_name == "session_start":
            # Create session start checkpoint
            checkpoint_id = self.checkpoint_manager.create_checkpoint(
                task_name="Session Start",
                task_status="starting",
                trigger=CheckpointTrigger.MANUAL,
                level=CheckpointLevel.METADATA,
                additional_metadata={
                    "session_start": True,
                    "hook_data": data,
                },
            )

        elif hook_name == "session_end":
            # Create session end checkpoint
            checkpoint_id = self.checkpoint_manager.create_checkpoint(
                task_name=self.checkpoint_manager.current_task.get("name", "Session End")
                if self.checkpoint_manager.current_task
                else "Session End",
                task_status="session_ended",
                trigger=CheckpointTrigger.MANUAL,
                level=CheckpointLevel.FULL,
                additional_metadata={
                    "session_end": True,
                    "hook_data": data,
                },
            )

        if checkpoint_id:
            self.hook_logger.info(f"Created checkpoint {checkpoint_id} from hook {hook_name}")

        return checkpoint_id

    def run_periodic_check(self) -> list[str]:
        """Run all periodic checks and return created checkpoint IDs

        Returns:
            List of created checkpoint IDs
        """
        checkpoint_ids = []

        # Check time interval
        time_checkpoint = self.check_time_interval()
        if time_checkpoint:
            checkpoint_ids.append(time_checkpoint)

        # Check auto-triggers from checkpoint manager
        auto_checkpoints = self.checkpoint_manager.check_auto_triggers()
        checkpoint_ids.extend(auto_checkpoints)

        return checkpoint_ids

    def get_trigger_statistics(self) -> dict[str, Any]:
        """Get statistics about trigger performance

        Returns:
            Dictionary with trigger statistics
        """
        from collections import Counter

        # Count trigger types
        trigger_counts = Counter(t["trigger"] for t in self.trigger_history)

        # Recent activity (last hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_triggers = [t for t in self.trigger_history if t["timestamp"] >= one_hour_ago]

        # Calculate trigger frequency
        if len(self.trigger_history) >= 2:
            first_trigger = self.trigger_history[0]["timestamp"]
            last_trigger = self.trigger_history[-1]["timestamp"]
            duration = (last_trigger - first_trigger).total_seconds() / 3600  # hours
            frequency = len(self.trigger_history) / max(duration, 1)
        else:
            frequency = 0

        return {
            "total_triggers": len(self.trigger_history),
            "trigger_types": dict(trigger_counts),
            "recent_triggers_1h": len(recent_triggers),
            "triggers_per_hour": frequency,
            "current_work_area": self.work_area_monitor.current_work_area,
            "active_files_count": len(self.active_files),
            "context_usage": self.context_monitor.current_usage,
            "context_trend": self.context_monitor.get_usage_trend(),
            "last_trigger_time": self.last_trigger_time.isoformat() if self.last_trigger_time else None,
        }

    # Private methods

    def _can_trigger(self) -> bool:
        """Check if triggers are allowed (minimum interval check)"""
        if self.last_trigger_time is None:
            return True

        time_since_last = datetime.now() - self.last_trigger_time
        min_interval = timedelta(minutes=self.min_interval_minutes)

        return time_since_last >= min_interval

    def _extract_task_name(self, message: str) -> str | None:
        """Extract task name from message

        Args:
            message: Message content

        Returns:
            Extracted task name or None
        """
        # Look for patterns like "implemented X", "fixed Y", "created Z"
        patterns = [
            r"(?i)(?:implement|create|add|build|develop)\s+([^,.!?]+)",
            r"(?i)(?:fix|resolve|solve)\s+([^,.!?]+)",
            r"(?i)(?:complete|finish)\s+(?:the\s+)?([^,.!?]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                task_name = match.group(1).strip()
                # Clean up the task name
                task_name = re.sub(r"\b(the|a|an)\b", "", task_name, flags=re.IGNORECASE).strip()
                if task_name:
                    return task_name

        return None

    def _record_trigger(self, trigger_type: CheckpointTrigger, checkpoint_id: str):
        """Record a trigger event for statistics

        Args:
            trigger_type: Type of trigger that fired
            checkpoint_id: ID of created checkpoint
        """
        self.last_trigger_time = datetime.now()
        self.trigger_history.append(
            {
                "timestamp": self.last_trigger_time,
                "trigger": trigger_type.value,
                "checkpoint_id": checkpoint_id,
            }
        )

        # Keep only last 1000 trigger events
        self.trigger_history = self.trigger_history[-1000:]

        self.hook_logger.info(f"Recorded trigger: {trigger_type.value} -> {checkpoint_id}")


# Global trigger system instance
_trigger_system: CheckpointTriggerSystem | None = None


def get_trigger_system(checkpoint_manager: CheckpointManager) -> CheckpointTriggerSystem:
    """Get or create the global trigger system"""
    global _trigger_system
    if _trigger_system is None:
        _trigger_system = CheckpointTriggerSystem(checkpoint_manager)
    return _trigger_system
