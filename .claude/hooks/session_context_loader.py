#!/home/markimus/projects/microsoft-amplifier/.venv/bin/python
"""
Automatic Context Loading System for Claude Code Sessions

This module provides automatic memory loading and context recovery
for Claude Code sessions to prevent critical technique loss.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


class ContextLoader:
    """Automatic context loading and recovery system"""

    def __init__(self):
        self.session_start = datetime.now()
        self.critical_memories = [
            "current_session_context",
            "prime_command_execution_patterns",
            "context_management_patterns",
            "agent_optimization_workflow_complete",
            "six_hour_optimization_session_2025_11_08",
            "mcp_context_saving_strategies_prime",
            "prime_fix_patterns_2025",
            "comprehensive_project_context_2025",
            "implementation_context_essential",
        ]

        self.critical_searches = [
            ("prime command optimization", 5),
            ("agent optimization workflow", 3),
            ("six hour optimization session", 3),
            ("context management patterns", 3),
            ("performance optimization", 5),
            ("MCP integration strategies", 3),
        ]

    def load_session_context(self) -> dict:
        """Load session context from available memory systems"""
        context = {
            "session_start": self.session_start.isoformat(),
            "memories_loaded": [],
            "searches_performed": [],
            "critical_techniques": [],
            "recovery_status": "partial",
        }

        print("🚀 AUTOMATIC CONTEXT LOADING STARTED")
        print("=" * 50)

        # Try to load from episodic memory
        try:
            from mcp_plugin_episodic_memory_episodic_memory import search_conversations

            print("📊 Episodic Memory Available")

            for query, limit in self.critical_searches:
                try:
                    results = search_conversations(query, limit=limit)
                    context["searches_performed"].append(
                        {
                            "query": query,
                            "results_count": len(results) if isinstance(results, list) else 1,
                            "status": "success",
                        }
                    )
                    print(f"  ✅ Found {len(results) if isinstance(results, list) else 1} results for: {query}")
                except Exception as e:
                    context["searches_performed"].append({"query": query, "error": str(e), "status": "failed"})
                    print(f"  ❌ Search failed for: {query} ({e})")

        except ImportError:
            print("⚠️  Episodic Memory Not Available")

        # Try to load from Serena memory system
        try:
            from mcp_serena import read_memory

            print("🧠 Serena Memory Available")

            for memory_name in self.critical_memories:
                try:
                    content = read_memory(memory_name)
                    context["memories_loaded"].append(
                        {"name": memory_name, "status": "success", "size": len(content) if content else 0}
                    )
                    print(f"  ✅ Loaded memory: {memory_name} ({len(content) if content else 0} chars)")

                    # Extract critical techniques from key memories
                    if "patterns" in memory_name or "workflow" in memory_name:
                        techniques = self._extract_techniques(content)
                        context["critical_techniques"].extend(techniques)

                except Exception as e:
                    context["memories_loaded"].append({"name": memory_name, "error": str(e), "status": "failed"})
                    print(f"  ❌ Memory not found: {memory_name}")

        except ImportError:
            print("⚠️  Serena Memory Not Available")

        # Determine recovery status
        memories_success = sum(1 for m in context["memories_loaded"] if m.get("status") == "success")
        searches_success = sum(1 for s in context["searches_performed"] if s.get("status") == "success")

        if memories_success >= len(self.critical_memories) // 2:
            context["recovery_status"] = "good"
        elif memories_success > 0:
            context["recovery_status"] = "partial"
        else:
            context["recovery_status"] = "poor"

        # Summary
        print("=" * 50)
        print("📈 RECOVERY SUMMARY:")
        print(f"  Memories: {memories_success}/{len(self.critical_memories)} loaded")
        print(f"  Searches: {searches_success}/{len(self.critical_searches)} completed")
        print(f"  Techniques: {len(context['critical_techniques'])} extracted")
        print(f"  Status: {context['recovery_status'].upper()}")
        print("=" * 50)

        return context

    def _extract_techniques(self, content: str) -> list[dict]:
        """Extract critical techniques from memory content"""
        techniques = []

        # Look for specific patterns in content
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if any(
                pattern in line.lower()
                for pattern in [
                    "pattern:",
                    "technique:",
                    "strategy:",
                    "approach:",
                    "fix:",
                    "optimization:",
                    "solution:",
                    "method:",
                    "framework:",
                ]
            ):
                # Extract technique description
                technique = {
                    "type": "extracted",
                    "line": i + 1,
                    "content": line.strip(),
                    "context": content[max(0, i - 2) : i + 3],  # 2 lines before and after
                }
                techniques.append(technique)

        return techniques

    def save_session_checkpoint(self, context: dict, additional_data: dict | None = None):
        """Save session checkpoint for future recovery"""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "session_start": context["session_start"],
            "recovery_status": context["recovery_status"],
            "memories_count": len(context["memories_loaded"]),
            "techniques_count": len(context["critical_techniques"]),
            "additional_data": additional_data or {},
        }

        # Try to save to multiple locations
        save_locations = [
            Path.home() / ".claude" / "session_checkpoint.json",
            Path(".claude") / "session_checkpoint.json",
            Path("session_checkpoint.json"),
        ]

        for location in save_locations:
            try:
                location.parent.mkdir(parents=True, exist_ok=True)
                with open(location, "w") as f:
                    json.dump(checkpoint, f, indent=2)
                print(f"💾 Session checkpoint saved: {location}")
                break
            except Exception as e:
                print(f"⚠️  Failed to save checkpoint to {location}: {e}")


def main():
    """Main entry point for automatic context loading"""
    loader = ContextLoader()

    print(f"🤖 Claude Code Context Loader - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Load session context
    context = loader.load_session_context()

    # Save checkpoint
    loader.save_session_checkpoint(context)

    # Return status code based on recovery quality
    if context["recovery_status"] == "good":
        print("✅ Context recovery successful - proceeding with enhanced capabilities")
        return 0
    if context["recovery_status"] == "partial":
        print("⚠️  Context recovery partial - some techniques may be unavailable")
        return 1
    print("❌ Context recovery failed - running in degraded mode")
    return 2


if __name__ == "__main__":
    sys.exit(main())
