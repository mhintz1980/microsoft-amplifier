"""
Tests for base types and interfaces
"""

import pytest
from pydantic import BaseModel

from ..base_types import ConfidenceLevel
from ..base_types import ExecutionContext
from ..base_types import PydanticContract
from ..base_types import SkillConfig
from ..base_types import SkillMetrics
from ..base_types import ValidationIssue
from ..base_types import ValidationLevel
from ..base_types import ValidationMode
from ..base_types import ValidationReport
from ..base_types import ValidationResult
from ..base_types import ValidationRule


class TestSkillConfig:
    """Test SkillConfig class"""

    def test_default_config(self):
        """Test default configuration values"""
        config = SkillConfig(skill_id="test_skill", name="Test Skill", description="A test skill")

        assert config.skill_id == "test_skill"
        assert config.name == "Test Skill"
        assert config.version == "1.0.0"
        assert config.timeout == 30.0
        assert config.zero_hallucination is True
        assert config.compound_multiplier == 1.0

    def test_custom_config(self):
        """Test custom configuration values"""
        config = SkillConfig(
            skill_id="custom_skill",
            name="Custom Skill",
            description="A custom skill",
            timeout=60.0,
            confidence_threshold=0.9,
            compound_multiplier=2.5,
        )

        assert config.timeout == 60.0
        assert config.confidence_threshold == 0.9
        assert config.compound_multiplier == 2.5

    def test_validation_mode_enum(self):
        """Test ValidationMode enum"""
        assert ValidationMode.STRICT.value == "strict"
        assert ValidationMode.LENIENT.value == "lenient"
        assert ValidationMode.PERMISSIVE.value == "permissive"

    def test_confidence_level_enum(self):
        """Test ConfidenceLevel enum"""
        assert ConfidenceLevel.CRITICAL.value == 1.0
        assert ConfidenceLevel.HIGH.value == 0.95
        assert ConfidenceLevel.UNKNOWN.value == 0.0


class TestSkillMetrics:
    """Test SkillMetrics class"""

    def test_initial_metrics(self):
        """Test initial metric values"""
        metrics = SkillMetrics()

        assert metrics.executions == 0
        assert metrics.successful_executions == 0
        assert metrics.success_rate == 0.0
        assert metrics.performance_score == 0.0

    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        metrics = SkillMetrics()

        # Add some executions
        metrics.executions = 10
        metrics.successful_executions = 8

        assert metrics.success_rate == 0.8

    def test_performance_score(self):
        """Test performance score calculation"""
        metrics = SkillMetrics(
            executions=10,
            successful_executions=8,
            average_execution_time=2.0,
            average_confidence=0.9,
            optimization_score=1.5,
        )

        # Should be a weighted average
        assert 0.0 <= metrics.performance_score <= 1.0

    def test_error_rate(self):
        """Test error rate calculation"""
        metrics = SkillMetrics()
        metrics.executions = 10
        metrics.successful_executions = 7

        assert metrics.error_rate == 0.3


class TestExecutionContext:
    """Test ExecutionContext class"""

    def test_default_context(self):
        """Test default execution context"""
        context = ExecutionContext()

        assert context.user_id is None
        assert context.session_id is None
        assert context.validation_mode == ValidationMode.STRICT
        assert context.zero_hallucination is True
        assert context.max_retries == 3

    def test_custom_context(self):
        """Test custom execution context"""
        context = ExecutionContext(
            user_id="user123",
            session_id="session456",
            validation_mode=ValidationMode.LENIENT,
            timeout=60.0,
            max_retries=5,
        )

        assert context.user_id == "user123"
        assert context.session_id == "session456"
        assert context.validation_mode == ValidationMode.LENIENT
        assert context.timeout == 60.0
        assert context.max_retries == 5


class TestValidationResult:
    """Test ValidationResult class"""

    def test_valid_result(self):
        """Test valid validation result"""
        result = ValidationResult(is_valid=True)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert result.confidence_adjustment == 0.0

    def test_invalid_result(self):
        """Test invalid validation result"""
        result = ValidationResult(is_valid=False)

        result.add_error("Invalid format")
        result.add_warning("Missing optional field")

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert result.confidence_adjustment == -0.15  # -0.1 - 0.05

    def test_confidence_adjustment(self):
        """Test confidence adjustment calculation"""
        result = ValidationResult(is_valid=True)

        assert result.confidence_adjustment == 0.0

        result.add_error("Critical error")
        assert result.confidence_adjustment == -0.1

        result.add_warning("Minor warning")
        assert result.confidence_adjustment == -0.15


class TestPydanticContract:
    """Test PydanticContract class"""

    def test_simple_model_validation(self):
        """Test validation with simple Pydantic model"""

        class TestModel(BaseModel):
            name: str
            age: int

        contract = PydanticContract(TestModel)

        # Valid data
        valid_data = {"name": "John", "age": 30}
        result = contract.validate(valid_data)
        assert result.is_valid is True

        # Invalid data
        invalid_data = {"name": "John", "age": "not_a_number"}
        result = contract.validate(invalid_data)
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_schema_generation(self):
        """Test schema generation"""

        class TestModel(BaseModel):
            name: str
            age: int
            email: str = "test@example.com"

        contract = PydanticContract(TestModel)
        schema = contract.get_schema()

        assert "properties" in schema
        assert "name" in schema["properties"]
        assert "age" in schema["properties"]
        assert "email" in schema["properties"]

    def test_sanitization(self):
        """Test data sanitization"""

        class TestModel(BaseModel):
            name: str
            age: int

        contract = PydanticContract(TestModel)

        # Data with extra fields
        data_with_extra = {"name": "John", "age": 30, "extra_field": "should_be_removed", "another_extra": 123}

        sanitized_data, result = contract.sanitize(data_with_extra)

        assert result.is_valid is True
        assert "extra_field" not in sanitized_data
        assert "another_extra" not in sanitized_data
        assert sanitized_data["name"] == "John"
        assert sanitized_data["age"] == 30


class TestValidationReport:
    """Test ValidationReport class"""

    def test_empty_report(self):
        """Test empty validation report"""
        report = ValidationReport(is_valid=True)

        assert report.is_valid is True
        assert len(report.issues) == 0
        assert len(report.validation_rules_applied) == 0
        assert report.confidence_score == 1.0

    def test_report_with_issues(self):
        """Test report with validation issues"""
        report = ValidationReport(is_valid=True)

        # Add different types of issues
        error_issue = ValidationIssue(
            rule=ValidationRule.TYPE_CHECK, level=ValidationLevel.ERROR, message="Type validation failed"
        )

        warning_issue = ValidationIssue(
            rule=ValidationRule.LENGTH_CHECK, level=ValidationLevel.WARNING, message="Length too long"
        )

        report.add_issue(error_issue)
        report.add_issue(warning_issue)

        assert report.is_valid is False  # Error level makes it invalid
        assert len(report.issues) == 2
        assert ValidationRule.TYPE_CHECK in report.validation_rules_applied
        assert ValidationRule.LENGTH_CHECK in report.validation_rules_applied
        assert report.confidence_score < 1.0  # Should be reduced by issues

    def test_issue_filtering(self):
        """Test filtering issues by level and rule"""
        report = ValidationReport(is_valid=True)

        # Add issues
        report.add_issue(
            ValidationIssue(rule=ValidationRule.TYPE_CHECK, level=ValidationLevel.ERROR, message="Type error")
        )

        report.add_issue(
            ValidationIssue(rule=ValidationRule.TYPE_CHECK, level=ValidationLevel.WARNING, message="Type warning")
        )

        report.add_issue(
            ValidationIssue(
                rule=ValidationRule.SECURITY_CHECK, level=ValidationLevel.CRITICAL, message="Security issue"
            )
        )

        # Filter by level
        error_issues = report.get_issues_by_level(ValidationLevel.ERROR)
        assert len(error_issues) == 1
        assert error_issues[0].message == "Type error"

        # Filter by rule
        type_issues = report.get_issues_by_rule(ValidationRule.TYPE_CHECK)
        assert len(type_issues) == 2

    def test_recommendations(self):
        """Test recommendation generation"""
        report = ValidationReport(is_valid=True)

        # Add issues with suggestions
        report.add_issue(
            ValidationIssue(
                rule=ValidationRule.TYPE_CHECK,
                level=ValidationLevel.ERROR,
                message="Invalid type",
                suggestion="Use correct data type",
            )
        )

        recommendations = report._generate_recommendations(report.issues)
        assert len(recommendations) > 0
        assert any("correct data type" in rec for rec in recommendations)


class TestValidationLevel:
    """Test ValidationLevel enum"""

    def test_level_values(self):
        """Test validation level values"""
        assert ValidationLevel.INFO.value == "info"
        assert ValidationLevel.WARNING.value == "warning"
        assert ValidationLevel.ERROR.value == "error"
        assert ValidationLevel.CRITICAL.value == "critical"


class TestValidationRule:
    """Test ValidationRule enum"""

    def test_rule_values(self):
        """Test validation rule values"""
        assert ValidationRule.TYPE_CHECK.value == "type_check"
        assert ValidationRule.RANGE_CHECK.value == "range_check"
        assert ValidationRule.PATTERN_CHECK.value == "pattern_check"
        assert ValidationRule.SECURITY_CHECK.value == "security_check"
        assert ValidationRule.HALLUCINATION_CHECK.value == "hallucination_check"


if __name__ == "__main__":
    pytest.main([__file__])
