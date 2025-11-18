"""
Skill Analyzer

Analyzes skill classes to extract documentation-relevant information
including patterns, dependencies, and usage characteristics.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import ast
import inspect
import re
from pathlib import Path


class AnalysisScope(Enum):
    """Scope of skill analysis."""

    BASIC = "basic"  # Basic interface analysis
    DETAILED = "detailed"  # Full code analysis
    COMPREHENSIVE = "comprehensive"  # Including dependencies and usage


class ComplexityLevel(Enum):
    """Complexity levels for skills."""

    SIMPLE = "simple"  # < 100 lines, straightforward logic
    MODERATE = "moderate"  # 100-500 lines, some complexity
    COMPLEX = "complex"  # 500+ lines, multiple components
    VERY_COMPLEX = "very_complex"  # 1000+ lines, highly complex


@dataclass
class AnalysisResult:
    """Result of skill analysis."""

    skill_name: str
    complexity: ComplexityLevel
    lines_of_code: int
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    suggested_tags: List[str] = field(default_factory=list)
    related_skills: List[str] = field(default_factory=list)
    usage_patterns: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    performance_characteristics: Dict[str, Any] = field(default_factory=dict)
    error_handling: List[str] = field(default_factory=list)
    integration_points: List[str] = field(default_factory=list)


class SkillAnalyzer:
    """Analyzes skill classes for documentation generation."""

    def __init__(self):
        self.type_mapping = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "list": "array",
            "dict": "object",
            "List": "array",
            "Dict": "object",
            "Optional": "optional",
            "Union": "union",
        }

    async def analyze_skill(self, skill_class: type, scope: AnalysisScope = AnalysisScope.DETAILED) -> Dict[str, Any]:
        """Comprehensive analysis of a skill class."""

        if scope == AnalysisScope.BASIC:
            return await self._basic_analysis(skill_class)
        elif scope == AnalysisScope.DETAILED:
            return await self._detailed_analysis(skill_class)
        elif scope == AnalysisScope.COMPREHENSIVE:
            return await self._comprehensive_analysis(skill_class)

        raise ValueError(f"Unknown analysis scope: {scope}")

    async def _basic_analysis(self, skill_class: type) -> Dict[str, Any]:
        """Basic interface analysis."""

        analysis = {
            "skill_name": skill_class.__name__,
            "inputs": [],
            "outputs": [],
            "description": self._extract_description(skill_class),
            "tags": getattr(skill_class, "tags", []),
            "complexity": ComplexityLevel.SIMPLE,
        }

        # Analyze execute method signature
        if hasattr(skill_class, "execute"):
            sig = inspect.signature(skill_class.execute)
            analysis["inputs"] = self._analyze_method_inputs(sig)
            analysis["outputs"] = self._analyze_method_returns(sig, skill_class)

        return analysis

    async def _detailed_analysis(self, skill_class: type) -> Dict[str, Any]:
        """Full code analysis."""

        # Start with basic analysis
        analysis = await self._basic_analysis(skill_class)

        # Get source code
        try:
            source = inspect.getsource(skill_class)
            tree = ast.parse(source)

            # Analyze source code
            code_analysis = self._analyze_source_code(tree)
            analysis.update(code_analysis)

        except Exception as e:
            analysis["source_error"] = str(e)

        return analysis

    async def _comprehensive_analysis(self, skill_class: type) -> Dict[str, Any]:
        """Including dependencies and usage patterns."""

        # Start with detailed analysis
        analysis = await self._detailed_analysis(skill_class)

        # Add dependency analysis
        dependencies = self._analyze_dependencies(skill_class)
        analysis["dependencies"] = dependencies

        # Add usage pattern analysis
        usage_patterns = self._analyze_usage_patterns(skill_class)
        analysis["usage_patterns"] = usage_patterns

        # Add suggested examples
        examples = self._generate_example_suggestions(skill_class, analysis)
        analysis["suggested_examples"] = examples

        # Add performance characteristics
        performance = self._analyze_performance_characteristics(skill_class, analysis)
        analysis["performance"] = performance

        return analysis

    def _extract_description(self, skill_class: type) -> str:
        """Extract description from skill class."""

        # Try explicit description attribute
        if hasattr(skill_class, "description"):
            return skill_class.description

        # Try docstring
        if skill_class.__doc__:
            docstring = skill_class.__doc__.strip()
            # Take first sentence
            sentences = re.split(r"[.!?]", docstring)
            if sentences:
                return sentences[0].strip()

        return "No description available"

    def _analyze_method_inputs(self, signature: inspect.Signature) -> List[Dict[str, Any]]:
        """Analyze method signature inputs."""

        inputs = []

        for param_name, param in signature.parameters.items():
            if param_name in ["self", "context", "level"]:
                continue

            input_info = {
                "name": param_name,
                "type": self._map_type_to_documentation(param.annotation),
                "required": param.default == inspect.Parameter.empty,
                "default": str(param.default) if param.default != inspect.Parameter.empty else None,
            }

            # Try to infer description from parameter name
            input_info["description"] = self._infer_parameter_description(param_name)

            inputs.append(input_info)

        return inputs

    def _analyze_method_returns(self, signature: inspect.Signature, skill_class: type) -> List[Dict[str, Any]]:
        """Analyze method return types."""

        outputs = []

        if "return" in signature.annotations:
            return_type = signature.annotations["return"]
            outputs.append(
                {
                    "name": "result",
                    "type": self._map_type_to_documentation(return_type),
                    "description": "Result of skill execution",
                }
            )

        else:
            # Try to infer from class name or common patterns
            skill_name = skill_class.__name__.lower()

            if "result" in skill_name or "output" in skill_name:
                outputs.append({"name": "result", "type": "object", "description": "Processed result"})
            elif "list" in skill_name or "items" in skill_name:
                outputs.append({"name": "items", "type": "array", "description": "List of processed items"})

        # Default output if none found
        if not outputs:
            outputs.append({"name": "result", "type": "any", "description": "Skill execution result"})

        return outputs

    def _analyze_source_code(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze AST of source code."""

        analysis = {
            "lines_of_code": 0,
            "complexity": ComplexityLevel.SIMPLE,
            "suggested_tags": [],
            "related_skills": [],
            "error_handling": [],
            "integration_points": [],
        }

        # Count lines and analyze complexity
        lines = ast.get_source_segment(open(tree.__file__, "r").read(), tree) if hasattr(tree, "__file__") else ""
        if lines:
            analysis["lines_of_code"] = len(lines.split("\n"))

            # Determine complexity
            if analysis["lines_of_code"] > 1000:
                analysis["complexity"] = ComplexityLevel.VERY_COMPLEX
            elif analysis["lines_of_code"] > 500:
                analysis["complexity"] = ComplexityLevel.COMPLEX
            elif analysis["lines_of_code"] > 100:
                analysis["complexity"] = ComplexityLevel.MODERATE

        # Analyze function calls and imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                analysis["suggested_tags"].extend(self._extract_tags_from_function_call(node))

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    analysis["integration_points"].append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    analysis["integration_points"].append(node.module)

        # Remove duplicates
        analysis["suggested_tags"] = list(set(analysis["suggested_tags"]))
        analysis["integration_points"] = list(set(analysis["integration_points"]))

        return analysis

    def _analyze_dependencies(self, skill_class: type) -> List[str]:
        """Analyze skill dependencies."""

        dependencies = []

        try:
            source = inspect.getsource(skill_class)
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module)

        except Exception:
            pass

        return dependencies

    def _analyze_usage_patterns(self, skill_class: type) -> List[str]:
        """Analyze common usage patterns."""

        patterns = []

        skill_name = skill_class.__name__.lower()

        # Infer patterns from skill name
        if "process" in skill_name:
            patterns.append("data_processing")
        if "analyze" in skill_name:
            patterns.append("data_analysis")
        if "generate" in skill_name:
            patterns.append("code_generation")
        if "transform" in skill_name:
            patterns.append("data_transformation")
        if "validate" in skill_name:
            patterns.append("validation")
        if "optimize" in skill_name:
            patterns.append("optimization")

        # Look for method names that indicate patterns
        for method_name in dir(skill_class):
            if method_name.startswith("_"):
                continue

            if "batch" in method_name:
                patterns.append("batch_processing")
            elif "stream" in method_name:
                patterns.append("stream_processing")
            elif "cache" in method_name:
                patterns.append("caching")
            elif "async" in method_name:
                patterns.append("asynchronous")

        return list(set(patterns))

    def _generate_example_suggestions(self, skill_class: type, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate suggested code examples."""

        examples = []

        # Basic usage example
        basic_example = self._create_basic_example(skill_class, analysis)
        examples.append(basic_example)

        # Add specific examples based on inputs
        inputs = analysis.get("inputs", [])
        if inputs:
            specific_example = self._create_input_specific_example(skill_class, inputs)
            examples.append(specific_example)

        # Add error handling example if errors are detected
        error_handling = analysis.get("error_handling", [])
        if error_handling:
            error_example = self._create_error_handling_example(skill_class)
            examples.append(error_example)

        return examples

    def _analyze_performance_characteristics(self, skill_class: type, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance characteristics."""

        performance = {
            "token_efficiency": "unknown",
            "memory_usage": "unknown",
            "cpu_intensive": False,
            "io_intensive": False,
            "parallelizable": False,
        }

        skill_name = skill_class.__name__.lower()
        complexity = analysis.get("complexity", ComplexityLevel.SIMPLE)

        # Infer from complexity
        if complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.VERY_COMPLEX]:
            performance["token_efficiency"] = "high"
        else:
            performance["token_efficiency"] = "low"

        # Infer from skill name and dependencies
        if any(dep in analysis.get("dependencies", []) for dep in ["pandas", "numpy", "torch"]):
            performance["cpu_intensive"] = True

        if any(dep in analysis.get("dependencies", []) for dep in ["asyncio", "aiohttp"]):
            performance["parallelizable"] = True

        if any(dep in analysis.get("dependencies", []) for dep in ["sqlite", "requests", "http"]):
            performance["io_intensive"] = True

        return performance

    def _map_type_to_documentation(self, type_hint: Any) -> str:
        """Map Python type hints to documentation-friendly types."""

        if type_hint == inspect.Parameter.empty:
            return "any"

        # Handle common types
        type_str = str(type_hint)

        # Clean up type annotations
        type_str = type_str.replace("typing.", "")
        type_str = type_str.replace("builtins.", "")

        # Map common types
        for python_type, doc_type in self.type_mapping.items():
            type_str = type_str.replace(python_type, doc_type)

        return type_str

    def _infer_parameter_description(self, param_name: str) -> str:
        """Infer parameter description from name."""

        name_lower = param_name.lower()

        if name_lower == "query":
            return "The query or request to process"
        elif name_lower == "context":
            return "Execution context information"
        elif name_lower == "level":
            return "Detail level for processing"
        elif name_lower == "data":
            return "Input data to process"
        elif name_lower == "config":
            return "Configuration options"
        elif name_lower == "options":
            return "Processing options"
        elif name_lower == "input" or name_lower == "inputs":
            return "Input parameters"
        elif name_lower == "output" or name_lower == "outputs":
            return "Output format specification"
        else:
            # Generate from parameter name
            return f"The {param_name} parameter"

    def _extract_tags_from_function_call(self, node: ast.Call) -> List[str]:
        """Extract relevant tags from function call."""

        tags = []

        if isinstance(node.func, ast.Name):
            func_name = node.func.id.lower()

            if func_name in ["open", "read", "write", "save"]:
                tags.append("file-operations")
            elif func_name in ["request", "fetch", "get", "post"]:
                tags.append("network")
            elif func_name in ["process", "transform", "analyze"]:
                tags.append("data-processing")
            elif func_name in ["generate", "create", "build"]:
                tags.append("generation")
            elif func_name in ["validate", "check", "verify"]:
                tags.append("validation")

        return tags

    def _create_basic_example(self, skill_class: type, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create basic usage example."""

        skill_name = skill_class.__name__
        instance_name = skill_name[0].lower() + skill_name[1:]

        example = {
            "description": f"Basic usage of {skill_name}",
            "code": f"""# Create skill instance
skill = {instance_name}()

# Execute with basic parameters
result = skill.execute(
    query="your query here",
    context=context
)

print(result)""",
        }

        return example

    def _create_input_specific_example(self, skill_class: type, inputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create example using specific inputs."""

        skill_name = skill_class.__name__
        instance_name = skill_name[0].lower() + skill_name[1:]

        # Build parameter string from inputs
        params = []
        for inp in inputs[:3]:  # Limit to 3 inputs
            if inp["required"]:
                if inp["type"] in ["string", "str"]:
                    params.append(f'{inp["name"]}="example"')
                elif inp["type"] in ["integer", "int"]:
                    params.append(f"{inp['name']}=1")
                elif inp["type"] in ["boolean", "bool"]:
                    params.append(f"{inp['name']}=True")
                else:
                    params.append(f"{inp['name']}=None")

        param_str = ",\n    ".join(params)

        example = {
            "description": f"Example with specific parameters for {skill_name}",
            "code": f"""# Create skill instance
skill = {instance_name}()

# Execute with specific parameters
result = skill.execute(
    {param_str}
)

# Process result
if result:
    print("Success:", result)
else:
    print("No result returned")""",
        }

        return example

    def _create_error_handling_example(self, skill_class: type) -> Dict[str, Any]:
        """Create example with error handling."""

        skill_name = skill_class.__name__
        instance_name = skill_name[0].lower() + skill_name[1:]

        example = {
            "description": f"Example with error handling for {skill_name}",
            "code": f"""# Create skill instance
skill = {instance_name}()

# Execute with error handling
try:
    result = skill.execute(
        query="your query here",
        context=context
    )

    if result:
        print("Success:", result)
    else:
        print("Empty result")

except Exception as e:
    print(f"Error executing skill: {{e}}")
    # Handle error appropriately
""",
        }

        return example
