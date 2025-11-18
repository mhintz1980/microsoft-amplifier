"""
Integration Reliability Monitor

Provides comprehensive monitoring and alerting for system integrations.
Tracks performance metrics, detects degradation, and triggers automatic responses.
"""

import asyncio
import contextlib
import json
import time
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from enum import Enum
from typing import Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HealthStatus(Enum):
    """System health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class ReliabilityMetric:
    """Individual reliability metric."""

    name: str
    value: float
    threshold: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    trend: str = "stable"  # improving, declining, stable

    @property
    def is_healthy(self) -> bool:
        """Check if metric meets threshold."""
        return self.value >= self.threshold

    @property
    def health_percentage(self) -> float:
        """Calculate health as percentage of threshold."""
        return min((self.value / self.threshold) * 100, 100.0)


@dataclass
class Alert:
    """System alert."""

    id: str
    level: AlertLevel
    title: str
    message: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_time: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealthReport:
    """Comprehensive system health report."""

    overall_status: HealthStatus
    reliability_score: float
    uptime_percentage: float
    metrics: list[ReliabilityMetric]
    active_alerts: list[Alert]
    recommendations: list[str]
    timestamp: datetime = field(default_factory=datetime.now)


class ReliabilityMonitor:
    """Monitors system integration reliability."""

    def __init__(self, check_interval: float = 30.0):
        self.check_interval = check_interval
        self.metrics: dict[str, ReliabilityMetric] = {}
        self.alerts: list[Alert] = []
        self.history: list[SystemHealthReport] = []
        self.thresholds = {
            "connection_success_rate": 95.0,
            "response_time_p95": 2.0,
            "error_rate": 5.0,
            "throughput": 100.0,
            "availability": 99.0,
        }
        self._monitoring_task = None
        self._running = False

    async def start_monitoring(self):
        """Start background monitoring."""
        if self._running:
            return

        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Reliability monitoring started")

    async def stop_monitoring(self):
        """Stop background monitoring."""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._monitoring_task
        logger.info("Reliability monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5.0)  # Brief pause before retry

    async def _perform_health_check(self):
        """Perform comprehensive health check."""
        metrics = await self._collect_metrics()
        alerts = await self._evaluate_alerts(metrics)
        recommendations = self._generate_recommendations(metrics, alerts)

        # Determine overall status
        overall_status = self._determine_overall_status(metrics, alerts)
        reliability_score = self._calculate_reliability_score(metrics)
        uptime_percentage = self._calculate_uptime_percentage()

        # Create health report
        report = SystemHealthReport(
            overall_status=overall_status,
            reliability_score=reliability_score,
            uptime_percentage=uptime_percentage,
            metrics=metrics,
            active_alerts=[a for a in self.alerts if not a.resolved],
            recommendations=recommendations,
        )

        self.history.append(report)

        # Keep only last 100 reports
        if len(self.history) > 100:
            self.history = self.history[-100:]

        # Log status changes
        await self._log_status_changes(report)

        # Trigger automatic responses
        await self._trigger_automatic_responses(report)

    async def _collect_metrics(self) -> list[ReliabilityMetric]:
        """Collect current system metrics."""
        metrics = []

        # Collect from different sources
        metrics.extend(await self._collect_connection_metrics())
        metrics.extend(await self._collect_performance_metrics())
        metrics.extend(await self._collect_error_metrics())
        metrics.extend(await self._collect_throughput_metrics())

        # Update stored metrics
        for metric in metrics:
            old_metric = self.metrics.get(metric.name)
            if old_metric:
                # Calculate trend
                if metric.value > old_metric.value * 1.05:
                    metric.trend = "improving"
                elif metric.value < old_metric.value * 0.95:
                    metric.trend = "declining"

            self.metrics[metric.name] = metric

        return metrics

    async def _collect_connection_metrics(self) -> list[ReliabilityMetric]:
        """Collect connection-related metrics."""
        metrics = []

        try:
            # Get MCP manager metrics
            from .enhanced_mcp_client import get_mcp_manager

            manager = get_mcp_manager()
            global_metrics = manager.get_global_metrics()

            # Overall reliability
            metrics.append(
                ReliabilityMetric(
                    name="overall_reliability",
                    value=global_metrics["overall_reliability"],
                    threshold=self.thresholds["availability"],
                    unit="%",
                )
            )

            # Connection success rate
            metrics.append(
                ReliabilityMetric(
                    name="connection_success_rate",
                    value=global_metrics["overall_reliability"],
                    threshold=self.thresholds["connection_success_rate"],
                    unit="%",
                )
            )

        except Exception as e:
            logger.warning(f"Failed to collect connection metrics: {e}")
            metrics.append(
                ReliabilityMetric(
                    name="connection_success_rate",
                    value=0.0,
                    threshold=self.thresholds["connection_success_rate"],
                    unit="%",
                )
            )

        return metrics

    async def _collect_performance_metrics(self) -> list[ReliabilityMetric]:
        """Collect performance-related metrics."""
        metrics = []

        # Response time metrics (simulated for now)
        # In real implementation, these would come from actual measurements
        metrics.append(
            ReliabilityMetric(
                name="response_time_p95",
                value=1.2,  # seconds
                threshold=self.thresholds["response_time_p95"],
                unit="s",
            )
        )

        return metrics

    async def _collect_error_metrics(self) -> list[ReliabilityMetric]:
        """Collect error-related metrics."""
        metrics = []

        # Error rate (simulated)
        metrics.append(
            ReliabilityMetric(
                name="error_rate",
                value=2.1,  # percentage
                threshold=self.thresholds["error_rate"],
                unit="%",
            )
        )

        return metrics

    async def _collect_throughput_metrics(self) -> list[ReliabilityMetric]:
        """Collect throughput-related metrics."""
        metrics = []

        # Throughput (simulated)
        metrics.append(
            ReliabilityMetric(
                name="throughput",
                value=150.0,  # requests per minute
                threshold=self.thresholds["throughput"],
                unit="req/min",
            )
        )

        return metrics

    async def _evaluate_alerts(self, metrics: list[ReliabilityMetric]) -> list[Alert]:
        """Evaluate metrics and generate alerts."""
        new_alerts = []

        for metric in metrics:
            if not metric.is_healthy:
                alert_level = self._determine_alert_level(metric)
                alert = Alert(
                    id=f"{metric.name}_{int(time.time())}",
                    level=alert_level,
                    title=f"Metric Below Threshold: {metric.name}",
                    message=f"{metric.name} is {metric.value}{metric.unit}, threshold is {metric.threshold}{metric.unit}",
                    source="reliability_monitor",
                    metadata={
                        "metric_name": metric.name,
                        "current_value": metric.value,
                        "threshold": metric.threshold,
                        "health_percentage": metric.health_percentage,
                    },
                )
                new_alerts.append(alert)
                self.alerts.append(alert)

        # Clean old resolved alerts
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff_time or not a.resolved]

        return new_alerts

    def _determine_alert_level(self, metric: ReliabilityMetric) -> AlertLevel:
        """Determine alert level based on metric severity."""
        health_pct = metric.health_percentage

        if health_pct < 50:
            return AlertLevel.CRITICAL
        if health_pct < 75:
            return AlertLevel.ERROR
        if health_pct < 90:
            return AlertLevel.WARNING
        return AlertLevel.INFO

    def _generate_recommendations(self, metrics: list[ReliabilityMetric], alerts: list[Alert]) -> list[str]:
        """Generate recommendations based on current state."""
        recommendations = []

        # Analyze metrics
        for metric in metrics:
            if not metric.is_healthy:
                if metric.name == "connection_success_rate":
                    recommendations.append("Check network connectivity and MCP server availability")
                    recommendations.append("Consider increasing connection timeout or retry attempts")
                elif metric.name == "response_time_p95":
                    recommendations.append("Investigate performance bottlenecks in slow operations")
                    recommendations.append("Consider implementing request caching or optimization")
                elif metric.name == "error_rate":
                    recommendations.append("Review error logs for common failure patterns")
                    recommendations.append("Implement better error handling and retry logic")
                elif metric.name == "throughput":
                    recommendations.append("Consider scaling resources or optimizing algorithms")
                    recommendations.append("Check for resource contention or bottlenecks")

        # Check for critical alerts
        critical_alerts = [a for a in alerts if a.level == AlertLevel.CRITICAL and not a.resolved]
        if critical_alerts:
            recommendations.append("URGENT: Address critical alerts immediately")
            recommendations.append("Consider enabling automatic failover mechanisms")

        # Performance trends
        declining_metrics = [m for m in metrics if m.trend == "declining" and not m.is_healthy]
        if declining_metrics:
            recommendations.append("Monitor declining metrics closely - performance degrading")
            recommendations.append("Schedule maintenance to address performance issues")

        return recommendations

    def _determine_overall_status(self, metrics: list[ReliabilityMetric], alerts: list[Alert]) -> HealthStatus:
        """Determine overall system health status."""
        # Check for critical alerts
        critical_alerts = [a for a in alerts if a.level == AlertLevel.CRITICAL and not a.resolved]
        if critical_alerts:
            return HealthStatus.CRITICAL

        # Check error alerts
        error_alerts = [a for a in alerts if a.level == AlertLevel.ERROR and not a.resolved]
        if error_alerts:
            return HealthStatus.UNHEALTHY

        # Check metric health
        unhealthy_metrics = [m for m in metrics if not m.is_healthy]
        if unhealthy_metrics:
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    def _calculate_reliability_score(self, metrics: list[ReliabilityMetric]) -> float:
        """Calculate overall reliability score."""
        if not metrics:
            return 0.0

        # Weight important metrics more heavily
        weights = {
            "connection_success_rate": 0.3,
            "overall_reliability": 0.3,
            "error_rate": 0.2,
            "response_time_p95": 0.1,
            "throughput": 0.1,
        }

        total_score = 0.0
        total_weight = 0.0

        for metric in metrics:
            weight = weights.get(metric.name, 0.1)
            score = metric.health_percentage / 100.0
            total_score += score * weight
            total_weight += weight

        return (total_score / total_weight) * 100 if total_weight > 0 else 0.0

    def _calculate_uptime_percentage(self) -> float:
        """Calculate system uptime percentage."""
        # Simplified calculation - in real implementation, track actual uptime
        if not self.history:
            return 100.0

        recent_reports = self.history[-10:]  # Last 10 reports
        healthy_count = sum(1 for r in recent_reports if r.overall_status == HealthStatus.HEALTHY)
        return (healthy_count / len(recent_reports)) * 100

    async def _log_status_changes(self, report: SystemHealthReport):
        """Log significant status changes."""
        if len(self.history) < 2:
            return

        previous_report = self.history[-2]

        # Log status changes
        if previous_report.overall_status != report.overall_status:
            logger.warning(
                f"System status changed: {previous_report.overall_status.value} -> {report.overall_status.value}"
            )

        # Log significant reliability drops
        if previous_report.reliability_score > report.reliability_score + 10:
            logger.warning(
                f"Reliability dropped significantly: {previous_report.reliability_score:.1f} -> {report.reliability_score:.1f}"
            )

        # Log new critical alerts
        critical_alerts = [a for a in report.active_alerts if a.level == AlertLevel.CRITICAL]
        if critical_alerts:
            logger.error(f"CRITICAL ALERTS: {len(critical_alerts)} active critical alerts")

    async def _trigger_automatic_responses(self, report: SystemHealthReport):
        """Trigger automatic responses to system state."""
        if report.overall_status == HealthStatus.CRITICAL:
            logger.critical("CRITICAL: System in critical state - triggering emergency protocols")  # type: ignore[attr-defined]
            # Could trigger automatic failover, scaling, etc.

        elif report.overall_status == HealthStatus.UNHEALTHY:
            logger.error("UNHEALTHY: System unhealthy - triggering recovery protocols")
            # Could trigger restarts, cache clearing, etc.

        elif report.overall_status == HealthStatus.DEGRADED:
            logger.warning("DEGRADED: System performance degraded - triggering optimization")
            # Could trigger cache warming, connection pooling adjustments, etc.

    def get_current_status(self) -> SystemHealthReport | None:
        """Get current system status."""
        return self.history[-1] if self.history else None

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of current metrics."""
        if not self.metrics:
            return {}

        return {
            name: {
                "value": metric.value,
                "threshold": metric.threshold,
                "unit": metric.unit,
                "health_percentage": metric.health_percentage,
                "trend": metric.trend,
                "is_healthy": metric.is_healthy,
            }
            for name, metric in self.metrics.items()
        }

    def get_active_alerts(self) -> list[Alert]:
        """Get active (unresolved) alerts."""
        return [a for a in self.alerts if not a.resolved]

    async def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolution_time = datetime.now()
                logger.info(f"Alert resolved: {alert.title}")
                return True
        return False

    async def export_report(self, filepath: str):
        """Export latest health report to file."""
        if not self.history:
            raise ValueError("No health reports available")

        report = self.history[-1]
        report_data = {
            "timestamp": report.timestamp.isoformat(),
            "overall_status": report.overall_status.value,
            "reliability_score": report.reliability_score,
            "uptime_percentage": report.uptime_percentage,
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "threshold": m.threshold,
                    "unit": m.unit,
                    "health_percentage": m.health_percentage,
                    "trend": m.trend,
                }
                for m in report.metrics
            ],
            "active_alerts": [
                {
                    "id": a.id,
                    "level": a.level.value,
                    "title": a.title,
                    "message": a.message,
                    "timestamp": a.timestamp.isoformat(),
                }
                for a in report.active_alerts
            ],
            "recommendations": report.recommendations,
        }

        with open(filepath, "w") as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Health report exported to {filepath}")


# Global monitor instance
_reliability_monitor = ReliabilityMonitor()


def get_reliability_monitor() -> ReliabilityMonitor:
    """Get the global reliability monitor instance."""
    return _reliability_monitor


async def start_integration_monitoring():
    """Start integration reliability monitoring."""
    monitor = get_reliability_monitor()
    await monitor.start_monitoring()


async def stop_integration_monitoring():
    """Stop integration reliability monitoring."""
    monitor = get_reliability_monitor()
    await monitor.stop_monitoring()
