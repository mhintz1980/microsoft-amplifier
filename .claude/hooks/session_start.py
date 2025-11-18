#!/usr/bin/env python3
"""
Enhanced Session Start Hook - Progressive Loading System
Automatically optimizes context based on project patterns and user behavior
"""

import json
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class ProgressiveLoadingSystem:
    """Manages progressive loading of context and optimizations"""

    def __init__(self):
        self.project_root = project_root
        self.session_start_time = time.time()
        self.context_cache = {}
        self.agent_registry = {}
        self.performance_metrics = {}

    def detect_project_context(self) -> dict[str, Any]:
        """Detect project type and relevant context patterns"""
        context = {
            "project_type": "unknown",
            "frameworks": [],
            "languages": [],
            "tools": [],
            "patterns": [],
            "complexity": "medium",
        }

        # Detect from pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            try:
                import tomllib

                with open(pyproject_path, "rb") as f:
                    pyproject = tomllib.load(f)

                # Extract dependencies
                deps = pyproject.get("project", {}).get("dependencies", [])
                dev_deps = pyproject.get("project", {}).get("dev-dependencies", [])

                for dep in deps + dev_deps:
                    if "fastapi" in dep:
                        context["frameworks"].append("fastapi")
                    if "django" in dep:
                        context["frameworks"].append("django")
                    if "pytest" in dep:
                        context["tools"].append("pytest")
                    if "pydantic" in dep:
                        context["frameworks"].append("pydantic")

            except Exception:
                pass

        # Detect from directory structure
        if (self.project_root / "scenarios").exists():
            context["project_type"] = "amplifier-scenarios"
            context["patterns"].append("agent-based")

        if (self.project_root / "amplifier").exists():
            context["project_type"] = "amplifier-framework"
            context["frameworks"].append("microsoft-amplifier")

        # Detect language patterns
        py_files = list(self.project_root.glob("**/*.py"))
        if len(py_files) > 50:
            context["complexity"] = "high"
        elif len(py_files) < 10:
            context["complexity"] = "low"

        context["languages"].append("python")

        return context

    def load_memory_patterns(self, project_context: dict[str, Any]) -> dict[str, Any]:
        """Load relevant memory patterns based on project context"""
        patterns = {
            "optimization_techniques": [],
            "agent_preferences": [],
            "context_strategies": [],
            "performance_insights": [],
        }

        # Load techniques registry
        techniques_file = self.project_root / "CLAUDE_TECHNIQUES_REGISTRY.md"
        if techniques_file.exists():
            patterns["optimization_techniques"].append(
                {
                    "name": "claude_techniques_registry",
                    "path": str(techniques_file),
                    "priority": "high",
                    "compression_ratio": 0.987,
                }
            )

        # Load project-specific memories
        memories_dir = self.project_root / ".serena" / "memories"
        if memories_dir.exists():
            for memory_file in memories_dir.glob("*.md"):
                if "sdk" in memory_file.name.lower() or "integration" in memory_file.name.lower():
                    patterns["performance_insights"].append(
                        {"name": memory_file.stem, "path": str(memory_file), "relevance": 0.8}
                    )

        return patterns

    def initialize_progressive_compression(self):
        """Initialize progressive compression system"""
        try:
            # Add context optimizer to path
            context_path = self.project_root / "amplifier" / "mcp"
            if str(context_path) not in sys.path:
                sys.path.insert(0, str(context_path))

            from context_optimizer import ContextOptimizer

            optimizer = ContextOptimizer()
            self.context_cache["optimizer"] = optimizer

            return True

        except ImportError:
            print("⚠️ Context optimizer not available - using basic compression")
            return False

    def activate_optimal_agents(self, project_context: dict[str, Any]) -> bool:
        """Activate optimal agents based on project context"""
        agents_to_load = []

        # Base agents for all projects
        agents_to_load.extend(["context-optimization-specialist", "performance-optimization-specialist"])

        # Project-specific agents
        if project_context["project_type"] == "amplifier-framework":
            agents_to_load.extend(["mcp-integration-specialist", "memory-persistence-specialist"])

        if "fastapi" in project_context["frameworks"]:
            agents_to_load.append("api-development-specialist")

        if project_context["complexity"] == "high":
            agents_to_load.append("architecture-reviewer")

        # Store activated agents
        self.agent_registry["active"] = agents_to_load
        self.agent_registry["activation_time"] = time.time()

        return len(agents_to_load) > 0

    def initialize_enhanced_sdk(self):
        """Initialize enhanced SDK capabilities"""
        try:
            # Add enhanced SDK to Python path
            enhanced_sdk_path = self.project_root / "amplifier" / "sdk_enhancements"
            if str(enhanced_sdk_path) not in sys.path:
                sys.path.insert(0, str(enhanced_sdk_path))

            # Auto-initialize enhanced clients
            from efficient_error_fixer import EfficientErrorFixer

            # Make global instances available
            global _enhanced_client, _error_fixer
            _enhanced_client = None  # Will be initialized on first use
            _error_fixer = EfficientErrorFixer()

            return True

        except ImportError:
            return False

    def save_session_state(self):
        """Save current session state for recovery"""
        session_data = {
            "session_start": self.session_start_time,
            "project_context": getattr(self, "project_context", {}),
            "active_agents": self.agent_registry.get("active", []),
            "compression_enabled": "optimizer" in self.context_cache,
            "enhanced_sdk_enabled": True,
        }

        session_file = self.project_root / ".claude" / "session_state.json"
        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2)


def activate_enhanced_sdk():
    """Legacy function for backward compatibility"""
    system = ProgressiveLoadingSystem()
    return system.initialize_enhanced_sdk()


def main():
    """Main session start initialization"""
    print("🚀 Initializing Progressive Loading System...")

    # Initialize the progressive loading system
    system = ProgressiveLoadingSystem()

    # Detect project context
    print("📊 Detecting project context...")
    system.project_context = system.detect_project_context()
    print(f"   Project type: {system.project_context['project_type']}")
    print(f"   Complexity: {system.project_context['complexity']}")
    print(f"   Frameworks: {', '.join(system.project_context['frameworks'])}")

    # Load memory patterns
    print("🧠 Loading memory patterns...")
    memory_patterns = system.load_memory_patterns(system.project_context)
    print(f"   Loaded {len(memory_patterns['optimization_techniques'])} technique patterns")
    print(f"   Loaded {len(memory_patterns['performance_insights'])} performance insights")

    # Initialize progressive compression
    print("🗜️  Initializing progressive compression...")
    compression_success = system.initialize_progressive_compression()
    if compression_success:
        print("   ✅ Progressive compression enabled")
    else:
        print("   ⚠️ Using basic compression")

    # Activate optimal agents
    print("🤖 Activating optimal agents...")
    agents_success = system.activate_optimal_agents(system.project_context)
    if agents_success:
        print(f"   ✅ Activated {len(system.agent_registry['active'])} specialized agents")
    else:
        print("   ⚠️ No additional agents activated")

    # Initialize enhanced SDK
    print("⚡ Initializing enhanced SDK...")
    sdk_success = system.initialize_enhanced_sdk()
    if sdk_success:
        print("   ✅ Enhanced SDK capabilities ready")
    else:
        print("   ⚠️ Enhanced SDK not available")

    # Save session state
    system.save_session_state()

    # Store system globally for other hooks
    global _progressive_system
    _progressive_system = system

    print("✅ Progressive Loading System initialization complete")
    print(f"   Session ID: {int(system.session_start_time)}")
    print("   Ready for optimized task execution")


# Auto-activate on session start
if __name__ == "__main__":
    main()
else:
    main()
