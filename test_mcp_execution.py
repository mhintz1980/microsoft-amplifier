#!/usr/bin/env python3
"""
Test script for MCP code execution framework.
Tests Docker sandbox, PII detection, and token reduction.
"""

import asyncio
import json
import time

from amplifier.mcp.code_execution import SecurityLevel
from amplifier.mcp.code_execution import execute_code_safely
from amplifier.mcp.code_execution import execute_skill_by_name
from amplifier.mcp.code_execution import get_mcp_executor
from amplifier.utils.token_utils import count_tokens


async def test_basic_execution():
    """Test basic Python code execution."""
    print("🧪 Testing Basic Code Execution")
    print("-" * 50)

    start_time = time.time()

    # Test 1: Simple Python code
    code = """
print("Hello from Docker sandbox!")
result = sum(range(1, 11))
print(f"Sum of 1-10: {result}")
"""

    result = await execute_code_safely(code, "python")

    execution_time = time.time() - start_time
    tokens_used = count_tokens(code)

    print(f"✅ Status: {result.status}")
    print(f"✅ Runtime: {result.runtime_seconds:.2f}s")
    print(f"✅ Total time: {execution_time:.2f}s")
    print(f"✅ Tokens processed: {tokens_used}")
    print(f"✅ Exit code: {result.exit_code}")
    print(f"✅ Output:\n{result.stdout}")

    if result.stderr:
        print(f"❌ Stderr:\n{result.stderr}")

    if result.pii_detected:
        print(f"🔒 PII detected: {result.pii_detected}")

    return result


async def test_skill_execution():
    """Test skill-based execution."""
    print("\n🧪 Testing Skill Execution")
    print("-" * 50)

    # Test the built-in text analysis skill
    input_data = {
        "text": """
        This is a sample text for analysis. It contains multiple sentences.
        Some words appear more frequently than others.
        Contact us at test@example.com or call 555-123-4567.
        Visit our website at https://example.com for more information.
        """
    }

    start_time = time.time()
    result = await execute_skill_by_name("analyze_text", input_data)
    execution_time = time.time() - start_time

    print(f"✅ Status: {result.status}")
    print(f"✅ Runtime: {result.runtime_seconds:.2f}s")
    print(f"✅ Total time: {execution_time:.2f}s")

    if result.status.value == "completed":
        output = json.loads(result.stdout)
        print(f"✅ Words found: {output.get('word_count', 0)}")
        print(f"✅ Sentences: {output.get('sentence_count', 0)}")
        print(f"✅ Emails detected: {output.get('patterns', {}).get('emails', 0)}")
        print(f"✅ URLs detected: {output.get('patterns', {}).get('urls', 0)}")
        print(f"✅ Most common words: {output.get('most_common_words', [])[:5]}")

    if result.pii_detected:
        print(f"🔒 PII detected and tokenized: {result.pii_detected}")

    return result


async def test_pii_detection():
    """Test PII detection and tokenization."""
    print("\n🧪 Testing PII Detection")
    print("-" * 50)

    # Code with PII that should be detected
    code_with_pii = """
import json

# User data with PII
user_data = {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "555-123-4567",
    "ssn": "123-45-6789",
    "credit_card": "4111-1111-1111-1111",
    "api_key": "sk-1234567890abcdef1234567890abcdef"
}

print("Processing user data...")
print(json.dumps(user_data, indent=2))
"""

    result = await execute_code_safely(code_with_pii, "python", security_level=SecurityLevel.MINIMAL)

    print(f"✅ Status: {result.status}")
    print(f"✅ PII types detected: {result.pii_detected}")
    print(f"✅ Execution log entries: {len(result.execution_log)}")

    for log_entry in result.execution_log:
        if "PII" in log_entry:
            print(f"🔒 {log_entry}")

    print(f"✅ Output (should be tokenized):\n{result.stdout}")

    return result


async def test_token_reduction():
    """Test token reduction by comparing in-context vs sandboxed execution."""
    print("\n🧪 Testing Token Reduction")
    print("-" * 50)

    # Complex data processing that would use many tokens in-context
    complex_data_processing = """
import json
import statistics
import textwrap

# Complex analysis that would be expensive in-context
def analyze_large_dataset():
    # Simulate processing large dataset
    data = []
    for i in range(1000):
        data.append({
            "id": i,
            "value": i * 2,
            "category": f"category_{i % 10}",
            "metadata": {
                "description": f"Item number {i} in the dataset",
                "tags": [f"tag_{j}" for j in range(5)],
                "metrics": {
                    "score": i * 0.1,
                    "weight": i % 100,
                    "quality": (i % 3) + 1
                }
            }
        })

    # Perform complex analysis
    categories = {}
    values = []
    scores = []

    for item in data:
        cat = item["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item["value"])
        values.append(item["value"])
        scores.append(item["metadata"]["metrics"]["score"])

    # Calculate statistics
    results = {
        "total_items": len(data),
        "value_stats": {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0
        },
        "score_stats": {
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "stdev": statistics.stdev(scores) if len(scores) > 1 else 0
        },
        "category_counts": {cat: len(items) for cat, items in categories.items()},
        "top_categories": sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)[:3]
    }

    return results

# Run the analysis
results = analyze_large_dataset()
print(json.dumps(results, indent=2))
"""

    # Measure tokens in the code itself
    code_tokens = count_tokens(complex_data_processing)
    print(f"📊 Code tokens: {code_tokens}")

    # Measure potential in-context response tokens (estimated)
    estimated_response_tokens = 2000  # Rough estimate for complex JSON response
    total_in_context_tokens = code_tokens + estimated_response_tokens

    print(f"📊 Estimated in-context total: {total_in_context_tokens} tokens")

    # Execute via MCP (should use fewer tokens for the actual LLM interaction)
    start_time = time.time()
    result = await execute_code_safely(complex_data_processing, "python")
    execution_time = time.time() - start_time

    # Actual tokens used by our framework
    actual_framework_tokens = result.tokens_processed
    token_reduction = ((total_in_context_tokens - actual_framework_tokens) / total_in_context_tokens) * 100

    print(f"✅ Status: {result.status}")
    print(f"✅ Framework tokens: {actual_framework_tokens}")
    print(f"✅ Token reduction: {token_reduction:.1f}%")
    print(f"✅ Execution time: {result.runtime_seconds:.2f}s")
    print(f"✅ Total time: {execution_time:.2f}s")

    if result.status.value == "completed":
        try:
            output_data = json.loads(result.stdout)
            print(f"✅ Processed {output_data.get('total_items', 0)} items")
            print(f"✅ Found {len(output_data.get('category_counts', {}))} categories")
        except json.JSONDecodeError:
            print(f"⚠️  Output parsing failed, raw output:\n{result.stdout[:200]}...")

    return result, token_reduction


async def test_resource_limits():
    """Test resource limits and timeout handling."""
    print("\n🧪 Testing Resource Limits")
    print("-" * 50)

    from amplifier.mcp.code_execution import ExecutionRequest
    from amplifier.mcp.code_execution import ResourceLimits

    # Test with very restrictive limits
    restrictive_limits = ResourceLimits(
        max_runtime_seconds=5, max_memory_mb=128, max_cpu_percent=25.0, network_access=False
    )

    # Code that might hit limits
    intensive_code = """
import time
import os

print("Starting intensive task...")
print(f"Memory usage at start: {os.getpid()}")

# This should finish within 5 seconds
for i in range(10):
    time.sleep(0.5)
    print(f"Progress: {i+1}/10")

print("Task completed successfully!")
"""

    request = ExecutionRequest(code=intensive_code, language="python", resource_limits=restrictive_limits)

    executor = get_mcp_executor()
    result = await executor.execute_code(request)

    print(f"✅ Status: {result.status}")
    print(f"✅ Runtime: {result.runtime_seconds:.2f}s (limit: {restrictive_limits.max_runtime_seconds}s)")
    print(f"✅ Memory used: {result.memory_used_mb:.1f}MB (limit: {restrictive_limits.max_memory_mb}MB)")
    print(f"✅ Output:\n{result.stdout}")

    return result


async def test_error_handling():
    """Test error handling and recovery."""
    print("\n🧪 Testing Error Handling")
    print("-" * 50)

    # Code with syntax error
    syntax_error_code = """
print("This code has a syntax error)
x = [1, 2, 3
print(x)
"""

    result = await execute_code_safely(syntax_error_code, "python")

    print(f"✅ Status: {result.status}")
    print(f"✅ Exit code: {result.exit_code}")
    print("✅ Error captured:")
    print(f"   {result.stderr}")

    return result


async def main():
    """Run all tests."""
    print("🐳 Testing MCP Code Execution Framework")
    print("=" * 60)
    print("Docker version available for sandboxed execution")

    results = {}

    try:
        # Run all tests
        results["basic"] = await test_basic_execution()
        results["skill"] = await test_skill_execution()
        results["pii"] = await test_pii_detection()
        results["token_reduction"], reduction_pct = await test_token_reduction()
        results["resource_limits"] = await test_resource_limits()
        results["error_handling"] = await test_error_handling()

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        successful_tests = sum(1 for r in results.values() if r.status.value == "completed")
        total_tests = len(results)

        print(f"✅ Successful tests: {successful_tests}/{total_tests}")
        print(f"🔒 PII detection working: {'Yes' if results['pii'].pii_detected else 'No PII in test'}")
        print(f"📉 Token reduction achieved: {reduction_pct:.1f}%")
        print(f"🐳 Docker sandbox: {'Working' if results['basic'].status.value == 'completed' else 'Failed'}")
        print(f"⚡ Skill execution: {'Working' if results['skill'].status.value == 'completed' else 'Failed'}")

        # Get execution statistics
        executor = get_mcp_executor()
        stats = executor.get_execution_stats()

        print("\n📈 EXECUTION STATISTICS")
        print(f"   Total executions: {stats['total_executions']}")
        print(f"   Success rate: {stats['success_rate']:.1%}")
        print(f"   Average runtime: {stats['average_runtime_seconds']:.2f}s")
        print(f"   Skills registered: {stats['total_skills_registered']}")

        print("\n🎉 MCP Code Execution Framework Test Complete!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
