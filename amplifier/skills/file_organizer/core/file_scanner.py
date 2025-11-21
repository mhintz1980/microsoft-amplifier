"""
File Scanner Module

Handles recursive file system scanning with performance optimization
and integration with the Performance Expert skill for efficient operations.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Set
import aiofiles
import aiofiles.os

from ..models.file_models import FileInfo, ScanProgress, FileScannerConfig


logger = logging.getLogger(__name__)


class FileScanner:
    """High-performance file system scanner with async operations."""

    def __init__(self, config: Optional[FileScannerConfig] = None):
        """
        Initialize the file scanner.

        Args:
            config: Scanner configuration options
        """
        self.config = config or FileScannerConfig()
        self._scanned_files: Set[Path] = set()
        self._scan_stats = {
            "total_files": 0,
            "total_directories": 0,
            "total_bytes": 0,
            "start_time": None,
            "errors": [],
        }

    async def scan_directory(self, directory: Path, progress_callback: Optional[callable] = None) -> List[FileInfo]:
        """
        Recursively scan a directory and return file information.

        Args:
            directory: Directory path to scan
            progress_callback: Optional callback for progress updates

        Returns:
            List of FileInfo objects for all discovered files

        Raises:
            ValueError: If directory doesn't exist or isn't a directory
            PermissionError: If lacking read permissions
        """
        # Validate input
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        # Reset state
        self._scanned_files.clear()
        self._scan_stats = {
            "total_files": 0,
            "total_directories": 0,
            "total_bytes": 0,
            "start_time": datetime.now(),
            "errors": [],
        }

        logger.info(f"Starting scan of directory: {directory}")

        try:
            files = []
            async for file_info in self._scan_recursive(directory, progress_callback):
                files.append(file_info)

            logger.info(f"Scan completed: {len(files)} files found")
            return files

        except Exception as e:
            logger.error(f"Scan failed: {e}")
            raise

    async def scan_single_file(self, file_path: Path) -> FileInfo:
        """
        Scan a single file and return its information.

        Args:
            file_path: Path to the file to scan

        Returns:
            FileInfo object with file details

        Raises:
            ValueError: If file doesn't exist
        """
        if not file_path.exists():
            raise ValueError(f"File does not exist: {file_path}")

        return await self._create_file_info(file_path)

    async def _scan_recursive(
        self, directory: Path, progress_callback: Optional[callable] = None
    ) -> AsyncGenerator[FileInfo, None]:
        """
        Internal recursive scanning implementation.

        Args:
            directory: Current directory to scan
            progress_callback: Optional progress callback

        Yields:
            FileInfo objects for discovered files
        """
        try:
            entries = await aiofiles.os.listdir(directory)
            self._scan_stats["total_directories"] += 1

            # Report directory progress
            if progress_callback:
                progress = ScanProgress(
                    current_file="",
                    files_scanned=self._scan_stats["total_files"],
                    total_files=None,  # Unknown until we finish
                    directories_scanned=self._scan_stats["total_directories"],
                    current_directory=str(directory),
                    bytes_processed=self._scan_stats["total_bytes"],
                    start_time=self._scan_stats["start_time"],
                )
                try:
                    if asyncio.iscoroutinefunction(progress_callback):
                        await progress_callback(progress)
                    else:
                        progress_callback(progress)
                except Exception as cb_error:
                    logger.warning(f"Progress callback error: {cb_error}")

            # Process each entry
            for entry in entries:
                entry_path = directory / entry

                try:
                    # Skip if we've already processed (symlink loops)
                    if entry_path in self._scanned_files:
                        continue

                    # Handle hidden files
                    if not self.config.include_hidden and entry.startswith("."):
                        continue

                    stat_info = await aiofiles.os.stat(entry_path)

                    if stat_info.st_mode & 0o170000 == 0o040000:  # Directory
                        # Check depth limit
                        current_depth = len(entry_path.relative_to(directory).parts)
                        if self.config.max_depth is None or current_depth < self.config.max_depth:
                            self._scanned_files.add(entry_path)
                            async for file_info in self._scan_recursive(entry_path, progress_callback):
                                yield file_info
                        else:
                            logger.debug(f"Max depth reached at: {entry_path}")

                    else:  # File
                        file_info = await self._create_file_info(entry_path, stat_info)

                        # Apply filters
                        if self.config.should_include_file(entry_path):
                            # Check size constraints
                            if file_info.size >= self.config.min_file_size and (
                                self.config.max_file_size is None or file_info.size <= self.config.max_file_size
                            ):
                                self._scan_stats["total_files"] += 1
                                self._scan_stats["total_bytes"] += file_info.size
                                self._scanned_files.add(entry_path)

                                # Report file progress
                                if progress_callback:
                                    progress = ScanProgress(
                                        current_file=str(entry_path),
                                        files_scanned=self._scan_stats["total_files"],
                                        total_files=None,
                                        directories_scanned=self._scan_stats["total_directories"],
                                        current_directory=str(directory),
                                        bytes_processed=self._scan_stats["total_bytes"],
                                        start_time=self._scan_stats["start_time"],
                                    )
                                    try:
                                        if asyncio.iscoroutinefunction(progress_callback):
                                            await progress_callback(progress)
                                        else:
                                            progress_callback(progress)
                                    except Exception as cb_error:
                                        logger.warning(f"Progress callback error: {cb_error}")

                                yield file_info

                except PermissionError as pe:
                    error_msg = f"Permission denied: {entry_path}"
                    logger.warning(error_msg)
                    self._scan_stats["errors"].append(error_msg)
                    continue
                except OSError as oe:
                    error_msg = f"OS error accessing {entry_path}: {oe}"
                    logger.warning(error_msg)
                    self._scan_stats["errors"].append(error_msg)
                    continue
                except Exception as e:
                    error_msg = f"Unexpected error processing {entry_path}: {e}"
                    logger.error(error_msg)
                    self._scan_stats["errors"].append(error_msg)
                    continue

        except PermissionError as pe:
            error_msg = f"Permission denied accessing directory {directory}: {pe}"
            logger.error(error_msg)
            self._scan_stats["errors"].append(error_msg)
            raise
        except OSError as oe:
            error_msg = f"OS error in directory {directory}: {oe}"
            logger.error(error_msg)
            self._scan_stats["errors"].append(error_msg)
            raise

    async def _create_file_info(self, file_path: Path, stat_info=None) -> FileInfo:
        """
        Create FileInfo object for a file path.

        Args:
            file_path: Path to the file
            stat_info: Optional pre-fetched stat information

        Returns:
            FileInfo object with file details
        """
        if stat_info is None:
            stat_info = await aiofiles.os.stat(file_path)

        # Handle symbolic links
        is_symlink = file_path.is_symlink()
        actual_path = file_path
        if is_symlink and self.config.follow_symlinks:
            try:
                actual_path = file_path.resolve()
                stat_info = await aiofiles.os.stat(actual_path)
            except (OSError, PermissionError):
                # Use original link if can't resolve
                pass

        is_file = actual_path.is_file()
        is_directory = actual_path.is_dir()

        # Get timestamps
        created_time = datetime.fromtimestamp(stat_info.st_ctime)
        modified_time = datetime.fromtimestamp(stat_info.st_mtime)
        accessed_time = datetime.fromtimestamp(stat_info.st_atime)

        # Get extension (without dot)
        extension = None
        if is_file and actual_path.suffix:
            extension = actual_path.suffix.lstrip(".").lower()

        return FileInfo(
            path=actual_path,
            name=actual_path.name,
            size=stat_info.st_size,
            is_file=is_file,
            is_directory=is_directory,
            extension=extension,
            created_time=created_time,
            modified_time=modified_time,
            accessed_time=accessed_time,
        )

    def get_scan_statistics(self) -> dict:
        """
        Get statistics from the last scan operation.

        Returns:
            Dictionary with scan statistics
        """
        stats = self._scan_stats.copy()
        if stats["start_time"]:
            stats["duration"] = (datetime.now() - stats["start_time"]).total_seconds()

        return stats

    async def estimate_directory_size(self, directory: Path) -> dict:
        """
        Quick estimate of directory size without full scan.

        Args:
            directory: Directory to estimate

        Returns:
            Dictionary with size estimates
        """
        try:
            # Use os.walk for faster directory counting (not async but faster for estimation)
            file_count = 0
            total_size = 0
            dir_count = 0

            for root, dirs, files in directory.rglob("*"):
                if root.is_dir():
                    dir_count += 1
                elif root.is_file():
                    file_count += 1
                    try:
                        total_size += root.stat().st_size
                    except (OSError, PermissionError):
                        pass

            return {
                "estimated_files": file_count,
                "estimated_directories": dir_count,
                "estimated_size_bytes": total_size,
                "estimated_size_mb": round(total_size / (1024 * 1024), 2),
            }

        except Exception as e:
            logger.error(f"Directory size estimation failed: {e}")
            return {"estimated_files": 0, "estimated_directories": 0, "estimated_size_bytes": 0, "estimated_size_mb": 0}
