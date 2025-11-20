"""
ShadCN/ui Expert System

Comprehensive ShadCN/ui expertise with zero hallucinations.
Provides mastery of modern React component libraries and design systems.
"""

from .accessibility import AccessibilityExpert
from .agent_lightning import AgentLightningIntegration
from .components import ComponentLibrary
from .core import ShadCNExpert
from .validation import ValidationEngine

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
