"""
Local MCP Catalog for testing and development
"""

import json
from pathlib import Path

from amplifier.mcp.dynamic_mcp import MCPServerInfo


def load_local_catalog(catalog_path: Path = None) -> dict[str, MCPServerInfo]:
    """Load MCP catalog from local JSON file"""
    if catalog_path is None:
        catalog_path = Path(__file__).parent.parent.parent / "test_mcp_catalog.json"

    if not catalog_path.exists():
        print(f"⚠️  Local catalog not found at {catalog_path}")
        return {}

    try:
        with open(catalog_path) as f:
            catalog_data = json.load(f)

        servers = {}
        for name, server_data in catalog_data.get("servers", {}).items():
            servers[name] = MCPServerInfo(**server_data)

        print(f"✅ Loaded {len(servers)} servers from local catalog")
        return servers

    except Exception as e:
        print(f"❌ Failed to load local catalog: {e}")
        return {}


def get_test_servers() -> dict[str, MCPServerInfo]:
    """Get test servers for development"""
    return cast(dict[str, Any], load_local_catalog())
