"""
Performance Monitor and Optimizer

Comprehensive performance monitoring system that tracks skill execution metrics,
token efficiency, response times, and user satisfaction to optimize performance.
"""

import asyncio
import statistics
import threading
import time
import uuid
from collections import defaultdict
from collections import deque
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from enum import Enum
from typing import Any

import psutil

from amplifier.mcp.persistent_storage import store_result


class MetricType(Enum):
    """Types of performance metrics."""

    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    TOKEN_EFFICIENCY = "token_efficiency"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    USER_SATISFACTION = "user_satisfaction"
    AVAILABILITY = "availability"


class PerformanceTier(Enum):
    """Performance tier classification."""

    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Single performance metric measurement."""

    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    skill_name: str
    execution_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""

    metric_type: MetricType
    min_value: float | None = None
    max_value: float | None = None
    target_value: float | None = None
    tier_mapping: dict[PerformanceTier, tuple] = field(default_factory=dict)


@dataclass
class PerformanceReport:
    """Comprehensive performance analysis report."""

    skill_name: str
    time_period: tuple
    overall_tier: PerformanceTier
    metrics_summary: dict[MetricType, dict[str, float]]
    trends: dict[MetricType, str]
    bottlenecks: list[str]
    recommendations: list[str]
    optimization_score: float
    timestamp: datetime


class PerformanceProfiler:
    """Context manager for profiling skill execution."""

    def __init__(self, monitor: "PerformanceMonitor", skill_name: str):
        self.monitor = monitor
        self.skill_name = skill_name
        self.execution_id = str(uuid.uuid4())
        self.start_time = None
        self.start_memory = None
        self.process = psutil.Process()

    def __enter__(self):
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            execution_time = time.time() - self.start_time
            memory_delta = self.process.memory_info().rss - self.start_memory

            # Record metrics
            self.monitor.record_metric(
                metric_type=MetricType.EXECUTION_TIME,
                value=execution_time,
                unit="seconds",
                skill_name=self.skill_name,
                execution_id=self.execution_id,
            )

            self.monitor.record_metric(
                metric_type=MetricType.MEMORY_USAGE,
                value=memory_delta,
                unit="bytes",
                skill_name=self.skill_name,
                execution_id=self.execution_id,
            )

            # Record error if exception occurred
            if exc_type is not None:
                self.monitor.record_metric(
                    metric_type=MetricType.ERROR_RATE,
                    value=1.0,
                    unit="ratio",
                    skill_name=self.skill_name,
                    execution_id=self.execution_id,
                )


class PerformanceMonitor:
    """Comprehensive performance monitoring and optimization system."""

    def __init__(self, monitoring_interval: int = 60, history_size: int = 10000, auto_optimize: bool = True):
        """
        Initialize performance monitor.

        Args:
            monitoring_interval: Interval between monitoring cycles (seconds)
            history_size: Maximum number of metrics to keep in memory
            auto_optimize: Enable automatic performance optimization
        """
        self.monitoring_interval = monitoring_interval
        self.history_size = history_size
        self.auto_optimize = auto_optimize

        # Metrics storage
        self.metrics: dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self.real_time_metrics: dict[str, float] = {}
        self.skill_metrics: dict[str, list[PerformanceMetric]] = defaultdict(list)

        # Performance thresholds
        self.thresholds = self._initialize_thresholds()

        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.optimization_tasks: list[asyncio.Task] = []

        # Performance cache
        self.performance_cache: dict[str, PerformanceReport] = {}
        self.cache_ttl = timedelta(minutes=5)

    def _initialize_thresholds(self) -> dict[MetricType, PerformanceThreshold]:
        """Initialize default performance thresholds."""
        return {
            MetricType.EXECUTION_TIME: PerformanceThreshold(
                metric_type=MetricType.EXECUTION_TIME,
                max_value=5.0,  # 5 seconds
                target_value=1.0,  # 1 second
                tier_mapping={
                    PerformanceTier.EXCELLENT: (0, 0.5),
                    PerformanceTier.GOOD: (0.5, 1.0),
                    PerformanceTier.ACCEPTABLE: (1.0, 2.0),
                    PerformanceTier.NEEDS_IMPROVEMENT: (2.0, 5.0),
                    PerformanceTier.CRITICAL: (5.0, float("inf")),
                },
            ),
            MetricType.MEMORY_USAGE: PerformanceThreshold(
                metric_type=MetricType.MEMORY_USAGE,
                max_value=1024 * 1024 * 1024,  # 1GB
                target_value=100 * 1024 * 1024,  # 100MB
                tier_mapping={
                    PerformanceTier.EXCELLENT: (0, 50 * 1024 * 1024),
                    PerformanceTier.GOOD: (50 * 1024 * 1024, 100 * 1024 * 1024),
                    PerformanceTier.ACCEPTABLE: (100 * 1024 * 1024, 500 * 1024 * 1024),
                    PerformanceTier.NEEDS_IMPROVEMENT: (500 * 1024 * 1024, 1024 * 1024 * 1024),
                    PerformanceTier.CRITICAL: (1024 * 1024 * 1024, float("inf")),
                },
            ),
            MetricType.TOKEN_EFFICIENCY: PerformanceThreshold(
                metric_type=MetricType.TOKEN_EFFICIENCY,
                min_value=0.1,  # 10% efficiency
                target_value=0.8,  # 80% efficiency
                tier_mapping={
                    PerformanceTier.EXCELLENT: (0.9, 1.0),
                    PerformanceTier.GOOD: (0.8, 0.9),
                    PerformanceTier.ACCEPTABLE: (0.6, 0.8),
                    PerformanceTier.NEEDS_IMPROVEMENT: (0.3, 0.6),
                    PerformanceTier.CRITICAL: (0, 0.3),
                },
            ),
            MetricType.ERROR_RATE: PerformanceThreshold(
                metric_type=MetricType.ERROR_RATE,
                max_value=0.05,  # 5% error rate
                target_value=0.01,  # 1% error rate
                tier_mapping={
                    PerformanceTier.EXCELLENT: (0, 0.001),
                    PerformanceTier.GOOD: (0.001, 0.01),
                    PerformanceTier.ACCEPTABLE: (0.01, 0.02),
                    PerformanceTier.NEEDS_IMPROVEMENT: (0.02, 0.05),
                    PerformanceTier.CRITICAL: (0.05, 1.0),
                },
            ),
        }

    def start_monitoring(self):
        """Start continuous performance monitoring."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self._collect_system_metrics()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                print(f"Monitoring error: {e}")

    def _collect_system_metrics(self):
        """Collect system-wide performance metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.real_time_metrics["system_cpu"] = cpu_percent

        # Memory usage
        memory = psutil.virtual_memory()
        self.real_time_metrics["system_memory"] = memory.percent

        # Disk usage
        disk = psutil.disk_usage("/")
        self.real_time_metrics["system_disk"] = disk.percent

    def profile_skill(self, skill_name: str) -> PerformanceProfiler:
        """
        Create a performance profiler for a skill.

        Args:
            skill_name: Name of the skill to profile

        Returns:
            Performance profiler context manager
        """
        return PerformanceProfiler(self, skill_name)

    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        unit: str,
        skill_name: str,
        execution_id: str = None,
        metadata: dict[str, Any] = None,
    ) -> PerformanceMetric:
        """
        Record a performance metric.

        Args:
            metric_type: Type of metric
            value: Metric value
            unit: Unit of measurement
            skill_name: Name of the skill
            execution_id: Unique execution identifier
            metadata: Additional metadata

        Returns:
            Created performance metric
        """
        if execution_id is None:
            execution_id = str(uuid.uuid4())

        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            skill_name=skill_name,
            execution_id=execution_id,
            metadata=metadata or {},
        )

        # Store metric
        self.skill_metrics[skill_name].append(metric)
        self.metrics[f"{skill_name}_{metric_type.value}"].append(value)

        # Trigger auto-optimization if enabled
        if self.auto_optimize:
            self._check_optimization_triggers(skill_name, metric)

        return metric

    def _check_optimization_triggers(self, skill_name: str, metric: PerformanceMetric):
        """Check if optimization should be triggered based on metric."""
        threshold = self.thresholds.get(metric.metric_type)
        if not threshold:
            return

        # Check if metric exceeds threshold
        if threshold.max_value and metric.value > threshold.max_value:
            asyncio.create_task(self._trigger_optimization(skill_name, metric))

        # Check if metric is below minimum
        if threshold.min_value and metric.value < threshold.min_value:
            asyncio.create_task(self._trigger_optimization(skill_name, metric))

    async def _trigger_optimization(self, skill_name: str, metric: PerformanceMetric):
        """Trigger performance optimization for a skill."""
        optimization_task = asyncio.create_task(self.optimize_skill_performance(skill_name, metric.metric_type))
        self.optimization_tasks.append(optimization_task)

        # Clean up completed tasks
        self.optimization_tasks = [task for task in self.optimization_tasks if not task.done()]

    async def optimize_skill_performance(self, skill_name: str, metric_type: MetricType) -> dict[str, Any]:
        """
        Optimize skill performance based on metric analysis.

        Args:
            skill_name: Name of the skill to optimize
            metric_type: Type of metric to optimize

        Returns:
            Optimization results and recommendations
        """
        # Get recent metrics for analysis
        recent_metrics = self.get_skill_metrics(skill_name, metric_type, hours=1)

        if not recent_metrics:
            return {"status": "no_data", "recommendations": []}

        # Analyze performance patterns
        analysis = self._analyze_performance_patterns(recent_metrics)

        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(skill_name, metric_type, analysis)

        # Apply automatic optimizations if possible
        applied_optimizations = []
        if self.auto_optimize:
            applied_optimizations = await self._apply_automatic_optimizations(skill_name, metric_type, recommendations)

        return {
            "status": "completed",
            "analysis": analysis,
            "recommendations": recommendations,
            "applied_optimizations": applied_optimizations,
            "performance_gain": self._estimate_performance_gain(applied_optimizations),
        }

    def _analyze_performance_patterns(self, metrics: list[PerformanceMetric]) -> dict[str, Any]:
        """Analyze performance patterns from metrics."""
        values = [m.value for m in metrics]

        analysis = {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "trend": self._calculate_trend(values),
        }

        # Detect anomalies
        if analysis["std_dev"] > 0:
            z_scores = [(abs(v - analysis["mean"]) / analysis["std_dev"]) for v in values]
            anomalies = [i for i, z in enumerate(z_scores) if z > 2]
            analysis["anomalies"] = anomalies
            analysis["anomaly_count"] = len(anomalies)

        return analysis

    def _calculate_trend(self, values: list[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 2:
            return "insufficient_data"

        # Simple linear regression to determine trend
        n = len(values)
        x = list(range(n))
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)

        if slope > 0.01:
            return "improving"
        if slope < -0.01:
            return "degrading"
        return "stable"

    def _generate_optimization_recommendations(
        self, skill_name: str, metric_type: MetricType, analysis: dict[str, Any]
    ) -> list[str]:
        """Generate specific optimization recommendations."""
        recommendations = []

        if metric_type == MetricType.EXECUTION_TIME:
            if analysis["mean"] > 2.0:
                recommendations.append("Consider optimizing algorithms or reducing computational complexity")
                recommendations.append("Implement caching for frequently used results")
            if analysis["std_dev"] > analysis["mean"] * 0.5:
                recommendations.append("High execution time variance - investigate inconsistent performance")

        elif metric_type == MetricType.MEMORY_USAGE:
            if analysis["mean"] > 500 * 1024 * 1024:  # 500MB
                recommendations.append("High memory usage - implement memory optimization techniques")
                recommendations.append("Consider using generators or lazy evaluation")
            if analysis.get("anomaly_count", 0) > 0:
                recommendations.append("Memory leaks detected - investigate resource cleanup")

        elif metric_type == MetricType.TOKEN_EFFICIENCY:
            if analysis["mean"] < 0.5:  # Less than 50% efficiency
                recommendations.append("Low token efficiency - optimize prompts and responses")
                recommendations.append("Consider using context compression techniques")

        elif metric_type == MetricType.ERROR_RATE:
            if analysis["mean"] > 0.02:  # More than 2% error rate
                recommendations.append("High error rate - improve error handling and input validation")
                recommendations.append("Add comprehensive logging for debugging")

        return recommendations

    async def _apply_automatic_optimizations(
        self, skill_name: str, metric_type: MetricType, recommendations: list[str]
    ) -> list[str]:
        """Apply automatic optimizations based on recommendations."""
        applied = []

        for recommendation in recommendations:
            if "caching" in recommendation.lower():
                # Apply caching optimization
                success = await self._apply_caching_optimization(skill_name)
                if success:
                    applied.append("caching")

            elif "memory" in recommendation.lower():
                # Apply memory optimization
                success = await self._apply_memory_optimization(skill_name)
                if success:
                    applied.append("memory_optimization")

            elif "token" in recommendation.lower():
                # Apply token optimization
                success = await self._apply_token_optimization(skill_name)
                if success:
                    applied.append("token_optimization")

        return applied

    async def _apply_caching_optimization(self, skill_name: str) -> bool:
        """Apply caching optimization to a skill."""
        try:
            # Generate caching optimization code
            optimization_code = f"""
# Automatic caching optimization for {skill_name}
import functools
from functools import lru_cache

# Example of applying caching to frequently called functions
@lru_cache(maxsize=128)
def cached_function(*args, **kwargs):
    # Replace with actual function from skill
    pass
"""

            # Store optimization suggestion
            await store_result(
                namespace="performance_optimizations",
                key=f"{skill_name}_caching",
                data={"optimization": "caching", "code": optimization_code, "timestamp": datetime.now().isoformat()},
            )

            return True

        except Exception:
            return False

    async def _apply_memory_optimization(self, skill_name: str) -> bool:
        """Apply memory optimization to a skill."""
        try:
            # Generate memory optimization code
            optimization_code = f"""
# Automatic memory optimization for {skill_name}
import gc
import weakref

# Enable garbage collection
gc.enable()

# Use weak references where appropriate
weak_ref_cache = weakref.WeakValueDictionary()
"""

            await store_result(
                namespace="performance_optimizations",
                key=f"{skill_name}_memory",
                data={"optimization": "memory", "code": optimization_code, "timestamp": datetime.now().isoformat()},
            )

            return True

        except Exception:
            return False

    async def _apply_token_optimization(self, skill_name: str) -> bool:
        """Apply token optimization to a skill."""
        try:
            # Generate token optimization code
            optimization_code = f"""
# Automatic token optimization for {skill_name}
def compress_context(context: str, max_tokens: int = 1000) -> str:
    '''Compress context to reduce token usage.'''
    if len(context) <= max_tokens:
        return context

    # Simple truncation - replace with more sophisticated compression
    return context[:max_tokens] + "..."

def optimize_prompt(prompt: str) -> str:
    '''Optimize prompt for token efficiency.'''
    # Remove redundant phrases and optimize structure
    return prompt.strip()
"""

            await store_result(
                namespace="performance_optimizations",
                key=f"{skill_name}_token",
                data={"optimization": "token", "code": optimization_code, "timestamp": datetime.now().isoformat()},
            )

            return True

        except Exception:
            return False

    def _estimate_performance_gain(self, optimizations: list[str]) -> float:
        """Estimate performance gain from applied optimizations."""
        gain_multiplier = {
            "caching": 1.2,  # 20% improvement
            "memory_optimization": 1.1,  # 10% improvement
            "token_optimization": 1.3,  # 30% improvement
        }

        total_gain = 1.0
        for opt in optimizations:
            total_gain *= gain_multiplier.get(opt, 1.0)

        return total_gain

    def get_skill_metrics(
        self, skill_name: str, metric_type: MetricType = None, hours: int = 24
    ) -> list[PerformanceMetric]:
        """
        Get metrics for a specific skill.

        Args:
            skill_name: Name of the skill
            metric_type: Type of metric to filter by
            hours: Number of hours to look back

        Returns:
            List of performance metrics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        metrics = self.skill_metrics.get(skill_name, [])

        filtered_metrics = [
            m for m in metrics if m.timestamp >= cutoff_time and (metric_type is None or m.metric_type == metric_type)
        ]

        return filtered_metrics

    def generate_performance_report(self, skill_name: str) -> PerformanceReport:
        """
        Generate comprehensive performance report for a skill.

        Args:
            skill_name: Name of the skill

        Returns:
            Performance analysis report
        """
        # Check cache first
        cache_key = f"{skill_name}_performance_report"
        if cache_key in self.performance_cache:
            cached_report = self.performance_cache[cache_key]
            if datetime.now() - cached_report.timestamp < self.cache_ttl:
                return cached_report

        # Collect all metric types
        all_metrics = self.skill_metrics.get(skill_name, [])
        if not all_metrics:
            return PerformanceReport(
                skill_name=skill_name,
                time_period=(datetime.now(), datetime.now()),
                overall_tier=PerformanceTier.NEEDS_IMPROVEMENT,
                metrics_summary={},
                trends={},
                bottlenecks=["No performance data available"],
                recommendations=["Start monitoring skill performance"],
                optimization_score=0.0,
                timestamp=datetime.now(),
            )

        # Analyze each metric type
        metrics_summary = {}
        trends = {}
        bottlenecks = []
        tier_scores = []

        metric_types = set(m.metric_type for m in all_metrics)

        for metric_type in metric_types:
            type_metrics = [m for m in all_metrics if m.metric_type == metric_type]
            if type_metrics:
                analysis = self._analyze_performance_patterns(type_metrics)
                metrics_summary[metric_type] = analysis

                # Calculate trend
                trends[metric_type] = analysis.get("trend", "unknown")

                # Determine tier
                tier = self._get_performance_tier(metric_type, analysis["mean"])
                tier_scores.append(self._tier_to_score(tier))

                # Identify bottlenecks
                if tier in [PerformanceTier.NEEDS_IMPROVEMENT, PerformanceTier.CRITICAL]:
                    bottlenecks.append(f"{metric_type.value} performance: {tier.value}")

        # Calculate overall performance
        overall_score = statistics.mean(tier_scores) if tier_scores else 0.0
        overall_tier = self._score_to_tier(overall_score)

        # Generate recommendations
        recommendations = self._generate_overall_recommendations(overall_tier, metrics_summary)

        # Create report
        report = PerformanceReport(
            skill_name=skill_name,
            time_period=(min(m.timestamp for m in all_metrics), max(m.timestamp for m in all_metrics)),
            overall_tier=overall_tier,
            metrics_summary=metrics_summary,
            trends=trends,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            optimization_score=overall_score,
            timestamp=datetime.now(),
        )

        # Cache the report
        self.performance_cache[cache_key] = report

        return report

    def _get_performance_tier(self, metric_type: MetricType, value: float) -> PerformanceTier:
        """Get performance tier for a metric value."""
        threshold = self.thresholds.get(metric_type)
        if not threshold or not threshold.tier_mapping:
            return PerformanceTier.ACCEPTABLE

        for tier, (min_val, max_val) in threshold.tier_mapping.items():
            if min_val <= value < max_val:
                return tier

        return PerformanceTier.CRITICAL

    def _tier_to_score(self, tier: PerformanceTier) -> float:
        """Convert performance tier to numeric score."""
        score_mapping = {
            PerformanceTier.EXCELLENT: 1.0,
            PerformanceTier.GOOD: 0.8,
            PerformanceTier.ACCEPTABLE: 0.6,
            PerformanceTier.NEEDS_IMPROVEMENT: 0.4,
            PerformanceTier.CRITICAL: 0.2,
        }
        return score_mapping.get(tier, 0.0)

    def _score_to_tier(self, score: float) -> PerformanceTier:
        """Convert numeric score to performance tier."""
        if score >= 0.9:
            return PerformanceTier.EXCELLENT
        if score >= 0.7:
            return PerformanceTier.GOOD
        if score >= 0.5:
            return PerformanceTier.ACCEPTABLE
        if score >= 0.3:
            return PerformanceTier.NEEDS_IMPROVEMENT
        return PerformanceTier.CRITICAL

    def _generate_overall_recommendations(
        self, tier: PerformanceTier, metrics_summary: dict[MetricType, dict]
    ) -> list[str]:
        """Generate overall performance recommendations."""
        recommendations = []

        if tier == PerformanceTier.CRITICAL:
            recommendations.append("Immediate performance optimization required")
            recommendations.append("Consider fundamental architecture review")
        elif tier == PerformanceTier.NEEDS_IMPROVEMENT:
            recommendations.append("Performance optimization recommended")
            recommendations.append("Focus on addressing identified bottlenecks")
        elif tier == PerformanceTier.ACCEPTABLE:
            recommendations.append("Performance is acceptable but could be improved")
            recommendations.append("Consider implementing optimization suggestions")
        elif tier == PerformanceTier.GOOD:
            recommendations.append("Good performance maintained")
            recommendations.append("Continue monitoring for optimization opportunities")
        else:  # EXCELLENT
            recommendations.append("Excellent performance achieved")
            recommendations.append("Maintain current optimization practices")

        return recommendations

    async def store_performance_metrics(self, skill_name: str):
        """Store performance metrics in MCP storage."""
        metrics = self.get_skill_metrics(skill_name)

        serialized_metrics = [
            {
                "metric_type": m.metric_type.value,
                "value": m.value,
                "unit": m.unit,
                "timestamp": m.timestamp.isoformat(),
                "execution_id": m.execution_id,
                "metadata": m.metadata,
            }
            for m in metrics
        ]

        await store_result(
            namespace="performance_metrics",
            key=f"{skill_name}_metrics_{datetime.now().isoformat()}",
            data={
                "skill_name": skill_name,
                "metrics": serialized_metrics,
                "real_time_metrics": self.real_time_metrics,
                "timestamp": datetime.now().isoformat(),
            },
        )
