"""
Pydantic models for file organization system.

This module defines the core data structures used throughout the file organizer,
including file information, categories, rules, and results.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, computed_field


class CategoryType(str, Enum):
    """Enumeration of standard file categories."""

    DOCUMENTS = "documents"
    IMAGES = "images"
    VIDEOS = "videos"
    AUDIO = "audio"
    CODE = "code"
    ARCHIVES = "archives"
    DOWNLOADS = "downloads"
    TEMPORARY = "temporary"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class OrganizationAction(str, Enum):
    """Types of organization actions that can be performed."""

    MOVE = "move"
    COPY = "copy"
    RENAME = "rename"
    DELETE = "delete"
    NONE = "none"


class FileInfo(BaseModel):
    """Complete information about a file or directory."""

    path: Path = Field(description="Full path to the file/directory")
    name: str = Field(description="File or directory name")
    size: int = Field(description="Size in bytes", ge=0)
    is_file: bool = Field(description="True if file, False if directory")
    is_directory: bool = Field(description="True if directory, False if file")
    extension: Optional[str] = Field(description="File extension without dot", default=None)
    created_time: datetime = Field(description="File creation timestamp")
    modified_time: datetime = Field(description="File last modified timestamp")
    accessed_time: datetime = Field(description="File last accessed timestamp")

    @computed_field
    @property
    def size_mb(self) -> float:
        """File size in megabytes."""
        return round(self.size / (1024 * 1024), 2)

    @computed_field
    @property
    def parent_directory(self) -> Path:
        """Parent directory path."""
        return self.path.parent

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat(), Path: lambda v: str(v)}


class Category(BaseModel):
    """File category with rules and metadata."""

    name: str = Field(description="Category name")
    type: CategoryType = Field(description="Category type")
    description: str = Field(description="Category description")
    extensions: List[str] = Field(default_factory=list, description="File extensions in this category")
    patterns: List[str] = Field(default_factory=list, description="File name patterns")
    max_size_mb: Optional[float] = Field(None, description="Maximum file size in MB")
    min_size_mb: Optional[float] = Field(None, description="Minimum file size in MB")
    target_directory: Optional[str] = Field(None, description="Target directory for files in this category")

    def matches_file(self, file_info: FileInfo) -> bool:
        """Check if a file matches this category rules."""
        # Check extension
        if self.extensions and file_info.extension:
            if file_info.extension.lower() in [ext.lower().lstrip(".") for ext in self.extensions]:
                return True

        # Check patterns
        if self.patterns:
            import fnmatch

            for pattern in self.patterns:
                if fnmatch.fnmatch(file_info.name.lower(), pattern.lower()):
                    return True

        # Check size constraints
        if self.max_size_mb is not None and file_info.size_mb > self.max_size_mb:
            return False
        if self.min_size_mb is not None and file_info.size_mb < self.min_size_mb:
            return False

        return False


class OrganizationRule(BaseModel):
    """Rule for organizing files."""

    name: str = Field(description="Rule name")
    category_type: CategoryType = Field(description="Category this rule applies to")
    action: OrganizationAction = Field(description="Action to perform")
    target_directory: Optional[str] = Field(None, description="Target directory for move/copy actions")
    pattern: Optional[str] = Field(None, description="File name pattern for matching")
    extensions: List[str] = Field(default_factory=list, description="File extensions this rule applies to")
    min_size_mb: Optional[float] = Field(None, description="Minimum file size to apply rule")
    max_size_mb: Optional[float] = Field(None, description="Maximum file size to apply rule")
    enabled: bool = Field(True, description="Whether this rule is enabled")

    def applies_to_file(self, file_info: FileInfo) -> bool:
        """Check if this rule applies to a specific file."""
        if not self.enabled:
            return False

        # Check extensions
        if self.extensions and file_info.extension:
            if file_info.extension.lower() not in [ext.lower().lstrip(".") for ext in self.extensions]:
                return False

        # Check pattern
        if self.pattern:
            import fnmatch

            if not fnmatch.fnmatch(file_info.name.lower(), self.pattern.lower()):
                return False

        # Check size constraints
        if self.min_size_mb is not None and file_info.size_mb < self.min_size_mb:
            return False
        if self.max_size_mb is not None and file_info.size_mb > self.max_size_mb:
            return False

        return True


class OrganizationResult(BaseModel):
    """Result of file organization operation."""

    success: bool = Field(description="Whether the operation was successful")
    total_files: int = Field(description="Total number of files processed")
    organized_files: int = Field(description="Number of files successfully organized")
    failed_files: int = Field(description="Number of files that failed to organize")
    skipped_files: int = Field(description="Number of files skipped")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    organized_paths: List[Dict[str, Union[str, Path]]] = Field(
        default_factory=list, description="Paths that were organized"
    )
    duration_seconds: float = Field(description="Time taken in seconds")

    @computed_field
    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.total_files == 0:
            return 0.0
        return round((self.organized_files / self.total_files) * 100, 2)


class ScanProgress(BaseModel):
    """Progress information for scanning operations."""

    current_file: str = Field(description="Current file being processed")
    files_scanned: int = Field(description="Number of files scanned so far")
    total_files: Optional[int] = Field(None, description="Estimated total files")
    directories_scanned: int = Field(description="Number of directories scanned")
    current_directory: str = Field(description="Current directory being scanned")
    bytes_processed: int = Field(description="Total bytes processed")
    start_time: datetime = Field(description="Scan start time")

    @computed_field
    @property
    def progress_percentage(self) -> float:
        """Progress percentage if total is known."""
        if self.total_files is None or self.total_files == 0:
            return 0.0
        return round((self.files_scanned / self.total_files) * 100, 2)


class FileScannerConfig(BaseModel):
    """Configuration for file scanning operations."""

    include_hidden: bool = Field(False, description="Include hidden files and directories")
    max_depth: Optional[int] = Field(None, description="Maximum directory depth to scan")
    follow_symlinks: bool = Field(False, description="Follow symbolic links")
    file_extensions_filter: Optional[List[str]] = Field(None, description="Only scan files with these extensions")
    exclude_patterns: List[str] = Field(default_factory=list, description="Patterns to exclude")
    min_file_size: int = Field(0, description="Minimum file size in bytes")
    max_file_size: Optional[int] = Field(None, description="Maximum file size in bytes")

    def should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included in scan."""
        # Check extension filter
        if self.file_extensions_filter:
            if file_path.suffix.lower().lstrip(".") not in [ext.lower() for ext in self.file_extensions_filter]:
                return False

        # Check exclude patterns
        import fnmatch

        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(file_path.name.lower(), pattern.lower()):
                return False

        return True
