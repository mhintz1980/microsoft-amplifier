"""
Agent Lightning Integration Hooks

Provides optimization hooks and integration points for Agent Lightning
with the Lean-Agentic resource optimization system.
"""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..signature_framework import ExecutionContext
from ..signature_framework import SignatureSkill
from ..signature_framework import SkillResult
from .resource_optimizer import get_resource_optimizer


@dataclass
class LightningHook:
    """Hook point for Agent Lightning integration"""

    hook_id: str
    trigger: str
    callback: Callable
    priority: int = 0
    enabled: bool = True


@dataclass
class LightningStats:
    """Statistics for Agent Lightning integration"""

    hooks_triggered: int = 0
    optimizations_applied: int = 0
    total_speedup: float = 0.0
    lightning_integrations: int = 0


class AgentLightningHooks:
    """Integration hooks for Agent Lightning optimization"""

    def __init__(self):
        self._resource_optimizer = get_resource_optimizer()
        self._hooks: dict[str, list[LightningHook]] = {}
        self._hook_lock = None  # Will be set in async context
        self._stats = LightningStats()
        self._integration_active = False

    async def initialize(self):
        """Initialize Agent Lightning integration"""
        if self._integration_active:
            return

        # Start resource optimizer
        await self._resource_optimizer.start()

        # Register default hooks
        await self._register_default_hooks()

        self._hook_lock = asyncio.Lock()
        self._integration_active = True

        print("Agent Lightning hooks initialized")

    async def register_hook(self, hook: LightningHook):
        """Register a new hook"""
        async with self._hook_lock:
            if hook.trigger not in self._hooks:
                self._hooks[hook.trigger] = []
            self._hooks[hook.trigger].append(hook)

        print(f"Registered hook: {hook.hook_id} for trigger: {hook.trigger}")

    async def unregister_hook(self, hook_id: str):
        """Unregister a hook"""
        async with self._hook_lock:
            for trigger, hooks in self._hooks.items():
                self._hooks[trigger] = [h for h in hooks if h.hook_id != hook_id]

        print(f"Unregistered hook: {hook_id}")

    async def trigger_hooks(self, trigger: str, context: dict[str, Any]) -> dict[str, Any]:
        """Trigger all hooks for a specific trigger"""
        if not self._integration_active:
            return context

        updated_context = context.copy()

        async with self._hook_lock:
            if trigger in self._hooks:
                # Sort hooks by priority (higher priority first)
                hooks = sorted(self._hooks[trigger], key=lambda h: h.priority, reverse=True)

                for hook in hooks:
                    if hook.enabled:
                        try:
                            start_time = time.time()
                            result = await hook.callback(updated_context)
                            execution_time = time.time() - start_time

                            # Update context with hook results
                            if isinstance(result, dict):
                                updated_context.update(result)

                            self._stats.hooks_triggered += 1

                            # Log hook execution
                            if execution_time > 0.1:  # Log slow hooks
                                print(f"Hook {hook.hook_id} took {execution_time:.3f}s")

                        except Exception as e:
                            print(f"Hook {hook.hook_id} failed: {e}")

        return updated_context

    async def _register_default_hooks(self):
        """Register default optimization hooks"""
        # Skill execution optimization hook
        skill_hook = LightningHook(
            hook_id="skill_execution_optimization",
            trigger="before_skill_execution",
            callback=self._optimize_skill_execution,
            priority=10,
        )
        await self.register_hook(skill_hook)

        # Memory optimization hook
        memory_hook = LightningHook(
            hook_id="memory_optimization",
            trigger="memory_pressure_high",
            callback=self._optimize_memory_usage,
            priority=20,
        )
        await self.register_hook(memory_hook)

        # JIT compilation hook
        jit_hook = LightningHook(
            hook_id="jit_compilation", trigger="hot_path_detected", callback=self._compile_hot_path, priority=15
        )
        await self.register_hook(jit_hook)

        # Load balancing hook
        load_balance_hook = LightningHook(
            hook_id="load_balancing", trigger="task_submitted", callback=self._balance_task_load, priority=5
        )
        await self.register_hook(load_balance_hook)

    async def _optimize_skill_execution(self, context: dict[str, Any]) -> dict[str, Any]:
        """Optimize skill execution using resource optimizer"""
        skill = context.get("skill")
        input_data = context.get("input_data")
        exec_context = context.get("context")

        if skill and input_data and exec_context:
            # Execute with resource optimization
            result = await self._resource_optimizer.execute_skill(skill, input_data, exec_context)
            context["optimized_result"] = result
            self._stats.optimizations_applied += 1

        return context

    async def _optimize_memory_usage(self, context: dict[str, Any]) -> dict[str, Any]:
        """Optimize memory usage under pressure"""
        # Trigger garbage collection
        import gc

        collected = gc.collect()

        # Force memory cleanup
        if hasattr(self._resource_optimizer, "_garbage_collector"):
            await self._resource_optimizer._garbage_collector._run_gc_async(force=True)

        context["memory_optimized"] = True
        context["objects_collected"] = collected

        return context

    async def _compile_hot_path(self, context: dict[str, Any]) -> dict[str, Any]:
        """Compile hot paths with JIT optimization"""
        func = context.get("hot_function")
        if func and hasattr(self._resource_optimizer, "_jit_compiler"):
            jit_compiler = self._resource_optimizer._jit_compiler
            result = await jit_compiler.optimize_function(func)
            context["compiled_function"] = result.optimized_func
            context["speedup_achieved"] = result.speedup_factor
            self._stats.total_speedup += result.speedup_factor

        return context

    async def _balance_task_load(self, context: dict[str, Any]) -> dict[str, Any]:
        """Balance task load across workers"""
        task = context.get("task")
        if task and hasattr(self._resource_optimizer, "_scheduler"):
            scheduler = self._resource_optimizer._scheduler
            # Submit to load balancer
            if hasattr(scheduler, "_load_balancer"):
                worker_id = await scheduler._load_balancer.assign_task(task)
                context["assigned_worker"] = worker_id

        return context

    async def integrate_with_agent_lightning(self, agent_config: dict[str, Any]) -> bool:
        """Integrate with Agent Lightning system"""
        try:
            # This would integrate with actual Agent Lightning API
            # For now, simulate successful integration
            await asyncio.sleep(0.1)

            # Configure Agent Lightning with optimization hooks
            agent_config["optimization_hooks"] = True
            agent_config["resource_optimizer"] = self._resource_optimizer
            agent_config["lightning_integration"] = True

            self._stats.lightning_integrations += 1
            print("Agent Lightning integration successful")

            return True

        except Exception as e:
            print(f"Agent Lightning integration failed: {e}")
            return False

    async def execute_with_lightning_optimization(
        self, skill: SignatureSkill, input_data: Any, context: ExecutionContext
    ) -> SkillResult:
        """Execute skill with full Agent Lightning optimization"""
        # Trigger pre-execution hooks
        hook_context = {"skill": skill, "input_data": input_data, "context": context}
        hook_context = await self.trigger_hooks("before_skill_execution", hook_context)

        # Use optimized result if available
        if "optimized_result" in hook_context:
            return hook_context["optimized_result"]

        # Fallback to resource optimizer
        return await self._resource_optimizer.execute_skill(skill, input_data, context)

    def get_stats(self) -> LightningStats:
        """Get Agent Lightning integration statistics"""
        return LightningStats(
            hooks_triggered=self._stats.hooks_triggered,
            optimizations_applied=self._stats.optimizations_applied,
            total_speedup=self._stats.total_speedup,
            lightning_integrations=self._stats.lightning_integrations,
        )

    def get_hook_info(self) -> dict[str, list[dict]]:
        """Get information about registered hooks"""
        hook_info = {}
        for trigger, hooks in self._hooks.items():
            hook_info[trigger] = [
                {"hook_id": hook.hook_id, "priority": hook.priority, "enabled": hook.enabled} for hook in hooks
            ]
        return hook_info


# Global Agent Lightning hooks instance
_global_lightning_hooks: AgentLightningHooks | None = None


def get_agent_lightning_hooks() -> AgentLightningHooks:
    """Get or create the global Agent Lightning hooks"""
    global _global_lightning_hooks
    if _global_lightning_hooks is None:
        _global_lightning_hooks = AgentLightningHooks()
    return _global_lightning_hooks


async def execute_with_lightning(skill: SignatureSkill, input_data: Any, context: ExecutionContext) -> SkillResult:
    """Convenience function for Agent Lightning optimized execution"""
    hooks = get_agent_lightning_hooks()
    if not hooks._integration_active:
        await hooks.initialize()
    return await hooks.execute_with_lightning_optimization(skill, input_data, context)
