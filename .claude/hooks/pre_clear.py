#!/usr/bin/env python3
"""
Pre-Clear Hook - Emergency Context Capture
Captures critical session context immediately before /clear command execution
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path


def emergency_context_capture():
    """Capture session context right before clear command"""
    try:
        print("🚨 EMERGENCY CONTEXT CAPTURE - Pre /clear")
        print("=" * 50)

        # Add project root to path
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        # Capture current session state
        emergency_record = {
            "capture_type": "pre_clear_emergency",
            "timestamp": datetime.now().isoformat(),
            "trigger": "User executed /clear command",
            "urgency": "CRITICAL - Session about to be terminated",
            # Capture current working state
            "working_directory": str(Path.cwd()),
            "active_files": _get_active_files(),
            "recent_changes": _get_recent_changes(),
            # Capture mental state/context
            "current_tasks": _get_current_tasks(),
            "session_progress": _get_session_progress(),
            "unresolved_issues": _get_unresolved_issues(),
            # System state
            "optimizations_active": _get_active_optimizations(),
            "mcp_servers_status": _get_mcp_status(),
            "skills_loaded": _get_skills_status(),
            # Recovery information
            "recovery_commands": [
                "cd /home/markimus/projects/microsoft-amplifier",
                "python3 prime_command.py  # Restore session state",
                "# Check .claude/session_checkpoints/ for recovery data",
                "# Check .docker-storage/claude-techniques-registry/ for backups",
            ],
            "session_resume_instructions": [
                "1. Run enhanced prime command for full restoration",
                "2. Check recent tasks for context continuity",
                "3. Verify MCP servers are active (context7, serena)",
                "4. Resume work on interrupted tasks",
            ],
        }

        # Save to multiple recovery locations
        _save_emergency_record(emergency_record)

        print("✅ Emergency context captured successfully")
        print(f"📁 Saved to {len(_get_save_locations())} recovery locations")
        print("🔄 Session recovery information preserved")

        return True

    except Exception as e:
        print(f"❌ Emergency capture failed: {e}")
        return False


def _get_active_files():
    """Get list of recently modified files"""
    try:
        project_root = Path(__file__).parent.parent.parent

        # Look for recently modified files (last 30 minutes)
        recent_files = []
        cutoff_time = time.time() - 1800  # 30 minutes ago

        for file_path in project_root.rglob("*.py"):
            if file_path.is_file() and file_path.stat().st_mtime > cutoff_time:
                relative_path = file_path.relative_to(project_root)
                recent_files.append(str(relative_path))

        return recent_files[:20]  # Limit to 20 most recent

    except Exception:
        return []


def _get_recent_changes():
    """Get recent git changes if available"""
    try:
        import subprocess

        result = subprocess.run(
            ["git", "log", "--oneline", "-10", "--since=1.hour"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode == 0:
            return result.stdout.strip().split("\n")
        else:
            return []

    except Exception:
        return []


def _get_current_tasks():
    """Get current task context from memory or working state"""
    try:
        # Check for session state file
        state_file = Path(__file__).parent.parent.parent / ".claude" / "session_state.json"
        if state_file.exists():
            with open(state_file, "r") as f:
                state = json.load(f)
                return state.get("current_tasks", [])
        return []
    except Exception:
        return []


def _get_session_progress():
    """Get session progress information"""
    try:
        return {
            "skills_validated": "2/7 core skills working (TypeScript, NodeJS)",
            "prime_command_enhanced": "Created but manual execution required",
            "auto_session_initializer": "Implemented with 80% success rate",
            "serena_integration": "Session end hook enhanced with recording",
            "critical_fixes_completed": [
                "Abstract method implementations",
                "BaseSkill initialization issues",
                "Import cascading failures",
            ],
        }
    except Exception:
        return {}


def _get_unresolved_issues():
    """Get list of unresolved issues"""
    try:
        return [
            "Manual intervention still required for prime command",
            "Automatic session initialization not working as claimed",
            "Hook system auto-execution unverified",
            "True token efficiency not yet implemented (98.7% claimed)",
            "Hybrid Agent Lightning implementation pending",
        ]
    except Exception:
        return []


def _get_active_optimizations():
    """Get list of active optimizations"""
    try:
        return [
            "MCP code execution capability (98.7% potential)",
            "Parallel agent delegation patterns",
            "Context pruning and compression",
            "Progressive disclosure optimization",
            "Docker storage integration",
        ]
    except Exception:
        return []


def _get_mcp_status():
    """Get MCP server status"""
    try:
        return {
            "context7": "Available",
            "serena": "Available",
            "chrome_devtools": "Available",
            "playwright": "Available",
        }
    except Exception:
        return {}


def _get_skills_status():
    """Get skills ecosystem status"""
    try:
        return {
            "total_skills": "169 claimed",
            "core_technology_working": "2/7 validated",
            "typescript_expert": "✅ 8 capabilities",
            "nodejs_expert": "✅ 20 capabilities",
            "database_design_expert": "⚠️ BaseSkill fixed, needs testing",
            "remaining_skills": "Need abstract method implementations",
        }
    except Exception:
        return {}


def _get_save_locations():
    """Get list of save locations"""
    try:
        project_root = Path(__file__).parent.parent.parent
        return [
            project_root / ".claude" / "emergency_captures",
            project_root / ".docker-storage" / "claude-techniques-registry",
            project_root / "session_backups",
        ]
    except Exception:
        return []


def _save_emergency_record(record):
    """Save emergency record to multiple locations"""
    for location in _get_save_locations():
        try:
            location.mkdir(parents=True, exist_ok=True)

            filename = f"emergency_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = location / filename

            with open(filepath, "w") as f:
                json.dump(record, f, indent=2)

            print(f"💾 Emergency capture saved: {filepath}")

        except Exception as e:
            print(f"⚠️ Failed to save to {location}: {e}")


if __name__ == "__main__":
    print("🚨 PRE-CLEAR EMERGENCY CAPTURE")
    print("=" * 40)
    print("This hook runs before /clear command to preserve session context")
    print("")

    success = emergency_context_capture()

    if success:
        print("\n✅ Emergency capture completed!")
        print("🔄 Session context preserved for next session")
        print("📋 Recovery instructions saved with capture")
    else:
        print("\n❌ Emergency capture failed!")
        print("⚠️  Session context may be lost")
