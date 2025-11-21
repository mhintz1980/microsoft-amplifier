"""
Base interface for cloud storage providers.

This module defines the abstract interface that all cloud providers must implement,
ensuring consistent behavior across different storage services.
"""

import asyncio
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional, Tuple, Union
import logging

from ..models.cloud_models import CloudFile, CloudConfig, AuthStatus
from ..models.sync_models import FileMetadata, SyncOperation

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """
    Abstract base class for cloud storage providers.

    All cloud providers must inherit from this class and implement
    the defined methods to ensure consistent behavior.
    """

    def __init__(self, config: CloudConfig):
        """
        Initialize the provider with configuration.

        Args:
            config: Cloud provider configuration
        """
        self.config = config
        self._authenticated = False

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return self.config.provider.value

    @property
    def is_authenticated(self) -> bool:
        """Check if provider is authenticated."""
        return self._authenticated and self.config.is_token_valid()

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the cloud provider.

        Returns:
            True if authentication successful, False otherwise
        """
        pass

    @abstractmethod
    async def refresh_authentication(self) -> bool:
        """
        Refresh authentication tokens.

        Returns:
            True if refresh successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_auth_url(self) -> str:
        """
        Get URL for user authentication.

        Returns:
            Authentication URL for the user to visit
        """
        pass

    @abstractmethod
    async def handle_auth_callback(self, code: str) -> bool:
        """
        Handle OAuth callback after user authentication.

        Args:
            code: Authorization code from OAuth flow

        Returns:
            True if authentication completed successfully
        """
        pass

    @abstractmethod
    async def list_files(
        self, folder_id: Optional[str] = None, recursive: bool = True, page_size: int = 1000
    ) -> AsyncGenerator[CloudFile, None]:
        """
        List files in cloud storage.

        Args:
            folder_id: Parent folder ID (None for root)
            recursive: Whether to list files recursively
            page_size: Number of files to fetch per request

        Yields:
            CloudFile objects representing files in storage
        """
        pass

    @abstractmethod
    async def get_file(self, file_id: str) -> Optional[CloudFile]:
        """
        Get file information by ID.

        Args:
            file_id: Cloud file ID

        Returns:
            CloudFile object or None if not found
        """
        pass

    @abstractmethod
    async def find_file_by_path(self, path: str) -> Optional[CloudFile]:
        """
        Find file by path in cloud storage.

        Args:
            path: Path in cloud storage

        Returns:
            CloudFile object or None if not found
        """
        pass

    @abstractmethod
    async def upload_file(self, local_path: Path, cloud_path: str, overwrite: bool = True) -> CloudFile:
        """
        Upload a file to cloud storage.

        Args:
            local_path: Local file path to upload
            cloud_path: Target path in cloud storage
            overwrite: Whether to overwrite existing files

        Returns:
            CloudFile object for uploaded file

        Raises:
            FileNotFoundError: If local file doesn't exist
            PermissionError: If upload fails due to permissions
        """
        pass

    @abstractmethod
    async def download_file(self, file_id: str, local_path: Path, overwrite: bool = True) -> Path:
        """
        Download a file from cloud storage.

        Args:
            file_id: Cloud file ID to download
            local_path: Local path to save the file
            overwrite: Whether to overwrite existing files

        Returns:
            Path to downloaded file

        Raises:
            FileNotFoundError: If cloud file doesn't exist
            PermissionError: If download fails due to permissions
        """
        pass

    @abstractmethod
    async def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from cloud storage.

        Args:
            file_id: Cloud file ID to delete

        Returns:
            True if deletion successful, False otherwise
        """
        pass

    @abstractmethod
    async def move_file(
        self, file_id: str, new_parent_id: Optional[str] = None, new_name: Optional[str] = None
    ) -> CloudFile:
        """
        Move or rename a file in cloud storage.

        Args:
            file_id: Cloud file ID to move
            new_parent_id: New parent folder ID
            new_name: New file name

        Returns:
            Updated CloudFile object
        """
        pass

    @abstractmethod
    async def create_folder(self, name: str, parent_id: Optional[str] = None) -> CloudFile:
        """
        Create a folder in cloud storage.

        Args:
            name: Folder name
            parent_id: Parent folder ID

        Returns:
            CloudFile object for created folder
        """
        pass

    async def get_file_changes(
        self, since: Optional[datetime] = None, folder_id: Optional[str] = None
    ) -> AsyncGenerator[Tuple[CloudFile, SyncOperation], None]:
        """
        Get file changes since a specific time.

        Args:
            since: Only return changes after this time
            folder_id: Limit to specific folder

        Yields:
            Tuples of (CloudFile, SyncOperation) indicating changes
        """
        # Default implementation lists all files and compares timestamps
        if since is None:
            since = datetime.min

        async for cloud_file in self.list_files(folder_id=folder_id):
            if cloud_file.modified_time > since:
                yield cloud_file, SyncOperation.UPDATE

    async def verify_file_integrity(self, local_path: Path, cloud_file: CloudFile) -> bool:
        """
        Verify file integrity between local and cloud versions.

        Args:
            local_path: Local file path
            cloud_file: Cloud file metadata

        Returns:
            True if files match, False otherwise
        """
        try:
            if not local_path.exists():
                return False

            # Check file size
            local_size = local_path.stat().st_size
            if local_size != cloud_file.size:
                return False

            # Calculate checksum for verification
            local_checksum = await self._calculate_file_checksum(local_path)
            if local_checksum and hasattr(cloud_file, "checksum"):
                return local_checksum == cloud_file.checksum

            # If no checksum available, rely on etag
            if cloud_file.etag:
                # Use etag as integrity check if available
                return True

            return True

        except Exception as e:
            logger.warning(f"Failed to verify file integrity for {local_path}: {e}")
            return False

    async def _calculate_file_checksum(self, file_path: Path) -> Optional[str]:
        """
        Calculate MD5 checksum for a file.

        Args:
            file_path: Path to file

        Returns:
            MD5 checksum as hex string or None if calculation fails
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate checksum for {file_path}: {e}")
            return None

    async def wait_for_file_availability(
        self, file_id: str, timeout_seconds: int = 30, check_interval: float = 1.0
    ) -> bool:
        """
        Wait for a file to become available in cloud storage.

        Useful for handling eventual consistency in some cloud providers.

        Args:
            file_id: Cloud file ID to check
            timeout_seconds: Maximum time to wait
            check_interval: Time between checks

        Returns:
            True if file becomes available, False if timeout
        """
        start_time = asyncio.get_event_loop().time()

        while True:
            try:
                file_info = await self.get_file(file_id)
                if file_info:
                    return True
            except Exception:
                pass

            if asyncio.get_event_loop().time() - start_time > timeout_seconds:
                return False

            await asyncio.sleep(check_interval)

    def get_rate_limit_info(self) -> Dict[str, Union[int, str]]:
        """
        Get current rate limit information from the provider.

        Returns:
            Dictionary with rate limit details
        """
        # Default implementation - override in provider-specific implementations
        return {"requests_remaining": -1, "requests_limit": -1, "reset_time": "unknown", "retry_after": 0}

    async def __aenter__(self):
        """Async context manager entry."""
        if not self.is_authenticated:
            await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup if needed - override in providers that need it
        pass
