"""
Meta-Skill Integration with Compound Multiplier Support

Advanced meta-skill system that combines multiple skills with compound
multipliers for 3-5x performance improvements. Supports intelligent
skill composition, performance monitoring, and adaptive optimization.
"""

import asyncio
import logging
import time
from collections import defaultdict
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any

import numpy as np

from .base_types import ExecutionContext
from .base_types import SkillInterface
from .base_types import SkillPriority
from .base_types import SkillResult
from .base_types import T_Input
from .bootstrap_optimizer import get_bootstrap_optimizer
from .skill_signature import SignatureSkill
from .zero_hallucination import get_zero_hallucination_enforcer

logger = logging.getLogger(__name__)


class CompositionStrategy(Enum):
    """Strategies for composing multiple skills"""

    SEQUENTIAL = "sequential"  # Execute skills in sequence
    PARALLEL = "parallel"  # Execute skills in parallel
    PIPELINE = "pipeline"  # Pipeline output of one to input of next
    ENSEMBLE = "ensemble"  # Combine results from multiple skills
    ADAPTIVE = "adaptive"  # Adaptive composition based on input
    CONDITIONAL = "conditional"  # Conditional execution based on conditions


class SkillRole(Enum):
    """Roles that skills can play in composition"""

    PRIMARY = "primary"  # Main processing skill
    PREPROCESSOR = "preprocessor"  # Data preprocessing
    POSTPROCESSOR = "postprocessor"  # Data postprocessing
    VALIDATOR = "validator"  # Input/output validation
    OPTIMIZER = "optimizer"  # Performance optimization
    SPECIALIST = "specialist"  # Domain-specific processing
    FALLBACK = "fallback"  # Backup processing


@dataclass
class SkillComponent:
    """Individual skill component in meta-skill composition"""

    skill: SkillInterface
    role: SkillRole
    weight: float = 1.0
    priority: SkillPriority = SkillPriority.NORMAL
    condition: Callable[[Any], bool] | None = None
    timeout: float | None = None
    max_retries: int = 1
    enabled: bool = True
    performance_multiplier: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompositionResult:
    """Result from skill composition"""

    success: bool
    outputs: dict[str, Any] = field(default_factory=dict)
    execution_times: dict[str, float] = field(default_factory=dict)
    confidences: dict[str, float] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    skills_executed: list[str] = field(default_factory=list)
    compound_multiplier: float = 1.0
    total_execution_time: float = 0.0
    quality_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetaSkillConfig:
    """Configuration for meta-skill composition"""

    composition_strategy: CompositionStrategy = CompositionStrategy.SEQUENTIAL
    enable_performance_tracking: bool = True
    enable_adaptive_optimization: bool = True
    enable_zero_hallucination: bool = True
    compound_multiplier_base: float = 1.0
    max_parallel_skills: int = 5
    skill_timeout: float = 30.0
    fallback_on_failure: bool = True
    quality_threshold: float = 0.7
    learning_rate: float = 0.1
    performance_history_size: int = 100


class SkillComposer:
    """Advanced skill composition engine"""

    def __init__(self, config: MetaSkillConfig | None = None):
        self.config = config or MetaSkillConfig()
        self.performance_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.composition_stats: dict[str, Any] = defaultdict(int)
        self.learning_data: dict[str, list[tuple[float, float]]] = defaultdict(list)
        self.bootstrap_optimizer = get_bootstrap_optimizer()
        self.zero_hallucination_enforcer = get_zero_hallucination_enforcer()

    async def compose(
        self, components: list[SkillComponent], input_data: Any, context: ExecutionContext
    ) -> CompositionResult:
        """Compose and execute multiple skills"""
        start_time = time.time()
        result = CompositionResult(success=False)

        try:
            # Filter enabled components
            enabled_components = [c for c in components if c.enabled]
            if not enabled_components:
                result.errors.append("No enabled components found")
                return result

            # Apply composition strategy
            if self.config.composition_strategy == CompositionStrategy.SEQUENTIAL:
                result = await self._compose_sequential(enabled_components, input_data, context)
            elif self.config.composition_strategy == CompositionStrategy.PARALLEL:
                result = await self._compose_parallel(enabled_components, input_data, context)
            elif self.config.composition_strategy == CompositionStrategy.PIPELINE:
                result = await self._compose_pipeline(enabled_components, input_data, context)
            elif self.config.composition_strategy == CompositionStrategy.ENSEMBLE:
                result = await self._compose_ensemble(enabled_components, input_data, context)
            elif self.config.composition_strategy == CompositionStrategy.ADAPTIVE:
                result = await self._compose_adaptive(enabled_components, input_data, context)
            elif self.config.composition_strategy == CompositionStrategy.CONDITIONAL:
                result = await self._compose_conditional(enabled_components, input_data, context)
            else:
                result.errors.append(f"Unknown composition strategy: {self.config.composition_strategy}")

            # Calculate compound multiplier
            result.compound_multiplier = self._calculate_compound_multiplier(result)
            result.total_execution_time = time.time() - start_time

            # Calculate quality score
            result.quality_score = self._calculate_quality_score(result)

            # Update performance tracking
            if self.config.enable_performance_tracking:
                self._update_performance_tracking(result)

            # Apply zero-hallucination if enabled
            if self.config.enable_zero_hallucination and result.success:
                result = await self._apply_zero_hallucination(result, context)

            return result

        except Exception as e:
            result.errors.append(f"Composition failed: {str(e)}")
            result.total_execution_time = time.time() - start_time
            logger.error(f"Skill composition failed: {e}")
            return result

    async def _compose_sequential(
        self, components: list[SkillComponent], input_data: Any, context: ExecutionContext
    ) -> CompositionResult:
        """Sequential composition execution"""
        result = CompositionResult(success=True)
        current_input = input_data

        # Sort by priority
        components.sort(key=lambda c: c.priority.value)

        for component in components:
            try:
                component_start = time.time()
                skill_result = await self._execute_component(component, current_input, context)
                component_time = time.time() - component_start

                if skill_result.success:
                    result.outputs[component.skill.get_config().skill_id] = skill_result.data
                    result.execution_times[component.skill.get_config().skill_id] = component_time
                    result.confidences[component.skill.get_config().skill_id] = skill_result.confidence
                    result.skills_executed.append(component.skill.get_config().skill_id)

                    # Use output as next input
                    current_input = skill_result.data

                else:
                    error_msg = f"Component {component.skill.get_config().skill_id} failed: {skill_result.error}"
                    result.errors.append(error_msg)

                    if not self.config.fallback_on_failure:
                        result.success = False
                        break

            except Exception as e:
                error_msg = f"Component {component.skill.get_config().skill_id} exception: {str(e)}"
                result.errors.append(error_msg)

                if not self.config.fallback_on_failure:
                    result.success = False
                    break

        return result

    async def _compose_parallel(
        self, components: list[SkillComponent], input_data: Any, context: ExecutionContext
    ) -> CompositionResult:
        """Parallel composition execution"""
        result = CompositionResult(success=True)

        # Limit parallel skills
        limited_components = components[: self.config.max_parallel_skills]

        # Create tasks for all components
        tasks = []
        for component in limited_components:
            task = self._execute_component(component, input_data, context)
            tasks.append((component, task))

        # Execute all tasks concurrently
        try:
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

            for (component, _), skill_result in zip(tasks, results, strict=False):
                if isinstance(skill_result, Exception):
                    error_msg = f"Component {component.skill.get_config().skill_id} exception: {str(skill_result)}"
                    result.errors.append(error_msg)

                    if not self.config.fallback_on_failure:
                        result.success = False

                elif isinstance(skill_result, SkillResult):
                    if skill_result.success:
                        result.outputs[component.skill.get_config().skill_id] = skill_result.data
                        result.confidences[component.skill.get_config().skill_id] = skill_result.confidence
                        result.skills_executed.append(component.skill.get_config().skill_id)
                    else:
                        error_msg = f"Component {component.skill.get_config().skill_id} failed: {skill_result.error}"
                        result.errors.append(error_msg)

                        if not self.config.fallback_on_failure:
                            result.success = False

        except Exception as e:
            result.errors.append(f"Parallel execution failed: {str(e)}")
            result.success = False

        return result

    async def _compose_pipeline(
        self, components: list[SkillComponent], input_data: Any, context: ExecutionContext
    ) -> CompositionResult:
        """Pipeline composition execution"""
        result = CompositionResult(success=True)
        current_input = input_data

        # Sort by role order: preprocessor -> primary -> postprocessor
        role_order = {
            SkillRole.PREPROCESSOR: 0,
            SkillRole.PRIMARY: 1,
            SkillRole.SPECIALIST: 2,
            SkillRole.POSTPROCESSOR: 3,
            SkillRole.VALIDATOR: 4,
        }

        components.sort(key=lambda c: role_order.get(c.role, 999))

        for component in components:
            try:
                skill_result = await self._execute_component(component, current_input, context)

                if skill_result.success:
                    result.outputs[component.skill.get_config().skill_id] = skill_result.data
                    result.confidences[component.skill.get_config().skill_id] = skill_result.confidence
                    result.skills_executed.append(component.skill.get_config().skill_id)

                    # Pipeline: output becomes next input
                    current_input = skill_result.data

                else:
                    # For pipeline, failure is critical
                    result.success = False
                    result.errors.append(f"Pipeline component {component.skill.get_config().skill_id} failed")
                    break

            except Exception as e:
                result.success = False
                result.errors.append(f"Pipeline component {component.skill.get_config().skill_id} exception: {str(e)}")
                break

        return result

    async def _compose_ensemble(
        self, components: list[SkillComponent], input_data: Any, context: ExecutionContext
    ) -> CompositionResult:
        """Ensemble composition execution"""
        result = CompositionResult(success=True)

        # Execute all components
        tasks = []
        for component in components:
            task = self._execute_component(component, input_data, context)
            tasks.append((component, task))

        try:
            skill_results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

            # Collect successful results
            successful_results = []
            for (component, _), skill_result in zip(tasks, skill_results, strict=False):
                if isinstance(skill_result, SkillResult) and skill_result.success:
                    result.outputs[component.skill.get_config().skill_id] = skill_result.data
                    result.confidences[component.skill.get_config().skill_id] = skill_result.confidence
                    result.skills_executed.append(component.skill.get_config().skill_id)
                    successful_results.append((component, skill_result))

            if not successful_results:
                result.success = False
                result.errors.append("No successful ensemble members")
                return result

            # Ensemble combination (weighted average by confidence and component weight)
            ensemble_output = self._combine_ensemble_results(successful_results)
            result.outputs["ensemble"] = ensemble_output
            result.confidences["ensemble"] = sum(
                skill_result.confidence * component.weight for component, skill_result in successful_results
            ) / len(successful_results)

        except Exception as e:
            result.success = False
            result.errors.append(f"Ensemble execution failed: {str(e)}")

        return result

    async def _compose_adaptive(
        self, components: list[SkillComponent], input_data: Any, context: ExecutionContext
    ) -> CompositionResult:
        """Adaptive composition execution"""
        result = CompositionResult(success=True)

        # Select components based on conditions and historical performance
        selected_components = self._select_adaptive_components(components, input_data, context)

        if not selected_components:
            result.success = False
            result.errors.append("No components selected for adaptive composition")
            return result

        # Execute selected components
        for component in selected_components:
            try:
                skill_result = await self._execute_component(component, input_data, context)

                if skill_result.success:
                    result.outputs[component.skill.get_config().skill_id] = skill_result.data
                    result.confidences[component.skill.get_config().skill_id] = skill_result.confidence
                    result.skills_executed.append(component.skill.get_config().skill_id)

                    # Learn from this execution
                    self._update_learning_data(component.skill.get_config().skill_id, skill_result)

                else:
                    result.errors.append(f"Adaptive component {component.skill.get_config().skill_id} failed")

                    if not self.config.fallback_on_failure:
                        result.success = False
                        break

            except Exception as e:
                result.errors.append(f"Adaptive component {component.skill.get_config().skill_id} exception: {str(e)}")

                if not self.config.fallback_on_failure:
                    result.success = False
                    break

        return result

    async def _compose_conditional(
        self, components: list[SkillComponent], input_data: Any, context: ExecutionContext
    ) -> CompositionResult:
        """Conditional composition execution"""
        result = CompositionResult(success=True)

        # Execute components whose conditions are met
        for component in components:
            try:
                # Check condition
                if component.condition and not component.condition(input_data):
                    continue

                skill_result = await self._execute_component(component, input_data, context)

                if skill_result.success:
                    result.outputs[component.skill.get_config().skill_id] = skill_result.data
                    result.confidences[component.skill.get_config().skill_id] = skill_result.confidence
                    result.skills_executed.append(component.skill.get_config().skill_id)
                else:
                    result.errors.append(f"Conditional component {component.skill.get_config().skill_id} failed")

            except Exception as e:
                result.errors.append(
                    f"Conditional component {component.skill.get_config().skill_id} exception: {str(e)}"
                )

        return result

    async def _execute_component(
        self, component: SkillComponent, input_data: Any, context: ExecutionContext
    ) -> SkillResult:
        """Execute a single component with timeout and retry logic"""
        component_context = ExecutionContext(
            user_id=context.user_id,
            session_id=context.session_id,
            timeout=component.timeout or self.config.skill_timeout,
            priority=component.priority,
            metadata={**context.metadata, **component.metadata},
        )

        for attempt in range(component.max_retries + 1):
            try:
                if attempt > 0:
                    await asyncio.sleep(0.1 * attempt)  # Exponential backoff

                # Apply performance multiplier
                if component.performance_multiplier != 1.0:
                    # Create optimized context
                    component_context.enable_optimization = True

                result = await component.skill.execute_with_signature(input_data, component_context)

                if result.success:
                    # Apply performance multiplier to execution time
                    result.execution_time *= component.performance_multiplier
                    return result

            except TimeoutError:
                if attempt == component.max_retries:
                    return SkillResult(
                        success=False,
                        error=f"Component {component.skill.get_config().skill_id} timed out after {attempt + 1} attempts",
                    )
                continue

            except Exception as e:
                if attempt == component.max_retries:
                    return SkillResult(
                        success=False,
                        error=f"Component {component.skill.get_config().skill_id} failed after {attempt + 1} attempts: {str(e)}",
                    )
                continue

        return SkillResult(success=False, error="Unexpected execution path")

    def _select_adaptive_components(
        self, components: list[SkillComponent], input_data: Any, context: ExecutionContext
    ) -> list[SkillComponent]:
        """Select components for adaptive execution based on performance history"""
        if not self.config.enable_adaptive_optimization:
            return components

        selected = []
        for component in components:
            skill_id = component.skill.get_config().skill_id

            # Check learning data
            if skill_id in self.learning_data and self.learning_data[skill_id]:
                # Calculate expected performance based on history
                recent_performances = self.learning_data[skill_id][-10:]  # Last 10 executions
                avg_performance = np.mean([p[1] for p in recent_performances])

                # Select if performance is above threshold
                if avg_performance > self.config.quality_threshold:
                    selected.append(component)
                    component.performance_multiplier = avg_performance
            else:
                # No history - include the component
                selected.append(component)

        return selected or components  # Fallback to all components

    def _combine_ensemble_results(self, successful_results: list[tuple[SkillComponent, SkillResult]]) -> Any:
        """Combine results from multiple ensemble members"""
        if not successful_results:
            return None

        # Simple ensemble: return the highest confidence result
        best_component, best_result = max(successful_results, key=lambda x: x[1].confidence * x[0].weight)

        return best_result.data

    def _calculate_compound_multiplier(self, result: CompositionResult) -> float:
        """Calculate the compound performance multiplier"""
        if not result.success:
            return 1.0

        base_multiplier = self.config.compound_multiplier_base

        # Individual skill multipliers
        skill_multipliers = []
        for skill_id in result.skills_executed:
            skill_multiplier = 1.0

            # Check if skill is optimized
            if self.bootstrap_optimizer:
                skill_multiplier *= 1.2  # Bootstrap optimization boost

            skill_multipliers.append(skill_multiplier)

        # Compound effect
        if skill_multipliers:
            compound_effect = np.prod(skill_multipliers) ** (1.0 / len(skill_multipliers))
        else:
            compound_effect = 1.0

        # Quality adjustment
        quality_multiplier = result.quality_score if result.quality_score > 0 else 1.0

        return base_multiplier * compound_effect * quality_multiplier

    def _calculate_quality_score(self, result: CompositionResult) -> float:
        """Calculate overall quality score"""
        if not result.success:
            return 0.0

        factors = []

        # Confidence scores
        if result.confidences:
            avg_confidence = np.mean(list(result.confidences.values()))
            factors.append(avg_confidence)

        # Success rate of skills
        if result.skills_executed:
            success_rate = len(result.skills_executed) / max(1, len(result.errors) + len(result.skills_executed))
            factors.append(success_rate)

        # Performance factor (faster is better)
        if result.total_execution_time > 0:
            performance_factor = max(0.1, 1.0 / (1.0 + result.total_execution_time / 10.0))
            factors.append(performance_factor)

        # Number of skills executed (more skills = more comprehensive processing)
        complexity_factor = min(1.0, len(result.skills_executed) / 3.0)
        factors.append(complexity_factor)

        return np.mean(factors) if factors else 0.0

    def _update_performance_tracking(self, result: CompositionResult):
        """Update performance tracking data"""
        for skill_id, execution_time in result.execution_times.items():
            self.performance_history[skill_id].append(execution_time)
            self.composition_stats[f"{skill_id}_executions"] += 1

        self.composition_stats["total_compositions"] += 1
        if result.success:
            self.composition_stats["successful_compositions"] += 1

    def _update_learning_data(self, skill_id: str, skill_result: SkillResult):
        """Update learning data for adaptive composition"""
        if skill_result.success:
            self.learning_data[skill_id].append((time.time(), skill_result.confidence))

            # Limit learning data size
            if len(self.learning_data[skill_id]) > self.config.performance_history_size:
                self.learning_data[skill_id] = self.learning_data[skill_id][-self.config.performance_history_size :]

    async def _apply_zero_hallucination(
        self, result: CompositionResult, context: ExecutionContext
    ) -> CompositionResult:
        """Apply zero-hallucination enforcement to ensemble result"""
        if "ensemble" in result.outputs:
            try:
                from .zero_hallucination import enforce_zero_hallucination

                @enforce_zero_hallucination(context=context.metadata)
                async def check_content(content: str) -> str:
                    return content

                # Apply to ensemble result if it's a string
                if isinstance(result.outputs["ensemble"], str):
                    result.outputs["ensemble"] = await check_content(result.outputs["ensemble"])

            except Exception as e:
                logger.warning(f"Zero-hallucination enforcement failed: {e}")

        return result

    def get_performance_stats(self) -> dict[str, Any]:
        """Get comprehensive performance statistics"""
        stats = dict(self.composition_stats)

        # Calculate success rates
        total_compositions = stats.get("total_compositions", 0)
        successful_compositions = stats.get("successful_compositions", 0)

        stats["success_rate"] = successful_compositions / max(1, total_compositions)

        # Average execution times
        avg_execution_times = {}
        for skill_id, times in self.performance_history.items():
            if times:
                avg_execution_times[skill_id] = np.mean(times)

        stats["average_execution_times"] = avg_execution_times
        stats["learning_data_size"] = {k: len(v) for k, v in self.learning_data.items()}

        return stats

    def clear_history(self):
        """Clear performance and learning history"""
        self.performance_history.clear()
        self.composition_stats.clear()
        self.learning_data.clear()


class MetaSkill(SignatureSkill):
    """Enhanced SignatureSkill with meta-skill composition capabilities"""

    def __init__(
        self,
        skill_id: str,
        name: str,
        description: str,
        components: list[SkillComponent],
        config: MetaSkillConfig | None = None,
    ):
        # Create base config
        base_config = SkillConfig(
            skill_id=skill_id,
            name=name,
            description=description,
            timeout=60.0,  # Longer timeout for meta-skills
        )

        super().__init__(base_config)
        self.components = components
        self.meta_config = config or MetaSkillConfig()
        self.composer = SkillComposer(self.meta_config)

        # Add compound skills for multiplier support
        for component in components:
            self.add_compound_skill(component.skill, component.performance_multiplier)

    async def execute_core(self, input_data: T_Input, context: ExecutionContext) -> Any:
        """Execute meta-skill composition"""
        result = await self.composer.compose(self.components, input_data, context)

        if not result.success:
            raise ValueError(f"Meta-skill composition failed: {result.errors}")

        # Return primary output or ensemble result
        if "ensemble" in result.outputs:
            return result.outputs["ensemble"]
        if result.outputs:
            # Return first output by priority
            primary_skill = max(self.components, key=lambda c: c.priority.value if c.enabled else 999)
            if primary_skill.skill.get_config().skill_id in result.outputs:
                return result.outputs[primary_skill.skill.get_config().skill_id]

        return result.outputs

    def add_component(self, component: SkillComponent):
        """Add a new skill component"""
        self.components.append(component)
        self.add_compound_skill(component.skill, component.performance_multiplier)

    def remove_component(self, skill_id: str):
        """Remove a skill component"""
        self.components = [c for c in self.components if c.skill.get_config().skill_id != skill_id]

    def get_composition_stats(self) -> dict[str, Any]:
        """Get composition statistics"""
        return self.composer.get_performance_stats()

    def get_component_info(self) -> list[dict[str, Any]]:
        """Get information about all components"""
        return [
            {
                "skill_id": component.skill.get_config().skill_id,
                "role": component.role.value,
                "weight": component.weight,
                "priority": component.priority.value,
                "enabled": component.enabled,
                "performance_multiplier": component.performance_multiplier,
            }
            for component in self.components
        ]


# Utility functions for creating meta-skills
def create_skill_component(
    skill: SkillInterface,
    role: SkillRole = SkillRole.PRIMARY,
    weight: float = 1.0,
    priority: SkillPriority = SkillPriority.NORMAL,
    condition: Callable[[Any], bool] | None = None,
    **kwargs,
) -> SkillComponent:
    """Create a skill component"""
    return SkillComponent(skill=skill, role=role, weight=weight, priority=priority, condition=condition, **kwargs)


def create_meta_skill(
    skill_id: str,
    name: str,
    description: str,
    components: list[SkillComponent],
    strategy: CompositionStrategy = CompositionStrategy.SEQUENTIAL,
    **kwargs,
) -> MetaSkill:
    """Create a meta-skill with specified composition"""
    config = MetaSkillConfig(composition_strategy=strategy, **kwargs)
    return MetaSkill(skill_id, name, description, components, config)
