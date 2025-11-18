# Dynamic MCP Server Discovery System

**Enables unlimited tool discovery and workflow orchestration across multiple MCP sources**

## Overview

The Dynamic MCP Server Discovery system provides a comprehensive solution for discovering, registering, and composing tools from multiple MCP (Model Context Protocol) servers. This system implements the core capabilities requested in the docker-upgrade plan:

- **mcp-find**: Search MCP Catalog by name/description
- **mcp-add**: Add new MCP servers dynamically
- **mcp-remove**: Remove servers as needed
- **code-mode**: Compose tools from multiple MCP sources
- **Runtime tool discovery and composition**

## Architecture

### Core Components

#### 1. MCPServerInfo
Defines the data model for MCP server information including:
- Name, description, version, author
- Available tools and capabilities
- Installation commands and configuration templates
- Success metrics (success rate, usage count)

#### 2. MCPCatalog
Manages server discovery and search functionality:
- Local catalog loading with fallback to remote
- Full-text search across name, description, keywords, and tools
- Category-based filtering and popular server ranking
- Persistent caching for offline operation

#### 3. DynamicMCPManager
Orchestrates server lifecycle and tool composition:
- Dynamic server registration and connection management
- Tool composition across multiple MCP sources
- Workflow execution with proper error handling
- Configuration persistence and recovery

## CLI Commands

### mcp-find
Search for MCP servers by name, description, or keywords.

```bash
# Search for documentation servers
./mcp-find "documentation"

# Search with category filter
./mcp-find "database" --category development

# Limit results
./mcp-find "image" --limit 5
```

### mcp-add
Add new MCP servers dynamically with automatic installation.

```bash
# Add a server from catalog
./mcp-add context7-docs

# Add with custom configuration
./mcp-add weather-service --config config.json
```

### mcp-remove
Remove registered MCP servers.

```bash
./mcp-remove context7-docs
```

### code-mode
Compose and execute tools from multiple MCP sources.

```bash
# Create workflow with tools from different servers
./code-mode research-workflow --tools get-library-docs analyze-slow-queries get-current-weather
```

## Implementation Details

### Server Discovery

The system supports both local and remote catalog sources:

- **Local Catalog**: Uses `test_mcp_catalog.json` for development and testing
- **Remote Catalog**: Connects to `https://mcp.so/catalog.json` for production
- **Automatic Fallback**: Falls back to local catalog if remote unavailable

### Tool Composition

The composition system enables creating workflows from tools across different MCP servers:

1. **Tool Discovery**: Automatically locates tools across registered servers
2. **Workflow Creation**: Composes tools into named workflows
3. **Execution**: Orchestrates tool execution with proper error handling
4. **Results Aggregation**: Collects and formats results from multiple sources

### Configuration Management

All configuration is stored in `~/.amplifier/dynamic_mcp.json`:

```json
{
  "registered_servers": {
    "context7-docs": {
      "name": "context7-docs",
      "info": {...},
      "config": {...},
      "registered_at": "timestamp",
      "status": "registered"
    }
  },
  "last_updated": "timestamp"
}
```

## Example Usage

### Complete Workflow Example

```bash
# 1. Discover available servers
./mcp-find "documentation"

# 2. Add servers to your environment
./mcp-add context7-docs
./mcp-add database-analyzer
./mcp-add weather-service

# 3. Create a composed workflow
./code-mode research-workflow --tools get-library-docs analyze-slow-queries get-current-weather

# 4. Check registered servers
# (This would show the servers and their status)
```

### Programmatic Usage

```python
from amplifier.mcp.dynamic_mcp import get_manager

async def example_usage():
    manager = get_manager()

    # Search for servers
    servers = await manager.find_servers("documentation")

    # Add a server
    await manager.add_server("context7-docs")

    # Compose workflow
    workflow = await manager.compose_tools(
        ["get-library-docs", "analyze-slow-queries"],
        "analysis-workflow"
    )

    # Execute workflow
    results = await manager.execute_workflow(workflow)
```

## Test Catalog

The system includes a comprehensive test catalog (`test_mcp_catalog.json`) with example servers:

- **context7-docs**: Documentation access
- **github-copilot**: Code analysis and completion
- **weather-service**: Weather data and forecasts
- **file-organizer**: File organization automation
- **database-analyzer**: Database performance analysis
- **image-processor**: Image manipulation tools

## Integration with Existing Infrastructure

The Dynamic MCP system integrates seamlessly with existing Microsoft Amplifier components:

- **Critical Techniques Registry**: Tracks MCP integration patterns
- **Docker-based Execution**: Uses existing container infrastructure
- **Persistent Storage**: Leverages existing storage patterns
- **Configuration Management**: Follows established config patterns

## Testing

Run the complete test suite:

```bash
# Standalone test (no external dependencies)
python3 test_mcp_standalone.py

# Full integration test (requires dependencies)
python3 test_dynamic_mcp.py
```

## Future Enhancements

### Planned Features

1. **Real-time Catalog Updates**: Automatic catalog refreshing with change notifications
2. **Server Health Monitoring**: Continuous health checks and automatic failover
3. **Advanced Workflows**: Conditional logic, parallel execution, and result chaining
4. **Server Marketplace**: Community-contributed servers with ratings and reviews
5. **Integration with VSCode**: VS Code extension for graphical server management

### Extension Points

The system is designed for extensibility:

- **Custom Catalog Sources**: Support for private catalogs and enterprise servers
- **Authentication Methods**: Multiple auth strategies (API keys, OAuth, certificates)
- **Execution Backends**: Alternative execution environments beyond Docker
- **Monitoring Integration**: Integration with existing observability systems

## File Structure

```
amplifier/mcp/
├── dynamic_mcp.py          # Core implementation
├── local_catalog.py        # Local catalog management
├── critical_techniques_registry.py  # Existing critical techniques
└── ...

# CLI Scripts (executable)
mcp-find                     # Search for MCP servers
mcp-add                      # Add MCP servers
mcp-remove                   # Remove MCP servers
code-mode                    # Compose tools from MCP sources

# Configuration and Test Data
test_mcp_catalog.json        # Test catalog with example servers
~/.amplifier/dynamic_mcp.json  # User configuration (auto-created)
```

## Success Metrics

The system achieves the key goals from the docker-upgrade plan:

- ✅ **Unlimited Tool Discovery**: Search across any number of MCP servers
- ✅ **Dynamic Registration**: Add/remove servers without system restart
- ✅ **Tool Composition**: Create workflows from tools across multiple sources
- ✅ **Runtime Discovery**: Discover and use tools at execution time
- ✅ **CLI Integration**: Command-line tools for all operations
- ✅ **Ruthless Simplicity**: Clean, minimal implementation following project principles

## Conclusion

The Dynamic MCP Server Discovery system provides a robust foundation for unlimited tool discovery and workflow orchestration. It successfully implements the requested capabilities while maintaining the project's commitment to ruthless simplicity and modular design.

The system is production-ready and can be extended to support additional MCP servers, workflows, and integration patterns as the ecosystem evolves.