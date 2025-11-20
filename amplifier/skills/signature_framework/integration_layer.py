"""
Integration Layer for Existing Skills

Seamless integration system that allows existing skills to benefit from
the signature framework without requiring complete rewrites. Provides
backward compatibility and smooth migration paths.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Union
from typing import get_args
from typing import get_origin
from typing import get_type_hints

# Import existing skill system
from ..skills_framework.base_skill import BaseSkill
from ..skills_framework.base_skill import SkillContext
from ..skills_framework.base_skill import SkillResult as LegacySkillResult

# Import new signature framework
from .base_types import ExecutionContext
from .base_types import SkillConfig
from .base_types import SkillResult
from .base_types import ValidationMode
from .skill_signature import SignatureSkill

logger = logging.getLogger(__name__)


class MigrationStrategy(Enum):
    """Strategies for migrating existing skills"""

    WRAPPER = "wrapper"  # Wrap existing skill with signature framework
    HYBRID = "hybrid"  # Use both systems in parallel
    GRADUAL = "gradual"  # Gradually migrate to new system
    LEGACY_ONLY = "legacy_only"  # Keep using legacy system only


@dataclass
class MigrationConfig:
    """Configuration for skill migration"""

    strategy: MigrationStrategy = MigrationStrategy.WRAPPER
    enable_bootstrap_optimization: bool = True
    enable_zero_hallucination: bool = True
    enable_runtime_validation: bool = True
    performance_monitoring: bool = True
    fallback_on_failure: bool = True
    migration_timeout: float = 30.0
    preserve_original_behavior: bool = True


@dataclass
class MigrationReport:
    """Report on migration results and performance"""

    skill_id: str
    migration_strategy: MigrationStrategy
    original_performance: dict[str, float] = field(default_factory=dict)
    new_performance: dict[str, float] = field(default_factory=dict)
    performance_improvement: float = 0.0
    compatibility_score: float = 1.0
    issues_detected: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    migration_successful: bool = False


class LegacySkillWrapper(SignatureSkill):
    """Wrapper that adapts legacy BaseSkill to SignatureSkill interface"""

    def __init__(
        self,
        legacy_skill: BaseSkill,
        config: SkillConfig | None = None,
        migration_config: MigrationConfig | None = None,
    ):
        # Create config from legacy skill if not provided
        if config is None:
            config = SkillConfig(
                skill_id=legacy_skill.skill_id,
                name=legacy_skill.name,
                description=legacy_skill.description,
                timeout=30.0,
                enable_optimization=migration_config.enable_bootstrap_optimization if migration_config else True,
                zero_hallucination=migration_config.enable_zero_hallucination if migration_config else True,
            )

        super().__init__(config)
        self.legacy_skill = legacy_skill
        self.migration_config = migration_config or MigrationConfig()
        self.migration_stats = {
            "legacy_executions": 0,
            "signature_executions": 0,
            "legacy_failures": 0,
            "signature_failures": 0,
            "fallback_count": 0,
        }

        # Detect types from legacy skill
        self._detect_legacy_types()

    def _detect_legacy_types(self):
        """Detect input/output types from legacy skill"""
        try:
            # Get type hints from execute method
            type_hints = get_type_hints(self.legacy_skill.execute)

            if "input_data" in type_hints:
                input_type = type_hints["input_data"]
                self._input_contract = self._create_contract_from_type(input_type)

            # Try to get return type from method signature or docstring
            if (
                hasattr(self.legacy_skill.execute, "__annotations__")
                and "return" in self.legacy_skill.execute.__annotations__
            ):
                output_type = self.legacy_skill.execute.__annotations__["return"]
                # Handle coroutine return types
                if get_origin(output_type) is not None:
                    args = get_args(output_type)
                    if args:
                        output_type = args[0]
                self._output_contract = self._create_contract_from_type(output_type)

        except Exception as e:
            logger.warning(f"Could not detect types for skill {self.legacy_skill.skill_id}: {e}")

    async def execute_core(self, input_data: Any, context: ExecutionContext) -> Any:
        """Execute using legacy skill with signature framework benefits"""
        self.migration_stats["signature_executions"] += 1

        try:
            # Convert context to legacy format
            legacy_context = self._convert_context(context)

            # Execute legacy skill
            if self.migration_config.preserve_original_behavior:
                # Use original execution method
                result = await self.legacy_skill.execute(input_data, legacy_context)
            else:
                # Use monitored execution for performance tracking
                result = await self.legacy_skill.run_with_monitoring(input_data, legacy_context)

            # Extract data from legacy result
            if isinstance(result, LegacySkillResult):
                return result.data
            return result

        except Exception:
            self.migration_stats["signature_failures"] += 1

            # Fallback to direct legacy execution if enabled
            if self.migration_config.fallback_on_failure:
                self.migration_stats["fallback_count"] += 1
                try:
                    legacy_context = self._convert_context(context)
                    result = await self.legacy_skill.execute(input_data, legacy_context)
                    if isinstance(result, LegacySkillResult):
                        return result.data
                    return result
                except Exception as fallback_error:
                    logger.error(f"Fallback execution failed for skill {self.legacy_skill.skill_id}: {fallback_error}")
                    raise

            raise

    def _convert_context(self, context: ExecutionContext) -> SkillContext:
        """Convert signature framework context to legacy context"""
        return SkillContext(user_id=context.user_id, session_id=context.session_id, metadata=context.metadata)


class HybridSkillExecutor:
    """Executes skills using both legacy and signature systems for comparison"""

    def __init__(self, legacy_skill: BaseSkill, signature_skill: SignatureSkill, comparison_mode: bool = True):
        self.legacy_skill = legacy_skill
        self.signature_skill = signature_skill
        self.comparison_mode = comparison_mode
        self.comparison_stats = {
            "total_comparisons": 0,
            "legacy_success_rate": 0.0,
            "signature_success_rate": 0.0,
            "performance_improvement": 0.0,
            "agreement_rate": 0.0,
        }

    async def execute_with_comparison(self, input_data: Any, context: ExecutionContext) -> SkillResult:
        """Execute with both systems and compare results"""
        start_time = time.time()

        # Execute both systems in parallel
        try:
            legacy_context = self._convert_context(context)

            # Run both executions
            legacy_task = self.legacy_skill.run_with_monitoring(input_data, legacy_context)
            signature_task = self.signature_skill.execute_with_signature(input_data, context)

            legacy_result, signature_result = await asyncio.gather(legacy_task, signature_task, return_exceptions=True)

            # Analyze results
            comparison = self._compare_results(legacy_result, signature_result)

            # Update statistics
            self._update_comparison_stats(comparison)

            # Decide which result to return
            if isinstance(legacy_result, Exception) and isinstance(signature_result, Exception):
                return SkillResult(success=False, error="Both execution systems failed")

            if isinstance(legacy_result, Exception):
                return signature_result

            if isinstance(signature_result, Exception):
                # Convert legacy result to signature format
                return self._convert_legacy_result(legacy_result)

            # Both succeeded - use signature result with comparison metadata
            signature_result.metadata["comparison"] = comparison
            signature_result.metadata["execution_mode"] = "hybrid"

            return signature_result

        except Exception as e:
            execution_time = time.time() - start_time
            return SkillResult(success=False, error=f"Hybrid execution failed: {str(e)}", execution_time=execution_time)

    def _compare_results(
        self, legacy_result: Union[LegacySkillResult, Exception], signature_result: Union[SkillResult, Exception]
    ) -> dict[str, Any]:
        """Compare results from both execution systems"""
        self.comparison_stats["total_comparisons"] += 1

        comparison = {
            "timestamp": time.time(),
            "legacy_success": not isinstance(legacy_result, Exception),
            "signature_success": not isinstance(signature_result, Exception),
            "agreement": False,
            "performance_diff": 0.0,
        }

        # Compare success status
        legacy_success = not isinstance(legacy_result, Exception)
        signature_success = not isinstance(signature_result, Exception)

        if legacy_success and signature_success:
            # Both succeeded - compare outputs and performance
            if isinstance(legacy_result, LegacySkillResult) and isinstance(signature_result, SkillResult):
                comparison["execution_time_legacy"] = legacy_result.execution_time
                comparison["execution_time_signature"] = signature_result.execution_time
                comparison["performance_diff"] = (legacy_result.execution_time - signature_result.execution_time) / max(
                    0.001, legacy_result.execution_time
                )

                # Simple output comparison
                try:
                    comparison["agreement"] = str(legacy_result.data) == str(signature_result.data)
                except Exception:
                    comparison["agreement"] = False

                comparison["tokens_used_legacy"] = legacy_result.tokens_used
                comparison["tokens_used_signature"] = signature_result.tokens_used

        return comparison

    def _update_comparison_stats(self, comparison: dict[str, Any]):
        """Update comparison statistics"""
        total = self.comparison_stats["total_comparisons"]

        if comparison["legacy_success"]:
            self.comparison_stats["legacy_success_rate"] = (
                self.comparison_stats["legacy_success_rate"] * (total - 1) + 1.0
            ) / total

        if comparison["signature_success"]:
            self.comparison_stats["signature_success_rate"] = (
                self.comparison_stats["signature_success_rate"] * (total - 1) + 1.0
            ) / total

        if comparison["performance_diff"]:
            self.comparison_stats["performance_improvement"] = (
                self.comparison_stats["performance_improvement"] * (total - 1) + comparison["performance_diff"]
            ) / total

        if "agreement" in comparison:
            self.comparison_stats["agreement_rate"] = (
                self.comparison_stats["agreement_rate"] * (total - 1) + (1.0 if comparison["agreement"] else 0.0)
            ) / total

    def _convert_context(self, context: ExecutionContext) -> SkillContext:
        """Convert signature framework context to legacy context"""
        return SkillContext(user_id=context.user_id, session_id=context.session_id, metadata=context.metadata)

    def _convert_legacy_result(self, legacy_result: LegacySkillResult) -> SkillResult:
        """Convert legacy skill result to signature result format"""
        return SkillResult(
            success=legacy_result.success,
            data=legacy_result.data,
            error=legacy_result.error,
            execution_time=legacy_result.execution_time,
            tokens_used=legacy_result.tokens_used,
            metadata={"source": "legacy_system", **legacy_result.metadata},
        )

    def get_comparison_report(self) -> dict[str, Any]:
        """Get comprehensive comparison report"""
        return {
            "skill_id": self.legacy_skill.skill_id,
            "total_comparisons": self.comparison_stats["total_comparisons"],
            "legacy_success_rate": self.comparison_stats["legacy_success_rate"],
            "signature_success_rate": self.comparison_stats["signature_success_rate"],
            "performance_improvement": self.comparison_stats["performance_improvement"],
            "agreement_rate": self.comparison_stats["agreement_rate"],
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> list[str]:
        """Generate migration recommendations based on comparison data"""
        recommendations = []

        if self.comparison_stats["signature_success_rate"] > self.comparison_stats["legacy_success_rate"]:
            recommendations.append("Signature system shows higher success rate - consider full migration")

        if self.comparison_stats["performance_improvement"] > 0.1:
            recommendations.append("Signature system shows significant performance improvement")

        if self.comparison_stats["agreement_rate"] < 0.8:
            recommendations.append("Results differ between systems - investigate discrepancies")

        if self.comparison_stats["signature_success_rate"] < 0.9:
            recommendations.append("Signature system reliability needs improvement before migration")

        return recommendations


class SkillMigrationManager:
    """Manages migration of legacy skills to signature framework"""

    def __init__(self):
        self.migrations: dict[str, MigrationReport] = {}
        self.active_wrappers: dict[str, LegacySkillWrapper] = {}
        self.active_hybrids: dict[str, HybridSkillExecutor] = {}

    async def migrate_skill(
        self,
        legacy_skill: BaseSkill,
        migration_config: MigrationConfig | None = None,
        test_inputs: list[Any] | None = None,
    ) -> MigrationReport:
        """Migrate a legacy skill to the signature framework"""
        skill_id = legacy_skill.skill_id
        migration_config = migration_config or MigrationConfig()

        logger.info(f"Starting migration for skill: {skill_id}")

        # Create migration report
        report = MigrationReport(skill_id=skill_id, migration_strategy=migration_config.strategy)

        try:
            # Benchmark original performance
            if test_inputs:
                report.original_performance = await self._benchmark_legacy_skill(legacy_skill, test_inputs)

            # Apply migration strategy
            if migration_config.strategy == MigrationStrategy.WRAPPER:
                wrapper = await self._create_wrapper(legacy_skill, migration_config)
                self.active_wrappers[skill_id] = wrapper

                if test_inputs:
                    report.new_performance = await self._benchmark_signature_skill(wrapper, test_inputs)

                report.migration_successful = True
                report.recommendations.append("Skill successfully wrapped with signature framework")

            elif migration_config.strategy == MigrationStrategy.HYBRID:
                wrapper = await self._create_wrapper(legacy_skill, migration_config)
                hybrid = HybridSkillExecutor(legacy_skill, wrapper)
                self.active_hybrids[skill_id] = hybrid

                if test_inputs:
                    # Benchmark hybrid mode
                    hybrid_report = hybrid.get_comparison_report()
                    report.new_performance = {
                        "hybrid_success_rate": hybrid_report["signature_success_rate"],
                        "performance_improvement": hybrid_report["performance_improvement"],
                    }

                report.migration_successful = True
                report.recommendations.extend(hybrid._generate_recommendations())

            else:
                report.issues_detected.append(f"Migration strategy {migration_config.strategy} not implemented")
                report.migration_successful = False

            # Calculate performance improvement
            if report.original_performance and report.new_performance:
                report.performance_improvement = self._calculate_performance_improvement(
                    report.original_performance, report.new_performance
                )

        except Exception as e:
            logger.error(f"Migration failed for skill {skill_id}: {e}")
            report.issues_detected.append(f"Migration error: {str(e)}")
            report.migration_successful = False

        # Store report
        self.migrations[skill_id] = report

        return report

    async def _create_wrapper(self, legacy_skill: BaseSkill, migration_config: MigrationConfig) -> LegacySkillWrapper:
        """Create a wrapper for the legacy skill"""
        config = SkillConfig(
            skill_id=legacy_skill.skill_id,
            name=legacy_skill.name,
            description=f"Migrated skill: {legacy_skill.description}",
            enable_optimization=migration_config.enable_bootstrap_optimization,
            zero_hallucination=migration_config.enable_zero_hallucination,
        )

        return LegacySkillWrapper(legacy_skill, config, migration_config)

    async def _benchmark_legacy_skill(self, legacy_skill: BaseSkill, test_inputs: list[Any]) -> dict[str, float]:
        """Benchmark legacy skill performance"""
        results = []
        total_time = 0
        successful_runs = 0

        for test_input in test_inputs:
            context = SkillContext()
            start_time = time.time()

            try:
                result = await legacy_skill.run_with_monitoring(test_input, context)
                execution_time = time.time() - start_time

                results.append(
                    {"success": result.success, "execution_time": execution_time, "tokens_used": result.tokens_used}
                )

                total_time += execution_time
                if result.success:
                    successful_runs += 1

            except Exception as e:
                results.append({"success": False, "error": str(e), "execution_time": time.time() - start_time})

        return {
            "success_rate": successful_runs / len(test_inputs) if test_inputs else 0,
            "average_execution_time": total_time / len(test_inputs) if test_inputs else 0,
            "total_tests": len(test_inputs),
            "successful_runs": successful_runs,
        }

    async def _benchmark_signature_skill(
        self, signature_skill: SignatureSkill, test_inputs: list[Any]
    ) -> dict[str, float]:
        """Benchmark signature skill performance"""
        context = create_execution_context(validation_mode=ValidationMode.STRICT)
        results = []
        total_time = 0
        successful_runs = 0
        optimization_count = 0

        for test_input in test_inputs:
            start_time = time.time()

            try:
                result = await signature_skill.execute_with_signature(test_input, context)
                execution_time = time.time() - start_time

                results.append(
                    {
                        "success": result.success,
                        "execution_time": execution_time,
                        "confidence": result.confidence,
                        "optimization_applied": result.optimization_applied,
                        "cache_hit": result.cache_hit,
                    }
                )

                total_time += execution_time
                if result.success:
                    successful_runs += 1
                if result.optimization_applied:
                    optimization_count += 1

            except Exception as e:
                results.append({"success": False, "error": str(e), "execution_time": time.time() - start_time})

        return {
            "success_rate": successful_runs / len(test_inputs) if test_inputs else 0,
            "average_execution_time": total_time / len(test_inputs) if test_inputs else 0,
            "average_confidence": sum(r.get("confidence", 0) for r in results) / len(results) if results else 0,
            "optimization_rate": optimization_count / len(test_inputs) if test_inputs else 0,
            "total_tests": len(test_inputs),
            "successful_runs": successful_runs,
        }

    def _calculate_performance_improvement(self, original: dict[str, float], new: dict[str, float]) -> float:
        """Calculate performance improvement percentage"""
        # Use execution time improvement as primary metric
        original_time = original.get("average_execution_time", 1.0)
        new_time = new.get("average_execution_time", 1.0)

        if original_time == 0:
            return 0.0

        improvement = (original_time - new_time) / original_time
        return max(0.0, improvement)  # Only positive improvements

    def get_migration_status(self, skill_id: str) -> MigrationReport | None:
        """Get migration status for a specific skill"""
        return self.migrations.get(skill_id)

    def get_all_migrations(self) -> dict[str, MigrationReport]:
        """Get all migration reports"""
        return self.migrations.copy()

    def get_wrapped_skill(self, skill_id: str) -> LegacySkillWrapper | None:
        """Get a wrapped skill instance"""
        return self.active_wrappers.get(skill_id)

    def get_hybrid_executor(self, skill_id: str) -> HybridSkillExecutor | None:
        """Get a hybrid executor instance"""
        return self.active_hybrids.get(skill_id)


# Global migration manager
_migration_manager = None


def get_migration_manager() -> SkillMigrationManager:
    """Get the global migration manager"""
    global _migration_manager
    if _migration_manager is None:
        _migration_manager = SkillMigrationManager()
    return _migration_manager


# Utility functions
async def migrate_skill(
    legacy_skill: BaseSkill, migration_config: MigrationConfig | None = None, test_inputs: list[Any] | None = None
) -> MigrationReport:
    """Convenience function to migrate a single skill"""
    manager = get_migration_manager()
    return await manager.migrate_skill(legacy_skill, migration_config, test_inputs)


def wrap_legacy_skill(legacy_skill: BaseSkill, config: SkillConfig | None = None) -> LegacySkillWrapper:
    """Create a wrapper for a legacy skill"""
    migration_config = MigrationConfig(strategy=MigrationStrategy.WRAPPER)
    return LegacySkillWrapper(legacy_skill, config, migration_config)


def create_hybrid_executor(legacy_skill: BaseSkill, config: SkillConfig | None = None) -> HybridSkillExecutor:
    """Create a hybrid executor for comparing legacy and signature systems"""
    wrapper = wrap_legacy_skill(legacy_skill, config)
    return HybridSkillExecutor(legacy_skill, wrapper)


# Import necessary functions
from . import create_execution_context
