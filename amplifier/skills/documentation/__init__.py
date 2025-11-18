"""
Amplifier Skills Documentation Management System

A comprehensive, agent-optimized documentation system for the 57-skill ecosystem.
Ensures consistency, completeness, and minimal token consumption.
"""

from .core.template_engine import DocumentationTemplate
from .core.progressive_formatter import ProgressiveFormatter
from .core.quality_validator import DocumentationValidator
from .core.cross_reference_manager import CrossReferenceManager
from .core.version_manager import DocumentationVersionManager
from .storage.mcp_integration import MCPDocumentationStorage
from .generation.auto_generator import AutomaticDocumentationGenerator

__all__ = [
    "DocumentationTemplate",
    "ProgressiveFormatter",
    "DocumentationValidator",
    "CrossReferenceManager",
    "DocumentationVersionManager",
    "MCPDocumentationStorage",
    "AutomaticDocumentationGenerator",
]
