"""
Load Balancer and Dependency Manager

Distributes workload evenly and manages skill dependencies with:
- Intelligent load balancing algorithms
- Task dependency resolution and optimization
- Compound effect optimization
- Resource allocation and scheduling
- Deadlock prevention and resolution

Philosophy: Smart workload distribution that maximizes throughput while respecting dependencies
"""

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum

from ...utils.logger import get_logger

logger = get_logger(__name__)


class TaskPriority(Enum):
    """Priority levels for task scheduling."""

    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    CAPABILITY_BASED = "capability_based"
    PERFORMANCE_BASED = "performance_based"
    ADAPTIVE = "adaptive"


class DependencyType(Enum):
    """Types of task dependencies."""

    SEQUENTIAL = "sequential"  # Task B must complete before Task A starts
    PARALLEL = "parallel"  # Tasks can run in parallel
    MUTEX = "mutex"  # Tasks cannot run simultaneously
    RESOURCE = "resource"  # Tasks compete for same resource
    DATA = "data"  # Task B needs data from Task A


@dataclass
class TaskDependency:
    """Defines a dependency between tasks."""

    task_id: str
    depends_on: str
    dependency_type: DependencyType
    strength: float = 1.0  # 0.0-1.0, how strong the dependency is
    metadata: dict[str, any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TaskNode:
    """Node in task dependency graph."""

    task_id: str
    priority: TaskPriority
    estimated_duration: float
    required_capabilities: set[str]
    resource_requirements: dict[str, float]
    dependencies: list[TaskDependency]
    dependents: list[str]  # Tasks that depend on this one
    status: str = "pending"  # pending, ready, running, completed, failed
    assigned_agent_id: str | None = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentLoadInfo:
    """Current load information for an agent."""

    agent_id: str
    current_tasks: int
    max_concurrent_tasks: int
    utilization_rate: float
    average_task_time: float
    success_rate: float
    capability_scores: dict[str, float]  # capability -> score
    last_task_completed: datetime | None = None
    total_tasks_completed: int = 0
    weighted_load: float = 0.0  # Load considering task complexity


@dataclass
class LoadBalancingDecision:
    """Decision made by load balancer."""

    task_id: str
    selected_agent_id: str
    strategy_used: LoadBalancingStrategy
    reasoning: str
    expected_completion_time: float
    load_distribution_score: float
    alternative_agents: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class DependencyManager:
    """Manages task dependencies and optimization."""

    def __init__(self):
        self.tasks: dict[str, TaskNode] = {}
        self.dependencies: list[TaskDependency] = []
        self.execution_graph: dict[str, set[str]] = defaultdict(set)  # task_id -> dependencies
        self.reverse_graph: dict[str, set[str]] = defaultdict(set)  # task_id -> dependents
        self._lock = asyncio.Lock()

    async def add_task(self, task: TaskNode) -> None:
        """Add a task to the dependency manager."""
        async with self._lock:
            self.tasks[task.task_id] = task

            # Update graph structures
            for dep in task.dependencies:
                self.dependencies.append(dep)
                self.execution_graph[task.task_id].add(dep.depends_on)
                self.reverse_graph[dep.depends_on].add(task.task_id)

        logger.debug(f"Added task {task.task_id} with {len(task.dependencies)} dependencies")

    async def get_ready_tasks(self) -> list[TaskNode]:
        """Get tasks that are ready to execute (dependencies satisfied)."""
        async with self._lock:
            ready_tasks = []

            for task_id, task in self.tasks.items():
                if task.status == "pending" and await self._dependencies_satisfied(task_id):
                    ready_tasks.append(task)

            # Sort by priority and duration
            ready_tasks.sort(key=lambda t: (t.priority.value, t.estimated_duration))
            return ready_tasks

    async def _dependencies_satisfied(self, task_id: str) -> bool:
        """Check if all dependencies for a task are satisfied."""
        dependencies = self.execution_graph.get(task_id, set())

        for dep_task_id in dependencies:
            dep_task = self.tasks.get(dep_task_id)
            if not dep_task or dep_task.status != "completed":
                return False

        return True

    async def mark_task_completed(self, task_id: str) -> list[str]:
        """Mark a task as completed and return newly ready tasks."""
        async with self._lock:
            if task_id not in self.tasks:
                return []

            self.tasks[task_id].status = "completed"

            # Check which dependents are now ready
            newly_ready = []
            for dependent_id in self.reverse_graph.get(task_id, set()):
                if self.tasks[dependent_id].status == "pending" and await self._dependencies_satisfied(dependent_id):
                    self.tasks[dependent_id].status = "ready"
                    newly_ready.append(dependent_id)

            return newly_ready

    async def detect_deadlocks(self) -> list[list[str]]:
        """Detect circular dependencies that would cause deadlocks."""
        async with self._lock:
            # Use DFS to detect cycles
            visited = set()
            rec_stack = set()
            cycles = []

            def dfs(node: str, path: list[str]) -> bool:
                if node in rec_stack:
                    # Found cycle
                    cycle_start = path.index(node)
                    cycles.append(path[cycle_start:] + [node])
                    return True

                if node in visited:
                    return False

                visited.add(node)
                rec_stack.add(node)

                for neighbor in self.execution_graph.get(node, set()):
                    if dfs(neighbor, path + [node]):
                        return True

                rec_stack.remove(node)
                return False

            for task_id in self.tasks:
                if task_id not in visited:
                    dfs(task_id, [])

            return cycles

    async def optimize_dependency_order(self) -> list[str]:
        """Optimize task execution order for maximum parallelism."""
        async with self._lock:
            # Topological sort with level assignment
            levels = {}
            in_degree = defaultdict(int)

            # Calculate in-degrees
            for task_id in self.tasks:
                in_degree[task_id] = len(self.execution_graph.get(task_id, set()))
                if in_degree[task_id] == 0:
                    levels[task_id] = 0

            # Process tasks level by level
            queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
            execution_order = []

            while queue:
                current_level = queue.copy()
                queue = []

                for task_id in current_level:
                    execution_order.append(task_id)

                    # Update dependents
                    for dependent in self.reverse_graph.get(task_id, set()):
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            levels[dependent] = levels.get(task_id, 0) + 1
                            queue.append(dependent)

            return execution_order

    async def get_dependency_statistics(self) -> dict[str, any]:
        """Get statistics about task dependencies."""
        async with self._lock:
            total_tasks = len(self.tasks)
            total_dependencies = len(self.dependencies)

            if total_tasks == 0:
                return {"total_tasks": 0}

            # Calculate dependency depth
            max_depth = 0
            total_depth = 0
            task_count = 0

            for task_id, task in self.tasks.items():
                depth = await self._calculate_dependency_depth(task_id)
                max_depth = max(max_depth, depth)
                total_depth += depth
                task_count += 1

            avg_depth = total_depth / task_count if task_count > 0 else 0

            # Check for cycles
            cycles = await self.detect_deadlocks()

            return {
                "total_tasks": total_tasks,
                "total_dependencies": total_dependencies,
                "avg_dependencies_per_task": total_dependencies / total_tasks if total_tasks > 0 else 0,
                "max_dependency_depth": max_depth,
                "avg_dependency_depth": avg_depth,
                "cycles_detected": len(cycles),
                "tasks_by_status": {
                    status: len([t for t in self.tasks.values() if t.status == status])
                    for status in set(t.status for t in self.tasks.values())
                },
            }

    async def _calculate_dependency_depth(self, task_id: str, visited: set[str] = None) -> int:
        """Calculate maximum dependency depth for a task."""
        if visited is None:
            visited = set()

        if task_id in visited:
            return 0  # Cycle detected

        visited.add(task_id)

        dependencies = self.execution_graph.get(task_id, set())
        if not dependencies:
            return 0

        max_depth = 0
        for dep_id in dependencies:
            depth = await self._calculate_dependency_depth(dep_id, visited.copy())
            max_depth = max(max_depth, depth + 1)

        return max_depth


class LoadBalancer:
    """Distributes workload across available agents."""

    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ADAPTIVE):
        self.strategy = strategy
        self.agent_loads: dict[str, AgentLoadInfo] = {}
        self.round_robin_index = 0
        self.decision_history: list[LoadBalancingDecision] = []
        self.performance_history: dict[str, list[float]] = defaultdict(list)  # agent_id -> performance scores
        self._lock = asyncio.Lock()

    async def update_agent_load(self, agent_id: str, load_info: AgentLoadInfo) -> None:
        """Update load information for an agent."""
        async with self._lock:
            self.agent_loads[agent_id] = load_info

            # Update performance history
            self.performance_history[agent_id].append(load_info.success_rate)
            if len(self.performance_history[agent_id]) > 100:
                self.performance_history[agent_id] = self.performance_history[agent_id][-50:]

    async def select_agent(self, task: TaskNode, available_agents: list[str]) -> LoadBalancingDecision:
        """Select the best agent for a task using the configured strategy."""
        if not available_agents:
            return LoadBalancingDecision(
                task_id=task.task_id,
                selected_agent_id="",
                strategy_used=self.strategy,
                reasoning="No available agents",
                expected_completion_time=0.0,
                load_distribution_score=0.0,
            )

        # Apply load balancing strategy
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            agent_id = await self._round_robin_select(available_agents)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            agent_id = await self._least_connections_select(available_agents)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            agent_id = await self._weighted_round_robin_select(available_agents)
        elif self.strategy == LoadBalancingStrategy.CAPABILITY_BASED:
            agent_id = await self._capability_based_select(task, available_agents)
        elif self.strategy == LoadBalancingStrategy.PERFORMANCE_BASED:
            agent_id = await self._performance_based_select(available_agents)
        else:  # ADAPTIVE
            agent_id = await self._adaptive_select(task, available_agents)

        # Create decision
        decision = await self._create_decision(task, agent_id, available_agents)

        # Record decision
        async with self._lock:
            self.decision_history.append(decision)
            if len(self.decision_history) > 1000:
                self.decision_history = self.decision_history[-500:]

        return decision

    async def _round_robin_select(self, available_agents: list[str]) -> str:
        """Round-robin agent selection."""
        async with self._lock:
            agent_id = available_agents[self.round_robin_index % len(available_agents)]
            self.round_robin_index += 1
            return agent_id

    async def _least_connections_select(self, available_agents: list[str]) -> str:
        """Select agent with least current connections."""
        best_agent = None
        min_load = float("inf")

        for agent_id in available_agents:
            load_info = self.agent_loads.get(agent_id)
            if load_info:
                current_load = load_info.current_tasks
                if current_load < min_load:
                    min_load = current_load
                    best_agent = agent_id

        return best_agent or available_agents[0]

    async def _weighted_round_robin_select(self, available_agents: list[str]) -> str:
        """Weighted round-robin based on agent performance."""
        weights = []
        for agent_id in available_agents:
            load_info = self.agent_loads.get(agent_id)
            if load_info:
                # Weight by success rate and capacity
                weight = load_info.success_rate * (1 - load_info.utilization_rate)
            else:
                weight = 1.0
            weights.append(weight)

        # Select based on weights
        total_weight = sum(weights)
        if total_weight == 0:
            return available_agents[0]

        import random

        r = random.uniform(0, total_weight)
        cum_weight = 0

        for i, weight in enumerate(weights):
            cum_weight += weight
            if r <= cum_weight:
                return available_agents[i]

        return available_agents[-1]

    async def _capability_based_select(self, task: TaskNode, available_agents: list[str]) -> str:
        """Select agent based on capability matching."""
        best_agent = None
        best_score = -1.0

        for agent_id in available_agents:
            load_info = self.agent_loads.get(agent_id)
            if not load_info:
                continue

            # Calculate capability match score
            matching_capabilities = task.required_capabilities.intersection(set(load_info.capability_scores.keys()))

            if not matching_capabilities:
                continue

            # Calculate weighted score
            capability_score = sum(load_info.capability_scores[cap] for cap in matching_capabilities) / len(
                matching_capabilities
            )
            load_factor = 1.0 - load_info.utilization_rate

            total_score = capability_score * 0.7 + load_factor * 0.3

            if total_score > best_score:
                best_score = total_score
                best_agent = agent_id

        return best_agent or available_agents[0]

    async def _performance_based_select(self, available_agents: list[str]) -> str:
        """Select agent based on historical performance."""
        best_agent = None
        best_performance = 0.0

        for agent_id in available_agents:
            performances = self.performance_history.get(agent_id, [])
            if not performances:
                continue

            # Use recent performance average
            recent_performance = sum(performures[-10:]) / min(len(performances), 10)

            load_info = self.agent_loads.get(agent_id)
            if load_info:
                # Factor in current load
                adjusted_performance = recent_performance * (1 - load_info.utilization_rate * 0.5)
            else:
                adjusted_performance = recent_performance

            if adjusted_performance > best_performance:
                best_performance = adjusted_performance
                best_agent = agent_id

        return best_agent or available_agents[0]

    async def _adaptive_select(self, task: TaskNode, available_agents: list[str]) -> str:
        """Adaptive selection combining multiple strategies."""
        # Get recommendations from different strategies
        strategies = [
            await self._least_connections_select(available_agents),
            await self._capability_based_select(task, available_agents),
            await self._performance_based_select(available_agents),
        ]

        # Count votes
        vote_counts = defaultdict(int)
        for agent_id in strategies:
            vote_counts[agent_id] += 1

        # Select agent with most votes, break ties with capability match
        max_votes = max(vote_counts.values())
        top_candidates = [agent_id for agent_id, votes in vote_counts.items() if votes == max_votes]

        if len(top_candidates) == 1:
            return top_candidates[0]
        # Tie-breaker: capability match
        return await self._capability_based_select(task, top_candidates)

    async def _create_decision(
        self, task: TaskNode, selected_agent_id: str, available_agents: list[str]
    ) -> LoadBalancingDecision:
        """Create a load balancing decision record."""
        load_info = self.agent_loads.get(selected_agent_id)

        if load_info:
            expected_completion = task.estimated_duration / (1 - load_info.utilization_rate + 0.1)
            load_score = 1.0 - load_info.utilization_rate
            reasoning = (
                f"Selected {selected_agent_id} with {load_info.current_tasks}/{load_info.max_concurrent_tasks} tasks"
            )
        else:
            expected_completion = task.estimated_duration
            load_score = 0.5
            reasoning = f"Selected {selected_agent_id} (no load info available)"

        # Get alternative agents
        alternatives = [agent_id for agent_id in available_agents if agent_id != selected_agent_id][:3]

        return LoadBalancingDecision(
            task_id=task.task_id,
            selected_agent_id=selected_agent_id,
            strategy_used=self.strategy,
            reasoning=reasoning,
            expected_completion_time=expected_completion,
            load_distribution_score=load_score,
            alternative_agents=alternatives,
        )

    async def get_load_statistics(self) -> dict[str, any]:
        """Get load balancing statistics."""
        async with self._lock:
            total_agents = len(self.agent_loads)
            if total_agents == 0:
                return {"total_agents": 0}

            total_tasks = sum(info.current_tasks for info in self.agent_loads.values())
            total_capacity = sum(info.max_concurrent_tasks for info in self.agent_loads.values())
            avg_utilization = sum(info.utilization_rate for info in self.agent_loads.values()) / total_agents
            avg_success_rate = sum(info.success_rate for info in self.agent_loads.values()) / total_agents

            return {
                "total_agents": total_agents,
                "total_active_tasks": total_tasks,
                "total_capacity": total_capacity,
                "overall_utilization": total_tasks / total_capacity if total_capacity > 0 else 0,
                "avg_agent_utilization": avg_utilization,
                "avg_success_rate": avg_success_rate,
                "load_balancing_strategy": self.strategy.value,
                "total_decisions": len(self.decision_history),
                "recent_decisions": len(
                    [d for d in self.decision_history if (datetime.now() - d.created_at).seconds < 3600]
                ),
            }

    async def optimize_strategy(self) -> LoadBalancingStrategy:
        """Optimize load balancing strategy based on performance."""
        if len(self.decision_history) < 50:
            return self.strategy

        # Analyze recent decision performance
        recent_decisions = self.decision_history[-50:]
        avg_load_score = sum(d.load_distribution_score for d in recent_decisions) / len(recent_decisions)

        # Strategy recommendations based on performance
        if avg_load_score < 0.6:
            # Poor load distribution, try different strategy
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return LoadBalancingStrategy.LEAST_CONNECTIONS
            if self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return LoadBalancingStrategy.ADAPTIVE
            return LoadBalancingStrategy.ADAPTIVE

        return self.strategy
