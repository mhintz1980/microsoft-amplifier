"""
CreaTech Assistant: Creative Development Agent

A specialized agent that seamlessly blends technical programming precision
with creative and artistic intelligence, built on Agent Lightning and integrated
with the Amplifier ecosystem.
"""

from .core.creative_engineer import CreativeEngineer
from .core.synthesizer import CreativeTechnicalSynthesizer
from .workflows.creative_workflows import CreativeWorkflows

__version__ = "1.0.0"
__all__ = ["CreativeEngineer", "CreativeTechnicalSynthesizer", "CreativeWorkflows"]
