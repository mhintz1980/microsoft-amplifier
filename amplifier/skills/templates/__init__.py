"""
Skills Templates

Integration templates and utilities for various use cases.
"""

from .claude_code_integration import analyze_conversation_needs
from .claude_code_integration import auto_context_management
from .claude_code_integration import compress_conversation_context
from .claude_code_integration import create_skill_context_from_claude_session
from .claude_code_integration import progressive_context_loading
from .claude_code_integration import suggest_context_strategy

__all__ = [
    "compress_conversation_context",
    "analyze_conversation_needs",
    "progressive_context_loading",
    "auto_context_management",
    "create_skill_context_from_claude_session",
    "suggest_context_strategy",
]
