#!/usr/bin/env python3
"""
Enhanced Claude Status Display with Token Budget Management

Provides comprehensive context monitoring, token efficiency metrics,
and intelligent recommendations for optimal Claude Code performance.
"""

import argparse
import sys
import time
from pathlib import Path

# Add the amplifier directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "amplifier"))

from skills.skills_framework import get_skill_registry

from utils.token_budget_manager import BudgetStatus
from utils.token_budget_manager import get_budget_manager


class StatusEnhancer:
    """Enhanced status display with token budget management integration."""

    def __init__(self):
        self.budget_manager = get_budget_manager()
        self.skill_registry = get_skill_registry()

        # Register token budget skill if not already registered
        self._ensure_token_budget_skill_registered()

    def _ensure_token_budget_skill_registered(self):
        """Ensure the token budget skill is registered."""
        # Check if token budget skill is already registered
        existing_skills = self.skill_registry.get_all_skills()
        token_budget_skill_exists = any(skill.skill_name == "token_budget" for skill in existing_skills)

        if not token_budget_skill_exists:
            from skills.context_management.token_budget_skill import register_token_budget_skill

            register_token_budget_skill()

    def show_status(self, monitor: bool = False, impact_only: bool = False, interval: int = 30):
        """Show enhanced status display."""
        if monitor:
            self._monitor_mode(interval)
        elif impact_only:
            self._show_impact_only()
        else:
            self._show_comprehensive_status()

    def _show_comprehensive_status(self):
        """Show comprehensive status with token budget integration."""
        # Get token budget status
        budget_status = self.budget_manager.get_status_display()

        # Get skills insights
        skills_insights = self._get_skills_insights()

        # Get learning recommendations
        learning_recommendations = self._get_learning_recommendations()

        # Display all information
        print(budget_status)
        print()

        if skills_insights:
            print("🧠 SKILLS FRAMEWORK INSIGHTS:")
            for insight in skills_insights:
                print(f"   {insight}")
            print()

        if learning_recommendations:
            print("📚 LEARNING RECOMMENDATIONS:")
            for rec in learning_recommendations:
                print(f"   {rec}")

    def _show_impact_only(self):
        """Show only the impact of the last operation."""
        self.budget_manager.get_current_metrics()

        if self.budget_manager.operations:
            last_op = self.budget_manager.operations[-1]
            impact_display = f"""
📊 LAST OPERATION IMPACT:
   Operation: {last_op.operation_type}
   Tokens Added: +{last_op.tokens_added} ({last_op.tokens_before} → {last_op.tokens_after})
   Execution Time: {last_op.execution_time:.2f}s
   Efficiency Score: {last_op.efficiency_score:.0f}/100
   Context Impact: {self._calculate_context_impact(last_op)}

💡 IMPACT ANALYSIS:
   {self._analyze_operation_efficiency(last_op)}
"""
            print(impact_display.strip())
        else:
            print("📊 No operations recorded yet")

    def _monitor_mode(self, interval: int):
        """Run in continuous monitoring mode."""
        print(f"🔄 Starting continuous monitoring (every {interval}s)")
        print("Press Ctrl+C to stop monitoring\n")

        try:
            while True:
                # Clear screen (works on most terminals)
                print("\033[2J\033[H", end="")

                # Show timestamp
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"📊 Claude Status Monitor - {timestamp}")
                print("=" * 50)

                # Show comprehensive status
                self._show_comprehensive_status()

                # Wait for next update
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped")

    def _get_skills_insights(self) -> list[str]:
        """Get insights from the Skills framework."""
        insights = []

        metrics = self.budget_manager.get_current_metrics()

        # Check if skills would be beneficial
        if metrics.status in [BudgetStatus.CRITICAL, BudgetStatus.EMERGENCY]:
            insights.append("🎯 Token Budget skill available for immediate assistance")

        # Recommend progressive loading
        if metrics.usage_percentage > 0.7:
            insights.append("📦 Consider progressive loading with Skills framework")

        # Check operation patterns
        if self.budget_manager.operations:
            recent_ops = self.budget_manager.operations[-5:]
            avg_efficiency = sum(op.efficiency_score for op in recent_ops) / len(recent_ops)

            if avg_efficiency < 70:
                insights.append("⚡ Recent operations showing low efficiency - Skills can help optimize")

        return insights

    def _get_learning_recommendations(self) -> list[str]:
        """Get learning recommendations based on current state."""
        recommendations = []
        metrics = self.budget_manager.get_current_metrics()

        # Status-based recommendations
        if metrics.status == BudgetStatus.EMERGENCY:
            recommendations.append("🚨 REVIEW: Check IMPLEMENTATION_PHILOSOPHY.md for context management")
        elif metrics.status == BudgetStatus.CRITICAL:
            recommendations.append("⚠️ LEARN: Study progressive compression techniques")

        # Pattern-based recommendations
        if metrics.last_operation_tokens > 2000:
            recommendations.append("📏 PATTERN: Large operations detected - consider surgical approach")

        # Session-based recommendations
        if metrics.session_duration > 1800:  # 30 minutes
            recommendations.append("⏰ REFLECT: Long session - review patterns and consider break")

        # Efficiency-based recommendations
        recent_efficiency = self._get_recent_efficiency()
        if recent_efficiency < 80:
            recommendations.append("🎯 IMPROVE: Efficiency declining - time for optimization review")

        # Skills framework recommendations
        if len(self.budget_manager.operations) > 10:
            recommendations.append("🧠 GROWTH: Explore Skills framework for better resource management")

        return recommendations

    def _calculate_context_impact(self, operation) -> str:
        """Calculate the context impact of an operation."""
        if operation.tokens_added == 0:
            return "Neutral (no tokens added)"
        if operation.tokens_added < 100:
            return "Minimal impact (efficient operation)"
        if operation.tokens_added < 500:
            return "Low impact (acceptable operation)"
        if operation.tokens_added < 1000:
            return "Moderate impact (watch usage)"
        return "High impact (consider optimization)"

    def _analyze_operation_efficiency(self, operation) -> str:
        """Analyze the efficiency of an operation."""
        analysis_points = []

        # Token efficiency
        if operation.tokens_added <= 100:
            analysis_points.append("Excellent token efficiency")
        elif operation.tokens_added <= 500:
            analysis_points.append("Good token efficiency")
        elif operation.tokens_added <= 1000:
            analysis_points.append("Acceptable token usage")
        else:
            analysis_points.append("High token usage - consider optimization")

        # Time efficiency
        if operation.execution_time <= 5:
            analysis_points.append("Fast execution")
        elif operation.execution_time <= 15:
            analysis_points.append("Reasonable execution time")
        else:
            analysis_points.append("Slow execution - consider breaking into smaller operations")

        # Overall efficiency
        if operation.efficiency_score >= 90:
            analysis_points.append("Excellent overall efficiency")
        elif operation.efficiency_score >= 70:
            analysis_points.append("Good overall efficiency")
        elif operation.efficiency_score >= 50:
            analysis_points.append("Moderate efficiency - room for improvement")
        else:
            analysis_points.append("Low efficiency - review approach")

        return " | ".join(analysis_points)

    def _get_recent_efficiency(self) -> float:
        """Get average efficiency of recent operations."""
        if not self.budget_manager.operations:
            return 100.0

        recent_ops = self.budget_manager.operations[-5:]
        return sum(op.efficiency_score for op in recent_ops) / len(recent_ops)


def main():
    """Main entry point for the status enhancer."""
    parser = argparse.ArgumentParser(description="Enhanced Claude Code status monitoring with token budget management")
    parser.add_argument("--monitor", action="store_true", help="Run in continuous monitoring mode")
    parser.add_argument("--impact", action="store_true", help="Show only the impact of the last operation")
    parser.add_argument("--interval", type=int, default=30, help="Monitoring interval in seconds (default: 30)")

    args = parser.parse_args()

    try:
        enhancer = StatusEnhancer()
        enhancer.show_status(monitor=args.monitor, impact_only=args.impact, interval=args.interval)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
