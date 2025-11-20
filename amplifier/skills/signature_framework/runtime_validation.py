"""
Runtime Validation System

Comprehensive validation system for skill inputs and outputs with
performance monitoring and adaptive validation strategies.
"""

import json
import logging
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any

from .base_types import ExecutionContext
from .base_types import TypeContract
from .base_types import ValidationMode

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationRule(Enum):
    """Types of validation rules"""

    TYPE_CHECK = "type_check"
    RANGE_CHECK = "range_check"
    PATTERN_CHECK = "pattern_check"
    LENGTH_CHECK = "length_check"
    CUSTOM_CHECK = "custom_check"
    SECURITY_CHECK = "security_check"
    HALLUCINATION_CHECK = "hallucination_check"


@dataclass
class ValidationConfig:
    """Configuration for runtime validation"""

    enable_security_checks: bool = True
    enable_hallucination_detection: bool = True
    enable_performance_monitoring: bool = True
    max_validation_time: float = 5.0  # Maximum time for validation in seconds
    cache_validation_results: bool = True
    strict_type_checking: bool = True
    allow_partial_validation: bool = False


@dataclass
class ValidationIssue:
    """Individual validation issue"""

    rule: ValidationRule
    level: ValidationLevel
    message: str
    field_path: str = ""
    confidence_impact: float = 0.0
    suggestion: str | None = None


@dataclass
class ValidationReport:
    """Comprehensive validation report"""

    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    execution_time: float = 0.0
    validation_rules_applied: set[ValidationRule] = field(default_factory=set)
    confidence_score: float = 1.0
    recommendations: list[str] = field(default_factory=list)

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue"""
        self.issues.append(issue)
        self.validation_rules_applied.add(issue.rule)

        # Update confidence score
        if issue.level == ValidationLevel.CRITICAL:
            self.confidence_score *= 0.5
        elif issue.level == ValidationLevel.ERROR:
            self.confidence_score *= 0.7
        elif issue.level == ValidationLevel.WARNING:
            self.confidence_score *= 0.9

        # Mark as invalid if critical or error issues exist
        if issue.level in [ValidationLevel.CRITICAL, ValidationLevel.ERROR]:
            self.is_valid = False

    def get_issues_by_level(self, level: ValidationLevel) -> list[ValidationIssue]:
        """Get issues filtered by level"""
        return [issue for issue in self.issues if issue.level == level]

    def get_issues_by_rule(self, rule: ValidationRule) -> list[ValidationIssue]:
        """Get issues filtered by rule"""
        return [issue for issue in self.issues if issue.rule == rule]


class RuntimeValidator:
    """Advanced runtime validation system for signature-based skills"""

    def __init__(self, config: ValidationConfig | None = None):
        self.config = config or ValidationConfig()
        self._validation_cache: dict[str, ValidationReport] = {}
        self._custom_validators: dict[str, Callable] = {}
        self._security_patterns: list[re.Pattern] = []
        self._hallucination_patterns: list[re.Pattern] = []

        # Initialize security patterns
        self._setup_security_patterns()

        # Initialize hallucination patterns
        self._setup_hallucination_patterns()

    def _setup_security_patterns(self):
        """Setup security validation patterns"""
        self._security_patterns = [
            # SQL injection patterns
            re.compile(r"(union|select|insert|update|delete|drop)\s+", re.IGNORECASE),
            re.compile(r'["\']\s*;\s*(union|select|insert)', re.IGNORECASE),
            # XSS patterns
            re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE),
            re.compile(r"javascript:", re.IGNORECASE),
            # Command injection patterns
            re.compile(r"[;&|`$()]", re.IGNORECASE),
            re.compile(r"\.\./", re.IGNORECASE),
            # Path traversal
            re.compile(r"\.\.[\\/]", re.IGNORECASE),
            # Suspicious content
            re.compile(r"(password|secret|key|token)\s*[:=]\s*\S+", re.IGNORECASE),
        ]

    def _setup_hallucination_patterns(self):
        """Setup hallucination detection patterns"""
        self._hallucination_patterns = [
            # Uncertainty indicators
            re.compile(r"\b(i think|i believe|probably|maybe|perhaps|might|could|possibly)\b", re.IGNORECASE),
            re.compile(r"\b(seems like|appears to be|i guess|i suppose)\b", re.IGNORECASE),
            # Lack of confidence
            re.compile(r"\b(not sure|uncertain|unclear|don\'t know|cannot say)\b", re.IGNORECASE),
            # Hedging language
            re.compile(r"\b(sort of|kind of|rather|quite|somewhat)\b", re.IGNORECASE),
            # Speculation
            re.compile(r"\b(presumably|ostensibly|apparently|supposedly)\b", re.IGNORECASE),
            # Avoidance
            re.compile(r"\b(may|might|could be|would be)\s+be\s+the\s+case", re.IGNORECASE),
        ]

    def add_custom_validator(self, name: str, validator: Callable[[Any], ValidationReport]):
        """Add a custom validation function"""
        self._custom_validators[name] = validator

    async def validate_input(
        self, data: Any, contract: TypeContract | None = None, context: ExecutionContext | None = None
    ) -> ValidationReport:
        """Comprehensive input validation"""
        start_time = time.time()

        # Check cache first
        if self.config.cache_validation_results:
            cache_key = self._create_cache_key(data, "input")
            if cache_key in self._validation_cache:
                return self._validation_cache[cache_key]

        report = ValidationReport(is_valid=True)

        try:
            # Type validation
            if contract:
                type_result = await self._validate_type_contract(data, contract)
                report.issues.extend(type_result.issues)
                report.validation_rules_applied.update(type_result.validation_rules_applied)

            # Security validation
            if self.config.enable_security_checks:
                security_result = await self._validate_security(data)
                report.issues.extend(security_result.issues)
                report.validation_rules_applied.update(security_result.validation_rules_applied)

            # Hallucination validation
            if self.config.enable_hallucination_detection:
                hallucination_result = await self._validate_hallucination(data)
                report.issues.extend(hallucination_result.issues)
                report.validation_rules_applied.update(hallucination_result.validation_rules_applied)

            # Custom validators
            for name, validator in self._custom_validators.items():
                try:
                    custom_result = validator(data)
                    if isinstance(custom_result, ValidationReport):
                        report.issues.extend(custom_result.issues)
                        report.validation_rules_applied.update(custom_result.validation_rules_applied)
                except Exception as e:
                    logger.warning(f"Custom validator {name} failed: {e}")

            # Update report status
            report.is_valid = all(
                issue.level not in [ValidationLevel.CRITICAL, ValidationLevel.ERROR] for issue in report.issues
            )

            # Generate recommendations
            report.recommendations = self._generate_recommendations(report.issues)

            # Cache result
            if self.config.cache_validation_results:
                self._validation_cache[cache_key] = report

        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            report.add_issue(
                ValidationIssue(
                    rule=ValidationRule.CUSTOM_CHECK,
                    level=ValidationLevel.CRITICAL,
                    message=f"Validation system error: {str(e)}",
                )
            )

        finally:
            report.execution_time = time.time() - start_time

        return report

    async def validate_output(
        self, data: Any, contract: TypeContract | None = None, context: ExecutionContext | None = None
    ) -> ValidationReport:
        """Comprehensive output validation"""
        start_time = time.time()

        # Check cache first
        if self.config.cache_validation_results:
            cache_key = self._create_cache_key(data, "output")
            if cache_key in self._validation_cache:
                return self._validation_cache[cache_key]

        report = ValidationReport(is_valid=True)

        try:
            # Type validation
            if contract:
                type_result = await self._validate_type_contract(data, contract)
                report.issues.extend(type_result.issues)
                report.validation_rules_applied.update(type_result.validation_rules_applied)

            # Hallucination validation (more strict for outputs)
            if self.config.enable_hallucination_detection:
                hallucination_result = await self._validate_hallucination_strict(data)
                report.issues.extend(hallucination_result.issues)
                report.validation_rules_applied.update(hallucination_result.validation_rules_applied)

            # Quality validation
            quality_result = await self._validate_output_quality(data)
            report.issues.extend(quality_result.issues)
            report.validation_rules_applied.update(quality_result.validation_rules_applied)

            # Update report status
            report.is_valid = all(
                issue.level not in [ValidationLevel.CRITICAL, ValidationLevel.ERROR] for issue in report.issues
            )

            # Generate recommendations
            report.recommendations = self._generate_recommendations(report.issues)

            # Cache result
            if self.config.cache_validation_results:
                self._validation_cache[cache_key] = report

        except Exception as e:
            logger.error(f"Output validation failed: {e}")
            report.add_issue(
                ValidationIssue(
                    rule=ValidationRule.CUSTOM_CHECK,
                    level=ValidationLevel.CRITICAL,
                    message=f"Output validation error: {str(e)}",
                )
            )

        finally:
            report.execution_time = time.time() - start_time

        return report

    async def _validate_type_contract(self, data: Any, contract: TypeContract) -> ValidationReport:
        """Validate data against type contract"""
        report = ValidationReport(is_valid=True)

        try:
            validation_result = contract.validate(data)

            if not validation_result.is_valid:
                for error in validation_result.errors:
                    report.add_issue(
                        ValidationIssue(
                            rule=ValidationRule.TYPE_CHECK,
                            level=ValidationLevel.ERROR,
                            message=f"Type validation failed: {error}",
                            suggestion="Check input data format and required fields",
                        )
                    )

            if validation_result.warnings:
                for warning in validation_result.warnings:
                    report.add_issue(
                        ValidationIssue(
                            rule=ValidationRule.TYPE_CHECK,
                            level=ValidationLevel.WARNING,
                            message=f"Type validation warning: {warning}",
                        )
                    )

            report.confidence_score += validation_result.confidence_adjustment

        except Exception as e:
            report.add_issue(
                ValidationIssue(
                    rule=ValidationRule.TYPE_CHECK,
                    level=ValidationLevel.CRITICAL,
                    message=f"Type contract validation error: {str(e)}",
                )
            )

        return report

    async def _validate_security(self, data: Any) -> ValidationReport:
        """Validate data for security issues"""
        report = ValidationReport(is_valid=True)

        if not isinstance(data, (str, dict, list)):
            return report

        # Convert data to string for pattern matching
        text_data = json.dumps(data) if isinstance(data, (dict, list)) else str(data)

        for pattern in self._security_patterns:
            matches = pattern.findall(text_data)
            if matches:
                report.add_issue(
                    ValidationIssue(
                        rule=ValidationRule.SECURITY_CHECK,
                        level=ValidationLevel.CRITICAL,
                        message=f"Security pattern detected: {pattern.pattern}",
                        suggestion="Remove potentially dangerous content",
                        confidence_impact=0.5,
                    )
                )

        # Check for sensitive data exposure
        sensitive_patterns = [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Credit card
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b",  # IP address
        ]

        for pattern in sensitive_patterns:
            matches = re.findall(pattern, text_data)
            if matches:
                report.add_issue(
                    ValidationIssue(
                        rule=ValidationRule.SECURITY_CHECK,
                        level=ValidationLevel.WARNING,
                        message=f"Sensitive data pattern detected: {len(matches)} matches",
                        suggestion="Consider masking or removing sensitive information",
                        confidence_impact=0.1,
                    )
                )

        return report

    async def _validate_hallucination(self, data: Any) -> ValidationReport:
        """Validate data for hallucination indicators"""
        report = ValidationReport(is_valid=True)

        if not isinstance(data, str):
            return report

        text_lower = data.lower()
        total_patterns = len(self._hallucination_patterns)
        matched_patterns = 0
        hallucination_score = 0.0

        for pattern in self._hallucination_patterns:
            matches = pattern.findall(data)
            if matches:
                matched_patterns += 1
                hallucination_score += len(matches) * 0.1

        # Calculate overall hallucination score
        if total_patterns > 0:
            pattern_ratio = matched_patterns / total_patterns
            hallucination_score = min(1.0, hallucination_score + pattern_ratio * 0.5)

        if hallucination_score > 0.1:
            level = ValidationLevel.WARNING if hallucination_score < 0.3 else ValidationLevel.ERROR
            report.add_issue(
                ValidationIssue(
                    rule=ValidationRule.HALLUCINATION_CHECK,
                    level=level,
                    message=f"Hallucination indicators detected (score: {hallucination_score:.2f})",
                    suggestion="Review content for accuracy and confidence",
                    confidence_impact=hallucination_score * 0.5,
                )
            )

        return report

    async def _validate_hallucination_strict(self, data: Any) -> ValidationReport:
        """Strict hallucination validation for outputs"""
        report = await self._validate_hallucination(data)

        # Additional strict checks for outputs
        if isinstance(data, str):
            # Check for incomplete or evasive responses
            incomplete_patterns = [
                r"\b(i cannot|i cannot help|i\'m not able|unable to)\b",
                r"\b(no information|insufficient data|cannot determine)\b",
                r"\b(contact.*support|consult.*documentation|refer to.*manual)\b",
            ]

            text_lower = data.lower()
            for pattern in incomplete_patterns:
                if re.search(pattern, text_lower):
                    report.add_issue(
                        ValidationIssue(
                            rule=ValidationRule.HALLUCINATION_CHECK,
                            level=ValidationLevel.WARNING,
                            message="Evasive or incomplete response detected",
                            suggestion="Provide more complete and direct answers",
                        )
                    )

            # Check for boilerplate or generic responses
            generic_indicators = [
                "thank you for your question",
                "as an ai assistant",
                "please note that",
                "it's important to remember",
                "keep in mind that",
            ]

            generic_count = sum(1 for indicator in generic_indicators if indicator in text_lower)
            if generic_count > 2:
                report.add_issue(
                    ValidationIssue(
                        rule=ValidationRule.HALLUCINATION_CHECK,
                        level=ValidationLevel.WARNING,
                        message="Generic or boilerplate response detected",
                        suggestion="Provide more specific and tailored responses",
                    )
                )

        return report

    async def _validate_output_quality(self, data: Any) -> ValidationReport:
        """Validate output quality metrics"""
        report = ValidationReport(is_valid=True)

        if isinstance(data, str):
            # Length validation
            if len(data) < 10:
                report.add_issue(
                    ValidationIssue(
                        rule=ValidationRule.LENGTH_CHECK,
                        level=ValidationLevel.WARNING,
                        message="Output is very short",
                        suggestion="Provide more detailed responses",
                    )
                )
            elif len(data) > 10000:
                report.add_issue(
                    ValidationIssue(
                        rule=ValidationRule.LENGTH_CHECK,
                        level=ValidationLevel.WARNING,
                        message="Output is very long",
                        suggestion="Consider being more concise",
                    )
                )

            # Character set validation
            if not data.strip():
                report.add_issue(
                    ValidationIssue(
                        rule=ValidationRule.CUSTOM_CHECK,
                        level=ValidationLevel.ERROR,
                        message="Output is empty or whitespace only",
                    )
                )

            # Repetition check
            words = data.lower().split()
            if len(words) > 10:
                unique_words = set(words)
                repetition_ratio = 1 - (len(unique_words) / len(words))
                if repetition_ratio > 0.5:
                    report.add_issue(
                        ValidationIssue(
                            rule=ValidationRule.CUSTOM_CHECK,
                            level=ValidationLevel.WARNING,
                            message="High repetition detected in output",
                            suggestion="Reduce repetitive content",
                        )
                    )

        return report

    def _create_cache_key(self, data: Any, validation_type: str) -> str:
        """Create a cache key for validation results"""
        try:
            # Create a hash of the data and type
            data_str = json.dumps(data, sort_keys=True, default=str)
            import hashlib

            return hashlib.md5(f"{validation_type}:{data_str}".encode()).hexdigest()
        except Exception:
            # Fallback to string representation
            return f"{validation_type}:{str(hash(str(data)))}"

    def _generate_recommendations(self, issues: list[ValidationIssue]) -> list[str]:
        """Generate recommendations based on validation issues"""
        recommendations = []

        error_counts = {}
        for issue in issues:
            error_counts[issue.rule] = error_counts.get(issue.rule, 0) + 1

        # General recommendations based on issue types
        if ValidationRule.TYPE_CHECK in error_counts:
            recommendations.append("Review input/output data formats and ensure they match expected types")

        if ValidationRule.SECURITY_CHECK in error_counts:
            recommendations.append("Implement input sanitization and security validation")

        if ValidationRule.HALLUCINATION_CHECK in error_counts:
            recommendations.append("Improve response confidence and reduce uncertainty indicators")

        if ValidationRule.LENGTH_CHECK in error_counts:
            recommendations.append("Balance response length for better user experience")

        # Add specific suggestions from issues
        for issue in issues:
            if issue.suggestion and issue.suggestion not in recommendations:
                recommendations.append(issue.suggestion)

        return recommendations[:5]  # Limit to top 5 recommendations

    def get_validation_stats(self) -> dict[str, Any]:
        """Get validation performance statistics"""
        total_validations = len(self._validation_cache)
        critical_issues = sum(
            1
            for report in self._validation_cache.values()
            if any(issue.level == ValidationLevel.CRITICAL for issue in report.issues)
        )

        return {
            "cache_size": total_validations,
            "critical_issue_rate": critical_issues / max(1, total_validations),
            "security_patterns_loaded": len(self._security_patterns),
            "hallucination_patterns_loaded": len(self._hallucination_patterns),
            "custom_validators": len(self._custom_validators),
        }

    def clear_cache(self):
        """Clear validation cache"""
        self._validation_cache.clear()

    def add_security_pattern(self, pattern: str, flags: int = re.IGNORECASE):
        """Add a custom security pattern"""
        try:
            compiled_pattern = re.compile(pattern, flags)
            self._security_patterns.append(compiled_pattern)
        except re.error as e:
            logger.error(f"Invalid security pattern '{pattern}': {e}")

    def add_hallucination_pattern(self, pattern: str, flags: int = re.IGNORECASE):
        """Add a custom hallucination detection pattern"""
        try:
            compiled_pattern = re.compile(pattern, flags)
            self._hallucination_patterns.append(compiled_pattern)
        except re.error as e:
            logger.error(f"Invalid hallucination pattern '{pattern}': {e}")


# Global validator instance
_global_validator = None


def get_runtime_validator(config: ValidationConfig | None = None) -> RuntimeValidator:
    """Get or create the global runtime validator"""
    global _global_validator
    if _global_validator is None:
        _global_validator = RuntimeValidator(config)
    return _global_validator


# Decorator for automatic validation
def validate_output(
    input_contract: TypeContract | None = None,
    output_contract: TypeContract | None = None,
    validator: RuntimeValidator | None = None,
):
    """
    Decorator for automatic input/output validation

    Usage:
        @validate_output(
            input_contract=PydanticContract(MyInputModel),
            output_contract=PydanticContract(MyOutputModel)
        )
        async def my_skill(input_data, context):
            return process_data(input_data)
    """

    def decorator(func):
        async def wrapper(input_data: Any, context: ExecutionContext) -> Any:
            val = validator or get_runtime_validator()

            # Validate input
            if input_contract:
                input_report = await val.validate_input(input_data, input_contract, context)
                if not input_report.is_valid and context.validation_mode == ValidationMode.STRICT:
                    raise ValueError(f"Input validation failed: {input_report.issues}")

            # Execute function
            result = await func(input_data, context)

            # Validate output
            if output_contract:
                output_report = await val.validate_output(result, output_contract, context)
                if not output_report.is_valid and context.validation_mode == ValidationMode.STRICT:
                    raise ValueError(f"Output validation failed: {output_report.issues}")

            return result

        return wrapper

    return decorator
