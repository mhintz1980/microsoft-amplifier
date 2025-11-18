"""
Job Matcher Service

Matches user profiles with job opportunities, calculates match scores,
and provides job application recommendations.
"""

import logging
from datetime import UTC
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any

from ..models.master_profile import JobMatch
from ..models.master_profile import SkillGap
from ..models.resume_data import ResumeData
from ..models.resume_data import SkillLevel
from ..models.user_preferences import UserPreferences

logger = logging.getLogger(__name__)


class JobMatcher:
    """Service for matching user profiles with job opportunities."""

    def __init__(self, claude_client=None):
        """Initialize job matcher with optional Claude client for AI analysis."""
        self.claude_client = claude_client

    async def find_job_matches(
        self,
        resume_data: ResumeData,
        user_preferences: UserPreferences,
        skill_gaps: list[SkillGap],
        job_postings: list[dict[str, Any]] | None = None,
        limit: int = 20,
    ) -> list[JobMatch]:
        """Find and rank job matches based on user profile and preferences.

        Args:
            resume_data: User's resume data
            user_preferences: User preferences and career goals
            skill_gaps: Identified skill gaps
            job_postings: List of job postings to match against (if None, uses sample data)
            limit: Maximum number of matches to return

        Returns:
            List of job matches sorted by relevance score
        """
        if not job_postings:
            job_postings = self._get_sample_job_postings()

        try:
            if self.claude_client:
                return await self._ai_job_matching(resume_data, user_preferences, skill_gaps, job_postings, limit)
            return await self._rule_based_job_matching(resume_data, user_preferences, skill_gaps, job_postings, limit)

        except Exception as e:
            logger.error(f"Job matching failed: {e}")
            return await self._rule_based_job_matching(resume_data, user_preferences, skill_gaps, job_postings, limit)

    async def _ai_job_matching(
        self,
        resume_data: ResumeData,
        user_preferences: UserPreferences,
        skill_gaps: list[SkillGap],
        job_postings: list[dict[str, Any]],
        limit: int,
    ) -> list[JobMatch]:
        """Use AI to analyze and score job matches."""
        user_skills = resume_data.get_all_skills()
        target_roles = user_preferences.career_goals.target_roles
        current_position = resume_data.get_current_position()

        matches = []

        for job in job_postings[: limit * 2]:  # Process more jobs to find best matches
            try:
                # Create AI prompt for each job
                prompt = f"""
Analyze how well this user profile matches the following job opportunity.

User Profile:
- Current Position: {current_position.position if current_position else "Not specified"}
- Total Experience: {resume_data.get_total_experience_years():.1f} years
- Top Skills: {", ".join([skill.name for skill in user_skills[:10]])}
- Target Roles: {", ".join(target_roles) if target_roles else "Not specified"}

Job Opportunity:
- Title: {job.get("title", "N/A")}
- Company: {job.get("company", "N/A")}
- Location: {job.get("location", "N/A")}
- Description: {job.get("description", "N/A")[:500]}...
- Required Skills: {job.get("required_skills", [])}
- Salary: {job.get("salary_range", "Not specified")}

Analyze and return JSON with this structure:
{{
    "match_score": 0.85,
    "key_matches": [
        "Strong match in Python development experience",
        "5+ years of experience aligns with senior level requirement"
    ],
    "skill_gaps": [
        {{
            "skill_name": "Cloud Architecture",
            "current_level": "intermediate",
            "required_level": "advanced",
            "priority": "medium"
        }}
    ],
    "overall_assessment": "Brief assessment of the match quality",
    "recommendation": "Advice on pursuing this opportunity"
}}

Rate the match from 0.0 to 1.0 where:
- 0.8-1.0: Excellent match, highly recommended
- 0.6-0.8: Good match, worth applying
- 0.4-0.6: Moderate match, consider with caveats
- 0.0-0.4: Poor match, not recommended
"""

                # Call AI for analysis
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

                if result:
                    # Parse AI response
                    from ...ccsdk_toolkit.defensive.llm_parsing import parse_llm_json

                    analysis = parse_llm_json(result)

                    if analysis:
                        # Create skill gap objects
                        job_skill_gaps = []
                        for gap_data in analysis.get("skill_gaps", []):  # type: ignore[attr-defined]
                            current_level = self._map_skill_level(gap_data.get("current_level", "intermediate"))
                            required_level = self._map_skill_level(gap_data.get("required_level", "intermediate"))

                            skill_gap = SkillGap(
                                skill_name=gap_data.get("skill_name", "Unknown"),
                                current_level=current_level,
                                required_level=required_level,
                                priority=gap_data.get("priority", "medium"),
                            )
                            job_skill_gaps.append(skill_gap)

                        # Create job match
                        job_match = JobMatch(
                            job_id=job.get("id", f"job_{len(matches)}"),
                            title=job.get("title", "N/A"),
                            company=job.get("company", "N/A"),
                            location=job.get("location", "N/A"),
                            match_score=analysis.get("match_score", 0.5),  # type: ignore[attr-defined]
                            key_matches=analysis.get("key_matches", []),  # type: ignore[attr-defined]
                            skill_gaps=job_skill_gaps,
                            salary_range=job.get("salary_range"),
                            posted_date=self._parse_date(job.get("posted_date")),
                            application_deadline=self._parse_date(job.get("application_deadline")),
                        )

                        matches.append(job_match)

            except Exception as e:
                logger.warning(f"Failed to analyze job {job.get('title', 'Unknown')}: {e}")
                continue

        # Sort by match score and return top matches
        matches.sort(key=lambda x: x.match_score, reverse=True)
        return matches[:limit]

    async def _rule_based_job_matching(
        self,
        resume_data: ResumeData,
        user_preferences: UserPreferences,
        skill_gaps: list[SkillGap],
        job_postings: list[dict[str, Any]],
        limit: int,
    ) -> list[JobMatch]:
        """Rule-based job matching as fallback."""
        logger.info("Using rule-based job matching")

        user_skills = resume_data.get_all_skills()
        user_skill_names = {skill.name.lower() for skill in user_skills}
        target_roles = [role.lower() for role in user_preferences.career_goals.target_roles]
        target_locations = [loc.lower() for loc in user_preferences.career_goals.locations]

        matches = []

        for job in job_postings:
            try:
                match_score = 0.0
                key_matches = []
                job_skill_gaps = []

                # Title matching (30% weight)
                job_title = job.get("title", "").lower()
                title_score = 0.0
                for target_role in target_roles:
                    if target_role in job_title:
                        title_score = max(title_score, self._similarity(target_role, job_title))
                match_score += title_score * 0.3
                if title_score > 0.7:
                    key_matches.append(f"Strong title match: {job.get('title')}")

                # Skills matching (40% weight)
                required_skills = [skill.lower() for skill in job.get("required_skills", [])]
                if required_skills:
                    matching_skills = []
                    missing_skills = []

                    for skill in required_skills:
                        if any(user_skill in skill or skill in user_skill for user_skill in user_skill_names):
                            matching_skills.append(skill)
                        else:
                            missing_skills.append(skill)

                    skill_match_ratio = len(matching_skills) / len(required_skills) if required_skills else 0
                    match_score += skill_match_ratio * 0.4

                    if matching_skills:
                        key_matches.append(f"Skills match: {', '.join(matching_skills[:3])}")

                    # Create skill gaps for missing skills
                    for skill in missing_skills[:5]:  # Limit to top 5 missing skills
                        skill_gap = SkillGap(
                            skill_name=skill,
                            current_level=None,
                            required_level=SkillLevel.INTERMEDIATE,
                            priority="high" if len(missing_skills) <= 2 else "medium",
                        )
                        job_skill_gaps.append(skill_gap)

                # Location matching (15% weight)
                job_location = job.get("location", "").lower()
                location_score = 0.0
                if target_locations:
                    for target_loc in target_locations:
                        if target_loc in job_location or "remote" in job_location:
                            location_score = max(location_score, 0.8 if "remote" in job_location else 1.0)
                match_score += location_score * 0.15
                if location_score > 0.5:
                    key_matches.append(f"Location match: {job.get('location')}")

                # Experience matching (15% weight)
                user_experience = resume_data.get_total_experience_years()
                required_experience = job.get("experience_required", 0)

                if required_experience:
                    if user_experience >= required_experience:
                        exp_score = min(1.0, user_experience / required_experience)
                        key_matches.append(f"Experience requirement met: {user_experience:.1f} years")
                    else:
                        exp_score = user_experience / required_experience
                else:
                    exp_score = 0.8  # Benefit of doubt if no requirement specified

                match_score += exp_score * 0.15

                # Only include matches with decent scores
                if match_score > 0.3:
                    job_match = JobMatch(
                        job_id=job.get("id", f"job_{len(matches)}"),
                        title=job.get("title", "N/A"),
                        company=job.get("company", "N/A"),
                        location=job.get("location", "N/A"),
                        match_score=match_score,
                        key_matches=key_matches,
                        skill_gaps=job_skill_gaps,
                        salary_range=job.get("salary_range"),
                        posted_date=self._parse_date(job.get("posted_date")),
                        application_deadline=self._parse_date(job.get("application_deadline")),
                    )
                    matches.append(job_match)

            except Exception as e:
                logger.warning(f"Failed to process job {job.get('title', 'Unknown')}: {e}")
                continue

        # Sort by match score and return top matches
        matches.sort(key=lambda x: x.match_score, reverse=True)
        return matches[:limit]

    def _get_sample_job_postings(self) -> list[dict[str, Any]]:
        """Get sample job postings for demonstration."""
        return [
            {
                "id": "job_001",
                "title": "Senior Software Engineer",
                "company": "TechCorp Inc.",
                "location": "San Francisco, CA",
                "description": "We're looking for a Senior Software Engineer to join our platform team...",
                "required_skills": ["Python", "JavaScript", "React", "AWS", "System Design"],
                "experience_required": 5,
                "salary_range": {"min": 130000, "max": 180000},
                "posted_date": "2024-01-15",
                "application_deadline": "2024-02-15",
            },
            {
                "id": "job_002",
                "title": "Full Stack Developer",
                "company": "StartupXYZ",
                "location": "Remote",
                "description": "Join our fast-growing startup as a Full Stack Developer...",
                "required_skills": ["Python", "React", "PostgreSQL", "Docker", "Git"],
                "experience_required": 3,
                "salary_range": {"min": 90000, "max": 130000},
                "posted_date": "2024-01-20",
                "application_deadline": "2024-02-20",
            },
            {
                "id": "job_003",
                "title": "Data Scientist",
                "company": "DataDrive Analytics",
                "location": "New York, NY",
                "description": "Seeking an experienced Data Scientist to join our ML team...",
                "required_skills": ["Python", "Machine Learning", "Statistics", "SQL", "TensorFlow"],
                "experience_required": 4,
                "salary_range": {"min": 110000, "max": 160000},
                "posted_date": "2024-01-10",
                "application_deadline": "2024-02-10",
            },
            {
                "id": "job_004",
                "title": "DevOps Engineer",
                "company": "CloudTech Solutions",
                "location": "Seattle, WA",
                "description": "Looking for a DevOps Engineer to help build our infrastructure...",
                "required_skills": ["AWS", "Docker", "Kubernetes", "CI/CD", "Linux"],
                "experience_required": 4,
                "salary_range": {"min": 120000, "max": 170000},
                "posted_date": "2024-01-18",
                "application_deadline": "2024-02-18",
            },
            {
                "id": "job_005",
                "title": "Product Manager",
                "company": "InnovateTech",
                "location": "Austin, TX",
                "description": "Join our product team as a Product Manager...",
                "required_skills": [
                    "Product Management",
                    "Data Analysis",
                    "Communication",
                    "Strategy",
                    "User Research",
                ],
                "experience_required": 5,
                "salary_range": {"min": 110000, "max": 150000},
                "posted_date": "2024-01-22",
                "application_deadline": "2024-02-22",
            },
        ]

    def _map_skill_level(self, level_str: str) -> SkillLevel:
        """Map string to SkillLevel enum."""
        level_mapping = {
            "beginner": SkillLevel.BEGINNER,
            "intermediate": SkillLevel.INTERMEDIATE,
            "advanced": SkillLevel.ADVANCED,
            "expert": SkillLevel.EXPERT,
        }
        return level_mapping.get(level_str.lower(), SkillLevel.INTERMEDIATE)

    def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parse date string to datetime object."""
        if not date_str:
            return None

        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            try:
                # Try common formats
                return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
            except ValueError:
                logger.warning(f"Could not parse date: {date_str}")
                return None

    def _similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, str1, str2).ratio()

    async def analyze_job_market(
        self,
        resume_data: ResumeData,
        user_preferences: UserPreferences,
        job_postings: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Analyze job market trends for user's profile and goals."""
        if not job_postings:
            job_postings = self._get_sample_job_postings()

        user_skills = resume_data.get_all_skills()
        user_skill_names = {skill.name.lower() for skill in user_skills}

        # Skill demand analysis
        skill_demand = {}
        for job in job_postings:
            required_skills = job.get("required_skills", [])
            for skill in required_skills:
                skill_lower = skill.lower()
                skill_demand[skill_lower] = skill_demand.get(skill_lower, 0) + 1

        # Sort skills by demand
        top_demanded_skills = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)

        # User's skill market value
        user_skill_value = {}
        for skill_name in user_skill_names:
            user_skill_value[skill_name] = skill_demand.get(skill_name, 0)

        # Salary analysis
        salaries = []
        for job in job_postings:
            salary_range = job.get("salary_range")
            if salary_range and isinstance(salary_range, dict):
                salaries.append(
                    {
                        "min": salary_range.get("min", 0),
                        "max": salary_range.get("max", 0),
                        "average": (salary_range.get("min", 0) + salary_range.get("max", 0)) / 2,
                    }
                )

        avg_salary = sum(s["average"] for s in salaries) / len(salaries) if salaries else 0

        # Location analysis
        locations = {}
        for job in job_postings:
            location = job.get("location", "Unknown")
            locations[location] = locations.get(location, 0) + 1

        return {
            "top_demanded_skills": [{"skill": skill, "demand": count} for skill, count in top_demanded_skills[:10]],
            "user_skill_market_value": [
                {"skill": skill, "demand": count}
                for skill, count in sorted(user_skill_value.items(), key=lambda x: x[1], reverse=True)[:10]
            ],
            "average_salary": int(avg_salary),
            "salary_range": {
                "min": min(s["min"] for s in salaries) if salaries else 0,
                "max": max(s["max"] for s in salaries) if salaries else 0,
            },
            "popular_locations": [
                {"location": loc, "count": count}
                for loc, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)
            ],
            "total_jobs_analyzed": len(job_postings),
            "analysis_date": datetime.now().isoformat(),
        }

    async def generate_application_strategy(
        self, job_matches: list[JobMatch], resume_data: ResumeData, user_preferences: UserPreferences
    ) -> dict[str, Any]:
        """Generate application strategy for job matches."""
        if not job_matches:
            return {"strategy": [], "summary": "No job matches available for application strategy."}

        # Categorize matches
        excellent_matches = [job for job in job_matches if job.match_score >= 0.8]
        good_matches = [job for job in job_matches if 0.6 <= job.match_score < 0.8]
        moderate_matches = [job for job in job_matches if 0.4 <= job.match_score < 0.6]

        strategy = []

        # Priority 1: Apply to excellent matches immediately
        if excellent_matches:
            strategy.append(
                {
                    "priority": 1,
                    "category": "Immediate Applications",
                    "description": f"Apply immediately to {len(excellent_matches)} excellent matches",
                    "jobs": [
                        {
                            "title": job.title,
                            "company": job.company,
                            "match_score": job.match_score,
                            "deadline": job.application_deadline.isoformat() if job.application_deadline else None,
                            "key_talking_points": job.key_matches[:3],
                        }
                        for job in excellent_matches[:5]
                    ],
                    "timeline": "This week",
                    "actions": [
                        "Customize resume for each position",
                        "Write targeted cover letters",
                        "Prepare for technical interviews",
                        "Leverage your strongest matching points",
                    ],
                }
            )

        # Priority 2: Prepare for good matches
        if good_matches:
            strategy.append(
                {
                    "priority": 2,
                    "category": "Targeted Applications",
                    "description": f"Prepare and apply to {len(good_matches)} good matches",
                    "jobs": [
                        {
                            "title": job.title,
                            "company": job.company,
                            "match_score": job.match_score,
                            "skill_gaps_to_address": [gap.skill_name for gap in job.skill_gaps[:3]],
                        }
                        for job in good_matches[:5]
                    ],
                    "timeline": "Next 2 weeks",
                    "actions": [
                        "Address key skill gaps quickly",
                        "Network with company employees",
                        "Research company culture and values",
                        "Prepare examples of relevant experience",
                    ],
                }
            )

        # Priority 3: Consider moderate matches
        if moderate_matches:
            strategy.append(
                {
                    "priority": 3,
                    "category": "Backup Options",
                    "description": f"Consider {len(moderate_matches)} moderate matches as backup options",
                    "jobs": [
                        {
                            "title": job.title,
                            "company": job.company,
                            "match_score": job.match_score,
                            "concerns": job.skill_gaps[:2],
                        }
                        for job in moderate_matches[:3]
                    ],
                    "timeline": "Next month",
                    "actions": [
                        "Evaluate if skill gaps are addressable",
                        "Consider if role aligns with long-term goals",
                        "Reach out for informational interviews",
                        "Assess company growth potential",
                    ],
                }
            )

        # Overall application strategy
        overall_strategy = {
            "total_applications_planned": len(excellent_matches) + len(good_matches) + len(moderate_matches),
            "focus_areas": [],
            "success_factors": [],
        }

        if excellent_matches:
            overall_strategy["focus_areas"].append("Leverage strong matches to get interviews quickly")

        if good_matches:
            overall_strategy["focus_areas"].append("Address skill gaps to improve match quality")

        overall_strategy["success_factors"].extend(
            [
                "Customize applications for each role",
                "Follow up within 1 week of application",
                "Prepare STAR method examples for interviews",
                "Research each company thoroughly",
            ]
        )

        return {
            "strategy": strategy,
            "overall_strategy": overall_strategy,
            "summary": f"Application strategy for {len(job_matches)} job matches",
            "created_at": datetime.now().isoformat(),
        }

    async def search_jobs(self, search_criteria: dict[str, Any]) -> list[dict[str, Any]]:
        """Search for jobs based on provided criteria.

        Args:
            search_criteria: Dictionary containing search parameters like keywords, location, etc.

        Returns:
            List of job postings matching the criteria
        """
        # This would integrate with external job APIs in production
        # For now, return filtered sample data

        keywords = search_criteria.get("keywords", [])
        location = search_criteria.get("location", "")
        experience_level = search_criteria.get("experience_level", "")

        sample_jobs = self._get_sample_job_postings()

        filtered_jobs = []
        for job in sample_jobs:
            match = True

            # Filter by keywords
            if keywords:
                job_text = f"{job['title']} {job['description']} {' '.join(job.get('requirements', []))}".lower()
                if not any(keyword.lower() in job_text for keyword in keywords):
                    match = False

            # Filter by location
            if location and location.lower() not in job.get("location", "").lower():
                match = False

            # Filter by experience level
            if experience_level and experience_level.lower() not in job.get("experience_level", "").lower():
                match = False

            if match:
                filtered_jobs.append(job)

        return filtered_jobs
