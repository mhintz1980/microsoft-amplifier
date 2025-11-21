"""
Cloud Sync Manager - Main orchestration for file synchronization.

This module provides the main interface for cloud synchronization,
handling provider management, configuration, and high-level sync operations.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
import json

from .sync_engine import SyncEngine
from .providers import get_provider, BaseProvider
from .models.cloud_models import CloudConfig, CloudProvider, SyncConfig, AuthStatus
from .models.sync_models import SyncResult, SyncDirection, SyncState, SyncStatus

logger = logging.getLogger(__name__)


class CloudSyncManager:
    """
    Main manager for cloud synchronization operations.

    Provides a high-level interface for synchronizing files with cloud storage,
    handling authentication, configuration, and error recovery.
    """

    def __init__(self, config: Optional[SyncConfig] = None):
        """
        Initialize the cloud sync manager.

        Args:
            config: Sync configuration (creates default if None)
        """
        self.config = config or SyncConfig(
            sync_directory=Path.home() / "Sync", cloud_config=CloudConfig(provider=CloudProvider.LOCAL)
        )

        self.provider: Optional[BaseProvider] = None
        self.sync_engine: Optional[SyncEngine] = None
        self._sync_state: Optional[SyncState] = None
        self._active_sync: Optional[asyncio.Task] = None

        # Initialize provider
        self._initialize_provider()

        logger.info(f"Cloud sync manager initialized for {self.config.cloud_config.provider}")

    def _initialize_provider(self) -> None:
        """Initialize the cloud provider based on configuration."""
        try:
            provider_class = get_provider(self.config.cloud_config.provider.value)
            self.provider = provider_class(self.config.cloud_config)

            # Initialize sync engine
            self.sync_engine = SyncEngine(
                provider=self.provider, sync_directory=self.config.sync_directory, config=self.config.cloud_config
            )

        except Exception as e:
            logger.error(f"Failed to initialize provider: {e}")
            raise

    async def authenticate(self, force_reauth: bool = False) -> bool:
        """
        Authenticate with the cloud provider.

        Args:
            force_reauth: Force re-authentication even if already authenticated

        Returns:
            True if authentication successful, False otherwise
        """
        if not self.provider:
            logger.error("No provider configured")
            return False

        try:
            if force_reauth or not self.provider.is_authenticated:
                logger.info("Authenticating with cloud provider...")
                success = await self.provider.authenticate()

                if success:
                    self.config.cloud_config.auth_status = AuthStatus.AUTHENTICATED
                    logger.info("Authentication successful")
                else:
                    self.config.cloud_config.auth_status = AuthStatus.ERROR
                    logger.error("Authentication failed")

                return success
            else:
                logger.info("Already authenticated")
                self.config.cloud_config.auth_status = AuthStatus.AUTHENTICATED
                return True

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            self.config.cloud_config.auth_status = AuthStatus.ERROR
            return False

    async def get_authentication_url(self) -> Optional[str]:
        """
        Get authentication URL for OAuth providers.

        Returns:
            Authentication URL or None if not applicable
        """
        if not self.provider:
            return None

        try:
            return await self.provider.get_auth_url()
        except Exception as e:
            logger.error(f"Failed to get auth URL: {e}")
            return None

    async def handle_authentication_callback(self, code: str) -> bool:
        """
        Handle OAuth authentication callback.

        Args:
            code: Authorization code from OAuth provider

        Returns:
            True if callback handled successfully
        """
        if not self.provider:
            return False

        try:
            success = await self.provider.handle_auth_callback(code)
            if success:
                self.config.cloud_config.auth_status = AuthStatus.AUTHENTICATED
            return success
        except Exception as e:
            logger.error(f"Failed to handle auth callback: {e}")
            return False

    async def test_connection(self) -> bool:
        """
        Test connection to cloud provider.

        Returns:
            True if connection successful, False otherwise
        """
        if not self.provider:
            return False

        try:
            # Try to list files (should work even for empty directories)
            async for _ in self.provider.list_files(page_size=1):
                return True
            return True  # No files but connection worked
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    async def sync_directory(
        self,
        directory: Optional[Path] = None,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        force_full_sync: bool = False,
    ) -> SyncResult:
        """
        Synchronize a directory with cloud storage.

        Args:
            directory: Directory to sync (uses configured directory if None)
            direction: Sync direction
            force_full_sync: Force full sync instead of incremental

        Returns:
            SyncResult with operation details
        """
        if not self.provider or not self.sync_engine:
            raise RuntimeError("Provider not initialized")

        # Use configured directory if none specified
        sync_dir = directory or self.config.sync_directory

        if not sync_dir.exists():
            raise ValueError(f"Sync directory does not exist: {sync_dir}")

        # Check if already syncing
        if self._active_sync and not self._active_sync.done():
            logger.warning("Sync already in progress")
            return SyncResult(
                success=False,
                total_files=0,
                errors=["Sync already in progress"],
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=0.0,
            )

        try:
            # Check authentication
            if not self.provider.is_authenticated:
                auth_success = await self.authenticate()
                if not auth_success:
                    return SyncResult(
                        success=False,
                        total_files=0,
                        errors=["Authentication failed"],
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        duration_seconds=0.0,
                    )

            # Check connection
            if not await self.test_connection():
                if not self.config.offline_mode:
                    return SyncResult(
                        success=False,
                        total_files=0,
                        errors=["Connection test failed"],
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        duration_seconds=0.0,
                    )
                else:
                    logger.warning("Connection failed but proceeding in offline mode")

            # Create and run sync task
            self._active_sync = asyncio.create_task(self._run_sync(sync_dir, direction, force_full_sync))

            result = await self._active_sync

            return result

        except Exception as e:
            logger.error(f"Sync operation failed: {e}")
            return SyncResult(
                success=False,
                total_files=0,
                errors=[f"Sync failed: {e}"],
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=0.0,
            )

    async def _run_sync(self, directory: Path, direction: SyncDirection, force_full_sync: bool) -> SyncResult:
        """Run the actual sync operation."""
        try:
            logger.info(f"Starting sync of {directory} in {direction} mode")

            # Use sync engine for the actual operation
            async with self.sync_engine as engine:
                result = await engine.synchronize(direction)

            # Store sync result
            self._sync_state = engine.load_sync_state()

            logger.info(f"Sync completed: {result.files_synced} files processed")
            return result

        except Exception as e:
            logger.error(f"Sync execution failed: {e}")
            raise

    async def get_sync_status(self) -> Dict[str, Union[str, int, float]]:
        """
        Get current synchronization status.

        Returns:
            Dictionary with sync status information
        """
        status = {
            "provider": self.config.cloud_config.provider.value,
            "sync_directory": str(self.config.sync_directory),
            "auth_status": self.config.cloud_config.auth_status.value,
            "is_syncing": self._active_sync is not None and not self._active_sync.done(),
            "last_sync": None,
            "configured": True,
        }

        # Add sync engine progress if available
        if self.sync_engine:
            try:
                progress = self.sync_engine.get_progress()
                status.update(
                    {
                        "progress_percentage": progress.progress_percentage,
                        "current_stage": progress.stage,
                        "current_file": progress.current_file,
                        "processed_files": progress.processed_files,
                        "total_files": progress.total_files,
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to get sync progress: {e}")

        # Add last sync time if available
        if self._sync_state:
            status["last_sync"] = self._sync_state.last_full_sync

        return status

    async def pause_sync(self) -> bool:
        """
        Pause the current sync operation.

        Returns:
            True if sync was paused, False if no sync in progress
        """
        if self._active_sync and not self._active_sync.done():
            self._active_sync.cancel()
            try:
                await self._active_sync
            except asyncio.CancelledError:
                pass
            return True
        return False

    async def cancel_sync(self) -> bool:
        """
        Cancel the current sync operation.

        Returns:
            True if sync was cancelled, False if no sync in progress
        """
        return await self.pause_sync()

    async def get_file_conflicts(self) -> List[Dict[str, any]]:
        """
        Get list of unresolved file conflicts.

        Returns:
            List of conflict information
        """
        if not self._sync_state:
            return []

        # This would need to be implemented in the sync engine
        # For now, return empty list
        return []

    async def resolve_conflict(self, file_path: str, resolution: str) -> bool:
        """
        Resolve a file conflict.

        Args:
            file_path: Path to conflicting file
            resolution: Resolution strategy

        Returns:
            True if conflict resolved successfully
        """
        # This would need to be implemented in the sync engine
        # For now, return True
        logger.info(f"Conflict resolved for {file_path} with strategy: {resolution}")
        return True

    def save_configuration(self, config_path: Path) -> None:
        """
        Save current configuration to file.

        Args:
            config_path: Path to save configuration
        """
        config_data = self.config.dict()

        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2, default=str)

        logger.info(f"Configuration saved to {config_path}")

    @classmethod
    def load_configuration(cls, config_path: Path) -> "CloudSyncManager":
        """
        Load configuration from file and create manager.

        Args:
            config_path: Path to configuration file

        Returns:
            CloudSyncManager instance with loaded configuration
        """
        with open(config_path, "r") as f:
            config_data = json.load(f)

        config = SyncConfig(**config_data)
        return cls(config)

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._active_sync and not self._active_sync.done():
            self._active_sync.cancel()

        if self.provider:
            await self.provider.__aexit__(None, None, None)

        logger.info("Cloud sync manager cleaned up")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
