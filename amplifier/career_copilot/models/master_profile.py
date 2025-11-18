"""
Master Profile Model

Central profile that combines resume data, user preferences, and AI-generated insights
to provide a comprehensive view of the user's professional profile and career development.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from .resume_data import ResumeData
from .resume_data import Skill
from .resume_data import SkillLevel
from .user_preferences import UserPreferences


class ProfileStatus(str, Enum):
    """Profile completion status."""

    DRAFT = "draft"
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"
    OPTIMIZED = "optimized"


class SkillGap(BaseModel):
    """Represents a gap between current skills and required skills."""

    skill_name: str = Field(..., description="Name of the skill")
    current_level: SkillLevel | None = Field(None, description="Current skill level")
    required_level: SkillLevel = Field(..., description="Required skill level")
    priority: str = Field(..., description="Priority level (high, medium, low)")
    estimated_learning_time: str | None = Field(None, description="Estimated time to acquire skill")
    recommended_resources: list[str] = Field(default_factory=list, description="Recommended learning resources")


class CareerInsight(BaseModel):
    """AI-generated career insight or recommendation."""

    type: str = Field(..., description="Type of insight (skill_gap, opportunity, trend, etc.)")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed description of the insight")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level in this insight")
    actionable: bool = Field(default=True, description="Whether this insight is actionable")
    priority: str = Field(default="medium", description="Priority level")
    category: str = Field(..., description="Category of the insight")
    data_points: list[str] = Field(default_factory=list, description="Supporting data points")
    created_at: datetime = Field(default_factory=datetime.now, description="When insight was generated")


class JobMatch(BaseModel):
    """Job match with relevance score and key details."""

    job_id: str = Field(..., description="Unique job identifier")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    match_score: float = Field(..., ge=0, le=1, description="Match relevance score")
    key_matches: list[str] = Field(default_factory=list, description="Key matching points")
    skill_gaps: list[SkillGap] = Field(default_factory=list, description="Missing or weak skills")
    salary_range: dict[str, Any] | None = Field(None, description="Salary information")
    posted_date: datetime | None = Field(None, description="When job was posted")
    application_deadline: datetime | None = Field(None, description="Application deadline")
    status: str = Field(default="new", description="Match status (new, viewed, applied, etc.)")
    notes: str | None = Field(None, description="User notes about this match")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class MasterProfile(BaseModel):
    """Master profile combining resume, preferences, and AI insights."""

    profile_id: str = Field(..., description="Unique profile identifier")
    user_id: str | None = Field(None, description="User identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="When profile was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When profile was last updated")
    last_analyzed: datetime | None = Field(None, description="When AI analysis was last run")

    # Core data
    resume_data: ResumeData = Field(..., description="Resume and professional information")
    user_preferences: UserPreferences = Field(..., description="User preferences and goals")

    # AI-generated insights
    skill_gaps: list[SkillGap] = Field(default_factory=list, description="Identified skill gaps")
    career_insights: list[CareerInsight] = Field(
        default_factory=list, description="Career insights and recommendations"
    )
    job_matches: list[JobMatch] = Field(default_factory=list, description="Matching job opportunities")
    career_trajectory: dict[str, Any] | None = Field(None, description="Predicted career trajectory")

    # Profile metadata
    status: ProfileStatus = Field(default=ProfileStatus.DRAFT, description="Profile completion status")
    completion_percentage: float = Field(default=0.0, ge=0, le=100, description="Profile completion percentage")
    overall_score: float | None = Field(None, ge=0, le=100, description="Overall profile strength score")
    market_readiness: float | None = Field(None, ge=0, le=100, description="Job market readiness score")

    # Analytics and tracking
    profile_views: int = Field(default=0, description="Number of profile views")
    job_applications: int = Field(default=0, description="Number of job applications through profile")
    skills_updated: list[str] = Field(default_factory=list, description="Skills that have been updated")
    goals_achieved: list[str] = Field(default_factory=list, description="Career goals that have been achieved")

    @field_validator("profile_id")
    @classmethod
    def validate_profile_id(cls, v):
        """Ensure profile ID is a valid identifier."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Profile ID cannot be empty")
        return v.strip()

    def update_timestamp(self):
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()

    def calculate_completion(self) -> float:
        """Calculate profile completion percentage."""
        completion_points = 0
        total_points = 100

        # Resume data (50 points)
        if self.resume_data.personal_info:
            completion_points += 10
        if self.resume_data.summary:
            completion_points += 10
        if self.resume_data.work_experience:
            completion_points += 15
        if self.resume_data.education:
            completion_points += 10
        if self.resume_data.skills:
            completion_points += 5

        # User preferences (30 points)
        if self.user_preferences.career_goals.target_roles:
            completion_points += 10
        if self.user_preferences.career_goals.target_industries:
            completion_points += 5
        if self.user_preferences.career_goals.salary_range:
            completion_points += 5
        if self.user_preferences.learning_preferences.preferred_formats:
            completion_points += 5
        if self.user_preferences.learning_preferences.topics_of_interest:
            completion_points += 5

        # Additional info (20 points)
        if self.resume_data.certifications:
            completion_points += 5
        if self.resume_data.projects:
            completion_points += 5
        if self.user_preferences.career_goals.locations:
            completion_points += 5
        if self.user_preferences.career_goals.priorities:
            completion_points += 5

        self.completion_percentage = (completion_points / total_points) * 100
        return self.completion_percentage

    def get_top_skills(self, limit: int = 10) -> list[Skill]:
        """Get top skills by level and experience."""
        all_skills = self.resume_data.get_all_skills()

        # Sort by level (expert first) then by years of experience
        def skill_priority(skill: Skill) -> tuple:
            level_priority = {
                SkillLevel.EXPERT: 4,
                SkillLevel.ADVANCED: 3,
                SkillLevel.INTERMEDIATE: 2,
                SkillLevel.BEGINNER: 1,
            }
            return (level_priority.get(skill.level, 0), skill.years_experience or 0)

        return sorted(all_skills, key=skill_priority, reverse=True)[:limit]

    def get_skill_gaps_by_priority(self, priority: str = "high") -> list[SkillGap]:
        """Get skill gaps filtered by priority."""
        return [gap for gap in self.skill_gaps if gap.priority == priority]

    def add_insight(self, insight: CareerInsight):
        """Add a new career insight."""
        self.career_insights.append(insight)
        self.update_timestamp()

    def add_job_match(self, job_match: JobMatch):
        """Add a new job match."""
        self.job_matches.append(job_match)
        self.update_timestamp()

    def get_active_goals(self) -> list[str]:
        """Get active career goals based on preferences."""
        goals = []
        if self.user_preferences.career_goals.target_roles:
            goals.extend(self.user_preferences.career_goals.target_roles)
        if self.user_preferences.career_goals.target_industries:
            goals.extend(self.user_preferences.career_goals.target_industries)
        return goals

    def generate_summary(self) -> dict[str, Any]:
        """Generate a summary of the master profile."""
        return {
            "profile_id": self.profile_id,
            "status": self.status.value,
            "completion_percentage": self.completion_percentage,
            "total_experience_years": self.resume_data.get_total_experience_years(),
            "current_position": (
                self.resume_data.get_current_position().position  # type: ignore[assignment]
                if self.resume_data.get_current_position() is not None
                else None
            ),
            "total_skills": len(self.resume_data.get_all_skills()),
            "skill_gaps": len(self.skill_gaps),
            "job_matches": len(self.job_matches),
            "career_insights": len(self.career_insights),
            "target_roles": self.user_preferences.career_goals.target_roles,
            "last_updated": self.updated_at.isoformat(),
        }

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}
        json_schema_extra = {
            "example": {
                "profile_id": "profile_12345",
                "user_id": "user_67890",
                "resume_data": {
                    "personal_info": {"name": "John Doe", "email": "john@example.com"},
                    "summary": "Experienced software developer",
                    "work_experience": [],
                    "skills": [],
                },
                "user_preferences": {
                    "career_goals": {"target_roles": ["Senior Software Engineer"], "target_industries": ["Technology"]}
                },
                "skill_gaps": [],
                "career_insights": [],
                "job_matches": [],
                "status": "incomplete",
                "completion_percentage": 45.0,
            }
        }
