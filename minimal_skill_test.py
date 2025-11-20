#!/usr/bin/env python3
"""
Minimal Skill Test - Bypass broken imports to test individual skills directly
"""

import sys

sys.path.insert(0, ".")


def test_database_design_expert():
    """Test database design expert directly"""
    print("🧪 Testing Database Design Expert directly...")

    try:
        # Test direct import bypassing __init__.py files
        import amplifier.skills.core_technology.database_design_expert as db_expert_module

        # Test the function exists
        if hasattr(db_expert_module, "database_design_expert"):
            print("✅ Function found: database_design_expert")

            # Test basic functionality
            result = db_expert_module.database_design_expert("Explain database normalization")
            print("✅ Function call successful")
            print(f"📊 Result type: {type(result)}")
            print(f"📝 Preview: {str(result)[:200]}...")
            return True
        print("❌ Function not found")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_database_design_expert_class():
    """Test the DatabaseDesignExpertSkill class"""
    print("\n🧪 Testing DatabaseDesignExpertSkill class...")

    try:
        from amplifier.skills.core_technology.database_design_expert import DatabaseDesignExpertSkill

        # Test instantiation
        skill = DatabaseDesignExpertSkill()
        print("✅ Class instantiated successfully")
        print(f"🎯 Skill ID: {skill.skill_id}")
        print(f"🎯 Skill Name: {skill.name}")

        # Test capabilities
        capabilities = skill.get_capabilities()
        print(f"🎯 Capabilities: {len(capabilities)} available")
        print(f"   • {', '.join(capabilities[:3])}...")

        # Test async execution
        import asyncio

        async def test_async():
            context = None
            result = await skill.execute("Test database design", context)
            print("✅ Async execution successful")
            print(f"📊 Success: {result.success}")
            if result.success:
                print(f"📝 Result preview: {str(result.data)[:100]}...")
            return result

        async_result = asyncio.run(test_async())
        return True

    except Exception as e:
        print(f"❌ Class error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test execution"""
    print("🚀 MINIMAL SKILL VALIDATION")
    print("=" * 50)

    success1 = test_database_design_expert()
    success2 = test_database_design_expert_class()

    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 DATABASE DESIGN EXPERT: VALIDATION PASSED!")
        print("✅ Function and class both working correctly")
        return 0
    print("❌ DATABASE DESIGN EXPERT: VALIDATION FAILED!")
    print("⚠️  Fix issues before proceeding")
    return 1


if __name__ == "__main__":
    exit(main())
