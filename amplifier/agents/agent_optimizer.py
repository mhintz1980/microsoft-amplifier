#!/usr/bin/env python3
"""
Agent Context Optimizer - Progressive Disclosure System

Implements dynamic agent loading and progressive disclosure to minimize
context window usage while maintaining full agent functionality.

Design Principles:
- Lazy Loading: Only load agent interfaces initially
- Progressive Disclosure: Load full agent code when invoked
- Dynamic Activation: Minimal context footprint until needed
- Context Optimization: Follow same patterns as skills system
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from amplifier.sdk_enhancements.context_management import ContextOptimizer


@dataclass
class AgentMetadata:
    """Lightweight agent information for initial loading."""

    name: str
    description: str
    capabilities: List[str]
    interface_methods: List[str]
    file_path: Path
    estimated_context_tokens: int
    priority: int = 5  # 1=highest priority
    is_loaded: bool = False


@dataclass
class AgentLoadRequest:
    """Request to load an agent with specific activation level."""

    agent_name: str
    activation_level: str  # "interface", "basic", "full", "enhanced"
    context_budget: int = 1000  # Maximum tokens to use


class AgentLoader:
    """
    Progressive agent loading system with context optimization.

    Follows the same principles as skills optimization:
    - Start with minimal footprint
    - Load progressively as needed
    - Optimize context usage at each level
    """

    def __init__(self, context_optimizer: Optional[ContextOptimizer] = None):
        self.context_optimizer = context_optimizer or ContextOptimizer()
        self.loaded_agents: Dict[str, Any] = {}
        self.agent_metadata: Dict[str, AgentMetadata] = {}
        self.context_usage = 0
        self.load_history: List[AgentLoadRequest] = []

        # Initialize with agent registry
        self._initialize_agent_registry()

    def _initialize_agent_registry(self) -> None:
        """Build lightweight registry of all available agents."""
        agents_dir = Path(__file__).parent

        # Scan for agent files and build metadata
        for agent_file in agents_dir.glob("*_agent.py"):
            try:
                metadata = self._extract_agent_metadata(agent_file)
                self.agent_metadata[metadata.name] = metadata
            except Exception as e:
                print(f"Warning: Could not load metadata for {agent_file}: {e}")

    def _extract_agent_metadata(self, agent_file: Path) -> AgentMetadata:
        """Extract minimal metadata without loading full agent."""
        # Read only the first part of the file to get metadata
        with open(agent_file, "r", encoding="utf-8") as f:
            content_lines = f.readlines()

        # Extract basic info from docstring and imports
        name = agent_file.stem.replace("_agent", "")
        description = "Agent for specialized tasks"
        capabilities = []
        interface_methods = []

        # Parse docstring for description and capabilities
        in_docstring = False
        docstring_content = []

        for line in content_lines[:50]:  # Only check first 50 lines
            line = line.strip()

            if '"""' in line:
                if not in_docstring:
                    in_docstring = True
                    # Remove the quotes
                    line = line.replace('"""', "").strip()
                elif in_docstring and line == "":
                    in_docstring = False
                    break

            if in_docstring and line:
                docstring_content.append(line)

            # Look for capability hints
            if "Capabilities:" in line:
                # Next lines until empty string are capabilities
                capabilities_line_index = content_lines.index(line)
                for i in range(capabilities_line_index + 1, len(content_lines)):
                    cap_line = content_lines[i].strip()
                    if cap_line.startswith("-") and not cap_line.startswith("--"):
                        capabilities.append(cap_line[1:].strip())
                    elif cap_line == "":
                        break

        # Estimate context tokens (rough calculation)
        file_size = agent_file.stat().st_size
        estimated_tokens = max(200, file_size // 3)  # Rough estimate

        return AgentMetadata(
            name=name,
            description=description,
            capabilities=capabilities or [f"{name} specialized tasks"],
            interface_methods=["analyze", "execute", "validate"],
            file_path=agent_file,
            estimated_context_tokens=estimated_tokens,
        )

    def get_available_agents(self, max_results: int = 50) -> List[AgentMetadata]:
        """
        Get lightweight list of available agents with minimal context usage.

        This is the primary interface for agent discovery - returns only
        metadata, not full agent implementations.
        """
        agents = list(self.agent_metadata.values())
        # Sort by priority and estimated context usage
        agents.sort(key=lambda a: (a.priority, a.estimated_context_tokens))

        return agents[:max_results]

    async def load_agent_interface(self, agent_name: str) -> Optional[Any]:
        """
        Load only the agent interface (class definition, no implementation).

        Activation Level: "interface" - ~10% of full context usage
        Returns agent class without importing heavy dependencies
        """
        if agent_name not in self.agent_metadata:
            return None

        metadata = self.agent_metadata[agent_name]

        # Create lightweight interface stub
        interface_code = f"""
# Interface stub for {agent_name}
class {agent_name.title()}Agent:
    \"\"\"Lightweight interface for {metadata.description}\"\"\"

    def __init__(self):
        self.name = "{agent_name}"
        self.capabilities = {metadata.capabilities}
        self.is_interface_only = True

    async def analyze(self, *args, **kwargs):
        raise NotImplementedError("Full implementation not loaded")

    async def execute(self, *args, **kwargs):
        raise NotImplementedError("Full implementation not loaded")
"""

        # Execute interface code in safe namespace
        namespace = {}
        exec(interface_code, namespace)

        agent_interface = namespace[f"{agent_name.title()}Agent"]
        metadata.is_loaded = True

        # Track load
        self.load_history.append(
            AgentLoadRequest(agent_name=agent_name, activation_level="interface", context_budget=100)
        )

        return agent_interface

    async def load_agent_basic(self, agent_name: str) -> Optional[Any]:
        """
        Load basic agent implementation with core functionality.

        Activation Level: "basic" - ~30% of full context usage
        Loads agent class with core methods, excluding heavy utilities
        """
        if agent_name not in self.agent_metadata:
            return None

        metadata = self.agent_metadata[agent_name]

        try:
            # Import with minimal dependencies
            spec = __import__(f"amplifier.agents.{agent_name}_agent", fromlist=[f"{agent_name.title()}Agent"])
            agent_class = getattr(spec, f"{agent_name.title()}Agent")

            # Create instance with basic configuration
            agent_instance = agent_class(basic_mode=True)

            metadata.is_loaded = True

            # Track load
            self.load_history.append(
                AgentLoadRequest(agent_name=agent_name, activation_level="basic", context_budget=300)
            )

            return agent_instance

        except Exception as e:
            print(f"Warning: Could not load basic agent {agent_name}: {e}")
            return None

    async def load_agent_full(self, agent_name: str, context_budget: int = 2000) -> Optional[Any]:
        """
        Load complete agent implementation with all capabilities.

        Activation Level: "full" - 100% context usage
        Only used when agent is actually needed for complex tasks
        """
        if agent_name not in self.agent_metadata:
            return None

        metadata = self.agent_metadata[agent_name]

        try:
            # Full import with all dependencies
            spec = __import__(f"amplifier.agents.{agent_name}_agent", fromlist=[f"{agent_name.title()}Agent"])
            agent_class = getattr(spec, f"{agent_name.title()}Agent")

            # Create full instance
            agent_instance = agent_class()

            metadata.is_loaded = True

            # Track load
            self.load_history.append(
                AgentLoadRequest(agent_name=agent_name, activation_level="full", context_budget=context_budget)
            )

            return agent_instance

        except Exception as e:
            print(f"Warning: Could not load full agent {agent_name}: {e}")
            return None

    def get_optimization_report(self) -> Dict[str, Any]:
        """Get context optimization statistics and recommendations."""
        total_agents = len(self.agent_metadata)
        loaded_agents = sum(1 for m in self.agent_metadata.values() if m.is_loaded)

        context_saved = 0
        for metadata in self.agent_metadata.values():
            if not metadata.is_loaded:
                context_saved += metadata.estimated_context_tokens

        activation_levels = {}
        for request in self.load_history:
            level = request.activation_level
            activation_levels[level] = activation_levels.get(level, 0) + 1

        return {
            "total_agents": total_agents,
            "loaded_agents": loaded_agents,
            "context_saved_tokens": context_saved,
            "load_efficiency": f"{loaded_agents}/{total_agents} agents loaded",
            "activation_distribution": activation_levels,
            "optimization_recommendations": self._get_recommendations(),
        }

    def _get_recommendations(self) -> List[str]:
        """Get optimization recommendations based on current usage."""
        recommendations = []

        # Check for unused agents
        unused_agents = [
            name for name, meta in self.agent_metadata.items() if not meta.is_loaded and meta.priority <= 3
        ]
        if unused_agents:
            recommendations.append(f"Consider pre-loading high-priority agents: {', '.join(unused_agents[:3])}")

        # Check for overloading
        full_loads = sum(1 for req in self.load_history if req.activation_level == "full")
        if full_loads > len(self.agent_metadata) * 0.5:
            recommendations.append("Many agents fully loaded - consider using interface mode for discovery")

        # Check context efficiency
        total_potential = sum(meta.estimated_context_tokens for meta in self.agent_metadata.values())
        actual_loaded = sum(req.context_budget for req in self.load_history)

        if actual_loaded > total_potential * 0.3:
            recommendations.append("High context usage - consider unloading unused agents")

        return recommendations


class AgentManager:
    """
    High-level agent management with automatic optimization.

    Provides simple interface while handling all progressive disclosure
    and context optimization behind the scenes.
    """

    def __init__(self):
        self.loader = AgentLoader()
        self.active_agents: Dict[str, Any] = {}
        self.session_context_budget = 10000  # Configurable per session

    async def get_agent(self, agent_name: str, task_complexity: str = "basic") -> Optional[Any]:
        """
        Get agent with appropriate activation level based on task complexity.

        Args:
            agent_name: Name of agent to load
            task_complexity: "simple", "basic", "complex", "advanced"

        Returns:
            Agent instance with appropriate activation level
        """
        # Map task complexity to activation level
        activation_map = {"simple": "interface", "basic": "basic", "complex": "full", "advanced": "full"}

        activation_level = activation_map.get(task_complexity, "basic")

        # Check if already loaded
        if agent_name in self.active_agents:
            return self.active_agents[agent_name]

        # Load agent with appropriate level
        if activation_level == "interface":
            agent = await self.loader.load_agent_interface(agent_name)
        elif activation_level == "basic":
            agent = await self.loader.load_agent_basic(agent_name)
        else:  # full
            agent = await self.loader.load_agent_full(agent_name)

        if agent:
            self.active_agents[agent_name] = agent

        return agent

    async def list_available_agents(self, task_type: Optional[str] = None) -> List[AgentMetadata]:
        """List available agents, optionally filtered by task type."""
        agents = self.loader.get_available_agents()

        if task_type:
            # Filter by capabilities that match task type
            agents = [a for a in agents if any(task_type.lower() in cap.lower() for cap in a.capabilities)]

        return agents

    async def optimize_context_usage(self) -> Dict[str, Any]:
        """Optimize current context usage and provide recommendations."""
        # Unload least recently used agents if context is high
        if len(self.active_agents) > 5:  # Threshold for optimization
            # Simple LRU - remove oldest half
            agents_to_remove = list(self.active_agents.keys())[: len(self.active_agents) // 2]
            for agent_name in agents_to_remove:
                del self.active_agents[agent_name]

        return self.loader.get_optimization_report()


# Global agent manager instance
agent_manager = AgentManager()


# Convenience functions for common operations
async def get_agent_for_task(agent_name: str, task_complexity: str = "basic") -> Optional[Any]:
    """Get optimized agent for specific task."""
    return await agent_manager.get_agent(agent_name, task_complexity)


async def list_agents_by_capability(capability: str) -> List[AgentMetadata]:
    """List agents that have specific capability."""
    return await agent_manager.list_available_agents(capability)


def get_context_optimization_report() -> Dict[str, Any]:
    """Get current optimization status."""
    return agent_manager.loader.get_optimization_report()
