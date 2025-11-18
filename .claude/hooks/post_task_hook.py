#!/usr/bin/env python3
"""
Post-Task Hook - Pattern Storage and Learning
Stores learnings and updates performance metrics after task completion
"""

import json
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class PostTaskLearner:
    """Learns from task execution and optimizes future performance"""

    def __init__(self):
        self.project_root = project_root
        self.task_end_time = time.time()
        self.learning_data = {}
        self.performance_metrics = {}

    def load_pre_task_result(self) -> dict[str, Any]:
        """Load the pre-task optimization result"""
        try:
            # Try to get from global variable
            global _pre_task_result
            if "_pre_task_result" in globals():
                return globals()["_pre_task_result"]
        except NameError:
            pass

        # Try to load from latest checkpoint
        checkpoint_dir = self.project_root / ".claude" / "session_checkpoints"
        if checkpoint_dir.exists():
            checkpoints = list(checkpoint_dir.glob("pre_task_*.json"))
            if checkpoints:
                latest_checkpoint = max(checkpoints, key=lambda p: p.stat().st_mtime)
                try:
                    with open(latest_checkpoint) as f:
                        return json.load(f)
                except Exception:
                    pass

        return {}

    def analyze_task_outcome(self, task_result: str = "", success: bool = True) -> dict[str, Any]:
        """Analyze the outcome of the task execution"""
        outcome = {
            "success": success,
            "completion_time": self.task_end_time,
            "error_patterns": [],
            "success_patterns": [],
            "performance_issues": [],
            "optimization_effectiveness": {},
            "learnings": [],
        }

        # Analyze task result if provided
        if task_result:
            result_lower = task_result.lower()

            # Look for error patterns
            error_indicators = ["error", "failed", "exception", "traceback", "cannot"]
            for indicator in error_indicators:
                if indicator in result_lower:
                    outcome["error_patterns"].append(indicator)

            # Look for success patterns
            success_indicators = ["success", "completed", "done", "finished", "ready"]
            for indicator in success_indicators:
                if indicator in result_lower:
                    outcome["success_patterns"].append(indicator)

            # Look for performance issues
            performance_indicators = ["slow", "timeout", "hang", "stuck", "long"]
            for indicator in performance_indicators:
                if indicator in result_lower:
                    outcome["performance_issues"].append(indicator)

        # Generate learnings
        if not success:
            outcome["learnings"].append("Task failed - review error handling")
            if outcome["error_patterns"]:
                outcome["learnings"].append(f"Common error: {outcome['error_patterns'][0]}")
        else:
            outcome["learnings"].append("Task completed successfully")
            if outcome["performance_issues"]:
                outcome["learnings"].append(f"Performance concern: {outcome['performance_issues'][0]}")

        return outcome

    def evaluate_optimization_effectiveness(
        self, pre_task_result: dict[str, Any], task_outcome: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate how well the pre-task optimizations worked"""
        effectiveness = {
            "overall_score": 0.5,  # Default to neutral
            "optimization_scores": {},
            "recommendations": [],
        }

        if not pre_task_result:
            effectiveness["recommendations"].append("No pre-task data available for evaluation")
            return effectiveness

        # Base score on task success
        if task_outcome["success"]:
            effectiveness["overall_score"] = 0.7
        else:
            effectiveness["overall_score"] = 0.3

        # Evaluate specific optimizations
        optimizations = pre_task_result.get("optimizations_applied", [])

        for optimization in optimizations:
            score = 0.5  # Neutral score

            # Task-specific optimization evaluation
            if "compression" in optimization:
                if task_outcome["success"]:
                    score = 0.8 if "high" in optimization else 0.7
                else:
                    score = 0.4  # Maybe too much compression

            elif "agents:" in optimization:
                if task_outcome["success"]:
                    score = 0.8
                else:
                    score = 0.3  # Wrong agent selection

            elif "tools" in optimization:
                if task_outcome["success"]:
                    score = 0.7
                else:
                    score = 0.4

            effectiveness["optimization_scores"][optimization] = score

        # Generate recommendations
        for optimization, score in effectiveness["optimization_scores"].items():
            if score < 0.4:
                effectiveness["recommendations"].append(f"Review optimization: {optimization}")
            elif score > 0.7:
                effectiveness["recommendations"].append(f"Effective optimization: {optimization}")

        return effectiveness

    def store_performance_patterns(
        self, pre_task_result: dict[str, Any], task_outcome: dict[str, Any], effectiveness: dict[str, Any]
    ):
        """Store performance patterns for future optimization"""
        patterns = {
            "timestamp": self.task_end_time,
            "task_type": pre_task_result.get("task_analysis", {}).get("type", "unknown"),
            "task_complexity": pre_task_result.get("task_analysis", {}).get("complexity", "medium"),
            "success": task_outcome["success"],
            "optimizations_used": pre_task_result.get("optimizations_applied", []),
            "effectiveness_score": effectiveness["overall_score"],
            "error_patterns": task_outcome.get("error_patterns", []),
            "success_patterns": task_outcome.get("success_patterns", []),
            "learnings": task_outcome.get("learnings", []),
        }

        # Store in patterns file
        patterns_file = self.project_root / ".claude" / "performance_patterns.json"
        existing_patterns = []

        if patterns_file.exists():
            try:
                with open(patterns_file) as f:
                    existing_patterns = json.load(f)
            except Exception:
                existing_patterns = []

        # Add new pattern (keep last 100 patterns)
        existing_patterns.append(patterns)
        if len(existing_patterns) > 100:
            existing_patterns = existing_patterns[-100:]

        # Save patterns
        with open(patterns_file, "w") as f:
            json.dump(existing_patterns, f, indent=2)

        self.learning_data["stored_patterns"] = True

    def update_agent_preferences(self, pre_task_result: dict[str, Any], effectiveness: dict[str, Any]):
        """Update agent preferences based on performance"""
        task_analysis = pre_task_result.get("task_analysis", {})
        recommended_agents = task_analysis.get("recommended_agents", [])

        if not recommended_agents:
            return

        # Load existing agent preferences
        preferences_file = self.project_root / ".claude" / "agent_preferences.json"
        preferences = {}

        if preferences_file.exists():
            try:
                with open(preferences_file) as f:
                    preferences = json.load(f)
            except Exception:
                preferences = {}

        # Update preferences for each agent
        for agent in recommended_agents:
            if agent not in preferences:
                preferences[agent] = {"usage_count": 0, "success_count": 0, "total_score": 0.0, "task_types": {}}

            agent_pref = preferences[agent]
            agent_pref["usage_count"] += 1

            if effectiveness["overall_score"] > 0.6:  # Considered successful
                agent_pref["success_count"] += 1

            agent_pref["total_score"] += effectiveness["overall_score"]

            # Track performance by task type
            task_type = task_analysis.get("type", "unknown")
            if task_type not in agent_pref["task_types"]:
                agent_pref["task_types"][task_type] = {"count": 0, "avg_score": 0.0}

            task_type_pref = agent_pref["task_types"][task_type]
            task_type_pref["count"] += 1

            # Update average score
            current_avg = task_type_pref["avg_score"]
            task_type_pref["avg_score"] = (
                current_avg * (task_type_pref["count"] - 1) + effectiveness["overall_score"]
            ) / task_type_pref["count"]

        # Save updated preferences
        with open(preferences_file, "w") as f:
            json.dump(preferences, f, indent=2)

        self.learning_data["agent_preferences_updated"] = True

    def create_post_task_checkpoint(
        self, pre_task_result: dict[str, Any], task_outcome: dict[str, Any], effectiveness: dict[str, Any]
    ):
        """Create checkpoint after task completion"""
        checkpoint_data = {
            "task_end": self.task_end_time,
            "task_success": task_outcome["success"],
            "effectiveness_score": effectiveness["overall_score"],
            "optimizations_evaluated": len(effectiveness["optimization_scores"]),
            "learnings_extracted": len(task_outcome.get("learnings", [])),
            "patterns_stored": self.learning_data.get("stored_patterns", False),
            "agent_preferences_updated": self.learning_data.get("agent_preferences_updated", False),
        }

        checkpoint_dir = self.project_root / ".claude" / "session_checkpoints"
        checkpoint_dir.mkdir(exist_ok=True)

        checkpoint_file = checkpoint_dir / f"post_task_{int(self.task_end_time)}.json"
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint_data, f, indent=2)

    def generate_learning_summary(
        self, pre_task_result: dict[str, Any], task_outcome: dict[str, Any], effectiveness: dict[str, Any]
    ) -> str:
        """Generate summary of learnings from the task"""
        summary_parts = []

        # Task outcome
        status = "✅ Success" if task_outcome["success"] else "❌ Failed"
        summary_parts.append(f"Task: {status}")

        # Effectiveness
        score = effectiveness["overall_score"]
        if score > 0.7:
            summary_parts.append("Optimizations: Highly Effective")
        elif score > 0.5:
            summary_parts.append("Optimizations: Moderately Effective")
        else:
            summary_parts.append("Optimizations: Need Review")

        # Key learnings
        if task_outcome.get("learnings"):
            key_learning = task_outcome["learnings"][0]
            summary_parts.append(f"Key Learning: {key_learning}")

        return " | ".join(summary_parts)

    def optimize_future_tasks(self, pre_task_result: dict[str, Any], effectiveness: dict[str, Any]) -> list[str]:
        """Generate recommendations for future task optimization"""
        recommendations = []

        task_analysis = pre_task_result.get("task_analysis", {})
        task_type = task_analysis.get("type", "unknown")

        # Based on effectiveness, suggest changes
        if effectiveness["overall_score"] < 0.5:
            recommendations.append(f"Consider different approach for {task_type} tasks")

        # Look at specific optimization scores
        for optimization, score in effectiveness["optimization_scores"].items():
            if score < 0.4:
                if "compression" in optimization:
                    recommendations.append("Reduce context compression for similar tasks")
                elif "agents:" in optimization:
                    recommendations.append("Review agent selection for this task type")
                elif "tools" in optimization:
                    recommendations.append("Update tool preparation for this domain")

        # Add success patterns
        if task_analysis.get("success_patterns"):
            recommendations.append("Leverage success patterns in future tasks")

        return recommendations


def learn_from_task(task_result: str = "", success: bool = True) -> dict[str, Any]:
    """Main function to learn from task execution"""
    learner = PostTaskLearner()

    # Load pre-task result
    pre_task_result = learner.load_pre_task_result()

    # Analyze task outcome
    task_outcome = learner.analyze_task_outcome(task_result, success)

    # Evaluate optimization effectiveness
    effectiveness = learner.evaluate_optimization_effectiveness(pre_task_result, task_outcome)

    # Store performance patterns
    learner.store_performance_patterns(pre_task_result, task_outcome, effectiveness)

    # Update agent preferences
    learner.update_agent_preferences(pre_task_result, effectiveness)

    # Create checkpoint
    learner.create_post_task_checkpoint(pre_task_result, task_outcome, effectiveness)

    # Generate summary
    summary = learner.generate_learning_summary(pre_task_result, task_outcome, effectiveness)

    # Generate recommendations
    recommendations = learner.optimize_future_tasks(pre_task_result, effectiveness)

    result = {
        "learned": True,
        "task_outcome": task_outcome,
        "effectiveness": effectiveness,
        "learning_data": learner.learning_data,
        "summary": summary,
        "recommendations": recommendations,
    }

    return result


def main():
    """Main post-task learning"""
    # Get task result from environment or stdin
    task_result = ""
    success = True

    # Try to read from environment variables
    import os

    if "CLAUDE_TASK_RESULT" in os.environ:
        task_result = os.environ["CLAUDE_TASK_RESULT"]
    if "CLAUDE_TASK_SUCCESS" in os.environ:
        success = os.environ["CLAUDE_TASK_SUCCESS"].lower() in ["true", "1", "yes"]

    # Try to read from stdin
    if not task_result:
        try:
            import sys

            task_result = sys.stdin.read().strip()
        except OSError:
            task_result = ""

    print("📚 Post-Task Learning and Optimization...")

    if not task_result:
        print("   No task result provided, assuming success")
        task_result = "Task completed"

    result = learn_from_task(task_result, success)

    if result["learned"]:
        print(f"   ✅ Learning captured: {result['summary']}")

        if result["recommendations"]:
            print("   💡 Recommendations for future tasks:")
            for rec in result["recommendations"][:3]:  # Show top 3
                print(f"      • {rec}")
    else:
        print("   ℹ️  No new patterns to store")

    return result


# Auto-run when executed
if __name__ == "__main__":
    main()
