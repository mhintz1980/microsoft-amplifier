"""
Parallel Agent Coordination System

Maximizes 40-70% efficiency gain from simultaneous agent execution through:
- Agent pool management for up to 15 specialized agents
- Intelligent task routing and distribution
- Result aggregation and conflict resolution
- Performance monitoring and optimization
- Load balancing and dependency management
- Zero-hallucination quality control

This system embodies the amplifier philosophy:
- Ruthless simplicity in coordination patterns
- Modular "bricks & studs" design
- Parallel-first execution approach
- Clear contracts between components
"""

from .agent_pool import AgentPool
from .agent_pool import AgentPoolManager
from .agent_pool import AgentStatus
from .agent_pool import PoolConfiguration
from .coordinator import CoordinationRequest
from .coordinator import CoordinationResult
from .coordinator import ParallelAgentCoordinator
from .coordinator import execute_parallel_tasks
from .coordinator import get_parallel_coordinator
from .load_balancer import LoadBalancer
from .load_balancer import TaskDependency
from .load_balancer import TaskPriority
from .performance_monitor import EfficiencyMetrics
from .performance_monitor import PerformanceMonitor
from .performance_monitor import PerformanceOptimizer
from .result_aggregator import AggregatedResult
from .result_aggregator import ConflictResolver
from .result_aggregator import ResultAggregator
from .task_router import TaskRouter
from .task_router import TaskRoutingDecision

__all__ = [
    # Core coordination
    "AgentPool",
    "AgentPoolManager",
    "AgentStatus",
    "PoolConfiguration",
    # Task routing and distribution
    "TaskRouter",
    "TaskRoutingDecision",
    # Result aggregation and conflict resolution
    "ResultAggregator",
    "AggregatedResult",
    "ConflictResolver",
    # Performance monitoring and optimization
    "PerformanceMonitor",
    "PerformanceOptimizer",
    "EfficiencyMetrics",
    # Load balancing and dependency management
    "LoadBalancer",
    "TaskDependency",
    "TaskPriority",
    # Main coordinator
    "ParallelAgentCoordinator",
    "CoordinationRequest",
    "CoordinationResult",
    "get_parallel_coordinator",
    "execute_parallel_tasks",
]
