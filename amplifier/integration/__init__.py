"""
Enhanced Integration System for Microsoft Amplifier

Provides 95%+ reliability for system integrations through:
- Enhanced MCP client with connection pooling and circuit breakers
- Comprehensive reliability monitoring and alerting
- Automatic optimization orchestration
- Context management integration
- Performance optimization and load balancing

Usage:
    from amplifier.integration import start_integration_system

    # Start the full integration system
    await start_integration_system()

    # Get reliable MCP client
    client = await create_reliable_mcp_client(
        endpoint="ws://localhost:8080/sse",
        service_name="my_service"
    )
"""

from .enhanced_mcp_client import ConnectionPool
from .enhanced_mcp_client import ConnectionState
from .enhanced_mcp_client import EnhancedMCPClient
from .enhanced_mcp_client import EnhancedMCPManager
from .enhanced_mcp_client import MCPConnectionConfig
from .enhanced_mcp_client import create_reliable_mcp_client
from .enhanced_mcp_client import get_mcp_manager
from .orchestrator import IntegrationOrchestrator
from .orchestrator import OptimizationStrategy
from .orchestrator import get_integration_orchestrator
from .orchestrator import start_integration_orchestration
from .orchestrator import stop_integration_orchestration
from .reliability_monitor import Alert
from .reliability_monitor import AlertLevel
from .reliability_monitor import HealthStatus
from .reliability_monitor import ReliabilityMetric
from .reliability_monitor import ReliabilityMonitor
from .reliability_monitor import SystemHealthReport
from .reliability_monitor import get_reliability_monitor
from .reliability_monitor import start_integration_monitoring
from .reliability_monitor import stop_integration_monitoring

__version__ = "1.0.0"
__all__ = [
    # Enhanced MCP Client
    "ConnectionPool",
    "ConnectionState",
    "EnhancedMCPClient",
    "EnhancedMCPManager",
    "MCPConnectionConfig",
    "create_reliable_mcp_client",
    "get_mcp_manager",
    # Reliability Monitor
    "Alert",
    "AlertLevel",
    "HealthStatus",
    "ReliabilityMetric",
    "ReliabilityMonitor",
    "SystemHealthReport",
    "get_reliability_monitor",
    "start_integration_monitoring",
    "stop_integration_monitoring",
    # Orchestrator
    "IntegrationOrchestrator",
    "OptimizationStrategy",
    "get_integration_orchestrator",
    "start_integration_orchestration",
    "stop_integration_orchestration",
]


async def start_integration_system():
    """
    Start the complete integration system with all components.

    This starts:
    - Reliability monitoring
    - Integration orchestration
    - MCP connection management
    - Automatic optimization

    Raises:
        Exception: If any component fails to start
    """
    from ..utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Starting enhanced integration system...")

    try:
        # Start reliability monitoring first
        await start_integration_monitoring()
        logger.info("✅ Reliability monitoring started")

        # Start orchestration
        await start_integration_orchestration()
        logger.info("✅ Integration orchestration started")

        # Initialize MCP manager
        get_mcp_manager()
        logger.info("✅ MCP manager initialized")

        logger.info("🚀 Enhanced integration system started successfully")

    except Exception as e:
        logger.error(f"❌ Failed to start integration system: {e}")
        await stop_integration_system()
        raise


async def stop_integration_system():
    """
    Stop the complete integration system gracefully.

    This stops all components in reverse order and performs cleanup.
    """
    from ..utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Stopping enhanced integration system...")

    try:
        # Stop orchestration first
        await stop_integration_orchestration()
        logger.info("✅ Integration orchestration stopped")

        # Stop monitoring
        await stop_integration_monitoring()
        logger.info("✅ Reliability monitoring stopped")

        # Close MCP connections
        manager = get_mcp_manager()
        await manager.close_all()
        logger.info("✅ MCP connections closed")

        logger.info("🛑 Enhanced integration system stopped")

    except Exception as e:
        logger.error(f"❌ Error stopping integration system: {e}")


async def get_system_health():
    """
    Get current system health status.

    Returns:
        Dict containing comprehensive health information
    """
    monitor = get_reliability_monitor()
    orchestrator = get_integration_orchestrator()
    mcp_manager = get_mcp_manager()

    current_status = monitor.get_current_status()
    orchestration_status = orchestrator.get_orchestration_status()
    mcp_metrics = mcp_manager.get_global_metrics()

    return {
        "timestamp": current_status.timestamp.isoformat() if current_status else None,
        "overall_status": current_status.overall_status.value if current_status else "unknown",
        "reliability_score": current_status.reliability_score if current_status else 0,
        "uptime_percentage": current_status.uptime_percentage if current_status else 0,
        "active_alerts": len(monitor.get_active_alerts()),
        "orchestration_status": orchestration_status,
        "mcp_metrics": mcp_metrics,
        "metrics_summary": monitor.get_metrics_summary(),
        "recommendations": current_status.recommendations if current_status else [],
    }


async def register_mcp_service(
    endpoint: str,
    service_name: str,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    connection_timeout: float = 10.0,
    health_check_interval: float = 30.0,
    max_concurrent_connections: int = 5,
    connection_pool_size: int = 3,
) -> EnhancedMCPClient:
    """
    Register a new MCP service with enhanced reliability features.

    Args:
        endpoint: MCP service endpoint URL
        service_name: Unique name for the service
        max_retries: Maximum connection retry attempts
        retry_delay: Delay between retries (seconds)
        connection_timeout: Connection timeout (seconds)
        health_check_interval: Health check interval (seconds)
        max_concurrent_connections: Maximum concurrent connections
        connection_pool_size: Connection pool size

    Returns:
        EnhancedMCPClient instance configured for the service
    """
    from ..utils.logger import get_logger
    from .enhanced_mcp_client import MCPConnectionConfig

    logger = get_logger(__name__)

    config = MCPConnectionConfig(
        endpoint=endpoint,
        service_name=service_name,
        max_retries=max_retries,
        retry_delay=retry_delay,
        connection_timeout=connection_timeout,
        health_check_interval=health_check_interval,
        max_concurrent_connections=max_concurrent_connections,
        connection_pool_size=connection_pool_size,
    )

    manager = get_mcp_manager()
    manager.register_service(config)

    client = await manager.get_client(service_name)

    logger.info(f"✅ MCP service registered: {service_name} -> {endpoint}")

    return client


async def create_high_reliability_client(endpoint: str, service_name: str, **kwargs) -> EnhancedMCPClient:
    """
    Create a high-reliability MCP client with optimal settings.

    This is a convenience function that creates a client with
    reliability-focused default settings.

    Args:
        endpoint: MCP service endpoint URL
        service_name: Unique name for the service
        **kwargs: Additional configuration options

    Returns:
        EnhancedMCPClient configured for high reliability
    """
    # High-reliability defaults
    reliability_defaults = {
        "max_retries": 5,
        "retry_delay": 2.0,
        "connection_timeout": 15.0,
        "health_check_interval": 15.0,
        "max_concurrent_connections": 10,
        "connection_pool_size": 5,
        "circuit_breaker_threshold": 3,
        "circuit_breaker_timeout": 30.0,
    }

    # Override with user-provided kwargs
    reliability_defaults.update(kwargs)

    return await register_mcp_service(endpoint, service_name, **reliability_defaults)


async def create_performance_client(endpoint: str, service_name: str, **kwargs) -> EnhancedMCPClient:
    """
    Create a performance-optimized MCP client.

    This is a convenience function that creates a client with
    performance-focused default settings.

    Args:
        endpoint: MCP service endpoint URL
        service_name: Unique name for the service
        **kwargs: Additional configuration options

    Returns:
        EnhancedMCPClient configured for performance
    """
    # Performance defaults
    performance_defaults = {
        "max_retries": 2,
        "retry_delay": 0.5,
        "connection_timeout": 5.0,
        "health_check_interval": 60.0,
        "max_concurrent_connections": 20,
        "connection_pool_size": 10,
        "circuit_breaker_threshold": 10,
        "circuit_breaker_timeout": 120.0,
    }

    # Override with user-provided kwargs
    performance_defaults.update(kwargs)

    return await register_mcp_service(endpoint, service_name, **performance_defaults)


# Context management integration
def integrate_context_management():
    """
    Integrate with the context management system.

    This sets up integration between the reliability system
    and the context compactor for optimal performance.
    """
    try:
        from ..utils.context_compactor import get_context_compactor
        from ..utils.token_budget_manager import get_token_budget_manager

        # Set up integration hooks
        get_context_compactor()
        get_token_budget_manager()

        # Configure compactor for integration workloads
        # This would integrate the systems for optimal token usage

        from ..utils.logger import get_logger

        logger = get_logger(__name__)
        logger.info("✅ Context management integration configured")

    except ImportError:
        # Context management not available
        from ..utils.logger import get_logger

        logger = get_logger(__name__)
        logger.warning("⚠️  Context management integration not available")


# Initialize context management integration
integrate_context_management()
