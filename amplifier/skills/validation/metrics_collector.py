"""
Comprehensive Metrics Collection System

Collects, aggregates, and analyzes performance metrics for Phase 1 improvements.
Provides real-time insights into system performance and optimization effectiveness.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict
from collections import deque
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from ..resource_optimization.arena_allocator import ArenaAllocator
from ..resource_optimization.arena_allocator import get_arena_allocator
from ..scheduler.work_stealing_scheduler import WorkStealingScheduler
from ..scheduler.work_stealing_scheduler import get_scheduler

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric data point with timestamp"""

    timestamp: float
    value: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedMetric:
    """Aggregated metric with statistics"""

    name: str
    count: int = 0
    sum_value: float = 0.0
    min_value: float = float("inf")
    max_value: float = float("-inf")
    avg_value: float = 0.0
    latest_value: float = 0.0
    trend: float = 0.0  # Recent trend (positive = improving)
    unit: str = ""
    description: str = ""

    def update(self, value: float):
        """Update metric with new value"""
        self.count += 1
        self.sum_value += value
        self.min_value = min(self.min_value, value)
        self.max_value = max(self.max_value, value)
        self.avg_value = self.sum_value / self.count
        self.latest_value = value

    def calculate_trend(self, recent_values: list[float]):
        """Calculate trend from recent values"""
        if len(recent_values) >= 2:
            # Simple linear trend calculation
            recent_avg = sum(recent_values[-5:]) / len(recent_values[-5:])
            older_avg = (
                sum(recent_values[-10:-5]) / len(recent_values[-10:-5])
                if len(recent_values) >= 10
                else recent_values[0]
            )
            self.trend = recent_avg - older_avg


@dataclass
class SkillMetric:
    """Skill-specific performance metric"""

    skill_id: str
    execution_count: int = 0
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    success_rate: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    optimization_applied_count: int = 0
    optimization_score: float = 0.0
    last_execution: float = 0.0

    def update_execution(
        self,
        execution_time: float,
        success: bool,
        cache_hit: bool,
        optimization_applied: bool,
        optimization_score: float,
    ):
        """Update skill execution metrics"""
        self.execution_count += 1
        self.total_execution_time += execution_time
        self.avg_execution_time = self.total_execution_time / self.execution_count

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        self.success_rate = (self.success_count / self.execution_count) * 100

        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

        total_cache_attempts = self.cache_hits + self.cache_misses
        if total_cache_attempts > 0:
            self.cache_hit_rate = (self.cache_hits / total_cache_attempts) * 100

        if optimization_applied:
            self.optimization_applied_count += 1
            self.optimization_score = max(self.optimization_score, optimization_score)

        self.last_execution = time.time()


class MetricsCollector:
    """
    Comprehensive metrics collection system for Phase 1 performance monitoring.

    Collects metrics for:
    - Work-stealing scheduler performance
    - Arena allocator memory efficiency
    - Signature skill execution statistics
    - BootstrapFewShot optimization effectiveness
    - Zero-hallucination validation results
    - Overall system performance trends
    """

    def __init__(
        self, collection_interval: float = 1.0, history_size: int = 10000, enable_real_time_collection: bool = True
    ):
        self.collection_interval = collection_interval
        self.history_size = history_size
        self.enable_real_time_collection = enable_real_time_collection

        # Collection state
        self._collecting = False
        self._collection_task: asyncio.Task | None = None

        # Core components to monitor
        self._scheduler: WorkStealingScheduler | None = None
        self._arena: ArenaAllocator | None = None

        # Metrics storage
        self._metrics: dict[str, AggregatedMetric] = {}
        self._metric_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self._skill_metrics: dict[str, SkillMetric] = {}

        # Real-time metric callbacks
        self._metric_callbacks: dict[str, list[Callable[[MetricPoint], None]]] = defaultdict(list)

        # Phase 1 specific metrics
        self._initialize_phase1_metrics()

        # Thread pool for collection operations
        self._executor = ThreadPoolExecutor(max_workers=4)

        # Collection statistics
        self._collection_stats = {
            "total_collections": 0,
            "metrics_collected": 0,
            "start_time": time.time(),
            "last_collection_time": 0.0,
            "errors": 0,
        }

    def _initialize_phase1_metrics(self):
        """Initialize Phase 1 specific metrics"""
        phase1_metrics = {
            # Performance metrics
            "system_throughput": AggregatedMetric(
                name="System Throughput",
                unit="msg/s",
                description="Messages processed per second by work-stealing scheduler",
            ),
            "memory_efficiency": AggregatedMetric(
                name="Memory Efficiency",
                unit="%",
                description="Memory reduction through arena allocation and hash-consing",
            ),
            "skill_reliability": AggregatedMetric(
                name="Skill Reliability", unit="%", description="Success rate of signature-based skills"
            ),
            "optimization_effectiveness": AggregatedMetric(
                name="Optimization Effectiveness", unit="x", description="Performance multiplier from optimizations"
            ),
            # Quality metrics
            "cache_hit_rate": AggregatedMetric(
                name="Cache Hit Rate", unit="%", description="BootstrapFewShot and other cache hit rates"
            ),
            "zero_hallucination_rate": AggregatedMetric(
                name="Zero Hallucination Rate", unit="%", description="Rate of outputs with zero hallucination"
            ),
            "type_safety_score": AggregatedMetric(
                name="Type Safety Score", unit="%", description="Type contract compliance score"
            ),
            # Resource metrics
            "cpu_utilization": AggregatedMetric(
                name="CPU Utilization", unit="%", description="Current CPU usage percentage"
            ),
            "memory_utilization": AggregatedMetric(
                name="Memory Utilization", unit="%", description="Current memory usage percentage"
            ),
            "worker_utilization": AggregatedMetric(
                name="Worker Utilization", unit="%", description="Work-stealing scheduler worker utilization"
            ),
            # System metrics
            "error_rate": AggregatedMetric(name="Error Rate", unit="%", description="System error rate"),
            "response_time": AggregatedMetric(
                name="Response Time", unit="ms", description="Average skill response time"
            ),
            "queue_depth": AggregatedMetric(name="Queue Depth", unit="tasks", description="Current task queue depth"),
        }

        self._metrics.update(phase1_metrics)

    async def start_collection(self):
        """Start metrics collection"""
        if self._collecting:
            return

        logger.info("Starting metrics collection")

        # Initialize monitored components
        await self._initialize_components()

        self._collecting = True
        if self.enable_real_time_collection:
            self._collection_task = asyncio.create_task(self._collection_loop())

        logger.info("Metrics collection started")

    async def stop_collection(self):
        """Stop metrics collection"""
        if not self._collecting:
            return

        logger.info("Stopping metrics collection")

        self._collecting = False

        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass

        self._executor.shutdown(wait=True)

        logger.info("Metrics collection stopped")

    async def _initialize_components(self):
        """Initialize components to monitor"""
        try:
            # Get work-stealing scheduler
            self._scheduler = get_scheduler()
            if not self._scheduler._running:
                await self._scheduler.start()

            # Get arena allocator
            self._arena = get_arena_allocator()

        except Exception as e:
            logger.error(f"Failed to initialize monitored components: {e}")

    async def _collection_loop(self):
        """Main collection loop"""
        while self._collecting:
            try:
                collection_start = time.time()

                # Collect all metrics
                await self._collect_all_metrics()

                # Update collection statistics
                self._collection_stats["total_collections"] += 1
                self._collection_stats["last_collection_time"] = time.time()

                # Calculate collection time
                collection_time = time.time() - collection_start
                if collection_time > self.collection_interval:
                    logger.warning(
                        f"Metrics collection took {collection_time:.3f}s, longer than interval {self.collection_interval}s"
                    )

            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                self._collection_stats["errors"] += 1

            # Wait for next collection
            await asyncio.sleep(self.collection_interval)

    async def _collect_all_metrics(self):
        """Collect all metrics from monitored components"""
        current_time = time.time()

        # Collect scheduler metrics
        if self._scheduler:
            await self._collect_scheduler_metrics(current_time)

        # Collect arena allocator metrics
        if self._arena:
            await self._collect_arena_metrics(current_time)

        # Collect system metrics
        await self._collect_system_metrics(current_time)

        # Calculate derived metrics
        await self._calculate_derived_metrics(current_time)

    async def _collect_scheduler_metrics(self, timestamp: float):
        """Collect work-stealing scheduler metrics"""
        try:
            scheduler_stats = self._scheduler.get_stats()

            # System throughput
            await self._record_metric(
                "system_throughput", scheduler_stats.throughput_tasks_per_sec, timestamp, {"component": "scheduler"}
            )

            # Worker utilization
            await self._record_metric(
                "worker_utilization", scheduler_stats.worker_utilization * 100, timestamp, {"component": "scheduler"}
            )

            # Queue depth
            await self._record_metric("queue_depth", scheduler_stats.queue_depth, timestamp, {"component": "scheduler"})

            # Error rate
            total_tasks = scheduler_stats.total_tasks
            failed_tasks = scheduler_stats.failed_tasks
            error_rate = (failed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            await self._record_metric("error_rate", error_rate, timestamp, {"component": "scheduler"})

        except Exception as e:
            logger.error(f"Error collecting scheduler metrics: {e}")

    async def _collect_arena_metrics(self, timestamp: float):
        """Collect arena allocator metrics"""
        try:
            arena_stats = self._arena.get_stats()

            # Memory efficiency (hash-consing savings)
            hash_consing_efficiency = self._arena.get_hash_consing_efficiency()
            memory_efficiency = hash_consing_efficiency * 100

            await self._record_metric(
                "memory_efficiency", memory_efficiency, timestamp, {"component": "arena_allocator"}
            )

            # Memory utilization
            memory_usage = self._arena.get_memory_usage() * 100

            await self._record_metric("memory_utilization", memory_usage, timestamp, {"component": "arena_allocator"})

        except Exception as e:
            logger.error(f"Error collecting arena metrics: {e}")

    async def _collect_system_metrics(self, timestamp: float):
        """Collect system-level metrics"""
        try:
            # CPU utilization
            cpu_usage = self._get_cpu_usage()
            await self._record_metric("cpu_utilization", cpu_usage, timestamp, {"component": "system"})

            # Memory utilization (if not already collected from arena)
            if "memory_utilization" not in self._metric_history or len(self._metric_history["memory_utilization"]) == 0:
                memory_usage = self._get_memory_usage()
                await self._record_metric("memory_utilization", memory_usage, timestamp, {"component": "system"})

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    async def _calculate_derived_metrics(self, timestamp: float):
        """Calculate derived metrics from collected data"""
        try:
            # Calculate overall optimization effectiveness
            memory_efficiency = self._metrics["memory_efficiency"].latest_value
            throughput = self._metrics["system_throughput"].latest_value
            cache_hit_rate = self._metrics["cache_hit_rate"].latest_value

            # Baseline values for comparison
            baseline_throughput = 5000.0  # 5K msg/s baseline
            baseline_memory_efficiency = 20.0  # 20% baseline

            throughput_improvement = throughput / baseline_throughput if baseline_throughput > 0 else 1.0
            memory_improvement = (
                memory_efficiency / baseline_memory_efficiency if baseline_memory_efficiency > 0 else 1.0
            )
            cache_improvement = 1.0 + (cache_hit_rate / 100.0)

            # Overall optimization effectiveness
            optimization_effectiveness = throughput_improvement * memory_improvement * cache_improvement

            await self._record_metric(
                "optimization_effectiveness",
                optimization_effectiveness,
                timestamp,
                {"component": "derived", "calculation": "compound"},
            )

        except Exception as e:
            logger.error(f"Error calculating derived metrics: {e}")

    async def _record_metric(self, metric_name: str, value: float, timestamp: float, metadata: dict[str, Any] = None):
        """Record a metric value"""
        try:
            # Create metric point
            metric_point = MetricPoint(timestamp=timestamp, value=value, metadata=metadata or {})

            # Update aggregated metric
            if metric_name not in self._metrics:
                self._metrics[metric_name] = AggregatedMetric(name=metric_name)

            self._metrics[metric_name].update(value)

            # Add to history
            self._metric_history[metric_name].append(metric_point)

            # Calculate trend
            recent_values = [p.value for p in list(self._metric_history[metric_name])[-10:]]
            if len(recent_values) >= 2:
                self._metrics[metric_name].calculate_trend(recent_values)

            # Trigger callbacks
            for callback in self._metric_callbacks.get(metric_name, []):
                try:
                    callback(metric_point)
                except Exception as e:
                    logger.error(f"Metric callback error for {metric_name}: {e}")

            # Update collection stats
            self._collection_stats["metrics_collected"] += 1

        except Exception as e:
            logger.error(f"Error recording metric {metric_name}: {e}")

    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            import psutil

            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0

    def _get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        try:
            import psutil

            return psutil.virtual_memory().percent
        except ImportError:
            return 0.0

    async def record_skill_execution(
        self,
        skill_id: str,
        execution_time: float,
        success: bool,
        cache_hit: bool = False,
        optimization_applied: bool = False,
        optimization_score: float = 1.0,
    ):
        """Record skill execution metrics"""
        if skill_id not in self._skill_metrics:
            self._skill_metrics[skill_id] = SkillMetric(skill_id=skill_id)

        self._skill_metrics[skill_id].update_execution(
            execution_time, success, cache_hit, optimization_applied, optimization_score
        )

        # Update global metrics
        await self._record_metric(
            "response_time",
            execution_time * 1000,  # Convert to ms
            time.time(),
            {"component": "skill", "skill_id": skill_id},
        )

    async def record_quality_metric(
        self, skill_id: str, quality_score: float, issues_count: int, zero_hallucination: bool
    ):
        """Record quality assurance metrics"""
        if skill_id not in self._skill_metrics:
            self._skill_metrics[skill_id] = SkillMetric(skill_id=skill_id)

        # Update skill quality metrics (would be expanded in real implementation)
        pass

        # Update global quality metrics
        await self._record_metric(
            "zero_hallucination_rate",
            100.0 if zero_hallucination else 0.0,
            time.time(),
            {"component": "quality", "skill_id": skill_id},
        )

    def add_metric_callback(self, metric_name: str, callback: Callable[[MetricPoint], None]):
        """Add callback for metric updates"""
        self._metric_callbacks[metric_name].append(callback)

    def remove_metric_callback(self, metric_name: str, callback: Callable[[MetricPoint], None]):
        """Remove metric callback"""
        if callback in self._metric_callbacks[metric_name]:
            self._metric_callbacks[metric_name].remove(callback)

    def get_metric(self, metric_name: str) -> AggregatedMetric | None:
        """Get aggregated metric by name"""
        return self._metrics.get(metric_name)

    def get_metric_history(self, metric_name: str, limit: int | None = None) -> list[MetricPoint]:
        """Get metric history"""
        history = list(self._metric_history[metric_name])
        if limit:
            history = history[-limit:]
        return history

    def get_skill_metrics(self, skill_id: str) -> SkillMetric | None:
        """Get metrics for a specific skill"""
        return self._skill_metrics.get(skill_id)

    def get_all_skill_metrics(self) -> dict[str, SkillMetric]:
        """Get metrics for all skills"""
        return self._skill_metrics.copy()

    def get_aggregated_metrics(self) -> dict[str, Any]:
        """Get all aggregated metrics as dictionary"""
        return {
            name: {
                "count": metric.count,
                "sum": metric.sum_value,
                "min": metric.min_value if metric.min_value != float("inf") else 0,
                "max": metric.max_value if metric.max_value != float("-inf") else 0,
                "avg": metric.avg_value,
                "latest": metric.latest_value,
                "trend": metric.trend,
                "unit": metric.unit,
                "description": metric.description,
            }
            for name, metric in self._metrics.items()
        }

    def get_phase1_performance_summary(self) -> dict[str, Any]:
        """Get Phase 1 performance summary"""
        # Calculate key performance indicators
        throughput = self._metrics["system_throughput"].latest_value
        memory_efficiency = self._metrics["memory_efficiency"].latest_value
        skill_reliability = self._metrics["skill_reliability"].latest_value
        optimization_effectiveness = self._metrics["optimization_effectiveness"].latest_value
        cache_hit_rate = self._metrics["cache_hit_rate"].latest_value
        zero_hallucination_rate = self._metrics["zero_hallucination_rate"].latest_value

        # Calculate overall improvement factor
        baseline_throughput = 5000.0
        throughput_improvement = throughput / baseline_throughput if baseline_throughput > 0 else 1.0

        # Phase 1 achievement status
        achievements = {
            "throughput_target_achieved": throughput >= 100000,  # 100K+ msg/s
            "memory_reduction_target_achieved": memory_efficiency >= 85.0,  # 85% reduction
            "reliability_target_achieved": skill_reliability >= 90.0,  # 90%+ reliability
            "zero_hallucination_target_achieved": zero_hallucination_rate >= 95.0,  # 95%+ zero hallucination
            "cache_optimization_achieved": cache_hit_rate >= 80.0,  # 80%+ cache hit rate
            "overall_improvement_achieved": optimization_effectiveness >= 20.0,  # 20x+ improvement
        }

        achievements_count = sum(achievements.values())
        total_achievements = len(achievements)
        achievement_percentage = (achievements_count / total_achievements) * 100

        return {
            "timestamp": time.time(),
            "key_metrics": {
                "throughput_msg_per_sec": throughput,
                "memory_efficiency_percent": memory_efficiency,
                "skill_reliability_percent": skill_reliability,
                "optimization_effectiveness_x": optimization_effectiveness,
                "cache_hit_rate_percent": cache_hit_rate,
                "zero_hallucination_rate_percent": zero_hallucination_rate,
                "throughput_improvement_x": throughput_improvement,
            },
            "phase1_achievements": achievements,
            "overall_achievement_percentage": achievement_percentage,
            "phase1_ready": achievement_percentage >= 90.0,
            "collection_stats": self._collection_stats.copy(),
            "monitored_skills_count": len(self._skill_metrics),
        }

    def export_metrics(self, format: str = "json") -> str:
        """Export all metrics in specified format"""
        data = {
            "export_timestamp": time.time(),
            "aggregated_metrics": self.get_aggregated_metrics(),
            "skill_metrics": {skill_id: asdict(skill_metric) for skill_id, skill_metric in self._skill_metrics.items()},
            "collection_stats": self._collection_stats,
        }

        if format.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        raise ValueError(f"Unsupported export format: {format}")

    def reset_metrics(self):
        """Reset all collected metrics"""
        self._metrics.clear()
        self._metric_history.clear()
        self._skill_metrics.clear()
        self._initialize_phase1_metrics()
        self._collection_stats = {
            "total_collections": 0,
            "metrics_collected": 0,
            "start_time": time.time(),
            "last_collection_time": 0.0,
            "errors": 0,
        }


# Global metrics collector instance
_global_metrics_collector: MetricsCollector | None = None


def get_metrics_collector(**kwargs) -> MetricsCollector:
    """Get or create the global metrics collector"""
    global _global_metrics_collector
    if _global_metrics_collector is None:
        _global_metrics_collector = MetricsCollector(**kwargs)
    return _global_metrics_collector


async def collect_phase1_metrics() -> dict[str, Any]:
    """Convenience function to collect Phase 1 metrics"""
    collector = get_metrics_collector()
    return collector.get_phase1_performance_summary()
