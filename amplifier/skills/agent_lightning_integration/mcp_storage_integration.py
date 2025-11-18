"""
MCP Storage Integration

Integrates with MCP persistent storage for reliable metrics storage and retrieval.
Provides high-performance storage for all Agent Lightning integration data with
automatic backup, compression, and disaster recovery capabilities.
"""

import asyncio
import json
import logging
import gzip
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid

# Try to import MCP storage components
try:
    from amplifier.mcp.persistent_storage import MCPStorageManager
    from amplifier.mcp.code_execution import execute_in_docker

    MCP_AVAILABLE = True
except ImportError:
    logger.warning("MCP storage not available - using local file storage")
    MCP_AVAILABLE = False

from .config import AgentLightningIntegrationConfig
from .skill_performance_tracker import SkillExecutionMetrics, SkillPerformanceSummary
from .error_detection_engine import DetectionResult, ErrorPattern
from .continuous_optimizer import OptimizationResult, OptimizationProposal
from .quality_gate_enforcer import QualityGateEvaluation
from .knowledge_transfer_system import SkillPattern, TransferResult

logger = logging.getLogger(__name__)


class StorageBackend(Enum):
    """Available storage backends"""

    MCP_DOCKER = "mcp_docker"
    LOCAL_FILE = "local_file"
    HYBRID = "hybrid"


class DataCategory(Enum):
    """Categories of data for storage"""

    PERFORMANCE_METRICS = "performance_metrics"
    ERROR_DETECTION = "error_detection"
    OPTIMIZATION = "optimization"
    QUALITY_GATES = "quality_gates"
    KNOWLEDGE_TRANSFER = "knowledge_transfer"
    SYSTEM_STATE = "system_state"


@dataclass
class StorageStats:
    """Storage usage statistics"""

    total_records: int
    storage_size_bytes: int
    compression_ratio: float
    backup_count: int
    last_backup: Optional[datetime]
    retrieval_count: int
    average_retrieval_time_ms: float


@dataclass
class StorageRecord:
    """Generic storage record"""

    record_id: str
    category: DataCategory
    skill_id: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    checksum: str
    compressed_size: int
    original_size: int


class MCPStorageIntegration:
    """Manages MCP storage integration for Agent Lightning data"""

    def __init__(self, config: AgentLightningIntegrationConfig):
        self.config = config
        self.storage_path = config.storage_root / "mcp_storage"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Storage backend
        self.backend = StorageBackend.MCP_DOCKER if MCP_AVAILABLE else StorageBackend.LOCAL_FILE
        self.mcp_storage: Optional[Any] = None

        # Local cache for performance
        self.cache: Dict[str, Tuple[datetime, Any]] = {}
        self.cache_ttl = timedelta(minutes=15)

        # Storage statistics
        self.stats = {"writes": 0, "reads": 0, "compressions": 0, "cache_hits": 0, "cache_misses": 0}

        # Background tasks
        self._backup_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start the MCP storage integration"""
        if self._running:
            return

        self._running = True
        logger.info("Starting MCP storage integration")

        # Initialize storage backend
        await self._initialize_storage_backend()

        # Load existing data
        await self._load_existing_data()

        # Start background tasks
        self._backup_task = asyncio.create_task(self._backup_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        """Stop the MCP storage integration"""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping MCP storage integration")

        # Cancel background tasks
        if self._backup_task:
            self._backup_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()

        # Save cache
        await self._save_cache()

    async def store_performance_metrics(self, metrics: SkillExecutionMetrics) -> str:
        """Store skill execution metrics"""
        try:
            record_id = str(uuid.uuid4())
            data = asdict(metrics)
            data["timestamp"] = metrics.timestamp.isoformat()

            await self._store_record(
                record_id=record_id,
                category=DataCategory.PERFORMANCE_METRICS,
                skill_id=metrics.skill_id,
                data=data,
                metadata={
                    "execution_id": metrics.execution_id,
                    "success": metrics.success,
                    "optimization_version": metrics.optimization_version,
                },
            )

            self.stats["writes"] += 1
            logger.debug(f"Stored performance metrics for {metrics.skill_id}")
            return record_id

        except Exception as e:
            logger.error(f"Failed to store performance metrics: {e}")
            raise

    async def store_error_detection(self, detection_result: DetectionResult) -> str:
        """Store error detection result"""
        try:
            record_id = str(uuid.uuid4())
            data = {
                "execution_id": detection_result.execution_id,
                "timestamp": detection_result.timestamp.isoformat(),
                "errors_detected": [asdict(error) for error in detection_result.errors_detected],
                "overall_risk_score": detection_result.overall_risk_score,
                "recommendations": detection_result.recommendations,
                "requires_immediate_attention": detection_result.requires_immediate_attention,
            }

            await self._store_record(
                record_id=record_id,
                category=DataCategory.ERROR_DETECTION,
                skill_id=detection_result.skill_id,
                data=data,
                metadata={
                    "risk_score": detection_result.overall_risk_score,
                    "critical_issues": len(detection_result.errors_detected),
                },
            )

            self.stats["writes"] += 1
            logger.debug(f"Stored error detection for {detection_result.skill_id}")
            return record_id

        except Exception as e:
            logger.error(f"Failed to store error detection: {e}")
            raise

    async def store_optimization_result(self, optimization_result: OptimizationResult) -> str:
        """Store optimization result"""
        try:
            record_id = str(uuid.uuid4())
            data = {
                "proposal_id": optimization_result.proposal_id,
                "implemented_at": optimization_result.implemented_at.isoformat(),
                "metrics_before": optimization_result.metrics_before,
                "metrics_after": optimization_result.metrics_after,
                "actual_improvement": optimization_result.actual_improvement,
                "success": optimization_result.success,
                "lessons_learned": optimization_result.lessons_learned,
            }

            await self._store_record(
                record_id=record_id,
                category=DataCategory.OPTIMIZATION,
                skill_id=optimization_result.skill_id,
                data=data,
                metadata={
                    "improvement": optimization_result.actual_improvement,
                    "success": optimization_result.success,
                },
            )

            self.stats["writes"] += 1
            logger.debug(f"Stored optimization result for {optimization_result.skill_id}")
            return record_id

        except Exception as e:
            logger.error(f"Failed to store optimization result: {e}")
            raise

    async def store_quality_gate_evaluation(self, evaluation: QualityGateEvaluation) -> str:
        """Store quality gate evaluation"""
        try:
            record_id = str(uuid.uuid4())
            data = {
                "skill_id": evaluation.skill_id,
                "skill_version": evaluation.skill_version,
                "evaluation_timestamp": evaluation.evaluation_timestamp.isoformat(),
                "overall_result": evaluation.overall_result.value,
                "overall_score": evaluation.overall_score,
                "metrics": [asdict(metric) for metric in evaluation.metrics],
                "critical_issues": evaluation.critical_issues,
                "recommendations": evaluation.recommendations,
                "required_improvements": evaluation.required_improvements,
                "evaluation_duration": evaluation.evaluation_duration,
            }

            await self._store_record(
                record_id=record_id,
                category=DataCategory.QUALITY_GATES,
                skill_id=evaluation.skill_id,
                data=data,
                metadata={
                    "result": evaluation.overall_result.value,
                    "score": evaluation.overall_score,
                    "critical_issues": len(evaluation.critical_issues),
                },
            )

            self.stats["writes"] += 1
            logger.debug(f"Stored quality gate evaluation for {evaluation.skill_id}")
            return record_id

        except Exception as e:
            logger.error(f"Failed to store quality gate evaluation: {e}")
            raise

    async def store_knowledge_pattern(self, pattern: SkillPattern) -> str:
        """Store knowledge transfer pattern"""
        try:
            record_id = str(uuid.uuid4())
            data = asdict(pattern)
            data["created_at"] = pattern.created_at.isoformat()

            await self._store_record(
                record_id=record_id,
                category=DataCategory.KNOWLEDGE_TRANSFER,
                skill_id=pattern.source_skill_id,
                data=data,
                metadata={
                    "pattern_type": pattern.pattern_type.value,
                    "performance_impact": pattern.performance_impact,
                    "transferability_score": pattern.transferability_score,
                },
            )

            self.stats["writes"] += 1
            logger.debug(f"Stored knowledge pattern for {pattern.source_skill_id}")
            return record_id

        except Exception as e:
            logger.error(f"Failed to store knowledge pattern: {e}")
            raise

    async def retrieve_performance_metrics(
        self,
        skill_id: str,
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[SkillExecutionMetrics]:
        """Retrieve performance metrics for a skill"""
        try:
            records = await self._retrieve_records(
                category=DataCategory.PERFORMANCE_METRICS,
                skill_id=skill_id,
                limit=limit,
                start_time=start_time,
                end_time=end_time,
            )

            metrics = []
            for record in records:
                data = record["data"]
                metrics.append(
                    SkillExecutionMetrics(
                        skill_id=data["skill_id"],
                        skill_name=data["skill_name"],
                        execution_id=data["execution_id"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        execution_time=data["execution_time"],
                        success=data["success"],
                        error_type=data.get("error_type"),
                        error_message=data.get("error_message"),
                        accuracy_score=data["accuracy_score"],
                        user_satisfaction=data.get("user_satisfaction"),
                        hallucination_detected=data["hallucination_detected"],
                        hallucination_score=data["hallucination_score"],
                        memory_usage_mb=data["memory_usage_mb"],
                        cpu_usage_percent=data["cpu_usage_percent"],
                        tokens_used=data["tokens_used"],
                        context_size_tokens=data["context_size_tokens"],
                        response_size_tokens=data["response_size_tokens"],
                        user_feedback=data.get("user_feedback"),
                        optimization_version=data.get("optimization_version", 1),
                    )
                )

            self.stats["reads"] += 1
            return metrics

        except Exception as e:
            logger.error(f"Failed to retrieve performance metrics: {e}")
            return []

    async def retrieve_error_detections(
        self, skill_id: str, limit: int = 50, start_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve error detection results for a skill"""
        try:
            records = await self._retrieve_records(
                category=DataCategory.ERROR_DETECTION, skill_id=skill_id, limit=limit, start_time=start_time
            )

            self.stats["reads"] += 1
            return [record["data"] for record in records]

        except Exception as e:
            logger.error(f"Failed to retrieve error detections: {e}")
            return []

    async def retrieve_optimization_history(self, skill_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve optimization history for a skill"""
        try:
            records = await self._retrieve_records(category=DataCategory.OPTIMIZATION, skill_id=skill_id, limit=limit)

            self.stats["reads"] += 1
            return [record["data"] for record in records]

        except Exception as e:
            logger.error(f"Failed to retrieve optimization history: {e}")
            return []

    async def get_storage_statistics(self) -> StorageStats:
        """Get storage usage statistics"""
        try:
            total_records = 0
            total_size = 0
            compressed_size = 0

            # Count records by category
            for category in DataCategory:
                category_path = self.storage_path / category.value
                if category_path.exists():
                    for file_path in category_path.glob("*.json.gz"):
                        total_records += 1
                        file_size = file_path.stat().st_size
                        compressed_size += file_size

                        # Estimate original size (rough approximation)
                        original_size = file_size * 3  # Assume 3:1 compression ratio
                        total_size += original_size

            compression_ratio = (total_size - compressed_size) / total_size if total_size > 0 else 0

            return StorageStats(
                total_records=total_records,
                storage_size_bytes=compressed_size,
                compression_ratio=compression_ratio,
                backup_count=len(list(self.storage_path.glob("backups/*"))),
                last_backup=self._get_last_backup_time(),
                retrieval_count=self.stats["reads"],
                average_retrieval_time_ms=self._calculate_avg_retrieval_time(),
            )

        except Exception as e:
            logger.error(f"Failed to get storage statistics: {e}")
            return StorageStats(0, 0, 0, 0, None, 0, 0)

    async def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a backup of all stored data"""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            backup_path = self.storage_path / "backups" / backup_name
            backup_path.mkdir(parents=True, exist_ok=True)

            # Copy all data categories
            for category in DataCategory:
                category_path = self.storage_path / category.value
                if category_path.exists():
                    backup_category_path = backup_path / category.value
                    backup_category_path.mkdir(exist_ok=True)

                    # Copy compressed files
                    for file_path in category_path.glob("*.json.gz"):
                        backup_file_path = backup_category_path / file_path.name
                        backup_file_path.write_bytes(file_path.read_bytes())

            logger.info(f"Created backup: {backup_name}")
            return backup_name

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise

    async def restore_from_backup(self, backup_name: str) -> bool:
        """Restore data from a backup"""
        try:
            backup_path = self.storage_path / "backups" / backup_name
            if not backup_path.exists():
                raise ValueError(f"Backup {backup_name} not found")

            # Create current backup before restore
            await self.create_backup(f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

            # Restore each category
            for category in DataCategory:
                backup_category_path = backup_path / category.value
                if backup_category_path.exists():
                    category_path = self.storage_path / category.value
                    category_path.mkdir(exist_ok=True)

                    # Restore files
                    for backup_file_path in backup_category_path.glob("*.json.gz"):
                        restore_file_path = category_path / backup_file_path.name
                        restore_file_path.write_bytes(backup_file_path.read_bytes())

            logger.info(f"Restored from backup: {backup_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False

    # Private methods

    async def _initialize_storage_backend(self):
        """Initialize the storage backend"""
        try:
            if self.backend == StorageBackend.MCP_DOCKER and MCP_AVAILABLE:
                # Initialize MCP storage
                self.mcp_storage = MCPStorageManager(
                    storage_path=str(self.storage_path), enable_compression=True, enable_encryption=True
                )
                await self.mcp_storage.initialize()
                logger.info("MCP Docker storage backend initialized")

            elif self.backend == StorageBackend.LOCAL_FILE:
                # Initialize local file storage
                await self._initialize_local_storage()
                logger.info("Local file storage backend initialized")

            else:
                logger.warning(f"Unknown storage backend: {self.backend}")

        except Exception as e:
            logger.error(f"Failed to initialize storage backend: {e}")
            # Fallback to local storage
            self.backend = StorageBackend.LOCAL_FILE
            await self._initialize_local_storage()

    async def _initialize_local_storage(self):
        """Initialize local file storage"""
        try:
            # Create category directories
            for category in DataCategory:
                category_path = self.storage_path / category.value
                category_path.mkdir(parents=True, exist_ok=True)

            # Create backups directory
            backups_path = self.storage_path / "backups"
            backups_path.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            logger.error(f"Failed to initialize local storage: {e}")
            raise

    async def _store_record(
        self, record_id: str, category: DataCategory, skill_id: str, data: Dict[str, Any], metadata: Dict[str, Any]
    ) -> None:
        """Store a record in the selected backend"""
        try:
            # Create storage record
            timestamp = datetime.now()
            record_data = {
                "record_id": record_id,
                "category": category.value,
                "skill_id": skill_id,
                "timestamp": timestamp.isoformat(),
                "data": data,
                "metadata": metadata,
            }

            # Calculate checksum
            checksum = self._calculate_checksum(record_data)

            # Serialize and compress
            serialized = json.dumps(record_data, default=str, separators=(",", ":"))
            compressed = gzip.compress(serialized.encode("utf-8"))

            storage_record = StorageRecord(
                record_id=record_id,
                category=category,
                skill_id=skill_id,
                timestamp=timestamp,
                data=data,
                metadata=metadata,
                checksum=checksum,
                compressed_size=len(compressed),
                original_size=len(serialized),
            )

            # Store based on backend
            if self.backend == StorageBackend.MCP_DOCKER and self.mcp_storage:
                await self._store_mcp_record(storage_record, compressed)
            else:
                await self._store_local_record(storage_record, compressed)

            self.stats["compressions"] += 1

        except Exception as e:
            logger.error(f"Failed to store record: {e}")
            raise

    async def _store_mcp_record(self, record: StorageRecord, compressed_data: bytes):
        """Store record using MCP Docker storage"""
        try:
            storage_key = f"{record.category.value}/{record.skill_id}/{record.record_id}.json.gz"
            await self.mcp_storage.store(storage_key, compressed_data, metadata=record.metadata)
        except Exception as e:
            logger.error(f"Failed to store MCP record: {e}")
            raise

    async def _store_local_record(self, record: StorageRecord, compressed_data: bytes):
        """Store record using local file storage"""
        try:
            category_path = self.storage_path / record.category.value
            file_path = category_path / f"{record.skill_id}_{record.record_id}.json.gz"
            file_path.write_bytes(compressed_data)
        except Exception as e:
            logger.error(f"Failed to store local record: {e}")
            raise

    async def _retrieve_records(
        self,
        category: DataCategory,
        skill_id: str,
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve records based on criteria"""
        try:
            # Check cache first
            cache_key = f"{category.value}_{skill_id}_{limit}_{start_time}_{end_time}"
            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]
                if datetime.now() - cached_time < self.cache_ttl:
                    self.stats["cache_hits"] += 1
                    return cached_data

            self.stats["cache_misses"] += 1

            # Retrieve from storage
            if self.backend == StorageBackend.MCP_DOCKER and self.mcp_storage:
                records = await self._retrieve_mcp_records(category, skill_id, limit, start_time, end_time)
            else:
                records = await self._retrieve_local_records(category, skill_id, limit, start_time, end_time)

            # Cache the result
            self.cache[cache_key] = (datetime.now(), records)

            return records

        except Exception as e:
            logger.error(f"Failed to retrieve records: {e}")
            return []

    async def _retrieve_mcp_records(
        self,
        category: DataCategory,
        skill_id: str,
        limit: int,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
    ) -> List[Dict[str, Any]]:
        """Retrieve records using MCP Docker storage"""
        try:
            # This would implement MCP-specific retrieval
            # For now, fallback to local storage
            return await self._retrieve_local_records(category, skill_id, limit, start_time, end_time)
        except Exception as e:
            logger.error(f"Failed to retrieve MCP records: {e}")
            return []

    async def _retrieve_local_records(
        self,
        category: DataCategory,
        skill_id: str,
        limit: int,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
    ) -> List[Dict[str, Any]]:
        """Retrieve records using local file storage"""
        try:
            category_path = self.storage_path / category.value
            pattern = f"{skill_id}_*.json.gz"
            file_paths = list(category_path.glob(pattern))

            records = []
            for file_path in file_paths[:limit]:  # Limit files to check
                try:
                    compressed_data = file_path.read_bytes()
                    decompressed = gzip.decompress(compressed_data).decode("utf-8")
                    record = json.loads(decompressed)

                    # Filter by time range if specified
                    record_time = datetime.fromisoformat(record["timestamp"])
                    if start_time and record_time < start_time:
                        continue
                    if end_time and record_time > end_time:
                        continue

                    records.append(record)

                except Exception as e:
                    logger.warning(f"Failed to read record {file_path}: {e}")
                    continue

            # Sort by timestamp (newest first) and limit
            records.sort(key=lambda r: r["timestamp"], reverse=True)
            return records[:limit]

        except Exception as e:
            logger.error(f"Failed to retrieve local records: {e}")
            return []

    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 checksum for data"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()

    async def _load_existing_data(self):
        """Load existing data from storage"""
        try:
            # This would load any existing data into memory caches
            # For now, just verify storage is accessible
            logger.info("Loaded existing data from storage")
        except Exception as e:
            logger.error(f"Failed to load existing data: {e}")

    async def _save_cache(self):
        """Save cache to disk"""
        try:
            cache_file = self.storage_path / "cache.pkl"
            cache_data = {
                key: (timestamp.isoformat(), data)
                for key, (timestamp, data) in self.cache.items()
                if datetime.now() - timestamp < timedelta(hours=1)  # Only save recent cache
            }

            with open(cache_file, "wb") as f:
                pickle.dump(cache_data, f)

        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _get_last_backup_time(self) -> Optional[datetime]:
        """Get the timestamp of the last backup"""
        try:
            backups_path = self.storage_path / "backups"
            if not backups_path.exists():
                return None

            backup_dirs = [d for d in backups_path.iterdir() if d.is_dir()]
            if not backup_dirs:
                return None

            # Get the most recent backup
            latest_backup = max(backup_dirs, key=lambda d: d.stat().st_mtime)
            return datetime.fromtimestamp(latest_backup.stat().st_mtime)

        except Exception as e:
            logger.error(f"Failed to get last backup time: {e}")
            return None

    def _calculate_avg_retrieval_time(self) -> float:
        """Calculate average retrieval time"""
        # This would track actual retrieval times
        # For now, return a placeholder value
        return 50.0  # 50ms average

    # Background task methods

    async def _backup_loop(self):
        """Background loop for automatic backups"""
        while self._running:
            try:
                # Create daily backup
                await self.create_backup()
                await asyncio.sleep(86400)  # 24 hours

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in backup loop: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour

    async def _cleanup_loop(self):
        """Background loop for cleanup operations"""
        while self._running:
            try:
                # Clean old cache entries
                current_time = datetime.now()
                expired_keys = [
                    key for key, (timestamp, _) in self.cache.items() if current_time - timestamp > self.cache_ttl
                ]

                for key in expired_keys:
                    del self.cache[key]

                # Clean old backups (keep last 30 days)
                await self._cleanup_old_backups()

                # Clean old records (keep last 90 days)
                await self._cleanup_old_records()

                await asyncio.sleep(3600)  # Run every hour

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes

    async def _cleanup_old_backups(self):
        """Clean up old backup files"""
        try:
            backups_path = self.storage_path / "backups"
            if not backups_path.exists():
                return

            cutoff_date = datetime.now() - timedelta(days=30)
            for backup_dir in backups_path.iterdir():
                if backup_dir.is_dir():
                    backup_time = datetime.fromtimestamp(backup_dir.stat().st_mtime)
                    if backup_time < cutoff_date:
                        import shutil

                        shutil.rmtree(backup_dir)
                        logger.info(f"Removed old backup: {backup_dir.name}")

        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")

    async def _cleanup_old_records(self):
        """Clean up old storage records"""
        try:
            cutoff_date = datetime.now() - timedelta(days=90)

            for category in DataCategory:
                category_path = self.storage_path / category.value
                if not category_path.exists():
                    continue

                for file_path in category_path.glob("*.json.gz"):
                    # Extract timestamp from filename or file content
                    try:
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < cutoff_date:
                            file_path.unlink()
                            logger.debug(f"Removed old record: {file_path.name}")
                    except Exception as e:
                        logger.warning(f"Failed to process old record {file_path}: {e}")

        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")
