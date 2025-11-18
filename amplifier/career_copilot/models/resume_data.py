"""
Resume Data Models

Comprehensive data models for representing resume information including work experience,
education, skills, and other professional details.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class SkillLevel(str, Enum):
    """Skill proficiency levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Skill(BaseModel):
    """Individual skill with proficiency level and context."""

    name: str = Field(..., description="Name of the skill")
    level: SkillLevel = Field(..., description="Proficiency level")
    years_experience: float | None = Field(None, ge=0, description="Years of experience with this skill")
    last_used: datetime | None = Field(None, description="When this skill was last used")
    context: str | None = Field(None, description="Context or projects where skill was used")
    certifications: list[str] = Field(default_factory=list, description="Related certifications")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class WorkExperience(BaseModel):
    """Work experience entry with detailed role information."""

    company: str = Field(..., description="Company name")
    position: str = Field(..., description="Job title/position")
    location: str | None = Field(None, description="Job location")
    start_date: datetime = Field(..., description="Start date of employment")
    end_date: datetime | None = Field(None, description="End date (None for current position)")
    is_current: bool = Field(default=False, description="Whether this is current employment")
    description: str | None = Field(None, description="Role description and responsibilities")
    achievements: list[str] = Field(default_factory=list, description="Key achievements and accomplishments")
    skills_used: list[Skill] = Field(default_factory=list, description="Skills utilized in this role")
    team_size: int | None = Field(None, ge=0, description="Size of team managed or worked in")
    projects: list[str] = Field(default_factory=list, description="Notable projects worked on")

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v, info):
        """Ensure end date is after start date."""
        if v and hasattr(info, "data") and "start_date" in info.data:
            start_date = info.data["start_date"]
            if v <= start_date:
                raise ValueError("End date must be after start date")
        return v

    @field_validator("is_current")
    @classmethod
    def validate_current_status(cls, v, info):
        """Ensure current positions have no end date."""
        if v and hasattr(info, "data") and "end_date" in info.data and info.data["end_date"]:
            raise ValueError("Current positions cannot have an end date")
        return v

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class Education(BaseModel):
    """Education entry with degree and institution details."""

    institution: str = Field(..., description="Educational institution name")
    degree: str = Field(..., description="Degree or qualification obtained")
    field_of_study: str = Field(..., description="Major or field of study")
    location: str | None = Field(None, description="Campus location")
    start_date: datetime | None = Field(None, description="Start date of program")
    end_date: datetime | None = Field(None, description="Graduation date")
    gpa: float | None = Field(None, ge=0, le=4.0, description="Grade point average")
    honors: list[str] = Field(default_factory=list, description="Academic honors and awards")
    relevant_coursework: list[str] = Field(default_factory=list, description="Relevant coursework")
    thesis: str | None = Field(None, description="Thesis or dissertation title")
    activities: list[str] = Field(default_factory=list, description="Extracurricular activities")

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v, info):
        """Ensure end date is after start date if both provided."""
        if v and hasattr(info, "data") and "start_date" in info.data and info.data["start_date"]:
            start_date = info.data["start_date"]
            if v <= start_date:
                raise ValueError("End date must be after start date")
        return v

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class ResumeData(BaseModel):
    """Complete resume data structure containing all professional information."""

    personal_info: dict[str, Any] = Field(
        default_factory=dict, description="Personal information (name, contact details, etc.)"
    )
    summary: str | None = Field(None, description="Professional summary or objective")
    work_experience: list[WorkExperience] = Field(default_factory=list, description="Work history")
    education: list[Education] = Field(default_factory=list, description="Educational background")
    skills: list[Skill] = Field(default_factory=list, description="Technical and soft skills")
    certifications: list[dict[str, Any]] = Field(default_factory=list, description="Professional certifications")
    languages: list[dict[str, Any]] = Field(default_factory=list, description="Languages spoken")
    projects: list[dict[str, Any]] = Field(default_factory=list, description="Personal or professional projects")
    publications: list[dict[str, Any]] = Field(
        default_factory=list, description="Academic or professional publications"
    )
    volunteer_work: list[dict[str, Any]] = Field(default_factory=list, description="Volunteer experience")
    interests: list[str] = Field(default_factory=list, description="Personal interests and hobbies")
    references_available: bool = Field(default=True, description="Whether references are available upon request")
    last_updated: datetime = Field(default_factory=datetime.now, description="When resume was last updated")

    def get_total_experience_years(self) -> float:
        """Calculate total years of work experience."""
        if not self.work_experience:
            return 0.0

        total_days = 0
        for exp in self.work_experience:
            end_date = exp.end_date or datetime.now()
            days = (end_date - exp.start_date).days
            total_days += days

        return total_days / 365.25

    def get_current_position(self) -> WorkExperience | None:
        """Get the most recent or current position."""
        if not self.work_experience:
            return None

        # Return current position if exists
        for exp in self.work_experience:
            if exp.is_current:
                return exp

        # Otherwise return most recent position
        return max(self.work_experience, key=lambda x: x.end_date or datetime.now())

    def get_all_skills(self) -> list[Skill]:
        """Get all skills including those from work experience."""
        all_skills = list(self.skills)

        for exp in self.work_experience:
            all_skills.extend(exp.skills_used)

        # Remove duplicates and sort by level
        unique_skills = {}
        for skill in all_skills:
            if skill.name not in unique_skills or skill.level.value > unique_skills[skill.name].level.value:
                unique_skills[skill.name] = skill

        return sorted(unique_skills.values(), key=lambda x: x.level.value, reverse=True)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}
        json_schema_extra = {
            "example": {
                "personal_info": {"name": "John Doe", "email": "john.doe@example.com", "phone": "+1-555-0123"},
                "summary": "Experienced software developer with 5+ years in full-stack development",
                "work_experience": [
                    {
                        "company": "Tech Company",
                        "position": "Senior Software Engineer",
                        "start_date": "2022-01-01T00:00:00",
                        "is_current": True,
                        "description": "Leading development of cloud-based applications",
                        "skills_used": [{"name": "Python", "level": "advanced", "years_experience": 4.0}],
                    }
                ],
                "skills": [{"name": "Python", "level": "advanced", "years_experience": 5.0}],
            }
        }
