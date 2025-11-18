#!/home/markimus/projects/microsoft-amplifier/.venv/bin/python
"""
Quick Session Recovery Check
Verifies that all optimization techniques are properly preserved after context reset
"""

import json
import sys
from pathlib import Path


def verify_recovery_state():
    """Verify that recovery state is properly saved"""

    print("🔍 Checking session recovery state...")

    # Check techniques registry
    registry_file = Path("CLAUDE_TECHNIQUES_REGISTRY.md")
    docker_storage = Path(".docker-storage/claude-techniques-registry/")

    print(f"\n📁 Registry File: {'✅' if registry_file.exists() else '❌'}")
    print(f"📁 Docker Storage: {'✅' if docker_storage.exists() else '❌'}")

    if docker_storage.exists():
        docker_files = list(docker_storage.glob("*"))
        print(f"📁 Docker Files: {len(docker_files)} files")

        # Check for critical files
        critical_files = [
            "CLAUDE_TECHNIQUES_REGISTRY.md",
            "RECOVERY_INSTRUCTIONS.md",
            "enhanced_prime_command.md",
            "mcp_integration_patterns.md",
        ]

        for file in critical_files:
            file_path = docker_storage / file
            print(f"  📄 {file}: {'✅' if file_path.exists() else '❌'}")

    # Check latest checkpoint
    checkpoint_dir = Path(".claude/session_checkpoints")
    if checkpoint_dir.exists():
        checkpoints = sorted(
            checkpoint_dir.glob("session_checkpoint_*.json"), key=lambda x: x.stat().st_mtime, reverse=True
        )

        if checkpoints:
            latest = checkpoints[0]
            print(f"\n📋 Latest Checkpoint: {latest.name}")

            with open(latest) as f:
                checkpoint = json.load(f)

            print(f"  📊 Context Usage: {checkpoint.get('context_usage', 'N/A')}")
            print(f"  🔧 Techniques Applied: {len(checkpoint.get('techniques_applied', []))}")
            print(
                f"  📈 Performance Trend: {checkpoint.get('performance_metrics', {}).get('performance_trend', 'N/A')}"
            )
            print(f"  🔄 Ready for Recovery: {'✅' if checkpoint.get('ready_for_recovery') else '❌'}")

    # Quick MCP integration test
    print("\n🧪 MCP Integration Test:")
    try:
        sys.path.insert(0, "/home/markimus/projects/microsoft-amplifier")
        from amplifier.mcp.persistent_storage import load_techniques_registry

        techniques = load_techniques_registry()
        print(f"  ✅ MCP Load: {len(techniques)} technique categories")
    except Exception as e:
        print(f"  ❌ MCP Load: {e}")

    print(
        f"\n🎯 Recovery Status: {'✅ READY' if registry_file.exists() and docker_storage.exists() else '❌ NEEDS SETUP'}"
    )


if __name__ == "__main__":
    verify_recovery_state()
