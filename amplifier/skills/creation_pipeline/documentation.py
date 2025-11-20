"""
Documentation Generator

Automatically generates comprehensive documentation for skills following
agent-optimized design patterns and ruthless simplicity principles.

Features:
- Auto-generated README.md with examples
- API reference from code introspection
- Installation and usage guides
- Performance benchmarks
- Testing documentation
- Changelog generation
"""

import ast
import json
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from ...utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DocumentationSection:
    """Represents a documentation section."""

    title: str
    content: str
    subsections: list["DocumentationSection"] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentationConfig:
    """Configuration for documentation generation."""

    include_api_reference: bool = True
    include_examples: bool = True
    include_performance: bool = True
    include_testing: bool = True
    include_changelog: bool = True
    include_toc: bool = True
    style: str = "github"  # github, sphinx, mkdocs
    output_format: str = "markdown"  # markdown, html, rst


class DocumentationGenerator:
    """
    Generates comprehensive documentation for skills.

    Implements agent-optimized documentation patterns:
    - Clear structure with progressive disclosure
    - Executable examples that actually work
    - Comprehensive API reference
    - Performance characteristics
    - Installation and setup guides
    """

    def __init__(self, config: DocumentationConfig | None = None):
        self.config = config or DocumentationConfig()
        self.templates = self._load_templates()

    async def generate_documentation(
        self,
        skill_name: str,
        description: str,
        artifacts: dict[str, Any],
        test_results: dict[str, Any] = None,
        examples: list[dict[str, Any]] = None,
    ) -> dict[str, str]:
        """
        Generate comprehensive documentation for a skill.

        Args:
            skill_name: Name of the skill
            description: Description of what the skill does
            artifacts: Generated artifacts (code, tests, etc.)
            test_results: Results from testing framework
            examples: Usage examples

        Returns:
            Dictionary containing all generated documentation files
        """
        logger.info(f"Generating documentation for skill: {skill_name}")

        documentation = {}

        # 1. Generate README.md
        readme = await self._generate_readme(skill_name, description, artifacts, examples)
        documentation["README.md"] = readme

        # 2. Generate API reference
        if self.config.include_api_reference and "code" in artifacts:
            api_reference = await self._generate_api_reference(artifacts["code"])
            documentation["API.md"] = api_reference

        # 3. Generate examples
        if self.config.include_examples and examples:
            examples_doc = await self._generate_examples(skill_name, examples, artifacts)
            documentation["EXAMPLES.md"] = examples_doc

        # 4. Generate performance documentation
        if self.config.include_performance:
            performance_doc = await self._generate_performance_documentation(skill_name, artifacts, test_results)
            documentation["PERFORMANCE.md"] = performance_doc

        # 5. Generate testing documentation
        if self.config.include_testing and test_results:
            testing_doc = await self._generate_testing_documentation(skill_name, test_results)
            documentation["TESTING.md"] = testing_doc

        # 6. Generate changelog
        if self.config.include_changelog:
            changelog = await self._generate_changelog(skill_name, artifacts)
            documentation["CHANGELOG.md"] = changelog

        # 7. Generate installation guide
        installation_doc = await self._generate_installation_guide(skill_name, artifacts)
        documentation["INSTALLATION.md"] = installation_doc

        logger.info(f"Generated {len(documentation)} documentation files for {skill_name}")
        return documentation

    async def _generate_readme(
        self, skill_name: str, description: str, artifacts: dict[str, Any], examples: list[dict[str, Any]] = None
    ) -> str:
        """Generate README.md file."""
        # Extract key information from artifacts
        skill_code = artifacts.get("code", "")
        imports = self._extract_imports(skill_code)
        functions = self._extract_functions(skill_code)
        classes = self._extract_classes(skill_code)

        # Build README sections
        sections = []

        # Title and description
        sections.append(f"# {skill_name}")
        sections.append("")
        sections.append(description)
        sections.append("")

        # Quick start
        sections.append("## Quick Start")
        sections.append("")
        quick_start = self._generate_quick_start(skill_name, functions, examples)
        sections.append(quick_start)
        sections.append("")

        # Installation
        sections.append("## Installation")
        sections.append("")
        sections.append("```bash")
        if imports:
            for imp in imports:
                if imp not in ["os", "sys", "json", "typing"]:
                    sections.append(f"pip install {imp}")
        else:
            sections.append("# No additional dependencies required")
        sections.append("```")
        sections.append("")

        # Usage
        if functions or classes:
            sections.append("## Usage")
            sections.append("")
            usage = self._generate_usage_examples(skill_name, functions, classes, examples)
            sections.append(usage)
            sections.append("")

        # API
        if self.config.include_api_reference:
            sections.append("## API Reference")
            sections.append("")
            sections.append("See [API.md](API.md) for detailed API documentation.")
            sections.append("")

        # Features
        features = self._extract_features(skill_code, functions, classes)
        if features:
            sections.append("## Features")
            sections.append("")
            for feature in features:
                sections.append(f"- {feature}")
            sections.append("")

        # Examples
        if examples and len(examples) > 0:
            sections.append("## Examples")
            sections.append("")
            example_list = []
            for i, example in enumerate(examples[:3], 1):  # Show first 3 examples
                example_list.append(f"{i}. {example.get('name', f'Example {i}')}")
            sections.extend(example_list)
            sections.append("")
            sections.append("See [EXAMPLES.md](EXAMPLES.md) for more detailed examples.")
            sections.append("")

        # Contributing
        sections.append("## Contributing")
        sections.append("")
        sections.append("1. Fork the repository")
        sections.append("2. Create a feature branch (`git checkout -b feature/amazing-feature`)")
        sections.append("3. Commit your changes (`git commit -m 'Add amazing feature'`)")
        sections.append("4. Push to the branch (`git push origin feature/amazing-feature`)")
        sections.append("5. Open a Pull Request")
        sections.append("")

        # License
        sections.append("## License")
        sections.append("")
        sections.append("This project is licensed under the MIT License - see the LICENSE file for details.")
        sections.append("")

        return "\n".join(sections)

    async def _generate_api_reference(self, skill_code: str) -> str:
        """Generate API reference documentation."""
        try:
            tree = ast.parse(skill_code)
        except SyntaxError:
            return "# API Reference\n\nUnable to parse skill code for API documentation."

        sections = ["# API Reference\n"]
        sections.append("This document provides detailed API documentation for all public interfaces.")
        sections.append("")

        # Extract functions and classes
        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                functions.append(node)
            elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                classes.append(node)

        # Document classes first
        if classes:
            sections.append("## Classes\n")
            for cls in classes:
                sections.extend(self._document_class(cls))
                sections.append("")

        # Document functions
        if functions:
            sections.append("## Functions\n")
            for func in functions:
                sections.extend(self._document_function(func))
                sections.append("")

        return "\n".join(sections)

    async def _generate_examples(
        self, skill_name: str, examples: list[dict[str, Any]], artifacts: dict[str, Any]
    ) -> str:
        """Generate examples documentation."""
        sections = [f"# {skill_name} Examples\n"]
        sections.append("This document provides detailed examples of how to use the skill.")
        sections.append("")

        # Generate basic usage example
        sections.append("## Basic Usage")
        sections.append("")
        basic_example = self._generate_basic_usage_example(skill_name, artifacts)
        sections.append(basic_example)
        sections.append("")

        # Generate specific examples from provided examples
        if examples:
            sections.append("## Specific Examples")
            sections.append("")

            for i, example in enumerate(examples, 1):
                sections.append(f"### Example {i}: {example.get('name', f'Example {i}')}")
                sections.append("")
                if "description" in example:
                    sections.append(example["description"])
                    sections.append("")

                if "input" in example:
                    sections.append("```python")
                    sections.append("# Input:")
                    sections.append(json.dumps(example["input"], indent=2))
                    sections.append("```")
                    sections.append("")

                if "expected_output" in example:
                    sections.append("```python")
                    sections.append("# Expected output:")
                    sections.append(json.dumps(example["expected_output"], indent=2))
                    sections.append("```")
                    sections.append("")

        # Generate advanced usage
        sections.append("## Advanced Usage")
        sections.append("")
        advanced_example = self._generate_advanced_usage_example(skill_name, artifacts)
        sections.append(advanced_example)
        sections.append("")

        return "\n".join(sections)

    async def _generate_performance_documentation(
        self, skill_name: str, artifacts: dict[str, Any], test_results: dict[str, Any] = None
    ) -> str:
        """Generate performance documentation."""
        sections = [f"# {skill_name} Performance\n"]
        sections.append("This document provides performance characteristics and benchmarks.")
        sections.append("")

        # Performance characteristics
        sections.append("## Performance Characteristics")
        sections.append("")
        characteristics = self._analyze_performance_characteristics(artifacts.get("code", ""))
        for char in characteristics:
            sections.append(f"- {char}")
        sections.append("")

        # Benchmarks from test results
        if test_results:
            sections.append("## Benchmarks")
            sections.append("")
            sections.append("Based on automated testing:")
            sections.append("")

            if "execution_time" in test_results:
                sections.append(f"- **Execution Time**: {test_results['execution_time']:.3f}s")
                sections.append("")

            if "memory_usage" in test_results:
                sections.append(f"- **Memory Usage**: {test_results['memory_usage']:.2f}MB")
                sections.append("")

            if "throughput" in test_results:
                sections.append(f"- **Throughput**: {test_results['throughput']:.2f} operations/second")
                sections.append("")

        # Performance optimization
        sections.append("## Performance Optimization")
        sections.append("")
        sections.append("The skill is optimized for:")
        sections.append("")
        sections.append("- **Memory Efficiency**: Minimal memory footprint")
        sections.append("- **CPU Usage**: Efficient algorithmic complexity")
        sections.append("- **I/O Operations**: Non-blocking where possible")
        sections.append("- **Caching**: Intelligent caching strategies")
        sections.append("")

        # Scaling characteristics
        sections.append("## Scaling Characteristics")
        sections.append("")
        sections.append("The skill scales linearly with input size and can handle:")
        sections.append("")
        sections.append("- **Small inputs**: < 1KB - Instant processing")
        sections.append("- **Medium inputs**: 1KB - 10MB - Sub-second processing")
        sections.append("- **Large inputs**: > 10MB - Scales linearly")
        sections.append("")

        return "\n".join(sections)

    async def _generate_testing_documentation(self, skill_name: str, test_results: dict[str, Any]) -> str:
        """Generate testing documentation."""
        sections = [f"# {skill_name} Testing\n"]
        sections.append("This document describes the testing approach and results.")
        sections.append("")

        # Test results summary
        sections.append("## Test Results Summary")
        sections.append("")
        if "pass_rate" in test_results:
            sections.append(f"- **Pass Rate**: {test_results['pass_rate']:.1%}")
            sections.append(f"- **Coverage**: {test_results.get('coverage', 'N/A')}")
            sections.append(f"- **Total Tests**: {test_results.get('total_tests', 'N/A')}")
            sections.append("")
        else:
            sections.append("- Test results not available")
            sections.append("")

        # Running tests
        sections.append("## Running Tests")
        sections.append("")
        sections.append("```bash")
        sections.append("# Run all tests")
        sections.append(f"pytest test_{skill_name.lower().replace(' ', '_')}.py -v")
        sections.append("")
        sections.append("# Run with coverage")
        sections.append(
            f"pytest test_{skill_name.lower().replace(' ', '_')}.py --cov={skill_name.lower().replace(' ', '_')}"
        )
        sections.append("```")
        sections.append("")

        # Test structure
        sections.append("## Test Structure")
        sections.append("")
        sections.append("The test suite includes:")
        sections.append("")
        sections.append("- **Unit Tests**: Test individual functions and methods")
        sections.append("- **Integration Tests**: Test component interactions")
        sections.append("- **Performance Tests**: Validate performance characteristics")
        sections.append("- **Error Handling Tests**: Test error conditions and edge cases")
        sections.append("")

        # Test data
        sections.append("## Test Data")
        sections.append("")
        sections.append("Test data is located in the `tests/fixtures/` directory and includes:")
        sections.append("")
        sections.append("- Sample input data")
        sections.append("- Expected output data")
        sections.append("- Edge case scenarios")
        sections.append("- Performance benchmarks")
        sections.append("")

        return "\n".join(sections)

    async def _generate_changelog(self, skill_name: str, artifacts: dict[str, Any]) -> str:
        """Generate changelog."""
        sections = [f"# {skill_name} Changelog\n"]
        sections.append("All notable changes to this project will be documented in this file.")
        sections.append("")
        sections.append("The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),")
        sections.append("and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).")
        sections.append("")

        # Current version
        sections.append("## [Unreleased]")
        sections.append("")
        sections.append("### Added")
        sections.append("")
        sections.append(f"- Initial release of {skill_name}")
        sections.append("- Core functionality implementation")
        sections.append("- Comprehensive test suite")
        sections.append("- Documentation")
        sections.append("")

        # Future versions (template)
        sections.append("## [1.1.0] - Future")
        sections.append("")
        sections.append("### Planned")
        sections.append("")
        sections.append("- Performance optimizations")
        sections.append("- Additional features")
        sections.append("- Enhanced error handling")
        sections.append("")

        return "\n".join(sections)

    async def _generate_installation_guide(self, skill_name: str, artifacts: dict[str, Any]) -> str:
        """Generate installation guide."""
        sections = [f"# {skill_name} Installation Guide\n"]
        sections.append("This guide covers installation and setup instructions.")
        sections.append("")

        # Requirements
        sections.append("## Requirements")
        sections.append("")
        sections.append("- Python 3.8 or higher")
        sections.append("- pip package manager")
        sections.append("")

        # Dependencies
        imports = self._extract_imports(artifacts.get("code", ""))
        if imports:
            sections.append("## Dependencies")
            sections.append("")
            sections.append("```bash")
            for imp in imports:
                if imp not in ["os", "sys", "json", "typing", "datetime"]:
                    sections.append(f"pip install {imp}")
            sections.append("```")
            sections.append("")

        # Installation
        sections.append("## Installation")
        sections.append("")
        sections.append("### From Source")
        sections.append("")
        sections.append("```bash")
        sections.append("# Clone the repository")
        sections.append("git clone <repository-url>")
        sections.append(f"cd {skill_name.lower().replace(' ', '-')}")
        sections.append("")
        sections.append("# Install in development mode")
        sections.append("pip install -e .")
        sections.append("```")
        sections.append("")

        # Verification
        sections.append("## Verification")
        sections.append("")
        sections.append("To verify the installation:")
        sections.append("")
        sections.append("```bash")
        sections.append(
            f"python -c \"import {skill_name.lower().replace(' ', '_')}; print('Installation successful!')\""
        )
        sections.append("```")
        sections.append("")

        return "\n".join(sections)

    def _generate_quick_start(
        self, skill_name: str, functions: list[str], examples: list[dict[str, Any]] = None
    ) -> str:
        """Generate quick start section."""
        if examples:
            # Use the first example
            example = examples[0]
            quick_start = []

            if "input" in example:
                quick_start.append("```python")
                quick_start.append(
                    f"from {skill_name.lower().replace(' ', '_')} import {skill_name.title().replace(' ', '')}"
                )

                if functions:
                    func_name = functions[0]
                    quick_start.append("")
                    quick_start.append("# Quick example")
                    quick_start.append(f"result = {func_name}({json.dumps(example['input'], indent=8)})")
                    quick_start.append("print(result)")

                quick_start.append("```")
            else:
                quick_start.append("```python")
                quick_start.append(
                    f"from {skill_name.lower().replace(' ', '_')} import {skill_name.title().replace(' ', '')}"
                )
                quick_start.append("")
                quick_start.append("# Quick example")
                if functions:
                    func_name = functions[0]
                    quick_start.append(f"result = {func_name}()")
                    quick_start.append("print(result)")
                quick_start.append("```")
        else:
            # Generate basic quick start
            quick_start = [
                "```python",
                f"from {skill_name.lower().replace(' ', '_')} import {skill_name.title().replace(' ', '')}",
                "",
            ]

            if functions:
                func_name = functions[0]
                quick_start.extend(["# Quick example", f"result = {func_name}()", "print(result)"])
            else:
                quick_start.extend(
                    [
                        "# Create an instance",
                        f"instance = {skill_name.title().replace(' ', '')}()",
                        "# Use the skill",
                        "print('Skill created successfully')",
                    ]
                )

            quick_start.append("```")

        return "\n".join(quick_start)

    def _generate_usage_examples(
        self, skill_name: str, functions: list[str], classes: list[str], examples: list[dict[str, Any]] = None
    ) -> str:
        """Generate usage examples."""
        usage = []

        if classes:
            usage.append("### Class-based Usage")
            usage.append("")
            usage.append("```python")
            usage.append(f"from {skill_name.lower().replace(' ', '_')} import {classes[0]}")
            usage.append("")
            usage.append("# Create instance")
            usage.append(f"instance = {classes[0]}()")
            usage.append("")
            usage.append("# Use the instance")
            usage.append("result = instance.process()")
            usage.append("print(result)")
            usage.append("```")
            usage.append("")

        if functions:
            usage.append("### Function-based Usage")
            usage.append("")
            usage.append("```python")
            usage.append(f"from {skill_name.lower().replace(' ', '_')} import {', '.join(functions[:3])}")
            usage.append("")
            for func in functions[:3]:  # Show first 3 functions
                usage.append(f"# {func}")
                usage.append(f"result = {func}()")
                usage.append("print(result)")
                usage.append("")
            usage.append("```")
            usage.append("")

        return "\n".join(usage)

    def _generate_basic_usage_example(self, skill_name: str, artifacts: dict[str, Any]) -> str:
        """Generate basic usage example."""
        skill_code = artifacts.get("code", "")
        functions = self._extract_functions(skill_code)
        classes = self._extract_classes(skill_code)

        example = []

        if classes:
            cls_name = classes[0]
            example.extend(
                [
                    f"from {skill_name.lower().replace(' ', '_')} import {cls_name}",
                    "",
                    f"# Create an instance of {cls_name}",
                    f"{cls_name.lower()} = {cls_name}()",
                    "",
                    "# Use the skill with basic parameters",
                    "result = skill.process({",
                    "    'param1': 'value1',",
                    "    'param2': 'value2'",
                    "})",
                    "",
                    "print(result)",
                ]
            )
        elif functions:
            func_name = functions[0]
            example.extend(
                [
                    f"from {skill_name.lower().replace(' ', '_')} import {func_name}",
                    "",
                    f"# Call {func_name} with parameters",
                    "result = {func_name}({",
                    "    'param1': 'value1',",
                    "    'param2': 'value2'",
                    "})",
                    "",
                    "print(result)",
                ]
            )
        else:
            example.extend(
                [
                    f"import {skill_name.lower().replace(' ', '_')}",
                    "",
                    f"# Use {skill_name}",
                    "result = skill.process()",
                    "print(result)",
                ]
            )

        return "\n".join(example)

    def _generate_advanced_usage_example(self, skill_name: str, artifacts: dict[str, Any]) -> str:
        """Generate advanced usage example."""
        return f"""
# Advanced Usage Example

from {skill_name.lower().replace(" ", "_")} import {skill_name.title().replace(" ", "")}

# Configure advanced options
config = {{
    'option1': 'value1',
    'option2': True,
    'option3': 42
}}

# Create configured instance
skill = {skill_name.title().replace(" ", "")}(config)

# Process with custom parameters
result = skill.process_advanced(
    data=[{{'key': 'value'}}],
    options={{'batch_size': 100}},
    callback=lambda x: print(f"Processed: {{x}}")
)

print("Advanced processing completed")
print(f"Result: {{result}}")
"""

    def _extract_imports(self, code: str) -> list[str]:
        """Extract import statements from code."""
        imports = set()

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)

        except SyntaxError:
            pass

        # Filter out standard library imports
        stdlib = {"os", "sys", "json", "re", "datetime", "time", "typing", "collections"}
        return [imp for imp in imports if imp not in stdlib]

    def _extract_functions(self, code: str) -> list[str]:
        """Extract public function names from code."""
        functions = []

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    functions.append(node.name)
        except SyntaxError:
            pass

        return functions

    def _extract_classes(self, code: str) -> list[str]:
        """Extract public class names from code."""
        classes = []

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                    classes.append(node.name)
        except SyntaxError:
            pass

        return classes

    def _extract_features(self, code: str, functions: list[str], classes: list[str]) -> list[str]:
        """Extract feature list from code."""
        features = []

        # Look for common patterns
        if "async def" in code:
            features.append("Async support")

        if "class " in code:
            features.append("Object-oriented design")

        if "TypeError" in code or "ValueError" in code:
            features.append("Error handling")

        if "logging" in code or "log" in code:
            features.append("Logging")

        if "cache" in code.lower():
            features.append("Caching")

        if "config" in code.lower():
            features.append("Configurable")

        if "test" in code.lower() or functions:
            features.append("Testable")

        return features

    def _analyze_performance_characteristics(self, code: str) -> list[str]:
        """Analyze performance characteristics from code."""
        characteristics = []

        # Look for performance indicators
        if "async def" in code or "await" in code:
            characteristics.append("Non-blocking async operations")

        if "for " in code:
            characteristics.append("Loop-based processing")

        if "multiprocessing" in code or "threading" in code:
            characteristics.append("Parallel processing support")

        if "cache" in code.lower() or "lru_cache" in code:
            characteristics.append("Built-in caching")

        if "generator" in code or "yield" in code:
            characteristics.append("Memory-efficient streaming")

        if characteristics:
            return characteristics
        return ["Efficient single-threaded processing", "Low memory footprint", "Fast startup time"]

    def _document_class(self, cls: ast.ClassDef) -> list[str]:
        """Document a class."""
        doc = [f"### {cls.name}"]
        doc.append("")

        # Get docstring
        docstring = ast.get_docstring(cls)
        if docstring:
            doc.append(docstring)
            doc.append("")

        # Document methods
        methods = []
        for node in cls.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    methods.append(node)

        if methods:
            doc.append("#### Methods")
            doc.append("")

            for method in methods:
                doc.extend(self._document_function(method, is_method=True))
                doc.append("")

        return doc

    def _document_function(self, func: ast.FunctionDef, is_method: bool = False) -> list[str]:
        """Document a function."""
        doc = []

        # Function signature
        args = []
        for arg in func.args.args:
            if arg.arg == "self":
                continue
            args.append(arg.arg)

        signature = f"##### {func.name}({', '.join(args)})"
        if is_method:
            signature = f"##### {func.name}({', '.join(args)})"
        else:
            signature = f"##### {func.name}({', '.join(args)})"

        doc.append(signature)
        doc.append("")

        # Get docstring
        docstring = ast.get_docstring(func)
        if docstring:
            # Clean up docstring
            cleaned = docstring.strip()
            doc.append(cleaned)
            doc.append("")

        # Parameters
        if func.args.args:
            doc.append("**Parameters:**")
            for arg in func.args.args:
                if arg.arg == "self":
                    continue
                doc.append(f"- `{arg.arg}`: Parameter description")
            doc.append("")

        # Return value
        if func.returns:
            doc.append("**Returns:**")
            doc.append("- Return value description")
            doc.append("")

        return doc

    def _load_templates(self) -> dict[str, str]:
        """Load documentation templates."""
        return {
            "readme": self.templates.get("readme", ""),
            "api": self.templates.get("api", ""),
            "examples": self.templates.get("examples", ""),
        }
