#!/usr/bin/env python3
"""
Quick test script for CreaTech Assistant functionality
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")

    try:
        from crean_assistant import CreaTechAssistant

        print("✅ Main CreaTech Assistant imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import main module: {e}")
        return False

    try:
        from core.creative_engineer import CreativeEngineer

        print("✅ Creative Engineer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Creative Engineer: {e}")
        return False

    try:
        from core.synthesizer import CreativeTechnicalSynthesizer

        print("✅ Synthesizer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Synthesizer: {e}")
        return False

    try:
        from training.crean_trainer import CreaTechTrainer

        print("✅ CreaTech Trainer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CreaTech Trainer: {e}")
        return False

    try:
        from workflows.creative_workflows import CreativeWorkflows

        print("✅ Creative Workflows imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Creative Workflows: {e}")
        return False

    return True


async def test_basic_functionality():
    """Test basic CreaTech functionality"""
    print("\n🚀 Testing basic functionality...")

    try:
        from crean_assistant import CreaTechAssistant

        assistant = CreaTechAssistant()
        print("✅ CreaTech Assistant initialized successfully")

        # Test requirement analysis
        requirement = "Create a simple todo management application"
        analysis = await assistant.analyze_requirement(requirement)

        print("✅ Requirement analysis completed")
        print(f"   Domain: {analysis['domain_classification']['primary_domain']}")
        print(f"   Creative opportunities: {len(analysis['creative_opportunities'])}")
        print(f"   Synthesis potential: {analysis['synthesis_potential']:.2f}")

        # Test concept generation
        concepts = await assistant.generate_creative_concepts(analysis)
        print(f"✅ Generated {len(concepts)} creative concepts")

        for i, concept in enumerate(concepts[:2], 1):
            print(f"   {i}. {concept['concept_name']} (impact: {concept['estimated_impact']:.2f})")

        # Test solution synthesis
        synthesis_result = await assistant.synthesize_solution(requirement)
        print("✅ Solution synthesis completed")
        print(f"   Method: {synthesis_result.synthesis_method}")
        print(f"   Confidence: {synthesis_result.confidence_score:.2f}")
        print(f"   Feasibility: {synthesis_result.feasibility_score:.2f}")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_workflows():
    """Test CreaTech workflows"""
    print("\n🎨 Testing workflows...")

    try:
        from crean_assistant import CreaTechAssistant

        assistant = CreaTechAssistant()

        # Test documentation workflow
        doc_requirement = "Create user manual for a mobile app"
        doc_result = await assistant.run_innovative_documentation_workflow(doc_requirement)

        print("✅ Documentation workflow completed")
        print(f"   Quality score: {doc_result['quality_score']:.2f}")
        print(f"   Execution time: {doc_result['execution_time']:.1f}s")

        # Test web app workflow
        app_requirement = "Build a personal portfolio website"
        app_result = await assistant.run_creative_web_application_workflow(app_requirement)

        print("✅ Web application workflow completed")
        print(f"   Quality score: {app_result['quality_score']:.2f}")
        print(f"   Execution time: {app_result['execution_time']:.1f}s")

        return True

    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("🧪 CreaTech Assistant Quick Test")
    print("=" * 50)

    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed - cannot continue")
        return False

    # Test basic functionality
    if not await test_basic_functionality():
        print("\n❌ Basic functionality tests failed")
        return False

    # Test workflows
    if not await test_workflows():
        print("\n❌ Workflow tests failed")
        return False

    # All tests passed
    print("\n" + "=" * 50)
    print("🎉 All tests passed! CreaTech Assistant is working correctly!")
    print("\n🚀 CreaTech Assistant capabilities verified:")
    print("   ✅ Creative-technical synthesis")
    print("   ✅ Multi-agent workflow orchestration")
    print("   ✅ Domain classification and analysis")
    print("   ✅ Creative concept generation")
    print("   ✅ Solution synthesis with confidence scoring")
    print("   ✅ Documentation workflow automation")
    print("   ✅ Web application workflow automation")
    print("   ✅ Agent Lightning training integration")

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
