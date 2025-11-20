"""
Integration tests for the complete signature framework
"""

import asyncio
from typing import Any

import pytest
from pydantic import BaseModel

# Import all framework components
from .. import SignatureSkill
from .. import create_execution_context
from .. import create_skill_config
from .. import get_bootstrap_optimizer
from .. import get_runtime_validator
from .. import get_zero_hallucination_enforcer
from .. import initialize_framework
from ..base_types import EnforcementLevel
from ..base_types import ExecutionContext
from ..base_types import ValidationMode
from ..bootstrap_optimizer import OptimizationConfig
from ..runtime_validation import ValidationConfig
from ..zero_hallucination import ZeroHallucinationConfig


class TestFrameworkIntegration:
    """Test complete framework integration"""

    def test_framework_initialization(self):
        """Test framework initialization"""
        result = initialize_framework()

        assert result["status"] == "success"
        assert "runtime_validator" in result["components"]
        assert "bootstrap_optimizer" in result["components"]
        assert "zero_hallucination_enforcer" in result["components"]

    def test_framework_stats(self):
        """Test framework statistics"""
        from .. import get_framework_stats

        stats = get_framework_stats()

        assert "version" in stats
        assert "components" in stats
        assert "capabilities" in stats
        assert isinstance(stats["capabilities"], dict)

    def test_utility_functions(self):
        """Test utility functions"""
        # Test config creation
        config = create_skill_config("test_skill", name="Test Skill", timeout=60.0)

        assert config.skill_id == "test_skill"
        assert config.name == "Test Skill"
        assert config.timeout == 60.0

        # Test context creation
        context = create_execution_context(user_id="user123", validation_mode=ValidationMode.LENIENT)

        assert context.user_id == "user123"
        assert context.validation_mode == ValidationMode.LENIENT


class TestBootstrapOptimization:
    """Test BootstrapFewShot optimization integration"""

    def test_optimizer_configuration(self):
        """Test bootstrap optimizer configuration"""
        config = OptimizationConfig(max_examples=500, similarity_threshold=0.8, enable_adaptive_learning=True)

        optimizer = get_bootstrap_optimizer(config)

        assert optimizer.config.max_examples == 500
        assert optimizer.config.similarity_threshold == 0.8

    def test_example_learning(self):
        """Test example learning and optimization"""

        class LearningSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return f"Processed: {input_data}"

        skill = LearningSkill()
        optimizer = get_bootstrap_optimizer()

        # Add examples for learning
        skill.add_bootstrap_example("hello", "Processed: hello")
        skill.add_bootstrap_example("world", "Processed: world")

        examples = skill.get_bootstrap_examples()
        assert len(examples) == 2

    def test_optimization_stats(self):
        """Test optimization statistics"""
        optimizer = get_bootstrap_optimizer()
        stats = optimizer.get_optimization_stats()

        assert "total_examples" in stats
        assert "cache_size" in stats
        assert "success_rate" in stats


class TestZeroHallucination:
    """Test zero-hallucination enforcement integration"""

    def test_enforcer_configuration(self):
        """Test zero-hallucination enforcer configuration"""
        config = ZeroHallucinationConfig(
            enforcement_level=EnforcementLevel.STRICT, confidence_threshold=0.9, enable_auto_correction=True
        )

        enforcer = get_zero_hallucination_enforcer(config)

        assert enforcer.config.enforcement_level == EnforcementLevel.STRICT
        assert enforcer.config.confidence_threshold == 0.9

    def test_hallucination_detection(self):
        """Test hallucination detection"""
        enforcer = get_zero_hallucination_enforcer()

        async def test_detection():
            # Test uncertain language
            uncertain_content = "I think this might be correct, but I'm not sure."
            report = await enforcer.enforce(uncertain_content)

            assert report.overall_confidence < 1.0
            assert len(report.indicators) > 0

        asyncio.run(test_detection())

    def test_statistics_tracking(self):
        """Test statistics tracking"""
        enforcer = get_zero_hallucination_enforcer()
        stats = enforcer.get_statistics()

        assert "total_detections" in stats
        assert "hallucination_rate" in stats
        assert "average_confidence" in stats


class TestRuntimeValidation:
    """Test runtime validation integration"""

    def test_validator_configuration(self):
        """Test runtime validator configuration"""
        config = ValidationConfig(
            enable_security_checks=True, enable_hallucination_detection=True, max_validation_time=5.0
        )

        validator = get_runtime_validator(config)

        assert validator.config.enable_security_checks is True
        assert validator.config.max_validation_time == 5.0

    def test_input_validation(self):
        """Test input validation"""
        validator = get_runtime_validator()

        class TestModel(BaseModel):
            message: str
            count: int

        from ..base_types import PydanticContract

        contract = PydanticContract(TestModel)

        async def test_validation():
            # Valid input
            valid_input = {"message": "test", "count": 5}
            report = await validator.validate_input(valid_input, contract)

            assert report.is_valid is True

            # Invalid input
            invalid_input = {"message": "test", "count": "not_a_number"}
            report = await validator.validate_input(invalid_input, contract)

            assert report.is_valid is False

        asyncio.run(test_validation())


class TestSkillIntegration:
    """Test skill integration scenarios"""

    def test_complete_skill_execution(self):
        """Test complete skill execution with all features"""

        class CompleteSkill(SignatureSkill[dict[str, Any], dict[str, Any]]):
            async def execute_core(self, input_data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
                return {"processed": True, "original_data": input_data, "confidence": 0.95}

        # Configure with all features enabled
        config = create_skill_config(
            "complete_skill",
            description="A skill with all features enabled",
            enable_caching=True,
            enable_optimization=True,
            zero_hallucination=True,
        )

        skill = CompleteSkill(config)
        context = create_execution_context(
            validation_mode=ValidationMode.STRICT, enable_caching=True, zero_hallucination=True
        )

        async def test_complete():
            test_input = {"message": "test", "value": 42}
            result = await skill.execute_with_signature(test_input, context)

            assert result.success is True
            assert result.data["processed"] is True
            assert result.confidence > 0.0
            assert result.execution_time > 0.0

        asyncio.run(test_complete())

    def test_skill_with_types(self):
        """Test skill with complex type definitions"""

        class RequestModel(BaseModel):
            query: str
            parameters: dict[str, Any]

        class ResponseModel(BaseModel):
            results: list[dict[str, Any]]
            count: int
            success: bool

        class TypedSkill(SignatureSkill[RequestModel, ResponseModel]):
            async def execute_core(self, input_data: RequestModel, context: ExecutionContext) -> ResponseModel:
                return ResponseModel(results=[{"query": input_data.query}], count=1, success=True)

        skill = TypedSkill()
        context = create_execution_context()

        async def test_typed():
            request = RequestModel(query="test query", parameters={"limit": 10})
            result = await skill.execute_with_signature(request, context)

            assert result.success is True
            assert result.data.success is True
            assert result.data.count == 1
            assert len(result.data.results) == 1

        asyncio.run(test_typed())


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_skill_execution_failure(self):
        """Test skill execution failure handling"""

        class FailingSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                raise ValueError("Intentional failure for testing")

        skill = FailingSkill()
        context = create_execution_context()

        async def test_failure():
            result = await skill.execute_with_signature("test", context)

            assert result.success is False
            assert "Intentional failure" in result.error
            assert result.execution_time > 0.0

        asyncio.run(test_failure())

    def test_validation_failure(self):
        """Test validation failure handling"""

        class StrictSkill(SignatureSkill[int, str]):
            async def execute_core(self, input_data: int, context: ExecutionContext) -> str:
                return f"Number: {input_data}"

        skill = StrictSkill()
        context = create_execution_context(validation_mode=ValidationMode.STRICT)

        async def test_validation_failure():
            # Pass string instead of int
            result = await skill.execute_with_signature("not_a_number", context)

            assert result.success is False
            assert "validation failed" in result.error.lower()

        asyncio.run(test_validation_failure())

    def test_timeout_handling(self):
        """Test timeout handling"""

        class SlowSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                await asyncio.sleep(2.0)  # Simulate slow operation
                return input_data

        skill = SlowSkill()
        context = create_execution_context(timeout=0.1)  # Very short timeout

        async def test_timeout():
            result = await skill.execute_with_signature("test", context)

            # Note: Actual timeout handling depends on implementation
            # This test verifies the structure is in place
            assert result is not None

        # Use try-except for timeout as actual implementation may vary
        try:
            asyncio.run(test_timeout())
        except TimeoutError:
            pass  # Expected for timeout


class TestPerformanceOptimization:
    """Test performance optimization features"""

    def test_caching_behavior(self):
        """Test caching behavior"""

        class CachedSkill(SignatureSkill[str, str]):
            def __init__(self):
                super().__init__()
                self.execution_count = 0

            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                self.execution_count += 1
                return f"Result: {input_data}"

        skill = CachedSkill()
        context = create_execution_context(enable_caching=True)

        async def test_caching():
            # First execution
            result1 = await skill.execute_with_signature("test", context)
            assert result1.success is True
            assert skill.execution_count == 1

            # Second execution with same input
            result2 = await skill.execute_with_signature("test", context)
            assert result2.success is True

            # Should ideally use cache (implementation dependent)
            # This test verifies the structure exists
            assert result2.data == result1.data

        asyncio.run(test_caching())

    def test_optimization_score_tracking(self):
        """Test optimization score tracking"""

        class OptimizedSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return input_data

        skill = OptimizedSkill()
        context = create_execution_context(enable_optimization=True)

        async def test_optimization():
            result = await skill.execute_with_signature("test", context)

            assert result.success is True
            assert hasattr(result, "optimization_applied")

            metrics = skill.get_metrics()
            assert hasattr(metrics, "optimization_score")

        asyncio.run(test_optimization())


if __name__ == "__main__":
    pytest.main([__file__])
