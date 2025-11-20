#!/usr/bin/env python3
"""
Direct test of DatabaseDesignExpertSkill without importing other broken modules
"""

import asyncio
import os
import sys

# Add the amplifier directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "amplifier"))

# Import directly from the specific file to avoid other broken imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "amplifier", "skills", "core_technology"))

from database_design_expert import DatabaseDesignExpertSkill
from database_design_expert import database_design_expert


async def test_basic_functionality():
    """Test basic functionality"""
    print("Testing DatabaseDesignExpertSkill basic functionality...")

    try:
        # Test 1: Class instantiation
        print("\n1. Testing class instantiation...")
        skill = DatabaseDesignExpertSkill()
        print(f"✅ Skill instantiated: {skill.name}")
        print(f"   Skill ID: {skill.skill_id}")
        print(f"   Description: {skill.description[:100]}...")

        # Test 2: Validation method
        print("\n2. Testing input validation...")
        valid = await skill.validate_input("How do I design a database?")
        print(f"✅ Valid input validation: {valid}")

        invalid_empty = await skill.validate_input("")
        print(f"✅ Empty string validation: {invalid_empty}")

        # Test 3: Capabilities method
        print("\n3. Testing capabilities...")
        capabilities = skill.get_capabilities()
        print(f"✅ Capabilities found: {len(capabilities)}")
        print(f"   First 3: {capabilities[:3]}")

        # Test 4: Simple execution (string input)
        print("\n4. Testing simple execution...")
        result = await skill.execute("What is database normalization?")

        if result.success:
            print("✅ Execution successful!")
            print(f"   Response length: {len(result.data)} characters")
            print(f"   First 100 chars: {result.data[:100]}...")
            print(f"   Tokens used: {result.tokens_used}")
            print(f"   Execution time: {result.execution_time:.4f}s")
        else:
            print(f"❌ Execution failed: {result.error}")
            return False

        # Test 5: Function interface
        print("\n5. Testing function interface...")
        func_result = await database_design_expert("Explain SQL joins")
        print("✅ Function interface works!")
        print(f"   Response length: {len(func_result)} characters")
        print(f"   First 100 chars: {func_result[:100]}...")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run the test"""
    print("=" * 60)
    print("DATABASE DESIGN EXPERT SKILL DIRECT TEST")
    print("=" * 60)

    success = await test_basic_functionality()

    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! The fixes are working correctly.")
    else:
        print("❌ Tests failed. Check output above.")
    print("=" * 60)

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
