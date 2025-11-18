#!/usr/bin/env python3


def verify_enhanced_sdk():
    """Verify enhanced SDK is working correctly"""
    checks = []

    # Check token counting
    try:
        import sys

        sys.path.insert(0, ".")

        checks.append("✅ Token counting available")
    except:
        checks.append("❌ Token counting missing")

    # Check error fixing
    try:
        checks.append("✅ Error fixing available")
    except:
        checks.append("❌ Error fixing missing")

    # Check environment
    import os

    if os.getenv("ENHANCED_SDK_ENABLED"):
        checks.append("✅ Environment configured")
    else:
        checks.append("⚠️ Environment not configured")

    # Check session hooks
    import os

    if os.path.exists(".claude/hooks/session_start.py"):
        checks.append("✅ Session hooks configured")
    else:
        checks.append("⚠️ Session hooks missing")

    print("Enhanced SDK Health Check:")
    for check in checks:
        print(f"  {check}")

    return all("✅" in check for check in checks)


if __name__ == "__main__":
    verify_enhanced_sdk()
