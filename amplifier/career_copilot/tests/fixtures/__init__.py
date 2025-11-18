"""
Test fixtures for AI Career Copilot tests.

This package contains sample data, mock objects, and test utilities
for testing all components of the career copilot service.
"""

from .sample_data import SAMPLE_API_RESPONSES
from .sample_data import SAMPLE_COACHING_RESPONSES
from .sample_data import SAMPLE_JOB_DESCRIPTIONS
from .sample_data import SAMPLE_JOB_MATCHES
from .sample_data import SAMPLE_RESUME_JSON
from .sample_data import SAMPLE_RESUME_TXT
from .sample_data import SAMPLE_SKILL_ANALYSIS
from .sample_data import SAMPLE_USER_PREFERENCES
from .sample_data import get_sample_api_response
from .sample_data import get_sample_coaching_response
from .sample_data import get_sample_job_description
from .sample_data import get_sample_resume_text

__all__ = [
    "SAMPLE_RESUME_TXT",
    "SAMPLE_RESUME_JSON",
    "SAMPLE_JOB_DESCRIPTIONS",
    "SAMPLE_USER_PREFERENCES",
    "SAMPLE_SKILL_ANALYSIS",
    "SAMPLE_COACHING_RESPONSES",
    "SAMPLE_JOB_MATCHES",
    "SAMPLE_API_RESPONSES",
    "get_sample_resume_text",
    "get_sample_job_description",
    "get_sample_coaching_response",
    "get_sample_api_response",
]
