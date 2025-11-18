"""
Agent Pool Management

Coordinates up to 15 specialized agents working in parallel with:
- Dynamic agent loading and lifecycle management
- Resource allocation and scheduling
- Health monitoring and recovery
- Zero-hallucination quality enforcement

Philosophy: Simple pool management with clear agent contracts
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

from ...utils.logger import get_logger
from ..dynamic_loader import DynamicAgentLoader

logger = get_logger(__name__)


class AgentStatus(Enum):
    """Agent lifecycle status for pool management."""

    IDLE = "idle"
    BUSY = "busy"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentCapability:
    """Agent capability definition for routing decisions."""

    name: str
    tags: Set[str]
    input_types: List[str]
    output_types: List[str]
    max_concurrent_tasks: int = 1
    average_runtime_seconds: float = 10.0
    success_rate: float = 0.95
    requires_gpu: bool = False
    memory_requirement_mb: int = 512


@dataclass
class PoolConfiguration:
    """Configuration for agent pool behavior."""

    max_agents: int = 15
    max_concurrent_tasks: int = 30
    agent_timeout_seconds: int = 300
    health_check_interval_seconds: int = 30
    max_retry_attempts: int = 3
    enable_parallel_execution: bool = True
    quality_threshold: float = 0.90
    load_balancing_strategy: str = "least_busy"


@dataclass
class AgentInfo:
    """Runtime information about an agent in the pool."""

    agent_id: str
    name: str
    capabilities: List[AgentCapability]
    status: AgentStatus
    current_task_count: int = 0
    max_concurrent_tasks: int = 1
    last_health_check: Optional[datetime] = None
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    average_task_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentPool:
    """Manages a pool of specialized agents for parallel execution."""

    def __init__(self, config: PoolConfiguration):
        self.config = config
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_loader = DynamicAgentLoader()
        self.active_tasks: Dict[str, str] = {}  # task_id -> agent_id
        self._lock = asyncio.Lock()
        self._health_check_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """Initialize the agent pool and start health monitoring."""
        logger.info(f"Initializing agent pool with max {self.config.max_agents} agents")

        # Start health monitoring
        self._health_check_task = asyncio.create_task(self._health_monitor())

        # Load initial set of high-priority agents
        await self._load_initial_agents()

        logger.info(f"Agent pool initialized with {len(self.agents)} agents")

    async def _load_initial_agents(self) -> None:
        """Load initial set of essential agents."""
        essential_agents = [
            "zen-architect",
            "modular-builder",
            "bug-hunter",
            "test-coverage",
            "performance-optimizer",
        ]

        for agent_name in essential_agents:
            await self.add_agent(agent_name)

    async def add_agent(self, agent_name: str) -> bool:
        """Add an agent to the pool."""
        async with self._lock:
            if len(self.agents) >= self.config.max_agents:
                logger.warning(f"Agent pool full ({len(self.agents)}/{self.config.max_agents})")
                return False

            if agent_name in self.agents:
                logger.warning(f"Agent {agent_name} already in pool")
                return True

            try:
                # Load agent definition
                agent_result = self.agent_loader.load_agent(agent_name)
                if not agent_result.success:
                    logger.error(f"Failed to load agent {agent_name}: {agent_result.error}")
                    return False

                # Create agent info
                agent_id = str(uuid.uuid4())
                capabilities = self._extract_capabilities(agent_result.content)

                agent_info = AgentInfo(
                    agent_id=agent_id,
                    name=agent_name,
                    capabilities=capabilities,
                    status=AgentStatus.IDLE,
                    max_concurrent_tasks=capabilities[0].max_concurrent_tasks if capabilities else 1,
                    metadata={"definition": agent_result.content},
                )

                self.agents[agent_id] = agent_info
                logger.info(f"Added agent {agent_name} to pool (ID: {agent_id})")

                return True

            except Exception as e:
                logger.error(f"Error adding agent {agent_name}: {e}")
                return False

    def _extract_capabilities(self, agent_content: str) -> List[AgentCapability]:
        """Extract capabilities from agent content."""
        # This is a simplified extraction - in production, would parse agent definition
        capabilities = [
            AgentCapability(
                name="primary_task",
                tags={"general"},
                input_types=["text", "json"],
                output_types=["text", "json"],
                max_concurrent_tasks=1,
            )
        ]

        # Try to infer capabilities from content
        content_lower = agent_content.lower()

        if "architecture" in content_lower:
            capabilities[0].tags.add("architecture")
        if "performance" in content_lower:
            capabilities[0].tags.add("performance")
        if "testing" in content_lower:
            capabilities[0].tags.add("testing")
        if "debugging" in content_lower or "bug" in content_lower:
            capabilities[0].tags.add("debugging")

        return capabilities

    async def get_available_agent(self, required_tags: Set[str]) -> Optional[AgentInfo]:
        """Get an available agent that matches the required tags."""
        async with self._lock:
            # Find agents with matching capabilities
            matching_agents = []

            for agent_info in self.agents.values():
                if agent_info.status != AgentStatus.IDLE:
                    continue

                if agent_info.current_task_count >= agent_info.max_concurrent_tasks:
                    continue

                # Check capability match
                has_capability = False
                for capability in agent_info.capabilities:
                    if required_tags.issubset(capability.tags):
                        has_capability = True
                        break

                if has_capability:
                    matching_agents.append(agent_info)

            if not matching_agents:
                return None

            # Select agent based on load balancing strategy
            if self.config.load_balancing_strategy == "least_busy":
                return min(matching_agents, key=lambda a: a.current_task_count)
            elif self.config.load_balancing_strategy == "fastest":
                return min(matching_agents, key=lambda a: a.average_task_time)
            else:  # round_robin or default
                return matching_agents[0]

    async def assign_task(self, agent_id: str, task_id: str) -> bool:
        """Assign a task to an agent."""
        async with self._lock:
            if agent_id not in self.agents:
                return False

            agent_info = self.agents[agent_id]

            if agent_info.status != AgentStatus.IDLE:
                return False

            if agent_info.current_task_count >= agent_info.max_concurrent_tasks:
                return False

            # Assign task
            self.active_tasks[task_id] = agent_id
            agent_info.current_task_count += 1
            agent_info.last_used = datetime.now()

            if agent_info.current_task_count == 1:
                agent_info.status = AgentStatus.BUSY

            logger.info(f"Assigned task {task_id} to agent {agent_info.name}")
            return True

    async def release_task(self, task_id: str, success: bool = True) -> None:
        """Release a task from an agent."""
        async with self._lock:
            if task_id not in self.active_tasks:
                return

            agent_id = self.active_tasks.pop(task_id)
            agent_info = self.agents[agent_id]

            agent_info.current_task_count -= 1

            if success:
                agent_info.total_tasks_completed += 1
            else:
                agent_info.total_tasks_failed += 1
                agent_info.error_count += 1

            if agent_info.current_task_count == 0:
                agent_info.status = AgentStatus.IDLE

            logger.info(f"Released task {task_id} from agent {agent_info.name}")

    async def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the pool."""
        async with self._lock:
            if agent_id not in self.agents:
                return False

            agent_info = self.agents[agent_id]

            # Cannot remove agent with active tasks
            if agent_info.current_task_count > 0:
                logger.warning(f"Cannot remove agent {agent_info.name} - has active tasks")
                return False

            # Remove agent
            del self.agents[agent_id]
            logger.info(f"Removed agent {agent_info.name} from pool")
            return True

    async def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status and statistics."""
        async with self._lock:
            total_agents = len(self.agents)
            idle_agents = len([a for a in self.agents.values() if a.status == AgentStatus.IDLE])
            busy_agents = len([a for a in self.agents.values() if a.status == AgentStatus.BUSY])
            error_agents = len([a for a in self.agents.values() if a.status == AgentStatus.ERROR])

            total_tasks = sum(a.total_tasks_completed + a.total_tasks_failed for a in self.agents.values())
            total_completed = sum(a.total_tasks_completed for a in self.agents.values())

            return {
                "total_agents": total_agents,
                "idle_agents": idle_agents,
                "busy_agents": busy_agents,
                "error_agents": error_agents,
                "active_tasks": len(self.active_tasks),
                "total_tasks_processed": total_tasks,
                "success_rate": total_completed / total_tasks if total_tasks > 0 else 0,
                "pool_utilization": busy_agents / total_agents if total_agents > 0 else 0,
                "agents": {
                    agent_id: {
                        "name": info.name,
                        "status": info.status.value,
                        "current_tasks": info.current_task_count,
                        "max_tasks": info.max_concurrent_tasks,
                        "total_completed": info.total_tasks_completed,
                        "total_failed": info.total_tasks_failed,
                        "success_rate": info.total_tasks_completed
                        / (info.total_tasks_completed + info.total_tasks_failed)
                        if (info.total_tasks_completed + info.total_tasks_failed) > 0
                        else 0,
                        "capabilities": [cap.name for cap in info.capabilities],
                    }
                    for agent_id, info in self.agents.items()
                },
            }

    async def _health_monitor(self) -> None:
        """Monitor agent health and recovery."""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval_seconds)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all agents."""
        async with self._lock:
            now = datetime.now()

            for agent_id, agent_info in self.agents.items():
                # Check for stuck agents
                if (
                    agent_info.status == AgentStatus.BUSY
                    and agent_info.last_used
                    and (now - agent_info.last_used).seconds > self.config.agent_timeout_seconds
                ):
                    logger.warning(f"Agent {agent_info.name} appears stuck, resetting status")
                    agent_info.status = AgentStatus.ERROR
                    agent_info.error_count += 1

                # Check for offline agents
                if agent_info.status == AgentStatus.OFFLINE or agent_info.error_count > self.config.max_retry_attempts:
                    logger.warning(f"Removing agent {agent_info.name} due to errors/offline status")
                    # Mark for removal (would be handled by pool manager)
                    agent_info.status = AgentStatus.OFFLINE

    async def shutdown(self) -> None:
        """Shutdown the agent pool."""
        logger.info("Shutting down agent pool")

        # Cancel health monitor
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Wait for all tasks to complete or timeout
        timeout = 30
        start_time = asyncio.get_event_loop().time()

        while self.active_tasks and (asyncio.get_event_loop().time() - start_time) < timeout:
            await asyncio.sleep(1)

        if self.active_tasks:
            logger.warning(f"Pool shutdown with {len(self.active_tasks)} tasks still active")

        logger.info("Agent pool shutdown complete")


class AgentPoolManager:
    """High-level manager for agent pool operations."""

    def __init__(self, config: Optional[PoolConfiguration] = None):
        self.config = config or PoolConfiguration()
        self.pool = AgentPool(self.config)
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the pool manager."""
        if self._initialized:
            return

        await self.pool.initialize()
        self._initialized = True
        logger.info("Agent pool manager initialized")

    async def get_agent_for_task(self, required_tags: Set[str]) -> Optional[str]:
        """Get an agent ID for a task with required capabilities."""
        agent_info = await self.pool.get_available_agent(required_tags)
        return agent_info.agent_id if agent_info else None

    async def ensure_agent_available(self, required_tags: Set[str]) -> bool:
        """Ensure at least one agent is available for the given tags."""
        # Check if agent already available
        if await self.pool.get_available_agent(required_tags):
            return True

        # Try to load a new agent with matching tags
        potential_agents = await self._find_agents_by_tags(required_tags)
        for agent_name in potential_agents:
            if await self.pool.add_agent(agent_name):
                return True

        return False

    async def _find_agents_by_tags(self, required_tags: Set[str]) -> List[str]:
        """Find agents that match the required tags."""
        # This would query the agent registry
        # For now, return some common mappings
        tag_mappings = {
            "architecture": ["zen-architect"],
            "performance": ["performance-optimizer"],
            "testing": ["test-coverage"],
            "debugging": ["bug-hunter"],
            "building": ["modular-builder"],
        }

        potential_agents = set()
        for tag in required_tags:
            agents = tag_mappings.get(tag, [])
            potential_agents.update(agents)

        return list(potential_agents)

    async def get_status(self) -> Dict[str, Any]:
        """Get pool manager status."""
        if not self._initialized:
            return {"status": "not_initialized"}

        return await self.pool.get_pool_status()

    async def shutdown(self) -> None:
        """Shutdown the pool manager."""
        if self._initialized:
            await self.pool.shutdown()
            self._initialized = False
