"""
Meta-Skill Coordination System

Coordinates compound effects across multiple skills with optimized
resource allocation and execution orchestration.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Any

from ..signature_framework import ExecutionContext
from ..signature_framework import SignatureSkill
from ..signature_framework import SkillResult
from .resource_optimizer import get_resource_optimizer


@dataclass
class SkillDependency:
    """Represents a dependency between skills"""

    skill_id: str
    depends_on: str
    dependency_type: str = "sequential"  # sequential, parallel, conditional


@dataclass
class SkillPlan:
    """Execution plan for multiple skills"""

    skills: list[SignatureSkill]
    dependencies: list[SkillDependency]
    execution_order: list[str]
    parallel_groups: list[list[str]]
    estimated_duration: float
    resource_requirements: dict[str, float]


@dataclass
class CoordinationStats:
    """Statistics for meta-skill coordination"""

    total_plans: int = 0
    skills_executed: int = 0
    parallel_executions: int = 0
    average_speedup: float = 0.0
    resource_efficiency: float = 0.0


class MetaSkillCoordinator:
    """Coordinates execution of multiple skills with optimization"""

    def __init__(self):
        self._resource_optimizer = get_resource_optimizer()
        self._skill_registry: dict[str, SignatureSkill] = {}
        self._execution_history: list[dict] = []
        self._stats = CoordinationStats()

    def register_skill(self, skill_id: str, skill: SignatureSkill):
        """Register a skill for coordination"""
        self._skill_registry[skill_id] = skill

    def create_execution_plan(
        self, skill_ids: list[str], dependencies: list[SkillDependency] | None = None
    ) -> SkillPlan:
        """Create optimized execution plan for multiple skills"""
        # Validate skills exist
        skills = []
        for skill_id in skill_ids:
            if skill_id not in self._skill_registry:
                raise ValueError(f"Skill {skill_id} not registered")
            skills.append(self._skill_registry[skill_id])

        dependencies = dependencies or []

        # Determine execution order
        execution_order = self._resolve_dependencies(skill_ids, dependencies)

        # Group parallel skills
        parallel_groups = self._identify_parallel_groups(execution_order, dependencies)

        # Estimate duration and resources
        estimated_duration = self._estimate_duration(skills, parallel_groups)
        resource_requirements = self._estimate_resources(skills)

        plan = SkillPlan(
            skills=skills,
            dependencies=dependencies,
            execution_order=execution_order,
            parallel_groups=parallel_groups,
            estimated_duration=estimated_duration,
            resource_requirements=resource_requirements,
        )

        self._stats.total_plans += 1
        return plan

    def _resolve_dependencies(self, skill_ids: list[str], dependencies: list[SkillDependency]) -> list[str]:
        """Resolve skill dependencies to determine execution order"""
        # Simple topological sort
        visited = set()
        temp_visited = set()
        result = []

        def visit(skill_id: str):
            if skill_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving {skill_id}")
            if skill_id in visited:
                return

            temp_visited.add(skill_id)

            # Visit dependencies first
            for dep in dependencies:
                if dep.skill_id == skill_id:
                    visit(dep.depends_on)

            temp_visited.remove(skill_id)
            visited.add(skill_id)
            result.append(skill_id)

        for skill_id in skill_ids:
            if skill_id not in visited:
                visit(skill_id)

        return result

    def _identify_parallel_groups(
        self, execution_order: list[str], dependencies: list[SkillDependency]
    ) -> list[list[str]]:
        """Identify groups of skills that can be executed in parallel"""
        groups = []
        remaining = execution_order.copy()

        while remaining:
            # Find skills that can be executed next
            ready = []
            for skill_id in remaining:
                # Check if all dependencies are satisfied
                deps_satisfied = True
                for dep in dependencies:
                    if dep.skill_id == skill_id and dep.depends_on in remaining:
                        deps_satisfied = False
                        break

                if deps_satisfied:
                    ready.append(skill_id)

            # Add ready skills as a parallel group
            if ready:
                groups.append(ready)
                for skill_id in ready:
                    remaining.remove(skill_id)
            else:
                # Fallback - add single skill
                groups.append([remaining[0]])
                remaining.pop(0)

        return groups

    def _estimate_duration(self, skills: list[SignatureSkill], parallel_groups: list[list[str]]) -> float:
        """Estimate total execution duration"""
        # Simplified estimation - would use historical data in real implementation
        sequential_time = len(skills) * 0.1  # Assume 100ms per skill
        parallel_reduction = len(parallel_groups) * 0.05  # 50ms savings per parallel group
        return max(0.1, sequential_time - parallel_reduction)

    def _estimate_resources(self, skills: list[SignatureSkill]) -> dict[str, float]:
        """Estimate resource requirements"""
        return {
            "memory_mb": len(skills) * 10,  # 10MB per skill
            "cpu_cores": min(len(skills), 4),  # Up to 4 cores
            "io_bandwidth": len(skills) * 1.0,  # 1MB/s per skill
        }

    async def execute_plan(self, plan: SkillPlan, input_data: Any, context: ExecutionContext) -> dict[str, SkillResult]:
        """Execute a skill plan with optimization"""
        start_time = time.time()
        results = {}
        context_updates = {}

        # Execute parallel groups
        for group in plan.parallel_groups:
            if len(group) == 1:
                # Sequential execution
                skill_id = group[0]
                skill = self._skill_registry[skill_id]

                # Prepare input with context updates
                skill_input = self._prepare_input(input_data, context_updates, skill_id)
                result = await self._execute_optimized_skill(skill, skill_input, context)
                results[skill_id] = result
                context_updates[skill_id] = result.data

            else:
                # Parallel execution
                tasks = []
                for skill_id in group:
                    skill = self._skill_registry[skill_id]
                    skill_input = self._prepare_input(input_data, context_updates, skill_id)
                    task = self._execute_optimized_skill(skill, skill_input, context)
                    tasks.append((skill_id, task))

                # Wait for all tasks in group
                group_results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

                for i, (skill_id, _) in enumerate(tasks):
                    if not isinstance(group_results[i], Exception):
                        results[skill_id] = group_results[i]
                        context_updates[skill_id] = group_results[i].data
                    else:
                        # Handle execution failure
                        error_result = SkillResult(success=False, data={}, error=str(group_results[i]), confidence=0.0)
                        results[skill_id] = error_result

        # Update statistics
        execution_time = time.time() - start_time
        self._stats.skills_executed += len(plan.skills)
        self._stats.parallel_executions += len(plan.parallel_groups)

        # Calculate speedup (simplified)
        sequential_time = len(plan.skills) * 0.1
        self._stats.average_speedup = sequential_time / execution_time

        return results

    def _prepare_input(self, base_input: Any, context_updates: dict[str, Any], skill_id: str) -> Any:
        """Prepare input for skill with context from previous executions"""
        # Simplified input preparation
        if context_updates:
            return {"original_input": base_input, "context": context_updates}
        return base_input

    async def _execute_optimized_skill(
        self, skill: SignatureSkill, input_data: Any, context: ExecutionContext
    ) -> SkillResult:
        """Execute a skill with resource optimization"""
        return await self._resource_optimizer.execute_skill(skill, input_data, context)

    def get_stats(self) -> CoordinationStats:
        """Get coordination statistics"""
        return CoordinationStats(
            total_plans=self._stats.total_plans,
            skills_executed=self._stats.skills_executed,
            parallel_executions=self._stats.parallel_executions,
            average_speedup=self._stats.average_speedup,
            resource_efficiency=0.8,  # Simplified
        )


# Global meta-skill coordinator instance
_global_coordinator: MetaSkillCoordinator | None = None


def get_meta_skill_coordinator() -> MetaSkillCoordinator:
    """Get or create the global meta-skill coordinator"""
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = MetaSkillCoordinator()
    return _global_coordinator
