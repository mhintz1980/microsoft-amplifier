"""
Tool Evaluation Framework for Amplifier Agents

This module implements systematic tool evaluation based on Anthropic's agent-computer
interface research. Provides metrics-driven tool assessment and optimization.

Key Features:
- Performance metrics collection (accuracy, runtime, tokens, errors)
- Tool ergonomics evaluation
- Agent-computer interface optimization
- Token efficiency measurement
"""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel

from .logger import get_logger

logger = get_logger(__name__)


class ToolErgonomicsLevel(Enum):
    """Tool ergonomics classification based on agent usage patterns."""

    EXCELLENT = "excellent"  # Designed for agents, token-efficient
    GOOD = "good"  # Human-usable with minor agent improvements
    FAIR = "fair"  # Usable but requires significant agent adaptation
    POOR = "poor"  # Designed for humans, difficult for agents


@dataclass
class ToolMetrics:
    """Performance metrics for a tool execution."""

    accuracy: float  # 0.0 to 1.0
    runtime_seconds: float
    tokens_used: int
    success: bool
    error_type: str | None = None
    response_size: int = 0  # Response size in characters


@dataclass
class ToolEvaluationResult:
    """Complete evaluation result for a tool."""

    tool_name: str
    ergonomics_level: ToolErgonomicsLevel
    metrics: list[ToolMetrics]
    evaluation_date: datetime
    test_cases: list[str] = field(default_factory=list)

    @property
    def average_accuracy(self) -> float:
        """Calculate average accuracy across all test cases."""
        if not self.metrics:
            return 0.0
        return sum(m.accuracy for m in self.metrics) / len(self.metrics)

    @property
    def average_runtime(self) -> float:
        """Calculate average runtime in seconds."""
        if not self.metrics:
            return 0.0
        return sum(m.runtime_seconds for m in self.metrics) / len(self.metrics)

    @property
    def average_tokens(self) -> int:
        """Calculate average token usage."""
        if not self.metrics:
            return 0
        return sum(m.tokens_used for m in self.metrics) // len(self.metrics)

    @property
    def success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)."""
        if not self.metrics:
            return 0.0
        return sum(1 for m in self.metrics if m.success) / len(self.metrics)


class ToolTestCase(BaseModel):
    """Test case definition for tool evaluation."""

    name: str
    description: str
    input_data: dict[str, Any]
    expected_output: dict[str, Any] | None = None
    evaluation_criteria: list[str] = field(default_factory=list)
    complexity: str = "simple"  # simple, medium, complex

    class Config:
        arbitrary_types_allowed = True


class ToolEvaluator:
    """Systematic tool evaluation framework."""

    def __init__(self):
        self.results: dict[str, ToolEvaluationResult] = {}
        self.test_cases: dict[str, list[ToolTestCase]] = {}

    def add_test_cases(self, tool_name: str, cases: list[ToolTestCase]) -> None:
        """Add test cases for a specific tool."""
        self.test_cases[tool_name] = cases
        logger.info(f"Added {len(cases)} test cases for tool: {tool_name}")

    async def evaluate_tool(
        self, tool_name: str, tool_function: Callable, test_cases: list[ToolTestCase] | None = None
    ) -> ToolEvaluationResult:
        """Evaluate a tool against test cases."""
        logger.info(f"Evaluating tool: {tool_name}")

        cases_to_use = test_cases or self.test_cases.get(tool_name, [])
        if not cases_to_use:
            raise ValueError(f"No test cases found for tool: {tool_name}")

        metrics = []
        for case in cases_to_use:
            try:
                metric = await self._run_single_test(tool_function, case)
                metrics.append(metric)
                logger.debug(f"Test '{case.name}': {metric.success} ({metric.runtime_seconds:.2f}s)")
            except Exception as e:
                logger.error(f"Test '{case.name}' failed: {e}")
                metrics.append(
                    ToolMetrics(
                        accuracy=0.0, runtime_seconds=0.0, tokens_used=0, success=False, error_type=type(e).__name__
                    )
                )

        # Determine ergonomics level
        ergonomics = self._assess_ergonomics(tool_name, metrics)

        result = ToolEvaluationResult(
            tool_name=tool_name,
            ergonomics_level=ergonomics,
            metrics=metrics,
            evaluation_date=datetime.now(),
            test_cases=[case.name for case in cases_to_use],
        )

        self.results[tool_name] = result
        return result

    async def _run_single_test(self, tool_function: Callable, test_case: ToolTestCase) -> ToolMetrics:
        """Run a single test case and collect metrics."""
        start_time = time.time()
        start_tokens = self._estimate_tokens(test_case.input_data)

        try:
            # Execute the tool function
            result = await self._execute_tool(tool_function, test_case.input_data)

            # Calculate metrics
            runtime = time.time() - start_time
            tokens_used = self._estimate_tokens(result) + start_tokens

            # Evaluate accuracy
            accuracy = self._calculate_accuracy(test_case, result)

            return ToolMetrics(
                accuracy=accuracy,
                runtime_seconds=runtime,
                tokens_used=tokens_used,
                success=True,
                response_size=len(str(result)),
            )

        except Exception as e:
            runtime = time.time() - start_time
            return ToolMetrics(
                accuracy=0.0,
                runtime_seconds=runtime,
                tokens_used=start_tokens,
                success=False,
                error_type=type(e).__name__,
            )

    async def _execute_tool(self, tool_function: Callable, input_data: dict[str, Any]) -> Any:
        """Execute a tool function with the given input data."""
        if asyncio.iscoroutinefunction(tool_function):
            return await tool_function(**input_data)
        return tool_function(**input_data)

    def _estimate_tokens(self, data: Any) -> int:
        """Rough token estimation (1 token ≈ 4 characters)."""
        return len(str(data)) // 4

    def _calculate_accuracy(self, test_case: ToolTestCase, result: Any) -> float:
        """Calculate accuracy based on expected output."""
        if test_case.expected_output is None:
            # If no expected output, assume success = accuracy
            return 1.0

        # Simple comparison - can be enhanced for more complex cases
        if isinstance(test_case.expected_output, dict) and isinstance(result, dict):
            matches = sum(
                1
                for key in test_case.expected_output
                if key in result and test_case.expected_output[key] == result[key]
            )
            total = len(test_case.expected_output)
            return matches / total if total > 0 else 1.0

        return 1.0 if result == test_case.expected_output else 0.0

    def _assess_ergonomics(self, tool_name: str, metrics: list[ToolMetrics]) -> ToolErgonomicsLevel:
        """Assess tool ergonomics based on performance metrics."""
        if not metrics:
            return ToolErgonomicsLevel.POOR

        success_rate = sum(1 for m in metrics if m.success) / len(metrics)
        avg_tokens = sum(m.tokens_used for m in metrics) / len(metrics)
        avg_runtime = sum(m.runtime_seconds for m in metrics) / len(metrics)

        # Agent-optimized tools should have:
        # - High success rate (>90%)
        # - Low token usage (<1000 tokens per call)
        # - Reasonable runtime (<5 seconds)

        if success_rate > 0.9 and avg_tokens < 1000 and avg_runtime < 5:
            return ToolErgonomicsLevel.EXCELLENT
        if success_rate > 0.8 and avg_tokens < 2000 and avg_runtime < 10:
            return ToolErgonomicsLevel.GOOD
        if success_rate > 0.6 and avg_tokens < 5000:
            return ToolErgonomicsLevel.FAIR
        return ToolErgonomicsLevel.POOR

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive evaluation report."""
        if not self.results:
            return {"message": "No evaluation results available"}

        report = {
            "summary": {
                "total_tools": len(self.results),
                "evaluation_date": datetime.now().isoformat(),
                "excellent_tools": len(
                    [r for r in self.results.values() if r.ergonomics_level == ToolErgonomicsLevel.EXCELLENT]
                ),
                "good_tools": len([r for r in self.results.values() if r.ergonomics_level == ToolErgonomicsLevel.GOOD]),
                "fair_tools": len([r for r in self.results.values() if r.ergonomics_level == ToolErgonomicsLevel.FAIR]),
                "poor_tools": len([r for r in self.results.values() if r.ergonomics_level == ToolErgonomicsLevel.POOR]),
            },
            "tools": {},
        }

        for tool_name, result in self.results.items():
            report["tools"][tool_name] = {
                "ergonomics": result.ergonomics_level.value,
                "success_rate": result.success_rate,
                "average_accuracy": result.average_accuracy,
                "average_runtime": result.average_runtime,
                "average_tokens": result.average_tokens,
                "test_cases": len(result.metrics),
                "recommendations": self._generate_recommendations(result),
            }

        return report

    def _generate_recommendations(self, result: ToolEvaluationResult) -> list[str]:
        """Generate improvement recommendations for a tool."""
        recommendations = []

        if result.success_rate < 0.8:
            recommendations.append("Improve error handling and reliability")

        if result.average_tokens > 2000:
            recommendations.append("Optimize response format for token efficiency")

        if result.average_runtime > 5:
            recommendations.append("Optimize performance and reduce execution time")

        if result.average_accuracy < 0.8:
            recommendations.append("Improve output accuracy and consistency")

        if result.ergonomics_level in [ToolErgonomicsLevel.POOR, ToolErgonomicsLevel.FAIR]:
            recommendations.append("Redesign interface for agent consumption")
            recommendations.append("Consider response format enums for token efficiency")
            recommendations.append("Add natural language identifiers")

        return recommendations

    def get_top_tools(self, metric: str = "accuracy", limit: int = 5) -> list[tuple[str, float]]:
        """Get top-performing tools by specific metric."""
        if not self.results:
            return []

        tool_scores = []
        for tool_name, result in self.results.items():
            if metric == "accuracy":
                score = result.average_accuracy
            elif metric == "success_rate":
                score = result.success_rate
            elif metric == "tokens":
                score = -result.average_tokens  # Lower is better
            elif metric == "runtime":
                score = -result.average_runtime  # Lower is better
            else:
                score = result.average_accuracy

            tool_scores.append((tool_name, score))

        tool_scores.sort(key=lambda x: x[1], reverse=True)
        return tool_scores[:limit]


# Global evaluator instance
_tool_evaluator = ToolEvaluator()


def get_tool_evaluator() -> ToolEvaluator:
    """Get the global tool evaluator instance."""
    return _tool_evaluator


async def evaluate_amplifier_tools() -> dict[str, Any]:
    """Evaluate all amplifier tools and generate report."""
    evaluator = get_tool_evaluator()

    # Define test cases for common amplifier tools
    test_cases = {
        "file_reader": [
            ToolTestCase(
                name="read_simple_file",
                description="Read a simple text file",
                input_data={"file_path": "test.txt"},
                expected_output={"content": "test content"},
                complexity="simple",
            )
        ],
        "memory_store": [
            ToolTestCase(
                name="store_and_retrieve",
                description="Store and retrieve memory",
                input_data={"key": "test", "value": "data"},
                expected_output={"success": True},
                complexity="simple",
            )
        ],
    }

    # Add test cases to evaluator
    for tool_name, cases in test_cases.items():
        evaluator.add_test_cases(tool_name, cases)

    return evaluator.generate_report()
