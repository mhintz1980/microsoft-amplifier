"""
Modular Architecture Validation Test Suite

Tests that the modular design principles are correctly implemented and maintained.
Validates separation of concerns, interface contracts, dependency management, and architectural patterns.
"""

import ast
import asyncio
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass
class ArchitectureViolation:
    """Represents an architecture violation"""

    file_path: str
    violation_type: str
    description: str
    severity: str  # "critical", "major", "minor"
    line_number: int | None = None


@dataclass
class ModuleAnalysis:
    """Analysis result for a single module"""

    file_path: str
    module_name: str
    imports: list[str]
    functions: list[str]
    classes: list[str]
    dependencies: list[str]
    circular_dependencies: list[str]
    interface_contracts: list[str]
    violations: list[ArchitectureViolation]
    modularity_score: float
    cohesion_score: float
    coupling_score: float


@dataclass
class ArchitectureTestResult:
    """Result of architecture validation"""

    total_modules: int
    analyzed_modules: int
    violations_found: int
    violations_by_severity: dict[str, int]
    modularity_scores: list[float]
    avg_modularity_score: float
    architectural_patterns_validated: dict[str, bool]
    recommendations: list[str]


class ModularArchitectureValidator:
    """Comprehensive modular architecture validation tool"""

    def __init__(self):
        self.module_analyses: dict[str, ModuleAnalysis] = {}
        self.violations: list[ArchitectureViolation] = []
        self.architecture_patterns = {
            "separation_of_concerns": self._validate_separation_of_concerns,
            "interface_contracts": self._validate_interface_contracts,
            "dependency_injection": self._validate_dependency_injection,
            "single_responsibility": self._validate_single_responsibility,
            "loose_coupling": self._validate_loose_coupling,
            "high_cohesion": self._validate_high_cohesion,
            "modular_boundaries": self._validate_modular_boundaries,
            "abstraction_layers": self._validate_abstraction_layers,
        }

    async def validate_architecture(self, root_directory: Path) -> ArchitectureTestResult:
        """Validate the entire architecture of the codebase"""

        print(f"🔍 Analyzing architecture in: {root_directory}")

        # Find all Python modules
        python_files = list(root_directory.rglob("*.py"))
        python_files = [f for f in python_files if "__pycache__" not in str(f)]

        print(f"📁 Found {len(python_files)} Python files to analyze")

        # Analyze each module
        analyzed_count = 0
        for file_path in python_files:
            try:
                analysis = await self._analyze_module(file_path)
                if analysis:
                    self.module_analyses[str(file_path)] = analysis
                    analyzed_count += 1
            except Exception as e:
                print(f"⚠️ Could not analyze {file_path}: {e}")

        # Validate architectural patterns
        pattern_results = {}
        for pattern_name, validator in self.architecture_patterns.items():
            try:
                pattern_results[pattern_name] = await validator()
            except Exception as e:
                print(f"⚠️ Could not validate pattern {pattern_name}: {e}")
                pattern_results[pattern_name] = False

        # Calculate overall metrics
        modularity_scores = [analysis.modularity_score for analysis in self.module_analyses.values()]
        avg_modularity = sum(modularity_scores) / len(modularity_scores) if modularity_scores else 0

        # Count violations by severity
        violations_by_severity = Counter(v.severity for v in self.violations)

        # Generate recommendations
        recommendations = self._generate_recommendations()

        return ArchitectureTestResult(
            total_modules=len(python_files),
            analyzed_modules=analyzed_count,
            violations_found=len(self.violations),
            violations_by_severity=dict(violations_by_severity),
            modularity_scores=modularity_scores,
            avg_modularity_score=avg_modularity,
            architectural_patterns_validated=pattern_results,
            recommendations=recommendations,
        )

    async def _analyze_module(self, file_path: Path) -> ModuleAnalysis | None:
        """Analyze a single Python module for architectural properties"""

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Extract basic information
            imports = self._extract_imports(tree)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            # Calculate dependencies
            dependencies = self._extract_dependencies(imports)

            # Check for circular dependencies (simplified)
            circular_dependencies = self._check_circular_dependencies(file_path, dependencies)

            # Identify interface contracts
            interface_contracts = self._identify_interface_contracts(tree)

            # Detect architectural violations
            violations = self._detect_violations(file_path, tree, content)

            # Calculate architectural metrics
            modularity_score = self._calculate_modularity_score(functions, classes, dependencies)
            cohesion_score = self._calculate_cohesion_score(tree, functions, classes)
            coupling_score = self._calculate_coupling_score(dependencies)

            return ModuleAnalysis(
                file_path=str(file_path),
                module_name=file_path.stem,
                imports=imports,
                functions=functions,
                classes=classes,
                dependencies=dependencies,
                circular_dependencies=circular_dependencies,
                interface_contracts=interface_contracts,
                violations=violations,
                modularity_score=modularity_score,
                cohesion_score=cohesion_score,
                coupling_score=coupling_score,
            )

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract import statements from AST"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)

        return imports

    def _extract_dependencies(self, imports: list[str]) -> list[str]:
        """Extract module dependencies from imports"""
        dependencies = []

        for imp in imports:
            # Filter out standard library and external dependencies
            if not imp.startswith(
                ("os", "sys", "json", "asyncio", "typing", "dataclasses", "pathlib", "time", "re", "collections")
            ):
                # Focus on local module dependencies
                if "amplifier" in imp or any(keyword in imp for keyword in ["ccsdk", "knowledge", "content"]):
                    dependencies.append(imp)

        return dependencies

    def _check_circular_dependencies(self, file_path: Path, dependencies: list[str]) -> list[str]:
        """Check for circular dependencies (simplified implementation)"""
        # This is a simplified check - a full implementation would build a dependency graph
        circular = []

        current_module = file_path.stem
        for dep in dependencies:
            if current_module in dep:
                circular.append(dep)

        return circular

    def _identify_interface_contracts(self, tree: ast.AST) -> list[str]:
        """Identify interface contracts and abstract base classes"""
        contracts = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for abstract classes
                has_abstract_methods = any(
                    isinstance(n, ast.FunctionDef)
                    and any(
                        decorator.id == "abstractmethod"
                        for decorator in getattr(n, "decorator_list", [])
                        if isinstance(decorator, ast.Name)
                    )
                    for n in node.body
                    if isinstance(n, ast.FunctionDef)
                )

                if has_abstract_methods:
                    contracts.append(node.name)

                # Check for protocol classes
                if any(base.id == "Protocol" for base in node.bases if isinstance(base, ast.Name)):
                    contracts.append(node.name)

        return contracts

    def _detect_violations(self, file_path: Path, tree: ast.AST, content: str) -> list[ArchitectureViolation]:
        """Detect architectural violations in the module"""
        violations = []

        # Check for overly long functions (violates SRP)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count lines of code
                lines_of_code = node.end_lineno - node.lineno if hasattr(node, "end_lineno") else 0
                if lines_of_code > 50:  # Function is too long
                    violations.append(
                        ArchitectureViolation(
                            file_path=str(file_path),
                            violation_type="function_too_long",
                            description=f"Function '{node.name}' is {lines_of_code} lines (should be < 50)",
                            severity="major",
                            line_number=node.lineno,
                        )
                    )

                # Check for too many parameters
                if len(node.args.args) > 7:
                    violations.append(
                        ArchitectureViolation(
                            file_path=str(file_path),
                            violation_type="too_many_parameters",
                            description=f"Function '{node.name}' has {len(node.args.args)} parameters (should be ≤ 7)",
                            severity="minor",
                            line_number=node.lineno,
                        )
                    )

        # Check for deep nesting
        max_depth = self._calculate_max_nesting_depth(tree)
        if max_depth > 4:
            violations.append(
                ArchitectureViolation(
                    file_path=str(file_path),
                    violation_type="deep_nesting",
                    description=f"Maximum nesting depth is {max_depth} (should be ≤ 4)",
                    severity="minor",
                )
            )

        # Check for hardcoded values (magic numbers)
        magic_numbers = re.findall(r"\b\d{2,}\b", content)
        if len(magic_numbers) > 5:
            violations.append(
                ArchitectureViolation(
                    file_path=str(file_path),
                    violation_type="magic_numbers",
                    description=f"Found {len(magic_numbers)} magic numbers, consider using constants",
                    severity="minor",
                )
            )

        # Check for god classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 20:  # Too many methods
                    violations.append(
                        ArchitectureViolation(
                            file_path=str(file_path),
                            violation_type="god_class",
                            description=f"Class '{node.name}' has {len(methods)} methods (should be ≤ 20)",
                            severity="major",
                            line_number=node.lineno,
                        )
                    )

        self.violations.extend(violations)
        return violations

    def _calculate_max_nesting_depth(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth in the AST"""
        max_depth = 0

        def calculate_depth(node, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)

            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.If | ast.While | ast.For | ast.With | ast.Try):
                    calculate_depth(child, current_depth + 1)
                else:
                    calculate_depth(child, current_depth)

        calculate_depth(tree)
        return max_depth

    def _calculate_modularity_score(self, functions: list[str], classes: list[str], dependencies: list[str]) -> float:
        """Calculate modularity score for the module"""
        # Factors that contribute to good modularity:
        # 1. Reasonable number of functions/classes
        # 2. Limited dependencies
        # 3. Clear purpose

        total_elements = len(functions) + len(classes)
        if total_elements == 0:
            return 1.0

        # Penalize too many or too few elements
        size_score = 1.0
        if total_elements > 50:  # Too large
            size_score = max(0.0, 1.0 - (total_elements - 50) / 100)
        elif total_elements < 3:  # Too small
            size_score = 0.5

        # Penalize too many dependencies
        dependency_score = max(0.0, 1.0 - len(dependencies) / 10)

        # Combine scores
        return (size_score + dependency_score) / 2

    def _calculate_cohesion_score(self, tree: ast.AST, functions: list[str], classes: list[str]) -> float:
        """Calculate cohesion score (how well elements belong together)"""
        # Simplified cohesion calculation based on naming and structure
        if not functions and not classes:
            return 1.0

        # Check if functions/classes have consistent naming/purpose
        name_parts = []
        for name in functions + classes:
            # Extract name components (simplified)
            parts = re.findall(r"[a-z]+|[A-Z][a-z]*", name)
            name_parts.extend([p.lower() for p in parts])

        # Calculate name similarity
        if not name_parts:
            return 0.5

        common_parts = Counter(name_parts).most_common(3)
        cohesion = sum(count for _, count in common_parts) / len(name_parts)

        return min(1.0, cohesion * 2)  # Scale to 0-1 range

    def _calculate_coupling_score(self, dependencies: list[str]) -> float:
        """Calculate coupling score (how dependent the module is on others)"""
        # Lower coupling is better
        if not dependencies:
            return 1.0

        # Penalize more dependencies
        coupling_score = max(0.0, 1.0 - len(dependencies) / 10)
        return coupling_score

    async def _validate_separation_of_concerns(self) -> bool:
        """Validate that concerns are properly separated"""
        # Check that modules have focused responsibilities
        focused_modules = 0
        total_modules = len(self.module_analyses)

        for analysis in self.module_analyses.values():
            # Simple heuristic: module should have either mostly functions or mostly classes
            func_count = len(analysis.functions)
            class_count = len(analysis.classes)

            total_elements = func_count + class_count
            if total_elements == 0:
                focused_modules += 1
                continue

            # Calculate focus (how skewed the distribution is)
            max_count = max(func_count, class_count)
            focus_ratio = max_count / total_elements

            if focus_ratio >= 0.7:  # 70% or more focused
                focused_modules += 1

        return focused_modules / total_modules >= 0.8 if total_modules > 0 else True

    async def _validate_interface_contracts(self) -> bool:
        """Validate that interface contracts are properly defined"""
        # Check for presence of abstract classes and interfaces
        total_interfaces = sum(len(analysis.interface_contracts) for analysis in self.module_analyses.values())
        total_modules = len(self.module_analyses)

        # Should have interfaces for major components
        return total_interfaces >= total_modules * 0.1  # At least 10% of modules should define interfaces

    async def _validate_dependency_injection(self) -> bool:
        """Validate dependency injection patterns"""
        # Look for constructor injection patterns
        injection_count = 0
        total_classes = sum(len(analysis.classes) for analysis in self.module_analyses.values())

        for analysis in self.module_analyses.values():
            # This is a simplified check - real implementation would analyze actual patterns
            for file_path in [analysis.file_path]:
                try:
                    with open(file_path) as f:
                        content = f.read()
                        # Look for constructor injection patterns
                        if "__init__" in content and "typing" in content:
                            injection_count += 1
                            break
                except Exception:
                    continue

        return injection_count >= total_classes * 0.2 if total_classes > 0 else True

    async def _validate_single_responsibility(self) -> bool:
        """Validate single responsibility principle"""
        # Check that classes and functions have focused responsibilities
        violations = [v for v in self.violations if v.violation_type in ["function_too_long", "god_class"]]
        total_modules = len(self.module_analyses)

        # Should have minimal SRP violations
        return len(violations) <= total_modules * 0.1 if total_modules > 0 else True

    async def _validate_loose_coupling(self) -> bool:
        """Validate loose coupling between modules"""
        # Check average coupling score
        coupling_scores = [analysis.coupling_score for analysis in self.module_analyses.values()]

        if not coupling_scores:
            return True

        avg_coupling = sum(coupling_scores) / len(coupling_scores)
        return avg_coupling >= 0.7  # Should have low coupling

    async def _validate_high_cohesion(self) -> bool:
        """Validate high cohesion within modules"""
        # Check average cohesion score
        cohesion_scores = [analysis.cohesion_score for analysis in self.module_analyses.values()]

        if not cohesion_scores:
            return True

        avg_cohesion = sum(cohesion_scores) / len(cohesion_scores)
        return avg_cohesion >= 0.6  # Should have high cohesion

    async def _validate_modular_boundaries(self) -> bool:
        """Validate that modular boundaries are respected"""
        # Check for circular dependencies
        circular_violations = sum(len(analysis.circular_dependencies) for analysis in self.module_analyses.values())

        # Should have minimal circular dependencies
        return circular_violations == 0

    async def _validate_abstraction_layers(self) -> bool:
        """Validate proper abstraction layers"""
        # Check that modules are properly layered
        # This is a simplified check - real implementation would analyze import patterns
        layer_violations = 0

        for analysis in self.module_analyses.values():
            # Check if implementation details leak across boundaries
            for dep in analysis.dependencies:
                if "implementation" in dep.lower() or "internal" in dep.lower():
                    layer_violations += 1

        return layer_violations <= len(self.module_analyses) * 0.1 if self.module_analyses else True

    def _generate_recommendations(self) -> list[str]:
        """Generate architectural improvement recommendations"""
        recommendations = []

        # Analyze violations
        critical_violations = [v for v in self.violations if v.severity == "critical"]
        major_violations = [v for v in self.violations if v.severity == "major"]

        if critical_violations:
            recommendations.append("🚨 Address critical architectural violations immediately")

        if major_violations:
            recommendations.append("⚠️ Refactor modules with major architectural issues")

        # Analyze modularity scores
        if self.module_analyses:
            avg_modularity = sum(a.modularity_score for a in self.module_analyses.values()) / len(self.module_analyses)
            if avg_modularity < 0.7:
                recommendations.append("📦 Improve modularity by breaking down large modules")

            # Analyze coupling
            avg_coupling = sum(a.coupling_score for a in self.module_analyses.values()) / len(self.module_analyses)
            if avg_coupling < 0.7:
                recommendations.append("🔗 Reduce coupling between modules")

            # Analyze cohesion
            avg_cohesion = sum(a.cohesion_score for a in self.module_analyses.values()) / len(self.module_analyses)
            if avg_cohesion < 0.6:
                recommendations.append("🎯 Improve cohesion by grouping related functionality")

        # Interface recommendations
        total_interfaces = sum(len(analysis.interface_contracts) for analysis in self.module_analyses.values())
        if total_interfaces < len(self.module_analyses) * 0.1:
            recommendations.append("📋 Define more interface contracts for better abstraction")

        return recommendations


# Pytest integration
@pytest.fixture
async def architecture_validator():
    """Pytest fixture for architecture validator"""
    validator = ModularArchitectureValidator()
    yield validator


@pytest.mark.asyncio
async def test_modular_architecture_validation(architecture_validator):
    """Test modular architecture validation"""
    # Test on the amplifier directory
    amplifier_dir = Path(__file__).parent.parent.parent / "amplifier"

    if amplifier_dir.exists():
        result = await architecture_validator.validate_architecture(amplifier_dir)

        # Validate results
        assert result.analyzed_modules > 0
        assert result.avg_modularity_score >= 0.5  # At least 50% modularity

        # Check that architectural patterns are mostly validated
        validated_patterns = sum(result.architectural_patterns_validated.values())
        total_patterns = len(result.architectural_patterns_validated)
        assert validated_patterns / total_patterns >= 0.6  # At least 60% of patterns should be valid


@pytest.mark.asyncio
async def test_separation_of_concerns(architecture_validator):
    """Test separation of concerns validation"""
    result = await architecture_validator._validate_separation_of_concerns()
    assert isinstance(result, bool)


# CLI interface
async def main():
    """Main CLI interface for architecture validation"""
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress
    from rich.progress import SpinnerColumn
    from rich.progress import TextColumn
    from rich.table import Table

    console = Console()
    validator = ModularArchitectureValidator()

    console.print("🏗️ [bold blue]Modular Architecture Validation Suite[/bold blue]")
    console.print("=" * 80)

    # Validate the amplifier directory
    amplifier_dir = Path(__file__).parent.parent.parent / "amplifier"

    if amplifier_dir.exists():
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("Analyzing architecture...", total=1)

            result = await validator.validate_architecture(amplifier_dir)
            progress.update(task, advance=1)

        # Print summary
        summary_text = f"""
        Total Modules: {result.total_modules}
        Analyzed Modules: {result.analyzed_modules}
        Architecture Violations: {result.violations_found}
        Average Modularity Score: {result.avg_modularity_score:.2f}/1.0
        """
        console.print(Panel(summary_text.strip(), title="Architecture Validation Summary", border_style="green"))

        # Violations breakdown
        if result.violations_by_severity:
            console.print("\n🚨 [bold red]Architecture Violations by Severity[/bold red]")
            console.print("-" * 80)

            violations_table = Table(title="Violations Breakdown")
            violations_table.add_column("Severity", style="red")
            violations_table.add_column("Count", style="yellow")

            for severity, count in result.violations_by_severity.items():
                violations_table.add_row(severity.upper(), str(count))

            console.print(violations_table)

        # Architectural patterns validation
        console.print("\n✅ [bold green]Architectural Patterns Validation[/bold green]")
        console.print("-" * 80)

        patterns_table = Table(title="Patterns Validation")
        patterns_table.add_column("Pattern", style="cyan")
        patterns_table.add_column("Status", style="green")

        for pattern_name, validated in result.architectural_patterns_validated.items():
            status = "✅ VALID" if validated else "❌ INVALID"
            color = "green" if validated else "red"
            patterns_table.add_row(pattern_name.replace("_", " ").title(), f"[{color}]{status}[/{color}]")

        console.print(patterns_table)

        # Modularity scores distribution
        if result.modularity_scores:
            console.print("\n📊 [bold cyan]Modularity Scores Distribution[/bold cyan]")
            console.print("-" * 80)

            # Simple histogram
            score_ranges = {"Excellent (0.8-1.0)": 0, "Good (0.6-0.8)": 0, "Fair (0.4-0.6)": 0, "Poor (0.0-0.4)": 0}

            for score in result.modularity_scores:
                if score >= 0.8:
                    score_ranges["Excellent (0.8-1.0)"] += 1
                elif score >= 0.6:
                    score_ranges["Good (0.6-0.8)"] += 1
                elif score >= 0.4:
                    score_ranges["Fair (0.4-0.6)"] += 1
                else:
                    score_ranges["Poor (0.0-0.4)"] += 1

            score_table = Table()
            score_table.add_column("Score Range", style="cyan")
            score_table.add_column("Modules", style="magenta")

            for range_name, count in score_ranges.items():
                score_table.add_row(range_name, str(count))

            console.print(score_table)

        # Recommendations
        if result.recommendations:
            console.print("\n💡 [bold yellow]Architectural Recommendations[/bold yellow]")
            console.print("-" * 80)

            for recommendation in result.recommendations:
                console.print(f"• {recommendation}")

        # Show some sample violations if any
        if validator.violations:
            console.print("\n🔍 [bold red]Sample Architecture Violations[/bold red]")
            console.print("-" * 80)

            for violation in validator.violations[:5]:  # Show first 5
                console.print(f"[{violation.severity.upper()}] {violation.description}")
                console.print(f"   📁 {violation.file_path}:{violation.line_number or '?'}")

        # Save results
        report_data = {
            "summary": {
                "total_modules": result.total_modules,
                "analyzed_modules": result.analyzed_modules,
                "violations_found": result.violations_found,
                "avg_modularity_score": result.avg_modularity_score,
                "violations_by_severity": result.violations_by_severity,
            },
            "patterns_validated": result.architectural_patterns_validated,
            "recommendations": result.recommendations,
            "modularity_scores": result.modularity_scores,
        }

        report_path = Path("architecture_validation_results.json")
        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        console.print(f"\n📁 Full report saved to: {report_path.absolute()}")

    else:
        console.print("❌ Amplifier directory not found")


if __name__ == "__main__":
    asyncio.run(main())
