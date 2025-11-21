#!/usr/bin/env python3
"""
Cloud Sync Example

This example demonstrates the cloud synchronization functionality
of the File Organizer system, showing how to:

1. Set up cloud synchronization with different providers
2. Configure sync behavior and conflict resolution
3. Organize files with automatic cloud sync
4. Handle authentication and configuration
"""

import asyncio
import logging
from pathlib import Path
import tempfile

# Import the cloud sync components
from amplifier.skills.file_organizer import (
    CloudEnhancedFileOrganizer,
    CloudSyncManager,
    SyncConfig,
    CloudConfig,
    CloudProvider,
    SyncDirection,
    FileOrganizerConfig,
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def basic_cloud_sync_example():
    """Demonstrate basic cloud synchronization setup and usage."""
    print("\n=== Basic Cloud Sync Example ===\n")

    # Create a temporary directory for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        sync_dir = Path(temp_dir) / "my_files"
        sync_dir.mkdir()

        print(f"Working directory: {sync_dir}")

        # 1. Create test files to organize and sync
        print("\n1. Creating test files...")
        test_files = {
            "documents/report.pdf": "PDF report content",
            "images/photo.jpg": "JPEG image content",
            "code/script.py": "Python script content",
            "downloads/archive.zip": "Zip archive content",
        }

        for file_path, content in test_files.items():
            full_path = sync_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            print(f"  Created: {file_path}")

        # 2. Set up cloud sync configuration
        print("\n2. Setting up cloud sync configuration...")
        sync_config = SyncConfig(
            sync_directory=sync_dir,
            cloud_config=CloudConfig(provider=CloudProvider.LOCAL),  # Use local for demo
            direction=SyncDirection.BIDIRECTIONAL,
            auto_sync=True,
            conflict_resolution="last_write_wins",
        )

        # 3. Create and initialize the cloud sync manager
        print("\n3. Initializing cloud sync manager...")
        async with CloudSyncManager(sync_config) as sync_manager:
            # Authenticate with the provider (local provider auto-authenticates)
            auth_success = await sync_manager.authenticate()
            print(f"  Authentication: {'✓ Success' if auth_success else '✗ Failed'}")

            # Test connection
            connection_ok = await sync_manager.test_connection()
            print(f"  Connection test: {'✓ Success' if connection_ok else '✗ Failed'}")

            # 4. Perform initial sync
            print("\n4. Performing initial synchronization...")
            sync_result = await sync_manager.sync_directory()
            print(f"  Sync status: {'✓ Success' if sync_result.success else '✗ Failed'}")
            print(f"  Files synced: {sync_result.files_synced}")
            print(f"  Duration: {sync_result.duration_seconds:.2f} seconds")

            # 5. Get sync status
            print("\n5. Current sync status:")
            status = await sync_manager.get_sync_status()
            for key, value in status.items():
                print(f"  {key}: {value}")

        print("\n✓ Basic cloud sync example completed successfully!")


async def enhanced_organizer_example():
    """Demonstrate the cloud-enhanced file organizer."""
    print("\n=== Enhanced File Organizer Example ===\n")

    # Create a temporary directory for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        org_dir = Path(temp_dir) / "to_organize"
        org_dir.mkdir()

        print(f"Organization directory: {org_dir}")

        # 1. Create test files that need organization
        print("\n1. Creating files to organize...")
        test_files = [
            ("document1.pdf", "PDF content 1"),
            ("photo1.jpg", "JPEG content 1"),
            ("script1.py", "Python content 1"),
            ("archive1.zip", "Zip content 1"),
            ("document2.docx", "Word content 2"),
            ("image1.png", "PNG content 1"),
        ]

        for filename, content in test_files:
            file_path = org_dir / filename
            file_path.write_text(content)
            print(f"  Created: {filename}")

        # 2. Configure the cloud-enhanced organizer
        print("\n2. Configuring cloud-enhanced organizer...")
        sync_config = SyncConfig(
            sync_directory=org_dir,
            cloud_config=CloudConfig(provider=CloudProvider.LOCAL),
            auto_sync=True,
            delta_sync=True,
        )

        # Create organizer with ML disabled for demo simplicity
        organizer = CloudEnhancedFileOrganizer(sync_config=sync_config, enable_ml=False)

        # Configure sync behavior
        organizer.set_sync_behavior(
            auto_sync_after=True,  # Sync after organization
            sync_before=False,  # Don't sync before
            conflict_resolution="last_write_wins",
        )

        # Configure file organization
        organizer.config.dry_run = False  # Actually move files for demo

        try:
            # 3. Authenticate with cloud provider
            print("\n3. Authenticating with cloud provider...")
            auth_success = await organizer.authenticate_cloud_provider()
            print(f"  Authentication: {'✓ Success' if auth_success else '✗ Failed'}")

            # 4. Perform organization with automatic sync
            print("\n4. Organizing files with automatic cloud sync...")
            result = await organizer.organize_directory(org_dir)

            print(f"  Organization: {'✓ Success' if result.success else '✗ Failed'}")
            print(f"  Files processed: {result.total_files}")
            print(f"  Files organized: {result.organized_files}")
            print(f"  Duration: {result.duration_seconds:.2f} seconds")

            # Show sync information if available
            if hasattr(result, "sync_info"):
                sync_info = result.sync_info
                print("\n5. Sync Results:")
                print(f"  Pre-sync files: {sync_info['pre_sync']['files_synced']}")
                print(f"  Post-sync files: {sync_info['post_sync']['files_synced']}")
                print(f"  Pre-sync duration: {sync_info['pre_sync']['duration']:.2f}s")
                print(f"  Post-sync duration: {sync_info['post_sync']['duration']:.2f}s")

            # 6. Show organized structure
            print("\n6. Organized file structure:")
            for root, dirs, files in org_dir.rglob("*"):
                if Path(root).is_dir():
                    level = len(Path(root).relative_to(org_dir).parts)
                    indent = "  " * level
                    dir_name = Path(root).name
                    if dir_name != org_dir.name:
                        print(f"{indent}📁 {dir_name}/")
                        for file in Path(root).iterdir():
                            if file.is_file():
                                print(f"{indent}  📄 {file.name}")

        finally:
            await organizer.cleanup()

        print("\n✓ Enhanced organizer example completed successfully!")


async def conflict_resolution_example():
    """Demonstrate conflict resolution scenarios."""
    print("\n=== Conflict Resolution Example ===\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        sync_dir = Path(temp_dir) / "conflict_test"
        sync_dir.mkdir()

        print(f"Testing directory: {sync_dir}")

        # Setup sync manager
        sync_config = SyncConfig(
            sync_directory=sync_dir,
            cloud_config=CloudConfig(provider=CloudProvider.LOCAL),
            conflict_resolution="last_write_wins",
        )

        async with CloudSyncManager(sync_config) as sync_manager:
            await sync_manager.authenticate()

            # 1. Create initial file and sync
            print("\n1. Creating initial file and syncing...")
            test_file = sync_dir / "shared_document.txt"
            test_file.write_text("Initial version - Local")
            print(f"  Created: {test_file.name}")

            result1 = await sync_manager.sync_directory(direction=SyncDirection.UPLOAD)
            print(f"  Upload result: {'✓ Success' if result1.success else '✗ Failed'}")

            # 2. Simulate conflict by modifying both local and "cloud" versions
            print("\n2. Simulating conflict scenario...")

            # Wait a moment to ensure different timestamps
            await asyncio.sleep(0.1)

            # Modify local version
            test_file.write_text("Modified local version")
            print("  Modified local version")

            # For local provider, simulate remote change by modifying in storage
            cloud_storage = Path.home() / ".local_cloud_storage"
            if cloud_storage.exists():
                cloud_file = cloud_storage / "shared_document.txt"
                if cloud_file.exists():
                    await asyncio.sleep(0.1)
                    cloud_file.write_text("Modified remote version")
                    print("  Modified 'remote' version (in cloud storage)")

            # 3. Sync with conflict resolution
            print("\n3. Syncing with automatic conflict resolution...")
            result2 = await sync_manager.sync_directory(direction=SyncDirection.BIDIRECTIONAL)
            print(f"  Conflict resolution: {'✓ Success' if result2.success else '✗ Failed'}")

            # 4. Show final result
            final_content = test_file.read_text()
            print(f"\n4. Final file content: {final_content}")

            # Check which version won (last-write-wins)
            if "local" in final_content.lower():
                print("  ✓ Local version won (last modified)")
            else:
                print("  ✓ Remote version won (last modified)")

        print("\n✓ Conflict resolution example completed!")


async def configuration_example():
    """Demonstrate configuration management."""
    print("\n=== Configuration Management Example ===\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir)
        sync_dir = config_dir / "my_sync"
        sync_dir.mkdir()

        # 1. Create comprehensive configuration
        print("1. Creating comprehensive configuration...")

        sync_config = SyncConfig(
            sync_directory=sync_dir,
            cloud_config=CloudConfig(
                provider=CloudProvider.LOCAL,
                chunk_size=1024 * 512,  # 512KB chunks
                max_retries=5,
            ),
            direction=SyncDirection.BIDIRECTIONAL,
            conflict_resolution="last_write_wins",
            auto_sync=True,
            sync_interval_minutes=15,
            delta_sync=True,
            max_file_size_mb=100.0,
            max_concurrent_uploads=2,
            max_concurrent_downloads=3,
            include_patterns=["*.txt", "*.pdf", "*.py"],
            exclude_patterns=["*.tmp", "*.temp"],
            offline_mode=False,
            encrypt_transfers=True,
            verify_checksums=True,
            enable_logging=True,
        )

        # 2. Save configuration
        config_file = config_dir / "sync_config.json"
        sync_manager = CloudSyncManager(sync_config)
        sync_manager.save_configuration(config_file)
        print(f"  Configuration saved to: {config_file}")

        # 3. Load configuration
        print("\n2. Loading configuration...")
        loaded_manager = CloudSyncManager.load_configuration(config_file)
        print(f"  Provider: {loaded_manager.config.cloud_config.provider}")
        print(f"  Sync directory: {loaded_manager.config.sync_directory}")
        print(f"  Direction: {loaded_manager.config.direction}")
        print(f"  Auto sync: {loaded_manager.config.auto_sync}")

        # 4. Display current settings
        print("\n3. Current sync settings:")
        status = await loaded_manager.get_sync_status()
        for key, value in status.items():
            if key not in ["sync_directory"]:  # Skip long path
                print(f"  {key}: {value}")

        await loaded_manager.cleanup()

        print("\n✓ Configuration management example completed!")


async def main():
    """Run all examples."""
    print("🚀 Cloud Synchronization Examples")
    print("=" * 50)

    try:
        await basic_cloud_sync_example()
        await enhanced_organizer_example()
        await conflict_resolution_example()
        await configuration_example()

        print("\n" + "=" * 50)
        print("🎉 All examples completed successfully!")
        print("\nNext steps:")
        print("1. Replace CloudProvider.LOCAL with actual provider (ONEDRIVE, GDRIVE, DROPBOX)")
        print("2. Configure OAuth credentials for real cloud providers")
        print("3. Set up proper authentication flows")
        print("4. Configure conflict resolution strategies")
        print("5. Add monitoring and logging for production use")

    except Exception as e:
        logger.error(f"Example failed: {e}")
        print(f"\n❌ Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
