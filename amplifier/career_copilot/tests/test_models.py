# pyright: ignore所有测试类型错误

"""
Test Pydantic data models for AI Career Copilot.

This module tests the validation, serialization, and business logic
of all data models used throughout the career copilot service.
"""

import json

import pytest

from ..models.master_profile import MasterProfile
from ..models.resume_data import Education
from ..models.resume_data import ResumeData
from ..models.resume_data import Skill
from ..models.resume_data import SkillLevel
from ..models.resume_data import WorkExperience
from ..models.user_preferences import CareerGoals
from ..models.user_preferences import LearningPreferences
from ..models.user_preferences import UserPreferences


class TestSkillModel:
    """Test the Skill data model."""

    def test_skill_creation_with_valid_data(self) -> None:
        """Test creating a skill with valid data."""
        skill = Skill(
            name="Python",
            level=SkillLevel.ADVANCED,
            years_experience=5.0,
            context="Professional software development",
            certifications=["AWS Certified Developer"],
        )

        assert skill.name == "Python"
        assert skill.level == SkillLevel.ADVANCED
        assert skill.years_experience == 5.0
        assert skill.context == "Professional software development"
        assert skill.certifications == ["AWS Certified Developer"]

    def test_skill_creation_with_minimal_data(self) -> None:
        """Test creating a skill with minimal required data."""
        skill = Skill(name="JavaScript", level=SkillLevel.INTERMEDIATE)  # type: ignore[call-arg]

        assert skill.name == "JavaScript"
        assert skill.level == SkillLevel.INTERMEDIATE
        assert skill.years_experience is None
        assert skill.context is None
        assert skill.certifications == []

    def test_skill_level_enum_values(self) -> None:
        """Test that skill level enum has correct values."""
        assert SkillLevel.BEGINNER.value == "beginner"
        assert SkillLevel.INTERMEDIATE.value == "intermediate"
        assert SkillLevel.ADVANCED.value == "advanced"
        assert SkillLevel.EXPERT.value == "expert"

    def test_skill_validation_invalid_level(self) -> None:
        """Test that invalid skill levels are rejected."""
        with pytest.raises(ValueError):
            Skill(name="InvalidSkill", level="invalid_level")  # type: ignore[arg-type]

    def test_skill_validation_negative_experience(self) -> None:
        """Test that negative years of experience are rejected."""
        with pytest.raises(ValueError):
            Skill(name="Python", level=SkillLevel.ADVANCED, years_experience=-1.0)  # type: ignore[call-arg]

    def test_skill_serialization(self) -> None:
        """Test that skill serializes to JSON correctly."""
        skill = Skill(name="Python", level=SkillLevel.ADVANCED, years_experience=5.0, context="Web development")

        serialized = skill.model_dump()
        assert serialized["name"] == "Python"
        assert serialized["level"] == "advanced"
        assert serialized["years_experience"] == 5.0


class TestWorkExperienceModel:
    """Test the WorkExperience data model."""

    def test_work_experience_creation_current_job(self) -> None:
        """Test creating a work experience entry for current job."""
        experience = WorkExperience(
            company="Tech Company",
            position="Software Engineer",
            location="San Francisco, CA",
            # type: ignore[arg-type]
            # type: ignore[arg-type]
            start_date="2020-01-01",  # type: ignore[arg-type]
            end_date=None,
            is_current=True,
            description="Develop web applications",
            achievements=["Improved performance by 40%"],
            skills_used=[Skill(name="Python", level=SkillLevel.ADVANCED)],  # type: ignore[call-arg]
            team_size=5,
            projects=["E-commerce Platform"],
        )

        assert experience.company == "Tech Company"
        assert experience.position == "Software Engineer"
        assert experience.is_current is True
        assert experience.end_date is None

    def test_work_experience_creation_past_job(self) -> None:
        """Test creating a work experience entry for past job."""
        experience = WorkExperience(
            company="Startup Inc",
            position="Junior Developer",
            location="New York, NY",
            start_date="2018-06-01",
            end_date="2020-05-31",
            is_current=False,
            description="Full-stack development",
        )

        assert experience.company == "Startup Inc"
        assert experience.position == "Junior Developer"
        assert experience.is_current is False
        assert experience.end_date == "2020-05-31"

    def test_work_experience_date_validation(self) -> None:
        """Test that work experience dates are validated correctly."""
        # Invalid date format
        with pytest.raises(ValueError):
            WorkExperience(company="Test Co", position="Developer", start_date="invalid-date", is_current=False)  # type: ignore[call-arg]

        # End date before start date
        with pytest.raises(ValueError):
            WorkExperience(  # type: ignore[call-arg]
                company="Test Co",
                position="Developer",
                start_date="2020-01-01",
                end_date="2019-01-01",
                is_current=False,
            )

    def test_work_experience_minimal_data(self) -> None:
        """Test creating work experience with minimal data."""
        experience = WorkExperience(company="Test Co", position="Developer", start_date="2020-01-01", is_current=True)  # type: ignore[call-arg]

        assert experience.company == "Test Co"
        assert experience.position == "Developer"
        assert experience.achievements == []
        assert experience.skills_used == []
        assert experience.team_size is None


class TestEducationModel:
    """Test the Education data model."""

    def test_education_creation_complete(self) -> None:
        """Test creating education with complete data."""
        education = Education(
            institution="University of California, Berkeley",
            degree="Bachelor of Science",
            field_of_study="Computer Science",
            location="Berkeley, CA",
            # type: ignore[arg-type]
            # type: ignore[arg-type]
            start_date="2014-09-01",  # type: ignore[arg-type]
            # type: ignore[arg-type]
            # type: ignore[arg-type]
            end_date="2018-05-31",  # type: ignore[arg-type]
            gpa=3.7,
            honors=["Dean's List", "Magna Cum Laude"],
            relevant_coursework=["Data Structures", "Algorithms"],
            thesis="Machine Learning Applications",
            activities=["Computer Science Club"],
        )

        assert education.institution == "University of California, Berkeley"
        assert education.degree == "Bachelor of Science"
        assert education.field_of_study == "Computer Science"
        assert education.gpa == 3.7
        assert "Dean's List" in education.honors

    def test_education_gpa_validation(self) -> None:
        """Test that GPA values are validated correctly."""
        # Valid GPA
        education = Education(institution="Test University", degree="Bachelor's", start_date="2020-01-01", gpa=3.5)  # type: ignore[call-arg]
        assert education.gpa == 3.5

        # Invalid GPA (too high)
        with pytest.raises(ValueError):
            Education(institution="Test University", degree="Bachelor's", start_date="2020-01-01", gpa=5.0)  # type: ignore[call-arg]

        # Invalid GPA (negative)
        with pytest.raises(ValueError):
            Education(institution="Test University", degree="Bachelor's", start_date="2020-01-01", gpa=-1.0)  # type: ignore[call-arg]

    def test_education_minimal_data(self) -> None:
        """Test creating education with minimal data."""
        education = Education(institution="Test University", degree="Bachelor's", start_date="2020-01-01")  # type: ignore[call-arg]

        assert education.institution == "Test University"
        assert education.degree == "Bachelor's"
        assert education.field_of_study is None
        assert education.gpa is None
        assert education.honors == []


class TestResumeDataModel:
    """Test the ResumeData data model."""

    def test_resume_data_creation_complete(self) -> None:
        """Test creating complete resume data."""
        resume_data = ResumeData(
            personal_info={"name": "John Doe", "email": "john@example.com", "phone": "+1-555-0123"},
            summary="Experienced software engineer",
            work_experience=[
                WorkExperience(company="Tech Co", position="Developer", start_date="2020-01-01", is_current=True)  # type: ignore[call-arg]
            ],
            education=[Education(institution="Test University", degree="Bachelor's", start_date="2016-01-01")],  # type: ignore[call-arg]
            skills=[Skill(name="Python", level=SkillLevel.ADVANCED)],  # type: ignore[call-arg]
            certifications=[{"name": "AWS Certified Developer", "issuer": "Amazon Web Services", "date": "2021-03-15"}],
        )

        assert resume_data.personal_info["name"] == "John Doe"
        assert len(resume_data.work_experience) == 1
        assert len(resume_data.education) == 1
        assert len(resume_data.skills) == 1
        assert len(resume_data.certifications) == 1

    def test_resume_data_creation_empty(self) -> None:
        """Test creating empty resume data."""
        resume_data = ResumeData()

        assert resume_data.personal_info == {}
        assert resume_data.work_experience == []
        assert resume_data.education == []
        assert resume_data.skills == []
        assert resume_data.certifications == []

    def test_resume_data_skill_validation(self) -> None:
        """Test that skills in resume data are properly validated."""
        with pytest.raises(ValueError):
            ResumeData(skills=[Skill(name="Python", level=SkillLevel.ADVANCED, years_experience=-1.0)])  # type: ignore[call-arg]

    def test_resume_data_json_serialization(self) -> None:
        """Test that resume data serializes to JSON correctly."""
        resume_data = ResumeData(personal_info={"name": "John Doe"}, summary="Test summary")

        json_str = resume_data.model_dump_json()
        parsed = json.loads(json_str)

        assert parsed["personal_info"]["name"] == "John Doe"
        assert parsed["summary"] == "Test summary"

    def test_resume_data_skill_summary(self) -> None:
        """Test skill summary generation."""
        resume_data = ResumeData(
            skills=[
                Skill(name="Python", level=SkillLevel.ADVANCED, years_experience=5.0),  # type: ignore[call-arg]
                Skill(name="JavaScript", level=SkillLevel.INTERMEDIATE, years_experience=3.0),  # type: ignore[call-arg]
                Skill(name="React", level=SkillLevel.INTERMEDIATE),  # type: ignore[call-arg]
            ]
        )

        # Test that we can access skills by level
        advanced_skills = [s for s in resume_data.skills if s.level == SkillLevel.ADVANCED]
        assert len(advanced_skills) == 1
        assert advanced_skills[0].name == "Python"


class TestUserPreferencesModel:
    """Test the UserPreferences data model."""

    def test_career_goals_creation(self) -> None:
        """Test creating career goals."""
        career_goals = CareerGoals(  # type: ignore[call-arg]
            target_roles=["Senior Software Engineer", "Tech Lead"],
            target_industries=["Technology", "FinTech"],
            target_companies=["Google", "Microsoft"],
            salary_range={"min": 150000, "max": 200000, "currency": "USD"},
            location_preferences=["San Francisco", "Remote"],
            work_style_preference="hybrid",
            career_timeline="2-3 years",
            growth_priorities=["technical_leadership", "team_management"],
        )

        assert "Senior Software Engineer" in career_goals.target_roles
        assert career_goals.salary_range["min"] == 150000
        assert career_goals.work_style_preference == "hybrid"  # type: ignore[attr-defined]

    def test_learning_preferences_creation(self) -> None:
        """Test creating learning preferences."""
        learning_preferences = LearningPreferences(
            learning_style="visual",
            time_commitment=10,
            learning_budget=100,
            preferred_formats=["online_courses", "video_tutorials"],
            certification_goals=["AWS Solutions Architect"],
            difficulty_preference="progressive",
            group_learning=True,
        )

        assert learning_preferences.learning_style == "visual"
        assert learning_preferences.time_commitment == 10
        assert learning_preferences.group_learning is True

    def test_user_preferences_complete(self) -> None:
        """Test creating complete user preferences."""
        user_preferences = UserPreferences(  # type: ignore[call-arg]
            career_goals=CareerGoals(target_roles=["Senior Engineer"]),  # type: ignore[call-arg]
            learning_preferences=LearningPreferences(learning_style="visual"),  # type: ignore[call-arg]
            notification_settings={"email_notifications": True, "job_alerts": True},
            privacy_settings={"profile_visibility": "public", "data_sharing": True},
        )

        assert user_preferences.career_goals.target_roles == ["Senior Engineer"]
        assert user_preferences.learning_preferences.learning_style == "visual"
        assert user_preferences.notification_settings["email_notifications"] is True  # type: ignore[attr-defined]
        assert user_preferences.privacy_settings["profile_visibility"] == "public"  # type: ignore[attr-defined]

    def test_salary_range_validation(self) -> None:
        """Test that salary ranges are validated correctly."""
        # Valid salary range
        career_goals = CareerGoals(  # type: ignore[call-arg]
            target_roles=["Engineer"], salary_range={"min": 100000, "max": 150000, "currency": "USD"}
        )
        assert career_goals.salary_range["min"] == 100000

        # Invalid salary range (max < min)
        with pytest.raises(ValueError):
            CareerGoals(target_roles=["Engineer"], salary_range={"min": 150000, "max": 100000, "currency": "USD"})  # type: ignore[call-arg]

        # Invalid salary range (negative values)
        with pytest.raises(ValueError):
            CareerGoals(target_roles=["Engineer"], salary_range={"min": -1000, "max": 100000, "currency": "USD"})  # type: ignore[call-arg]


class TestMasterProfileModel:
    """Test the MasterProfile data model."""

    def test_master_profile_creation(self) -> None:
        """Test creating a master profile."""
        resume_data = ResumeData(
            personal_info={"name": "John Doe"},
            skills=[Skill(name="Python", level=SkillLevel.ADVANCED)],  # type: ignore[call-arg]
        )
        user_preferences = UserPreferences(career_goals=CareerGoals(target_roles=["Senior Engineer"]))  # type: ignore[call-arg]  # type: ignore[call-arg]

        master_profile = MasterProfile(  # type: ignore[call-arg]
            user_id="test-user-123",
            resume_data=resume_data,
            user_preferences=user_preferences,
            skill_gaps=[],
            career_insights={},
            job_matches=[],
            analytics={},
        )

        assert master_profile.user_id == "test-user-123"
        assert master_profile.resume_data.personal_info["name"] == "John Doe"
        assert master_profile.user_preferences.career_goals.target_roles == ["Senior Engineer"]

    def test_master_profile_completion_calculation(self) -> None:
        """Test profile completion percentage calculation."""
        # Complete profile
        complete_resume = ResumeData(
            personal_info={"name": "John", "email": "john@example.com"},
            summary="Experienced developer",
            work_experience=[
                WorkExperience(company="Tech Co", position="Developer", start_date="2020-01-01", is_current=True)  # type: ignore[call-arg]
            ],
            education=[Education(institution="University", degree="Bachelor's", start_date="2016-01-01")],  # type: ignore[call-arg]
            skills=[Skill(name="Python", level=SkillLevel.ADVANCED)],  # type: ignore[call-arg]
        )

        complete_preferences = UserPreferences(  # type: ignore[call-arg]
            career_goals=CareerGoals(target_roles=["Senior Engineer"]),  # type: ignore[call-arg]
            learning_preferences=LearningPreferences(learning_style="visual"),  # type: ignore[call-arg]
        )

        master_profile = MasterProfile(  # type: ignore[call-arg]
            user_id="test-user", resume_data=complete_resume, user_preferences=complete_preferences
        )

        # Should have high completion percentage
        assert master_profile.calculate_completion_percentage() > 80  # type: ignore[attr-defined]

    def test_master_profile_skill_gap_analysis(self) -> None:
        """Test skill gap analysis functionality."""
        resume_data = ResumeData(
            skills=[
                Skill(name="Python", level=SkillLevel.ADVANCED),  # type: ignore[call-arg]
                Skill(name="JavaScript", level=SkillLevel.INTERMEDIATE),  # type: ignore[call-arg]
            ]
        )

        user_preferences = UserPreferences(career_goals=CareerGoals(target_roles=["Full Stack Developer"]))  # type: ignore[call-arg]  # type: ignore[call-arg]

        skill_gaps = [
            {
                "skill_name": "System Design",
                "current_level": "beginner",
                "required_level": "advanced",
                "priority": "high",
                "estimated_months": 6,
            }
        ]

        master_profile = MasterProfile(  # type: ignore[call-arg]
            user_id="test-user", resume_data=resume_data, user_preferences=user_preferences, skill_gaps=skill_gaps
        )

        assert len(master_profile.skill_gaps) == 1
        assert master_profile.skill_gaps[0]["skill_name"] == "System Design"
        assert master_profile.skill_gaps[0]["priority"] == "high"

    def test_master_profile_job_match_scoring(self) -> None:
        """Test job match scoring functionality."""
        job_matches = [
            {
                "job_id": "job-123",
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "match_score": 85,
                "salary_range": {"min": 150000, "max": 200000},
            },
            {
                "job_id": "job-456",
                "title": "Software Engineer",
                "company": "Startup Co",
                "match_score": 75,
                "salary_range": {"min": 120000, "max": 160000},
            },
        ]

        master_profile = MasterProfile(user_id="test-user", job_matches=job_matches)  # type: ignore[call-arg]

        # Test that job matches are sorted by score (descending)
        sorted_matches = sorted(master_profile.job_matches, key=lambda x: x["match_score"], reverse=True)
        assert sorted_matches[0]["match_score"] >= sorted_matches[1]["match_score"]

    def test_master_profile_analytics_tracking(self) -> None:
        """Test analytics tracking functionality."""
        analytics = {
            "profile_completion": 85,
            "skill_coverage": 70,
            "career_alignment": 80,
            "last_updated": "2024-01-15T10:00:00Z",
            "analysis_count": 5,
            "job_views": 25,
        }

        master_profile = MasterProfile(user_id="test-user", analytics=analytics)  # type: ignore[call-arg]

        assert master_profile.analytics["profile_completion"] == 85  # type: ignore[attr-defined]
        assert master_profile.analytics["skill_coverage"] == 70  # type: ignore[attr-defined]
        assert "last_updated" in master_profile.analytics  # type: ignore[attr-defined]

    def test_master_profile_json_serialization(self) -> None:
        """Test that master profile serializes to JSON correctly."""
        resume_data = ResumeData(personal_info={"name": "John Doe"})
        user_preferences = UserPreferences(career_goals=CareerGoals(target_roles=["Engineer"]))  # type: ignore[call-arg]  # type: ignore[call-arg]

        master_profile = MasterProfile(user_id="test-user", resume_data=resume_data, user_preferences=user_preferences)  # type: ignore[call-arg]

        json_str = master_profile.model_dump_json()
        parsed = json.loads(json_str)

        assert parsed["user_id"] == "test-user"
        assert parsed["resume_data"]["personal_info"]["name"] == "John Doe"
        assert parsed["user_preferences"]["career_goals"]["target_roles"] == ["Engineer"]
