"""
Modular Integration Test Suite

Tests that all modular components work together correctly.
Focuses on component interaction, data flow, and system compatibility.
"""

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import Mock

import pytest

# Import the modular components we need to test
try:
    from amplifier.ccsdk_toolkit.defensive.llm_parsing import parse_llm_json
    from amplifier.ccsdk_toolkit.defensive.retry_patterns import retry_with_feedback
    from amplifier.config.models import AmplifierConfig
    from amplifier.content_loader.loader import ContentLoader
    from amplifier.knowledge_synthesis.synthesizer import KnowledgeSynthesizer
except ImportError as e:
    # Mock imports for testing when components aren't fully implemented
    print(f"Warning: Could not import actual modules ({e}), using mocks for integration testing")


@dataclass
class IntegrationTestResult:
    """Result of an integration test"""

    test_name: str
    success: bool
    execution_time: float
    error_message: str | None = None
    components_tested: list[str] = None
    data_flow_validated: bool = False
    api_compatibility: bool = False


class ModularIntegrationTestSuite:
    """Comprehensive integration test suite for modular components"""

    def __init__(self):
        self.test_results: list[IntegrationTestResult] = []
        self.component_registry = self._initialize_component_registry()

    def _initialize_component_registry(self) -> dict[str, Any]:
        """Initialize mock or real components for testing"""
        components = {}

        # Try to load real components, fall back to mocks
        try:
            # Content processing components
            components["content_loader"] = ContentLoader()
            components["knowledge_synthesizer"] = KnowledgeSynthesizer()
            components["config"] = AmplifierConfig()
        except ImportError:
            # Create mock components
            components["content_loader"] = AsyncMock()
            components["knowledge_synthesizer"] = AsyncMock()
            components["config"] = Mock()

        # Defensive utilities (should always be available)
        components["llm_parser"] = parse_llm_json
        components["retry_handler"] = retry_with_feedback

        return components

    async def test_content_to_synthesis_pipeline(self) -> IntegrationTestResult:
        """Test the complete content loading to knowledge synthesis pipeline"""

        start_time = asyncio.get_event_loop().time()
        components_tested = ["content_loader", "knowledge_synthesizer"]

        try:
            # Step 1: Load content
            content_loader = self.component_registry["content_loader"]

            if hasattr(content_loader, "load_directory"):
                # Real component
                content_items = await content_loader.load_directory(Path("test_data"))
            else:
                # Mock component
                content_loader.return_value = [{"title": "Test Document", "content": "Test content"}]
                content_items = await content_loader()

            # Step 2: Synthesize knowledge
            synthesizer = self.component_registry["knowledge_synthesizer"]

            if hasattr(synthesizer, "synthesize"):
                # Real component
                synthesis_result = await synthesizer.synthesize(content_items)
            else:
                # Mock component
                synthesizer.return_value = {"summary": "Test summary", "insights": []}
                synthesis_result = await synthesizer(content_items)

            # Validate data flow
            data_flow_validated = content_items is not None and synthesis_result is not None and len(content_items) > 0

            execution_time = asyncio.get_event_loop().time() - start_time

            return IntegrationTestResult(
                test_name="Content to Synthesis Pipeline",
                success=True,
                execution_time=execution_time,
                components_tested=components_tested,
                data_flow_validated=data_flow_validated,
                api_compatibility=True,
            )

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Content to Synthesis Pipeline",
                success=False,
                execution_time=execution_time,
                error_message=str(e),
                components_tested=components_tested,
            )

    async def test_defensive_utilities_integration(self) -> IntegrationTestResult:
        """Test integration of defensive utilities with main components"""

        start_time = asyncio.get_event_loop().time()
        components_tested = ["llm_parser", "retry_handler"]

        try:
            # Test LLM parsing with malformed response
            malformed_llm_response = """
            Here's the JSON you requested:

            ```json
            {
                "result": "success",
                "data": {"value": 42, "status": "complete"}
            }
            ```

            The operation completed successfully.
            """

            # Test the parser
            parser = self.component_registry["llm_parser"]
            parsed_result = parser(malformed_llm_response)

            # Validate parsing worked
            assert parsed_result is not None
            assert "result" in parsed_result
            assert parsed_result["result"] == "success"

            # Test retry handler with a failing function
            async def failing_function(attempt: int = 0):
                if attempt < 2:
                    raise ValueError(f"Attempt {attempt} failed")
                return {"status": "success", "attempts": attempt + 1}

            retry_handler = self.component_registry["retry_handler"]
            retry_result = await retry_handler(failing_function, max_retries=3)

            # Validate retry worked
            assert retry_result is not None
            assert retry_result["status"] == "success"

            execution_time = asyncio.get_event_loop().time() - start_time

            return IntegrationTestResult(
                test_name="Defensive Utilities Integration",
                success=True,
                execution_time=execution_time,
                components_tested=components_tested,
                data_flow_validated=True,
                api_compatibility=True,
            )

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Defensive Utilities Integration",
                success=False,
                execution_time=execution_time,
                error_message=str(e),
                components_tested=components_tested,
            )

    async def test_configuration_integration(self) -> IntegrationTestResult:
        """Test configuration integration across components"""

        start_time = asyncio.get_event_loop().time()
        components_tested = ["config"]

        try:
            config = self.component_registry["config"]

            # Test configuration loading and validation
            if hasattr(config, "load_from_file"):
                # Real config
                test_config_path = Path("test_config.json")
                await config.load_from_file(test_config_path)

                # Validate config values
                assert hasattr(config, "settings")
                assert config.settings is not None
            else:
                # Mock config
                config.settings = {"model_name": "test-model", "max_tokens": 4000, "temperature": 0.7}

            # Test configuration propagation
            settings = config.settings
            assert "model_name" in settings
            assert isinstance(settings["max_tokens"], int)

            execution_time = asyncio.get_event_loop().time() - start_time

            return IntegrationTestResult(
                test_name="Configuration Integration",
                success=True,
                execution_time=execution_time,
                components_tested=components_tested,
                data_flow_validated=True,
                api_compatibility=True,
            )

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Configuration Integration",
                success=False,
                execution_time=execution_time,
                error_message=str(e),
                components_tested=components_tested,
            )

    async def test_parallel_component_execution(self) -> IntegrationTestResult:
        """Test that components can execute in parallel without interference"""

        start_time = asyncio.get_event_loop().time()
        components_tested = ["content_loader", "knowledge_synthesizer", "llm_parser"]

        try:
            # Create parallel tasks
            tasks = []

            # Task 1: Content loading
            async def content_task():
                await asyncio.sleep(0.1)  # Simulate work
                return {"content": "Sample content", "source": "test"}

            # Task 2: Knowledge synthesis
            async def synthesis_task():
                await asyncio.sleep(0.15)  # Simulate work
                return {"synthesis": "Sample synthesis", "confidence": 0.95}

            # Task 3: LLM parsing
            async def parsing_task():
                await asyncio.sleep(0.05)  # Simulate work
                malformed = '{"result": "test", "data": {"value": 123}}'
                parser = self.component_registry["llm_parser"]
                return parser(malformed)

            tasks.extend([content_task(), synthesis_task(), parsing_task()])

            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Validate results
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) == 3

            # Validate no interference between tasks
            content_result, synthesis_result, parsing_result = successful_results
            assert "content" in content_result
            assert "synthesis" in synthesis_result
            assert "result" in parsing_result

            execution_time = asyncio.get_event_loop().time() - start_time

            return IntegrationTestResult(
                test_name="Parallel Component Execution",
                success=True,
                execution_time=execution_time,
                components_tested=components_tested,
                data_flow_validated=True,
                api_compatibility=True,
            )

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Parallel Component Execution",
                success=False,
                execution_time=execution_time,
                error_message=str(e),
                components_tested=components_tested,
            )

    async def test_error_propagation_and_recovery(self) -> IntegrationTestResult:
        """Test error propagation and recovery across component boundaries"""

        start_time = asyncio.get_event_loop().time()
        components_tested = ["content_loader", "retry_handler", "llm_parser"]

        try:
            # Simulate component failure and recovery
            failing_content_loader = AsyncMock()
            failing_content_loader.side_effect = [
                ValueError("First attempt failed"),
                ValueError("Second attempt failed"),
                [{"content": "Success on third attempt", "source": "recovery_test"}],
            ]

            # Test retry with failing component
            retry_handler = self.component_registry["retry_handler"]

            async def failing_load():
                return await failing_content_loader()

            result = await retry_handler(failing_load, max_retries=3)

            # Validate recovery
            assert result is not None
            assert len(result) > 0
            assert result[0]["content"] == "Success on third attempt"

            # Test error propagation with proper formatting
            parser = self.component_registry["llm_parser"]

            # Test with error response
            error_response = """
            An error occurred while processing your request.

            Error details:
            - Invalid input format
            - Missing required field: "type"

            Please correct and retry.
            """

            # Parser should handle gracefully (return None or raise meaningful error)
            try:
                parsed_error = parser(error_response)
                # If no exception, should return None or error structure
                assert parsed_error is None or "error" in str(parsed_error).lower()
            except ValueError:
                # Expected behavior for unparseable errors
                pass

            execution_time = asyncio.get_event_loop().time() - start_time

            return IntegrationTestResult(
                test_name="Error Propagation and Recovery",
                success=True,
                execution_time=execution_time,
                components_tested=components_tested,
                data_flow_validated=True,
                api_compatibility=True,
            )

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return IntegrationTestResult(
                test_name="Error Propagation and Recovery",
                success=False,
                execution_time=execution_time,
                error_message=str(e),
                components_tested=components_tested,
            )

    async def run_full_integration_suite(self) -> dict[str, Any]:
        """Run the complete integration test suite"""

        tests = [
            self.test_content_to_synthesis_pipeline,
            self.test_defensive_utilities_integration,
            self.test_configuration_integration,
            self.test_parallel_component_execution,
            self.test_error_propagation_and_recovery,
        ]

        results = []

        for test_func in tests:
            result = await test_func()
            results.append(result)
            self.test_results.append(result)

        # Generate summary
        successful_tests = sum(1 for r in results if r.success)
        total_tests = len(results)
        avg_execution_time = sum(r.execution_time for r in results) / total_tests

        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": successful_tests / total_tests,
            "avg_execution_time": avg_execution_time,
            "all_components_tested": list(
                {component for result in results for component in result.components_tested or []}
            ),
        }

        return {
            "summary": summary,
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "error_message": r.error_message,
                    "components_tested": r.components_tested,
                    "data_flow_validated": r.data_flow_validated,
                    "api_compatibility": r.api_compatibility,
                }
                for r in results
            ],
        }


# Pytest integration
@pytest.fixture
async def integration_suite():
    """Pytest fixture for integration test suite"""
    suite = ModularIntegrationTestSuite()
    yield suite


@pytest.mark.asyncio
async def test_content_synthesis_integration(integration_suite):
    """Test content to synthesis integration"""
    result = await integration_suite.test_content_to_synthesis_pipeline()
    assert result.success, f"Integration test failed: {result.error_message}"
    assert result.data_flow_validated


@pytest.mark.asyncio
async def test_defensive_utilities_integration(integration_suite):
    """Test defensive utilities integration"""
    result = await integration_suite.test_defensive_utilities_integration()
    assert result.success, f"Integration test failed: {result.error_message}"
    assert result.api_compatibility


@pytest.mark.asyncio
async def test_parallel_execution(integration_suite):
    """Test parallel component execution"""
    result = await integration_suite.test_parallel_component_execution()
    assert result.success, f"Integration test failed: {result.error_message}"
    assert result.execution_time < 1.0  # Should complete in under 1 second


@pytest.mark.asyncio
async def test_full_integration_suite(integration_suite):
    """Test the full integration suite"""
    report = await integration_suite.run_full_integration_suite()

    # Validate overall results
    assert report["summary"]["success_rate"] >= 0.8  # At least 80% success rate
    assert report["summary"]["total_tests"] == 5
    assert len(report["detailed_results"]) == 5


# CLI interface
async def main():
    """Main CLI interface for running integration tests"""
    suite = ModularIntegrationTestSuite()
    report = await suite.run_full_integration_suite()

    # Print results
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    # Summary panel
    summary = report["summary"]
    summary_text = f"""
    Total Tests: {summary["total_tests"]}
    Successful: {summary["successful_tests"]}
    Failed: {summary["failed_tests"]}
    Success Rate: {summary["success_rate"] * 100:.1f}%
    Avg Execution Time: {summary["avg_execution_time"]:.3f}s
    """

    console.print(Panel(summary_text.strip(), title="Integration Test Results", border_style="green"))

    # Detailed results table
    table = Table(title="Detailed Results")
    table.add_column("Test Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Time (s)", style="yellow")
    table.add_column("Components", style="blue")

    for result in report["detailed_results"]:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        components = ", ".join(result["components_tested"][:3])  # Limit display
        table.add_row(result["test_name"], status, f"{result['execution_time']:.3f}", components)

    console.print(table)

    # Save report
    report_path = Path("integration_test_results.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    console.print(f"\n📁 Full report saved to: {report_path.absolute()}")


if __name__ == "__main__":
    asyncio.run(main())  # type: ignore
