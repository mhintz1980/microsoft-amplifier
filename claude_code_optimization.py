"""
Claude Code Optimization Module for Agent-Lightning Integration

This module provides specialized training and optimization capabilities for improving Claude Code's performance through the Agent-Lightning framework.
"""

import json
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic import field_validator


@dataclass
class ClaudeCodeInteraction:
    """Represents a single Claude Code interaction for training."""

    timestamp: str
    user_request: str
    claude_response: str
    tools_used: list[str]
    execution_time: float
    success_rating: float  # 0.0 to 1.0
    user_satisfaction: float | None = None
    error_occurred: bool = False
    error_type: str | None = None


@dataclass
class TrainingMetrics:
    """Training performance metrics."""

    iteration: int
    reward_score: float
    accuracy: float
    efficiency: float
    clarity: float
    safety: float
    timestamp: str


class ClaudeCodeRewardFunction(BaseModel):
    """Reward function for Claude Code optimization."""

    weights: dict[str, float] = {
        "accuracy": 0.3,
        "efficiency": 0.25,
        "clarity": 0.2,
        "safety": 0.15,
        "user_satisfaction": 0.1,
    }

    @field_validator("weights")
    @classmethod
    def validate_weights(cls, v):
        """Ensure weights sum to 1.0."""
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        return v

    def calculate_reward(self, interaction: ClaudeCodeInteraction) -> float:
        """Calculate reward score for a Claude Code interaction."""
        scores = {
            "accuracy": self._calculate_accuracy(interaction),
            "efficiency": self._calculate_efficiency(interaction),
            "clarity": self._calculate_clarity(interaction),
            "safety": self._calculate_safety(interaction),
            "user_satisfaction": self._calculate_user_satisfaction(interaction),
        }

        total_reward = 0.0
        for metric, score in scores.items():
            total_reward += score * self.weights[metric]

        return total_reward

    def _calculate_accuracy(self, interaction: ClaudeCodeInteraction) -> float:
        """Calculate accuracy score based on task completion."""
        if interaction.error_occurred:
            return 0.0
        return interaction.success_rating

    def _calculate_efficiency(self, interaction: ClaudeCodeInteraction) -> float:
        """Calculate efficiency score based on execution time."""
        # Normalize execution time (assuming <30s is ideal)
        ideal_time = 30.0
        if interaction.execution_time <= ideal_time:
            return 1.0
        return max(0.0, ideal_time / interaction.execution_time)

    def _calculate_clarity(self, interaction: ClaudeCodeInteraction) -> float:
        """Calculate clarity score based on response quality."""
        # Simple heuristic based on response length and structure
        response = interaction.claude_response
        if not response:
            return 0.0

        # Check for structured responses
        has_code_blocks = "```" in response
        has_lists = any(marker in response for marker in ["* ", "- ", "1.", "2."])
        has_explanations = len(response.split()) > 50

        clarity_score = 0.0
        if has_code_blocks:
            clarity_score += 0.4
        if has_lists:
            clarity_score += 0.3
        if has_explanations:
            clarity_score += 0.3

        return min(1.0, clarity_score)

    def _calculate_safety(self, interaction: ClaudeCodeInteraction) -> float:
        """Calculate safety score based on error handling."""
        if interaction.error_occurred:
            # Deduct points for errors, but less for recoverable ones
            if interaction.error_type and "recoverable" in interaction.error_type.lower():
                return 0.7
            return 0.3
        return 1.0

    def _calculate_user_satisfaction(self, interaction: ClaudeCodeInteraction) -> float:
        """Calculate user satisfaction score."""
        if interaction.user_satisfaction is not None:
            return interaction.user_satisfaction
        # Default to success rating if no explicit satisfaction
        return interaction.success_rating


class ClaudeCodeOptimizer:
    """Optimizes Claude Code performance using Agent-Lightning principles."""

    def __init__(self, training_data_path: str = "claude_code_training.json"):
        self.training_data_path = Path(training_data_path)
        self.reward_function = ClaudeCodeRewardFunction()
        self.interactions: list[ClaudeCodeInteraction] = []
        self.metrics_history: list[TrainingMetrics] = []
        self.load_training_data()

    def load_training_data(self):
        """Load existing training data."""
        if self.training_data_path.exists():
            try:
                with open(self.training_data_path) as f:
                    data = json.load(f)
                    for item in data.get("interactions", []):
                        self.interactions.append(ClaudeCodeInteraction(**item))
                    for item in data.get("metrics", []):
                        self.metrics_history.append(TrainingMetrics(**item))
                print(f"✅ Loaded {len(self.interactions)} interactions")
            except Exception as e:
                print(f"⚠️  Error loading training data: {e}")

    def save_training_data(self):
        """Save training data to disk."""
        data = {
            "interactions": [asdict(interaction) for interaction in self.interactions],
            "metrics": [asdict(metric) for metric in self.metrics_history],
            "last_updated": datetime.now().isoformat(),
        }

        with open(self.training_data_path, "w") as f:
            json.dump(data, f, indent=2)

    def record_interaction(
        self,
        user_request: str,
        claude_response: str,
        tools_used: list[str],
        execution_time: float,
        success_rating: float,
        user_satisfaction: float | None = None,
        error_occurred: bool = False,
        error_type: str | None = None,
    ) -> float:
        """Record a Claude Code interaction and return reward score."""

        interaction = ClaudeCodeInteraction(
            timestamp=datetime.now().isoformat(),
            user_request=user_request,
            claude_response=claude_response,
            tools_used=tools_used,
            execution_time=execution_time,
            success_rating=success_rating,
            user_satisfaction=user_satisfaction,
            error_occurred=error_occurred,
            error_type=error_type,
        )

        reward = self.reward_function.calculate_reward(interaction)
        self.interactions.append(interaction)
        self.save_training_data()

        return reward

    def get_performance_summary(self) -> dict[str, Any]:
        """Get summary of current performance."""
        if not self.interactions:
            return {"status": "No data available"}

        recent_interactions = self.interactions[-50:]  # Last 50 interactions
        rewards = [self.reward_function.calculate_reward(i) for i in recent_interactions]

        return {
            "total_interactions": len(self.interactions),
            "recent_interactions": len(recent_interactions),
            "average_reward": sum(rewards) / len(rewards),
            "performance_trend": "improving" if len(rewards) > 10 and rewards[-1] > rewards[0] else "stable",
            "top_performing_tools": self._get_top_tools(recent_interactions),
            "common_errors": self._get_common_errors(recent_interactions),
        }

    def _get_top_tools(self, interactions: list[ClaudeCodeInteraction]) -> dict[str, int]:
        """Get most frequently used tools."""
        tool_counts = {}
        for interaction in interactions:
            for tool in interaction.tools_used:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1
        return dict(sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5])

    def _get_common_errors(self, interactions: list[ClaudeCodeInteraction]) -> dict[str, int]:
        """Get most common error types."""
        error_counts = {}
        for interaction in interactions:
            if interaction.error_occurred and interaction.error_type:
                error_counts[interaction.error_type] = error_counts.get(interaction.error_type, 0) + 1
        return error_counts

    def generate_improvement_suggestions(self) -> list[str]:
        """Generate suggestions for performance improvement."""
        summary = self.get_performance_summary()
        suggestions = []

        if summary.get("performance_trend") == "stable":
            suggestions.append("🎯 Consider varying task complexity to enable learning")

        avg_reward = summary.get("average_reward", 0)
        if avg_reward < 0.7:
            suggestions.append("📈 Focus on improving response accuracy and efficiency")

        if summary.get("common_errors"):
            suggestions.append("🔧 Address common error patterns in training")

        tools = summary.get("top_performing_tools", {})
        if len(tools) < 3:
            suggestions.append("🛠️  Expand tool usage diversity")

        return suggestions

    def run_training_cycle(self) -> TrainingMetrics:
        """Run a training cycle and return metrics."""
        if len(self.interactions) < 10:
            raise ValueError("Need at least 10 interactions to run training")

        # Calculate current performance metrics
        recent_interactions = self.interactions[-100:]  # Last 100 interactions
        rewards = [self.reward_function.calculate_reward(i) for i in recent_interactions]

        # Calculate individual metric scores
        accuracy_scores = [self.reward_function._calculate_accuracy(i) for i in recent_interactions]
        efficiency_scores = [self.reward_function._calculate_efficiency(i) for i in recent_interactions]
        clarity_scores = [self.reward_function._calculate_clarity(i) for i in recent_interactions]
        safety_scores = [self.reward_function._calculate_safety(i) for i in recent_interactions]

        metrics = TrainingMetrics(
            iteration=len(self.metrics_history) + 1,
            reward_score=sum(rewards) / len(rewards),
            accuracy=sum(accuracy_scores) / len(accuracy_scores),
            efficiency=sum(efficiency_scores) / len(efficiency_scores),
            clarity=sum(clarity_scores) / len(clarity_scores),
            safety=sum(safety_scores) / len(safety_scores),
            timestamp=datetime.now().isoformat(),
        )

        self.metrics_history.append(metrics)
        self.save_training_data()

        return metrics


# Global optimizer instance
claude_optimizer = ClaudeCodeOptimizer()


def record_claude_interaction(
    user_request: str,
    claude_response: str,
    tools_used: list[str],
    execution_time: float,
    success_rating: float = 1.0,
    user_satisfaction: float | None = None,
    error_occurred: bool = False,
    error_type: str | None = None,
) -> float:
    """Convenience function to record Claude Code interactions."""
    return claude_optimizer.record_interaction(
        user_request=user_request,
        claude_response=claude_response,
        tools_used=tools_used,
        execution_time=execution_time,
        success_rating=success_rating,
        user_satisfaction=user_satisfaction,
        error_occurred=error_occurred,
        error_type=error_type,
    )


def get_claude_performance() -> dict[str, Any]:
    """Get current Claude Code performance summary."""
    return claude_optimizer.get_performance_summary()


def run_claude_optimization() -> TrainingMetrics:
    """Run a Claude Code optimization cycle."""
    return claude_optimizer.run_training_cycle()


if __name__ == "__main__":
    # Example usage
    print("🚀 Claude Code Optimizer - Example Usage")

    # Record a sample interaction
    reward = record_claude_interaction(
        user_request="Help me implement a React component",
        claude_response="Here's how to create a React component with TypeScript...",
        tools_used=["Write", "Read", "Bash"],
        execution_time=15.2,
        success_rating=0.9,
        user_satisfaction=0.95,
    )

    print(f"✅ Recorded interaction with reward: {reward:.3f}")

    # Get performance summary
    summary = get_claude_performance()
    print(f"📊 Performance Summary: {summary}")

    # Get improvement suggestions
    suggestions = claude_optimizer.generate_improvement_suggestions()
    print(f"💡 Suggestions: {suggestions}")
