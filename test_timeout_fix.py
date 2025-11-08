#!/usr/bin/env python3
"""Test the fixed timeout handling."""

import asyncio

from amplifier.mcp.code_execution import ExecutionRequest
from amplifier.mcp.code_execution import ResourceLimits
from amplifier.mcp.code_execution import get_mcp_executor


async def test_timeout_fixed():
    """Test that timeout handling now works correctly."""
    print("🧪 Testing Fixed Timeout Handling")
    print("-" * 50)

    # Short timeout test (2 seconds)
    limits = ResourceLimits(max_runtime_seconds=2, max_memory_mb=128, network_access=False)

    # Code that takes 5 seconds
    code = """
import time
print("Starting 5-second task...")
for i in range(5):
    time.sleep(1)
    print(f"Progress: {i+1}/5")
print("Task completed!")
"""

    request = ExecutionRequest(code=code, language="python", resource_limits=limits)

    executor = get_mcp_executor()
    result = await executor.execute_code(request)

    print(f"✅ Status: {result.status}")
    print(f"✅ Runtime: {result.runtime_seconds:.2f}s (limit: {limits.max_runtime_seconds}s)")
    print(f"✅ Timeout detected: {'Yes' if result.status.value == 'timeout' else 'No'}")
    print(f"✅ Error message: {result.stderr}")

    return result.status.value == "timeout"


if __name__ == "__main__":
    success = asyncio.run(test_timeout_fixed())
    print(f"\n🎯 Timeout fix {'SUCCESSFUL' if success else 'FAILED'}")
