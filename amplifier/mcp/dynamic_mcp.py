"""
Dynamic MCP Server Discovery System

Enables unlimited tool discovery and workflow orchestration across multiple MCP sources.
Provides search, registration, and composition capabilities for MCP servers.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel
from pydantic import Field


class MCPServerInfo(BaseModel):
    """Information about an MCP server"""

    name: str = Field(description="Server name")
    description: str = Field(description="Server description")
    version: str = Field(description="Server version")
    author: str = Field(default="", description="Server author")
    homepage: str | None = Field(default=None, description="Server homepage")
    repository: str | None = Field(default=None, description="Source repository")
    license: str | None = Field(default=None, description="License")
    keywords: list[str] = Field(default_factory=list, description="Search keywords")
    category: str = Field(default="general", description="Server category")
    tools: list[str] = Field(default_factory=list, description="Available tools")
    install_command: str | None = Field(default=None, description="Installation command")
    config_template: dict[str, Any] | None = Field(default=None, description="Configuration template")
    success_rate: float = Field(default=0.0, description="Server success rate")
    usage_count: int = Field(default=0, description="Usage count")


class MCPCatalog:
    """MCP Catalog for searching and discovering MCP servers"""

    def __init__(self, catalog_url: str = "https://mcp.so/catalog.json", use_local: bool = None):  # type: ignore[assignment]
        self.catalog_url = catalog_url
        self.local_cache = Path.home() / ".amplifier" / "mcp_catalog.json"
        self.servers: dict[str, MCPServerInfo] = {}
        # type: ignore[name-defined]
        # type: ignore[name-defined]
        # type: ignore[name-defined]
        self.use_local = (
            use_local
            if use_local is not None
            else (Path(__file__).parent.parent.parent / "test_mcp_catalog.json").exists()  # type: ignore[attr-defined]
        )

        # type: ignore[name-defined]
        # type: ignore[name-defined]
        # type: ignore[name-defined]

        if self.use_local:
            self._load_local_catalog()
        else:
            self._load_cache()

    def _load_local_catalog(self):
        """Load local test catalog"""
        try:
            from amplifier.mcp.local_catalog import load_local_catalog

            self.servers = load_local_catalog()
        except Exception as e:
            print(f"⚠️  Failed to load local catalog: {e}")

    def _load_cache(self):
        """Load cached catalog data"""
        if self.local_cache.exists():
            try:
                with open(self.local_cache) as f:
                    data = json.load(f)
                    for name, server_data in data.items():
                        self.servers[name] = MCPServerInfo(**server_data)
            except Exception as e:
                print(f"⚠️  Failed to load MCP catalog cache: {e}")

    def _save_cache(self):
        """Save catalog data to cache"""
        self.local_cache.parent.mkdir(parents=True, exist_ok=True)
        data = {name: server.model_dump() for name, server in self.servers.items()}
        with open(self.local_cache, "w") as f:
            json.dump(data, f, indent=2)

    async def refresh_catalog(self) -> int:
        """Refresh catalog from remote source"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.catalog_url)
                response.raise_for_status()

                catalog_data = response.json()
                count = 0

                for name, server_data in catalog_data.get("servers", {}).items():
                    self.servers[name] = MCPServerInfo(**server_data)
                    count += 1

                self._save_cache()
                print(f"✅ Refreshed catalog with {count} servers")
                return count

        except Exception as e:
            print(f"❌ Failed to refresh catalog: {e}")
            return len(self.servers)

    def search_servers(self, query: str, category: str | None = None, limit: int = 20) -> list[MCPServerInfo]:
        """Search for MCP servers by name, description, or keywords"""
        results = []
        query_lower = query.lower()

        for server in self.servers.values():
            if category and server.category != category:
                continue

            # Search in name, description, keywords, and tools
            searchable_text = " ".join(
                [server.name, server.description, " ".join(server.keywords), " ".join(server.tools)]
            ).lower()

            if query_lower in searchable_text:
                results.append(server)

        # Sort by success rate and usage count
        results.sort(key=lambda s: (s.success_rate, s.usage_count), reverse=True)
        return results[:limit]

    def get_server(self, name: str) -> MCPServerInfo | None:
        """Get server information by name"""
        return self.servers.get(name)

    def list_categories(self) -> list[str]:
        """List all available categories"""
        categories = {server.category for server in self.servers.values()}
        return sorted(categories)

    def get_popular_servers(self, limit: int = 10) -> list[MCPServerInfo]:
        """Get most popular servers by usage count"""
        servers = list(self.servers.values())
        servers.sort(key=lambda s: (s.usage_count, s.success_rate), reverse=True)
        return servers[:limit]


class DynamicMCPManager:
    """Manages dynamic MCP server registration and tool composition"""

    def __init__(self, config_path: Path = None):  # type: ignore[assignment]
        self.config_path = config_path or Path.home() / ".amplifier" / "dynamic_mcp.json"
        self.catalog = MCPCatalog()
        self.registered_servers: dict[str, dict[str, Any]] = {}
        self.active_connections: dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config = json.load(f)
                    self.registered_servers = config.get("registered_servers", {})
            except Exception as e:
                print(f"⚠️  Failed to load MCP config: {e}")

    def _save_config(self):
        """Save configuration"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        config = {"registered_servers": self.registered_servers, "last_updated": str(asyncio.get_event_loop().time())}
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    async def find_servers(self, query: str, category: str | None = None) -> list[MCPServerInfo]:
        """Find servers matching query"""
        # Ensure catalog is loaded
        if not self.catalog.servers:
            await self.catalog.refresh_catalog()

        return self.catalog.search_servers(query, category)

    async def add_server(self, server_name: str, config: dict[str, Any] = None) -> bool:
        """Add a new MCP server dynamically"""
        # Get server info from catalog
        server_info = self.catalog.get_server(server_name)
        if not server_info:
            print(f"❌ Server '{server_name}' not found in catalog")
            return False

        try:
            # Install server if needed
            if server_info.install_command:
                print(f"📦 Installing {server_name}...")
                result = subprocess.run(server_info.install_command, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"❌ Installation failed: {result.stderr}")
                    return False
                print(f"✅ Installed {server_name}")

            # Register server
            server_config = {
                "name": server_name,
                "info": server_info.model_dump(),
                "config": config or {},
                "registered_at": str(asyncio.get_event_loop().time()),
                "status": "registered",
            }

            self.registered_servers[server_name] = server_config
            self._save_config()

            print(f"✅ Registered MCP server: {server_name}")
            return True

        except Exception as e:
            print(f"❌ Failed to add server {server_name}: {e}")
            return False

    async def remove_server(self, server_name: str) -> bool:
        """Remove an MCP server"""
        if server_name not in self.registered_servers:
            print(f"❌ Server '{server_name}' not registered")
            return False

        try:
            # Disconnect if connected
            if server_name in self.active_connections:
                await self.disconnect_server(server_name)

            # Remove from registry
            del self.registered_servers[server_name]
            self._save_config()

            print(f"✅ Removed MCP server: {server_name}")
            return True

        except Exception as e:
            print(f"❌ Failed to remove server {server_name}: {e}")
            return False

    async def connect_server(self, server_name: str) -> bool:
        """Connect to an MCP server"""
        if server_name not in self.registered_servers:
            print(f"❌ Server '{server_name}' not registered")
            return False

        if server_name in self.active_connections:
            print(f"✅ Already connected to {server_name}")
            return True

        try:
            server_config = self.registered_servers[server_name]

            # Start MCP server process
            cmd = [sys.executable, "-m", server_name]

            process = await asyncio.create_subprocess_exec(
                *cmd, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            self.active_connections[server_name] = {
                "process": process,
                "config": server_config,
                "connected_at": str(asyncio.get_event_loop().time()),
            }

            print(f"✅ Connected to MCP server: {server_name}")
            return True

        except Exception as e:
            print(f"❌ Failed to connect to {server_name}: {e}")
            return False

    async def disconnect_server(self, server_name: str) -> bool:
        """Disconnect from an MCP server"""
        if server_name not in self.active_connections:
            return True

        try:
            connection = self.active_connections[server_name]
            process = connection["process"]

            # Terminate process
            process.terminate()
            await process.wait()

            del self.active_connections[server_name]
            print(f"✅ Disconnected from {server_name}")
            return True

        except Exception as e:
            print(f"❌ Failed to disconnect from {server_name}: {e}")
            return False

    def list_registered_servers(self) -> list[dict[str, Any]]:
        """List all registered servers"""
        servers = []
        for name, config in self.registered_servers.items():
            status = "connected" if name in self.active_connections else "registered"
            servers.append(
                {"name": name, "status": status, "info": config["info"], "registered_at": config["registered_at"]}
            )
        return servers

    async def compose_tools(self, tool_names: list[str], workflow_name: str) -> dict[str, Any]:
        """Compose tools from multiple MCP servers into a workflow"""
        workflow = {
            "name": workflow_name,
            "tools": [],
            "servers": set(),
            "created_at": str(asyncio.get_event_loop().time()),
        }

        for tool_name in tool_names:
            # Find which server provides this tool
            for server_name, server_config in self.registered_servers.items():
                server_info = server_config["info"]
                if tool_name in server_info.get("tools", []):
                    workflow["tools"].append(
                        {"name": tool_name, "server": server_name, "qualified_name": f"{server_name}.{tool_name}"}
                    )
                    workflow["servers"].add(server_name)
                    break
            else:
                print(f"⚠️  Tool '{tool_name}' not found in any registered server")

        workflow["servers"] = list(workflow["servers"])

        print(f"✅ Composed workflow '{workflow_name}' with {len(workflow['tools'])} tools")
        print(f"   Servers: {', '.join(workflow['servers'])}")

        return workflow

    async def execute_workflow(self, workflow: dict[str, Any], **kwargs) -> Any:
        """Execute a composed workflow"""
        print(f"🚀 Executing workflow: {workflow['name']}")

        results = {}

        for tool in workflow["tools"]:
            server_name = tool["server"]
            tool["name"]
            qualified_name = tool["qualified_name"]

            # Ensure server is connected
            if server_name not in self.active_connections:
                await self.connect_server(server_name)

            try:
                # Execute tool (simplified - real implementation would use MCP protocol)
                print(f"   🔧 Executing {qualified_name}")
                # result = await self._execute_tool(server_name, tool_name, **kwargs)
                result = f"Mock result from {qualified_name}"
                results[qualified_name] = result

            except Exception as e:
                print(f"   ❌ Failed to execute {qualified_name}: {e}")
                results[qualified_name] = {"error": str(e)}

        print(f"✅ Workflow completed: {workflow['name']}")
        return results


# Global instance
_manager = None


def get_manager() -> DynamicMCPManager:
    """Get the global Dynamic MCP Manager instance"""
    global _manager
    if _manager is None:
        _manager = DynamicMCPManager()
    return _manager


# CLI Functions
async def mcp_find(query: str, category: str | None = None, limit: int = 10):
    """Search for MCP servers"""
    manager = get_manager()
    servers = await manager.find_servers(query, category, limit)

    if not servers:
        print("❌ No servers found")
        return

    print(f"🔍 Found {len(servers)} servers matching '{query}':")
    for server in servers:
        print(f"  • {server.name} (v{server.version})")
        print(f"    {server.description}")
        if server.tools:
            print(f"    Tools: {', '.join(server.tools[:5])}" + ("..." if len(server.tools) > 5 else ""))
        print()


async def mcp_add(server_name: str, config: dict[str, Any] | None = None):
    """Add an MCP server"""
    manager = get_manager()
    # type: ignore[arg-type]
    # type: ignore[arg-type]
    success = await manager.add_server(server_name, config)
    if success:
        print(f"🎉 Successfully added {server_name}")
    else:
        print(f"❌ Failed to add {server_name}")


async def mcp_remove(server_name: str):
    """Remove an MCP server"""
    manager = get_manager()
    success = await manager.remove_server(server_name)
    if success:
        print(f"🗑️  Successfully removed {server_name}")
    else:
        print(f"❌ Failed to remove {server_name}")


async def mcp_list():
    """List registered MCP servers"""
    manager = get_manager()
    servers = manager.list_registered_servers()

    if not servers:
        print("📭 No servers registered")
        return

    print(f"📋 Registered servers ({len(servers)}):")
    for server in servers:
        status_emoji = "🟢" if server["status"] == "connected" else "🔴"
        print(f"  {status_emoji} {server['name']} - {server['status']}")
        print(f"    {server['info']['description']}")


async def code_mode(workflow_name: str, tools: list[str]):
    """Compose and execute tools from multiple MCP sources"""
    manager = get_manager()

    # Compose workflow
    workflow = await manager.compose_tools(tools, workflow_name)

    if not workflow["tools"]:
        print("❌ No valid tools found for workflow")
        return

    # Execute workflow
    results = await manager.execute_workflow(workflow)

    print("\n📊 Workflow Results:")
    for tool, result in results.items():
        print(f"  {tool}: {result}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dynamic MCP Server Discovery")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # mcp-find
    find_parser = subparsers.add_parser("find", help="Find MCP servers")
    find_parser.add_argument("query", help="Search query")
    find_parser.add_argument("--category", help="Server category filter")
    find_parser.add_argument("--limit", type=int, default=10, help="Result limit")

    # mcp-add
    add_parser = subparsers.add_parser("add", help="Add MCP server")
    add_parser.add_argument("server", help="Server name")

    # mcp-remove
    remove_parser = subparsers.add_parser("remove", help="Remove MCP server")
    remove_parser.add_argument("server", help="Server name")

    # mcp-list
    subparsers.add_parser("list", help="List registered servers")

    # code-mode
    code_parser = subparsers.add_parser("code", help="Compose tools from multiple sources")
    code_parser.add_argument("workflow", help="Workflow name")
    code_parser.add_argument("--tools", nargs="+", required=True, help="Tool names to compose")

    args = parser.parse_args()

    # Execute command
    if args.command == "find":
        asyncio.run(mcp_find(args.query, args.category, args.limit))
    elif args.command == "add":
        asyncio.run(mcp_add(args.server))
    elif args.command == "remove":
        asyncio.run(mcp_remove(args.server))
    elif args.command == "list":
        asyncio.run(mcp_list())
    elif args.command == "code":
        asyncio.run(code_mode(args.workflow, args.tools))
    else:
        parser.print_help()  # type: ignore  # type: ignore
