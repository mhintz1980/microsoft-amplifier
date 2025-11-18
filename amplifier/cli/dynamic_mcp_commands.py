"""
Dynamic MCP CLI Commands

Provides command-line interface for Dynamic MCP Server Discovery system.
"""

import asyncio

import click

from amplifier.mcp.dynamic_mcp import get_manager


@click.group()
def mcp():
    """Dynamic MCP Server Discovery System"""
    pass


@mcp.command()
@click.argument("query")
@click.option("--category", "-c", help="Filter by server category")
@click.option("--limit", "-l", default=10, help="Maximum number of results")
def find(query: str, category: str | None, limit: int):
    """Search for MCP servers by name, description, or keywords"""

    async def _find():
        manager = get_manager()
        servers = await manager.find_servers(query, category, limit)

        if not servers:
            click.echo("❌ No servers found")
            return

        click.echo(f"🔍 Found {len(servers)} servers matching '{query}':")
        for server in servers:
            click.echo(f"  • {click.style(server.name, bold=True)} (v{server.version})")
            click.echo(f"    {server.description}")
            if server.tools:
                tools_display = ", ".join(server.tools[:5])
                if len(server.tools) > 5:
                    tools_display += "..."
                click.echo(f"    🛠️  Tools: {tools_display}")
            if server.homepage:
                click.echo(f"    🌐 {server.homepage}")
            click.echo()

    asyncio.run(_find())


@mcp.command()
@click.argument("server_name")
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file")
def add(server_name: str, config: str | None):
    """Add a new MCP server dynamically"""

    async def _add():
        manager = get_manager()

        # Load config if provided
        server_config = None
        if config:
            import json

            with open(config) as f:
                server_config = json.load(f)

        # type: ignore[arg-type]
        # type: ignore[arg-type]
        success = await manager.add_server(server_name, server_config)
        if success:
            click.echo(f"🎉 Successfully added {click.style(server_name, bold=True)}")
        else:
            click.echo(f"❌ Failed to add {server_name}", err=True)

    asyncio.run(_add())


@mcp.command()
@click.argument("server_name")
@click.confirmation_option(prompt="Are you sure you want to remove this server?")
def remove(server_name: str):
    """Remove an MCP server"""

    async def _remove():
        manager = get_manager()
        success = await manager.remove_server(server_name)
        if success:
            click.echo(f"🗑️  Successfully removed {click.style(server_name, bold=True)}")
        else:
            click.echo(f"❌ Failed to remove {server_name}", err=True)

    asyncio.run(_remove())


@mcp.command()
def list():
    """List all registered MCP servers"""

    async def _list():
        manager = get_manager()
        servers = manager.list_registered_servers()

        if not servers:
            click.echo("📭 No servers registered")
            return

        click.echo(f"📋 Registered servers ({len(servers)}):")
        for server in servers:
            status_emoji = "🟢" if server["status"] == "connected" else "🔴"
            click.echo(f"  {status_emoji} {click.style(server['name'], bold=True)} - {server['status']}")
            click.echo(f"    {server['info']['description']}")

            # Show tools if available
            tools = server["info"].get("tools", [])
            if tools:
                tools_display = ", ".join(tools[:3])
                if len(tools) > 3:
                    tools_display += f" (+{len(tools) - 3} more)"
                click.echo(f"    🛠️  {tools_display}")

    asyncio.run(_list())


@mcp.command()
def refresh():
    """Refresh the MCP server catalog"""

    async def _refresh():
        manager = get_manager()
        count = await manager.catalog.refresh_catalog()
        click.echo(f"📦 Catalog refreshed with {count} servers")

    asyncio.run(_refresh())


@mcp.command()
def categories():
    """List all available server categories"""

    async def _categories():
        manager = get_manager()

        # Ensure catalog is loaded
        if not manager.catalog.servers:
            await manager.catalog.refresh_catalog()

        categories = manager.catalog.list_categories()

        if not categories:
            click.echo("📭 No categories found")
            return

        click.echo("📂 Available categories:")
        for category in categories:
            # Count servers in this category
            count = sum(1 for s in manager.catalog.servers.values() if s.category == category)
            click.echo(f"  • {click.style(category, bold=True)} ({count} servers)")

    asyncio.run(_categories())


@click.command()
@click.argument("workflow_name")
@click.option("--tools", "-t", multiple=True, required=True, help="Tools to include in workflow")
def code_mode(workflow_name: str, tools):
    """Compose and execute tools from multiple MCP sources"""

    async def _code_mode():
        manager = get_manager()

        # Compose workflow
        workflow = await manager.compose_tools(list(tools), workflow_name)

        if not workflow["tools"]:
            click.echo("❌ No valid tools found for workflow")
            return

        # Show workflow composition
        click.echo(f"🔧 Workflow '{click.style(workflow_name, bold=True)}' composition:")
        for tool in workflow["tools"]:
            click.echo(f"  • {tool['qualified_name']}")

        # Execute workflow
        results = await manager.execute_workflow(workflow)

        click.echo("\n📊 Workflow Results:")
        for tool, result in results.items():
            click.echo(f"  {tool}: {result}")

    asyncio.run(_code_mode())


# Register commands with main CLI
def register_commands(cli_group):
    """Register dynamic MCP commands with the main CLI group"""
    cli_group.add_command(mcp)
    cli_group.add_command(code_mode, name="code")


if __name__ == "__main__":
    # For testing purposes
    mcp()  # type: ignore
