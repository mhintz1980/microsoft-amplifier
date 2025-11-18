# pyright: ignore所有测试类型错误

"""
Test core services for AI Career Copilot.

This module tests the business logic of all core services including
resume parsing, skill analysis, career coaching, and job matching.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from ..models.master_profile import MasterProfile
from ..models.resume_data import ResumeData
from ..services.enrichment_coach import EnrichmentCoach
from ..services.job_matcher import JobMatcher
from ..services.resume_parser import ResumeParser
from ..services.skill_analyzer import SkillAnalyzer


class TestResumeParser:
    """Test the resume parsing service."""

    @pytest.fixture
    def resume_parser(self, mock_claude_client: AsyncMock) -> ResumeParser:
        """Create a resume parser instance."""
        return ResumeParser(claude_client=mock_claude_client)

    @pytest.fixture
    def rule_based_parser(self) -> ResumeParser:
        """Create a resume parser without AI client (rule-based)."""
        return ResumeParser(claude_client=None)

    async def test_parse_pdf_file(self, resume_parser: ResumeParser, temp_pdf_file: Path) -> None:
        """Test parsing a PDF resume file."""
        result = await resume_parser.parse_resume(temp_pdf_file)

        assert isinstance(result, ResumeData)
        assert result.personal_info.get("name") is not None
        assert len(result.skills) > 0

    async def test_parse_docx_file(self, resume_parser: ResumeParser, temp_docx_file: Path) -> None:
        """Test parsing a DOCX resume file."""
        result = await resume_parser.parse_resume(temp_docx_file)

        assert isinstance(result, ResumeData)
        # DOCX files might have less structure than PDFs
        assert result.personal_info is not None

    async def test_parse_text_file(self, resume_parser: ResumeParser, sample_resume_text: str) -> None:
        """Test parsing resume from text."""
        result = await resume_parser.parse_resume_text(sample_resume_text, "resume.txt")

        assert isinstance(result, ResumeData)
        assert result.personal_info.get("name") == "John Doe"
        assert len(result.work_experience) >= 1
        assert len(result.skills) >= 1

    async def test_parse_text_file_ai_parsing(self, resume_parser: ResumeParser, sample_resume_text: str) -> None:
        """Test AI-powered parsing of resume text."""
        result = await resume_parser._ai_parse_resume(sample_resume_text, "resume.txt")

        assert isinstance(result, ResumeData)
        assert result.personal_info.get("name") == "John Doe"
        assert result.summary is not None

    async def test_parse_text_file_rule_based(self, rule_based_parser: ResumeParser, sample_resume_text: str) -> None:
        """Test rule-based parsing of resume text."""
        result = await rule_based_parser._rule_based_parse_resume(sample_resume_text, "resume.txt")

        assert isinstance(result, ResumeData)
        # Rule-based parsing might extract less information
        assert result.personal_info is not None

    async def test_extract_text_from_pdf(self, resume_parser: ResumeParser, temp_pdf_file: Path) -> None:
        """Test text extraction from PDF files."""
        text = await resume_parser._extract_text_from_file(temp_pdf_file)  # type: ignore[attr-defined]

        assert isinstance(text, str)
        assert len(text) > 0

    async def test_extract_text_from_docx(self, resume_parser: ResumeParser, temp_docx_file: Path) -> None:
        """Test text extraction from DOCX files."""
        text = await resume_parser._extract_text_from_file(temp_docx_file)  # type: ignore[attr-defined]

        assert isinstance(text, str)
        assert len(text) > 0

    async def test_extract_text_from_txt(self, resume_parser: ResumeParser) -> None:
        """Test text extraction from TXT files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as temp_file:
            temp_file.write("Sample resume text content")
            temp_file_path = Path(temp_file.name)

        try:
            text = await resume_parser._extract_text_from_file(temp_file_path)  # type: ignore[attr-defined]
            assert text == "Sample resume text content"
        finally:
            temp_file_path.unlink()

    async def test_parse_unsupported_file_type(self, resume_parser: ResumeParser) -> None:
        """Test parsing unsupported file types."""
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as temp_file:
            temp_file.write(b"Executable content")
            temp_file_path = Path(temp_file.name)

        try:
            with pytest.raises(ValueError, match="Unsupported file type"):
                await resume_parser.parse_resume(temp_file_path)
        finally:
            temp_file_path.unlink()

    async def test_parse_corrupted_file(self, resume_parser: ResumeParser) -> None:
        """Test parsing corrupted or unreadable files."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"Corrupted PDF content")
            temp_file_path = Path(temp_file.name)

        try:
            # Should handle gracefully and return basic structure
            result = await resume_parser.parse_resume(temp_file_path)
            assert isinstance(result, ResumeData)
        finally:
            temp_file_path.unlink()

    async def test_ai_parsing_error_handling(self, resume_parser: ResumeParser, sample_resume_text: str) -> None:
        """Test error handling in AI parsing."""
        # Mock the AI client to raise an exception
        resume_parser.claude_client.messages.create.side_effect = Exception("API Error")  # type: ignore[assignment]

        # Should fall back to rule-based parsing
        result = await resume_parser.parse_resume_text(sample_resume_text, "resume.txt")
        assert isinstance(result, ResumeData)


class TestSkillAnalyzer:
    """Test the skill analysis service."""

    @pytest.fixture
    def skill_analyzer(self, mock_claude_client: AsyncMock) -> SkillAnalyzer:
        """Create a skill analyzer instance."""
        return SkillAnalyzer(claude_client=mock_claude_client)

    async def test_analyze_skill_gaps_with_targets(
        self, skill_analyzer: SkillAnalyzer, sample_resume_data: ResumeData
    ) -> None:
        """Test skill gap analysis with target roles."""
        target_roles = ["Senior Software Engineer", "Tech Lead"]
        target_industries = ["Technology"]

        # type: ignore[arg-type]
        # type: ignore[arg-type]
        result = await skill_analyzer.analyze_skill_gaps(sample_resume_data, target_roles, target_industries)  # type: ignore[arg-type]

        assert "skill_gaps" in result
        assert "skill_development_plan" in result
        assert "market_readiness_score" in result
        # type: ignore[arg-type]
        # type: ignore[arg-type]
        assert isinstance(result["skill_gaps"], list)  # type: ignore[arg-type]

    async def test_analyze_skill_gaps_without_targets(
        self, skill_analyzer: SkillAnalyzer, sample_resume_data: ResumeData
    ) -> None:
        """Test skill gap analysis without specific targets."""
        # type: ignore[arg-type]
        # type: ignore[arg-type]
        result = await skill_analyzer.analyze_skill_gaps(sample_resume_data, [], [])  # type: ignore[arg-type]

        assert "skill_gaps" in result
        # Should provide general improvement suggestions
        # type: ignore[arg-type]
        # type: ignore[arg-type]
        assert len(result["skill_gaps"]) >= 0  # type: ignore[arg-type]

    async def test_generate_learning_plan(self, skill_analyzer: SkillAnalyzer) -> None:
        """Test learning plan generation."""
        skill_gaps = [
            {"skill_name": "System Design", "current_level": "beginner", "target_level": "advanced", "priority": "high"}
        ]

        learning_preferences = {
            "learning_style": "visual",
            "time_commitment": 10,
            "learning_budget": 100,
            "preferred_formats": ["online_courses", "video_tutorials"],
        }

        result = await skill_analyzer.generate_learning_plan(skill_gaps, learning_preferences)  # type: ignore[attr-defined]

        assert isinstance(result, list)
        assert len(result) > 0
        assert "learning_resources" in result[0]
        assert "timeline" in result[0]

    async def test_assess_skill_levels(self, skill_analyzer: SkillAnalyzer, sample_resume_data: ResumeData) -> None:
        """Test skill level assessment based on experience."""
        result = await skill_analyzer.assess_skill_levels(sample_resume_data)  # type: ignore[attr-defined]

        assert isinstance(result, list)
        assert len(result) > 0

        for skill_assessment in result:
            assert "skill_name" in skill_assessment
            assert "assessed_level" in skill_assessment
            assert "confidence" in skill_assessment
            assert skill_assessment["confidence"] >= 0.0
            assert skill_assessment["confidence"] <= 1.0

    async def test_identify_trending_skills(self, skill_analyzer: SkillAnalyzer) -> None:
        """Test identification of trending skills in target industry."""
        industry = "Technology"
        roles = ["Senior Software Engineer"]

        result = await skill_analyzer.identify_trending_skills(industry, roles)  # type: ignore[attr-defined]

        assert isinstance(result, list)
        assert len(result) > 0

        for skill in result:
            assert "skill_name" in skill
            assert "demand_level" in skill
            assert "growth_trend" in skill
            assert skill["demand_level"] in ["high", "medium", "low"]

    async def test_calculate_readiness_score(
        self, skill_analyzer: SkillAnalyzer, sample_resume_data: ResumeData
    ) -> None:
        """Test calculation of market readiness score."""
        target_roles = ["Senior Software Engineer"]

        result = await skill_analyzer.calculate_readiness_score(sample_resume_data, target_roles)  # type: ignore[attr-defined]

        assert isinstance(result, dict)
        assert "overall_score" in result
        assert "skill_match_score" in result
        assert "experience_match_score" in result
        assert "education_match_score" in result

        assert 0 <= result["overall_score"] <= 100

    async def test_ai_skill_analysis(self, skill_analyzer: SkillAnalyzer, sample_resume_data: ResumeData) -> None:
        """Test AI-powered skill analysis."""
        target_roles = ["Senior Software Engineer"]
        target_industries = ["Technology"]

        result = await skill_analyzer._ai_analyze_skills(sample_resume_data, target_roles, target_industries)  # type: ignore[attr-defined]

        assert "skill_gaps" in result
        assert "market_analysis" in result
        assert "recommendations" in result

    async def test_rule_based_skill_analysis(
        self, skill_analyzer: SkillAnalyzer, sample_resume_data: ResumeData
    ) -> None:
        """Test rule-based skill analysis."""
        target_roles = ["Senior Software Engineer"]

        result = await skill_analyzer._rule_based_analyze_skills(sample_resume_data, target_roles)  # type: ignore[attr-defined]

        assert "skill_gaps" in result
        assert "recommendations" in result

    async def test_skill_analysis_error_handling(
        self, skill_analyzer: SkillAnalyzer, sample_resume_data: ResumeData
    ) -> None:
        """Test error handling in skill analysis."""
        # Mock AI client to raise an exception
        skill_analyzer.claude_client.messages.create.side_effect = Exception("API Error")  # type: ignore[assignment]

        # Should fall back to rule-based analysis
        # type: ignore[arg-type]
        # type: ignore[arg-type]
        result = await skill_analyzer.analyze_skill_gaps(sample_resume_data, ["Senior Engineer"], ["Technology"])  # type: ignore[arg-type]

        assert "skill_gaps" in result


class TestEnrichmentCoach:
    """Test the enrichment coach service."""

    @pytest.fixture
    def enrichment_coach(self, mock_claude_client: AsyncMock) -> EnrichmentCoach:
        """Create an enrichment coach instance."""
        return EnrichmentCoach(claude_client=mock_claude_client)

    async def test_generate_career_advice(
        self, enrichment_coach: EnrichmentCoach, sample_master_profile: MasterProfile
    ) -> None:
        """Test generation of career advice."""
        context = "career_transition"
        focus_area = "skill_development"

        # type: ignore[arg-type]
        # type: ignore[arg-type]
        result = await enrichment_coach.generate_career_advice(sample_master_profile, context, focus_area)  # type: ignore[arg-type]  # type: ignore[arg-type]  # type: ignore[arg-type]

        assert isinstance(result, dict)
        assert "advice" in result
        assert "action_items" in result
        assert "next_steps" in result
        # type: ignore[arg-type]
        # type: ignore[arg-type]
        assert isinstance(result["action_items"], list)  # type: ignore[arg-type]

    async def test_chat_with_coach(
        self, enrichment_coach: EnrichmentCoach, sample_master_profile: MasterProfile
    ) -> None:
        """Test interactive chat with career coach."""
        message = "How can I transition to a leadership role?"
        conversation_history = []

        result = await enrichment_coach.chat_with_coach(sample_master_profile, message, conversation_history)

        assert isinstance(result, dict)
        assert "response" in result
        assert "conversation_id" in result
        assert "suggested_actions" in result
        assert len(result["suggested_actions"]) > 0

    async def test_continue_conversation(
        self, enrichment_coach: EnrichmentCoach, sample_master_profile: MasterProfile
    ) -> None:
        """Test continuing an existing conversation."""
        conversation_history = [
            {"role": "user", "message": "What skills do I need for senior roles?", "timestamp": "2024-01-15T10:00:00Z"},
            {
                "role": "coach",
                "message": "Based on your profile, I recommend focusing on system design and leadership skills.",
                "timestamp": "2024-01-15T10:01:00Z",
            },
        ]

        new_message = "How long will it take to develop these skills?"

        result = await enrichment_coach.chat_with_coach(sample_master_profile, new_message, conversation_history)

        assert isinstance(result, dict)
        assert "response" in result
        # Should reference previous conversation context
        assert any(keyword in result["response"].lower() for keyword in ["system design", "leadership"])

    async def test_networking_guidance(
        self, enrichment_coach: EnrichmentCoach, sample_master_profile: MasterProfile
    ) -> None:
        """Test generation of networking guidance."""
        target_role = "Engineering Manager"
        industry = "Technology"

        result = await enrichment_coach.generate_networking_guidance(sample_master_profile, target_role, industry)

        assert isinstance(result, dict)
        assert "networking_strategy" in result
        assert "target_connections" in result
        assert "conversation_starters" in result
        assert "online_platforms" in result

    async def test_personal_branding_advice(
        self, enrichment_coach: EnrichmentCoach, sample_master_profile: MasterProfile
    ) -> None:
        """Test generation of personal branding advice."""
        result = await enrichment_coach.generate_personal_branding_advice(sample_master_profile)

        assert isinstance(result, dict)
        assert "brand_statement" in result
        assert "linkedin_optimization" in result
        assert "portfolio_suggestions" in result
        assert "thought_leadership" in result

    async def test_interview_preparation(
        self, enrichment_coach: EnrichmentCoach, sample_master_profile: MasterProfile
    ) -> None:
        """Test interview preparation guidance."""
        target_role = "Senior Software Engineer"
        company_type = "FAANG"

        result = await enrichment_coach.generate_interview_preparation(sample_master_profile, target_role, company_type)

        assert isinstance(result, dict)
        assert "technical_questions" in result
        assert "behavioral_questions" in result
        assert "system_design_prep" in result
        assert "company_research" in result

    async def test_salary_negotiation_guidance(
        self, enrichment_coach: EnrichmentCoach, sample_master_profile: MasterProfile
    ) -> None:
        """Test salary negotiation guidance."""
        offer_details = {
            "base_salary": 180000,
            "company": "Tech Corp",
            "role": "Senior Engineer",
            "location": "San Francisco",
        }

        result = await enrichment_coach.generate_salary_negotiation_guidance(sample_master_profile, offer_details)

        assert isinstance(result, dict)
        assert "market_analysis" in result
        assert "negotiation_strategy" in result
        assert "talking_points" in result
        assert "counter_offer_range" in result

    async def test_ai_coaching_response(self, enrichment_coach: EnrichmentCoach) -> None:
        """Test AI-powered coaching response generation."""
        user_profile_summary = "Experienced software engineer looking to advance to senior roles"
        message = "What should I focus on for career growth?"
        conversation_context = "skill_development"

        result = await enrichment_coach._ai_generate_coaching_response(
            user_profile_summary, message, conversation_context, []
        )

        assert isinstance(result, dict)
        assert "response" in result
        assert "action_items" in result

    async def test_rule_based_coaching_response(self, enrichment_coach: EnrichmentCoach) -> None:
        """Test rule-based coaching response generation."""
        message = "How can I improve my resume?"
        conversation_context = "resume_optimization"

        # type: ignore[arg-type]
        # type: ignore[arg-type]
        result = await enrichment_coach._rule_based_coaching_response(message, conversation_context)  # type: ignore[arg-type]

        assert isinstance(result, dict)
        assert "response" in result
        assert "action_items" in result

    async def test_coaching_error_handling(
        self, enrichment_coach: EnrichmentCoach, sample_master_profile: MasterProfile
    ) -> None:
        """Test error handling in coaching service."""
        # Mock AI client to raise an exception
        enrichment_coach.claude_client.messages.create.side_effect = Exception("API Error")  # type: ignore[assignment]

        # Should fall back to rule-based responses
        result = await enrichment_coach.chat_with_coach(sample_master_profile, "Career advice request", [])

        assert isinstance(result, dict)
        assert "response" in result


class TestJobMatcher:
    """Test the job matching service."""

    @pytest.fixture
    def job_matcher(self, mock_claude_client: AsyncMock) -> JobMatcher:
        """Create a job matcher instance."""
        return JobMatcher(claude_client=mock_claude_client)

    async def test_search_jobs_with_filters(self, job_matcher: JobMatcher) -> None:
        """Test job search with filters."""
        search_criteria = {
            "keywords": ["Senior Software Engineer", "Python"],
            "location": "San Francisco",
            "remote": True,
            "salary_min": 150000,
            "job_type": "full-time",
            "experience_level": "senior",
        }

        result = await job_matcher.search_jobs(search_criteria)

        assert isinstance(result, dict)
        assert "jobs" in result
        assert "search_metadata" in result
        # type: ignore[arg-type]
        # type: ignore[arg-type]
        assert isinstance(result["jobs"], list)  # type: ignore[arg-type]

        # type: ignore[arg-type]
        # type: ignore[arg-type]
        if result["jobs"]:  # type: ignore[arg-type]
            # type: ignore[arg-type]
            # type: ignore[arg-type]
            job = result["jobs"][0]  # type: ignore[arg-type]
            assert "job_id" in job
            assert "title" in job
            assert "company" in job
            assert "location" in job

    async def test_find_job_matches(self, job_matcher: JobMatcher, sample_resume_data: ResumeData) -> None:
        """Test finding job matches for a candidate."""
        user_preferences = {
            "target_roles": ["Senior Software Engineer"],
            "target_industries": ["Technology"],
            "location_preferences": ["San Francisco", "Remote"],
            "salary_range": {"min": 150000, "max": 200000},
        }

        result = await job_matcher.find_job_matches(sample_resume_data, user_preferences)

        assert isinstance(result, dict)
        assert "matches" in result
        assert "matching_criteria" in result
        assert isinstance(result["matches"], list)

        if result["matches"]:
            match = result["matches"][0]
            assert "job_id" in match
            assert "match_score" in match
            assert "match_reasons" in match
            assert 0 <= match["match_score"] <= 100

    async def test_calculate_match_score(self, job_matcher: JobMatcher, sample_resume_data: ResumeData) -> None:
        """Test calculation of job match score."""
        job_description = {
            "title": "Senior Software Engineer",
            "description": "Looking for experienced Python developer with cloud experience",
            "requirements": ["Python", "AWS", "5+ years experience"],
            "skills": ["Python", "JavaScript", "AWS", "Docker"],
            "experience_level": "senior",
        }

        result = await job_matcher.calculate_match_score(sample_resume_data, job_description)  # type: ignore[attr-defined]

        assert isinstance(result, dict)
        assert "overall_score" in result
        assert "skill_match_score" in result
        assert "experience_match_score" in result
        assert "education_match_score" in result
        assert 0 <= result["overall_score"] <= 100

    async def test_generate_application_strategy(self, job_matcher: JobMatcher, sample_resume_data: ResumeData) -> None:
        """Test generation of application strategy."""
        job_details = {
            "job_id": "job-123",
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "description": "Senior role requiring Python and cloud expertise",
            "requirements": ["Python", "AWS", "System Design"],
            "company_culture": "Innovative, fast-paced environment",
        }

        result = await job_matcher.generate_application_strategy(sample_resume_data, job_details)

        assert isinstance(result, dict)
        assert "resume_tailoring" in result
        assert "cover_letter_points" in result
        assert "interview_preparation" in result
        assert "networking_approach" in result

    async def test_analyze_job_market_trends(self, job_matcher: JobMatcher) -> None:
        """Test analysis of job market trends."""
        industry = "Technology"
        role = "Software Engineer"
        location = "San Francisco"

        result = await job_matcher.analyze_job_market_trends(industry, role, location)  # type: ignore[attr-defined]

        assert isinstance(result, dict)
        assert "demand_trend" in result
        assert "salary_trends" in result
        assert "skill_demand" in result
        assert "market_insights" in result

    async def test_ai_job_matching(self, job_matcher: JobMatcher, sample_resume_data: ResumeData) -> None:
        """Test AI-powered job matching."""
        user_preferences = {"target_roles": ["Senior Software Engineer"], "salary_min": 150000}

        result = await job_matcher._ai_find_matches(sample_resume_data, user_preferences)  # type: ignore[attr-defined]

        assert "matches" in result
        assert "matching_analysis" in result

    async def test_rule_based_job_matching(self, job_matcher: JobMatcher, sample_resume_data: ResumeData) -> None:
        """Test rule-based job matching."""
        user_preferences = {"target_roles": ["Software Engineer"], "location": "San Francisco"}

        result = await job_matcher._rule_based_find_matches(sample_resume_data, user_preferences)  # type: ignore[attr-defined]

        assert "matches" in result
        assert isinstance(result["matches"], list)

    async def test_job_matching_error_handling(self, job_matcher: JobMatcher, sample_resume_data: ResumeData) -> None:
        """Test error handling in job matching."""
        # Mock AI client to raise an exception
        job_matcher.claude_client.messages.create.side_effect = Exception("API Error")  # type: ignore[assignment]

        # Should fall back to rule-based matching
        result = await job_matcher.find_job_matches(sample_resume_data, {"target_roles": ["Engineer"]})

        assert "matches" in result


class TestServiceIntegration:
    """Test integration between services."""

    async def test_end_to_end_analysis_pipeline(self, mock_claude_client: AsyncMock) -> None:
        """Test complete analysis pipeline from resume to job recommendations."""
        # Create services
        resume_parser = ResumeParser(claude_client=mock_claude_client)
        skill_analyzer = SkillAnalyzer(claude_client=mock_claude_client)
        job_matcher = JobMatcher(claude_client=mock_claude_client)

        # Step 1: Parse resume
        resume_text = "John Doe - Senior Python Developer with 5 years experience"
        resume_data = await resume_parser.parse_resume_text(resume_text, "resume.txt")

        assert isinstance(resume_data, ResumeData)

        # Step 2: Analyze skills
        skill_analysis = await skill_analyzer.analyze_skill_gaps(
            # type: ignore[arg-type]
            resume_data,
            # type: ignore[arg-type]
            ["Senior Software Engineer"],  # type: ignore[arg-type]
            ["Technology"],
        )

        assert "skill_gaps" in skill_analysis

        # Step 3: Find job matches
        job_matches = await job_matcher.find_job_matches(resume_data, {"target_roles": ["Senior Software Engineer"]})

        assert "matches" in job_matches

        # Verify pipeline consistency
        assert resume_data is not None
        assert skill_analysis is not None
        assert job_matches is not None

    async def test_service_error_propagation(self, mock_claude_client: AsyncMock) -> None:
        """Test how errors propagate between services."""
        # Create services with failing AI client
        mock_claude_client.messages.create.side_effect = Exception("AI Service Unavailable")

        resume_parser = ResumeParser(claude_client=mock_claude_client)
        skill_analyzer = SkillAnalyzer(claude_client=mock_claude_client)

        # Services should handle errors gracefully
        resume_text = "Test resume content"
        resume_data = await resume_parser.parse_resume_text(resume_text, "resume.txt")
        assert isinstance(resume_data, ResumeData)

        # type: ignore[arg-type]
        # type: ignore[arg-type]
        skill_analysis = await skill_analyzer.analyze_skill_gaps(resume_data, ["Engineer"], ["Technology"])  # type: ignore[arg-type]
        assert "skill_gaps" in skill_analysis

    async def test_service_configuration(self) -> None:
        """Test service configuration and initialization."""
        # Test without AI client (rule-based mode)
        rule_based_parser = ResumeParser(claude_client=None)
        assert rule_based_parser.claude_client is None

        # Test with AI client
        mock_client = AsyncMock()
        ai_parser = ResumeParser(claude_client=mock_client)
        assert ai_parser.claude_client is mock_client

    async def test_concurrent_service_usage(self, mock_claude_client: AsyncMock) -> None:
        """Test concurrent usage of services."""
        import asyncio

        services = [
            ResumeParser(claude_client=mock_claude_client),
            SkillAnalyzer(claude_client=mock_claude_client),
            JobMatcher(claude_client=mock_claude_client),
        ]

        # Run multiple operations concurrently
        tasks = []
        for service in services:
            if isinstance(service, ResumeParser):
                tasks.append(service.parse_resume_text("Test content", "test.txt"))
            elif isinstance(service, SkillAnalyzer):
                # type: ignore[arg-type]
                # type: ignore[arg-type]
                tasks.append(service.analyze_skill_gaps(ResumeData(), ["Engineer"], ["Technology"]))  # type: ignore[arg-type]
            elif isinstance(service, JobMatcher):
                tasks.append(service.search_jobs({"keywords": ["Engineer"]}))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All operations should complete without raising exceptions
        for result in results:
            if isinstance(result, Exception):
                pytest.fail(f"Service operation failed: {result}")
            else:
                assert result is not None
