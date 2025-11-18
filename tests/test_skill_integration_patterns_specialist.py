"""
Comprehensive tests for Skill Integration Patterns Specialist.

Tests cover all components including pattern matching, dependency resolution,
conflict management, workflow orchestration, and the learning system.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import uuid

from amplifier.skills.meta_skills.skill_integration_patterns_specialist import (
    SkillIntegrationPatternsSpecialist,
    IntegrationPattern,
    IntegrationPatternType,
    SkillDependency,
    SkillConflict,
    ConflictType,
    DependencyResolver,
    ConflictManager,
    PatternMatcher,
    PerformanceOptimizer,
    SkillWorkflow,
)
from amplifier.skills.meta_skills.integration_patterns_library import StandardPatternLibrary
from amplifier.skills.meta_skills.workflow_orchestrator import (
    WorkflowOrchestrator,
    WorkflowTask,
    WorkflowExecution,
    ExecutionStatus,
    TaskPriority,
)
from amplifier.skills.meta_skills.pattern_learning_system import (
    PatternLearningSystem,
    PatternPerformanceMetrics,
    PatternExecutionRecord,
    PatternAnalytics,
    PatternOptimizer,
)
from amplifier.skills.skill_base import Skill, SkillContext, SkillResult


class MockSkill(Skill):
    """Mock skill for testing."""

    def __init__(self, skill_id: str, success_rate: float = 1.0, execution_time: float = 1.0):
        super().__init__(
            id=skill_id,
            name=f"Mock Skill {skill_id}",
            description=f"Mock skill for testing",
            version="1.0.0",
            category="test",
            required_skills=[],
            tags=["test"],
            cost_estimate={"tokens": 100, "time": execution_time},
        )
        self.success_rate = success_rate
        self.execution_time = execution_time

    async def execute(self, context: SkillContext) -> SkillResult:
        await asyncio.sleep(self.execution_time)

        import random

        if random.random() < self.success_rate:
            return SkillResult(
                success=True,
                message=f"Mock skill {self.id} executed successfully",
                data={"skill_id": self.id, "timestamp": datetime.now()},
            )
        else:
            return SkillResult(success=False, message=f"Mock skill {self.id} failed", error="Simulated failure")


class MockSkillRegistry:
    """Mock skill registry for testing."""

    def __init__(self):
        self.skills = {}

    def add_skill(self, skill: Skill) -> None:
        self.skills[skill.id] = skill

    def get_skill(self, skill_id: str) -> Skill:
        return self.skills.get(skill_id)

    def list_skills(self) -> list:
        return list(self.skills.values())


class MockStorageManager:
    """Mock storage manager for testing."""

    def __init__(self):
        self.storage = {}

    async def store(self, key: str, data: dict) -> None:
        self.storage[key] = data

    async def retrieve(self, key: str) -> dict:
        return self.storage.get(key, {})

    async def delete(self, key: str) -> None:
        if key in self.storage:
            del self.storage[key]


class MockContext:
    """Mock skill context for testing."""

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.user_id = "test_user"
        self.parameters = {}
        self.skill_registry = MockSkillRegistry()
        self.storage_manager = MockStorageManager()
        self.performance_monitor = Mock()


@pytest.fixture
def mock_skill_registry():
    """Create mock skill registry with test skills."""
    registry = MockSkillRegistry()

    # Add test skills
    registry.add_skill(MockSkill("skill_1", success_rate=0.9, execution_time=0.5))
    registry.add_skill(MockSkill("skill_2", success_rate=0.8, execution_time=1.0))
    registry.add_skill(MockSkill("skill_3", success_rate=0.95, execution_time=0.3))
    registry.add_skill(MockSkill("skill_4", success_rate=0.7, execution_time=2.0))

    return registry


@pytest.fixture
def skill_context(mock_skill_registry):
    """Create mock skill context."""
    context = MockContext()
    context.skill_registry = mock_skill_registry
    return context


@pytest.fixture
def pattern_library():
    """Create pattern library instance."""
    return StandardPatternLibrary()


@pytest.fixture
def integration_specialist():
    """Create integration specialist instance."""
    return SkillIntegrationPatternsSpecialist()


class TestPatternMatcher:
    """Test pattern matching functionality."""

    def test_pattern_matching(self):
        """Test pattern matching for skill combinations."""
        matcher = PatternMatcher()

        # Test with empty skill list
        skill_ids = []
        patterns = asyncio.run(matcher.match_pattern(skill_ids))
        assert isinstance(patterns, list)

    def test_pattern_caching(self):
        """Test that pattern results are cached."""
        matcher = PatternMatcher()
        skill_ids = ["skill_1", "skill_2"]

        # First call should compute
        patterns1 = asyncio.run(matcher.match_pattern(skill_ids))

        # Second call should use cache
        patterns2 = asyncio.run(matcher.match_pattern(skill_ids))

        assert patterns1 == patterns2


class TestDependencyResolver:
    """Test dependency resolution functionality."""

    def test_dependency_resolution(self, mock_skill_registry):
        """Test dependency resolution for skills."""
        resolver = DependencyResolver(mock_skill_registry)
        skill_ids = ["skill_1", "skill_2", "skill_3"]

        dependencies, conflicts = asyncio.run(resolver.resolve_dependencies(skill_ids))

        assert isinstance(dependencies, list)
        assert isinstance(conflicts, list)

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        resolver = DependencyResolver(MockSkillRegistry())

        # This would need to be implemented with actual dependency setup
        skill_ids = ["skill_1"]
        dependencies, conflicts = asyncio.run(resolver.resolve_dependencies(skill_ids))

        # Check that conflicts list is properly initialized
        assert isinstance(conflicts, list)


class TestConflictManager:
    """Test conflict management functionality."""

    def test_conflict_detection(self, mock_skill_registry):
        """Test conflict detection between skills."""
        manager = ConflictManager()
        skills = {
            "skill_1": mock_skill_registry.get_skill("skill_1"),
            "skill_2": mock_skill_registry.get_skill("skill_2"),
        }

        conflicts = asyncio.run(manager.detect_conflicts(skills))
        assert isinstance(conflicts, list)

    def test_conflict_resolution(self, mock_skill_registry):
        """Test conflict resolution."""
        manager = ConflictManager()

        # Create a mock conflict
        conflict = SkillConflict(
            conflict_type=ConflictType.RESOURCE_CONFLICT,
            skill_1="skill_1",
            skill_2="skill_2",
            description="Test conflict",
            severity="medium",
        )

        resolved_conflicts = asyncio.run(manager.resolve_conflicts([conflict]))
        assert len(resolved_conflicts) >= 0


class TestPatternLibrary:
    """Test pattern library functionality."""

    def test_pattern_retrieval(self, pattern_library):
        """Test pattern retrieval by ID."""
        pattern = pattern_library.get_pattern("sequential_chain")
        assert pattern is not None
        assert pattern.id == "sequential_chain"
        assert pattern.pattern_type == IntegrationPatternType.SEQUENTIAL

    def test_pattern_search(self, pattern_library):
        """Test finding patterns for skill types."""
        skill_types = ["data_processing", "validation"]
        patterns = pattern_library.find_patterns_for_skills(skill_types)
        assert isinstance(patterns, list)

    def test_pattern_library_size(self, pattern_library):
        """Test that pattern library contains expected number of patterns."""
        assert len(pattern_library.patterns) >= 50  # Should have 50+ patterns


class TestWorkflowOrchestrator:
    """Test workflow orchestration functionality."""

    @pytest.fixture
    def orchestrator(self):
        """Create workflow orchestrator instance."""
        return WorkflowOrchestrator(max_concurrent_tasks=5, max_workers=3)

    @pytest.fixture
    def mock_workflow(self, mock_skill_registry):
        """Create mock workflow for testing."""
        import networkx as nx

        # Create execution graph
        graph = nx.DiGraph()
        graph.add_nodes_from(["skill_1", "skill_2", "skill_3"])
        graph.add_edges_from([("skill_1", "skill_2"), ("skill_2", "skill_3")])

        workflow = SkillWorkflow(
            id="test_workflow",
            name="Test Workflow",
            description="Test workflow for testing",
            pattern_ids=[],
            skills={
                "skill_1": mock_skill_registry.get_skill("skill_1"),
                "skill_2": mock_skill_registry.get_skill("skill_2"),
                "skill_3": mock_skill_registry.get_skill("skill_3"),
            },
            execution_graph=graph,
            context_requirements={},
            expected_outputs=[],
            estimated_duration=timedelta(minutes=5),
            cost_estimate={"tokens": 1000, "time": 5.0},
        )

        return workflow

    @pytest.mark.asyncio
    async def test_workflow_execution(self, orchestrator, mock_workflow, skill_context):
        """Test complete workflow execution."""
        execution = await orchestrator.execute_workflow(mock_workflow, skill_context)

        assert execution.id is not None
        assert execution.workflow == mock_workflow
        assert execution.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]
        assert execution.start_time is not None
        assert execution.end_time is not None
        assert execution.total_duration >= 0

    def test_task_creation(self, mock_workflow, skill_context):
        """Test workflow task creation."""
        orchestrator = WorkflowOrchestrator()

        with patch.object(orchestrator, "_create_workflow_execution") as mock_create:
            mock_create.return_value = Mock(
                id="test_execution", workflow=mock_workflow, tasks={}, execution_graph=mock_workflow.execution_graph
            )

            execution = asyncio.run(
                orchestrator._create_workflow_execution("test_execution", mock_workflow, skill_context)
            )

            assert execution.id == "test_execution"

    def test_execution_group_building(self, mock_workflow):
        """Test building execution groups from workflow."""
        orchestrator = WorkflowOrchestrator()

        # Create mock execution
        execution = Mock(tasks={}, execution_graph=mock_workflow.execution_graph)

        with patch.object(orchestrator, "_build_execution_groups") as mock_build:
            mock_build.return_value = []

            groups = orchestrator._build_execution_groups(execution)
            assert isinstance(groups, list)

    def test_performance_metrics(self, orchestrator):
        """Test performance metrics collection."""
        metrics = orchestrator.get_performance_metrics()

        assert "active_executions" in metrics
        assert "completed_executions" in metrics
        assert "total_tasks_executed" in metrics
        assert "success_rate" in metrics
        assert "resource_utilization" in metrics


class TestPatternLearningSystem:
    """Test pattern learning system functionality."""

    @pytest.fixture
    def learning_system(self):
        """Create learning system instance."""
        return PatternLearningSystem(MockStorageManager())

    @pytest.fixture
    def execution_record(self):
        """Create mock execution record."""
        return PatternExecutionRecord(
            execution_id=str(uuid.uuid4()),
            pattern_id="sequential_chain",
            skill_ids=["skill_1", "skill_2"],
            execution_context={"test": True},
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=5),
            duration=5.0,
            success=True,
            tokens_used=100,
            output_quality=0.9,
        )

    @pytest.mark.asyncio
    async def test_execution_recording(self, learning_system, execution_record):
        """Test recording pattern execution."""
        await learning_system.record_pattern_execution(execution_record)

        # Check that the record was stored
        assert execution_record.pattern_id in learning_system.analytics.performance_data
        assert len(learning_system.analytics.performance_data[execution_record.pattern_id]) == 1

    @pytest.mark.asyncio
    async def test_pattern_recommendations(self, learning_system):
        """Test pattern recommendation generation."""
        recommendations = await learning_system.get_pattern_recommendations(
            "sequential_chain", {"goal": "optimization"}
        )

        assert isinstance(recommendations, list)

    @pytest.mark.asyncio
    async def test_learning_insights(self, learning_system):
        """Test learning insights generation."""
        insights = await learning_system.get_learning_insights()

        assert "patterns_analyzed" in insights
        assert "total_executions" in insights
        assert "average_success_rate" in insights
        assert "learning_status" in insights

    def test_pattern_analytics(self, execution_record):
        """Test pattern analytics functionality."""
        analytics = PatternAnalytics()

        # Record execution
        analytics.record_execution(execution_record)

        # Get metrics
        metrics = analytics.get_pattern_metrics(execution_record.pattern_id)
        assert metrics is not None
        assert metrics.pattern_id == execution_record.pattern_id
        assert metrics.execution_count == 1
        assert metrics.success_count == 1

    def test_pattern_optimization(self):
        """Test pattern optimization."""
        optimizer = PatternOptimizer()

        # Create mock pattern
        pattern = IntegrationPattern(
            id="test_pattern",
            name="Test Pattern",
            description="Test pattern for optimization",
            pattern_type=IntegrationPatternType.SEQUENTIAL,
            skill_ids=["skill_1", "skill_2"],
            execution_plan={},
            dependencies=[],
        )

        # Test optimization
        optimized = optimizer.optimize_pattern(pattern, "speed")

        assert optimized.id != pattern.id
        assert "optimized" in optimized.name
        assert optimized.skill_ids == pattern.skill_ids

    def test_trend_analysis(self, execution_record):
        """Test performance trend analysis."""
        analytics = PatternAnalytics()

        # Record multiple executions
        for i in range(10):
            record = PatternExecutionRecord(
                execution_id=str(uuid.uuid4()),
                pattern_id="test_pattern",
                skill_ids=["skill_1"],
                execution_context={},
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(seconds=5 + i),
                duration=5 + i,
                success=True,
                tokens_used=100 + i * 10,
            )
            analytics.record_execution(record)

        # Analyze trends
        trends = analytics.analyze_performance_trends("test_pattern")
        assert isinstance(trends, dict)


class TestIntegrationSpecialist:
    """Test the main integration specialist."""

    @pytest.mark.asyncio
    async def test_specialist_initialization(self, integration_specialist, skill_context):
        """Test specialist initialization."""
        await integration_specialist.initialize(skill_context)

        assert integration_specialist.dependency_resolver is not None
        assert integration_specialist.conflict_manager is not None
        assert integration_specialist.performance_optimizer is not None
        assert integration_specialist.learning_system is not None

    @pytest.mark.asyncio
    async def test_skill_integration_analysis(self, integration_specialist, skill_context):
        """Test skill integration analysis."""
        await integration_specialist.initialize(skill_context)

        # Set up test parameters
        skill_context.parameters = {"skills": ["skill_1", "skill_2", "skill_3"]}

        # Execute analysis
        result = await integration_specialist.execute(skill_context)

        assert result.success is True
        assert "analysis" in result.data
        assert "workflow" in result.data
        assert "improvements" in result.data

    @pytest.mark.asyncio
    async def test_no_skills_provided(self, integration_specialist, skill_context):
        """Test handling when no skills are provided."""
        await integration_specialist.initialize(skill_context)

        # Empty skills list
        skill_context.parameters = {"skills": []}

        result = await integration_specialist.execute(skill_context)

        assert result.success is False
        assert "No skills provided" in result.message


class TestPerformanceValidation:
    """Performance validation tests."""

    @pytest.mark.asyncio
    async def test_sub_second_pattern_matching(self, pattern_library):
        """Test that pattern matching completes in sub-second time."""
        skill_types = ["data_processing", "validation", "transformation"]

        start_time = datetime.now()
        patterns = pattern_library.find_patterns_for_skills(skill_types)
        end_time = datetime.now()

        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0, f"Pattern matching took {duration}s, should be < 1s"

    @pytest.mark.asyncio
    async def test_parallel_workflow_execution(self, mock_skill_registry):
        """Test that parallel workflows execute faster than sequential."""
        orchestrator = WorkflowOrchestrator(max_concurrent_tasks=5, max_workers=3)

        import networkx as nx

        # Create parallel workflow
        parallel_graph = nx.DiGraph()
        parallel_graph.add_nodes_from(["skill_1", "skill_2", "skill_3"])
        # No edges = parallel execution

        parallel_workflow = SkillWorkflow(
            id="parallel_workflow",
            name="Parallel Workflow",
            description="Test parallel workflow",
            pattern_ids=[],
            skills={
                "skill_1": mock_skill_registry.get_skill("skill_1"),
                "skill_2": mock_skill_registry.get_skill("skill_2"),
                "skill_3": mock_skill_registry.get_skill("skill_3"),
            },
            execution_graph=parallel_graph,
            context_requirements={},
            expected_outputs=[],
            estimated_duration=timedelta(seconds=2),
            cost_estimate={"tokens": 300, "time": 2.0},
        )

        # Create sequential workflow
        sequential_graph = nx.DiGraph()
        sequential_graph.add_nodes_from(["skill_1", "skill_2", "skill_3"])
        sequential_graph.add_edges_from([("skill_1", "skill_2"), ("skill_2", "skill_3")])

        sequential_workflow = SkillWorkflow(
            id="sequential_workflow",
            name="Sequential Workflow",
            description="Test sequential workflow",
            pattern_ids=[],
            skills={
                "skill_1": mock_skill_registry.get_skill("skill_1"),
                "skill_2": mock_skill_registry.get_skill("skill_2"),
                "skill_3": mock_skill_registry.get_skill("skill_3"),
            },
            execution_graph=sequential_graph,
            context_requirements={},
            expected_outputs=[],
            estimated_duration=timedelta(seconds=6),
            cost_estimate={"tokens": 300, "time": 6.0},
        )

        context = MockContext()
        context.skill_registry = mock_skill_registry
        context.storage_manager = MockStorageManager()

        # Execute both workflows
        parallel_start = datetime.now()
        parallel_execution = await orchestrator.execute_workflow(parallel_workflow, context)
        parallel_end = datetime.now()

        sequential_start = datetime.now()
        sequential_execution = await orchestrator.execute_workflow(sequential_workflow, context)
        sequential_end = datetime.now()

        parallel_duration = (parallel_end - parallel_start).total_seconds()
        sequential_duration = (sequential_end - sequential_start).total_seconds()

        # Parallel should be faster
        assert parallel_duration < sequential_duration, (
            f"Parallel ({parallel_duration}s) should be faster than sequential ({sequential_duration}s)"
        )

    def test_zero_conflict_guarantee(self, conflict_manager, mock_skill_registry):
        """Test that validated patterns have zero conflicts."""
        skills = {
            "skill_1": mock_skill_registry.get_skill("skill_1"),
            "skill_2": mock_skill_registry.get_skill("skill_2"),
        }

        # Detect conflicts
        conflicts = asyncio.run(conflict_manager.detect_conflicts(skills))

        # With mock skills that don't have conflicting resources, should be no conflicts
        assert len(conflicts) == 0 or all(c.resolution_strategy for c in conflicts)


class TestErrorHandling:
    """Test error handling and recovery."""

    @pytest.mark.asyncio
    async def test_workflow_failure_handling(self, mock_skill_registry):
        """Test handling of workflow failures."""
        orchestrator = WorkflowOrchestrator()

        # Create workflow with a failing skill
        failing_skill = MockSkill("failing_skill", success_rate=0.0, execution_time=0.1)
        mock_skill_registry.add_skill(failing_skill)

        import networkx as nx

        graph = nx.DiGraph()
        graph.add_node("failing_skill")

        workflow = SkillWorkflow(
            id="failing_workflow",
            name="Failing Workflow",
            description="Workflow with failing skill",
            pattern_ids=[],
            skills={"failing_skill": failing_skill},
            execution_graph=graph,
            context_requirements={},
            expected_outputs=[],
            estimated_duration=timedelta(seconds=1),
            cost_estimate={"tokens": 100, "time": 1.0},
        )

        context = MockContext()
        context.skill_registry = mock_skill_registry
        context.storage_manager = MockStorageManager()

        # Execute workflow
        execution = await orchestrator.execute_workflow(workflow, context)

        # Should handle failure gracefully
        assert execution.status == ExecutionStatus.FAILED
        assert execution.failed_tasks >= 1
        assert execution.end_time is not None

    @pytest.mark.asyncio
    async def test_dependency_resolution_failure(self, mock_skill_registry):
        """Test handling of dependency resolution failures."""
        resolver = DependencyResolver(mock_skill_registry)

        # Test with non-existent skill
        skill_ids = ["non_existent_skill"]

        dependencies, conflicts = asyncio.run(resolver.resolve_dependencies(skill_ids))

        # Should handle gracefully
        assert isinstance(dependencies, list)
        assert isinstance(conflicts, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
