"""
Career Copilot API

FastAPI endpoints for the AI Career Copilot service.
Provides REST API for resume parsing, skill analysis, career coaching, and job matching.
"""

from .endpoints import router
from .middleware import setup_middleware

__all__ = ["router", "setup_middleware"]
