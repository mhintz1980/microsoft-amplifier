"""
Basic Categorizer Module

Rule-based file categorization system with integration with the
Security Expert skill for safe rule processing.
"""

import logging
from typing import Dict, List, Optional

from ..models.file_models import FileInfo, Category, CategoryType


logger = logging.getLogger(__name__)


class BasicCategorizer:
    """Rule-based file categorizer with built-in category definitions."""

    def __init__(self):
        """Initialize the categorizer with default categories."""
        self._categories = self._create_default_categories()
        self._category_lookup = self._build_category_lookup()

    def _create_default_categories(self) -> Dict[CategoryType, Category]:
        """Create default file categories based on common file types."""
        return {
            CategoryType.DOCUMENTS: Category(
                name="Documents",
                type=CategoryType.DOCUMENTS,
                description="Text documents and office files",
                extensions=["pdf", "doc", "docx", "txt", "rtf", "odt", "pages", "md"],
                patterns=["*.readme", "*.changelog", "*.license"],
                max_size_mb=100.0,
                target_directory="documents",
            ),
            CategoryType.IMAGES: Category(
                name="Images",
                type=CategoryType.IMAGES,
                description="Image files and graphics",
                extensions=["jpg", "jpeg", "png", "gif", "bmp", "tiff", "svg", "webp", "ico", "heic"],
                max_size_mb=50.0,
                target_directory="images",
            ),
            CategoryType.VIDEOS: Category(
                name="Videos",
                type=CategoryType.VIDEOS,
                description="Video files and movies",
                extensions=["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm", "m4v", "3gp"],
                max_size_mb=5000.0,
                target_directory="videos",
            ),
            CategoryType.AUDIO: Category(
                name="Audio",
                type=CategoryType.AUDIO,
                description="Audio files and music",
                extensions=["mp3", "wav", "flac", "aac", "ogg", "wma", "m4a", "opus"],
                max_size_mb=500.0,
                target_directory="audio",
            ),
            CategoryType.CODE: Category(
                name="Code",
                type=CategoryType.CODE,
                description="Source code and development files",
                extensions=[
                    "py",
                    "js",
                    "ts",
                    "html",
                    "css",
                    "java",
                    "cpp",
                    "c",
                    "h",
                    "cs",
                    "php",
                    "rb",
                    "go",
                    "rs",
                    "swift",
                ],
                patterns=["Makefile", "Dockerfile", "*.yml", "*.yaml", "package.json", "requirements.txt"],
                max_size_mb=10.0,
                target_directory="code",
            ),
            CategoryType.ARCHIVES: Category(
                name="Archives",
                type=CategoryType.ARCHIVES,
                description="Compressed archives and backups",
                extensions=["zip", "rar", "7z", "tar", "gz", "bz2", "xz", "z", "arj"],
                max_size_mb=1000.0,
                target_directory="archives",
            ),
            CategoryType.DOWNLOADS: Category(
                name="Downloads",
                type=CategoryType.DOWNLOADS,
                description="Files from downloads folder",
                patterns=["download*", "temp*", "*.tmp", "*.part"],
                target_directory="downloads",
            ),
            CategoryType.TEMPORARY: Category(
                name="Temporary",
                type=CategoryType.TEMPORARY,
                description="Temporary files and caches",
                extensions=["tmp", "temp", "cache", "log"],
                patterns=["*.tmp", "*.temp", "*.cache", "*.log", "thumbs.db", ".DS_Store"],
                target_directory="temporary",
            ),
            CategoryType.SYSTEM: Category(
                name="System",
                type=CategoryType.SYSTEM,
                description="System and configuration files",
                extensions=["ini", "cfg", "conf", "config", "sys", "dll", "exe", "bat", "sh"],
                patterns=["*.ini", "*.cfg", "*.conf", "*.config"],
                target_directory="system",
            ),
            CategoryType.UNKNOWN: Category(
                name="Unknown",
                type=CategoryType.UNKNOWN,
                description="Files that don't match any category",
                target_directory="unknown",
            ),
        }

    def _build_category_lookup(self) -> Dict[str, CategoryType]:
        """Build a quick lookup table for file extensions."""
        lookup = {}
        for category_type, category in self._categories.items():
            for ext in category.extensions:
                lookup[ext.lower()] = category_type
        return lookup

    def categorize_file(self, file_info: FileInfo) -> Category:
        """
        Categorize a single file based on its properties.

        Args:
            file_info: File information object

        Returns:
            Category object that best matches the file
        """
        # Quick extension lookup first
        if file_info.extension:
            ext_lower = file_info.extension.lower()
            if ext_lower in self._category_lookup:
                category_type = self._category_lookup[ext_lower]
                category = self._categories[category_type]

                # Verify size constraints
                if self._check_size_constraints(file_info, category):
                    return category

        # Detailed category matching
        for category_type, category in self._categories.items():
            if category_type == CategoryType.UNKNOWN:
                continue  # Skip unknown for now

            if category.matches_file(file_info):
                if self._check_size_constraints(file_info, category):
                    return category

        # Default to unknown
        return self._categories[CategoryType.UNKNOWN]

    def _check_size_constraints(self, file_info: FileInfo, category: Category) -> bool:
        """Check if file meets category size constraints."""
        if category.max_size_mb is not None and file_info.size_mb > category.max_size_mb:
            return False
        if category.min_size_mb is not None and file_info.size_mb < category.min_size_mb:
            return False
        return True

    def categorize_files(self, file_infos: List[FileInfo]) -> Dict[CategoryType, List[FileInfo]]:
        """
        Categorize multiple files.

        Args:
            file_infos: List of file information objects

        Returns:
            Dictionary mapping category types to lists of files
        """
        categorized = {category_type: [] for category_type in CategoryType}

        for file_info in file_infos:
            category = self.categorize_file(file_info)
            categorized[category.type].append(file_info)

        return categorized

    def get_category(self, category_type: CategoryType) -> Optional[Category]:
        """
        Get a specific category by type.

        Args:
            category_type: The category type to retrieve

        Returns:
            Category object or None if not found
        """
        return self._categories.get(category_type)

    def add_custom_category(self, category: Category) -> None:
        """
        Add a custom category to the categorizer.

        Args:
            category: Custom category to add
        """
        self._categories[category.type] = category
        # Rebuild lookup table
        self._category_lookup = self._build_category_lookup()

    def remove_category(self, category_type: CategoryType) -> bool:
        """
        Remove a category from the categorizer.

        Args:
            category_type: Category type to remove

        Returns:
            True if removed, False if not found
        """
        if category_type in self._categories and category_type != CategoryType.UNKNOWN:
            del self._categories[category_type]
            self._category_lookup = self._build_category_lookup()
            return True
        return False

    def get_all_categories(self) -> List[Category]:
        """Get all configured categories."""
        return list(self._categories.values())

    def get_category_statistics(self, file_infos: List[FileInfo]) -> Dict[CategoryType, dict]:
        """
        Get categorization statistics for a list of files.

        Args:
            file_infos: List of files to analyze

        Returns:
            Dictionary with statistics per category
        """
        categorized = self.categorize_files(file_infos)
        stats = {}

        for category_type, files in categorized.items():
            total_size = sum(f.size for f in files)
            avg_size = total_size / len(files) if files else 0

            stats[category_type] = {
                "count": len(files),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "average_size_mb": round(avg_size / (1024 * 1024), 2),
                "largest_file_mb": round(max(f.size_mb for f in files), 2) if files else 0,
                "smallest_file_mb": round(min(f.size_mb for f in files), 2) if files else 0,
            }

        return stats

    def suggest_organization(self, file_infos: List[FileInfo]) -> Dict[str, List[str]]:
        """
        Suggest organization actions based on categorization.

        Args:
            file_infos: Files to analyze

        Returns:
            Dictionary with organization suggestions
        """
        categorized = self.categorize_files(file_infos)
        suggestions = {}

        for category_type, files in categorized:
            if not files:
                continue

            category = self._categories[category_type]
            suggestion_list = []

            # Suggest moving files to target directory
            if category.target_directory and len(files) > 1:
                suggestion_list.append(
                    f"Move {len(files)} {category.name.lower()} files to '{category.target_directory}/'"
                )

            # Suggest cleanup for temporary files
            if category_type == CategoryType.TEMPORARY and len(files) > 10:
                suggestion_list.append(f"Consider deleting {len(files)} temporary files to free up space")

            # Suggest archive cleanup for large files
            if category_type == CategoryType.ARCHIVES:
                large_archives = [f for f in files if f.size_mb > 100]
                if large_archives:
                    suggestion_list.append(f"Review {len(large_archives)} large archive files (>100MB)")

            if suggestion_list:
                suggestions[category.name] = suggestion_list

        return suggestions

    def validate_category_rules(self) -> List[str]:
        """
        Validate category rules for potential conflicts or issues.

        Returns:
            List of validation warnings/errors
        """
        warnings = []
        extensions_seen = {}

        # Check for extension conflicts
        for category_type, category in self._categories.items():
            for ext in category.extensions:
                ext_lower = ext.lower()
                if ext_lower in extensions_seen:
                    other_category = extensions_seen[ext_lower]
                    warnings.append(
                        f"Extension '.{ext}' is used by both '{other_category}' and '{category.name}' categories"
                    )
                else:
                    extensions_seen[ext_lower] = category.name

        # Check for empty categories
        for category_type, category in self._categories.items():
            if not category.extensions and not category.patterns:
                warnings.append(f"Category '{category.name}' has no matching rules")

        return warnings
