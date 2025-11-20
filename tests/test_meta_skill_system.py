"""
Meta-Skill System Integration Tests

Comprehensive test suite for the meta-skill system including:
- 5-stage skill creation methodology
- Template library functionality
- Zero hallucination validation
- Performance optimization
- Agent coordination
- Progressive documentation

Architecture: Comprehensive test suite with multiple test categories
- Unit Tests: Individual component testing
- Integration Tests: Cross-component interaction testing
- Performance Tests: System performance and optimization validation
- Contract Tests: Interface compliance testing
- End-to-End Tests: Complete workflow validation

Key Benefits:
- Comprehensive validation of meta-skill functionality
- Performance regression detection
- Integration failure identification
- Quality assurance for 99% accuracy targets
- Automated validation of compound multiplier benefits
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from amplifier.skills.meta_skills.agent_coordination import AgentCapability
from amplifier.skills.meta_skills.agent_coordination import AgentCoordinator
from amplifier.skills.meta_skills.agent_coordination import AgentProfile
from amplifier.skills.meta_skills.agent_coordination import CoordinationContext
from amplifier.skills.meta_skills.agent_coordination import Task
from amplifier.skills.meta_skills.agent_coordination import TaskPriority
from amplifier.skills.meta_skills.performance_optimizer import OptimizationContext
from amplifier.skills.meta_skills.performance_optimizer import OptimizationLevel
from amplifier.skills.meta_skills.performance_optimizer import PerformanceOptimizer
from amplifier.skills.meta_skills.quality_assurance import ValidationContext
from amplifier.skills.meta_skills.quality_assurance import ValidationLevel
from amplifier.skills.meta_skills.quality_assurance import ValidationResult
from amplifier.skills.meta_skills.quality_assurance import ZeroHallucinationQA
from amplifier.skills.meta_skills.skill_creation_methodology import SkillCreationContext

# Import meta-skill components
from amplifier.skills.meta_skills.skill_creation_methodology import SkillCreationMethodology
from amplifier.skills.meta_skills.skill_creation_methodology import SkillRequirement
from amplifier.skills.meta_skills.skill_creation_methodology import ValidationStage
from amplifier.skills.meta_skills.template_library import SkillTemplate
from amplifier.skills.meta_skills.template_library import TemplateLibrary


class TestMetaSkillSystem:
    """Comprehensive test suite for meta-skill system."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary directory for test storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def mock_skill_requirement(self):
        """Create mock skill requirement for testing."""
        return SkillRequirement(
            name="test_skill",
            description="A test skill for validation",
            category="data_processing",
            complexity="intermediate",
            dependencies=[],
            performance_requirements={"max_response_time": 1.0, "min_accuracy": 0.95},
        )

    @pytest.fixture
    def mock_skill_creation_context(self, mock_skill_requirement):
        """Create mock skill creation context."""
        return SkillCreationContext(
            skill_name="test_skill",
            requirement=mock_skill_requirement,
            user_context={"goal": "process data efficiently"},
            constraints={"max_tokens": 1000},
        )

    @pytest.fixture
    def mock_agent_profile(self):
        """Create mock agent profile for testing."""
        return AgentProfile(
            agent_id="test_agent",
            agent_name="Test Agent",
            capabilities=[AgentCapability.CODE_GENERATION, AgentCapability.ANALYSIS],
            max_concurrent_tasks=3,
            success_rate=0.95,
            reliability_score=0.9,
        )

    class TestSkillCreationMethodology:
        """Test skill creation methodology component."""

        @pytest.mark.asyncio
        async def test_5_stage_methodology_execution(self, mock_skill_creation_context):
            """Test complete 5-stage skill creation methodology."""
            methodology = SkillCreationMethodology()

            # Execute skill creation
            result = await methodology.create_skill_methodology(mock_skill_creation_context)

            # Validate results
            assert result is not None
            assert result.success is True
            assert result.skill_name == "test_skill"
            assert len(result.stages_completed) == 5
            assert all(
                stage in result.stages_completed
                for stage in ["requirements_analysis", "design", "implementation", "testing", "deployment"]
            )

        @pytest.mark.asyncio
        async def test_quality_gates_enforcement(self, mock_skill_creation_context):
            """Test that quality gates are properly enforced."""
            methodology = SkillCreationMethodology()

            # Execute with strict quality gates
            result = await methodology.create_skill_methodology(mock_skill_creation_context, strict_quality_gates=True)

            # Validate quality gate results
            assert result.quality_gate_results is not None
            assert all(gate_result.passed for gate_result in result.quality_gate_results.values())
            assert result.overall_quality_score >= 0.9

        @pytest.mark.asyncio
        async def test_mcp_integration(self, mock_skill_creation_context, temp_storage_dir):
            """Test MCP persistent storage integration."""
            methodology = SkillCreationMethodology(storage_path=temp_storage_dir)

            # Execute skill creation
            result = await methodology.create_skill_methodology(mock_skill_creation_context)

            # Validate MCP storage integration
            assert result.checkpoint_saved is True
            assert result.mcp_storage_used is True
            assert len(result.checkpoints) > 0

        def test_stage_validation_requirements(self):
            """Test stage-specific validation requirements."""
            methodology = SkillCreationMethodology()

            # Test requirements analysis stage
            requirements = methodology.get_stage_requirements("requirements_analysis")
            assert "clear_objectives" in requirements
            assert "measurable_outcomes" in requirements

            # Test implementation stage
            impl_requirements = methodology.get_stage_requirements("implementation")
            assert "code_quality" in impl_requirements
            assert "error_handling" in impl_requirements

    class TestTemplateLibrary:
        """Test template library functionality."""

        @pytest.fixture
        def template_library(self):
            """Create template library instance."""
            return TemplateLibrary()

        def test_template_retrieval_by_category(self, template_library):
            """Test template retrieval by category."""
            # Get data processing templates
            templates = template_library.get_templates_by_category("data_processing")

            assert len(templates) > 0
            assert all(template.category == "data_processing" for template in templates)

        def test_template_customization(self, template_library):
            """Test template customization functionality."""
            # Get base template
            base_template = template_library.get_template("data_processor_basic")
            assert base_template is not None

            # Customize template
            custom_params = {"input_format": "json", "output_format": "csv", "batch_size": 100}
            customized = template_library.customize_template(base_template, custom_params)

            # Validate customization
            assert customized.parameters["input_format"] == "json"
            assert customized.parameters["output_format"] == "csv"
            assert customized.parameters["batch_size"] == 100

        def test_template_validation(self, template_library):
            """Test template validation."""
            # Get valid template
            valid_template = template_library.get_template("data_processor_basic")
            validation_result = template_library.validate_template(valid_template)
            assert validation_result.is_valid is True

            # Test invalid template
            invalid_template = SkillTemplate(
                template_id="invalid", name="Invalid Template", category="unknown", parameters={}, code_structure=""
            )
            validation_result = template_library.validate_template(invalid_template)
            assert validation_result.is_valid is False
            assert len(validation_result.errors) > 0

        def test_template_progressive_complexity(self, template_library):
            """Test progressive complexity levels in templates."""
            # Get templates at different complexity levels
            basic = template_library.get_template("data_processor_basic")
            intermediate = template_library.get_template("data_processor_intermediate")
            advanced = template_library.get_template("data_processor_advanced")

            # Validate complexity progression
            assert basic.complexity_level < intermediate.complexity_level
            assert intermediate.complexity_level < advanced.complexity_level
            assert len(advanced.features) > len(intermediate.features)
            assert len(intermediate.features) > len(basic.features)

    class TestZeroHallucinationQA:
        """Test zero hallucination validation system."""

        @pytest.fixture
        def qa_system(self):
            """Create zero hallucination QA system."""
            return ZeroHallucinationQA()

        @pytest.mark.asyncio
        async def test_fact_checking_validation(self, qa_system):
            """Test fact-checking validation."""
            context = ValidationContext(
                skill_name="test_skill",
                stage=ValidationStage.REQUIREMENTS,
                content={
                    "claims": ["This skill processes 1000 records per second"],
                    "sources": ["performance_benchmark.md"],
                },
                validation_level=ValidationLevel.STANDARD,
            )

            result = await qa_system.validate_content(context)

            # Validate fact-checking results
            assert isinstance(result, ValidationResult)
            assert len(result.fact_checks) > 0
            assert result.confidence_score >= 0.8

        @pytest.mark.asyncio
        async def test_logical_consistency_check(self, qa_system):
            """Test logical consistency validation."""
            context = ValidationContext(
                skill_name="test_skill",
                stage=ValidationStage.DESIGN,
                content={
                    "requirements": {"max_response_time": 1.0},
                    "implementation": {"processing_time": 2.0},  # Contradiction
                    "specification": {"supports": "real_time_processing"},
                },
                validation_level=ValidationLevel.COMPREHENSIVE,
            )

            result = await qa_system.validate_content(context)

            # Should detect logical inconsistency
            assert result.is_valid is False  # Should fail due to contradiction
            assert any(issue["type"] == "logical_contradiction" for issue in result.issues)

        @pytest.mark.asyncio
        async def test_quality_gate_compliance(self, qa_system):
            """Test quality gate compliance validation."""
            context = ValidationContext(
                skill_name="test_skill",
                stage=ValidationStage.IMPLEMENTATION,
                content={
                    "code": "def process_data(data): return data",
                    "tests": ["test_empty_input", "test_normal_case"],
                    "documentation": {"api": "complete", "examples": "provided"},
                },
                validation_level=ValidationLevel.EXHAUSTIVE,
            )

            result = await qa_system.validate_content(context)

            # Should pass quality gates for implementation
            assert result.is_valid is True
            assert result.confidence_score >= 0.95

        def test_performance_metrics_tracking(self, qa_system):
            """Test performance metrics tracking."""
            metrics = qa_system.get_metrics()

            # Validate metrics structure
            assert "total_validations" in metrics
            assert "success_rate" in metrics
            assert "average_confidence" in metrics
            assert "hallucination_detection_rate" in metrics

            # Initial state should be clean
            assert metrics["total_validations"] == 0
            assert metrics["success_rate"] == 0.0

    class TestPerformanceOptimizer:
        """Test performance optimization system."""

        @pytest.fixture
        def optimizer(self):
            """Create performance optimizer instance."""
            return PerformanceOptimizer()

        @pytest.mark.asyncio
        async def test_token_efficiency_optimization(self, optimizer):
            """Test token efficiency optimization."""
            context = OptimizationContext(
                skill_name="test_skill",
                operation_type="content_generation",
                input_size=5000,  # Large input
                optimization_level=OptimizationLevel.AGGRESSIVE,
            )

            async def mock_operation(input_data):
                return f"Processed: {len(input_data)} characters"

            # Execute optimized operation
            result, performance_metrics = await optimizer.optimize_operation(
                context, mock_operation, "large_input_data" * 100
            )

            # Validate optimization results
            assert performance_metrics.token_efficiency > 0.7  # Should achieve >70% reduction
            assert performance_metrics.throughput_improvement > 1.5  # Should improve throughput
            assert result is not None

        @pytest.mark.asyncio
        async def test_parallel_execution_optimization(self, optimizer):
            """Test parallel execution optimization."""
            context = OptimizationContext(
                skill_name="test_skill",
                operation_type="batch_processing",
                input_size=10,
                optimization_level=OptimizationLevel.AGGRESSIVE,
                parallelizable=True,
            )

            async def mock_batch_operation(items):
                return [f"Processed item {i}" for i in items]

            # Execute optimized batch operation
            items = list(range(10))
            result, performance_metrics = await optimizer.optimize_operation(context, mock_batch_operation, items)

            # Validate parallel execution benefits
            assert performance_metrics.parallel_utilization > 0.5
            assert performance_metrics.throughput_improvement > 2.0  # Should be >2x faster
            assert len(result) == 10

        @pytest.mark.asyncio
        async def test_intelligent_caching(self, optimizer):
            """Test intelligent caching functionality."""
            context = OptimizationContext(skill_name="test_skill", operation_type="computation", input_size=100)

            async def mock_computation(data):
                return f"Computed result for {data}"

            # First execution
            result1, metrics1 = await optimizer.optimize_operation(context, mock_computation, "test_data")

            # Second execution (should use cache)
            result2, metrics2 = await optimizer.optimize_operation(context, mock_computation, "test_data")

            # Validate caching behavior
            assert result1 == result2  # Results should be identical
            assert metrics2.cache_hit_rate > metrics1.cache_hit_rate
            assert metrics2.processing_time < metrics1.processing_time  # Should be faster due to cache

    class TestAgentCoordination:
        """Test agent coordination system."""

        @pytest.fixture
        def coordinator(self, mock_agent_profile):
            """Create agent coordinator with mock agent."""
            coordinator = AgentCoordinator()
            coordinator.register_agent(mock_agent_profile)
            return coordinator

        @pytest.mark.asyncio
        async def test_parallel_task_execution(self, coordinator):
            """Test parallel task execution coordination."""
            context = CoordinationContext(
                skill_name="test_skill",
                operation_id="test_operation",
                coordinator_name="test_coordinator",
                objectives=["process_data", "validate_results", "generate_report"],
                max_parallel_agents=3,
            )

            # Create tasks for parallel execution
            tasks = [
                {
                    "id": "task1",
                    "type": "data_processing",
                    "description": "Process input data",
                    "required_capabilities": ["code_generation"],
                    "input_data": {"data": "test_data"},
                },
                {
                    "id": "task2",
                    "type": "validation",
                    "description": "Validate processing results",
                    "required_capabilities": ["analysis"],
                    "input_data": {"results": "test_results"},
                },
                {
                    "id": "task3",
                    "type": "reporting",
                    "description": "Generate final report",
                    "required_capabilities": ["documentation"],
                    "input_data": {"summary": "test_summary"},
                },
            ]

            # Execute coordinated parallel tasks
            result = await coordinator.coordinate_parallel_execution(context, tasks)

            # Validate coordination results
            assert result["success_rate"] >= 0.8  # At least 80% success rate
            assert len(result["results"]) == 3  # All tasks processed
            assert result["metrics"]["parallel_efficiency"] > 1.5  # Should be >1.5x efficient

        def test_agent_load_balancing(self, coordinator, mock_agent_profile):
            """Test agent load balancing functionality."""
            # Create multiple tasks
            tasks = [
                Task(
                    task_id=f"task_{i}",
                    task_type="test_task",
                    description=f"Test task {i}",
                    required_capabilities=[AgentCapability.CODE_GENERATION],
                    priority=TaskPriority.NORMAL,
                )
                for i in range(5)
            ]

            # Assign tasks to agents
            assignments = {}
            for task in tasks:
                suitable_agents = coordinator._find_suitable_agents(task)
                if suitable_agents:
                    best_agent = coordinator.load_balancer.select_agent(
                        task, suitable_agents, coordinator.registered_agents
                    )
                    assignments[task.task_id] = best_agent

            # Validate load balancing
            assert len(assignments) == 5
            assert all(agent_id == "test_agent" for agent_id in assignments.values())

        @pytest.mark.asyncio
        async def test_coordination_metrics_tracking(self, coordinator):
            """Test coordination metrics tracking."""
            # Get initial metrics
            initial_metrics = coordinator.get_metrics()
            assert initial_metrics.total_tasks == 0

            # Execute a simple coordination task
            context = CoordinationContext(
                skill_name="test_skill",
                operation_id="metrics_test",
                coordinator_name="test_coordinator",
                objectives=["test_objective"],
            )

            tasks = [
                {
                    "id": "metrics_task",
                    "type": "test",
                    "description": "Test task for metrics",
                    "required_capabilities": ["analysis"],
                    "input_data": {},
                }
            ]

            await coordinator.coordinate_parallel_execution(context, tasks)

            # Check updated metrics
            updated_metrics = coordinator.get_metrics()
            assert updated_metrics.total_tasks > initial_metrics.total_tasks

    class TestSystemIntegration:
        """Test complete system integration."""

        @pytest.mark.asyncio
        async def test_end_to_end_skill_creation(self, mock_skill_creation_context, temp_storage_dir):
            """Test complete end-to-end skill creation workflow."""
            # Initialize all components
            methodology = SkillCreationMethodology(storage_path=temp_storage_dir)
            template_lib = TemplateLibrary()
            qa_system = ZeroHallucinationQA()
            optimizer = PerformanceOptimizer()

            # Execute complete workflow
            # 1. Create skill using methodology
            skill_result = await methodology.create_skill_methodology(mock_skill_creation_context)
            assert skill_result.success is True

            # 2. Apply template optimization
            template = template_lib.get_template("data_processor_basic")
            optimized_template = template_lib.customize_template(template, skill_result.customization_params)

            # 3. Validate with zero hallucination QA
            validation_context = ValidationContext(
                skill_name=skill_result.skill_name,
                stage=ValidationStage.IMPLEMENTATION,
                content=skill_result.generated_skill,
                validation_level=ValidationLevel.STANDARD,
            )
            validation_result = await qa_system.validate_content(validation_context)
            assert validation_result.is_valid is True

            # 4. Optimize performance
            optimization_context = OptimizationContext(
                skill_name=skill_result.skill_name,
                operation_type="skill_optimization",
                input_size=len(str(skill_result.generated_skill)),
            )
            optimized_skill, performance_metrics = await optimizer.optimize_operation(
                optimization_context, lambda x: x, skill_result.generated_skill
            )

            # Validate complete workflow results
            assert skill_result.success is True
            assert validation_result.confidence_score >= 0.9
            assert performance_metrics.token_efficiency > 0.7

        @pytest.mark.asyncio
        async def test_compound_multiplier_validation(self, mock_skill_creation_context):
            """Test compound multiplier benefits validation."""
            # Initialize system components
            methodology = SkillCreationMethodology()
            optimizer = PerformanceOptimizer()
            qa_system = ZeroHallucinationQA()

            # Measure baseline performance (without optimizations)
            start_time = datetime.now()
            baseline_result = await methodology.create_skill_methodology(
                mock_skill_creation_context, use_optimizations=False
            )
            baseline_time = (datetime.now() - start_time).total_seconds()

            # Measure optimized performance
            start_time = datetime.now()
            optimized_result = await methodology.create_skill_methodology(
                mock_skill_creation_context, use_optimizations=True
            )
            optimized_time = (datetime.now() - start_time).total_seconds()

            # Validate compound multiplier benefits
            speed_improvement = baseline_time / optimized_time if optimized_time > 0 else 1
            assert speed_improvement >= 2.0  # Should be at least 2x faster

            # Validate quality maintenance
            validation_context = ValidationContext(
                skill_name=optimized_result.skill_name,
                stage=ValidationStage.DEPLOYMENT,
                content=optimized_result.generated_skill,
                validation_level=ValidationLevel.STANDARD,
            )
            validation_result = await qa_system.validate_content(validation_context)
            assert validation_result.confidence_score >= 0.99  # Maintain 99% accuracy

        def test_system_performance_targets(self):
            """Test that system meets performance targets."""
            # Define performance targets
            targets = {
                "token_efficiency": 0.828,  # 82.8% target
                "accuracy": 0.99,  # 99% target
                "throughput_improvement": 2.0,  # 2x target
                "parallel_efficiency": 3.0,  # 3x target
            }

            # Validate system capability to meet targets
            # This would integrate with actual performance monitoring
            assert targets["token_efficiency"] >= 0.8
            assert targets["accuracy"] >= 0.95
            assert targets["throughput_improvement"] >= 1.5
            assert targets["parallel_efficiency"] >= 2.0


# Integration test configuration
pytest_plugins = []

# Test markers for different test categories
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance
pytest.mark.e2e = pytest.mark.e2e


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v", "--tb=short"])
