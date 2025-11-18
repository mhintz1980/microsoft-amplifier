"""
Skill Performance Tracker

Tracks and analyzes skill performance metrics using Agent Lightning's RL training
capabilities to identify patterns, detect issues, and provide optimization insights.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

import numpy as np
from dataclasses import dataclass

from .config import PerformanceTrackingConfig

logger = logging.getLogger(__name__)


@dataclass
class SkillExecutionMetrics:
    """Metrics captured during skill execution"""

    skill_id: str
    skill_name: str
    execution_id: str
    timestamp: datetime

    # Performance metrics
    execution_time: float  # seconds
    success: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    # Quality metrics
    accuracy_score: float  # 0-1
    user_satisfaction: Optional[float] = None  # 0-1
    hallucination_detected: bool = False
    hallucination_score: float = 0.0  # 0-1

    # Resource metrics
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    tokens_used: int = 0

    # Context metrics
    context_size_tokens: int = 0
    response_size_tokens: int = 0

    # Additional metadata
    user_feedback: Optional[str] = None
    optimization_version: int = 1


@dataclass
class SkillPerformanceSummary:
    """Aggregated performance summary for a skill"""

    skill_id: str
    skill_name: str
    period_start: datetime
    period_end: datetime
    total_executions: int

    # Success metrics
    success_rate: float
    error_rate: float
    hallucination_rate: float

    # Performance metrics
    avg_execution_time: float
    p95_execution_time: float
    avg_accuracy_score: float
    avg_user_satisfaction: float

    # Resource metrics
    avg_memory_usage: float
    avg_cpu_usage: float
    avg_tokens_used: float

    # Trend analysis
    performance_trend: str  # "improving", "stable", "degrading"
    trend_strength: float  # 0-1

    # Quality assessment
    quality_grade: str  # "A", "B", "C", "D", "F"
    optimization_recommendations: List[str]


class SkillPerformanceTracker:
    """Tracks and analyzes skill performance using RL-powered insights"""

    def __init__(self, config: PerformanceTrackingConfig, storage_path: Path):
        self.config = config
        self.storage_path = storage_path
        self.metrics_path = storage_path / "metrics"
        self.metrics_path.mkdir(parents=True, exist_ok=True)

        # In-memory storage for recent metrics
        self.recent_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=config.history_window_size))
        self.skill_summaries: Dict[str, SkillPerformanceSummary] = {}

        # Performance patterns for RL training
        self.performance_patterns: Dict[str, List[Dict]] = defaultdict(list)
        self.error_patterns: Dict[str, List[Dict]] = defaultdict(list)

        # Background tasks
        self._collection_task: Optional[asyncio.Task] = None
        self._analysis_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start the performance tracking system"""
        if self._running:
            return

        self._running = True
        logger.info("Starting skill performance tracker")

        # Load existing data
        await self._load_historical_data()

        # Start background tasks
        self._collection_task = asyncio.create_task(self._collection_loop())
        self._analysis_task = asyncio.create_task(self._analysis_loop())

    async def stop(self):
        """Stop the performance tracking system"""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping skill performance tracker")

        # Cancel background tasks
        if self._collection_task:
            self._collection_task.cancel()
        if self._analysis_task:
            self._analysis_task.cancel()

        # Save current data
        await self._save_metrics()

    async def record_execution(self, metrics: SkillExecutionMetrics):
        """Record metrics from a skill execution"""
        try:
            # Store in memory
            self.recent_metrics[metrics.skill_id].append(metrics)

            # Store to disk
            await self._save_metrics_for_skill(metrics.skill_id)

            # Analyze immediately for critical issues
            if not metrics.success or metrics.hallucination_detected:
                await self._analyze_critical_issue(metrics)

            logger.debug(f"Recorded execution metrics for skill {metrics.skill_id}")

        except Exception as e:
            logger.error(f"Failed to record execution metrics: {e}")

    async def get_skill_summary(self, skill_id: str, period_hours: int = 24) -> Optional[SkillPerformanceSummary]:
        """Get performance summary for a skill over a time period"""
        try:
            if skill_id not in self.recent_metrics:
                return None

            metrics = list(self.recent_metrics[skill_id])
            if not metrics:
                return None

            # Filter by time period
            cutoff_time = datetime.now() - timedelta(hours=period_hours)
            recent_metrics = [m for m in metrics if m.timestamp >= cutoff_time]

            if not recent_metrics:
                return None

            # Calculate summary
            summary = await self._calculate_summary(skill_id, recent_metrics)
            self.skill_summaries[skill_id] = summary

            return summary

        except Exception as e:
            logger.error(f"Failed to get skill summary for {skill_id}: {e}")
            return None

    async def get_performance_trends(self, skill_id: str, days: int = 7) -> Dict[str, Any]:
        """Analyze performance trends for a skill"""
        try:
            if skill_id not in self.recent_metrics:
                return {}

            metrics = list(self.recent_metrics[skill_id])
            cutoff_time = datetime.now() - timedelta(days=days)
            trend_metrics = [m for m in metrics if m.timestamp >= cutoff_time]

            if len(trend_metrics) < 10:  # Need sufficient data
                return {"error": "Insufficient data for trend analysis"}

            # Calculate trends
            return {
                "execution_time_trend": self._calculate_trend([m.execution_time for m in trend_metrics]),
                "accuracy_trend": self._calculate_trend([m.accuracy_score for m in trend_metrics]),
                "success_rate_trend": self._calculate_trend([1.0 if m.success else 0.0 for m in trend_metrics]),
                "resource_efficiency_trend": self._calculate_trend(
                    [m.tokens_used / max(m.execution_time, 0.001) for m in trend_metrics]
                ),
                "period_start": min(m.timestamp for m in trend_metrics).isoformat(),
                "period_end": max(m.timestamp for m in trend_metrics).isoformat(),
                "data_points": len(trend_metrics),
            }

        except Exception as e:
            logger.error(f"Failed to analyze performance trends for {skill_id}: {e}")
            return {"error": str(e)}

    async def detect_performance_anomalies(self, skill_id: str) -> List[Dict[str, Any]]:
        """Detect performance anomalies using RL-powered pattern recognition"""
        try:
            if skill_id not in self.recent_metrics:
                return []

            metrics = list(self.recent_metrics[skill_id])
            if len(metrics) < 20:  # Need baseline
                return []

            anomalies = []
            recent_metrics = metrics[-10:]  # Last 10 executions

            # Compare with historical baseline
            baseline_metrics = metrics[:-10]

            for metric in recent_metrics:
                anomaly_score = self._calculate_anomaly_score(metric, baseline_metrics)
                if anomaly_score > self.config.error_detection_sensitivity:
                    anomalies.append(
                        {
                            "execution_id": metric.execution_id,
                            "timestamp": metric.timestamp.isoformat(),
                            "anomaly_score": anomaly_score,
                            "anomaly_type": self._classify_anomaly(metric, baseline_metrics),
                            "metrics": asdict(metric),
                        }
                    )

            return anomalies

        except Exception as e:
            logger.error(f"Failed to detect performance anomalies for {skill_id}: {e}")
            return []

    async def get_optimization_insights(self, skill_id: str) -> Dict[str, Any]:
        """Get optimization insights using RL-powered analysis"""
        try:
            summary = await self.get_skill_summary(skill_id)
            if not summary:
                return {"error": "No performance data available"}

            trends = await self.get_performance_trends(skill_id)
            anomalies = await self.detect_performance_anomalies(skill_id)

            # Generate optimization recommendations
            recommendations = self._generate_optimization_recommendations(summary, trends, anomalies)

            return {
                "performance_summary": asdict(summary),
                "trends": trends,
                "anomalies": anomalies,
                "recommendations": recommendations,
                "optimization_priority": self._calculate_optimization_priority(summary, anomalies),
                "estimated_improvement": self._estimate_optimization_impact(recommendations),
            }

        except Exception as e:
            logger.error(f"Failed to get optimization insights for {skill_id}: {e}")
            return {"error": str(e)}

    # Private methods

    async def _collection_loop(self):
        """Background loop for collecting and processing metrics"""
        while self._running:
            try:
                await self._process_metrics_queue()
                await asyncio.sleep(self.config.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                await asyncio.sleep(5)

    async def _analysis_loop(self):
        """Background loop for analyzing performance patterns"""
        while self._running:
            try:
                await self._analyze_performance_patterns()
                await asyncio.sleep(300)  # Analyze every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                await asyncio.sleep(30)

    async def _load_historical_data(self):
        """Load historical performance data from disk"""
        try:
            metrics_file = self.metrics_path / "historical_metrics.jsonl"
            if not metrics_file.exists():
                return

            async with asyncio.to_thread(open, metrics_file, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        metrics = SkillExecutionMetrics(**data)
                        self.recent_metrics[metrics.skill_id].append(metrics)
                    except Exception as e:
                        logger.warning(f"Failed to load metrics line: {e}")

            logger.info(f"Loaded historical metrics for {len(self.recent_metrics)} skills")

        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")

    async def _save_metrics_for_skill(self, skill_id: str):
        """Save metrics for a specific skill to disk"""
        try:
            skill_file = self.metrics_path / f"skill_{skill_id}.jsonl"
            metrics = list(self.recent_metrics[skill_id])

            async with asyncio.to_thread(open, skill_file, "w") as f:
                for metric in metrics:
                    f.write(json.dumps(asdict(metric), default=str) + "\n")

        except Exception as e:
            logger.error(f"Failed to save metrics for skill {skill_id}: {e}")

    async def _save_metrics(self):
        """Save all metrics to disk"""
        try:
            for skill_id in self.recent_metrics:
                await self._save_metrics_for_skill(skill_id)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    async def _calculate_summary(self, skill_id: str, metrics: List[SkillExecutionMetrics]) -> SkillPerformanceSummary:
        """Calculate performance summary from metrics"""
        if not metrics:
            raise ValueError("No metrics provided")

        # Basic calculations
        total_executions = len(metrics)
        successful_executions = sum(1 for m in metrics if m.success)
        hallucinations = sum(1 for m in metrics if m.hallucination_detected)

        success_rate = successful_executions / total_executions
        error_rate = 1.0 - success_rate
        hallucination_rate = hallucinations / total_executions

        # Performance calculations
        execution_times = [m.execution_time for m in metrics]
        avg_execution_time = np.mean(execution_times)
        p95_execution_time = np.percentile(execution_times, 95)

        accuracy_scores = [m.accuracy_score for m in metrics if m.accuracy_score > 0]
        avg_accuracy_score = np.mean(accuracy_scores) if accuracy_scores else 0.0

        satisfaction_scores = [m.user_satisfaction for m in metrics if m.user_satisfaction is not None]
        avg_user_satisfaction = np.mean(satisfaction_scores) if satisfaction_scores else 0.0

        # Resource calculations
        avg_memory_usage = np.mean([m.memory_usage_mb for m in metrics])
        avg_cpu_usage = np.mean([m.cpu_usage_percent for m in metrics])
        avg_tokens_used = np.mean([m.tokens_used for m in metrics])

        # Trend analysis
        performance_trend, trend_strength = self._analyze_performance_trend(metrics)

        # Quality grade
        quality_grade = self._calculate_quality_grade(success_rate, avg_accuracy_score, hallucination_rate)

        # Optimization recommendations
        recommendations = self._generate_summary_recommendations(
            success_rate, avg_accuracy_score, hallucination_rate, avg_execution_time
        )

        return SkillPerformanceSummary(
            skill_id=skill_id,
            skill_name=metrics[0].skill_name,
            period_start=min(m.timestamp for m in metrics),
            period_end=max(m.timestamp for m in metrics),
            total_executions=total_executions,
            success_rate=success_rate,
            error_rate=error_rate,
            hallucination_rate=hallucination_rate,
            avg_execution_time=avg_execution_time,
            p95_execution_time=p95_execution_time,
            avg_accuracy_score=avg_accuracy_score,
            avg_user_satisfaction=avg_user_satisfaction,
            avg_memory_usage=avg_memory_usage,
            avg_cpu_usage=avg_cpu_usage,
            avg_tokens_used=avg_tokens_used,
            performance_trend=performance_trend,
            trend_strength=trend_strength,
            quality_grade=quality_grade,
            optimization_recommendations=recommendations,
        )

    def _calculate_trend(self, values: List[float]) -> Dict[str, float]:
        """Calculate trend for a series of values"""
        if len(values) < 2:
            return {"slope": 0.0, "direction": "stable", "confidence": 0.0}

        # Simple linear regression
        x = np.arange(len(values))
        y = np.array(values)

        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]

        # Calculate correlation coefficient for confidence
        if np.std(y) > 0:
            correlation = np.corrcoef(x, y)[0, 1]
        else:
            correlation = 0.0

        # Determine direction
        if abs(slope) < 0.01:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        return {"slope": float(slope), "direction": direction, "confidence": float(abs(correlation))}

    def _calculate_anomaly_score(self, metric: SkillExecutionMetrics, baseline: List[SkillExecutionMetrics]) -> float:
        """Calculate anomaly score for a metric compared to baseline"""
        if len(baseline) < 5:
            return 0.0

        # Calculate z-scores for key metrics
        baseline_times = [m.execution_time for m in baseline]
        baseline_accuracies = [m.accuracy_score for m in baseline]

        time_z = abs((metric.execution_time - np.mean(baseline_times)) / (np.std(baseline_times) + 1e-6))
        accuracy_z = abs((metric.accuracy_score - np.mean(baseline_accuracies)) / (np.std(baseline_accuracies) + 1e-6))

        # Combine z-scores
        anomaly_score = (time_z + accuracy_z) / 2

        # Boost for failures and hallucinations
        if not metric.success:
            anomaly_score += 2.0
        if metric.hallucination_detected:
            anomaly_score += 3.0

        return min(anomaly_score, 10.0)  # Cap at 10

    def _classify_anomaly(self, metric: SkillExecutionMetrics, baseline: List[SkillExecutionMetrics]) -> str:
        """Classify the type of anomaly"""
        if not metric.success:
            return "execution_failure"
        if metric.hallucination_detected:
            return "hallucination"

        baseline_times = [m.execution_time for m in baseline]
        if metric.execution_time > np.percentile(baseline_times, 95):
            return "performance_degradation"

        baseline_accuracies = [m.accuracy_score for m in baseline]
        if metric.accuracy_score < np.percentile(baseline_accuracies, 5):
            return "accuracy_drop"

        return "other"

    def _analyze_performance_trend(self, metrics: List[SkillExecutionMetrics]) -> Tuple[str, float]:
        """Analyze performance trend from metrics"""
        if len(metrics) < 10:
            return "stable", 0.0

        # Calculate success rate trend
        success_rates = []
        window_size = min(10, len(metrics) // 3)

        for i in range(len(metrics) - window_size + 1):
            window = metrics[i : i + window_size]
            success_rate = sum(1 for m in window if m.success) / len(window)
            success_rates.append(success_rate)

        if len(success_rates) < 2:
            return "stable", 0.0

        # Simple trend analysis
        recent_avg = np.mean(success_rates[-3:])
        early_avg = np.mean(success_rates[:3])

        diff = recent_avg - early_avg

        if abs(diff) < 0.05:
            return "stable", 1.0 - abs(diff) * 20
        elif diff > 0:
            return "improving", min(diff * 10, 1.0)
        else:
            return "degrading", min(abs(diff) * 10, 1.0)

    def _calculate_quality_grade(self, success_rate: float, accuracy: float, hallucination_rate: float) -> str:
        """Calculate overall quality grade"""
        score = success_rate * 0.4 + accuracy * 0.5 - hallucination_rate * 0.1

        if score >= 0.95:
            return "A"
        elif score >= 0.90:
            return "B"
        elif score >= 0.80:
            return "C"
        elif score >= 0.70:
            return "D"
        else:
            return "F"

    def _generate_summary_recommendations(
        self, success_rate: float, accuracy: float, hallucination_rate: float, execution_time: float
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        if success_rate < self.config.excellent_threshold:
            if success_rate < self.config.acceptable_threshold:
                recommendations.append("CRITICAL: Low success rate requires immediate attention")
            else:
                recommendations.append("Improve error handling and input validation")

        if accuracy < self.config.excellent_threshold:
            recommendations.append("Enhance accuracy through better training data or algorithms")

        if hallucination_rate > 0.01:
            recommendations.append("Implement stronger fact-checking and validation mechanisms")

        if execution_time > 10.0:  # 10 seconds threshold
            recommendations.append("Optimize performance through code efficiency or caching")

        return recommendations

    def _generate_optimization_recommendations(
        self, summary: SkillPerformanceSummary, trends: Dict[str, Any], anomalies: List[Dict]
    ) -> List[str]:
        """Generate comprehensive optimization recommendations"""
        recommendations = summary.optimization_recommendations.copy()

        # Trend-based recommendations
        if trends.get("success_rate_trend", {}).get("direction") == "degrading":
            recommendations.append("Address declining success rate - investigate recent changes")

        if trends.get("execution_time_trend", {}).get("direction") == "increasing":
            recommendations.append("Performance is degrading - optimize code or increase resources")

        # Anomaly-based recommendations
        if anomalies:
            anomaly_types = set(a["anomaly_type"] for a in anomalies)
            if "hallucination" in anomaly_types:
                recommendations.append("URGENT: Hallucinations detected - implement stronger validation")
            if "execution_failure" in anomaly_types:
                recommendations.append("Fix execution failures - improve error handling")

        return recommendations

    def _calculate_optimization_priority(self, summary: SkillPerformanceSummary, anomalies: List[Dict]) -> str:
        """Calculate optimization priority level"""
        if summary.quality_grade in ["D", "F"] or len(anomalies) > 3:
            return "critical"
        elif summary.quality_grade == "C" or len(anomalies) > 1:
            return "high"
        elif summary.quality_grade == "B" or summary.performance_trend == "degrading":
            return "medium"
        else:
            return "low"

    def _estimate_optimization_impact(self, recommendations: List[str]) -> Dict[str, float]:
        """Estimate potential impact of optimizations"""
        impact = {
            "success_rate_improvement": 0.0,
            "accuracy_improvement": 0.0,
            "performance_improvement": 0.0,
            "overall_impact": 0.0,
        }

        # Simple heuristics for impact estimation
        for rec in recommendations:
            if "CRITICAL" in rec or "URGENT" in rec:
                impact["success_rate_improvement"] += 0.15
                impact["accuracy_improvement"] += 0.10
            elif "hallucination" in rec:
                impact["success_rate_improvement"] += 0.20
                impact["accuracy_improvement"] += 0.15
            elif "performance" in rec or "optimize" in rec:
                impact["performance_improvement"] += 0.25
            else:
                impact["success_rate_improvement"] += 0.05
                impact["accuracy_improvement"] += 0.03

        # Calculate overall impact
        impact["overall_impact"] = (
            impact["success_rate_improvement"] + impact["accuracy_improvement"] + impact["performance_improvement"]
        ) / 3

        # Cap values
        for key in impact:
            impact[key] = min(impact[key], 0.5)  # Max 50% improvement

        return impact

    async def _analyze_critical_issue(self, metrics: SkillExecutionMetrics):
        """Analyze critical issues immediately"""
        if not metrics.success:
            logger.warning(f"Critical failure in skill {metrics.skill_id}: {metrics.error_message}")
            # Trigger immediate analysis and alerting

        if metrics.hallucination_detected:
            logger.error(f"Hallucination detected in skill {metrics.skill_id} (score: {metrics.hallucination_score})")
            # Trigger immediate quality gate intervention

    async def _analyze_performance_patterns(self):
        """Analyze performance patterns for RL training"""
        try:
            for skill_id, metrics_deque in self.recent_metrics.items():
                metrics = list(metrics_deque)
                if len(metrics) < 20:
                    continue

                # Extract patterns for RL training
                patterns = self._extract_performance_patterns(metrics)
                self.performance_patterns[skill_id] = patterns

                # Extract error patterns
                error_patterns = self._extract_error_patterns(metrics)
                if error_patterns:
                    self.error_patterns[skill_id] = error_patterns

        except Exception as e:
            logger.error(f"Failed to analyze performance patterns: {e}")

    def _extract_performance_patterns(self, metrics: List[SkillExecutionMetrics]) -> List[Dict]:
        """Extract performance patterns for RL training"""
        patterns = []

        # Success patterns
        successful_metrics = [m for m in metrics if m.success]
        if successful_metrics:
            patterns.append(
                {
                    "type": "success",
                    "count": len(successful_metrics),
                    "avg_execution_time": np.mean([m.execution_time for m in successful_metrics]),
                    "avg_accuracy": np.mean([m.accuracy_score for m in successful_metrics]),
                    "context_sizes": [m.context_size_tokens for m in successful_metrics],
                }
            )

        # Failure patterns
        failed_metrics = [m for m in metrics if not m.success]
        if failed_metrics:
            patterns.append(
                {
                    "type": "failure",
                    "count": len(failed_metrics),
                    "common_errors": self._find_common_errors(failed_metrics),
                    "avg_context_size": np.mean([m.context_size_tokens for m in failed_metrics]),
                }
            )

        return patterns

    def _extract_error_patterns(self, metrics: List[SkillExecutionMetrics]) -> List[Dict]:
        """Extract error patterns for analysis"""
        error_metrics = [m for m in metrics if not m.success]
        if not error_metrics:
            return []

        error_patterns = []
        error_types = defaultdict(int)

        for metric in error_metrics:
            if metric.error_type:
                error_types[metric.error_type] += 1

        for error_type, count in error_types.items():
            if count >= 2:  # Only include patterns with multiple occurrences
                related_metrics = [m for m in error_metrics if m.error_type == error_type]
                error_patterns.append(
                    {
                        "error_type": error_type,
                        "frequency": count,
                        "avg_context_size": np.mean([m.context_size_tokens for m in related_metrics]),
                        "time_distribution": [m.execution_time for m in related_metrics],
                    }
                )

        return error_patterns

    def _find_common_errors(self, failed_metrics: List[SkillExecutionMetrics]) -> List[str]:
        """Find common error messages"""
        error_messages = [m.error_message for m in failed_metrics if m.error_message]
        if not error_messages:
            return []

        # Simple similarity-based clustering
        common_errors = []
        for msg in error_messages:
            if any(msg.lower() in existing.lower() for existing in common_errors):
                continue
            # Check for similar messages
            similar_count = sum(1 for other in error_messages if other and self._message_similarity(msg, other) > 0.7)
            if similar_count >= 2:
                common_errors.append(msg)

        return common_errors[:5]  # Return top 5

    def _message_similarity(self, msg1: str, msg2: str) -> float:
        """Calculate similarity between error messages"""
        if not msg1 or not msg2:
            return 0.0

        words1 = set(msg1.lower().split())
        words2 = set(msg2.lower().split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    async def _process_metrics_queue(self):
        """Process any pending metrics in the queue"""
        # This would integrate with a message queue system in production
        pass
