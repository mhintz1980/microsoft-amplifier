"""
Dynamic Agent Loading Framework

Progressive agent discovery and on-demand loading system for efficient context management.

Usage:
    from amplifier.agents import find_agents_by_tags, load_agent

    # Find agents for architecture tasks
    agents = find_agents_by_tags(['architecture', 'design'])

    # Load specific agent
    result = load_agent('zen-architect')
    if result.success:
        agent_content = result.content
"""

from .dynamic_loader import AgentLoadResult
from .dynamic_loader import AgentMetadata
from .dynamic_loader import DynamicAgentLoader
from .dynamic_loader import find_agents_by_description
from .dynamic_loader import find_agents_by_tags
from .dynamic_loader import get_agent_loader
from .dynamic_loader import load_agent
from .task_integration import TaskAgentResolver
from .task_integration import get_agent_content
from .task_integration import get_task_resolver
from .task_integration import resolve_agent_for_task

__all__ = [
    "DynamicAgentLoader",
    "AgentMetadata",
    "AgentLoadResult",
    "get_agent_loader",
    "find_agents_by_tags",
    "find_agents_by_description",
    "load_agent",
    "TaskAgentResolver",
    "get_task_resolver",
    "resolve_agent_for_task",
    "get_agent_content",
]


# Auto-build registry on import
def _auto_build_registry():
    """Auto-build registry if needed"""
    loader = get_agent_loader()
    if not loader.registry_file.exists():
        loader.build_registry()


_auto_build_registry()
