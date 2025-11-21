"""
Synchronization engine for cloud storage operations.

This module implements the core sync logic including:
- File comparison and change detection
- Conflict resolution (last-write-wins)
- Progress tracking and error handling
- Sync state persistence
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
import sqlite3
from contextlib import asynccontextmanager

from .providers.base_provider import BaseProvider
from .models.sync_models import (
    SyncResult,
    SyncConflict,
    SyncStatus,
    SyncDirection,
    SyncOperation,
    FileMetadata,
    SyncState,
)
from .models.cloud_models import CloudFile, CloudConfig

logger = logging.getLogger(__name__)


@dataclass
class SyncProgress:
    """Progress tracking for sync operations."""

    total_files: int = 0
    processed_files: int = 0
    current_file: str = ""
    stage: str = "initializing"
    start_time: datetime = None

    @property
    def progress_percentage(self) -> float:
        """Progress as percentage."""
        if self.total_files == 0:
            return 0.0
        return round((self.processed_files / self.total_files) * 100, 2)


class SyncEngine:
    """
    Core synchronization engine.

    Handles the logic of comparing local and cloud files, detecting changes,
    resolving conflicts, and executing sync operations.
    """

    def __init__(
        self, provider: BaseProvider, sync_directory: Path, config: CloudConfig, db_path: Optional[Path] = None
    ):
        """
        Initialize the sync engine.

        Args:
            provider: Cloud storage provider
            sync_directory: Local directory to synchronize
            config: Sync configuration
            db_path: Path to SQLite database for sync state
        """
        self.provider = provider
        self.sync_directory = sync_directory.resolve()
        self.config = config
        self.db_path = db_path or sync_directory / ".sync_state.db"

        # Initialize database
        self._init_database()

        # Progress tracking
        self._progress = SyncProgress(start_time=datetime.now())

        logger.info(f"Sync engine initialized for {sync_directory} with {provider.provider_name}")

    def _init_database(self) -> None:
        """Initialize SQLite database for sync state tracking."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_metadata (
                    path TEXT PRIMARY KEY,
                    size INTEGER,
                    modified_time REAL,
                    checksum TEXT,
                    cloud_id TEXT,
                    etag TEXT,
                    version INTEGER DEFAULT 1,
                    sync_status TEXT DEFAULT 'pending',
                    last_sync_time REAL,
                    local_path TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time REAL,
                    end_time REAL,
                    total_files INTEGER,
                    files_synced INTEGER,
                    conflicts_resolved INTEGER,
                    success BOOLEAN,
                    error_message TEXT
                )
            """)

            conn.commit()

    def save_sync_state(self, sync_state: SyncState) -> None:
        """Save sync state to database."""
        with sqlite3.connect(self.db_path) as conn:
            # Clear existing metadata
            conn.execute("DELETE FROM file_metadata")

            # Insert current metadata
            for path_str, metadata in sync_state.file_metadata.items():
                conn.execute(
                    """
                    INSERT INTO file_metadata (
                        path, size, modified_time, checksum, cloud_id,
                        etag, version, sync_status, last_sync_time, local_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        path_str,
                        metadata.size,
                        metadata.modified_time.timestamp(),
                        metadata.checksum,
                        metadata.cloud_id,
                        metadata.etag,
                        metadata.version,
                        metadata.sync_status.value,
                        metadata.last_sync_time.timestamp() if metadata.last_sync_time else None,
                        str(metadata.path),
                    ),
                )

            conn.commit()

    def load_sync_state(self) -> SyncState:
        """Load sync state from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM file_metadata")
            file_metadata = {}

            for row in cursor.fetchall():
                (
                    path_str,
                    size,
                    modified_ts,
                    checksum,
                    cloud_id,
                    etag,
                    version,
                    sync_status,
                    last_sync_ts,
                    local_path,
                ) = row

                metadata = FileMetadata(
                    path=Path(local_path),
                    size=size,
                    modified_time=datetime.fromtimestamp(modified_ts),
                    checksum=checksum,
                    cloud_id=cloud_id,
                    etag=etag,
                    version=version,
                    sync_status=SyncStatus(sync_status),
                    last_sync_time=datetime.fromtimestamp(last_sync_ts) if last_sync_ts else None,
                )
                file_metadata[path_str] = metadata

        return SyncState(
            sync_directory=self.sync_directory, cloud_provider=self.provider.provider_name, file_metadata=file_metadata
        )

    async def scan_local_files(self) -> Dict[Path, FileMetadata]:
        """
        Scan local files and return metadata.

        Returns:
            Dictionary mapping local paths to file metadata
        """
        local_files = {}
        total_files = 0

        # Count files first for progress
        for file_path in self.sync_directory.rglob("*"):
            if file_path.is_file() and self.config.should_sync_file(file_path, file_path.stat().st_size):
                total_files += 1

        self._progress.total_files = total_files
        self._progress.stage = "scanning_local"

        # Scan files
        for file_path in self.sync_directory.rglob("*"):
            if not file_path.is_file():
                continue

            try:
                stat = file_path.stat()
                file_size = stat.st_size

                # Check if file should be synced
                if not self.config.should_sync_file(file_path, file_size):
                    continue

                # Calculate checksum if configured
                checksum = None
                if self.config.verify_checksums:
                    checksum = await self.provider._calculate_file_checksum(file_path)

                metadata = FileMetadata(
                    path=file_path,
                    size=file_size,
                    modified_time=datetime.fromtimestamp(stat.st_mtime),
                    checksum=checksum,
                    sync_status=SyncStatus.PENDING,
                )

                local_files[file_path] = metadata
                self._progress.processed_files += 1
                self._progress.current_file = str(file_path.relative_to(self.sync_directory))

            except Exception as e:
                logger.warning(f"Failed to scan file {file_path}: {e}")

        return local_files

    async def scan_cloud_files(self) -> Dict[str, CloudFile]:
        """
        Scan cloud files and return metadata.

        Returns:
            Dictionary mapping cloud paths to CloudFile objects
        """
        cloud_files = {}
        self._progress.stage = "scanning_cloud"

        try:
            async for cloud_file in self.provider.list_files(recursive=True):
                cloud_files[cloud_file.path] = cloud_file
                self._progress.processed_files += 1
                self._progress.current_file = cloud_file.path

        except Exception as e:
            logger.error(f"Failed to scan cloud files: {e}")
            raise

        return cloud_files

    async def detect_changes(
        self, local_files: Dict[Path, FileMetadata], cloud_files: Dict[str, CloudFile]
    ) -> Tuple[List[Tuple[Path, FileMetadata, str]], List[Tuple[CloudFile, str]]]:
        """
        Detect changes between local and cloud files.

        Returns:
            Tuple of (local_changes, cloud_changes) where changes are (file, operation_type)
        """
        local_changes = []
        cloud_changes = []

        # Load previous sync state
        sync_state = self.load_sync_state()

        # Detect local changes
        for local_path, local_meta in local_files.items():
            relative_path = str(local_path.relative_to(self.sync_directory))
            cloud_path = relative_path.replace("\\", "/")

            # Get previous metadata
            prev_meta = sync_state.get_file_metadata(local_path)

            # Check if file is new or modified
            if not prev_meta:
                local_changes.append((local_path, local_meta, "create"))
            elif local_meta.modified_time > prev_meta.modified_time:
                local_changes.append((local_path, local_meta, "update"))

            # Check if file exists in cloud
            cloud_file = cloud_files.get(cloud_path)
            if cloud_file:
                # Check for potential conflicts
                if cloud_file.modified_time > local_meta.modified_time:
                    # Cloud version is newer - potential conflict
                    pass

        # Detect cloud changes
        for cloud_path, cloud_file in cloud_files.items():
            local_path = self.sync_directory / cloud_path.replace("/", os.sep)

            # Check if cloud file is new
            if not local_path.exists():
                cloud_changes.append((cloud_file, "create"))
            else:
                # Check if cloud version is newer than local
                local_meta = local_files.get(local_path)
                if local_meta and cloud_file.modified_time > local_meta.modified_time:
                    cloud_changes.append((cloud_file, "update"))

        # Detect local deletions
        prev_sync_state = self.load_sync_state()
        for prev_path in prev_sync_state.file_metadata.keys():
            prev_local_path = self.sync_directory / prev_path
            if not prev_local_path.exists():
                # File was deleted locally
                cloud_path = prev_path.replace("\\", "/")
                if cloud_path in cloud_files:
                    cloud_changes.append((cloud_files[cloud_path], "delete"))

        return local_changes, cloud_changes

    async def resolve_conflicts(self, local_meta: FileMetadata, cloud_file: CloudFile) -> Optional[SyncConflict]:
        """
        Resolve conflicts between local and cloud files.

        Args:
            local_meta: Local file metadata
            cloud_file: Cloud file metadata

        Returns:
            SyncConflict if unresolved, None if auto-resolved
        """
        # Last-write-wins resolution
        if local_meta.modified_time > cloud_file.modified_time:
            # Local wins
            logger.info(f"Conflict resolved: Local version wins for {local_meta.path}")
            return None
        else:
            # Cloud wins
            logger.info(f"Conflict resolved: Cloud version wins for {local_meta.path}")
            return None

    async def sync_file(
        self,
        direction: SyncDirection,
        local_path: Optional[Path] = None,
        cloud_file: Optional[CloudFile] = None,
        operation: str = "update",
    ) -> bool:
        """
        Sync a single file in the specified direction.

        Args:
            direction: Sync direction
            local_path: Local file path
            cloud_file: Cloud file metadata
            operation: Operation type

        Returns:
            True if sync successful, False otherwise
        """
        try:
            if direction == SyncDirection.UPLOAD and local_path:
                # Upload local file to cloud
                cloud_path = str(local_path.relative_to(self.sync_directory)).replace("\\", "/")
                await self.provider.upload_file(local_path, cloud_path)
                logger.info(f"Uploaded {local_path} to cloud")

            elif direction == SyncDirection.DOWNLOAD and cloud_file:
                # Download cloud file to local
                local_path = self.sync_directory / cloud_file.path.replace("/", os.sep)
                local_path.parent.mkdir(parents=True, exist_ok=True)
                await self.provider.download_file(cloud_file.id, local_path)
                logger.info(f"Downloaded {cloud_file.path} from cloud")

            return True

        except Exception as e:
            logger.error(f"Failed to sync file: {e}")
            return False

    async def synchronize(self, direction: SyncDirection = SyncDirection.BIDIRECTIONAL) -> SyncResult:
        """
        Perform full synchronization.

        Args:
            direction: Sync direction

        Returns:
            SyncResult with operation details
        """
        start_time = datetime.now()
        result = SyncResult(success=False, total_files=0, start_time=start_time)

        try:
            logger.info(f"Starting {direction} synchronization")
            self._progress.stage = "synchronizing"

            # Scan local files
            local_files = await self.scan_local_files()

            # Scan cloud files
            cloud_files = await self.scan_cloud_files()

            # Detect changes
            local_changes, cloud_changes = await self.detect_changes(local_files, cloud_files)

            result.total_files = len(local_changes) + len(cloud_changes)

            # Process local changes (uploads)
            if direction in [SyncDirection.UPLOAD, SyncDirection.BIDIRECTIONAL]:
                for local_path, local_meta, operation in local_changes:
                    self._progress.current_file = str(local_path.relative_to(self.sync_directory))

                    if await self.sync_file(SyncDirection.UPLOAD, local_path=local_path, operation=operation):
                        result.files_uploaded += 1
                    else:
                        result.failed_files += 1
                        result.errors.append(f"Failed to upload {local_path}")

            # Process cloud changes (downloads)
            if direction in [SyncDirection.DOWNLOAD, SyncDirection.BIDIRECTIONAL]:
                for cloud_file, operation in cloud_changes:
                    self._progress.current_file = cloud_file.path

                    if operation == "delete":
                        # Handle deletions
                        local_path = self.sync_directory / cloud_file.path.replace("/", os.sep)
                        if local_path.exists():
                            local_path.unlink()
                            result.files_deleted += 1
                    else:
                        if await self.sync_file(SyncDirection.DOWNLOAD, cloud_file=cloud_file, operation=operation):
                            result.files_downloaded += 1
                        else:
                            result.failed_files += 1
                            result.errors.append(f"Failed to download {cloud_file.path}")

            # Update sync state
            new_sync_state = SyncState(
                sync_directory=self.sync_directory,
                cloud_provider=self.provider.provider_name,
                last_full_sync=datetime.now(),
                file_metadata={str(path.relative_to(self.sync_directory)): meta for path, meta in local_files.items()},
            )
            self.save_sync_state(new_sync_state)

            result.success = True
            result.end_time = datetime.now()
            result.duration_seconds = (result.end_time - start_time).total_seconds()

            logger.info(f"Synchronization completed: {result.files_synced} files synced")

        except Exception as e:
            result.success = False
            result.errors.append(f"Synchronization failed: {e}")
            result.end_time = datetime.now()
            result.duration_seconds = (result.end_time - start_time).total_seconds()
            logger.error(f"Synchronization failed: {e}")

        return result

    def get_progress(self) -> SyncProgress:
        """Get current sync progress."""
        return self._progress

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass
