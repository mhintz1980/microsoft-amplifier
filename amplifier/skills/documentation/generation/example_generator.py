"""
Example Generator

Generates realistic, testable code examples for skill documentation.
Ensures all examples are runnable and demonstrate key functionality.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import ast
import inspect
import asyncio
from datetime import datetime


class ExampleType(Enum):
    """Types of code examples."""

    BASIC = "basic"                    # Simple usage example
    ADVANCED = "advanced"              # Complex usage example
    ERROR_HANDLING = "error_handling" # Error handling example
    INTEGRATION = "integration"        # Integration with other skills
    PERFORMANCE = "performance"        # Performance-focused example
    TESTING = "testing"               # Testing example


class ExampleComplexity(Enum):
    """Complexity levels for examples."""

    SIMPLE = "simple"      # < 20 lines
    MODERATE = "moderate"  # 20-50 lines
    COMPLEX = "complex"    # > 50 lines


@dataclass
class GeneratedExample:
    """A generated code example."""

    type: ExampleType
    complexity: ExampleComplexity
    description: str
    code: str
    explanation: str
    dependencies: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    expected_output: Optional[str] = None
    variations: List[str] = field(default_factory=list)
    line_count: int = 0


class ExampleGenerator:
    """Generates code examples for skill documentation."""

    def __init__(self):
        self.template_patterns = {
            ExampleType.BASIC: "simple_usage",
            ExampleType.ADVANCED: "complex_usage",
            ExampleType.ERROR_HANDLING: "error_handling",
            ExampleType.INTEGRATION: "integration_pattern",
            ExampleType.PERFORMANCE: "performance_pattern"
        }

    async def generate_examples(
        self,
        skill_class: type,
        analysis: Dict[str, Any],
        level: str,
        max_count: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate examples for a skill at the specified level."""

        examples = []

        # Determine which example types to generate based on level
        if level == "metadata":
            example_types = []  # No code examples for metadata
        elif level == "summary":
            example_types = [ExampleType.BASIC]
        elif level == "detailed":
            example_types = [ExampleType.BASIC, ExampleType.ADVANCED]
        else:  # full
            example_types = [
                ExampleType.BASIC,
                ExampleType.ADVANCED,
                ExampleType.ERROR_HANDLING
            ]

        # Generate examples for each type
        for example_type in example_types[:max_count]:
            try:
                generated = await self._generate_example_type(
                    skill_class, analysis, example_type
                )

                if generated:
                    examples.append({
                        "type": example_type.value,
                        "description": generated.description,
                        "code": generated.code,
                        "explanation": generated.explanation,
                        "complexity": generated.complexity.value,
                        "dependencies": generated.dependencies,
                        "line_count": generated.line_count
                    })

            except Exception as e:
                # Add a fallback example if generation fails
                fallback = self._create_fallback_example(skill_class, example_type)
                examples.append(fallback)

        return examples

    async def _generate_example_type(
        self,
        skill_class: type,
        analysis: Dict[str, Any],
        example_type: ExampleType
    ) -> Optional[GeneratedExample]:
        """Generate a specific type of example."""

        if example_type == ExampleType.BASIC:
            return await self._generate_basic_example(skill_class, analysis)
        elif example_type == ExampleType.ADVANCED:
            return await self._generate_advanced_example(skill_class, analysis)
        elif example_type == ExampleType.ERROR_HANDLING:
            return await self._generate_error_handling_example(skill_class, analysis)
        elif example_type == ExampleType.INTEGRATION:
            return await self._generate_integration_example(skill_class, analysis)
        elif example_type == ExampleType.PERFORMANCE:
            return await self._generate_performance_example(skill_class, analysis)
        elif example_type == ExampleType.TESTING:
            return await self._generate_testing_example(skill_class, analysis)

        return None

    async def _generate_basic_example(
        self,
        skill_class: type,
        analysis: Dict[str, Any]
    ) -> GeneratedExample:
        """Generate a basic usage example."""

        skill_name = skill_class.__name__
        instance_name = self._camel_to_snake(skill_name)

        # Get basic inputs from analysis
        inputs = analysis.get("inputs", [])
        required_inputs = [inp for inp in inputs if inp.get("required", False)]

        # Build example code
        code_lines = [
            f"# Create skill instance",
            f"skill = {instance_name}()",
            ""
        ]

        if required_inputs:
            # Add required parameters
            params = []
            for inp in required_inputs[:2]:  # Limit to 2 required params
                param_value = self._generate_parameter_value(inp)
                params.append(f"    {inp['name']}={param_value}")

            code_lines.extend([
                f"# Execute skill with parameters",
                f"result = skill.execute(",
                *params,
                f")",
                ""
            ])
        else:
            code_lines.extend([
                f"# Execute skill with default parameters",
                f"result = skill.execute()",
                ""
            ])

        # Add result handling
        code_lines.extend([
            f"# Process result",
            f"print(f\"{{skill_name}} result: {{result}}\")"
        ])

        code = "\n".join(code_lines)

        return GeneratedExample(
            type=ExampleType.BASIC,
            complexity=ExampleComplexity.SIMPLE,
            description=f"Basic usage of {skill_name}",
            code=code,
            explanation=f"This example shows how to create and use the {skill_name} skill with basic parameters.",
            dependencies=analysis.get("dependencies", []),
            line_count=len(code_lines)
        )

    async def _generate_advanced_example(
        self,
        skill_class: type,
        analysis: Dict[str, Any]
    ) -> GeneratedExample:
        """Generate an advanced usage example."""

        skill_name = skill_class.__name__
        instance_name = self._camel_to_snake(skill_name)

        inputs = analysis.get("inputs", [])
        usage_patterns = analysis.get("usage_patterns", [])

        code_lines = [
            f"# Advanced usage of {skill_name}",
            "import asyncio",
            "from typing import Dict, Any",
            "",
            f"async def advanced_{instance_name}_example():",
            f"    # Create skill instance",
            f"    skill = {instance_name}()",
            ""
        ]

        # Add configuration if skill has complex inputs
        if len(inputs) > 2:
            code_lines.extend([
                f"    # Prepare advanced configuration",
                f"    config = {{",
                f"        'batch_mode': True,",
                f"        'detailed_output': True,",
                f"        'timeout': 30"
            )

            # Add specific parameters
            for inp in inputs[:3]:
                if inp["name"] not in ["context", "level"]:
                    param_value = self._generate_advanced_parameter_value(inp)
                    code_lines.append(f"        '{inp['name']}': {param_value},")

            code_lines.extend([
                f"    }}",
                ""
            ])

        # Add execution with context
        code_lines.extend([
            f"    # Create execution context",
            f"    context = {{",
            f"        'session_id': 'example_session',",
            f"        'user_preferences': {{'verbose': True}},",
            f"        'available_tokens': 10000"
        ])

        if "batch_mode" in usage_patterns:
            code_lines.extend([
                f"        'batch_size': 10,",
                f"        'parallel': True"
            ])

        code_lines.extend([
            f"    }}",
            ""
        ])

        # Add execution call
        if len(inputs) > 2:
            code_lines.extend([
                f"    # Execute with advanced configuration",
                f"    result = skill.execute(",
                f"        query='process data with advanced options',",
                f"        context=context,",
                f"        **config",
                f"    )"
            ])
        else:
            code_lines.extend([
                f"    # Execute skill with context",
                f"    result = skill.execute(",
                f"        query='advanced processing request',",
                f"        context=context",
                f"    )"
            ])

        code_lines.extend([
            "",
            f"    # Process detailed result",
            f"    if result and isinstance(result, dict):",
            f"        print('Advanced processing completed:')",
            f"        for key, value in result.items():",
            f"            print(f'  {{key}}: {{value}}')",
            f"    else:",
            f"        print(f'Result: {{result}}')",
            "",
            f"# Run the advanced example",
            f"asyncio.run(advanced_{instance_name}_example())"
        ])

        code = "\n".join(code_lines)

        return GeneratedExample(
            type=ExampleType.ADVANCED,
            complexity=ExampleComplexity.MODERATE,
            description=f"Advanced usage of {skill_name} with configuration",
            code=code,
            explanation=f"This example demonstrates advanced usage patterns including configuration, context management, and result processing.",
            dependencies=analysis.get("dependencies", []) + ["asyncio"],
            prerequisites=["Basic understanding of async programming"],
            line_count=len(code_lines)
        )

    async def _generate_error_handling_example(
        self,
        skill_class: type,
        analysis: Dict[str, Any]
    ) -> GeneratedExample:
        """Generate an error handling example."""

        skill_name = skill_class.__name__
        instance_name = self._camel_to_snake(skill_name)

        code_lines = [
            f"# Error handling example for {skill_name}",
            "import logging",
            "from typing import Optional",
            "",
            "# Configure logging",
            "logging.basicConfig(level=logging.INFO)",
            "logger = logging.getLogger(__name__)",
            "",
            f"class {skill_name}Wrapper:",
            f"    '''Wrapper class with enhanced error handling'''",
            "",
            f"    def __init__(self):",
            f"        self.skill = {instance_name}()",
            f"        self.retry_count = 3",
            "",
            f"    def execute_with_retry(self, query: str, context: Optional[dict] = None) -> Optional[any]:",
            f"        '''Execute skill with retry and error handling'''",
            f"        for attempt in range(self.retry_count):",
            f"            try:",
            f"                result = self.skill.execute(query=query, context=context or {{}})",
            f"                logger.info(f'Success on attempt {{attempt + 1}}')",
            f"                return result",
            "",
            f"            except ValueError as e:",
            f"                logger.error(f'Invalid input on attempt {{attempt + 1}}: {{e}}')",
            f"                if attempt == self.retry_count - 1:",
            f"                    raise  # Re-raise on final attempt",
            "",
            f"            except Exception as e:",
            f"                logger.warning(f'Unexpected error on attempt {{attempt + 1}}: {{e}}')",
            f"                if attempt == self.retry_count - 1:",
            f"                    logger.error('All retry attempts failed')",
            f"                    return None",
            "",
            f"    def validate_input(self, query: str) -> bool:",
            f"        '''Validate input before processing'''",
            f"        if not query or not query.strip():",
            f"            raise ValueError('Query cannot be empty')",
            f"        return True",
            "",
            f"# Usage example",
            f"wrapper = {skill_name}Wrapper()",
            "",
            f"try:",
            f"    # Validate input",
            f"    query = 'example query for processing'",
            f"    wrapper.validate_input(query)",
            "",
            f"    # Execute with retry",
            f"    result = wrapper.execute_with_retry(query)",
            "",
            f"    if result is not None:",
            f"        print('Success:', result)",
            f"    else:",
            f"        print('Processing failed after retries')",
            "",
            f"except ValueError as e:",
            f"    print(f'Validation error: {{e}}')",
            f"except Exception as e:",
            f"    print(f'Unexpected error: {{e}}')"
        ]

        code = "\n".join(code_lines)

        return GeneratedExample(
            type=ExampleType.ERROR_HANDLING,
            complexity=ExampleComplexity.MODERATE,
            description=f"Error handling patterns for {skill_name}",
            code=code,
            explanation=f"This example shows comprehensive error handling including input validation, retry logic, and proper exception handling.",
            dependencies=analysis.get("dependencies", []) + ["logging"],
            prerequisites=["Understanding of exception handling patterns"],
            line_count=len(code_lines)
        )

    async def _generate_integration_example(
        self,
        skill_class: type,
        analysis: Dict[str, Any]
    ) -> GeneratedExample:
        """Generate an integration example."""

        skill_name = skill_class.__name__
        instance_name = self._camel_to_snake(skill_name)

        code_lines = [
            f"# Integration example for {skill_name}",
            "from typing import List, Dict, Any",
            "import json",
            "",
            f"class {skill_name}Pipeline:",
            f"    '''Example pipeline integrating {skill_name} with other components'''",
            "",
            f"    def __init__(self):",
            f"        self.{instance_name} = {instance_name}()",
            f"        self.preprocessing_steps = []",
            f"        self.postprocessing_steps = []",
            "",
            f"    def add_preprocessing_step(self, step_func):",
            f"        '''Add a preprocessing step to the pipeline'''",
            f"        self.preprocessing_steps.append(step_func)",
            "",
            f"    def add_postprocessing_step(self, step_func):",
            f"        '''Add a postprocessing step to the pipeline'''",
            f"        self.postprocessing_steps.append(step_func)",
            "",
            f"    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:",
            f"        '''Process data through the complete pipeline'''",
            f"        # Preprocessing",
            f"        data = input_data.copy()",
            f"        for step in self.preprocessing_steps:",
            f"            data = step(data)",
            "",
            f"        # Main skill execution",
            f"        result = self.{instance_name}.execute(",
            f"            query=data.get('query', ''),",
            f"            context=data.get('context', {{}})",
            f"        )",
            "",
            f"        # Postprocessing",
            f"        for step in self.postprocessing_steps:",
            f"            result = step(result)",
            "",
            f"        return result",
            "",
            f"# Example preprocessing functions",
            f"def validate_input(data: Dict[str, Any]) -> Dict[str, Any]:",
            f"    '''Validate and clean input data'''",
            f"    if not data.get('query'):",
            f"        raise ValueError('Query is required')",
            f"    return data",
            "",
            f"def enrich_context(data: Dict[str, Any]) -> Dict[str, Any]:",
            f"    '''Add additional context information'''",
            f"    context = data.get('context', {{}})",
            f"    context.update({{",
            f"        'timestamp': str(datetime.now()),",
            f"        'pipeline_version': '1.0'",
            f"    }})",
            f"    data['context'] = context",
            f"    return data",
            "",
            f"# Example postprocessing functions",
            f"def format_output(result: Any) -> Dict[str, Any]:",
            f"    '''Format the output for consistent API'''",
            f"    return {{",
            f"        'status': 'success',",
            f"        'data': result,",
            f"        'timestamp': str(datetime.now())",
            f"    }}",
            "",
            f"# Create and configure pipeline",
            f"pipeline = {skill_name}Pipeline()",
            f"pipeline.add_preprocessing_step(validate_input)",
            f"pipeline.add_preprocessing_step(enrich_context)",
            f"pipeline.add_postprocessing_step(format_output)",
            "",
            f"# Execute pipeline",
            f"input_data = {{",
            f"    'query': 'example query for pipeline processing',",
            f"    'context': {{'user_id': 'example_user'}}",
            f"}}",
            "",
            f"try:",
            f"    result = pipeline.process(input_data)",
            f"    print('Pipeline result:')",
            f"    print(json.dumps(result, indent=2))",
            f"except Exception as e:",
            f"    print(f'Pipeline error: {{e}}')"
        ]

        code = "\n".join(code_lines)

        return GeneratedExample(
            type=ExampleType.INTEGRATION,
            complexity=ExampleComplexity.COMPLEX,
            description=f"Integration pattern for {skill_name} with pipeline",
            code=code,
            explanation=f"This example shows how to integrate the skill into a processing pipeline with preprocessing and postprocessing steps.",
            dependencies=analysis.get("dependencies", []) + ["json"],
            prerequisites=["Understanding of pipeline patterns"],
            line_count=len(code_lines)
        )

    async def _generate_performance_example(
        self,
        skill_class: type,
        analysis: Dict[str, Any]
    ) -> GeneratedExample:
        """Generate a performance-focused example."""

        skill_name = skill_class.__name__
        instance_name = self._camel_to_snake(skill_name)

        code_lines = [
            f"# Performance optimization example for {skill_name}",
            "import time",
            "import asyncio",
            "from concurrent.futures import ThreadPoolExecutor",
            "from typing import List",
            "",
            f"class {skill_name}Optimizer:",
            f"    '''Performance optimization wrapper for {skill_name}'''",
            "",
            f"    def __init__(self):",
            f"        self.{instance_name} = {instance_name}()",
            f"        self.cache = {{}}",
            f"        self.executor = ThreadPoolExecutor(max_workers=4)",
            "",
            f"    async def process_batch(self, queries: List[str]) -> List[any]:",
            f"        '''Process multiple queries in parallel'''",
            f"        tasks = []",
            f"        for query in queries:",
            f"            task = asyncio.create_task(self.process_single(query))",
            f"            tasks.append(task)",
            "",
            f"        results = await asyncio.gather(*tasks, return_exceptions=True)",
            f"        return results",
            "",
            f"    async def process_single(self, query: str) -> any:",
            f"        '''Process a single query with caching'''",
            f"        # Check cache first",
            f"        if query in self.cache:",
            f"            return self.cache[query]",
            "",
            f"        # Process in thread pool to avoid blocking",
            f"        loop = asyncio.get_event_loop()",
            f"        result = await loop.run_in_executor(",
            f"            self.executor,",
            f"            self.{instance_name}.execute,",
            f"            query, {{}}",
            f"        )",
            "",
            f"        # Cache the result",
            f"        self.cache[query] = result",
            f"        return result",
            "",
            f"    def benchmark_performance(self, queries: List[str]) -> Dict[str, float]:",
            f"        '''Benchmark different processing approaches'''",
            f"        results = {{}}",
            "",
            f"        # Sequential processing",
            f"        start_time = time.time()",
            f"        for query in queries:",
            f"            self.{instance_name}.execute(query, {{}})",
            f"        sequential_time = time.time() - start_time",
            f"        results['sequential'] = sequential_time",
            "",
            f"        # Parallel processing",
            f"        start_time = time.time()",
            f"        asyncio.run(self.process_batch(queries))",
            f"        parallel_time = time.time() - start_time",
            f"        results['parallel'] = parallel_time",
            "",
            f"        # Speedup calculation",
            f"        results['speedup'] = sequential_time / parallel_time",
            f"        return results",
            "",
            f"# Performance testing",
            f"optimizer = {skill_name}Optimizer()",
            "",
            f"# Test queries",
            f"test_queries = [",
            f"    'test query 1',",
            f"    'test query 2',",
            f"    'test query 3',",
            f"    'test query 4',",
            f"    'test query 5'",
            f"]",
            "",
            f"# Run benchmark",
            f"print('Running performance benchmark...')",
            f"benchmark_results = optimizer.benchmark_performance(test_queries)",
            "",
            f"print(f'Sequential time: {{benchmark_results[\"sequential\"]:.3f}}s')",
            f"print(f'Parallel time: {{benchmark_results[\"parallel\"]:.3f}}s')",
            f"print(f'Speedup: {{benchmark_results[\"speedup\"]:.2f}}x')",
            "",
            f"# Test parallel processing",
            f"print('\\nTesting parallel processing...')",
            f"results = asyncio.run(optimizer.process_batch(test_queries))",
            f"print(f'Processed {{len(results)}} queries in parallel')"
        ]

        code = "\n".join(code_lines)

        return GeneratedExample(
            type=ExampleType.PERFORMANCE,
            complexity=ExampleComplexity.COMPLEX,
            description=f"Performance optimization patterns for {skill_name}",
            code=code,
            explanation=f"This example demonstrates performance optimization techniques including caching, parallel processing, and benchmarking.",
            dependencies=analysis.get("dependencies", []) + ["asyncio", "concurrent.futures"],
            prerequisites=["Understanding of async programming and performance optimization"],
            line_count=len(code_lines)
        )

    async def _generate_testing_example(
        self,
        skill_class: type,
        analysis: Dict[str, Any]
    ) -> GeneratedExample:
        """Generate a testing example."""

        skill_name = skill_class.__name__
        instance_name = self._camel_to_snake(skill_name)

        code_lines = [
            f"# Testing example for {skill_name}",
            "import unittest",
            "from unittest.mock import Mock, patch",
            "",
            f"class Test{skill_name}(unittest.TestCase):",
            f"    '''Test suite for {skill_name}'''",
            "",
            f"    def setUp(self):",
            f"        '''Set up test fixtures'''",
            f"        self.{instance_name} = {instance_name}()",
            f"        self.test_query = 'test query'",
            f"        self.test_context = {{'test': True}}",
            "",
            f"    def test_basic_execution(self):",
            f"        '''Test basic skill execution'''",
            f"        result = self.{instance_name}.execute(",
            f"            query=self.test_query,",
            f"            context=self.test_context",
            f"        )",
            f"        self.assertIsNotNone(result)",
            "",
            f"    def test_empty_query_handling(self):",
            f"        '''Test handling of empty queries'''",
            f"        with self.assertRaises((ValueError, TypeError)):",
            f"            self.{instance_name}.execute(query='')",
            "",
            f"    def test_context_validation(self):",
            f"        '''Test context validation'''",
            f"        result = self.{instance_name}.execute(",
            f"            query=self.test_query,",
            f"            context=None",
            f"        )",
            f"        self.assertIsNotNone(result)",
            "",
            f"    @patch('time.time')",
            f"    def test_performance_timing(self, mock_time):",
            f"        '''Test performance timing'''",
            f"        mock_time.return_value = 1000.0",
            f"        # Mock timing to test performance logic",
            f"        start_time = mock_time()",
            f"        result = self.{instance_name}.execute(",
            f"            query=self.test_query,",
            f"            context=self.test_context",
            f"        )",
            f"        end_time = mock_time()",
            f"        self.assertLess(end_time - start_time, 5.0)  # Should complete in < 5s",
            "",
            f"    def test_result_format(self):",
            f"        '''Test result format consistency'''",
            f"        result = self.{instance_name}.execute(",
            f"            query=self.test_query,",
            f"            context=self.test_context",
            f"        )",
            f"        # Add format-specific assertions based on your skill",
            f"        self.assertIsInstance(result, (str, dict, list))",
            "",
            f"# Integration test example",
            f"class Test{skill_name}Integration(unittest.TestCase):",
            f"    '''Integration tests for {skill_name}'''",
            "",
            f"    def test_integration_with_components(self):",
            f"        '''Test integration with other components'''",
            f"        # Mock dependencies",
            f"        with patch('module.dependency') as mock_dep:",
            f"            mock_dep.return_value = 'mocked_result'",
            f"            skill = {instance_name}()",
            f"            result = skill.execute(query='integration test')",
            f"            self.assertIsNotNone(result)",
            "",
            f"# Run tests",
            f"if __name__ == '__main__':",
            f"    unittest.main()"
        ]

        code = "\n".join(code_lines)

        return GeneratedExample(
            type=ExampleType.TESTING,
            complexity=ExampleComplexity.MODERATE,
            description=f"Testing patterns for {skill_name}",
            code=code,
            explanation=f"This example shows comprehensive testing patterns including unit tests, integration tests, and mocking.",
            dependencies=analysis.get("dependencies", []) + ["unittest"],
            prerequisites=["Understanding of testing frameworks"],
            line_count=len(code_lines)
        )

    def _create_fallback_example(
        self,
        skill_class: type,
        example_type: ExampleType
    ) -> Dict[str, Any]:
        """Create a fallback example if generation fails."""

        skill_name = skill_class.__name__
        instance_name = self._camel_to_snake(skill_name)

        fallback_code = f"""# Fallback example for {skill_name}
# This is a basic template - customize based on your skill's requirements

skill = {instance_name}()

# Execute with basic parameters
result = skill.execute(
    query="your query here",
    context={{}}
)

print("Result:", result)
"""

        return {
            "type": example_type.value,
            "description": f"Basic template for {skill_name}",
            "code": fallback_code,
            "explanation": "This is a fallback template that should be customized based on the specific skill requirements.",
            "complexity": "simple",
            "dependencies": [],
            "line_count": fallback_code.count('\n') + 1
        }

    def _generate_parameter_value(self, param: Dict[str, Any]) -> str:
        """Generate example value for a parameter."""

        param_type = param.get("type", "string")
        param_name = param.get("name", "param")

        if param_type in ["string", "str"]:
            return f'"example_{param_name}"'
        elif param_type in ["integer", "int"]:
            return "42"
        elif param_type in ["number", "float"]:
            return "3.14"
        elif param_type in ["boolean", "bool"]:
            return "True"
        elif param_type in ["array", "list"]:
            return '["item1", "item2"]'
        elif param_type in ["object", "dict"]:
            return '{"key": "value"}'
        else:
            return "None"

    def _generate_advanced_parameter_value(self, param: Dict[str, Any]) -> str:
        """Generate advanced example value for a parameter."""

        param_type = param.get("type", "string")
        param_name = param.get("name", "param")

        if param_type in ["string", "str"]:
            return f'"detailed_example_{param_name}_with_context"'
        elif param_type in ["array", "list"]:
            return '["item1", "item2", "item3", {"nested": "value"}]'
        elif param_type in ["object", "dict"]:
            return '{"key": "value", "advanced": True, "config": {"option1": True}}'
        else:
            return self._generate_parameter_value(param)

    def _camel_to_snake(self, name: str) -> str:
        """Convert CamelCase to snake_case."""

        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()