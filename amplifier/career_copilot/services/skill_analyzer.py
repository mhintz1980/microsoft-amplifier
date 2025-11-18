"""
Skill Analyzer Service

Analyzes user skills, identifies skill gaps, and provides learning recommendations
based on career goals and job market trends.
"""

import logging
from datetime import datetime
from typing import Any

from ...ccsdk_toolkit.defensive.llm_parsing import parse_llm_json
from ...ccsdk_toolkit.defensive.retry_patterns import retry_with_feedback
from ..models.master_profile import CareerInsight
from ..models.master_profile import SkillGap
from ..models.resume_data import ResumeData
from ..models.resume_data import Skill
from ..models.resume_data import SkillLevel
from ..models.user_preferences import UserPreferences

logger = logging.getLogger(__name__)


class SkillAnalyzer:
    """Service for analyzing skills and providing career guidance."""

    def __init__(self, claude_client=None):
        """Initialize skill analyzer with optional Claude client for AI analysis."""
        self.claude_client = claude_client

    async def analyze_skill_gaps(
        self, resume_data: ResumeData, user_preferences: UserPreferences, target_roles: list[str] | None = None
    ) -> list[SkillGap]:
        """Analyze skill gaps based on current skills and career goals.

        Args:
            resume_data: User's resume data with current skills
            user_preferences: User preferences and career goals
            target_roles: Specific target roles to analyze for

        Returns:
            List of skill gaps with learning recommendations
        """
        if not target_roles:
            target_roles = user_preferences.career_goals.target_roles

        if not target_roles:
            logger.warning("No target roles specified for skill gap analysis")
            return []

        try:
            if self.claude_client:
                return await self._ai_analyze_skill_gaps(resume_data, target_roles)
            return await self._rule_based_skill_gaps(resume_data, target_roles)

        except Exception as e:
            logger.error(f"Skill gap analysis failed: {e}")
            return []

    async def _ai_analyze_skill_gaps(self, resume_data: ResumeData, target_roles: list[str]) -> list[SkillGap]:
        """Use AI to analyze skill gaps for target roles."""
        current_skills = resume_data.get_all_skills()

        prompt = f"""
Analyze skill gaps for the following target roles and provide specific learning recommendations.

Current Skills:
{self._format_skills_for_prompt(current_skills)}

Target Roles:
{", ".join(target_roles)}

Current Experience Level:
{self._get_experience_summary(resume_data)}

Analyze and return JSON with this structure:
{{
    "skill_gaps": [
        {{
            "skill_name": "Skill Name",
            "current_level": "beginner|intermediate|advanced|expert|null",
            "required_level": "beginner|intermediate|advanced|expert",
            "priority": "high|medium|low",
            "estimated_learning_time": "X months",
            "recommended_resources": [
                "Resource 1 with brief description",
                "Resource 2 with brief description"
            ]
        }}
    ],
    "analysis_summary": "Brief summary of key findings and recommendations"
}}

Guidelines:
1. Focus on skills that are most important for the target roles
2. Consider the user's current experience level when suggesting learning time
3. Recommend specific, actionable learning resources
4. Prioritize skills that will have the biggest impact on career progression
5. Consider both technical skills and soft skills
6. For skills not currently in user's profile, set current_level to null
"""

        try:
            # Use retry with feedback for robust AI analysis
            result = await retry_with_feedback(
                func=lambda: self._call_claude_for_analysis(prompt), prompt=prompt, max_retries=3
            )

            if not result:
                logger.error("AI skill analysis returned empty result")
                return []

            # Parse the JSON response
            parsed_data = parse_llm_json(result)
            if not parsed_data or "skill_gaps" not in parsed_data:
                logger.error("Failed to parse AI skill gap response")
                return []

            # Convert to SkillGap objects
            skill_gaps = []
            # type: ignore[arg-type]
            # type: ignore[arg-type]
            for gap_data in parsed_data["skill_gaps"]:  # type: ignore[arg-type]
                try:
                    # Map level strings to enum values
                    required_level = self._map_skill_level(gap_data.get("required_level", "intermediate"))
                    current_level = (
                        self._map_skill_level(gap_data.get("current_level")) if gap_data.get("current_level") else None
                    )

                    skill_gap = SkillGap(
                        skill_name=gap_data["skill_name"],
                        current_level=current_level,
                        required_level=required_level,
                        priority=gap_data.get("priority", "medium"),
                        estimated_learning_time=gap_data.get("estimated_learning_time"),
                        recommended_resources=gap_data.get("recommended_resources", []),
                    )
                    skill_gaps.append(skill_gap)

                except Exception as e:
                    logger.warning(f"Failed to parse skill gap {gap_data}: {e}")
                    continue

            return skill_gaps

        except Exception as e:
            logger.error(f"AI skill gap analysis failed: {e}")
            return await self._rule_based_skill_gaps(resume_data, target_roles)

    async def _call_claude_for_analysis(self, prompt: str) -> str:
        """Call Claude API for skill analysis."""
        try:
            response = await self.claude_client.query(prompt)  # type: ignore[assignment]

            # Collect response content
            result = ""
            async for message in response:
                if hasattr(message, "content") and isinstance(message.content, list):
                    for block in message.content:
                        if hasattr(block, "text"):
                            result += block.text
                elif hasattr(message, "text"):
                    result += message.text

            return result
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise

    async def _rule_based_skill_gaps(self, resume_data: ResumeData, target_roles: list[str]) -> list[SkillGap]:
        """Rule-based skill gap analysis as fallback."""
        logger.info("Using rule-based skill gap analysis")

        # Define common skill requirements for different roles
        role_skill_requirements = {
            "software engineer": {
                "Python": SkillLevel.INTERMEDIATE,
                "Git": SkillLevel.INTERMEDIATE,
                "Data Structures": SkillLevel.ADVANCED,
                "Algorithms": SkillLevel.ADVANCED,
                "System Design": SkillLevel.INTERMEDIATE,
            },
            "senior software engineer": {
                "Python": SkillLevel.ADVANCED,
                "Git": SkillLevel.ADVANCED,
                "Data Structures": SkillLevel.EXPERT,
                "Algorithms": SkillLevel.EXPERT,
                "System Design": SkillLevel.ADVANCED,
                "Mentoring": SkillLevel.INTERMEDIATE,
            },
            "data scientist": {
                "Python": SkillLevel.ADVANCED,
                "Statistics": SkillLevel.ADVANCED,
                "Machine Learning": SkillLevel.INTERMEDIATE,
                "Data Visualization": SkillLevel.INTERMEDIATE,
                "SQL": SkillLevel.INTERMEDIATE,
            },
            "product manager": {
                "Communication": SkillLevel.ADVANCED,
                "Project Management": SkillLevel.ADVANCED,
                "Data Analysis": SkillLevel.INTERMEDIATE,
                "User Research": SkillLevel.INTERMEDIATE,
                "Strategic Thinking": SkillLevel.ADVANCED,
            },
        }

        current_skills = resume_data.get_all_skills()
        current_skill_map = {skill.name.lower(): skill for skill in current_skills}

        skill_gaps = []

        # Analyze each target role
        for role in target_roles:
            role_lower = role.lower()

            # Find matching role requirements
            required_skills = {}
            for role_key, requirements in role_skill_requirements.items():
                if role_key in role_lower:
                    required_skills.update(requirements)

            # Check for gaps
            for skill_name, required_level in required_skills.items():
                current_skill = current_skill_map.get(skill_name.lower())

                if not current_skill or current_skill.level.value < required_level.value:
                    # Determine priority based on importance
                    priority = "high" if required_level in [SkillLevel.ADVANCED, SkillLevel.EXPERT] else "medium"

                    # Estimate learning time
                    if not current_skill:
                        learning_time = self._estimate_learning_time(None, required_level)
                    else:
                        learning_time = self._estimate_learning_time(current_skill.level, required_level)

                    skill_gap = SkillGap(
                        skill_name=skill_name,
                        current_level=current_skill.level if current_skill else None,
                        required_level=required_level,
                        priority=priority,
                        estimated_learning_time=learning_time,
                        recommended_resources=self._get_learning_resources(skill_name),
                    )
                    skill_gaps.append(skill_gap)

        # Remove duplicates and sort by priority
        unique_gaps = {}
        for gap in skill_gaps:
            if gap.skill_name not in unique_gaps or gap.priority == "high":
                unique_gaps[gap.skill_name] = gap

        return sorted(unique_gaps.values(), key=lambda x: {"high": 0, "medium": 1, "low": 2}[x.priority])

    def _format_skills_for_prompt(self, skills: list[Skill]) -> str:
        """Format skills list for AI prompt."""
        if not skills:
            return "No skills listed"

        skill_lines = []
        for skill in sorted(skills, key=lambda x: x.level.value, reverse=True):
            line = f"- {skill.name}: {skill.level.value}"
            if skill.years_experience:
                line += f" ({skill.years_experience} years)"
            if skill.context:
                line += f" - {skill.context}"
            skill_lines.append(line)

        return "\n".join(skill_lines)

    def _get_experience_summary(self, resume_data: ResumeData) -> str:
        """Get summary of user's experience level."""
        total_years = resume_data.get_total_experience_years()
        current_position = resume_data.get_current_position()

        summary = f"Total experience: {total_years:.1f} years"
        if current_position:
            summary += f"\nCurrent role: {current_position.position} at {current_position.company}"

        return summary

    def _map_skill_level(self, level_str: str) -> SkillLevel:
        """Map string to SkillLevel enum."""
        level_mapping = {
            "beginner": SkillLevel.BEGINNER,
            "intermediate": SkillLevel.INTERMEDIATE,
            "advanced": SkillLevel.ADVANCED,
            "expert": SkillLevel.EXPERT,
        }
        return level_mapping.get(level_str.lower(), SkillLevel.INTERMEDIATE)

    def _estimate_learning_time(self, current_level: SkillLevel | None, target_level: SkillLevel) -> str:
        """Estimate time required to reach target skill level."""
        if current_level is None:
            base_time = 6  # months for complete beginner
        else:
            level_diff = target_level.value - current_level.value
            base_time = max(2, level_diff * 3)  # months per level difference

        # Adjust based on target level
        if target_level == SkillLevel.EXPERT:
            base_time *= 1.5
        elif target_level == SkillLevel.BEGINNER:
            base_time *= 0.5

        return f"{int(base_time)} months"

    def _get_learning_resources(self, skill_name: str) -> list[str]:
        """Get recommended learning resources for a skill."""
        resource_map = {
            "Python": [
                "Python.org official tutorial",
                "Coursera: Python for Everybody",
                "Real Python: comprehensive tutorials",
            ],
            "Git": ["Git official documentation", "GitHub Learning Lab", "Atlassian Git Tutorial"],
            "Machine Learning": [
                "Coursera: Machine Learning by Andrew Ng",
                "Fast.ai: practical deep learning",
                "Google's ML Crash Course",
            ],
            "Data Structures": [
                "GeeksforGeeks: DS & Algorithm tutorials",
                "Coursera: Data Structures by UC San Diego",
                "LeetCode: practice problems",
            ],
            "Communication": [
                "Toastmasters International",
                "Dale Carnegie: How to Win Friends",
                "Coursera: Business Communication",
            ],
        }

        return resource_map.get(
            skill_name,
            [
                f"Online courses for {skill_name}",
                f"Books and tutorials on {skill_name}",
                f"Practice projects with {skill_name}",
            ],
        )

    async def generate_skill_insights(
        self, resume_data: ResumeData, user_preferences: UserPreferences, skill_gaps: list[SkillGap]
    ) -> list[CareerInsight]:
        """Generate career insights based on skill analysis."""
        insights = []

        # High-priority skill gaps insight
        high_priority_gaps = [gap for gap in skill_gaps if gap.priority == "high"]
        if high_priority_gaps:
            insight = CareerInsight(
                type="skill_gap",
                title="High-Priority Skill Gaps Identified",
                description=f"You have {len(high_priority_gaps)} high-priority skill gaps to address. Focus on these skills first as they are most critical for your target roles.",
                confidence=0.9,
                actionable=True,
                priority="high",
                category="skills",
                data_points=[gap.skill_name for gap in high_priority_gaps[:5]],
            )
            insights.append(insight)

        # Skill diversification insight
        all_skills = resume_data.get_all_skills()
        skill_categories = self._categorize_skills(all_skills)
        if len(skill_categories) < 3:
            insight = CareerInsight(
                type="skill_diversity",
                title="Diversify Your Skill Set",
                description="Consider developing skills in additional categories to increase your versatility and market value.",
                confidence=0.7,
                actionable=True,
                priority="medium",
                category="skills",
                data_points=list(skill_categories.keys()),
            )
            insights.append(insight)

        # Learning path recommendation
        if skill_gaps:
            learning_time = self._calculate_total_learning_time(skill_gaps)
            insight = CareerInsight(
                type="learning_path",
                title="Structured Learning Path Available",
                description=f"Based on your skill gaps, we estimate {learning_time} of focused learning to reach your target role requirements.",
                confidence=0.8,
                actionable=True,
                priority="medium",
                category="learning",
                data_points=[f"Estimated time: {learning_time}"],
            )
            insights.append(insight)

        return insights

    def _categorize_skills(self, skills: list[Skill]) -> dict[str, list[Skill]]:
        """Categorize skills into different domains."""
        categories = {
            "Programming": [],
            "Data & Analytics": [],
            "Design": [],
            "Communication": [],
            "Management": [],
            "Tools & Platforms": [],
            "Other": [],
        }

        programming_keywords = ["python", "java", "javascript", "c++", "go", "rust", "sql", "html", "css"]
        data_keywords = ["data", "analytics", "statistics", "machine learning", "ai", "visualization"]
        design_keywords = ["design", "ui", "ux", "figma", "sketch", "photoshop"]
        communication_keywords = ["communication", "writing", "presentation", "public speaking"]
        management_keywords = ["management", "leadership", "project", "agile", "scrum"]
        tools_keywords = ["git", "docker", "aws", "azure", "gcp", "kubernetes"]

        for skill in skills:
            skill_lower = skill.name.lower()
            if any(keyword in skill_lower for keyword in programming_keywords):
                categories["Programming"].append(skill)
            elif any(keyword in skill_lower for keyword in data_keywords):
                categories["Data & Analytics"].append(skill)
            elif any(keyword in skill_lower for keyword in design_keywords):
                categories["Design"].append(skill)
            elif any(keyword in skill_lower for keyword in communication_keywords):
                categories["Communication"].append(skill)
            elif any(keyword in skill_lower for keyword in management_keywords):
                categories["Management"].append(skill)
            elif any(keyword in skill_lower for keyword in tools_keywords):
                categories["Tools & Platforms"].append(skill)
            else:
                categories["Other"].append(skill)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def _calculate_total_learning_time(self, skill_gaps: list[SkillGap]) -> str:
        """Calculate total estimated learning time for all skill gaps."""
        total_months = 0

        for gap in skill_gaps:
            if gap.estimated_learning_time:
                # Extract number from string like "6 months"
                import re

                match = re.search(r"(\d+)", gap.estimated_learning_time)
                if match:
                    total_months += int(match.group(1))

        if total_months < 12:
            return f"{total_months} months"
        years = total_months // 12
        months = total_months % 12
        return f"{years} year{'' if years == 1 else 's'}" + (f" {months} months" if months > 0 else "")

    async def assess_skill_market_demand(
        self, skills: list[Skill], target_industries: list[str] | None = None
    ) -> dict[str, Any]:
        """Assess market demand for user's skills."""
        # This would integrate with job market APIs in a real implementation
        # For now, return simulated data

        skill_demand_scores = {}
        for skill in skills:
            # Simulated demand scores (would be real data in production)
            base_demand = 0.7  # Average demand
            if skill.level in [SkillLevel.ADVANCED, SkillLevel.EXPERT]:
                base_demand += 0.2

            # Add some variation for different skills
            if skill.name.lower() in ["python", "machine learning", "cloud computing"]:
                base_demand += 0.2
            elif skill.name.lower() in ["communication", "leadership"]:
                base_demand += 0.1

            skill_demand_scores[skill.name] = min(1.0, base_demand)

        # Calculate overall market readiness
        if skill_demand_scores:
            overall_score = sum(skill_demand_scores.values()) / len(skill_demand_scores)
        else:
            overall_score = 0.0

        return {
            "skill_demand_scores": skill_demand_scores,
            "overall_market_readiness": overall_score,
            "high_demand_skills": [skill for skill, score in skill_demand_scores.items() if score > 0.8],
            "assessment_date": datetime.now().isoformat(),
        }
