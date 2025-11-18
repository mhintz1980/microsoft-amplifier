"""
Advanced Context System Integration

Integrates the advanced context compression, management, and retrieval systems
with existing amplifier infrastructure for seamless operation.

Key Features:
- Seamless integration with existing amplifier modules
- Configuration management and optimization
- Health monitoring and diagnostics
- Performance metrics collection
- Backward compatibility with existing context systems
"""

import asyncio
import json
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import Any

from .context_compactor import get_context_compactor
from .context_engine import ContextStrategy
from .context_engine import get_context_engine
from .context_engine import initialize_context_engine
from .context_engine import shutdown_context_engine
from .context_retrieval import get_context_retriever
from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class SystemConfiguration:
    """Configuration for the advanced context system."""

    # Compression settings
    enable_clustering: bool = True
    enable_semantic_analysis: bool = True
    compression_cache_size: int = 1000

    # Engine settings
    max_working_memory: int = 50000
    consolidation_threshold: int = 100
    default_strategy: str = "progressive"

    # Retrieval settings
    enable_semantic_search: bool = True
    semantic_threshold: float = 0.5
    max_retrieval_results: int = 10

    # Performance settings
    enable_background_tasks: bool = True
    performance_monitoring: bool = True
    auto_optimization: bool = True

    # Integration settings
    legacy_compatibility_mode: bool = False
    external_system_sync: bool = True


@dataclass
class SystemHealth:
    """Health status of the advanced context system."""

    status: str = "healthy"  # healthy, degraded, unhealthy
    timestamp: datetime = field(default_factory=datetime.now)
    components: dict[str, bool] = field(default_factory=dict)
    performance_metrics: dict[str, float] = field(default_factory=dict)
    active_operations: int = 0
    error_count: int = 0
    last_error: str | None = None
    uptime_seconds: float = 0.0


class ContextSystemManager:
    """Main manager for the advanced context system."""

    def __init__(self, config: SystemConfiguration | None = None):
        self.config = config or SystemConfiguration()
        self.start_time = datetime.now()
        self.is_initialized = False

        # System components
        self.compactor = None
        self.engine = None
        self.retriever = None

        # Health monitoring
        self.health = SystemHealth()
        self.operation_count = 0

        # Performance tracking
        self.performance_history = []

    async def initialize(self) -> bool:
        """Initialize the advanced context system."""
        try:
            logger.info("Initializing advanced context system...")

            # Initialize compactor
            self.compactor = get_context_compactor()

            # Initialize engine
            if self.config.enable_background_tasks:
                self.engine = await initialize_context_engine()
            else:
                self.engine = get_context_engine()

            # Initialize retriever
            self.retriever = get_context_retriever()

            # Configure components based on settings
            await self._configure_components()

            # Start health monitoring
            if self.config.performance_monitoring:
                asyncio.create_task(self._health_monitoring_loop())

            self.is_initialized = True
            self._update_health_component("initialization", True)

            logger.info("Advanced context system initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize context system: {e}")
            self._update_health_component("initialization", False, str(e))
            return False

    async def shutdown(self) -> None:
        """Shutdown the advanced context system."""
        logger.info("Shutting down advanced context system...")

        try:
            if self.engine:
                await shutdown_context_engine()

            # Save final statistics
            await self._save_system_stats()

            self.is_initialized = False
            logger.info("Advanced context system shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    async def _configure_components(self) -> None:
        """Configure system components based on configuration."""
        # Configure compactor
        if self.compactor and self.config.auto_optimization:
            self.compactor.optimize_performance()

        # Configure engine
        if self.engine:
            # Set working memory size
            self.engine.max_working_memory = self.config.max_working_memory
            self.engine.consolidation_threshold = self.config.consolidation_threshold

            # Set default strategy
            try:
                self.engine.strategy = ContextStrategy(self.config.default_strategy)
            except ValueError:
                logger.warning(f"Invalid strategy: {self.config.default_strategy}, using default")

    async def process_context_request(self, request_data: dict[str, Any]) -> dict[str, Any]:
        """Process a context request with full system integration."""
        self.operation_count += 1

        if not self.is_initialized:
            raise RuntimeError("Context system not initialized")

        try:
            # Extract request parameters
            query = request_data.get("query", "")
            max_tokens = request_data.get("max_tokens", 10000)
            strategy = request_data.get("strategy", self.config.default_strategy)
            topics = request_data.get("topics", [])
            priority = request_data.get("priority", 1)

            # Create engine request
            from .context_engine import ContextRequest

            engine_request = ContextRequest(
                request_id=f"req_{self.operation_count}_{int(asyncio.get_event_loop().time())}",
                query=query,
                max_tokens=max_tokens,
                strategy=ContextStrategy(strategy),
                topics=topics,
                priority=priority,
            )

            # Process through engine
            start_time = asyncio.get_event_loop().time()
            response = await self.engine.get_context(engine_request)  # type: ignore[assignment]
            processing_time = asyncio.get_event_loop().time() - start_time

            # Create integrated response
            result = {
                "success": True,
                "content": response.content,
                "tokens_used": response.tokens_used,
                "chunks_included": response.chunks_included,
                "compression_level": response.compression_level.value,
                "processing_time": processing_time,
                "metadata": {
                    "system_version": "2.0",
                    "components_used": ["engine", "compactor"],
                    "optimization_applied": self.config.auto_optimization,
                    **response.metadata,
                },
            }

            # Update performance tracking
            self._update_performance_metrics(
                {
                    "processing_time": processing_time,
                    "tokens_processed": response.tokens_used,
                    "chunks_included": response.chunks_included,
                    "compression_ratio": response.metadata.get("compression_ratio", 1.0),
                }
            )

            return result

        except Exception as e:
            self.health.error_count += 1
            self.health.last_error = str(e)
            logger.error(f"Error processing context request: {e}")

            return {"success": False, "error": str(e), "processing_time": 0, "metadata": {"system_version": "2.0"}}

    async def search_context(self, query_data: dict[str, Any]) -> dict[str, Any]:
        """Perform semantic context search."""
        if not self.retriever:
            return {"success": False, "error": "Retriever not available"}

        try:
            from .context_retrieval import RetrievalMode
            from .context_retrieval import RetrievalQuery

            query = RetrievalQuery(
                query_id=f"search_{self.operation_count}_{int(asyncio.get_event_loop().time())}",
                query_text=query_data.get("query", ""),
                retrieval_mode=RetrievalMode(query_data.get("mode", "semantic")),
                max_results=query_data.get("max_results", self.config.max_retrieval_results),
                similarity_threshold=query_data.get("threshold", self.config.semantic_threshold),
                context_types=query_data.get("context_types", []),
            )

            result = await self.retriever.retrieve_context(query)

            return {
                "success": True,
                "matched_chunks": len(result.matched_chunks),
                "similarity_scores": result.similarity_scores,
                "reconstruction_level": result.reconstruction_level.value,
                "retrieval_time": result.retrieval_time,
                "metadata": result.metadata,
            }

        except Exception as e:
            logger.error(f"Error in context search: {e}")
            return {"success": False, "error": str(e)}

    async def reconstruct_context(self, reconstruction_data: dict[str, Any]) -> dict[str, Any]:
        """Reconstruct detailed context from compressed version."""
        if not self.retriever:
            return {"success": False, "error": "Retriever not available"}

        try:
            from .context_compactor import CompactContext
            from .context_compactor import ContextLevel
            from .context_retrieval import ReconstructionLevel
            from .context_retrieval import ReconstructionRequest

            # Reconstruct CompactContext from data
            compact_data = reconstruction_data.get("compact_context")
            compact_context = CompactContext(
                original_tokens=compact_data["original_tokens"],
                compressed_tokens=compact_data["compressed_tokens"],
                compression_ratio=compact_data["compression_ratio"],
                level=ContextLevel(compact_data["level"]),
                content=compact_data["content"],
                metadata=compact_data.get("metadata", {}),  # type: ignore[assignment]
                reconstruction_hints=compact_data.get("reconstruction_hints", []),  # type: ignore[assignment]
            )

            request = ReconstructionRequest(
                request_id=f"reconstruct_{self.operation_count}_{int(asyncio.get_event_loop().time())}",
                compact_context=compact_context,
                target_level=ReconstructionLevel(reconstruction_data.get("target_level", "detailed")),
                expansion_queries=reconstruction_data.get("expansion_queries", []),
                focus_areas=reconstruction_data.get("focus_areas", []),
            )

            result = await self.retriever.reconstruct_context(request)

            return {
                "success": True,
                "reconstructed_content": result.reconstructed_content,
                "original_level": result.original_level.value,
                "reconstructed_level": result.reconstructed_level.value,
                "expansion_ratio": result.expansion_ratio,
                "confidence_score": result.confidence_score,
                "reconstruction_time": result.reconstruction_time,
            }

        except Exception as e:
            logger.error(f"Error in context reconstruction: {e}")
            return {"success": False, "error": str(e)}

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status."""
        if not self.is_initialized:
            return {"status": "not_initialized", "message": "System not initialized"}

        # Update health
        self._update_health()

        # Collect component statistics
        stats = {
            "health": {
                "status": self.health.status,
                "uptime_seconds": self.health.uptime_seconds,
                "operations_processed": self.operation_count,
                "error_count": self.health.error_count,
                "active_operations": self.health.active_operations,
                "components": self.health.components,
            },
            "performance": {
                "recent_metrics": self.performance_history[-10:] if self.performance_history else [],
                "average_processing_time": self._calculate_avg_processing_time(),
                "compression_efficiency": self._calculate_compression_efficiency(),
            },
            "components": {},
        }

        # Add component-specific stats
        if self.compactor:
            stats["components"]["compactor"] = self.compactor.get_compression_stats()

        if self.engine:
            stats["components"]["engine"] = self.engine.get_engine_stats()

        if self.retriever:
            stats["components"]["retriever"] = self.retriever.get_retrieval_stats()

        return stats

    def _update_health_component(self, component: str, status: bool, error: str | None = None) -> None:
        """Update health status for a component."""
        self.health.components[component] = status
        if not status and error:
            self.health.last_error = error
            self.health.error_count += 1

        # Update overall health
        failed_components = sum(1 for status in self.health.components.values() if not status)
        total_components = len(self.health.components)

        if total_components == 0:
            self.health.status = "unknown"
        elif failed_components == 0:
            self.health.status = "healthy"
        elif failed_components < total_components / 2:
            self.health.status = "degraded"
        else:
            self.health.status = "unhealthy"

    def _update_health(self) -> None:
        """Update overall system health."""
        self.health.timestamp = datetime.now()
        self.health.uptime_seconds = (datetime.now() - self.start_time).total_seconds()

        # Update component health
        self._update_health_component("compactor", self.compactor is not None)
        self._update_health_component("engine", self.engine is not None)
        self._update_health_component("retriever", self.retriever is not None)

    def _update_performance_metrics(self, metrics: dict[str, float]) -> None:
        """Update performance metrics tracking."""
        # type: ignore[arg-type]
        # type: ignore[arg-type]
        metrics["timestamp"] = datetime.now().isoformat()  # type: ignore[arg-type]
        self.performance_history.append(metrics)

        # Keep only recent history (last 100 operations)
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]

    def _calculate_avg_processing_time(self) -> float:
        """Calculate average processing time from recent operations."""
        if not self.performance_history:
            return 0.0

        processing_times = [m.get("processing_time", 0) for m in self.performance_history[-20:]]
        return sum(processing_times) / len(processing_times)

    def _calculate_compression_efficiency(self) -> float:
        """Calculate average compression efficiency."""
        if not self.compactor:
            return 0.0

        stats = self.compactor.get_compression_stats()
        if "advanced_analytics" not in stats:
            return 0.0

        return stats["advanced_analytics"].get("compression_efficiency", 0.0)

    async def _health_monitoring_loop(self) -> None:
        """Background health monitoring loop."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                self._update_health()

                # Auto-optimize if enabled
                if self.config.auto_optimization and self.compactor:
                    optimization_result = self.compactor.optimize_performance()
                    if optimization_result["optimizations_applied"]:
                        logger.info(f"Auto-optimization applied: {optimization_result['optimizations_applied']}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")

    async def _save_system_stats(self) -> None:
        """Save system statistics to file."""
        try:
            stats = {
                "system_info": {
                    "version": "2.0",
                    "shutdown_time": datetime.now().isoformat(),
                    "total_operations": self.operation_count,
                    "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                },
                "configuration": {
                    "clustering_enabled": self.config.enable_clustering,
                    "semantic_analysis_enabled": self.config.enable_semantic_analysis,
                    "background_tasks_enabled": self.config.enable_background_tasks,
                },
                "performance_history": self.performance_history,
                "final_health": self.health.__dict__,
            }

            # Save to current directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stats_file = Path(f"context_system_stats_{timestamp}.json")

            with open(stats_file, "w") as f:
                json.dump(stats, f, indent=2, default=str)

            logger.info(f"System statistics saved to {stats_file}")

        except Exception as e:
            logger.error(f"Error saving system stats: {e}")


# Global system manager instance
_system_manager: ContextSystemManager | None = None


async def initialize_advanced_context_system(config: SystemConfiguration | None = None) -> ContextSystemManager:
    """Initialize the global advanced context system."""
    global _system_manager
    if _system_manager is None:
        _system_manager = ContextSystemManager(config)
    await _system_manager.initialize()
    return _system_manager


def get_context_system_manager() -> ContextSystemManager:
    """Get the global context system manager."""
    global _system_manager
    if _system_manager is None:
        _system_manager = ContextSystemManager()
    return _system_manager


async def shutdown_advanced_context_system() -> None:
    """Shutdown the global advanced context system."""
    global _system_manager
    if _system_manager:
        await _system_manager.shutdown()
        _system_manager = None


# Convenience functions for external integration
async def process_context(request_data: dict[str, Any]) -> dict[str, Any]:
    """Convenience function for context processing."""
    manager = get_context_system_manager()
    return await manager.process_context_request(request_data)


async def search_context(query_data: dict[str, Any]) -> dict[str, Any]:
    """Convenience function for context search."""
    manager = get_context_system_manager()
    return await manager.search_context(query_data)


async def reconstruct_context(reconstruction_data: dict[str, Any]) -> dict[str, Any]:
    """Convenience function for context reconstruction."""
    manager = get_context_system_manager()
    return await manager.reconstruct_context(reconstruction_data)


def get_system_status() -> dict[str, Any]:
    """Convenience function for system status."""
    manager = get_context_system_manager()
    return manager.get_system_status()
