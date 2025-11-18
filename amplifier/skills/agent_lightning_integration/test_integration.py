"""
Test script for Agent Lightning Integration System

Comprehensive testing of all integration components to ensure
they work together correctly with the existing skill pipeline.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from amplifier.skills.agent_lightning_integration import (
    AgentLightningIntegrationManager,
    AgentLightningIntegrationConfig,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class IntegrationTester:
    """Test suite for Agent Lightning integration"""

    def __init__(self):
        self.config = AgentLightningIntegrationConfig()
        self.integration_manager = None
        self.test_results = []

    async def run_all_tests(self):
        """Run all integration tests"""
        logger.info("Starting Agent Lightning Integration Tests")
        logger.info("=" * 60)

        try:
            # Initialize integration manager
            await self.setup_integration()

            # Run component tests
            await self.test_performance_tracking()
            await self.test_error_detection()
            await self.test_optimization()
            await self.test_quality_gates()
            await self.test_knowledge_transfer()
            await self.test_storage_integration()
            await self.test_monitoring()
            await self.test_end_to_end_flow()

            # Generate test report
            await self.generate_test_report()

        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            raise
        finally:
            await self.cleanup()

    async def setup_integration(self):
        """Initialize the integration system"""
        logger.info("Setting up integration system...")

        self.integration_manager = AgentLightningIntegrationManager()
        await self.integration_manager.start()

        # Wait for components to initialize
        await asyncio.sleep(2)

        logger.info("✅ Integration system initialized successfully")
        self.test_results.append(("Setup", "PASS", "Integration system initialized"))

    async def test_performance_tracking(self):
        """Test skill performance tracking"""
        logger.info("Testing performance tracking...")

        try:
            # Simulate skill execution
            execution_data = {
                "skill_id": "test_skill_001",
                "skill_name": "Test Skill",
                "execution_id": "exec_test_001",
                "execution_time": 2.5,
                "success": True,
                "accuracy_score": 0.92,
                "user_satisfaction": 0.88,
                "hallucination_detected": False,
                "hallucination_score": 0.05,
                "memory_usage_mb": 128.5,
                "cpu_usage_percent": 45.2,
                "tokens_used": 850,
                "context_size_tokens": 1200,
                "response_size_tokens": 650,
            }

            result = await self.integration_manager.process_skill_execution(execution_data)

            assert result["execution_successful"], "Execution should be successful"
            assert result["performance_metrics"]["accuracy_score"] == 0.92, "Accuracy score mismatch"
            assert result["performance_metrics"]["execution_time"] == 2.5, "Execution time mismatch"

            logger.info("✅ Performance tracking test passed")
            self.test_results.append(("Performance Tracking", "PASS", "All checks passed"))

        except Exception as e:
            logger.error(f"❌ Performance tracking test failed: {e}")
            self.test_results.append(("Performance Tracking", "FAIL", str(e)))

    async def test_error_detection(self):
        """Test error detection engine"""
        logger.info("Testing error detection...")

        try:
            # Simulate execution with errors
            execution_data = {
                "skill_id": "test_skill_002",
                "skill_name": "Test Skill with Errors",
                "execution_id": "exec_test_002",
                "execution_time": 15.0,  # Slow execution
                "success": False,
                "error_type": "ValueError",
                "error_message": "Invalid input parameter",
                "accuracy_score": 0.0,
                "code": """
def process_data(data):
    # Potential division by zero
    result = 100 / len(data)
    return result
""",
            }

            result = await self.integration_manager.process_skill_execution(execution_data)

            assert not result["execution_successful"], "Execution should fail"
            assert result["error_detection"]["errors_found"] > 0, "Should detect errors"
            assert result["error_detection"]["risk_score"] > 0.5, "Should have elevated risk score"

            logger.info("✅ Error detection test passed")
            self.test_results.append(("Error Detection", "PASS", "Errors detected correctly"))

        except Exception as e:
            logger.error(f"❌ Error detection test failed: {e}")
            self.test_results.append(("Error Detection", "FAIL", str(e)))

    async def test_optimization(self):
        """Test continuous optimization"""
        logger.info("Testing optimization system...")

        try:
            # Get optimization recommendations
            result = await self.integration_manager.optimize_skill("test_skill_001")

            assert result["skill_id"] == "test_skill_001", "Skill ID mismatch"
            assert "proposals" in result, "Should contain optimization proposals"
            assert isinstance(result["proposals_generated"], int), "Proposals count should be integer"

            logger.info(f"Generated {result['proposals_generated']} optimization proposals")
            logger.info("✅ Optimization test passed")
            self.test_results.append(("Optimization", "PASS", f"Generated {result['proposals_generated']} proposals"))

        except Exception as e:
            logger.error(f"❌ Optimization test failed: {e}")
            self.test_results.append(("Optimization", "FAIL", str(e)))

    async def test_quality_gates(self):
        """Test quality gate enforcement"""
        logger.info("Testing quality gate enforcement...")

        try:
            # Evaluate quality gates
            result = await self.integration_manager.evaluate_quality_gate("test_skill_001", "1.0.0")

            assert result["skill_id"] == "test_skill_001", "Skill ID mismatch"
            assert "result" in result, "Should contain quality gate result"
            assert "score" in result, "Should contain quality score"
            assert isinstance(result["score"], (int, float)), "Score should be numeric"

            logger.info(f"Quality gate result: {result['result']} (score: {result['score']})")
            logger.info("✅ Quality gate test passed")
            self.test_results.append(("Quality Gates", "PASS", f"Result: {result['result']}"))

        except Exception as e:
            logger.error(f"❌ Quality gate test failed: {e}")
            self.test_results.append(("Quality Gates", "FAIL", str(e)))

    async def test_knowledge_transfer(self):
        """Test knowledge transfer system"""
        logger.info("Testing knowledge transfer...")

        try:
            # Get skill insights
            result = await self.integration_manager.get_skill_insights("test_skill_001")

            assert result["skill_id"] == "test_skill_001", "Skill ID mismatch"
            assert "performance" in result, "Should contain performance data"
            assert "optimization" in result, "Should contain optimization data"
            assert "quality" in result, "Should contain quality data"

            logger.info("✅ Knowledge transfer test passed")
            self.test_results.append(("Knowledge Transfer", "PASS", "Skill insights retrieved"))

        except Exception as e:
            logger.error(f"❌ Knowledge transfer test failed: {e}")
            self.test_results.append(("Knowledge Transfer", "FAIL", str(e)))

    async def test_storage_integration(self):
        """Test MCP storage integration"""
        logger.info("Testing storage integration...")

        try:
            # Get storage statistics
            storage_stats = await self.integration_manager.storage.get_storage_statistics()

            assert storage_stats is not None, "Should return storage statistics"
            assert hasattr(storage_stats, "total_records"), "Should have total records"
            assert hasattr(storage_stats, "storage_size_bytes"), "Should have storage size"

            logger.info(
                f"Storage stats: {storage_stats.total_records} records, {storage_stats.storage_size_bytes} bytes"
            )
            logger.info("✅ Storage integration test passed")
            self.test_results.append(("Storage Integration", "PASS", "Storage stats retrieved"))

        except Exception as e:
            logger.error(f"❌ Storage integration test failed: {e}")
            self.test_results.append(("Storage Integration", "FAIL", str(e)))

    async def test_monitoring(self):
        """Test performance monitoring"""
        logger.info("Testing performance monitoring...")

        try:
            # Get dashboard data
            dashboard_data = await self.integration_manager.performance_monitor.get_dashboard_data("overview")

            assert dashboard_data is not None, "Should return dashboard data"
            assert "timestamp" in dashboard_data, "Should contain timestamp"
            assert "system_health" in dashboard_data, "Should contain system health"

            # Get statistics
            stats = await self.integration_manager.performance_monitor.get_statistics()
            assert stats is not None, "Should return statistics"

            logger.info("✅ Performance monitoring test passed")
            self.test_results.append(("Performance Monitoring", "PASS", "Dashboard data retrieved"))

        except Exception as e:
            logger.error(f"❌ Performance monitoring test failed: {e}")
            self.test_results.append(("Performance Monitoring", "FAIL", str(e)))

    async def test_end_to_end_flow(self):
        """Test complete end-to-end flow"""
        logger.info("Testing end-to-end flow...")

        try:
            # Simulate multiple skill executions with varying performance
            test_executions = [
                {
                    "skill_id": "skill_end_to_end_1",
                    "skill_name": "End-to-End Test Skill 1",
                    "execution_id": "exec_e2e_001",
                    "success": True,
                    "accuracy_score": 0.85,
                    "execution_time": 8.0,
                    "hallucination_detected": False,
                },
                {
                    "skill_id": "skill_end_to_end_2",
                    "skill_name": "End-to-End Test Skill 2",
                    "execution_id": "exec_e2e_002",
                    "success": True,
                    "accuracy_score": 0.95,
                    "execution_time": 1.2,
                    "hallucination_detected": False,
                },
                {
                    "skill_id": "skill_end_to_end_1",
                    "skill_name": "End-to-End Test Skill 1",
                    "execution_id": "exec_e2e_003",
                    "success": False,
                    "accuracy_score": 0.0,
                    "execution_time": 20.0,
                    "hallucination_detected": True,
                    "error_type": "RuntimeError",
                    "error_message": "Processing failed",
                },
            ]

            results = []
            for execution in test_executions:
                result = await self.integration_manager.process_skill_execution(execution)
                results.append(result)
                await asyncio.sleep(0.1)  # Small delay between executions

            # Verify results
            assert len(results) == 3, "Should process all 3 executions"
            assert results[0]["execution_successful"], "First execution should succeed"
            assert results[1]["execution_successful"], "Second execution should succeed"
            assert not results[2]["execution_successful"], "Third execution should fail"

            # Check system status
            system_status = await self.integration_manager.get_system_status()
            assert system_status is not None, "Should return system status"

            logger.info(f"Processed {len(results)} executions successfully")
            logger.info("✅ End-to-end flow test passed")
            self.test_results.append(("End-to-End Flow", "PASS", f"Processed {len(results)} executions"))

        except Exception as e:
            logger.error(f"❌ End-to-end flow test failed: {e}")
            self.test_results.append(("End-to-End Flow", "FAIL", str(e)))

    async def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("\n" + "=" * 60)
        logger.info("AGENT LIGHTNING INTEGRATION TEST REPORT")
        logger.info("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r[1] == "PASS"])
        failed_tests = total_tests - passed_tests

        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests / total_tests * 100):.1f}%")
        logger.info("")

        for test_name, status, message in self.test_results:
            status_icon = "✅" if status == "PASS" else "❌"
            logger.info(f"{status_icon} {test_name}: {status} - {message}")

        logger.info("\n" + "=" * 60)

        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "test_results": [
                {"test_name": name, "status": status, "message": message} for name, status, message in self.test_results
            ],
            "system_statistics": await self.integration_manager.get_system_statistics(),
        }

        report_file = Path("test_report.json")
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Detailed report saved to: {report_file}")

    async def cleanup(self):
        """Clean up test environment"""
        logger.info("Cleaning up test environment...")

        if self.integration_manager:
            await self.integration_manager.stop()

        logger.info("✅ Cleanup completed")


async def main():
    """Main test function"""
    tester = IntegrationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
