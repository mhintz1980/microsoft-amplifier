"""
Data models for synchronization operations and state management.

This module defines the core data structures for tracking sync operations,
handling conflicts, and maintaining sync state across devices.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field


class SyncStatus(str, Enum):
    """Status of synchronization operations."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    CONFLICT = "conflict"


class SyncDirection(str, Enum):
    """Direction of synchronization."""

    UPLOAD = "upload"  # Local to cloud
    DOWNLOAD = "download"  # Cloud to local
    BIDIRECTIONAL = "bidirectional"  # Both ways


class SyncOperation(str, Enum):
    """Types of sync operations."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MOVE = "move"
    CONFLICT = "conflict"


class ConflictResolution(str, Enum):
    """Strategies for resolving sync conflicts."""

    LOCAL_WINS = "local_wins"  # Use local version
    REMOTE_WINS = "remote_wins"  # Use remote version
    LAST_WRITE_WINS = "last_write_wins"  # Use most recently modified
    MANUAL = "manual"  # Require user intervention
    SKIP = "skip"  # Skip conflicting file


class FileMetadata(BaseModel):
    """Metadata for file synchronization tracking."""

    path: Path = Field(description="Relative path within sync directory")
    size: int = Field(description="File size in bytes", ge=0)
    modified_time: datetime = Field(description="File last modified timestamp")
    checksum: Optional[str] = Field(None, description="MD5 checksum for integrity verification")
    etag: Optional[str] = Field(None, description="Cloud provider etag")
    cloud_id: Optional[str] = Field(None, description="Cloud provider file ID")
    version: int = Field(1, description="Local version number", ge=1)
    sync_status: SyncStatus = Field(SyncStatus.PENDING, description="Current sync status")
    last_sync_time: Optional[datetime] = Field(None, description="Last successful sync timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Path: lambda v: str(v),
        }


class SyncConflict(BaseModel):
    """Represents a sync conflict that needs resolution."""

    path: Path = Field(description="File path with conflict")
    local_metadata: FileMetadata = Field(description="Local file metadata")
    remote_metadata: FileMetadata = Field(description="Remote file metadata")
    conflict_type: str = Field(description="Type of conflict detected")
    resolution: Optional[ConflictResolution] = Field(None, description="Chosen resolution strategy")
    resolved: bool = Field(False, description="Whether conflict has been resolved")
    resolution_time: Optional[datetime] = Field(None, description="When conflict was resolved")

    def auto_resolve(self, strategy: ConflictResolution = ConflictResolution.LAST_WRITE_WINS) -> bool:
        """
        Attempt to automatically resolve the conflict using the specified strategy.

        Args:
            strategy: Resolution strategy to apply

        Returns:
            True if conflict was resolved successfully
        """
        if strategy == ConflictResolution.LAST_WRITE_WINS:
            # Choose the file with the most recent modification time
            if self.local_metadata.modified_time > self.remote_metadata.modified_time:
                self.resolution = ConflictResolution.LOCAL_WINS
            else:
                self.resolution = ConflictResolution.REMOTE_WINS
        else:
            self.resolution = strategy

        self.resolved = True
        self.resolution_time = datetime.now()
        return True


class SyncResult(BaseModel):
    """Result of a synchronization operation."""

    success: bool = Field(description="Whether sync operation was successful")
    total_files: int = Field(description="Total files processed")
    files_uploaded: int = Field(0, description="Files uploaded to cloud")
    files_downloaded: int = Field(0, description="Files downloaded from cloud")
    files_deleted: int = Field(0, description="Files deleted")
    files_skipped: int = Field(0, description="Files skipped")
    conflicts_resolved: int = Field(0, description="Number of conflicts resolved")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    conflicts: List[SyncConflict] = Field(default_factory=list, description="Unresolved conflicts")

    # Performance metrics
    duration_seconds: float = Field(description="Total sync duration")
    bytes_uploaded: int = Field(0, description="Total bytes uploaded")
    bytes_downloaded: int = Field(0, description="Total bytes downloaded")

    # Sync state
    start_time: datetime = Field(description="Sync operation start time")
    end_time: Optional[datetime] = Field(None, description="Sync operation end time")

    @property
    def files_synced(self) -> int:
        """Total number of files synchronized."""
        return self.files_uploaded + self.files_downloaded + self.files_deleted

    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.total_files == 0:
            return 0.0
        return round((self.files_synced / self.total_files) * 100, 2)

    @property
    def bandwidth_used_mb(self) -> float:
        """Total bandwidth used in megabytes."""
        total_bytes = self.bytes_uploaded + self.bytes_downloaded
        return round(total_bytes / (1024 * 1024), 2)


class SyncState(BaseModel):
    """Persistent synchronization state."""

    sync_directory: Path = Field(description="Local directory being synchronized")
    cloud_provider: str = Field(description="Cloud provider name")
    last_full_sync: Optional[datetime] = Field(None, description="Last full sync timestamp")
    last_incremental_sync: Optional[datetime] = Field(None, description="Last incremental sync timestamp")
    file_metadata: Dict[str, FileMetadata] = Field(default_factory=dict, description="File metadata by path")
    sync_version: str = Field("1.0", description="Sync state version for migrations")

    def get_file_metadata(self, path: Path) -> Optional[FileMetadata]:
        """Get metadata for a specific file."""
        return self.file_metadata.get(str(path.relative_to(self.sync_directory)))

    def update_file_metadata(self, path: Path, metadata: FileMetadata) -> None:
        """Update metadata for a file."""
        relative_path = str(path.relative_to(self.sync_directory))
        self.file_metadata[relative_path] = metadata

    def remove_file_metadata(self, path: Path) -> None:
        """Remove metadata for a file."""
        relative_path = str(path.relative_to(self.sync_directory))
        self.file_metadata.pop(relative_path, None)

    def get_all_files(self) -> Dict[Path, FileMetadata]:
        """Get all file metadata as Path->FileMetadata mapping."""
        return {Path(relative_path): metadata for relative_path, metadata in self.file_metadata.items()}

    def mark_all_pending(self) -> None:
        """Mark all files as pending for next sync."""
        for metadata in self.file_metadata.values():
            metadata.sync_status = SyncStatus.PENDING
