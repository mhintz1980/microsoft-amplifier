"""
Pattern Learning System

Advanced learning system for improving integration patterns based on
execution data and performance metrics. Implements machine learning
algorithms for pattern optimization and adaptation.
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

from ...mcp.persistent_storage import MCPStorageManager
from .skill_integration_patterns_specialist import IntegrationPattern


@dataclass
class PatternPerformanceMetrics:
    """Performance metrics for integration patterns."""

    pattern_id: str
    execution_count: int = 0
    success_count: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    min_duration: float = float("inf")
    max_duration: float = 0.0
    token_consumption: float = 0.0
    avg_tokens: float = 0.0
    error_count: int = 0
    error_rate: float = 0.0
    resource_utilization: dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class PatternExecutionRecord:
    """Record of a single pattern execution."""

    execution_id: str
    pattern_id: str
    skill_ids: list[str]
    execution_context: dict[str, Any]
    start_time: datetime
    end_time: datetime
    duration: float
    success: bool
    error_message: str | None = None
    tokens_used: int = 0
    resources_used: dict[str, float] = field(default_factory=dict)
    output_quality: float = 0.0  # 0-1 scale
    user_satisfaction: float | None = None  # 0-1 scale
    performance_metrics: dict[str, float] = field(default_factory=dict)


@dataclass
class PatternRecommendation:
    """Recommendation for pattern improvement or usage."""

    pattern_id: str
    recommendation_type: str  # "optimize", "replace", "combine", "avoid"
    confidence: float  # 0-1 scale
    reasoning: str
    suggested_changes: list[dict[str, Any]]
    expected_improvement: dict[str, float]
    risk_assessment: str  # "low", "medium", "high"


class PatternAnalytics:
    """Analytics engine for pattern performance analysis."""

    def __init__(self):
        self.performance_data: dict[str, list[PatternExecutionRecord]] = defaultdict(list)
        self.metrics_cache: dict[str, PatternPerformanceMetrics] = {}
        self.trend_analyzers = {}
        self.anomaly_detectors = {}

    def record_execution(self, record: PatternExecutionRecord) -> None:
        """Record a pattern execution for analysis."""
        self.performance_data[record.pattern_id].append(record)

        # Update metrics cache
        self._update_pattern_metrics(record.pattern_id)

        # Trigger trend analysis if enough data
        if len(self.performance_data[record.pattern_id]) >= 10:
            self._analyze_trends(record.pattern_id)

    def get_pattern_metrics(self, pattern_id: str) -> PatternPerformanceMetrics | None:
        """Get performance metrics for a pattern."""
        if pattern_id not in self.metrics_cache:
            self._update_pattern_metrics(pattern_id)
        return self.metrics_cache.get(pattern_id)

    def analyze_performance_trends(self, pattern_id: str) -> dict[str, Any]:
        """Analyze performance trends for a pattern."""
        records = self.performance_data.get(pattern_id, [])
        if len(records) < 5:
            return {"status": "insufficient_data"}

        # Convert to pandas for analysis
        df = pd.DataFrame(
            [
                {
                    "timestamp": r.start_time,
                    "duration": r.duration,
                    "success": r.success,
                    "tokens": r.tokens_used,
                    "quality": r.output_quality,
                }
                for r in records
            ]
        )

        # Calculate trends
        trends = {}

        # Duration trend
        duration_trend = self._calculate_trend(df["duration"])
        trends["duration_trend"] = {
            "slope": duration_trend[0],
            "direction": "improving" if duration_trend[0] < 0 else "degrading",
            "confidence": duration_trend[1],
        }

        # Success rate trend
        success_rate = df["success"].rolling(window=10).mean()
        if len(success_rate.dropna()) > 0:
            success_trend = self._calculate_trend(success_rate.dropna())
            trends["success_rate_trend"] = {
                "slope": success_trend[0],
                "direction": "improving" if success_trend[0] > 0 else "degrading",
                "confidence": success_trend[1],
            }

        # Token efficiency trend
        if len(df["tokens"]) > 0:
            token_efficiency = df["tokens"] / df["duration"]  # tokens per second
            token_trend = self._calculate_trend(token_efficiency)
            trends["token_efficiency_trend"] = {
                "slope": token_trend[0],
                "direction": "improving" if token_trend[0] > 0 else "degrading",
                "confidence": token_trend[1],
            }

        return trends

    def detect_anomalies(self, pattern_id: str) -> list[dict[str, Any]]:
        """Detect anomalous executions for a pattern."""
        records = self.performance_data.get(pattern_id, [])
        if len(records) < 20:
            return []

        anomalies = []

        # Use statistical methods to detect anomalies
        durations = [r.duration for r in records]
        token_usage = [r.tokens_used for r in records]

        # Calculate statistical thresholds
        duration_mean = np.mean(durations)
        duration_std = np.std(durations)
        token_mean = np.mean(token_usage)
        token_std = np.std(token_usage)

        for record in records:
            anomaly_indicators = []

            # Duration anomaly
            if abs(record.duration - duration_mean) > 2 * duration_std:
                anomaly_indicators.append("duration_anomaly")

            # Token usage anomaly
            if abs(record.tokens_used - token_mean) > 2 * token_std:
                anomaly_indicators.append("token_anomaly")

            # Failure anomaly
            if not record.success and record.error_message:
                anomaly_indicators.append("failure_anomaly")

            if anomaly_indicators:
                anomalies.append(
                    {
                        "execution_id": record.execution_id,
                        "timestamp": record.start_time,
                        "anomaly_types": anomaly_indicators,
                        "duration_z_score": (record.duration - duration_mean) / duration_std,
                        "token_z_score": (record.tokens_used - token_mean) / token_std if token_std > 0 else 0,
                        "error_message": record.error_message,
                    }
                )

        return anomalies

    def _update_pattern_metrics(self, pattern_id: str) -> None:
        """Update cached metrics for a pattern."""
        records = self.performance_data.get(pattern_id, [])
        if not records:
            return

        successful_records = [r for r in records if r.success]

        metrics = PatternPerformanceMetrics(
            pattern_id=pattern_id,
            execution_count=len(records),
            success_count=len(successful_records),
            total_duration=sum(r.duration for r in records),
            min_duration=min(r.duration for r in records),
            max_duration=max(r.duration for r in records),
            token_consumption=sum(r.tokens_used for r in records),
            error_count=len([r for r in records if not r.success]),
        )

        # Calculate averages
        if records:
            metrics.avg_duration = metrics.total_duration / len(records)
            metrics.avg_tokens = metrics.token_consumption / len(records)
            metrics.success_rate = metrics.success_count / len(records)
            metrics.error_rate = metrics.error_count / len(records)

        # Calculate resource utilization averages
        if records:
            for resource in records[0].resources_used:
                total_usage = sum(r.resources_used.get(resource, 0) for r in records)
                metrics.resource_utilization[resource] = total_usage / len(records)

        metrics.last_updated = datetime.now()
        self.metrics_cache[pattern_id] = metrics

    def _calculate_trend(self, values: pd.Series) -> tuple[float, float]:
        """Calculate trend slope and confidence."""
        if len(values) < 2:
            return 0.0, 0.0

        x = np.arange(len(values))
        y = values.values

        # Linear regression
        slope, intercept = np.polyfit(x, y, 1)

        # Calculate R² for confidence
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        return slope, r2

    def _analyze_trends(self, pattern_id: str) -> None:
        """Analyze trends for a pattern."""
        trends = self.analyze_performance_trends(pattern_id)
        self.trend_analyzers[pattern_id] = trends


class PatternOptimizer:
    """Machine learning-based pattern optimizer."""

    def __init__(self):
        self.duration_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.success_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.feature_columns = [
            "skill_count",
            "parallel_potential",
            "dependency_depth",
            "resource_intensity",
            "complexity_score",
            "historical_success_rate",
        ]
        self.is_trained = False

    def extract_features(
        self, pattern: IntegrationPattern, historical_metrics: PatternPerformanceMetrics | None = None
    ) -> np.ndarray:
        """Extract features from pattern for ML prediction."""
        features = []

        # Basic pattern features
        features.append(len(pattern.skill_ids))  # skill_count
        features.append(
            1.0 if pattern.pattern_type.value in ["parallel", "fan_out_fan_in"] else 0.0
        )  # parallel_potential
        features.append(len(pattern.dependencies))  # dependency_depth

        # Resource intensity (normalized)
        resource_intensity = 0.0
        if historical_metrics:
            total_resources = sum(historical_metrics.resource_utilization.values())
            resource_intensity = min(1.0, total_resources / 100.0)
        features.append(resource_intensity)  # resource_intensity

        # Complexity score
        complexity_score = self._calculate_complexity_score(pattern)
        features.append(complexity_score)  # complexity_score

        # Historical success rate
        success_rate = historical_metrics.success_rate if historical_metrics else 0.5
        features.append(success_rate)  # historical_success_rate

        return np.array(features).reshape(1, -1)

    def predict_performance(self, pattern: IntegrationPattern, context: dict[str, Any]) -> dict[str, float]:
        """Predict pattern performance metrics."""
        if not self.is_trained:
            return {"estimated_duration": 10.0, "success_probability": 0.5}

        # Get historical metrics if available
        metrics = None  # Would be passed from analytics
        features = self.extract_features(pattern, metrics)
        scaled_features = self.scaler.transform(features)

        # Predictions
        estimated_duration = self.duration_model.predict(scaled_features)[0]
        success_probability = self.success_model.predict(scaled_features)[0]

        # Ensure valid ranges
        estimated_duration = max(0.1, estimated_duration)
        success_probability = max(0.0, min(1.0, success_probability))

        return {"estimated_duration": estimated_duration, "success_probability": success_probability}

    def optimize_pattern(self, pattern: IntegrationPattern, performance_goal: str = "speed") -> IntegrationPattern:
        """Optimize a pattern for a specific performance goal."""
        optimized_pattern = IntegrationPattern(
            id=f"{pattern.id}_optimized_{performance_goal}",
            name=f"Optimized {pattern.name}",
            description=f"Optimized version of {pattern.name} for {performance_goal}",
            pattern_type=pattern.pattern_type,
            skill_ids=pattern.skill_ids.copy(),
            execution_plan=pattern.execution_plan.copy(),
            dependencies=pattern.dependencies.copy(),
            conflicts=pattern.conflicts.copy(),
        )

        if performance_goal == "speed":
            optimized_pattern = self._optimize_for_speed(optimized_pattern)
        elif performance_goal == "reliability":
            optimized_pattern = self._optimize_for_reliability(optimized_pattern)
        elif performance_goal == "efficiency":
            optimized_pattern = self._optimize_for_efficiency(optimized_pattern)

        return optimized_pattern

    def train_models(self, training_data: list[tuple[IntegrationPattern, PatternPerformanceMetrics]]) -> None:
        """Train ML models with historical data."""
        if len(training_data) < 10:
            return  # Not enough data for training

        # Extract features and targets
        X = []
        y_duration = []
        y_success = []

        for pattern, metrics in training_data:
            features = self.extract_features(pattern, metrics)
            X.append(features[0])
            y_duration.append(metrics.avg_duration)
            y_success.append(metrics.success_rate)

        X = np.array(X)
        y_duration = np.array(y_duration)
        y_success = np.array(y_success)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train models
        self.duration_model.fit(X_scaled, y_duration)
        self.success_model.fit(X_scaled, y_success)

        self.is_trained = True

    def _calculate_complexity_score(self, pattern: IntegrationPattern) -> float:
        """Calculate complexity score for a pattern."""
        score = 0.0

        # Base complexity from skill count
        score += min(1.0, len(pattern.skill_ids) / 10.0)

        # Dependency complexity
        score += min(0.5, len(pattern.dependencies) / 5.0)

        # Conflict complexity
        score += min(0.3, len(pattern.conflicts) / 3.0)

        # Pattern type complexity
        complex_types = {"pipeline", "orchestrator", "saga", "conditional", "composite"}
        if pattern.pattern_type.value in complex_types:
            score += 0.2

        return min(1.0, score)

    def _optimize_for_speed(self, pattern: IntegrationPattern) -> IntegrationPattern:
        """Optimize pattern for execution speed."""
        # Add parallel execution opportunities
        if "parallel_groups" not in pattern.execution_plan:
            pattern.execution_plan["parallel_groups"] = []
            pattern.execution_plan["parallel_groups"].append(
                {
                    "skills": pattern.skill_ids[:2],  # Parallelize first two skills
                    "optimization": "speed",
                }
            )

        # Add caching hints
        pattern.execution_plan["optimization_hints"] = {
            "cache_intermediate_results": True,
            "prefetch_likely_inputs": True,
        }

        return pattern

    def _optimize_for_reliability(self, pattern: IntegrationPattern) -> IntegrationPattern:
        """Optimize pattern for reliability."""
        # Add retry mechanisms
        pattern.execution_plan["retry_policy"] = {
            "max_retries": 3,
            "backoff_strategy": "exponential",
            "retry_on_errors": ["timeout", "network", "temporary"],
        }

        # Add circuit breaker
        pattern.execution_plan["circuit_breaker"] = {
            "failure_threshold": 5,
            "recovery_timeout": 60,
            "fallback_enabled": True,
        }

        return pattern

    def _optimize_for_efficiency(self, pattern: IntegrationPattern) -> IntegrationPattern:
        """Optimize pattern for resource efficiency."""
        # Add resource constraints
        pattern.execution_plan["resource_constraints"] = {
            "max_tokens": 1000,
            "max_memory": "512MB",
            "prefer_local_execution": True,
        }

        # Add batching opportunities
        if len(pattern.skill_ids) > 2:
            pattern.execution_plan["batch_opportunities"] = [
                {"skills": pattern.skill_ids[1:3], "batch_size": 10, "batch_timeout": 30}
            ]

        return pattern


class PatternLearningSystem:
    """
    Advanced learning system for integration patterns.

    Features:
    - Performance analytics and trend analysis
    - Anomaly detection and alerting
    - ML-based pattern optimization
    - Automated recommendation generation
    - Continuous improvement loop
    """

    def __init__(self, storage_manager: MCPStorageManager):
        self.storage = storage_manager
        self.analytics = PatternAnalytics()
        self.optimizer = PatternOptimizer()
        self.logger = logging.getLogger(__name__)
        self.recommendation_engine = RecommendationEngine()
        self.learning_loop_task = None

    async def initialize(self) -> None:
        """Initialize the learning system."""
        # Load historical data
        await self._load_historical_data()

        # Train ML models
        await self._train_models()

        # Start continuous learning loop
        self.learning_loop_task = asyncio.create_task(self._continuous_learning_loop())

    async def record_pattern_execution(self, execution_record: PatternExecutionRecord) -> None:
        """Record pattern execution for learning."""
        # Store in analytics
        self.analytics.record_execution(execution_record)

        # Store in persistent storage
        await self.storage.store(
            key=f"pattern_execution/{execution_record.pattern_id}/{execution_record.execution_id}",
            data={
                "execution_id": execution_record.execution_id,
                "pattern_id": execution_record.pattern_id,
                "skill_ids": execution_record.skill_ids,
                "duration": execution_record.duration,
                "success": execution_record.success,
                "tokens_used": execution_record.tokens_used,
                "timestamp": execution_record.start_time.isoformat(),
                "quality_score": execution_record.output_quality,
            },
        )

    async def get_pattern_recommendations(
        self, pattern_id: str, context: dict[str, Any]
    ) -> list[PatternRecommendation]:
        """Get recommendations for pattern improvement."""
        return await self.recommendation_engine.generate_recommendations(pattern_id, context, self.analytics)

    async def optimize_pattern(
        self, pattern: IntegrationPattern, performance_goal: str = "balanced"
    ) -> IntegrationPattern:
        """Optimize a pattern based on learned insights."""
        # Get pattern performance
        metrics = self.analytics.get_pattern_metrics(pattern.id)

        # Use ML optimizer
        optimized = self.optimizer.optimize_pattern(pattern, performance_goal)

        # Add learned optimizations
        if metrics:
            optimized = await self._apply_learned_optimizations(optimized, metrics)

        return optimized

    async def get_learning_insights(self) -> dict[str, Any]:
        """Get comprehensive learning insights."""
        insights = {
            "patterns_analyzed": len(self.analytics.performance_data),
            "total_executions": sum(len(records) for records in self.analytics.performance_data.values()),
            "average_success_rate": self._calculate_overall_success_rate(),
            "top_performing_patterns": self._get_top_performing_patterns(),
            "patterns_needing_attention": self._get_attention_needed_patterns(),
            "optimization_opportunities": await self._identify_optimization_opportunities(),
            "learning_status": "active"
            if self.learning_loop_task and not self.learning_loop_task.done()
            else "inactive",
        }

        return insights

    async def shutdown(self) -> None:
        """Shutdown the learning system."""
        if self.learning_loop_task:
            self.learning_loop_task.cancel()
            try:
                await self.learning_loop_task
            except asyncio.CancelledError:
                pass

        # Save current state
        await self._save_current_state()

    async def _load_historical_data(self) -> None:
        """Load historical execution data from storage."""
        try:
            # This would load from MCP storage
            # For now, initialize with empty data
            pass
        except Exception as e:
            self.logger.warning(f"Failed to load historical data: {str(e)}")

    async def _train_models(self) -> None:
        """Train ML models with historical data."""
        # Prepare training data from analytics
        training_data = []
        for pattern_id, records in self.analytics.performance_data.items():
            metrics = self.analytics.get_pattern_metrics(pattern_id)
            if metrics and len(records) >= 5:
                # Create a mock pattern for training
                pattern = IntegrationPattern(
                    id=pattern_id,
                    name=pattern_id,
                    description=f"Pattern {pattern_id}",
                    pattern_type=IntegrationPatternType.SEQUENTIAL,
                    skill_ids=[],
                    execution_plan={},
                    dependencies=[],
                )
                training_data.append((pattern, metrics))

        if training_data:
            self.optimizer.train_models(training_data)
            self.logger.info(f"Trained ML models with {len(training_data)} patterns")

    async def _continuous_learning_loop(self) -> None:
        """Continuous background learning loop."""
        while True:
            try:
                # Periodic model retraining
                await self._periodic_model_retraining()

                # Anomaly detection and alerting
                await self._anomaly_detection_and_alerting()

                # Performance optimization
                await self._performance_optimization()

                # Sleep for learning interval (1 hour)
                await asyncio.sleep(3600)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in learning loop: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _periodic_model_retraining(self) -> None:
        """Periodically retrain ML models."""
        # Check if we have enough new data
        total_executions = sum(len(records) for records in self.analytics.performance_data.values())
        if total_executions % 100 == 0:  # Retrain every 100 executions
            await self._train_models()
            self.logger.info("Retrained ML models with new data")

    async def _anomaly_detection_and_alerting(self) -> None:
        """Detect anomalies and generate alerts."""
        for pattern_id in self.analytics.performance_data:
            anomalies = self.analytics.detect_anomalies(pattern_id)
            if anomalies:
                # Store anomaly alerts
                await self.storage.store(
                    key=f"anomaly_alerts/{pattern_id}/{datetime.now().timestamp()}",
                    data={"pattern_id": pattern_id, "anomalies": anomalies, "timestamp": datetime.now().isoformat()},
                )
                self.logger.warning(f"Detected {len(anomalies)} anomalies for pattern {pattern_id}")

    async def _performance_optimization(self) -> None:
        """Identify and implement performance optimizations."""
        # This would implement automatic optimization based on learning
        pass

    async def _apply_learned_optimizations(
        self, pattern: IntegrationPattern, metrics: PatternPerformanceMetrics
    ) -> IntegrationPattern:
        """Apply learned optimizations to a pattern."""
        # Apply optimizations based on historical performance
        if metrics.avg_duration > 30:  # Slow pattern
            pattern.execution_plan["optimization_hints"] = pattern.execution_plan.get("optimization_hints", {})
            pattern.execution_plan["optimization_hints"]["parallel_execution"] = True

        if metrics.success_rate < 0.9:  # Low success rate
            pattern.execution_plan["retry_policy"] = {"max_retries": 3, "backoff": "exponential"}

        if metrics.avg_tokens > 1000:  # High token usage
            pattern.execution_plan["token_optimization"] = {"compression_enabled": True, "context_pruning": True}

        return pattern

    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate across all patterns."""
        total_executions = sum(len(records) for records in self.analytics.performance_data.values())
        if total_executions == 0:
            return 0.0

        total_successes = sum(
            sum(1 for record in records if record.success) for records in self.analytics.performance_data.values()
        )

        return total_successes / total_executions

    def _get_top_performing_patterns(self, limit: int = 5) -> list[dict[str, Any]]:
        """Get top performing patterns."""
        pattern_performance = []
        for pattern_id, metrics in self.analytics.metrics_cache.items():
            if metrics.execution_count >= 5:  # Minimum executions
                pattern_performance.append(
                    {
                        "pattern_id": pattern_id,
                        "success_rate": metrics.success_rate,
                        "avg_duration": metrics.avg_duration,
                        "execution_count": metrics.execution_count,
                    }
                )

        # Sort by success rate and duration
        pattern_performance.sort(key=lambda x: (x["success_rate"], -x["avg_duration"]), reverse=True)

        return pattern_performance[:limit]

    def _get_attention_needed_patterns(self, limit: int = 5) -> list[dict[str, Any]]:
        """Get patterns that need attention."""
        attention_patterns = []
        for pattern_id, metrics in self.analytics.metrics_cache.items():
            if metrics.execution_count >= 5:
                # Check for issues
                issues = []
                if metrics.success_rate < 0.8:
                    issues.append("low_success_rate")
                if metrics.avg_duration > 60:
                    issues.append("slow_execution")
                if metrics.error_rate > 0.2:
                    issues.append("high_error_rate")

                if issues:
                    attention_patterns.append(
                        {
                            "pattern_id": pattern_id,
                            "issues": issues,
                            "success_rate": metrics.success_rate,
                            "avg_duration": metrics.avg_duration,
                        }
                    )

        return attention_patterns[:limit]

    async def _identify_optimization_opportunities(self) -> list[dict[str, Any]]:
        """Identify optimization opportunities."""
        opportunities = []
        for pattern_id, metrics in self.analytics.metrics_cache.items():
            if metrics.execution_count >= 10:
                # Check for optimization opportunities
                if metrics.avg_duration > 20:
                    opportunities.append(
                        {
                            "pattern_id": pattern_id,
                            "opportunity": "speed_optimization",
                            "potential_improvement": "30-50% faster execution",
                        }
                    )

                if metrics.avg_tokens > 500:
                    opportunities.append(
                        {
                            "pattern_id": pattern_id,
                            "opportunity": "token_optimization",
                            "potential_improvement": "20-40% token reduction",
                        }
                    )

        return opportunities

    async def _save_current_state(self) -> None:
        """Save current learning state to storage."""
        state = {
            "timestamp": datetime.now().isoformat(),
            "patterns_tracked": len(self.analytics.metrics_cache),
            "total_executions": sum(len(records) for records in self.analytics.performance_data.values()),
            "models_trained": self.optimizer.is_trained,
        }

        await self.storage.store(key="learning_system_state", data=state)


class RecommendationEngine:
    """Engine for generating pattern recommendations."""

    async def generate_recommendations(
        self, pattern_id: str, context: dict[str, Any], analytics: PatternAnalytics
    ) -> list[PatternRecommendation]:
        """Generate recommendations for a pattern."""
        recommendations = []
        metrics = analytics.get_pattern_metrics(pattern_id)

        if not metrics:
            return recommendations

        # Performance-based recommendations
        if metrics.success_rate < 0.8:
            recommendations.append(
                PatternRecommendation(
                    pattern_id=pattern_id,
                    recommendation_type="optimize",
                    confidence=0.8,
                    reasoning=f"Low success rate ({metrics.success_rate:.1%}) indicates need for optimization",
                    suggested_changes=[
                        {"action": "add_retry_logic", "parameters": {"max_retries": 3}},
                        {"action": "add_error_handling", "parameters": {"graceful_degradation": True}},
                    ],
                    expected_improvement={"success_rate": 0.15, "reliability": 0.25},
                    risk_assessment="low",
                )
            )

        if metrics.avg_duration > 30:
            recommendations.append(
                PatternRecommendation(
                    pattern_id=pattern_id,
                    recommendation_type="optimize",
                    confidence=0.7,
                    reasoning=f"Slow execution time ({metrics.avg_duration:.1f}s) suggests optimization opportunities",
                    suggested_changes=[
                        {"action": "enable_parallel_execution", "parameters": {"max_workers": 4}},
                        {"action": "add_caching", "parameters": {"ttl": 300}},
                    ],
                    expected_improvement={"duration_reduction": 0.40, "throughput_increase": 0.30},
                    risk_assessment="medium",
                )
            )

        return recommendations


# Export the learning system
__all__ = [
    "PatternLearningSystem",
    "PatternAnalytics",
    "PatternOptimizer",
    "PatternRecommendation",
    "PatternPerformanceMetrics",
    "PatternExecutionRecord",
]
