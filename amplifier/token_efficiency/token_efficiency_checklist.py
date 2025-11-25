#!/usr/bin/env python3
"""
Token Efficiency Checklist - Always Check Most Efficient Approaches First

CRITICAL: Before any tool execution, research task type and use most token-efficient method.
This prevents wasting tokens on expensive operations when cheaper alternatives exist.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TokenEfficiencyOption:
    """Represents a token-efficient approach for a task."""

    method_name: str
    estimated_tokens: int
    estimated_time_seconds: int
    confidence_level: str  # high, medium, low
    pros: List[str]
    cons: List[str]
    tools_required: List[str]


class TokenEfficiencyManager:
    """
    Manages token-efficient decision making for all operations.

    ALWAYS use this before launching expensive agents or tools.
    """

    def __init__(self):
        self.efficiency_cache = {}
        self.token_thresholds = {
            "quick_check": 5000,  # 5k tokens or less
            "standard_task": 15000,  # 15k tokens or less
            "heavy_analysis": 50000,  # 50k tokens or less
            "critical_decision": 100000,  # 100k tokens maximum
        }

    def analyze_task_efficiency(
        self, task_description: str, task_type: str
    ) -> Tuple[TokenEfficiencyOption, List[TokenEfficiencyOption]]:
        """
        Analyze a task and return the most efficient approach + alternatives.

        Args:
            task_description: What needs to be done
            task_type: Type of task (research, analysis, implementation, etc.)

        Returns:
            Tuple of (best_option, alternative_options)
        """
        # Use efficient task classification first
        task_category = self._classify_task_efficiently(task_description, task_type)

        # Get efficiency options based on task category
        options = self._get_efficiency_options(task_category, task_description)

        # Score options for token efficiency
        scored_options = self._score_options_for_efficiency(options)

        # Sort by efficiency score (lower tokens, higher confidence)
        sorted_options = sorted(scored_options, key=lambda x: (x.estimated_tokens, x.confidence_level != "high"))

        return sorted_options[0], sorted_options[1:]

    def _classify_task_efficiently(self, task_description: str, task_type: str) -> str:
        """Efficiently classify task without expensive processing."""
        # Quick keyword-based classification (minimal tokens)
        desc_lower = task_description.lower()
        type_lower = task_type.lower()

        if any(word in desc_lower for word in ["research", "analyze repository", "github repo", "investigate"]):
            return "repository_research"
        elif any(word in desc_lower for word in ["design", "architecture", "plan", "strategy"]):
            return "planning_design"
        elif any(word in desc_lower for word in ["implement", "build", "create", "develop"]):
            return "implementation"
        elif any(word in desc_lower for word in ["test", "validate", "verify", "check"]):
            return "validation"
        elif any(word in desc_lower for word in ["fix", "debug", "troubleshoot", "error"]):
            return "debugging"
        else:
            return "general_task"

    def _get_efficiency_options(self, task_category: str, task_description: str) -> List[TokenEfficiencyOption]:
        """Get token-efficient options for task category."""

        if task_category == "repository_research":
            return [
                TokenEfficiencyOption(
                    method_name="GitHub API Analysis",
                    estimated_tokens=2000,
                    estimated_time_seconds=30,
                    confidence_level="high",
                    pros=["Fast", "Accurate", "Token-efficient", "Real-time data"],
                    cons=["Limited to public repos", "Requires GitHub token"],
                    tools_required=["curl", "jq", "git"],
                ),
                TokenEfficiencyOption(
                    method_name="GitHub CLI Tools",
                    estimated_tokens=5000,
                    estimated_time_seconds=120,
                    confidence_level="high",
                    pros=["Comprehensive", "Familiar interface", "No API limits"],
                    cons=["More tokens", "Requires installation"],
                    tools_required=["gh", "git"],
                ),
                TokenEfficiencyOption(
                    method_name="LLM Research Agent",
                    estimated_tokens=25000,
                    estimated_time_seconds=300,
                    confidence_level="medium",
                    pros=["Deep analysis", "Contextual understanding"],
                    cons=["Expensive", "Slower", "Variable quality"],
                    tools_required=["claude", "anthropic"],
                ),
            ]

        elif task_category == "planning_design":
            return [
                TokenEfficiencyOption(
                    method_name="Template-Based Planning",
                    estimated_tokens=3000,
                    estimated_time_seconds=60,
                    confidence_level="high",
                    pros=["Fast", "Consistent", "Proven patterns"],
                    cons=["Less creative", "Template limitations"],
                    tools_required=["existing_templates", "make"],
                ),
                TokenEfficiencyOption(
                    method_name="Targeted LLM Architecture",
                    estimated_tokens=8000,
                    estimated_time_seconds=180,
                    confidence_level="high",
                    pros=["Contextual", "Flexible", "Good quality"],
                    cons=["More expensive", "Requires prompt engineering"],
                    tools_required=["claude", "templates"],
                ),
            ]

        elif task_category == "implementation":
            return [
                TokenEfficiencyOption(
                    method_name="Existing Tool Integration",
                    estimated_tokens=1000,
                    estimated_time_seconds=30,
                    confidence_level="high",
                    pros=["Instant", "Zero tokens for new logic", "Proven"],
                    cons=["Limited to existing functionality"],
                    tools_required=["existing_tools", "make"],
                ),
                TokenEfficiencyOption(
                    method_name="Minimal Code Generation",
                    estimated_tokens=5000,
                    estimated_time_seconds=120,
                    confidence_level="medium",
                    pros=["Custom solution", "Efficient generation"],
                    cons=["Requires testing", "Integration effort"],
                    tools_required=["claude", "test_framework"],
                ),
            ]

        elif task_category == "validation":
            return [
                TokenEfficiencyOption(
                    method_name="Automated Testing",
                    estimated_tokens=500,
                    estimated_time_seconds=15,
                    confidence_level="high",
                    pros=["Fast", "Reliable", "Zero LLM cost"],
                    cons=["Requires existing tests"],
                    tools_required=["pytest", "make check"],
                ),
                TokenEfficiencyOption(
                    method_name="Targeted Validation",
                    estimated_tokens=3000,
                    estimated_time_seconds=90,
                    confidence_level="medium",
                    pros=["Contextual validation", "Good coverage"],
                    cons=["Expensive for routine checks"],
                    tools_required=["claude", "test_cases"],
                ),
            ]

        # Default general task options
        return [
            TokenEfficiencyOption(
                method_name="Direct Implementation",
                estimated_tokens=2000,
                estimated_time_seconds=60,
                confidence_level="medium",
                pros=["Fast", "No external dependencies"],
                cons=["Limited scope", "Manual effort"],
                tools_required=["existing_tools"],
            ),
            TokenEfficiencyOption(
                method_name="Efficient LLM Assistance",
                estimated_tokens=8000,
                estimated_time_seconds=180,
                confidence_level="medium",
                pros=["Contextual help", "Problem solving"],
                cons=["Token cost", "Variable quality"],
                tools_required=["claude"],
            ),
        ]

    def _score_options_for_efficiency(self, options: List[TokenEfficiencyOption]) -> List[TokenEfficiencyOption]:
        """Score options for token efficiency."""
        scored_options = []

        for option in options:
            # Calculate efficiency score (lower is better)
            token_score = option.estimated_tokens
            time_score = option.estimated_time_seconds

            # Confidence bonus (high confidence gets bonus)
            confidence_bonus = 0
            if option.confidence_level == "high":
                confidence_bonus = -1000  # Bonus for high confidence
            elif option.confidence_level == "low":
                confidence_bonus = 2000  # Penalty for low confidence

            # Total score (lower is better)
            total_score = token_score + time_score + confidence_bonus

            # Store score in option for debugging
            option._efficiency_score = total_score
            scored_options.append(option)

        return scored_options

    def check_agent_efficiency(self, agent_name: str, task_description: str) -> Tuple[bool, str]:
        """
        Check if an agent is the most efficient approach for a task.

        Args:
            agent_name: Name of the agent being considered
            task_description: Description of the task

        Returns:
            Tuple of (is_most_efficient, recommendation)
        """
        # Analyze the task for efficiency
        best_option, alternatives = self.analyze_task_efficiency(task_description, "agent_task")

        # Check if expensive agent is being used when cheaper alternatives exist
        expensive_agents = ["integration-specialist", "zen-architect", "bug-hunter", "performance-optimizer"]
        is_expensive = any(agent in agent_name.lower() for agent in expensive_agents)

        if is_expensive and best_option.estimated_tokens < 10000:
            return (
                False,
                f"Use '{best_option.method_name}' instead (saves {183600 - best_option.estimated_tokens} tokens)",
            )

        return True, f"Agent '{agent_name}' is appropriate for this task"

    def get_token_efficiency_report(self, task_description: str, task_type: str) -> str:
        """
        Generate a token efficiency report for a task.

        Args:
            task_description: What needs to be done
            task_type: Type of task

        Returns:
            Formatted efficiency report
        """
        best_option, alternatives = self.analyze_task_efficiency(task_description, task_type)

        report = f"""📊 TOKEN EFFICIENCY REPORT

Task: {task_description}
Type: {task_type}

🎯 MOST EFFICIENT APPROACH:
Method: {best_option.method_name}
Estimated Tokens: {best_option.estimated_tokens:,}
Estimated Time: {best_option.estimated_time_seconds}s
Confidence: {best_option.confidence_level}

✅ Advantages:
"""

        for pro in best_option.pro:
            report += f"  • {pro}\n"

        report += f"""
❌ Disadvantages:
"""

        for con in best_option.cons:
            report += f"  • {con}\n"

        report += f"""
🔧 Tools Required: {", ".join(best_option.tools_required)}

💰 TOKEN SAVINGS: Up to {183600 - best_option.estimated_tokens:,} tokens compared to expensive agent usage

📋 ALTERNATIVES:
"""

        for alt in alternatives[:2]:  # Show top 2 alternatives
            report += f"""• {alt.method_name} ({alt.estimated_tokens:,} tokens, {alt.confidence_level} confidence)
"""

        return report


# Global instance for easy access
token_efficiency_manager = TokenEfficiencyManager()


def check_token_efficiency_first(task_description: str, task_type: str = "general") -> Tuple[bool, str]:
    """
    Quick efficiency check function to use before any tool execution.

    Args:
        task_description: What you're about to do
        task_type: Type of task (optional)

    Returns:
        Tuple of (is_efficient, recommendation)
    """
    best_option, _ = token_efficiency_manager.analyze_task_efficiency(task_description, task_type)

    # If the most efficient approach uses <10k tokens, it's probably efficient
    if best_option.estimated_tokens <= 10000:
        return True, f"Efficient approach: {best_option.method_name} ({best_option.estimated_tokens:,} tokens)"
    else:
        # Check if we're about to use an expensive agent when cheaper alternatives exist
        expensive_threshold = 15000
        if best_option.estimated_tokens > expensive_threshold:
            return (
                False,
                f"Consider cheaper alternative: {best_option.method_name} ({best_option.estimated_tokens:,} tokens)",
            )

        return True, "Approach within acceptable token range"


# Convenience function for common checks
def should_use_expensive_agent(task_description: str, agent_name: str) -> bool:
    """
    Check if an expensive agent is justified for a task.

    Args:
        task_description: Description of the task
        agent_name: Name of the agent being considered

    Returns:
        True if agent is justified, False otherwise
    """
    is_efficient, recommendation = token_efficiency_manager.check_agent_efficiency(agent_name, task_description)

    if not is_efficient:
        logger.warning(f"Token Inefficiency Detected: {recommendation}")
        return False

    return True


if __name__ == "__main__":
    # Test the efficiency manager
    task = "Research Claude-Flow repository for integration possibilities"

    print("🔍 TOKEN EFFICIENCY CHECK")
    print("=" * 50)

    is_efficient, recommendation = check_token_efficiency_first(task, "research")
    print(f"Efficient: {is_efficient}")
    print(f"Recommendation: {recommendation}")

    print("\n📊 FULL ANALYSIS:")
    print(token_efficiency_manager.get_token_efficiency_report(task, "research"))
