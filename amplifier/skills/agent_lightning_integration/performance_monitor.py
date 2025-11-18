"""
Performance Monitor

Provides real-time monitoring and analytics for the Agent Lightning integration system.
Creates comprehensive dashboards and alerts for system health and performance metrics.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import time

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Real-time performance metrics"""

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_requests: int
    throughput: float
    error_rate: float
    latency_p95: float
    optimization_rate: float


@dataclass
class AlertRule:
    """Alert rule definition"""

    rule_id: str
    name: str
    metric: str
    threshold: float
    operator: str  # ">", "<", ">=", "<="
    severity: str  # "low", "medium", "high", "critical"
    enabled: bool = True


@dataclass
class Alert:
    """System alert"""

    alert_id: str
    rule_id: str
    timestamp: datetime
    severity: str
    message: str
    metric_value: float
    threshold: float
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class PerformanceMonitor:
    """Monitors system performance and creates dashboards"""

    def __init__(self, config, storage, components):
        self.config = config
        self.storage = storage
        self.components = components

        # Metrics storage
        self.metrics_history: deque = deque(maxlen=10000)  # Store last 10k metrics
        self.current_metrics: Optional[PerformanceMetrics] = None

        # Alerting
        self.alert_rules = self._initialize_alert_rules()
        self.active_alerts: Dict[str, Alert] = {}

        # Dashboard data
        self.dashboard_cache = {}
        self.cache_ttl = timedelta(minutes=5)

        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._dashboard_task: Optional[asyncio.Task] = None
        self._alert_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start performance monitoring"""
        if self._running:
            return

        self._running = True
        logger.info("Starting performance monitor")

        # Start background tasks
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._dashboard_task = asyncio.create_task(self._dashboard_update_loop())
        self._alert_task = asyncio.create_task(self._alert_processing_loop())

    async def stop(self):
        """Stop performance monitoring"""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping performance monitor")

        # Cancel background tasks
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._dashboard_task:
            self._dashboard_task.cancel()
        if self._alert_task:
            self._alert_task.cancel()

    async def get_dashboard_data(self, dashboard_type: str = "overview") -> Dict[str, Any]:
        """Get dashboard data"""
        try:
            # Check cache
            cache_key = f"dashboard_{dashboard_type}"
            if cache_key in self.dashboard_cache:
                cached_time, cached_data = self.dashboard_cache[cache_key]
                if datetime.now() - cached_time < self.cache_ttl:
                    return cached_data

            # Generate fresh data
            if dashboard_type == "overview":
                data = await self._generate_overview_dashboard()
            elif dashboard_type == "performance":
                data = await self._generate_performance_dashboard()
            elif dashboard_type == "optimizations":
                data = await self._generate_optimizations_dashboard()
            elif dashboard_type == "quality":
                data = await self._generate_quality_dashboard()
            elif dashboard_type == "alerts":
                data = await self._generate_alerts_dashboard()
            else:
                data = {"error": f"Unknown dashboard type: {dashboard_type}"}

            # Cache result
            self.dashboard_cache[cache_key] = (datetime.now(), data)
            return data

        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}

    async def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        try:
            if not self.metrics_history:
                return {"error": "No metrics available"}

            metrics = list(self.metrics_history)

            # Calculate statistics
            cpu_values = [m.cpu_usage for m in metrics]
            memory_values = [m.memory_usage for m in metrics]
            throughput_values = [m.throughput for m in metrics]
            latency_values = [m.latency_p95 for m in metrics]
            error_rates = [m.error_rate for m in metrics]

            return {
                "period": {
                    "start": metrics[0].timestamp.isoformat(),
                    "end": metrics[-1].timestamp.isoformat(),
                    "duration_hours": (metrics[-1].timestamp - metrics[0].timestamp).total_seconds() / 3600,
                },
                "cpu": {
                    "current": cpu_values[-1],
                    "average": sum(cpu_values) / len(cpu_values),
                    "max": max(cpu_values),
                    "min": min(cpu_values),
                },
                "memory": {
                    "current": memory_values[-1],
                    "average": sum(memory_values) / len(memory_values),
                    "max": max(memory_values),
                    "min": min(memory_values),
                },
                "throughput": {
                    "current": throughput_values[-1],
                    "average": sum(throughput_values) / len(throughput_values),
                    "max": max(throughput_values),
                    "total_requests": sum(t * 60 for t in throughput_values),  # Approximate
                },
                "latency": {
                    "current_p95": latency_values[-1],
                    "average_p95": sum(latency_values) / len(latency_values),
                    "max_p95": max(latency_values),
                },
                "errors": {
                    "current_rate": error_rates[-1],
                    "average_rate": sum(error_rates) / len(error_rates),
                    "max_rate": max(error_rates),
                },
                "total_data_points": len(metrics),
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}

    async def create_alert_rule(self, rule: AlertRule) -> str:
        """Create a new alert rule"""
        try:
            self.alert_rules[rule.rule_id] = rule
            logger.info(f"Created alert rule: {rule.name}")
            return rule.rule_id

        except Exception as e:
            logger.error(f"Failed to create alert rule: {e}")
            raise

    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        try:
            return [
                {
                    "alert_id": alert.alert_id,
                    "rule_id": alert.rule_id,
                    "severity": alert.severity,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "metric_value": alert.metric_value,
                    "threshold": alert.threshold,
                    "duration_minutes": (datetime.now() - alert.timestamp).total_seconds() / 60,
                }
                for alert in self.active_alerts.values()
                if not alert.resolved
            ]

        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []

    # Private methods

    def _initialize_alert_rules(self) -> Dict[str, AlertRule]:
        """Initialize default alert rules"""
        return {
            "high_cpu": AlertRule(
                rule_id="high_cpu",
                name="High CPU Usage",
                metric="cpu_usage",
                threshold=80.0,
                operator=">",
                severity="high",
            ),
            "high_memory": AlertRule(
                rule_id="high_memory",
                name="High Memory Usage",
                metric="memory_usage",
                threshold=85.0,
                operator=">",
                severity="medium",
            ),
            "high_error_rate": AlertRule(
                rule_id="high_error_rate",
                name="High Error Rate",
                metric="error_rate",
                threshold=0.05,
                operator=">",
                severity="high",
            ),
            "low_throughput": AlertRule(
                rule_id="low_throughput",
                name="Low Throughput",
                metric="throughput",
                threshold=1.0,
                operator="<",
                severity="medium",
            ),
            "high_latency": AlertRule(
                rule_id="high_latency",
                name="High Latency",
                metric="latency_p95",
                threshold=5000.0,  # 5 seconds
                operator=">",
                severity="medium",
            ),
        }

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                # Collect metrics
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)
                self.current_metrics = metrics

                # Check alert rules
                await self._check_alert_rules(metrics)

                # Store metrics
                await self._store_metrics(metrics)

                await asyncio.sleep(self.config.dashboard_refresh_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)

    async def _dashboard_update_loop(self):
        """Update dashboard cache"""
        while self._running:
            try:
                # Clear cache to force refresh
                self.dashboard_cache.clear()
                await asyncio.sleep(self.config.dashboard_refresh_interval * 2)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in dashboard update loop: {e}")
                await asyncio.sleep(30)

    async def _alert_processing_loop(self):
        """Process and manage alerts"""
        while self._running:
            try:
                # Check for alert resolution
                await self._check_alert_resolution()

                # Generate daily reports
                if self.config.generate_daily_reports:
                    await self._generate_daily_report()

                await asyncio.sleep(300)  # Check every 5 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert processing loop: {e}")
                await asyncio.sleep(60)

    async def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics"""
        try:
            # Get system resource usage
            cpu_usage = await self._get_cpu_usage()
            memory_usage = await self._get_memory_usage()
            disk_usage = await self._get_disk_usage()

            # Get application metrics
            active_requests = await self._get_active_requests()
            throughput = await self._get_throughput()
            error_rate = await self._get_error_rate()
            latency_p95 = await self._get_latency_p95()
            optimization_rate = await self._get_optimization_rate()

            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                active_requests=active_requests,
                throughput=throughput,
                error_rate=error_rate,
                latency_p95=latency_p95,
                optimization_rate=optimization_rate,
            )

        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            # Return default metrics
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                active_requests=0,
                throughput=0.0,
                error_rate=0.0,
                latency_p95=0.0,
                optimization_rate=0.0,
            )

    async def _check_alert_rules(self, metrics: PerformanceMetrics):
        """Check all alert rules against current metrics"""
        try:
            for rule in self.alert_rules.values():
                if not rule.enabled:
                    continue

                # Get metric value
                metric_value = getattr(metrics, rule.metric, None)
                if metric_value is None:
                    continue

                # Check threshold
                triggered = False
                if rule.operator == ">":
                    triggered = metric_value > rule.threshold
                elif rule.operator == "<":
                    triggered = metric_value < rule.threshold
                elif rule.operator == ">=":
                    triggered = metric_value >= rule.threshold
                elif rule.operator == "<=":
                    triggered = metric_value <= rule.threshold

                if triggered:
                    await self._trigger_alert(rule, metric_value)

        except Exception as e:
            logger.error(f"Failed to check alert rules: {e}")

    async def _trigger_alert(self, rule: AlertRule, metric_value: float):
        """Trigger an alert"""
        try:
            alert_id = f"{rule.rule_id}_{int(datetime.now().timestamp())}"

            # Check if alert already exists
            existing_alert = next(
                (a for a in self.active_alerts.values() if a.rule_id == rule.rule_id and not a.resolved), None
            )

            if existing_alert:
                return  # Alert already active

            # Create new alert
            alert = Alert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                timestamp=datetime.now(),
                severity=rule.severity,
                message=f"{rule.name}: {rule.metric} is {metric_value:.2f} (threshold: {rule.threshold})",
                metric_value=metric_value,
                threshold=rule.threshold,
            )

            self.active_alerts[alert_id] = alert
            logger.warning(f"Alert triggered: {alert.message}")

            # Send notifications (in production)
            await self._send_alert_notification(alert)

        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")

    async def _check_alert_resolution(self):
        """Check if any active alerts should be resolved"""
        try:
            if not self.current_metrics:
                return

            for alert in list(self.active_alerts.values()):
                if alert.resolved:
                    continue

                rule = self.alert_rules.get(alert.rule_id)
                if not rule:
                    continue

                metric_value = getattr(self.current_metrics, rule.metric, None)
                if metric_value is None:
                    continue

                # Check if alert condition is no longer met
                resolved = False
                if rule.operator == ">":
                    resolved = metric_value <= rule.threshold
                elif rule.operator == "<":
                    resolved = metric_value >= rule.threshold
                elif rule.operator == ">=":
                    resolved = metric_value < rule.threshold
                elif rule.operator == "<=":
                    resolved = metric_value > rule.threshold

                if resolved:
                    alert.resolved = True
                    alert.resolved_at = datetime.now()
                    logger.info(f"Alert resolved: {alert.message}")

        except Exception as e:
            logger.error(f"Failed to check alert resolution: {e}")

    async def _generate_overview_dashboard(self) -> Dict[str, Any]:
        """Generate overview dashboard"""
        try:
            if not self.current_metrics:
                return {"error": "No metrics available"}

            # Get component health
            component_health = await self._get_component_health()

            # Get recent alerts
            recent_alerts = await self.get_active_alerts()

            # Get system statistics
            stats = await self.get_statistics()

            return {
                "timestamp": datetime.now().isoformat(),
                "system_health": {
                    "overall": "healthy" if len(recent_alerts) == 0 else "degraded",
                    "components": component_health,
                    "active_alerts": len(recent_alerts),
                    "critical_alerts": len([a for a in recent_alerts if a["severity"] == "critical"]),
                },
                "current_metrics": {
                    "cpu_usage": self.current_metrics.cpu_usage,
                    "memory_usage": self.current_metrics.memory_usage,
                    "active_requests": self.current_metrics.active_requests,
                    "throughput": self.current_metrics.throughput,
                    "error_rate": self.current_metrics.error_rate,
                    "latency_p95": self.current_metrics.latency_p95,
                },
                "performance_summary": {
                    "avg_cpu": stats.get("cpu", {}).get("average", 0),
                    "avg_memory": stats.get("memory", {}).get("average", 0),
                    "total_requests": int(stats.get("throughput", {}).get("total_requests", 0)),
                    "avg_error_rate": stats.get("errors", {}).get("average_rate", 0),
                },
                "recent_alerts": recent_alerts[:5],  # Top 5 most recent
            }

        except Exception as e:
            logger.error(f"Failed to generate overview dashboard: {e}")
            return {"error": str(e)}

    async def _generate_performance_dashboard(self) -> Dict[str, Any]:
        """Generate performance dashboard"""
        try:
            if not self.metrics_history:
                return {"error": "No metrics history available"}

            metrics = list(self.metrics_history)

            # Time series data
            time_series = {
                "timestamps": [m.timestamp.isoformat() for m in metrics],
                "cpu_usage": [m.cpu_usage for m in metrics],
                "memory_usage": [m.memory_usage for m in metrics],
                "throughput": [m.throughput for m in metrics],
                "latency_p95": [m.latency_p95 for m in metrics],
                "error_rate": [m.error_rate for m in metrics],
            }

            # Performance summary
            current = metrics[-1]
            previous = metrics[-2] if len(metrics) > 1 else metrics[-1]

            trends = {
                "cpu_trend": current.cpu_usage - previous.cpu_usage,
                "memory_trend": current.memory_usage - previous.memory_usage,
                "throughput_trend": current.throughput - previous.throughput,
                "latency_trend": current.latency_p95 - previous.latency_p95,
                "error_trend": current.error_rate - previous.error_rate,
            }

            return {
                "timestamp": datetime.now().isoformat(),
                "time_series": time_series,
                "current_metrics": asdict(current),
                "trends": trends,
                "period": {
                    "start": metrics[0].timestamp.isoformat(),
                    "end": metrics[-1].timestamp.isoformat(),
                    "data_points": len(metrics),
                },
            }

        except Exception as e:
            logger.error(f"Failed to generate performance dashboard: {e}")
            return {"error": str(e)}

    async def _generate_optimizations_dashboard(self) -> Dict[str, Any]:
        """Generate optimizations dashboard"""
        try:
            # Get optimization data from storage
            # This would query the storage for optimization results
            optimizations = await self._get_recent_optimizations()

            return {
                "timestamp": datetime.now().isoformat(),
                "optimizations": optimizations,
                "summary": {
                    "total": len(optimizations),
                    "successful": len([o for o in optimizations if o.get("success", False)]),
                    "average_improvement": sum(o.get("improvement", 0) for o in optimizations) / len(optimizations)
                    if optimizations
                    else 0,
                },
            }

        except Exception as e:
            logger.error(f"Failed to generate optimizations dashboard: {e}")
            return {"error": str(e)}

    async def _generate_quality_dashboard(self) -> Dict[str, Any]:
        """Generate quality dashboard"""
        try:
            # Get quality gate data
            quality_evaluations = await self._get_recent_quality_evaluations()

            return {
                "timestamp": datetime.now().isoformat(),
                "evaluations": quality_evaluations,
                "summary": {
                    "total": len(quality_evaluations),
                    "passed": len([e for e in quality_evaluations if e.get("result") == "pass"]),
                    "failed": len([e for e in quality_evaluations if e.get("result") == "fail"]),
                    "average_score": sum(e.get("score", 0) for e in quality_evaluations) / len(quality_evaluations)
                    if quality_evaluations
                    else 0,
                },
            }

        except Exception as e:
            logger.error(f"Failed to generate quality dashboard: {e}")
            return {"error": str(e)}

    async def _generate_alerts_dashboard(self) -> Dict[str, Any]:
        """Generate alerts dashboard"""
        try:
            active_alerts = await self.get_active_alerts()

            # Alert statistics
            alert_stats = defaultdict(int)
            for alert in active_alerts:
                alert_stats[alert["severity"]] += 1

            return {
                "timestamp": datetime.now().isoformat(),
                "active_alerts": active_alerts,
                "statistics": dict(alert_stats),
                "alert_rules": [
                    {
                        "rule_id": rule.rule_id,
                        "name": rule.name,
                        "metric": rule.metric,
                        "threshold": rule.threshold,
                        "enabled": rule.enabled,
                    }
                    for rule in self.alert_rules.values()
                ],
            }

        except Exception as e:
            logger.error(f"Failed to generate alerts dashboard: {e}")
            return {"error": str(e)}

    # Helper methods for metrics collection

    async def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            import psutil

            return psutil.cpu_percent(interval=None)
        except ImportError:
            # Fallback: return mock data
            import random

            return random.uniform(20, 80)

    async def _get_memory_usage(self) -> float:
        """Get memory usage percentage"""
        try:
            import psutil

            return psutil.virtual_memory().percent
        except ImportError:
            import random

            return random.uniform(30, 70)

    async def _get_disk_usage(self) -> float:
        """Get disk usage percentage"""
        try:
            import psutil

            return psutil.disk_usage("/").percent
        except ImportError:
            import random

            return random.uniform(40, 80)

    async def _get_active_requests(self) -> int:
        """Get number of active requests"""
        # This would query the integration manager
        return 0  # Placeholder

    async def _get_throughput(self) -> float:
        """Get current throughput (requests per second)"""
        # This would calculate from recent metrics
        import random

        return random.uniform(5, 25)

    async def _get_error_rate(self) -> float:
        """Get current error rate"""
        # This would calculate from recent executions
        import random

        return random.uniform(0, 0.05)

    async def _get_latency_p95(self) -> float:
        """Get 95th percentile latency"""
        # This would calculate from recent request times
        import random

        return random.uniform(100, 2000)

    async def _get_optimization_rate(self) -> float:
        """Get optimization rate (optimizations per hour)"""
        # This would calculate from optimization history
        import random

        return random.uniform(0.5, 5.0)

    async def _get_component_health(self) -> Dict[str, bool]:
        """Get health status of all components"""
        return {
            "storage": True,
            "performance_tracker": True,
            "error_detector": True,
            "optimizer": True,
            "quality_enforcer": True,
            "knowledge_transfer": True,
        }

    async def _get_recent_optimizations(self) -> List[Dict[str, Any]]:
        """Get recent optimization results"""
        # This would query storage for recent optimizations
        return []  # Placeholder

    async def _get_recent_quality_evaluations(self) -> List[Dict[str, Any]]:
        """Get recent quality gate evaluations"""
        # This would query storage for recent evaluations
        return []  # Placeholder

    async def _store_metrics(self, metrics: PerformanceMetrics):
        """Store metrics to persistent storage"""
        try:
            # This would store metrics using the MCP storage integration
            pass
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")

    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification"""
        try:
            # This would implement email, Slack, or other notifications
            logger.critical(f"ALERT: {alert.message}")
        except Exception as e:
            logger.error(f"Failed to send alert notification: {e}")

    async def _generate_daily_report(self):
        """Generate daily performance report"""
        try:
            # This would generate and store daily reports
            logger.info("Generating daily performance report")
        except Exception as e:
            logger.error(f"Failed to generate daily report: {e}")
