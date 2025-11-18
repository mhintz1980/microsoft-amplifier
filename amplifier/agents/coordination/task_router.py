"""
Intelligent Task Router and Distributor

Routes skill creation tasks to appropriate specialist agents with:
- Capability-based routing decisions
- Task complexity analysis
- Parallel task decomposition
- Resource requirement matching
- Quality assurance routing

Philosophy: Smart routing that maximizes parallel efficiency and agent specialization
"""

import asyncio
import uuid
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from ...utils.logger import get_logger

logger = get_logger(__name__)


class TaskComplexity(Enum):
    """Task complexity levels for routing decisions."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"


class TaskType(Enum):
    """Types of tasks that can be routed."""

    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    DEBUGGING = "debugging"
    TESTING = "testing"
    OPTIMIZATION = "optimization"
    ARCHITECTURE = "architecture"
    INTEGRATION = "integration"
    RESEARCH = "research"
    VALIDATION = "validation"
    COORDINATION = "coordination"


@dataclass
class TaskDefinition:
    """Complete definition of a task to be routed."""

    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType = TaskType.CODE_GENERATION
    description: str = ""
    required_capabilities: Set[str] = field(default_factory=set)
    input_data: Dict[str, Any] = field(default_factory=dict)
    expected_output_types: Set[str] = field(default_factory=set)
    priority: int = 5  # 1-10, higher is more important
    complexity: TaskComplexity = TaskComplexity.MODERATE
    estimated_runtime_seconds: float = 10.0
    max_concurrency: int = 1
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    requires_gpu: bool = False
    memory_requirement_mb: int = 512
    quality_threshold: float = 0.90
    timeout_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TaskRoutingDecision:
    """Decision made by the task router."""

    task_id: str
    selected_agent_ids: List[str]
    routing_strategy: str
    confidence: float
    reasoning: str
    estimated_success_probability: float
    parallel_execution_plan: Optional[Dict[str, Any]] = None
    fallback_agents: List[str] = field(default_factory=list)
    resource_allocation: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentCapabilityMatch:
    """Match between task requirements and agent capabilities."""

    agent_id: str
    agent_name: str
    match_score: float
    capability_coverage: Set[str]
    missing_capabilities: Set[str]
    performance_history: Dict[str, float]
    current_load: int
    max_concurrent_tasks: int
    estimated_queue_time: float


class TaskRouter:
    """Intelligent router for distributing tasks to specialized agents."""

    def __init__(self, agent_pool_manager):
        self.agent_pool_manager = agent_pool_manager
        self.routing_history: List[TaskRoutingDecision] = []
        self.performance_cache: Dict[str, Dict[str, float]] = {}  # agent_id -> metrics
        self._lock = asyncio.Lock()

    async def route_task(self, task: TaskDefinition) -> TaskRoutingDecision:
        """Route a task to the most appropriate agents."""
        logger.info(f"Routing task {task.task_id} of type {task.task_type.value}")

        try:
            # Analyze task requirements
            required_capabilities = await self._analyze_task_requirements(task)

            # Find matching agents
            matching_agents = await self._find_matching_agents(required_capabilities)

            if not matching_agents:
                logger.warning(f"No agents found for task {task.task_id}")
                return self._create_no_agents_decision(task)

            # Select best agents based on strategy
            selected_agents = await self._select_agents(task, matching_agents, required_capabilities)

            # Create routing decision
            decision = TaskRoutingDecision(
                task_id=task.task_id,
                selected_agent_ids=selected_agents,
                routing_strategy=self._determine_routing_strategy(task),
                confidence=self._calculate_confidence(task, matching_agents),
                reasoning=self._generate_reasoning(task, selected_agents),
                estimated_success_probability=self._estimate_success_probability(task, selected_agents),
                parallel_execution_plan=await self._create_parallel_plan(task, selected_agents),
                resource_allocation=self._allocate_resources(task, selected_agents),
            )

            # Update routing history
            async with self._lock:
                self.routing_history.append(decision)

            logger.info(f"Routed task {task.task_id} to {len(selected_agents)} agents")
            return decision

        except Exception as e:
            logger.error(f"Error routing task {task.task_id}: {e}")
            return self._create_error_decision(task, str(e))

    async def _analyze_task_requirements(self, task: TaskDefinition) -> Set[str]:
        """Analyze task to determine required capabilities."""
        required_capabilities = set(task.required_capabilities)

        # Infer capabilities from task type and description
        task_type_capabilities = {
            TaskType.CODE_GENERATION: {"code_generation", "implementation"},
            TaskType.ANALYSIS: {"analysis", "research", "information_gathering"},
            TaskType.DEBUGGING: {"debugging", "troubleshooting", "error_resolution"},
            TaskType.TESTING: {"testing", "quality_assurance", "validation"},
            TaskType.OPTIMIZATION: {"optimization", "performance", "efficiency"},
            TaskType.ARCHITECTURE: {"architecture", "design", "planning"},
            TaskType.INTEGRATION: {"integration", "apis", "external_services"},
            TaskType.RESEARCH: {"research", "content_analysis", "learning"},
            TaskType.VALIDATION: {"validation", "quality_check", "verification"},
            TaskType.COORDINATION: {"coordination", "orchestration", "management"},
        }

        # Add task type capabilities
        required_capabilities.update(task_type_capabilities.get(task.task_type, set()))

        # Analyze description for additional capabilities
        description_lower = task.description.lower()

        capability_keywords = {
            "architecture": {"architecture", "design", "planning", "structure"},
            "performance": {"performance", "optimization", "speed", "efficiency"},
            "security": {"security", "authentication", "authorization", "vulnerability"},
            "database": {"database", "sql", "data", "storage"},
            "api": {"api", "rest", "graphql", "endpoint"},
            "frontend": {"frontend", "ui", "react", "vue", "css"},
            "backend": {"backend", "server", "service", "microservice"},
            "testing": {"test", "testing", "pytest", "unit", "integration"},
            "deployment": {"deploy", "deployment", "docker", "kubernetes"},
            "documentation": {"docs", "documentation", "readme", "guide"},
        }

        for capability, keywords in capability_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                required_capabilities.add(capability)

        # Add complexity-based requirements
        if task.complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]:
            required_capabilities.add("expert_level")
            required_capabilities.add("quality_assurance")

        logger.debug(f"Task {task.task_id} requires capabilities: {required_capabilities}")
        return required_capabilities

    async def _find_matching_agents(self, required_capabilities: Set[str]) -> List[AgentCapabilityMatch]:
        """Find agents that can handle the required capabilities."""
        matches = []

        # Get pool status to see available agents
        pool_status = await self.agent_pool_manager.get_status()
        agents = pool_status.get("agents", {})

        for agent_id, agent_info in agents.items():
            # Get agent capabilities (simplified - would use actual agent registry)
            agent_capabilities = set(agent_info.get("capabilities", []))

            # Calculate match score
            intersection = required_capabilities.intersection(agent_capabilities)
            match_score = len(intersection) / len(required_capabilities) if required_capabilities else 0

            # Only consider agents with reasonable match
            if match_score > 0.3:  # At least 30% capability match
                match = AgentCapabilityMatch(
                    agent_id=agent_id,
                    agent_name=agent_info.get("name", "Unknown"),
                    match_score=match_score,
                    capability_coverage=intersection,
                    missing_capabilities=required_capabilities - agent_capabilities,
                    performance_history={
                        "success_rate": agent_info.get("success_rate", 0.95),
                        "avg_task_time": 10.0,  # Would get from performance history
                    },
                    current_load=agent_info.get("current_tasks", 0),
                    max_concurrent_tasks=agent_info.get("max_tasks", 1),
                    estimated_queue_time=0.0,  # Would calculate based on current tasks
                )

                matches.append(match)

        # Sort by match score (best first)
        matches.sort(key=lambda m: (m.match_score, -m.current_load), reverse=True)
        return matches

    async def _select_agents(
        self, task: TaskDefinition, matches: List[AgentCapabilityMatch], required_capabilities: Set[str]
    ) -> List[str]:
        """Select the best agents for the task."""
        if not matches:
            return []

        # Strategy depends on task complexity and type
        if task.complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]:
            # Use multiple agents for complex tasks
            return await self._select_multiple_agents(task, matches, required_capabilities)
        else:
            # Use single best agent for simple/moderate tasks
            return [matches[0].agent_id]

    async def _select_multiple_agents(
        self, task: TaskDefinition, matches: List[AgentCapabilityMatch], required_capabilities: Set[str]
    ) -> List[str]:
        """Select multiple agents for complex task decomposition."""
        selected_agents = []
        covered_capabilities = set()

        # First, select the best primary agent
        if matches:
            primary_agent = matches[0]
            selected_agents.append(primary_agent.agent_id)
            covered_capabilities.update(primary_agent.capability_coverage)

        # Add secondary agents to cover missing capabilities
        if len(required_capabilities - covered_capabilities) > 0:
            # Look for agents with complementary capabilities
            for match in matches[1:]:
                if len(selected_agents) >= task.max_concurrency:
                    break

                new_capabilities = match.capability_coverage - covered_capabilities
                if new_capabilities:
                    selected_agents.append(match.agent_id)
                    covered_capabilities.update(new_capabilities)

        return selected_agents

    def _determine_routing_strategy(self, task: TaskDefinition) -> str:
        """Determine the routing strategy for the task."""
        if task.complexity == TaskComplexity.SIMPLE:
            return "single_best"
        elif task.complexity == TaskComplexity.MODERATE:
            return "capability_match"
        elif task.complexity == TaskComplexity.COMPLEX:
            return "parallel_decomposition"
        else:  # CRITICAL
            return "redundant_execution"

    def _calculate_confidence(self, task: TaskDefinition, matches: List[AgentCapabilityMatch]) -> float:
        """Calculate confidence in the routing decision."""
        if not matches:
            return 0.0

        best_match = matches[0]

        # Base confidence from match score
        base_confidence = best_match.match_score

        # Adjust for agent performance history
        success_rate = best_match.performance_history.get("success_rate", 0.95)
        performance_factor = success_rate

        # Adjust for current load
        load_factor = 1.0 - (best_match.current_load / best_match.max_concurrent_tasks) * 0.2

        # Adjust for task complexity
        complexity_factor = {
            TaskComplexity.SIMPLE: 1.0,
            TaskComplexity.MODERATE: 0.9,
            TaskComplexity.COMPLEX: 0.8,
            TaskComplexity.CRITICAL: 0.7,
        }.get(task.complexity, 0.8)

        confidence = base_confidence * performance_factor * load_factor * complexity_factor
        return min(confidence, 1.0)

    def _generate_reasoning(self, task: TaskDefinition, selected_agents: List[str]) -> str:
        """Generate human-readable reasoning for the routing decision."""
        reasoning_parts = []

        # Task analysis
        reasoning_parts.append(f"Task type: {task.task_type.value}")
        reasoning_parts.append(f"Complexity: {task.complexity.value}")
        reasoning_parts.append(f"Required capabilities: {len(task.required_capabilities)}")

        # Agent selection
        reasoning_parts.append(f"Selected {len(selected_agents)} agent(s)")

        # Strategy explanation
        if task.complexity == TaskComplexity.SIMPLE:
            reasoning_parts.append("Strategy: Single best agent sufficient")
        elif task.complexity == TaskComplexity.COMPLEX:
            reasoning_parts.append("Strategy: Parallel decomposition across specialized agents")
        else:
            reasoning_parts.append("Strategy: Redundant execution for reliability")

        return " | ".join(reasoning_parts)

    def _estimate_success_probability(self, task: TaskDefinition, selected_agents: List[str]) -> float:
        """Estimate probability of successful task completion."""
        if not selected_agents:
            return 0.0

        # Base success probability from task quality threshold
        base_success = task.quality_threshold

        # Adjust for number of agents (redundancy helps)
        redundancy_factor = min(1.0 + (len(selected_agents) - 1) * 0.1, 1.3)

        # Adjust for task complexity
        complexity_factor = {
            TaskComplexity.SIMPLE: 1.0,
            TaskComplexity.MODERATE: 0.95,
            TaskComplexity.COMPLEX: 0.85,
            TaskComplexity.CRITICAL: 0.75,
        }.get(task.complexity, 0.9)

        success_probability = base_success * redundancy_factor * complexity_factor
        return min(success_probability, 1.0)

    async def _create_parallel_plan(self, task: TaskDefinition, selected_agents: List[str]) -> Dict[str, Any]:
        """Create parallel execution plan for multiple agents."""
        if len(selected_agents) <= 1:
            return None

        return {
            "primary_agent": selected_agents[0],
            "secondary_agents": selected_agents[1:],
            "coordination_strategy": "result_aggregation",
            "timeout_per_agent": task.timeout_seconds // len(selected_agents),
            "fallback_order": selected_agents,
            "quality_check": "cross_validation",
        }

    def _allocate_resources(self, task: TaskDefinition, selected_agents: List[str]) -> Dict[str, Any]:
        """Allocate resources for task execution."""
        total_memory = task.memory_requirement_mb
        memory_per_agent = total_memory // len(selected_agents) if selected_agents else total_memory

        return {
            "memory_per_agent_mb": memory_per_agent,
            "cpu_allocation": "high"
            if task.complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]
            else "normal",
            "gpu_required": task.requires_gpu,
            "network_access": task.task_type in [TaskType.RESEARCH, TaskType.INTEGRATION],
            "priority": task.priority,
        }

    def _create_no_agents_decision(self, task: TaskDefinition) -> TaskRoutingDecision:
        """Create decision when no suitable agents are found."""
        return TaskRoutingDecision(
            task_id=task.task_id,
            selected_agent_ids=[],
            routing_strategy="no_agents",
            confidence=0.0,
            reasoning=f"No agents found with required capabilities: {task.required_capabilities}",
            estimated_success_probability=0.0,
        )

    def _create_error_decision(self, task: TaskDefinition, error_message: str) -> TaskRoutingDecision:
        """Create decision when routing fails."""
        return TaskRoutingDecision(
            task_id=task.task_id,
            selected_agent_ids=[],
            routing_strategy="error",
            confidence=0.0,
            reasoning=f"Routing error: {error_message}",
            estimated_success_probability=0.0,
        )

    async def update_performance_feedback(
        self, task_id: str, agent_id: str, success: bool, runtime_seconds: float
    ) -> None:
        """Update performance cache with execution feedback."""
        async with self._lock:
            if agent_id not in self.performance_cache:
                self.performance_cache[agent_id] = {
                    "success_count": 0,
                    "total_count": 0,
                    "total_runtime": 0.0,
                    "avg_runtime": 0.0,
                    "success_rate": 0.0,
                }

            metrics = self.performance_cache[agent_id]
            metrics["total_count"] += 1
            metrics["total_runtime"] += runtime_seconds

            if success:
                metrics["success_count"] += 1

            metrics["avg_runtime"] = metrics["total_runtime"] / metrics["total_count"]
            metrics["success_rate"] = metrics["success_count"] / metrics["total_count"]

            logger.debug(f"Updated performance for agent {agent_id}: success_rate={metrics['success_rate']:.2f}")

    async def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing performance statistics."""
        async with self._lock:
            total_routings = len(self.routing_history)
            if total_routings == 0:
                return {"total_routings": 0}

            successful_routings = len([r for r in self.routing_history if r.selected_agent_ids])
            avg_confidence = sum(r.confidence for r in self.routing_history) / total_routings
            avg_success_probability = (
                sum(r.estimated_success_probability for r in self.routing_history) / total_routings
            )

            strategy_counts = {}
            for decision in self.routing_history:
                strategy_counts[decision.routing_strategy] = strategy_counts.get(decision.routing_strategy, 0) + 1

            return {
                "total_routings": total_routings,
                "successful_routings": successful_routings,
                "routing_success_rate": successful_routings / total_routings,
                "avg_confidence": avg_confidence,
                "avg_estimated_success_probability": avg_success_probability,
                "routing_strategies": strategy_counts,
                "performance_cache_size": len(self.performance_cache),
            }
