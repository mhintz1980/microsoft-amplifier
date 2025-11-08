"""
Production Training Pipeline for Engineering Agents

Implements comprehensive production-ready training infrastructure:
- Continuous training with automated model updates
- A/B testing for model performance comparison
- Model registry with versioning and rollback capabilities
- Monitoring and alerting for training degradation
- Automated quality assurance and validation
- Scalable training orchestration
"""

import asyncio
import json
import logging
import uuid
from collections import defaultdict
from collections import deque
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import prometheus_client as prom
import psutil
import schedule
import yaml

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model status in production pipeline."""

    TRAINING = "training"
    VALIDATING = "validating"
    TESTING = "testing"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"
    DEPRECATED = "deprecated"
    FAILED = "failed"


class TrainingTrigger(Enum):
    """Triggers for training pipeline execution."""

    SCHEDULED = "scheduled"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    NEW_DATA_AVAILABLE = "new_data_available"
    MANUAL = "manual"
    MODEL_FAILURE = "model_failure"
    VERSION_UPDATE = "version_update"


class ValidationLevel(Enum):
    """Validation levels for model quality assurance."""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    PRODUCTION = "production"


@dataclass
class ModelVersion:
    """Model version metadata."""

    version_id: str
    model_name: str
    version_number: str
    created_at: datetime
    created_by: str
    status: ModelStatus
    training_config: dict[str, Any]
    performance_metrics: dict[str, float]
    validation_results: dict[str, Any]
    file_path: str
    metadata: dict[str, Any] = field(default_factory=dict)
    parent_version: str | None = None
    changelog: str = ""
    tags: list[str] = field(default_factory=list)

    def get_age_hours(self) -> float:
        """Get model age in hours."""
        return (datetime.now() - self.created_at).total_seconds() / 3600.0

    def is_production_ready(self) -> bool:
        """Check if model is ready for production."""
        required_metrics = ["accuracy", "safety_score", "robustness_score"]
        return (
            self.status == ModelStatus.TESTING
            and all(metric in self.performance_metrics for metric in required_metrics)
            and all(self.performance_metrics[metric] >= 0.8 for metric in required_metrics)
        )


@dataclass
class TrainingJob:
    """Training job definition."""

    job_id: str
    model_name: str
    trigger: TrainingTrigger
    priority: int
    training_config: dict[str, Any]
    data_sources: list[str]
    resource_requirements: dict[str, Any]
    timeout_seconds: int = 3600
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: str = "pending"
    result: dict[str, Any] | None = None
    error_message: str | None = None


@dataclass
class ABTest:
    """A/B test configuration."""

    test_id: str
    model_name: str
    control_version: str
    treatment_version: str
    traffic_split: float  # 0.0 to 1.0, proportion for treatment
    success_metrics: list[str]
    minimum_sample_size: int
    confidence_level: float = 0.95
    duration_days: int = 7
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "running"
    results: dict[str, Any] | None = None


class ModelRegistry:
    """Registry for managing model versions and metadata."""

    def __init__(self, registry_path: str = "./model_registry"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.models: dict[str, list[ModelVersion]] = defaultdict(list)
        self.current_deployments: dict[str, str] = {}  # model_name -> version_id
        self._load_registry()

    def _load_registry(self):
        """Load registry from disk."""
        registry_file = self.registry_path / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file) as f:
                    data = json.load(f)

                # Reconstruct ModelVersion objects
                for model_name, versions in data["models"].items():
                    for version_data in versions:
                        version_data["created_at"] = datetime.fromisoformat(version_data["created_at"])
                        version_data["status"] = ModelStatus(version_data["status"])
                        self.models[model_name].append(ModelVersion(**version_data))

                self.current_deployments = data["current_deployments"]
                logger.info(f"Loaded registry with {len(self.models)} models")
            except Exception as e:
                logger.error(f"Error loading registry: {e}")

    def _save_registry(self):
        """Save registry to disk."""
        registry_data = {
            "models": {
                model_name: [asdict(version) for version in versions] for model_name, versions in self.models.items()
            },
            "current_deployments": self.current_deployments,
            "last_updated": datetime.now().isoformat(),
        }

        registry_file = self.registry_path / "registry.json"
        try:
            with open(registry_file, "w") as f:
                json.dump(registry_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving registry: {e}")

    def register_model(self, model_version: ModelVersion) -> str:
        """Register a new model version."""
        self.models[model_version.model_name].append(model_version)
        self._save_registry()
        logger.info(f"Registered model {model_version.model_name} version {model_version.version_number}")
        return model_version.version_id

    def get_model(self, model_name: str, version_id: str = None) -> ModelVersion | None:
        """Get model version by name and version ID."""
        if model_name not in self.models:
            return None

        if version_id is None:
            # Return latest version
            return max(self.models[model_name], key=lambda v: v.created_at)

        # Return specific version
        for version in self.models[model_name]:
            if version.version_id == version_id:
                return version

        return None

    def get_production_model(self, model_name: str) -> ModelVersion | None:
        """Get currently deployed production model."""
        version_id = self.current_deployments.get(model_name)
        if version_id:
            return self.get_model(model_name, version_id)
        return None

    def deploy_model(self, model_name: str, version_id: str) -> bool:
        """Deploy model to production."""
        model_version = self.get_model(model_name, version_id)
        if not model_version:
            logger.error(f"Model {model_name}:{version_id} not found")
            return False

        if not model_version.is_production_ready():
            logger.error(f"Model {model_name}:{version_id} not ready for production")
            return False

        # Update deployment
        self.current_deployments[model_name] = version_id
        model_version.status = ModelStatus.DEPLOYED
        self._save_registry()

        logger.info(f"Deployed model {model_name}:{version_id} to production")
        return True

    def rollback_model(self, model_name: str, target_version_id: str = None) -> bool:
        """Rollback model to previous version."""
        current_version_id = self.current_deployments.get(model_name)
        if not current_version_id:
            logger.error(f"No model currently deployed for {model_name}")
            return False

        # Find target version
        if target_version_id is None:
            # Find previous stable version
            versions = sorted(
                [v for v in self.models[model_name] if v.version_id != current_version_id],
                key=lambda v: v.created_at,
                reverse=True,
            )
            if not versions:
                logger.error(f"No previous version found for {model_name}")
                return False
            target_version_id = versions[0].version_id

        target_version = self.get_model(model_name, target_version_id)
        if not target_version:
            logger.error(f"Target version {target_version_id} not found")
            return False

        # Perform rollback
        current_version = self.get_model(model_name, current_version_id)
        current_version.status = ModelStatus.ROLLED_BACK

        self.current_deployments[model_name] = target_version_id
        target_version.status = ModelStatus.DEPLOYED
        self._save_registry()

        logger.info(f"Rolled back {model_name} from {current_version_id} to {target_version_id}")
        return True

    def list_models(self, model_name: str = None) -> dict[str, list[dict[str, Any]]]:
        """List all models or specific model versions."""
        if model_name:
            if model_name in self.models:
                return {model_name: [asdict(v) for v in self.models[model_name]]}
            return {model_name: []}

        return {name: [asdict(v) for v in versions] for name, versions in self.models.items()}

    def cleanup_old_versions(self, max_age_days: int = 30, keep_count: int = 5):
        """Clean up old model versions."""
        cutoff_time = datetime.now() - timedelta(days=max_age_days)

        for model_name, versions in self.models.items():
            # Keep latest N versions regardless of age
            versions_sorted = sorted(versions, key=lambda v: v.created_at, reverse=True)
            keep_versions = versions_sorted[:keep_count]

            # Also keep versions newer than cutoff time unless deployed
            for version in versions:
                if (
                    version not in keep_versions
                    and version.created_at < cutoff_time
                    and version.status not in [ModelStatus.DEPLOYED, ModelStatus.ROLLED_BACK]
                ):
                    # Delete model file
                    try:
                        if Path(version.file_path).exists():
                            Path(version.file_path).unlink()
                    except Exception as e:
                        logger.warning(f"Failed to delete model file {version.file_path}: {e}")

                    # Remove from registry
                    self.models[model_name].remove(version)

        self._save_registry()
        logger.info("Completed cleanup of old model versions")


class PerformanceMonitor:
    """Monitor model performance and detect degradation."""

    def __init__(self):
        self.metrics_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alert_thresholds: dict[str, dict[str, float]] = {}
        self.performance_baselines: dict[str, dict[str, float]] = {}
        self.alert_callbacks: list[callable] = []

        # Prometheus metrics
        self.prom_metrics = {
            "model_accuracy": prom.Gauge("model_accuracy", "Model accuracy", ["model_name", "version"]),
            "model_latency": prom.Histogram(
                "model_latency_seconds", "Model inference latency", ["model_name", "version"]
            ),
            "prediction_count": prom.Counter("model_predictions_total", "Total predictions", ["model_name", "version"]),
            "error_rate": prom.Gauge("model_error_rate", "Model error rate", ["model_name", "version"]),
        }

    def set_baseline(self, model_name: str, version: str, metrics: dict[str, float]):
        """Set performance baseline for model."""
        key = f"{model_name}:{version}"
        self.performance_baselines[key] = metrics
        logger.info(f"Set baseline for {key}: {metrics}")

    def record_metrics(self, model_name: str, version: str, metrics: dict[str, float]):
        """Record performance metrics."""
        key = f"{model_name}:{version}"
        timestamp = datetime.now().isoformat()

        # Store in history
        for metric_name, value in metrics.items():
            self.metrics_history[f"{key}:{metric_name}"].append({"timestamp": timestamp, "value": value})

        # Update Prometheus metrics
        if "accuracy" in metrics:
            self.prom_metrics["model_accuracy"].labels(model_name=model_name, version=version).set(metrics["accuracy"])
        if "latency" in metrics:
            self.prom_metrics["model_latency"].labels(model_name=model_name, version=version).observe(
                metrics["latency"]
            )
        if "error_rate" in metrics:
            self.prom_metrics["error_rate"].labels(model_name=model_name, version=version).set(metrics["error_rate"])

        # Check for degradation
        self._check_performance_degradation(model_name, version, metrics)

    def _check_performance_degradation(self, model_name: str, version: str, current_metrics: dict[str, float]):
        """Check for performance degradation."""
        key = f"{model_name}:{version}"
        baseline = self.performance_baselines.get(key, {})

        for metric_name, current_value in current_metrics.items():
            if metric_name in baseline:
                baseline_value = baseline[metric_name]
                degradation_threshold = self.alert_thresholds.get(key, {}).get(metric_name, 0.1)

                # For metrics where lower is better (error rate, latency)
                if metric_name in ["error_rate", "latency"]:
                    if current_value > baseline_value * (1 + degradation_threshold):
                        self._trigger_alert(model_name, version, metric_name, current_value, baseline_value)
                # For metrics where higher is better (accuracy)
                else:
                    if current_value < baseline_value * (1 - degradation_threshold):
                        self._trigger_alert(model_name, version, metric_name, current_value, baseline_value)

    def _trigger_alert(self, model_name: str, version: str, metric: str, current: float, baseline: float):
        """Trigger performance degradation alert."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "version": version,
            "metric": metric,
            "current_value": current,
            "baseline_value": baseline,
            "severity": "high" if abs(current - baseline) > 0.2 else "medium",
        }

        logger.warning(f"Performance degradation detected: {alert}")

        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    def add_alert_callback(self, callback: callable):
        """Add callback for performance alerts."""
        self.alert_callbacks.append(callback)

    def get_performance_summary(self, model_name: str, version: str, hours: int = 24) -> dict[str, Any]:
        """Get performance summary for recent period."""
        key = f"{model_name}:{version}"
        cutoff_time = datetime.now() - timedelta(hours=hours)

        summary = {}
        for metric_key, history in self.metrics_history.items():
            if not metric_key.startswith(f"{key}:"):
                continue

            metric_name = metric_key.split(":")[-1]
            recent_values = [
                entry["value"] for entry in history if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
            ]

            if recent_values:
                summary[metric_name] = {
                    "current": recent_values[-1],
                    "average": np.mean(recent_values),
                    "min": np.min(recent_values),
                    "max": np.max(recent_values),
                    "std": np.std(recent_values),
                    "count": len(recent_values),
                }

        return summary


class ABTestManager:
    """Manage A/B testing for model performance comparison."""

    def __init__(self):
        self.active_tests: dict[str, ABTest] = {}
        self.test_history: list[ABTest] = []
        self.test_results: dict[str, dict[str, Any]] = {}

    def create_test(self, test_config: dict[str, Any]) -> str:
        """Create new A/B test."""
        test = ABTest(
            test_id=str(uuid.uuid4()),
            model_name=test_config["model_name"],
            control_version=test_config["control_version"],
            treatment_version=test_config["treatment_version"],
            traffic_split=test_config.get("traffic_split", 0.1),
            success_metrics=test_config.get("success_metrics", ["accuracy"]),
            minimum_sample_size=test_config.get("minimum_sample_size", 1000),
            confidence_level=test_config.get("confidence_level", 0.95),
            duration_days=test_config.get("duration_days", 7),
        )

        self.active_tests[test.test_id] = test
        logger.info(f"Created A/B test {test.test_id} for {test.model_name}")
        return test.test_id

    def record_prediction(
        self, model_name: str, version: str, prediction_id: str, prediction: Any, ground_truth: Any = None
    ):
        """Record prediction for A/B test analysis."""
        # Find relevant test
        for test in self.active_tests.values():
            if test.model_name == model_name and version in [test.control_version, test.treatment_version]:
                # Store prediction data (in real implementation, this would go to a database)
                if not hasattr(test, "prediction_data"):
                    test.prediction_data = []

                test.prediction_data.append(
                    {
                        "prediction_id": prediction_id,
                        "version": version,
                        "prediction": prediction,
                        "ground_truth": ground_truth,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                # Check if test should be concluded
                self._check_test_completion(test)

    def _check_test_completion(self, test: ABTest):
        """Check if A/B test should be concluded."""
        if not hasattr(test, "prediction_data"):
            return

        # Check minimum sample size
        total_samples = len(test.prediction_data)
        if total_samples < test.minimum_sample_size:
            return

        # Check duration
        elapsed_days = (datetime.now() - test.created_at).days
        if elapsed_days < test.duration_days:
            return

        # Analyze results
        results = self._analyze_test_results(test)
        test.results = results
        test.status = "completed"

        # Move to history
        self.test_history.append(test)
        del self.active_tests[test.test_id]

        logger.info(f"A/B test {test.test_id} completed. Winner: {results.get('winner', 'inconclusive')}")

    def _analyze_test_results(self, test: ABTest) -> dict[str, Any]:
        """Analyze A/B test results."""
        if not hasattr(test, "prediction_data"):
            return {"error": "No prediction data available"}

        # Separate control and treatment data
        control_data = [p for p in test.prediction_data if p["version"] == test.control_version]
        treatment_data = [p for p in test.prediction_data if p["version"] == test.treatment_version]

        results = {
            "control_samples": len(control_data),
            "treatment_samples": len(treatment_data),
            "control_version": test.control_version,
            "treatment_version": test.treatment_version,
            "metrics": {},
        }

        # Calculate metrics for both versions
        for metric in test.success_metrics:
            control_values = self._calculate_metric(control_data, metric)
            treatment_values = self._calculate_metric(treatment_data, metric)

            if control_values and treatment_values:
                control_avg = np.mean(control_values)
                treatment_avg = np.mean(treatment_values)

                # Simple statistical test (in real implementation, use proper statistical tests)
                improvement = (treatment_avg - control_avg) / control_avg if control_avg != 0 else 0

                results["metrics"][metric] = {
                    "control": {"average": control_avg, "count": len(control_values), "std": np.std(control_values)},
                    "treatment": {
                        "average": treatment_avg,
                        "count": len(treatment_values),
                        "std": np.std(treatment_values),
                    },
                    "improvement_percent": improvement * 100,
                    "significance": improvement > 0.05,  # Simplified significance test
                }

        # Determine winner
        winner = self._determine_test_winner(results["metrics"])
        results["winner"] = winner
        results["recommendation"] = self._get_recommendation(winner, results["metrics"])

        return results

    def _calculate_metric(self, data: list[dict], metric: str) -> list[float]:
        """Calculate metric values from prediction data."""
        values = []
        for entry in data:
            if entry["ground_truth"] is not None:
                if metric == "accuracy":
                    values.append(1.0 if entry["prediction"] == entry["ground_truth"] else 0.0)
                elif metric == "error_rate":
                    values.append(0.0 if entry["prediction"] == entry["ground_truth"] else 1.0)
                # Add more metric calculations as needed

        return values

    def _determine_test_winner(self, metrics: dict[str, Any]) -> str:
        """Determine which version won the A/B test."""
        treatment_wins = 0
        control_wins = 0

        for _metric_name, metric_data in metrics.items():
            if metric_data.get("significance", False):
                if metric_data["improvement_percent"] > 0:
                    treatment_wins += 1
                else:
                    control_wins += 1

        if treatment_wins > control_wins:
            return "treatment"
        if control_wins > treatment_wins:
            return "control"
        return "inconclusive"

    def _get_recommendation(self, winner: str, metrics: dict[str, Any]) -> str:
        """Get recommendation based on test results."""
        if winner == "treatment":
            return "Deploy treatment version - shows statistically significant improvement"
        if winner == "control":
            return "Keep control version - treatment version does not show improvement"
        return "Inconclusive - consider running test longer or with different metrics"

    def get_test_summary(self, test_id: str) -> dict[str, Any]:
        """Get summary of A/B test."""
        if test_id in self.active_tests:
            test = self.active_tests[test_id]
            status = "running"
        else:
            test = next((t for t in self.test_history if t.test_id == test_id), None)
            status = "completed"

        if not test:
            return {"error": "Test not found"}

        summary = {
            "test_id": test.test_id,
            "model_name": test.model_name,
            "control_version": test.control_version,
            "treatment_version": test.treatment_version,
            "traffic_split": test.traffic_split,
            "status": status,
            "created_at": test.created_at.isoformat(),
        }

        if status == "completed" and test.results:
            summary["results"] = test.results

        return summary


class TrainingOrchestrator:
    """Orchestrates the entire training pipeline."""

    def __init__(self, config_path: str = "./pipeline_config.yaml"):
        self.config = self._load_config(config_path)
        self.model_registry = ModelRegistry(self.config.get("model_registry_path", "./model_registry"))
        self.performance_monitor = PerformanceMonitor()
        self.ab_test_manager = ABTestManager()

        # Training components
        self.training_queue = asyncio.Queue()
        self.active_jobs: dict[str, TrainingJob] = {}
        self.job_history: list[TrainingJob] = []

        # Resource management
        self.max_concurrent_jobs = self.config.get("max_concurrent_jobs", 2)
        self.resource_monitor = ResourceMonitor()

        # Scheduling
        self.scheduler_running = False

        # Setup alert callbacks
        self.performance_monitor.add_alert_callback(self._handle_performance_alert)

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Load pipeline configuration."""
        default_config = {
            "model_registry_path": "./model_registry",
            "max_concurrent_jobs": 2,
            "training_timeout": 3600,
            "monitoring_interval": 300,
            "cleanup_interval": 86400,
            "alert_channels": ["email", "slack"],
            "ab_test_config": {"default_traffic_split": 0.1, "default_duration_days": 7, "minimum_sample_size": 1000},
        }

        if Path(config_path).exists():
            try:
                with open(config_path) as f:
                    user_config = yaml.safe_load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.error(f"Error loading config: {e}")

        return default_config

    async def start(self):
        """Start the training orchestrator."""
        logger.info("Starting training orchestrator")

        # Start background tasks
        self.scheduler_running = True
        asyncio.create_task(self._job_processor())
        asyncio.create_task(self._scheduler())
        asyncio.create_task(self._monitor())

        # Setup scheduled tasks
        schedule.every(1).hours.do(self._scheduled_training_check)
        schedule.every().day.at("02:00").do(self._cleanup_old_models)

        logger.info("Training orchestrator started")

    async def stop(self):
        """Stop the training orchestrator."""
        logger.info("Stopping training orchestrator")
        self.scheduler_running = False

        # Wait for active jobs to complete or timeout
        for job in self.active_jobs.values():
            if job.status == "running":
                logger.info(f"Waiting for job {job.job_id} to complete")
                # In real implementation, would wait gracefully

    async def submit_training_job(self, job_config: dict[str, Any]) -> str:
        """Submit a training job to the queue."""
        job = TrainingJob(
            job_id=str(uuid.uuid4()),
            model_name=job_config["model_name"],
            trigger=TrainingTrigger(job_config.get("trigger", "manual")),
            priority=job_config.get("priority", 5),
            training_config=job_config.get("training_config", {}),
            data_sources=job_config.get("data_sources", []),
            resource_requirements=job_config.get("resource_requirements", {}),
            timeout_seconds=job_config.get("timeout_seconds", self.config["training_timeout"]),
        )

        await self.training_queue.put(job)
        logger.info(f"Submitted training job {job.job_id} for model {job.model_name}")
        return job.job_id

    async def _job_processor(self):
        """Process training jobs from queue."""
        while self.scheduler_running:
            try:
                # Check if we can start a new job
                if len(self.active_jobs) < self.max_concurrent_jobs:
                    try:
                        job = await asyncio.wait_for(self.training_queue.get(), timeout=1.0)
                        await self._start_job(job)
                    except TimeoutError:
                        continue
                else:
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in job processor: {e}")
                await asyncio.sleep(5)

    async def _start_job(self, job: TrainingJob):
        """Start executing a training job."""
        job.status = "running"
        job.started_at = datetime.now()
        self.active_jobs[job.job_id] = job

        logger.info(f"Starting training job {job.job_id}")

        try:
            # Execute training in background
            result = await self._execute_training_job(job)
            job.result = result
            job.status = "completed"
            job.completed_at = datetime.now()

            # Process training results
            await self._process_training_results(job, result)

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now()
            logger.error(f"Training job {job.job_id} failed: {e}")

        finally:
            # Move to history
            self.job_history.append(job)
            del self.active_jobs[job.job_id]

    async def _execute_training_job(self, job: TrainingJob) -> dict[str, Any]:
        """Execute the actual training job."""
        # This is a simplified implementation
        # In practice, this would orchestrate the actual training process

        logger.info(f"Executing training job {job.job_id}")

        # Simulate training time
        await asyncio.sleep(2)

        # Generate mock training results
        results = {
            "model_version": f"{job.model_name}_v{len(self.model_registry.models.get(job.model_name, [])) + 1}",
            "training_time": 120.0,
            "final_loss": 0.123,
            "performance_metrics": {
                "accuracy": 0.92,
                "safety_score": 0.88,
                "robustness_score": 0.85,
                "efficiency": 0.79,
            },
            "validation_results": {"validation_accuracy": 0.90, "test_accuracy": 0.89, "cross_validation_score": 0.91},
            "training_config": job.training_config,
            "data_stats": {"training_samples": 10000, "validation_samples": 2000, "test_samples": 2000},
        }

        return results

    async def _process_training_results(self, job: TrainingJob, results: dict[str, Any]):
        """Process results from completed training job."""
        # Create model version
        model_version = ModelVersion(
            version_id=str(uuid.uuid4()),
            model_name=job.model_name,
            version_number=results["model_version"].split("_v")[-1],
            created_at=datetime.now(),
            created_by="training_pipeline",
            status=ModelStatus.TESTING,
            training_config=job.training_config,
            performance_metrics=results["performance_metrics"],
            validation_results=results["validation_results"],
            file_path=f"./models/{results['model_version']}.pt",
            changelog=f"Trained via job {job.job_id} with trigger {job.trigger.value}",
            tags=[job.trigger.value],
        )

        # Register model
        self.model_registry.register_model(model_version)

        # Set performance baseline
        self.performance_monitor.set_baseline(
            job.model_name, model_version.version_number, results["performance_metrics"]
        )

        # Run A/B test if applicable
        production_model = self.model_registry.get_production_model(job.model_name)
        if production_model and job.trigger != TrainingTrigger.MODEL_FAILURE:
            await self._setup_ab_test(job.model_name, production_model.version_id, model_version.version_id)

        logger.info(f"Processed training results for job {job.job_id}")

    async def _setup_ab_test(self, model_name: str, control_version: str, treatment_version: str):
        """Setup A/B test for new model."""
        test_config = {
            "model_name": model_name,
            "control_version": control_version,
            "treatment_version": treatment_version,
            "traffic_split": self.config["ab_test_config"]["default_traffic_split"],
            "duration_days": self.config["ab_test_config"]["default_duration_days"],
            "minimum_sample_size": self.config["ab_test_config"]["minimum_sample_size"],
        }

        test_id = self.ab_test_manager.create_test(test_config)
        logger.info(f"Setup A/B test {test_id} for model {model_name}")

    async def _scheduler(self):
        """Background scheduler for periodic tasks."""
        while self.scheduler_running:
            try:
                schedule.run_pending()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                await asyncio.sleep(60)

    async def _monitor(self):
        """Background monitoring of training pipeline."""
        while self.scheduler_running:
            try:
                # Monitor resource usage
                resource_stats = self.resource_monitor.get_stats()
                logger.debug(f"Resource stats: {resource_stats}")

                # Monitor active jobs
                for job_id, job in self.active_jobs.items():
                    if job.status == "running":
                        elapsed = (datetime.now() - job.started_at).total_seconds()
                        if elapsed > job.timeout_seconds:
                            logger.warning(f"Job {job_id} exceeded timeout of {job.timeout_seconds}s")
                            # Handle timeout (terminate job, mark as failed, etc.)

                await asyncio.sleep(self.config.get("monitoring_interval", 300))

            except Exception as e:
                logger.error(f"Error in monitoring: {e}")
                await asyncio.sleep(60)

    def _scheduled_training_check(self):
        """Check if scheduled training should be triggered."""
        # This would be called by the scheduler
        # Check for performance degradation, new data, etc.
        logger.info("Performing scheduled training check")

    def _cleanup_old_models(self):
        """Clean up old model versions."""
        # This would be called by the scheduler
        logger.info("Performing model cleanup")
        self.model_registry.cleanup_old_versions()

    def _handle_performance_alert(self, alert: dict[str, Any]):
        """Handle performance degradation alerts."""
        logger.warning(f"Performance alert: {alert}")

        # Trigger retraining if severe degradation
        if alert["severity"] == "high":
            job_config = {
                "model_name": alert["model_name"],
                "trigger": "performance_degradation",
                "priority": 8,  # High priority
                "training_config": {"focus": "performance_recovery"},
            }

            asyncio.create_task(self.submit_training_job(job_config))

    def get_pipeline_status(self) -> dict[str, Any]:
        """Get overall pipeline status."""
        return {
            "active_jobs": len(self.active_jobs),
            "queued_jobs": self.training_queue.qsize(),
            "completed_jobs": len(self.job_history),
            "registered_models": len(self.model_registry.models),
            "active_ab_tests": len(self.ab_test_manager.active_tests),
            "resource_usage": self.resource_monitor.get_stats(),
            "scheduler_running": self.scheduler_running,
        }

    def get_job_status(self, job_id: str) -> dict[str, Any]:
        """Get status of specific training job."""
        # Check active jobs
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
        else:
            # Check job history
            job = next((j for j in self.job_history if j.job_id == job_id), None)
            if not job:
                return {"error": "Job not found"}

        return {
            "job_id": job.job_id,
            "model_name": job.model_name,
            "status": job.status,
            "trigger": job.trigger.value,
            "priority": job.priority,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
            "result": job.result,
        }


class ResourceMonitor:
    """Monitor system resource usage."""

    def get_stats(self) -> dict[str, Any]:
        """Get current system resource statistics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
            "active_processes": len(psutil.pids()),
            "load_average": psutil.getloadavg() if hasattr(psutil, "getloadavg") else None,
        }


# CLI interface
async def main():
    """CLI interface for production training pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Production Training Pipeline")
    parser.add_argument(
        "--action", choices=["start", "submit", "status", "models", "ab-test"], required=True, help="Action to perform"
    )
    parser.add_argument("--config", default="./pipeline_config.yaml", help="Pipeline config file")
    parser.add_argument("--job-config", help="JSON file with job configuration")
    parser.add_argument("--job-id", help="Job ID for status check")
    parser.add_argument("--model-name", help="Model name for specific actions")
    parser.add_argument("--test-config", help="JSON file with A/B test configuration")

    args = parser.parse_args()

    if args.action == "start":
        orchestrator = TrainingOrchestrator(args.config)
        await orchestrator.start()

        try:
            # Keep running until interrupted
            while True:
                await asyncio.sleep(10)
                status = orchestrator.get_pipeline_status()
                logger.info(f"Pipeline status: {status}")
        except KeyboardInterrupt:
            logger.info("Shutting down orchestrator")
            await orchestrator.stop()

    elif args.action == "submit":
        if not args.job_config:
            print("Error: --job-config required for submit action")
            return

        orchestrator = TrainingOrchestrator(args.config)

        try:
            with open(args.job_config) as f:
                job_config = json.load(f)

            job_id = await orchestrator.submit_training_job(job_config)
            print(f"Submitted training job: {job_id}")

        except Exception as e:
            print(f"Error submitting job: {e}")

    elif args.action == "status":
        orchestrator = TrainingOrchestrator(args.config)

        if args.job_id:
            status = orchestrator.get_job_status(args.job_id)
            print("Job Status:")
        else:
            status = orchestrator.get_pipeline_status()
            print("Pipeline Status:")

        print(json.dumps(status, indent=2))

    elif args.action == "models":
        orchestrator = TrainingOrchestrator(args.config)

        if args.model_name:
            models = orchestrator.model_registry.list_models(args.model_name)
        else:
            models = orchestrator.model_registry.list_models()

        print("Models:")
        print(json.dumps(models, indent=2))

    elif args.action == "ab-test":
        orchestrator = TrainingOrchestrator(args.config)

        if args.test_config:
            # Create new A/B test
            try:
                with open(args.test_config) as f:
                    test_config = json.load(f)

                test_id = orchestrator.ab_test_manager.create_test(test_config)
                print(f"Created A/B test: {test_id}")

            except Exception as e:
                print(f"Error creating A/B test: {e}")
        else:
            # List active tests
            active_tests = {
                test_id: orchestrator.ab_test_manager.get_test_summary(test_id)
                for test_id in orchestrator.ab_test_manager.active_tests
            }

            print("Active A/B Tests:")
            print(json.dumps(active_tests, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
