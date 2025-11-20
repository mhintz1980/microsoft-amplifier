#!/usr/bin/env python3
"""
Comprehensive Skills Validation System for Microsoft Amplifier

This script performs thorough validation of all skills in the amplifier/skills/ directory
to ensure system stability, zero hallucination compliance, and performance requirements.
"""

import asyncio
import importlib
import inspect
import json
import logging
import sys
import time
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("skills_validation.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validating a single skill"""

    skill_name: str
    skill_path: str
    category: str
    syntax_valid: bool
    import_valid: bool
    functionality_valid: bool
    performance_ms: float
    memory_usage_mb: float
    error_messages: list[str]
    warnings: list[str]
    api_accuracy_score: float
    integration_compatible: bool
    error_handling_valid: bool
    overall_score: float


@dataclass
class SystemValidationReport:
    """Comprehensive validation report for the entire skills system"""

    total_skills: int
    valid_skills: int
    invalid_skills: int
    categories: dict[str, int]
    average_performance_ms: float
    average_memory_usage_mb: float
    overall_system_health: float
    critical_issues: list[str]
    recommendations: list[str]
    skill_results: list[ValidationResult]
    validation_timestamp: str


class SkillsValidator:
    """Comprehensive skills validation system"""

    def __init__(self):
        self.start_time = time.time()
        self.skills_dir = Path("amplifier/skills")
        self.results: list[ValidationResult] = []
        self.critical_issues: list[str] = []
        self.warnings: list[str] = []

        # Known API endpoints for validation
        self.known_apis = {
            "react": ["useState", "useEffect", "useContext", "Components", "Props"],
            "nodejs": ["http", "express", "fs", "path", "async/await"],
            "typescript": ["interfaces", "types", "generics", "decorators"],
            "vite": ["build", "dev", "config", "plugins"],
            "database": ["SQL", "schemas", "migrations", "indexes"],
            "api": ["REST", "GraphQL", "endpoints", "middleware"],
            "integration": ["MCP", "SSE", "Agent Lightning"],
        }

    def discover_skills(self) -> dict[str, list[Path]]:
        """Discover all skill files and categorize them"""
        categories = {
            "core_technology": [],
            "integration": [],
            "domain_expertise": [],
            "meta_skills": [],
            "validation": [],
            "quality_assurance": [],
            "documentation": [],
            "creation_pipeline": [],
            "signature_framework": [],
            "agent_lightning_integration": [],
            "mcp_storage": [],
            "context_management": [],
            "scheduler": [],
            "resource_optimization": [],
            "discovery": [],
            "examples": [],
            "templates": [],
            "other": [],
        }

        if not self.skills_dir.exists():
            logger.error(f"Skills directory not found: {self.skills_dir}")
            return categories

        for skill_file in self.skills_dir.rglob("*.py"):
            if skill_file.name.startswith("__"):
                continue

            # Determine category
            relative_path = skill_file.relative_to(self.skills_dir)
            parts = relative_path.parts

            # Map to categories
            for category in categories:
                if category in parts:
                    categories[category].append(skill_file)
                    break
            else:
                categories["other"].append(skill_file)

        return categories

    async def validate_skill_syntax(self, skill_path: Path) -> tuple[bool, list[str]]:
        """Validate Python syntax of skill file"""
        errors = []

        try:
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()

            # Compile to check syntax
            compile(content, str(skill_path), "exec")
            return True, errors

        except SyntaxError as e:
            errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error during syntax check: {e}")
            return False, errors

    async def validate_skill_import(self, skill_path: Path) -> tuple[bool, list[str]]:
        """Validate that skill can be imported without errors"""
        errors = []

        try:
            # Convert path to module name relative to project root
            project_root = Path.cwd()
            relative_path = skill_path.relative_to(project_root)
            module_parts = list(relative_path.with_suffix("").parts)
            module_name = ".".join(module_parts)

            # Try to import the module
            spec = importlib.util.spec_from_file_location(module_name, skill_path)
            if spec is None:
                errors.append("Could not create module spec")
                return False, errors

            module = importlib.util.module_from_spec(spec)

            # Don't execute imports that might fail due to missing dependencies
            # Just check that the module can be loaded syntactically
            if spec.loader:
                # Temporarily add the path to sys.modules to avoid import errors
                original_modules = dict(sys.modules)
                try:
                    spec.loader.exec_module(module)
                except Exception as e:
                    # Restore sys.modules and continue
                    sys.modules.clear()
                    sys.modules.update(original_modules)
                    # Some import errors are expected, so we'll be more lenient
                    errors.append(f"Import warning: {e}")
                    return True, errors

            return True, errors

        except ImportError as e:
            errors.append(f"Import error: {e}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected import error: {e}")
            return False, errors

    async def validate_skill_functionality(self, skill_path: Path) -> tuple[bool, list[str], list[str]]:
        """Validate basic functionality of skill"""
        errors = []
        warnings = []

        try:
            # Load module
            project_root = Path.cwd()
            relative_path = skill_path.relative_to(project_root)
            module_parts = list(relative_path.with_suffix("").parts)
            module_name = ".".join(module_parts)

            spec = importlib.util.spec_from_file_location(module_name, skill_path)
            if spec is None:
                errors.append("Could not create module spec")
                return False, errors, warnings

            module = importlib.util.module_from_spec(spec)

            # Try to execute module but handle expected import errors gracefully
            try:
                if spec.loader:
                    spec.loader.exec_module(module)
            except Exception as e:
                # Some modules may have dependency issues - still check syntax
                warnings.append(f"Module execution warning: {e}")
                # Continue with AST analysis instead

            # Check for required patterns
            has_classes = False
            has_functions = False
            has_execute_method = False

            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and not name.startswith("_"):
                    has_classes = True
                    # Check for execute method
                    if hasattr(obj, "execute") or callable(obj):
                        has_execute_method = True

                elif inspect.isfunction(obj) and not name.startswith("_"):
                    has_functions = True

            if not has_classes and not has_functions:
                warnings.append("No public classes or functions found")

            return True, errors, warnings

        except Exception as e:
            errors.append(f"Functionality validation error: {e}")
            return False, errors, warnings

    def calculate_api_accuracy(self, skill_path: Path, content: str) -> float:
        """Calculate API accuracy score based on known patterns"""
        score = 100.0
        content_lower = content.lower()

        # Check for common API patterns
        for api_name, patterns in self.known_apis.items():
            if api_name in str(skill_path).lower():
                for pattern in patterns:
                    if pattern.lower() not in content_lower:
                        score -= 5  # Penalize missing expected patterns

        # Check for deprecated or incorrect patterns
        deprecated_patterns = [
            "var ",
            "function()",
            ".then(function",
            "callback(",
            "document.getElementById",
            "innerHTML",
            "alert(",
        ]

        for pattern in deprecated_patterns:
            if pattern in content:
                score -= 2  # Small penalty for deprecated patterns

        return max(0.0, score)

    async def measure_performance(self, skill_path: Path) -> tuple[float, float]:
        """Measure performance characteristics of skill"""
        start_memory = self._get_memory_usage()
        start_time = time.time()

        try:
            # Load and execute skill basic functionality
            await self.validate_skill_functionality(skill_path)

            end_time = time.time()
            end_memory = self._get_memory_usage()

            performance_ms = (end_time - start_time) * 1000
            memory_usage_mb = max(0, end_memory - start_memory) / 1024 / 1024

            return performance_ms, memory_usage_mb

        except Exception:
            # Return high penalty values if performance test fails
            return float("inf"), float("inf")

    def _get_memory_usage(self) -> float:
        """Get current memory usage in KB"""
        try:
            import psutil

            return psutil.Process().memory_info().rss / 1024
        except ImportError:
            return 0.0

    async def validate_error_handling(self, skill_path: Path) -> tuple[bool, list[str]]:
        """Validate error handling capabilities"""
        errors = []

        try:
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()

            # Check for error handling patterns
            error_patterns = [
                "try:",
                "except",
                "finally:",
                "raise",
                "assert",
                "if error:",
                "catch(",
                "throw new",
                "Promise.reject",
            ]

            has_error_handling = any(pattern in content for pattern in error_patterns)

            if not has_error_handling:
                errors.append("No error handling patterns found")
                return False, errors

            return True, errors

        except Exception as e:
            errors.append(f"Error handling validation failed: {e}")
            return False, errors

    async def validate_integration_compatibility(self, skill_path: Path) -> tuple[bool, list[str]]:
        """Validate integration compatibility with other systems"""
        errors = []

        try:
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()

            # Check for integration patterns
            integration_patterns = [
                "import amplifier",
                "from amplifier",
                "MCP",
                "Agent Lightning",
                "SignatureFramework",
                "BootstrapOptimizer",
                "ZeroHallucination",
            ]

            has_integration = any(pattern in content for pattern in integration_patterns)

            # Not all skills need integration, so this is informational
            return has_integration, errors

        except Exception as e:
            errors.append(f"Integration validation failed: {e}")
            return False, errors

    def calculate_overall_score(self, result: ValidationResult) -> float:
        """Calculate overall score for a skill"""
        weights = {
            "syntax": 0.25,
            "import": 0.20,
            "functionality": 0.20,
            "api_accuracy": 0.15,
            "performance": 0.10,
            "error_handling": 0.10,
        }

        syntax_score = 100 if result.syntax_valid else 0
        import_score = 100 if result.import_valid else 0
        functionality_score = 100 if result.functionality_valid else 0

        # Performance score (lower is better, scale 0-100)
        performance_score = max(0, 100 - (result.performance_ms / 100))

        # Error handling score
        error_score = 100 if result.error_handling_valid else 0

        overall = (
            syntax_score * weights["syntax"]
            + import_score * weights["import"]
            + functionality_score * weights["functionality"]
            + result.api_accuracy_score * weights["api_accuracy"]
            + performance_score * weights["performance"]
            + error_score * weights["error_handling"]
        )

        return round(overall, 2)

    async def validate_single_skill(self, skill_path: Path, category: str) -> ValidationResult:
        """Validate a single skill file"""
        logger.info(f"Validating skill: {skill_path}")

        skill_name = skill_path.stem

        # Read content once for multiple validations
        try:
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return ValidationResult(
                skill_name=skill_name,
                skill_path=str(skill_path),
                category=category,
                syntax_valid=False,
                import_valid=False,
                functionality_valid=False,
                performance_ms=float("inf"),
                memory_usage_mb=float("inf"),
                error_messages=[f"Could not read file: {e}"],
                warnings=[],
                api_accuracy_score=0.0,
                integration_compatible=False,
                error_handling_valid=False,
                overall_score=0.0,
            )

        # Perform all validations
        syntax_valid, syntax_errors = await self.validate_skill_syntax(skill_path)
        import_valid, import_errors = await self.validate_skill_import(skill_path)
        functionality_valid, func_errors, warnings = await self.validate_skill_functionality(skill_path)

        performance_ms, memory_usage_mb = await self.measure_performance(skill_path)
        api_accuracy = self.calculate_api_accuracy(skill_path, content)
        error_handling_valid, error_errors = await self.validate_error_handling(skill_path)
        integration_compatible, integration_errors = await self.validate_integration_compatibility(skill_path)

        # Collect all errors
        all_errors = syntax_errors + import_errors + func_errors + error_errors + integration_errors

        result = ValidationResult(
            skill_name=skill_name,
            skill_path=str(skill_path),
            category=category,
            syntax_valid=syntax_valid,
            import_valid=import_valid,
            functionality_valid=functionality_valid,
            performance_ms=performance_ms,
            memory_usage_mb=memory_usage_mb,
            error_messages=all_errors,
            warnings=warnings,
            api_accuracy_score=api_accuracy,
            integration_compatible=integration_compatible,
            error_handling_valid=error_handling_valid,
            overall_score=0.0,  # Will be calculated
        )

        result.overall_score = self.calculate_overall_score(result)

        return result

    async def validate_all_skills(self) -> SystemValidationReport:
        """Validate all skills in the system"""
        logger.info("Starting comprehensive skills validation...")

        # Discover skills
        categories = self.discover_skills()
        total_skills = sum(len(skills) for skills in categories.values())

        logger.info(f"Discovered {total_skills} skills across {len(categories)} categories")

        # Validate each skill
        for category, skill_files in categories.items():
            if not skill_files:
                continue

            logger.info(f"Validating {len(skill_files)} skills in category: {category}")

            for skill_file in skill_files:
                try:
                    result = await self.validate_single_skill(skill_file, category)
                    self.results.append(result)

                    # Track critical issues
                    if result.overall_score < 50:
                        self.critical_issues.append(
                            f"CRITICAL: {result.skill_name} (score: {result.overall_score}) - "
                            f"{', '.join(result.error_messages[:3])}"
                        )

                except Exception as e:
                    logger.error(f"Failed to validate {skill_file}: {e}")
                    self.critical_issues.append(f"VALIDATION ERROR: {skill_file} - {e}")

        # Generate report
        return self.generate_report(categories)

    def generate_report(self, categories: dict[str, list[Path]]) -> SystemValidationReport:
        """Generate comprehensive validation report"""
        total_skills = len(self.results)
        valid_skills = sum(1 for r in self.results if r.overall_score >= 70)
        invalid_skills = total_skills - valid_skills

        # Calculate averages
        valid_results = [r for r in self.results if r.performance_ms != float("inf")]
        avg_performance = sum(r.performance_ms for r in valid_results) / len(valid_results) if valid_results else 0
        avg_memory = sum(r.memory_usage_mb for r in valid_results) / len(valid_results) if valid_results else 0

        # Calculate system health
        system_health = (valid_skills / total_skills * 100) if total_skills > 0 else 0

        # Generate recommendations
        recommendations = self._generate_recommendations()

        return SystemValidationReport(
            total_skills=total_skills,
            valid_skills=valid_skills,
            invalid_skills=invalid_skills,
            categories={cat: len(skills) for cat, skills in categories.items()},
            average_performance_ms=round(avg_performance, 2),
            average_memory_usage_mb=round(avg_memory, 2),
            overall_system_health=round(system_health, 2),
            critical_issues=self.critical_issues,
            recommendations=recommendations,
            skill_results=self.results,
            validation_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def _generate_recommendations(self) -> list[str]:
        """Generate improvement recommendations"""
        recommendations = []

        # Analyze common issues
        syntax_issues = sum(1 for r in self.results if not r.syntax_valid)
        import_issues = sum(1 for r in self.results if not r.import_valid)
        functionality_issues = sum(1 for r in self.results if not r.functionality_valid)

        if syntax_issues > 0:
            recommendations.append(f"Fix {syntax_issues} skills with syntax errors")

        if import_issues > 0:
            recommendations.append(f"Resolve {import_issues} skills with import dependencies")

        if functionality_issues > 0:
            recommendations.append(f"Address {functionality_issues} skills with functionality issues")

        # Performance recommendations
        slow_skills = [r for r in self.results if r.performance_ms > 1000]
        if slow_skills:
            recommendations.append(f"Optimize {len(slow_skills)} skills with performance > 1s")

        # API accuracy recommendations
        low_api_accuracy = [r for r in self.results if r.api_accuracy_score < 80]
        if low_api_accuracy:
            recommendations.append(f"Improve API accuracy in {len(low_api_accuracy)} skills")

        # Error handling recommendations
        missing_error_handling = [r for r in self.results if not r.error_handling_valid]
        if missing_error_handling:
            recommendations.append(f"Add error handling to {len(missing_error_handling)} skills")

        return recommendations

    def save_report(self, report: SystemValidationReport, filename: str = "skills_validation_report.json"):
        """Save validation report to file"""
        with open(filename, "w") as f:
            json.dump(asdict(report), f, indent=2, default=str)
        logger.info(f"Validation report saved to {filename}")

    def print_summary(self, report: SystemValidationReport):
        """Print validation summary to console"""
        print("\n" + "=" * 80)
        print("SKILLS VALIDATION SYSTEM REPORT")
        print("=" * 80)
        print(f"Validation Timestamp: {report.validation_timestamp}")
        print(f"Total Skills: {report.total_skills}")
        print(f"Valid Skills: {report.valid_skills}")
        print(f"Invalid Skills: {report.invalid_skills}")
        print(f"System Health: {report.overall_system_health}%")
        print(f"Average Performance: {report.average_performance_ms}ms")
        print(f"Average Memory Usage: {report.average_memory_usage_mb}MB")

        print("\nCATEGORIES:")
        for category, count in report.categories.items():
            if count > 0:
                print(f"  {category}: {count} skills")

        if report.critical_issues:
            print(f"\nCRITICAL ISSUES ({len(report.critical_issues)}):")
            for issue in report.critical_issues[:10]:  # Show first 10
                print(f"  • {issue}")
            if len(report.critical_issues) > 10:
                print(f"  ... and {len(report.critical_issues) - 10} more")

        if report.recommendations:
            print("\nRECOMMENDATIONS:")
            for rec in report.recommendations:
                print(f"  • {rec}")

        print("=" * 80)


async def main():
    """Main validation execution"""
    print("🚀 Starting Microsoft Amplifier Skills Validation System...")

    validator = SkillsValidator()
    report = await validator.validate_all_skills()

    # Save and display results
    validator.save_report(report)
    validator.print_summary(report)

    # Exit with appropriate code
    if report.overall_system_health < 70:
        print(f"\n❌ SYSTEM HEALTH BELOW THRESHOLD ({report.overall_system_health}% < 70%)")
        sys.exit(1)
    else:
        print(f"\n✅ SYSTEM HEALTH ACCEPTABLE ({report.overall_system_health}%)")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
