"""
Tailwind CSS Agent Lightning Integration

Optimizes Tailwind CSS patterns, performance, and best practices
through continuous learning and pattern analysis.
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, Counter
import re

from ..agent_lightning_integration.performance_monitor import PerformanceMonitor
from ..agent_lightning_integration.knowledge_transfer_system import KnowledgeTransferSystem


@dataclass
class DesignPattern:
    """Represents a learned design pattern."""

    pattern_name: str
    html_structure: str
    tailwind_classes: str
    performance_score: int
    usage_frequency: int
    context_tags: List[str]
    optimization_applied: Optional[str]
    created_at: float


@dataclass
class PerformanceMetrics:
    """Performance metrics for Tailwind usage."""

    bundle_size_trend: List[float]
    render_performance_trend: List[float]
    class_usage_frequency: Dict[str, int]
    error_patterns: List[Dict[str, Any]]
    optimization_success_rate: float


class TailwindAgentLightning:
    """
    Agent Lightning integration for Tailwind CSS expertise.

    Features:
    - Continuous learning from usage patterns
    - Performance optimization through ML-driven insights
    - Pattern recognition and recommendation
    - Knowledge transfer across projects
    - Real-time performance monitoring
    """

    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.knowledge_system = KnowledgeTransferSystem()

        # Learning data storage
        self.learned_patterns: List[DesignPattern] = []
        self.performance_metrics = PerformanceMetrics(
            bundle_size_trend=[],
            render_performance_trend=[],
            class_usage_frequency=defaultdict(int),
            error_patterns=[],
            optimization_success_rate=0.0,
        )

        # Optimization cache
        self.optimization_cache: Dict[str, Any] = {}
        self.pattern_library: Dict[str, DesignPattern] = {}

        # Initialize with baseline knowledge
        self._init_baseline_patterns()
        self._init_performance_benchmarks()

    def _init_baseline_patterns(self):
        """Initialize with proven Tailwind CSS patterns."""
        baseline_patterns = [
            DesignPattern(
                pattern_name="high_performance_card",
                html_structure='<div class="card"><div class="card-content"></div></div>',
                tailwind_classes="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow duration-200",
                performance_score=95,
                usage_frequency=100,
                context_tags=["card", "container", "performance"],
                optimization_applied="minimal_shadow_hover_only",
                created_at=time.time(),
            ),
            DesignPattern(
                pattern_name="optimized_button",
                html_structure='<button><span class="button-text"></span></button>',
                tailwind_classes="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200",
                performance_score=98,
                usage_frequency=150,
                context_tags=["button", "interactive", "accessibility"],
                optimization_applied="focus_ring_transform",
                created_at=time.time(),
            ),
            DesignPattern(
                pattern_name="responsive_navigation",
                html_structure='<nav class="nav-container"><div class="nav-brand"></div><ul class="nav-menu"></ul></nav>',
                tailwind_classes="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40 transition-colors duration-200",
                performance_score=92,
                usage_frequency=80,
                context_tags=["navigation", "responsive", "sticky"],
                optimization_applied="sticky_optimized_zindex",
                created_at=time.time(),
            ),
        ]

        for pattern in baseline_patterns:
            self.pattern_library[pattern.pattern_name] = pattern

    def _init_performance_benchmarks(self):
        """Initialize performance benchmarks for comparison."""
        self.benchmarks = {
            "bundle_size_target": 50000,  # 50KB
            "render_performance_target": 90,  # 90/100 score
            "class_efficiency_target": 0.8,  # 80% usage efficiency
            "accessibility_compliance_target": 0.95,  # 95% compliance
        }

    def analyze_and_optimize_pattern(self, html_content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze HTML content and provide optimized Tailwind CSS recommendations.

        Args:
            html_content: HTML content to analyze
            context: Additional context about usage

        Returns:
            Optimization recommendations and analysis
        """
        start_time = time.time()

        # Extract current Tailwind classes
        current_classes = self._extract_tailwind_classes(html_content)

        # Analyze current usage patterns
        pattern_analysis = self._analyze_usage_patterns(current_classes)

        # Identify optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities(
            current_classes, pattern_analysis, context
        )

        # Generate optimized recommendations
        recommendations = self._generate_optimization_recommendations(
            current_classes, optimization_opportunities, pattern_analysis
        )

        # Learn from this analysis
        self._learn_from_analysis(html_content, current_classes, recommendations)

        execution_time = time.time() - start_time

        return {
            "current_analysis": {
                "classes_count": len(current_classes),
                "unique_classes": len(set(current_classes)),
                "pattern_analysis": pattern_analysis,
            },
            "optimization_opportunities": optimization_opportunities,
            "recommendations": recommendations,
            "performance_impact": self._estimate_performance_impact(recommendations),
            "execution_time": execution_time,
            "confidence_score": self._calculate_confidence_score(recommendations),
        }

    def _extract_tailwind_classes(self, html_content: str) -> List[str]:
        """Extract all Tailwind CSS classes from HTML content."""
        class_pattern = r'(?:class(?:Name)?=["\'])([^"\']*)(?=["\'])'
        classes = []

        matches = re.finditer(class_pattern, html_content)
        for match in matches:
            class_string = match.group(1)
            classes.extend(class_string.split())

        return classes

    def _analyze_usage_patterns(self, classes: List[str]) -> Dict[str, Any]:
        """Analyze usage patterns in Tailwind classes."""
        class_counter = Counter(classes)
        unique_classes = set(classes)

        # Categorize classes by type
        categorized = defaultdict(list)
        for cls in unique_classes:
            category = self._categorize_class(cls)
            categorized[category].append(cls)

        # Analyze responsive variants usage
        responsive_classes = [
            cls for cls in classes if any(cls.startswith(variant) for variant in ["sm:", "md:", "lg:", "xl:", "2xl:"])
        ]
        responsive_usage = len(responsive_classes) / len(classes) if classes else 0

        # Analyze state variants usage
        state_classes = [
            cls
            for cls in classes
            if any(cls.startswith(state) for state in ["hover:", "focus:", "active:", "disabled:"])
        ]
        state_usage = len(state_classes) / len(classes) if classes else 0

        return {
            "total_classes": len(classes),
            "unique_classes": len(unique_classes),
            "most_used": class_counter.most_common(10),
            "categories": dict(categorized),
            "responsive_usage": responsive_usage,
            "state_usage": state_usage,
            "efficiency_score": len(unique_classes) / len(classes) if classes else 0,
        }

    def _categorize_class(self, class_name: str) -> str:
        """Categorize a Tailwind class by its purpose."""
        base_class = self._remove_variants(class_name)

        if any(prefix in base_class for prefix in ["p", "m", "space"]):
            return "spacing"
        elif any(prefix in base_class for prefix in ["w", "h", "max-w", "max-h"]):
            return "sizing"
        elif any(prefix in base_class for prefix in ["bg", "text", "border"]):
            return "colors"
        elif any(prefix in base_class for prefix in ["font", "text", "leading", "tracking"]):
            return "typography"
        elif any(prefix in base_class for prefix in ["flex", "grid", "block"]):
            return "layout"
        elif any(prefix in base_class for prefix in ["rounded", "shadow"]):
            return "styling"
        elif "transition" in base_class or "animate" in base_class:
            return "animation"
        else:
            return "other"

    def _remove_variants(self, class_name: str) -> str:
        """Remove variants from class name for categorization."""
        variants = ["sm:", "md:", "lg:", "xl:", "2xl:", "hover:", "focus:", "active:", "dark:"]
        for variant in variants:
            if class_name.startswith(variant):
                return class_name[len(variant) :]
        return class_name

    def _identify_optimization_opportunities(
        self, classes: List[str], pattern_analysis: Dict[str, Any], context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities."""
        opportunities = []

        # Check for redundant classes
        redundant_classes = self._find_redundant_classes(classes)
        if redundant_classes:
            opportunities.append(
                {
                    "type": "redundant_classes",
                    "description": f"Found {len(redundant_classes)} potentially redundant classes",
                    "details": redundant_classes,
                    "impact": "high",
                }
            )

        # Check for performance-heavy patterns
        performance_issues = self._identify_performance_issues(classes)
        if performance_issues:
            opportunities.append(
                {
                    "type": "performance_optimization",
                    "description": f"Performance-heavy patterns detected: {len(performance_issues)}",
                    "details": performance_issues,
                    "impact": "high",
                }
            )

        # Check for component abstraction opportunities
        if pattern_analysis["total_classes"] > 20:
            opportunities.append(
                {
                    "type": "component_abstraction",
                    "description": "Consider abstracting repeated patterns into components",
                    "suggestion": "Create reusable component classes with @apply",
                    "impact": "medium",
                }
            )

        # Check for responsive optimization
        if pattern_analysis["responsive_usage"] > 0.5:
            opportunities.append(
                {
                    "type": "responsive_optimization",
                    "description": "High responsive usage - potential for optimization",
                    "suggestion": "Consider container queries or CSS custom properties",
                    "impact": "medium",
                }
            )

        # Check for bundle size optimization
        unique_classes = len(set(classes))
        if unique_classes > 100:
            opportunities.append(
                {
                    "type": "bundle_optimization",
                    "description": f"High number of unique classes ({unique_classes}) may impact bundle size",
                    "suggestion": "Review PurgeCSS configuration and content paths",
                    "impact": "high",
                }
            )

        return opportunities

    def _find_redundant_classes(self, classes: List[str]) -> List[str]:
        """Find potentially redundant or conflicting classes."""
        redundant = []
        class_set = set(classes)

        # Check for conflicting display classes
        display_classes = [c for c in class_set if c in ["block", "inline", "flex", "grid", "hidden"]]
        if len(display_classes) > 1:
            redundant.extend(display_classes)

        # Check for redundant spacing
        padding_classes = [
            c for c in class_set if c.startswith("p-") and not any(v in c for v in ["x", "y", "t", "b", "l", "r"])
        ]
        if len(padding_classes) > 1:
            redundant.extend(padding_classes[1:])

        # Check for text size conflicts
        text_sizes = [
            c for c in class_set if c in ["text-xs", "text-sm", "text-base", "text-lg", "text-xl", "text-2xl"]
        ]
        if len(text_sizes) > 1:
            redundant.extend(text_sizes[1:])

        return redundant

    def _identify_performance_issues(self, classes: List[str]) -> List[Dict[str, Any]]:
        """Identify performance-heavy CSS patterns."""
        issues = []

        # Check for expensive properties
        expensive_properties = ["backdrop-filter", "filter", "box-shadow", "text-shadow"]

        for cls in classes:
            base_class = self._remove_variants(cls)
            for prop in expensive_properties:
                if prop in base_class:
                    issues.append(
                        {
                            "class": cls,
                            "property": prop,
                            "severity": "high" if prop == "backdrop-filter" else "medium",
                            "recommendation": self._get_performance_recommendation(prop),
                        }
                    )

        return issues

    def _get_performance_recommendation(self, property_name: str) -> str:
        """Get performance recommendation for a specific property."""
        recommendations = {
            "backdrop-filter": "Consider using opacity + background-color for better performance",
            "filter": "Use sparingly and test on target devices",
            "box-shadow": "Consider CSS containment or simpler shadows",
            "text-shadow": "Use minimal blur values or alternatives",
        }
        return recommendations.get(property_name, "Review usage and test performance")

    def _generate_optimization_recommendations(
        self, classes: List[str], opportunities: List[Dict[str, Any]], pattern_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate specific optimization recommendations."""
        recommendations = []

        # Pattern-based recommendations
        for opportunity in opportunities:
            if opportunity["type"] == "redundant_classes":
                recommendations.append(
                    {
                        "type": "class_cleanup",
                        "title": "Remove Redundant Classes",
                        "description": "Remove conflicting or redundant utility classes",
                        "action": "Review and remove classes: " + ", ".join(opportunity["details"][:5]),
                        "code_example": self._generate_cleanup_example(opportunity["details"]),
                        "estimated_improvement": "10-20% bundle reduction",
                    }
                )

            elif opportunity["type"] == "performance_optimization":
                recommendations.append(
                    {
                        "type": "performance_optimization",
                        "title": "Optimize Performance-Heavy Patterns",
                        "description": "Replace expensive CSS properties with alternatives",
                        "action": "Replace backdrop-filter and heavy filters",
                        "code_example": self._generate_performance_example(opportunity["details"]),
                        "estimated_improvement": "30-50% render performance",
                    }
                )

            elif opportunity["type"] == "component_abstraction":
                recommendations.append(
                    {
                        "type": "component_abstraction",
                        "title": "Abstract Repeated Patterns",
                        "description": "Create reusable component classes",
                        "action": "Define @apply rules for common patterns",
                        "code_example": self._generate_abstraction_example(classes),
                        "estimated_improvement": "20-40% maintainability improvement",
                    }
                )

        # Proactive recommendations based on patterns
        if pattern_analysis["categories"].get("animation", []):
            recommendations.append(
                {
                    "type": "animation_optimization",
                    "title": "Optimize Animations",
                    "description": "Ensure animations use GPU-accelerated properties",
                    "action": "Use transform/opacity instead of width/height",
                    "code_example": """
/* Good: GPU accelerated */
.element { @apply transform translate-x-2 transition-transform; }

/* Avoid: CPU intensive */
.element { @apply w-32 transition-all; }
                """,
                    "estimated_improvement": "50-70% animation performance",
                }
            )

        return recommendations

    def _generate_cleanup_example(self, redundant_classes: List[str]) -> str:
        """Generate code example for class cleanup."""
        example = """
<!-- Before -->
<div class="block flex p-4 p-2 text-sm text-base">
  Content
</div>

<!-- After -->
<div class="flex p-4 text-sm">
  Content
</div>
        """
        return example.strip()

    def _generate_performance_example(self, performance_issues: List[Dict[str, Any]]) -> str:
        """Generate code example for performance optimization."""
        example = """
<!-- Before: Performance heavy -->
<div class="backdrop-filter-blur-md bg-opacity-90">
  Content
</div>

<!-- After: Performance optimized -->
<div class="bg-gray-900 bg-opacity-90">
  Content
</div>
        """
        return example.strip()

    def _generate_abstraction_example(self, classes: List[str]) -> str:
        """Generate code example for component abstraction."""
        example = """
/* CSS with @apply */
.btn-primary {
  @apply px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200;
}

/* HTML usage */
<button class="btn-primary">Click me</button>
        """
        return example.strip()

    def _estimate_performance_impact(self, recommendations: List[Dict[str, Any]]) -> Dict[str, float]:
        """Estimate performance impact of recommendations."""
        impact = {"bundle_size_reduction": 0.0, "render_improvement": 0.0, "maintainability_improvement": 0.0}

        for rec in recommendations:
            if rec["type"] == "class_cleanup":
                impact["bundle_size_reduction"] += 15
            elif rec["type"] == "performance_optimization":
                impact["render_improvement"] += 40
            elif rec["type"] == "component_abstraction":
                impact["maintainability_improvement"] += 30
            elif rec["type"] == "animation_optimization":
                impact["render_improvement"] += 60

        # Cap values at 100%
        for key in impact:
            impact[key] = min(100, impact[key])

        return impact

    def _calculate_confidence_score(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for recommendations."""
        if not recommendations:
            return 100.0

        base_confidence = 80.0

        # Adjust based on recommendation types
        for rec in recommendations:
            if rec["type"] in ["class_cleanup", "performance_optimization"]:
                base_confidence += 5
            elif rec["type"] == "component_abstraction":
                base_confidence += 3

        return min(100, base_confidence)

    def _learn_from_analysis(self, html_content: str, classes: List[str], recommendations: List[Dict[str, Any]]):
        """Learn from analysis to improve future recommendations."""
        # Update class usage frequency
        for cls in classes:
            self.performance_metrics.class_usage_frequency[cls] += 1

        # Identify patterns that led to recommendations
        if len(recommendations) > 2:
            # This was a complex case with many optimization opportunities
            pattern_name = f"complex_pattern_{int(time.time())}"

            pattern = DesignPattern(
                pattern_name=pattern_name,
                html_structure=html_content[:200] + "...",  # Truncated for storage
                tailwind_classes=" ".join(classes[:20]),  # Limit for storage
                performance_score=max(50, 100 - len(recommendations) * 10),
                usage_frequency=1,
                context_tags=["learned", "complex"],
                optimization_applied="auto_generated",
                created_at=time.time(),
            )

            self.learned_patterns.append(pattern)
            self.pattern_library[pattern_name] = pattern

        # Update performance trends (simplified)
        if len(classes) < 20:
            self.performance_metrics.render_performance_trend.append(95)
        else:
            self.performance_metrics.render_performance_trend.append(80)

        # Keep only last 50 data points
        if len(self.performance_metrics.render_performance_trend) > 50:
            self.performance_metrics.render_performance_trend.pop(0)

    def get_optimization_insights(self) -> Dict[str, Any]:
        """Get insights from learned optimization patterns."""
        if not self.learned_patterns:
            return {"message": "No learning data available yet"}

        # Analyze learned patterns
        high_performing_patterns = [p for p in self.learned_patterns if p.performance_score > 85]

        common_contexts = Counter()
        for pattern in self.learned_patterns:
            for tag in pattern.context_tags:
                common_contexts[tag] += 1

        return {
            "total_patterns_learned": len(self.learned_patterns),
            "high_performing_patterns": len(high_performing_patterns),
            "average_performance_score": sum(p.performance_score for p in self.learned_patterns)
            / len(self.learned_patterns),
            "common_contexts": dict(common_contexts.most_common(10)),
            "optimization_success_rate": self.performance_metrics.optimization_success_rate,
            "performance_trend": {
                "average": sum(self.performance_metrics.render_performance_trend)
                / len(self.performance_metrics.render_performance_trend)
                if self.performance_metrics.render_performance_trend
                else 0,
                "latest": self.performance_metrics.render_performance_trend[-1]
                if self.performance_metrics.render_performance_trend
                else 0,
                "trend_direction": "improving"
                if len(self.performance_metrics.render_performance_trend) > 1
                and self.performance_metrics.render_performance_trend[-1]
                > self.performance_metrics.render_performance_trend[-2]
                else "stable",
            },
        }

    def export_knowledge(self) -> Dict[str, Any]:
        """Export learned knowledge for sharing across projects."""
        return {
            "patterns": [asdict(pattern) for pattern in self.pattern_library.values()],
            "performance_metrics": asdict(self.performance_metrics),
            "benchmarks": self.benchmarks,
            "optimization_cache": self.optimization_cache,
            "export_timestamp": time.time(),
        }

    def import_knowledge(self, knowledge_data: Dict[str, Any]) -> bool:
        """Import knowledge from another project or session."""
        try:
            # Import patterns
            if "patterns" in knowledge_data:
                for pattern_data in knowledge_data["patterns"]:
                    pattern = DesignPattern(**pattern_data)
                    self.pattern_library[pattern.pattern_name] = pattern

            # Import performance metrics
            if "performance_metrics" in knowledge_data:
                metrics_data = knowledge_data["performance_metrics"]
                self.performance_metrics = PerformanceMetrics(**metrics_data)

            # Merge optimization cache
            if "optimization_cache" in knowledge_data:
                self.optimization_cache.update(knowledge_data["optimization_cache"])

            return True
        except Exception as e:
            print(f"Error importing knowledge: {e}")
            return False

    def reset_learning_data(self):
        """Reset all learning data (use with caution)."""
        self.learned_patterns.clear()
        self.pattern_library.clear()
        self.optimization_cache.clear()
        self._init_baseline_patterns()
        self._init_performance_benchmarks()
