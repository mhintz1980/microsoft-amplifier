"""
Intelligent Context Management Module

Provides intelligent context pruning, auto-checkpointing, and progressive compression
for maintaining optimal context usage while preserving critical information.

Key Components:
- IntelligentContextPruner: Main service for context management
- ContextUsageMonitor: Monitors usage and triggers pruning
- PruningConfig: Configuration for pruning behavior
- Progressive compression with Docker storage integration
"""

from .intelligent_pruning_service import ContextCheckpoint
from .intelligent_pruning_service import ContextLevel
from .intelligent_pruning_service import ContextUsageMonitor
from .intelligent_pruning_service import IntelligentContextPruner
from .intelligent_pruning_service import PruningConfig
from .intelligent_pruning_service import PruningTrigger
from .intelligent_pruning_service import add_context_and_check
from .intelligent_pruning_service import create_manual_checkpoint
from .intelligent_pruning_service import get_compression_performance
from .intelligent_pruning_service import get_context_status
from .intelligent_pruning_service import get_intelligent_pruner
from .intelligent_pruning_service import initialize_intelligent_pruning

__all__ = [
    "ContextCheckpoint",
    "ContextLevel",
    "ContextUsageMonitor",
    "IntelligentContextPruner",
    "PruningConfig",
    "PruningTrigger",
    "add_context_and_check",
    "create_manual_checkpoint",
    "get_compression_performance",
    "get_context_status",
    "get_intelligent_pruner",
    "initialize_intelligent_pruning",
]
