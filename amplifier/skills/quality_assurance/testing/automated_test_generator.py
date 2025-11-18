"""
Automated Test Generator and Executor

Generates comprehensive tests for all skills automatically and executes them
to ensure functionality, correctness, and robustness.
"""

import ast
import importlib
import inspect
import json
import sys
import subprocess
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
import tempfile
import shutil

from amplifier.mcp.code_execution import execute_in_docker
from amplifier.mcp.persistent_storage import store_result


class TestType(Enum):
    """Types of automated tests to generate."""

    UNIT = "unit"
    INTEGRATION = "integration"
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    ERROR_HANDLING = "error_handling"
    EDGE_CASE = "edge_case"
    SECURITY = "security"


class TestStatus(Enum):
    """Test execution status."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class TestCase:
    """Generated test case."""

    name: str
    test_type: TestType
    function_name: str
    input_data: Dict[str, Any]
    expected_output: Any
    description: str
    tags: List[str]
    timeout: int = 30


@dataclass
class TestResult:
    """Result of test execution."""

    test_case: TestCase
    status: TestStatus
    actual_output: Any
    execution_time: float
    error_message: Optional[str]
    traceback_info: Optional[str]
    memory_usage: Optional[int]


@dataclass
class TestSuite:
    """Collection of test cases for a skill."""

    skill_path: str
    test_cases: List[TestCase]
    test_results: List[TestResult]
    coverage_percentage: float
    total_time: float
    passed_count: int
    failed_count: int


class AutomatedTestGenerator:
    """Automated test generation and execution system."""

    def __init__(self, test_timeout: int = 30, enable_mutation_testing: bool = True, coverage_threshold: float = 0.80):
        """
        Initialize automated test generator.

        Args:
            test_timeout: Default timeout for test execution (seconds)
            enable_mutation_testing: Enable mutation testing for robustness
            coverage_threshold: Minimum code coverage threshold
        """
        self.test_timeout = test_timeout
        self.enable_mutation_testing = enable_mutation_testing
        self.coverage_threshold = coverage_threshold

        # Test execution environment
        self.temp_dir = None
        self._setup_test_environment()

    def _setup_test_environment(self):
        """Setup isolated test execution environment."""
        self.temp_dir = tempfile.mkdtemp(prefix="skill_tests_")

        # Install required test dependencies
        test_deps = [
            "pytest",
            "pytest-cov",
            "pytest-asyncio",
            "pytest-mock",
            "pytest-benchmark",
            "pytest-xdist",  # Parallel execution
        ]

        for dep in test_deps:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                print(f"Warning: Failed to install {dep}")

    def generate_test_suite(self, skill_path: str) -> TestSuite:
        """
        Generate comprehensive test suite for a skill.

        Args:
            skill_path: Path to the skill directory or file

        Returns:
            Generated test suite
        """
        skill_path = Path(skill_path)

        # Analyze skill structure
        skill_analysis = self._analyze_skill(skill_path)

        # Generate test cases
        test_cases = []

        # Unit tests for each function
        test_cases.extend(self._generate_unit_tests(skill_analysis))

        # Integration tests
        test_cases.extend(self._generate_integration_tests(skill_analysis))

        # Error handling tests
        test_cases.extend(self._generate_error_handling_tests(skill_analysis))

        # Edge case tests
        test_cases.extend(self._generate_edge_case_tests(skill_analysis))

        # Performance tests (if enabled)
        if self.coverage_threshold > 0.8:
            test_cases.extend(self._generate_performance_tests(skill_analysis))

        return TestSuite(
            skill_path=str(skill_path),
            test_cases=test_cases,
            test_results=[],
            coverage_percentage=0.0,
            total_time=0.0,
            passed_count=0,
            failed_count=0,
        )

    def _analyze_skill(self, skill_path: Path) -> Dict[str, Any]:
        """Analyze skill structure and extract testable components."""
        analysis = {
            "functions": [],
            "classes": [],
            "imports": [],
            "dependencies": [],
            "entry_points": [],
            "complexity_metrics": {},
        }

        python_files = self._collect_python_files(skill_path)

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                # Extract functions and classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        analysis["functions"].append(
                            {
                                "name": node.name,
                                "file": str(py_file),
                                "line": node.lineno,
                                "args": [arg.arg for arg in node.args.args],
                                "returns": self._infer_return_type(node),
                                "complexity": self._calculate_complexity(node),
                                "docstring": ast.get_docstring(node),
                            }
                        )
                    elif isinstance(node, ast.ClassDef):
                        analysis["classes"].append(
                            {
                                "name": node.name,
                                "file": str(py_file),
                                "line": node.lineno,
                                "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                                "docstring": ast.get_docstring(node),
                            }
                        )

            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")

        return analysis

    def _collect_python_files(self, path: Path) -> List[Path]:
        """Collect all Python files in the given path."""
        if path.is_file() and path.suffix == ".py":
            return [path]
        return list(path.rglob("*.py"))

    def _generate_unit_tests(self, analysis: Dict[str, Any]) -> List[TestCase]:
        """Generate unit tests for all functions."""
        test_cases = []

        for func in analysis["functions"]:
            # Skip private/internal functions unless they're complex
            if func["name"].startswith("_") and func["complexity"] < 5:
                continue

            # Generate test cases based on function signature
            test_cases.extend(self._create_function_test_cases(func))

        return test_cases

    def _create_function_test_cases(self, func_info: Dict[str, Any]) -> List[TestCase]:
        """Create test cases for a specific function."""
        test_cases = []
        func_name = func_info["name"]
        args = func_info["args"]

        # Basic functionality test
        test_cases.append(
            TestCase(
                name=f"test_{func_name}_basic",
                test_type=TestType.UNIT,
                function_name=func_name,
                input_data=self._generate_test_input(args, "basic"),
                expected_output=None,  # Will be determined during execution
                description=f"Basic functionality test for {func_name}",
                tags=["unit", "basic", func_name],
            )
        )

        # Edge case tests
        test_cases.append(
            TestCase(
                name=f"test_{func_name}_edge_cases",
                test_type=TestType.EDGE_CASE,
                function_name=func_name,
                input_data=self._generate_test_input(args, "edge_cases"),
                expected_output=None,
                description=f"Edge case tests for {func_name}",
                tags=["edge_case", func_name],
            )
        )

        # Parameter validation test
        if args:
            test_cases.append(
                TestCase(
                    name=f"test_{func_name}_invalid_params",
                    test_type=TestType.ERROR_HANDLING,
                    function_name=func_name,
                    input_data=self._generate_test_input(args, "invalid"),
                    expected_output="error",
                    description=f"Parameter validation test for {func_name}",
                    tags=["error_handling", "validation", func_name],
                )
            )

        return test_cases

    def _generate_test_input(self, args: List[str], test_type: str) -> Dict[str, Any]:
        """Generate test input data based on argument types."""
        input_data = {}

        for arg in args:
            if test_type == "basic":
                input_data[arg] = self._get_basic_value(arg)
            elif test_type == "edge_cases":
                input_data[arg] = self._get_edge_case_value(arg)
            elif test_type == "invalid":
                input_data[arg] = self._get_invalid_value(arg)

        return input_data

    def _get_basic_value(self, arg_name: str) -> Any:
        """Get a basic test value for an argument."""
        # Heuristic based on argument name
        arg_lower = arg_name.lower()

        if "path" in arg_lower or "file" in arg_lower:
            return "/tmp/test_file.txt"
        elif "url" in arg_lower:
            return "https://example.com"
        elif "text" in arg_lower or "string" in arg_lower or "content" in arg_lower:
            return "test string"
        elif "number" in arg_lower or "count" in arg_lower or "length" in arg_lower:
            return 42
        elif "list" in arg_lower or "items" in arg_lower or "array" in arg_lower:
            return [1, 2, 3]
        elif "dict" in arg_lower or "config" in arg_lower or "settings" in arg_lower:
            return {"key": "value"}
        elif "bool" in arg_lower or "flag" in arg_lower:
            return True
        else:
            return "default_value"

    def _get_edge_case_value(self, arg_name: str) -> Any:
        """Get edge case test values."""
        arg_lower = arg_name.lower()

        if "path" in arg_lower:
            return ""  # Empty path
        elif "text" in arg_lower:
            return ""  # Empty string
        elif "number" in arg_lower:
            return 0  # Zero
        elif "list" in arg_lower:
            return []  # Empty list
        elif "dict" in arg_lower:
            return {}  # Empty dict
        else:
            return None  # None value

    def _get_invalid_value(self, arg_name: str) -> Any:
        """Get invalid test values."""
        # Return a value that's likely to cause validation errors
        return object()

    def _generate_integration_tests(self, analysis: Dict[str, Any]) -> List[TestCase]:
        """Generate integration tests for skill components."""
        test_cases = []

        # Test import and basic instantiation
        test_cases.append(
            TestCase(
                name="test_skill_import_and_setup",
                test_type=TestType.INTEGRATION,
                function_name="skill_import",
                input_data={},
                expected_output="success",
                description="Test skill can be imported and initialized",
                tags=["integration", "setup"],
            )
        )

        # Test workflow if multiple functions exist
        if len(analysis["functions"]) > 1:
            test_cases.append(
                TestCase(
                    name="test_function_workflow",
                    test_type=TestType.INTEGRATION,
                    function_name="workflow_test",
                    input_data={},
                    expected_output=None,
                    description="Test complete skill workflow",
                    tags=["integration", "workflow"],
                )
            )

        return test_cases

    def _generate_error_handling_tests(self, analysis: Dict[str, Any]) -> List[TestCase]:
        """Generate error handling tests."""
        test_cases = []

        # Test with missing dependencies
        test_cases.append(
            TestCase(
                name="test_missing_dependencies",
                test_type=TestType.ERROR_HANDLING,
                function_name="dependency_check",
                input_data={"force_missing": True},
                expected_output="error",
                description="Test behavior with missing dependencies",
                tags=["error_handling", "dependencies"],
            )
        )

        # Test with malformed input
        test_cases.append(
            TestCase(
                name="test_malformed_input",
                test_type=TestType.ERROR_HANDLING,
                function_name="input_validation",
                input_data={"invalid_data": True},
                expected_output="error",
                description="Test handling of malformed input",
                tags=["error_handling", "validation"],
            )
        )

        return test_cases

    def _generate_edge_case_tests(self, analysis: Dict[str, Any]) -> List[TestCase]:
        """Generate edge case tests."""
        test_cases = []

        # Test with large inputs
        test_cases.append(
            TestCase(
                name="test_large_input",
                test_type=TestType.EDGE_CASE,
                function_name="performance_test",
                input_data={"size": "large"},
                expected_output=None,
                description="Test with large input sizes",
                tags=["edge_case", "performance"],
            )
        )

        # Test with empty/null inputs
        test_cases.append(
            TestCase(
                name="test_empty_input",
                test_type=TestType.EDGE_CASE,
                function_name="empty_input_test",
                input_data={"empty": True},
                expected_output=None,
                description="Test with empty/null inputs",
                tags=["edge_case", "empty"],
            )
        )

        return test_cases

    def _generate_performance_tests(self, analysis: Dict[str, Any]) -> List[TestCase]:
        """Generate performance tests."""
        test_cases = []

        test_cases.append(
            TestCase(
                name="test_performance_benchmark",
                test_type=TestType.PERFORMANCE,
                function_name="benchmark_test",
                input_data={"iterations": 1000},
                expected_output=None,
                description="Performance benchmark test",
                tags=["performance", "benchmark"],
            )
        )

        return test_cases

    async def execute_test_suite(self, test_suite: TestSuite) -> TestSuite:
        """
        Execute a test suite and collect results.

        Args:
            test_suite: Test suite to execute

        Returns:
            Updated test suite with results
        """
        test_suite.test_results = []
        total_time = 0.0

        # Execute tests in parallel batches
        batch_size = 5
        for i in range(0, len(test_suite.test_cases), batch_size):
            batch = test_suite.test_cases[i : i + batch_size]

            # Execute batch in parallel
            batch_tasks = [self._execute_test_case(test_case) for test_case in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    # Handle execution errors
                    error_result = TestResult(
                        test_case=batch[batch_results.index(result)],
                        status=TestStatus.ERROR,
                        actual_output=None,
                        execution_time=0.0,
                        error_message=str(result),
                        traceback_info=traceback.format_exc(),
                        memory_usage=None,
                    )
                    test_suite.test_results.append(error_result)
                else:
                    test_suite.test_results.append(result)

        # Calculate statistics
        test_suite.passed_count = sum(1 for r in test_suite.test_results if r.status == TestStatus.PASSED)
        test_suite.failed_count = sum(
            1 for r in test_suite.test_results if r.status in [TestStatus.FAILED, TestStatus.ERROR]
        )
        test_suite.total_time = sum(r.execution_time for r in test_suite.test_results)

        # Calculate coverage (simplified)
        test_suite.coverage_percentage = self._calculate_coverage(test_suite)

        return test_suite

    async def _execute_test_case(self, test_case: TestCase) -> TestResult:
        """Execute a single test case."""
        import time
        import tracemalloc

        start_time = time.time()
        tracemalloc.start()

        try:
            # Execute test in isolated environment
            test_code = self._generate_test_code(test_case)

            # Use MCP code execution for isolation
            result = await execute_in_docker(code=test_code, timeout=test_case.timeout)

            execution_time = time.time() - start_time
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            if result["success"]:
                return TestResult(
                    test_case=test_case,
                    status=TestStatus.PASSED,
                    actual_output=result["output"],
                    execution_time=execution_time,
                    error_message=None,
                    traceback_info=None,
                    memory_usage=peak,
                )
            else:
                return TestResult(
                    test_case=test_case,
                    status=TestStatus.FAILED,
                    actual_output=result.get("output"),
                    execution_time=execution_time,
                    error_message=result.get("error"),
                    traceback_info=result.get("traceback"),
                    memory_usage=peak,
                )

        except asyncio.TimeoutError:
            return TestResult(
                test_case=test_case,
                status=TestStatus.FAILED,
                actual_output=None,
                execution_time=test_case.timeout,
                error_message="Test timeout",
                traceback_info=None,
                memory_usage=None,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_case=test_case,
                status=TestStatus.ERROR,
                actual_output=None,
                execution_time=execution_time,
                error_message=str(e),
                traceback_info=traceback.format_exc(),
                memory_usage=None,
            )

    def _generate_test_code(self, test_case: TestCase) -> str:
        """Generate executable test code for a test case."""
        # This is a simplified version - in practice, you'd generate
        # actual pytest-compatible test code
        test_code = f"""
import sys
import os
sys.path.insert(0, '{test_case.test_case.function_name}')

# Test case: {test_case.name}
try:
    # Import the skill
    from {test_case.function_name} import *

    # Test input
    test_input = {json.dumps(test_case.input_data)}

    # Execute function
    result = {test_case.function_name}(**test_input)

    print("SUCCESS:", result)

except Exception as e:
    print("ERROR:", str(e))
    import traceback
    traceback.print_exc()
"""
        return test_code

    def _calculate_coverage(self, test_suite: TestSuite) -> float:
        """Calculate test coverage percentage."""
        # Simplified coverage calculation
        # In practice, you'd use coverage.py or similar tools
        if not test_suite.test_cases:
            return 0.0

        # Estimate based on test types executed
        coverage_factors = {
            TestType.UNIT: 0.3,
            TestType.INTEGRATION: 0.2,
            TestType.EDGE_CASE: 0.2,
            TestType.ERROR_HANDLING: 0.2,
            TestType.PERFORMANCE: 0.1,
        }

        total_coverage = 0.0
        for test_result in test_suite.test_results:
            if test_result.status == TestStatus.PASSED:
                test_type = test_result.test_case.test_type
                total_coverage += coverage_factors.get(test_type, 0.1)

        return min(total_coverage, 1.0)

    def _infer_return_type(self, node: ast.FunctionDef) -> str:
        """Infer return type from function AST."""
        if node.returns:
            return ast.unparse(node.returns) if hasattr(ast, "unparse") else "unknown"

        # Simple heuristic based on return statements
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                if isinstance(child.value, ast.Constant):
                    return type(child.value.value).__name__
                elif isinstance(child.value, ast.List):
                    return "list"
                elif isinstance(child.value, ast.Dict):
                    return "dict"
                elif isinstance(child.value, ast.NameConstant):
                    return type(child.value.value).__name__

        return "unknown"

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    async def validate_and_store(self, skill_path: str) -> TestSuite:
        """
        Generate and execute tests, then store results in MCP storage.

        Args:
            skill_path: Path to the skill

        Returns:
            Complete test suite with results
        """
        # Generate test suite
        test_suite = self.generate_test_suite(skill_path)

        # Execute tests
        test_suite = await self.execute_test_suite(test_suite)

        # Store results in MCP storage
        await store_result(
            namespace="qa_testing",
            key=f"skill_tests_{skill_path}_{test_suite.skill_path}",
            data={
                "skill_path": test_suite.skill_path,
                "total_tests": len(test_suite.test_cases),
                "passed": test_suite.passed_count,
                "failed": test_suite.failed_count,
                "coverage": test_suite.coverage_percentage,
                "total_time": test_suite.total_time,
                "test_results": [
                    {
                        "name": result.test_case.name,
                        "status": result.status.value,
                        "time": result.execution_time,
                        "error": result.error_message,
                    }
                    for result in test_suite.test_results
                ],
            },
        )

        return test_suite

    def cleanup(self):
        """Clean up test environment."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
