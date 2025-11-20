"""
Tests for skill signature implementation
"""

import asyncio
from typing import Any

import pytest
from pydantic import BaseModel

from ..base_types import ExecutionContext
from ..base_types import SkillConfig
from ..base_types import SkillMetrics
from ..base_types import ValidationMode
from ..skill_signature import SignatureSkill
from ..skill_signature import signature_skill


class TestSignatureSkill:
    """Test SignatureSkill class"""

    def test_skill_creation(self):
        """Test basic skill creation"""
        config = SkillConfig(skill_id="test_skill", name="Test Skill", description="A test skill")

        class TestSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return f"Processed: {input_data}"

        skill = TestSkill(config)

        assert skill.config.skill_id == "test_skill"
        assert skill.config.name == "Test Skill"
        assert isinstance(skill.metrics, SkillMetrics)

    def test_skill_execution(self):
        """Test basic skill execution"""

        class TestSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return f"Hello, {input_data}!"

        skill = TestSkill()
        context = ExecutionContext()

        async def test_execution():
            result = await skill.execute_with_signature("World", context)

            assert result.success is True
            assert result.data == "Hello, World!"
            assert result.confidence > 0.0
            assert result.execution_time > 0.0

        asyncio.run(test_execution())

    def test_skill_with_pydantic_types(self):
        """Test skill with Pydantic types"""

        class InputModel(BaseModel):
            message: str
            count: int

        class OutputModel(BaseModel):
            response: str
            processed_count: int

        class TypedSkill(SignatureSkill[InputModel, OutputModel]):
            async def execute_core(self, input_data: InputModel, context: ExecutionContext) -> OutputModel:
                return OutputModel(response=f"Processed: {input_data.message}", processed_count=input_data.count)

        skill = TypedSkill()
        context = ExecutionContext()

        async def test_typed_execution():
            input_data = InputModel(message="Test", count=5)
            result = await skill.execute_with_signature(input_data, context)

            assert result.success is True
            assert result.data.response == "Processed: Test"
            assert result.data.processed_count == 5

        asyncio.run(test_typed_execution())

    def test_bootstrap_examples(self):
        """Test bootstrap example functionality"""

        class TestSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return f"Processed: {input_data}"

        skill = TestSkill()

        # Add examples
        skill.add_bootstrap_example("input1", "output1")
        skill.add_bootstrap_example("input2", "output2")

        examples = skill.get_bootstrap_examples()
        assert len(examples) == 2
        assert examples[0]["input"] == "input1"
        assert examples[0]["output"] == "output1"

    def test_few_shot_configuration(self):
        """Test few-shot configuration"""

        class TestSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return f"Processed: {input_data}"

        skill = TestSkill()

        assert skill._few_shot_enabled is True

        skill.set_few_shot_enabled(False)
        assert skill._few_shot_enabled is False

    def test_compound_skills(self):
        """Test compound skill addition"""

        class TestSkill1(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return f"Skill1: {input_data}"

        class TestSkill2(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return f"Skill2: {input_data}"

        skill1 = TestSkill1()
        skill2 = TestSkill2()

        skill1.add_compound_skill(skill2, multiplier=1.5)

        assert len(skill1._compound_skills) == 1
        assert skill1._multiplier_applied == 1.5

    def test_optimization_info(self):
        """Test optimization information"""

        class TestSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return f"Processed: {input_data}"

        skill = TestSkill()

        # Add some examples
        skill.add_bootstrap_example("test", "output")

        optimization_info = skill.get_optimization_info()

        assert "bootstrap_examples_count" in optimization_info
        assert "few_shot_enabled" in optimization_info
        assert "compound_skills_count" in optimization_info
        assert optimization_info["bootstrap_examples_count"] == 1

    def test_cache_operations(self):
        """Test cache operations"""

        class TestSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return f"Processed: {input_data}"

        skill = TestSkill()

        # Add example to create cache
        skill.add_bootstrap_example("test_input", "test_output")

        assert len(skill._bootstrap_cache) == 0  # Cache is created on execution

        skill.clear_cache()
        assert len(skill._bootstrap_cache) == 0

        skill.reset_examples()
        assert len(skill._bootstrap_examples) == 0

    def test_repr(self):
        """Test string representation"""

        class TestSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return f"Processed: {input_data}"

        skill = TestSkill()
        skill.add_bootstrap_example("test", "output")

        repr_str = repr(skill)
        assert "SignatureSkill" in repr_str
        assert "examples=1" in repr_str


class TestSignatureDecorator:
    """Test signature_skill decorator"""

    def test_basic_decorator(self):
        """Test basic decorator usage"""

        @signature_skill(skill_id="decorated_skill", description="A decorated skill")
        async def test_skill(input_data: str, context: ExecutionContext) -> str:
            return f"Decorated: {input_data}"

        # The decorator returns a skill class, not an instance
        assert callable(test_skill)

    def test_decorator_with_parameters(self):
        """Test decorator with custom parameters"""

        @signature_skill(
            skill_id="custom_skill", name="Custom Skill", description="A skill with custom parameters", timeout=60.0
        )
        async def custom_skill(input_data: str, context: ExecutionContext) -> str:
            return f"Custom: {input_data}"

        # Test that the skill has the right configuration
        skill_instance = custom_skill()
        assert skill_instance.config.skill_id == "custom_skill"
        assert skill_instance.config.name == "Custom Skill"
        assert skill_instance.config.timeout == 60.0

    def test_decorator_execution(self):
        """Test execution of decorated skill"""

        @signature_skill(skill_id="executable_skill")
        async def executable_skill(input_data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
            return {"processed": True, "original": input_data}

        skill = executable_skill()
        context = ExecutionContext()

        async def test_execution():
            test_input = {"message": "test"}
            result = await skill.execute_with_signature(test_input, context)

            assert result.success is True
            assert result.data["processed"] is True
            assert result.data["original"] == test_input

        asyncio.run(test_execution())


class TestTypeContracts:
    """Test automatic type contract creation"""

    def test_primitive_type_contracts(self):
        """Test contracts for primitive types"""

        class StringSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return input_data.upper()

        skill = StringSkill()

        # Should have created contracts automatically
        assert skill._input_contract is not None
        assert skill._output_contract is not None

    def test_complex_type_contracts(self):
        """Test contracts for complex types"""

        class ComplexSkill(SignatureSkill[dict[str, list[int]], str]):
            async def execute_core(self, input_data: dict[str, list[int]], context: ExecutionContext) -> str:
                return f"Processed {len(input_data)} items"

        skill = ComplexSkill()

        # Should have created contracts
        assert skill._input_contract is not None
        assert skill._output_contract is not None

    def test_contract_validation(self):
        """Test contract validation during execution"""

        class ValidatedSkill(SignatureSkill[str, int]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> int:
                return len(input_data)

        skill = ValidatedSkill()
        context = ExecutionContext(validation_mode=ValidationMode.STRICT)

        async def test_validation():
            # Valid input
            result = await skill.execute_with_signature("test", context)
            assert result.success is True
            assert result.data == 4

        asyncio.run(test_validation())

    def test_invalid_input_handling(self):
        """Test handling of invalid input"""

        class ValidatedSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return input_data

        skill = ValidatedSkill()
        context = ExecutionContext(validation_mode=ValidationMode.STRICT)

        async def test_invalid():
            # Invalid input type
            result = await skill.execute_with_signature(123, context)  # Should be string

            # Should fail validation
            assert result.success is False
            assert "validation failed" in result.error.lower()

        asyncio.run(test_invalid())


class TestSkillMetrics:
    """Test skill metrics tracking"""

    def test_metrics_initialization(self):
        """Test metrics initialization"""

        class MetricSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return input_data

        skill = MetricSkill()

        metrics = skill.get_metrics()
        assert metrics.executions == 0
        assert metrics.successful_executions == 0
        assert metrics.average_execution_time == 0.0

    def test_metrics_update(self):
        """Test metrics update after execution"""

        class MetricSkill(SignatureSkill[str, str]):
            async def execute_core(self, input_data: str, context: ExecutionContext) -> str:
                return input_data

        skill = MetricSkill()
        context = ExecutionContext()

        async def test_metrics():
            await skill.execute_with_signature("test", context)

            metrics = skill.get_metrics()
            assert metrics.executions == 1
            assert metrics.successful_executions == 1
            assert metrics.average_execution_time > 0.0

        asyncio.run(test_metrics())


if __name__ == "__main__":
    pytest.main([__file__])
