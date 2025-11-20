"""
Resource Optimization Integration

Coordinates all resource optimization components for seamless integration
with the signature framework and skill execution system.
"""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from ..jit_compiler import get_jit_compiler
from ..resource_optimization import get_arena_allocator
from ..resource_optimization import get_garbage_collector
from ..resource_optimization import get_memory_monitor
from ..resource_optimization import get_memory_pool
from ..scheduler import get_work_stealing_scheduler
from ..signature_framework import ExecutionContext
from ..signature_framework import SignatureSkill
from ..signature_framework import SkillResult


@dataclass
class ResourceOptimizationConfig:
    """Configuration for resource optimization integration"""

    enable_arena_allocator: bool = True
    enable_memory_pool: bool = True
    enable_garbage_collector: bool = True
    enable_memory_monitor: bool = True
    enable_work_stealing: bool = True
    enable_jit_optimization: bool = True

    # Performance targets
    memory_reduction_target: float = 0.85  # 85% reduction
    throughput_target: float = 100000  # 100K tasks/sec
    speedup_target: float = 50.0  # 50x speedup

    # Auto-tuning
    enable_auto_tuning: bool = True
    tuning_interval: float = 30.0


@dataclass
class OptimizationStats:
    """Statistics for resource optimization"""

    memory_reduction_ratio: float = 0.0
    throughput_tasks_per_sec: float = 0.0
    average_speedup: float = 0.0
    total_optimizations: int = 0
    active_optimizations: list[str] = field(default_factory=list)


class ResourceOptimizer:
    """Coordinates all resource optimization components"""

    def __init__(self, config: ResourceOptimizationConfig | None = None):
        self.config = config or ResourceOptimizationConfig()

        # Component references
        self._arena_allocator = None
        self._memory_pool = None
        self._garbage_collector = None
        self._memory_monitor = None
        self._scheduler = None
        self._jit_compiler = None

        # Optimization state
        self._initialized = False
        self._active = False

        # Statistics
        self._stats = OptimizationStats()

    async def initialize(self):
        """Initialize all resource optimization components"""
        if self._initialized:
            return

        # Initialize components based on configuration
        if self.config.enable_arena_allocator:
            self._arena_allocator = get_arena_allocator()

        if self.config.enable_memory_pool:
            self._memory_pool = get_memory_pool()

        if self.config.enable_garbage_collector:
            self._garbage_collector = get_garbage_collector()

        if self.config.enable_memory_monitor:
            self._memory_monitor = get_memory_monitor()

        if self.config.enable_work_stealing:
            self._scheduler = get_work_stealing_scheduler()
            await self._scheduler.start()

        if self.config.enable_jit_optimization:
            self._jit_compiler = get_jit_compiler()

        self._initialized = True
        print("Resource optimizer initialized")

    async def start(self):
        """Start all resource optimization services"""
        if not self._initialized:
            await self.initialize()

        if self._active:
            return

        # Start components
        if self.config.enable_memory_monitor and self._memory_monitor:
            # Memory monitor starts automatically on creation
            pass

        self._active = True

        # Start auto-tuning if enabled
        if self.config.enable_auto_tuning:
            asyncio.create_task(self._auto_tuning_loop())

        print("Resource optimization services started")

    async def stop(self):
        """Stop all resource optimization services"""
        if not self._active:
            return

        self._active = False

        # Stop scheduler
        if self._scheduler:
            await self._scheduler.stop()

        print("Resource optimization services stopped")

    async def execute_skill(self, skill: SignatureSkill, input_data: Any, context: ExecutionContext) -> SkillResult:
        """Execute a skill with full resource optimization"""
        if not self._active:
            # Fallback to direct execution
            return await skill.execute_with_signature(input_data, context)

        start_time = time.time()

        try:
            # JIT optimization for skill execution method
            if self.config.enable_jit_optimization and self._jit_compiler:
                optimized_execution = self._jit_compiler.get_optimized_function(skill.execute_with_signature)
                if optimized_execution:
                    result = await optimized_execution(input_data, context)
                else:
                    result = await skill.execute_with_signature(input_data, context)
            else:
                result = await skill.execute_with_signature(input_data, context)

            # Record execution metrics
            execution_time = time.time() - start_time

            if self._jit_compiler:
                self._jit_compiler.record_execution(skill.execute_with_signature, execution_time)

            return result

        except Exception as e:
            # Handle optimization failures gracefully
            print(f"Optimized execution failed, falling back to direct execution: {e}")
            return await skill.execute_with_signature(input_data, context)

    async def submit_optimized_task(self, func: Callable, *args, **kwargs) -> Any:
        """Submit a task for optimized execution"""
        if not self._active or not self._scheduler:
            # Direct execution fallback
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        # Create task for scheduler
        from ..scheduler.work_stealing_scheduler import Task
        from ..scheduler.work_stealing_scheduler import TaskPriority

        task = Task(
            id=f"optimized_task_{time.time()}", func=func, args=args, kwargs=kwargs, priority=TaskPriority.NORMAL
        )

        # Submit to scheduler
        future = await self._scheduler.submit(task)
        return await future

    async def _auto_tuning_loop(self):
        """Background loop for automatic performance tuning"""
        while self._active:
            try:
                await self._update_optimization_stats()
                await self._adjust_parameters()
                await asyncio.sleep(self.config.tuning_interval)
            except Exception as e:
                print(f"Auto-tuning error: {e}")
                await asyncio.sleep(5.0)

    async def _update_optimization_stats(self):
        """Update optimization statistics"""
        active_optimizations = []

        # Memory optimization stats
        if self._arena_allocator and self._memory_monitor:
            arena_stats = self._arena_allocator.get_stats()
            memory_efficiency = self._arena_allocator.get_hash_consing_efficiency()
            self._stats.memory_reduction_ratio = memory_efficiency
            active_optimizations.append("arena_allocator")

        # Scheduler stats
        if self._scheduler:
            scheduler_stats = self._scheduler.get_stats()
            self._stats.throughput_tasks_per_sec = scheduler_stats.throughput_tasks_per_sec
            active_optimizations.append("work_stealing_scheduler")

        # JIT compilation stats
        if self._jit_compiler:
            jit_stats = self._jit_compiler.get_compilation_stats()
            self._stats.average_speedup = jit_stats.get("average_speedup", 0.0)
            active_optimizations.append("jit_compiler")

        self._stats.active_optimizations = active_optimizations

    async def _adjust_parameters(self):
        """Adjust optimization parameters based on performance"""
        # This would implement dynamic parameter tuning
        # For now, just log current status
        if self._stats.memory_reduction_ratio < self.config.memory_reduction_target:
            print(
                f"Memory reduction below target: {self._stats.memory_reduction_ratio:.2%} < {self.config.memory_reduction_target:.2%}"
            )

        if self._stats.throughput_tasks_per_sec < self.config.throughput_target:
            print(
                f"Throughput below target: {self._stats.throughput_tasks_per_sec:.0f} < {self.config.throughput_target:.0f}"
            )

        if self._stats.average_speedup < self.config.speedup_target:
            print(f"Speedup below target: {self._stats.average_speedup:.1f}x < {self.config.speedup_target:.1f}x")

    def get_stats(self) -> OptimizationStats:
        """Get current optimization statistics"""
        return OptimizationStats(
            memory_reduction_ratio=self._stats.memory_reduction_ratio,
            throughput_tasks_per_sec=self._stats.throughput_tasks_per_sec,
            average_speedup=self._stats.average_speedup,
            total_optimizations=len(self._stats.active_optimizations),
            active_optimizations=self._stats.active_optimizations.copy(),
        )

    def get_performance_report(self) -> dict:
        """Get comprehensive performance report"""
        report = {"optimization_stats": self.get_stats().__dict__, "component_stats": {}, "targets_met": {}}

        # Component statistics
        if self._arena_allocator:
            report["component_stats"]["arena_allocator"] = self._arena_allocator.get_stats().__dict__

        if self._memory_pool:
            report["component_stats"]["memory_pool"] = self._memory_pool.get_stats().__dict__

        if self._garbage_collector:
            report["component_stats"]["garbage_collector"] = self._garbage_collector.get_stats().__dict__

        if self._memory_monitor:
            report["component_stats"]["memory_monitor"] = self._memory_monitor.get_stats().__dict__

        if self._scheduler:
            report["component_stats"]["scheduler"] = self._scheduler.get_stats().__dict__

        if self._jit_compiler:
            report["component_stats"]["jit_compiler"] = self._jit_compiler.get_compilation_stats()

        # Target achievement
        report["targets_met"] = {
            "memory_reduction": self._stats.memory_reduction_ratio >= self.config.memory_reduction_target,
            "throughput": self._stats.throughput_tasks_per_sec >= self.config.throughput_target,
            "speedup": self._stats.average_speedup >= self.config.speedup_target,
        }

        return report


# Global resource optimizer instance
_global_resource_optimizer: ResourceOptimizer | None = None


def get_resource_optimizer(**kwargs) -> ResourceOptimizer:
    """Get or create the global resource optimizer"""
    global _global_resource_optimizer
    if _global_resource_optimizer is None:
        _global_resource_optimizer = ResourceOptimizer(**kwargs)
    return _global_resource_optimizer


async def execute_optimized_skill(skill: SignatureSkill, input_data: Any, context: ExecutionContext) -> SkillResult:
    """Convenience function for optimized skill execution"""
    optimizer = get_resource_optimizer()
    if not optimizer._active:
        await optimizer.start()
    return await optimizer.execute_skill(skill, input_data, context)
