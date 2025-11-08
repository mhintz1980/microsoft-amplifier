#!/usr/bin/env python3
"""
Practical Examples for Mechanical Engineering Agent Workflows

Demonstrates real-world usage of the multi-framework integration system
for mechanical engineering applications including CAD analysis, safety review,
manufacturing assessment, and quality control.

Following amplifier philosophy:
- Real-world practical examples
- Simple but comprehensive demonstrations
- Modular workflows that can be extended
- Clear separation of concerns
"""

import asyncio
import json
from dataclasses import dataclass
from typing import Any

from amplifier.utils.logger import get_logger

from .advanced_adapters import DataFormat
from .advanced_adapters import EngineeringData
from .advanced_adapters import EngineeringDomain
from .advanced_adapters import create_mechanical_engineering_pipeline
from .framework_agnostic_layer import TaskDefinition
from .framework_agnostic_layer import TaskType
from .framework_agnostic_layer import UniversalAgentManager
from .framework_agnostic_layer import create_mechanical_engineering_tasks
from .framework_optimizations import OptimizationStrategy
from .interoperability_layer import HybridOrchestrator
from .interoperability_layer import MigrationAnalyzer
from .interoperability_layer import create_mechanical_engineering_hybrid_architecture

# Import our framework integration components
from .multi_framework_integration import MultiFrameworkOrchestrator
from .multi_framework_integration import create_multi_framework_system

logger = get_logger(__name__)


@dataclass
class CADAnalysisRequest:
    """Request for CAD analysis workflow."""

    cad_file_path: str
    analysis_type: str  # "manufacturability", "safety", "cost", "assembly"
    requirements: list[str]
    constraints: list[str]
    priority: str = "normal"


@dataclass
class SafetyReviewRequest:
    """Request for safety review workflow."""

    design_description: str
    safety_standards: list[str]  # ISO, OSHA, ASME, etc.
    risk_factors: list[str]
    operating_conditions: dict[str, Any]
    priority: str = "high"


@dataclass
class ManufacturingAssessmentRequest:
    """Request for manufacturing assessment workflow."""

    part_specifications: dict[str, Any]
    available_processes: list[str]  # CNC, 3D printing, injection molding, etc.
    volume_requirements: dict[str, int]
    cost_targets: dict[str, float]
    priority: str = "normal"


class MechanicalEngineeringWorkflows:
    """Collection of practical mechanical engineering workflows."""

    def __init__(self):
        self.orchestrator: MultiFrameworkOrchestrator | None = None
        self.agent_manager: UniversalAgentManager | None = None
        self.hybrid_orchestrator: HybridOrchestrator | None = None

    async def initialize_frameworks(self, frameworks: list[str] = None):
        """Initialize the agent frameworks for engineering workflows."""
        if frameworks is None:
            frameworks = ["langchain", "openai_sdk", "autogen", "crewai"]

        logger.info(f"Initializing frameworks: {frameworks}")

        # Create multi-framework system
        self.orchestrator = await create_multi_framework_system(frameworks)

        # Create universal agent manager
        self.agent_manager = UniversalAgentManager()

        # Add agents to universal manager
        for framework in frameworks:
            config = {
                "id": f"{framework}_mech_engineer",
                "framework": framework,
                "model_config": {"model": "gpt-3.5-turbo", "temperature": 0.1},
                "tool_config": [
                    {"name": "cad_analyzer", "description": "Analyze CAD files"},
                    {"name": "safety_checker", "description": "Check safety compliance"},
                    {"name": "manufacturing_assessor", "description": "Assess manufacturing feasibility"},
                ],
            }
            await self.agent_manager.add_agent(framework, config)

        await self.agent_manager.start_system()
        logger.info("Framework initialization completed")

    async def initialize_hybrid_architecture(self):
        """Initialize hybrid architecture for complex workflows."""
        self.hybrid_orchestrator = HybridOrchestrator()

        # Register mock agents (in real implementation, these would be actual framework agents)
        for framework in ["langchain", "openai_sdk", "autogen", "crewai"]:
            self.hybrid_orchestrator.register_framework_agent(framework, f"{framework}_agent")

        # Create mechanical engineering hybrid architecture
        architecture = create_mechanical_engineering_hybrid_architecture()
        self.hybrid_orchestrator.create_hybrid_architecture("mech_engineering_hybrid", architecture)

        logger.info("Hybrid architecture initialized")

    async def cad_analysis_workflow(self, request: CADAnalysisRequest) -> dict[str, Any]:
        """Execute CAD analysis workflow using multiple frameworks."""
        logger.info(f"Starting CAD analysis: {request.cad_file_path}")

        # Create task for CAD analysis
        TaskDefinition(
            task_type=TaskType.DESIGN_REVIEW,
            description=f"Analyze CAD file for {request.analysis_type}",
            requirements=request.requirements,
            constraints=request.constraints,
            domain_context={
                "domain": "mechanical_engineering",
                "cad_file": request.cad_file_path,
                "analysis_type": request.analysis_type,
            },
            priority=request.priority,
        )

        # Execute with all frameworks
        if self.orchestrator:
            results = await self.orchestrator.execute_all_frameworks(
                f"Analyze CAD file {request.cad_file_path} for {request.analysis_type}"
            )

            # Process and compare results
            analysis_results = {}
            for framework, interaction in results.items():
                analysis_results[framework] = {
                    "recommendation": interaction.output_message,
                    "confidence": interaction.metadata.get("confidence", 0.5),
                    "tools_used": interaction.tools_used,
                    "reasoning": interaction.reasoning_steps,
                }

            # Find best result
            best_framework = max(analysis_results.items(), key=lambda x: x[1]["confidence"])[0]

            return {
                "workflow_type": "cad_analysis",
                "cad_file": request.cad_file_path,
                "analysis_type": request.analysis_type,
                "best_result": analysis_results[best_framework],
                "selected_framework": best_framework,
                "all_results": analysis_results,
                "success": True,
            }

        return {"error": "Orchestrator not initialized", "success": False}

    async def safety_review_workflow(self, request: SafetyReviewRequest) -> dict[str, Any]:
        """Execute safety review workflow using hybrid architecture."""
        logger.info(f"Starting safety review with standards: {request.safety_standards}")

        if not self.hybrid_orchestrator:
            # Fallback to single framework
            return await self._fallback_safety_review(request)

        # Create task for safety review
        task = {
            "type": "safety_analysis",
            "input": f"Safety review for: {request.design_description}",
            "safety_standards": request.safety_standards,
            "risk_factors": request.risk_factors,
            "operating_conditions": request.operating_conditions,
            "priority": request.priority,
        }

        # Execute with hybrid architecture
        result = await self.hybrid_orchestrator.execute_with_architecture("mech_engineering_hybrid", task)

        return {
            "workflow_type": "safety_review",
            "design_description": request.design_description,
            "safety_standards": request.safety_standards,
            "result": result,
            "success": result.get("success", False),
        }

    async def _fallback_safety_review(self, request: SafetyReviewRequest) -> dict[str, Any]:
        """Fallback safety review using single framework."""
        if not self.agent_manager:
            return {"error": "No agent system available", "success": False}

        task = TaskDefinition(
            task_type=TaskType.SAFETY_ANALYSIS,
            description=f"Safety review for design according to {request.safety_standards}",
            requirements=[
                f"Compliance with {', '.join(request.safety_standards)}",
                "Risk assessment for identified factors",
                "Safety recommendations",
            ],
            constraints=request.operating_conditions,
            domain_context={
                "domain": "safety_engineering",
                "standards": request.safety_standards,
                "risk_factors": request.risk_factors,
            },
            priority=request.priority,
        )

        result = await self.agent_manager.scheduler.execute_task(task)

        return {
            "workflow_type": "safety_review",
            "design_description": request.design_description,
            "safety_standards": request.safety_standards,
            "result": result.__dict__,
            "success": result.success,
        }

    async def manufacturing_assessment_workflow(self, request: ManufacturingAssessmentRequest) -> dict[str, Any]:
        """Execute manufacturing assessment workflow."""
        logger.info(f"Starting manufacturing assessment for processes: {request.available_processes}")

        # Create engineering data for manufacturing analysis
        engineering_data = EngineeringData(
            content=request.part_specifications,
            format=DataFormat.SPREADSHEET_XLSX,
            domain=EngineeringDomain.MANUFACTURING,
            metadata={
                "available_processes": request.available_processes,
                "volume_requirements": request.volume_requirements,
                "cost_targets": request.cost_targets,
            },
        )

        # Create pipeline for data processing
        pipeline = create_mechanical_engineering_pipeline()

        # Process the engineering data
        await pipeline.process_engineering_data([engineering_data])

        # Create task for manufacturing assessment
        task = TaskDefinition(
            task_type=TaskType.MANUFACTURING_ASSESSMENT,
            description="Assess manufacturing feasibility and recommend optimal process",
            requirements=[
                "Process compatibility analysis",
                "Cost estimation",
                "Quality considerations",
                "Production timeline",
            ],
            constraints={
                "max_cost_per_part": request.cost_targets.get("max_per_part", 1000),
                "min_quality": 0.95,
                "available_processes": request.available_processes,
            },
            domain_context={
                "domain": "manufacturing",
                "volume": request.volume_requirements,
                "cost_targets": request.cost_targets,
            },
        )

        # Execute with agent system
        if self.agent_manager:
            result = await self.agent_manager.scheduler.execute_task(task)

            return {
                "workflow_type": "manufacturing_assessment",
                "part_specifications": request.part_specifications,
                "recommended_process": result.output,
                "cost_analysis": result.metadata.get("cost_analysis", {}),
                "quality_assessment": result.metadata.get("quality_assessment", {}),
                "result": result.__dict__,
                "success": result.success,
            }

        return {"error": "Agent system not available", "success": False}

    async def comprehensive_design_review(self, design_data: dict[str, Any]) -> dict[str, Any]:
        """Execute comprehensive design review using all available capabilities."""
        logger.info("Starting comprehensive design review")

        # Create multiple tasks for different aspects
        tasks = create_mechanical_engineering_tasks()

        # Add design-specific context to all tasks
        for task in tasks:
            task.domain_context.update(design_data)

        # Execute all tasks
        if self.agent_manager:
            results = await self.agent_manager.execute_workflow(tasks)

            # Process results
            review_summary = {
                "design_overview": design_data.get("description", "No description"),
                "task_results": [],
                "overall_assessment": {},
                "recommendations": [],
            }

            for i, result in enumerate(results):
                task_type = tasks[i].task_type.value
                review_summary["task_results"].append(
                    {
                        "task_type": task_type,
                        "success": result.success,
                        "output": result.output,
                        "confidence": result.confidence,
                    }
                )

                # Collect recommendations
                if result.output and "recommend" in result.output.lower():
                    review_summary["recommendations"].append(result.output)

            # Calculate overall assessment
            successful_tasks = sum(1 for r in results if r.success)
            review_summary["overall_assessment"] = {
                "completion_rate": successful_tasks / len(results),
                "average_confidence": sum(r.confidence for r in results) / len(results),
                "critical_issues": [r for r in results if not r.success],
            }

            return {
                "workflow_type": "comprehensive_design_review",
                "review_summary": review_summary,
                "success": successful_tasks > 0,
            }

        return {"error": "Agent system not available", "success": False}

    async def framework_migration_demo(self) -> dict[str, Any]:
        """Demonstrate framework migration capabilities."""
        logger.info("Starting framework migration demonstration")

        # Create sample agent profile
        from .interoperability_layer import AgentProfile

        profile = AgentProfile(
            agent_id="mech_design_agent_001",
            name="Mechanical Design Specialist",
            description="Specialized agent for mechanical design and analysis",
            capabilities=["cad_analysis", "design_optimization", "material_selection", "manufacturing_assessment"],
            current_framework="langchain",
            performance_metrics={"accuracy": 0.87, "latency": 1.5, "success_rate": 0.92},
            configuration={"model": "gpt-3.5-turbo", "temperature": 0.1, "specialization": "mechanical_engineering"},
        )

        # Analyze migration options
        analyzer = MigrationAnalyzer()
        migration_options = {}

        for target_framework in ["openai_sdk", "autogen", "crewai"]:
            plan = analyzer.analyze_migration_feasibility(profile, target_framework)
            migration_options[target_framework] = {
                "success_probability": plan.estimated_success_rate,
                "estimated_time": plan.estimated_time,
                "compatibility_issues": plan.compatibility_issues,
                "migration_steps": len(plan.migration_steps),
            }

        # Select best migration target
        best_target = max(migration_options.items(), key=lambda x: x[1]["success_probability"])[0]

        return {
            "workflow_type": "framework_migration_demo",
            "original_profile": {
                "agent_id": profile.agent_id,
                "name": profile.name,
                "current_framework": profile.current_framework,
                "capabilities": profile.capabilities,
            },
            "migration_options": migration_options,
            "recommended_target": best_target,
            "recommendation_reason": f"Highest success probability: {migration_options[best_target]['success_probability']:.2f}",
        }


# Example usage and demonstration functions


async def demonstrate_cad_analysis():
    """Demonstrate CAD analysis workflow."""
    workflows = MechanicalEngineeringWorkflows()
    await workflows.initialize_frameworks(["langchain", "openai_sdk"])

    # Create CAD analysis request
    request = CADAnalysisRequest(
        cad_file_path="designs/engine_block.step",
        analysis_type="manufacturability",
        requirements=[
            "Check CNC machining feasibility",
            "Assess material requirements",
            "Evaluate assembly complexity",
        ],
        constraints=["Maximum material cost: $500", "Tolerance: ±0.1mm", "Lead time: < 2 weeks"],
        priority="high",
    )

    # Execute workflow
    result = await workflows.cad_analysis_workflow(request)
    print("CAD Analysis Result:")
    print(json.dumps(result, indent=2))

    return result


async def demonstrate_safety_review():
    """Demonstrate safety review workflow."""
    workflows = MechanicalEngineeringWorkflows()
    await workflows.initialize_frameworks(["autogen", "crewai"])
    await workflows.initialize_hybrid_architecture()

    # Create safety review request
    request = SafetyReviewRequest(
        design_description="Pressure vessel for industrial compressed air system",
        safety_standards=["ASME Boiler and Pressure Vessel Code", "OSHA 1910.169"],
        risk_factors=["High pressure (150 PSI)", "Cyclic loading", "Corrosive environment"],
        operating_conditions={"pressure": 150, "temperature": 80, "environment": "indoor"},
        priority="critical",
    )

    # Execute workflow
    result = await workflows.safety_review_workflow(request)
    print("Safety Review Result:")
    print(json.dumps(result, indent=2))

    return result


async def demonstrate_manufacturing_assessment():
    """Demonstrate manufacturing assessment workflow."""
    workflows = MechanicalEngineeringWorkflows()
    await workflows.initialize_frameworks(["langchain", "crewai"])

    # Create manufacturing assessment request
    request = ManufacturingAssessmentRequest(
        part_specifications={
            "material": "Aluminum 6061-T6",
            "dimensions": {"length": 100, "width": 50, "height": 25},
            "tolerances": {"general": 0.1, "critical": 0.05},
            "surface_finish": "Ra 1.6",
        },
        available_processes=["CNC_machining", "3D_printing", "injection_molding"],
        volume_requirements={"prototype": 10, "production": 10000},
        cost_targets={"prototype_max": 50, "production_max": 5},
    )

    # Execute workflow
    result = await workflows.manufacturing_assessment_workflow(request)
    print("Manufacturing Assessment Result:")
    print(json.dumps(result, indent=2))

    return result


async def demonstrate_comprehensive_review():
    """Demonstrate comprehensive design review."""
    workflows = MechanicalEngineeringWorkflows()
    await workflows.initialize_frameworks(["langchain", "openai_sdk", "autogen", "crewai"])

    # Design data for review
    design_data = {
        "description": "Automotive suspension component",
        "material": "Steel 4140",
        "critical_features": ["Load bearing", "Fatigue resistance", "Weight optimization"],
        "constraints": ["Cost < $25", "Weight < 500g", "Safety factor > 2.0"],
        "requirements": ["ISO 9001", "Automotive industry standards"],
    }

    # Execute comprehensive review
    result = await workflows.comprehensive_design_review(design_data)
    print("Comprehensive Design Review Result:")
    print(json.dumps(result, indent=2))

    return result


async def demonstrate_training_optimization():
    """Demonstrate training optimization for mechanical engineering."""
    from .framework_optimizations import optimize_all_frameworks_for_mechanical_engineering

    # Create sample training data
    training_data = [
        {
            "task_type": "cad_analysis",
            "input": "Analyze bracket design for CNC machining",
            "expected_output": "Machinable with standard tooling",
            "domain": "mechanical_engineering",
        },
        {
            "task_type": "safety_review",
            "input": "Review pressure vessel design",
            "expected_output": "Complies with ASME standards",
            "domain": "safety_engineering",
        },
    ]

    # Optimize frameworks
    results = await optimize_all_frameworks_for_mechanical_engineering(
        training_data, OptimizationStrategy.REINFORCEMENT_LEARNING
    )

    print("Training Optimization Results:")
    for result in results:
        print(f"{result.framework}: {result.improvement_percentage:.2f}% improvement")

    return results


async def run_all_demonstrations():
    """Run all workflow demonstrations."""
    print("=== Mechanical Engineering Workflow Demonstrations ===\n")

    demonstrations = [
        ("CAD Analysis", demonstrate_cad_analysis),
        ("Safety Review", demonstrate_safety_review),
        ("Manufacturing Assessment", demonstrate_manufacturing_assessment),
        ("Comprehensive Design Review", demonstrate_comprehensive_review),
        ("Training Optimization", demonstrate_training_optimization),
    ]

    results = {}
    for name, demo_func in demonstrations:
        print(f"\n--- {name} Demo ---")
        try:
            result = await demo_func()
            results[name] = {"success": True, "result": result}
            print(f"✓ {name} completed successfully")
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            results[name] = {"success": False, "error": str(e)}

    print("\n=== Summary ===")
    successful = sum(1 for r in results.values() if r["success"])
    print(f"Successful demonstrations: {successful}/{len(demonstrations)}")

    return results


if __name__ == "__main__":
    """Run demonstrations when script is executed directly."""
    asyncio.run(run_all_demonstrations())
