#!/usr/bin/env python3
"""
Multi-Agent Workflow Examples for CreaTech Assistant

Demonstrates how CreaTech Assistant orchestrates multiple specialized agents
to solve complex creative-technical challenges.
"""

import asyncio
import json
import logging
from pathlib import Path

from crean_assistant import CreaTechAssistant

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MultiAgentWorkflowExamples:
    """Examples of multi-agent workflows with CreaTech Assistant"""

    def __init__(self):
        self.crean_assistant = CreaTechAssistant()
        self.results_dir = Path("crean_workspace/workflow_examples")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def example_1_smart_home_device_design(self):
        """Example 1: Smart Home Device Design (CAD + Technical + Creative)"""

        logger.info("🏠 Starting Smart Home Device Design Workflow...")

        # User requirement
        requirement = """
        Design a smart home hub that combines beautiful aesthetics with
        powerful functionality. It should be wall-mountable, have LED status
        indicators, and include touch controls. The design should be modern
        but approachable for mainstream consumers.
        """

        # Phase 1: Creative CAD Analysis
        logger.info("Phase 1: Running Creative CAD Workflow...")
        cad_result = await self.crean_assistant.run_creative_cad_workflow(
            requirement,
            preferences={"aesthetic_priority": "high", "innovation_level": "medium", "user_focus": "consumer_friendly"},
        )

        # Phase 2: Technical Implementation Planning
        logger.info("Phase 2: Technical Implementation Synthesis...")
        tech_analysis = await self.crean_assistant.analyze_requirement(requirement)
        tech_concepts = await self.crean_assistant.generate_creative_concepts(tech_analysis)
        synthesis_result = await self.crean_assistant.synthesize_solution(requirement, tech_analysis, tech_concepts)

        # Phase 3: User Documentation Creation
        logger.info("Phase 3: Creating User Documentation...")
        doc_requirement = """
        Create user documentation for the smart home hub including:
        - Installation guide
        - Setup instructions
        - Feature overview
        - Troubleshooting tips
        """
        doc_result = await self.crean_assistant.run_innovative_documentation_workflow(doc_requirement, "consumer_users")

        # Combine results
        workflow_result = {
            "workflow_name": "Smart Home Device Design",
            "requirement": requirement.strip(),
            "phases": {
                "creative_cad": {
                    "quality_score": cad_result["quality_score"],
                    "execution_time": cad_result["execution_time"],
                    "key_concepts": list(cad_result["solution"].keys())[:3],
                },
                "technical_synthesis": {
                    "confidence_score": synthesis_result.confidence_score,
                    "synthesis_method": synthesis_result.synthesis_method,
                    "feasibility_score": synthesis_result.feasibility_score,
                },
                "documentation": {
                    "quality_score": doc_result["quality_score"],
                    "workflow": doc_result["workflow_name"],
                },
            },
            "overall_quality": (
                cad_result["quality_score"] + synthesis_result.confidence_score + doc_result["quality_score"]
            )
            / 3,
            "recommendations": cad_result["recommendations"] + doc_result["recommendations"],
        }

        # Save results
        result_file = self.results_dir / "smart_home_design.json"
        with open(result_file, "w") as f:
            json.dump(workflow_result, f, indent=2, default=str)

        logger.info(f"✅ Smart Home Design workflow completed: {result_file}")
        return workflow_result

    async def example_2_creative_dashboard_application(self):
        """Example 2: Creative Web Dashboard (Web App + Data Visualization + UX)"""

        logger.info("🌐 Starting Creative Dashboard Application Workflow...")

        # User requirement
        requirement = """
        Create a web dashboard for visualizing creative project metrics.
        Should show project progress, team collaboration patterns, and
        creative insights through beautiful, interactive charts.
        Need real-time updates and an inspiring, modern interface.
        """

        # Phase 1: Creative Web Application Design
        logger.info("Phase 1: Creative Web Application Workflow...")
        web_result = await self.crean_assistant.run_creative_web_application_workflow(
            requirement,
            design_preferences={
                "visual_style": "modern_creative",
                "user_experience": "delightful_interactions",
                "accessibility": "high_priority",
                "real_time_features": "required",
            },
        )

        # Phase 2: Technical Architecture Synthesis
        logger.info("Phase 2: Technical Architecture Planning...")
        await self.crean_assistant.analyze_requirement(requirement)

        # Focus on real-time data and visualization aspects
        enhanced_requirement = (
            requirement
            + """

        Technical constraints:
        - Must handle real-time data streaming
        - Support for interactive data visualization
        - Responsive design for desktop and mobile
        - Smooth animations and transitions
        """
        )

        synthesis_result = await self.crean_assistant.synthesize_solution(enhanced_requirement)

        # Phase 3: API Documentation for Developers
        logger.info("Phase 3: Developer API Documentation...")
        api_requirement = """
        Create comprehensive API documentation for the creative dashboard:
        - REST API endpoints
        - WebSocket connection guide
        - Data schema documentation
        - Integration examples
        """
        api_result = await self.crean_assistant.run_innovative_documentation_workflow(
            api_requirement, "technical_users"
        )

        # Combine results
        workflow_result = {
            "workflow_name": "Creative Dashboard Application",
            "requirement": requirement.strip(),
            "phases": {
                "web_design": {
                    "quality_score": web_result["quality_score"],
                    "execution_time": web_result["execution_time"],
                    "design_approach": web_result["solution"].get("design_approach", "modern"),
                },
                "technical_architecture": {
                    "confidence_score": synthesis_result.confidence_score,
                    "synthesis_method": synthesis_result.synthesis_method,
                    "creative_elements": synthesis_result.creative_elements[:3],
                },
                "api_documentation": {
                    "quality_score": api_result["quality_score"],
                    "target_audience": "technical_users",
                },
            },
            "technical_feasibility": synthesis_result.feasibility_score,
            "innovation_score": synthesis_result.aesthetic_score,
            "implementation_plan": synthesis_result.synthesized_solution.get("implementation_plan", {}),
        }

        # Save results
        result_file = self.results_dir / "creative_dashboard.json"
        with open(result_file, "w") as f:
            json.dump(workflow_result, f, indent=2, default=str)

        logger.info(f"✅ Creative Dashboard workflow completed: {result_file}")
        return workflow_result

    async def example_3_educational_tool_suite(self):
        """Example 3: Educational Tool Suite (Documentation + UX + Technical)"""

        logger.info("📚 Starting Educational Tool Suite Workflow...")

        # User requirement
        requirement = """
        Design an educational platform that teaches programming through
        creative projects. Should combine interactive lessons with hands-on
        coding exercises and showcase student work beautifully.
        """

        # Phase 1: Educational Content Design
        logger.info("Phase 1: Educational Content Strategy...")
        doc_requirement = """
        Create comprehensive educational materials for learning programming:
        - Interactive lesson plans
        - Progressive skill building
        - Project-based learning guides
        - Assessment and feedback systems
        """
        edu_result = await self.crean_assistant.run_innovative_documentation_workflow(
            doc_requirement, "educational_content"
        )

        # Phase 2: Learning Platform Web Application
        logger.info("Phase 2: Learning Platform Design...")
        app_requirement = """
        Create an engaging web application for programming education:
        - Interactive code editor
        - Real-time feedback
        - Progress tracking
        - Student portfolio gallery
        - Gamification elements
        """
        app_result = await self.crean_assistant.run_creative_web_application_workflow(
            app_requirement,
            design_preferences={
                "visual_style": "engaging_educational",
                "user_experience": "motivational",
                "accessibility": "inclusive_design",
                "interactive_elements": "high_priority",
            },
        )

        # Phase 3: Creative Technical Synthesis
        logger.info("Phase 3: Creative-Technical Integration...")
        analysis = await self.crean_assistant.analyze_requirement(requirement)
        concepts = await self.crean_assistant.generate_creative_concepts(analysis)

        # Focus on educational psychology and engagement
        enhanced_analysis = {
            **analysis,
            "educational_psychology": ["constructivist_learning", "immediate_feedback", "social_learning"],
            "technical_constraints": ["real_time_collaboration", "code_execution", "progress_persistence"],
        }

        synthesis_result = await self.crean_assistant.synthesize_solution(requirement, enhanced_analysis, concepts)

        # Combine results
        workflow_result = {
            "workflow_name": "Educational Tool Suite",
            "requirement": requirement.strip(),
            "phases": {
                "educational_content": {
                    "quality_score": edu_result["quality_score"],
                    "content_type": "educational_materials",
                },
                "learning_platform": {
                    "quality_score": app_result["quality_score"],
                    "design_focus": "engaging_educational",
                },
                "creative_synthesis": {
                    "confidence_score": synthesis_result.confidence_score,
                    "learning_approach": synthesis_result.creative_elements[:3],
                },
            },
            "educational_effectiveness": (
                edu_result["quality_score"] + app_result["quality_score"] + synthesis_result.aesthetic_score
            )
            / 3,
            "technical_approach": synthesis_result.synthesis_method,
            "implementation_complexity": "medium" if synthesis_result.feasibility_score > 0.7 else "high",
        }

        # Save results
        result_file = self.results_dir / "educational_tool_suite.json"
        with open(result_file, "w") as f:
            json.dump(workflow_result, f, indent=2, default=str)

        logger.info(f"✅ Educational Tool Suite workflow completed: {result_file}")
        return workflow_result

    async def run_all_examples(self):
        """Run all multi-agent workflow examples"""

        logger.info("🚀 Starting Multi-Agent Workflow Examples...")
        logger.info("=" * 60)

        examples = [
            ("Smart Home Device Design", self.example_1_smart_home_device_design),
            ("Creative Dashboard Application", self.example_2_creative_dashboard_application),
            ("Educational Tool Suite", self.example_3_educational_tool_suite),
        ]

        results = {}

        for example_name, example_func in examples:
            logger.info(f"\n{'=' * 20} {example_name} {'=' * 20}")
            try:
                result = await example_func()
                results[example_name] = {
                    "status": "success",
                    "quality_metrics": {
                        "overall_quality": result.get("overall_quality", 0),
                        "technical_feasibility": result.get("technical_feasibility", 0),
                        "innovation_score": result.get("innovation_score", 0),
                    },
                }
                logger.info(f"✅ {example_name} completed successfully")
            except Exception as e:
                logger.error(f"❌ {example_name} failed: {str(e)}")
                results[example_name] = {"status": "failed", "error": str(e)}

        # Create summary report
        summary = {
            "run_timestamp": str(asyncio.get_event_loop().time()),
            "total_examples": len(examples),
            "successful_examples": len([r for r in results.values() if r["status"] == "success"]),
            "results": results,
            "crean_capabilities_demonstrated": [
                "creative_cad_workflow",
                "creative_web_application_workflow",
                "innovative_documentation_workflow",
                "creative_technical_synthesis",
                "multi_agent_orchestration",
            ],
        }

        # Save summary
        summary_file = self.results_dir / "workflow_examples_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info("\n📊 Multi-Agent Workflow Examples Summary:")
        logger.info(f"Total Examples: {summary['total_examples']}")
        logger.info(f"Successful: {summary['successful_examples']}")
        logger.info(f"Results saved to: {summary_file}")

        return summary


# CLI interface for running examples
async def main():
    """Main CLI interface for multi-agent workflow examples"""
    import argparse

    parser = argparse.ArgumentParser(description="CreaTech Multi-Agent Workflow Examples")
    parser.add_argument(
        "--example", type=int, choices=[1, 2, 3], help="Run specific example (1=Smart Home, 2=Dashboard, 3=Education)"
    )
    parser.add_argument("--all", action="store_true", help="Run all examples")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    examples = MultiAgentWorkflowExamples()

    if args.all:
        await examples.run_all_examples()
    elif args.example == 1:
        await examples.example_1_smart_home_device_design()
    elif args.example == 2:
        await examples.example_2_creative_dashboard_application()
    elif args.example == 3:
        await examples.example_3_educational_tool_suite()
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
