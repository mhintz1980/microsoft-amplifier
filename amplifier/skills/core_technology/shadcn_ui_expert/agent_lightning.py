"""
Agent Lightning Integration for ShadCN/ui Expert

Continuous learning and optimization system that learns from usage patterns
and improves component recommendations and code generation over time.
"""

import time
from collections import Counter
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any


class LearningType(Enum):
    """Types of learning patterns."""

    COMPONENT_USAGE = "component_usage"
    ERROR_PREVENTION = "error_prevention"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ACCESSIBILITY_IMPROVEMENT = "accessibility_improvement"
    USER_PREFERENCE = "user_preference"
    BEST_PRACTICE = "best_practice"


class OptimizationLevel(Enum):
    """Levels of optimization."""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class LearningMetric:
    """Represents a learning metric for tracking improvements."""

    metric_type: LearningType
    component: str
    value: float
    timestamp: float
    context: dict[str, Any] = field(default_factory=dict)
    improvement_suggestion: str = ""


@dataclass
class PerformancePattern:
    """Represents a learned performance pattern."""

    pattern_id: str
    description: str
    component_types: list[str]
    optimization_applied: str
    improvement_percentage: float
    usage_count: int
    success_rate: float


@dataclass
class ErrorPattern:
    """Represents a learned error prevention pattern."""

    error_type: str
    component: str
    frequency: int
    prevention_strategy: str
    automated_fix: str
    success_rate: float


class AgentLightningIntegration:
    """
    Agent Lightning integration for continuous learning and optimization.

    Provides:
    - Component usage pattern learning
    - Error prevention and correction
    - Performance optimization recommendations
    - Accessibility improvement tracking
    - User preference adaptation
    - Best practice evolution
    """

    def __init__(self):
        self.learning_metrics = []
        self.performance_patterns = []
        self.error_patterns = []
        self.user_preferences = defaultdict(list)
        self.component_stats = defaultdict(lambda: {"usage": 0, "success": 0, "errors": 0})
        self.optimization_history = []

        # Initialize with common patterns
        self._init_common_patterns()

    def _init_common_patterns(self):
        """Initialize with common ShadCN/ui patterns."""
        self.performance_patterns = [
            PerformancePattern(
                pattern_id="form_validation_optimization",
                description="Optimize form components with efficient validation",
                component_types=["Form", "Input", "Textarea"],
                optimization_applied="useCallback + debounced validation",
                improvement_percentage=35.0,
                usage_count=0,
                success_rate=0.95,
            ),
            PerformancePattern(
                pattern_id="table_virtualization",
                description="Apply virtualization to large data tables",
                component_types=["Table", "DataTable"],
                optimization_applied="react-window + memoization",
                improvement_percentage=60.0,
                usage_count=0,
                success_rate=0.98,
            ),
            PerformancePattern(
                pattern_id="dialog_lazy_loading",
                description="Lazy load dialog content for better initial load",
                component_types=["Dialog", "Sheet"],
                optimization_applied="React.lazy + Suspense",
                improvement_percentage=25.0,
                usage_count=0,
                success_rate=0.92,
            ),
            PerformancePattern(
                pattern_id="component_memoization",
                description="Memoize expensive component calculations",
                component_types=["Chart", "DataTable", "Card"],
                optimization_applied="useMemo + React.memo",
                improvement_percentage=40.0,
                usage_count=0,
                success_rate=0.89,
            ),
        ]

        self.error_patterns = [
            ErrorPattern(
                error_type="missing_aria_label",
                component="Button",
                frequency=15,
                prevention_strategy="Auto-generate aria-label for icon-only buttons",
                automated_fix='aria-label={{action || "Button action"}}',
                success_rate=0.98,
            ),
            ErrorPattern(
                error_type="missing_form_label",
                component="Input",
                frequency=12,
                prevention_strategy="Auto-generate label from field name",
                automated_fix="<Label htmlFor={id}>{label}</Label>",
                success_rate=0.95,
            ),
            ErrorPattern(
                error_type="focus_management",
                component="Dialog",
                frequency=8,
                prevention_strategy="Auto-add focus management",
                automated_fix="useEffect(() => { /* focus logic */ }, [])",
                success_rate=0.97,
            ),
            ErrorPattern(
                error_type="keyboard_navigation",
                component="DropdownMenu",
                frequency=10,
                prevention_strategy="Auto-add keyboard event handlers",
                automated_fix="onKeyDown={handleKeyDown}",
                success_rate=0.94,
            ),
        ]

    def record_generation(self, component_type: str, features: list[str], success: bool = True):
        """Record component generation for learning."""
        self.component_stats[component_type]["usage"] += 1
        if success:
            self.component_stats[component_type]["success"] += 1
        else:
            self.component_stats[component_type]["errors"] += 1

        metric = LearningMetric(
            metric_type=LearningType.COMPONENT_USAGE,
            component=component_type,
            value=1 if success else 0,
            timestamp=time.time(),
            context={"features": features},
        )
        self.learning_metrics.append(metric)

        # Learn from usage patterns
        self._analyze_usage_patterns(component_type, features, success)

    def record_error(self, component_type: str, error_type: str, context: dict[str, Any]):
        """Record component error for learning and prevention."""
        self.component_stats[component_type]["errors"] += 1

        metric = LearningMetric(
            metric_type=LearningType.ERROR_PREVENTION,
            component=component_type,
            value=1,  # Error count
            timestamp=time.time(),
            context={"error_type": error_type, **context},
        )
        self.learning_metrics.append(metric)

        # Update error patterns
        self._update_error_patterns(component_type, error_type)

    def record_optimization(self, component_type: str, optimization: str, improvement: float):
        """Record performance optimization for learning."""
        metric = LearningMetric(
            metric_type=LearningType.PERFORMANCE_OPTIMIZATION,
            component=component_type,
            value=improvement,
            timestamp=time.time(),
            context={"optimization": optimization},
        )
        self.learning_metrics.append(metric)

        # Update optimization history
        self.optimization_history.append(
            {
                "component": component_type,
                "optimization": optimization,
                "improvement": improvement,
                "timestamp": time.time(),
            }
        )

        self._update_performance_patterns(component_type, optimization, improvement)

    def record_preference(self, user_id: str, preference: dict[str, Any]):
        """Record user preference for personalization."""
        self.user_preferences[user_id].append({"preference": preference, "timestamp": time.time()})

        metric = LearningMetric(
            metric_type=LearningType.USER_PREFERENCE,
            component="user",
            value=1,
            timestamp=time.time(),
            context={"user_id": user_id, "preference": preference},
        )
        self.learning_metrics.append(metric)

    def get_optimization_recommendations(self, component_type: str, current_code: str) -> list[dict[str, Any]]:
        """
        Get optimization recommendations based on learned patterns.

        Args:
            component_type: Type of component to optimize
            current_code: Current component implementation

        Returns:
            List of optimization recommendations
        """
        recommendations = []

        # Check against known performance patterns
        for pattern in self.performance_patterns:
            if component_type in pattern.component_types:
                if pattern.success_rate > 0.9 and pattern.improvement_percentage > 20:
                    recommendations.append(
                        {
                            "type": "performance",
                            "pattern_id": pattern.pattern_id,
                            "description": pattern.description,
                            "optimization": pattern.optimization_applied,
                            "expected_improvement": pattern.improvement_percentage,
                            "confidence": pattern.success_rate,
                            "usage_count": pattern.usage_count,
                        }
                    )

        # Analyze current code for specific optimizations
        code_recommendations = self._analyze_code_for_optimizations(component_type, current_code)
        recommendations.extend(code_recommendations)

        # Sort by confidence and expected improvement
        recommendations.sort(key=lambda x: (x["confidence"], x["expected_improvement"]), reverse=True)

        return recommendations[:5]  # Return top 5 recommendations

    def get_error_prevention_strategies(self, component_type: str) -> list[dict[str, Any]]:
        """
        Get error prevention strategies based on learned patterns.

        Args:
            component_type: Type of component to get strategies for

        Returns:
            List of error prevention strategies
        """
        strategies = []

        for pattern in self.error_patterns:
            if pattern.component == component_type:
                strategies.append(
                    {
                        "error_type": pattern.error_type,
                        "frequency": pattern.frequency,
                        "prevention_strategy": pattern.prevention_strategy,
                        "automated_fix": pattern.automated_fix,
                        "success_rate": pattern.success_rate,
                    }
                )

        # Sort by frequency and success rate
        strategies.sort(key=lambda x: (x["frequency"], x["success_rate"]), reverse=True)

        return strategies

    def get_component_insights(self, component_type: str) -> dict[str, Any]:
        """
        Get comprehensive insights about a component type.

        Args:
            component_type: Type of component to analyze

        Returns:
            Comprehensive component insights
        """
        stats = self.component_stats[component_type]
        total_usage = stats["usage"]
        success_rate = stats["success"] / total_usage if total_usage > 0 else 0

        # Get recent metrics
        recent_metrics = [
            m
            for m in self.learning_metrics
            if m.component == component_type and time.time() - m.timestamp < 86400 * 7  # Last 7 days
        ]

        # Analyze feature usage
        feature_usage = Counter()
        for metric in recent_metrics:
            if metric.context.get("features"):
                feature_usage.update(metric.context["features"])

        # Get popular patterns
        error_strategies = self.get_error_prevention_strategies(component_type)
        optimization_recommendations = self.get_optimization_recommendations(component_type, "")

        return {
            "component": component_type,
            "usage_stats": {
                "total_usage": total_usage,
                "success_rate": success_rate,
                "error_rate": 1 - success_rate,
                "recent_usage": len(recent_metrics),
            },
            "popular_features": feature_usage.most_common(5),
            "common_errors": [s["error_type"] for s in error_strategies[:3]],
            "top_optimizations": optimization_recommendations[:3],
            "trend": self._calculate_usage_trend(component_type),
            "recommendations": self._generate_component_recommendations(component_type, stats),
        }

    def _analyze_usage_patterns(self, component_type: str, features: list[str], success: bool):
        """Analyze component usage patterns for learning."""
        # Track feature success rates
        for feature in features:
            feature_key = f"{component_type}:{feature}"
            if not hasattr(self, "feature_stats"):
                self.feature_stats = defaultdict(lambda: {"usage": 0, "success": 0})

            self.feature_stats[feature_key]["usage"] += 1
            if success:
                self.feature_stats[feature_key]["success"] += 1

    def _update_error_patterns(self, component_type: str, error_type: str):
        """Update error patterns based on new errors."""
        for pattern in self.error_patterns:
            if pattern.component == component_type and pattern.error_type == error_type:
                pattern.frequency += 1
                return

        # Add new error pattern
        self.error_patterns.append(
            ErrorPattern(
                error_type=error_type,
                component=component_type,
                frequency=1,
                prevention_strategy="Needs analysis",
                automated_fix="",
                success_rate=0.0,
            )
        )

    def _update_performance_patterns(self, component_type: str, optimization: str, improvement: float):
        """Update performance patterns based on new optimizations."""
        for pattern in self.performance_patterns:
            if component_type in pattern.component_types and optimization in pattern.optimization_applied:
                pattern.usage_count += 1
                # Update improvement percentage with weighted average
                pattern.improvement_percentage = (
                    pattern.improvement_percentage * pattern.usage_count + improvement
                ) / (pattern.usage_count + 1)
                return

        # Add new performance pattern if significant
        if improvement > 15:
            new_pattern = PerformancePattern(
                pattern_id=f"custom_{int(time.time())}",
                description=f"Custom optimization for {component_type}",
                component_types=[component_type],
                optimization_applied=optimization,
                improvement_percentage=improvement,
                usage_count=1,
                success_rate=0.9,
            )
            self.performance_patterns.append(new_pattern)

    def _analyze_code_for_optimizations(self, component_type: str, code: str) -> list[dict[str, Any]]:
        """Analyze code for specific optimization opportunities."""
        recommendations = []

        # Check for missing optimizations
        if "useCallback" not in code and "onClick" in code:
            recommendations.append(
                {
                    "type": "performance",
                    "description": "Add useCallback for event handlers",
                    "optimization": "Wrap event handlers in useCallback",
                    "expected_improvement": 15,
                    "confidence": 0.8,
                }
            )

        if "useMemo" not in code and ".map(" in code:
            recommendations.append(
                {
                    "type": "performance",
                    "description": "Add useMemo for mapped arrays",
                    "optimization": "Wrap map operation in useMemo",
                    "expected_improvement": 20,
                    "confidence": 0.75,
                }
            )

        if "React.memo" not in code and component_type in ["Card", "ListItem"]:
            recommendations.append(
                {
                    "type": "performance",
                    "description": "Add React.memo for component optimization",
                    "optimization": "Wrap component in React.memo",
                    "expected_improvement": 25,
                    "confidence": 0.7,
                }
            )

        return recommendations

    def _calculate_usage_trend(self, component_type: str) -> str:
        """Calculate usage trend for a component."""
        # Get last 30 days of metrics
        thirty_days_ago = time.time() - 86400 * 30
        recent_metrics = [
            m for m in self.learning_metrics if m.component == component_type and m.timestamp > thirty_days_ago
        ]

        if len(recent_metrics) < 2:
            return "insufficient_data"

        # Calculate trend based on usage frequency
        usage_by_day = defaultdict(int)
        for metric in recent_metrics:
            day = int(metric.timestamp // 86400)
            usage_by_day[day] += 1

        if len(usage_by_day) < 7:
            return "insufficient_data"

        # Simple trend calculation
        days = sorted(usage_by_day.keys())
        recent_week = sum(usage_by_day[day] for day in days[-7:])
        previous_week = sum(usage_by_day[day] for day in days[-14:-7]) if len(days) >= 14 else 0

        if previous_week == 0:
            return "increasing"

        change = (recent_week - previous_week) / previous_week
        if change > 0.2:
            return "increasing"
        if change < -0.2:
            return "decreasing"
        return "stable"

    def _generate_component_recommendations(self, component_type: str, stats: dict[str, Any]) -> list[str]:
        """Generate recommendations for component improvement."""
        recommendations = []

        success_rate = stats["success"] / stats["usage"] if stats["usage"] > 0 else 0

        if success_rate < 0.8:
            recommendations.append("Focus on improving component reliability and error handling")

        if stats["usage"] < 10:
            recommendations.append("Consider promoting this component more in documentation")

        error_rate = 1 - success_rate
        if error_rate > 0.2:
            recommendations.append("High error rate detected - review error prevention strategies")

        return recommendations

    def export_learning_data(self) -> dict[str, Any]:
        """Export learning data for backup and analysis."""
        return {
            "learning_metrics": [
                {
                    "type": metric.metric_type.value,
                    "component": metric.component,
                    "value": metric.value,
                    "timestamp": metric.timestamp,
                    "context": metric.context,
                }
                for metric in self.learning_metrics
            ],
            "component_stats": dict(self.component_stats),
            "performance_patterns": [
                {
                    "pattern_id": pattern.pattern_id,
                    "description": pattern.description,
                    "component_types": pattern.component_types,
                    "optimization_applied": pattern.optimization_applied,
                    "improvement_percentage": pattern.improvement_percentage,
                    "usage_count": pattern.usage_count,
                    "success_rate": pattern.success_rate,
                }
                for pattern in self.performance_patterns
            ],
            "error_patterns": [
                {
                    "error_type": pattern.error_type,
                    "component": pattern.component,
                    "frequency": pattern.frequency,
                    "prevention_strategy": pattern.prevention_strategy,
                    "automated_fix": pattern.automated_fix,
                    "success_rate": pattern.success_rate,
                }
                for pattern in self.error_patterns
            ],
            "optimization_history": self.optimization_history,
            "export_timestamp": time.time(),
        }

    def get_learning_summary(self) -> dict[str, Any]:
        """Get summary of learning and optimization achievements."""
        if not self.learning_metrics:
            return {
                "total_metrics": 0,
                "components_analyzed": 0,
                "optimizations_applied": 0,
                "errors_prevented": 0,
                "average_improvement": 0,
            }

        total_metrics = len(self.learning_metrics)
        components_analyzed = len(set(m.component for m in self.learning_metrics))

        optimization_metrics = [
            m for m in self.learning_metrics if m.metric_type == LearningType.PERFORMANCE_OPTIMIZATION
        ]
        error_metrics = [m for m in self.learning_metrics if m.metric_type == LearningType.ERROR_PREVENTION]

        average_improvement = (
            sum(m.value for m in optimization_metrics) / len(optimization_metrics) if optimization_metrics else 0
        )

        return {
            "total_metrics": total_metrics,
            "components_analyzed": components_analyzed,
            "optimizations_applied": len(optimization_metrics),
            "errors_prevented": len(error_metrics),
            "average_improvement": average_improvement,
            "most_optimized_component": self._get_most_optimized_component(),
            "top_performance_patterns": self._get_top_performance_patterns(),
            "common_error_patterns": self._get_common_error_patterns(),
        }

    def _get_most_optimized_component(self) -> str:
        """Get the component with most optimizations."""
        component_optimizations = defaultdict(int)
        for metric in self.learning_metrics:
            if metric.metric_type == LearningType.PERFORMANCE_OPTIMIZATION:
                component_optimizations[metric.component] += 1

        return max(component_optimizations.items(), key=lambda x: x[1])[0] if component_optimizations else "None"

    def _get_top_performance_patterns(self) -> list[dict[str, Any]]:
        """Get top performing patterns."""
        return sorted(
            [
                {
                    "pattern_id": p.pattern_id,
                    "description": p.description,
                    "improvement": p.improvement_percentage,
                    "usage_count": p.usage_count,
                }
                for p in self.performance_patterns
            ],
            key=lambda x: x["improvement"] * x["usage_count"],
            reverse=True,
        )[:5]

    def _get_common_error_patterns(self) -> list[dict[str, Any]]:
        """Get most common error patterns."""
        return sorted(
            [
                {
                    "component": p.component,
                    "error_type": p.error_type,
                    "frequency": p.frequency,
                    "success_rate": p.success_rate,
                }
                for p in self.error_patterns
            ],
            key=lambda x: x["frequency"],
            reverse=True,
        )[:5]
