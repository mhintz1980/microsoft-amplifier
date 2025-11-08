#!/usr/bin/env python3
"""
Learning & Feedback System: Self-Improving Creative Assistant

Implements continuous learning from user feedback, project outcomes,
and performance metrics to improve CreaTech's capabilities over time.
"""

import asyncio
import json
import logging
import statistics
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class FeedbackEntry:
    """Individual feedback entry"""

    timestamp: str
    project_id: str
    feedback_type: str  # user_feedback, performance_metrics, outcome_analysis
    rating: float  # 0-1 scale
    comments: str
    context: dict[str, Any]
    improvements_suggested: list[str]
    success_indicators: list[str]


@dataclass
class PerformanceMetrics:
    """Performance metrics for a project"""

    project_id: str
    completion_time: float  # seconds
    user_satisfaction: float  # 0-1 scale
    technical_success: float  # 0-1 scale
    creative_quality: float  # 0-1 scale
    iteration_count: int
    user_engagement: float  # 0-1 scale


@dataclass
class LearningInsight:
    """Extracted learning insight"""

    pattern: str
    confidence: float  # 0-1 scale
    frequency: int
    impact_score: float  # 0-1 scale
    actionable: bool
    recommendation: str


class LearningFeedbackSystem:
    """Self-improving learning and feedback system for CreaTech"""

    def __init__(self):
        self.workspace = Path("learning_feedback_workspace")
        self.workspace.mkdir(exist_ok=True)

        # Data storage
        self.feedback_db = self.workspace / "feedback_database.json"
        self.metrics_db = self.workspace / "performance_metrics.json"
        self.insights_db = self.workspace / "learning_insights.json"
        self.improvement_log = self.workspace / "improvement_log.json"

        # Initialize databases
        self.feedback_entries = self._load_feedback_entries()
        self.performance_metrics = self._load_performance_metrics()
        self.learning_insights = self._load_learning_insights()
        self.improvement_history = self._load_improvement_history()

        logger.info("🧠 Learning Feedback System initialized")
        logger.info(f"📊 Loaded {len(self.feedback_entries)} feedback entries")
        logger.info(f"📈 Loaded {len(self.performance_metrics)} performance metrics")
        logger.info(f"💡 Loaded {len(self.learning_insights)} learning insights")

    def _load_feedback_entries(self) -> list[FeedbackEntry]:
        """Load feedback entries from database"""
        try:
            if self.feedback_db.exists():
                with open(self.feedback_db) as f:
                    data = json.load(f)
                return [FeedbackEntry(**entry) for entry in data]
        except Exception as e:
            logger.warning(f"Could not load feedback database: {e}")
        return []

    def _load_performance_metrics(self) -> list[PerformanceMetrics]:
        """Load performance metrics from database"""
        try:
            if self.metrics_db.exists():
                with open(self.metrics_db) as f:
                    data = json.load(f)
                return [PerformanceMetrics(**metric) for metric in data]
        except Exception as e:
            logger.warning(f"Could not load metrics database: {e}")
        return []

    def _load_learning_insights(self) -> list[LearningInsight]:
        """Load learning insights from database"""
        try:
            if self.insights_db.exists():
                with open(self.insights_db) as f:
                    data = json.load(f)
                return [LearningInsight(**insight) for insight in data]
        except Exception as e:
            logger.warning(f"Could not load insights database: {e}")
        return []

    def _load_improvement_history(self) -> list[dict[str, Any]]:
        """Load improvement history from database"""
        try:
            if self.improvement_log.exists():
                with open(self.improvement_log) as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load improvement history: {e}")
        return []

    def _save_feedback_entries(self):
        """Save feedback entries to database"""
        try:
            with open(self.feedback_db, "w") as f:
                json.dump([asdict(entry) for entry in self.feedback_entries], f, indent=2)
        except Exception as e:
            logger.error(f"Could not save feedback database: {e}")

    def _save_performance_metrics(self):
        """Save performance metrics to database"""
        try:
            with open(self.metrics_db, "w") as f:
                json.dump([asdict(metric) for metric in self.performance_metrics], f, indent=2)
        except Exception as e:
            logger.error(f"Could not save metrics database: {e}")

    def _save_learning_insights(self):
        """Save learning insights to database"""
        try:
            with open(self.insights_db, "w") as f:
                json.dump([asdict(insight) for insight in self.learning_insights], f, indent=2)
        except Exception as e:
            logger.error(f"Could not save insights database: {e}")

    def _save_improvement_history(self):
        """Save improvement history to database"""
        try:
            with open(self.improvement_log, "w") as f:
                json.dump(self.improvement_history, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save improvement history: {e}")

    async def record_user_feedback(
        self,
        project_id: str,
        rating: float,
        comments: str,
        context: dict[str, Any],
        improvements: list[str] = None,
        successes: list[str] = None,
    ) -> str:
        """Record user feedback for a project"""

        feedback_id = str(datetime.now().timestamp())

        feedback_entry = FeedbackEntry(
            timestamp=datetime.now().isoformat(),
            project_id=project_id,
            feedback_type="user_feedback",
            rating=rating,
            comments=comments,
            context=context,
            improvements_suggested=improvements or [],
            success_indicators=successes or [],
        )

        self.feedback_entries.append(feedback_entry)
        self._save_feedback_entries()

        # Generate insights from new feedback
        await self._analyze_new_feedback(feedback_entry)

        logger.info(f"📝 Recorded user feedback for project {project_id} (rating: {rating:.1f})")
        return feedback_id

    async def record_performance_metrics(
        self,
        project_id: str,
        completion_time: float,
        user_satisfaction: float,
        technical_success: float,
        creative_quality: float,
        iteration_count: int,
        user_engagement: float,
    ) -> str:
        """Record performance metrics for a project"""

        metrics_id = str(datetime.now().timestamp())

        performance_metric = PerformanceMetrics(
            project_id=project_id,
            completion_time=completion_time,
            user_satisfaction=user_satisfaction,
            technical_success=technical_success,
            creative_quality=creative_quality,
            iteration_count=iteration_count,
            user_engagement=user_engagement,
        )

        self.performance_metrics.append(performance_metric)
        self._save_performance_metrics()

        # Analyze performance trends
        await self._analyze_performance_trends()

        logger.info(f"📊 Recorded performance metrics for project {project_id}")
        return metrics_id

    async def record_outcome_analysis(
        self,
        project_id: str,
        outcome_description: str,
        success_factors: list[str],
        challenges: list[str],
        lessons_learned: list[str],
        unexpected_results: list[str],
    ) -> str:
        """Record detailed outcome analysis"""

        feedback_entry = FeedbackEntry(
            timestamp=datetime.now().isoformat(),
            project_id=project_id,
            feedback_type="outcome_analysis",
            rating=0.7,  # Default rating for outcome analysis
            comments=outcome_description,
            context={
                "success_factors": success_factors,
                "challenges": challenges,
                "lessons_learned": lessons_learned,
                "unexpected_results": unexpected_results,
            },
            improvements_suggested=[],
            success_indicators=success_factors,
        )

        self.feedback_entries.append(feedback_entry)
        self._save_feedback_entries()

        # Generate insights from outcome analysis
        await self._analyze_outcome_patterns(feedback_entry)

        logger.info(f"🔍 Recorded outcome analysis for project {project_id}")
        return str(datetime.now().timestamp())

    async def _analyze_new_feedback(self, feedback: FeedbackEntry):
        """Analyze new feedback to extract learning insights"""

        # Look for patterns in feedback
        insights = []

        # Analyze sentiment patterns
        if feedback.rating < 0.5:
            insights.append(
                LearningInsight(
                    pattern="low_user_satisfaction",
                    confidence=0.8,
                    frequency=1,
                    impact_score=0.9,
                    actionable=True,
                    recommendation="Investigate user pain points and improve UX",
                )
            )
        elif feedback.rating > 0.8:
            insights.append(
                LearningInsight(
                    pattern="high_user_satisfaction",
                    confidence=0.8,
                    frequency=1,
                    impact_score=0.7,
                    actionable=True,
                    recommendation="Document successful patterns for reuse",
                )
            )

        # Analyze improvement suggestions
        for improvement in feedback.improvements_suggested:
            insights.append(
                LearningInsight(
                    pattern=f"improvement_suggestion: {improvement.lower()}",
                    confidence=0.6,
                    frequency=1,
                    impact_score=0.6,
                    actionable=True,
                    recommendation=f"Address: {improvement}",
                )
            )

        # Analyze success indicators
        for success in feedback.success_indicators:
            insights.append(
                LearningInsight(
                    pattern=f"success_factor: {success.lower()}",
                    confidence=0.7,
                    frequency=1,
                    impact_score=0.5,
                    actionable=True,
                    recommendation=f"Reinforce: {success}",
                )
            )

        # Add insights to database
        for insight in insights:
            self.learning_insights.append(insight)
        self._save_learning_insights()

        logger.info(f"💡 Generated {len(insights)} insights from new feedback")

    async def _analyze_performance_trends(self):
        """Analyze performance metrics to identify trends and patterns"""

        if len(self.performance_metrics) < 3:
            return  # Need at least 3 data points for trend analysis

        recent_metrics = self.performance_metrics[-10:]  # Last 10 projects
        insights = []

        # Analyze completion time trends
        completion_times = [m.completion_time for m in recent_metrics]
        if len(completion_times) >= 3:
            time_trend = statistics.linear_regression(range(len(completion_times)), completion_times)
            if time_trend.slope > 0:
                insights.append(
                    LearningInsight(
                        pattern="increasing_completion_time",
                        confidence=abs(time_trend.slope) / statistics.mean(completion_times),
                        frequency=len(recent_metrics),
                        impact_score=0.7,
                        actionable=True,
                        recommendation="Optimize workflows to reduce completion time",
                    )
                )

        # Analyze satisfaction trends
        satisfaction_scores = [m.user_satisfaction for m in recent_metrics]
        if len(satisfaction_scores) >= 3:
            satisfaction_trend = statistics.linear_regression(range(len(satisfaction_scores)), satisfaction_scores)
            if satisfaction_trend.slope < -0.1:
                insights.append(
                    LearningInsight(
                        pattern="declining_satisfaction",
                        confidence=abs(satisfaction_trend.slope),
                        frequency=len(recent_metrics),
                        impact_score=0.9,
                        actionable=True,
                        recommendation="Investigate satisfaction decline and improve user experience",
                    )
                )

        # Analyze iteration patterns
        iteration_counts = [m.iteration_count for m in recent_metrics]
        avg_iterations = statistics.mean(iteration_counts)
        if avg_iterations > 5:
            insights.append(
                LearningInsight(
                    pattern="high_iteration_count",
                    confidence=0.6,
                    frequency=len(recent_metrics),
                    impact_score=0.6,
                    actionable=True,
                    recommendation="Improve initial solution quality to reduce iterations",
                )
            )

        # Add insights to database
        for insight in insights:
            self.learning_insights.append(insight)
        self._save_learning_insights()

        logger.info(f"📈 Generated {len(insights)} insights from performance trends")

    async def _analyze_outcome_patterns(self, feedback: FeedbackEntry):
        """Analyze outcome patterns to extract learning insights"""

        insights = []
        context = feedback.context

        # Analyze success factors
        for factor in context.get("success_factors", []):
            insights.append(
                LearningInsight(
                    pattern=f"success_pattern: {factor.lower()}",
                    confidence=0.7,
                    frequency=1,
                    impact_score=0.6,
                    actionable=True,
                    recommendation=f"Document and replicate: {factor}",
                )
            )

        # Analyze challenges
        for challenge in context.get("challenges", []):
            insights.append(
                LearningInsight(
                    pattern=f"challenge_pattern: {challenge.lower()}",
                    confidence=0.6,
                    frequency=1,
                    impact_score=0.7,
                    actionable=True,
                    recommendation=f"Address recurring challenge: {challenge}",
                )
            )

        # Analyze lessons learned
        for lesson in context.get("lessons_learned", []):
            insights.append(
                LearningInsight(
                    pattern=f"lesson_learned: {lesson.lower()}",
                    confidence=0.8,
                    frequency=1,
                    impact_score=0.5,
                    actionable=True,
                    recommendation=f"Incorporate lesson: {lesson}",
                )
            )

        # Add insights to database
        for insight in insights:
            self.learning_insights.append(insight)
        self._save_learning_insights()

        logger.info(f"🎯 Generated {len(insights)} insights from outcome analysis")

    async def generate_improvement_recommendations(self) -> list[dict[str, Any]]:
        """Generate improvement recommendations based on learning insights"""

        # Filter for actionable insights with high impact
        actionable_insights = [
            insight for insight in self.learning_insights if insight.actionable and insight.impact_score > 0.6
        ]

        # Group insights by pattern
        pattern_groups = {}
        for insight in actionable_insights:
            pattern = insight.pattern
            if pattern not in pattern_groups:
                pattern_groups[pattern] = []
            pattern_groups[pattern].append(insight)

        # Generate recommendations
        recommendations = []

        for pattern, insights_list in pattern_groups.items():
            # Calculate aggregate metrics
            avg_confidence = statistics.mean([i.confidence for i in insights_list])
            total_frequency = sum([i.frequency for i in insights_list])
            avg_impact = statistics.mean([i.impact_score for i in insights_list])

            # Create recommendation
            recommendation = {
                "pattern": pattern,
                "description": f"Pattern detected: {pattern.replace('_', ' ').title()}",
                "frequency": total_frequency,
                "confidence": avg_confidence,
                "impact_score": avg_impact,
                "priority": self._calculate_priority(avg_confidence, avg_impact, total_frequency),
                "recommendation": insights_list[0].recommendation,
                "supporting_evidence": len(insights_list),
                "suggested_actions": self._generate_suggested_actions(pattern, insights_list),
            }

            recommendations.append(recommendation)

        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"], reverse=True)

        logger.info(f"🎯 Generated {len(recommendations)} improvement recommendations")
        return recommendations

    def _calculate_priority(self, confidence: float, impact: float, frequency: int) -> float:
        """Calculate priority score for recommendation"""
        # Weighted combination of factors
        return confidence * 0.3 + impact * 0.4 + min(frequency / 10, 1.0) * 0.3

    def _generate_suggested_actions(self, pattern: str, insights: list[LearningInsight]) -> list[str]:
        """Generate specific actions for addressing a pattern"""
        actions = []

        # Get unique recommendations from insights
        unique_recommendations = list({i.recommendation for i in insights})

        # Add specific actions based on pattern type
        if "satisfaction" in pattern:
            actions.extend(
                [
                    "Conduct user satisfaction surveys",
                    "Implement user feedback loops",
                    "Review and improve UI/UX design",
                    "A/B test different approaches",
                ]
            )
        elif "performance" in pattern or "time" in pattern:
            actions.extend(
                [
                    "Optimize algorithm efficiency",
                    "Review resource allocation",
                    "Implement performance monitoring",
                    "Consider caching strategies",
                ]
            )
        elif "quality" in pattern:
            actions.extend(
                [
                    "Implement quality gates",
                    "Add comprehensive testing",
                    "Review code quality standards",
                    "Implement peer review process",
                ]
            )
        elif "iteration" in pattern:
            actions.extend(
                [
                    "Improve requirement gathering",
                    "Enhance initial solution quality",
                    "Add prototype validation steps",
                    "Implement incremental delivery",
                ]
            )

        # Add recommendations from insights
        actions.extend(unique_recommendations)

        return list(set(actions))  # Remove duplicates

    async def implement_improvement(self, recommendation: dict[str, Any]) -> bool:
        """Implement an improvement recommendation"""

        improvement_id = str(datetime.now().timestamp())

        improvement_record = {
            "improvement_id": improvement_id,
            "recommendation": recommendation,
            "status": "planned",
            "created_at": datetime.now().isoformat(),
            "estimated_impact": recommendation["impact_score"],
            "implementation_plan": self._create_implementation_plan(recommendation),
        }

        self.improvement_history.append(improvement_record)
        self._save_improvement_history()

        logger.info(f"🔧 Planned improvement: {recommendation['pattern']}")
        return True

    def _create_implementation_plan(self, recommendation: dict[str, Any]) -> list[dict[str, Any]]:
        """Create implementation plan for recommendation"""
        recommendation["pattern"]
        priority = recommendation["priority"]

        plan = []

        if priority > 0.8:  # High priority
            plan.extend(
                [
                    {
                        "phase": "Immediate Action",
                        "timeline": "1-2 days",
                        "actions": ["Address critical issue", "Implement quick fix", "Monitor results"],
                    },
                    {
                        "phase": "Follow-up",
                        "timeline": "1 week",
                        "actions": ["Validate solution", "Measure improvement", "Document changes"],
                    },
                ]
            )
        else:  # Medium/Low priority
            plan.append(
                {
                    "phase": "Scheduled Improvement",
                    "timeline": "1-2 weeks",
                    "actions": ["Plan implementation", "Execute changes", "Validate results"],
                }
            )

        return plan

    def get_learning_summary(self) -> dict[str, Any]:
        """Get comprehensive learning summary"""

        return {
            "summary_date": datetime.now().isoformat(),
            "data_points": {
                "total_feedback_entries": len(self.feedback_entries),
                "total_performance_metrics": len(self.performance_metrics),
                "total_learning_insights": len(self.learning_insights),
                "total_improvements": len(self.improvement_history),
            },
            "recent_trends": self._analyze_recent_trends(),
            "top_insights": self._get_top_insights(),
            "improvement_opportunities": len(
                [i for i in self.learning_insights if i.actionable and i.impact_score > 0.7]
            ),
            "learning_maturity": self._assess_learning_maturity(),
        }

    def _analyze_recent_trends(self) -> dict[str, Any]:
        """Analyze recent learning trends"""
        # Get feedback from last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_feedback = [f for f in self.feedback_entries if datetime.fromisoformat(f.timestamp) > cutoff_date]

        if not recent_feedback:
            return {"message": "Insufficient recent data"}

        avg_rating = statistics.mean([f.rating for f in recent_feedback])
        feedback_types = [f.feedback_type for f in recent_feedback]

        return {
            "average_recent_rating": avg_rating,
            "feedback_volume": len(recent_feedback),
            "feedback_types": list(set(feedback_types)),
            "trend_direction": "improving" if avg_rating > 0.7 else "needs_attention",
        }

    def _get_top_insights(self) -> list[dict[str, Any]]:
        """Get top learning insights"""
        # Sort insights by impact and confidence
        sorted_insights = sorted(self.learning_insights, key=lambda i: (i.impact_score * i.confidence), reverse=True)

        return [
            {
                "pattern": i.pattern,
                "confidence": i.confidence,
                "impact": i.impact_score,
                "recommendation": i.recommendation,
            }
            for i in sorted_insights[:5]
        ]

    def _assess_learning_maturity(self) -> str:
        """Assess learning system maturity"""
        total_data_points = len(self.feedback_entries) + len(self.performance_metrics)
        actionable_insights = len([i for i in self.learning_insights if i.actionable])

        if total_data_points > 50 and actionable_insights > 10:
            return "Mature - Systematically learning and improving"
        if total_data_points > 20 and actionable_insights > 5:
            return "Developing - Building learning foundation"
        if total_data_points > 5:
            return "Early - Starting to capture insights"
        return "Initial - Learning system just starting"


# CLI interface
def main():
    """Main CLI interface for Learning Feedback System"""
    import argparse

    parser = argparse.ArgumentParser(description="Learning Feedback System - Self-Improving Assistant")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--summary", action="store_true", help="Show learning summary")
    parser.add_argument("--recommendations", action="store_true", help="Generate improvement recommendations")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    async def run_cli():
        learning_system = LearningFeedbackSystem()

        if args.interactive:
            await learning_system.interactive_session()
        elif args.summary:
            summary = learning_system.get_learning_summary()
            print(json.dumps(summary, indent=2, default=str))
        elif args.recommendations:
            recommendations = await learning_system.generate_improvement_recommendations()
            print(json.dumps(recommendations, indent=2, default=str))
        else:
            parser.print_help()

    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
