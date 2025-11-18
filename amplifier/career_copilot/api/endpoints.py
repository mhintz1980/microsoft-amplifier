"""
Career Copilot API Endpoints

REST API endpoints for resume parsing, skill analysis, career coaching, and job matching.
"""

import logging
import uuid
from typing import Any

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from pydantic import BaseModel
from pydantic import Field

from ..models.master_profile import JobMatch
from ..models.master_profile import MasterProfile
from ..models.master_profile import SkillGap
from ..models.resume_data import ResumeData
from ..models.user_preferences import LearningPreferences
from ..models.user_preferences import UserPreferences
from ..services.enrichment_coach import EnrichmentCoach
from ..services.job_matcher import JobMatcher
from ..services.resume_parser import ResumeParseError
from ..services.resume_parser import ResumeParser
from ..services.skill_analyzer import SkillAnalyzer

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1", tags=["career-copilot"])

# Global service instances (in production, these would be properly initialized)
resume_parser = ResumeParser()
skill_analyzer = SkillAnalyzer()
enrichment_coach = EnrichmentCoach()
job_matcher = JobMatcher()


# Request/Response Models
class ResumeParseRequest(BaseModel):
    """Request model for resume parsing."""

    file_path: str | None = None
    resume_text: str | None = None


class SkillAnalysisRequest(BaseModel):
    """Request model for skill analysis."""

    resume_data: ResumeData
    user_preferences: UserPreferences
    target_roles: list[str] | None = None


class CareerAdviceRequest(BaseModel):
    """Request model for career advice."""

    resume_data: ResumeData
    user_preferences: UserPreferences
    skill_gaps: list[SkillGap]


class JobMatchRequest(BaseModel):
    """Request model for job matching."""

    resume_data: ResumeData
    user_preferences: UserPreferences
    skill_gaps: list[SkillGap]
    job_postings: list[dict[str, Any]] | None = None
    limit: int = Field(default=20, ge=1, le=100)


class ProfileCreateRequest(BaseModel):
    """Request model for creating master profile."""

    resume_data: ResumeData
    user_preferences: UserPreferences


class ProfileUpdateRequest(BaseModel):
    """Request model for updating master profile."""

    profile_id: str
    resume_data: ResumeData | None = None
    user_preferences: UserPreferences | None = None


# Health Check
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "career-copilot", "version": "1.0.0"}


# Resume Parsing Endpoints
@router.post("/resume/parse")
async def parse_resume_from_text(request: ResumeParseRequest):
    """Parse resume from text content."""
    if not request.resume_text:
        raise HTTPException(status_code=400, detail="Resume text is required")

    try:
        # Create temporary file for parsing
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(request.resume_text)
            tmp_file_path = tmp_file.name

        # Parse resume
        resume_data = await resume_parser.parse_resume(tmp_file_path)

        # Clean up temporary file
        import os

        os.unlink(tmp_file_path)

        return {"success": True, "data": resume_data.dict(), "message": "Resume parsed successfully"}

    except ResumeParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Resume parsing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse resume")


@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse resume from file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file type
    allowed_extensions = {".pdf", ".docx", ".txt", ".json", ".md"}
    file_extension = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )

    try:
        # Save uploaded file
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Parse resume
        resume_data = await resume_parser.parse_resume(tmp_file_path)

        # Clean up temporary file
        import os

        os.unlink(tmp_file_path)

        return {
            "success": True,
            "data": resume_data.dict(),
            "filename": file.filename,
            "message": "Resume uploaded and parsed successfully",
        }

    except ResumeParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Resume upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process uploaded resume")


# Skill Analysis Endpoints
@router.post("/skills/analyze")
async def analyze_skills(request: SkillAnalysisRequest):
    """Analyze skills and identify skill gaps."""
    try:
        skill_gaps = await skill_analyzer.analyze_skill_gaps(
            resume_data=request.resume_data,
            user_preferences=request.user_preferences,
            target_roles=request.target_roles,
        )

        # Generate skill insights
        insights = await skill_analyzer.generate_skill_insights(
            resume_data=request.resume_data, user_preferences=request.user_preferences, skill_gaps=skill_gaps
        )

        # Assess market demand
        market_demand = await skill_analyzer.assess_skill_market_demand(
            skills=request.resume_data.get_all_skills(),
            target_industries=request.user_preferences.career_goals.target_industries,
        )

        return {
            "success": True,
            "data": {
                "skill_gaps": [gap.dict() for gap in skill_gaps],
                "insights": [insight.dict() for insight in insights],
                "market_demand": market_demand,
            },
            "message": "Skill analysis completed successfully",
        }

    except Exception as e:
        logger.error(f"Skill analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze skills")


@router.post("/skills/learning-plan")
async def create_learning_plan(
    skill_gaps: list[SkillGap], learning_preferences: LearningPreferences, time_horizon: int = 12
):
    """Create a structured learning plan."""
    try:
        learning_plan = await enrichment_coach.create_learning_plan(
            skill_gaps=skill_gaps, learning_preferences=learning_preferences, time_horizon=time_horizon
        )

        return {"success": True, "data": learning_plan, "message": "Learning plan created successfully"}

    except Exception as e:
        logger.error(f"Learning plan creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create learning plan")


# Career Coaching Endpoints
@router.post("/career/advice")
async def get_career_advice(request: CareerAdviceRequest):
    """Get personalized career advice."""
    try:
        advice = await enrichment_coach.generate_career_advice(
            resume_data=request.resume_data, user_preferences=request.user_preferences, skill_gaps=request.skill_gaps
        )

        return {
            "success": True,
            "data": [insight.dict() for insight in advice],
            "message": "Career advice generated successfully",
        }

    except Exception as e:
        logger.error(f"Career advice generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate career advice")


@router.post("/career/networking")
async def get_networking_advice(
    resume_data: ResumeData, user_preferences: UserPreferences, target_industries: list[str] | None = None
):
    """Get networking advice."""
    try:
        networking_advice = await enrichment_coach.generate_networking_advice(
            resume_data=resume_data, user_preferences=user_preferences, target_industries=target_industries
        )

        return {"success": True, "data": networking_advice, "message": "Networking advice generated successfully"}

    except Exception as e:
        logger.error(f"Networking advice generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate networking advice")


@router.post("/career/personal-branding")
async def get_personal_branding_advice(resume_data: ResumeData, user_preferences: UserPreferences):
    """Get personal branding advice."""
    try:
        branding_advice = await enrichment_coach.generate_personal_branding_advice(
            resume_data=resume_data, user_preferences=user_preferences
        )

        return {"success": True, "data": branding_advice, "message": "Personal branding advice generated successfully"}

    except Exception as e:
        logger.error(f"Personal branding advice generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate personal branding advice")


# Job Matching Endpoints
@router.post("/jobs/matches")
async def find_job_matches(request: JobMatchRequest):
    """Find job matches based on profile and preferences."""
    try:
        matches = await job_matcher.find_job_matches(
            resume_data=request.resume_data,
            user_preferences=request.user_preferences,
            skill_gaps=request.skill_gaps,
            job_postings=request.job_postings,
            limit=request.limit,
        )

        return {
            "success": True,
            "data": [match.dict() for match in matches],
            "total_matches": len(matches),
            "message": f"Found {len(matches)} job matches",
        }

    except Exception as e:
        logger.error(f"Job matching failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to find job matches")


@router.post("/jobs/market-analysis")
async def analyze_job_market(
    resume_data: ResumeData, user_preferences: UserPreferences, job_postings: list[dict[str, Any]] | None = None
):
    """Analyze job market trends."""
    try:
        market_analysis = await job_matcher.analyze_job_market(
            resume_data=resume_data, user_preferences=user_preferences, job_postings=job_postings
        )

        return {"success": True, "data": market_analysis, "message": "Job market analysis completed successfully"}

    except Exception as e:
        logger.error(f"Job market analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze job market")


@router.post("/jobs/application-strategy")
async def generate_application_strategy(
    job_matches: list[JobMatch], resume_data: ResumeData, user_preferences: UserPreferences
):
    """Generate application strategy for job matches."""
    try:
        strategy = await job_matcher.generate_application_strategy(
            job_matches=job_matches, resume_data=resume_data, user_preferences=user_preferences
        )

        return {"success": True, "data": strategy, "message": "Application strategy generated successfully"}

    except Exception as e:
        logger.error(f"Application strategy generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate application strategy")


# Master Profile Endpoints
@router.post("/profiles")
async def create_profile(request: ProfileCreateRequest):
    """Create a new master profile."""
    try:
        # Generate unique profile ID
        profile_id = str(uuid.uuid4())

        # Create master profile
        profile = MasterProfile(
            profile_id=profile_id,
            resume_data=request.resume_data,
            user_preferences=request.user_preferences,
            user_id=None,
            last_analyzed=None,
            career_trajectory=None,
            overall_score=None,
            market_readiness=None,
        )

        # Calculate completion percentage
        profile.calculate_completion()

        return {"success": True, "data": profile.dict(), "message": "Profile created successfully"}

    except Exception as e:
        logger.error(f"Profile creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create profile")


@router.get("/profiles/{profile_id}")
async def get_profile(profile_id: str):
    """Get master profile by ID."""
    # In a real implementation, this would fetch from database
    # For now, return a mock response
    return {
        "success": True,
        "data": {"profile_id": profile_id, "status": "Profile would be fetched from database"},
        "message": "Profile retrieved successfully",
    }


@router.put("/profiles/{profile_id}")
async def update_profile(profile_id: str, request: ProfileUpdateRequest):
    """Update master profile."""
    try:
        # In a real implementation, this would update in database
        # For now, return a mock response
        return {
            "success": True,
            "data": {"profile_id": profile_id, "updated": True},
            "message": "Profile updated successfully",
        }

    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")


@router.post("/profiles/{profile_id}/analyze")
async def analyze_profile(profile_id: str, background_tasks: BackgroundTasks):
    """Run comprehensive analysis on a profile."""
    try:
        # In a real implementation, this would:
        # 1. Fetch profile from database
        # 2. Run skill gap analysis
        # 3. Generate career insights
        # 4. Find job matches
        # 5. Save results back to profile

        # For now, return a mock response
        analysis_id = str(uuid.uuid4())

        # Add background task for processing
        background_tasks.add_task(run_profile_analysis, profile_id=profile_id, analysis_id=analysis_id)

        return {
            "success": True,
            "data": {"analysis_id": analysis_id, "status": "processing", "estimated_completion": "2-5 minutes"},
            "message": "Profile analysis started",
        }

    except Exception as e:
        logger.error(f"Profile analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to start profile analysis")


async def run_profile_analysis(profile_id: str, analysis_id: str):
    """Background task for profile analysis."""
    try:
        logger.info(f"Starting profile analysis for {profile_id} (analysis: {analysis_id})")

        # In a real implementation, this would:
        # 1. Load profile from database
        # 2. Run all analysis services
        # 3. Update profile with results
        # 4. Notify user of completion

        logger.info(f"Profile analysis completed for {profile_id} (analysis: {analysis_id})")

    except Exception as e:
        logger.error(f"Profile analysis failed for {profile_id}: {e}")


# Analytics and Insights
@router.get("/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary for the service."""
    # In a real implementation, this would query analytics database
    return {
        "success": True,
        "data": {
            "total_profiles": 0,
            "total_resumes_parsed": 0,
            "total_analyses_completed": 0,
            "popular_skills": [],
            "average_profile_completion": 0.0,
            "active_users_today": 0,
        },
        "message": "Analytics summary retrieved successfully",
    }
