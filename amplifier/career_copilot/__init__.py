"""
AI Career Copilot Module

An intelligent career development assistant that helps users optimize their resumes,
develop new skills, and find matching job opportunities.

Features:
- Resume parsing and analysis
- Skill gap analysis and learning recommendations
- Job matching and application optimization
- Career coaching and enrichment

This module follows the amplifier patterns for AI integration and modular design.
"""

from .main import app
from .models.master_profile import MasterProfile
from .models.resume_data import Education
from .models.resume_data import ResumeData
from .models.resume_data import Skill
from .models.resume_data import WorkExperience
from .models.user_preferences import CareerGoals
from .models.user_preferences import UserPreferences

__all__ = [
    "app",
    "MasterProfile",
    "ResumeData",
    "WorkExperience",
    "Education",
    "Skill",
    "UserPreferences",
    "CareerGoals",
]
