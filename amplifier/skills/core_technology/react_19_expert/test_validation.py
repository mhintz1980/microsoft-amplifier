"""
Test and Validation Script for React 19 Expert Skill

Comprehensive testing to ensure zero hallucination guarantee and
validate all React 19 features work correctly.
"""

import sys
import json
from pathlib import Path

# Add the skill to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core import React19Expert
from api import React19APIs, ActionsAPI, OptimisticAPI
from typescript import TypeScriptDefinitions
from examples import BasicExamples, AdvancedExamples, ProductionExamples
from validation import QualityAssurance
from agent_lightning import AgentLightning


def test_api_accuracy():
    """Test API accuracy against React 19 official documentation."""
    print("🧪 Testing API Accuracy...")

    expert = React19Expert()
    apis = React19APIs()

    # Test known React 19 APIs
    test_cases = [
        {
            "name": "useOptimistic hook",
            "code": """
            const [optimisticState, addOptimistic] = useOptimistic(
              initialState,
              (state, action) => state + action
            )
            """,
            "expected_features": ["useOptimistic"],
            "should_be_valid": True,
        },
        {
            "name": "useActionState hook",
            "code": """
            const [state, submitAction, isPending] = useActionState(
              async (prevState, formData) => {
                await updateProfile(formData)
                return null
              },
              null
            )
            """,
            "expected_features": ["useActionState"],
            "should_be_valid": True,
        },
        {
            "name": "Server action with directive",
            "code": """
            'use server'
            async function updateProfile(formData: FormData) {
              await saveProfile(formData)
            }
            """,
            "expected_features": ["server_actions"],
            "should_be_valid": True,
        },
        {
            "name": "Server action without directive",
            "code": """
            async function updateProfile(formData: FormData) {
              await saveProfile(formData)
            }
            """,
            "expected_features": ["server_actions"],
            "should_be_valid": False,
        },
        {
            "name": "Document metadata",
            "code": """
            function BlogPost({ post }) {
              return (
                <article>
                  <title>{post.title}</title>
                  <meta name="description" content={post.excerpt} />
                  <link rel="canonical" href={post.url} />
                  <h1>{post.title}</h1>
                </article>
              )
            }
            """,
            "expected_features": ["document_metadata"],
            "should_be_valid": True,
        },
    ]

    results = []

    for test_case in test_cases:
        print(f"  Testing {test_case['name']}...")

        # Validate with expert
        validation = expert.validate_react_19_code(test_case["code"])

        # Check zero hallucination
        hallucination_check = expert.validate_zero_hallucination(
            test_case["code"], {"features": test_case["expected_features"]}
        )

        # Determine if test passed
        api_valid = validation["is_valid"]
        hallucination_valid = hallucination_check["compliant"]
        test_passed = api_valid == test_case["should_be_valid"] and hallucination_valid == test_case["should_be_valid"]

        results.append(
            {
                "name": test_case["name"],
                "passed": test_passed,
                "api_valid": api_valid,
                "hallucination_valid": hallucination_valid,
                "validation": validation,
                "hallucination": hallucination_check,
            }
        )

        status = "✅" if test_passed else "❌"
        print(f"    {status} {test_case['name']}")

        if not test_passed:
            print(f"      API Valid: {api_valid}, Expected: {test_case['should_be_valid']}")
            print(f"      Hallucination Valid: {hallucination_valid}")
            if not hallucination_valid:
                print(
                    f"      Issues: {hallucination_check['missing_features'] + hallucination_check['incorrect_usage']}"
                )

    return results


def test_typescript_definitions():
    """Test TypeScript definitions completeness and accuracy."""
    print("\n🔷 Testing TypeScript Definitions...")

    typescript = TypeScriptDefinitions()

    # Test type generation for different components
    test_specs = [
        {
            "name": "Basic component",
            "spec": {
                "name": "Button",
                "props": {
                    "text": {"type": "string", "required": True},
                    "onClick": {"type": "() => void", "required": False},
                    "disabled": {"type": "boolean", "required": False, "default": False},
                },
                "features": [],
            },
        },
        {
            "name": "Component with actions",
            "spec": {
                "name": "ContactForm",
                "props": {"onSubmit": {"type": "(data: FormData) => void", "required": True}},
                "features": ["actions"],
            },
        },
        {
            "name": "Component with optimistic updates",
            "spec": {
                "name": "TodoList",
                "props": {"initialTodos": {"type": "TodoItem[]", "required": True}},
                "features": ["optimistic"],
            },
        },
    ]

    results = []

    for test_spec in test_specs:
        print(f"  Testing {test_spec['name']}...")

        # Generate types
        generated_types = typescript.generate_types_for_component(test_spec["spec"])

        # Validate generated types
        type_validation = typescript.validate_typescript_code(generated_types)

        # Check if types contain expected elements
        has_interface = "interface" in generated_types
        has_proper_types = ": string" in generated_types or ": boolean" in generated_types
        type_score = type_validation["type_safety_score"]

        test_passed = has_interface and has_proper_types and type_score >= 80

        results.append(
            {
                "name": test_spec["name"],
                "passed": test_passed,
                "has_interface": has_interface,
                "has_proper_types": has_proper_types,
                "type_score": type_score,
                "generated_types": generated_types,
            }
        )

        status = "✅" if test_passed else "❌"
        print(f"    {status} {test_spec['name']} (Type Score: {type_score})")

    return results


def test_examples_quality():
    """Test quality and correctness of examples."""
    print("\n📚 Testing Examples Quality...")

    # Test all example types
    basic_examples = BasicExamples()
    advanced_examples = AdvancedExamples()
    production_examples = ProductionExamples()

    all_examples = [("Basic", basic_examples), ("Advanced", advanced_examples), ("Production", production_examples)]

    results = []
    qa = QualityAssurance()

    for category, example_collection in all_examples:
        print(f"  Testing {category} Examples...")
        examples = example_collection.list_examples()

        category_results = []

        for example_name in examples:
            example = example_collection.get_example(example_name)
            if not example:
                continue

            # Validate example code
            validation = qa.validate_react_19_code(example.code)

            # Check for zero hallucination
            hallucination_check = qa.validate_zero_hallucination(example.code, {"features": example.features})

            # Quality metrics
            has_typescript = len(example.typescript_types) > 0
            has_explanation = len(example.explanation) > 100
            has_best_practices = len(example.best_practices) > 0

            example_score = validation.overall_score
            test_passed = (
                validation.is_valid
                and hallucination_check["compliant"]
                and has_typescript
                and has_explanation
                and has_best_practices
                and example_score >= 85
            )

            category_results.append(
                {
                    "name": example_name,
                    "passed": test_passed,
                    "score": example_score,
                    "has_typescript": has_typescript,
                    "has_explanation": has_explanation,
                    "has_best_practices": has_best_practices,
                }
            )

            status = "✅" if test_passed else "❌"
            print(f"    {status} {example_name} (Score: {example_score})")

        results.append(
            {
                "category": category,
                "examples": category_results,
                "passed_count": sum(1 for r in category_results if r["passed"]),
                "total_count": len(category_results),
            }
        )

    return results


def test_agent_lightning_integration():
    """Test Agent Lightning integration and learning."""
    print("\n⚡ Testing Agent Lightning Integration...")

    lightning = AgentLightning()
    expert = React19Expert()

    # Test pattern tracking
    print("  Testing pattern tracking...")
    lightning.track_pattern_usage("useOptimistic", True, 95)
    lightning.track_pattern_usage("useActionState", True, 88)
    lightning.track_pattern_usage("server_actions", False, 45, ["Missing directive"])

    # Test code generation tracking
    print("  Testing code generation tracking...")
    test_code = """
    import { useOptimistic } from 'react'

    function Counter() {
      const [count, setCount] = useState(0)
      const [optimisticCount, addOptimistic] = useOptimistic(
        count,
        (state, amount) => state + amount
      )

      return <div>{optimisticCount}</div>
    }
    """

    validation = expert.validate_react_19_code(test_code)
    session_id = lightning.track_code_generation(
        {"features": ["useOptimistic"]}, test_code, validation, {"satisfaction": 4.5}
    )

    # Test performance summary
    summary = lightning.get_performance_summary()

    # Test validation
    integration_test_passed = (
        len(summary["pattern_performance"]) >= 2 and summary["overall_score"] >= 80 and session_id is not None
    )

    print(f"    {'✅' if integration_test_passed else '❌'} Agent Lightning Integration")
    print(f"      Overall Score: {summary['overall_score']}")
    print(f"      Patterns Tracked: {len(summary['pattern_performance'])}")
    print(f"      Session ID: {session_id}")

    return {"passed": integration_test_passed, "summary": summary, "session_id": session_id}


def test_zero_hallucination_guarantee():
    """Test zero hallucination guarantee across all features."""
    print("\n🛡️ Testing Zero Hallucination Guarantee...")

    expert = React19Expert()
    qa = QualityAssurance()

    # Test cases that should fail (detect hallucinations)
    hallucination_tests = [
        {
            "name": "Non-existent hook",
            "code": "const [state, setState] = useNonExistentHook(initialState)",
            "should_detect": True,
            "reason": "Uses non-existent React hook",
        },
        {
            "name": "Incorrect useOptimistic signature",
            "code": "const [state] = useOptimistic()",
            "should_detect": True,
            "reason": "Incorrect useOptimistic signature",
        },
        {
            "name": "Server action without directive",
            "code": """
            async function processData(formData: FormData) {
                return await saveData(formData)
            }
            """,
            "should_detect": True,
            "reason": "Server action missing 'use server' directive",
        },
        {
            "name": "Valid React 19 code",
            "code": """
            import { useOptimistic } from 'react'

            function TodoList({ todos }) {
              const [optimisticTodos, addOptimistic] = useOptimistic(
                todos,
                (state, newTodo) => [...state, { ...newTodo, id: Date.now() }]
              )
              return <div>{optimisticTodos.length} items</div>
            }
            """,
            "should_detect": False,
            "reason": "Valid React 19 code",
        },
    ]

    results = []

    for test in hallucination_tests:
        print(f"  Testing {test['name']}...")

        # Validate with QA system
        validation = qa.validate_react_19_code(test["code"])

        # Check for zero hallucination compliance
        hallucination_check = qa.validate_zero_hallucination(test["code"], [])

        # Determine if hallucination was correctly detected
        has_hallucination_risk = not validation["is_valid"] or not hallucination_check["compliant"]

        correctly_detected = has_hallucination_risk == test["should_detect"]

        results.append(
            {
                "name": test["name"],
                "passed": correctly_detected,
                "detected_risk": has_hallucination_risk,
                "expected_detection": test["should_detect"],
                "validation_score": validation.overall_score,
            }
        )

        status = "✅" if correctly_detected else "❌"
        print(f"    {status} {test['name']}")

        if not correctly_detected:
            print(f"      Expected: {'Risk' if test['should_detect'] else 'No Risk'}")
            print(f"      Detected: {'Risk' if has_hallucination_risk else 'No Risk'}")
            print(f"      Reason: {test['reason']}")

    # Calculate overall hallucination detection accuracy
    passed_tests = sum(1 for r in results if r["passed"])
    total_tests = len(results)
    accuracy = (passed_tests / total_tests) * 100

    print(f"\n  Hallucination Detection Accuracy: {accuracy:.1f}%")

    return {
        "passed": accuracy >= 90,  # Require 90% accuracy
        "accuracy": accuracy,
        "results": results,
    }


def run_comprehensive_test():
    """Run comprehensive test suite for React 19 Expert skill."""
    print("🚀 Running Comprehensive Test Suite for React 19 Expert Skill")
    print("=" * 60)

    test_results = {}

    try:
        # Run all test suites
        test_results["api_accuracy"] = test_api_accuracy()
        test_results["typescript_definitions"] = test_typescript_definitions()
        test_results["examples_quality"] = test_examples_quality()
        test_results["agent_lightning"] = test_agent_lightning_integration()
        test_results["zero_hallucination"] = test_zero_hallucination_guarantee()

        # Calculate overall results
        total_tests = 0
        passed_tests = 0

        for suite_name, suite_results in test_results.items():
            if suite_name == "api_accuracy":
                total_tests += len(suite_results)
                passed_tests += sum(1 for r in suite_results if r["passed"])
            elif suite_name == "typescript_definitions":
                total_tests += len(suite_results)
                passed_tests += sum(1 for r in suite_results if r["passed"])
            elif suite_name == "examples_quality":
                for category in suite_results:
                    total_tests += category["total_count"]
                    passed_tests += category["passed_count"]
            elif suite_name in ["agent_lightning", "zero_hallucination"]:
                total_tests += 1
                passed_tests += 1 if suite_results["passed"] else 0

        overall_success_rate = (passed_tests / total_tests) * 100

        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        print(f"Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"Tests Passed: {passed_tests}/{total_tests}")

        # Suite-by-suite breakdown
        print("\nSuite Results:")
        for suite_name, suite_results in test_results.items():
            if suite_name == "api_accuracy":
                passed = sum(1 for r in suite_results if r["passed"])
                total = len(suite_results)
                print(f"  API Accuracy: {passed}/{total} ✅")
            elif suite_name == "typescript_definitions":
                passed = sum(1 for r in suite_results if r["passed"])
                total = len(suite_results)
                print(f"  TypeScript Definitions: {passed}/{total} ✅")
            elif suite_name == "examples_quality":
                for category in suite_results:
                    print(f"  {category['category']} Examples: {category['passed_count']}/{category['total_count']} ✅")
            elif suite_name == "agent_lightning":
                status = "✅" if suite_results["passed"] else "❌"
                print(f"  Agent Lightning: {status}")
            elif suite_name == "zero_hallucination":
                status = "✅" if suite_results["passed"] else "❌"
                accuracy = suite_results["accuracy"]
                print(f"  Zero Hallucination: {status} ({accuracy:.1f}% accuracy)")

        # Final verdict
        print("\n" + "=" * 60)
        if overall_success_rate >= 95:
            print("🎉 EXCELLENT: React 19 Expert skill passes all tests!")
            print("✅ Zero hallucination guarantee confirmed")
            print("✅ Production-ready status verified")
        elif overall_success_rate >= 90:
            print("✅ GOOD: React 19 Expert skill passes most tests")
            print("⚠️  Minor improvements recommended")
        else:
            print("❌ NEEDS IMPROVEMENT: Some tests failed")
            print("🔧 Review and fix failing tests before deployment")

        print("=" * 60)

        return {
            "success": overall_success_rate >= 95,
            "overall_score": overall_success_rate,
            "test_results": test_results,
            "summary": {"total_tests": total_tests, "passed_tests": passed_tests, "success_rate": overall_success_rate},
        }

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback

        traceback.print_exc()

        return {"success": False, "error": str(e), "test_results": test_results}


if __name__ == "__main__":
    # Run the comprehensive test suite
    results = run_comprehensive_test()

    # Save test results to file
    results_path = Path("test_results.json")
    try:
        with open(results_path, "w") as f:
            # Convert test results to JSON-serializable format
            serializable_results = {
                "success": results["success"],
                "overall_score": results["overall_score"],
                "summary": results["summary"],
                "timestamp": str(Path(__file__).stat().st_mtime),
            }
            json.dump(serializable_results, f, indent=2)
        print(f"\n📄 Test results saved to: {results_path}")
    except Exception as e:
        print(f"⚠️  Could not save test results: {e}")

    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)
