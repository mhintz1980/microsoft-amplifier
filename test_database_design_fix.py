#!/usr/bin/env python3
"""
Test script to validate DatabaseDesignExpertSkill fixes
"""

import asyncio
import os
import sys

# Add the amplifier directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "amplifier"))

from amplifier.skills.core_technology.database_design_expert import DatabaseDesignExpertSkill
from amplifier.skills.core_technology.database_design_expert import database_design_expert
from amplifier.skills.core_technology.database_design_expert import database_design_expert_instance


async def test_function_interface():
    """Test the direct function interface"""
    print("Testing function interface...")

    try:
        # Test direct function call
        result = await database_design_expert("How do I design a database schema for an e-commerce application?")
        print(f"✅ Function interface works! Length: {len(result)} characters")
        print(f"First 100 characters: {result[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Function interface failed: {e}")
        return False


async def test_class_interface():
    """Test the class async execute method"""
    print("\nTesting class interface...")

    try:
        # Test class instantiation and execute
        skill = DatabaseDesignExpertSkill()
        result = await skill.execute("What are the best practices for SQL query optimization?")

        if result.success:
            print(f"✅ Class interface works! Length: {len(result.data)} characters")
            print(f"First 100 characters: {result.data[:100]}...")
        else:
            print(f"❌ Class interface returned error: {result.error}")
            return False

        return True
    except Exception as e:
        print(f"❌ Class interface failed: {e}")
        return False


async def test_instance_interface():
    """Test the pre-created instance"""
    print("\nTesting pre-created instance interface...")

    try:
        # Test pre-created instance
        result = await database_design_expert_instance.execute("Explain NoSQL vs SQL databases")

        if result.success:
            print(f"✅ Instance interface works! Length: {len(result.data)} characters")
            print(f"First 100 characters: {result.data[:100]}...")
        else:
            print(f"❌ Instance interface returned error: {result.error}")
            return False

        return True
    except Exception as e:
        print(f"❌ Instance interface failed: {e}")
        return False


async def test_validation_methods():
    """Test input validation methods"""
    print("\nTesting validation methods...")

    try:
        skill = DatabaseDesignExpertSkill()

        # Test valid input
        valid = await skill.validate_input("What is database normalization?")
        print(f"✅ Valid input validation: {valid}")

        # Test invalid inputs
        invalid_empty = await skill.validate_input("")
        print(f"✅ Empty string validation: {invalid_empty}")

        invalid_none = await skill.validate_input(None)
        print(f"✅ None validation: {invalid_none}")

        return True
    except Exception as e:
        print(f"❌ Validation methods failed: {e}")
        return False


async def test_capabilities():
    """Test capabilities method"""
    print("\nTesting capabilities method...")

    try:
        skill = DatabaseDesignExpertSkill()
        capabilities = skill.get_capabilities()
        print(f"✅ Capabilities: {len(capabilities)} capabilities found")
        print(f"First few: {capabilities[:3]}")
        return True
    except Exception as e:
        print(f"❌ Capabilities method failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("DATABASE DESIGN EXPERT SKILL VALIDATION")
    print("=" * 60)

    tests = [
        test_function_interface,
        test_class_interface,
        test_instance_interface,
        test_validation_methods,
        test_capabilities,
    ]

    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("🎉 ALL TESTS PASSED! DatabaseDesignExpertSkill is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
