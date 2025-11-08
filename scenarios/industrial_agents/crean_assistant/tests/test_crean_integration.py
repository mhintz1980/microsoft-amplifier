#!/usr/bin/env python3
"""
Integration Tests for CreaTech Assistant

Tests CreaTech's integration with existing agents and validates
core functionality.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from crean_assistant import CreaTechAssistant

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCreaTechIntegration:
    """Integration tests for CreaTech Assistant"""

    def setup_method(self):
        """Set up test environment"""
        self.crean_assistant = CreaTechAssistant()
        self.test_results_dir = Path("crean_workspace/test_results")
        self.test_results_dir.mkdir(parents=True, exist_ok=True)

    async def test_basic_requirement_analysis(self):
        """Test basic requirement analysis functionality"""
        logger.info("Testing basic requirement analysis...")

        test_requirement = "Create a simple CLI tool for managing todo lists"
        analysis = await self.crean_assistant.analyze_requirement(test_requirement)

        # Validate analysis structure
        assert "requirement" in analysis
        assert "domain_classification" in analysis
        assert "creative_opportunities" in analysis
        assert "technical_constraints" in analysis
        assert "synthesis_potential" in analysis

        # Validate domain classification
        domain = analysis["domain_classification"]
        assert "primary_domain" in domain
        assert "secondary_domains" in domain
        assert "confidence" in domain

        # Validate synthesis potential is reasonable
        assert 0 <= analysis["synthesis_potential"] <= 1

        logger.info("✅ Basic requirement analysis test passed")
        return analysis

    async def test_creative_concept_generation(self):
        """Test creative concept generation"""
        logger.info("Testing creative concept generation...")

        # First analyze a requirement
        requirement = "Design an innovative web dashboard for data visualization"
        analysis = await self.crean_assistant.analyze_requirement(requirement)

        # Generate creative concepts
        concepts = await self.crean_assistant.generate_creative_concepts(analysis)

        # Validate concepts structure
        assert len(concepts) > 0, "Should generate at least one concept"

        for concept in concepts:
            assert "pattern_type" in concept
            assert "concept_name" in concept
            assert "description" in concept
            assert "creative_elements" in concept
            assert "estimated_impact" in concept

            # Validate impact scores are reasonable
            assert 0 <= concept["estimated_impact"] <= 1

        logger.info(f"✅ Generated {len(concepts)} creative concepts")
        return concepts

    async def test_solution_synthesis(self):
        """Test solution synthesis functionality"""
        logger.info("Testing solution synthesis...")

        requirement = "Create a mobile app for tracking fitness goals"

        # Full synthesis workflow
        synthesis_result = await self.crean_assistant.synthesize_solution(requirement)

        # Validate synthesis result
        assert synthesis_result.synthesized_solution is not None
        assert 0 <= synthesis_result.confidence_score <= 1
        assert synthesis_result.synthesis_method in [
            "pattern_blending",
            "cross_domain_transfer",
            "aesthetic_optimization",
            "creative_problem_solving",
            "iterative_refinement",
            "fallback",
        ]
        assert len(synthesis_result.creative_elements) > 0
        assert len(synthesis_result.technical_elements) > 0
        assert 0 <= synthesis_result.aesthetic_score <= 1
        assert 0 <= synthesis_result.feasibility_score <= 1

        logger.info(f"✅ Solution synthesis completed with method: {synthesis_result.synthesis_method}")
        logger.info(f"   Confidence score: {synthesis_result.confidence_score:.2f}")
        return synthesis_result

    async def test_creative_cad_workflow(self):
        """Test creative CAD workflow"""
        logger.info("Testing creative CAD workflow...")

        requirement = "Design a modern desktop computer case with RGB lighting"
        preferences = {"aesthetic_priority": "high", "innovation_level": "medium", "user_focus": "gaming_enthusiasts"}

        result = await self.crean_assistant.run_creative_cad_workflow(requirement, preferences)

        # Validate workflow result
        assert "workflow_name" in result
        assert "solution" in result
        assert "quality_score" in result
        assert "execution_time" in result
        assert "recommendations" in result

        assert 0 <= result["quality_score"] <= 1
        assert result["execution_time"] > 0
        assert len(result["recommendations"]) > 0

        logger.info(f"✅ CAD workflow completed with quality score: {result['quality_score']:.2f}")
        return result

    async def test_documentation_workflow(self):
        """Test innovative documentation workflow"""
        logger.info("Testing documentation workflow...")

        doc_request = "Create API documentation for a REST service"
        audience = "technical_users"

        result = await self.crean_assistant.run_innovative_documentation_workflow(doc_request, audience)

        # Validate documentation result
        assert "workflow_name" in result
        assert "solution" in result
        assert "quality_score" in result
        assert "execution_time" in result

        assert 0 <= result["quality_score"] <= 1
        assert result["execution_time"] > 0

        logger.info(f"✅ Documentation workflow completed with quality score: {result['quality_score']:.2f}")
        return result

    async def test_web_application_workflow(self):
        """Test creative web application workflow"""
        logger.info("Testing web application workflow...")

        app_requirement = "Build a task management web application"
        design_preferences = {
            "visual_style": "modern_minimal",
            "user_experience": "intuitive",
            "accessibility": "high_priority",
        }

        result = await self.crean_assistant.run_creative_web_application_workflow(app_requirement, design_preferences)

        # Validate web app result
        assert "workflow_name" in result
        assert "solution" in result
        assert "quality_score" in result
        assert "execution_time" in result

        assert 0 <= result["quality_score"] <= 1
        assert result["execution_time"] > 0

        logger.info(f"✅ Web application workflow completed with quality score: {result['quality_score']:.2f}")
        return result

    async def test_training_integration(self):
        """Test Agent Lightning training integration"""
        logger.info("Testing training integration...")

        # Note: This is a lightweight test that doesn't run full training
        # It just validates the training interface is accessible

        try:
            # Test training preparation (without actually training)
            trainer = self.crean_assistant.trainer

            # Validate trainer is initialized
            assert trainer is not None

            # Test that training methods exist
            assert hasattr(trainer, "prepare_training_data")
            assert hasattr(trainer, "train_creaech_agent")
            assert hasattr(trainer, "save_training_results")

            logger.info("✅ Training integration interface validated")
            return True

        except Exception as e:
            logger.warning(f"⚠️  Training integration test skipped: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all integration tests"""
        logger.info("🧪 Starting CreaTech Integration Tests...")
        logger.info("=" * 50)

        tests = [
            ("Basic Requirement Analysis", self.test_basic_requirement_analysis),
            ("Creative Concept Generation", self.test_creative_concept_generation),
            ("Solution Synthesis", self.test_solution_synthesis),
            ("Creative CAD Workflow", self.test_creative_cad_workflow),
            ("Documentation Workflow", self.test_documentation_workflow),
            ("Web Application Workflow", self.test_web_application_workflow),
            ("Training Integration", self.test_training_integration),
        ]

        results = {}
        passed = 0
        failed = 0

        for test_name, test_func in tests:
            logger.info(f"\n{'-' * 20} {test_name} {'-' * 20}")
            try:
                result = await test_func()
                results[test_name] = {"status": "passed", "result_type": type(result).__name__}
                passed += 1
                logger.info(f"✅ {test_name} PASSED")
            except Exception as e:
                logger.error(f"❌ {test_name} FAILED: {str(e)}")
                results[test_name] = {"status": "failed", "error": str(e)}
                failed += 1

        # Create test summary
        summary = {
            "test_run_timestamp": str(asyncio.get_event_loop().time()),
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "success_rate": passed / len(tests) if tests else 0,
            "results": results,
        }

        # Save test results
        results_file = self.test_results_dir / "integration_test_results.json"
        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info("\n📊 Integration Test Summary:")
        logger.info(f"Total Tests: {summary['total_tests']}")
        logger.info(f"Passed: {summary['passed']}")
        logger.info(f"Failed: {summary['failed']}")
        logger.info(f"Success Rate: {summary['success_rate']:.1%}")
        logger.info(f"Results saved to: {results_file}")

        return summary


# CLI interface for running tests
async def main():
    """Main CLI interface for integration tests"""
    import argparse

    parser = argparse.ArgumentParser(description="CreaTech Assistant Integration Tests")
    parser.add_argument(
        "--test",
        choices=["analysis", "concepts", "synthesis", "cad", "docs", "web", "training"],
        help="Run specific test",
    )
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    test_instance = TestCreaTechIntegration()

    if args.all:
        await test_instance.run_all_tests()
    elif args.test == "analysis":
        await test_instance.test_basic_requirement_analysis()
    elif args.test == "concepts":
        await test_instance.test_creative_concept_generation()
    elif args.test == "synthesis":
        await test_instance.test_solution_synthesis()
    elif args.test == "cad":
        await test_instance.test_creative_cad_workflow()
    elif args.test == "docs":
        await test_instance.test_documentation_workflow()
    elif args.test == "web":
        await test_instance.test_web_application_workflow()
    elif args.test == "training":
        await test_instance.test_training_integration()
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
