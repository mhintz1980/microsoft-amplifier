# pyright: ignore所有测试类型错误

"""
Test FastAPI endpoints for AI Career Copilot.

This module tests API endpoints, request/response validation,
error handling, and integration with services.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock
from unittest.mock import patch

from fastapi.testclient import TestClient

from ..models.resume_data import ResumeData


class TestHealthEndpoints:
    """Test health check and status endpoints."""

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test the root health endpoint."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "AI Career Copilot"
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

    def test_health_endpoint(self, client: TestClient) -> None:
        """Test the detailed health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "checks" in data
        assert "timestamp" in data

    def test_debug_config_endpoint_development(self, client: TestClient) -> None:
        """Test debug config endpoint in development mode."""
        response = client.get("/debug/config")
        assert response.status_code == 200

        data = response.json()
        assert "config" in data
        assert "features" in data


class TestResumeEndpoints:
    """Test resume management endpoints."""

    def test_upload_resume_pdf(self, client: TestClient, temp_pdf_file: Path, mock_claude_client: AsyncMock) -> None:
        """Test uploading a PDF resume file."""
        with (
            patch("...services.resume_parser.get_claude_client", return_value=mock_claude_client),
            open(temp_pdf_file, "rb") as f,
        ):
            response = client.post("/api/v1/resume/upload", files={"file": ("resume.pdf", f, "application/pdf")})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "resume_data" in data
        assert "processing_time" in data

    def test_upload_resume_docx(self, client: TestClient, temp_docx_file: Path) -> None:
        """Test uploading a DOCX resume file."""
        with open(temp_docx_file, "rb") as f:
            response = client.post(
                "/api/v1/resume/upload",
                files={
                    "file": (
                        "resume.docx",
                        f,
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_upload_resume_invalid_format(self, client: TestClient) -> None:
        """Test uploading an invalid file format."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"This is not a valid format")
            temp_file_path = Path(temp_file.name)

        try:
            with open(temp_file_path, "rb") as f:
                response = client.post(
                    "/api/v1/resume/upload", files={"file": ("invalid.exe", f, "application/x-executable")}
                )

            assert response.status_code == 400
            data = response.json()
            assert "Invalid file format" in data["detail"]
        finally:
            temp_file_path.unlink()

    def test_upload_resume_file_too_large(self, client: TestClient) -> None:
        """Test uploading a file that exceeds size limits."""
        # Create a large file (larger than 10MB default limit)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            large_content = b"X" * (11 * 1024 * 1024)  # 11MB
            temp_file.write(large_content)
            temp_file_path = Path(temp_file.name)

        try:
            with open(temp_file_path, "rb") as f:
                response = client.post("/api/v1/resume/upload", files={"file": ("large.pdf", f, "application/pdf")})

            assert response.status_code == 413
            data = response.json()
            assert "File size exceeds" in data["detail"]
        finally:
            temp_file_path.unlink()

    def test_get_current_resume_no_resume(self, client: TestClient) -> None:
        """Test getting resume when none exists."""
        response = client.get("/api/v1/resume/current")
        assert response.status_code == 404

        data = response.json()
        assert "No resume found" in data["detail"]

    def test_update_resume_data(self, client: TestClient, sample_resume_data: ResumeData) -> None:
        """Test updating resume data."""
        resume_dict = sample_resume_data.model_dump()

        response = client.put("/api/v1/resume/current", json=resume_dict)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "resume_data" in data

    def test_update_resume_invalid_data(self, client: TestClient) -> None:
        """Test updating resume with invalid data."""
        invalid_data = {"invalid": "data"}

        response = client.put("/api/v1/resume/current", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_parse_resume_text(
        self, client: TestClient, sample_resume_text: str, mock_claude_client: AsyncMock
    ) -> None:
        """Test parsing resume from text."""
        with patch("...services.resume_parser.get_claude_client", return_value=mock_claude_client):
            response = client.post(
                "/api/v1/resume/parse-text", json={"text": sample_resume_text, "filename": "resume.txt"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "resume_data" in data


class TestProfileEndpoints:
    """Test profile management endpoints."""

    def test_get_profile_complete(self, client: TestClient, sample_master_profile: dict) -> None:
        """Test getting a complete user profile."""
        # First set up resume data
        with patch("amplifier.career_copilot.services.resume_parser.get_claude_client"):
            client.put("/api/v1/resume/current", json=sample_master_profile["resume_data"])

        response = client.get("/api/v1/profile")
        assert response.status_code == 200

        data = response.json()
        assert "user_id" in data
        assert "resume_data" in data
        assert "analytics" in data

    def test_get_profile_empty(self, client: TestClient) -> None:
        """Test getting profile when no data exists."""
        response = client.get("/api/v1/profile")
        assert response.status_code == 200

        data = response.json()
        # Should return default/empty profile structure
        assert "user_id" in data
        assert "analytics" in data

    def test_update_user_preferences(self, client: TestClient, sample_user_preferences: dict) -> None:
        """Test updating user preferences."""
        response = client.put("/api/v1/profile/preferences", json=sample_user_preferences)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True

    def test_get_profile_analytics(self, client: TestClient) -> None:
        """Test getting profile analytics."""
        response = client.get("/api/v1/profile/analytics")
        assert response.status_code == 200

        data = response.json()
        assert "profile_completion" in data
        assert "skill_coverage" in data
        assert "career_alignment" in data

    def test_delete_profile_data(self, client: TestClient) -> None:
        """Test deleting all profile data."""
        response = client.delete("/api/v1/profile")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Profile data deleted successfully"


class TestAnalysisEndpoints:
    """Test skill analysis and career insights endpoints."""

    def test_analyze_skills_with_targets(self, client: TestClient, sample_resume_data: ResumeData) -> None:
        """Test skill analysis with target roles."""
        # Setup resume data first
        with patch("amplifier.career_copilot.services.resume_parser.get_claude_client"):
            client.put("/api/v1/resume/current", json=sample_resume_data.model_dump())

        analysis_request = {
            "target_roles": ["Senior Software Engineer", "Tech Lead"],
            "target_industries": ["Technology", "FinTech"],
            "analysis_depth": "comprehensive",
        }

        response = client.post("/api/v1/analysis/skills", json=analysis_request)
        assert response.status_code == 200

        data = response.json()
        assert "skill_gaps" in data
        assert "skill_development_plan" in data
        assert "market_readiness_score" in data

    def test_analyze_skills_no_targets(self, client: TestClient) -> None:
        """Test skill analysis without specific targets."""
        response = client.post("/api/v1/analysis/skills", json={})
        assert response.status_code == 400

        data = response.json()
        assert "target_roles" in data["detail"]

    def test_analyze_career_path(self, client: TestClient, sample_resume_data: ResumeData) -> None:
        """Test career path analysis."""
        with patch("amplifier.career_copilot.services.resume_parser.get_claude_client"):
            client.put("/api/v1/resume/current", json=sample_resume_data.model_dump())

        analysis_request = {
            "target_roles": ["Engineering Manager"],
            "timeline": "3-5 years",
            "include_industry_trends": True,
        }

        response = client.post("/api/v1/analysis/career", json=analysis_request)
        assert response.status_code == 200

        data = response.json()
        assert "career_roadmap" in data
        assert "skill_requirements" in data
        assert "industry_insights" in data

    def test_get_analysis_history(self, client: TestClient) -> None:
        """Test getting analysis history."""
        response = client.get("/api/v1/analysis/history")
        assert response.status_code == 200

        data = response.json()
        assert "analyses" in data
        assert isinstance(data["analyses"], list)

    def test_get_progress_analytics(self, client: TestClient) -> None:
        """Test getting progress analytics."""
        response = client.get("/api/v1/analytics/progress")
        assert response.status_code == 200

        data = response.json()
        assert "skill_progress" in data
        assert "career_readiness_trend" in data
        assert "completion_tracking" in data


class TestChatEndpoints:
    """Test career coaching chat endpoints."""

    def test_start_coaching_conversation(self, client: TestClient) -> None:
        """Test starting a coaching conversation."""
        chat_request = {
            "message": "How can I transition from software engineering to data science?",
            "conversation_context": "career_transition",
        }

        response = client.post("/api/v1/chat/coach", json=chat_request)
        assert response.status_code == 200

        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert "suggested_actions" in data
        assert len(data["suggested_actions"]) > 0

    def test_continue_conversation(self, client: TestClient) -> None:
        """Test continuing an existing conversation."""
        # Start conversation first
        start_request = {
            "message": "What skills do I need for senior roles?",
            "conversation_context": "skill_development",
        }

        start_response = client.post("/api/v1/chat/coach", json=start_request)
        conversation_id = start_response.json()["conversation_id"]

        # Continue conversation
        continue_request = {
            "message": "How long will it take to develop these skills?",
            "conversation_id": conversation_id,
        }

        response = client.post("/api/v1/chat/coach", json=continue_request)
        assert response.status_code == 200

        data = response.json()
        assert "response" in data
        assert data["conversation_id"] == conversation_id

    def test_get_chat_history(self, client: TestClient) -> None:
        """Test getting chat conversation history."""
        response = client.get("/api/v1/chat/history")
        assert response.status_code == 200

        data = response.json()
        assert "conversations" in data
        assert isinstance(data["conversations"], list)

    def test_clear_chat_history(self, client: TestClient) -> None:
        """Test clearing chat history."""
        response = client.delete("/api/v1/chat/history")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True

    def test_chat_message_too_long(self, client: TestClient) -> None:
        """Test sending a message that exceeds length limits."""
        long_message = "x" * 5000  # Assuming limit is 4000 characters

        chat_request = {"message": long_message, "conversation_context": "general"}

        response = client.post("/api/v1/chat/coach", json=chat_request)
        assert response.status_code == 400

        data = response.json()
        assert "Message too long" in data["detail"]


class TestJobEndpoints:
    """Test job matching and search endpoints."""

    def test_search_jobs_with_filters(self, client: TestClient) -> None:
        """Test searching for jobs with filters."""
        search_request = {
            "keywords": ["Senior Software Engineer", "Python"],
            "location": "San Francisco",
            "remote": True,
            "salary_min": 150000,
            "job_type": "full-time",
        }

        response = client.post("/api/v1/jobs/search", json=search_request)
        assert response.status_code == 200

        data = response.json()
        assert "jobs" in data
        assert "search_metadata" in data
        assert isinstance(data["jobs"], list)

    def test_get_job_recommendations(self, client: TestClient, sample_resume_data: ResumeData) -> None:
        """Test getting personalized job recommendations."""
        # Setup resume data first
        with patch("amplifier.career_copilot.services.resume_parser.get_claude_client"):
            client.put("/api/v1/resume/current", json=sample_resume_data.model_dump())

        response = client.get("/api/v1/jobs/recommendations")
        assert response.status_code == 200

        data = response.json()
        assert "recommendations" in data
        assert "matching_criteria" in data
        assert isinstance(data["recommendations"], list)

        if data["recommendations"]:
            job = data["recommendations"][0]
            assert "job_id" in job
            assert "match_score" in job
            assert "match_reasons" in job

    def test_generate_application_strategy(self, client: TestClient) -> None:
        """Test generating application strategy for a specific job."""
        strategy_request = {
            "job_id": "test-job-123",
            "job_description": "Senior Software Engineer position requiring Python and cloud experience",
            "company_info": "Tech company focused on cloud solutions",
            "focus_areas": ["resume_tailoring", "interview_prep", "networking"],
        }

        response = client.post("/api/v1/jobs/strategy", json=strategy_request)
        assert response.status_code == 200

        data = response.json()
        assert "strategy" in data
        assert "resume_suggestions" in data["strategy"]
        assert "interview_tips" in data["strategy"]
        assert "networking_approach" in data["strategy"]

    def test_save_job_interest(self, client: TestClient) -> None:
        """Test saving a job as interesting."""
        save_request = {
            "job_id": "test-job-456",
            "status": "interested",
            "notes": "Interesting company culture and tech stack",
        }

        response = client.post("/api/v1/jobs/save", json=save_request)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True

    def test_get_saved_jobs(self, client: TestClient) -> None:
        """Test getting saved/interesting jobs."""
        response = client.get("/api/v1/jobs/saved")
        assert response.status_code == 200

        data = response.json()
        assert "saved_jobs" in data
        assert isinstance(data["saved_jobs"], list)


class TestErrorHandling:
    """Test API error handling and edge cases."""

    def test_404_not_found(self, client: TestClient) -> None:
        """Test 404 error for non-existent endpoints."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, client: TestClient) -> None:
        """Test 405 error for unsupported HTTP methods."""
        response = client.patch("/api/v1/resume/current")
        assert response.status_code == 405

    def test_invalid_json_request(self, client: TestClient) -> None:
        """Test handling of invalid JSON in request body."""
        response = client.post(
            # type: ignore[arg-type]
            "/api/v1/analysis/skills",
            # type: ignore[arg-type]
            data="invalid json",  # type: ignore[arg-type]
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_missing_required_fields(self, client: TestClient) -> None:
        """Test validation errors for missing required fields."""
        response = client.post("/api/v1/resume/parse-text", json={})
        assert response.status_code == 422

        data = response.json()
        assert "text" in str(data["detail"])

    def test_rate_limiting(self, client: TestClient) -> None:
        """Test rate limiting behavior."""
        # Make multiple rapid requests to trigger rate limiting
        responses = []
        for _ in range(70):  # Assuming limit is 60 per minute
            response = client.get("/api/v1/profile")
            responses.append(response)
            if response.status_code == 429:
                break

        # Should eventually hit rate limit
        rate_limited = any(r.status_code == 429 for r in responses)
        assert rate_limited, "Rate limiting should be triggered"

    def test_authentication_required(self, client: TestClient) -> None:
        """Test endpoints that require authentication when it's enabled."""
        # This test would need to be run with authentication enabled
        # For now, just test that the endpoint exists
        response = client.get("/api/v1/profile/protected")
        # Should succeed in test environment (no auth required)
        assert response.status_code in [200, 401, 403]


class TestResponseFormats:
    """Test API response formats and content types."""

    def test_json_response_headers(self, client: TestClient) -> None:
        """Test that responses include proper JSON headers."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    def test_cors_headers(self, client: TestClient) -> None:
        """Test CORS headers are properly set."""
        response = client.options("/api/v1/profile")
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_response_data_structure(self, client: TestClient, sample_resume_data: ResumeData) -> None:
        """Test that response data follows expected structure."""
        with patch("amplifier.career_copilot.services.resume_parser.get_claude_client"):
            response = client.put("/api/v1/resume/current", json=sample_resume_data.model_dump())

        assert response.status_code == 200
        data = response.json()

        # Check that response includes expected fields
        assert "success" in data
        assert "resume_data" in data
        assert "timestamp" in data

    def test_error_response_structure(self, client: TestClient) -> None:
        """Test that error responses follow consistent structure."""
        response = client.post("/api/v1/analysis/skills", json={})
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str | list)
