#!/usr/bin/env python3
"""
Hook Manager - Centralized Hook Integration
Manages the integration between progressive loading, compression, and agent systems
"""

import json
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class HookManager:
    """Centralized management of hook-driven progressive loading system"""

    def __init__(self):
        self.project_root = project_root
        self.settings = self._load_settings()
        self.hooks_config = self.settings.get("hooks", {})
        self.progressive_config = self.settings.get("progressiveLoading", {})
        self.hook_registry = {}
        self.session_active = False

    def _load_settings(self) -> dict[str, Any]:
        """Load hook configuration from settings"""
        settings_file = self.project_root / ".claude" / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file) as f:
                    return json.load(f)
            except Exception:
                pass

        # Default settings
        return {
            "hooks": {
                "sessionStart": {"enabled": True, "autoExecute": True},
                "preTask": {"enabled": True, "autoExecute": True},
                "postTask": {"enabled": True, "autoExecute": True},
            },
            "progressiveLoading": {"enabled": True, "autoContextOptimization": True, "patternLearning": True},
        }

    def register_hook(self, hook_name: str, hook_function: Callable, priority: int = 50):
        """Register a hook function with priority"""
        if hook_name not in self.hook_registry:
            self.hook_registry[hook_name] = []

        self.hook_registry[hook_name].append({"function": hook_function, "priority": priority, "enabled": True})

        # Sort by priority (higher = earlier execution)
        self.hook_registry[hook_name].sort(key=lambda x: x["priority"], reverse=True)

    def execute_hooks(self, hook_name: str, *args, **kwargs) -> list[dict[str, Any]]:
        """Execute all registered hooks for a given hook name"""
        results = []

        if hook_name not in self.hook_registry:
            return results

        # Check if hook is enabled in settings
        hook_config = self.hooks_config.get(hook_name, {})
        if not hook_config.get("enabled", True):
            return results

        for hook_info in self.hook_registry[hook_name]:
            if not hook_info["enabled"]:
                continue

            try:
                start_time = time.time()
                result = hook_info["function"](*args, **kwargs)
                execution_time = time.time() - start_time

                results.append(
                    {"success": True, "result": result, "execution_time": execution_time, "hook_name": hook_name}
                )

            except Exception as e:
                results.append({"success": False, "error": str(e), "hook_name": hook_name})

        return results

    def initialize_session(self) -> bool:
        """Initialize the session with progressive loading"""
        if self.session_active:
            return True

        # Check if progressive loading is enabled
        if not self.progressive_config.get("enabled", True):
            return False

        try:
            # Execute session start hooks
            results = self.execute_hooks("sessionStart")

            # Check if any hook succeeded
            session_initialized = any(r["success"] for r in results)

            if session_initialized:
                self.session_active = True
                self._log_hook_execution("sessionStart", results)

            return session_initialized

        except Exception as e:
            print(f"⚠️ Hook Manager: Session initialization failed: {e}")
            return False

    def optimize_for_task(self, task_content: str = "") -> dict[str, Any]:
        """Optimize context before task execution"""
        if not self.session_active:
            self.initialize_session()

        # Check if pre-task optimization is enabled
        pre_task_config = self.hooks_config.get("preTask", {})
        if not pre_task_config.get("enabled", True):
            return {"optimized": False, "reason": "preTask hooks disabled"}

        # Check if task detection is enabled
        task_detection = pre_task_config.get("taskDetection", {})
        if task_detection.get("enabled", True):
            keywords = task_detection.get("keywords", [])
            if keywords and not any(keyword in task_content.lower() for keyword in keywords):
                return {"optimized": False, "reason": "no task keywords detected"}

        try:
            # Execute pre-task hooks
            results = self.execute_hooks("preTask", task_content)

            # Collect optimization results
            optimization_results = []
            for result in results:
                if result["success"]:
                    optimization_results.append(result["result"])

            self._log_hook_execution("preTask", results)

            return {
                "optimized": len(optimization_results) > 0,
                "optimizations": optimization_results,
                "hooks_executed": len(results),
            }

        except Exception as e:
            print(f"⚠️ Hook Manager: Pre-task optimization failed: {e}")
            return {"optimized": False, "reason": str(e)}

    def learn_from_task(self, task_result: str = "", success: bool = True) -> dict[str, Any]:
        """Learn from task execution"""
        # Check if post-task learning is enabled
        post_task_config = self.hooks_config.get("postTask", {})
        if not post_task_config.get("enabled", True):
            return {"learned": False, "reason": "postTask hooks disabled"}

        if not post_task_config.get("learningEnabled", True):
            return {"learned": False, "reason": "learning disabled"}

        try:
            # Execute post-task hooks
            results = self.execute_hooks("postTask", task_result, success)

            # Collect learning results
            learning_results = []
            for result in results:
                if result["success"]:
                    learning_results.append(result["result"])

            self._log_hook_execution("postTask", results)

            return {"learned": len(learning_results) > 0, "learnings": learning_results, "hooks_executed": len(results)}

        except Exception as e:
            print(f"⚠️ Hook Manager: Post-task learning failed: {e}")
            return {"learned": False, "reason": str(e)}

    def _log_hook_execution(self, hook_name: str, results: list[dict[str, Any]]):
        """Log hook execution results"""
        log_data = {
            "timestamp": time.time(),
            "hook_name": hook_name,
            "results": results,
            "success_count": sum(1 for r in results if r["success"]),
            "total_count": len(results),
        }

        # Store in session checkpoints
        checkpoint_dir = self.project_root / ".claude" / "session_checkpoints"
        checkpoint_dir.mkdir(exist_ok=True)

        log_file = checkpoint_dir / f"hook_log_{hook_name}_{int(time.time())}.json"
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=2)

    def register_default_hooks(self):
        """Register the default hook implementations with error handling"""
        # Setup error handling
        from error_handler import apply_safe_execution_to_hooks
        from error_handler import get_error_handler

        error_handler = get_error_handler()

        # Import safe_execute decorator
        from error_handler import safe_execute

        # Import and register session start hook
        try:
            from session_start import main as session_start_main

            safe_session_start = safe_execute("sessionStart", error_handler)(session_start_main)
            self.register_hook("sessionStart", safe_session_start, priority=100)
        except ImportError as e:
            print(f"⚠️ Could not register session start hook: {e}")

        # Import and register pre-task hook
        try:
            from pre_task_hook import optimize_for_task

            safe_pre_task = safe_execute("preTask", error_handler)(optimize_for_task)
            self.register_hook("preTask", safe_pre_task, priority=100)
        except ImportError as e:
            print(f"⚠️ Could not register pre-task hook: {e}")

        # Import and register post-task hook
        try:
            from post_task_hook import learn_from_task

            safe_post_task = safe_execute("postTask", error_handler)(learn_from_task)
            self.register_hook("postTask", safe_post_task, priority=100)
        except ImportError as e:
            print(f"⚠️ Could not register post-task hook: {e}")

        # Apply safe execution to all registered hooks
        try:
            apply_safe_execution_to_hooks(self)
        except Exception as e:
            print(f"⚠️ Could not apply safe execution to hooks: {e}")

    def get_system_status(self) -> dict[str, Any]:
        """Get the current status of the hook system"""
        return {
            "session_active": self.session_active,
            "progressive_loading_enabled": self.progressive_config.get("enabled", True),
            "registered_hooks": list(self.hook_registry.keys()),
            "hooks_config": self.hooks_config,
            "hook_counts": {name: len(hooks) for name, hooks in self.hook_registry.items()},
        }

    def cleanup_old_data(self):
        """Clean up old checkpoints and data"""
        try:
            checkpoint_dir = self.project_root / ".claude" / "session_checkpoints"
            if checkpoint_dir.exists():
                # Clean up old session checkpoints
                retention = self.progressive_config.get("checkpointRetention", {})
                max_session_checkpoints = retention.get("sessionCheckpoints", 50)

                session_files = list(checkpoint_dir.glob("*.json"))
                session_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

                for old_file in session_files[max_session_checkpoints:]:
                    old_file.unlink()

        except Exception as e:
            print(f"⚠️ Hook Manager: Cleanup failed: {e}")


# Global hook manager instance
_hook_manager = None


def get_hook_manager() -> HookManager:
    """Get the global hook manager instance"""
    global _hook_manager
    if _hook_manager is None:
        _hook_manager = HookManager()
        _hook_manager.register_default_hooks()
    return _hook_manager


def initialize_progressive_loading() -> bool:
    """Initialize progressive loading system"""
    manager = get_hook_manager()
    return manager.initialize_session()


def optimize_context_for_task(task_content: str = "") -> dict[str, Any]:
    """Optimize context for a task"""
    manager = get_hook_manager()
    return manager.optimize_for_task(task_content)


def learn_from_task_execution(task_result: str = "", success: bool = True) -> dict[str, Any]:
    """Learn from task execution"""
    manager = get_hook_manager()
    return manager.learn_from_task(task_result, success)


def get_system_status() -> dict[str, Any]:
    """Get hook system status"""
    manager = get_hook_manager()
    return manager.get_system_status()


def main():
    """Main function for testing the hook manager"""
    print("🔧 Hook Manager - Progressive Loading System")

    # Initialize the system
    print("\n📋 Initializing session...")
    session_initialized = initialize_progressive_loading()
    print(f"   Session initialized: {session_initialized}")

    # Show system status
    status = get_system_status()
    print("\n📊 System Status:")
    print(f"   Session active: {status['session_active']}")
    print(f"   Progressive loading: {status['progressive_loading_enabled']}")
    print(f"   Registered hooks: {', '.join(status['registered_hooks'])}")

    # Test task optimization
    print("\n🎯 Testing task optimization...")
    test_task = "Implement a new feature for user authentication"
    optimization_result = optimize_context_for_task(test_task)
    print(f"   Optimization applied: {optimization_result.get('optimized', False)}")

    # Test learning
    print("\n📚 Testing task learning...")
    learning_result = learn_from_task_execution("Task completed successfully", True)
    print(f"   Learning captured: {learning_result.get('learned', False)}")

    print("\n✅ Hook Manager test complete")


if __name__ == "__main__":
    main()
