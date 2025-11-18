# pyright: ignore所有测试类型错误

"""
Pytest configuration and shared fixtures for AI Career Copilot tests.

This module provides common test utilities, fixtures, and configuration
for all test modules in the career copilot test suite.
"""

import json
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from .. import app
from ..config import config
from ..models.master_profile import MasterProfile
from ..models.resume_data import Education
from ..models.resume_data import ResumeData
from ..models.resume_data import Skill
from ..models.resume_data import WorkExperience
from ..models.user_preferences import CareerGoals
from ..models.user_preferences import LearningPreferences
from ..models.user_preferences import UserPreferences


@pytest.fixture(scope="session")
def test_config():
    """Override configuration for testing."""
    original_env = config.environment
    config.environment = "testing"
    config.database_url = "sqlite:///./test_career_copilot.db"
    config.upload_temp_dir = tempfile.gettempdir()
    config.enable_redis_cache = False
    config.require_authentication = False
    config.rate_limit_enabled = False

    yield config

    # Restore original configuration
    config.environment = original_env


@pytest.fixture
def client(test_config: Any) -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_claude_client() -> AsyncMock:
    """Create a mock Claude API client."""
    mock_client = AsyncMock()

    # Configure default responses
    mock_client.messages.create.return_value = {
        "content": [
            {
                "type": "text",
                "text": json.dumps(
                    {
                        "personal_info": {"name": "John Doe", "email": "john@example.com", "phone": "+1-555-0123"},
                        "work_experience": [
                            {
                                "company": "Tech Company",
                                "position": "Software Engineer",
                                "start_date": "2020-01-01",
                                "is_current": True,
                                "description": "Developed software applications",
                            }
                        ],
                        "skills": [{"name": "Python", "level": "advanced", "years_experience": 3.0}],
                    }
                ),
            }
        ]
    }

    return mock_client


@pytest.fixture
def sample_resume_data() -> ResumeData:
    """Create sample resume data for testing."""
    return ResumeData(
        personal_info={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-0123",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/johndoe",
            "github": "github.com/johndoe",
        },
        summary="Experienced software engineer with expertise in Python and web development.",
        work_experience=[
            WorkExperience(
                company="Tech Company",
                position="Senior Software Engineer",
                location="San Francisco, CA",
                # type: ignore[arg-type]
                # type: ignore[arg-type]
                start_date="2020-01-01",  # type: ignore[arg-type]
                end_date=None,
                is_current=True,
                description="Lead development of web applications using Python and React.",
                achievements=["Improved application performance by 40%", "Mentored junior developers"],
                skills_used=[
                    Skill(name="Python", level="advanced", years_experience=5.0),  # type: ignore[call-arg]
                    Skill(name="React", level="intermediate", years_experience=3.0),  # type: ignore[call-arg]
                ],
                team_size=5,
                projects=["E-commerce Platform", "API Gateway"],
            ),
            WorkExperience(
                company="Startup Inc",
                position="Software Engineer",
                location="New York, NY",
                # type: ignore[arg-type]
                # type: ignore[arg-type]
                start_date="2018-06-01",  # type: ignore[arg-type]
                # type: ignore[arg-type]
                # type: ignore[arg-type]
                end_date="2019-12-31",  # type: ignore[arg-type]
                is_current=False,
                description="Full-stack development for SaaS platform.",
                achievements=["Built RESTful APIs", "Implemented CI/CD pipeline"],
                skills_used=[
                    Skill(name="JavaScript", level="advanced", years_experience=4.0),  # type: ignore[call-arg]
                    Skill(name="Node.js", level="intermediate", years_experience=2.0),  # type: ignore[call-arg]
                ],
                team_size=3,
                projects=["Analytics Dashboard"],
            ),
        ],
        education=[
            Education(
                institution="University of California, Berkeley",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                location="Berkeley, CA",
                start_date="2014-09-01",
                end_date="2018-05-31",
                gpa=3.7,
                honors=["Dean's List", "Magna Cum Laude"],
                relevant_coursework=["Data Structures", "Algorithms", "Machine Learning"],
                activities=["Computer Science Club", "Hackathon Organizer"],
            )
        ],
        skills=[
            Skill(name="Python", level="advanced", years_experience=5.0, context="Professional software development"),
            Skill(
                name="JavaScript", level="advanced", years_experience=4.0, context="Frontend and backend development"
            ),
            Skill(name="React", level="intermediate", years_experience=3.0, context="Frontend framework"),
            Skill(name="Node.js", level="intermediate", years_experience=2.0, context="Backend development"),
            Skill(name="SQL", level="intermediate", years_experience=3.0, context="Database queries"),
            Skill(name="Git", level="advanced", years_experience=5.0, context="Version control"),
        ],
        certifications=[
            {
                "name": "AWS Certified Developer",
                "issuer": "Amazon Web Services",
                "date": "2021-03-15",
                "credential_id": "AWS-DEV-123456",
            }
        ],
        languages=[
            {"language": "English", "proficiency": "native"},
            {"language": "Spanish", "proficiency": "conversational"},
        ],
        projects=[
            {
                "name": "Personal Blog Platform",
                "description": "Full-stack blog platform with user authentication and content management",
                "technologies": ["React", "Node.js", "MongoDB"],
                "url": "https://github.com/johndoe/blog-platform",
                "highlights": ["Implemented real-time comments", "Added rich text editor"],
            }
        ],
        interests=["Open Source", "Machine Learning", "Hiking", "Photography"],
        references_available=True,
    )


@pytest.fixture
def sample_user_preferences() -> UserPreferences:
    """Create sample user preferences for testing."""
    return UserPreferences(  # type: ignore[call-arg]
        career_goals=CareerGoals(  # type: ignore[call-arg]
            target_roles=["Senior Software Engineer", "Tech Lead"],
            target_industries=["Technology", "FinTech"],
            target_companies=["Google", "Stripe", "Airbnb"],
            salary_range={"min": 150000, "max": 200000, "currency": "USD"},
            location_preferences=["San Francisco", "Remote"],
            work_style_preference="hybrid",
            career_timeline="2-3 years",
            growth_priorities=["technical_leadership", "team_management"],
        ),
        learning_preferences=LearningPreferences(
            learning_style="visual",
            time_commitment=10,
            learning_budget=100,
            preferred_formats=["online_courses", "video_tutorials", "books"],
            certification_goals=["AWS Certified Solutions Architect", "Google Cloud Professional"],
            difficulty_preference="progressive",
            group_learning=True,
        ),
        notification_settings={
            "email_notifications": True,
            "job_alerts": True,
            "skill_updates": True,
            "career_insights": False,
            "frequency": "weekly",
        },
        privacy_settings={"profile_visibility": "public", "data_sharing": True, "analytics_consent": True},
    )


@pytest.fixture
def sample_master_profile(sample_resume_data: ResumeData, sample_user_preferences: UserPreferences) -> MasterProfile:
    """Create a sample master profile for testing."""
    return MasterProfile(  # type: ignore[call-arg]
        user_id="test-user-123",
        resume_data=sample_resume_data,
        user_preferences=sample_user_preferences,
        skill_gaps=[
            {
                "skill_name": "System Design",
                "current_level": "beginner",
                "required_level": "advanced",
                "priority": "high",
                "learning_resources": [
                    {
                        "type": "course",
                        "title": "System Design Fundamentals",
                        "provider": "Coursera",
                        "url": "https://coursera.com/system-design",
                    }
                ],
            }
        ],
        career_insights={
            "readiness_score": 75,
            "strengths": ["Strong technical skills", "Good experience"],
            "improvement_areas": ["Leadership experience", "System design"],
            "market_demand": "high",
            "salary_potential": {"min": 140000, "max": 180000},
        },
        job_matches=[
            {
                "job_id": "job-123",
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "match_score": 85,
                "salary_range": {"min": 150000, "max": 200000},
                "requirements_match": 90,
                "culture_fit": 80,
            }
        ],
        analytics={
            "profile_completion": 90,
            "skill_coverage": 75,
            "career_alignment": 80,
            "last_updated": "2024-01-15T10:00:00Z",
        },
    )


@pytest.fixture
def sample_resume_text() -> str:
    """Sample resume text for testing parsing functionality."""
    return """
    John Doe
    San Francisco, CA | +1-555-0123 | john@example.com | linkedin.com/in/johndoe

    SUMMARY
    Experienced software engineer with 5+ years of expertise in Python, JavaScript, and full-stack development.
    Proven track record of delivering high-quality web applications and leading development teams.

    EXPERIENCE
    Senior Software Engineer | Tech Company | San Francisco, CA
    Jan 2020 - Present
    - Lead development of web applications using Python and React
    - Improved application performance by 40% through optimization
    - Mentored team of 3 junior developers
    - Implemented CI/CD pipeline reducing deployment time by 60%

    Software Engineer | Startup Inc | New York, NY
    Jun 2018 - Dec 2019
    - Developed RESTful APIs using Node.js and Express
    - Built responsive frontend applications with React
    - Collaborated with cross-functional team of 5 developers

    EDUCATION
    Bachelor of Science in Computer Science
    University of California, Berkeley | Berkeley, CA
    Sep 2014 - May 2018
    - GPA: 3.7/4.0, Magna Cum Laude
    - Dean's List: Fall 2016, Fall 2017

    SKILLS
    Programming Languages: Python (Expert), JavaScript (Expert), Java (Intermediate)
    Frameworks: React, Django, Express.js, Flask
    Databases: PostgreSQL, MongoDB, Redis
    Tools: Git, Docker, AWS, Jenkins
    Other: RESTful APIs, Microservices, CI/CD

    CERTIFICATIONS
    - AWS Certified Developer - Associate (2021)
    - Certified ScrumMaster (2020)

    PROJECTS
    Personal Blog Platform
    - Full-stack blog application with user authentication and content management
    - Technologies: React, Node.js, MongoDB, AWS
    - GitHub: github.com/johndoe/blog-platform
    """


@pytest.fixture
def temp_pdf_file() -> Generator[Path, None, None]:
    """Create a temporary PDF file for testing file uploads."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        # Write some dummy content that resembles a PDF header
        temp_file.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n")
        temp_file_path = Path(temp_file.name)

    yield temp_file_path

    # Cleanup
    if temp_file_path.exists():
        temp_file_path.unlink()


@pytest.fixture
def temp_docx_file() -> Generator[Path, None, None]:
    """Create a temporary DOCX file for testing file uploads."""
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
        # Write some dummy content that resembles a DOCX header
        temp_file.write(b"PK\x03\x04\x14\x00\x06\x00")  # ZIP signature for DOCX
        temp_file_path = Path(temp_file.name)

    yield temp_file_path

    # Cleanup
    if temp_file_path.exists():
        temp_file_path.unlink()


@pytest.fixture
def mock_redis() -> MagicMock:
    """Create a mock Redis client."""
    redis_mock = MagicMock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = 1
    return redis_mock


@pytest.fixture
def mock_background_tasks() -> AsyncMock:
    """Create a mock background tasks manager."""
    background_tasks = AsyncMock()
    background_tasks.add_task.return_value = None
    return background_tasks


@pytest.fixture
def sample_api_responses() -> dict[str, Any]:
    """Sample API responses for testing."""
    return {
        "skill_analysis": {
            "skill_gaps": [
                {
                    "skill_name": "System Design",
                    "current_level": "beginner",
                    "target_level": "advanced",
                    "priority": "high",
                    "estimated_months": 6,
                }
            ],
            "skill_development_plan": [
                {
                    "skill_name": "System Design",
                    "learning_resources": [
                        {
                            "type": "course",
                            "title": "System Design Fundamentals",
                            "provider": "Coursera",
                            "cost": "paid",
                        }
                    ],
                }
            ],
            "market_readiness_score": 75,
        },
        "job_matches": [
            {
                "job_id": "job-123",
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "match_score": 85,
                "salary_range": {"min": 150000, "max": 200000},
            }
        ],
        "career_coach_response": {
            "message": "Based on your profile, I recommend focusing on system design skills to advance to senior roles.",
            "action_items": [
                "Take a system design course",
                "Practice with real-world scenarios",
                "Join design discussions at work",
            ],
            "next_steps": "Would you like me to suggest specific learning resources for system design?",
        },
    }


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Automatically clean up temporary files after each test."""
    yield

    # Clean up any temporary files created during tests
    temp_dir = Path(tempfile.gettempdir())
    for pattern in ["career_copilot_test_*", "test_resume_*"]:
        for file_path in temp_dir.glob(pattern):
            try:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    file_path.rmdir()
            except (PermissionError, FileNotFoundError):
                pass  # Ignore cleanup errors, thesis=""), last_used=None), last_used=None), last_used=None), last_used=None), last_used=None), last_used=None), budget=None)
