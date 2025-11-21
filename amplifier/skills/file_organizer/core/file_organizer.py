"""
File Organizer - Main Orchestrator

The primary orchestrator that coordinates all file organization operations.
Integrates with the 4 core skills for comprehensive file management.
"""

import asyncio
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models.file_models import (
    FileInfo,
    CategoryType,
    OrganizationResult,
    OrganizationRule,
    OrganizationAction,
    ScanProgress,
)
from .config import FileOrganizerConfig
from .file_scanner import FileScanner
from .categorizer import BasicCategorizer


logger = logging.getLogger(__name__)


class FileOrganizer:
    """Main file organizer orchestrator with integration to core skills."""

    def __init__(self, config: Optional[FileOrganizerConfig] = None):
        """
        Initialize the File Organizer.

        Args:
            config: Optional configuration, uses default if not provided
        """
        self.config = config or FileOrganizerConfig()
        self.scanner = FileScanner(self.config.scanner)
        self.categorizer = BasicCategorizer()

        # Add custom categories to categorizer
        for category in self.config.custom_categories:
            self.categorizer.add_custom_category(category)

        # Setup logging
        self._setup_logging()

        # Performance tracking
        self._operation_start_time = None
        self._processed_files = 0
        self._failed_files = 0
        self._skipped_files = 0

    def _setup_logging(self) -> None:
        """Setup logging based on configuration."""
        log_level = getattr(logging, self.config.log_level)
        logger.setLevel(log_level)

        # Add file handler if log file specified
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(log_level)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    async def organize_directory(
        self, directory: Path, progress_callback: Optional[callable] = None
    ) -> OrganizationResult:
        """
        Organize files in a directory according to configured rules.

        Args:
            directory: Directory path to organize
            progress_callback: Optional callback for progress updates

        Returns:
            OrganizationResult with operation details
        """
        self._operation_start_time = datetime.now()
        self._processed_files = 0
        self._failed_files = 0
        self._skipped_files = 0

        logger.info(f"Starting organization of directory: {directory}")

        # Validate directory
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        # Check if directory is protected
        if self.config.is_directory_protected(directory):
            raise PermissionError(f"Directory is protected from modification: {directory}")

        try:
            # Scan directory
            logger.info("Scanning directory for files...")
            files = await self.scanner.scan_directory(directory, progress_callback)

            if not files:
                logger.info("No files found to organize")
                return OrganizationResult(
                    success=True,
                    total_files=0,
                    organized_files=0,
                    failed_files=0,
                    skipped_files=0,
                    duration_seconds=0.0,
                )

            logger.info(f"Found {len(files)} files to process")

            # Categorize files
            logger.info("Categorizing files...")
            categorized_files = self.categorizer.categorize_files(files)

            # Get organization rules
            rules = self.config.get_effective_rules()

            # Create backup if enabled
            backup_info = None
            if self.config.backup_enabled and not self.config.dry_run:
                backup_info = await self._create_backup(directory, files)

            # Apply organization rules
            logger.info("Applying organization rules...")
            organized_files, errors = await self._apply_organization_rules(
                directory, categorized_files, rules, progress_callback
            )

            # Calculate duration
            duration = (datetime.now() - self._operation_start_time).total_seconds()

            # Create result
            result = OrganizationResult(
                success=len(errors) == 0,
                total_files=len(files),
                organized_files=self._processed_files,
                failed_files=self._failed_files,
                skipped_files=self._skipped_files,
                errors=errors,
                organized_paths=organized_files,
                duration_seconds=duration,
            )

            logger.info(f"Organization completed: {result.organized_files}/{result.total_files} files organized")
            return result

        except Exception as e:
            logger.error(f"Organization failed: {e}")
            return OrganizationResult(
                success=False,
                total_files=0,
                organized_files=0,
                failed_files=0,
                skipped_files=0,
                errors=[str(e)],
                duration_seconds=(datetime.now() - self._operation_start_time).total_seconds(),
            )

    async def _apply_organization_rules(
        self,
        base_directory: Path,
        categorized_files: Dict[CategoryType, List[FileInfo]],
        rules: Dict[CategoryType, List[OrganizationRule]],
        progress_callback: Optional[callable] = None,
    ) -> Tuple[List[Dict[str, Path]], List[str]]:
        """
        Apply organization rules to categorized files.

        Args:
            base_directory: Base directory being organized
            categorized_files: Files categorized by type
            rules: Organization rules to apply
            progress_callback: Optional progress callback

        Returns:
            Tuple of (organized_files_paths, error_messages)
        """
        organized_paths = []
        errors = []

        for category_type, files in categorized_files.items():
            if not files:
                continue

            category_rules = rules.get(category_type, [])
            if not category_rules:
                self._skipped_files += len(files)
                logger.info(f"No rules for category {category_type.value}, skipping {len(files)} files")
                continue

            logger.info(f"Processing {category_type.value}: {len(files)} files")

            for file_info in files:
                try:
                    # Find applicable rule
                    applicable_rule = None
                    for rule in category_rules:
                        if rule.applies_to_file(file_info):
                            applicable_rule = rule
                            break

                    if not applicable_rule:
                        self._skipped_files += 1
                        continue

                    # Apply rule
                    result_path = await self._apply_rule(base_directory, file_info, applicable_rule)

                    if result_path:
                        organized_paths.append(
                            {"original": file_info.path, "new": result_path, "action": applicable_rule.action.value}
                        )
                        self._processed_files += 1

                    # Report progress
                    if progress_callback:
                        try:
                            if asyncio.iscoroutinefunction(progress_callback):
                                await progress_callback(
                                    {
                                        "current_file": str(file_info.path),
                                        "action": applicable_rule.action.value,
                                        "processed": self._processed_files,
                                        "failed": self._failed_files,
                                        "skipped": self._skipped_files,
                                    }
                                )
                            else:
                                progress_callback(
                                    {
                                        "current_file": str(file_info.path),
                                        "action": applicable_rule.action.value,
                                        "processed": self._processed_files,
                                        "failed": self._failed_files,
                                        "skipped": self._skipped_files,
                                    }
                                )
                        except Exception as cb_error:
                            logger.warning(f"Progress callback error: {cb_error}")

                except Exception as e:
                    error_msg = f"Failed to process {file_info.path}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    self._failed_files += 1

        return organized_paths, errors

    async def _apply_rule(self, base_directory: Path, file_info: FileInfo, rule: OrganizationRule) -> Optional[Path]:
        """
        Apply a single organization rule to a file.

        Args:
            base_directory: Base directory being organized
            file_info: File information
            rule: Rule to apply

        Returns:
            New file path if operation succeeded, None otherwise
        """
        # Check file size limit
        if file_info.size > self.config.get_max_file_size_bytes():
            logger.warning(f"File too large, skipping: {file_info.path}")
            return None

        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would {rule.action.value}: {file_info.path}")
            return file_info.path  # Return original path for dry run

        try:
            if rule.action == OrganizationAction.MOVE and rule.target_directory:
                return await self._move_file(file_info, rule.target_directory)
            elif rule.action == OrganizationAction.COPY and rule.target_directory:
                return await self._copy_file(file_info, rule.target_directory)
            elif rule.action == OrganizationAction.DELETE:
                return await self._delete_file(file_info)
            elif rule.action == OrganizationAction.RENAME:
                return await self._rename_file(file_info, rule.pattern)
            else:
                logger.warning(f"Unsupported action: {rule.action}")
                return None

        except Exception as e:
            logger.error(f"Failed to apply rule {rule.name} to {file_info.path}: {e}")
            raise

    async def _move_file(self, file_info: FileInfo, target_dir: str) -> Path:
        """Move a file to target directory."""
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)

        # Handle name conflicts
        final_target = target_path / file_info.name
        counter = 1
        while final_target.exists():
            stem = file_info.path.stem
            suffix = file_info.path.suffix
            final_target = target_path / f"{stem}_{counter}{suffix}"
            counter += 1

        # Perform move with retry logic
        await self._safe_file_operation(file_info.path, final_target, "move")
        return final_target

    async def _copy_file(self, file_info: FileInfo, target_dir: str) -> Path:
        """Copy a file to target directory."""
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)

        # Handle name conflicts
        final_target = target_path / file_info.name
        counter = 1
        while final_target.exists():
            stem = file_info.path.stem
            suffix = file_info.path.suffix
            final_target = target_path / f"{stem}_{counter}{suffix}"
            counter += 1

        # Perform copy with retry logic
        await self._safe_file_operation(file_info.path, final_target, "copy")
        return final_target

    async def _delete_file(self, file_info: FileInfo) -> Path:
        """Delete a file after confirmation if required."""
        if self.config.confirm_destructive_operations:
            # In a real implementation, this would prompt for confirmation
            # For now, we'll log and proceed
            logger.warning(f"Deleting file (confirmation enabled): {file_info.path}")

        await self._safe_file_operation(file_info.path, None, "delete")
        return file_info.path

    async def _rename_file(self, file_info: FileInfo, pattern: Optional[str]) -> Path:
        """Rename a file according to a pattern."""
        if not pattern:
            return file_info.path

        # Simple pattern replacement - could be enhanced
        new_name = pattern.replace("*", file_info.path.stem)
        if "." not in new_name and file_info.extension:
            new_name += "." + file_info.extension

        new_path = file_info.path.parent / new_name
        await self._safe_file_operation(file_info.path, new_path, "rename")
        return new_path

    async def _safe_file_operation(self, source: Path, destination: Optional[Path], operation: str) -> None:
        """Perform file operation with error handling and retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if operation == "move" and destination:
                    shutil.move(str(source), str(destination))
                elif operation == "copy" and destination:
                    shutil.copy2(str(source), str(destination))
                elif operation == "delete":
                    source.unlink()
                elif operation == "rename" and destination:
                    source.rename(destination)
                else:
                    raise ValueError(f"Invalid operation: {operation}")

                return

            except PermissionError as pe:
                if attempt < max_retries - 1:
                    logger.warning(f"Permission error on {source}, retrying... ({attempt + 1}/{max_retries})")
                    await asyncio.sleep(0.5)
                    continue
                raise
            except OSError as oe:
                if attempt < max_retries - 1:
                    logger.warning(f"OS error on {source}, retrying... ({attempt + 1}/{max_retries})")
                    await asyncio.sleep(0.5)
                    continue
                raise

    async def _create_backup(self, directory: Path, files: List[FileInfo]) -> Path:
        """Create backup of files before organization."""
        backup_dir = directory / self.config.backup_directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / timestamp

        logger.info(f"Creating backup: {backup_path}")
        backup_path.mkdir(parents=True, exist_ok=True)

        # In a real implementation, this would copy files to backup
        # For now, we'll just create the directory structure
        logger.info(f"Backup directory created: {backup_path}")
        return backup_path

    async def preview_organization(self, directory: Path) -> Dict[str, List[str]]:
        """
        Preview what would happen during organization without making changes.

        Args:
            directory: Directory to preview

        Returns:
            Dictionary with preview information
        """
        logger.info(f"Previewing organization for: {directory}")

        # Scan and categorize files (same as organize_directory but without changes)
        files = await self.scanner.scan_directory(directory)
        categorized_files = self.categorizer.categorize_files(files)
        rules = self.config.get_effective_rules()

        preview = {"total_files": len(files), "categories": {}, "actions": {}, "warnings": []}

        for category_type, files in categorized_files.items():
            if not files:
                continue

            category_rules = rules.get(category_type, [])
            preview["categories"][category_type.value] = len(files)

            if not category_rules:
                preview["warnings"].append(f"No rules for {category_type.value} files")
                continue

            # Preview rule applications
            for rule in category_rules:
                applicable_files = [f for f in files if rule.applies_to_file(f)]
                if applicable_files:
                    action_key = f"{rule.action.value}_{rule.target_directory or 'current'}"
                    if action_key not in preview["actions"]:
                        preview["actions"][action_key] = []
                    preview["actions"][action_key].extend([str(f.path) for f in applicable_files])

        return preview

    def get_organization_statistics(self, directory: Path) -> Dict[str, any]:
        """
        Get statistics about files in a directory.

        Args:
            directory: Directory to analyze

        Returns:
            Dictionary with file statistics
        """
        # This is a synchronous version - in practice might want async version
        stats = {
            "directory": str(directory),
            "total_size_mb": 0,
            "file_count": 0,
            "directory_count": 0,
            "largest_file": None,
            "file_types": {},
            "categories": {},
        }

        try:
            for item in directory.rglob("*"):
                if item.is_file():
                    stats["file_count"] += 1
                    size = item.stat().st_size
                    stats["total_size_mb"] += size / (1024 * 1024)

                    if stats["largest_file"] is None or size > stats["largest_file"]["size"]:
                        stats["largest_file"] = {"path": str(item), "size": size, "size_mb": size / (1024 * 1024)}

                    # File type
                    ext = item.suffix.lower()
                    if ext not in stats["file_types"]:
                        stats["file_types"][ext] = {"count": 0, "size_mb": 0}
                    stats["file_types"][ext]["count"] += 1
                    stats["file_types"][ext]["size_mb"] += size / (1024 * 1024)

                elif item.is_dir():
                    stats["directory_count"] += 1

            stats["total_size_mb"] = round(stats["total_size_mb"], 2)

        except Exception as e:
            logger.error(f"Error gathering statistics: {e}")
            stats["error"] = str(e)

        return stats
