"""
Agent Lightning Hooks Integration
Connects pre-task optimization with Agent Lightning continuous learning system
Provides intelligent learning hooks for optimization improvement over time
"""

import asyncio
import time
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

# Add amplifier to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from amplifier.skills.learning.agent_lightning_core import (
    agent_lightning_core,
    LearningSignalType,
    initialize_agent_lightning,
)
from amplifier.optimization.pre_task_optimization import OptimizationResult, TaskComplexity, pre_task_optimizer
from amplifier.optimization.token_efficiency_integration import (
    EfficiencyCheckResult,
    TokenEfficiencyLevel,
    token_efficiency_integrator,
)


class LearningHookType(Enum):
    """Types of learning hooks"""

    PRE_OPTIMIZATION = "pre_optimization"
    POST_OPTIMIZATION = "post_optimization"
    TASK_COMPLETION = "task_completion"
    EFFICIENCY_VALIDATION = "efficiency_validation"
    AGENT_PERFORMANCE = "agent_performance"
    PATTERN_DISCOVERY = "pattern_discovery"


class HookPriority(Enum):
    """Hook execution priority"""

    CRITICAL = 1  # Always execute
    HIGH = 2  # Important, usually execute
    MEDIUM = 3  # Standard hooks
    LOW = 4  # Nice to have
    DEBUG = 5  # Debugging only


@dataclass
class LearningHook:
    """Learning hook definition"""

    hook_type: LearningHookType
    priority: HookPriority
    condition: Callable[[Dict[str, Any]], bool]
    action: Callable[[Dict[str, Any]], Dict[str, Any]]
    description: str
    enabled: bool = True
    execution_count: int = 0
    success_count: int = 0
    total_processing_time: float = 0.0


@dataclass
class LearningSignal:
    """Structured learning signal for Agent Lightning"""

    signal_type: LearningSignalType
    source: str
    data: Dict[str, Any]
    confidence: float
    timestamp: float
    context: Dict[str, Any]
    signal_id: str


class AgentLightningHooks:
    """
    Comprehensive hooks system for Agent Lightning integration
    Captures learning opportunities throughout the optimization lifecycle
    """

    def __init__(self, storage_path: str = ".data/agent_lightning_hooks"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Hook registry
        self.hooks: List[LearningHook] = []
        self.hooks_by_type: Dict[LearningHookType, List[LearningHook]] = {}

        # Learning metrics
        self.learning_signals_sent = 0
        self.learning_signals_successful = 0
        self.patterns_discovered = 0
        self.optimizations_applied = 0

        # Performance tracking
        self.total_hook_execution_time = 0.0
        self.average_hook_time = 0.0

        # Initialize default hooks
        self._register_default_hooks()

        # Agent Lightning integration
        self.agent_lightning_enabled = True

    def register_hook(self, hook: LearningHook):
        """Register a new learning hook"""

        self.hooks.append(hook)

        # Organize by type
        if hook.hook_type not in self.hooks_by_type:
            self.hooks_by_type[hook.hook_type] = []
        self.hooks_by_type[hook.hook_type].append(hook)

        # Sort by priority
        self.hooks_by_type[hook.hook_type].sort(key=lambda h: h.priority.value)

    def _register_default_hooks(self):
        """Register default learning hooks"""

        # Pre-optimization hooks
        self.register_hook(
            LearningHook(
                hook_type=LearningHookType.PRE_OPTIMIZATION,
                priority=HookPriority.HIGH,
                condition=lambda ctx: ctx.get("task_analysis", {}).get("complexity") == TaskComplexity.REVOLUTIONARY,
                action=self._pre_optimization_revolutionary_hook,
                description="Handle revolutionary task complexity",
            )
        )

        self.register_hook(
            LearningHook(
                hook_type=LearningHookType.PRE_OPTIMIZATION,
                priority=HookPriority.MEDIUM,
                condition=lambda ctx: ctx.get("original_tokens", 0) > 10000,
                action=self._pre_optimization_high_token_hook,
                description="Handle high token usage tasks",
            )
        )

        # Post-optimization hooks
        self.register_hook(
            LearningHook(
                hook_type=LearningHookType.POST_OPTIMIZATION,
                priority=HookPriority.CRITICAL,
                condition=lambda ctx: True,  # Always run
                action=self._post_optimization_efficiency_hook,
                description="Track optimization efficiency",
            )
        )

        self.register_hook(
            LearningHook(
                hook_type=LearningHookType.POST_OPTIMIZATION,
                priority=HookPriority.HIGH,
                condition=lambda ctx: ctx.get("token_reduction_percentage", 0) > 50,
                action=self._post_optimization_excellent_hook,
                description="Excellent optimization discovery",
            )
        )

        # Efficiency validation hooks
        self.register_hook(
            LearningHook(
                hook_type=LearningHookType.EFFICIENCY_VALIDATION,
                priority=HookPriority.HIGH,
                condition=lambda ctx: not ctx.get("efficiency_check", {}).get("passes_threshold", True),
                action=self._efficiency_failure_hook,
                description="Learn from efficiency failures",
            )
        )

        # Pattern discovery hooks
        self.register_hook(
            LearningHook(
                hook_type=LearningHookType.PATTERN_DISCOVERY,
                priority=HookPriority.MEDIUM,
                condition=lambda ctx: self._is_pattern_discovery_opportunity(ctx),
                action=self._pattern_discovery_hook,
                description="Discover optimization patterns",
            )
        )

    async def execute_hooks(self, hook_type: LearningHookType, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute all hooks of a specific type"""

        results = []
        hooks_to_execute = self.hooks_by_type.get(hook_type, [])

        start_time = time.time()

        for hook in hooks_to_execute:
            if not hook.enabled:
                continue

            try:
                # Check if hook condition is met
                if hook.condition(context):
                    hook_start = time.time()

                    # Execute hook action
                    result = (
                        await hook.action(context) if asyncio.iscoroutinefunction(hook.action) else hook.action(context)
                    )

                    hook_time = time.time() - hook_start
                    hook.execution_count += 1
                    hook.total_processing_time += hook_time

                    # Track success
                    if result.get("success", True):
                        hook.success_count += 1

                    results.append({"hook": hook.description, "result": result, "execution_time": hook_time})

            except Exception as e:
                # Don't fail entire pipeline for hook errors
                results.append(
                    {"hook": hook.description, "result": {"success": False, "error": str(e)}, "execution_time": 0}
                )

        total_time = time.time() - start_time
        self.total_hook_execution_time += total_time

        if len(hooks_to_execute) > 0:
            self.average_hook_time = total_time / len(hooks_to_execute)

        return results

    async def _pre_optimization_revolutionary_hook(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle revolutionary task pre-optimization"""

        task_analysis = context.get("task_analysis", {})

        learning_signal = LearningSignal(
            signal_type=LearningSignalType.OPTIMIZATION_PATTERN,
            source="pre_optimization_revolutionary",
            data={
                "complexity": "revolutionary",
                "task_type": task_analysis.get("task_type", "unknown"),
                "estimated_duration": task_analysis.get("estimated_duration", 0),
                "agent_requirements": task_analysis.get("agent_requirements", []),
                "pattern": "revolutionary_task_handling",
                "recommended_approach": "phased_implementation",
            },
            confidence=0.8,
            timestamp=time.time(),
            context=context,
            signal_id=self._generate_signal_id(),
        )

        success = await self._send_learning_signal(learning_signal)

        return {
            "success": success,
            "pattern_detected": "revolutionary_task",
            "recommended_strategy": "phased_implementation",
            "learning_signal_sent": success,
        }

    async def _pre_optimization_high_token_hook(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle high token usage pre-optimization"""

        original_tokens = context.get("original_tokens", 0)
        user_prompt = context.get("user_prompt", "")

        learning_signal = LearningSignal(
            signal_type=LearningSignalType.TOKEN_EFFICIENCY_PATTERN,
            source="pre_optimization_high_token",
            data={
                "token_count": original_tokens,
                "prompt_length": len(user_prompt),
                "complexity_indicators": self._analyze_prompt_complexity(user_prompt),
                "pattern": "high_token_usage",
                "recommended_optimization": "progressive_disclosure",
            },
            confidence=0.9,
            timestamp=time.time(),
            context=context,
            signal_id=self._generate_signal_id(),
        )

        success = await self._send_learning_signal(learning_signal)

        return {
            "success": success,
            "pattern_detected": "high_token_usage",
            "recommended_strategy": "progressive_disclosure",
            "token_count": original_tokens,
            "learning_signal_sent": success,
        }

    async def _post_optimization_efficiency_hook(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Track post-optimization efficiency"""

        optimization_result = context.get("optimization_result")
        efficiency_check = context.get("efficiency_check")

        if not optimization_result:
            return {"success": False, "error": "No optimization result"}

        # Calculate efficiency metrics
        token_reduction = optimization_result.optimized_prompt.token_reduction
        efficiency_score = optimization_result.token_efficiency_score
        success_probability = optimization_result.confidence_score

        learning_signal = LearningSignal(
            signal_type=LearningSignalType.PERFORMANCE_METRIC,
            source="post_optimization_efficiency",
            data={
                "token_reduction": token_reduction,
                "efficiency_score": efficiency_score,
                "success_probability": success_probability,
                "task_complexity": optimization_result.task_analysis.complexity.value,
                "optimization_technique": optimization_result.optimized_prompt.optimization_technique,
                "agent_count": len(optimization_result.agent_allocation["execution_order"]),
                "workflow_efficiency": optimization_result.selected_workflow.get("token_optimization", {}),
            },
            confidence=0.95,
            timestamp=time.time(),
            context=context,
            signal_id=self._generate_signal_id(),
        )

        success = await self._send_learning_signal(learning_signal)

        return {
            "success": success,
            "efficiency_metrics": {
                "token_reduction": token_reduction,
                "efficiency_score": efficiency_score,
                "success_probability": success_probability,
            },
            "learning_signal_sent": success,
        }

    async def _post_optimization_excellent_hook(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle excellent optimization discoveries"""

        optimization_result = context.get("optimization_result")

        if not optimization_result:
            return {"success": False, "error": "No optimization result"}

        token_reduction = optimization_result.optimized_prompt.token_reduction
        technique = optimization_result.optimized_prompt.optimization_technique
        task_complexity = optimization_result.task_analysis.complexity.value

        learning_signal = LearningSignal(
            signal_type=LearningSignalType.OPTIMIZATION_PATTERN,
            source="excellent_optimization_discovery",
            data={
                "excellent_technique": technique,
                "token_reduction": token_reduction,
                "task_complexity": task_complexity,
                "applicable_contexts": [task_complexity],
                "pattern_strength": "high",
                "reusable_pattern": True,
            },
            confidence=0.9,
            timestamp=time.time(),
            context=context,
            signal_id=self._generate_signal_id(),
        )

        success = await self._send_learning_signal(learning_signal)

        return {
            "success": success,
            "excellent_pattern": technique,
            "token_reduction": token_reduction,
            "pattern_saved": success,
            "learning_signal_sent": success,
        }

    async def _efficiency_failure_hook(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from efficiency validation failures"""

        efficiency_check = context.get("efficiency_check", {})
        optimization_result = context.get("optimization_result")

        if not efficiency_check:
            return {"success": False, "error": "No efficiency check result"}

        metrics = efficiency_check.get("metrics", {})
        failure_reasons = efficiency_check.get("alternative_approaches", [])

        learning_signal = LearningSignal(
            signal_type=LearningSignalType.ERROR_PATTERN,
            source="efficiency_validation_failure",
            data={
                "failure_type": "efficiency_threshold_exceeded",
                "token_count": metrics.get("optimized_tokens", 0),
                "efficiency_level": metrics.get("efficiency_level", {}).value
                if hasattr(metrics.get("efficiency_level", {}), "value")
                else "unknown",
                "task_complexity": optimization_result.task_analysis.complexity.value
                if optimization_result
                else "unknown",
                "failure_patterns": failure_reasons,
                "prevention_strategy": "early_token_check",
            },
            confidence=0.85,
            timestamp=time.time(),
            context=context,
            signal_id=self._generate_signal_id(),
        )

        success = await self._send_learning_signal(learning_signal)

        return {
            "success": success,
            "failure_learned": True,
            "failure_patterns": failure_reasons,
            "prevention_strategy": "early_token_check",
            "learning_signal_sent": success,
        }

    async def _pattern_discovery_hook(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Discover optimization patterns"""

        optimization_result = context.get("optimization_result")
        if not optimization_result:
            return {"success": False, "error": "No optimization result"}

        # Analyze for patterns
        patterns = []

        # Pattern 1: Task type optimization
        task_type = optimization_result.task_analysis.task_type
        technique = optimization_result.optimized_prompt.optimization_technique
        patterns.append(
            {
                "pattern_type": "task_type_optimization",
                "task_type": task_type,
                "successful_technique": technique,
                "confidence": optimization_result.confidence_score,
            }
        )

        # Pattern 2: Complexity-based optimization
        complexity = optimization_result.task_analysis.complexity.value
        token_efficiency = optimization_result.token_efficiency_score
        patterns.append(
            {
                "pattern_type": "complexity_optimization",
                "complexity": complexity,
                "efficiency_achieved": token_efficiency,
                "applicable": token_efficiency > 0.8,
            }
        )

        # Pattern 3: Agent selection success
        agent_count = len(optimization_result.agent_allocation["execution_order"])
        success_probability = optimization_result.confidence_score
        patterns.append(
            {
                "pattern_type": "agent_allocation",
                "agent_count": agent_count,
                "success_rate": success_probability,
                "optimal_range": agent_count <= 5,
            }
        )

        learning_signal = LearningSignal(
            signal_type=LearningSignalType.OPTIMIZATION_PATTERN,
            source="pattern_discovery",
            data={
                "patterns_discovered": patterns,
                "overall_success": optimization_result.confidence_score > 0.8,
                "repeatable_patterns": [p for p in patterns if p.get("confidence", 0) > 0.7],
                "pattern_source": "optimization_analysis",
            },
            confidence=0.75,
            timestamp=time.time(),
            context=context,
            signal_id=self._generate_signal_id(),
        )

        success = await self._send_learning_signal(learning_signal)

        return {
            "success": success,
            "patterns_discovered": len(patterns),
            "repeatable_patterns": len([p for p in patterns if p.get("confidence", 0) > 0.7]),
            "patterns": patterns,
            "learning_signal_sent": success,
        }

    def _analyze_prompt_complexity(self, prompt: str) -> List[str]:
        """Analyze prompt for complexity indicators"""

        indicators = []

        # Length-based indicators
        if len(prompt) > 1000:
            indicators.append("long_prompt")
        if len(prompt.split()) > 200:
            indicators.append("many_words")

        # Content-based indicators
        complexity_words = ["analyze", "implement", "optimize", "integrate", "design", "architecture"]
        if any(word in prompt.lower() for word in complexity_words):
            indicators.append("complex_task")

        # Multi-step indicators
        multi_step_words = ["and then", "after that", "followed by", "finally", "additionally"]
        if any(word in prompt.lower() for word in multi_step_words):
            indicators.append("multi_step")

        return indicators

    def _is_pattern_discovery_opportunity(self, context: Dict[str, Any]) -> bool:
        """Check if this is a good opportunity for pattern discovery"""

        optimization_result = context.get("optimization_result")
        if not optimization_result:
            return False

        # Good opportunities for pattern discovery:
        # 1. High success rate (>85%)
        # 2. Significant token reduction (>30%)
        # 3. Complex or revolutionary tasks
        # 4. Multiple agents involved

        conditions = [
            optimization_result.confidence_score > 0.85,
            optimization_result.optimized_prompt.token_reduction > 30,
            optimization_result.task_analysis.complexity in [TaskComplexity.COMPLEX, TaskComplexity.REVOLUTIONARY],
            len(optimization_result.agent_allocation["execution_order"]) > 2,
        ]

        return any(conditions)

    async def _send_learning_signal(self, signal: LearningSignal) -> bool:
        """Send learning signal to Agent Lightning"""

        if not self.agent_lightning_enabled:
            return False

        try:
            await agent_lightning_core.receive_learning_signal(
                signal.signal_type, signal.source, signal.data, signal.confidence
            )

            self.learning_signals_sent += 1
            self.learning_signals_successful += 1

            return True

        except Exception as e:
            # Don't fail optimization if learning fails
            self.learning_signals_sent += 1
            return False

    def _generate_signal_id(self) -> str:
        """Generate unique signal ID"""
        return hashlib.md5(f"{time.time()}{os.urandom(8)}".encode()).hexdigest()[:16]

    async def complete_optimization_lifecycle(
        self,
        user_prompt: str,
        optimization_result: OptimizationResult,
        efficiency_check: Optional[EfficiencyCheckResult] = None,
        execution_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Complete optimization lifecycle with all hooks"""

        lifecycle_results = {}

        # Phase 1: Pre-optimization hooks
        pre_context = {
            "user_prompt": user_prompt,
            "original_tokens": optimization_result.task_analysis.token_estimate,
            "task_analysis": asdict(optimization_result.task_analysis),
        }

        lifecycle_results["pre_optimization"] = await self.execute_hooks(LearningHookType.PRE_OPTIMIZATION, pre_context)

        # Phase 2: Post-optimization hooks
        post_context = {"optimization_result": optimization_result, "user_prompt": user_prompt}

        lifecycle_results["post_optimization"] = await self.execute_hooks(
            LearningHookType.POST_OPTIMIZATION, post_context
        )

        # Phase 3: Efficiency validation hooks
        if efficiency_check:
            efficiency_context = {
                "efficiency_check": asdict(efficiency_check),
                "optimization_result": optimization_result,
            }

            lifecycle_results["efficiency_validation"] = await self.execute_hooks(
                LearningHookType.EFFICIENCY_VALIDATION, efficiency_context
            )

        # Phase 4: Pattern discovery hooks
        pattern_context = {
            "optimization_result": optimization_result,
            "efficiency_check": asdict(efficiency_check) if efficiency_check else None,
        }

        lifecycle_results["pattern_discovery"] = await self.execute_hooks(
            LearningHookType.PATTERN_DISCOVERY, pattern_context
        )

        # Phase 5: Task completion hooks
        if execution_result:
            completion_context = {
                "execution_result": execution_result,
                "optimization_result": optimization_result,
                "actual_tokens_used": execution_result.get("tokens_used", 0),
                "actual_duration": execution_result.get("duration", 0),
            }

            lifecycle_results["task_completion"] = await self.execute_hooks(
                LearningHookType.TASK_COMPLETION, completion_context
            )

        return lifecycle_results

    def get_hook_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive hook performance report"""

        hook_performance = []
        for hook in self.hooks:
            success_rate = hook.success_count / max(hook.execution_count, 1)
            avg_time = hook.total_processing_time / max(hook.execution_count, 1)

            hook_performance.append(
                {
                    "hook": hook.description,
                    "type": hook.hook_type.value,
                    "priority": hook.priority.value,
                    "execution_count": hook.execution_count,
                    "success_count": hook.success_count,
                    "success_rate": success_rate,
                    "average_time": avg_time,
                    "total_time": hook.total_processing_time,
                    "enabled": hook.enabled,
                }
            )

        return {
            "hook_summary": {
                "total_hooks": len(self.hooks),
                "enabled_hooks": len([h for h in self.hooks if h.enabled]),
                "total_executions": sum(h.execution_count for h in self.hooks),
                "total_hook_time": self.total_hook_execution_time,
                "average_hook_time": self.average_hook_time,
            },
            "learning_summary": {
                "learning_signals_sent": self.learning_signals_sent,
                "learning_signals_successful": self.learning_signals_successful,
                "success_rate": self.learning_signals_successful / max(self.learning_signals_sent, 1),
                "patterns_discovered": self.patterns_discovered,
                "optimizations_applied": self.optimizations_applied,
            },
            "hook_performance": hook_performance,
            "recommendations": [
                "Monitor hook performance for optimization opportunities",
                "Consider disabling low-performing hooks",
                "Scale up successful pattern discovery hooks",
                "Improve error handling in failed hooks",
            ],
        }

    def save_hook_history(self, filename: Optional[str] = None) -> str:
        """Save hook execution history"""

        if not filename:
            filename = f"hook_history_{time.strftime('%Y%m%d_%H%M%S')}.json"

        history_file = self.storage_path / filename

        history_data = {
            "hook_performance": self.get_hook_performance_report(),
            "learning_metrics": {
                "signals_sent": self.learning_signals_sent,
                "signals_successful": self.learning_signals_successful,
                "patterns_discovered": self.patterns_discovered,
            },
            "hook_configuration": [
                {
                    "hook": hook.description,
                    "type": hook.hook_type.value,
                    "priority": hook.priority.value,
                    "enabled": hook.enabled,
                    "execution_count": hook.execution_count,
                    "success_count": hook.success_count,
                }
                for hook in self.hooks
            ],
            "metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "agent_lightning_enabled": self.agent_lightning_enabled,
            },
        }

        with open(history_file, "w") as f:
            json.dump(history_data, f, indent=2)

        return str(history_file)


# Global Agent Lightning hooks instance
agent_lightning_hooks = AgentLightningHooks()


# Convenience functions
async def complete_optimization_lifecycle(
    user_prompt: str,
    optimization_result: OptimizationResult,
    efficiency_check: Optional[EfficiencyCheckResult] = None,
    execution_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Complete optimization lifecycle with Agent Lightning learning"""
    return await agent_lightning_hooks.complete_optimization_lifecycle(
        user_prompt, optimization_result, efficiency_check, execution_result
    )


def get_hook_performance_report() -> Dict[str, Any]:
    """Get current hook performance report"""
    return agent_lightning_hooks.get_hook_performance_report()
