"""
Critical Techniques Registry for MCP-based Persistent Storage

This module provides persistent storage for critical techniques and optimizations
using MCP infrastructure, ensuring survival across context resets.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


class CriticalTechniquesRegistry:
    """Persistent registry for critical techniques and optimizations"""

    def __init__(self, storage_path: Path | None = None):
        self.storage_path = storage_path or Path(".docker-storage/critical_techniques.json")
        self.techniques = self._load_registry()

    def _load_registry(self) -> dict[str, Any]:
        """Load existing registry from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Failed to load techniques registry: {e}")

        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "techniques": {},
            "categories": {
                "prime_optimization": [],
                "context_management": [],
                "agent_delegation": [],
                "performance_optimization": [],
                "mcp_integration": [],
                "fix_patterns": [],
            },
            "metadata": {"total_techniques": 0, "success_rate": 0.0, "usage_count": 0},
        }

    def _save_registry(self):
        """Save registry to persistent storage"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.techniques["last_updated"] = datetime.now().isoformat()

        with open(self.storage_path, "w") as f:
            json.dump(self.techniques, f, indent=2)

    def add_technique(
        self,
        name: str,
        category: str,
        description: str,
        implementation: str,
        success_rate: float = 0.0,
        usage_count: int = 0,
        tags: list[str] = None,
    ) -> str:
        """Add a new critical technique to the registry"""

        technique_id = hashlib.md5(f"{name}_{category}_{description}".encode()).hexdigest()[:12]

        technique = {
            "id": technique_id,
            "name": name,
            "category": category,
            "description": description,
            "implementation": implementation,
            "success_rate": success_rate,
            "usage_count": usage_count,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "last_used": None,
        }

        self.techniques["techniques"][technique_id] = technique

        if category not in self.techniques["categories"]:
            self.techniques["categories"][category] = []

        if technique_id not in self.techniques["categories"][category]:
            self.techniques["categories"][category].append(technique_id)

        self._update_metadata()
        self._save_registry()

        return technique_id

    def get_technique(self, technique_id: str) -> dict | None:
        """Retrieve a specific technique by ID"""
        return self.techniques["techniques"].get(technique_id)

    def get_techniques_by_category(self, category: str) -> list[dict]:
        """Get all techniques in a specific category"""
        if category not in self.techniques["categories"]:
            return []

        techniques = []
        for technique_id in self.techniques["categories"][category]:
            technique = self.get_technique(technique_id)
            if technique:
                techniques.append(technique)

        return techniques

    def update_usage(self, technique_id: str, success: bool = True):
        """Update usage statistics for a technique"""
        technique = self.get_technique(technique_id)
        if technique:
            technique["usage_count"] += 1
            technique["last_used"] = datetime.now().isoformat()

            if success:
                # Update success rate with exponential moving average
                current_rate = technique["success_rate"]
                technique["success_rate"] = (current_rate * 0.9) + (1.0 * 0.1)
            else:
                current_rate = technique["success_rate"]
                technique["success_rate"] = (current_rate * 0.9) + (0.0 * 0.1)

            self._save_registry()

    def _update_metadata(self):
        """Update registry metadata"""
        total_techniques = len(self.techniques["techniques"])
        if total_techniques == 0:
            self.techniques["metadata"]["success_rate"] = 0.0
        else:
            success_rates = [t["success_rate"] for t in self.techniques["techniques"].values()]
            self.techniques["metadata"]["success_rate"] = sum(success_rates) / len(success_rates)

        self.techniques["metadata"]["total_techniques"] = total_techniques
        self.techniques["metadata"]["usage_count"] = sum(
            t["usage_count"] for t in self.techniques["techniques"].values()
        )

    def search_techniques(self, query: str, category: str | None = None) -> list[dict]:
        """Search techniques by query and optional category"""
        results = []
        query_lower = query.lower()

        for technique in self.techniques["techniques"].values():
            if category and technique["category"] != category:
                continue

            # Search in name, description, and tags
            searchable_text = f"{technique['name']} {technique['description']} {' '.join(technique['tags'])}"
            if query_lower in searchable_text.lower():
                results.append(technique)

        # Sort by success rate and usage count
        results.sort(key=lambda t: (t["success_rate"], t["usage_count"]), reverse=True)
        return results

    def get_top_techniques(self, category: str | None = None, limit: int = 10) -> list[dict]:
        """Get top performing techniques"""
        techniques = []

        for technique in self.techniques["techniques"].values():
            if category and technique["category"] != category:
                continue
            techniques.append(technique)

        # Sort by success rate and usage count
        techniques.sort(key=lambda t: (t["success_rate"], t["usage_count"]), reverse=True)
        return techniques[:limit]

    def export_for_mcp(self) -> dict:
        """Export registry in MCP-compatible format"""
        return {
            "registry_version": self.techniques["version"],
            "export_timestamp": datetime.now().isoformat(),
            "techniques": self.techniques["techniques"],
            "categories": self.techniques["categories"],
            "metadata": self.techniques["metadata"],
        }


# Pre-populated critical techniques based on recovered context
def initialize_critical_techniques(registry: CriticalTechniquesRegistry):
    """Initialize registry with critical techniques from recovered context"""

    techniques_data = [
        {
            "name": "Serena-First Code Analysis",
            "category": "context_management",
            "description": "Always use Serena tools (get_symbols_overview, find_symbol, search_for_pattern) before direct file operations",
            "implementation": "Use Serena tools for code analysis first. Only break pattern for small config files or when Serena tools fail.",
            "tags": ["serena", "code_analysis", "efficiency"],
        },
        {
            "name": "Parallel Execution Strategy",
            "category": "context_management",
            "description": "Single message with multiple tool calls whenever possible for maximum efficiency",
            "implementation": "Use parallel tool calls when tasks don't depend on each other's output",
            "tags": ["parallel", "efficiency", "tool_usage"],
        },
        {
            "name": "Memory Checkpoint Schedule",
            "category": "context_management",
            "description": "Auto-checkpoint after major tasks, when context >50% full, or every 30 minutes",
            "implementation": "Store session progress at regular intervals to prevent context loss",
            "tags": ["memory", "checkpoints", "context"],
        },
        {
            "name": "Token Efficiency Rules",
            "category": "prime_optimization",
            "description": "Targeted search first, never read entire files unless absolutely necessary",
            "implementation": "Use Grep/find_symbol for targeted searches, only read full files when essential",
            "tags": ["tokens", "efficiency", "search"],
        },
        {
            "name": "Async Pytest Fixtures Pattern",
            "category": "fix_patterns",
            "description": "Change @pytest.fixture + async def to @pytest_asyncio.fixture + import pytest_asyncio",
            "implementation": "Replace pytest fixtures with pytest_asyncio fixtures and add proper imports",
            "tags": ["pytest", "async", "fix"],
        },
        {
            "name": "Agent Delegation Decision Tree",
            "category": "agent_delegation",
            "description": "Ask before coding: Is there specialized agent? Can this benefit from expertise? Is this repetitive?",
            "implementation": "Use Task tool immediately when answer is YES to delegation questions",
            "tags": ["agents", "delegation", "specialization"],
        },
        {
            "name": "Container Pooling Optimization",
            "category": "performance_optimization",
            "description": "50-70% container startup reduction through pooling strategies",
            "implementation": "Reuse warm containers instead of creating new ones for each task",
            "tags": ["containers", "performance", "mcp"],
        },
        {
            "name": "MCP Code Execution Framework",
            "category": "mcp_integration",
            "description": "98.7% token reduction through Docker-based execution",
            "implementation": "Execute code in isolated Docker containers with minimal context transfer",
            "tags": ["mcp", "execution", "tokens"],
        },
    ]

    for tech_data in techniques_data:
        registry.add_technique(**tech_data)

    print(f"✅ Initialized {len(techniques_data)} critical techniques in registry")


# Global registry instance
_registry = None


def get_registry() -> CriticalTechniquesRegistry:
    """Get the global techniques registry instance"""
    global _registry
    if _registry is None:
        _registry = CriticalTechniquesRegistry()
        # Initialize with critical techniques if registry is empty
        if _registry.techniques["metadata"]["total_techniques"] == 0:
            initialize_critical_techniques(_registry)
    return _registry


if __name__ == "__main__":
    # Demo: Create and initialize registry
    registry = CriticalTechniquesRegistry()
    initialize_critical_techniques(registry)

    print("🚀 Critical Techniques Registry Initialized")
    print(f"Total techniques: {registry.techniques['metadata']['total_techniques']}")
    print(f"Categories: {list(registry.techniques['categories'].keys())}")

    # Show top techniques
    print("\n📊 Top Techniques:")
    for technique in registry.get_top_techniques(limit=5):
        print(f"  • {technique['name']} ({technique['category']}) - {technique['success_rate']:.1%} success")  # type: ignore
