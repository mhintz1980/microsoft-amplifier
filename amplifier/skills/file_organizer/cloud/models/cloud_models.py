"""
Data models for cloud provider integration and configuration.

This module defines models for cloud providers, authentication,
and sync configuration management.
"""

from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from secrets import token_urlsafe
from pydantic import BaseModel, Field, validator


class CloudProvider(str, Enum):
    """Supported cloud storage providers."""

    ONEDRIVE = "onedrive"
    GOOGLE_DRIVE = "gdrive"
    DROPBOX = "dropbox"
    LOCAL = "local"  # For testing and offline mode


class SyncDirection(str, Enum):
    """Synchronization direction options."""

    UPLOAD = "upload"  # Local to cloud only
    DOWNLOAD = "download"  # Cloud to local only
    BIDIRECTIONAL = "bidirectional"  # Both directions with conflict resolution


class ConflictResolution(str, Enum):
    """Conflict resolution strategies for synchronization."""

    LAST_WRITE_WINS = "last_write_wins"  # Most recently modified file wins
    LOCAL_WINS = "local_wins"  # Local version always wins
    REMOTE_WINS = "remote_wins"  # Remote/cloud version always wins
    MANUAL = "manual"  # Require manual resolution


class AuthStatus(str, Enum):
    """Authentication status for cloud providers."""

    NOT_AUTHENTICATED = "not_authenticated"
    PENDING = "pending"
    AUTHENTICATED = "authenticated"
    EXPIRED = "expired"
    ERROR = "error"


class CloudFile(BaseModel):
    """Representation of a file in cloud storage."""

    id: str = Field(description="Unique file identifier in cloud storage")
    name: str = Field(description="File name")
    path: str = Field(description="Full path in cloud storage")
    size: int = Field(description="File size in bytes", ge=0)
    modified_time: datetime = Field(description="Last modified timestamp")
    etag: Optional[str] = Field(None, description="Entity tag for version tracking")
    mime_type: Optional[str] = Field(None, description="MIME type")
    download_url: Optional[str] = Field(None, description="Temporary download URL")
    parent_id: Optional[str] = Field(None, description="Parent folder ID")
    is_folder: bool = Field(False, description="Whether this is a folder")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class CloudConfig(BaseModel):
    """Configuration for a specific cloud provider."""

    provider: CloudProvider = Field(description="Cloud storage provider")
    auth_status: AuthStatus = Field(AuthStatus.NOT_AUTHENTICATED, description="Authentication status")
    client_id: Optional[str] = Field(None, description="OAuth client ID")
    client_secret: Optional[str] = Field(None, description="OAuth client secret")
    access_token: Optional[str] = Field(None, description="Access token")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    token_expires: Optional[datetime] = Field(None, description="Token expiration time")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI")
    scope: List[str] = Field(default_factory=list, description="OAuth scopes")

    # Provider-specific settings
    api_endpoint: Optional[str] = Field(None, description="Custom API endpoint")
    chunk_size: int = Field(1024 * 1024, description="Upload chunk size in bytes", ge=1024)
    max_retries: int = Field(3, description="Maximum retry attempts", ge=0)
    timeout_seconds: int = Field(30, description="Request timeout in seconds", ge=1)

    @validator("redirect_uri")
    def validate_redirect_uri(cls, v):
        """Validate redirect URI format."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("Redirect URI must start with http:// or https://")
        return v

    def is_token_valid(self) -> bool:
        """Check if access token is valid and not expired."""
        if not self.access_token:
            return False
        if self.token_expires and datetime.now() >= self.token_expires:
            return False
        return True

    def needs_refresh(self) -> bool:
        """Check if token needs refresh (within 5 minutes of expiration)."""
        if not self.token_expires:
            return False
        refresh_threshold = self.token_expires - timedelta(minutes=5)
        return datetime.now() >= refresh_threshold


class SyncConfig(BaseModel):
    """Configuration for synchronization operations."""

    sync_directory: Path = Field(description="Local directory to synchronize")
    cloud_config: CloudConfig = Field(description="Cloud provider configuration")
    direction: SyncDirection = Field(SyncDirection.BIDIRECTIONAL, description="Sync direction")
    conflict_resolution: ConflictResolution = Field(
        ConflictResolution.LAST_WRITE_WINS, description="Default conflict resolution strategy"
    )

    # Sync behavior
    auto_sync: bool = Field(True, description="Enable automatic synchronization")
    sync_interval_minutes: int = Field(30, description="Auto-sync interval in minutes", ge=1)
    delta_sync: bool = Field(True, description="Enable delta synchronization")
    max_file_size_mb: float = Field(1024.0, description="Maximum file size to sync in MB", ge=1.0)

    # Bandwidth and performance
    max_concurrent_uploads: int = Field(3, description="Maximum concurrent uploads", ge=1)
    max_concurrent_downloads: int = Field(5, description="Maximum concurrent downloads", ge=1)
    bandwidth_limit_mbps: Optional[float] = Field(None, description="Bandwidth limit in Mbps", ge=0.1)

    # File filtering
    include_patterns: List[str] = Field(default_factory=list, description="Include file patterns")
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [
            "*.tmp",
            "*.temp",
            ".DS_Store",
            "Thumbs.db",
            ".organizer_backup",
        ],
        description="Exclude file patterns",
    )
    include_hidden: bool = Field(False, description="Include hidden files")
    max_depth: Optional[int] = Field(None, description="Maximum directory depth", ge=1)

    # Offline support
    offline_mode: bool = Field(False, description="Force offline mode")
    queue_offline_changes: bool = Field(True, description="Queue changes when offline")
    auto_retry_failed_syncs: bool = Field(True, description="Automatically retry failed syncs")
    retry_attempts: int = Field(3, description="Maximum retry attempts for failed syncs", ge=0)

    # Security
    encrypt_transfers: bool = Field(True, description="Encrypt file transfers")
    verify_checksums: bool = Field(True, description="Verify file integrity with checksums")

    # Monitoring and logging
    enable_logging: bool = Field(True, description="Enable detailed sync logging")
    log_level: str = Field("INFO", description="Log level")
    log_file: Optional[Path] = Field(None, description="Sync log file path")

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @validator("sync_directory")
    def validate_sync_directory(cls, v):
        """Validate sync directory."""
        if not v.is_absolute():
            raise ValueError("Sync directory must be an absolute path")
        return v.resolve()

    def should_sync_file(self, file_path: Path, file_size: int) -> bool:
        """
        Determine if a file should be synchronized based on configuration.

        Args:
            file_path: Path to the file
            file_size: File size in bytes

        Returns:
            True if file should be synchronized
        """
        import fnmatch

        relative_path = file_path.relative_to(self.sync_directory)

        # Check file size
        if file_size > self.max_file_size_mb * 1024 * 1024:
            return False

        # Check hidden files
        if not self.include_hidden and any(part.startswith(".") for part in relative_path.parts):
            return False

        # Check max depth
        if self.max_depth is not None:
            depth = len(relative_path.parts)
            if depth > self.max_depth:
                return False

        # Check include patterns
        if self.include_patterns:
            if not any(fnmatch.fnmatch(file_path.name, pattern) for pattern in self.include_patterns):
                return False

        # Check exclude patterns
        if self.exclude_patterns:
            if any(fnmatch.fnmatch(file_path.name, pattern) for pattern in self.exclude_patterns):
                return False

        return True

    def get_max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return int(self.max_file_size_mb * 1024 * 1024)


# Import SyncDirection and ConflictResolution from sync_models
from .sync_models import SyncDirection, ConflictResolution
