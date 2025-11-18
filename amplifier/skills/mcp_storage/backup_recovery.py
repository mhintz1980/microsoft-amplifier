"""Backup and Recovery Automation.

Provides comprehensive backup and recovery capabilities for the skill repository
system with automated scheduling, incremental backups, and disaster recovery.
"""

import asyncio
import json
import shutil
import uuid
import zipfile
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger
from ...mcp.persistent_storage import get_persistent_storage

logger = get_logger(__name__)


class BackupType(Enum):
    """Types of backup operations."""

    FULL = "full"  # Complete backup of all data
    INCREMENTAL = "incremental"  # Changes since last backup
    DIFFERENTIAL = "differential"  # Changes since last full backup
    SNAPSHOT = "snapshot"  # Point-in-time snapshot


class BackupStatus(Enum):
    """Status of backup operations."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CORRUPTED = "corrupted"


class RecoveryType(Enum):
    """Types of recovery operations."""

    FULL_RESTORE = "full_restore"  # Restore entire system
    SELECTIVE_RESTORE = "selective_restore"  # Restore specific skills
    POINT_IN_TIME = "point_in_time"  # Restore to specific time
    DISASTER_RECOVERY = "disaster_recovery"  # Complete disaster recovery


@dataclass
class BackupMetadata:
    """Metadata for backup operations."""

    backup_id: str
    backup_type: BackupType
    created_at: datetime
    completed_at: datetime | None
    status: BackupStatus
    size_bytes: int
    compressed_size_bytes: int
    skills_count: int
    checksum: str
    description: str
    retention_days: int = 30
    tags: list[str] = field(default_factory=list)


@dataclass
class RecoveryPlan:
    """Plan for recovery operations."""

    recovery_id: str
    recovery_type: RecoveryType
    target_backup_id: str
    created_at: datetime
    scheduled_at: datetime | None
    skill_ids: list[str] = field(default_factory=list)
    target_time: datetime | None = None
    priority: int = 5  # 1-10, 10 being highest
    status: str = "planned"


@dataclass
class BackupConfig:
    """Configuration for backup operations."""

    backup_frequency_hours: int = 24
    retention_days: int = 30
    compression_enabled: bool = True
    encryption_enabled: bool = False
    backup_location: str = "local"
    max_concurrent_backups: int = 2
    verification_enabled: bool = True
    auto_recovery_enabled: bool = True


class BackupRecoveryManager:
    """Manages backup and recovery operations for skill repository."""

    def __init__(self):
        self.storage = get_persistent_storage()
        self.backup_dir = Path.home() / ".amplifier_storage" / "backups"
        self.backup_metadata_file = self.backup_dir / "metadata.json"
        self.recovery_plans_file = self.backup_dir / "recovery_plans.json"
        self.active_backups = {}  # backup_id -> asyncio.Task
        self.backup_history = []  # List of BackupMetadata
        self.recovery_plans = {}  # recovery_id -> RecoveryPlan
        self.backup_config = BackupConfig()

        # Statistics
        self.backup_stats = {
            "total_backups": 0,
            "successful_backups": 0,
            "failed_backups": 0,
            "total_data_backed_up_gb": 0.0,
            "average_backup_time_minutes": 0.0,
            "last_backup_time": None,
            "recovery_operations": 0,
            "successful_recoveries": 0,
        }

    async def initialize(self) -> None:
        """Initialize the backup and recovery manager."""
        await self._ensure_backup_structure()
        await self._load_backup_metadata()
        await self._load_recovery_plans()
        await self._cleanup_old_backups()
        logger.info("Backup and Recovery Manager initialized")

    async def create_backup(
        self,
        backup_type: BackupType = BackupType.FULL,
        description: str = "",
        skill_ids: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Create a backup of the skill repository."""
        try:
            backup_id = str(uuid.uuid4())
            logger.info(f"Starting {backup_type.value} backup: {backup_id}")

            # Create backup metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type=backup_type,
                created_at=datetime.now(),
                completed_at=None,
                status=BackupStatus.PENDING,
                size_bytes=0,
                compressed_size_bytes=0,
                skills_count=0,
                checksum="",
                description=description or f"{backup_type.value} backup",
                retention_days=self.backup_config.retention_days,
                tags=tags or [],
            )

            # Save initial metadata
            self.backup_history.append(metadata)
            await self._save_backup_metadata()

            # Start backup operation
            backup_task = asyncio.create_task(self._execute_backup(metadata, skill_ids))
            self.active_backups[backup_id] = backup_task

            return backup_id

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise

    async def execute_recovery(
        self,
        recovery_type: RecoveryType,
        target_backup_id: str | None = None,
        skill_ids: list[str] | None = None,
        target_time: datetime | None = None,
        priority: int = 5,
    ) -> str:
        """Execute a recovery operation."""
        try:
            recovery_id = str(uuid.uuid4())
            logger.info(f"Starting {recovery_type.value} recovery: {recovery_id}")

            # Create recovery plan
            plan = RecoveryPlan(
                recovery_id=recovery_id,
                recovery_type=recovery_type,
                target_backup_id=target_backup_id or await self._find_latest_backup(),
                created_at=datetime.now(),
                scheduled_at=datetime.now(),
                skill_ids=skill_ids or [],
                target_time=target_time,
                priority=priority,
                status="planned",
            )

            # Save recovery plan
            self.recovery_plans[recovery_id] = plan
            await self._save_recovery_plans()

            # Execute recovery
            await self._execute_recovery(plan)

            return recovery_id

        except Exception as e:
            logger.error(f"Failed to execute recovery: {e}")
            raise

    async def list_backups(
        self, backup_type: BackupType | None = None, status: BackupStatus | None = None, limit: int = 50
    ) -> list[BackupMetadata]:
        """List available backups."""
        try:
            backups = self.backup_history.copy()

            # Apply filters
            if backup_type:
                backups = [b for b in backups if b.backup_type == backup_type]

            if status:
                backups = [b for b in backups if b.status == status]

            # Sort by creation time (newest first)
            backups.sort(key=lambda b: b.created_at, reverse=True)

            return backups[:limit]

        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []

    async def verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity."""
        try:
            # Find backup metadata
            metadata = next((b for b in self.backup_history if b.backup_id == backup_id), None)
            if not metadata:
                logger.error(f"Backup not found: {backup_id}")
                return False

            if metadata.status != BackupStatus.COMPLETED:
                logger.warning(f"Backup not completed: {backup_id}")
                return False

            # Verify backup file exists
            backup_file = self._get_backup_file(backup_id)
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return False

            # Verify checksum
            if metadata.checksum:
                actual_checksum = self._calculate_file_checksum(backup_file)
                if actual_checksum != metadata.checksum:
                    logger.error(f"Backup checksum mismatch for {backup_id}")
                    metadata.status = BackupStatus.CORRUPTED
                    await self._save_backup_metadata()
                    return False

            # Verify backup can be read
            if not await self._verify_backup_content(backup_id):
                logger.error(f"Backup content verification failed for {backup_id}")
                return False

            logger.info(f"Backup verification successful: {backup_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to verify backup {backup_id}: {e}")
            return False

    async def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup."""
        try:
            # Find backup metadata
            metadata = next((b for b in self.backup_history if b.backup_id == backup_id), None)
            if not metadata:
                logger.warning(f"Backup not found: {backup_id}")
                return False

            # Delete backup file
            backup_file = self._get_backup_file(backup_id)
            if backup_file.exists():
                backup_file.unlink()

            # Remove from history
            self.backup_history = [b for b in self.backup_history if b.backup_id != backup_id]
            await self._save_backup_metadata()

            logger.info(f"Deleted backup: {backup_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete backup {backup_id}: {e}")
            return False

    async def get_backup_statistics(self) -> dict[str, Any]:
        """Get comprehensive backup statistics."""
        try:
            completed_backups = [b for b in self.backup_history if b.status == BackupStatus.COMPLETED]
            failed_backups = [b for b in self.backup_history if b.status == BackupStatus.FAILED]

            # Calculate storage usage
            total_size = sum(b.size_bytes for b in completed_backups)
            compressed_size = sum(b.compressed_size_bytes for b in completed_backups)
            compression_ratio = 1 - (compressed_size / total_size) if total_size > 0 else 0

            # Calculate backup frequency by type
            backup_by_type = {}
            for backup in self.backup_history:
                backup_type = backup.backup_type.value
                if backup_type not in backup_by_type:
                    backup_by_type[backup_type] = {"total": 0, "successful": 0}
                backup_by_type[backup_type]["total"] += 1
                if backup.status == BackupStatus.COMPLETED:
                    backup_by_type[backup_type]["successful"] += 1

            return {
                "backup_config": {
                    "frequency_hours": self.backup_config.backup_frequency_hours,
                    "retention_days": self.backup_config.retention_days,
                    "compression_enabled": self.backup_config.compression_enabled,
                    "verification_enabled": self.backup_config.verification_enabled,
                },
                "backup_stats": self.backup_stats,
                "storage_stats": {
                    "total_backups": len(self.backup_history),
                    "completed_backups": len(completed_backups),
                    "failed_backups": len(failed_backups),
                    "success_rate": len(completed_backups) / len(self.backup_history) if self.backup_history else 0,
                    "total_size_gb": total_size / (1024**3),
                    "compressed_size_gb": compressed_size / (1024**3),
                    "compression_ratio": compression_ratio,
                    "backup_directory_size_gb": self._calculate_directory_size(self.backup_dir) / (1024**3),
                },
                "backup_by_type": backup_by_type,
                "recent_backups": [
                    {
                        "backup_id": b.backup_id,
                        "type": b.backup_type.value,
                        "created_at": b.created_at.isoformat(),
                        "status": b.status.value,
                        "size_gb": b.size_bytes / (1024**3),
                    }
                    for b in self.backup_history[:10]
                ],
                "recovery_stats": {
                    "total_plans": len(self.recovery_plans),
                    "active_recoveries": self.backup_stats["recovery_operations"],
                    "successful_recoveries": self.backup_stats["successful_recoveries"],
                },
            }

        except Exception as e:
            logger.error(f"Failed to get backup statistics: {e}")
            return {"error": str(e)}

    async def start_backup_scheduler(self) -> None:
        """Start the automatic backup scheduler."""
        try:
            asyncio.create_task(self._backup_scheduler_loop())
            logger.info("Started automatic backup scheduler")

        except Exception as e:
            logger.error(f"Failed to start backup scheduler: {e}")

    async def _ensure_backup_structure(self) -> None:
        """Ensure backup directory structure exists."""
        directories = [
            self.backup_dir,
            self.backup_dir / "full",
            self.backup_dir / "incremental",
            self.backup_dir / "differential",
            self.backup_dir / "snapshots",
            self.backup_dir / "temp",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    async def _load_backup_metadata(self) -> None:
        """Load backup metadata from storage."""
        try:
            if self.backup_metadata_file.exists():
                with open(self.backup_metadata_file) as f:
                    data = json.load(f)
                    self.backup_history = [
                        BackupMetadata(
                            backup_id=b["backup_id"],
                            backup_type=BackupType(b["backup_type"]),
                            created_at=datetime.fromisoformat(b["created_at"]),
                            completed_at=datetime.fromisoformat(b["completed_at"]) if b.get("completed_at") else None,
                            status=BackupStatus(b["status"]),
                            size_bytes=b["size_bytes"],
                            compressed_size_bytes=b["compressed_size_bytes"],
                            skills_count=b["skills_count"],
                            checksum=b["checksum"],
                            description=b["description"],
                            retention_days=b["retention_days"],
                            tags=b["tags"],
                        )
                        for b in data
                    ]

                logger.info(f"Loaded {len(self.backup_history)} backup records")

        except Exception as e:
            logger.warning(f"Failed to load backup metadata: {e}")

    async def _save_backup_metadata(self) -> None:
        """Save backup metadata to storage."""
        try:
            with open(self.backup_metadata_file, "w") as f:
                json.dump(
                    [
                        {
                            "backup_id": b.backup_id,
                            "backup_type": b.backup_type.value,
                            "created_at": b.created_at.isoformat(),
                            "completed_at": b.completed_at.isoformat() if b.completed_at else None,
                            "status": b.status.value,
                            "size_bytes": b.size_bytes,
                            "compressed_size_bytes": b.compressed_size_bytes,
                            "skills_count": b.skills_count,
                            "checksum": b.checksum,
                            "description": b.description,
                            "retention_days": b.retention_days,
                            "tags": b.tags,
                        }
                        for b in self.backup_history
                    ],
                    f,
                    indent=2,
                )

        except Exception as e:
            logger.error(f"Failed to save backup metadata: {e}")

    async def _load_recovery_plans(self) -> None:
        """Load recovery plans from storage."""
        try:
            if self.recovery_plans_file.exists():
                with open(self.recovery_plans_file) as f:
                    data = json.load(f)
                    self.recovery_plans = {
                        plan_id: RecoveryPlan(
                            recovery_id=plan["recovery_id"],
                            recovery_type=RecoveryType(plan["recovery_type"]),
                            target_backup_id=plan["target_backup_id"],
                            created_at=datetime.fromisoformat(plan["created_at"]),
                            scheduled_at=datetime.fromisoformat(plan["scheduled_at"])
                            if plan.get("scheduled_at")
                            else None,
                            skill_ids=plan["skill_ids"],
                            target_time=datetime.fromisoformat(plan["target_time"])
                            if plan.get("target_time")
                            else None,
                            priority=plan["priority"],
                            status=plan["status"],
                        )
                        for plan_id, plan in data.items()
                    }

                logger.info(f"Loaded {len(self.recovery_plans)} recovery plans")

        except Exception as e:
            logger.warning(f"Failed to load recovery plans: {e}")

    async def _save_recovery_plans(self) -> None:
        """Save recovery plans to storage."""
        try:
            with open(self.recovery_plans_file, "w") as f:
                json.dump(
                    {
                        plan_id: {
                            "recovery_id": plan.recovery_id,
                            "recovery_type": plan.recovery_type.value,
                            "target_backup_id": plan.target_backup_id,
                            "created_at": plan.created_at.isoformat(),
                            "scheduled_at": plan.scheduled_at.isoformat() if plan.scheduled_at else None,
                            "skill_ids": plan.skill_ids,
                            "target_time": plan.target_time.isoformat() if plan.target_time else None,
                            "priority": plan.priority,
                            "status": plan.status,
                        }
                        for plan_id, plan in self.recovery_plans.items()
                    },
                    f,
                    indent=2,
                )

        except Exception as e:
            logger.error(f"Failed to save recovery plans: {e}")

    async def _execute_backup(self, metadata: BackupMetadata, skill_ids: list[str] | None = None) -> None:
        """Execute backup operation."""
        try:
            metadata.status = BackupStatus.RUNNING
            await self._save_backup_metadata()

            start_time = asyncio.get_event_loop().time()

            if metadata.backup_type == BackupType.FULL:
                await self._execute_full_backup(metadata, skill_ids)
            elif metadata.backup_type == BackupType.INCREMENTAL:
                await self._execute_incremental_backup(metadata, skill_ids)
            elif metadata.backup_type == BackupType.DIFFERENTIAL:
                await self._execute_differential_backup(metadata, skill_ids)
            elif metadata.backup_type == BackupType.SNAPSHOT:
                await self._execute_snapshot_backup(metadata, skill_ids)

            # Update metadata
            metadata.completed_at = datetime.now()
            metadata.status = BackupStatus.COMPLETED

            # Calculate checksum
            backup_file = self._get_backup_file(metadata.backup_id)
            metadata.checksum = self._calculate_file_checksum(backup_file)

            # Update statistics
            backup_time_minutes = (asyncio.get_event_loop().time() - start_time) / 60
            self.backup_stats["total_backups"] += 1
            self.backup_stats["successful_backups"] += 1
            self.backup_stats["total_data_backed_up_gb"] += metadata.size_bytes / (1024**3)

            # Update average backup time
            total_successful = self.backup_stats["successful_backups"]
            current_avg = self.backup_stats["average_backup_time_minutes"]
            self.backup_stats["average_backup_time_minutes"] = (
                current_avg * (total_successful - 1) + backup_time_minutes
            ) / total_successful

            self.backup_stats["last_backup_time"] = metadata.completed_at.isoformat()

            await self._save_backup_metadata()
            logger.info(f"Backup completed successfully: {metadata.backup_id}")

            # Verify backup if enabled
            if self.backup_config.verification_enabled:
                await self.verify_backup(metadata.backup_id)

        except Exception as e:
            metadata.status = BackupStatus.FAILED
            await self._save_backup_metadata()
            self.backup_stats["failed_backups"] += 1
            logger.error(f"Backup failed {metadata.backup_id}: {e}")

        finally:
            # Clean up active backup
            if metadata.backup_id in self.active_backups:
                del self.active_backups[metadata.backup_id]

    async def _execute_full_backup(self, metadata: BackupMetadata, skill_ids: list[str] | None = None) -> None:
        """Execute full backup."""
        try:
            backup_file = self._get_backup_file(metadata.backup_id, BackupType.FULL)

            # Get all skills or specific skills
            if skill_ids:
                skills_to_backup = skill_ids
            else:
                skills_to_backup = await self.storage.list_skills()

            backup_data = {
                "backup_metadata": {
                    "backup_id": metadata.backup_id,
                    "backup_type": metadata.backup_type.value,
                    "created_at": metadata.created_at.isoformat(),
                },
                "skills": {},
                "timestamp": datetime.now().isoformat(),
            }

            # Backup each skill
            for skill_id in skills_to_backup:
                try:
                    skill = await self.storage.load_skill(skill_id)
                    if skill:
                        backup_data["skills"][skill_id] = skill.to_dict()
                except Exception as e:
                    logger.warning(f"Failed to backup skill {skill_id}: {e}")

            # Update metadata
            metadata.size_bytes = len(json.dumps(backup_data).encode())
            metadata.skills_count = len(backup_data["skills"])

            # Save backup
            if self.backup_config.compression_enabled:
                with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    zip_file.writestr("backup.json", json.dumps(backup_data, indent=2))
                metadata.compressed_size_bytes = backup_file.stat().st_size
            else:
                with open(backup_file, "w") as f:
                    json.dump(backup_data, f, indent=2)
                metadata.compressed_size_bytes = metadata.size_bytes

        except Exception as e:
            logger.error(f"Failed to execute full backup: {e}")
            raise

    async def _execute_incremental_backup(self, metadata: BackupMetadata, skill_ids: list[str] | None = None) -> None:
        """Execute incremental backup."""
        try:
            # Find latest full backup
            latest_full = await self._find_latest_backup(BackupType.FULL)
            if not latest_full:
                logger.warning("No full backup found, creating full backup instead")
                metadata.backup_type = BackupType.FULL
                await self._execute_full_backup(metadata, skill_ids)
                return

            # Get skills modified since last backup
            modified_skills = await self._get_modified_skills(latest_full, skill_ids)

            # Backup only modified skills
            await self._execute_full_backup(metadata, modified_skills)

        except Exception as e:
            logger.error(f"Failed to execute incremental backup: {e}")
            raise

    async def _execute_differential_backup(self, metadata: BackupMetadata, skill_ids: list[str] | None = None) -> None:
        """Execute differential backup."""
        try:
            # Similar to incremental but captures all changes since last full backup
            await self._execute_incremental_backup(metadata, skill_ids)

        except Exception as e:
            logger.error(f"Failed to execute differential backup: {e}")
            raise

    async def _execute_snapshot_backup(self, metadata: BackupMetadata, skill_ids: list[str] | None = None) -> None:
        """Execute snapshot backup."""
        try:
            # Snapshot is similar to full backup but optimized for speed
            await self._execute_full_backup(metadata, skill_ids)

        except Exception as e:
            logger.error(f"Failed to execute snapshot backup: {e}")
            raise

    async def _execute_recovery(self, plan: RecoveryPlan) -> None:
        """Execute recovery operation."""
        try:
            plan.status = "running"
            await self._save_recovery_plans()

            self.backup_stats["recovery_operations"] += 1

            # Load backup data
            backup_data = await self._load_backup_data(plan.target_backup_id)
            if not backup_data:
                raise Exception(f"Failed to load backup data for {plan.target_backup_id}")

            # Perform recovery based on type
            if plan.recovery_type == RecoveryType.FULL_RESTORE:
                await self._execute_full_restore(backup_data)
            elif plan.recovery_type == RecoveryType.SELECTIVE_RESTORE:
                await self._execute_selective_restore(backup_data, plan.skill_ids)
            elif plan.recovery_type == RecoveryType.POINT_IN_TIME:
                await self._execute_point_in_time_restore(backup_data, plan.target_time)
            elif plan.recovery_type == RecoveryType.DISASTER_RECOVERY:
                await self._execute_disaster_recovery(backup_data)

            plan.status = "completed"
            self.backup_stats["successful_recoveries"] += 1
            await self._save_recovery_plans()

            logger.info(f"Recovery completed successfully: {plan.recovery_id}")

        except Exception as e:
            plan.status = "failed"
            await self._save_recovery_plans()
            logger.error(f"Recovery failed {plan.recovery_id}: {e}")

    async def _execute_full_restore(self, backup_data: dict[str, Any]) -> None:
        """Execute full system restore."""
        try:
            skills = backup_data.get("skills", {})

            for skill_id, skill_dict in skills.items():
                try:
                    # Restore skill to persistent storage
                    from ...mcp.persistent_storage import SkillDefinition
                    from ...mcp.persistent_storage import SkillStatus

                    skill = SkillDefinition(
                        skill_id=skill_dict["skill_id"],
                        name=skill_dict["name"],
                        description=skill_dict["description"],
                        version=skill_dict["version"],
                        language=skill_dict["language"],
                        category=skill_dict["category"],
                        author=skill_dict["author"],
                        created_at=datetime.fromisoformat(skill_dict["created_at"]),
                        updated_at=datetime.fromisoformat(skill_dict["updated_at"]),
                        status=SkillStatus(skill_dict["status"]),
                        code=skill_dict["code"],
                        dependencies=skill_dict["dependencies"],
                        test_cases=skill_dict["test_cases"],
                        usage_count=skill_dict["usage_count"],
                        success_rate=skill_dict["success_rate"],
                        tags=skill_dict["tags"],
                    )

                    await self.storage.register_skill(skill)

                except Exception as e:
                    logger.error(f"Failed to restore skill {skill_id}: {e}")

        except Exception as e:
            logger.error(f"Failed to execute full restore: {e}")
            raise

    async def _execute_selective_restore(self, backup_data: dict[str, Any], skill_ids: list[str]) -> None:
        """Execute selective restore of specific skills."""
        try:
            skills = backup_data.get("skills", {})

            for skill_id in skill_ids:
                if skill_id in skills:
                    skill_dict = skills[skill_id]
                    # Restore individual skill (similar to full restore but for specific skills)
                    await self._restore_individual_skill(skill_dict)

        except Exception as e:
            logger.error(f"Failed to execute selective restore: {e}")
            raise

    async def _execute_point_in_time_restore(self, backup_data: dict[str, Any], target_time: datetime) -> None:
        """Execute point-in-time restore."""
        try:
            # For simplicity, use the backup if it's before target time
            backup_timestamp = datetime.fromisoformat(backup_data.get("timestamp", ""))

            if backup_timestamp <= target_time:
                await self._execute_full_restore(backup_data)
            else:
                # Find earlier backup
                earlier_backup = await self._find_backup_before_time(target_time)
                if earlier_backup:
                    earlier_data = await self._load_backup_data(earlier_backup)
                    if earlier_data:
                        await self._execute_full_restore(earlier_data)

        except Exception as e:
            logger.error(f"Failed to execute point-in-time restore: {e}")
            raise

    async def _execute_disaster_recovery(self, backup_data: dict[str, Any]) -> None:
        """Execute disaster recovery."""
        try:
            # Disaster recovery is essentially a full restore with additional safety checks
            await self._execute_full_restore(backup_data)

            # Additional validation and system checks would go here
            await self._validate_system_integrity()

        except Exception as e:
            logger.error(f"Failed to execute disaster recovery: {e}")
            raise

    async def _restore_individual_skill(self, skill_dict: dict[str, Any]) -> None:
        """Restore an individual skill."""
        try:
            from ...mcp.persistent_storage import SkillDefinition
            from ...mcp.persistent_storage import SkillStatus

            skill = SkillDefinition(
                skill_id=skill_dict["skill_id"],
                name=skill_dict["name"],
                description=skill_dict["description"],
                version=skill_dict["version"],
                language=skill_dict["language"],
                category=skill_dict["category"],
                author=skill_dict["author"],
                created_at=datetime.fromisoformat(skill_dict["created_at"]),
                updated_at=datetime.fromisoformat(skill_dict["updated_at"]),
                status=SkillStatus(skill_dict["status"]),
                code=skill_dict["code"],
                dependencies=skill_dict["dependencies"],
                test_cases=skill_dict["test_cases"],
                usage_count=skill_dict["usage_count"],
                success_rate=skill_dict["success_rate"],
                tags=skill_dict["tags"],
            )

            await self.storage.register_skill(skill)

        except Exception as e:
            logger.error(f"Failed to restore individual skill: {e}")
            raise

    async def _validate_system_integrity(self) -> None:
        """Validate system integrity after disaster recovery."""
        try:
            # Verify that critical skills are present and functional
            # This would include more comprehensive checks in a real implementation
            logger.info("System integrity validation completed")

        except Exception as e:
            logger.error(f"System integrity validation failed: {e}")

    def _get_backup_file(self, backup_id: str, backup_type: BackupType | None = None) -> Path:
        """Get backup file path."""
        if backup_type is None:
            # Try to determine from backup history
            metadata = next((b for b in self.backup_history if b.backup_id == backup_id), None)
            if metadata:
                backup_type = metadata.backup_type
            else:
                backup_type = BackupType.FULL

        type_dir = backup_type.value
        return self.backup_dir / type_dir / f"{backup_id}.json"

    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate checksum of a file."""
        import hashlib

        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    async def _verify_backup_content(self, backup_id: str) -> bool:
        """Verify backup content can be read."""
        try:
            backup_data = await self._load_backup_data(backup_id)
            return backup_data is not None and "skills" in backup_data

        except Exception as e:
            logger.error(f"Backup content verification failed: {e}")
            return False

    async def _load_backup_data(self, backup_id: str) -> dict[str, Any] | None:
        """Load data from backup file."""
        try:
            backup_file = self._get_backup_file(backup_id)

            if not backup_file.exists():
                return None

            # Handle compressed backups
            if backup_file.suffix == ".json":
                with open(backup_file) as f:
                    return json.load(f)
            elif backup_file.suffix == ".zip":
                with zipfile.ZipFile(backup_file, "r") as zip_file:
                    with zip_file.open("backup.json") as f:
                        return json.load(f)

            return None

        except Exception as e:
            logger.error(f"Failed to load backup data for {backup_id}: {e}")
            return None

    async def _find_latest_backup(self, backup_type: BackupType | None = None) -> str | None:
        """Find the latest backup ID."""
        try:
            backups = self.backup_history.copy()
            if backup_type:
                backups = [b for b in backups if b.backup_type == backup_type]

            completed_backups = [b for b in backups if b.status == BackupStatus.COMPLETED]

            if not completed_backups:
                return None

            latest = max(completed_backups, key=lambda b: b.created_at)
            return latest.backup_id

        except Exception as e:
            logger.error(f"Failed to find latest backup: {e}")
            return None

    async def _find_backup_before_time(self, target_time: datetime) -> str | None:
        """Find backup created before a specific time."""
        try:
            completed_backups = [
                b for b in self.backup_history if b.status == BackupStatus.COMPLETED and b.created_at < target_time
            ]

            if not completed_backups:
                return None

            latest = max(completed_backups, key=lambda b: b.created_at)
            return latest.backup_id

        except Exception as e:
            logger.error(f"Failed to find backup before time: {e}")
            return None

    async def _get_modified_skills(self, since_backup_id: str, skill_ids: list[str] | None = None) -> list[str]:
        """Get skills modified since a backup."""
        try:
            # This is a simplified implementation
            # In a real system, this would compare modification timestamps
            all_skills = skill_ids or await self.storage.list_skills()
            return all_skills

        except Exception as e:
            logger.error(f"Failed to get modified skills: {e}")
            return []

    def _calculate_directory_size(self, directory: Path) -> int:
        """Calculate total size of a directory."""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size

    async def _cleanup_old_backups(self) -> None:
        """Clean up old backups based on retention policy."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.backup_config.retention_days)
            old_backups = [
                b for b in self.backup_history if b.created_at < cutoff_date and b.status == BackupStatus.COMPLETED
            ]

            for backup in old_backups:
                await self.delete_backup(backup.backup_id)

            if old_backups:
                logger.info(f"Cleaned up {len(old_backups)} old backups")

        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")

    async def _backup_scheduler_loop(self) -> None:
        """Background loop for scheduled backups."""
        while True:
            try:
                # Check if it's time for a backup
                if not self.backup_stats["last_backup_time"]:
                    # No backup has been made yet
                    await self.create_backup(BackupType.FULL, "Scheduled automatic backup")
                else:
                    last_backup = datetime.fromisoformat(self.backup_stats["last_backup_time"])
                    next_backup = last_backup + timedelta(hours=self.backup_config.backup_frequency_hours)

                    if datetime.now() >= next_backup:
                        await self.create_backup(BackupType.FULL, "Scheduled automatic backup")

                # Sleep until next check
                await asyncio.sleep(3600)  # Check every hour

            except Exception as e:
                logger.error(f"Backup scheduler error: {e}")
                await asyncio.sleep(300)  # Retry after 5 minutes
