"""
Cloud-Enhanced File Organizer

Integrates cloud synchronization with the existing file organizer functionality.
Combines Phase 1-2 features with Phase 3 cloud sync capabilities.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from .enhanced_file_organizer import EnhancedFileOrganizer
from .config import FileOrganizerConfig
from ..models.file_models import OrganizationResult, FileInfo
from ..cloud import CloudSyncManager, SyncConfig, CloudConfig, CloudProvider, SyncDirection
from ..cloud.models.cloud_models import ConflictResolution
from ..cloud.models.sync_models import SyncResult

logger = logging.getLogger(__name__)


class CloudEnhancedFileOrganizer:
    """
    File organizer with integrated cloud synchronization.

    Combines the enhanced file organization capabilities with cloud sync
    functionality to provide seamless multi-device file management.
    """

    def __init__(
        self,
        config: Optional[FileOrganizerConfig] = None,
        sync_config: Optional[SyncConfig] = None,
        enable_ml: bool = True,
        confidence_threshold: float = 0.7,
    ):
        """
        Initialize the cloud-enhanced file organizer.

        Args:
            config: File organizer configuration
            sync_config: Cloud sync configuration
            enable_ml: Enable ML-powered categorization
            confidence_threshold: ML confidence threshold
        """
        # Initialize core file organizer
        self.config = config or FileOrganizerConfig()
        self.core_organizer = EnhancedFileOrganizer(
            config=self.config, enable_ml=enable_ml, confidence_threshold=confidence_threshold
        )

        # Initialize cloud sync manager
        self.sync_config = sync_config or SyncConfig(
            sync_directory=Path.home() / "OrganizedFiles",
            cloud_config=CloudConfig(provider=CloudProvider.LOCAL),
        )
        self.sync_manager = CloudSyncManager(self.sync_config)

        # Integration settings
        self.auto_sync_after_organize: bool = True
        self.sync_before_organize: bool = False
        self.conflict_resolution: ConflictResolution = ConflictResolution.LAST_WRITE_WINS

        logger.info("Cloud-enhanced file organizer initialized")

    async def organize_directory(
        self, directory_path: Path, sync_after: Optional[bool] = None, sync_before: Optional[bool] = None, **kwargs
    ) -> OrganizationResult:
        """
        Organize a directory with optional cloud synchronization.

        Args:
            directory_path: Directory to organize
            sync_after: Whether to sync after organization (uses default if None)
            sync_before: Whether to sync before organization (uses default if None)
            **kwargs: Additional arguments for organization

        Returns:
            OrganizationResult with sync information added
        """
        try:
            logger.info(f"Starting cloud-enhanced organization of {directory_path}")

            # Determine sync behavior
            should_sync_before = sync_before if sync_before is not None else self.sync_before_organize
            should_sync_after = sync_after if sync_after is not None else self.auto_sync_after_organize

            # Pre-organization sync if requested
            sync_result = None
            if should_sync_before:
                logger.info("Performing pre-organization sync...")
                sync_result = await self.sync_manager.sync_directory(directory_path, SyncDirection.DOWNLOAD)

            # Perform organization
            logger.info("Performing file organization...")
            org_result = await self.core_organizer.organize_directory(directory_path, **kwargs)

            # Add sync information to organization result
            if sync_result:
                org_result.errors.extend([f"Pre-sync: {error}" for error in sync_result.errors])
                org_result.warnings = getattr(org_result, "warnings", [])
                org_result.warnings.extend([f"Pre-sync: {warning}" for warning in sync_result.warnings])

            # Post-organization sync if requested
            if should_sync_after:
                logger.info("Performing post-organization sync...")
                post_sync_result = await self.sync_manager.sync_directory(directory_path, SyncDirection.UPLOAD)

                # Add post-sync information
                org_result.errors.extend([f"Post-sync: {error}" for error in post_sync_result.errors])
                if not hasattr(org_result, "warnings"):
                    org_result.warnings = []
                org_result.warnings.extend([f"Post-sync: {warning}" for warning in post_sync_result.warnings])

                # Add sync metadata to result
                org_result.__dict__["sync_info"] = {
                    "pre_sync": {
                        "files_synced": sync_result.files_synced if sync_result else 0,
                        "success": sync_result.success if sync_result else True,
                        "duration": sync_result.duration_seconds if sync_result else 0.0,
                    },
                    "post_sync": {
                        "files_synced": post_sync_result.files_synced,
                        "success": post_sync_result.success,
                        "duration": post_sync_result.duration_seconds,
                    },
                }

            logger.info(f"Cloud-enhanced organization completed: {org_result.organized_files} files organized")
            return org_result

        except Exception as e:
            logger.error(f"Cloud-enhanced organization failed: {e}")
            # Return failed organization result
            return OrganizationResult(
                success=False,
                total_files=0,
                organized_files=0,
                failed_files=0,
                skipped_files=0,
                errors=[f"Organization failed: {e}"],
                organized_paths=[],
                duration_seconds=0.0,
            )

    async def sync_directory_only(
        self, directory_path: Path, direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    ) -> SyncResult:
        """
        Perform only synchronization without organization.

        Args:
            directory_path: Directory to sync
            direction: Sync direction

        Returns:
            SyncResult with sync operation details
        """
        return await self.sync_manager.sync_directory(directory_path, direction)

    async def get_sync_status(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get comprehensive sync and organization status.

        Returns:
            Dictionary with combined status information
        """
        sync_status = await self.sync_manager.get_sync_status()

        # Add organization-specific information
        combined_status = {
            **sync_status,
            "auto_sync_after_organize": self.auto_sync_after_organize,
            "sync_before_organize": self.sync_before_organize,
            "conflict_resolution": self.conflict_resolution.value,
            "ml_enabled": self.core_organizer.enable_ml,
            "confidence_threshold": self.core_organizer.confidence_threshold,
        }

        return combined_status

    async def configure_cloud_sync(self, provider: CloudProvider, sync_directory: Path, **provider_kwargs) -> bool:
        """
        Configure cloud synchronization settings.

        Args:
            provider: Cloud provider to use
            sync_directory: Directory to synchronize
            **provider_kwargs: Provider-specific configuration

        Returns:
            True if configuration successful
        """
        try:
            # Create new cloud config
            cloud_config = CloudConfig(provider=provider, **provider_kwargs)

            # Create new sync config
            self.sync_config = SyncConfig(sync_directory=sync_directory, cloud_config=cloud_config)

            # Reinitialize sync manager
            self.sync_manager = CloudSyncManager(self.sync_config)

            logger.info(f"Cloud sync configured for {provider} at {sync_directory}")
            return True

        except Exception as e:
            logger.error(f"Failed to configure cloud sync: {e}")
            return False

    async def authenticate_cloud_provider(self, force_reauth: bool = False) -> bool:
        """
        Authenticate with the configured cloud provider.

        Args:
            force_reauth: Force re-authentication

        Returns:
            True if authentication successful
        """
        return await self.sync_manager.authenticate(force_reauth)

    async def get_authentication_url(self) -> Optional[str]:
        """
        Get authentication URL for OAuth providers.

        Returns:
            Authentication URL or None
        """
        return await self.sync_manager.get_authentication_url()

    async def handle_authentication_callback(self, code: str) -> bool:
        """
        Handle OAuth authentication callback.

        Args:
            code: Authorization code

        Returns:
            True if callback handled successfully
        """
        return await self.sync_manager.handle_authentication_callback(code)

    def set_sync_behavior(
        self,
        auto_sync_after: bool = True,
        sync_before: bool = False,
        conflict_resolution: ConflictResolution = ConflictResolution.LAST_WRITE_WINS,
    ) -> None:
        """
        Configure sync behavior around organization operations.

        Args:
            auto_sync_after: Enable automatic sync after organization
            sync_before: Enable sync before organization
            conflict_resolution: Default conflict resolution strategy
        """
        self.auto_sync_after_organize = auto_sync_after
        self.sync_before_organize = sync_before
        self.conflict_resolution = conflict_resolution

        logger.info(
            f"Sync behavior updated: after={auto_sync_after}, before={sync_before}, resolution={conflict_resolution}"
        )

    async def resolve_sync_conflicts(self) -> int:
        """
        Resolve any pending synchronization conflicts.

        Returns:
            Number of conflicts resolved
        """
        conflicts = await self.sync_manager.get_file_conflicts()
        resolved_count = 0

        for conflict in conflicts:
            file_path = conflict.get("path", "")
            if await self.sync_manager.resolve_conflict(file_path, self.conflict_resolution.value):
                resolved_count += 1

        logger.info(f"Resolved {resolved_count} sync conflicts")
        return resolved_count

    def save_configuration(self, config_path: Path) -> None:
        """
        Save complete configuration to file.

        Args:
            config_path: Path to save configuration
        """
        import json

        config_data = {
            "file_organizer": self.config.dict(),
            "cloud_sync": self.sync_config.dict(),
            "integration": {
                "auto_sync_after_organize": self.auto_sync_after_organize,
                "sync_before_organize": self.sync_before_organize,
                "conflict_resolution": self.conflict_resolution.value,
            },
            "ml": {
                "enabled": self.core_organizer.enable_ml,
                "confidence_threshold": self.core_organizer.confidence_threshold,
            },
        }

        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2, default=str)

        logger.info(f"Configuration saved to {config_path}")

    @classmethod
    def load_configuration(cls, config_path: Path) -> "CloudEnhancedFileOrganizer":
        """
        Load configuration from file and create organizer.

        Args:
            config_path: Path to configuration file

        Returns:
            CloudEnhancedFileOrganizer instance with loaded configuration
        """
        import json

        with open(config_path, "r") as f:
            config_data = json.load(f)

        # Load configurations
        file_config = FileOrganizerConfig(**config_data["file_organizer"])
        sync_config = SyncConfig(**config_data["cloud_sync"])

        # Create organizer
        organizer = cls(
            config=file_config,
            sync_config=sync_config,
            enable_ml=config_data["ml"]["enabled"],
            confidence_threshold=config_data["ml"]["confidence_threshold"],
        )

        # Set integration behavior
        integration = config_data["integration"]
        organizer.set_sync_behavior(
            auto_sync_after=integration["auto_sync_after_organize"],
            sync_before=integration["sync_before_organize"],
            conflict_resolution=ConflictResolution(integration["conflict_resolution"]),
        )

        return organizer

    async def cleanup(self) -> None:
        """Clean up resources."""
        await self.sync_manager.cleanup()
        logger.info("Cloud-enhanced file organizer cleaned up")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
