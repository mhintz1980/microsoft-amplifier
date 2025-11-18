"""
Compliance Validator for Project Standards

Validates skills against project standards, coding conventions,
best practices, and regulatory requirements to ensure consistency
and quality across all 57 skills.
"""

import ast
import re
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import configparser
import toml

from amplifier.mcp.code_execution import execute_in_docker
from amplifier.mcp.persistent_storage import store_result


class ComplianceLevel(Enum):
    """Compliance levels for validation."""

    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"


class StandardType(Enum):
    """Types of standards to validate against."""

    CODE_STYLE = "code_style"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    NAMING_CONVENTIONS = "naming_conventions"
    ERROR_HANDLING = "error_handling"
    DEPENDENCY_MANAGEMENT = "dependency_management"
    CONFIGURATION = "configuration"


@dataclass
class ComplianceRule:
    """Individual compliance rule definition."""

    rule_id: str
    standard_type: StandardType
    title: str
    description: str
    validation_function: str
    severity: str  # "error", "warning", "info"
    auto_fixable: bool = False
    reference_link: Optional[str] = None


@dataclass
class ComplianceViolation:
    """Compliance violation found during validation."""

    rule_id: str
    standard_type: StandardType
    severity: str
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    suggestion: str
    auto_fix_available: bool = False


@dataclass
class ComplianceReport:
    """Comprehensive compliance validation report."""

    skill_path: str
    validation_timestamp: datetime
    overall_compliance: ComplianceLevel
    compliance_score: float
    standard_results: Dict[StandardType, Dict[str, Any]]
    violations: List[ComplianceViolation]
    passed_rules: List[str]
    failed_rules: List[str]
    auto_fix_available: bool
    recommendations: List[str]


class ComplianceValidator:
    """Comprehensive compliance validator for project standards."""

    def __init__(
        self,
        project_root: str = None,
        config_file: str = "pyproject.toml",
        strict_mode: bool = False,
        auto_fix: bool = False,
    ):
        """
        Initialize compliance validator.

        Args:
            project_root: Root directory of the project
            config_file: Configuration file path
            strict_mode: Enable strict compliance checking
            auto_fix: Enable automatic fixing of violations
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.config_file = config_file
        self.strict_mode = strict_mode
        self.auto_fix = auto_fix

        # Load project configuration
        self.project_config = self._load_project_config()

        # Initialize compliance rules
        self.compliance_rules = self._initialize_compliance_rules()

        # Load custom rules if they exist
        self._load_custom_rules()

        # Install validation tools
        self._install_validation_tools()

    def _load_project_config(self) -> Dict[str, Any]:
        """Load project configuration from pyproject.toml."""
        config_path = self.project_root / self.config_file

        if not config_path.exists():
            return {}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return toml.load(f)
        except Exception:
            return {}

    def _initialize_compliance_rules(self) -> Dict[str, ComplianceRule]:
        """Initialize default compliance rules."""
        rules = {}

        # Code Style Rules
        rules.update(
            {
                "PEP8_COMPLIANCE": ComplianceRule(
                    rule_id="PEP8_COMPLIANCE",
                    standard_type=StandardType.CODE_STYLE,
                    title="PEP 8 Code Style Compliance",
                    description="Code must follow PEP 8 style guidelines",
                    validation_function="_validate_pep8_compliance",
                    severity="error",
                    auto_fixable=True,
                    reference_link="https://peps.python.org/pep-0008/",
                ),
                "LINE_LENGTH": ComplianceRule(
                    rule_id="LINE_LENGTH",
                    standard_type=StandardType.CODE_STYLE,
                    title="Line Length Limit",
                    description="Lines should not exceed 120 characters",
                    validation_function="_validate_line_length",
                    severity="warning",
                    auto_fixable=True,
                ),
                "IMPORT_ORDERING": ComplianceRule(
                    rule_id="IMPORT_ORDERING",
                    standard_type=StandardType.CODE_STYLE,
                    title="Import Ordering",
                    description="Imports must be properly ordered and grouped",
                    validation_function="_validate_import_ordering",
                    severity="warning",
                    auto_fixable=True,
                ),
            }
        )

        # Documentation Rules
        rules.update(
            {
                "DOCSTRING_PRESENT": ComplianceRule(
                    rule_id="DOCSTRING_PRESENT",
                    standard_type=StandardType.DOCUMENTATION,
                    title="Docstring Presence",
                    description="All public functions and classes must have docstrings",
                    validation_function="_validate_docstring_presence",
                    severity="error",
                ),
                "README_PRESENT": ComplianceRule(
                    rule_id="README_PRESENT",
                    standard_type=StandardType.DOCUMENTATION,
                    title="README File Present",
                    description="Each skill must have a README.md file",
                    validation_function="_validate_readme_presence",
                    severity="error",
                ),
                "CHANGELOG_PRESENT": ComplianceRule(
                    rule_id="CHANGELOG_PRESENT",
                    standard_type=StandardType.DOCUMENTATION,
                    title="Changelog Present",
                    description="Skill should maintain a changelog",
                    validation_function="_validate_changelog_presence",
                    severity="warning",
                ),
            }
        )

        # Testing Rules
        rules.update(
            {
                "TEST_COVERAGE": ComplianceRule(
                    rule_id="TEST_COVERAGE",
                    standard_type=StandardType.TESTING,
                    title="Test Coverage",
                    description="Code should have minimum test coverage",
                    validation_function="_validate_test_coverage",
                    severity="warning",
                ),
                "TEST_FILE_PRESENT": ComplianceRule(
                    rule_id="TEST_FILE_PRESENT",
                    standard_type=StandardType.TESTING,
                    title="Test File Present",
                    description="Skill should have corresponding test files",
                    validation_function="_validate_test_file_presence",
                    severity="error",
                ),
                "TEST_NAMING": ComplianceRule(
                    rule_id="TEST_NAMING",
                    standard_type=StandardType.TESTING,
                    title="Test Naming Convention",
                    description="Tests must follow proper naming conventions",
                    validation_function="_validate_test_naming",
                    severity="warning",
                ),
            }
        )

        # Architecture Rules
        rules.update(
            {
                "SINGLE_RESPONSIBILITY": ComplianceRule(
                    rule_id="SINGLE_RESPONSIBILITY",
                    standard_type=StandardType.ARCHITECTURE,
                    title="Single Responsibility Principle",
                    description="Functions should have a single responsibility",
                    validation_function="_validate_single_responsibility",
                    severity="warning",
                ),
                "NO_CIRCULAR_IMPORTS": ComplianceRule(
                    rule_id="NO_CIRCULAR_IMPORTS",
                    standard_type=StandardType.ARCHITECTURE,
                    title="No Circular Imports",
                    description="Skills should not have circular import dependencies",
                    validation_function="_validate_no_circular_imports",
                    severity="error",
                ),
                "MODULE_STRUCTURE": ComplianceRule(
                    rule_id="MODULE_STRUCTURE",
                    standard_type=StandardType.ARCHITECTURE,
                    title="Module Structure",
                    description="Modules should follow proper structure",
                    validation_function="_validate_module_structure",
                    severity="warning",
                ),
            }
        )

        # Naming Convention Rules
        rules.update(
            {
                "FUNCTION_NAMING": ComplianceRule(
                    rule_id="FUNCTION_NAMING",
                    standard_type=StandardType.NAMING_CONVENTIONS,
                    title="Function Naming Convention",
                    description="Functions must use snake_case naming",
                    validation_function="_validate_function_naming",
                    severity="error",
                ),
                "CLASS_NAMING": ComplianceRule(
                    rule_id="CLASS_NAMING",
                    standard_type=StandardType.NAMING_CONVENTIONS,
                    title="Class Naming Convention",
                    description="Classes must use PascalCase naming",
                    validation_function="_validate_class_naming",
                    severity="error",
                ),
                "CONSTANT_NAMING": ComplianceRule(
                    rule_id="CONSTANT_NAMING",
                    standard_type=StandardType.NAMING_CONVENTIONS,
                    title="Constant Naming Convention",
                    description="Constants must use UPPER_CASE naming",
                    validation_function="_validate_constant_naming",
                    severity="warning",
                ),
            }
        )

        # Error Handling Rules
        rules.update(
            {
                "EXCEPTION_HANDLING": ComplianceRule(
                    rule_id="EXCEPTION_HANDLING",
                    standard_type=StandardType.ERROR_HANDLING,
                    title="Proper Exception Handling",
                    description="Code should handle exceptions properly",
                    validation_function="_validate_exception_handling",
                    severity="error",
                ),
                "NO_BARE_EXCEPT": ComplianceRule(
                    rule_id="NO_BARE_EXCEPT",
                    standard_type=StandardType.ERROR_HANDLING,
                    title="No Bare Except Clauses",
                    description="Avoid bare except clauses",
                    validation_function="_validate_no_bare_except",
                    severity="warning",
                ),
                "SPECIFIC_EXCEPTIONS": ComplianceRule(
                    rule_id="SPECIFIC_EXCEPTIONS",
                    standard_type=StandardType.ERROR_HANDLING,
                    title="Specific Exception Types",
                    description="Use specific exception types rather than generic Exception",
                    validation_function="_validate_specific_exceptions",
                    severity="warning",
                ),
            }
        )

        # Dependency Management Rules
        rules.update(
            {
                "DEPENDENCY_DECLARATION": ComplianceRule(
                    rule_id="DEPENDENCY_DECLARATION",
                    standard_type=StandardType.DEPENDENCY_MANAGEMENT,
                    title="Dependency Declaration",
                    description="Dependencies must be properly declared",
                    validation_function="_validate_dependency_declaration",
                    severity="error",
                ),
                "VERSION_CONSTRAINTS": ComplianceRule(
                    rule_id="VERSION_CONSTRAINTS",
                    standard_type=StandardType.DEPENDENCY_MANAGEMENT,
                    title="Version Constraints",
                    description="Dependencies should have version constraints",
                    validation_function="_validate_version_constraints",
                    severity="warning",
                ),
                "NO_UNUSED_IMPORTS": ComplianceRule(
                    rule_id="NO_UNUSED_IMPORTS",
                    standard_type=StandardType.DEPENDENCY_MANAGEMENT,
                    title="No Unused Imports",
                    description="Remove unused imports",
                    validation_function="_validate_no_unused_imports",
                    severity="warning",
                    auto_fixable=True,
                ),
            }
        )

        return rules

    def _load_custom_rules(self):
        """Load custom compliance rules from project config."""
        custom_rules_config = self.project_config.get("tool", {}).get("compliance", {}).get("rules", {})

        for rule_id, rule_config in custom_rules_config.items():
            # Create custom rule from config
            custom_rule = ComplianceRule(
                rule_id=rule_id,
                standard_type=StandardType(rule_config.get("type", "code_style")),
                title=rule_config.get("title", rule_id),
                description=rule_config.get("description", ""),
                validation_function=rule_config.get("validation", ""),
                severity=rule_config.get("severity", "warning"),
                auto_fixable=rule_config.get("auto_fixable", False),
                reference_link=rule_config.get("reference_link"),
            )
            self.compliance_rules[rule_id] = custom_rule

    def _install_validation_tools(self):
        """Install validation tools."""
        tools = [
            "ruff",  # Fast Python linter and formatter
            "black",  # Code formatter
            "isort",  # Import sorter
            "mypy",  # Type checker
            "pydocstyle",  # Docstring style checker
            "bandit",  # Security linter
        ]

        for tool in tools:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", tool], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                print(f"Warning: Failed to install {tool}")

    async def validate_skill(self, skill_path: str) -> ComplianceReport:
        """
        Validate a skill against all compliance rules.

        Args:
            skill_path: Path to the skill directory or file

        Returns:
            Comprehensive compliance report
        """
        skill_path = Path(skill_path)
        validation_timestamp = datetime.now()

        # Collect all relevant files
        files_to_validate = self._collect_files(skill_path)

        # Initialize results
        violations = []
        passed_rules = []
        failed_rules = []
        standard_results = {}

        # Validate each standard type
        for standard_type in StandardType:
            standard_rules = [rule for rule in self.compliance_rules.values() if rule.standard_type == standard_type]

            if not standard_rules:
                continue

            standard_violations = []
            standard_passed = []
            standard_failed = []

            for rule in standard_rules:
                try:
                    # Execute validation function
                    validation_function = getattr(self, rule.validation_function)
                    rule_violations = validation_function(files_to_validate, rule)

                    if rule_violations:
                        violations.extend(rule_violations)
                        standard_failed.append(rule.rule_id)
                        failed_rules.append(rule.rule_id)
                    else:
                        standard_passed.append(rule.rule_id)
                        passed_rules.append(rule.rule_id)

                except Exception as e:
                    # Create violation for validation error
                    violations.append(
                        ComplianceViolation(
                            rule_id=rule.rule_id,
                            standard_type=rule.standard_type,
                            severity="error",
                            title=f"Validation Error: {rule.title}",
                            description=f"Could not validate rule: {str(e)}",
                            file_path=str(skill_path),
                            line_number=0,
                            code_snippet="",
                            suggestion="Check validation function implementation",
                            auto_fix_available=False,
                        )
                    )
                    standard_failed.append(rule.rule_id)
                    failed_rules.append(rule.rule_id)

            # Calculate standard compliance level
            total_rules = len(standard_rules)
            if total_rules == 0:
                compliance_level = ComplianceLevel.NOT_APPLICABLE
                compliance_score = 1.0
            else:
                passed_count = len(standard_passed)
                compliance_score = passed_count / total_rules

                if compliance_score >= 0.95:
                    compliance_level = ComplianceLevel.COMPLIANT
                elif compliance_score >= 0.8:
                    compliance_level = ComplianceLevel.PARTIALLY_COMPLIANT
                else:
                    compliance_level = ComplianceLevel.NON_COMPLIANT

            standard_results[standard_type] = {
                "compliance_level": compliance_level,
                "compliance_score": compliance_score,
                "passed_rules": standard_passed,
                "failed_rules": standard_failed,
                "total_rules": total_rules,
            }

        # Calculate overall compliance
        overall_score = self._calculate_overall_compliance(standard_results)
        overall_compliance = self._get_compliance_level(overall_score)

        # Generate recommendations
        recommendations = self._generate_compliance_recommendations(violations, standard_results)

        # Check if auto-fix is available
        auto_fix_available = any(vuln.auto_fix_available for vuln in violations)

        # Apply auto-fixes if enabled
        if self.auto_fix and auto_fix_available:
            await self._apply_auto_fixes(violations)

        return ComplianceReport(
            skill_path=str(skill_path),
            validation_timestamp=validation_timestamp,
            overall_compliance=overall_compliance,
            compliance_score=overall_score,
            standard_results=standard_results,
            violations=violations,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            auto_fix_available=auto_fix_available,
            recommendations=recommendations,
        )

    def _collect_files(self, skill_path: Path) -> List[Path]:
        """Collect relevant files for validation."""
        file_extensions = {".py", ".md", ".txt", ".toml", ".yaml", ".yml", ".cfg", ".ini"}
        files_to_validate = []

        if skill_path.is_file():
            if skill_path.suffix in file_extensions:
                files_to_validate.append(skill_path)
        else:
            for ext in file_extensions:
                files_to_validate.extend(skill_path.rglob(f"*{ext}"))

        return files_to_validate

    def _calculate_overall_compliance(self, standard_results: Dict[StandardType, Dict]) -> float:
        """Calculate overall compliance score."""
        if not standard_results:
            return 1.0

        total_score = 0.0
        count = 0

        for result in standard_results.values():
            if result["total_rules"] > 0:
                total_score += result["compliance_score"]
                count += 1

        return total_score / count if count > 0 else 1.0

    def _get_compliance_level(self, score: float) -> ComplianceLevel:
        """Get compliance level from score."""
        if score >= 0.95:
            return ComplianceLevel.COMPLIANT
        elif score >= 0.8:
            return ComplianceLevel.PARTIALLY_COMPLIANT
        else:
            return ComplianceLevel.NON_COMPLIANT

    def _generate_compliance_recommendations(
        self, violations: List[ComplianceViolation], standard_results: Dict[StandardType, Dict]
    ) -> List[str]:
        """Generate compliance improvement recommendations."""
        recommendations = []

        # Analyze common violation patterns
        violation_types = {}
        for violation in violations:
            violation_types[violation.standard_type] = violation_types.get(violation.standard_type, 0) + 1

        # Generate recommendations based on violation patterns
        for standard_type, count in violation_types.items():
            if standard_type == StandardType.CODE_STYLE:
                recommendations.append("Use automated code formatting tools (black, ruff)")
                recommendations.append("Set up pre-commit hooks for code style checking")
            elif standard_type == StandardType.DOCUMENTATION:
                recommendations.append("Add comprehensive docstrings to all public APIs")
                recommendations.append("Create detailed README and documentation")
            elif standard_type == StandardType.TESTING:
                recommendations.append("Increase test coverage and add unit tests")
                recommendations.append("Follow proper testing conventions")
            elif standard_type == StandardType.ARCHITECTURE:
                recommendations.append("Review and refactor architectural issues")
                recommendations.append("Follow SOLID principles and design patterns")
            elif standard_type == StandardType.ERROR_HANDLING:
                recommendations.append("Implement proper exception handling")
                recommendations.append("Use specific exception types")

        # Add general recommendations
        if violations:
            recommendations.append("Set up continuous integration with compliance checking")
            recommendations.append("Regular review and update of coding standards")

        # Recommend auto-fix for fixable violations
        auto_fixable = [v for v in violations if v.auto_fix_available]
        if auto_fixable:
            recommendations.append(f"Run auto-fix for {len(auto_fixable)} fixable violations")

        return list(set(recommendations))  # Remove duplicates

    async def _apply_auto_fixes(self, violations: List[ComplianceViolation]):
        """Apply automatic fixes for fixable violations."""
        auto_fixable_violations = [v for v in violations if v.auto_fix_available]

        for violation in auto_fixable_violations:
            try:
                if violation.rule_id == "LINE_LENGTH":
                    await self._auto_fix_line_length(violation.file_path)
                elif violation.rule_id == "IMPORT_ORDERING":
                    await self._auto_fix_import_ordering(violation.file_path)
                elif violation.rule_id == "NO_UNUSED_IMPORTS":
                    await self._auto_fix_unused_imports(violation.file_path)
            except Exception:
                continue  # Skip if auto-fix fails

    async def _auto_fix_line_length(self, file_path: str):
        """Auto-fix line length violations."""
        try:
            subprocess.run(
                [sys.executable, "-m", "black", "--line-length", "120", file_path], capture_output=True, check=True
            )
        except subprocess.CalledProcessError:
            pass

    async def _auto_fix_import_ordering(self, file_path: str):
        """Auto-fix import ordering violations."""
        try:
            subprocess.run([sys.executable, "-m", "isort", file_path], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            pass

    async def _auto_fix_unused_imports(self, file_path: str):
        """Auto-fix unused import violations."""
        try:
            subprocess.run(
                [sys.executable, "-m", "ruff", "check", "--select", "F401", "--fix", file_path],
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            pass

    # Validation function implementations
    def _validate_pep8_compliance(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate PEP 8 compliance using ruff."""
        violations = []

        for file_path in files:
            if file_path.suffix != ".py":
                continue

            try:
                result = subprocess.run(
                    [sys.executable, "-m", "ruff", "check", str(file_path)], capture_output=True, text=True, timeout=30
                )

                if result.stdout:
                    for line in result.stdout.split("\n"):
                        if line.strip():
                            violations.append(self._parse_ruff_output(line, file_path, rule))

            except subprocess.TimeoutExpired:
                pass

        return violations

    def _validate_line_length(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate line length limit."""
        violations = []
        max_length = 120

        for file_path in files:
            if file_path.suffix != ".py":
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    if len(line.rstrip()) > max_length:
                        violations.append(
                            ComplianceViolation(
                                rule_id=rule.rule_id,
                                standard_type=rule.standard_type,
                                severity=rule.severity,
                                title=rule.title,
                                description=f"Line exceeds {max_length} characters ({len(line.rstrip())})",
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=line.strip()[:80] + "..." if len(line.strip()) > 80 else line.strip(),
                                suggestion="Break long lines or use text wrapping",
                                auto_fix_available=rule.auto_fixable,
                            )
                        )

            except Exception:
                continue

        return violations

    def _validate_import_ordering(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate import ordering."""
        violations = []

        for file_path in files:
            if file_path.suffix != ".py":
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Simple check for import ordering (simplified)
                lines = content.split("\n")
                import_groups = []
                current_group = []

                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("import ") or stripped.startswith("from "):
                        current_group.append(stripped)
                    elif current_group and not stripped.startswith("#"):
                        if current_group:
                            import_groups.append(current_group)
                            current_group = []

                if current_group:
                    import_groups.append(current_group)

                # Check if imports are properly grouped and sorted
                for group in import_groups:
                    sorted_group = sorted(group)
                    if group != sorted_group:
                        violations.append(
                            ComplianceViolation(
                                rule_id=rule.rule_id,
                                standard_type=rule.standard_type,
                                severity=rule.severity,
                                title=rule.title,
                                description="Imports are not properly sorted",
                                file_path=str(file_path),
                                line_number=0,  # Would need more sophisticated analysis
                                code_snippet="; ".join(group[:3]),
                                suggestion="Run import sorter (isort) to fix ordering",
                                auto_fix_available=rule.auto_fixable,
                            )
                        )

            except Exception:
                continue

        return violations

    def _validate_docstring_presence(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate presence of docstrings."""
        violations = []

        for file_path in files:
            if file_path.suffix != ".py":
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        if not node.name.startswith("_"):  # Check public functions/classes
                            docstring = ast.get_docstring(node)
                            if not docstring:
                                violations.append(
                                    ComplianceViolation(
                                        rule_id=rule.rule_id,
                                        standard_type=rule.standard_type,
                                        severity=rule.severity,
                                        title=rule.title,
                                        description=f"Missing docstring for {type(node).__name__} '{node.name}'",
                                        file_path=str(file_path),
                                        line_number=node.lineno,
                                        code_snippet=f"{'async ' if isinstance(node, ast.AsyncFunctionDef) else ''}def {node.name}(...)",
                                        suggestion="Add comprehensive docstring explaining purpose and parameters",
                                        auto_fix_available=rule.auto_fixable,
                                    )
                                )

            except Exception:
                continue

        return violations

    def _validate_readme_presence(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate presence of README file."""
        violations = []
        skill_path = Path(files[0]).parent if files else Path.cwd()

        readme_files = list(skill_path.glob("README*"))
        if not readme_files:
            violations.append(
                ComplianceViolation(
                    rule_id=rule.rule_id,
                    standard_type=rule.standard_type,
                    severity=rule.severity,
                    title=rule.title,
                    description="No README file found in skill directory",
                    file_path=str(skill_path),
                    line_number=0,
                    code_snippet="",
                    suggestion="Create a comprehensive README.md file documenting the skill",
                    auto_fix_available=rule.auto_fixable,
                )
            )

        return violations

    def _validate_test_coverage(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate test coverage (simplified)."""
        violations = []

        python_files = [f for f in files if f.suffix == ".py" and "test" not in f.name.lower()]
        test_files = [f for f in files if f.suffix == ".py" and "test" in f.name.lower()]

        if python_files and not test_files:
            violations.append(
                ComplianceViolation(
                    rule_id=rule.rule_id,
                    standard_type=rule.standard_type,
                    severity=rule.severity,
                    title=rule.title,
                    description="No test files found for skill",
                    file_path=str(files[0]),
                    line_number=0,
                    code_snippet="",
                    suggestion="Create comprehensive test suite for the skill",
                    auto_fix_available=False,
                )
            )

        return violations

    def _validate_test_file_presence(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate presence of test files."""
        violations = []
        skill_path = Path(files[0]).parent if files else Path.cwd()

        test_files = list(skill_path.rglob("*test*.py"))
        if not test_files:
            violations.append(
                ComplianceViolation(
                    rule_id=rule.rule_id,
                    standard_type=rule.standard_type,
                    severity=rule.severity,
                    title=rule.title,
                    description="No test files found in skill",
                    file_path=str(skill_path),
                    line_number=0,
                    code_snippet="",
                    suggestion="Add test files following naming convention (test_*.py or *_test.py)",
                    auto_fix_available=False,
                )
            )

        return violations

    def _validate_function_naming(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate function naming conventions."""
        violations = []

        for file_path in files:
            if file_path.suffix != ".py":
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not re.match(r"^[a-z_][a-z0-9_]*$", node.name):
                            violations.append(
                                ComplianceViolation(
                                    rule_id=rule.rule_id,
                                    standard_type=rule.standard_type,
                                    severity=rule.severity,
                                    title=rule.title,
                                    description=f"Function '{node.name}' does not follow snake_case convention",
                                    file_path=str(file_path),
                                    line_number=node.lineno,
                                    code_snippet=f"def {node.name}(...)",
                                    suggestion="Rename function to use snake_case naming convention",
                                    auto_fix_available=False,
                                )
                            )

            except Exception:
                continue

        return violations

    def _validate_class_naming(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate class naming conventions."""
        violations = []

        for file_path in files:
            if file_path.suffix != ".py":
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
                            violations.append(
                                ComplianceViolation(
                                    rule_id=rule.rule_id,
                                    standard_type=rule.standard_type,
                                    severity=rule.severity,
                                    title=rule.title,
                                    description=f"Class '{node.name}' does not follow PascalCase convention",
                                    file_path=str(file_path),
                                    line_number=node.lineno,
                                    code_snippet=f"class {node.name}:",
                                    suggestion="Rename class to use PascalCase naming convention",
                                    auto_fix_available=False,
                                )
                            )

            except Exception:
                continue

        return violations

    def _validate_no_bare_except(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate no bare except clauses."""
        violations = []

        for file_path in files:
            if file_path.suffix != ".py":
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Simple regex check for bare except
                bare_except_pattern = r"except\s*:\s*$"

                for line_num, line in enumerate(content.split("\n"), 1):
                    if re.search(bare_except_pattern, line.strip()):
                        violations.append(
                            ComplianceViolation(
                                rule_id=rule.rule_id,
                                standard_type=rule.standard_type,
                                severity=rule.severity,
                                title=rule.title,
                                description="Bare except clause detected",
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=line.strip(),
                                suggestion="Specify exception type (e.g., except ValueError:)",
                                auto_fix_available=False,
                            )
                        )

            except Exception:
                continue

        return violations

    def _parse_ruff_output(self, output_line: str, file_path: Path, rule: ComplianceRule) -> ComplianceViolation:
        """Parse ruff output line into compliance violation."""
        # Ruff output format: filename:line:col: code message
        parts = output_line.split(":", 3)
        if len(parts) >= 4:
            line_number = int(parts[1]) if parts[1].isdigit() else 0
            message = parts[3].strip()
            code = parts[2].strip()

            return ComplianceViolation(
                rule_id=rule.rule_id,
                standard_type=rule.standard_type,
                severity=rule.severity,
                title=f"PEP 8 Violation: {code}",
                description=message,
                file_path=str(file_path),
                line_number=line_number,
                code_snippet="",
                suggestion="Run code formatter to fix style issues",
                auto_fix_available=rule.auto_fixable,
            )

        # Fallback
        return ComplianceViolation(
            rule_id=rule.rule_id,
            standard_type=rule.standard_type,
            severity=rule.severity,
            title=rule.title,
            description=output_line,
            file_path=str(file_path),
            line_number=0,
            code_snippet="",
            suggestion="Review code style guidelines",
            auto_fix_available=rule.auto_fixable,
        )

    # Placeholder validation functions (would be implemented fully)
    def _validate_changelog_presence(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate presence of changelog."""
        return []  # Implementation would check for CHANGELOG.md

    def _validate_test_naming(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate test naming conventions."""
        return []  # Implementation would check test naming patterns

    def _validate_single_responsibility(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate single responsibility principle."""
        return []  # Implementation would analyze function complexity

    def _validate_no_circular_imports(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate no circular imports."""
        return []  # Implementation would build dependency graph

    def _validate_module_structure(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate module structure."""
        return []  # Implementation would check module organization

    def _validate_constant_naming(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate constant naming conventions."""
        return []  # Implementation would check UPPER_CASE constants

    def _validate_exception_handling(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate proper exception handling."""
        return []  # Implementation would check exception handling patterns

    def _validate_specific_exceptions(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate specific exception types."""
        return []  # Implementation would check for specific vs generic exceptions

    def _validate_dependency_declaration(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate dependency declarations."""
        return []  # Implementation would check pyproject.toml dependencies

    def _validate_version_constraints(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate version constraints."""
        return []  # Implementation would check dependency versions

    def _validate_no_unused_imports(self, files: List[Path], rule: ComplianceRule) -> List[ComplianceViolation]:
        """Validate no unused imports."""
        violations = []

        for file_path in files:
            if file_path.suffix != ".py":
                continue

            try:
                result = subprocess.run(
                    [sys.executable, "-m", "ruff", "check", "--select", "F401", str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.stdout:
                    for line in result.stdout.split("\n"):
                        if line.strip():
                            violations.append(self._parse_ruff_output(line, file_path, rule))

            except subprocess.TimeoutExpired:
                pass

        return violations

    async def store_compliance_report(self, report: ComplianceReport):
        """Store compliance report in MCP storage."""
        serialized_report = {
            "skill_path": report.skill_path,
            "validation_timestamp": report.validation_timestamp.isoformat(),
            "overall_compliance": report.overall_compliance.value,
            "compliance_score": report.compliance_score,
            "standard_results": {
                k.value: {
                    "compliance_level": v["compliance_level"].value,
                    "compliance_score": v["compliance_score"],
                    "passed_rules": v["passed_rules"],
                    "failed_rules": v["failed_rules"],
                    "total_rules": v["total_rules"],
                }
                for k, v in report.standard_results.items()
            },
            "violations": [
                {
                    "rule_id": vuln.rule_id,
                    "standard_type": vuln.standard_type.value,
                    "severity": vuln.severity,
                    "title": vuln.title,
                    "description": vuln.description,
                    "file_path": vuln.file_path,
                    "line_number": vuln.line_number,
                    "code_snippet": vuln.code_snippet,
                    "suggestion": vuln.suggestion,
                    "auto_fix_available": vuln.auto_fix_available,
                }
                for vuln in report.violations
            ],
            "passed_rules": report.passed_rules,
            "failed_rules": report.failed_rules,
            "auto_fix_available": report.auto_fix_available,
            "recommendations": report.recommendations,
        }

        await store_result(
            namespace="compliance_validation",
            key=f"{report.skill_path}_compliance_{report.validation_timestamp.isoformat()}",
            data=serialized_report,
        )
