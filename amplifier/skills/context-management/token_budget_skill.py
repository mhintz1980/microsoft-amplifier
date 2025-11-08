"""
Token Budget Management Skill

Integrates token budget management with the Skills framework for progressive
context loading and intelligent resource allocation.
"""

import time

from ...utils.token_budget_manager import BudgetStatus
from ...utils.token_budget_manager import get_budget_manager
from ..skills_framework import BaseSkill
from ..skills_framework import SkillContext
from ..skills_framework import SkillLevel
from ..skills_framework import SkillResult


class TokenBudgetSkill(BaseSkill):
    """Skill for intelligent token budget management and context optimization."""

    @property
    def description(self) -> str:
        """Clear description of skill functionality."""
        return "Manages token budget with intelligent monitoring and automatic compression"

    @property
    def tags(self) -> list[str]:
        """Tags for skill discovery."""
        return ["token-management", "context-optimization", "budget-monitoring", "compression"]

    def can_handle(self, context: SkillContext) -> float:
        """Determine if this skill can handle the context."""
        query_lower = context.query.lower()

        # High confidence for explicit budget/token queries
        if any(term in query_lower for term in ["token", "budget", "context", "compression"]):
            return 0.9

        # Medium confidence for performance optimization queries
        if any(term in query_lower for term in ["optimize", "efficient", "performance", "memory"]):
            return 0.6

        # Low confidence for general help queries
        if any(term in query_lower for term in ["status", "help", "monitor"]):
            return 0.3

        return 0.0

    def execute(self, context: SkillContext, level: SkillLevel = SkillLevel.SUMMARY) -> SkillResult:
        """Execute the skill at the specified level."""
        import time

        start_time = time.time()

        budget_manager = get_budget_manager()

        if level == SkillLevel.METADATA:
            return self._get_metadata_level(start_time)
        if level == SkillLevel.SUMMARY:
            return self._get_summary_level(budget_manager, start_time, context)
        # FULL level
        return self._get_full_level(budget_manager, start_time, context)

    def _get_metadata_level(self, start_time: float) -> SkillResult:
        """Return minimal metadata about the skill."""
        return SkillResult(
            skill_name=self.skill_name,
            level=SkillLevel.METADATA,
            content="Token budget monitoring and compression management",
            tokens_used=20,
            execution_time=time.time() - start_time,
            metadata={"category": "system", "priority": "high"},
            next_level_available=True,
        )

    def _get_summary_level(self, budget_manager, start_time: float, context: SkillContext) -> SkillResult:
        """Return summary level information."""
        metrics = budget_manager.get_current_metrics()

        # Create concise status summary
        status_summary = (
            f"Token Budget: {metrics.usage_percentage:.1%} used "
            f"({metrics.used_tokens:,}/{metrics.total_tokens:,}) - "
            f"Status: {metrics.status.value.upper()}"
        )

        # Add key recommendations
        recommendations = self._get_key_recommendations(metrics)
        if recommendations:
            status_summary += f"\nRecommendations: {', '.join(recommendations)}"

        return SkillResult(
            skill_name=self.skill_name,
            level=SkillLevel.SUMMARY,
            content=status_summary,
            tokens_used=80,
            execution_time=time.time() - start_time,
            metadata={
                "status": metrics.status.value,
                "usage_percentage": metrics.usage_percentage,
                "recommendations_count": len(recommendations),
            },
            next_level_available=True,
        )

    def _get_full_level(self, budget_manager, start_time: float, context: SkillContext) -> SkillResult:
        """Return full detailed information and actionable advice."""
        metrics = budget_manager.get_current_metrics()

        # Get comprehensive status display
        full_status = budget_manager.get_status_display()

        # Add contextual advice based on available tokens
        contextual_advice = self._get_contextual_advice(budget_manager, metrics, context)

        # Add progressive loading recommendations
        loading_recommendations = self._get_loading_recommendations(budget_manager, context)

        full_content = f"{full_status}\n\n{contextual_advice}\n\n{loading_recommendations}"

        return SkillResult(
            skill_name=self.skill_name,
            level=SkillLevel.FULL,
            content=full_content,
            tokens_used=300,
            execution_time=time.time() - start_time,
            metadata={
                "detailed_status": True,
                "contextual_advice": True,
                "loading_recommendations": True,
                "available_tokens": metrics.available_tokens,
                "compression_events": len(budget_manager.compression_events),
            },
            next_level_available=False,
        )

    def _get_key_recommendations(self, metrics) -> list[str]:
        """Get key recommendations based on current status."""
        recommendations = []

        if metrics.status == BudgetStatus.EMERGENCY:
            recommendations.append("Immediate compression required")
        elif metrics.status == BudgetStatus.CRITICAL:
            recommendations.append("Consider manual compression")
        elif metrics.status == BudgetStatus.WARNING:
            recommendations.append("Monitor usage")

        if metrics.last_operation_tokens > 1000:
            recommendations.append("Reduce operation size")

        return recommendations[:2]  # Return top 2 recommendations

    def _get_contextual_advice(self, budget_manager, metrics, context: SkillContext) -> str:
        """Get advice based on current context and available tokens."""
        advice_parts = []

        # Context-specific advice
        if metrics.available_tokens < 1000:
            advice_parts.append("🚨 Low context budget - request compression immediately")
        elif metrics.available_tokens < 5000:
            advice_parts.append("⚠️ Limited context available - plan operations carefully")

        # Operation-specific advice
        if context.available_tokens < 1000:
            advice_parts.append("📏 Request exceeds available budget - consider breaking into smaller operations")

        # Skills integration advice
        if metrics.status in [BudgetStatus.CRITICAL, BudgetStatus.EMERGENCY]:
            advice_parts.append("🔄 Consider using progressive loading with Skills framework")

        if advice_parts:
            return "CONTEXTUAL ADVICE:\n" + "\n".join(f"   {advice}" for advice in advice_parts)
        return "CONTEXTUAL ADVICE:\n   ✅ Context budget is healthy for continued operations"

    def _get_loading_recommendations(self, budget_manager, context: SkillContext) -> str:
        """Get progressive loading recommendations using Skills framework."""
        recommendations = []

        metrics = budget_manager.get_current_metrics()

        # Recommend progressive loading strategies
        if metrics.usage_percentage > 0.8:
            recommendations.append("📦 Use METADATA level for skill discovery (<50 tokens)")
            recommendations.append("📋 Use SUMMARY level for understanding (<200 tokens)")
            recommendations.append("🔍 Request FULL level only when needed")

        if context.available_tokens < 2000:
            recommendations.append("⚡ Enable progressive disclosure for large content")

        # Recommend specific compression strategies
        if len(budget_manager.operations) > 20:
            recommendations.append("🧹 Consider compressing old operation history")

        if recommendations:
            return "PROGRESSIVE LOADING RECOMMENDATIONS:\n" + "\n".join(f"   {rec}" for rec in recommendations)
        return "PROGRESSIVE LOADING RECOMMENDATIONS:\n   ✅ Current usage allows for full content loading"

    def get_compression_strategies(self) -> dict[str, str]:
        """Get available compression strategies and their descriptions."""
        return {
            "auto": "Automatic compression using optimal strategies",
            "old_operations": "Remove old operation history to save tokens",
            "duplicates": "Compress duplicate operations and entries",
            "low_importance": "Compress low-importance context items",
        }


def register_token_budget_skill():
    """Register the token budget skill with the global registry."""
    from ..skills_framework import register_skill

    register_skill(TokenBudgetSkill())
