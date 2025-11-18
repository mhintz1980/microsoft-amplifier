"""
Continuous Improvement Learning System

Analyzes validation results, user feedback, and performance metrics to
continuously learn and improve quality standards, validation rules, and
skill quality across the entire ecosystem.
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import asyncio
from pathlib import Path

from amplifier.mcp.code_execution import execute_in_docker
from amplifier.mcp.persistent_storage import store_result, retrieve_result


class LearningType(Enum):
    """Types of learning and improvement."""

    PATTERN_RECOGNITION = "pattern_recognition"
    FEEDBACK_ANALYSIS = "feedback_analysis"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    STANDARDS_EVOLUTION = "standards_evolution"
    ANOMALY_DETECTION = "anomaly_detection"
    PREDICTIVE_ANALYSIS = "predictive_analysis"


class ImprovementType(Enum):
    """Types of improvements to apply."""

    VALIDATION_RULE_UPDATE = "validation_rule_update"
    THRESHOLD_ADJUSTMENT = "threshold_adjustment"
    NEW_PATTERN_DETECTION = "new_pattern_detection"
    PERFORMANCE_TUNING = "performance_tuning"
    STANDARDS_ENHANCEMENT = "standards_enhancement"


@dataclass
class LearningInsight:
    """Insight discovered through continuous learning."""

    insight_id: str
    learning_type: LearningType
    title: str
    description: str
    confidence: float
    evidence: List[str]
    recommendation: str
    impact_score: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityTrend:
    """Quality trend analysis over time."""

    metric_name: str
    time_period: Tuple[datetime, datetime]
    trend_direction: str  # "improving", "degrading", "stable"
    trend_strength: float
    data_points: List[Tuple[datetime, float]]
    analysis_summary: str


@dataclass
class ImprovementAction:
    """Action to be taken based on learning insights."""

    action_id: str
    improvement_type: ImprovementType
    title: str
    description: str
    priority: str  # "high", "medium", "low"
    target_skill_patterns: List[str]
    implementation_steps: List[str]
    expected_impact: float
    status: str = "pending"  # "pending", "in_progress", "completed", "failed"


@dataclass
class LearningReport:
    """Comprehensive learning and improvement report."""

    report_period: Tuple[datetime, datetime]
    insights: List[LearningInsight]
    trends: List[QualityTrend]
    improvement_actions: List[ImprovementAction]
    quality_score_change: float
    key_findings: List[str]
    recommendations: List[str]
    next_learning_focus: List[str]


class ContinuousImprovement:
    """Continuous improvement learning system for quality assurance."""

    def __init__(
        self,
        learning_interval_hours: int = 24,
        insight_confidence_threshold: float = 0.7,
        auto_apply_improvements: bool = True,
    ):
        """
        Initialize continuous improvement system.

        Args:
            learning_interval_hours: Hours between learning cycles
            insight_confidence_threshold: Minimum confidence for insights
            auto_apply_improvements: Enable automatic improvement application
        """
        self.learning_interval_hours = learning_interval_hours
        self.insight_confidence_threshold = insight_confidence_threshold
        self.auto_apply_improvements = auto_apply_improvements

        # Learning data storage
        self.quality_history: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
        self.validation_patterns: Dict[str, int] = defaultdict(int)
        self.feedback_data: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, List[float]] = defaultdict(list)

        # Learning models (simplified ML components)
        self.pattern_detector = PatternDetector()
        self.feedback_analyzer = FeedbackAnalyzer()
        self.trend_analyzer = TrendAnalyzer()

        # Improvement tracking
        self.active_improvements: List[ImprovementAction] = []
        self.completed_improvements: List[ImprovementAction] = []

    async def start_learning_cycle(self) -> LearningReport:
        """
        Execute a complete learning cycle.

        Returns:
            Comprehensive learning report with insights and recommendations
        """
        start_time = datetime.now()
        end_time = start_time - timedelta(hours=self.learning_interval_hours)

        # Collect recent data
        recent_data = await self._collect_recent_data(end_time, start_time)

        # Generate insights
        insights = await self._generate_insights(recent_data)

        # Analyze trends
        trends = await self._analyze_quality_trends(recent_data)

        # Determine improvement actions
        improvement_actions = await self._determine_improvement_actions(insights, trends)

        # Calculate quality score change
        quality_change = self._calculate_quality_score_change(recent_data)

        # Generate key findings and recommendations
        key_findings = self._extract_key_findings(insights, trends)
        recommendations = self._generate_recommendations(insights, trends, improvement_actions)

        # Determine next learning focus
        next_focus = self._determine_next_learning_focus(insights, trends)

        # Create report
        report = LearningReport(
            report_period=(end_time, start_time),
            insights=insights,
            trends=trends,
            improvement_actions=improvement_actions,
            quality_score_change=quality_change,
            key_findings=key_findings,
            recommendations=recommendations,
            next_learning_focus=next_focus,
        )

        # Apply automatic improvements if enabled
        if self.auto_apply_improvements:
            await self._apply_automatic_improvements(improvement_actions)

        # Store report and learning data
        await self._store_learning_report(report)
        await self._update_learning_models(recent_data)

        return report

    async def _collect_recent_data(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Collect recent quality data from all sources."""
        recent_data = {
            "validation_results": await self._collect_validation_data(start_time, end_time),
            "performance_metrics": await self._collect_performance_data(start_time, end_time),
            "user_feedback": await self._collect_feedback_data(start_time, end_time),
            "security_scans": await self._collect_security_data(start_time, end_time),
            "compliance_reports": await self._collect_compliance_data(start_time, end_time),
        }

        return recent_data

    async def _collect_validation_data(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Collect validation data from MCP storage."""
        try:
            # In a real implementation, you'd query MCP storage
            # For now, return simulated data
            return [
                {
                    "skill_name": f"skill_{i}",
                    "timestamp": start_time + timedelta(hours=i),
                    "validation_type": "zero_hallucination",
                    "score": np.random.uniform(0.7, 1.0),
                    "violations": np.random.randint(0, 5),
                }
                for i in range(10)
            ]
        except Exception:
            return []

    async def _collect_performance_data(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Collect performance metrics data."""
        return [
            {
                "skill_name": f"skill_{i}",
                "timestamp": start_time + timedelta(hours=i),
                "execution_time": np.random.uniform(0.1, 2.0),
                "memory_usage": np.random.uniform(50, 500),
                "error_rate": np.random.uniform(0, 0.1),
            }
            for i in range(10)
        ]

    async def _collect_feedback_data(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Collect user feedback data."""
        return [
            {
                "skill_name": f"skill_{i}",
                "timestamp": start_time + timedelta(hours=i),
                "rating": np.random.randint(1, 6),
                "feedback_text": f"Sample feedback for skill {i}",
                "category": np.random.choice(["performance", "accuracy", "usability"]),
            }
            for i in range(5)
        ]

    async def _collect_security_data(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Collect security scan data."""
        return [
            {
                "skill_name": f"skill_{i}",
                "timestamp": start_time + timedelta(hours=i),
                "vulnerabilities_found": np.random.randint(0, 10),
                "risk_score": np.random.uniform(0, 10),
            }
            for i in range(8)
        ]

    async def _collect_compliance_data(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Collect compliance validation data."""
        return [
            {
                "skill_name": f"skill_{i}",
                "timestamp": start_time + timedelta(hours=i),
                "compliance_score": np.random.uniform(0.6, 1.0),
                "violations_count": np.random.randint(0, 15),
            }
            for i in range(8)
        ]

    async def _generate_insights(self, data: Dict[str, Any]) -> List[LearningInsight]:
        """Generate learning insights from collected data."""
        insights = []

        # Pattern recognition insights
        pattern_insights = await self.pattern_detector.detect_patterns(data)
        insights.extend(pattern_insights)

        # Feedback analysis insights
        feedback_insights = await self.feedback_analyzer.analyze_feedback(data.get("user_feedback", []))
        insights.extend(feedback_insights)

        # Performance optimization insights
        performance_insights = self._analyze_performance_patterns(data.get("performance_metrics", []))
        insights.extend(performance_insights)

        # Security trend insights
        security_insights = self._analyze_security_trends(data.get("security_scans", []))
        insights.extend(security_insights)

        # Compliance evolution insights
        compliance_insights = self._analyze_compliance_evolution(data.get("compliance_reports", []))
        insights.extend(compliance_insights)

        # Filter by confidence threshold
        filtered_insights = [insight for insight in insights if insight.confidence >= self.insight_confidence_threshold]

        return filtered_insights

    async def _analyze_quality_trends(self, data: Dict[str, Any]) -> List[QualityTrend]:
        """Analyze quality trends over time."""
        trends = []

        # Analyze validation score trends
        validation_trend = await self.trend_analyzer.analyze_trend(
            data.get("validation_results", []), "validation_score", "validation accuracy over time"
        )
        if validation_trend:
            trends.append(validation_trend)

        # Analyze performance trends
        performance_trend = await self.trend_analyzer.analyze_trend(
            data.get("performance_metrics", []), "execution_time", "performance execution time trends"
        )
        if performance_trend:
            trends.append(performance_trend)

        # Analyze user satisfaction trends
        satisfaction_trend = await self.trend_analyzer.analyze_trend(
            data.get("user_feedback", []), "rating", "user satisfaction trends"
        )
        if satisfaction_trend:
            trends.append(satisfaction_trend)

        return trends

    async def _determine_improvement_actions(
        self, insights: List[LearningInsight], trends: List[QualityTrend]
    ) -> List[ImprovementAction]:
        """Determine improvement actions based on insights and trends."""
        actions = []

        # Generate actions from insights
        for insight in insights:
            action = self._create_action_from_insight(insight)
            if action:
                actions.append(action)

        # Generate actions from trends
        for trend in trends:
            if trend.trend_direction == "degrading" and trend.trend_strength > 0.5:
                action = self._create_action_from_trend(trend)
                if action:
                    actions.append(action)

        # Prioritize actions
        actions = self._prioritize_actions(actions)

        return actions

    def _create_action_from_insight(self, insight: LearningInsight) -> Optional[ImprovementAction]:
        """Create improvement action from learning insight."""
        if insight.learning_type == LearningType.PATTERN_RECOGNITION:
            return ImprovementAction(
                action_id=f"pattern_{insight.insight_id}",
                improvement_type=ImprovementType.NEW_PATTERN_DETECTION,
                title=f"Address Pattern: {insight.title}",
                description=insight.description,
                priority="high" if insight.impact_score > 0.7 else "medium",
                target_skill_patterns=insight.metadata.get("affected_skills", []),
                implementation_steps=[
                    "Update validation rules",
                    "Add new pattern detection",
                    "Train team on new patterns",
                ],
                expected_impact=insight.impact_score,
            )
        elif insight.learning_type == LearningType.PERFORMANCE_OPTIMIZATION:
            return ImprovementAction(
                action_id=f"perf_{insight.insight_id}",
                improvement_type=ImprovementType.PERFORMANCE_TUNING,
                title=f"Performance Optimization: {insight.title}",
                description=insight.description,
                priority="medium",
                target_skill_patterns=insight.metadata.get("affected_skills", []),
                implementation_steps=[
                    "Analyze performance bottlenecks",
                    "Implement optimization strategies",
                    "Monitor improvements",
                ],
                expected_impact=insight.impact_score,
            )

        return None

    def _create_action_from_trend(self, trend: QualityTrend) -> Optional[ImprovementAction]:
        """Create improvement action from quality trend."""
        if trend.trend_direction == "degrading":
            return ImprovementAction(
                action_id=f"trend_{trend.metric_name}",
                improvement_type=ImprovementType.THRESHOLD_ADJUSTMENT,
                title=f"Address Degrading Trend: {trend.metric_name}",
                description=trend.analysis_summary,
                priority="high",
                target_skill_patterns=["all"],
                implementation_steps=[
                    "Investigate root cause of degradation",
                    "Adjust validation thresholds",
                    "Implement corrective measures",
                ],
                expected_impact=trend.trend_strength,
            )

        return None

    def _prioritize_actions(self, actions: List[ImprovementAction]) -> List[ImprovementAction]:
        """Prioritize improvement actions."""
        priority_scores = {"high": 3, "medium": 2, "low": 1}

        return sorted(actions, key=lambda x: (priority_scores.get(x.priority, 0), x.expected_impact), reverse=True)

    def _calculate_quality_score_change(self, data: Dict[str, Any]) -> float:
        """Calculate overall quality score change."""
        # Simplified calculation - in practice would use weighted metrics
        validation_scores = [d.get("score", 0) for d in data.get("validation_results", [])]
        compliance_scores = [d.get("compliance_score", 0) for d in data.get("compliance_reports", [])]
        satisfaction_scores = [d.get("rating", 0) / 5.0 for d in data.get("user_feedback", [])]

        all_scores = validation_scores + compliance_scores + satisfaction_scores

        if not all_scores:
            return 0.0

        current_avg = statistics.mean(all_scores)
        # In practice, you'd compare with historical average
        baseline_avg = 0.8

        return current_avg - baseline_avg

    def _extract_key_findings(self, insights: List[LearningInsight], trends: List[QualityTrend]) -> List[str]:
        """Extract key findings from insights and trends."""
        findings = []

        # Top insights
        top_insights = sorted(insights, key=lambda x: x.impact_score, reverse=True)[:3]
        for insight in top_insights:
            findings.append(f"{insight.title}: {insight.description[:100]}...")

        # Significant trends
        significant_trends = [t for t in trends if t.trend_strength > 0.6]
        for trend in significant_trends:
            findings.append(f"{trend.metric_name} is {trend.trend_direction} with strength {trend.trend_strength:.2f}")

        return findings

    def _generate_recommendations(
        self, insights: List[LearningInsight], trends: List[QualityTrend], actions: List[ImprovementAction]
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Recommend top priority actions
        high_priority_actions = [a for a in actions if a.priority == "high"][:3]
        for action in high_priority_actions:
            recommendations.append(f"Priority: {action.title}")

        # Recommend focus areas based on insights
        insight_types = Counter(insight.learning_type for insight in insights)
        most_common_type = insight_types.most_common(1)[0][0] if insight_types else None

        if most_common_type:
            if most_common_type == LearningType.PERFORMANCE_OPTIMIZATION:
                recommendations.append("Focus on performance optimization across skills")
            elif most_common_type == LearningType.PATTERN_RECOGNITION:
                recommendations.append("Enhance validation patterns and detection")
            elif most_common_type == LearningType.FEEDBACK_ANALYSIS:
                recommendations.append("Address user feedback and satisfaction issues")

        # General recommendations
        recommendations.append("Continue monitoring quality metrics and trends")
        recommendations.append("Implement high-priority improvement actions")
        recommendations.append("Review and update quality standards regularly")

        return recommendations

    def _determine_next_learning_focus(self, insights: List[LearningInsight], trends: List[QualityTrend]) -> List[str]:
        """Determine areas for next learning focus."""
        focus_areas = []

        # Based on insights confidence and impact
        low_confidence_high_impact = [
            insight for insight in insights if insight.confidence < 0.8 and insight.impact_score > 0.7
        ]

        if low_confidence_high_impact:
            focus_areas.append("Gather more data for high-impact, low-confidence insights")

        # Based on trend volatility
        volatile_trends = [t for t in trends if t.trend_strength > 0.8]
        if volatile_trends:
            focus_areas.append(f"Investigate volatile trends: {[t.metric_name for t in volatile_trends]}")

        # Based on improvement action effectiveness
        if self.completed_improvements:
            # Analyze which improvement types were most effective
            effective_types = Counter(a.improvement_type for a in self.completed_improvements[-5:])
            if effective_types:
                focus_areas.append(f"Focus on {effective_types.most_common(1)[0][0].value} improvements")

        return focus_areas

    async def _apply_automatic_improvements(self, actions: List[ImprovementAction]):
        """Apply automatic improvements where possible."""
        for action in actions:
            if action.priority == "high" and action.improvement_type in [
                ImprovementType.THRESHOLD_ADJUSTMENT,
                ImprovementType.VALIDATION_RULE_UPDATE,
            ]:
                try:
                    success = await self._apply_improvement(action)
                    if success:
                        action.status = "completed"
                        self.completed_improvements.append(action)
                    else:
                        action.status = "failed"
                except Exception:
                    action.status = "failed"

    async def _apply_improvement(self, action: ImprovementAction) -> bool:
        """Apply a specific improvement action."""
        try:
            if action.improvement_type == ImprovementType.THRESHOLD_ADJUSTMENT:
                # Adjust validation thresholds
                return await self._adjust_validation_thresholds(action)
            elif action.improvement_type == ImprovementType.VALIDATION_RULE_UPDATE:
                # Update validation rules
                return await self._update_validation_rules(action)
            elif action.improvement_type == ImprovementType.PERFORMANCE_TUNING:
                # Apply performance optimizations
                return await self._apply_performance_optimizations(action)
        except Exception:
            return False

        return False

    async def _adjust_validation_thresholds(self, action: ImprovementAction) -> bool:
        """Adjust validation thresholds based on learning."""
        # Implementation would adjust thresholds in validation components
        await store_result(
            namespace="improvements",
            key=f"threshold_adjustment_{action.action_id}",
            data={"action": action.__dict__, "timestamp": datetime.now().isoformat(), "status": "applied"},
        )
        return True

    async def _update_validation_rules(self, action: ImprovementAction) -> bool:
        """Update validation rules based on new patterns."""
        # Implementation would update rules in validators
        await store_result(
            namespace="improvements",
            key=f"rule_update_{action.action_id}",
            data={"action": action.__dict__, "timestamp": datetime.now().isoformat(), "status": "applied"},
        )
        return True

    async def _apply_performance_optimizations(self, action: ImprovementAction) -> bool:
        """Apply performance optimizations."""
        # Implementation would apply optimizations to performance monitor
        await store_result(
            namespace="improvements",
            key=f"performance_opt_{action.action_id}",
            data={"action": action.__dict__, "timestamp": datetime.now().isoformat(), "status": "applied"},
        )
        return True

    def _analyze_performance_patterns(self, performance_data: List[Dict]) -> List[LearningInsight]:
        """Analyze performance patterns for insights."""
        insights = []

        if not performance_data:
            return insights

        # Analyze execution time patterns
        execution_times = [d.get("execution_time", 0) for d in performance_data]
        if execution_times:
            avg_time = statistics.mean(execution_times)
            if avg_time > 1.5:  # High execution time threshold
                insights.append(
                    LearningInsight(
                        insight_id="perf_high_execution_time",
                        learning_type=LearningType.PERFORMANCE_OPTIMIZATION,
                        title="High Average Execution Time",
                        description=f"Average execution time is {avg_time:.2f}s, exceeding optimal threshold",
                        confidence=0.8,
                        evidence=[f"Average: {avg_time:.2f}s"],
                        recommendation="Optimize algorithms and reduce computational complexity",
                        impact_score=0.7,
                        timestamp=datetime.now(),
                        metadata={"avg_execution_time": avg_time},
                    )
                )

        return insights

    def _analyze_security_trends(self, security_data: List[Dict]) -> List[LearningInsight]:
        """Analyze security trends for insights."""
        insights = []

        if not security_data:
            return insights

        # Analyze vulnerability patterns
        total_vulnerabilities = sum(d.get("vulnerabilities_found", 0) for d in security_data)
        avg_vulnerabilities = total_vulnerabilities / len(security_data)

        if avg_vulnerabilities > 5:  # High vulnerability threshold
            insights.append(
                LearningInsight(
                    insight_id="sec_high_vulnerabilities",
                    learning_type=LearningType.PATTERN_RECOGNITION,
                    title="High Security Vulnerability Count",
                    description=f"Average {avg_vulnerabilities:.1f} vulnerabilities found per skill",
                    confidence=0.9,
                    evidence=[f"Average vulnerabilities: {avg_vulnerabilities:.1f}"],
                    recommendation="Enhance security scanning and implement secure coding practices",
                    impact_score=0.8,
                    timestamp=datetime.now(),
                    metadata={"avg_vulnerabilities": avg_vulnerabilities},
                )
            )

        return insights

    def _analyze_compliance_evolution(self, compliance_data: List[Dict]) -> List[LearningInsight]:
        """Analyze compliance evolution for insights."""
        insights = []

        if not compliance_data:
            return insights

        # Analyze compliance score trends
        compliance_scores = [d.get("compliance_score", 0) for d in compliance_data]
        avg_compliance = statistics.mean(compliance_scores)

        if avg_compliance < 0.8:  # Low compliance threshold
            insights.append(
                LearningInsight(
                    insight_id="comp_low_compliance",
                    learning_type=LearningType.STANDARDS_EVOLUTION,
                    title="Low Compliance Score",
                    description=f"Average compliance score is {avg_compliance:.2f}, below target",
                    confidence=0.85,
                    evidence=[f"Average compliance: {avg_compliance:.2f}"],
                    recommendation="Review and update coding standards, provide additional training",
                    impact_score=0.6,
                    timestamp=datetime.now(),
                    metadata={"avg_compliance": avg_compliance},
                )
            )

        return insights

    async def _store_learning_report(self, report: LearningReport):
        """Store learning report in MCP storage."""
        serialized_report = {
            "report_period": {"start": report.report_period[0].isoformat(), "end": report.report_period[1].isoformat()},
            "insights": [
                {
                    "insight_id": insight.insight_id,
                    "learning_type": insight.learning_type.value,
                    "title": insight.title,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "evidence": insight.evidence,
                    "recommendation": insight.recommendation,
                    "impact_score": insight.impact_score,
                    "timestamp": insight.timestamp.isoformat(),
                    "metadata": insight.metadata,
                }
                for insight in report.insights
            ],
            "trends": [
                {
                    "metric_name": trend.metric_name,
                    "trend_direction": trend.trend_direction,
                    "trend_strength": trend.trend_strength,
                    "analysis_summary": trend.analysis_summary,
                }
                for trend in report.trends
            ],
            "improvement_actions": [
                {
                    "action_id": action.action_id,
                    "improvement_type": action.improvement_type.value,
                    "title": action.title,
                    "description": action.description,
                    "priority": action.priority,
                    "status": action.status,
                    "expected_impact": action.expected_impact,
                }
                for action in report.improvement_actions
            ],
            "quality_score_change": report.quality_score_change,
            "key_findings": report.key_findings,
            "recommendations": report.recommendations,
            "next_learning_focus": report.next_learning_focus,
            "timestamp": datetime.now().isoformat(),
        }

        await store_result(
            namespace="continuous_improvement",
            key=f"learning_report_{datetime.now().isoformat()}",
            data=serialized_report,
        )

    async def _update_learning_models(self, data: Dict[str, Any]):
        """Update learning models with new data."""
        # Update pattern detector
        await self.pattern_detector.update_patterns(data)

        # Update feedback analyzer
        await self.feedback_analyzer.update_feedback_model(data.get("user_feedback", []))

        # Store updated model data
        model_data = {
            "pattern_detector_state": self.pattern_detector.get_state(),
            "feedback_analyzer_state": self.feedback_analyzer.get_state(),
            "timestamp": datetime.now().isoformat(),
        }

        await store_result(
            namespace="learning_models", key=f"model_update_{datetime.now().isoformat()}", data=model_data
        )


class PatternDetector:
    """Simplified pattern detection for learning insights."""

    def __init__(self):
        self.patterns = {}
        self.pattern_counts = defaultdict(int)

    async def detect_patterns(self, data: Dict[str, Any]) -> List[LearningInsight]:
        """Detect patterns in validation and quality data."""
        insights = []

        # Analyze validation patterns
        validation_data = data.get("validation_results", [])
        if validation_data:
            insights.extend(self._detect_validation_patterns(validation_data))

        # Analyze performance patterns
        performance_data = data.get("performance_metrics", [])
        if performance_data:
            insights.extend(self._detect_performance_patterns(performance_data))

        return insights

    def _detect_validation_patterns(self, validation_data: List[Dict]) -> List[LearningInsight]:
        """Detect patterns in validation results."""
        insights = []

        # Pattern: recurring validation failures
        failure_patterns = defaultdict(int)
        for result in validation_data:
            if result.get("violations", 0) > 0:
                failure_patterns[result.get("skill_name", "unknown")] += 1

        if failure_patterns:
            most_failing = max(failure_patterns.items(), key=lambda x: x[1])
            if most_failing[1] > 2:  # More than 2 failures
                insights.append(
                    LearningInsight(
                        insight_id="pattern_recurring_failures",
                        learning_type=LearningType.PATTERN_RECOGNITION,
                        title="Recurring Validation Failures",
                        description=f"Skill {most_failing[0]} has {most_failing[1]} validation failures",
                        confidence=0.8,
                        evidence=[f"Most failing skill: {most_failing[0]} ({most_failing[1]} failures)"],
                        recommendation="Investigate root cause of recurring failures in skill",
                        impact_score=0.6,
                        timestamp=datetime.now(),
                        metadata={"skill_name": most_failing[0], "failure_count": most_failing[1]},
                    )
                )

        return insights

    def _detect_performance_patterns(self, performance_data: List[Dict]) -> List[LearningInsight]:
        """Detect patterns in performance data."""
        insights = []

        # Pattern: performance degradation
        if len(performance_data) > 1:
            recent_half = performance_data[len(performance_data) // 2 :]
            early_half = performance_data[: len(performance_data) // 2]

            recent_avg = statistics.mean(d.get("execution_time", 0) for d in recent_half)
            early_avg = statistics.mean(d.get("execution_time", 0) for d in early_half)

            if recent_avg > early_avg * 1.2:  # 20% degradation
                insights.append(
                    LearningInsight(
                        insight_id="pattern_performance_degradation",
                        learning_type=LearningType.PERFORMANCE_OPTIMIZATION,
                        title="Performance Degradation Pattern",
                        description=f"Execution time increased by {((recent_avg / early_avg - 1) * 100):.1f}%",
                        confidence=0.7,
                        evidence=[f"Recent avg: {recent_avg:.2f}s, Early avg: {early_avg:.2f}s"],
                        recommendation="Investigate performance regression causes",
                        impact_score=0.5,
                        timestamp=datetime.now(),
                        metadata={"recent_avg": recent_avg, "early_avg": early_avg},
                    )
                )

        return insights

    async def update_patterns(self, data: Dict[str, Any]):
        """Update pattern detection with new data."""
        # Update internal pattern counts
        for result in data.get("validation_results", []):
            skill_name = result.get("skill_name", "unknown")
            self.pattern_counts[skill_name] += 1

    def get_state(self) -> Dict[str, Any]:
        """Get current pattern detector state."""
        return {"patterns": self.patterns, "pattern_counts": dict(self.pattern_counts)}


class FeedbackAnalyzer:
    """Simplified feedback analysis for learning insights."""

    def __init__(self):
        self.feedback_history = []
        self.sentiment_patterns = {}

    async def analyze_feedback(self, feedback_data: List[Dict]) -> List[LearningInsight]:
        """Analyze user feedback for insights."""
        insights = []

        if not feedback_data:
            return insights

        # Analyze satisfaction trends
        ratings = [f.get("rating", 0) for f in feedback_data]
        avg_rating = statistics.mean(ratings)

        if avg_rating < 3.5:  # Low satisfaction threshold
            insights.append(
                LearningInsight(
                    insight_id="feedback_low_satisfaction",
                    learning_type=LearningType.FEEDBACK_ANALYSIS,
                    title="Low User Satisfaction",
                    description=f"Average user rating is {avg_rating:.1f}/5.0",
                    confidence=0.9,
                    evidence=[f"Average rating: {avg_rating:.1f}/5.0"],
                    recommendation="Investigate user concerns and improve skill quality",
                    impact_score=0.8,
                    timestamp=datetime.now(),
                    metadata={"avg_rating": avg_rating, "total_feedback": len(feedback_data)},
                )
            )

        # Analyze feedback categories
        categories = [f.get("category", "general") for f in feedback_data]
        category_counts = Counter(categories)

        if category_counts:
            most_common_category = category_counts.most_common(1)[0]
            insights.append(
                LearningInsight(
                    insight_id="feedback_category_pattern",
                    learning_type=LearningType.FEEDBACK_ANALYSIS,
                    title=f"Common Feedback Category: {most_common_category[0]}",
                    description=f"Most feedback relates to {most_common_category[0]} ({most_common_category[1]} mentions)",
                    confidence=0.7,
                    evidence=[f"Category: {most_common_category[0]} ({most_common_category[1]} times)"],
                    recommendation=f"Focus improvements on {most_common_category[0]} aspects",
                    impact_score=0.6,
                    timestamp=datetime.now(),
                    metadata={"category": most_common_category[0], "count": most_common_category[1]},
                )
            )

        return insights

    async def update_feedback_model(self, feedback_data: List[Dict]):
        """Update feedback analysis model with new data."""
        self.feedback_history.extend(feedback_data)
        # In a more complex implementation, you'd update ML models here

    def get_state(self) -> Dict[str, Any]:
        """Get current feedback analyzer state."""
        return {"feedback_count": len(self.feedback_history), "sentiment_patterns": self.sentiment_patterns}


class TrendAnalyzer:
    """Simplified trend analysis for quality metrics."""

    async def analyze_trend(self, data: List[Dict], metric_name: str, description: str) -> Optional[QualityTrend]:
        """Analyze trend for a specific metric."""
        if not data or len(data) < 2:
            return None

        # Extract metric values and timestamps
        data_points = []
        for item in data:
            timestamp = item.get("timestamp")
            value = item.get(metric_name)
            if timestamp and value is not None:
                data_points.append((timestamp, value))

        if len(data_points) < 2:
            return None

        # Sort by timestamp
        data_points.sort(key=lambda x: x[0])

        # Calculate trend direction and strength
        values = [point[1] for point in data_points]
        if len(values) >= 3:
            # Simple linear regression for trend
            n = len(values)
            x = list(range(n))
            sum_x = sum(x)
            sum_y = sum(values)
            sum_xy = sum(x[i] * values[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)

            # Determine trend direction
            if slope > 0.01:
                trend_direction = "improving"
            elif slope < -0.01:
                trend_direction = "degrading"
            else:
                trend_direction = "stable"

            # Calculate trend strength (normalized slope)
            trend_strength = min(abs(slope) * 10, 1.0)  # Normalize to 0-1

            # Generate analysis summary
            if trend_direction == "improving":
                summary = f"{metric_name} is improving with strength {trend_strength:.2f}"
            elif trend_direction == "degrading":
                summary = f"{metric_name} is degrading with strength {trend_strength:.2f}"
            else:
                summary = f"{metric_name} is stable"

            return QualityTrend(
                metric_name=metric_name,
                time_period=(data_points[0][0], data_points[-1][0]),
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                data_points=data_points,
                analysis_summary=summary,
            )

        return None
