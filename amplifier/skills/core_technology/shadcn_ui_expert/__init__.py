"""
ShadCN/ui Expert System

Comprehensive ShadCN/ui expertise with zero hallucinations.
Provides mastery of modern React component libraries and design systems.
"""

from .core import ShadCNExpert
from .components import ComponentLibrary
from .accessibility import AccessibilityExpert
from .validation import ValidationEngine
from .agent_lightning import AgentLightningIntegration

__all__ = [
    "ShadCNExpert",
    "ComponentLibrary",
    "AccessibilityExpert",
    "ValidationEngine",
    "AgentLightningIntegration",
]

# Version and compatibility information
VERSION = "1.0.0"
SHADCN_VERSION_SUPPORTED = "^0.8.0"
REACT_VERSION_REQUIRED = "^18.0.0"
TYPESCRIPT_VERSION_REQUIRED = "^5.0.0"
