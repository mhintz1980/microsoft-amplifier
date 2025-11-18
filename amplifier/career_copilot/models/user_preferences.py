"""
User Preferences and Career Goals Models

Models for representing user preferences, career goals, and settings for
personalized career guidance and recommendations.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class WorkEnvironment(str, Enum):
    """Preferred work environment types."""

    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on_site"
    FLEXIBLE = "flexible"


class CompanySize(str, Enum):
    """Preferred company sizes."""

    STARTUP = "startup"  # 1-50 employees
    SMALL = "small"  # 51-200 employees
    MEDIUM = "medium"  # 201-1000 employees
    LARGE = "large"  # 1001-10000 employees
    ENTERPRISE = "enterprise"  # 10000+ employees


class CareerLevel(str, Enum):
    """Career level targets."""

    ENTRY = "entry_level"
    JUNIOR = "junior"
    MID = "mid_level"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"


class LearningStyle(str, Enum):
    """Preferred learning styles."""

    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"
    MIXED = "mixed"


class CareerGoals(BaseModel):
    """Career goals and aspirations."""

    target_roles: list[str] = Field(default_factory=list, description="Target job titles or roles")
    target_industries: list[str] = Field(default_factory=list, description="Preferred industries")
    target_companies: list[str] = Field(default_factory=list, description="Dream companies to work for")
    career_level_target: CareerLevel | None = Field(None, description="Target career level")
    salary_range: dict[str, int] | None = Field(None, description="Expected salary range (min/max)")
    locations: list[str] = Field(default_factory=list, description="Preferred work locations")
    work_environment: WorkEnvironment | None = Field(None, description="Preferred work environment")
    company_size_preference: CompanySize | None = Field(None, description="Preferred company size")
    time_to_goal: int | None = Field(None, ge=1, le=10, description="Years to achieve goal")
    priorities: list[str] = Field(
        default_factory=list, description="Career priorities (e.g., work-life balance, salary, growth, impact)"
    )
    deal_breakers: list[str] = Field(
        default_factory=list, description="Things that would prevent accepting a job offer"
    )

    @field_validator("salary_range")
    @classmethod
    def validate_salary_range(cls, v):
        """Ensure salary range has valid min/max values."""
        if v:
            if "min" not in v or "max" not in v:
                raise ValueError("Salary range must include 'min' and 'max' values")
            if v["min"] >= v["max"]:
                raise ValueError("Salary minimum must be less than maximum")
        return v


class LearningPreferences(BaseModel):
    """Learning and development preferences."""

    learning_style: LearningStyle | None = Field(None, description="Preferred learning style")
    preferred_formats: list[str] = Field(
        default_factory=list, description="Preferred learning formats (courses, books, videos, mentorship, etc.)"
    )
    time_commitment: int | None = Field(None, ge=1, le=40, description="Hours per week for learning")
    budget: dict[str, Any] | None = Field(None, description="Learning budget (monthly/yearly)")
    topics_of_interest: list[str] = Field(default_factory=list, description="Topics interested in learning")
    certification_goals: list[str] = Field(default_factory=list, description="Certifications to pursue")
    mentorship_interest: bool = Field(default=False, description="Interest in mentorship programs")
    group_learning: bool = Field(default=False, description="Preference for group vs individual learning")


class CommunicationPreferences(BaseModel):
    """Communication and interaction preferences."""

    language: str = Field(default="English", description="Preferred communication language")
    tone: str = Field(default="professional", description="Preferred communication tone")
    frequency: str = Field(default="weekly", description="Preferred update frequency")
    channels: list[str] = Field(
        default_factory=list, description="Preferred communication channels (email, chat, video, etc.)"
    )
    response_time: str | None = Field(None, description="Expected response time for inquiries")
    feedback_style: str = Field(default="constructive", description="Preferred feedback style")


class UserPreferences(BaseModel):
    """Complete user preferences for personalized career guidance."""

    user_id: str | None = Field(None, description="Unique user identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="When preferences were created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When preferences were last updated")

    # Career preferences
    career_goals: CareerGoals = Field(
        default_factory=lambda: CareerGoals(param_name=None),  # type: ignore[call-arg]
        description="Career goals and targets",
        param_name=None,  # type: ignore[call-arg]
    )
    learning_preferences: LearningPreferences = Field(
        default_factory=lambda: LearningPreferences(param_name=None),  # type: ignore[call-arg]
        description="Learning and development preferences",  # type: ignore[call-arg]
    )
    communication_preferences: CommunicationPreferences = Field(
        default_factory=lambda: CommunicationPreferences(param_name=None), description="Communication preferences"
    )

    # Privacy and settings
    data_sharing: bool = Field(default=True, description="Allow data sharing for improvement")
    notifications: bool = Field(default=True, description="Enable notifications")
    public_profile: bool = Field(default=False, description="Make profile public to recruiters")

    # Additional preferences
    work_life_balance: int | None = Field(None, ge=1, le=10, description="Importance of work-life balance (1-10)")
    technical_vs_managerial: int | None = Field(
        None, ge=0, le=100, description="Preference for technical vs managerial work (0=technical, 100=managerial)"
    )
    risk_tolerance: int | None = Field(None, ge=1, le=10, description="Risk tolerance for career changes (1-10)")

    # Custom preferences
    custom_preferences: dict[str, Any] = Field(default_factory=dict, description="Additional custom preferences")

    def update_timestamp(self):
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}
        json_schema_extra = {
            "example": {
                "career_goals": {
                    "target_roles": ["Senior Software Engineer", "Engineering Manager"],
                    "target_industries": ["Technology", "FinTech"],
                    "career_level_target": "senior",
                    "salary_range": {"min": 120000, "max": 180000},
                    "locations": ["San Francisco", "New York", "Remote"],
                    "work_environment": "hybrid",
                    "priorities": ["growth", "work-life balance", "impact"],
                    "deal_breakers": ["long commute", "limited vacation"],
                },
                "learning_preferences": {
                    "learning_style": "visual",
                    "preferred_formats": ["online courses", "projects", "mentorship"],
                    "time_commitment": 10,
                    "topics_of_interest": ["machine learning", "leadership", "cloud architecture"],
                    "certification_goals": ["AWS Solutions Architect", "Google Cloud Professional"],
                },
                "communication_preferences": {
                    "language": "English",
                    "tone": "professional",
                    "frequency": "weekly",
                    "channels": ["email", "slack"],
                },
                "work_life_balance": 8,
                "technical_vs_managerial": 30,
                "risk_tolerance": 6,
            }
        }
