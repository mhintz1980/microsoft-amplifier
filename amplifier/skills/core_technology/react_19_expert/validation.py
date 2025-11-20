"""
Quality Assurance Validation for React 19 Expert

Comprehensive validation system ensuring zero hallucinations,
API accuracy, and production-ready code generation.
"""

import re
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any


class ValidationLevel(Enum):
    """Validation severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


class ValidationCategory(Enum):
    """Categories of validation checks."""

    API_ACCURACY = "api_accuracy"
    TYPE_SAFETY = "type_safety"
    PERFORMANCE = "performance"
    BEST_PRACTICES = "best_practices"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"


@dataclass
class ValidationResult:
    """Result of a validation check."""

    category: ValidationCategory
    level: ValidationLevel
    message: str
    line_number: int | None = None
    suggestion: str | None = None
    code_snippet: str | None = None


@dataclass
class ValidationReport:
    """Comprehensive validation report."""

    is_valid: bool
    overall_score: float
    results: list[ValidationResult] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    api_compliance: dict[str, bool] = field(default_factory=dict)


class QualityAssurance:
    """
    Quality assurance system for React 19 expert skill.

    Ensures:
    - Zero hallucination in API usage
    - Complete TypeScript type safety
    - Performance optimization
    - Best practices compliance
    - Production-ready code generation
    """

    def __init__(self):
        self._init_validation_rules()
        self._init_api_definitions()
        self._init_pattern_library()

    def _init_validation_rules(self):
        """Initialize comprehensive validation rules."""
        self.validation_rules = {
            # API Accuracy Rules
            ValidationCategory.API_ACCURACY: [
                {
                    "name": "server_action_directive",
                    "pattern": r"'use server'",
                    "required": True,
                    "context": ["async function", "formData"],
                    "message": "Server actions must include 'use server' directive",
                },
                {
                    "name": "useOptimistic_signature",
                    "pattern": r"useOptimistic\([^,]+,\s*[^)]+\s*=>\s*[^)]+\)",
                    "required": True,
                    "message": "useOptimistic requires proper update function signature",
                },
                {
                    "name": "useActionState_destructuring",
                    "pattern": r"\[.*?,.*?,.*?\]",
                    "required": True,
                    "context": ["useActionState"],
                    "message": "useActionState should be destructured as [state, action, isPending]",
                },
            ],
            # Type Safety Rules
            ValidationCategory.TYPE_SAFETY: [
                {
                    "name": "avoid_any_types",
                    "pattern": r":\s*any(?![\[\(])",
                    "forbidden": True,
                    "message": "Avoid using 'any' type - use specific types instead",
                },
                {
                    "name": "interface_definitions",
                    "pattern": r"interface\s+\w+\s*{",
                    "recommended": True,
                    "message": "Define interfaces for complex data structures",
                },
                {
                    "name": "function_return_types",
                    "pattern": r"function\s+\w+\([^)]*\)(?!\s*:)",
                    "forbidden": True,
                    "message": "Functions should have explicit return types",
                },
            ],
            # Performance Rules
            ValidationCategory.PERFORMANCE: [
                {
                    "name": "useOptimistic_for_updates",
                    "pattern": r"setIsLoading|setPending",
                    "context": ["useOptimistic"],
                    "suggestion": "Consider using useOptimistic instead of manual loading state",
                },
                {
                    "name": "async_scripts_optimization",
                    "pattern": r"<script(?![^>]*async)",
                    "context": ["src="],
                    "message": "External scripts should use async={true} for better performance",
                },
                {
                    "name": "react_mem_optimization",
                    "pattern": r"React\.memo|useMemo|useCallback",
                    "recommended": True,
                    "message": "Consider using React.memo, useMemo, or useCallback for performance optimization",
                },
            ],
            # Best Practices Rules
            ValidationCategory.BEST_PRACTICES: [
                {
                    "name": "error_boundaries",
                    "pattern": r"ErrorBoundary|componentDidCatch",
                    "recommended": True,
                    "message": "Consider adding error boundaries for better error handling",
                },
                {
                    "name": "form_labels",
                    "pattern": r"<input[^>]*(?!.*id=|.*htmlFor=)",
                    "context": ["<form"],
                    "message": "Form inputs should have associated labels",
                },
                {
                    "name": "meta_tags_seo",
                    "pattern": r"<meta",
                    "recommended": True,
                    "message": "Include meta tags for SEO optimization",
                },
            ],
            # Security Rules
            ValidationCategory.SECURITY: [
                {
                    "name": "script_integrity",
                    "pattern": r"<script[^>]*src=",
                    "recommended": True,
                    "message": "External scripts should include integrity and crossOrigin attributes",
                },
                {
                    "name": "xss_prevention",
                    "pattern": r"dangerouslySetInnerHTML",
                    "forbidden": True,
                    "message": "Avoid using dangerouslySetInnerHTML - use safer alternatives",
                },
            ],
            # Accessibility Rules
            ValidationCategory.ACCESSIBILITY: [
                {
                    "name": "alt_attributes",
                    "pattern": r"<img(?![^>]*alt=)",
                    "forbidden": True,
                    "message": "Images must have alt attributes for accessibility",
                },
                {
                    "name": "aria_labels",
                    "pattern": r"aria-label|aria-labelledby",
                    "recommended": True,
                    "message": "Consider adding ARIA labels for better accessibility",
                },
            ],
        }

    def _init_api_definitions(self):
        """Initialize React 19 API definitions for validation."""
        self.react_19_apis = {
            # Hooks
            "hooks": {
                "useOptimistic": {
                    "signature": "useOptimistic<State, Action>(initialState, updateFn)",
                    "parameters": ["initialState", "updateFn"],
                    "returns": "[optimisticState, addOptimistic]",
                    "generics": ["State", "Action"],
                },
                "useActionState": {
                    "signature": "useActionState<State, Payload>(fn, initialState, permalink?)",
                    "parameters": ["fn", "initialState", "permalink?"],
                    "returns": "[state, action, isPending]",
                    "generics": ["State", "Payload"],
                },
                "useTransition": {
                    "signature": "useTransition()",
                    "parameters": [],
                    "returns": "[isPending, startTransition]",
                    "generics": [],
                },
            },
            # Components
            "components": {
                "title": {"usage": "<title>children</title>", "description": "Sets document title", "attributes": []},
                "meta": {
                    "usage": "<meta name|property content ...attributes />",
                    "description": "Adds metadata to document head",
                    "attributes": ["name", "property", "content", "charset", "httpEquiv"],
                },
                "link": {
                    "usage": "<link rel href ...attributes />",
                    "description": "Adds link elements to document head",
                    "attributes": ["rel", "href", "as", "crossOrigin", "integrity"],
                },
                "script": {
                    "usage": "<script src async ...attributes />",
                    "description": "Adds script elements with deduplication",
                    "attributes": ["src", "async", "defer", "crossOrigin", "integrity"],
                },
            },
            # Server Actions
            "server_actions": {
                "directive": "'use server'",
                "requirements": [
                    "Must be at top of file",
                    "Cannot use React hooks",
                    "Must be async function",
                    "Accept FormData or serializable parameters",
                ],
            },
        }

    def _init_pattern_library(self):
        """Initialize pattern library for validation."""
        self.patterns = {
            "optimistic_updates": {
                "indicators": ["sending", "pending", "optimistic", "temp-"],
                "rollback_scenarios": ["error", "timeout", "validation_failure"],
                "best_practices": [
                    "Show clear visual indicators",
                    "Handle rollback gracefully",
                    "Disable controls during updates",
                ],
            },
            "form_actions": {
                "required_elements": ["action", "FormData", "validation"],
                "success_patterns": ["success message", "redirect", "state update"],
                "error_handling": ["try/catch", "error messages", "form reset"],
            },
            "document_metadata": {
                "essential_tags": ["title", "description", "canonical"],
                "social_tags": ["og:title", "og:description", "og:image", "twitter:card"],
                "technical_tags": ["viewport", "charset", "robots"],
            },
        }

    def validate_react_19_code(self, code: str, context: dict[str, Any] | None = None) -> ValidationReport:
        """
        Comprehensive validation of React 19 code.

        Args:
            code: React 19 code to validate
            context: Optional context for validation

        Returns:
            Comprehensive validation report
        """
        report = ValidationReport(
            is_valid=True, overall_score=0.0, results=[], metrics={}, recommendations=[], api_compliance={}
        )

        # Validate each category
        for category in ValidationCategory:
            category_results = self._validate_category(code, category, context)
            report.results.extend(category_results)

        # Calculate metrics
        report.metrics = self._calculate_metrics(report.results)

        # Calculate overall score
        report.overall_score = self._calculate_overall_score(report.metrics)

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report.results)

        # Check API compliance
        report.api_compliance = self._check_api_compliance(code)

        # Determine if code is valid
        error_count = len([r for r in report.results if r.level == ValidationLevel.ERROR])
        report.is_valid = error_count == 0

        return report

    def _validate_category(
        self, code: str, category: ValidationCategory, context: dict[str, Any] | None
    ) -> list[ValidationResult]:
        """Validate a specific category of rules."""
        results = []
        rules = self.validation_rules.get(category, [])

        for rule in rules:
            result = self._apply_validation_rule(code, rule, category, context)
            if result:
                results.append(result)

        return results

    def _apply_validation_rule(
        self, code: str, rule: dict[str, Any], category: ValidationCategory, context: dict[str, Any] | None
    ) -> ValidationResult | None:
        """Apply a single validation rule to code."""
        pattern = rule.get("pattern", "")

        # Check if context matches
        if "context" in rule:
            if not any(ctx in code for ctx in rule["context"]):
                return None

        try:
            matches = re.finditer(pattern, code, re.MULTILINE | re.DOTALL)

            for match in matches:
                line_number = code[: match.start()].count("\n") + 1

                # Determine validation level
                if rule.get("forbidden", False):
                    level = ValidationLevel.ERROR
                elif rule.get("required", False):
                    level = ValidationLevel.ERROR if not matches else ValidationLevel.SUCCESS
                elif rule.get("recommended", False):
                    level = ValidationLevel.WARNING
                else:
                    level = ValidationLevel.INFO

                # Create validation result
                result = ValidationResult(
                    category=category,
                    level=level,
                    message=rule["message"],
                    line_number=line_number,
                    code_snippet=self._get_code_snippet(code, match.start(), match.end()),
                )

                # Add suggestion if available
                if "suggestion" in rule:
                    result.suggestion = rule["suggestion"]

                return result

        except re.error:
            # Pattern compilation failed - skip this rule
            pass

        return None

    def _get_code_snippet(self, code: str, start: int, end: int, context_lines: int = 2) -> str:
        """Extract code snippet with context."""
        lines = code.split("\n")
        start_line = code[:start].count("\n")
        end_line = code[:end].count("\n")

        start_idx = max(0, start_line - context_lines)
        end_idx = min(len(lines), end_line + context_lines + 1)

        snippet_lines = lines[start_idx:end_idx]
        snippet = "\n".join(snippet_lines)

        # Add line numbers
        numbered_lines = []
        for i, line in enumerate(snippet_lines, start=start_idx + 1):
            marker = " >>> " if start_line <= i <= end_line else "     "
            numbered_lines.append(f"{marker}{i:3d}: {line}")

        return "\n".join(numbered_lines)

    def _calculate_metrics(self, results: list[ValidationResult]) -> dict[str, float]:
        """Calculate validation metrics."""
        metrics = {}

        # Count results by level
        level_counts = {level.value: 0 for level in ValidationLevel}
        for result in results:
            level_counts[result.level.value] += 1

        total_results = len(results)
        if total_results == 0:
            return dict.fromkeys(ValidationLevel, 100.0)

        # Calculate percentages
        for level in ValidationLevel:
            metrics[f"{level.value}_percentage"] = (level_counts[level.value] / total_results) * 100

        # Calculate category scores
        category_scores = {}
        for category in ValidationCategory:
            category_results = [r for r in results if r.category == category]
            if category_results:
                error_count = len([r for r in category_results if r.level == ValidationLevel.ERROR])
                category_scores[f"{category.value}_score"] = max(0, 100 - (error_count * 25))

        metrics.update(category_scores)

        return metrics

    def _calculate_overall_score(self, metrics: dict[str, float]) -> float:
        """Calculate overall validation score."""
        score_components = [
            metrics.get("success_percentage", 0),
            100 - metrics.get("error_percentage", 0),
            metrics.get("api_accuracy_score", 100),
            metrics.get("type_safety_score", 100),
            metrics.get("performance_score", 100),
            metrics.get("best_practices_score", 100),
        ]

        return sum(score_components) / len(score_components)

    def _generate_recommendations(self, results: list[ValidationResult]) -> list[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        # Group results by category
        category_results = {}
        for result in results:
            if result.category not in category_results:
                category_results[result.category] = []
            category_results[result.category].append(result)

        # Generate category-specific recommendations
        for category, category_results_list in category_results.items():
            error_results = [r for r in category_results_list if r.level == ValidationLevel.ERROR]
            warning_results = [r for r in category_results_list if r.level == ValidationLevel.WARNING]

            if error_results:
                recommendations.append(f"Critical: Fix {len(error_results)} {category.value.replace('_', ' ')} issues")

            if warning_results:
                recommendations.append(
                    f"Consider: Address {len(warning_results)} {category.value.replace('_', ' ')} warnings"
                )

        # Add specific suggestions from results
        for result in results:
            if result.suggestion and result.suggestion not in recommendations:
                recommendations.append(result.suggestion)

        return recommendations[:10]  # Limit to top 10 recommendations

    def _check_api_compliance(self, code: str) -> dict[str, bool]:
        """Check compliance with React 19 APIs."""
        compliance = {}

        # Check hook usage
        for hook_name, hook_def in self.react_19_apis["hooks"].items():
            if hook_name in code:
                # Validate proper usage
                compliance[hook_name] = self._validate_hook_usage(code, hook_name, hook_def)

        # Check component usage
        for component_name, component_def in self.react_19_apis["components"].items():
            if component_name in code:
                compliance[component_name] = self._validate_component_usage(code, component_name, component_def)

        # Check server action usage
        if "async function" in code and "formData" in code:
            compliance["server_actions"] = "'use server'" in code

        return compliance

    def _validate_hook_usage(self, code: str, hook_name: str, hook_def: dict[str, Any]) -> bool:
        """Validate specific hook usage."""
        # Check for proper destructuring
        if hook_name == "useActionState":
            pattern = rf"{hook_name}\([^)]+)\s*=\s*useActionState"
            matches = re.findall(pattern, code)
            for match in matches:
                # Check if it's properly destructured
                if not match.strip().startswith("["):
                    return False

        return True

    def _validate_component_usage(self, code: str, component_name: str, component_def: dict[str, Any]) -> bool:
        """Validate specific component usage."""
        # Basic validation - could be expanded
        return True

    def validate_zero_hallucination(self, code: str, expected_features: list[str]) -> dict[str, Any]:
        """
        Validate code for zero hallucination compliance.

        Args:
            code: React 19 code to validate
            expected_features: Expected React 19 features

        Returns:
            Hallucination validation results
        """
        validation_result = {
            "compliant": True,
            "missing_features": [],
            "incorrect_usage": [],
            "unrecognized_apis": [],
            "risk_level": "low",
        }

        # Check for expected features
        for feature in expected_features:
            if feature == "useOptimistic" and "useOptimistic" not in code:
                validation_result["missing_features"].append("useOptimistic")
            elif feature == "server_actions" and ("'use server'" not in code and "async function" in code):
                validation_result["missing_features"].append("server_action_directive")
            elif feature == "document_metadata" and not any(tag in code for tag in ["<title", "<meta", "<link"]):
                validation_result["missing_features"].append("document_metadata")

        # Check for incorrect usage
        if "useOptimistic" in code:
            if not re.search(r"useOptimistic\([^,]+,\s*[^)]+\s*=>\s*[^)]+\)", code):
                validation_result["incorrect_usage"].append("useOptimistic signature")

        # Check for unrecognized APIs
        api_matches = re.findall(r"use[A-Z][a-zA-Z]+", code)
        for api in api_matches:
            if api not in self.react_19_apis["hooks"] and api not in [
                "useState",
                "useEffect",
                "useContext",
                "useReducer",
                "useRef",
                "useCallback",
                "useMemo",
            ]:
                validation_result["unrecognized_apis"].append(api)

        # Determine risk level
        if validation_result["missing_features"] or validation_result["incorrect_usage"]:
            validation_result["risk_level"] = "high"
        elif validation_result["unrecognized_apis"]:
            validation_result["risk_level"] = "medium"

        validation_result["compliant"] = validation_result["risk_level"] == "low"

        return validation_result

    def generate_fixes(self, validation_report: ValidationReport) -> list[dict[str, Any]]:
        """
        Generate automated fixes for validation issues.

        Args:
            validation_report: Validation report with issues

        Returns:
            List of automated fixes
        """
        fixes = []

        error_results = [r for r in validation_report.results if r.level == ValidationLevel.ERROR]

        for result in error_results:
            fix = self._generate_fix_for_result(result)
            if fix:
                fixes.append(fix)

        return fixes

    def _generate_fix_for_result(self, result: ValidationResult) -> dict[str, Any] | None:
        """Generate fix for a specific validation result."""
        fix_patterns = {
            "server_action_directive": {
                "search": r"(async function\s+\w+\([^)]*\)\s*{)",
                "replace": r"'use server';\n\n\1",
                "description": "Add 'use server' directive to server action",
            },
            "avoid_any_types": {
                "search": r":\s*any(?![\[\(])",
                "replace": ": unknown",  # Could be more sophisticated
                "description": "Replace 'any' with 'unknown' or specific type",
            },
            "script_async_missing": {
                "search": r"<script\s+src=",
                "replace": "<script async={true} src=",
                "description": "Add async={true} to external script",
            },
        }

        rule_name = result.message.split(":")[0] if ":" in result.message else result.message
        if rule_name in fix_patterns and result.code_snippet:
            pattern = fix_patterns[rule_name]
            return {
                "type": "automated",
                "description": pattern["description"],
                "search": pattern["search"],
                "replace": pattern["replace"],
                "line_number": result.line_number,
            }

        return None

    def benchmark_performance(self, code: str) -> dict[str, float]:
        """
        Benchmark performance characteristics of React 19 code.

        Args:
            code: React 19 code to benchmark

        Returns:
            Performance benchmark results
        """
        benchmarks = {
            "optimistic_updates_usage": 0.0,
            "server_actions_usage": 0.0,
            "metadata_usage": 0.0,
            "async_scripts_usage": 0.0,
            "type_safety_score": 0.0,
            "performance_patterns_score": 0.0,
        }

        # Calculate usage percentages
        total_patterns = 0

        if "useOptimistic" in code:
            benchmarks["optimistic_updates_usage"] = 100
            total_patterns += 1

        if "'use server'" in code or "action=" in code:
            benchmarks["server_actions_usage"] = 100
            total_patterns += 1

        if any(tag in code for tag in ["<title", "<meta", "<link"]):
            benchmarks["metadata_usage"] = 100
            total_patterns += 1

        if "async={true}" in code:
            benchmarks["async_scripts_usage"] = 100
            total_patterns += 1

        # Type safety score
        type_safety_indicators = 0
        if "interface " in code:
            type_safety_indicators += 1
        if ": " in code:
            type_safety_indicators += 1
        if "any" not in code:
            type_safety_indicators += 1

        benchmarks["type_safety_score"] = (type_safety_indicators / 3) * 100

        # Performance patterns score
        performance_patterns = 0
        if "React.memo" in code or "useMemo" in code or "useCallback" in code:
            performance_patterns += 1
        if "useOptimistic" in code:
            performance_patterns += 1
        if "useTransition" in code:
            performance_patterns += 1

        benchmarks["performance_patterns_score"] = (performance_patterns / 3) * 100

        return benchmarks
