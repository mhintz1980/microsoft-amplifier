"""
Core documentation management components.
"""

from .template_engine import DocumentationTemplate
from .progressive_formatter import ProgressiveFormatter, DisclosureLevel
from .quality_validator import DocumentationValidator, ValidationRule
from .cross_reference_manager import CrossReferenceManager, SkillRelationship
from .version_manager import DocumentationVersionManager, VersionInfo

__all__ = [
    "DocumentationTemplate",
    "ProgressiveFormatter",
    "DisclosureLevel",
    "DocumentationValidator",
    "ValidationRule",
    "CrossReferenceManager",
    "SkillRelationship",
    "DocumentationVersionManager",
    "VersionInfo",
]
