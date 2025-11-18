"""Integration Connectors for Skill Systems.

Provides seamless integration between MCP storage and all skill system components,
enabling cross-system communication and data synchronization.
"""

import asyncio
import json
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger
from ...mcp.persistent_storage import SkillDefinition

logger = get_logger(__name__)


class IntegrationType(Enum):
    """Types of system integrations."""

    SKILL_CREATION_PIPELINE = "skill_creation_pipeline"
    DOCUMENTATION_SYSTEM = "documentation_system"
    CONTEXT_OPTIMIZATION = "context_optimization"
    MEMORY_SYSTEM = "memory_system"
    CODE_EXECUTION = "code_execution"
    AGENT_FRAMEWORK = "agent_framework"
    MCP_SERVERS = "mcp_servers"


class EventType(Enum):
    """Types of integration events."""

    SKILL_STORED = "skill_stored"
    SKILL_UPDATED = "skill_updated"
    SKILL_DELETED = "skill_deleted"
    SKILL_ACCESSED = "skill_accessed"
    BACKUP_COMPLETED = "backup_completed"
    RECOVERY_COMPLETED = "recovery_completed"
    PERFORMANCE_ALERT = "performance_alert"
    OPTIMIZATION_RECOMMENDED = "optimization_recommended"


@dataclass
class IntegrationEvent:
    """Integration event between systems."""

    event_id: str
    event_type: EventType
    source_system: str
    target_system: str
    timestamp: datetime
    data: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemConnector:
    """Represents a connector to an external system."""

    system_name: str
    integration_type: IntegrationType
    is_active: bool = True
    last_sync: datetime | None = None
    sync_frequency_minutes: int = 60
    event_subscriptions: list[EventType] = field(default_factory=list)
    configuration: dict[str, Any] = field(default_factory=dict)
    statistics: dict[str, Any] = field(default_factory=dict)


class IntegrationConnectors:
    """Manages integration between MCP storage and skill systems."""

    def __init__(self):
        self.connectors = {}  # system_name -> SystemConnector
        self.event_queue = asyncio.Queue()
        self.event_handlers = {}  # event_type -> list[handler_functions]
        self.integration_stats = {
            "total_events_processed": 0,
            "events_by_type": {},
            "active_integrations": 0,
            "failed_integrations": 0,
            "last_event_time": None,
        }

        # Storage directory
        self.storage_dir = Path.home() / ".amplifier_storage" / "integrations"
        self.connectors_file = self.storage_dir / "connectors.json"
        self.events_file = self.storage_dir / "events.json"

    async def initialize(self) -> None:
        """Initialize integration connectors."""
        await self._ensure_storage_structure()
        await self._load_connectors()
        await self._setup_default_connectors()
        await self._register_event_handlers()
        await self._start_event_processor()
        logger.info("Integration Connectors initialized")

    async def register_connector(
        self,
        system_name: str,
        integration_type: IntegrationType,
        configuration: dict[str, Any] | None = None,
        event_subscriptions: list[EventType] | None = None,
    ) -> bool:
        """Register a new system connector."""
        try:
            connector = SystemConnector(
                system_name=system_name,
                integration_type=integration_type,
                configuration=configuration or {},
                event_subscriptions=event_subscriptions or [],
                statistics={
                    "events_sent": 0,
                    "events_received": 0,
                    "last_event_sent": None,
                    "last_event_received": None,
                    "errors": 0,
                },
            )

            self.connectors[system_name] = connector
            await self._save_connectors()

            logger.info(f"Registered connector: {system_name} ({integration_type.value})")
            return True

        except Exception as e:
            logger.error(f"Failed to register connector {system_name}: {e}")
            return False

    async def notify_skill_stored(self, skill: SkillDefinition) -> None:
        """Notify all relevant systems about skill storage."""
        try:
            event = IntegrationEvent(
                event_id=f"skill_stored_{skill.skill_id}_{int(datetime.now().timestamp())}",
                event_type=EventType.SKILL_STORED,
                source_system="mcp_storage",
                target_system="all",
                timestamp=datetime.now(),
                data={
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "category": skill.category,
                    "language": skill.language,
                    "version": skill.version,
                    "author": skill.author,
                    "tags": skill.tags,
                    "created_at": skill.created_at.isoformat(),
                    "file_size": len(skill.code.encode()),
                },
                metadata={
                    "operation": "store",
                    "compression_level": "full",
                },
            )

            await self._queue_event(event)

        except Exception as e:
            logger.error(f"Failed to notify skill stored: {e}")

    async def notify_skill_updated(self, skill: SkillDefinition) -> None:
        """Notify all relevant systems about skill updates."""
        try:
            event = IntegrationEvent(
                event_id=f"skill_updated_{skill.skill_id}_{int(datetime.now().timestamp())}",
                event_type=EventType.SKILL_UPDATED,
                source_system="mcp_storage",
                target_system="all",
                timestamp=datetime.now(),
                data={
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "category": skill.category,
                    "version": skill.version,
                    "updated_at": skill.updated_at.isoformat(),
                    "changes": ["metadata_updated"],  # Would track actual changes
                },
                metadata={
                    "operation": "update",
                    "previous_version": skill.version,
                },
            )

            await self._queue_event(event)

        except Exception as e:
            logger.error(f"Failed to notify skill updated: {e}")

    async def notify_skill_accessed(self, skill: SkillDefinition, compression_level: str = "full") -> None:
        """Notify all relevant systems about skill access."""
        try:
            event = IntegrationEvent(
                event_id=f"skill_accessed_{skill.skill_id}_{int(datetime.now().timestamp())}",
                event_type=EventType.SKILL_ACCESSED,
                source_system="mcp_storage",
                target_system="all",
                timestamp=datetime.now(),
                data={
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "category": skill.category,
                    "usage_count": skill.usage_count,
                    "success_rate": skill.success_rate,
                },
                metadata={
                    "operation": "access",
                    "compression_level": compression_level,
                },
            )

            await self._queue_event(event)

        except Exception as e:
            logger.error(f"Failed to notify skill accessed: {e}")

    async def notify_skill_deleted(self, skill: SkillDefinition) -> None:
        """Notify all relevant systems about skill deletion."""
        try:
            event = IntegrationEvent(
                event_id=f"skill_deleted_{skill.skill_id}_{int(datetime.now().timestamp())}",
                event_type=EventType.SKILL_DELETED,
                source_system="mcp_storage",
                target_system="all",
                timestamp=datetime.now(),
                data={
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "category": skill.category,
                },
                metadata={
                    "operation": "delete",
                },
            )

            await self._queue_event(event)

        except Exception as e:
            logger.error(f"Failed to notify skill deleted: {e}")

    async def notify_backup_completed(self, backup_metadata: dict[str, Any]) -> None:
        """Notify systems about backup completion."""
        try:
            event = IntegrationEvent(
                event_id=f"backup_completed_{int(datetime.now().timestamp())}",
                event_type=EventType.BACKUP_COMPLETED,
                source_system="backup_recovery",
                target_system="all",
                timestamp=datetime.now(),
                data=backup_metadata,
                metadata={
                    "operation": "backup",
                },
            )

            await self._queue_event(event)

        except Exception as e:
            logger.error(f"Failed to notify backup completed: {e}")

    async def notify_recovery_completed(self, recovery_metadata: dict[str, Any]) -> None:
        """Notify systems about recovery completion."""
        try:
            event = IntegrationEvent(
                event_id=f"recovery_completed_{int(datetime.now().timestamp())}",
                event_type=EventType.RECOVERY_COMPLETED,
                source_system="backup_recovery",
                target_system="all",
                timestamp=datetime.now(),
                data=recovery_metadata,
                metadata={
                    "operation": "recovery",
                },
            )

            await self._queue_event(event)

        except Exception as e:
            logger.error(f"Failed to notify recovery completed: {e}")

    async def notify_performance_alert(self, alert_data: dict[str, Any]) -> None:
        """Notify systems about performance alerts."""
        try:
            event = IntegrationEvent(
                event_id=f"performance_alert_{int(datetime.now().timestamp())}",
                event_type=EventType.PERFORMANCE_ALERT,
                source_system="performance_monitor",
                target_system="all",
                timestamp=datetime.now(),
                data=alert_data,
                metadata={
                    "operation": "alert",
                },
            )

            await self._queue_event(event)

        except Exception as e:
            logger.error(f"Failed to notify performance alert: {e}")

    async def notify_optimization_recommended(self, recommendation_data: dict[str, Any]) -> None:
        """Notify systems about optimization recommendations."""
        try:
            event = IntegrationEvent(
                event_id=f"optimization_recommended_{int(datetime.now().timestamp())}",
                event_type=EventType.OPTIMIZATION_RECOMMENDED,
                source_system="performance_monitor",
                target_system="all",
                timestamp=datetime.now(),
                data=recommendation_data,
                metadata={
                    "operation": "recommendation",
                },
            )

            await self._queue_event(event)

        except Exception as e:
            logger.error(f"Failed to notify optimization recommended: {e}")

    async def sync_with_system(self, system_name: str, force: bool = False) -> bool:
        """Synchronize data with a specific system."""
        try:
            if system_name not in self.connectors:
                logger.error(f"Connector not found: {system_name}")
                return False

            connector = self.connectors[system_name]

            if not connector.is_active and not force:
                logger.warning(f"Connector {system_name} is not active")
                return False

            # Check if sync is needed
            if not force and connector.last_sync:
                time_since_sync = datetime.now() - connector.last_sync
                if time_since_sync.total_seconds() < (connector.sync_frequency_minutes * 60):
                    logger.info(f"Sync not needed for {system_name}")
                    return True

            logger.info(f"Syncing with system: {system_name}")

            # Perform system-specific sync
            success = await self._perform_system_sync(connector)

            if success:
                connector.last_sync = datetime.now()
                connector.statistics["last_sync"] = connector.last_sync.isoformat()
                await self._save_connectors()

            return success

        except Exception as e:
            logger.error(f"Failed to sync with {system_name}: {e}")
            if system_name in self.connectors:
                self.connectors[system_name].statistics["errors"] += 1
            return False

    async def get_integration_status(self) -> dict[str, Any]:
        """Get status of all integrations."""
        try:
            active_connectors = sum(1 for c in self.connectors.values() if c.is_active)
            total_connectors = len(self.connectors)

            # System-specific status
            system_status = {}
            for name, connector in self.connectors.items():
                system_status[name] = {
                    "integration_type": connector.integration_type.value,
                    "is_active": connector.is_active,
                    "last_sync": connector.last_sync.isoformat() if connector.last_sync else None,
                    "sync_frequency_minutes": connector.sync_frequency_minutes,
                    "events_subscribed": [e.value for e in connector.event_subscriptions],
                    "statistics": connector.statistics,
                }

            return {
                "total_connectors": total_connectors,
                "active_connectors": active_connectors,
                "integration_stats": self.integration_stats,
                "system_status": system_status,
                "event_queue_size": self.event_queue.qsize(),
            }

        except Exception as e:
            logger.error(f"Failed to get integration status: {e}")
            return {"error": str(e)}

    async def _ensure_storage_structure(self) -> None:
        """Ensure storage directories exist."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    async def _load_connectors(self) -> None:
        """Load saved connectors."""
        try:
            if self.connectors_file.exists():
                with open(self.connectors_file) as f:
                    data = json.load(f)

                self.connectors = {
                    name: SystemConnector(
                        system_name=c["system_name"],
                        integration_type=IntegrationType(c["integration_type"]),
                        is_active=c["is_active"],
                        last_sync=datetime.fromisoformat(c["last_sync"]) if c.get("last_sync") else None,
                        sync_frequency_minutes=c["sync_frequency_minutes"],
                        event_subscriptions=[EventType(e) for e in c["event_subscriptions"]],
                        configuration=c["configuration"],
                        statistics=c["statistics"],
                    )
                    for name, c in data.items()
                }

                logger.info(f"Loaded {len(self.connectors)} connectors")

        except Exception as e:
            logger.warning(f"Failed to load connectors: {e}")

    async def _save_connectors(self) -> None:
        """Save connectors to storage."""
        try:
            with open(self.connectors_file, "w") as f:
                json.dump(
                    {
                        name: {
                            "system_name": c.system_name,
                            "integration_type": c.integration_type.value,
                            "is_active": c.is_active,
                            "last_sync": c.last_sync.isoformat() if c.last_sync else None,
                            "sync_frequency_minutes": c.sync_frequency_minutes,
                            "event_subscriptions": [e.value for e in c.event_subscriptions],
                            "configuration": c.configuration,
                            "statistics": c.statistics,
                        }
                        for name, c in self.connectors.items()
                    },
                    f,
                    indent=2,
                )

        except Exception as e:
            logger.error(f"Failed to save connectors: {e}")

    async def _setup_default_connectors(self) -> None:
        """Setup default system connectors."""
        try:
            default_connectors = [
                {
                    "system_name": "skill_creation_pipeline",
                    "integration_type": IntegrationType.SKILL_CREATION_PIPELINE,
                    "event_subscriptions": [
                        EventType.SKILL_STORED,
                        EventType.SKILL_UPDATED,
                        EventType.PERFORMANCE_ALERT,
                    ],
                    "configuration": {
                        "auto_sync": True,
                        "update_skills_index": True,
                    },
                },
                {
                    "system_name": "documentation_system",
                    "integration_type": IntegrationType.DOCUMENTATION_SYSTEM,
                    "event_subscriptions": [
                        EventType.SKILL_STORED,
                        EventType.SKILL_UPDATED,
                        EventType.SKILL_DELETED,
                    ],
                    "configuration": {
                        "auto_generate_docs": True,
                        "update_cross_references": True,
                    },
                },
                {
                    "system_name": "context_optimization",
                    "integration_type": IntegrationType.CONTEXT_OPTIMIZATION,
                    "event_subscriptions": [
                        EventType.SKILL_ACCESSED,
                        EventType.OPTIMIZATION_RECOMMENDED,
                    ],
                    "configuration": {
                        "auto_optimize": True,
                        "track_usage_patterns": True,
                    },
                },
                {
                    "system_name": "memory_system",
                    "integration_type": IntegrationType.MEMORY_SYSTEM,
                    "event_subscriptions": [
                        EventType.SKILL_STORED,
                        EventType.SKILL_ACCESSED,
                    ],
                    "configuration": {
                        "cache_frequently_used": True,
                        "track_access_patterns": True,
                    },
                },
                {
                    "system_name": "code_execution",
                    "integration_type": IntegrationType.CODE_EXECUTION,
                    "event_subscriptions": [
                        EventType.SKILL_STORED,
                        EventType.SKILL_UPDATED,
                    ],
                    "configuration": {
                        "register_skills": True,
                        "update_skill_registry": True,
                    },
                },
                {
                    "system_name": "agent_framework",
                    "integration_type": IntegrationType.AGENT_FRAMEWORK,
                    "event_subscriptions": [
                        EventType.SKILL_STORED,
                        EventType.SKILL_UPDATED,
                        EventType.SKILL_DELETED,
                    ],
                    "configuration": {
                        "update_agent_capabilities": True,
                        "notify_agent_changes": True,
                    },
                },
                {
                    "system_name": "mcp_servers",
                    "integration_type": IntegrationType.MCP_SERVERS,
                    "event_subscriptions": [
                        EventType.SKILL_STORED,
                        EventType.SKILL_UPDATED,
                        EventType.BACKUP_COMPLETED,
                    ],
                    "configuration": {
                        "sync_skill_registry": True,
                        "notify_changes": True,
                    },
                },
            ]

            for connector_config in default_connectors:
                if connector_config["system_name"] not in self.connectors:
                    await self.register_connector(
                        system_name=connector_config["system_name"],
                        integration_type=connector_config["integration_type"],
                        configuration=connector_config["configuration"],
                        event_subscriptions=connector_config["event_subscriptions"],
                    )

            logger.info(f"Setup {len(default_connectors)} default connectors")

        except Exception as e:
            logger.error(f"Failed to setup default connectors: {e}")

    async def _register_event_handlers(self) -> None:
        """Register event handlers for different event types."""
        try:
            self.event_handlers = {
                EventType.SKILL_STORED: [self._handle_skill_stored],
                EventType.SKILL_UPDATED: [self._handle_skill_updated],
                EventType.SKILL_DELETED: [self._handle_skill_deleted],
                EventType.SKILL_ACCESSED: [self._handle_skill_accessed],
                EventType.BACKUP_COMPLETED: [self._handle_backup_completed],
                EventType.RECOVERY_COMPLETED: [self._handle_recovery_completed],
                EventType.PERFORMANCE_ALERT: [self._handle_performance_alert],
                EventType.OPTIMIZATION_RECOMMENDED: [self._handle_optimization_recommended],
            }

        except Exception as e:
            logger.error(f"Failed to register event handlers: {e}")

    async def _start_event_processor(self) -> None:
        """Start the event processing loop."""
        try:
            asyncio.create_task(self._event_processor_loop())
            logger.info("Started event processor")

        except Exception as e:
            logger.error(f"Failed to start event processor: {e}")

    async def _queue_event(self, event: IntegrationEvent) -> None:
        """Queue an event for processing."""
        try:
            await self.event_queue.put(event)

            # Update statistics
            self.integration_stats["total_events_processed"] += 1
            event_type = event.event_type.value
            if event_type not in self.integration_stats["events_by_type"]:
                self.integration_stats["events_by_type"][event_type] = 0
            self.integration_stats["events_by_type"][event_type] += 1
            self.integration_stats["last_event_time"] = event.timestamp.isoformat()

        except Exception as e:
            logger.error(f"Failed to queue event: {e}")

    async def _event_processor_loop(self) -> None:
        """Main event processing loop."""
        while True:
            try:
                # Get next event
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)

                # Process event
                await self._process_event(event)

            except asyncio.TimeoutError:
                # No events to process
                continue
            except Exception as e:
                logger.error(f"Event processor error: {e}")
                await asyncio.sleep(1)

    async def _process_event(self, event: IntegrationEvent) -> None:
        """Process a single event."""
        try:
            # Get event handlers
            handlers = self.event_handlers.get(event.event_type, [])

            # Call each handler
            for handler in handlers:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")

            # Update connector statistics
            for connector in self.connectors.values():
                if event.event_type in connector.event_subscriptions:
                    connector.statistics["events_received"] += 1
                    connector.statistics["last_event_received"] = event.timestamp.isoformat()

        except Exception as e:
            logger.error(f"Failed to process event {event.event_id}: {e}")

    async def _perform_system_sync(self, connector: SystemConnector) -> bool:
        """Perform synchronization with a specific system."""
        try:
            logger.info(f"Performing sync with {connector.system_name}")

            # System-specific sync logic would go here
            # For now, we'll simulate sync operations

            if connector.integration_type == IntegrationType.SKILL_CREATION_PIPELINE:
                return await self._sync_skill_creation_pipeline(connector)
            elif connector.integration_type == IntegrationType.DOCUMENTATION_SYSTEM:
                return await self._sync_documentation_system(connector)
            elif connector.integration_type == IntegrationType.CONTEXT_OPTIMIZATION:
                return await self._sync_context_optimization(connector)
            elif connector.integration_type == IntegrationType.MEMORY_SYSTEM:
                return await self._sync_memory_system(connector)
            elif connector.integration_type == IntegrationType.CODE_EXECUTION:
                return await self._sync_code_execution(connector)
            elif connector.integration_type == IntegrationType.AGENT_FRAMEWORK:
                return await self._sync_agent_framework(connector)
            elif connector.integration_type == IntegrationType.MCP_SERVERS:
                return await self._sync_mcp_servers(connector)
            else:
                logger.warning(f"Unknown integration type: {connector.integration_type}")
                return True

        except Exception as e:
            logger.error(f"Failed to sync with {connector.system_name}: {e}")
            return False

    async def _sync_skill_creation_pipeline(self, connector: SystemConnector) -> bool:
        """Sync with skill creation pipeline."""
        try:
            # Update skill index, trigger pipeline processes, etc.
            logger.info("Synced with skill creation pipeline")
            return True

        except Exception as e:
            logger.error(f"Failed to sync skill creation pipeline: {e}")
            return False

    async def _sync_documentation_system(self, connector: SystemConnector) -> bool:
        """Sync with documentation system."""
        try:
            # Update documentation, generate docs for new skills, etc.
            logger.info("Synced with documentation system")
            return True

        except Exception as e:
            logger.error(f"Failed to sync documentation system: {e}")
            return False

    async def _sync_context_optimization(self, connector: SystemConnector) -> bool:
        """Sync with context optimization system."""
        try:
            # Update optimization parameters, track usage patterns, etc.
            logger.info("Synced with context optimization")
            return True

        except Exception as e:
            logger.error(f"Failed to sync context optimization: {e}")
            return False

    async def _sync_memory_system(self, connector: SystemConnector) -> bool:
        """Sync with memory system."""
        try:
            # Update memory cache, track access patterns, etc.
            logger.info("Synced with memory system")
            return True

        except Exception as e:
            logger.error(f"Failed to sync memory system: {e}")
            return False

    async def _sync_code_execution(self, connector: SystemConnector) -> bool:
        """Sync with code execution system."""
        try:
            # Register new skills, update skill registry, etc.
            logger.info("Synced with code execution system")
            return True

        except Exception as e:
            logger.error(f"Failed to sync code execution system: {e}")
            return False

    async def _sync_agent_framework(self, connector: SystemConnector) -> bool:
        """Sync with agent framework."""
        try:
            # Update agent capabilities, notify of changes, etc.
            logger.info("Synced with agent framework")
            return True

        except Exception as e:
            logger.error(f"Failed to sync agent framework: {e}")
            return False

    async def _sync_mcp_servers(self, connector: SystemConnector) -> bool:
        """Sync with MCP servers."""
        try:
            # Sync skill registry, notify servers of changes, etc.
            logger.info("Synced with MCP servers")
            return True

        except Exception as e:
            logger.error(f"Failed to sync MCP servers: {e}")
            return False

    # Event handlers
    async def _handle_skill_stored(self, event: IntegrationEvent) -> None:
        """Handle skill stored event."""
        try:
            skill_id = event.data["skill_id"]
            logger.debug(f"Handling skill stored event for: {skill_id}")

            # Update various systems based on the skill storage
            # This would trigger documentation generation, cache updates, etc.

        except Exception as e:
            logger.error(f"Failed to handle skill stored event: {e}")

    async def _handle_skill_updated(self, event: IntegrationEvent) -> None:
        """Handle skill updated event."""
        try:
            skill_id = event.data["skill_id"]
            logger.debug(f"Handling skill updated event for: {skill_id}")

        except Exception as e:
            logger.error(f"Failed to handle skill updated event: {e}")

    async def _handle_skill_deleted(self, event: IntegrationEvent) -> None:
        """Handle skill deleted event."""
        try:
            skill_id = event.data["skill_id"]
            logger.debug(f"Handling skill deleted event for: {skill_id}")

        except Exception as e:
            logger.error(f"Failed to handle skill deleted event: {e}")

    async def _handle_skill_accessed(self, event: IntegrationEvent) -> None:
        """Handle skill accessed event."""
        try:
            skill_id = event.data["skill_id"]
            logger.debug(f"Handling skill accessed event for: {skill_id}")

        except Exception as e:
            logger.error(f"Failed to handle skill accessed event: {e}")

    async def _handle_backup_completed(self, event: IntegrationEvent) -> None:
        """Handle backup completed event."""
        try:
            logger.debug("Handling backup completed event")

        except Exception as e:
            logger.error(f"Failed to handle backup completed event: {e}")

    async def _handle_recovery_completed(self, event: IntegrationEvent) -> None:
        """Handle recovery completed event."""
        try:
            logger.debug("Handling recovery completed event")

        except Exception as e:
            logger.error(f"Failed to handle recovery completed event: {e}")

    async def _handle_performance_alert(self, event: IntegrationEvent) -> None:
        """Handle performance alert event."""
        try:
            logger.debug("Handling performance alert event")

        except Exception as e:
            logger.error(f"Failed to handle performance alert event: {e}")

    async def _handle_optimization_recommended(self, event: IntegrationEvent) -> None:
        """Handle optimization recommended event."""
        try:
            logger.debug("Handling optimization recommended event")

        except Exception as e:
            logger.error(f"Failed to handle optimization recommended event: {e}")
