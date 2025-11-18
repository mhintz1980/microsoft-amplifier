#!/usr/bin/env python3
"""
Error Handler - Graceful Degradation for Hook System
Provides robust error handling and fallback mechanisms for all hooks
"""

import json
import logging
import sys
import traceback
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class HookErrorHandler:
    """Handles errors in hook execution with graceful degradation"""

    def __init__(self):
        self.project_root = project_root
        self.error_log = []
        self.fallback_strategies = {}
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for hook errors"""
        log_dir = self.project_root / ".claude" / "logs"
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / "hook_errors.log"

        # Configure logging
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stderr)],
        )

        self.logger = logging.getLogger("hook_errors")

    def register_fallback(self, hook_name: str, fallback_function: Callable, priority: int = 50):
        """Register a fallback strategy for a hook"""
        if hook_name not in self.fallback_strategies:
            self.fallback_strategies[hook_name] = []

        self.fallback_strategies[hook_name].append({"function": fallback_function, "priority": priority})

        # Sort by priority (higher = earlier)
        self.fallback_strategies[hook_name].sort(key=lambda x: x["priority"], reverse=True)

    def handle_hook_error(self, hook_name: str, error: Exception, context: dict[str, Any] = None) -> dict[str, Any]:
        """Handle an error in hook execution"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "hook_name": hook_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "fallback_attempted": False,
            "fallback_successful": False,
        }

        # Log the error
        self.logger.error(f"Hook error in {hook_name}: {error}")

        # Try fallback strategies
        fallback_result = self.try_fallback(hook_name, error, context)
        if fallback_result is not None:
            error_info["fallback_attempted"] = True
            error_info["fallback_successful"] = True
            error_info["fallback_result"] = fallback_result

        # Store error for analysis
        self.error_log.append(error_info)

        # Save error log
        self.save_error_log()

        return {
            "success": False,
            "error": error_info,
            "fallback_result": fallback_result if error_info["fallback_successful"] else None,
        }

    def try_fallback(self, hook_name: str, error: Exception, context: dict[str, Any] = None) -> Any | None:
        """Try fallback strategies for a failed hook"""
        if hook_name not in self.fallback_strategies:
            return None

        for fallback_info in self.fallback_strategies[hook_name]:
            try:
                self.logger.info(f"Trying fallback for {hook_name}")
                result = fallback_info["function"](error, context)
                self.logger.info(f"Fallback successful for {hook_name}")
                return result
            except Exception as fallback_error:
                self.logger.warning(f"Fallback failed for {hook_name}: {fallback_error}")
                continue

        return None

    def save_error_log(self):
        """Save error log to file"""
        log_file = self.project_root / ".claude" / "hook_errors.json"
        try:
            # Keep only last 100 errors
            recent_errors = self.error_log[-100:]
            with open(log_file, "w") as f:
                json.dump(recent_errors, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save error log: {e}")

    def get_error_summary(self) -> dict[str, Any]:
        """Get summary of recent errors"""
        if not self.error_log:
            return {"total_errors": 0, "recent_errors": []}

        recent_errors = self.error_log[-10:]  # Last 10 errors
        error_counts = {}
        for error in self.error_log:
            hook_name = error["hook_name"]
            error_counts[hook_name] = error_counts.get(hook_name, 0) + 1

        return {
            "total_errors": len(self.error_log),
            "recent_errors": recent_errors,
            "error_counts_by_hook": error_counts,
            "most_problematic_hook": max(error_counts.items(), key=lambda x: x[1])[0] if error_counts else None,
        }


def safe_execute(hook_name: str, error_handler: HookErrorHandler = None):
    """Decorator for safe hook execution"""
    if error_handler is None:
        error_handler = HookErrorHandler()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {"function_name": func.__name__, "args_count": len(args), "kwargs_keys": list(kwargs.keys())}
                error_result = error_handler.handle_hook_error(hook_name, e, context)

                # Return fallback result if available
                if error_result.get("fallback_result") is not None:
                    return error_result["fallback_result"]

                # Return minimal safe result
                return get_safe_default_result(hook_name)

        return wrapper

    return decorator


def get_safe_default_result(hook_name: str) -> dict[str, Any]:
    """Get safe default result for a hook type"""
    safe_defaults = {
        "sessionStart": {"session_initialized": False, "fallback_mode": True, "basic_functionality": True},
        "preTask": {"optimized": False, "fallback_mode": True, "basic_optimizations": ["context_pruning"]},
        "postTask": {"learned": False, "fallback_mode": True, "basic_logging": True},
    }

    return safe_defaults.get(hook_name, {"success": False, "fallback_mode": True, "error": "Hook execution failed"})


# Default fallback strategies
def session_start_fallback(error: Exception, context: dict[str, Any] = None) -> dict[str, Any]:
    """Fallback for session start hook"""
    print("⚠️ Using fallback session initialization")

    # Basic session setup
    return {"session_initialized": True, "fallback_mode": True, "enhanced_features": False, "basic_functionality": True}


def pre_task_fallback(error: Exception, context: dict[str, Any] = None) -> dict[str, Any]:
    """Fallback for pre-task hook"""
    print("⚠️ Using fallback pre-task optimization")

    # Basic optimizations
    return {
        "optimized": True,
        "fallback_mode": True,
        "optimizations_applied": ["basic_context_pruning"],
        "agent_recommendations": [],
    }


def post_task_fallback(error: Exception, context: dict[str, Any] = None) -> dict[str, Any]:
    """Fallback for post-task hook"""
    print("⚠️ Using fallback post-task learning")

    # Basic logging
    return {"learned": True, "fallback_mode": True, "basic_logging": True, "patterns_stored": False}


def setup_error_handling():
    """Setup error handling for all hooks"""
    error_handler = HookErrorHandler()

    # Register fallback strategies
    error_handler.register_fallback("sessionStart", session_start_fallback, priority=100)
    error_handler.register_fallback("preTask", pre_task_fallback, priority=100)
    error_handler.register_fallback("postTask", post_task_fallback, priority=100)

    return error_handler


def apply_safe_execution_to_hooks(hook_manager):
    """Apply safe execution decorators to all registered hooks"""
    error_handler = setup_error_handling()

    for hook_name, hooks in hook_manager.hook_registry.items():
        for i, hook_info in enumerate(hooks):
            # Apply safe execution decorator
            original_function = hook_info["function"]
            safe_function = safe_execute(hook_name, error_handler)(original_function)
            hook_manager.hook_registry[hook_name][i]["function"] = safe_function

    return error_handler


# Global error handler instance
_global_error_handler = None


def get_error_handler() -> HookErrorHandler:
    """Get the global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = setup_error_handling()
    return _global_error_handler


def main():
    """Main function for testing error handling"""
    print("🛡️ Hook Error Handler - Testing Graceful Degradation")

    error_handler = get_error_handler()

    # Test error handling
    print("\n🧪 Testing error handling...")

    def failing_hook():
        raise ValueError("This is a test error")

    # Test with safe execution
    safe_failing_hook = safe_execute("testHook", error_handler)(failing_hook)

    try:
        result = safe_failing_hook()
        print(f"   Safe execution result: {result}")
    except Exception as e:
        print(f"   Unexpected error: {e}")

    # Show error summary
    error_summary = error_handler.get_error_summary()
    print("\n📊 Error Summary:")
    print(f"   Total errors: {error_summary['total_errors']}")
    if error_summary["most_problematic_hook"]:
        print(f"   Most problematic hook: {error_summary['most_problematic_hook']}")

    print("\n✅ Error handler test complete")


if __name__ == "__main__":
    main()
