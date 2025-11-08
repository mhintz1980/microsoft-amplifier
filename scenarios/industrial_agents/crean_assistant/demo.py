#!/usr/bin/env python3
"""
CreaTech Assistant Demo Script

Demonstrates CreaTech Assistant's creative-technical synthesis capabilities
and multi-agent workflow orchestration.
"""

import asyncio
import time

from main_assistant import CreaTechAssistant


async def demo_crean_capabilities():
    """Demonstrate CreaTech Assistant capabilities"""

    print("🎨 CreaTech Assistant Demonstration")
    print("=" * 60)
    print("Creative Development Agent - Blending Technical Precision with Artistic Intelligence")
    print()

    assistant = CreaTechAssistant()

    # Demo 1: Requirement Analysis and Creative Concepts
    print("📊 Demo 1: Requirement Analysis & Creative Concepts")
    print("-" * 50)

    requirement = "Create an innovative weather dashboard with beautiful visualizations"
    print(f"Requirement: {requirement}")

    start_time = time.time()
    analysis = await assistant.analyze_requirement(requirement)
    concepts = await assistant.generate_creative_concepts(analysis)

    print("\n🔍 Analysis Results:")
    print(f"   Primary Domain: {analysis['domain_classification']['primary_domain']}")
    print(f"   Creative Opportunities: {', '.join(analysis['creative_opportunities'])}")
    print(f"   Synthesis Potential: {analysis['synthesis_potential']:.2f}")

    print("\n💡 Generated Creative Concepts:")
    for i, concept in enumerate(concepts, 1):
        print(f"   {i}. {concept['concept_name']}")
        print(f"      Impact: {concept['estimated_impact']:.2f}")

    print(f"\n⏱️  Analysis completed in {time.time() - start_time:.1f}s")

    # Demo 2: Solution Synthesis
    print("\n🚀 Demo 2: Creative-Technical Solution Synthesis")
    print("-" * 50)

    start_time = time.time()
    synthesis_result = await assistant.synthesize_solution(requirement)

    print("🎯 Synthesis Results:")
    print(f"   Method: {synthesis_result.synthesis_method}")
    print(f"   Confidence: {synthesis_result.confidence_score:.2f}")
    print(f"   Feasibility: {synthesis_result.feasibility_score:.2f}")
    print(f"   Creative Elements: {', '.join(synthesis_result.creative_elements)}")

    print(f"\n⏱️  Synthesis completed in {time.time() - start_time:.1f}s")

    # Demo 3: Multi-Agent Workflows
    print("\n🤝 Demo 3: Multi-Agent Workflow Orchestration")
    print("-" * 50)

    workflows = [
        {
            "name": "Creative Web Application",
            "requirement": "Build a portfolio website for creative professionals",
            "workflow": "webapp",
        },
        {
            "name": "Innovative Documentation",
            "requirement": "Create API documentation with interactive examples",
            "workflow": "documentation",
        },
        {"name": "Creative CAD Design", "requirement": "Design an ergonomic computer mouse", "workflow": "cad"},
    ]

    results = {}

    for workflow in workflows:
        print(f"\n🔧 Running {workflow['name']} Workflow...")
        print(f"   Requirement: {workflow['requirement']}")

        start_time = time.time()

        if workflow["workflow"] == "webapp":
            result = await assistant.run_creative_web_application_workflow(workflow["requirement"])
        elif workflow["workflow"] == "documentation":
            result = await assistant.run_innovative_documentation_workflow(workflow["requirement"])
        elif workflow["workflow"] == "cad":
            result = await assistant.run_creative_cad_workflow(workflow["requirement"])

        results[workflow["name"]] = result

        print("   ✅ Workflow completed")
        print(f"   📊 Quality Score: {result['quality_score']:.2f}")
        print(f"   ⏱️  Execution Time: {result['execution_time']:.1f}s")
        print(f"   🎯 Workflow: {result['workflow_name']}")

    # Demo 4: Integration Analysis
    print("\n🔗 Demo 4: Multi-Agent Integration Analysis")
    print("-" * 50)

    total_quality = sum(r["quality_score"] for r in results.values())
    avg_quality = total_quality / len(results)

    print("📈 Performance Metrics:")
    print(f"   Total Workflows: {len(results)}")
    print(f"   Average Quality Score: {avg_quality:.2f}")
    print(f"   Components Available: {assistant.creative_engineer is not None}")
    print(f"   Synthesis Available: {assistant.synthesizer is not None}")
    print(f"   Workflows Available: {assistant.workflows is not None}")

    # Summary
    print("\n🎉 Demo Summary")
    print("=" * 60)
    print("✅ Requirement Analysis: Domain classification and creative opportunity identification")
    print("✅ Creative Concept Generation: Multiple approaches with impact scoring")
    print("✅ Solution Synthesis: Creative-technical integration with confidence scoring")
    print("✅ Multi-Agent Workflows: CAD, Documentation, and Web Application workflows")
    print("✅ Quality Assessment: Automated scoring and recommendations")
    print("✅ Agent Lightning Integration: Training infrastructure ready")

    print("\n🚀 CreaTech Assistant successfully demonstrated creative-technical synthesis!")
    print(f"   Average workflow quality: {avg_quality:.2f}")
    print("   All workflows completed successfully")

    return results


async def interactive_demo():
    """Interactive demo where user can input their own requirements"""

    print("\n🎮 Interactive CreaTech Demo")
    print("=" * 60)
    print("Try CreaTech Assistant with your own requirements!")
    print()

    assistant = CreaTechAssistant()

    while True:
        print("\nWhat would you like to explore?")
        print("1. Analyze a requirement")
        print("2. Run a complete workflow")
        print("3. Exit interactive demo")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            requirement = input("Enter your requirement: ").strip()
            if requirement:
                print(f"\n🔍 Analyzing: {requirement}")
                analysis = await assistant.analyze_requirement(requirement)
                concepts = await assistant.generate_creative_concepts(analysis)

                print(f"   Domain: {analysis['domain_classification']['primary_domain']}")
                print(f"   Creative opportunities: {', '.join(analysis['creative_opportunities'])}")
                print(f"   Generated {len(concepts)} concepts")

                for concept in concepts[:2]:  # Show top 2
                    print(f"   • {concept['concept_name']} (impact: {concept['estimated_impact']:.2f})")

        elif choice == "2":
            requirement = input("Enter your project requirement: ").strip()
            if requirement:
                print("\nChoose workflow type:")
                print("1. Web Application")
                print("2. Documentation")
                print("3. CAD Design")

                workflow_choice = input("Enter workflow type (1-3): ").strip()

                if workflow_choice == "1":
                    result = await assistant.run_creative_web_application_workflow(requirement)
                elif workflow_choice == "2":
                    result = await assistant.run_innovative_documentation_workflow(requirement)
                elif workflow_choice == "3":
                    result = await assistant.run_creative_cad_workflow(requirement)
                else:
                    print("Invalid choice")
                    continue

                print("\n✅ Workflow completed!")
                print(f"   Quality Score: {result['quality_score']:.2f}")
                print(f"   Execution Time: {result['execution_time']:.1f}s")
                print("   Top Recommendations:")
                for rec in result["recommendations"][:2]:
                    print(f"   • {rec}")

        elif choice == "3":
            print("\n👋 Thanks for trying CreaTech Assistant!")
            break

        else:
            print("Invalid choice. Please try again.")


async def main():
    """Main demo function"""
    print("🎨 CreaTech Assistant Demonstration Suite")
    print("=" * 60)
    print("Creative Development Agent for Multi-Agent Workflows")
    print()

    choice = input("Choose demo type:\n1. Automated Demo\n2. Interactive Demo\nEnter choice (1-2): ").strip()

    if choice == "1":
        await demo_crean_capabilities()
    elif choice == "2":
        await interactive_demo()
    else:
        print("Invalid choice. Running automated demo...")
        await demo_crean_capabilities()


if __name__ == "__main__":
    asyncio.run(main())
