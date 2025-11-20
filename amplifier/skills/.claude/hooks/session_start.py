"""
Session Start Hook - Automatic Enhanced Prime Command

This hook runs automatically at session start to ensure consistent
system state and eliminate manual prime command execution.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_enhanced_prime():
    """Run enhanced prime command automatically"""
    try:
        # Import the enhanced prime command
        from prime_command import main as prime_main

        print("🔄 AUTO-SESSION INITIALIZATION")
        print("Running enhanced prime command...")

        # Run prime command
        exit_code = prime_main()

        if exit_code == 0:
            print("✅ Auto-session initialization successful")
        else:
            print(f"⚠️  Auto-session initialization completed with warnings (exit code: {exit_code})")

        return exit_code

    except ImportError as e:
        print(f"⚠️  Could not import enhanced prime command: {e}")
        print("🔄 Falling back to basic initialization...")
        return basic_session_init()
    except Exception as e:
        print(f"❌ Auto-session initialization failed: {e}")
        return 1


def basic_session_init():
    """Basic session initialization fallback"""
    print("🔄 BASIC SESSION INITIALIZATION")

    # Essential setup
    if str(Path(__file__).parent.parent.parent / "amplifier") not in sys.path:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "amplifier"))
        print("✅ Python path configured")

    # Check for basic requirements
    techniques_file = Path(__file__).parent.parent.parent / "CLAUDE_TECHNIQUES_REGISTRY.md"
    if techniques_file.exists():
        print("✅ Techniques registry available")
    else:
        print("⚠️  Techniques registry not found")

    print("✅ Basic session initialization complete")
    return 0


# Automatically run when this hook is imported
if __name__ == "__main__":
    exit_code = run_enhanced_prime()
    sys.exit(exit_code)
else:
    # When imported as a hook, run automatically
    run_enhanced_prime()
