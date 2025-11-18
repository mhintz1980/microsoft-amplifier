"""
Data Models for AI Career Copilot

This module contains Pydantic models for representing career-related data structures.
All models include comprehensive validation and serialization for API integration.
"""

from .master_profile import MasterProfile
from .resume_data import Education
from .resume_data import ResumeData
from .resume_data import Skill
from .resume_data import WorkExperience
from .user_preferences import CareerGoals
from .user_preferences import UserPreferences

__all__ = [
    "MasterProfile",
    "ResumeData",
    "WorkExperience",
    "Education",
    "Skill",
    "UserPreferences",
    "CareerGoals",
]
