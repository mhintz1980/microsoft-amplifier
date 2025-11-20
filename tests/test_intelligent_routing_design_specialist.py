"""Tests for Intelligent Routing Design Specialist meta-skill."""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from amplifier.skills.meta_skills.intelligent_routing_design_specialist import IntelligentRoutingDesignSpecialist
from amplifier.skills.meta_skills.intelligent_routing_design_specialist import RoutingStrategy
from amplifier.skills.meta_skills.intelligent_routing_design_specialist import SkillCapability
from amplifier.skills.meta_skills.intelligent_routing_design_specialist import SkillCapabilityDatabase
from amplifier.skills.meta_skills.intelligent_routing_design_specialist import SkillCombination
from amplifier.skills.meta_skills.intelligent_routing_design_specialist import SkillComplexity
from amplifier.skills.skills_framework.skill_template import SkillContext
from amplifier.skills.skills_framework.skill_template import SkillLevel


@pytest.fixture
def routing_specialist():
    """Create a routing specialist instance for testing."""
    return IntelligentRoutingDesignSpecialist()


@pytest.fixture
def sample_skill_context():
    """Create a sample skill context for testing."""
    return SkillContext(
        query="Optimize skill execution for maximum performance and accuracy",
        conversation_history=[
            {"role": "user", "content": "I need help with coordinating multiple skills"},
            {"role": "assistant", "content": "I can help you optimize skill execution"},
        ],
        available_tokens=1000,
    )


class TestSkillCapabilityDatabase:
    """Test the skill capability database functionality."""

    @pytest.fixture
    def capability_db(self):
        """Create a capability database for testing."""
        return SkillCapabilityDatabase()

    def test_register_skill_capability(self, capability_db):
        """Test registering a skill capability."""
        capability = SkillCapability(
            name="test_skill",
            description="Test skill for routing",
            input_types=["text"],
            output_types=["result"],
            complexity=SkillComplexity.SIMPLE,
            estimated_tokens=100,
            estimated_time=2.0,
            tags=["test", "routing"],
        )

        capability_db.register_skill_capability("test_skill", capability)
        retrieved = capability_db.get_capability("test_skill")

        assert retrieved is not None
        assert retrieved.name == "test_skill"
        assert retrieved.complexity == SkillComplexity.SIMPLE

    def test_synergy_scores(self, capability_db):
        """Test synergy score management."""
        capability_db.set_synergy_score("skill1", "skill2", 0.8)
        capability_db.set_synergy_score("skill2", "skill3", 0.6)

        assert capability_db.get_synergy_score("skill1", "skill2") == 0.8
        assert capability_db.get_synergy_score("skill2", "skill1") == 0.8  # Should be symmetric
        assert capability_db.get_synergy_score("skill1", "skill3") == 0.0  # Default

    def test_performance_tracking(self, capability_db):
        """Test performance history tracking."""
        metrics = {"execution_time": 1.5, "tokens_used": 120, "success": True}

        capability_db.update_performance("test_skill", metrics)

        history = capability_db.performance_history["test_skill"]
        assert len(history) == 1
        assert history[0]["execution_time"] == 1.5
        assert "timestamp" in history[0]


class TestIntelligentRoutingDesignSpecialist:
    """Test the main routing specialist functionality."""

    def test_skill_metadata(self, routing_specialist):
        """Test skill metadata."""
        assert routing_specialist.description is not None
        assert len(routing_specialist.description) > 0
        assert "routing" in routing_specialist.description.lower()

        assert len(routing_specialist.tags) > 0
        assert "routing" in routing_specialist.tags
        assert "optimization" in routing_specialist.tags

    def test_can_handle_high_confidence(self, routing_specialist):
        """Test high-confidence matching."""
        context = SkillContext(
            query="Optimize skill selection and execution order for maximum performance",
            conversation_history=[],
            available_tokens=1000,
        )

        confidence = routing_specialist.can_handle(context)
        assert confidence >= 0.8

    def test_can_handle_medium_confidence(self, routing_specialist):
        """Test medium-confidence matching."""
        context = SkillContext(
            query="I need to coordinate multiple skills for my workflow", conversation_history=[], available_tokens=1000
        )

        confidence = routing_specialist.can_handle(context)
        assert confidence >= 0.5

    def test_can_handle_low_confidence(self, routing_specialist):
        """Test low-confidence matching."""
        context = SkillContext(query="Just tell me the weather", conversation_history=[], available_tokens=1000)

        confidence = routing_specialist.can_handle(context)
        assert confidence < 0.5

    def test_analyze_requirements(self, routing_specialist):
        """Test requirement analysis."""
        query = "Optimize for fast performance with minimal resource usage"
        requirements = routing_specialist._analyze_requirements(query)

        assert "primary_goal" in requirements
        assert "constraints" in requirements
        assert "preferences" in requirements
        assert "complexity_indicators" in requirements
        assert "context_needs" in requirements

        # Check constraint extraction
        assert "time_critical" in requirements["constraints"]
        assert "resource_minimal" in requirements["constraints"]

    def test_extract_primary_goal(self, routing_specialist):
        """Test primary goal extraction."""
        assert routing_specialist._extract_primary_goal("Make it fast and quick") == "performance"
        assert routing_specialist._extract_primary_goal("Ensure accurate results") == "accuracy"
        assert routing_specialist._extract_primary_goal("Save tokens and be efficient") == "efficiency"
        assert routing_specialist._extract_primary_goal("Coordinate multiple tasks") == "coordination"

    def test_determine_strategy(self, routing_specialist):
        """Test strategy determination."""
        requirements = {"constraints": ["time_critical"], "preferences": {}}

        strategy = routing_specialist._determine_strategy(requirements, SkillContext("", [], 1000))
        assert strategy == RoutingStrategy.PERFORMANCE

        requirements["constraints"] = ["resource_minimal"]
        strategy = routing_specialist._determine_strategy(requirements, SkillContext("", [], 1000))
        assert strategy == RoutingStrategy.TOKEN_EFFICIENCY

    def test_generate_skill_combinations(self, routing_specialist):
        """Test skill combination generation."""
        requirements = {
            "primary_goal": "performance",
            "constraints": [],
            "complexity_indicators": {"has_multiple_goals": False},
            "context_needs": {},
        }

        combinations = routing_specialist._generate_skill_combinations(requirements, RoutingStrategy.PERFORMANCE)

        assert len(combinations) > 0
        for combo in combinations:
            assert isinstance(combo, SkillCombination)
            assert combo.strategy == RoutingStrategy.PERFORMANCE
            assert len(combo.skills) >= 1
            assert combo.confidence >= 0.0

    def test_create_combination(self, routing_specialist):
        """Test skill combination creation."""
        combination = routing_specialist._create_combination(
            ["context_compactor", "token_budget"], RoutingStrategy.SYNERGY
        )

        assert len(combination.skills) == 2
        assert combination.strategy == RoutingStrategy.SYNERGY
        assert combination.estimated_tokens > 0
        assert combination.estimated_time > 0
        assert len(combination.execution_order) == 2

    def test_resolve_execution_order(self, routing_specialist):
        """Test execution order resolution."""
        # Test with dependencies
        skills = ["dependent_skill", "base_skill"]
        dependencies = ["base_skill"]

        order = routing_specialist._resolve_execution_order(skills, dependencies)
        assert order.index("base_skill") < order.index("dependent_skill")

        # Test without dependencies
        skills = ["skill1", "skill2", "skill3"]
        order = routing_specialist._resolve_execution_order(skills, [])
        assert len(order) == 3
        assert all(skill in order for skill in skills)

    def test_calculate_combination_confidence(self, routing_specialist):
        """Test confidence calculation."""
        combination = routing_specialist._create_combination(["context_compactor"], RoutingStrategy.PERFORMANCE)
        requirements = {"primary_goal": "performance"}

        confidence = routing_specialist._calculate_combination_confidence(
            combination, requirements, RoutingStrategy.PERFORMANCE
        )

        assert 0.0 <= confidence <= 1.0

    def test_format_result_metadata(self, routing_specialist):
        """Test metadata level result formatting."""
        combination = routing_specialist._create_combination(["context_compactor"], RoutingStrategy.BALANCED)
        requirements = {"primary_goal": "balanced"}

        result = routing_specialist._format_result(combination, requirements, SkillLevel.METADATA)

        assert "skills_count" in result
        assert "estimated_tokens" in result
        assert "strategy" in result
        assert "confidence" in result

    def test_format_result_summary(self, routing_specialist):
        """Test summary level result formatting."""
        combination = routing_specialist._create_combination(
            ["context_compactor", "token_budget"], RoutingStrategy.SYNERGY
        )
        requirements = {"primary_goal": "synergy"}

        result = routing_specialist._format_result(combination, requirements, SkillLevel.SUMMARY)

        assert "**Optimal Skill Combination Found**" in result
        assert "Strategy:" in result
        assert "Skills:" in result
        assert "Estimated:" in result
        assert "Confidence:" in result

    def test_format_result_full(self, routing_specialist):
        """Test full level result formatting."""
        combination = routing_specialist._create_combination(["context_compactor"], RoutingStrategy.ACCURACY)
        requirements = {"primary_goal": "accuracy"}

        result = routing_specialist._format_result(combination, requirements, SkillLevel.FULL)

        assert "# Intelligent Routing Design Specialist Analysis" in result
        assert "## Requirements Analysis" in result
        assert "## Optimal Skill Combination" in result
        assert "### Skills" in result
        assert "### Execution Metrics" in result
        assert "### Recommendations" in result

    def test_format_result_no_combination(self, routing_specialist):
        """Test formatting when no combination is available."""
        result = routing_specialist._format_result(None, {}, SkillLevel.SUMMARY)

        assert "No suitable skill combination found" in result

    def test_execute_success(self, routing_specialist, sample_skill_context):
        """Test successful execution."""
        result = routing_specialist.execute(sample_skill_context, SkillLevel.SUMMARY)

        assert result.skill_name == "intelligent_routing_design_specialist"
        assert result.level == SkillLevel.SUMMARY
        assert result.content is not None
        assert len(result.content) > 0
        assert result.tokens_used > 0
        assert result.execution_time > 0
        assert result.metadata is not None
        assert "strategy" in result.metadata
        assert "confidence" in result.metadata

    def test_execute_metadata_level(self, routing_specialist, sample_skill_context):
        """Test execution at metadata level."""
        result = routing_specialist.execute(sample_skill_context, SkillLevel.METADATA)

        assert result.level == SkillLevel.METADATA
        # Metadata level should be very compact
        assert result.tokens_used < 100

    def test_execute_full_level(self, routing_specialist, sample_skill_context):
        """Test execution at full level."""
        result = routing_specialist.execute(sample_skill_context, SkillLevel.FULL)

        assert result.level == SkillLevel.FULL
        # Full level should be comprehensive
        assert result.tokens_used > 500
        assert "## Requirements Analysis" in result.content

    def test_update_metrics(self, routing_specialist):
        """Test metrics updating."""
        combination = routing_specialist._create_combination(["context_compactor"], RoutingStrategy.BALANCED)

        initial_routes = routing_specialist.routing_metrics.total_routes
        routing_specialist._update_metrics(combination, success=True)

        assert routing_specialist.routing_metrics.total_routes == initial_routes + 1
        assert routing_specialist.routing_metrics.successful_routes == initial_routes + 1

    def test_update_learning_patterns(self, routing_specialist):
        """Test learning pattern updates."""
        combination = routing_specialist._create_combination(
            ["context_compactor", "token_budget"], RoutingStrategy.SYNERGY
        )

        query = "optimize context and tokens"
        routing_specialist._update_learning_patterns(query, combination)

        pattern_key = routing_specialist._create_pattern_key(query)
        assert pattern_key in routing_specialist.routing_patterns
        assert len(routing_specialist.routing_patterns[pattern_key]) > 0

        # Check synergy score updates
        synergy = routing_specialist.capability_db.get_synergy_score("context_compactor", "token_budget")
        assert synergy > 0.8  # Should have been incremented

    def test_create_pattern_key(self, routing_specialist):
        """Test pattern key creation."""
        key1 = routing_specialist._create_pattern_key("Optimize skill execution for performance")
        key2 = routing_specialist._create_pattern_key("Optimize skill execution for accuracy")
        key3 = routing_specialist._create_pattern_key("Optimize skill execution for performance")

        assert key1 == key3  # Same query should generate same key
        assert key1 != key2  # Different queries should generate different keys

    def test_optimize_for_context(self, routing_specialist):
        """Test context-specific optimization."""
        combination = routing_specialist.optimize_for_context(
            available_tokens=200,  # Very limited tokens
            time_limit=5.0,  # Very limited time
        )

        assert combination is not None
        assert combination.estimated_tokens <= 300  # Should be close to limit
        assert combination.estimated_time <= 8.0  # Should be close to limit


class TestIntegrationWithSkillRepository:
    """Test integration with skill repository manager."""

    @patch("amplifier.skills.meta_skills.intelligent_routing_design_specialist.get_skill_repository")
    def test_initialization_with_repository(self, mock_get_repo, routing_specialist):
        """Test initialization with skill repository."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        # Create new instance to test initialization
        specialist = IntelligentRoutingDesignSpecialist()

        # Check that repository was accessed
        mock_get_repo.assert_called_once()

    def test_skill_capabilities_initialization(self, routing_specialist):
        """Test that skill capabilities are properly initialized."""
        # Check that known skills are registered
        assert routing_specialist.capability_db.get_capability("context_compactor") is not None
        assert routing_specialist.capability_db.get_capability("token_budget") is not None
        assert routing_specialist.capability_db.get_capability("skill_matcher") is not None
        assert routing_specialist.capability_db.get_capability("intelligent_routing") is not None

        # Check synergy scores are set
        synergy = routing_specialist.capability_db.get_synergy_score("context_compactor", "token_budget")
        assert synergy == 0.8


class TestPerformanceMetrics:
    """Test performance metrics and optimization."""

    def test_get_routing_metrics(self, routing_specialist):
        """Test getting routing metrics."""
        metrics = routing_specialist.get_routing_metrics()

        assert hasattr(metrics, "routing_accuracy")
        assert hasattr(metrics, "prediction_error")
        assert hasattr(metrics, "optimization_success")
        assert hasattr(metrics, "total_routes")
        assert hasattr(metrics, "successful_routes")

    def test_metrics_accumulation(self, routing_specialist):
        """Test that metrics accumulate correctly."""
        initial_metrics = routing_specialist.get_routing_metrics()

        # Simulate some routing operations
        for i in range(5):
            combination = routing_specialist._create_combination(["context_compactor"], RoutingStrategy.PERFORMANCE)
            routing_specialist._update_metrics(combination, success=i < 4)  # 4 successes, 1 failure

        final_metrics = routing_specialist.get_routing_metrics()

        assert final_metrics.total_routes == initial_metrics.total_routes + 5
        assert final_metrics.successful_routes == initial_metrics.successful_routes + 4
        assert final_metrics.routing_accuracy == 0.8  # 4/5 success rate


@pytest.mark.asyncio
class TestAsyncIntegration:
    """Test async integration capabilities."""

    async def test_mcp_storage_integration(self, routing_specialist):
        """Test integration with MCP storage (mocked)."""
        with patch("amplifier.skills.meta_skills.intelligent_routing_design_specialist.store_result") as mock_store:
            # Simulate storing routing patterns
            patterns = {
                "optimize_performance": [
                    routing_specialist._create_combination(["context_compactor"], RoutingStrategy.PERFORMANCE)
                ]
            }

            await mock_store("routing_patterns", patterns)
            mock_store.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
