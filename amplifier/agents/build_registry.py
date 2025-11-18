#!/usr/bin/env python3
"""
Build agent registry script

Builds the lightweight agent registry from all agent definitions.
Run this after adding new agents or updating existing ones.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from amplifier.agents.dynamic_loader import get_agent_loader


def main():
    parser = argparse.ArgumentParser(description="Build agent registry")
    parser.add_argument("--force", "-f", action="store_true", help="Force rebuild registry even if it exists")
    parser.add_argument("--stats", "-s", action="store_true", help="Show registry statistics after building")
    parser.add_argument("--agents-dir", "-a", default=".claude/agents", help="Directory containing agent definitions")

    args = parser.parse_args()

    print("🔧 Building Agent Registry")
    print(f"📁 Agents directory: {args.agents_dir}")

    loader = get_agent_loader()
    loader.agents_dir = Path(args.agents_dir)

    # Build registry
    count = loader.build_registry(force_rebuild=args.force)

    if count > 0:
        print(f"✅ Built registry with {count} agents")
        print(f"📄 Registry file: {loader.registry_file}")

        if args.stats:
            stats = loader.get_registry_stats()
            print("\n📊 Registry Statistics:")
            print(f"   Total agents: {stats['total_agents']}")
            print(f"   Total tokens (full definitions): {stats['total_tokens_full']:,}")
            print(f"   Metadata tokens: {stats['total_tokens_metadata']:,}")
            print(f"   Memory efficiency: {stats['memory_efficiency']:.1f}%")

            print("\n🏷️  Tag Distribution:")
            for tag, count in list(stats["tag_distribution"].items())[:10]:
                print(f"   {tag}: {count}")

    else:
        print("❌ No agents found")
        sys.exit(1)


if __name__ == "__main__":
    main()
