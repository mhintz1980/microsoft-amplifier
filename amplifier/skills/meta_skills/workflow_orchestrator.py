"""
Workflow Orchestrator

High-performance workflow orchestration system for complex multi-skill workflows.
Provides parallel execution, dynamic scheduling, and real-time monitoring.
"""

import asyncio
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

import networkx as nx

from ...utils.performance_monitor import PerformanceMonitor
from ..skill_base import Skill
from ..skill_base import SkillContext
from ..skill_base import SkillResult
from .skill_integration_patterns_specialist import SkillWorkflow


class ExecutionStatus(Enum):
    """Status of workflow execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskPriority(Enum):
    """Priority levels for workflow tasks."""

    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    BACKGROUND = 4


@dataclass
class WorkflowTask:
    """Represents a task within a workflow."""

    id: str
    skill_id: str
    skill: Skill
    context: SkillContext
    dependencies: list[str] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.MEDIUM
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: SkillResult | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    execution_time: float = 0.0
    retry_count: int = 0
    max_retries: int = 3
    parallel_group: str | None = None
    resource_requirements: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Represents the execution of a workflow."""

    id: str
    workflow: SkillWorkflow
    tasks: dict[str, WorkflowTask]
    execution_graph: nx.DiGraph
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: datetime | None = None
    end_time: datetime | None = None
    total_duration: float = 0.0
    completed_tasks: int = 0
    failed_tasks: int = 0
    context_data: dict[str, Any] = field(default_factory=dict)
    performance_metrics: dict[str, Any] = field(default_factory=dict)


class DynamicScheduler:
    """Dynamic task scheduler for workflow execution."""

    def __init__(self, max_concurrent_tasks: int = 10):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.running_tasks: set[str] = set()
        self.completed_tasks: set[str] = set()
        self.failed_tasks: set[str] = set()
        self.task_queue = asyncio.PriorityQueue()
        self.resource_pool = ResourcePool()

    async def schedule_task(self, task: WorkflowTask) -> None:
        """Schedule a task for execution."""
        if task.id in self.running_tasks or task.id in self.completed_tasks:
            return

        # Check dependencies
        if not self._dependencies_satisfied(task):
            return

        # Check resource availability
        if not self._resources_available(task):
            await self._wait_for_resources(task)
            return

        # Add to execution queue
        await self.task_queue.put((task.priority.value, task))
        self.running_tasks.add(task.id)

    async def get_next_task(self) -> WorkflowTask | None:
        """Get the next task to execute."""
        try:
            priority, task = await asyncio.wait_for(self.task_queue.get(), timeout=0.1)
            return task
        except TimeoutError:
            return None

    def complete_task(self, task_id: str, success: bool = True) -> None:
        """Mark a task as completed."""
        if task_id in self.running_tasks:
            self.running_tasks.remove(task_id)

        if success:
            self.completed_tasks.add(task_id)
        else:
            self.failed_tasks.add(task_id)

        # Release resources
        self.resource_pool.release_task_resources(task_id)

    def _dependencies_satisfied(self, task: WorkflowTask) -> bool:
        """Check if task dependencies are satisfied."""
        return all(dep_id in self.completed_tasks for dep_id in task.dependencies)

    def _resources_available(self, task: WorkflowTask) -> bool:
        """Check if required resources are available."""
        return self.resource_pool.check_availability(task.resource_requirements)

    async def _wait_for_resources(self, task: WorkflowTask) -> None:
        """Wait for required resources to become available."""
        while not self._resources_available(task):
            await asyncio.sleep(0.1)


class ResourcePool:
    """Manages resource allocation for workflow tasks."""

    def __init__(self):
        self.resources = {
            "cpu": {"total": 100, "allocated": 0},
            "memory": {"total": 16384, "allocated": 0},  # MB
            "disk": {"total": 1024000, "allocated": 0},  # MB
            "network": {"total": 1000, "allocated": 0},  # Mbps
            "tokens": {"total": 10000, "allocated": 0},  # Per minute
        }
        self.task_allocations: dict[str, dict[str, float]] = {}

    def check_availability(self, requirements: dict[str, Any]) -> bool:
        """Check if resources are available for given requirements."""
        for resource, amount in requirements.items():
            if resource in self.resources:
                available = self.resources[resource]["total"] - self.resources[resource]["allocated"]
                if available < amount:
                    return False
        return True

    def allocate_resources(self, task_id: str, requirements: dict[str, Any]) -> bool:
        """Allocate resources to a task."""
        if not self.check_availability(requirements):
            return False

        self.task_allocations[task_id] = {}
        for resource, amount in requirements.items():
            if resource in self.resources:
                self.resources[resource]["allocated"] += amount
                self.task_allocations[task_id][resource] = amount

        return True

    def release_task_resources(self, task_id: str) -> None:
        """Release resources allocated to a task."""
        if task_id in self.task_allocations:
            for resource, amount in self.task_allocations[task_id].items():
                if resource in self.resources:
                    self.resources[resource]["allocated"] -= amount
            del self.task_allocations[task_id]


class ParallelExecutor:
    """Executes tasks in parallel with resource management."""

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_futures: dict[str, asyncio.Future] = {}

    async def execute_task(self, task: WorkflowTask) -> SkillResult:
        """Execute a single task."""
        task.status = ExecutionStatus.RUNNING
        task.start_time = datetime.now()

        try:
            # Execute skill in thread pool
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(self.executor, self._execute_skill_sync, task.skill, task.context)

            self.running_futures[task.id] = future
            result = await future
            del self.running_futures[task.id]

            task.end_time = datetime.now()
            task.execution_time = (task.end_time - task.start_time).total_seconds()
            task.result = result

            if result.success:
                task.status = ExecutionStatus.COMPLETED
            else:
                task.status = ExecutionStatus.FAILED

            return result

        except Exception as e:
            task.status = ExecutionStatus.FAILED
            task.end_time = datetime.now()
            task.execution_time = (task.end_time - task.start_time).total_seconds()

            error_result = SkillResult(success=False, message=f"Task execution failed: {str(e)}", error=str(e))
            task.result = error_result
            return error_result

    def _execute_skill_sync(self, skill: Skill, context: SkillContext) -> SkillResult:
        """Execute skill synchronously."""
        try:
            # Run skill initialization if needed
            if hasattr(skill, "initialize") and not getattr(skill, "_initialized", False):
                import asyncio

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(skill.initialize(context))
                    skill._initialized = True
                finally:
                    loop.close()

            # Execute skill
            if asyncio.iscoroutinefunction(skill.execute):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(skill.execute(context))
                finally:
                    loop.close()
            else:
                result = skill.execute(context)

            return result

        except Exception as e:
            return SkillResult(success=False, message=f"Skill execution failed: {str(e)}", error=str(e))

    async def execute_parallel_group(self, tasks: list[WorkflowTask]) -> list[SkillResult]:
        """Execute multiple tasks in parallel."""
        if not tasks:
            return []

        # Limit parallelism to max_workers
        semaphore = asyncio.Semaphore(self.max_workers)

        async def execute_with_semaphore(task):
            async with semaphore:
                return await self.execute_task(task)

        # Execute all tasks concurrently
        results = await asyncio.gather(*[execute_with_semaphore(task) for task in tasks], return_exceptions=True)

        # Convert exceptions to SkillResult objects
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    SkillResult(success=False, message=f"Parallel execution failed: {str(result)}", error=str(result))
                )
            else:
                processed_results.append(result)

        return processed_results

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id in self.running_futures:
            future = self.running_futures[task_id]
            future.cancel()
            return True
        return False

    def shutdown(self) -> None:
        """Shutdown the executor."""
        self.executor.shutdown(wait=True)


class WorkflowOrchestrator:
    """
    High-performance workflow orchestrator for complex multi-skill workflows.

    Features:
    - Dynamic task scheduling
    - Parallel execution with resource management
    - Real-time monitoring and adaptation
    - Automatic error recovery
    - Performance optimization
    """

    def __init__(self, max_concurrent_tasks: int = 10, max_workers: int = 5):
        self.scheduler = DynamicScheduler(max_concurrent_tasks)
        self.executor = ParallelExecutor(max_workers)
        self.resource_pool = ResourcePool()
        self.performance_monitor = PerformanceMonitor()
        self.active_executions: dict[str, WorkflowExecution] = {}
        self.execution_history: list[WorkflowExecution] = []
        self.logger = logging.getLogger(__name__)

    async def execute_workflow(self, workflow: SkillWorkflow, context: SkillContext) -> WorkflowExecution:
        """Execute a complete workflow."""
        execution_id = str(uuid.uuid4())

        # Create workflow execution
        execution = await self._create_workflow_execution(execution_id, workflow, context)
        self.active_executions[execution_id] = execution

        try:
            # Start execution
            execution.status = ExecutionStatus.RUNNING
            execution.start_time = datetime.now()

            # Execute workflow
            await self._execute_workflow_tasks(execution)

            # Complete execution
            execution.status = ExecutionStatus.COMPLETED
            execution.end_time = datetime.now()
            execution.total_duration = (execution.end_time - execution.start_time).total_seconds()

        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.end_time = datetime.now()
            execution.total_duration = (execution.end_time - execution.start_time).total_seconds()
            self.logger.error(f"Workflow execution failed: {str(e)}")

        finally:
            # Move to history
            self.execution_history.append(execution)
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]

        return execution

    async def _create_workflow_execution(
        self, execution_id: str, workflow: SkillWorkflow, context: SkillContext
    ) -> WorkflowExecution:
        """Create a workflow execution object."""
        tasks = {}

        # Create tasks from workflow execution graph
        for node in workflow.execution_graph.nodes():
            task_id = f"{execution_id}_{node}"

            # Get skill for this node
            skill = workflow.skills.get(node)
            if not skill:
                continue

            # Create task context
            task_context = SkillContext(
                session_id=context.session_id,
                user_id=context.user_id,
                parameters=context.parameters.copy(),
                skill_registry=context.skill_registry,
                storage_manager=context.storage_manager,
                performance_monitor=context.performance_monitor,
            )

            # Get dependencies
            dependencies = list(workflow.execution_graph.predecessors(node))

            # Create task
            task = WorkflowTask(
                id=task_id,
                skill_id=node,
                skill=skill,
                context=task_context,
                dependencies=[f"{execution_id}_{dep}" for dep in dependencies],
                priority=self._calculate_task_priority(workflow, node),
                resource_requirements=self._estimate_resource_requirements(skill),
            )

            tasks[task_id] = task

        return WorkflowExecution(
            id=execution_id, workflow=workflow, tasks=tasks, execution_graph=workflow.execution_graph.copy()
        )

    async def _execute_workflow_tasks(self, execution: WorkflowExecution) -> None:
        """Execute all tasks in the workflow."""
        # Build execution schedule
        execution_groups = self._build_execution_groups(execution)

        # Execute groups in order
        for group in execution_groups:
            if group["type"] == "parallel":
                # Execute parallel group
                tasks = [execution.tasks[task_id] for task_id in group["tasks"]]
                results = await self.executor.execute_parallel_group(tasks)

                # Update tasks with results
                for i, task_id in enumerate(group["tasks"]):
                    task = execution.tasks[task_id]
                    task.result = results[i]

                    if results[i].success:
                        execution.completed_tasks += 1
                    else:
                        execution.failed_tasks += 1

            else:  # sequential
                # Execute tasks sequentially
                for task_id in group["tasks"]:
                    task = execution.tasks[task_id]
                    result = await self.executor.execute_task(task)

                    if result.success:
                        execution.completed_tasks += 1
                    else:
                        execution.failed_tasks += 1
                        # Check if we should continue on failure
                        if not self._should_continue_on_failure(task, result):
                            raise Exception(f"Critical task failed: {task.skill_id}")

    def _build_execution_groups(self, execution: WorkflowExecution) -> list[dict[str, Any]]:
        """Build execution groups from workflow graph."""
        groups = []
        processed_tasks = set()
        remaining_tasks = set(execution.tasks.keys())

        while remaining_tasks:
            # Find tasks that can be executed now (all dependencies satisfied)
            ready_tasks = []
            for task_id in remaining_tasks:
                task = execution.tasks[task_id]
                if all(dep in processed_tasks for dep in task.dependencies):
                    ready_tasks.append(task_id)

            if not ready_tasks:
                # Circular dependency or missing dependencies
                raise Exception("Cannot resolve task dependencies")

            # Determine if tasks can be executed in parallel
            if len(ready_tasks) == 1:
                # Single task - sequential execution
                groups.append({"type": "sequential", "tasks": ready_tasks})
            else:
                # Multiple tasks - check if they can be parallelized
                if self._can_execute_parallel(ready_tasks, execution):
                    groups.append({"type": "parallel", "tasks": ready_tasks})
                else:
                    # Execute sequentially
                    for task_id in ready_tasks:
                        groups.append({"type": "sequential", "tasks": [task_id]})

            # Mark tasks as processed
            for task_id in ready_tasks:
                processed_tasks.add(task_id)
                remaining_tasks.remove(task_id)

        return groups

    def _can_execute_parallel(self, task_ids: list[str], execution: WorkflowExecution) -> bool:
        """Check if tasks can be executed in parallel."""
        # Check resource constraints
        total_requirements = {"cpu": 0, "memory": 0, "tokens": 0}

        for task_id in task_ids:
            task = execution.tasks[task_id]
            for resource, amount in task.resource_requirements.items():
                if resource in total_requirements:
                    total_requirements[resource] += amount

        # Check if total requirements are within limits
        return self.resource_pool.check_availability(total_requirements)

    def _calculate_task_priority(self, workflow: SkillWorkflow, node: str) -> TaskPriority:
        """Calculate task priority based on workflow structure."""
        # Critical path analysis
        try:
            # Find longest path from this node to an exit node
            successors = list(nx.descendants(workflow.execution_graph, node))
            if not successors:
                return TaskPriority.CRITICAL  # Exit node

            # More successors = higher priority (affects more tasks)
            if len(successors) > 3:
                return TaskPriority.HIGH
            if len(successors) > 1:
                return TaskPriority.MEDIUM
            return TaskPriority.LOW

        except Exception:
            return TaskPriority.MEDIUM

    def _estimate_resource_requirements(self, skill: Skill) -> dict[str, Any]:
        """Estimate resource requirements for a skill."""
        # Default estimates based on skill metadata
        requirements = {
            "cpu": 10,  # 10% CPU
            "memory": 512,  # 512 MB RAM
            "tokens": 100,  # 100 tokens per minute
        }

        # Adjust based on skill cost estimate
        if hasattr(skill, "cost_estimate"):
            cost = skill.cost_estimate
            if isinstance(cost, dict):
                requirements["tokens"] = cost.get("tokens", 100)
                # Adjust other resources based on token cost
                requirements["cpu"] = min(50, max(5, requirements["tokens"] // 20))
                requirements["memory"] = min(4096, max(256, requirements["tokens"] * 5))

        return requirements

    def _should_continue_on_failure(self, task: WorkflowTask, result: SkillResult) -> bool:
        """Determine if workflow should continue after task failure."""
        # Check if task is marked as critical
        if task.priority == TaskPriority.CRITICAL:
            return False

        # Check retry count
        if task.retry_count < task.max_retries:
            return True

        # Check error type
        if result.error and "critical" in result.error.lower():
            return False

        return True

    async def get_execution_status(self, execution_id: str) -> WorkflowExecution | None:
        """Get the status of a workflow execution."""
        return self.active_executions.get(execution_id)

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running workflow execution."""
        execution = self.active_executions.get(execution_id)
        if not execution or execution.status != ExecutionStatus.RUNNING:
            return False

        # Cancel all running tasks
        for task in execution.tasks.values():
            if task.status == ExecutionStatus.RUNNING:
                self.executor.cancel_task(task.id)
                task.status = ExecutionStatus.CANCELLED

        execution.status = ExecutionStatus.CANCELLED
        return True

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics for the orchestrator."""
        return {
            "active_executions": len(self.active_executions),
            "completed_executions": len(self.execution_history),
            "total_tasks_executed": sum(len(exec.tasks) for exec in self.execution_history),
            "average_execution_time": sum(exec.total_duration for exec in self.execution_history)
            / max(1, len(self.execution_history)),
            "success_rate": sum(1 for exec in self.execution_history if exec.status == ExecutionStatus.COMPLETED)
            / max(1, len(self.execution_history)),
            "resource_utilization": {
                resource: {
                    "total": pool["total"],
                    "allocated": pool["allocated"],
                    "utilization": pool["allocated"] / pool["total"],
                }
                for resource, pool in self.resource_pool.resources.items()
            },
        }

    def shutdown(self) -> None:
        """Shutdown the orchestrator."""
        self.executor.shutdown()


# Export the orchestrator
__all__ = ["WorkflowOrchestrator", "WorkflowExecution", "WorkflowTask", "ExecutionStatus", "TaskPriority"]
