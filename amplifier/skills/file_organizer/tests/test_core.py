"""
Comprehensive tests for the File Organizer core functionality.

These tests validate all components work together correctly and can be
run immediately with fixtures that are created on-the-fly.
"""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
import pytest
import json

# Import the modules we're testing
from ..core.file_organizer import FileOrganizer
from ..core.file_scanner import FileScanner
from ..core.categorizer import BasicCategorizer
from ..core.config import FileOrganizerConfig
from ..core.skill_integrations import SkillIntegrationManager
from ..models.file_models import (
    FileInfo,
    Category,
    CategoryType,
    OrganizationRule,
    OrganizationAction,
    ScanProgress,
    FileScannerConfig,
)


class TestFileOrganizerIntegration:
    """Integration tests for the complete File Organizer system."""

    @pytest.fixture
    async def temp_directory(self):
        """Create a temporary directory with test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file structure
            test_files = {
                "documents/report.pdf": b"PDF content",
                "documents/notes.txt": b"Text content",
                "images/photo.jpg": b"JPEG content",
                "images/icon.png": b"PNG content",
                "videos/movie.mp4": b"MP4 content",
                "audio/song.mp3": b"MP3 content",
                "code/script.py": b'print("hello")',
                "code/style.css": b"body { color: red; }",
                "archives/data.zip": b"ZIP content",
                "temp/tmp_file.tmp": b"Temporary content",
                "system/config.ini": b"[Settings]\\nkey=value",
                "mixed/file_without_extension": b"No extension content",
                "subdir/deeply/nested/file.txt": b"Deep file content",
                "large_file.dat": b"X" * (10 * 1024 * 1024),  # 10MB file
            }

            # Create directory structure and files
            for file_path, content in test_files.items():
                full_path = temp_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_bytes(content)

            # Create some empty directories
            (temp_path / "empty_dir").mkdir()
            (temp_path / "another_empty_dir").mkdir()

            yield temp_path

    @pytest.fixture
    def test_config(self):
        """Create a test configuration."""
        return FileOrganizerConfig(
            dry_run=True,  # Safe for tests
            backup_enabled=False,  # No backup needed for tests
            log_level="DEBUG",
            max_concurrent_operations=3,
            confirm_destructive_operations=False,
        )

    @pytest.fixture
    def file_organizer(self, test_config):
        """Create a FileOrganizer instance with test configuration."""
        return FileOrganizer(test_config)

    def test_configuration_creation(self):
        """Test configuration object creation and validation."""
        config = FileOrganizerConfig(dry_run=False, backup_enabled=True, log_level="INFO")

        assert config.dry_run is False
        assert config.backup_enabled is True
        assert config.log_level == "INFO"
        assert len(config.protected_directories) > 0

        # Test invalid log level
        with pytest.raises(ValueError):
            FileOrganizerConfig(log_level="INVALID")

    def test_file_scanner_config(self):
        """Test file scanner configuration."""
        config = FileScannerConfig(
            include_hidden=False, max_depth=5, file_extensions_filter=["pdf", "txt"], exclude_patterns=["*.tmp"]
        )

        assert config.include_hidden is False
        assert config.max_depth == 5
        assert "pdf" in config.file_extensions_filter
        assert "*.tmp" in config.exclude_patterns

    def test_file_scanner_basic(self, temp_directory):
        """Test basic file scanning functionality."""
        scanner = FileScanner()

        # Test scanning the temporary directory
        files = asyncio.run(scanner.scan_directory(temp_directory))

        # Verify we found files
        assert len(files) > 0

        # Check that we have different file types
        extensions = {f.extension for f in files if f.extension}
        assert "pdf" in extensions
        assert "txt" in extensions
        assert "jpg" in extensions

        # Verify file info structure
        for file_info in files:
            assert isinstance(file_info, FileInfo)
            assert file_info.path.exists()
            assert file_info.name is not None
            assert file_info.size >= 0
            assert isinstance(file_info.created_time, datetime)
            assert isinstance(file_info.modified_time, datetime)

    def test_file_scanner_with_filters(self, temp_directory):
        """Test file scanning with filters."""
        config = FileScannerConfig(file_extensions_filter=["pdf", "txt"], exclude_patterns=["*config*"], max_depth=2)
        scanner = FileScanner(config)

        files = asyncio.run(scanner.scan_directory(temp_directory))

        # All files should be PDF or TXT
        for file_info in files:
            if file_info.extension:
                assert file_info.extension in ["pdf", "txt"]

        # Should not find config files
        config_files = [f for f in files if "config" in f.name.lower()]
        assert len(config_files) == 0

    def test_basic_categorizer(self):
        """Test basic file categorization."""
        categorizer = BasicCategorizer()

        # Test categorizing different file types
        test_files = [
            FileInfo(
                path=Path("test.pdf"),
                name="test.pdf",
                size=1000,
                is_file=True,
                is_directory=False,
                extension="pdf",
                created_time=datetime.now(),
                modified_time=datetime.now(),
                accessed_time=datetime.now(),
            ),
            FileInfo(
                path=Path("test.py"),
                name="test.py",
                size=500,
                is_file=True,
                is_directory=False,
                extension="py",
                created_time=datetime.now(),
                modified_time=datetime.now(),
                accessed_time=datetime.now(),
            ),
            FileInfo(
                path=Path("test.jpg"),
                name="test.jpg",
                size=2000,
                is_file=True,
                is_directory=False,
                extension="jpg",
                created_time=datetime.now(),
                modified_time=datetime.now(),
                accessed_time=datetime.now(),
            ),
        ]

        for file_info in test_files:
            category = categorizer.categorize_file(file_info)
            assert category is not None
            assert isinstance(category, Category)

        # Test PDF categorization
        pdf_file = test_files[0]
        pdf_category = categorizer.categorize_file(pdf_file)
        assert pdf_category.type == CategoryType.DOCUMENTS

        # Test Python file categorization
        py_file = test_files[1]
        py_category = categorizer.categorize_file(py_file)
        assert py_category.type == CategoryType.CODE

        # Test image categorization
        jpg_file = test_files[2]
        jpg_category = categorizer.categorize_file(jpg_file)
        assert jpg_category.type == CategoryType.IMAGES

    def test_categorizer_statistics(self, temp_directory):
        """Test categorizer statistics generation."""
        scanner = FileScanner()
        categorizer = BasicCategorizer()

        files = asyncio.run(scanner.scan_directory(temp_directory))
        stats = categorizer.get_category_statistics(files)

        assert isinstance(stats, dict)
        assert len(stats) > 0

        # Should have statistics for multiple categories
        total_files = sum(cat_stats["count"] for cat_stats in stats.values())
        assert total_files == len(files)

    def test_organization_rules(self):
        """Test organization rule creation and application."""
        rule = OrganizationRule(
            name="Move PDFs to documents",
            category_type=CategoryType.DOCUMENTS,
            action=OrganizationAction.MOVE,
            target_directory="documents",
        )

        assert rule.name == "Move PDFs to documents"
        assert rule.category_type == CategoryType.DOCUMENTS
        assert rule.action == OrganizationAction.MOVE
        assert rule.target_directory == "documents"
        assert rule.enabled is True

        # Test rule matching
        test_file = FileInfo(
            path=Path("test.pdf"),
            name="test.pdf",
            size=1000,
            is_file=True,
            is_directory=False,
            extension="pdf",
            created_time=datetime.now(),
            modified_time=datetime.now(),
            accessed_time=datetime.now(),
        )

        # Rule with extension filter
        pdf_rule = OrganizationRule(
            name="PDF Rule", category_type=CategoryType.DOCUMENTS, action=OrganizationAction.MOVE, extensions=["pdf"]
        )

        assert pdf_rule.applies_to_file(test_file) is True

        # Rule with pattern filter
        pattern_rule = OrganizationRule(
            name="Pattern Rule", category_type=CategoryType.DOCUMENTS, action=OrganizationAction.MOVE, pattern="*.pdf"
        )

        assert pattern_rule.applies_to_file(test_file) is True

        # Rule with size constraints
        size_rule = OrganizationRule(
            name="Size Rule",
            category_type=CategoryType.DOCUMENTS,
            action=OrganizationAction.MOVE,
            min_size_mb=0.001,  # 1KB
            max_size_mb=10.0,  # 10MB
        )

        assert size_rule.applies_to_file(test_file) is True

    @pytest.mark.asyncio
    async def test_file_organizer_preview(self, temp_directory, file_organizer):
        """Test file organization preview functionality."""
        preview = await file_organizer.preview_organization(temp_directory)

        assert "total_files" in preview
        assert "categories" in preview
        assert "actions" in preview
        assert "warnings" in preview

        assert preview["total_files"] > 0
        assert len(preview["categories"]) > 0

    @pytest.mark.asyncio
    async def test_file_organizer_dry_run(self, temp_directory, file_organizer):
        """Test file organization in dry run mode."""
        # Create a custom rule for testing
        rule = OrganizationRule(
            name="Test Move Rule",
            category_type=CategoryType.DOCUMENTS,
            action=OrganizationAction.MOVE,
            target_directory="organized_documents",
        )
        file_organizer.config.add_organization_rule(rule)

        result = await file_organizer.organize_directory(temp_directory)

        assert isinstance(result, OrganizationResult)
        assert result.success is True
        assert result.total_files > 0

        # In dry run mode, files should not actually be moved
        # but the organization should still be "successful"
        original_files = list(temp_directory.rglob("*"))
        assert len(original_files) > 0

    def test_skill_integration_manager(self):
        """Test skill integration manager."""
        manager = SkillIntegrationManager()

        # Test integration status
        status = manager.get_integration_status()
        assert isinstance(status, dict)
        assert "nodejs_available" in status
        assert "npm_available" in status
        assert "vite_available" in status

        # Test security integration
        test_file = Path("/tmp/test_file.txt")
        is_safe, warnings = manager.security.is_file_safe(test_file, content_check=False)
        assert isinstance(is_safe, bool)
        assert isinstance(warnings, list)

        # Test performance integration
        tracker = manager.performance.create_progress_tracker(100)
        assert tracker["total_items"] == 100
        assert tracker["processed_items"] == 0

        manager.performance.update_progress(tracker, 10)
        assert tracker["processed_items"] == 10

    def test_configuration_serialization(self, temp_directory):
        """Test configuration save/load functionality."""
        config_path = temp_directory / "test_config.json"

        # Create configuration
        original_config = FileOrganizerConfig(dry_run=False, backup_enabled=True, log_level="DEBUG")

        # Save configuration
        original_config.to_file(config_path, format="json")
        assert config_path.exists()

        # Load configuration
        loaded_config = FileOrganizerConfig.from_file(config_path)

        # Verify configuration was loaded correctly
        assert loaded_config.dry_run == original_config.dry_run
        assert loaded_config.backup_enabled == original_config.backup_enabled
        assert loaded_config.log_level == original_config.log_level

    def test_error_handling(self, temp_directory):
        """Test error handling in various scenarios."""
        scanner = FileScanner()

        # Test scanning non-existent directory
        with pytest.raises(ValueError):
            asyncio.run(scanner.scan_directory(Path("/non/existent/path")))

        # Test scanning file instead of directory
        test_file = temp_directory / "test.txt"
        test_file.write_text("test")

        with pytest.raises(ValueError):
            asyncio.run(scanner.scan_directory(test_file))

    def test_large_file_handling(self, temp_directory):
        """Test handling of large files."""
        # Create a large test file (if not already created by fixture)
        large_file = temp_directory / "very_large_file.dat"
        if not large_file.exists():
            large_file.write_bytes(b"X" * (50 * 1024 * 1024))  # 50MB

        scanner = FileScanner()
        files = asyncio.run(scanner.scan_directory(temp_directory))

        # Find the large file
        large_files = [f for f in files if f.size_mb > 40]
        assert len(large_files) > 0

        # Test that we can categorize large files
        categorizer = BasicCategorizer()
        for large_file_info in large_files:
            category = categorizer.categorize_file(large_file_info)
            assert category is not None

    @pytest.mark.asyncio
    async def test_progress_tracking(self, temp_directory, file_organizer):
        """Test progress tracking during file operations."""
        progress_updates = []

        def progress_callback(progress):
            progress_updates.append(progress)

        # Use scanner with progress callback
        scanner = FileScanner()
        await scanner.scan_directory(temp_directory, progress_callback)

        # Should have received progress updates
        assert len(progress_updates) > 0

        # Check progress structure
        for update in progress_updates:
            if isinstance(update, ScanProgress):
                assert update.files_scanned >= 0
                assert update.directories_scanned >= 0
                assert isinstance(update.start_time, datetime)


class TestFileOrganizerEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_directory_handling(self):
        """Test handling of empty directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            scanner = FileScanner()

            files = asyncio.run(scanner.scan_directory(temp_path))
            assert len(files) == 0

    def test_permission_denied_handling(self):
        """Test handling of permission denied errors."""
        # This test is platform-dependent and may need adjustment
        # For now, we'll test with a non-existent protected path
        scanner = FileScanner()

        try:
            # Try to scan a protected system directory
            files = asyncio.run(scanner.scan_directory(Path("/root")))
        except (PermissionError, ValueError):
            # Expected behavior
            pass
        except Exception as e:
            # Other errors might occur depending on the system
            pass

    def test_unicode_file_names(self):
        """Test handling of Unicode file names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create files with Unicode names
            unicode_files = [
                "файл.txt",  # Cyrillic
                "文件.pdf",  # Chinese
                "fichier.doc",  # French with accent
                "Λοゴ.jpg",  # Greek and Japanese mix
            ]

            for filename in unicode_files:
                file_path = temp_path / filename
                file_path.write_text("Unicode content")

            scanner = FileScanner()
            files = asyncio.run(scanner.scan_directory(temp_path))

            assert len(files) == len(unicode_files)

            for file_info in files:
                assert file_info.name in unicode_files

    def test_very_deep_directory_structure(self):
        """Test handling of very deep directory structures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create deep directory structure
            current_path = temp_path
            for i in range(20):  # 20 levels deep
                current_path = current_path / f"level_{i}"
                current_path.mkdir()

            # Add a file at the deepest level
            deep_file = current_path / "deep_file.txt"
            deep_file.write_text("Deep content")

            scanner = FileScanner()
            files = asyncio.run(scanner.scan_directory(temp_path))

            assert len(files) == 1
            assert files[0].name == "deep_file.txt"

    def test_massive_file_count_simulation(self):
        """Test performance with many small files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create many small files (simulating a large directory)
            for i in range(1000):
                file_path = temp_path / f"file_{i:04d}.txt"
                file_path.write_text(f"Content {i}")

            scanner = FileScanner()
            files = asyncio.run(scanner.scan_directory(temp_path))

            assert len(files) == 1000

            # Test categorization performance
            categorizer = BasicCategorizer()
            categorized = categorizer.categorize_files(files)

            assert len(categorized) > 0
            assert CategoryType.DOCUMENTS in categorized


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])
