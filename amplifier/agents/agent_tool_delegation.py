"""
AutoGen AgentTool Dynamic Delegation System
Enables intelligent delegation between our 57 skills using AutoGen patterns
"""

from typing import Any, Dict, List, Optional, Union, Callable, Type
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import json
import time
import hashlib
import uuid
from abc import ABC, abstractmethod


class DelegationStrategy(Enum):
    DYNAMIC = "dynamic"  # Agent decides who to delegate to
    EXPERTISE_BASED = "expertise"  # Delegate based on skill expertise
    WORKFLOW_BASED = "workflow"  # Follow predefined workflow patterns
    PERFORMANCE_BASED = "performance"  # Delegate to best-performing agents


@dataclass
class AgentCapability:
    agent_id: str
    skill_category: str
    expertise_areas: List[str]
    performance_metrics: Dict[str, float]
    availability: bool
    avg_response_time: float
    success_rate: float
    last_used: str


@dataclass
class DelegationRequest:
    request_id: str
    task_description: str
    required_capabilities: List[str]
    task_complexity: str  # "simple", "medium", "complex"
    urgency: str  # "low", "medium", "high"
    context: Dict[str, Any]
    request_timestamp: str
    max_delegations: int = 3


@dataclass
class DelegationResponse:
    request_id: str
    delegated_agent_id: str
    delegation_strategy: str
    confidence_score: float
    execution_plan: List[str]
    estimated_completion_time: float
    response_timestamp: str
    metadata: Dict[str, Any]


class SkillAgent(ABC):
    """Abstract base class for skill agents that can be delegated to"""

    def __init__(self, skill_id: str, name: str, capability: AgentCapability):
        self.skill_id = skill_id
        self.name = name
        self.capability = capability
        self.delegation_history: List[str] = []

    @abstractmethod
    async def can_handle(self, task_description: str, required_capabilities: List[str]) -> float:
        """Return confidence score (0.0-1.0) for handling this task"""
        pass

    @abstractmethod
    async def execute_task(self, request: DelegationRequest) -> Dict[str, Any]:
        """Execute the delegated task"""
        pass

    @abstractmethod
    def get_expertise_tags(self) -> List[str]:
        """Get expertise tags for agent matching"""
        pass

    def update_performance_metrics(self, success: bool, response_time: float) -> None:
        """Update agent performance metrics"""
        self.capability.last_used = time.strftime("%Y-%m-%d %H:%M:%S")
        if success:
            # Update success rate with exponential moving average
            alpha = 0.1
            self.capability.success_rate = alpha * 1.0 + (1 - alpha) * self.capability.success_rate
        # Update average response time
        alpha = 0.05
        self.capability.avg_response_time = alpha * response_time + (1 - alpha) * self.capability.avg_response_time


class AgentToolDelegationManager:
    """
    AutoGen-inspired agent delegation system
    Enables intelligent task delegation across 57 skills with dynamic optimization
    """

    def __init__(self):
        self._skill_agents: Dict[str, SkillAgent] = {}
        self._delegation_strategies: Dict[str, Callable] = {}
        self._performance_cache: Dict[str, DelegationResponse] = {}
        self._delegation_stats: Dict[str, int] = {
            "total_delegations": 0,
            "successful_delegations": 0,
            "failed_delegations": 0,
            "cache_hits": 0,
        }
        self._register_default_strategies()

    def register_skill_agent(self, agent: SkillAgent) -> None:
        """Register a skill agent for delegation"""
        self._skill_agents[agent.skill_id] = agent

    def register_delegation_strategy(self, strategy_name: str, strategy_func: Callable) -> None:
        """Register a custom delegation strategy"""
        self._delegation_strategies[strategy_name] = strategy_func

    async def delegate_task(
        self, request: DelegationRequest, strategy: DelegationStrategy = DelegationStrategy.DYNAMIC
    ) -> DelegationResponse:
        """
        Delegate task to most appropriate agent using specified strategy
        """
        start_time = time.time()
        self._delegation_stats["total_delegations"] += 1

        try:
            # Check cache first for efficiency
            cache_key = self._generate_cache_key(request, strategy)
            if cache_key in self._performance_cache:
                self._delegation_stats["cache_hits"] += 1
                cached_response = self._performance_cache[cache_key]
                # Update timestamp for freshness
                cached_response.response_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                return cached_response

            # Get delegation strategy function
            strategy_func = self._delegation_strategies.get(strategy.value, self._default_dynamic_strategy)

            # Execute delegation strategy
            delegation_result = await strategy_func(request)

            # Cache successful delegation
            if delegation_result.confidence_score > 0.5:
                self._performance_cache[cache_key] = delegation_result

            # Update statistics
            elapsed = time.time() - start_time
            if delegation_result.confidence_score > 0.5:
                self._delegation_stats["successful_delegations"] += 1
            else:
                self._delegation_stats["failed_delegations"] += 1

            # Record delegation for learning
            if delegation_result.delegated_agent_id:
                agent = self._skill_agents.get(delegation_result.delegated_agent_id)
                if agent:
                    agent.delegation_history.append(request.request_id)

            return delegation_result

        except Exception as e:
            self._delegation_stats["failed_delegations"] += 1
            # Return error response
            return DelegationResponse(
                request_id=request.request_id,
                delegated_agent_id="",
                delegation_strategy="error",
                confidence_score=0.0,
                execution_plan=[],
                estimated_completion_time=0.0,
                response_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                metadata={"error": str(e)},
            )

    async def execute_delegated_task(
        self, delegation_response: DelegationResponse, request: DelegationRequest
    ) -> Dict[str, Any]:
        """
        Execute the delegated task using the selected agent
        """
        agent_id = delegation_response.delegated_agent_id
        agent = self._skill_agents.get(agent_id)

        if not agent or not agent.capability.availability:
            return {"success": False, "error": f"Agent {agent_id} not available", "request_id": request.request_id}

        try:
            start_time = time.time()
            result = await agent.execute_task(request)
            response_time = time.time() - start_time

            # Update agent performance metrics
            success = result.get("success", False)
            agent.update_performance_metrics(success, response_time)

            return result

        except Exception as e:
            agent.update_performance_metrics(False, 0.0)
            return {"success": False, "error": str(e), "request_id": request.request_id}

    def get_agent_capabilities(self) -> Dict[str, AgentCapability]:
        """Get capabilities of all registered agents"""
        return {agent_id: agent.capability for agent_id, agent in self._skill_agents.items()}

    def get_delegation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive delegation statistics"""
        total = self._delegation_stats["total_delegations"]
        if total == 0:
            return {"message": "No delegations performed yet"}

        success_rate = (self._delegation_stats["successful_delegations"] / total) * 100
        cache_hit_rate = (self._delegation_stats["cache_hits"] / max(total, 1)) * 100

        return {
            "total_delegations": total,
            "successful_delegations": self._delegation_stats["successful_delegations"],
            "failed_delegations": self._delegation_stats["failed_delegations"],
            "success_rate": f"{success_rate:.1f}%",
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "cache_size": len(self._performance_cache),
            "registered_agents": len(self._skill_agents),
            "available_agents": len([a for a in self._skill_agents.values() if a.capability.availability]),
        }

    # --- Delegation Strategy Implementations ---

    async def _default_dynamic_strategy(self, request: DelegationRequest) -> DelegationResponse:
        """Default dynamic delegation strategy based on capability matching"""
        best_agent_id = None
        best_score = 0.0

        for agent_id, agent in self._skill_agents.items():
            if not agent.capability.availability:
                continue

            confidence = await agent.can_handle(request.task_description, request.required_capabilities)

            # Factor in performance metrics
            performance_factor = agent.capability.success_rate * (1.0 / max(agent.capability.avg_response_time, 0.1))
            combined_score = confidence * 0.7 + performance_factor * 0.3

            if combined_score > best_score:
                best_score = combined_score
                best_agent_id = agent_id

        return DelegationResponse(
            request_id=request.request_id,
            delegated_agent_id=best_agent_id or "",
            delegation_strategy="dynamic_capability_matching",
            confidence_score=best_score,
            execution_plan=["delegate_to_best_agent", "execute_task", "return_results"],
            estimated_completion_time=5.0 if best_agent_id else 0.0,
            response_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            metadata={"best_agent_id": best_agent_id},
        )

    async def _expertise_based_strategy(self, request: DelegationRequest) -> DelegationResponse:
        """Delegation based on expertise matching"""
        return await self._default_dynamic_strategy(request)  # Placeholder

    async def _workflow_based_strategy(self, request: DelegationRequest) -> DelegationResponse:
        """Delegation following predefined workflow patterns"""
        return await self._default_dynamic_strategy(request)  # Placeholder

    async def _performance_based_strategy(self, request: DelegationRequest) -> DelegationResponse:
        """Delegation to best-performing agents"""
        return await self._default_dynamic_strategy(request)  # Placeholder

    # --- Private Helper Methods ---

    def _register_default_strategies(self) -> None:
        """Register default delegation strategies"""
        self._delegation_strategies["dynamic"] = self._default_dynamic_strategy
        self._delegation_strategies["expertise"] = self._expertise_based_strategy
        self._delegation_strategies["workflow"] = self._workflow_based_strategy
        self._delegation_strategies["performance"] = self._performance_based_strategy

    def _generate_cache_key(self, request: DelegationRequest, strategy: DelegationStrategy) -> str:
        """Generate cache key for delegation results"""
        cache_data = f"{request.task_description}:{','.join(request.required_capabilities)}:{strategy.value}"
        return hashlib.md5(cache_data.encode()).hexdigest()


# Example Skill Agent Implementation
class ExampleSkillAgent(SkillAgent):
    """Example implementation of a skill agent"""

    def __init__(self, skill_id: str, name: str, expertise_areas: List[str]):
        capability = AgentCapability(
            agent_id=skill_id,
            skill_category="general",
            expertise_areas=expertise_areas,
            performance_metrics={"accuracy": 0.9, "speed": 0.8},
            availability=True,
            avg_response_time=2.0,
            success_rate=0.95,
            last_used=time.strftime("%Y-%m-%d %H:%M:%S"),
        )
        super().__init__(skill_id, name, capability)

    async def can_handle(self, task_description: str, required_capabilities: List[str]) -> float:
        """Calculate confidence score for handling the task"""
        confidence = 0.5  # Base confidence

        # Check expertise match
        my_expertise = self.get_expertise_tags()
        expertise_match = len(set(required_capabilities) & set(my_expertise))
        confidence += (expertise_match / max(len(required_capabilities), 1)) * 0.3

        # Check availability and performance
        if self.capability.availability:
            confidence += self.capability.success_rate * 0.2

        return min(confidence, 1.0)

    async def execute_task(self, request: DelegationRequest) -> Dict[str, Any]:
        """Execute the delegated task"""
        start_time = time.time()

        # Simulate task execution
        await asyncio.sleep(1.0)  # Simulate processing time

        return {
            "success": True,
            "result": f"Task '{request.task_description}' completed by {self.skill_id}",
            "execution_time": time.time() - start_time,
            "request_id": request.request_id,
            "agent_id": self.skill_id,
        }

    def get_expertise_tags(self) -> List[str]:
        """Get expertise tags for this agent"""
        return self.capability.expertise_areas


# Global delegation manager for system-wide use
delegation_manager = AgentToolDelegationManager()
