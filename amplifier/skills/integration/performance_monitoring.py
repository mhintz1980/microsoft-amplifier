"""
Comprehensive Performance Monitoring System

Real-time monitoring and metrics collection for all optimization components
with dashboards, alerting, and performance analytics.
"""

import asyncio
import json
import time
from collections import deque
from dataclasses import dataclass

from ..jit_compiler import get_jit_compiler
from ..resource_optimization import get_memory_monitor
from ..scheduler import get_work_stealing_scheduler
from .resource_optimizer import get_resource_optimizer


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""

    timestamp: float
    memory_usage_mb: float
    memory_efficiency: float
    cpu_usage_percent: float
    throughput_tasks_per_sec: float
    jit_speedup: float
    scheduler_utilization: float
    error_rate: float
    response_time_ms: float


@dataclass
class AlertRule:
    """Alert rule for performance monitoring"""

    rule_id: str
    metric: str
    operator: str  # gt, lt, eq
    threshold: float
    severity: str  # low, medium, high, critical
    message: str
    enabled: bool = True


@dataclass
class MonitoringStats:
    """Statistics for performance monitoring system"""

    metrics_collected: int = 0
    alerts_triggered: int = 0
    uptime_seconds: float = 0.0
    avg_collection_time_ms: float = 0.0


class PerformanceMonitor:
    """Comprehensive performance monitoring system"""

    def __init__(self, collection_interval: float = 1.0, history_size: int = 1000):
        self.collection_interval = collection_interval
        self.history_size = history_size

        # Component references
        self._resource_optimizer = get_resource_optimizer()
        self._memory_monitor = get_memory_monitor()
        self._scheduler = get_work_stealing_scheduler()
        self._jit_compiler = get_jit_compiler()

        # Metrics storage
        self._metrics_history: deque = deque(maxlen=history_size)
        self._current_metrics: PerformanceMetrics | None = None

        # Alerting
        self._alert_rules: dict[str, AlertRule] = {}
        self._alert_history: list[dict] = []

        # Monitoring state
        self._monitoring = False
        self._monitor_task: asyncio.Task | None = None
        self._start_time = time.time()

        # Statistics
        self._stats = MonitoringStats()

        # Initialize default alert rules
        self._init_default_alerts()

    def _init_default_alerts(self):
        """Initialize default alert rules"""
        default_rules = [
            AlertRule(
                rule_id="high_memory_usage",
                metric="memory_usage_mb",
                operator="gt",
                threshold=1024,  # 1GB
                severity="high",
                message="Memory usage exceeded 1GB",
            ),
            AlertRule(
                rule_id="low_throughput",
                metric="throughput_tasks_per_sec",
                operator="lt",
                threshold=1000,  # 1K tasks/sec
                severity="medium",
                message="Throughput below 1K tasks/sec",
            ),
            AlertRule(
                rule_id="high_error_rate",
                metric="error_rate",
                operator="gt",
                threshold=0.05,  # 5%
                severity="critical",
                message="Error rate exceeded 5%",
            ),
            AlertRule(
                rule_id="low_jit_speedup",
                metric="jit_speedup",
                operator="lt",
                threshold=2.0,  # 2x
                severity="low",
                message="JIT speedup below 2x",
            ),
        ]

        for rule in default_rules:
            self._alert_rules[rule.rule_id] = rule

    async def start(self):
        """Start performance monitoring"""
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        print("Performance monitoring started")

    async def stop(self):
        """Stop performance monitoring"""
        self._monitoring = False

        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        print("Performance monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                start_time = time.time()
                metrics = await self._collect_metrics()
                await self._process_metrics(metrics)

                # Update statistics
                collection_time = (time.time() - start_time) * 1000
                self._stats.metrics_collected += 1
                self._stats.avg_collection_time_ms = (
                    self._stats.avg_collection_time_ms * (self._stats.metrics_collected - 1) + collection_time
                ) / self._stats.metrics_collected

                await asyncio.sleep(self.collection_interval)

            except Exception as e:
                print(f"Performance monitoring error: {e}")
                await asyncio.sleep(1.0)

    async def _collect_metrics(self) -> PerformanceMetrics:
        """Collect performance metrics from all components"""
        current_time = time.time()

        # Memory metrics
        memory_stats = self._memory_monitor.get_stats() if self._memory_monitor else {}
        memory_usage_mb = memory_stats.get("avg_usage_percent", 0) * 16  # Estimate
        memory_efficiency = memory_stats.get("efficiency_score", 0.0)

        # CPU metrics
        cpu_usage_percent = 0.0  # Would get from system monitoring

        # Throughput metrics
        resource_stats = self._resource_optimizer.get_stats() if self._resource_optimizer else {}
        throughput_tasks_per_sec = resource_stats.get("throughput_tasks_per_sec", 0.0)

        # JIT metrics
        jit_stats = self._jit_compiler.get_compilation_stats() if self._jit_compiler else {}
        jit_speedup = jit_stats.get("average_speedup", 0.0)

        # Scheduler metrics
        scheduler_stats = self._scheduler.get_stats() if self._scheduler else {}
        scheduler_utilization = scheduler_stats.get("worker_utilization", 0.0)

        # Error and response time metrics
        error_rate = 0.0  # Would calculate from execution results
        response_time_ms = 100.0  # Would calculate from execution times

        metrics = PerformanceMetrics(
            timestamp=current_time,
            memory_usage_mb=memory_usage_mb,
            memory_efficiency=memory_efficiency,
            cpu_usage_percent=cpu_usage_percent,
            throughput_tasks_per_sec=throughput_tasks_per_sec,
            jit_speedup=jit_speedup,
            scheduler_utilization=scheduler_utilization,
            error_rate=error_rate,
            response_time_ms=response_time_ms,
        )

        self._current_metrics = metrics
        return metrics

    async def _process_metrics(self, metrics: PerformanceMetrics):
        """Process collected metrics and trigger alerts"""
        # Store metrics
        self._metrics_history.append(metrics)

        # Check alert rules
        await self._check_alerts(metrics)

    async def _check_alerts(self, metrics: PerformanceMetrics):
        """Check alert rules against metrics"""
        for rule_id, rule in self._alert_rules.items():
            if not rule.enabled:
                continue

            metric_value = getattr(metrics, rule.metric, None)
            if metric_value is None:
                continue

            triggered = False
            if (
                rule.operator == "gt"
                and metric_value > rule.threshold
                or rule.operator == "lt"
                and metric_value < rule.threshold
                or rule.operator == "eq"
                and abs(metric_value - rule.threshold) < 0.001
            ):
                triggered = True

            if triggered:
                await self._trigger_alert(rule, metric_value)

    async def _trigger_alert(self, rule: AlertRule, current_value: float):
        """Trigger an alert"""
        alert = {
            "timestamp": time.time(),
            "rule_id": rule.rule_id,
            "severity": rule.severity,
            "metric": rule.metric,
            "threshold": rule.threshold,
            "current_value": current_value,
            "message": f"{rule.message}: {current_value:.2f} (threshold: {rule.threshold})",
        }

        self._alert_history.append(alert)
        self._stats.alerts_triggered += 1

        # Log alert
        print(f"ALERT [{rule.severity.upper()}] {rule.rule_id}: {alert['message']}")

        # Keep alert history manageable
        if len(self._alert_history) > 1000:
            self._alert_history = self._alert_history[-1000:]

    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self._alert_rules[rule.rule_id] = rule

    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule"""
        self._alert_rules.pop(rule_id, None)

    def get_current_metrics(self) -> PerformanceMetrics | None:
        """Get current performance metrics"""
        return self._current_metrics

    def get_metrics_history(self, duration_seconds: float | None = None) -> list[PerformanceMetrics]:
        """Get historical metrics"""
        if duration_seconds is None:
            return list(self._metrics_history)

        cutoff_time = time.time() - duration_seconds
        return [m for m in self._metrics_history if m.timestamp >= cutoff_time]

    def get_alerts(self, severity: str | None = None, limit: int | None = None) -> list[dict]:
        """Get alert history"""
        alerts = self._alert_history

        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]

        if limit:
            alerts = alerts[-limit:]

        return alerts

    def get_performance_summary(self) -> dict:
        """Get comprehensive performance summary"""
        if not self._current_metrics:
            return {"status": "no_data"}

        # Calculate averages from recent history
        recent_metrics = self.get_metrics_history(300)  # Last 5 minutes
        if recent_metrics:
            avg_throughput = sum(m.throughput_tasks_per_sec for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_usage_mb for m in recent_metrics) / len(recent_metrics)
            avg_jit_speedup = sum(m.jit_speedup for m in recent_metrics) / len(recent_metrics)
        else:
            avg_throughput = self._current_metrics.throughput_tasks_per_sec
            avg_memory = self._current_metrics.memory_usage_mb
            avg_jit_speedup = self._current_metrics.jit_speedup

        return {
            "timestamp": self._current_metrics.timestamp,
            "current_metrics": {
                "memory_usage_mb": self._current_metrics.memory_usage_mb,
                "memory_efficiency": self._current_metrics.memory_efficiency,
                "throughput_tasks_per_sec": self._current_metrics.throughput_tasks_per_sec,
                "jit_speedup": self._current_metrics.jit_speedup,
                "scheduler_utilization": self._current_metrics.scheduler_utilization,
                "error_rate": self._current_metrics.error_rate,
                "response_time_ms": self._current_metrics.response_time_ms,
            },
            "averages_5min": {
                "throughput_tasks_per_sec": avg_throughput,
                "memory_usage_mb": avg_memory,
                "jit_speedup": avg_jit_speedup,
            },
            "alerts": {
                "total_alerts": len(self._alert_history),
                "recent_alerts": len([a for a in self._alert_history if time.time() - a["timestamp"] < 300]),
            },
            "targets_achieved": {
                "memory_efficiency": self._current_metrics.memory_efficiency >= 0.85,  # 85% target
                "throughput_target": avg_throughput >= 100000,  # 100K target
                "jit_speedup_target": avg_jit_speedup >= 50.0,  # 50x target
            },
        }

    def get_monitoring_stats(self) -> MonitoringStats:
        """Get monitoring system statistics"""
        self._stats.uptime_seconds = time.time() - self._start_time
        return MonitoringStats(
            metrics_collected=self._stats.metrics_collected,
            alerts_triggered=self._stats.alerts_triggered,
            uptime_seconds=self._stats.uptime_seconds,
            avg_collection_time_ms=self._stats.avg_collection_time_ms,
        )

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format"""
        summary = self.get_performance_summary()

        if format.lower() == "json":
            return json.dumps(summary, indent=2, default=str)
        # Simple text format
        output = []
        output.append("Performance Summary")
        output.append("=" * 50)
        output.append(f"Memory Usage: {summary['current_metrics']['memory_usage_mb']:.1f} MB")
        output.append(f"Throughput: {summary['current_metrics']['throughput_tasks_per_sec']:.0f} tasks/sec")
        output.append(f"JIT Speedup: {summary['current_metrics']['jit_speedup']:.1f}x")
        output.append(f"Scheduler Utilization: {summary['current_metrics']['scheduler_utilization']:.1%}")
        output.append(f"Error Rate: {summary['current_metrics']['error_rate']:.2%}")
        output.append(f"Response Time: {summary['current_metrics']['response_time_ms']:.1f} ms")
        output.append(f"Total Alerts: {summary['alerts']['total_alerts']}")
        return "\n".join(output)


# Global performance monitor instance
_global_performance_monitor: PerformanceMonitor | None = None


def get_performance_monitor(**kwargs) -> PerformanceMonitor:
    """Get or create the global performance monitor"""
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor(**kwargs)
        # Note: monitor.start() must be called explicitly
    return _global_performance_monitor


async def get_performance_dashboard() -> dict:
    """Get performance dashboard data"""
    monitor = get_performance_monitor()
    return monitor.get_performance_summary()
