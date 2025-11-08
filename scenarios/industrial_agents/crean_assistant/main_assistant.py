#!/usr/bin/env python3
"""
CreaTech Assistant: Creative Development Agent - Main Interface

Main interface for the CreaTech Assistant - a specialized agent that combines
technical programming precision with creative and artistic intelligence.
"""

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CreaTechAssistant:
    """Main CreaTech Assistant interface"""

    def __init__(self):
        self.working_directory = Path("crean_workspace")
        self.working_directory.mkdir(exist_ok=True)

        # Import core components
        try:
            from core.creative_engineer import CreativeEngineer
            from core.synthesizer import CreativeTechnicalSynthesizer
            from training.crean_trainer import CreaTechTrainer
            from workflows.creative_workflows import CreativeWorkflows

            self.creative_engineer = CreativeEngineer()
            self.synthesizer = CreativeTechnicalSynthesizer()
            self.workflows = CreativeWorkflows()
            self.trainer = CreaTechTrainer()

            logger.info("✅ All CreaTech components loaded successfully")
        except ImportError as e:
            logger.warning(f"⚠️  Some components failed to import: {e}")
            # Fallback implementations
            self.creative_engineer = None
            self.synthesizer = None
            self.workflows = None
            self.trainer = None

    async def analyze_requirement(self, requirement: str, context: dict | None = None) -> dict[str, Any]:
        """Analyze a requirement for creative-technical opportunities"""
        logger.info(f"Analyzing requirement: {requirement}")

        if self.creative_engineer:
            analysis = await self.creative_engineer.analyze_requirement(requirement)
        else:
            # Fallback basic analysis
            analysis = {
                "requirement": requirement,
                "domain_classification": {"primary_domain": "general", "secondary_domains": [], "confidence": 0.5},
                "creative_opportunities": ["aesthetic_enhancement", "user_experience"],
                "technical_constraints": ["functionality", "reliability"],
                "synthesis_potential": 0.7,
            }

        # Add context information if provided
        if context:
            analysis.update({"context": context})

        return analysis

    async def generate_creative_concepts(self, analysis: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate creative concepts based on requirement analysis"""
        logger.info("Generating creative concepts...")

        if self.creative_engineer:
            concepts = await self.creative_engineer.generate_creative_concepts(analysis)
        else:
            # Fallback basic concepts
            concepts = [
                {
                    "pattern_type": "design_thinking",
                    "concept_name": "Design Thinking Approach",
                    "description": "Apply human-centered design principles",
                    "creative_elements": {"algorithm": "human_centered_design", "parameters": {}},
                    "estimated_impact": 0.8,
                }
            ]

        # Add metadata
        for concept in concepts:
            concept["generation_timestamp"] = str(asyncio.get_event_loop().time())
            concept["crean_confidence"] = concept.get("estimated_impact", 0.8)

        return concepts

    async def synthesize_solution(
        self, requirement: str, context: dict | None = None, concepts: list[dict[str, Any]] | None = None
    ) -> Any:
        """Synthesize creative-technical solution"""
        logger.info(f"Synthesizing solution for: {requirement}")

        # Analyze requirement if not already done
        if not context:
            context = await self.analyze_requirement(requirement)

        # Generate concepts if not provided
        if not concepts:
            concepts = await self.generate_creative_concepts(context)

        if self.synthesizer:
            # Create technical requirements
            technical_requirements = {
                "structure": self._infer_technical_structure(requirement),
                "domain": context.get("domain_classification", {}).get("primary_domain", "general"),
                "constraints": self._infer_constraints(requirement),
            }

            # Synthesize solution
            synthesis_result = await self.synthesizer.synthesize(concepts, technical_requirements, context)

            logger.info(f"Solution synthesized with confidence score: {synthesis_result.confidence_score:.2f}")
            return synthesis_result

        # Fallback mock synthesis result
        class MockSynthesisResult:
            def __init__(self):
                self.synthesized_solution = {"concept": "Mock Solution", "implementation": "Basic implementation"}
                self.confidence_score = 0.7
                self.synthesis_method = "fallback"
                self.creative_elements = ["creativity"]
                self.technical_elements = ["technical"]
                self.aesthetic_score = 0.6
                self.feasibility_score = 0.8

        result = MockSynthesisResult()
        logger.info(f"Mock solution created with confidence score: {result.confidence_score:.2f}")
        return result

    async def run_creative_cad_workflow(self, requirement: str, preferences: dict[str, Any] = None) -> dict[str, Any]:
        """Run creative CAD analysis workflow"""
        logger.info("Running creative CAD workflow...")

        if preferences is None:
            preferences = {"aesthetic_priority": "high", "innovation_level": "high", "user_focus": "professional"}

        if self.workflows:
            result = await self.workflows.creative_cad_workflow(requirement, preferences)
            return {
                "workflow_name": result.workflow_name,
                "solution": result.final_solution,
                "quality_score": result.overall_quality_score,
                "execution_time": result.execution_time,
                "recommendations": self._generate_recommendations(result),
            }
        # Fallback mock result
        return {
            "workflow_name": "Mock Creative CAD Workflow",
            "solution": {"design": "Mock CAD design", "features": ["basic", "functional"]},
            "quality_score": 0.7,
            "execution_time": 1.5,
            "recommendations": ["Consider aesthetic enhancements", "Validate with real tools"],
        }

    async def run_innovative_documentation_workflow(
        self, documentation_request: str, audience: str = "technical_users"
    ) -> dict[str, Any]:
        """Run innovative documentation workflow"""
        logger.info("Running innovative documentation workflow...")

        if self.workflows:
            result = await self.workflows.innovative_documentation_workflow(documentation_request, audience)
            return {
                "workflow_name": result.workflow_name,
                "solution": result.final_solution,
                "quality_score": result.overall_quality_score,
                "execution_time": result.execution_time,
                "recommendations": self._generate_recommendations(result),
            }
        # Fallback mock result
        return {
            "workflow_name": "Mock Documentation Workflow",
            "solution": {"content": "Mock documentation", "format": "markdown"},
            "quality_score": 0.75,
            "execution_time": 1.2,
            "recommendations": ["Add real examples", "Include interactive elements"],
        }

    async def run_creative_web_application_workflow(
        self, app_requirement: str, design_preferences: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Run creative web application workflow"""
        logger.info("Running creative web application workflow...")

        if design_preferences is None:
            design_preferences = {
                "visual_style": "modern_professional",
                "user_experience": "delightful",
                "accessibility": "high_priority",
            }

        if self.workflows:
            result = await self.workflows.creative_web_application_workflow(app_requirement, design_preferences)
            return {
                "workflow_name": result.workflow_name,
                "solution": result.final_solution,
                "quality_score": result.overall_quality_score,
                "execution_time": result.execution_time,
                "recommendations": self._generate_recommendations(result),
            }
        # Fallback mock result
        return {
            "workflow_name": "Mock Web Application Workflow",
            "solution": {"framework": "Mock web app", "features": ["responsive", "interactive"]},
            "quality_score": 0.8,
            "execution_time": 2.1,
            "recommendations": ["Add real framework integration", "Implement testing"],
        }

    def _infer_technical_structure(self, requirement: str) -> list[str]:
        """Infer technical structure from requirement"""
        structure_keywords = {
            "web": ["frontend", "backend", "api", "database"],
            "app": ["interface", "logic", "data"],
            "tool": ["cli", "interface", "functionality"],
            "system": ["components", "integration", "workflow"],
            "service": ["api", "processing", "storage"],
        }

        requirement_lower = requirement.lower()
        for domain, components in structure_keywords.items():
            if domain in requirement_lower:
                return components

        return ["interface", "logic", "data"]

    def _infer_constraints(self, requirement: str) -> list[str]:
        """Infer constraints from requirement"""
        constraints = []

        if "fast" in requirement.lower() or "quick" in requirement.lower():
            constraints.append("performance")
        if "safe" in requirement.lower() or "secure" in requirement.lower():
            constraints.append("security")
        if "simple" in requirement.lower() or "easy" in requirement.lower():
            constraints.append("simplicity")
        if "beautiful" in requirement.lower() or "aesthetic" in requirement.lower():
            constraints.append("aesthetic_quality")

        if not constraints:
            constraints = ["functionality", "reliability"]

        return constraints

    def _generate_recommendations(self, result) -> list[str]:
        """Generate recommendations based on workflow result"""
        recommendations = []

        # Handle both real workflow results and mock results
        quality_score = getattr(result, "overall_quality_score", None) or result.get("quality_score", 0.7)
        execution_time = getattr(result, "execution_time", None) or result.get("execution_time", 1.0)

        if quality_score > 0.8:
            recommendations.append("Solution meets high quality standards")
        else:
            recommendations.append("Consider refinement to improve quality")

        if execution_time < 10:
            recommendations.append("Efficient workflow execution")
        else:
            recommendations.append("Consider optimization for faster execution")

        recommendations.extend(
            [
                "Continue learning from user feedback",
                "Expand creative-technical pattern library",
                "Integrate with additional specialized agents",
            ]
        )

        return recommendations

    async def interactive_session(self):
        """Run an interactive session with CreaTech Assistant"""
        print("\n🎨 Welcome to CreaTech Assistant!")
        print("Creative Development Agent that blends technical precision with artistic intelligence")
        print("=" * 60)

        while True:
            print("\n🎯 What would you like to do?")
            print("1. Analyze a requirement")
            print("2. Generate creative concepts")
            print("3. Synthesize a solution")
            print("4. Run creative CAD workflow")
            print("5. Run documentation workflow")
            print("6. Run web app workflow")
            print("7. Exit")

            choice = input("\nEnter your choice (1-7): ").strip()

            if choice == "1":
                requirement = input("Enter your requirement: ").strip()
                analysis = await self.analyze_requirement(requirement)
                print("\n📊 Analysis Result:")
                print(f"Domain: {analysis['domain_classification']['primary_domain']}")
                print(f"Creative opportunities: {', '.join(analysis['creative_opportunities'])}")
                print(f"Synthesis potential: {analysis['synthesis_potential']:.2f}")

            elif choice == "2":
                requirement = input("Enter your requirement: ").strip()
                analysis = await self.analyze_requirement(requirement)
                concepts = await self.generate_creative_concepts(analysis)
                print("\n💡 Creative Concepts:")
                for i, concept in enumerate(concepts, 1):
                    print(f"{i}. {concept['concept_name']} (impact: {concept['estimated_impact']:.2f})")

            elif choice == "3":
                requirement = input("Enter your requirement: ").strip()
                synthesis = await self.synthesize_solution(requirement)
                print("\n🚀 Synthesis Result:")
                print(
                    f"Concept: {synthesis.synthesized_solution['concept'] if hasattr(synthesis.synthesized_solution, '__getitem__') else 'Synthesized solution'}"
                )
                print(f"Confidence: {synthesis.confidence_score:.2f}")
                print(f"Creative elements: {', '.join(synthesis.creative_elements)}")
                print(f"Feasibility: {synthesis.feasibility_score:.2f}")

            elif choice == "4":
                requirement = input("Enter your CAD design requirement: ").strip()
                result = await self.run_creative_cad_workflow(requirement)
                print("\n🔧 Creative CAD Result:")
                print(f"Workflow: {result['workflow_name']}")
                print(f"Quality score: {result['quality_score']:.2f}")
                print(f"Execution time: {result['execution_time']:.1f}s")

            elif choice == "5":
                doc_request = input("Enter documentation request: ").strip()
                audience = input("Enter target audience (technical/business/general): ").strip()
                result = await self.run_innovative_documentation_workflow(doc_request, audience)
                print("\n📚 Documentation Result:")
                print(f"Workflow: {result['workflow_name']}")
                print(f"Quality score: {result['quality_score']:.2f}")

            elif choice == "6":
                app_req = input("Enter web app requirement: ").strip()
                result = await self.run_creative_web_application_workflow(app_req)
                print("\n🌐 Web App Result:")
                print(f"Workflow: {result['workflow_name']}")
                print(f"Quality score: {result['quality_score']:.2f}")

            elif choice == "7":
                print("\n👋 Thank you for using CreaTech Assistant!")
                break
            else:
                print("Invalid choice. Please try again.")


# CLI interface
def main():
    """Main CLI interface for CreaTech Assistant"""
    parser = argparse.ArgumentParser(description="CreaTech Assistant - Creative Development Agent")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--requirement", help="Requirement to analyze")
    parser.add_argument("--workflow", choices=["cad", "documentation", "webapp"], help="Workflow to run")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set up logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    async def run_cli():
        assistant = CreaTechAssistant()

        if args.interactive:
            await assistant.interactive_session()
        elif args.requirement and args.workflow:
            if args.workflow == "cad":
                result = await assistant.run_creative_cad_workflow(args.requirement)
                print(json.dumps(result, indent=2))
            elif args.workflow == "documentation":
                result = await assistant.run_innovative_documentation_workflow(args.requirement)
                print(json.dumps(result, indent=2))
            elif args.workflow == "webapp":
                result = await assistant.run_creative_web_application_workflow(args.requirement)
                print(json.dumps(result, indent=2))
        elif args.requirement:
            # Simple synthesis
            synthesis = await assistant.synthesize_solution(args.requirement)
            print(
                json.dumps(
                    synthesis.synthesized_solution.__dict__
                    if hasattr(synthesis.synthesized_solution, "__dict__")
                    else synthesis.synthesized_solution,
                    indent=2,
                    default=str,
                )
            )
        else:
            parser.print_help()

    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
