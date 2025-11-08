"""
CAD Design Review Agent

A specialized AI agent for analyzing SolidWorks designs of industrial dewatering pumps
and sound-attenuating enclosures. Provides expert feedback on mechanical designs.
"""

from .core.analyzer import analyze_design
from .core.models import AnalysisResult, DesignRecommendation
from .core.reviewer import CADReviewer

__version__ = "1.0.0"
__all__ = ["CADReviewer", "analyze_design", "AnalysisResult", "DesignRecommendation"]
