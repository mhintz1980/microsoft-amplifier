"""
Tests for cloud synchronization functionality.

This test suite validates:
- Local provider functionality
- Sync engine operations
- Cloud sync manager orchestration
- Conflict resolution
- Integration with file organizer
"""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
import pytest
import shutil

from ..cloud import CloudSyncManager, SyncConfig, CloudConfig, CloudProvider, SyncDirection
from ..cloud.providers.local_provider import LocalProvider
from ..cloud.models.sync_models import SyncStatus, ConflictResolution
from ..core.cloud_enhanced_organizer import CloudEnhancedFileOrganizer


class TestLocalProvider:
    """Test the local provider implementation."""

    @pytest.fixture
    async def temp_provider(self):
        """Create a temporary local provider."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_root = Path(temp_dir) / "cloud_storage"
            config = CloudConfig(provider=CloudProvider.LOCAL)
            provider = LocalProvider(config, storage_root)
            yield provider

    @pytest.mark.asyncio
    async def test_provider_authentication(self, temp_provider):
        """Test provider authentication."""
        assert await temp_provider.authenticate() is True
        assert temp_provider.is_authenticated is True

    @pytest.mark.asyncio
    async def test_file_upload_download(self, temp_provider):
        """Test file upload and download operations."""
        # Create test file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Test content for cloud sync")
            test_file = Path(f.name)

        try:
            # Upload file
            cloud_file = await temp_provider.upload_file(test_file, "test_file.txt")
            assert cloud_file.name == "test_file.txt"
            assert cloud_file.size > 0

            # Download file
            download_path = test_file.parent / "downloaded_file.txt"
            await temp_provider.download_file(cloud_file.id, download_path)

            # Verify content
            assert download_path.exists()
            assert download_path.read_text() == "Test content for cloud sync"

        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()
            download_path = test_file.parent / "downloaded_file.txt"
            if download_path.exists():
                download_path.unlink()

    @pytest.mark.asyncio
    async def test_file_listing(self, temp_provider):
        """Test file listing functionality."""
        # Create test files
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f1:
            f1.write("Content 1")
            test_file1 = Path(f1.name)

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f2:
            f2.write("Content 2")
            test_file2 = Path(f2.name)

        try:
            # Upload files
            await temp_provider.upload_file(test_file1, "folder1/file1.txt")
            await temp_provider.upload_file(test_file2, "folder2/file2.txt")

            # List files
            files = []
            async for cloud_file in temp_provider.list_files(recursive=True):
                files.append(cloud_file)

            assert len(files) >= 2
            file_names = [f.name for f in files]
            assert "file1.txt" in file_names
            assert "file2.txt" in file_names

        finally:
            # Cleanup
            for f in [test_file1, test_file2]:
                if f.exists():
                    f.unlink()


class TestCloudSyncManager:
    """Test the cloud sync manager."""

    @pytest.fixture
    async def temp_sync_manager(self):
        """Create a temporary sync manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            sync_dir = Path(temp_dir) / "sync"
            sync_dir.mkdir()

            config = SyncConfig(sync_directory=sync_dir, cloud_config=CloudConfig(provider=CloudProvider.LOCAL))
            manager = CloudSyncManager(config)
            yield manager

    @pytest.mark.asyncio
    async def test_sync_manager_initialization(self, temp_sync_manager):
        """Test sync manager initialization."""
        assert temp_sync_manager.provider is not None
        assert temp_sync_manager.config.cloud_config.provider == CloudProvider.LOCAL

    @pytest.mark.asyncio
    async def test_authentication(self, temp_sync_manager):
        """Test authentication with cloud provider."""
        assert await temp_sync_manager.authenticate() is True
        assert temp_sync_manager.config.cloud_config.auth_status.value == "authenticated"

    @pytest.mark.asyncio
    async def test_connection_test(self, temp_sync_manager):
        """Test connection to cloud provider."""
        assert await temp_sync_manager.test_connection() is True

    @pytest.mark.asyncio
    async def test_sync_empty_directory(self, temp_sync_manager):
        """Test syncing an empty directory."""
        result = await temp_sync_manager.sync_directory()
        assert result.success is True
        assert result.total_files == 0
        assert result.files_synced == 0

    @pytest.mark.asyncio
    async def test_sync_with_files(self, temp_sync_manager):
        """Test syncing directory with files."""
        sync_dir = temp_sync_manager.config.sync_directory

        # Create test files
        test_files = []
        for i in range(3):
            test_file = sync_dir / f"test_file_{i}.txt"
            test_file.write_text(f"Test content {i}")
            test_files.append(test_file)

        try:
            # Perform sync
            result = await temp_sync_manager.sync_directory()
            assert result.success is True
            assert result.total_files >= 3

            # Get sync status
            status = await temp_sync_manager.get_sync_status()
            assert status["is_syncing"] is False
            assert status["auth_status"] == "authenticated"

        finally:
            # Cleanup
            for test_file in test_files:
                if test_file.exists():
                    test_file.unlink()


class TestCloudEnhancedOrganizer:
    """Test the cloud-enhanced file organizer."""

    @pytest.fixture
    async def temp_organizer(self):
        """Create a temporary cloud-enhanced organizer."""
        with tempfile.TemporaryDirectory() as temp_dir:
            sync_dir = Path(temp_dir) / "sync"
            sync_dir.mkdir()

            # Create sync config with local provider
            sync_config = SyncConfig(sync_directory=sync_dir, cloud_config=CloudConfig(provider=CloudProvider.LOCAL))

            organizer = CloudEnhancedFileOrganizer(
                sync_config=sync_config,
                enable_ml=False,  # Disable ML for simpler testing
            )
            yield organizer

    @pytest.mark.asyncio
    async def test_organizer_initialization(self, temp_organizer):
        """Test organizer initialization."""
        assert temp_organizer.sync_manager is not None
        assert temp_organizer.core_organizer is not None
        assert temp_organizer.auto_sync_after_organize is True

    @pytest.mark.asyncio
    async def test_organize_with_sync(self, temp_organizer):
        """Test file organization with cloud sync."""
        # Create test directory with files
        test_dir = temp_organizer.sync_config.sync_directory
        test_files = []

        # Create test files of different types
        (test_dir / "test_document.pdf").write_text("PDF content")
        (test_dir / "test_image.jpg").write_text("JPG content")
        (test_dir / "test_code.py").write_text("Python code")

        try:
            # Configure organization to not actually move files (dry run)
            temp_organizer.config.dry_run = True

            # Perform organization with sync
            result = await temp_organizer.organize_directory(test_dir)

            assert result.success is True
            assert hasattr(result, "sync_info")

        finally:
            # Cleanup
            for test_file in test_files:
                if test_file.exists():
                    test_file.unlink()

    @pytest.mark.asyncio
    async def test_sync_configuration(self, temp_organizer):
        """Test cloud sync configuration."""
        # Configure with different settings
        with tempfile.TemporaryDirectory() as temp_dir:
            new_sync_dir = Path(temp_dir) / "new_sync"
            new_sync_dir.mkdir()

            success = await temp_organizer.configure_cloud_sync(
                provider=CloudProvider.LOCAL, sync_directory=new_sync_dir
            )

            assert success is True
            assert temp_organizer.sync_config.sync_directory == new_sync_dir

    def test_sync_behavior_configuration(self, temp_organizer):
        """Test sync behavior configuration."""
        # Configure sync behavior
        temp_organizer.set_sync_behavior(
            auto_sync_after=False, sync_before=True, conflict_resolution=ConflictResolution.LOCAL_WINS
        )

        assert temp_organizer.auto_sync_after_organize is False
        assert temp_organizer.sync_before_organize is True
        assert temp_organizer.conflict_resolution == ConflictResolution.LOCAL_WINS


class TestIntegration:
    """Integration tests for the complete cloud sync system."""

    @pytest.mark.asyncio
    async def test_end_to_end_sync_workflow(self):
        """Test complete end-to-end sync workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup
            source_dir = Path(temp_dir) / "source"
            source_dir.mkdir()

            sync_config = SyncConfig(sync_directory=source_dir, cloud_config=CloudConfig(provider=CloudProvider.LOCAL))

            manager = CloudSyncManager(sync_config)

            # Create test files
            test_file1 = source_dir / "document1.txt"
            test_file1.write_text("This is document 1")

            test_file2 = source_dir / "document2.txt"
            test_file2.write_text("This is document 2")

            try:
                # Authenticate
                assert await manager.authenticate() is True

                # Upload files
                result = await manager.sync_directory(direction=SyncDirection.UPLOAD)
                assert result.success is True
                assert result.files_uploaded >= 2

                # Remove local file and download
                test_file1.unlink()
                assert not test_file1.exists()

                result = await manager.sync_directory(direction=SyncDirection.DOWNLOAD)
                assert result.success is True
                assert result.files_downloaded >= 1
                assert test_file1.exists()

            finally:
                # Cleanup
                if test_file1.exists():
                    test_file1.unlink()
                if test_file2.exists():
                    test_file2.unlink()

    @pytest.mark.asyncio
    async def test_conflict_resolution(self):
        """Test conflict resolution scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup
            sync_dir = Path(temp_dir) / "sync"
            sync_dir.mkdir()

            sync_config = SyncConfig(sync_directory=sync_dir, cloud_config=CloudConfig(provider=CloudProvider.LOCAL))

            manager = CloudSyncManager(sync_config)
            await manager.authenticate()

            # Create local file
            test_file = sync_dir / "conflict_test.txt"
            test_file.write_text("Local version")

            try:
                # Upload local version
                await manager.sync_directory(direction=SyncDirection.UPLOAD)

                # Simulate remote modification by directly modifying in cloud storage
                # For local provider, this means modifying the file in storage
                cloud_storage = Path.home() / ".local_cloud_storage"
                if cloud_storage.exists():
                    cloud_file = cloud_storage / "conflict_test.txt"
                    if cloud_file.exists():
                        # Wait a moment to ensure different timestamp
                        await asyncio.sleep(0.1)
                        cloud_file.write_text("Remote version")

                        # Modify local file to create conflict
                        await asyncio.sleep(0.1)
                        test_file.write_text("Updated local version")

                        # Sync should resolve conflict using last-write-wins
                        result = await manager.sync_directory(direction=SyncDirection.BIDIRECTIONAL)
                        assert result.success is True

            finally:
                # Cleanup
                if test_file.exists():
                    test_file.unlink()


if __name__ == "__main__":
    # Simple test runner for manual testing
    async def run_basic_tests():
        """Run basic functionality tests."""
        print("Running basic cloud sync tests...")

        # Test local provider
        print("\n1. Testing Local Provider...")
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_root = Path(temp_dir) / "cloud_storage"
            config = CloudConfig(provider=CloudProvider.LOCAL)
            provider = LocalProvider(config, storage_root)

            assert await provider.authenticate() is True
            print("✓ Provider authentication successful")

            # Test file operations
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Test content")

            cloud_file = await provider.upload_file(test_file, "test.txt")
            assert cloud_file.name == "test.txt"
            print("✓ File upload successful")

            download_path = Path(temp_dir) / "downloaded.txt"
            await provider.download_file(cloud_file.id, download_path)
            assert download_path.read_text() == "Test content"
            print("✓ File download successful")

        # Test sync manager
        print("\n2. Testing Cloud Sync Manager...")
        with tempfile.TemporaryDirectory() as temp_dir:
            sync_dir = Path(temp_dir) / "sync"
            sync_dir.mkdir()

            config = SyncConfig(sync_directory=sync_dir, cloud_config=CloudConfig(provider=CloudProvider.LOCAL))
            manager = CloudSyncManager(config)

            assert await manager.authenticate() is True
            print("✓ Sync manager authentication successful")

            # Create test file
            test_file = sync_dir / "sync_test.txt"
            test_file.write_text("Sync test content")

            result = await manager.sync_directory()
            assert result.success is True
            print(f"✓ Sync completed: {result.files_synced} files synced")

        print("\nAll basic tests passed! ✅")

    # Run tests
    asyncio.run(run_basic_tests())
