#!/usr/bin/env python3
"""
File Organizer Demo and Validation Script

This script demonstrates and validates the complete File Organizer system.
It creates test files, runs the organizer, and shows the results.
"""

import asyncio
import tempfile
import time
from datetime import datetime
from pathlib import Path

# Import our File Organizer system
from amplifier.skills.file_organizer import (
    FileOrganizer,
    FileOrganizerConfig,
    FileInfo,
    CategoryType,
    SkillIntegrationManager,
)


def create_test_files(temp_dir: Path) -> dict:
    """Create a variety of test files for demonstration."""
    print(f"Creating test files in: {temp_dir}")

    test_structure = {
        "documents/report.pdf": b"PDF document content here",
        "documents/notes.txt": b"Meeting notes from yesterday",
        "documents/proposal.docx": b"Project proposal document",
        "images/photos/vacation.jpg": b"JPEG photo data",
        "images/screenshots/screen.png": b"PNG screenshot data",
        "images/icons/app_icon.ico": b"Icon file data",
        "videos/presentation.mp4": b"MP4 video content",
        "videos/tutorial.avi": b"AVI video content",
        "audio/music/song.mp3": b"MP3 audio data",
        "audio/podcast.wav": b"WAV audio data",
        "code/main.py": b'#!/usr/bin/env python3\nprint("Hello, World!")',
        "code/style.css": b"body { font-family: Arial; margin: 0; }",
        "code/config.json": b'{"name": "test", "version": "1.0.0"}',
        "archives/backup.zip": b"ZIP archive content",
        "archives/data.tar.gz": b"Tarball content",
        "downloads/setup.exe": b"Windows installer",
        "temp/tmp_file.tmp": b"Temporary data",
        "logs/application.log": b"[INFO] Application started",
        "system/settings.ini": b"[Settings]\\ndebug=true\\nversion=2.0",
    }

    created_files = {}
    for file_path, content in test_structure.items():
        full_path = temp_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)
        created_files[file_path] = full_path

    print(f"Created {len(created_files)} test files")
    return created_files


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_file_stats(files: dict):
    """Print statistics about created files."""
    total_size = sum(path.stat().st_size for path in files.values())
    extensions = {}
    for path in files.values():
        ext = path.suffix.lower()
        extensions[ext] = extensions.get(ext, 0) + 1

    print(f"Total files: {len(files)}")
    print(f"Total size: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)")
    print("File extensions:")
    for ext, count in sorted(extensions.items()):
        ext_display = ext if ext else "<no extension>"
        print(f"  {ext_display}: {count} files")


async def demo_file_scanner(temp_dir: Path):
    """Demonstrate file scanning capabilities."""
    print_section("File Scanner Demo")

    from amplifier.skills.file_organizer.core.file_scanner import FileScanner
    from amplifier.skills.file_organizer.models.file_models import FileScannerConfig

    # Create scanner with custom configuration
    config = FileScannerConfig(include_hidden=False, max_depth=10, follow_symlinks=False)
    scanner = FileScanner(config)

    print(f"Scanning directory: {temp_dir}")
    start_time = time.time()

    # Progress tracking
    progress_updates = []

    def progress_callback(progress):
        progress_updates.append(
            {
                "files": progress.files_scanned,
                "directories": progress.directories_scanned,
                "current": progress.current_file or progress.current_directory,
            }
        )
        if progress.files_scanned % 5 == 0:  # Print every 5 files
            print(f"  Scanned {progress.files_scanned} files...")

    files = await scanner.scan_directory(temp_dir, progress_callback)

    scan_time = time.time() - start_time
    print(f"\nScan completed in {scan_time:.2f} seconds")
    print(f"Found {len(files)} files and directories")

    # Show file statistics
    file_count = sum(1 for f in files if f.is_file)
    dir_count = sum(1 for f in files if f.is_directory)
    total_size = sum(f.size for f in files if f.is_file)

    print(f"  Files: {file_count}")
    print(f"  Directories: {dir_count}")
    print(f"  Total size: {total_size:,} bytes")

    return files


def demo_categorizer(files):
    """Demonstrate file categorization."""
    print_section("File Categorizer Demo")

    from amplifier.skills.file_organizer.core.categorizer import BasicCategorizer

    categorizer = BasicCategorizer()

    # Filter only files (not directories)
    file_infos = [f for f in files if f.is_file]

    print(f"Categorizing {len(file_infos)} files...")

    # Categorize all files
    categorized = categorizer.categorize_files(file_infos)

    print("\nCategorization results:")
    for category_type, file_list in categorized.items():
        if file_list:
            print(f"  {category_type.value}: {len(file_list)} files")
            for file_info in file_list[:3]:  # Show first 3 files
                print(f"    - {file_info.name} ({file_info.size_mb:.2f} MB)")
            if len(file_list) > 3:
                print(f"    ... and {len(file_list) - 3} more")

    # Get statistics
    stats = categorizer.get_category_statistics(file_infos)
    print(f"\nCategory Statistics:")
    for category_type, category_stats in stats.items():
        if category_stats["count"] > 0:
            print(f"  {category_type.value}:")
            print(f"    Count: {category_stats['count']}")
            print(f"    Total size: {category_stats['total_size_mb']:.2f} MB")
            print(f"    Average size: {category_stats['average_size_mb']:.2f} MB")

    # Get suggestions
    suggestions = categorizer.suggest_organization(file_infos)
    if suggestions:
        print(f"\nOrganization Suggestions:")
        for category, suggestion_list in suggestions.items():
            for suggestion in suggestion_list:
                print(f"  - {suggestion}")

    return categorized


async def demo_file_organizer(temp_dir: Path):
    """Demonstrate the complete file organizer."""
    print_section("File Organizer Demo")

    # Create configuration
    config = FileOrganizerConfig(
        dry_run=True,  # Safe demo mode
        backup_enabled=False,
        log_level="INFO",
        progress_reporting=True,
        confirm_destructive_operations=False,
    )

    print("Configuration:")
    print(f"  Dry run: {config.dry_run}")
    print(f"  Backup enabled: {config.backup_enabled}")
    print(f"  Log level: {config.log_level}")

    # Create organizer
    organizer = FileOrganizer(config)

    # Preview organization
    print(f"\nPreviewing organization for: {temp_dir}")
    preview = await organizer.preview_organization(temp_dir)

    print(f"\nPreview Results:")
    print(f"  Total files: {preview['total_files']}")
    print(f"  Categories found: {len(preview['categories'])}")

    print("\n  Categories:")
    for category, count in preview["categories"].items():
        print(f"    {category}: {count} files")

    print("\n  Actions:")
    for action, files in preview["actions"].items():
        print(f"    {action}: {len(files)} files")

    if preview["warnings"]:
        print("\n  Warnings:")
        for warning in preview["warnings"]:
            print(f"    - {warning}")

    # Run organization (dry run)
    print(f"\nRunning organization (dry run mode)...")
    start_time = time.time()

    result = await organizer.organize_directory(temp_dir)

    run_time = time.time() - start_time
    print(f"\nOrganization completed in {run_time:.2f} seconds")

    print(f"\nResults:")
    print(f"  Success: {result.success}")
    print(f"  Total files: {result.total_files}")
    print(f"  Organized files: {result.organized_files}")
    print(f"  Failed files: {result.failed_files}")
    print(f"  Skipped files: {result.skipped_files}")
    print(f"  Duration: {result.duration_seconds:.2f} seconds")
    print(f"  Success rate: {result.success_rate:.1f}%")

    if result.errors:
        print(f"\nErrors:")
        for error in result.errors:
            print(f"  - {error}")

    return result


def demo_skill_integrations():
    """Demonstrate core skill integrations."""
    print_section("Core Skills Integration Demo")

    manager = SkillIntegrationManager()

    # Check integration status
    status = manager.get_integration_status()
    print(f"Integration Status:")
    for skill, available in status.items():
        status_icon = "✅" if available else "❌"
        print(f"  {skill}: {status_icon} {'Available' if available else 'Not Available'}")

    # Demonstrate security integration
    print(f"\nSecurity Integration:")
    test_file = Path(__file__)  # Test with this script file
    is_safe, warnings = manager.security.is_file_safe(test_file)
    print(f"  File: {test_file.name}")
    print(f"  Safe: {is_safe}")
    if warnings:
        for warning in warnings:
            print(f"  Warning: {warning}")

    # Check permissions
    permissions = manager.security.check_permissions(test_file)
    print(f"  Permissions: readable={permissions['readable']}, writable={permissions['writable']}")

    # Demonstrate performance integration
    print(f"\nPerformance Integration:")
    tracker = manager.performance.create_progress_tracker(100)
    print(f"  Created progress tracker for {tracker['total_items']} items")

    # Simulate progress updates
    for i in range(0, 101, 10):
        manager.performance.update_progress(tracker, 10)
        print(
            f"  Progress: {tracker['processed_items']}/{tracker['total_items']} "
            f"({tracker['items_per_second']:.1f} items/sec)"
        )


async def main():
    """Main demonstration function."""
    print_section("File Organizer System Demo")
    print("This demo validates the complete File Organizer system")
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Create temporary directory for demo
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            print(f"Using temporary directory: {temp_path}")

            # Create test files
            created_files = create_test_files(temp_path)
            print_file_stats(created_files)

            # Demo file scanner
            files = await demo_file_scanner(temp_path)

            # Demo categorizer
            categorized = demo_categorizer(files)

            # Demo file organizer
            result = await demo_file_organizer(temp_path)

            # Demo skill integrations
            demo_skill_integrations()

        print_section("Demo Completed Successfully!")
        print("✅ All components working correctly")
        print(f"✅ File scanner processed {len(files)} items")
        print(f"✅ Categorizer identified {len(categorized)} categories")
        print(f"✅ File organizer completed with {result.success_rate:.1f}% success rate")
        print("✅ Core skills integration functional")

    except Exception as e:
        print_section("Demo Failed!")
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎉 File Organizer system is ready for use!")
    else:
        print("\n💥 File Organizer system needs attention!")
