"""
Training Monitoring and Evaluation System for Agent Lightning.

This module provides comprehensive monitoring, evaluation, and visualization
capabilities for training processes, including real-time metrics tracking,
performance analysis, and automated alerting.
"""

import asyncio
import contextlib
import json
import time
from collections import defaultdict
from collections import deque
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Any
from typing import Union

import numpy as np
from pydantic import BaseModel

from ..store.sqlite_store import SQLiteLightningStore
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TrainingAlert:
    """Alert for training monitoring."""

    alert_id: str
    session_id: str
    alert_type: str
    severity: str  # info, warning, error, critical
    message: str
    timestamp: datetime
    metrics: dict[str, float] = field(default_factory=dict)
    resolved: bool = False
    resolution_time: datetime | None = None


@dataclass
class PerformanceMetrics:
    """Performance metrics for a training session."""

    session_id: str
    timestamp: datetime
    epoch: int
    step: int
    loss: float
    accuracy: float
    learning_rate: float
    batch_size: int
    gpu_utilization: float | None = None
    memory_usage: float | None = None
    training_time: float | None = None


class AlertRule(BaseModel):
    """Rule for generating training alerts."""

    name: str
    condition: str  # Python expression
    severity: str
    message_template: str
    enabled: bool = True
    cooldown_minutes: int = 5


class MetricsAggregator:
    """Aggregates and processes training metrics."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.session_metrics: dict[str, list[PerformanceMetrics]] = defaultdict(list)

    def add_metrics(self, metrics: PerformanceMetrics):
        """Add new metrics to the aggregator."""
        self.metrics_history[metrics.session_id].append(metrics)
        self.session_metrics[metrics.session_id].append(metrics)

    def get_recent_metrics(self, session_id: str, count: int = 10) -> list[PerformanceMetrics]:
        """Get recent metrics for a session."""
        history = self.metrics_history[session_id]
        return list(history)[-count:]

    def get_session_summary(self, session_id: str) -> dict[str, Any]:
        """Get summary statistics for a session."""
        metrics = self.session_metrics[session_id]
        if not metrics:
            return {}

        losses = [m.loss for m in metrics]
        accuracies = [m.accuracy for m in metrics]

        return {
            "session_id": session_id,
            "total_epochs": len(metrics),
            "current_epoch": metrics[-1].epoch if metrics else 0,
            "best_loss": min(losses),
            "latest_loss": losses[-1] if losses else 0,
            "best_accuracy": max(accuracies),
            "latest_accuracy": accuracies[-1] if accuracies else 0,
            "loss_trend": self._compute_trend(losses[-10:]) if len(losses) >= 2 else 0,
            "accuracy_trend": self._compute_trend(accuracies[-10:]) if len(accuracies) >= 2 else 0,
            "training_duration": (metrics[-1].timestamp - metrics[0].timestamp).total_seconds()
            if len(metrics) > 1
            else 0,
            "average_epoch_time": np.mean([m.training_time for m in metrics if m.training_time])
            if any(m.training_time for m in metrics)
            else None,
        }

    def _compute_trend(self, values: list[float]) -> float:
        """Compute linear trend (slope) of values."""
        if len(values) < 2:
            return 0.0

        x = np.arange(len(values))
        y = np.array(values)
        slope = np.polyfit(x, y, 1)[0]
        return slope

    def get_cross_session_comparison(self, session_ids: list[str]) -> dict[str, Any]:
        """Compare performance across multiple sessions."""
        comparisons = {}

        for session_id in session_ids:
            summary = self.get_session_summary(session_id)
            if summary:
                comparisons[session_id] = summary

        if not comparisons:
            return {}

        # Compute rankings
        best_accuracy_session = max(comparisons.items(), key=lambda x: x[1]["best_accuracy"])
        best_loss_session = min(comparisons.items(), key=lambda x: x[1]["best_loss"])
        fastest_session = min(comparisons.items(), key=lambda x: x[1]["average_epoch_time"] or float("inf"))

        return {
            "sessions": comparisons,
            "rankings": {
                "best_accuracy": {
                    "session": best_accuracy_session[0],
                    "value": best_accuracy_session[1]["best_accuracy"],
                },
                "best_loss": {"session": best_loss_session[0], "value": best_loss_session[1]["best_loss"]},
                "fastest_training": {"session": fastest_session[0], "value": fastest_session[1]["average_epoch_time"]},
            },
        }


class AlertManager:
    """Manages training alerts and notifications."""

    def __init__(self):
        self.alerts: dict[str, TrainingAlert] = {}
        self.alert_rules: list[AlertRule] = []
        self.alert_history: list[TrainingAlert] = []
        self.last_alert_times: dict[str, datetime] = {}

        # Initialize default alert rules
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """Initialize default alert rules."""
        default_rules = [
            AlertRule(
                name="high_loss",
                condition="metrics.loss > 2.0",
                severity="error",
                message_template="High loss detected: {metrics.loss:.4f} at epoch {metrics.epoch}",
            ),
            AlertRule(
                name="loss_plateau",
                condition="len(metrics_history) >= 10 and abs(metrics.loss - metrics_history[-10].loss) < 0.01",
                severity="warning",
                message_template="Loss plateau detected for last 10 epochs: {metrics.loss:.4f}",
            ),
            AlertRule(
                name="accuracy_decline",
                condition="len(metrics_history) >= 5 and metrics.accuracy < metrics_history[-5].accuracy",
                severity="warning",
                message_template="Accuracy declining: {metrics.accuracy:.4f} (was {metrics_history[-5].accuracy:.4f})",
            ),
            AlertRule(
                name="training_too_slow",
                condition="metrics.training_time and metrics.training_time > 300",  # 5 minutes per epoch
                severity="warning",
                message_template="Training slow: {metrics.training_time:.1f}s per epoch",
            ),
            AlertRule(
                name="low_accuracy",
                condition="metrics.epoch >= 50 and metrics.accuracy < 0.6",
                severity="error",
                message_template="Low accuracy after {metrics.epoch} epochs: {metrics.accuracy:.4f}",
            ),
            AlertRule(
                name="gpu_memory_high",
                condition="metrics.gpu_utilization and metrics.gpu_utilization > 0.95",
                severity="warning",
                message_template="High GPU utilization: {metrics.gpu_utilization:.1%}",
            ),
        ]

        self.alert_rules.extend(default_rules)

    def check_alerts(
        self, metrics: PerformanceMetrics, metrics_history: list[PerformanceMetrics]
    ) -> list[TrainingAlert]:
        """Check for alert conditions."""
        new_alerts = []

        for rule in self.alert_rules:
            if not rule.enabled:
                continue

            # Check cooldown
            cooldown_key = f"{metrics.session_id}_{rule.name}"
            if cooldown_key in self.last_alert_times:
                time_since_last = datetime.now() - self.last_alert_times[cooldown_key]
                if time_since_last < timedelta(minutes=rule.cooldown_minutes):
                    continue

            try:
                # Evaluate condition
                context = {"metrics": metrics, "metrics_history": metrics_history, "len": len, "abs": abs}

                if eval(rule.condition, {"__builtins__": {}}, context):
                    alert = TrainingAlert(
                        alert_id=f"{metrics.session_id}_{rule.name}_{int(time.time())}",
                        session_id=metrics.session_id,
                        alert_type=rule.name,
                        severity=rule.severity,
                        message=rule.message_template.format(**context),
                        timestamp=datetime.now(),
                        metrics={"loss": metrics.loss, "accuracy": metrics.accuracy, "epoch": metrics.epoch},
                    )

                    new_alerts.append(alert)
                    self.alerts[alert.alert_id] = alert
                    self.alert_history.append(alert)
                    self.last_alert_times[cooldown_key] = datetime.now()

                    logger.warning(f"Alert triggered: {alert.message}")

            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule.name}: {e}")

        return new_alerts

    def get_active_alerts(self, session_id: str | None = None) -> list[TrainingAlert]:
        """Get active (unresolved) alerts."""
        alerts = [alert for alert in self.alerts.values() if not alert.resolved]

        if session_id:
            alerts = [alert for alert in alerts if alert.session_id == session_id]

        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)

    def resolve_alert(self, alert_id: str, resolution_time: datetime | None = None) -> bool:
        """Resolve an alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            self.alerts[alert_id].resolution_time = resolution_time or datetime.now()
            logger.info(f"Resolved alert: {alert_id}")
            return True
        return False

    def get_alert_summary(self, session_id: str | None = None) -> dict[str, Any]:
        """Get summary of alerts."""
        all_alerts = list(self.alerts.values())

        if session_id:
            all_alerts = [alert for alert in all_alerts if alert.session_id == session_id]

        severity_counts = defaultdict(int)
        for alert in all_alerts:
            severity_counts[alert.severity] += 1

        recent_alerts = [alert for alert in all_alerts if alert.timestamp > datetime.now() - timedelta(hours=24)]

        return {
            "total_alerts": len(all_alerts),
            "active_alerts": len(self.get_active_alerts(session_id)),
            "severity_breakdown": dict(severity_counts),
            "recent_alerts_24h": len(recent_alerts),
            "most_common_alert": self._get_most_common_alert_type(all_alerts),
        }

    def _get_most_common_alert_type(self, alerts: list[TrainingAlert]) -> str | None:
        """Get the most common alert type."""
        if not alerts:
            return None

        type_counts = defaultdict(int)
        for alert in alerts:
            type_counts[alert.alert_type] += 1

        return max(type_counts.items(), key=lambda x: x[1])[0]


class TrainingMonitor:
    """Main training monitoring system."""

    def __init__(self, store: SQLiteLightningStore):
        self.store = store
        self.metrics_aggregator = MetricsAggregator()
        self.alert_manager = AlertManager()
        self.monitoring_active = False
        self.monitoring_task: asyncio.Task | None = None

    async def start_monitoring(self, check_interval: int = 30):
        """Start real-time monitoring."""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop(check_interval))
        logger.info("Started training monitoring")

    async def stop_monitoring(self):
        """Stop monitoring."""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.monitoring_task
        logger.info("Stopped training monitoring")

    async def _monitoring_loop(self, check_interval: int):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                await self._check_training_sessions()
                await asyncio.sleep(check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(check_interval)

    async def _check_training_sessions(self):
        """Check all active training sessions."""
        # Get running sessions
        running_sessions = await self.store.list_training_sessions(status="running")

        for session in running_sessions:
            await self._check_session(session.session_id)

    async def _check_session(self, session_id: str):
        """Check a specific training session."""
        try:
            # Get recent metrics
            recent_metrics = await self.store.get_training_metrics(session_id, last_n=50)

            if not recent_metrics:
                return

            # Convert to PerformanceMetrics
            performance_metrics = []
            for metric in recent_metrics:
                metrics_data = metric.metrics
                perf_metric = PerformanceMetrics(
                    session_id=session_id,
                    timestamp=metric.timestamp,
                    epoch=metric.epoch,
                    step=metric.step,
                    loss=metrics_data.get("loss", 0.0),
                    accuracy=metrics_data.get("accuracy", 0.0),
                    learning_rate=metrics_data.get("learning_rate", 0.0),
                    batch_size=metrics_data.get("batch_size", 0),
                    gpu_utilization=metrics_data.get("gpu_utilization"),
                    memory_usage=metrics_data.get("memory_usage"),
                    training_time=metrics_data.get("training_time"),
                )
                performance_metrics.append(perf_metric)

            # Add to aggregator
            for perf_metric in performance_metrics:
                self.metrics_aggregator.add_metrics(perf_metric)

            # Check alerts
            if len(performance_metrics) > 0:
                latest_metrics = performance_metrics[-1]
                alerts = self.alert_manager.check_alerts(latest_metrics, performance_metrics[:-1])

                # Store alerts in database
                for alert in alerts:
                    await self._store_alert(alert)

        except Exception as e:
            logger.error(f"Error checking session {session_id}: {e}")

    async def _store_alert(self, alert: TrainingAlert):
        """Store alert in database (implementation depends on schema)."""
        # This would store alerts in a database table
        # For now, just log the alert
        logger.info(f"Alert stored: {alert.alert_id} - {alert.message}")

    async def get_dashboard_data(self, session_id: str | None = None) -> dict[str, Any]:
        """Get data for monitoring dashboard."""
        if session_id:
            session_summary = self.metrics_aggregator.get_session_summary(session_id)
            recent_metrics = self.metrics_aggregator.get_recent_metrics(session_id, 20)
            active_alerts = self.alert_manager.get_active_alerts(session_id)
            alert_summary = self.alert_manager.get_alert_summary(session_id)
        else:
            # Get data for all sessions
            all_sessions = await self.store.list_training_sessions(limit=10)
            session_ids = [s.session_id for s in all_sessions]

            session_summary = {}
            recent_metrics = []
            for sid in session_ids:
                recent_metrics.extend(self.metrics_aggregator.get_recent_metrics(sid, 5))

            active_alerts = self.alert_manager.get_active_alerts()
            alert_summary = self.alert_manager.get_alert_summary()

        return {
            "session_summary": session_summary,
            "recent_metrics": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "epoch": m.epoch,
                    "loss": m.loss,
                    "accuracy": m.accuracy,
                    "learning_rate": m.learning_rate,
                }
                for m in recent_metrics
            ],
            "active_alerts": [
                {
                    "alert_id": a.alert_id,
                    "type": a.alert_type,
                    "severity": a.severity,
                    "message": a.message,
                    "timestamp": a.timestamp.isoformat(),
                }
                for a in active_alerts
            ],
            "alert_summary": alert_summary,
        }

    async def generate_training_report(self, session_id: str, output_path: Path) -> bool:
        """Generate comprehensive training report."""
        try:
            # Get session data
            session = await self.store.get_training_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return False

            # Get metrics and alerts
            session_summary = self.metrics_aggregator.get_session_summary(session_id)
            all_metrics = self.metrics_aggregator.session_metrics[session_id]
            session_alerts = [a for a in self.alert_manager.alert_history if a.session_id == session_id]

            # Generate report
            report = {
                "session_info": {
                    "session_id": session.session_id,
                    "agent_name": session.agent_name,
                    "algorithm": session.algorithm,
                    "start_time": session.start_time.isoformat(),
                    "end_time": session.end_time.isoformat() if session.end_time else None,
                    "status": session.status,
                    "config": session.config,
                },
                "performance_summary": session_summary,
                "detailed_metrics": [
                    {
                        "epoch": m.epoch,
                        "timestamp": m.timestamp.isoformat(),
                        "loss": m.loss,
                        "accuracy": m.accuracy,
                        "learning_rate": m.learning_rate,
                        "batch_size": m.batch_size,
                    }
                    for m in all_metrics
                ],
                "alerts": [
                    {
                        "alert_id": a.alert_id,
                        "type": a.alert_type,
                        "severity": a.severity,
                        "message": a.message,
                        "timestamp": a.timestamp.isoformat(),
                        "resolved": a.resolved,
                        "resolution_time": a.resolution_time.isoformat() if a.resolution_time else None,
                    }
                    for a in session_alerts
                ],
                "analysis": {
                    "convergence_epoch": self._find_convergence_epoch(all_metrics),
                    "best_performance_epoch": self._find_best_performance_epoch(all_metrics),
                    "training_stability": self._compute_training_stability(all_metrics),
                    "alert_frequency": len(session_alerts) / max(1, len(all_metrics)),
                },
            }

            # Save report
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"Training report saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generating training report: {e}")
            return False

    def _find_convergence_epoch(self, metrics: list[PerformanceMetrics]) -> int | None:
        """Find the epoch where training converged."""
        if len(metrics) < 10:
            return None

        # Look for plateau in loss
        losses = [m.loss for m in metrics]
        for i in range(10, len(losses)):
            recent_losses = losses[i - 10 : i]
            if max(recent_losses) - min(recent_losses) < 0.01:
                return metrics[i].epoch

        return None

    def _find_best_performance_epoch(self, metrics: list[PerformanceMetrics]) -> int | None:
        """Find the epoch with best performance."""
        if not metrics:
            return None

        best_metric = max(metrics, key=lambda m: m.accuracy)
        return best_metric.epoch

    def _compute_training_stability(self, metrics: list[PerformanceMetrics]) -> float:
        """Compute training stability metric."""
        if len(metrics) < 5:
            return 1.0

        accuracies = [m.accuracy for m in metrics]
        stability = 1.0 - (np.std(accuracies) / np.mean(accuracies)) if np.mean(accuracies) > 0 else 0.0
        return max(0.0, min(1.0, stability))

    async def export_metrics(
        self, session_id: str, format: str = "json", output_path: Path | None = None
    ) -> Union[str, dict]:
        """Export training metrics."""
        metrics = self.metrics_aggregator.session_metrics[session_id]

        if format == "json":
            data = [
                {
                    "epoch": m.epoch,
                    "timestamp": m.timestamp.isoformat(),
                    "loss": m.loss,
                    "accuracy": m.accuracy,
                    "learning_rate": m.learning_rate,
                    "batch_size": m.batch_size,
                    "gpu_utilization": m.gpu_utilization,
                    "memory_usage": m.memory_usage,
                }
                for m in metrics
            ]

            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    json.dump(data, f, indent=2)
                return str(output_path)
            return data

        if format == "csv":
            import csv

            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["epoch", "timestamp", "loss", "accuracy", "learning_rate", "batch_size"])
                    for m in metrics:
                        writer.writerow(
                            [m.epoch, m.timestamp.isoformat(), m.loss, m.accuracy, m.learning_rate, m.batch_size]
                        )
                return str(output_path)
            return "epoch,timestamp,loss,accuracy,learning_rate,batch_size\n" + "\n".join(
                [
                    f"{m.epoch},{m.timestamp.isoformat()},{m.loss},{m.accuracy},{m.learning_rate},{m.batch_size}"
                    for m in metrics
                ]
            )

        raise ValueError(f"Unsupported format: {format}")


class TrainingEvaluator:
    """Evaluates trained models and compares performance."""

    def __init__(self, store: SQLiteLightningStore):
        self.store = store

    async def evaluate_model(
        self, session_id: str, test_data: list[dict[str, Any]], metrics: list[str] = None
    ) -> dict[str, float]:
        """Evaluate a trained model on test data."""
        if metrics is None:
            metrics = ["accuracy", "precision", "recall", "f1_score", "loss"]

        # Get best checkpoint
        checkpoint = await self.store.get_best_checkpoint(session_id)
        if not checkpoint:
            raise ValueError(f"No checkpoint found for session {session_id}")

        # Mock evaluation (in practice, load actual model and evaluate)
        results = {}
        for metric in metrics:
            if metric == "accuracy":
                results[metric] = 0.85 + np.random.normal(0, 0.05)
            elif metric == "precision":
                results[metric] = 0.82 + np.random.normal(0, 0.03)
            elif metric == "recall":
                results[metric] = 0.88 + np.random.normal(0, 0.03)
            elif metric == "f1_score":
                results[metric] = 0.85 + np.random.normal(0, 0.02)
            elif metric == "loss":
                results[metric] = 0.3 + np.random.normal(0, 0.05)
            else:
                results[metric] = np.random.random()

        # Ensure values are in reasonable ranges
        results = {k: max(0.0, min(1.0, v)) for k, v in results.items()}

        return results

    async def compare_models(
        self, session_ids: list[str], test_data: list[dict[str, Any]], metrics: list[str] = None
    ) -> dict[str, Any]:
        """Compare multiple models."""
        if metrics is None:
            metrics = ["accuracy", "precision", "recall", "f1_score"]

        comparisons = {}
        for session_id in session_ids:
            try:
                results = await self.evaluate_model(session_id, test_data, metrics)
                comparisons[session_id] = results
            except Exception as e:
                logger.error(f"Error evaluating model {session_id}: {e}")
                comparisons[session_id] = dict.fromkeys(metrics, 0.0)

        # Compute rankings
        rankings = {}
        for metric in metrics:
            if metric == "loss":
                # Lower is better for loss
                best_session = min(comparisons.items(), key=lambda x: x[1].get(metric, float("inf")))
            else:
                # Higher is better for other metrics
                best_session = max(comparisons.items(), key=lambda x: x[1].get(metric, 0.0))

            rankings[metric] = {
                "best_session": best_session[0],
                "best_value": best_session[1].get(metric, 0.0),
                "all_values": {sid: results.get(metric, 0.0) for sid, results in comparisons.items()},
            }

        return {
            "comparisons": comparisons,
            "rankings": rankings,
            "overall_best": max(comparisons.items(), key=lambda x: np.mean(list(x[1].values())))[0]
            if comparisons
            else None,
        }

    async def generate_evaluation_report(
        self, session_id: str, test_results: dict[str, float], output_path: Path
    ) -> bool:
        """Generate evaluation report."""
        try:
            # Get session info
            session = await self.store.get_training_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return False

            # Get training metrics for comparison
            training_metrics = await self.store.get_training_metrics(session_id, last_n=100)
            final_training_metrics = training_metrics[-1].metrics if training_metrics else {}

            # Generate report
            report = {
                "model_info": {
                    "session_id": session_id,
                    "agent_name": session.agent_name,
                    "algorithm": session.algorithm,
                    "training_completed": session.end_time.isoformat() if session.end_time else None,
                },
                "test_results": test_results,
                "training_vs_test": {
                    "training_accuracy": final_training_metrics.get("accuracy", 0.0),
                    "test_accuracy": test_results.get("accuracy", 0.0),
                    "generalization_gap": abs(
                        final_training_metrics.get("accuracy", 0.0) - test_results.get("accuracy", 0.0)
                    ),
                },
                "evaluation_metadata": {
                    "test_samples": len(test_results),  # This would be actual test sample count
                    "evaluation_timestamp": datetime.now().isoformat(),
                    "metrics_computed": list(test_results.keys()),
                },
            }

            # Save report
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"Evaluation report saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generating evaluation report: {e}")
            return False
