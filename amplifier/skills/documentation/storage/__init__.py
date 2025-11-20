"""
Storage components for documentation management system.
"""

from .mcp_integration import MCPDocumentationStorage
from .mcp_integration import StorageConfig

__all__ = [
    "MCPDocumentationStorage",
    "StorageConfig",
]
