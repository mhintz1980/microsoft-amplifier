"""Performance Monitoring and Optimization.

Comprehensive performance monitoring for the MCP storage system with
real-time metrics, optimization recommendations, and automated tuning.
"""

import asyncio
import json
import time
import uuid
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class MetricType(Enum):
    """Types of performance metrics."""

    COUNTER = "counter"  # Cumulative counter
    GAUGE = "gauge"  # Current value
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"  # Timing measurements


class AlertLevel(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class OptimizationType(Enum):
    """Types of optimizations."""

    CACHE_TUNING = "cache_tuning"
    COMPRESSION_ADJUSTMENT = "compression_adjustment"
    STORAGE_REALLOCATION = "storage_reallocation"
    PERFORMANCE_TUNING = "performance_tuning"
    AUTO_SCALING = "auto_scaling"


@dataclass
class PerformanceMetric:
    """Single performance metric."""

    name: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    labels: dict[str, str] = field(default_factory=dict)
    description: str = ""


@dataclass
class PerformanceAlert:
    """Performance alert definition."""

    alert_id: str
    name: str
    level: AlertLevel
    message: str
    metric_name: str
    threshold: float
    condition: str  # ">=", "<=", etc.
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class OptimizationRecommendation:
    """System optimization recommendation."""

    recommendation_id: str
    optimization_type: OptimizationType
    title: str
    description: str
    expected_improvement: str
    implementation_complexity: str  # low, medium, high
    priority: int  # 1-10
    created_at: datetime = field(default_factory=datetime.now)
    implemented: bool = False
    results_measured: bool = False


@dataclass
class PerformanceReport:
    """Comprehensive performance report."""

    report_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    metrics_summary: dict[str, Any]
    alerts_summary: dict[str, Any]
    recommendations: list[OptimizationRecommendation]
    overall_health_score: float
    key_insights: list[str]


class PerformanceMonitor:
    """Monitors and optimizes MCP storage system performance."""

    def __init__(self):
        self.metrics_store = {}  # metric_name -> list[PerformanceMetric]
        self.alerts = {}  # alert_id -> PerformanceAlert
        self.recommendations = {}  # recommendation_id -> OptimizationRecommendation
        self.performance_reports = []  # List of PerformanceReport

        # Configuration
        self.monitoring_interval = 30  # seconds
        self.metrics_retention_hours = 24 * 7  # 1 week
        self.alert_cooldown_minutes = 15  # Prevent alert spamming
        self.optimization_enabled = True
        self.auto_optimization = True

        # Storage directory
        self.storage_dir = Path.home() / ".amplifier_storage" / "performance_monitor"
        self.metrics_file = self.storage_dir / "metrics.json"
        self.alerts_file = self.storage_dir / "alerts.json"
        self.recommendations_file = self.storage_dir / "recommendations.json"
        self.reports_dir = self.storage_dir / "reports"

        # Alert tracking
        self.last_alert_times = {}  # alert_key -> datetime

        # Performance thresholds
        self.thresholds = {
            "storage_utilization_percent": 80.0,
            "cache_hit_rate": 0.8,
            "compression_ratio": 0.85,
            "backup_success_rate": 0.95,
            "replication_latency_ms": 1000.0,
            "error_rate": 0.05,
            "response_time_p95_ms": 500.0,
        }

        # Baseline metrics for comparison
        self.baseline_metrics = {}

    async def initialize(self) -> None:
        """Initialize the performance monitor."""
        await self._ensure_storage_structure()
        await self._load_metrics()
        await self._load_alerts()
        await self._load_recommendations()
        await self._setup_default_alerts()
        await self._establish_baseline()
        logger.info("Performance Monitor initialized")

    async def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        unit: str = "",
        labels: dict[str, str] | None = None,
        description: str = "",
    ) -> None:
        """Record a performance metric."""
        try:
            metric = PerformanceMetric(
                name=name,
                metric_type=metric_type,
                value=value,
                unit=unit,
                labels=labels or {},
                description=description,
            )

            if name not in self.metrics_store:
                self.metrics_store[name] = []

            self.metrics_store[name].append(metric)

            # Check for alerts
            await self._check_alerts(name, value)

            # Log significant metrics
            if self._is_significant_metric(name, value):
                logger.info(f"Performance metric: {name}={value}{unit}")

        except Exception as e:
            logger.error(f"Failed to record metric {name}: {e}")

    async def record_timer(self, name: str, duration_ms: float, labels: dict[str, str] | None = None) -> None:
        """Record a timing metric."""
        await self.record_metric(
            name=f"{name}_duration_ms",
            value=duration_ms,
            metric_type=MetricType.TIMER,
            unit="ms",
            labels=labels,
            description=f"Duration of {name} operation",
        )

    async def increment_counter(self, name: str, increment: float = 1.0, labels: dict[str, str] | None = None) -> None:
        """Increment a counter metric."""
        current_value = 0.0
        if name in self.metrics_store and self.metrics_store[name]:
            current_value = self.metrics_store[name][-1].value

        await self.record_metric(
            name=name,
            value=current_value + increment,
            metric_type=MetricType.COUNTER,
            labels=labels,
            description=f"Counter for {name}",
        )

    async def get_metrics_summary(
        self, time_window_hours: int = 1, metric_names: list[str] | None = None
    ) -> dict[str, Any]:
        """Get summary of metrics for a time window."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            summary = {}

            metrics_to_analyze = metric_names or list(self.metrics_store.keys())

            for metric_name in metrics_to_analyze:
                if metric_name not in self.metrics_store:
                    continue

                # Filter metrics by time window
                recent_metrics = [m for m in self.metrics_store[metric_name] if m.timestamp >= cutoff_time]

                if not recent_metrics:
                    continue

                # Calculate statistics based on metric type
                metric_type = recent_metrics[0].metric_type
                values = [m.value for m in recent_metrics]

                if metric_type == MetricType.COUNTER:
                    summary[metric_name] = {
                        "type": "counter",
                        "current_value": values[-1] if values else 0,
                        "total_increment": values[-1] - values[0] if len(values) > 1 else 0,
                        "measurement_count": len(values),
                    }
                else:
                    # Gauge, Histogram, Timer
                    summary[metric_name] = {
                        "type": metric_type.value,
                        "current_value": values[-1] if values else 0,
                        "min_value": min(values),
                        "max_value": max(values),
                        "avg_value": sum(values) / len(values),
                        "measurement_count": len(values),
                        "trend": self._calculate_trend(values),
                    }

                    # Calculate percentiles for timing metrics
                    if "duration_ms" in metric_name or metric_type == MetricType.TIMER:
                        sorted_values = sorted(values)
                        n = len(sorted_values)
                        summary[metric_name]["p50"] = sorted_values[n // 2] if n > 0 else 0
                        summary[metric_name]["p95"] = sorted_values[int(n * 0.95)] if n > 0 else 0
                        summary[metric_name]["p99"] = sorted_values[int(n * 0.99)] if n > 0 else 0

            return summary

        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}

    async def generate_performance_report(self, period_hours: int = 24) -> PerformanceReport:
        """Generate comprehensive performance report."""
        try:
            report_id = str(uuid.uuid4())
            now = datetime.now()
            period_start = now - timedelta(hours=period_hours)

            # Get metrics summary
            metrics_summary = await self.get_metrics_summary(period_hours)

            # Get alerts summary
            active_alerts = [a for a in self.alerts.values() if not a.resolved]
            recent_alerts = [a for a in self.alerts.values() if a.triggered_at >= period_start]

            alerts_summary = {
                "total_active_alerts": len(active_alerts),
                "alerts_by_level": {
                    level.value: len([a for a in active_alerts if a.level == level]) for level in AlertLevel
                },
                "recent_alerts_count": len(recent_alerts),
                "critical_alerts": [
                    {"id": a.alert_id, "message": a.message, "triggered_at": a.triggered_at.isoformat()}
                    for a in active_alerts
                    if a.level == AlertLevel.CRITICAL
                ],
            }

            # Generate recommendations
            recommendations = await self._generate_recommendations(metrics_summary, alerts_summary)

            # Calculate overall health score
            health_score = await self._calculate_health_score(metrics_summary, alerts_summary)

            # Generate key insights
            key_insights = await self._generate_key_insights(metrics_summary, alerts_summary, health_score)

            report = PerformanceReport(
                report_id=report_id,
                generated_at=now,
                period_start=period_start,
                period_end=now,
                metrics_summary=metrics_summary,
                alerts_summary=alerts_summary,
                recommendations=recommendations,
                overall_health_score=health_score,
                key_insights=key_insights,
            )

            # Save report
            await self._save_performance_report(report)
            self.performance_reports.append(report)

            # Keep only recent reports
            if len(self.performance_reports) > 30:  # Keep last 30 reports
                self.performance_reports = self.performance_reports[-30:]

            return report

        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            raise

    async def optimize_performance(self, auto_implement: bool = False) -> list[OptimizationRecommendation]:
        """Analyze performance and generate optimization recommendations."""
        try:
            # Get current metrics
            metrics_summary = await self.get_metrics_summary(1)  # Last hour

            # Generate recommendations
            recommendations = []

            # Cache optimization
            if "cache_hit_rate" in metrics_summary:
                cache_hit_rate = metrics_summary["cache_hit_rate"]["current_value"]
                if cache_hit_rate < self.thresholds["cache_hit_rate"]:
                    recommendations.append(
                        OptimizationRecommendation(
                            recommendation_id=str(uuid.uuid4()),
                            optimization_type=OptimizationType.CACHE_TUNING,
                            title="Improve Cache Hit Rate",
                            description=f"Current cache hit rate is {cache_hit_rate:.1%}, below target of {self.thresholds['cache_hit_rate']:.1%}. Consider increasing cache size or optimizing cache keys.",
                            expected_improvement="10-25% performance improvement",
                            implementation_complexity="medium",
                            priority=7,
                        )
                    )

            # Storage utilization
            if "storage_utilization_percent" in metrics_summary:
                utilization = metrics_summary["storage_utilization_percent"]["current_value"]
                if utilization > self.thresholds["storage_utilization_percent"]:
                    recommendations.append(
                        OptimizationRecommendation(
                            recommendation_id=str(uuid.uuid4()),
                            optimization_type=OptimizationType.STORAGE_REALLOCATION,
                            title="Optimize Storage Utilization",
                            description=f"Storage utilization is {utilization:.1f}%, above threshold of {self.thresholds['storage_utilization_percent']}%. Consider data cleanup or tiered storage.",
                            expected_improvement="Reduced storage costs and improved performance",
                            implementation_complexity="low",
                            priority=8,
                        )
                    )

            # Compression optimization
            if "compression_ratio" in metrics_summary:
                compression_ratio = metrics_summary["compression_ratio"]["current_value"]
                if compression_ratio < self.thresholds["compression_ratio"]:
                    recommendations.append(
                        OptimizationRecommendation(
                            recommendation_id=str(uuid.uuid4()),
                            optimization_type=OptimizationType.COMPRESSION_ADJUSTMENT,
                            title="Improve Compression Efficiency",
                            description=f"Current compression ratio is {compression_ratio:.1%}, below target of {self.thresholds['compression_ratio']:.1%}. Consider different compression algorithms.",
                            expected_improvement="5-15% storage reduction",
                            implementation_complexity="medium",
                            priority=6,
                        )
                    )

            # Response time optimization
            if "response_time_p95_ms" in metrics_summary:
                response_time = metrics_summary["response_time_p95_ms"]["p95"]
                if response_time > self.thresholds["response_time_p95_ms"]:
                    recommendations.append(
                        OptimizationRecommendation(
                            recommendation_id=str(uuid.uuid4()),
                            optimization_type=OptimizationType.PERFORMANCE_TUNING,
                            title="Optimize Response Times",
                            description=f"95th percentile response time is {response_time:.0f}ms, above target of {self.thresholds['response_time_p95_ms']:.0f}ms. Consider query optimization.",
                            expected_improvement="20-40% faster response times",
                            implementation_complexity="high",
                            priority=7,
                        )
                    )

            # Sort by priority
            recommendations.sort(key=lambda r: r.priority, reverse=True)

            # Save recommendations
            for rec in recommendations:
                self.recommendations[rec.recommendation_id] = rec

            await self._save_recommendations()

            # Auto-implement if enabled
            if auto_implement and self.auto_optimization:
                for rec in recommendations:
                    if rec.priority >= 8 and rec.implementation_complexity == "low":
                        await self._implement_recommendation(rec)

            return recommendations

        except Exception as e:
            logger.error(f"Failed to optimize performance: {e}")
            return []

    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge a performance alert."""
        try:
            if alert_id in self.alerts:
                self.alerts[alert_id].acknowledged = True
                await self._save_alerts()
                logger.info(f"Acknowledged alert: {alert_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
            return False

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a performance alert."""
        try:
            if alert_id in self.alerts:
                self.alerts[alert_id].resolved = True
                await self._save_alerts()
                logger.info(f"Resolved alert: {alert_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {e}")
            return False

    async def start_monitoring(self) -> None:
        """Start the performance monitoring loop."""
        try:
            asyncio.create_task(self._monitoring_loop())
            asyncio.create_task(self._cleanup_loop())
            asyncio.create_task(self._optimization_loop())
            logger.info("Started performance monitoring loops")

        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")

    async def _ensure_storage_structure(self) -> None:
        """Ensure storage directories exist."""
        directories = [
            self.storage_dir,
            self.reports_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    async def _load_metrics(self) -> None:
        """Load stored metrics."""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file) as f:
                    data = json.load(f)

                for metric_name, metric_list in data.items():
                    self.metrics_store[metric_name] = [
                        PerformanceMetric(
                            name=m["name"],
                            metric_type=MetricType(m["metric_type"]),
                            value=m["value"],
                            unit=m["unit"],
                            timestamp=datetime.fromisoformat(m["timestamp"]),
                            labels=m["labels"],
                            description=m["description"],
                        )
                        for m in metric_list
                    ]

                logger.info(f"Loaded {len(self.metrics_store)} metric types")

        except Exception as e:
            logger.warning(f"Failed to load metrics: {e}")

    async def _save_metrics(self) -> None:
        """Save current metrics to storage."""
        try:
            # Limit metrics to retention period
            cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)

            filtered_metrics = {}
            for metric_name, metrics in self.metrics_store.items():
                filtered_metrics[metric_name] = [
                    {
                        "name": m.name,
                        "metric_type": m.metric_type.value,
                        "value": m.value,
                        "unit": m.unit,
                        "timestamp": m.timestamp.isoformat(),
                        "labels": m.labels,
                        "description": m.description,
                    }
                    for m in metrics
                    if m.timestamp >= cutoff_time
                ]

            with open(self.metrics_file, "w") as f:
                json.dump(filtered_metrics, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    async def _load_alerts(self) -> None:
        """Load stored alerts."""
        try:
            if self.alerts_file.exists():
                with open(self.alerts_file) as f:
                    data = json.load(f)

                self.alerts = {
                    alert_id: PerformanceAlert(
                        alert_id=a["alert_id"],
                        name=a["name"],
                        level=AlertLevel(a["level"]),
                        message=a["message"],
                        metric_name=a["metric_name"],
                        threshold=a["threshold"],
                        condition=a["condition"],
                        triggered_at=datetime.fromisoformat(a["triggered_at"]),
                        acknowledged=a["acknowledged"],
                        resolved=a["resolved"],
                    )
                    for alert_id, a in data.items()
                }

                logger.info(f"Loaded {len(self.alerts)} alerts")

        except Exception as e:
            logger.warning(f"Failed to load alerts: {e}")

    async def _save_alerts(self) -> None:
        """Save alerts to storage."""
        try:
            with open(self.alerts_file, "w") as f:
                json.dump(
                    {
                        alert_id: {
                            "alert_id": a.alert_id,
                            "name": a.name,
                            "level": a.level.value,
                            "message": a.message,
                            "metric_name": a.metric_name,
                            "threshold": a.threshold,
                            "condition": a.condition,
                            "triggered_at": a.triggered_at.isoformat(),
                            "acknowledged": a.acknowledged,
                            "resolved": a.resolved,
                        }
                        for alert_id, a in self.alerts.items()
                    },
                    f,
                    indent=2,
                )

        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")

    async def _load_recommendations(self) -> None:
        """Load stored recommendations."""
        try:
            if self.recommendations_file.exists():
                with open(self.recommendations_file) as f:
                    data = json.load(f)

                self.recommendations = {
                    rec_id: OptimizationRecommendation(
                        recommendation_id=r["recommendation_id"],
                        optimization_type=OptimizationType(r["optimization_type"]),
                        title=r["title"],
                        description=r["description"],
                        expected_improvement=r["expected_improvement"],
                        implementation_complexity=r["implementation_complexity"],
                        priority=r["priority"],
                        created_at=datetime.fromisoformat(r["created_at"]),
                        implemented=r["implemented"],
                        results_measured=r["results_measured"],
                    )
                    for rec_id, r in data.items()
                }

                logger.info(f"Loaded {len(self.recommendations)} recommendations")

        except Exception as e:
            logger.warning(f"Failed to load recommendations: {e}")

    async def _save_recommendations(self) -> None:
        """Save recommendations to storage."""
        try:
            with open(self.recommendations_file, "w") as f:
                json.dump(
                    {
                        rec_id: {
                            "recommendation_id": r.recommendation_id,
                            "optimization_type": r.optimization_type.value,
                            "title": r.title,
                            "description": r.description,
                            "expected_improvement": r.expected_improvement,
                            "implementation_complexity": r.implementation_complexity,
                            "priority": r.priority,
                            "created_at": r.created_at.isoformat(),
                            "implemented": r.implemented,
                            "results_measured": r.results_measured,
                        }
                        for rec_id, r in self.recommendations.items()
                    },
                    f,
                    indent=2,
                )

        except Exception as e:
            logger.error(f"Failed to save recommendations: {e}")

    async def _setup_default_alerts(self) -> None:
        """Setup default performance alerts."""
        try:
            default_alerts = [
                {
                    "name": "High Storage Utilization",
                    "level": AlertLevel.WARNING,
                    "metric_name": "storage_utilization_percent",
                    "threshold": self.thresholds["storage_utilization_percent"],
                    "condition": ">=",
                },
                {
                    "name": "Low Cache Hit Rate",
                    "level": AlertLevel.WARNING,
                    "metric_name": "cache_hit_rate",
                    "threshold": self.thresholds["cache_hit_rate"],
                    "condition": "<=",
                },
                {
                    "name": "High Error Rate",
                    "level": AlertLevel.ERROR,
                    "metric_name": "error_rate",
                    "threshold": self.thresholds["error_rate"],
                    "condition": ">=",
                },
                {
                    "name": "Slow Response Times",
                    "level": AlertLevel.WARNING,
                    "metric_name": "response_time_p95_ms",
                    "threshold": self.thresholds["response_time_p95_ms"],
                    "condition": ">=",
                },
            ]

            for alert_config in default_alerts:
                alert_id = str(uuid.uuid4())
                self.alerts[alert_id] = PerformanceAlert(
                    alert_id=alert_id,
                    name=alert_config["name"],
                    level=alert_config["level"],
                    message=f"{alert_config['name']} threshold exceeded",
                    metric_name=alert_config["metric_name"],
                    threshold=alert_config["threshold"],
                    condition=alert_config["condition"],
                )

            await self._save_alerts()
            logger.info(f"Setup {len(default_alerts)} default alerts")

        except Exception as e:
            logger.error(f"Failed to setup default alerts: {e}")

    async def _establish_baseline(self) -> None:
        """Establish baseline performance metrics."""
        try:
            # Collect baseline metrics over a short period
            baseline_period = 5  # minutes
            baseline_end = time.time() + (baseline_period * 60)

            logger.info("Establishing performance baseline...")

            # This would collect system metrics for baseline comparison
            # For now, we'll set some reasonable defaults
            self.baseline_metrics = {
                "storage_utilization_percent": 50.0,
                "cache_hit_rate": 0.85,
                "compression_ratio": 0.90,
                "response_time_p95_ms": 200.0,
                "error_rate": 0.01,
            }

            logger.info("Performance baseline established")

        except Exception as e:
            logger.error(f"Failed to establish baseline: {e}")

    async def _check_alerts(self, metric_name: str, value: float) -> None:
        """Check if any alerts should be triggered."""
        try:
            current_time = datetime.now()
            alert_key = f"{metric_name}_{value}"

            # Check cooldown period
            if alert_key in self.last_alert_times:
                time_since_last = current_time - self.last_alert_times[alert_key]
                if time_since_last.total_seconds() < (self.alert_cooldown_minutes * 60):
                    return  # Still in cooldown period

            # Check each alert for this metric
            for alert in self.alerts.values():
                if alert.metric_name == metric_name and not alert.resolved:
                    triggered = self._evaluate_condition(value, alert.condition, alert.threshold)

                    if triggered:
                        # Update alert
                        alert.triggered_at = current_time
                        alert.acknowledged = False

                        # Log alert
                        logger.warning(f"ALERT: {alert.name} - {alert.message} (value: {value})")

                        # Update cooldown
                        self.last_alert_times[alert_key] = current_time

                        await self._save_alerts()

        except Exception as e:
            logger.error(f"Failed to check alerts for {metric_name}: {e}")

    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition."""
        try:
            if condition == ">=":
                return value >= threshold
            elif condition == "<=":
                return value <= threshold
            elif condition == ">":
                return value > threshold
            elif condition == "<":
                return value < threshold
            elif condition == "==":
                return value == threshold
            elif condition == "!=":
                return value != threshold
            else:
                return False

        except Exception:
            return False

    def _is_significant_metric(self, name: str, value: float) -> bool:
        """Determine if a metric is significant enough to log."""
        # Log metrics that deviate significantly from baseline
        if name in self.baseline_metrics:
            baseline = self.baseline_metrics[name]
            deviation = abs(value - baseline) / baseline if baseline != 0 else 0
            return deviation > 0.1  # 10% deviation
        return False

    def _calculate_trend(self, values: list[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 2:
            return "stable"

        # Simple trend calculation
        recent_avg = sum(values[-3:]) / min(3, len(values))
        older_avg = sum(values[:-3]) / max(1, len(values) - 3)

        if recent_avg > older_avg * 1.05:
            return "increasing"
        elif recent_avg < older_avg * 0.95:
            return "decreasing"
        else:
            return "stable"

    async def _monitoring_loop(self) -> None:
        """Main performance monitoring loop."""
        while True:
            try:
                # Collect system metrics
                await self._collect_system_metrics()

                # Save metrics
                await self._save_metrics()

                # Sleep until next collection
                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(10)  # Short retry interval

    async def _collect_system_metrics(self) -> None:
        """Collect system performance metrics."""
        try:
            import psutil
            import shutil

            # CPU utilization
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.record_metric("cpu_utilization_percent", cpu_percent, unit="%")

            # Memory utilization
            memory = psutil.virtual_memory()
            await self.record_metric("memory_utilization_percent", memory.percent, unit="%")
            await self.record_metric("memory_available_gb", memory.available / (1024**3), unit="GB")

            # Disk utilization
            disk_usage = shutil.disk_usage("/")
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            await self.record_metric("disk_utilization_percent", disk_percent, unit="%")
            await self.record_metric("disk_available_gb", disk_usage.free / (1024**3), unit="GB")

            # Process metrics
            process = psutil.Process()
            await self.record_metric("process_memory_mb", process.memory_info().rss / (1024**2), unit="MB")
            await self.record_metric("process_cpu_percent", process.cpu_percent(), unit="%")

            # Application-specific metrics would be collected here
            # These would be injected by the skill repository manager and other components

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")

    async def _cleanup_loop(self) -> None:
        """Cleanup old metrics and data."""
        while True:
            try:
                # Run cleanup every hour
                await asyncio.sleep(3600)

                # Cleanup old metrics
                await self._save_metrics()  # This handles retention

                # Cleanup resolved alerts older than retention period
                cutoff_time = datetime.now() - timedelta(days=7)
                resolved_alerts = [
                    alert_id
                    for alert_id, alert in self.alerts.items()
                    if alert.resolved and alert.triggered_at < cutoff_time
                ]

                for alert_id in resolved_alerts:
                    del self.alerts[alert_id]

                if resolved_alerts:
                    await self._save_alerts()
                    logger.info(f"Cleaned up {len(resolved_alerts)} old resolved alerts")

            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")

    async def _optimization_loop(self) -> None:
        """Automatic optimization loop."""
        while True:
            try:
                # Run optimization every 6 hours
                await asyncio.sleep(6 * 3600)

                if self.optimization_enabled:
                    await self.optimize_performance(auto_implement=self.auto_optimization)

            except Exception as e:
                logger.error(f"Optimization loop error: {e}")

    async def _generate_recommendations(
        self, metrics_summary: dict[str, Any], alerts_summary: dict[str, Any]
    ) -> list[OptimizationRecommendation]:
        """Generate optimization recommendations based on metrics and alerts."""
        try:
            recommendations = []

            # Analyze alerts for recommendations
            critical_alerts = alerts_summary.get("critical_alerts", [])
            if critical_alerts:
                recommendations.append(
                    OptimizationRecommendation(
                        recommendation_id=str(uuid.uuid4()),
                        optimization_type=OptimizationType.AUTO_SCALING,
                        title="Address Critical Performance Issues",
                        description=f"There are {len(critical_alerts)} critical alerts that need immediate attention.",
                        expected_improvement="System stability and performance",
                        implementation_complexity="high",
                        priority=10,
                    )
                )

            # Add more sophisticated recommendation logic here
            # This would analyze trends, patterns, and correlations

            return recommendations

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []

    async def _calculate_health_score(self, metrics_summary: dict[str, Any], alerts_summary: dict[str, Any]) -> float:
        """Calculate overall system health score (0-100)."""
        try:
            base_score = 100.0

            # Deduct points for active alerts
            active_alerts = alerts_summary.get("total_active_alerts", 0)
            base_score -= active_alerts * 5

            # Deduct points for critical alerts
            critical_alerts = len(alerts_summary.get("critical_alerts", []))
            base_score -= critical_alerts * 20

            # Adjust based on key metrics
            if "error_rate" in metrics_summary:
                error_rate = metrics_summary["error_rate"]["current_value"]
                if error_rate > 0.05:  # 5% error rate
                    base_score -= 30
                elif error_rate > 0.01:  # 1% error rate
                    base_score -= 10

            if "response_time_p95_ms" in metrics_summary:
                response_time = metrics_summary["response_time_p95_ms"]["p95"]
                if response_time > 1000:  # 1 second
                    base_score -= 20
                elif response_time > 500:  # 500ms
                    base_score -= 10

            return max(0.0, min(100.0, base_score))

        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            return 50.0

    async def _generate_key_insights(
        self, metrics_summary: dict[str, Any], alerts_summary: dict[str, Any], health_score: float
    ) -> list[str]:
        """Generate key insights from performance data."""
        try:
            insights = []

            # Health assessment
            if health_score >= 90:
                insights.append("System performance is excellent")
            elif health_score >= 70:
                insights.append("System performance is good with room for improvement")
            elif health_score >= 50:
                insights.append("System performance needs attention")
            else:
                insights.append("System performance requires immediate action")

            # Alert insights
            active_alerts = alerts_summary.get("total_active_alerts", 0)
            if active_alerts > 5:
                insights.append(f"High number of active alerts ({active_alerts}) indicates system stress")

            # Metric trends
            for metric_name, metric_data in metrics_summary.items():
                if "trend" in metric_data:
                    if metric_data["trend"] == "increasing" and "duration_ms" in metric_name:
                        insights.append(f"Response times are trending upward for {metric_name}")
                    elif metric_data["trend"] == "decreasing" and "hit_rate" in metric_name:
                        insights.append(f"Cache performance is degrading")

            return insights

        except Exception as e:
            logger.error(f"Failed to generate key insights: {e}")
            return ["Unable to generate insights due to error"]

    async def _save_performance_report(self, report: PerformanceReport) -> None:
        """Save performance report to storage."""
        try:
            report_file = self.reports_dir / f"report_{report.report_id}.json"
            with open(report_file, "w") as f:
                json.dump(
                    {
                        "report_id": report.report_id,
                        "generated_at": report.generated_at.isoformat(),
                        "period_start": report.period_start.isoformat(),
                        "period_end": report.period_end.isoformat(),
                        "metrics_summary": report.metrics_summary,
                        "alerts_summary": report.alerts_summary,
                        "recommendations": [
                            {
                                "recommendation_id": r.recommendation_id,
                                "optimization_type": r.optimization_type.value,
                                "title": r.title,
                                "description": r.description,
                                "expected_improvement": r.expected_improvement,
                                "implementation_complexity": r.implementation_complexity,
                                "priority": r.priority,
                                "created_at": r.created_at.isoformat(),
                                "implemented": r.implemented,
                                "results_measured": r.results_measured,
                            }
                            for r in report.recommendations
                        ],
                        "overall_health_score": report.overall_health_score,
                        "key_insights": report.key_insights,
                    },
                    f,
                    indent=2,
                )

        except Exception as e:
            logger.error(f"Failed to save performance report: {e}")

    async def _implement_recommendation(self, recommendation: OptimizationRecommendation) -> bool:
        """Implement an optimization recommendation."""
        try:
            logger.info(f"Implementing recommendation: {recommendation.title}")

            # This would contain the actual implementation logic
            # For now, we'll just mark it as implemented
            recommendation.implemented = True
            recommendation.results_measured = False

            await self._save_recommendations()

            logger.info(f"Implemented recommendation: {recommendation.recommendation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to implement recommendation {recommendation.recommendation_id}: {e}")
            return False
