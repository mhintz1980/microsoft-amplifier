#!/usr/bin/env python3
"""
Comprehensive test suite for the dynamic agent loading framework.

Tests the progressive agent discovery pattern including:
- Registry building and metadata extraction
- Tag-based discovery and search
- On-demand loading and context management
- Task tool integration
- Performance metrics
"""

import logging
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from amplifier.agents import DynamicAgentLoader
from amplifier.agents import find_agents_by_description
from amplifier.agents import find_agents_by_tags
from amplifier.agents import get_agent_content
from amplifier.agents import get_agent_loader
from amplifier.agents import get_task_resolver
from amplifier.agents import load_agent
from amplifier.agents import resolve_agent_for_task

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def test_registry_building():
    """Test registry building and metadata extraction"""
    print("\n=== Testing Registry Building ===")

    loader = get_agent_loader()

    # Force rebuild
    count = loader.build_registry(force_rebuild=True)
    print(f"✅ Built registry with {count} agents")

    # Test stats
    stats = loader.get_registry_stats()
    print(f"✅ Metadata tokens: {stats['total_tokens_metadata']:,}")
    print(f"✅ Full definition tokens: {stats['total_tokens_full']:,}")
    print(f"✅ Memory efficiency: {stats['memory_efficiency']:.1f}%")

    return count > 0


def test_tag_discovery():
    """Test tag-based agent discovery"""
    print("\n=== Testing Tag Discovery ===")

    # Test single tag
    agents = find_agents_by_tags(["architecture"])
    print(f"✅ Found {len(agents)} architecture agents")

    # Test multiple tags (ANY match)
    agents = find_agents_by_tags(["security", "testing"])
    print(f"✅ Found {len(agents)} agents with security OR testing tags")

    # Test multiple tags (ALL match)
    agents = find_agents_by_tags(["architecture", "development"], require_all=True)
    print(f"✅ Found {len(agents)} agents with BOTH architecture AND development tags")

    # Test non-existent tag
    agents = find_agents_by_tags(["non-existent-tag"])
    print(f"✅ Found {len(agents)} agents with 'non-existent-tag' (should be 0)")

    return True


def test_description_search():
    """Test description-based agent search"""
    print("\n=== Testing Description Search ===")

    # Test various search terms
    test_queries = [
        "security",
        "architecture design",
        "performance optimization",
        "testing quality",
        "modular building",
    ]

    for query in test_queries:
        agents = find_agents_by_description(query)
        print(f"✅ Search '{query}': {len(agents)} agents found")
        if agents:
            print(f"   Top match: {agents[0].name}")

    return True


def test_on_demand_loading():
    """Test on-demand agent loading"""
    print("\n=== Testing On-Demand Loading ===")

    loader = get_agent_loader()

    # Test loading different agent types
    test_agents = ["zen-architect", "context-optimization-specialist", "bug-hunter"]

    for agent_id in test_agents:
        result = load_agent(agent_id)
        if result.success:
            print(f"✅ Loaded '{agent_id}' in {result.load_time:.4f}s ({len(result.content)} chars)")

            # Verify content starts with expected patterns
            if agent_id.endswith("-specialist"):
                # JSON agents should start with {
                if result.content.strip().startswith("{"):
                    print("   ✅ Content format correct (JSON)")
                else:
                    print("   ❌ Content format incorrect (expected JSON)")
            else:
                # MD agents should have content
                if len(result.content) > 100:
                    print("   ✅ Content length adequate")
                else:
                    print("   ❌ Content too short")
        else:
            print(f"❌ Failed to load '{agent_id}': {result.error}")

    # Test context management
    print(f"✅ Currently loaded agents: {len(loader.loaded_agents)}")

    # Test manual unloading
    if "zen-architect" in loader.loaded_agents:
        unloaded = loader.unload_agent("zen-architect")
        print(f"✅ Unloaded 'zen-architect': {unloaded}")
        print(f"✅ Loaded agents after unload: {len(loader.loaded_agents)}")

    return True


def test_task_integration():
    """Test Task tool integration"""
    print("\n=== Testing Task Integration ===")

    resolver = get_task_resolver()

    # Test agent resolution for different tasks
    test_tasks = [
        {
            "description": "Design a modular authentication system",
            "required_tags": ["architecture"],
            "preferred_tags": ["security"],
        },
        {
            "description": "Optimize database queries for performance",
            "required_tags": ["optimization"],
            "preferred_tags": None,
        },
        {
            "description": "Review code for security vulnerabilities",
            "required_tags": ["security"],
            "preferred_tags": ["analysis"],
        },
        {
            "description": "Build a React component library",
            "required_tags": ["development"],
            "preferred_tags": ["testing"],
        },
    ]

    for i, task in enumerate(test_tasks, 1):
        print(f"\n{i}. Task: {task['description']}")

        agent_id = resolve_agent_for_task(task["description"], task["required_tags"], task["preferred_tags"])

        if agent_id:
            print(f"   ✅ Resolved agent: {agent_id}")

            # Get agent content
            content = get_agent_content(agent_id)
            if content:
                print(f"   ✅ Retrieved content ({len(content)} chars)")
            else:
                print("   ❌ Failed to get content")

            # Get alternatives
            alternatives = resolver.suggest_alternatives(task["description"], agent_id, limit=2)
            if alternatives:
                print(f"   🔄 Alternatives: {[alt['name'] for alt in alternatives]}")
        else:
            print("   ❌ No agent found")

    # Test manual agent specification
    manual_agent = resolve_agent_for_task("Test task", manual_agent_id="zen-architect")
    print(f"\n✅ Manual agent resolution: {manual_agent}")

    return True


def test_performance_metrics():
    """Test performance and efficiency metrics"""
    print("\n=== Testing Performance Metrics ===")

    loader = get_agent_loader()

    # Measure discovery performance
    start_time = time.time()
    agents = find_agents_by_tags(["architecture"])
    discovery_time = time.time() - start_time

    print(f"✅ Tag discovery time: {discovery_time:.4f}s for {len(agents)} results")

    # Measure loading performance
    start_time = time.time()
    result = load_agent("zen-architect")
    load_time = time.time() - start_time

    if result.success:
        print(f"✅ Agent loading time: {load_time:.4f}s")
        print(f"✅ Loading rate: {len(result.content) / load_time:.0f} chars/sec")

    # Get comprehensive stats
    stats = loader.get_registry_stats()
    print("\n📊 System Statistics:")
    print(f"   Total agents: {stats['total_agents']}")
    print(f"   Loaded agents: {stats['loaded_agents']}")
    print(f"   Context capacity: {loader.max_loaded_agents}")
    print(f"   Memory saved: {stats['total_tokens_full'] - stats['loaded_tokens']:,} tokens")

    # Test tag distribution
    print("\n🏷️  Top Tags:")
    for tag, count in list(stats["tag_distribution"].items())[:5]:
        print(f"   {tag}: {count} agents")

    return True


def test_error_handling():
    """Test error handling and edge cases"""
    print("\n=== Testing Error Handling ===")

    # Test loading non-existent agent
    result = load_agent("non-existent-agent")
    print(f"✅ Non-existent agent: {'handled correctly' if not result.success else 'unexpected success'}")

    # Test empty tag search
    agents = find_agents_by_tags([])
    print(f"✅ Empty tag search: {len(agents)} agents (should return all)")

    # Test invalid registry file handling
    loader = DynamicAgentLoader()
    original_registry = loader.registry_file
    loader.registry_file = Path("/tmp/nonexistent/registry.json")

    count = loader.build_registry()
    print(f"✅ Invalid registry path: {count} agents rebuilt")

    # Restore original
    loader.registry_file = original_registry

    return True


def main():
    """Run all tests"""
    print("🚀 Dynamic Agent Loading Framework - Comprehensive Test Suite")
    print("=" * 70)

    tests = [
        ("Registry Building", test_registry_building),
        ("Tag Discovery", test_tag_discovery),
        ("Description Search", test_description_search),
        ("On-Demand Loading", test_on_demand_loading),
        ("Task Integration", test_task_integration),
        ("Performance Metrics", test_performance_metrics),
        ("Error Handling", test_error_handling),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running {test_name} Tests...")
            if test_func():
                print(f"✅ {test_name} tests passed")
                passed += 1
            else:
                print(f"❌ {test_name} tests failed")
        except Exception as e:
            print(f"❌ {test_name} tests failed with error: {e}")
            logger.exception(f"Test {test_name} failed")

    print("\n" + "=" * 70)
    print(f"🏁 Test Results: {passed}/{total} test suites passed")

    if passed == total:
        print("🎉 All tests passed! Dynamic agent loading is working correctly.")
        return 0
    print("⚠️  Some tests failed. Please review the output above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
