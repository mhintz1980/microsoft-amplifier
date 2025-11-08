"""
Token Budget Manager

Intelligent token monitoring and automatic compression system for Claude Code.
Provides real-time budget management with progressive context optimization.
"""

import json
import logging
import time
from collections.abc import Callable
from dataclasses import asdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from .token_utils import count_tokens

logger = logging.getLogger(__name__)


class BudgetStatus(Enum):
    """Token budget status levels."""

    OPTIMAL = "optimal"  # < 70% usage
    WARNING = "warning"  # 70-85% usage
    CRITICAL = "critical"  # 85-95% usage
    EMERGENCY = "emergency"  # > 95% usage


class CompressionTrigger(Enum):
    """Automatic compression triggers."""

    THRESHOLD_WARNING = "threshold_warning"
    THRESHOLD_CRITICAL = "threshold_critical"
    THRESHOLD_EMERGENCY = "threshold_emergency"
    OPERATION_TOO_LARGE = "operation_too_large"
    CONTEXT_SPIKE = "context_spike"


@dataclass
class BudgetMetrics:
    """Current budget metrics."""

    total_tokens: int
    used_tokens: int
    available_tokens: int
    usage_percentage: float
    status: BudgetStatus
    last_operation_tokens: int
    operation_count: int
    session_duration: float


@dataclass
class OperationMetrics:
    """Metrics for a single operation."""

    operation_type: str
    tokens_before: int
    tokens_after: int
    tokens_added: int
    execution_time: float
    timestamp: float
    efficiency_score: float  # 0-100 based on philosophy compliance


@dataclass
class CompressionEvent:
    """Record of a compression event."""

    trigger: CompressionTrigger
    tokens_before: int
    tokens_after: int
    tokens_saved: int
    compression_strategy: str
    timestamp: float
    effectiveness: float  # 0-100


class TokenBudgetManager:
    """
    Intelligent token budget management system.

    Provides real-time monitoring, automatic compression triggers,
    and intelligent context allocation based on importance scoring.
    """

    def __init__(
        self,
        max_tokens: int = 200000,
        warning_threshold: float = 0.7,
        critical_threshold: float = 0.85,
        emergency_threshold: float = 0.95,
        max_operation_tokens: int = 1000,
        context_spike_threshold: float = 0.1,
        persistence_file: Path | None = None,
    ):
        """Initialize token budget manager."""
        self.max_tokens = max_tokens
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.emergency_threshold = emergency_threshold
        self.max_operation_tokens = max_operation_tokens
        self.context_spike_threshold = context_spike_threshold

        # State tracking
        self.current_tokens = 0
        self.operation_count = 0
        self.session_start = time.time()
        self.last_operation_tokens = 0
        self.operations: list[OperationMetrics] = []
        self.compression_events: list[CompressionEvent] = []

        # Compression handlers
        self.compression_handlers: dict[CompressionTrigger, Callable] = {}

        # Status integration
        self.status_callbacks: list[Callable[[BudgetMetrics], None]] = []

        # Persistence
        self.persistence_file = persistence_file or Path.home() / ".amplifier" / "token_budget.json"
        self._load_state()

        logger.info(f"TokenBudgetManager initialized: max_tokens={max_tokens}")

    def get_current_metrics(self) -> BudgetMetrics:
        """Get current budget metrics."""
        usage_percentage = self.current_tokens / self.max_tokens
        status = self._calculate_status(usage_percentage)

        session_duration = time.time() - self.session_start

        return BudgetMetrics(
            total_tokens=self.max_tokens,
            used_tokens=self.current_tokens,
            available_tokens=self.max_tokens - self.current_tokens,
            usage_percentage=usage_percentage,
            status=status,
            last_operation_tokens=self.last_operation_tokens,
            operation_count=self.operation_count,
            session_duration=session_duration,
        )

    def record_operation(
        self, operation_type: str, content_added: str, execution_time: float, efficiency_score: float | None = None
    ) -> OperationMetrics:
        """Record a new operation and check triggers."""
        tokens_before = self.current_tokens
        tokens_added = count_tokens(content_added)
        self.current_tokens += tokens_added
        self.operation_count += 1
        self.last_operation_tokens = tokens_added

        # Calculate efficiency score if not provided
        if efficiency_score is None:
            efficiency_score = self._calculate_efficiency_score(tokens_added, execution_time)

        # Create operation record
        operation = OperationMetrics(
            operation_type=operation_type,
            tokens_before=tokens_before,
            tokens_after=self.current_tokens,
            tokens_added=tokens_added,
            execution_time=execution_time,
            timestamp=time.time(),
            efficiency_score=efficiency_score,
        )

        self.operations.append(operation)
        self._check_triggers(operation)
        self._notify_status_change()
        self._save_state()

        return operation

    def register_compression_handler(self, trigger: CompressionTrigger, handler: Callable[[], int]) -> None:
        """Register a compression handler for a trigger."""
        self.compression_handlers[trigger] = handler
        logger.debug(f"Registered compression handler for {trigger.value}")

    def register_status_callback(self, callback: Callable[[BudgetMetrics], None]) -> None:
        """Register a callback for status changes."""
        self.status_callbacks.append(callback)

    def request_compression(self, strategy: str = "auto") -> int:
        """Request manual compression."""
        tokens_before = self.current_tokens

        if strategy == "auto":
            saved = self._auto_compress()
        else:
            saved = self._compress_with_strategy(strategy)

        # Record compression event
        if saved > 0:
            event = CompressionEvent(
                trigger=CompressionTrigger.THRESHOLD_WARNING,  # Manual compression
                tokens_before=tokens_before,
                tokens_after=self.current_tokens,
                tokens_saved=saved,
                compression_strategy=strategy,
                timestamp=time.time(),
                effectiveness=min(100, (saved / tokens_before) * 100) if tokens_before > 0 else 0,
            )
            self.compression_events.append(event)
            self._save_state()

        return saved

    def allocate_context_budget(
        self, contexts: list[dict[str, Any]], max_budget: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Allocate context budget based on importance scoring.

        Args:
            contexts: List of context items with 'content' and 'importance' keys
            max_budget: Maximum tokens to allocate (defaults to available tokens)

        Returns:
            Filtered and sorted contexts within budget
        """
        if max_budget is None:
            max_budget = self.max_tokens - self.current_tokens

        # Sort by importance score (descending)
        sorted_contexts = sorted(contexts, key=lambda x: x.get("importance", 0.5), reverse=True)

        allocated = []
        used_tokens = 0

        for context in sorted_contexts:
            content_tokens = count_tokens(context.get("content", ""))

            if used_tokens + content_tokens <= max_budget:
                allocated.append(context)
                used_tokens += content_tokens
            else:
                # Try to truncate content if important enough
                importance = context.get("importance", 0.5)
                if importance > 0.7:  # High importance - try to fit
                    remaining_tokens = max_budget - used_tokens
                    if remaining_tokens > 50:  # Minimum useful content
                        # Truncate to fit
                        truncated_content, _, _ = truncate_to_tokens(context["content"], remaining_tokens)
                        truncated_context = context.copy()
                        truncated_context["content"] = truncated_content
                        truncated_context["truncated"] = True
                        allocated.append(truncated_context)
                        used_tokens += remaining_tokens
                break

        return allocated

    def get_status_display(self) -> str:
        """Get formatted status display for CLI."""
        metrics = self.get_current_metrics()

        # Progress bar
        filled_bars = int(metrics.usage_percentage * 20)
        empty_bars = 20 - filled_bars
        progress_bar = "█" * filled_bars + "░" * empty_bars

        # Status color indicators
        status_symbols = {
            BudgetStatus.OPTIMAL: "🟢",
            BudgetStatus.WARNING: "🟡",
            BudgetStatus.CRITICAL: "🟠",
            BudgetStatus.EMERGENCY: "🔴",
        }

        status_symbol = status_symbols[metrics.status]

        # Calculate ops per minute
        ops_per_minute = (
            (metrics.operation_count / metrics.session_duration) * 60 if metrics.session_duration > 0 else 0
        )

        # Get recent efficiency
        recent_efficiency = self._get_recent_efficiency()

        display = f"""
{status_symbol} TOKEN BUDGET STATUS:
   Usage: {progress_bar} {metrics.usage_percentage:.1%}
   Tokens: {metrics.used_tokens:,} / {metrics.total_tokens:,}
   Last operation: +{metrics.last_operation_tokens} tokens
   Status: {metrics.status.value.upper()}

⚡ PERFORMANCE METRICS:
   Operations: {metrics.operation_count} ({ops_per_minute:.1f}/min)
   Runtime: {metrics.session_duration:.0f}s
   Efficiency: {recent_efficiency:.0f}/100
"""

        # Add recommendations
        recommendations = self._get_recommendations(metrics)
        if recommendations:
            display += "💡 RECOMMENDATIONS:\n"
            for rec in recommendations:
                display += f"   {rec}\n"

        return display.strip()

    def _calculate_status(self, usage_percentage: float) -> BudgetStatus:
        """Calculate budget status from usage percentage."""
        if usage_percentage >= self.emergency_threshold:
            return BudgetStatus.EMERGENCY
        if usage_percentage >= self.critical_threshold:
            return BudgetStatus.CRITICAL
        if usage_percentage >= self.warning_threshold:
            return BudgetStatus.WARNING
        return BudgetStatus.OPTIMAL

    def _calculate_efficiency_score(self, tokens_added: int, execution_time: float) -> float:
        """Calculate efficiency score for an operation."""
        score = 100.0

        # Penalize large operations
        if tokens_added > self.max_operation_tokens:
            score -= ((tokens_added - self.max_operation_tokens) / self.max_operation_tokens) * 50

        # Penalize slow operations
        if execution_time > 30:  # 30 second threshold
            score -= ((execution_time - 30) / 30) * 20

        # Bonus for efficient operations
        if tokens_added < 100 and execution_time < 5:
            score = min(100, score + 10)

        return max(0, score)

    def _check_triggers(self, operation: OperationMetrics) -> None:
        """Check if any compression triggers should fire."""
        usage_percentage = self.current_tokens / self.max_tokens

        # Threshold triggers
        if usage_percentage >= self.emergency_threshold:
            self._fire_trigger(CompressionTrigger.THRESHOLD_EMERGENCY)
        elif usage_percentage >= self.critical_threshold:
            self._fire_trigger(CompressionTrigger.THRESHOLD_CRITICAL)
        elif usage_percentage >= self.warning_threshold:
            self._fire_trigger(CompressionTrigger.THRESHOLD_WARNING)

        # Operation size trigger
        if operation.tokens_added > self.max_operation_tokens:
            self._fire_trigger(CompressionTrigger.OPERATION_TOO_LARGE)

        # Context spike trigger
        if len(self.operations) > 1:
            prev_operation = self.operations[-2]
            spike_percentage = operation.tokens_added / max(1, prev_operation.tokens_added)
            if spike_percentage > 2.0 and operation.tokens_added > 500:  # 2x increase and significant size
                self._fire_trigger(CompressionTrigger.CONTEXT_SPIKE)

    def _fire_trigger(self, trigger: CompressionTrigger) -> None:
        """Fire a compression trigger."""
        logger.warning(f"Compression trigger fired: {trigger.value}")

        if trigger in self.compression_handlers:
            try:
                saved = self.compression_handlers[trigger]()
                if saved > 0:
                    logger.info(f"Compression saved {saved} tokens")
                else:
                    logger.warning("Compression handler saved no tokens")
            except Exception as e:
                logger.error(f"Compression handler failed: {e}")
        else:
            logger.warning(f"No compression handler registered for {trigger.value}")

    def _auto_compress(self) -> int:
        """Automatic compression using available strategies."""
        saved = 0

        # Try different strategies in order of preference
        strategies = [
            ("remove_old_operations", self._compress_old_operations),
            ("compress_duplicates", self._compress_duplicates),
            ("truncate_low_importance", self._compress_low_importance),
        ]

        for name, strategy in strategies:
            strategy_saved = strategy()
            saved += strategy_saved
            logger.debug(f"Strategy {name} saved {strategy_saved} tokens")

            # Stop if we've saved enough to get below warning threshold
            if self.current_tokens <= (self.max_tokens * self.warning_threshold):
                break

        return saved

    def _compress_old_operations(self) -> int:
        """Compress by removing old operation history."""
        if len(self.operations) <= 10:
            return 0

        # Keep only last 10 operations
        old_count = len(self.operations)
        self.operations = self.operations[-10:]

        # Estimate saved tokens (rough calculation)
        saved = (old_count - 10) * 100  # Estimate ~100 tokens per operation record
        return saved

    def _compress_duplicates(self) -> int:
        """Compress by removing duplicate operations."""
        if len(self.operations) < 2:
            return 0

        # Simple duplicate detection based on operation type and token count
        seen = set()
        filtered_operations = []

        for op in self.operations:
            key = (op.operation_type, op.tokens_added // 100)  # Bucket by 100s
            if key not in seen:
                seen.add(key)
                filtered_operations.append(op)

        saved = (len(self.operations) - len(filtered_operations)) * 100
        self.operations = filtered_operations
        return saved

    def _compress_low_importance(self) -> int:
        """Placeholder for low-importance context compression."""
        # This would integrate with Skills framework to identify low-importance context
        return 0

    def _compress_with_strategy(self, strategy: str) -> int:
        """Compress using a specific strategy."""
        strategy_map = {
            "old_operations": self._compress_old_operations,
            "duplicates": self._compress_duplicates,
            "low_importance": self._compress_low_importance,
        }

        if strategy in strategy_map:
            return strategy_map[strategy]()
        logger.warning(f"Unknown compression strategy: {strategy}")
        return 0

    def _get_recommendations(self, metrics: BudgetMetrics) -> list[str]:
        """Get recommendations based on current status."""
        recommendations = []

        if metrics.status == BudgetStatus.EMERGENCY:
            recommendations.append("🚨 EMERGENCY: Immediate compression required")
        elif metrics.status == BudgetStatus.CRITICAL:
            recommendations.append("⚠️ CRITICAL: Consider manual compression")
        elif metrics.status == BudgetStatus.WARNING:
            recommendations.append("📊 WARNING: Monitor usage, consider compression soon")

        if metrics.last_operation_tokens > self.max_operation_tokens:
            recommendations.append("📏 Last operation exceeded efficiency guidelines")

        # Check efficiency trend
        recent_efficiency = self._get_recent_efficiency()
        if recent_efficiency < 70:
            recommendations.append("⚡ Efficiency declining - review approach")

        # Session length recommendation
        if metrics.session_duration > 1800:  # 30 minutes
            recommendations.append("⏰ Long session - consider break and review")

        return recommendations

    def _get_recent_efficiency(self) -> float:
        """Get average efficiency score of recent operations."""
        if not self.operations:
            return 100.0

        recent_ops = self.operations[-10:]  # Last 10 operations
        if not recent_ops:
            return 100.0

        return sum(op.efficiency_score for op in recent_ops) / len(recent_ops)

    def _notify_status_change(self) -> None:
        """Notify all registered callbacks of status change."""
        metrics = self.get_current_metrics()

        for callback in self.status_callbacks:
            try:
                callback(metrics)
            except Exception as e:
                logger.error(f"Status callback failed: {e}")

    def _save_state(self) -> None:
        """Save current state to persistence file."""
        try:
            self.persistence_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert compression events to JSON-serializable format
            compression_events_serializable = []
            for event in self.compression_events[-10:]:
                compression_events_serializable.append(
                    {
                        "trigger": event.trigger.value,
                        "tokens_before": event.tokens_before,
                        "tokens_after": event.tokens_after,
                        "tokens_saved": event.tokens_saved,
                        "compression_strategy": event.compression_strategy,
                        "timestamp": event.timestamp,
                        "effectiveness": event.effectiveness,
                    }
                )

            state = {
                "current_tokens": self.current_tokens,
                "operation_count": self.operation_count,
                "session_start": self.session_start,
                "operations": [asdict(op) for op in self.operations[-20:]],  # Keep last 20
                "compression_events": compression_events_serializable,
                "last_saved": time.time(),
            }

            with open(self.persistence_file, "w") as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def _load_state(self) -> None:
        """Load state from persistence file."""
        if not self.persistence_file.exists():
            return

        try:
            with open(self.persistence_file) as f:
                state = json.load(f)

            self.current_tokens = state.get("current_tokens", 0)
            self.operation_count = state.get("operation_count", 0)
            self.session_start = state.get("session_start", time.time())

            # Load operations
            ops_data = state.get("operations", [])
            self.operations = []
            for op_data in ops_data:
                try:
                    self.operations.append(OperationMetrics(**op_data))
                except Exception:
                    # Skip corrupted operation records
                    continue

            # Load compression events
            events_data = state.get("compression_events", [])
            self.compression_events = []
            for event_data in events_data:
                try:
                    # Handle both old and new formats
                    if isinstance(event_data.get("trigger"), str):
                        # New format - trigger is string value
                        trigger_value = event_data["trigger"]
                        trigger = (
                            CompressionTrigger(trigger_value)
                            if trigger_value in [t.value for t in CompressionTrigger]
                            else CompressionTrigger.THRESHOLD_WARNING
                        )
                    else:
                        # Old format - trigger might be enum or other format
                        trigger = CompressionTrigger.THRESHOLD_WARNING

                    event = CompressionEvent(
                        trigger=trigger,
                        tokens_before=event_data["tokens_before"],
                        tokens_after=event_data["tokens_after"],
                        tokens_saved=event_data["tokens_saved"],
                        compression_strategy=event_data["compression_strategy"],
                        timestamp=event_data["timestamp"],
                        effectiveness=event_data["effectiveness"],
                    )
                    self.compression_events.append(event)
                except Exception:
                    # Skip corrupted event records
                    continue

            logger.debug(f"Loaded state: {self.operation_count} operations, {self.current_tokens} tokens")

        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            # Start fresh if loading fails
            self.current_tokens = 0
            self.operation_count = 0
            self.session_start = time.time()


# Global instance for easy access
_budget_manager: TokenBudgetManager | None = None


def get_budget_manager() -> TokenBudgetManager:
    """Get the global token budget manager."""
    global _budget_manager
    if _budget_manager is None:
        _budget_manager = TokenBudgetManager()
    return _budget_manager


def record_operation(
    operation_type: str, content_added: str, execution_time: float, efficiency_score: float | None = None
) -> OperationMetrics:
    """Record an operation with the global budget manager."""
    return get_budget_manager().record_operation(operation_type, content_added, execution_time, efficiency_score)


def get_status_display() -> str:
    """Get status display from the global budget manager."""
    return get_budget_manager().get_status_display()


def request_compression(strategy: str = "auto") -> int:
    """Request compression with the global budget manager."""
    return get_budget_manager().request_compression(strategy)


# Import truncate_to_tokens for use in allocation
def truncate_to_tokens(text: str, max_tokens: int, model: str = "cl100k_base") -> tuple[str, int, int]:
    """Truncate text to fit within token limit."""
    from .token_utils import truncate_to_tokens as _truncate_to_tokens

    return _truncate_to_tokens(text, max_tokens, model)
