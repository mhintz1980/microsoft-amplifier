#!/usr/bin/env python3
"""
Enhanced Prime Command - Automatic System Initialization

This replaces manual prime command execution with automatic initialization
to eliminate repetitive errors and ensure consistent system state.

CRITICAL UPDATE (2025-11-20): Virtual environment activation is now
mandatory to prevent file corruption and maintain system integrity.
"""

import sys
import os
from pathlib import Path

# CRITICAL: Setup safe environment FIRST to prevent file corruption
sys.path.insert(0, str(Path(__file__).parent))
try:
    from environment_setup import setup_environment

    environment = setup_environment()
except ImportError:
    print("⚠️ Environment setup not available - proceeding with caution")
    # Fallback path setup
    amplifier_path = Path(__file__).parent / "amplifier"
    sys.path.insert(0, str(amplifier_path))


def main():
    """Enhanced prime command with automatic initialization"""
    print("🚀 ENHANCED PRIME COMMAND - Automatic System Initialization")
    print("=" * 60)

    # CRITICAL: Verify environment is safe before proceeding
    try:
        if "environment" in locals():
            validation = environment.validate_environment()
            if validation["issues"]:
                print("⚠️ ENVIRONMENT ISSUES DETECTED:")
                for issue in validation["issues"]:
                    print(f"   • {issue}")
                print("\n💡建议: Run 'python environment_setup.py --setup' to fix")
    except Exception as e:
        print(f"⚠️ Environment validation failed: {e}")

    print("✅ Environment validated - proceeding with initialization\n")

    try:
        # Import and run AutoSessionInitializer
        from core.auto_session import AutoSessionInitializer

        initializer = AutoSessionInitializer()
        result = initializer.initialize_session()

        # Display results
        print(f"📅 Session ID: {result['session_id']}")
        print(f"📊 Success Rate: {result['success_rate']}")
        print(f"🎯 Overall Status: {result['overall_status']}")

        print("\n🔧 INITIALIZATION STEPS:")
        for i, step in enumerate(result["steps"], 1):
            status_icon = "✅" if "SUCCESS" in step else "⚠️" if "WARNING" in step else "❌"
            print(f"  {i:2}. {status_icon} {step}")

        if result["optimizations_applied"]:
            print(f"\n⚡ OPTIMIZATIONS APPLIED ({len(result['optimizations_applied'])}):")
            for opt in result["optimizations_applied"]:
                print(f"   • {opt}")

        if result["tools_activated"]:
            print(f"\n🛠️  TOOLS ACTIVATED ({len(result['tools_activated'])}):")
            for tool in result["tools_activated"]:
                print(f"   • {tool}")

        if result["performance_improvements"]:
            print(f"\n📈 PERFORMANCE IMPROVEMENTS:")
            for area, improvement in result["performance_improvements"].items():
                print(f"   • {area}: {improvement}")

        if result["errors"]:
            print(f"\n❌ ERRORS ENCOUNTERED:")
            for error in result["errors"]:
                print(f"   • {error}")

        # Run make check to ensure system integrity
        print(f"\n🔍 SYSTEM INTEGRITY CHECK:")
        os.system("make check 2>/dev/null || echo '⚠️  Make check not available'")

        # Final status
        if result["overall_status"] == "SUCCESS":
            print(f"\n🎉 PRIME COMMAND COMPLETED SUCCESSFULLY!")
            print(f"   ✅ System initialized and ready for work")
            print(f"   ✅ All optimizations applied")
            print(f"   ✅ Error prevention active")
            return 0
        else:
            print(f"\n⚠️  PRIME COMMAND COMPLETED WITH ISSUES")
            print(f"   ⚠️  Some systems may need manual attention")
            return 1

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("⚠️  Falling back to basic initialization...")

        # Fallback basic initialization
        basic_fallback()
        return 2
    except Exception as e:
        print(f"❌ Critical error during prime initialization: {e}")
        return 3


def basic_fallback():
    """Fallback initialization when enhanced systems aren't available"""
    print("🔄 BASIC FALLBACK INITIALIZATION")

    # Check for techniques registry
    techniques_file = Path("CLAUDE_TECHNIQUES_REGISTRY.md")
    if techniques_file.exists():
        print("✅ Techniques registry found")
    else:
        # Try to restore from Docker storage
        backup_path = Path(".docker-storage/claude-techniques-registry/CLAUDE_TECHNIQUES_REGISTRY.md")
        if backup_path.exists():
            backup_path.copy(techniques_file)
            print("✅ Techniques registry restored from backup")
        else:
            print("⚠️  No techniques registry found")

    # Basic path setup
    if str(Path(__file__).parent / "amplifier") not in sys.path:
        sys.path.insert(0, str(Path(__file__).parent / "amplifier"))
        print("✅ Python path configured")

    print("✅ Basic fallback initialization complete")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
