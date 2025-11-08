#!/usr/bin/env python3
"""
Creative Workflow Orchestrator: Multi-Agent Integration Hub

Orchestrates multiple specialized agents for complete creative-technical workflows.
Integrates CreaTech Assistant with existing Amplifier agents for end-to-end solutions.
"""

import argparse
import asyncio
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from main_assistant import CreaTechAssistant
from ui_rapid_prototyper import UIRapidPrototyper

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CreativeWorkflowOrchestrator:
    """Orchestrates creative-technical workflows across multiple specialized agents"""

    def __init__(self):
        self.crean_assistant = CreaTechAssistant()
        self.ui_prototyper = UIRapidPrototyper()
        self.workspace = Path("creative_workflow_workspace")
        self.workspace.mkdir(exist_ok=True)

        # Workflow history for learning
        self.workflow_history = []
        self.agent_registry = self._initialize_agent_registry()

        logger.info("🎭 Creative Workflow Orchestrator initialized")
        logger.info(f"📋 Registered {len(self.agent_registry)} specialized agents")

    def _initialize_agent_registry(self) -> dict[str, dict[str, Any]]:
        """Initialize registry of available specialized agents"""
        return {
            "crean_assistant": {
                "name": "CreaTech Assistant",
                "capabilities": [
                    "requirement_analysis",
                    "creative_concept_generation",
                    "solution_synthesis",
                    "creative_cad_workflow",
                    "documentation_workflow",
                    "web_application_workflow",
                ],
                "strengths": ["creative_technical_synthesis", "multi_agent_coordination"],
                "contact": self.crean_assistant,
            },
            "ui_rapid_prototyper": {
                "name": "UI Rapid Prototyper",
                "capabilities": [
                    "ui_requirement_analysis",
                    "ui_concept_generation",
                    "prototype_specification",
                    "html_prototype_generation",
                    "interactive_prototype_creation",
                ],
                "strengths": ["rapid_ui_iteration", "visual_design", "user_experience"],
                "contact": self.ui_prototyper,
            },
            # Placeholder for future agents
            "code_generator": {
                "name": "Code Generator (Future)",
                "capabilities": ["component_generation", "api_implementation", "database_schema", "testing_code"],
                "strengths": ["code_generation", "technical_implementation"],
                "contact": None,
            },
            "testing_agent": {
                "name": "Testing Agent (Future)",
                "capabilities": [
                    "test_planning",
                    "automated_testing",
                    "user_acceptance_testing",
                    "performance_testing",
                ],
                "strengths": ["quality_assurance", "test_coverage"],
                "contact": None,
            },
            "documentation_agent": {
                "name": "Documentation Agent (Future)",
                "capabilities": ["technical_documentation", "user_guides", "api_documentation", "deployment_guides"],
                "strengths": ["documentation_quality", "knowledge_transfer"],
                "contact": None,
            },
        }

    async def analyze_project_requirements(self, project_description: str) -> dict[str, Any]:
        """Analyze project requirements using CreaTech and determine optimal agent coordination"""

        logger.info(f"🔍 Analyzing project requirements: {project_description}")

        # Use CreaTech for initial analysis
        crean_analysis = await self.crean_assistant.analyze_requirement(project_description)

        # Determine required agents and workflow
        agent_coordination = self._plan_agent_coordination(project_description, crean_analysis)

        project_analysis = {
            "project_id": str(uuid.uuid4())[:8],
            "description": project_description,
            "crean_analysis": crean_analysis,
            "required_agents": agent_coordination["required_agents"],
            "workflow_plan": agent_coordination["workflow_plan"],
            "estimated_complexity": agent_coordination["complexity"],
            "estimated_duration": agent_coordination["estimated_duration"],
            "success_factors": agent_coordination["success_factors"],
            "risk_factors": agent_coordination["risk_factors"],
        }

        return project_analysis

    def _plan_agent_coordination(self, description: str, crean_analysis: dict[str, Any]) -> dict[str, Any]:
        """Plan optimal agent coordination based on project requirements"""

        desc_lower = description.lower()
        required_agents = ["crean_assistant"]  # Always include CreaTech

        # Determine required agents based on description
        if "ui" in desc_lower or "interface" in desc_lower or "prototype" in desc_lower:
            required_agents.append("ui_rapid_prototyper")

        if "code" in desc_lower or "implement" in desc_lower or "build" in desc_lower:
            required_agents.append("code_generator")

        if "test" in desc_lower or "testing" in desc_lower or "quality" in desc_lower:
            required_agents.append("testing_agent")

        if "documentation" in desc_lower or "docs" in desc_lower or "guide" in desc_lower:
            required_agents.append("documentation_agent")

        # Plan workflow phases
        workflow_plan = []
        complexity_score = 0

        if "ui_rapid_prototyper" in required_agents:
            workflow_plan.append(
                {
                    "phase": "UI Prototyping",
                    "agents": ["ui_rapid_prototyper"],
                    "deliverables": ["HTML prototype", "UI specifications", "Interaction design"],
                    "estimated_time": "1-3 days",
                }
            )
            complexity_score += 2

        if "code_generator" in required_agents:
            workflow_plan.append(
                {
                    "phase": "Implementation",
                    "agents": ["code_generator"],
                    "deliverables": ["Source code", "Components", "Integration"],
                    "estimated_time": "3-7 days",
                }
            )
            complexity_score += 3

        if "testing_agent" in required_agents:
            workflow_plan.append(
                {
                    "phase": "Testing & QA",
                    "agents": ["testing_agent"],
                    "deliverables": ["Test suite", "Quality reports", "Bug fixes"],
                    "estimated_time": "2-4 days",
                }
            )
            complexity_score += 1

        if "documentation_agent" in required_agents:
            workflow_plan.append(
                {
                    "phase": "Documentation",
                    "agents": ["documentation_agent"],
                    "deliverables": ["User docs", "API docs", "Deployment guides"],
                    "estimated_time": "1-2 days",
                }
            )
            complexity_score += 1

        # Assess complexity
        if complexity_score <= 3:
            complexity = "Low"
            duration = "1-1 weeks"
        elif complexity_score <= 6:
            complexity = "Medium"
            duration = "1-2 weeks"
        else:
            complexity = "High"
            duration = "2-4 weeks"

        return {
            "required_agents": required_agents,
            "workflow_plan": workflow_plan,
            "complexity": complexity,
            "estimated_duration": duration,
            "success_factors": self._identify_success_factors(description, required_agents),
            "risk_factors": self._identify_risk_factors(description, required_agents),
        }

    def _identify_success_factors(self, description: str, agents: list[str]) -> list[str]:
        """Identify factors that contribute to project success"""
        factors = ["Clear requirements", "Agent coordination", "User feedback integration"]

        desc_lower = description.lower()
        if "simple" in desc_lower or "intuitive" in desc_lower:
            factors.append("User-centered design")
        if "quick" in desc_lower or "rapid" in desc_lower:
            factors.append("Fast iteration cycles")
        if "iterate" in desc_lower:
            factors.append("Iterative refinement")

        return factors

    def _identify_risk_factors(self, description: str, agents: list[str]) -> list[str]:
        """Identify potential risk factors"""
        risks = ["Agent integration complexity", "Scope creep", "Technical debt"]

        desc_lower = description.lower()
        if "complex" in desc_lower:
            risks.append("Over-engineering")
        if "many" in desc_lower or "multiple" in desc_lower:
            risks.append("Feature bloat")
        if len(agents) > 3:
            risks.append("Communication overhead")

        return risks

    async def execute_workflow(self, project_analysis: dict[str, Any]) -> dict[str, Any]:
        """Execute the complete creative workflow using coordinated agents"""

        logger.info(f"🚀 Executing workflow for project {project_analysis['project_id']}")

        workflow_result = {
            "project_id": project_analysis["project_id"],
            "execution_id": str(uuid.uuid4())[:8],
            "start_time": datetime.now().isoformat(),
            "phase_results": {},
            "overall_success": False,
            "deliverables": [],
            "agent_feedback": [],
            "lessons_learned": [],
        }

        try:
            # Execute each phase in the workflow plan
            for phase in project_analysis["workflow_plan"]:
                phase_result = await self._execute_workflow_phase(phase, project_analysis)
                workflow_result["phase_results"][phase["phase"]] = phase_result
                workflow_result["deliverables"].extend(phase_result.get("deliverables", []))

                # Check if phase succeeded before continuing
                if not phase_result.get("success", False):
                    logger.warning(f"Phase {phase['phase']} failed - stopping workflow")
                    break

            workflow_result["overall_success"] = True
            workflow_result["end_time"] = datetime.now().isoformat()

            # Generate lessons learned
            workflow_result["lessons_learned"] = self._generate_lessons_learned(workflow_result)

            # Save to history
            self.workflow_history.append(workflow_result)

            logger.info(f"✅ Workflow execution completed for project {project_analysis['project_id']}")
            return workflow_result

        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {str(e)}")
            workflow_result["error"] = str(e)
            workflow_result["end_time"] = datetime.now().isoformat()
            return workflow_result

    async def _execute_workflow_phase(self, phase: dict[str, Any], project_analysis: dict[str, Any]) -> dict[str, Any]:
        """Execute a single workflow phase using specified agents"""

        phase_name = phase["phase"]
        logger.info(f"🔄 Executing phase: {phase_name}")

        phase_result = {
            "phase": phase_name,
            "success": False,
            "start_time": datetime.now().isoformat(),
            "agent_results": {},
            "deliverables": [],
            "issues": [],
        }

        try:
            for agent_name in phase["agents"]:
                if agent_name in self.agent_registry:
                    agent = self.agent_registry[agent_name]
                    if agent["contact"]:  # Agent is available
                        agent_result = await self._execute_agent_task(agent_name, agent, phase, project_analysis)
                        phase_result["agent_results"][agent_name] = agent_result
                        phase_result["deliverables"].extend(agent_result.get("deliverables", []))
                    else:
                        # Mock result for unavailable agents
                        mock_result = self._create_mock_agent_result(agent_name, phase)
                        phase_result["agent_results"][agent_name] = mock_result
                        phase_result["deliverables"].extend(mock_result.get("deliverables", []))
                        phase_result["issues"].append(f"Agent {agent_name} not available - used mock result")

            phase_result["success"] = True
            phase_result["end_time"] = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"❌ Phase {phase_name} failed: {str(e)}")
            phase_result["error"] = str(e)
            phase_result["end_time"] = datetime.now().isoformat()

        return phase_result

    async def _execute_agent_task(
        self, agent_name: str, agent: dict[str, Any], phase: dict[str, Any], project_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a task using a specific agent"""

        logger.info(f"🤖 Executing task with agent: {agent['name']}")

        if agent_name == "ui_rapid_prototyper":
            return await self._execute_ui_prototyping_task(project_analysis)
        if agent_name == "crean_assistant":
            return await self._execute_crean_task(project_analysis, phase)
        return self._create_mock_agent_result(agent_name, phase)

    async def _execute_ui_prototyping_task(self, project_analysis: dict[str, Any]) -> dict[str, Any]:
        """Execute UI prototyping task"""

        description = project_analysis["description"]
        logger.info("🎨 Creating UI prototype...")

        # Analyze UI requirements
        ui_analysis = await self.ui_prototyper.analyze_ui_requirements(description)

        # Generate UI concepts
        ui_concepts = await self.ui_prototyper.generate_ui_concepts(ui_analysis)

        # Create prototype specification
        if ui_concepts:
            specification = await self.ui_prototyper.create_prototype_specification(ui_concepts[0], ui_analysis)

            # Generate HTML prototype
            prototype_file = await self.ui_prototyper.generate_html_prototype(specification)

            return {
                "success": True,
                "deliverables": [
                    f"UI analysis: {len(ui_analysis['ui_challenges'])} challenges identified",
                    f"Generated {len(ui_concepts)} UI concepts",
                    "Prototype specification created",
                    f"HTML prototype: {prototype_file}",
                ],
                "metrics": {
                    "concepts_generated": len(ui_concepts),
                    "confidence_score": ui_concepts[0]["confidence_score"] if ui_concepts else 0,
                    "prototype_complexity": ui_concepts[0]["prototype_complexity"] if ui_concepts else "Unknown",
                },
                "files": [prototype_file] if "prototype_file" in locals() else [],
            }
        return {"success": False, "deliverables": [], "error": "No UI concepts generated"}

    async def _execute_crean_task(self, project_analysis: dict[str, Any], phase: dict[str, Any]) -> dict[str, Any]:
        """Execute CreaTech task based on phase"""

        description = project_analysis["description"]
        phase_name = phase["phase"]

        if "UI" in phase_name:
            # CreaTech assists with creative analysis for UI
            analysis = await self.crean_assistant.analyze_requirement(description)
            concepts = await self.crean_assistant.generate_creative_concepts(analysis)

            return {
                "success": True,
                "deliverables": [
                    "Creative-technical analysis completed",
                    f"Generated {len(concepts)} creative concepts",
                    "Design thinking approach applied",
                ],
                "insights": {
                    "domain": analysis["domain_classification"]["primary_domain"],
                    "synthesis_potential": analysis["synthesis_potential"],
                    "creative_opportunities": analysis["creative_opportunities"],
                },
            }
        # General CreaTech synthesis
        synthesis = await self.crean_assistant.synthesize_solution(description)

        return {
            "success": True,
            "deliverables": [
                "Creative-technical synthesis completed",
                f"Method: {synthesis.synthesis_method}",
                f"Confidence: {synthesis.confidence_score:.2f}",
            ],
            "insights": {
                "synthesis_method": synthesis.synthesis_method,
                "confidence_score": synthesis.confidence_score,
                "feasibility_score": synthesis.feasibility_score,
            },
        }

    def _create_mock_agent_result(self, agent_name: str, phase: dict[str, Any]) -> dict[str, Any]:
        """Create mock result for unavailable agents"""

        agent = self.agent_registry[agent_name]

        return {
            "success": True,
            "deliverables": [
                f"Mock {phase['phase']} deliverables for {agent['name']}",
                f"Simulated results based on {agent['capabilities'][0]}",
            ],
            "mock": True,
            "note": f"Agent {agent_name} not yet implemented - using placeholder results",
        }

    def _generate_lessons_learned(self, workflow_result: dict[str, Any]) -> list[str]:
        """Generate lessons learned from workflow execution"""

        lessons = []

        # Analyze phase results
        for phase_name, phase_result in workflow_result["phase_results"].items():
            if phase_result.get("success", False):
                lessons.append(f"{phase_name} phase completed successfully")
            else:
                lessons.append(f"{phase_name} phase encountered issues")

            # Check for mock results
            for agent_name, agent_result in phase_result.get("agent_results", {}).items():
                if agent_result.get("mock", False):
                    lessons.append(f"Agent {agent_name} needs implementation for full functionality")

        # General lessons
        if workflow_result["overall_success"]:
            lessons.append("Multi-agent coordination can produce comprehensive solutions")
            lessons.append("Creative-technical synthesis provides valuable insights")
        else:
            lessons.append("Workflow execution needs refinement for better reliability")

        return lessons

    async def create_comprehensive_project_plan(self, project_description: str) -> dict[str, Any]:
        """Create comprehensive project plan using all available creative-technical intelligence"""

        logger.info(f"📋 Creating comprehensive project plan: {project_description}")

        # Analyze requirements
        project_analysis = await self.analyze_project_requirements(project_description)

        # Use CreaTech for creative-technical synthesis
        synthesis_result = await self.crean_assistant.synthesize_solution(project_description)

        # Create comprehensive plan
        comprehensive_plan = {
            "project_id": project_analysis["project_id"],
            "description": project_description,
            "created_at": datetime.now().isoformat(),
            "strategic_analysis": {
                "domain_classification": project_analysis["crean_analysis"]["domain_classification"],
                "creative_opportunities": project_analysis["crean_analysis"]["creative_opportunities"],
                "technical_considerations": self._extract_technical_considerations(project_analysis),
                "innovation_potential": self._assess_innovation_potential(project_analysis, synthesis_result),
            },
            "execution_plan": {
                "workflow_phases": project_analysis["workflow_plan"],
                "agent_coordination": project_analysis["required_agents"],
                "estimated_timeline": project_analysis["estimated_duration"],
                "complexity_assessment": project_analysis["estimated_complexity"],
            },
            "creative_technical_synthesis": {
                "synthesis_method": synthesis_result.synthesis_method,
                "confidence_score": synthesis_result.confidence_score,
                "feasibility_score": synthesis_result.feasibility_score,
                "creative_elements": synthesis_result.creative_elements,
                "technical_elements": synthesis_result.technical_elements,
            },
            "success_metrics": self._define_success_metrics(project_analysis, synthesis_result),
            "risk_mitigation": self._define_risk_mitigation(project_analysis),
            "next_steps": self._define_next_steps(project_analysis),
        }

        return comprehensive_plan

    def _extract_technical_considerations(self, project_analysis: dict[str, Any]) -> list[str]:
        """Extract technical considerations from project analysis"""
        considerations = []

        # From CreaTech analysis
        crean_analysis = project_analysis["crean_analysis"]
        if "technical_constraints" in crean_analysis:
            considerations.extend(crean_analysis["technical_constraints"])

        # From agent coordination
        for agent_name in project_analysis["required_agents"]:
            if agent_name == "ui_rapid_prototyper":
                considerations.extend(
                    ["Frontend framework selection", "Responsive design", "User interaction patterns"]
                )
            elif agent_name == "code_generator":
                considerations.extend(["Backend architecture", "Database design", "API development"])
            elif agent_name == "testing_agent":
                considerations.extend(["Test automation", "Quality assurance", "Performance testing"])

        return list(set(considerations))  # Remove duplicates

    def _assess_innovation_potential(self, project_analysis: dict[str, Any], synthesis_result) -> str:
        """Assess innovation potential"""
        synthesis_score = synthesis_result.confidence_score
        domain = project_analysis["crean_analysis"]["domain_classification"]["primary_domain"]

        if synthesis_score > 0.8 and domain != "general":
            return "High - Strong creative-technical synthesis potential"
        if synthesis_score > 0.6:
            return "Medium - Good opportunities for innovation"
        return "Standard - Focus on reliable implementation"

    def _define_success_metrics(self, project_analysis: dict[str, Any], synthesis_result) -> list[str]:
        """Define success metrics for the project"""
        metrics = [
            "User satisfaction score > 4.0/5.0",
            "Technical implementation meets requirements",
            "Creative elements enhance user experience",
            "Project completed within estimated timeline",
        ]

        # Add specific metrics based on project type
        if "ui_rapid_prototyper" in project_analysis["required_agents"]:
            metrics.append("UI prototype receives positive user feedback")
            metrics.append("Design iteration cycles < 3")

        if synthesis_result.feasibility_score > 0.8:
            metrics.append("Technical feasibility validated through implementation")

        return metrics

    def _define_risk_mitigation(self, project_analysis: dict[str, Any]) -> list[str]:
        """Define risk mitigation strategies"""
        mitigations = [
            "Regular stakeholder feedback sessions",
            "Incremental development approach",
            "Clear success criteria definition",
        ]

        # Address specific risks
        for risk in project_analysis["risk_factors"]:
            if "Agent integration" in risk:
                mitigations.append("Robust agent communication protocols")
            elif "Scope creep" in risk:
                mitigations.append("Strict change management process")
            elif "Over-engineering" in risk:
                mitigations.append("Regular simplicity reviews")

        return mitigations

    def _define_next_steps(self, project_analysis: dict[str, Any]) -> list[str]:
        """Define immediate next steps"""
        steps = ["Review and approve project plan", "Set up development environment", "Begin first workflow phase"]

        # Add specific next steps
        if project_analysis["workflow_plan"]:
            first_phase = project_analysis["workflow_plan"][0]
            steps.append(f"Prepare for {first_phase['phase']} phase")

        if "ui_rapid_prototyper" in project_analysis["required_agents"]:
            steps.append("Gather UI requirements and user preferences")

        return steps

    async def interactive_session(self):
        """Run interactive session for comprehensive project planning"""

        print("\n🎭 Creative Workflow Orchestrator")
        print("🚀 Multi-Agent Creative-Technical Coordination")
        print("=" * 60)

        while True:
            print("\n🎯 What would you like to do?")
            print("1. Analyze project requirements")
            print("2. Create comprehensive project plan")
            print("3. Execute complete workflow")
            print("4. Run UI rapid prototyping")
            print("5. View workflow history")
            print("6. Exit")

            choice = input("\nEnter your choice (1-6): ").strip()

            if choice == "1":
                description = input("Describe your project: ").strip()
                analysis = await self.analyze_project_requirements(description)

                print("\n📊 Project Analysis:")
                print(f"   Project ID: {analysis['project_id']}")
                print(f"   Required Agents: {', '.join(analysis['required_agents'])}")
                print(f"   Complexity: {analysis['estimated_complexity']}")
                print(f"   Estimated Duration: {analysis['estimated_duration']}")
                print(f"   Workflow Phases: {len(analysis['workflow_plan'])}")

            elif choice == "2":
                description = input("Describe your project for comprehensive planning: ").strip()
                plan = await self.create_comprehensive_project_plan(description)

                print("\n📋 Comprehensive Project Plan:")
                print(f"   Project ID: {plan['project_id']}")
                print(f"   Domain: {plan['strategic_analysis']['domain_classification']['primary_domain']}")
                print(f"   Innovation Potential: {plan['strategic_analysis']['innovation_potential']}")
                print(f"   Synthesis Method: {plan['creative_technical_synthesis']['synthesis_method']}")
                print(f"   Confidence Score: {plan['creative_technical_synthesis']['confidence_score']:.1%}")

                # Save plan
                plan_file = self.workspace / f"project-plan-{plan['project_id']}.json"
                with open(plan_file, "w") as f:
                    json.dump(plan, f, indent=2, default=str)
                print(f"   📄 Plan saved to: {plan_file}")

            elif choice == "3":
                description = input("Describe the project to execute: ").strip()
                analysis = await self.analyze_project_requirements(description)

                print("\n🚀 Executing workflow...")
                result = await self.execute_workflow(analysis)

                if result["overall_success"]:
                    print("✅ Workflow completed successfully!")
                    print(f"   Phases completed: {len(result['phase_results'])}")
                    print(f"   Deliverables: {len(result['deliverables'])}")
                    print(f"   Lessons learned: {len(result['lessons_learned'])}")
                else:
                    print("❌ Workflow encountered issues")
                    if "error" in result:
                        print(f"   Error: {result['error']}")

            elif choice == "4":
                description = input("Describe the UI you want to prototype: ").strip()
                ui_result = await self._execute_ui_prototyping_task({"description": description})

                if ui_result["success"]:
                    print("\n✅ UI Prototyping completed!")
                    for deliverable in ui_result["deliverables"]:
                        print(f"   • {deliverable}")
                else:
                    print(f"❌ UI prototyping failed: {ui_result.get('error', 'Unknown error')}")

            elif choice == "5":
                if self.workflow_history:
                    print(f"\n📚 Workflow History ({len(self.workflow_history)} projects):")
                    for i, workflow in enumerate(self.workflow_history[-5:], 1):  # Show last 5
                        status = "✅" if workflow["overall_success"] else "❌"
                        print(
                            f"   {i}. {status} {workflow['project_id']} - {len(workflow['deliverables'])} deliverables"
                        )
                else:
                    print("\n📚 No workflow history yet.")

            elif choice == "6":
                print("\n👋 Thanks for using the Creative Workflow Orchestrator!")
                break
            else:
                print("Invalid choice. Please try again.")


# CLI interface
def main():
    """Main CLI interface for Creative Workflow Orchestrator"""
    parser = argparse.ArgumentParser(description="Creative Workflow Orchestrator - Multi-Agent Coordination")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--project", help="Project description to analyze")
    parser.add_argument("--plan", action="store_true", help="Create comprehensive project plan")
    parser.add_argument("--execute", action="store_true", help="Execute complete workflow")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    async def run_cli():
        orchestrator = CreativeWorkflowOrchestrator()

        if args.interactive:
            await orchestrator.interactive_session()
        elif args.project and args.plan:
            plan = await orchestrator.create_comprehensive_project_plan(args.project)
            print(json.dumps(plan, indent=2, default=str))
        elif args.project and args.execute:
            analysis = await orchestrator.analyze_project_requirements(args.project)
            result = await orchestrator.execute_workflow(analysis)
            print(json.dumps(result, indent=2, default=str))
        else:
            parser.print_help()

    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
