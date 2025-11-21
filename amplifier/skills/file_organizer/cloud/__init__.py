"""
Cloud Sync Module for File Organizer

Phase 3: Cloud sync awareness and multi-device consistency.

This module provides cloud storage integration with:
- Provider abstraction (OneDrive, Google Drive, Dropbox)
- Last-write-wins conflict resolution
- Delta sync optimization
- Cross-device consistency
- Offline support

Basic Usage:
    >>> from amplifier.skills.file_organizer.cloud import CloudSyncManager
    >>> sync_manager = CloudSyncManager()
    >>> result = await sync_manager.sync_directory("/path/to/files")
    >>> print(f"Synced {result.files_synced} files")
"""

from .cloud_sync_manager import CloudSyncManager
from .sync_engine import SyncEngine, SyncDirection
from .models.sync_models import SyncResult, SyncConflict, SyncStatus
from .models.cloud_models import (
    CloudFile, CloudProvider, CloudConfig, SyncConfig,
    ConflictResolution, AuthStatus
)

__all__ = [
    "CloudSyncManager",
    "SyncEngine",
    "SyncDirection",
    "SyncResult",
    "SyncConflict",
    "SyncStatus",
    "CloudFile",
    "CloudProvider",
    "CloudConfig",
    "SyncConfig",
    "ConflictResolution",
    "AuthStatus",
]
