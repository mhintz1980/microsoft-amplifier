"""
Enrichment Coach Service

Provides personalized career coaching, skill development guidance,
and actionable recommendations for career advancement.
"""

import logging
from datetime import datetime
from typing import Any

from ..models.master_profile import CareerInsight
from ..models.master_profile import SkillGap
from ..models.resume_data import ResumeData
from ..models.user_preferences import LearningPreferences
from ..models.user_preferences import UserPreferences

logger = logging.getLogger(__name__)


class EnrichmentCoach:
    """Service for providing personalized career coaching and enrichment."""

    def __init__(self, claude_client=None):
        """Initialize enrichment coach with optional Claude client for AI coaching."""
        self.claude_client = claude_client

    async def generate_career_advice(
        self, resume_data: ResumeData, user_preferences: UserPreferences, skill_gaps: list[SkillGap]
    ) -> list[CareerInsight]:
        """Generate personalized career advice based on user profile and goals."""
        insights = []

        try:
            if self.claude_client:
                ai_insights = await self._ai_generate_career_advice(resume_data, user_preferences, skill_gaps)
                insights.extend(ai_insights)

            # Always add rule-based insights for comprehensive coverage
            rule_based_insights = await self._generate_rule_based_advice(resume_data, user_preferences, skill_gaps)
            insights.extend(rule_based_insights)

            # Remove duplicates and sort by priority
            unique_insights = self._deduplicate_insights(insights)
            return sorted(unique_insights, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x.priority])

        except Exception as e:
            logger.error(f"Career advice generation failed: {e}")
            return await self._generate_rule_based_advice(resume_data, user_preferences, skill_gaps)

    async def _ai_generate_career_advice(
        self, resume_data: ResumeData, user_preferences: UserPreferences, skill_gaps: list[SkillGap]
    ) -> list[CareerInsight]:
        """Use AI to generate personalized career advice."""
        current_position = resume_data.get_current_position()
        target_roles = user_preferences.career_goals.target_roles
        total_experience = resume_data.get_total_experience_years()

        prompt = f"""
Generate personalized career advice based on the following profile:

Current Profile:
- Current Position: {current_position.position if current_position else "Not specified"}
- Total Experience: {total_experience:.1f} years
- Top Skills: {", ".join([skill.name for skill in resume_data.skills(5)])}  # type: ignore[attribute]  # type: ignore[attribute]  # type: ignore[attribute]  # type: ignore[attribute]  # type: ignore[attr-defined]  # type: ignore[attr-defined]  # type: ignore[attr-defined]  # type: ignore[attr-defined]  # type: ignore[attr-defined]  # type: ignore[attr-defined]

Career Goals:
- Target Roles: {", ".join(target_roles) if target_roles else "Not specified"}
- Target Industries: {", ".join(user_preferences.career_goals.target_industries) if user_preferences.career_goals.target_industries else "Not specified"}
- Career Level Target: {user_preferences.career_goals.career_level_target.value if user_preferences.career_goals.career_level_target else "Not specified"}

Skill Gaps:
{self._format_skill_gaps_for_prompt(skill_gaps)}

Learning Preferences:
- Learning Style: {user_preferences.learning_preferences.learning_style.value if user_preferences.learning_preferences.learning_style else "Not specified"}
- Time Commitment: {user_preferences.learning_preferences.time_commitment or "Not specified"} hours/week
- Preferred Formats: {", ".join(user_preferences.learning_preferences.preferred_formats) if user_preferences.learning_preferences.preferred_formats else "Not specified"}

Generate JSON with this structure:
{{
    "insights": [
        {{
            "type": "career_strategy|skill_development|networking|personal_branding|job_search",
            "title": "Insight Title",
            "description": "Detailed, actionable advice",
            "confidence": 0.8,
            "actionable": true,
            "priority": "high|medium|low",
            "category": "strategy|skills|networking|branding|applications",
            "data_points": ["supporting point 1", "supporting point 2"]
        }}
    ]
}}

Guidelines:
1. Provide specific, actionable advice tailored to the user's situation
2. Consider their experience level and career goals
3. Account for their learning preferences and time constraints
4. Include advice on networking, personal branding, and job search strategy
5. Focus on high-impact recommendations that can accelerate their career
6. Be encouraging but realistic about challenges and timelines
"""

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
                    result += block.text

            if not result:
                return []

            # Parse JSON response
            from ...ccsdk_toolkit.defensive.llm_parsing import parse_llm_json

            parsed_data = parse_llm_json(result)
            if not parsed_data or "insights" not in parsed_data:
                return []

            # Convert to CareerInsight objects
            insights = []
            # type: ignore[arg-type]
            # type: ignore[arg-type]
            for insight_data in parsed_data["insights"]:  # type: ignore[arg-type]
                try:
                    insight = CareerInsight(
                        type=insight_data.get("type", "career_strategy"),
                        title=insight_data.get("title", "Career Advice"),
                        description=insight_data.get("description", ""),
                        confidence=insight_data.get("confidence", 0.7),
                        actionable=insight_data.get("actionable", True),
                        priority=insight_data.get("priority", "medium"),
                        category=insight_data.get("category", "strategy"),
                        data_points=insight_data.get("data_points", []),
                    )
                    insights.append(insight)
                except Exception as e:
                    logger.warning(f"Failed to parse insight {insight_data}: {e}")
                    continue

            return insights

        except Exception as e:
            logger.error(f"AI career advice generation failed: {e}")
            return []

    async def _generate_rule_based_advice(
        self, resume_data: ResumeData, user_preferences: UserPreferences, skill_gaps: list[SkillGap]
    ) -> list[CareerInsight]:
        """Generate rule-based career advice."""
        insights = []

        # Experience-based advice
        total_experience = resume_data.get_total_experience_years()
        if total_experience < 2:
            insights.append(
                CareerInsight(
                    type="career_strategy",
                    title="Focus on Foundation Building",
                    description="Early career focus should be on building strong technical foundations and gaining diverse project experience. Don't worry about specialization yet.",
                    confidence=0.9,
                    actionable=True,
                    priority="high",
                    category="strategy",
                    data_points=[f"Experience level: {total_experience:.1f} years"],
                )
            )
        elif 2 <= total_experience < 5:
            insights.append(
                CareerInsight(
                    type="career_strategy",
                    title="Develop Specialization",
                    description="You have enough experience to start specializing. Focus on becoming an expert in 2-3 key areas while maintaining breadth.",
                    confidence=0.8,
                    actionable=True,
                    priority="high",
                    category="strategy",
                    data_points=[f"Experience level: {total_experience:.1f} years"],
                )
            )
        elif total_experience >= 5:
            insights.append(
                CareerInsight(
                    type="career_strategy",
                    title="Leverage Senior Experience",
                    description="Your experience is valuable. Consider mentoring, technical leadership, or architect roles. Focus on strategic impact.",
                    confidence=0.9,
                    actionable=True,
                    priority="medium",
                    category="strategy",
                    data_points=[f"Experience level: {total_experience:.1f} years"],
                )
            )

        # Skill gap based advice
        if skill_gaps:
            high_priority_gaps = [gap for gap in skill_gaps if gap.priority == "high"]
            if high_priority_gaps:
                insights.append(
                    CareerInsight(
                        type="skill_development",
                        title="Address Critical Skill Gaps",
                        description=f"Focus on acquiring {len(high_priority_gaps)} high-priority skills. These will have the biggest impact on reaching your target roles.",
                        confidence=0.9,
                        actionable=True,
                        priority="high",
                        category="skills",
                        data_points=[gap.skill_name for gap in high_priority_gaps[:3]],
                    )
                )

        # Learning preference based advice
        if user_preferences.learning_preferences.time_commitment:
            weekly_hours = user_preferences.learning_preferences.time_commitment
            if weekly_hours < 5:
                insights.append(
                    CareerInsight(
                        type="skill_development",
                        title="Optimize Limited Learning Time",
                        description=f"With {weekly_hours} hours/week, focus on one skill at a time. Use micro-learning approaches and integrate learning into daily work.",
                        confidence=0.8,
                        actionable=True,
                        priority="medium",
                        category="skills",
                        data_points=[f"Available time: {weekly_hours} hours/week"],
                    )
                )
            elif weekly_hours >= 10:
                insights.append(
                    CareerInsight(
                        type="skill_development",
                        title="Accelerated Learning Plan Possible",
                        description=f"With {weekly_hours} hours/week, you can pursue multiple skills simultaneously. Consider structured courses and hands-on projects.",
                        confidence=0.8,
                        actionable=True,
                        priority="medium",
                        category="skills",
                        data_points=[f"Available time: {weekly_hours} hours/week"],
                    )
                )

        # Career transition advice
        current_position = resume_data.get_current_position()
        target_roles = user_preferences.career_goals.target_roles

        if current_position and target_roles:
            current_role = current_position.position.lower()
            transition_needed = any(target_role.lower() not in current_role for target_role in target_roles)

            if transition_needed:
                insights.append(
                    CareerInsight(
                        type="career_strategy",
                        title="Plan Career Transition",
                        description="You're aiming for a role transition. Focus on transferable skills and consider bridge positions that can help you reach your target.",
                        confidence=0.8,
                        actionable=True,
                        priority="high",
                        category="strategy",
                        data_points=[f"From: {current_position.position}", f"To: {', '.join(target_roles)}"],
                    )
                )

        return insights

    def _format_skill_gaps_for_prompt(self, skill_gaps: list[SkillGap]) -> str:
        """Format skill gaps for AI prompt."""
        if not skill_gaps:
            return "No skill gaps identified"

        gap_lines = []
        for gap in skill_gaps[:10]:  # Limit to prevent prompt overflow
            line = f"- {gap.skill_name}: {gap.current_level.value if gap.current_level else 'None'} → {gap.required_level.value} ({gap.priority} priority)"
            if gap.estimated_learning_time:
                line += f" - {gap.estimated_learning_time}"
            gap_lines.append(line)

        return "\n".join(gap_lines)

    def _deduplicate_insights(self, insights: list[CareerInsight]) -> list[CareerInsight]:
        """Remove duplicate insights based on title similarity."""
        unique_insights = []
        seen_titles = set()

        for insight in insights:
            title_lower = insight.title.lower()
            # Check for similar titles
            is_duplicate = any(self._title_similarity(title_lower, seen_title) > 0.8 for seen_title in seen_titles)

            if not is_duplicate:
                unique_insights.append(insight)
                seen_titles.add(title_lower)

        return unique_insights

    def _title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles."""
        # Simple word overlap similarity
        words1 = set(title1.split())
        words2 = set(title2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    async def create_learning_plan(
        self,
        skill_gaps: list[SkillGap],
        learning_preferences: LearningPreferences,
        time_horizon: int = 12,  # months
    ) -> dict[str, Any]:
        """Create a structured learning plan based on skill gaps and preferences."""
        if not skill_gaps:
            return {"plan": [], "summary": "No skill gaps identified for learning plan."}

        # Sort skill gaps by priority and learning time
        sorted_gaps = sorted(
            skill_gaps,
            key=lambda x: (
                {"high": 0, "medium": 1, "low": 2}[x.priority],
                self._extract_months(x.estimated_learning_time or "6 months"),
            ),
        )

        plan = []
        current_month = 0
        weekly_hours = learning_preferences.time_commitment or 5

        for gap in sorted_gaps:
            if current_month >= time_horizon:
                break

            learning_months = self._extract_months(gap.estimated_learning_time or "6 months")
            end_month = min(current_month + learning_months, time_horizon)

            # Adjust learning pace based on available time
            adjusted_months = self._adjust_learning_pace(learning_months, weekly_hours)
            end_month = min(current_month + adjusted_months, time_horizon)

            plan.append(
                {
                    "skill_name": gap.skill_name,
                    "start_month": current_month + 1,
                    "end_month": end_month,
                    "priority": gap.priority,
                    "required_level": gap.required_level.value,
                    "current_level": gap.current_level.value if gap.current_level else "None",
                    "resources": gap.recommended_resources,
                    "weekly_hours": min(weekly_hours, 15),  # Cap at 15 hours per week per skill
                    "milestones": self._generate_learning_milestones(gap, end_month - current_month),
                }
            )

            current_month = end_month

        return {
            "plan": plan,
            "summary": f"Learning plan covering {len(plan)} skills over {current_month} months",
            "total_skills": len(plan),
            "time_horizon_months": current_month,
            "weekly_commitment": weekly_hours,
            "created_at": datetime.now().isoformat(),
        }

    def _extract_months(self, time_string: str) -> int:
        """Extract number of months from time string."""
        import re

        match = re.search(r"(\d+)", time_string)
        return int(match.group(1)) if match else 6

    def _adjust_learning_pace(self, base_months: int, weekly_hours: int) -> int:
        """Adjust learning duration based on available time."""
        # Base assumption: 10 hours/week for base_months
        base_hours_per_week = 10
        adjustment_factor = base_hours_per_week / max(weekly_hours, 2)  # Minimum 2 hours/week
        return max(1, int(base_months * adjustment_factor))

    def _generate_learning_milestones(self, skill_gap: SkillGap, duration_months: int) -> list[str]:
        """Generate learning milestones for a skill."""
        milestones = []

        if not skill_gap.current_level:
            milestones.append("Complete foundational learning materials")
            milestones.append("Build first practice project")
        else:
            current_level = skill_gap.current_level.value
            target_level = skill_gap.required_level.value
            level_diff = target_level - current_level

            if level_diff >= 2:
                milestones.append(f"Advance from {skill_gap.current_level.value} to intermediate level")
                milestones.append(f"Progress from intermediate to {skill_gap.required_level.value}")
            else:
                milestones.append(f"Advance from {skill_gap.current_level.value} to {skill_gap.required_level.value}")

        # Add project-based milestone
        milestones.append("Complete capstone project demonstrating skill proficiency")

        # Add assessment milestone
        milestones.append("Pass skill assessment or obtain certification")

        return milestones

    async def generate_networking_advice(
        self, resume_data: ResumeData, user_preferences: UserPreferences, target_industries: list[str] | None = None
    ) -> dict[str, Any]:
        """Generate networking advice based on career goals and industry."""
        experience_level = "early" if resume_data.get_total_experience_years() < 3 else "experienced"

        networking_strategies = []

        # Experience-based networking advice
        if experience_level == "early":
            networking_strategies.extend(
                [
                    {
                        "strategy": "Build Technical Network",
                        "description": "Focus on GitHub contributions, tech meetups, and online communities",
                        "actions": [
                            "Contribute to open source",
                            "Attend local tech meetups",
                            "Join relevant Discord/Slack communities",
                        ],
                    },
                    {
                        "strategy": "Mentorship Connections",
                        "description": "Find mentors in your target field",
                        "actions": [
                            "Reach out to senior professionals on LinkedIn",
                            "Join mentorship programs",
                            "Ask for informational interviews",
                        ],
                    },
                ]
            )
        else:
            networking_strategies.extend(
                [
                    {
                        "strategy": "Industry Leadership",
                        "description": "Establish yourself as a thought leader",
                        "actions": ["Speak at conferences", "Write technical articles", "Mentor junior professionals"],
                    },
                    {
                        "strategy": "Executive Networking",
                        "description": "Build relationships with decision makers",
                        "actions": [
                            "Join industry associations",
                            "Attend executive events",
                            "Participate in strategic discussions",
                        ],
                    },
                ]
            )

        # Industry-specific advice
        if target_industries:
            for industry in target_industries[:3]:  # Limit to top 3 industries
                industry_lower = industry.lower()
                if "tech" in industry_lower or "software" in industry_lower:
                    networking_strategies.append(
                        {
                            "strategy": "Tech Industry Networking",
                            "description": f"Build connections in the {industry} sector",
                            "actions": [
                                f"Join {industry} professional groups",
                                "Attend hackathons and tech conferences",
                                "Participate in tech forums",
                            ],
                        }
                    )
                elif "finance" in industry_lower or "fintech" in industry_lower:
                    networking_strategies.append(
                        {
                            "strategy": "Finance Industry Networking",
                            "description": f"Build connections in the {industry} sector",
                            "actions": [
                                f"Join {industry} associations",
                                "Attend finance tech events",
                                "Connect with finance professionals",
                            ],
                        }
                    )

        return {
            "strategies": networking_strategies,
            "experience_level": experience_level,
            "target_industries": target_industries or [],
            "generated_at": datetime.now().isoformat(),
        }

    async def generate_personal_branding_advice(
        self, resume_data: ResumeData, user_preferences: UserPreferences
    ) -> dict[str, Any]:
        """Generate personal branding advice."""
        current_position = resume_data.get_current_position()
        top_skills = resume_data.skills(5)  # type: ignore[attr-defined]
        career_goals = user_preferences.career_goals

        advice = {"online_presence": [], "content_strategy": [], "profile_optimization": []}

        # Online presence advice
        if "linkedin" in resume_data.personal_info:
            advice["online_presence"].append("Optimize LinkedIn profile with target keywords and achievements")
        else:
            advice["online_presence"].append(
                "Create and optimize LinkedIn profile - essential for professional networking"
            )

        if "github" in resume_data.personal_info:
            advice["online_presence"].append("Maintain active GitHub with quality projects and contributions")
        elif any("developer" in skill.name.lower() or "engineer" in skill.name.lower() for skill in top_skills):
            advice["online_presence"].append("Create GitHub profile and showcase development projects")

        # Content strategy based on skills and goals
        if career_goals.target_roles:
            advice["content_strategy"].append(f"Create content about {', '.join(career_goals.target_roles[:2])} topics")

        if top_skills:
            advice["content_strategy"].append(
                f"Share insights about {', '.join([skill.name for skill in top_skills[:3]])}"
            )

        advice["content_strategy"].extend(
            [
                "Write about your learning journey and challenges",
                "Share project experiences and lessons learned",
                "Comment on industry trends and developments",
            ]
        )

        # Profile optimization
        if current_position:
            advice["profile_optimization"].append(
                f"Update headline to reflect transition from {current_position.position} to target roles"
            )

        advice["profile_optimization"].extend(
            [
                "Quantify achievements with metrics and results",
                "Include keywords from target job descriptions",
                "Get recommendations from colleagues and managers",
                "Customize profile for your target industries",
            ]
        )

        return {
            "advice": advice,
            "focus_areas": ["LinkedIn optimization", "Content creation", "Professional networking"],
            "timeline": "30-60 days to see initial results",
            "generated_at": datetime.now().isoformat(),
        }

    async def chat_with_coach(
        self, master_profile, message: str, conversation_history: list[dict[str, str]] | None = None
    ) -> dict[str, Any]:
        """Interactive chat with career coach."""
        if not conversation_history:
            conversation_history = []

        try:
            if self.claude_client:
                return await self._ai_generate_coaching_response(
                    message, {"master_profile": master_profile, "conversation_history": conversation_history}
                )
            return await self._rule_based_coaching_response(
                message, {"master_profile": master_profile, "conversation_history": conversation_history}
            )
        except Exception as e:
            logger.error(f"Chat with coach failed: {e}")
            return {
                "response": "I'm sorry, I'm having trouble providing coaching advice right now. Please try again later.",
                "success": False,
                "error": str(e),
            }

    async def generate_networking_guidance(self, master_profile, target_role: str, industry: str) -> dict[str, Any]:
        """Generate networking guidance for career transition."""
        # Alias to existing method for compatibility
        # type: ignore[arg-type]
        # type: ignore[arg-type]
        return await self.generate_networking_advice(master_profile, target_role, industry)  # type: ignore[arg-type]  # type: ignore[arg-type]

    async def generate_interview_preparation(
        self, master_profile, target_role: str, company_type: str
    ) -> dict[str, Any]:
        """Generate interview preparation guidance."""
        guidance = {
            "preparation_areas": [],
            "common_questions": [],
            "success_tips": [],
            "company_research": [],
            "timeline": "1-2 weeks preparation",
        }

        # Skills-based preparation
        guidance["preparation_areas"] = [
            "Review your STAR method examples for key accomplishments",
            "Prepare stories that demonstrate problem-solving skills",
            "Research the company's recent projects and challenges",
            "Practice technical questions relevant to the role",
            "Prepare thoughtful questions to ask the interviewer",
        ]

        # Common questions by role type
        if "engineer" in target_role.lower() or "developer" in target_role.lower():
            guidance["common_questions"] = [
                "Tell me about a challenging technical problem you solved",
                "How do you approach debugging complex issues?",
                "What's your experience with [relevant technologies]?",
                "How do you stay current with technology trends?",
                "Describe a project you're proud of and why",
            ]
        else:
            guidance["common_questions"] = [
                "Tell me about yourself and your career goals",
                "Why are you interested in this role/company?",
                "Describe a time you faced a major challenge",
                "What are your greatest strengths and weaknesses?",
                "Where do you see yourself in 5 years?",
            ]

        # Success tips
        guidance["success_tips"] = [
            "Research the interviewer(s) on LinkedIn beforehand",
            "Bring a notebook with prepared questions and talking points",
            "Practice your 30-second elevator pitch",
            "Prepare 3-5 specific examples of your accomplishments",
            "Follow up with a personalized thank-you note within 24 hours",
        ]

        # Company research points
        guidance["company_research"] = [
            "Recent company news and announcements",
            "Key products or services",
            "Company culture and values",
            "Competitors and market position",
            "Interview team members' backgrounds",
        ]

        return guidance

    async def generate_salary_negotiation_guidance(
        self, master_profile, offer_details: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate salary negotiation guidance."""
        guidance = {
            "research_steps": [],
            "negotiation_points": [],
            "timing_strategy": [],
            "common_mistakes": [],
            "sample_scripts": [],
        }

        # Research steps
        guidance["research_steps"] = [
            "Research salary ranges for similar roles in your location",
            "Consider your total compensation package, not just base salary",
            "Factor in your experience level and special skills",
            "Research the company's salary structure and equity policies",
            "Know your market value and walk-away point",
        ]

        # Negotiation points
        guidance["negotiation_points"] = [
            "Base salary adjustments",
            "Performance bonuses and commission structures",
            "Equity/stock options and vesting schedules",
            "Additional vacation time and flexible work arrangements",
            "Professional development and education budgets",
            "Signing bonuses and relocation assistance",
        ]

        # Timing strategy
        guidance["timing_strategy"] = [
            "Wait until you have a formal offer before negotiating",
            "Express enthusiasm while discussing compensation",
            "Ask for 24-48 hours to review the offer carefully",
            "Negotiate key points via email or phone, not text",
            "Get all agreements in writing before accepting",
        ]

        # Common mistakes to avoid
        guidance["common_mistakes"] = [
            "Accepting the first offer without research",
            "Focusing only on base salary",
            "Making demands instead of respectful requests",
            "Negotiating before receiving a formal offer",
            "Forgetting to consider the total compensation package",
        ]

        # Sample scripts
        guidance["sample_scripts"] = [
            "Thank you for the offer! I'm very excited about this opportunity. Based on my research and the value I can bring, I was hoping for a base salary closer to $X.",
            "I appreciate the generous offer. Would it be possible to discuss the equity component or add a signing bonus?",
            "This is a strong offer. I'd like to request an additional week of vacation time to help with work-life balance.",
        ]

        return guidance

    async def _ai_generate_coaching_response(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        """Generate AI-powered coaching response."""
        # This would integrate with Claude API in production
        return {"response": f"AI coaching response to: {message}", "success": True}

    async def _rule_based_coaching_response(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        """Generate rule-based coaching response."""
        # Simple rule-based responses
        responses = {
            "interview": "Focus on preparing STAR method examples and researching the company.",
            "salary": "Research market rates and consider the total compensation package.",
            "skills": "Identify skill gaps and create a learning plan with specific milestones.",
            "career": "Clarify your goals and work backwards to create a career path.",
        }

        response = "I'm here to help with your career development. "
        for key, value in responses.items():
            if key in message.lower():
                response += value
                break
        else:
            response += "Could you tell me more about what specific aspect you'd like guidance on?"

        return {"response": response, "success": True}
