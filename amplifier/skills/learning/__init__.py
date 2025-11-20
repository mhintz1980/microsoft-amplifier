"""
Development Learning System

Bridges development fixes to Agent Lightning's learning patterns.
Provides comprehensive fix recording, pattern extraction, and prevention systems
for continuous improvement of the skill ecosystem.

Key Components:
- DevelopmentFixRecorder: Records and learns from development fixes
- SkillCreationIntegrator: Integrates patterns into skill creation pipeline
- PreventionValidator: Validates skills against known failure patterns

This system connects development fixes to existing learning infrastructure:
- Pattern Learning System (meta_skills/pattern_learning_system.py)
- Knowledge Transfer System (agent_lightning_integration/knowledge_transfer_system.py)
- Error Detection Engine (agent_lightning_integration/error_detection_engine.py)
"""

from .development_fix_recorder import AffectedSkill
from .development_fix_recorder import DevelopmentFix
from .development_fix_recorder import DevelopmentFixRecorder
from .development_fix_recorder import FixApplication
from .development_fix_recorder import FixPattern
from .development_fix_recorder import FixType
from .development_fix_recorder import PreventionStrategy
from .development_fix_recorder import SeverityLevel
from .development_fix_recorder import ValidationRule
from .skill_creation_integration import SkillCreationIntegrator

__all__ = [
    # Core recording system
    "DevelopmentFixRecorder",
    "SkillCreationIntegrator",

    # Data models
    "DevelopmentFix",
    "FixPattern",
    "AffectedSkill",
    "ValidationRule",
    "FixApplication",

    # Enums
    "FixType",
    "SeverityLevel",
    "PreventionStrategy",
]

# Version information
__version__ = "1.0.0"
__author__ = "Development Learning System"

# System capabilities
SYSTEM_CAPABILITIES = {
    "fix_recording": True,
    "pattern_extraction": True,
    "prevention_validation": True,
    "skill_creation_integration": True,
    "knowledge_transfer_sync": True,
    "pattern_learning_sync": True,
    "automated_prevention": True,
    "template_integration": True,
}

def get_system_info() -> dict:
    """Get system information and capabilities"""
    return {
        "name": "Development Learning System",
        "version": __version__,
        "author": __author__,
        "capabilities": SYSTEM_CAPABILITIES,
        "description": "Bridges development fixes to Agent Lightning's learning patterns",
        "integration_points": [
            "Pattern Learning System",
            "Knowledge Transfer System",
            "Error Detection Engine",
            "Skill Creation Pipeline",
        ],
    }