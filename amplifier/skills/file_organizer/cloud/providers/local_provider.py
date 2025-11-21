"""
Local provider for testing and offline mode.

This provider uses local filesystem to simulate cloud storage,
useful for testing and offline functionality.
"""

import asyncio
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional, Tuple
import logging

from .base_provider import BaseProvider
from ..models.cloud_models import CloudFile, CloudConfig, AuthStatus, CloudProvider
from ..models.sync_models import FileMetadata, SyncOperation

logger = logging.getLogger(__name__)


class LocalProvider(BaseProvider):
    """
    Local filesystem provider that simulates cloud storage.

    Uses a local directory to store "cloud" files for testing purposes
    and offline functionality.
    """

    def __init__(self, config: CloudConfig, storage_root: Optional[Path] = None):
        """
        Initialize local provider.

        Args:
            config: Cloud configuration (ignored for local provider)
            storage_root: Root directory for cloud simulation
        """
        # Create a default config for local provider
        local_config = CloudConfig(provider=CloudProvider.LOCAL)
        super().__init__(local_config)

        self.storage_root = storage_root or Path.home() / ".local_cloud_storage"
        self.storage_root.mkdir(parents=True, exist_ok=True)

        # Create metadata directory
        self.metadata_dir = self.storage_root / ".metadata"
        self.metadata_dir.mkdir(exist_ok=True)

        # Initialize authentication
        self._authenticated = True

        logger.info(f"Local provider initialized with storage root: {self.storage_root}")

    async def authenticate(self) -> bool:
        """Local provider is always authenticated."""
        self._authenticated = True
        return True

    async def refresh_authentication(self) -> bool:
        """No authentication to refresh for local provider."""
        return True

    async def get_auth_url(self) -> str:
        """Local provider doesn't need authentication."""
        return "local://authenticated"

    async def handle_auth_callback(self, code: str) -> bool:
        """Local provider doesn't need OAuth callback."""
        return True

    def _get_file_path(self, cloud_path: str) -> Path:
        """Convert cloud path to local storage path."""
        # Remove leading slash and normalize
        normalized_path = cloud_path.lstrip("/")
        return self.storage_root / normalized_path

    def _get_metadata_path(self, file_path: Path) -> Path:
        """Get metadata file path for a cloud file."""
        relative_path = file_path.relative_to(self.storage_root)
        return self.metadata_dir / f"{relative_path}.json"

    def _load_file_metadata(self, file_path: Path) -> Optional[Dict]:
        """Load metadata for a cloud file."""
        metadata_path = self._get_metadata_path(file_path)
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                return json.load(f)
        return None

    def _save_file_metadata(self, file_path: Path, metadata: Dict) -> None:
        """Save metadata for a cloud file."""
        metadata_path = self._get_metadata_path(file_path)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

    async def list_files(
        self, folder_id: Optional[str] = None, recursive: bool = True, page_size: int = 1000
    ) -> AsyncGenerator[CloudFile, None]:
        """List files in local cloud storage."""
        base_path = self._get_file_path(folder_id or "")

        if not base_path.exists():
            return

        if base_path.is_file():
            # If folder_id points to a file, return that file
            yield await self._path_to_cloud_file(base_path)
            return

        pattern = "**/*" if recursive else "*"
        count = 0

        for path in base_path.glob(pattern):
            if count >= page_size:
                break

            # Skip metadata directory
            if path.is_relative_to(self.metadata_dir):
                continue

            cloud_file = await self._path_to_cloud_file(path)
            if cloud_file:
                yield cloud_file
                count += 1

    async def get_file(self, file_id: str) -> Optional[CloudFile]:
        """Get file information by ID (path for local provider)."""
        file_path = self._get_file_path(file_id)
        if file_path.exists():
            return await self._path_to_cloud_file(file_path)
        return None

    async def find_file_by_path(self, path: str) -> Optional[CloudFile]:
        """Find file by path in local storage."""
        file_path = self._get_file_path(path)
        if file_path.exists():
            return await self._path_to_cloud_file(file_path)
        return None

    async def _path_to_cloud_file(self, file_path: Path) -> Optional[CloudFile]:
        """Convert local path to CloudFile object."""
        try:
            if not file_path.exists():
                return None

            stat = file_path.stat()
            relative_path = file_path.relative_to(self.storage_root)
            cloud_path = str(relative_path).replace("\\", "/")

            # Load metadata if available
            metadata = self._load_file_metadata(file_path)
            cloud_id = metadata.get("cloud_id") if metadata else cloud_path
            etag = metadata.get("etag") if metadata else None

            return CloudFile(
                id=cloud_id,
                name=file_path.name,
                path=cloud_path,
                size=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                etag=etag,
                mime_type=self._get_mime_type(file_path),
                parent_id=str(relative_path.parent) if relative_path.parent != Path(".") else None,
                is_folder=file_path.is_dir(),
            )
        except Exception as e:
            logger.warning(f"Failed to convert path to CloudFile {file_path}: {e}")
            return None

    def _get_mime_type(self, file_path: Path) -> Optional[str]:
        """Get MIME type for a file."""
        import mimetypes

        if file_path.is_dir():
            return "application/vnd.google-apps.folder"

        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type

    async def upload_file(self, local_path: Path, cloud_path: str, overwrite: bool = True) -> CloudFile:
        """Upload a file to local cloud storage."""
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        target_path = self._get_file_path(cloud_path)

        # Check if file exists and overwrite is False
        if target_path.exists() and not overwrite:
            raise FileExistsError(f"Target file exists and overwrite=False: {cloud_path}")

        # Create parent directories
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file
        shutil.copy2(local_path, target_path)

        # Create metadata
        cloud_id = cloud_path
        etag = f"etag_{datetime.now().timestamp()}"

        metadata = {
            "cloud_id": cloud_id,
            "etag": etag,
            "upload_time": datetime.now().isoformat(),
            "original_path": str(local_path),
        }
        self._save_file_metadata(target_path, metadata)

        # Return CloudFile object
        return await self._path_to_cloud_file(target_path)

    async def download_file(self, file_id: str, local_path: Path, overwrite: bool = True) -> Path:
        """Download a file from local cloud storage."""
        cloud_path = self._get_file_path(file_id)

        if not cloud_path.exists():
            raise FileNotFoundError(f"Cloud file not found: {file_id}")

        # Check if local file exists and overwrite is False
        if local_path.exists() and not overwrite:
            raise FileExistsError(f"Local file exists and overwrite=False: {local_path}")

        # Create parent directories
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file
        shutil.copy2(cloud_path, local_path)

        logger.info(f"Downloaded {file_id} to {local_path}")
        return local_path

    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from local cloud storage."""
        cloud_path = self._get_file_path(file_id)

        try:
            if cloud_path.is_dir():
                shutil.rmtree(cloud_path)
            else:
                cloud_path.unlink()

            # Remove metadata
            metadata_path = self._get_metadata_path(cloud_path)
            if metadata_path.exists():
                metadata_path.unlink()

            logger.info(f"Deleted {file_id} from local cloud storage")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {file_id}: {e}")
            return False

    async def move_file(
        self, file_id: str, new_parent_id: Optional[str] = None, new_name: Optional[str] = None
    ) -> CloudFile:
        """Move or rename a file in local cloud storage."""
        old_path = self._get_file_path(file_id)

        if not old_path.exists():
            raise FileNotFoundError(f"File not found: {file_id}")

        # Determine new path
        if new_parent_id:
            parent_path = self._get_file_path(new_parent_id)
        else:
            parent_path = old_path.parent

        if new_name:
            new_path = parent_path / new_name
        else:
            new_path = parent_path / old_path.name

        # Create parent directories if needed
        new_path.parent.mkdir(parents=True, exist_ok=True)

        # Move the file
        shutil.move(str(old_path), str(new_path))

        # Update metadata
        metadata = self._load_file_metadata(new_path) or {}
        metadata["moved_time"] = datetime.now().isoformat()
        self._save_file_metadata(new_path, metadata)

        # Return updated CloudFile
        return await self._path_to_cloud_file(new_path)

    async def create_folder(self, name: str, parent_id: Optional[str] = None) -> CloudFile:
        """Create a folder in local cloud storage."""
        if parent_id:
            parent_path = self._get_file_path(parent_id)
        else:
            parent_path = self.storage_root

        folder_path = parent_path / name
        folder_path.mkdir(parents=True, exist_ok=True)

        # Create metadata
        metadata = {
            "cloud_id": str(folder_path.relative_to(self.storage_root)).replace("\\", "/"),
            "created_time": datetime.now().isoformat(),
            "is_folder": True,
        }
        self._save_file_metadata(folder_path, metadata)

        return await self._path_to_cloud_file(folder_path)

    async def get_file_changes(
        self, since: Optional[datetime] = None, folder_id: Optional[str] = None
    ) -> AsyncGenerator[Tuple[CloudFile, SyncOperation], None]:
        """Get file changes since a specific time."""
        if since is None:
            since = datetime.min

        async for cloud_file in self.list_files(folder_id=folder_id):
            if cloud_file.modified_time > since:
                yield cloud_file, SyncOperation.UPDATE

    async def verify_file_integrity(self, local_path: Path, cloud_file: CloudFile) -> bool:
        """Verify file integrity between local and cloud versions."""
        try:
            cloud_path = self._get_file_path(cloud_file.path)

            if not local_path.exists() or not cloud_path.exists():
                return False

            # Compare file sizes
            local_size = local_path.stat().st_size
            cloud_size = cloud_path.stat().st_size

            if local_size != cloud_size:
                return False

            # Compare modification times (within 1 second tolerance)
            local_mtime = datetime.fromtimestamp(local_path.stat().st_mtime)
            cloud_mtime = cloud_file.modified_time

            time_diff = abs((local_mtime - cloud_mtime).total_seconds())
            if time_diff > 1.0:
                return False

            return True

        except Exception as e:
            logger.warning(f"Failed to verify file integrity: {e}")
            return False

    def get_rate_limit_info(self) -> Dict[str, int]:
        """Local provider has no rate limits."""
        return {"requests_remaining": -1, "requests_limit": -1, "reset_time": "unlimited", "retry_after": 0}
