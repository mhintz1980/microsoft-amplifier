"""
Signature Framework for Skills

Core framework implementing type-safe, zero-hallucination skill execution
with BootstrapFewShot optimization and Agent Lightning integration.

This framework provides:
- Type-safe input/output contracts with Pydantic integration
- Zero-hallucination enforcement with comprehensive detection
- BootstrapFewShot optimization for 20-30x performance improvements
- Runtime validation with security and quality checks
- Compound multipliers and meta-skill integration
- Progressive disclosure documentation support

Usage:
    from amplifier.skills.signature_framework import SignatureSkill, SkillConfig

    class MySkill(SignatureSkill[str, str]):
        async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
            return f"Processed: {input_data}"
"""

from typing import Optional
import time

# Core framework components
from .base_types import ConfidenceLevel
from .base_types import ExecutionContext
from .base_types import OptimizationFunction
from .base_types import PydanticContract
from .base_types import SkillConfig
from .base_types import SkillHandler
from .base_types import SkillInterface  # Core types and interfaces
from .base_types import SkillMetrics
from .base_types import SkillPriority
from .base_types import SkillResult
from .base_types import SkillSignature
from .base_types import T_Input  # Utility types
from .base_types import T_Output
from .base_types import TypeContract  # Contracts and validation
from .base_types import ValidationFunction
from .base_types import ValidationMode
from .base_types import ValidationResult
from .bootstrap_optimizer import BootstrapExample
from .bootstrap_optimizer import BootstrapOptimizer  # Bootstrap optimization
from .bootstrap_optimizer import FeatureExtractor  # Feature extraction and similarity
from .bootstrap_optimizer import OptimizationConfig
from .bootstrap_optimizer import OptimizationResult
from .bootstrap_optimizer import OptimizationStrategy
from .bootstrap_optimizer import SimilarityCalculator
from .bootstrap_optimizer import SimilarityMetric
from .bootstrap_optimizer import get_bootstrap_optimizer  # Utilities
from .runtime_validation import RuntimeValidator  # Validation system
from .runtime_validation import ValidationConfig
from .runtime_validation import ValidationIssue
from .runtime_validation import ValidationLevel
from .runtime_validation import ValidationReport
from .runtime_validation import ValidationRule
from .runtime_validation import get_runtime_validator  # Utilities
from .runtime_validation import validate_output
from .skill_signature import SignatureSkill  # Main skill classes
from .skill_signature import signature_skill
from .zero_hallucination import ConfidenceLevel
from .zero_hallucination import ContextVerifier
from .zero_hallucination import EnforcementLevel
from .zero_hallucination import HallucinationIndicator
from .zero_hallucination import HallucinationPatterns
from .zero_hallucination import HallucinationReport
from .zero_hallucination import HallucinationType
from .zero_hallucination import ZeroHallucinationConfig
from .zero_hallucination import ZeroHallucinationEnforcer  # Zero-hallucination system
from .zero_hallucination import enforce_zero_hallucination
from .zero_hallucination import get_zero_hallucination_enforcer  # Utilities

# Version and metadata
__version__ = "1.0.0"
__author__ = "Amplifier Skills Framework Team"
__description__ = "Type-safe, zero-hallucination skill framework with BootstrapFewShot optimization"

# Public API
__all__ = [
    # Core framework
    "SignatureSkill",
    "SkillInterface",
    "SkillSignature",
    "ExecutionContext",
    "SkillResult",
    "SkillConfig",
    "SkillMetrics",
    "signature_skill",
    # Type system
    "T_Input",
    "T_Output",
    "TypeContract",
    "PydanticContract",
    "ValidationResult",
    "ValidationMode",
    "ConfidenceLevel",
    "SkillPriority",
    # Validation
    "RuntimeValidator",
    "ValidationConfig",
    "ValidationReport",
    "ValidationIssue",
    "ValidationLevel",
    "ValidationRule",
    "get_runtime_validator",
    "validate_output",
    # Bootstrap optimization
    "BootstrapOptimizer",
    "OptimizationConfig",
    "OptimizationResult",
    "OptimizationStrategy",
    "SimilarityMetric",
    "FeatureExtractor",
    "SimilarityCalculator",
    "BootstrapExample",
    "get_bootstrap_optimizer",
    # Zero-hallucination
    "ZeroHallucinationEnforcer",
    "HallucinationReport",
    "HallucinationIndicator",
    "HallucinationType",
    "EnforcementLevel",
    "ZeroHallucinationConfig",
    "HallucinationPatterns",
    "ContextVerifier",
    "get_zero_hallucination_enforcer",
    "enforce_zero_hallucination",
]


# Quick setup utilities
def create_skill_config(
    skill_id: str, name: Optional[str] = None, description: Optional[str] = None, **kwargs
) -> SkillConfig:
    """Create a skill configuration with sensible defaults"""
    return SkillConfig(
        skill_id=skill_id,
        name=name or skill_id,
        description=description or f"Signature-based skill: {skill_id}",
        **kwargs,
    )


def create_execution_context(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    validation_mode: ValidationMode = ValidationMode.STRICT,
    zero_hallucination: bool = True,
    **kwargs,
) -> ExecutionContext:
    """Create an execution context with common settings"""
    return ExecutionContext(
        user_id=user_id,
        session_id=session_id,
        validation_mode=validation_mode,
        zero_hallucination=zero_hallucination,
        **kwargs,
    )


# Framework statistics and health
def get_framework_stats() -> dict:
    """Get comprehensive framework statistics"""
    try:
        validator = get_runtime_validator()
        optimizer = get_bootstrap_optimizer()
        enforcer = get_zero_hallucination_enforcer()

        return {
            "version": __version__,
            "components": {
                "runtime_validator": validator.get_validation_stats(),
                "bootstrap_optimizer": optimizer.get_optimization_stats(),
                "zero_hallucination_enforcer": enforcer.get_statistics(),
            },
            "capabilities": {
                "type_contracts": True,
                "runtime_validation": True,
                "bootstrap_optimization": True,
                "zero_hallucination": True,
                "compound_multipliers": True,
                "progressive_disclosure": True,
            },
        }
    except Exception as e:
        return {"version": __version__, "error": str(e), "status": "initialization_incomplete"}


def initialize_framework(
    validation_config: Optional[ValidationConfig] = None,
    optimization_config: Optional[OptimizationConfig] = None,
    hallucination_config: Optional[ZeroHallucinationConfig] = None,
) -> dict:
    """Initialize all framework components with custom configurations"""
    try:
        # Initialize components
        validator = get_runtime_validator(validation_config)
        optimizer = get_bootstrap_optimizer(optimization_config)
        enforcer = get_zero_hallucination_enforcer(hallucination_config)

        return {
            "status": "success",
            "message": "Signature framework initialized successfully",
            "components": {
                "runtime_validator": "initialized",
                "bootstrap_optimizer": "initialized",
                "zero_hallucination_enforcer": "initialized",
            },
            "version": __version__,
        }
    except Exception as e:
        return {"status": "error", "message": f"Framework initialization failed: {str(e)}", "version": __version__}


# Performance optimization utilities
async def benchmark_skill(skill: SkillInterface, test_inputs: list, context: Optional[ExecutionContext] = None) -> dict:
    """Benchmark a skill's performance"""
    if not context:
        context = create_execution_context()

    results = []
    total_time = 0
    successful_runs = 0

    for test_input in test_inputs:
        start_time = time.time()
        try:
            result = await skill.execute_with_signature(test_input, context)
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

        except Exception as e:
            results.append({"success": False, "error": str(e), "execution_time": time.time() - start_time})

    return {
        "skill_id": skill.get_config().skill_id,
        "total_tests": len(test_inputs),
        "successful_runs": successful_runs,
        "success_rate": successful_runs / len(test_inputs) if test_inputs else 0,
        "average_execution_time": total_time / len(test_inputs) if test_inputs else 0,
        "total_execution_time": total_time,
        "detailed_results": results,
        "skill_metrics": skill.get_metrics().__dict__,
    }


# Export default configurations
DEFAULT_VALIDATION_CONFIG = ValidationConfig()
DEFAULT_OPTIMIZATION_CONFIG = OptimizationConfig()
DEFAULT_HALLUCINATION_CONFIG = ZeroHallucinationConfig()

# Logging configuration
import logging

# Create framework logger
framework_logger = logging.getLogger(__name__)
framework_logger.setLevel(logging.INFO)

# Prevent duplicate handlers
if not framework_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    framework_logger.addHandler(handler)


# Export the logger for external use
def get_framework_logger() -> logging.Logger:
    """Get the framework logger"""
    return framework_logger
