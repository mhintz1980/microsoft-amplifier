"""
Enhanced File Organizer - Main Orchestrator with ML Support

The primary orchestrator that coordinates all file organization operations
with ML-enhanced categorization capabilities. Integrates with the 4 core skills
and adds intelligent learning from user feedback.
"""

import asyncio
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ..models.file_models import (
    FileInfo,
    CategoryType,
    OrganizationResult,
    OrganizationRule,
    OrganizationAction,
    ScanProgress,
    Category,
)
from .config import FileOrganizerConfig
from .file_scanner import FileScanner
from .categorizer import BasicCategorizer
from ..ml.enhanced_categorizer import EnhancedCategorizer
from ..ml.models.learning_models import ConfidenceScore
from ..ml.models.feedback_models import UserFeedback, FeedbackType

logger = logging.getLogger(__name__)


class EnhancedFileOrganizer:
    """
    Enhanced file organizer with ML categorization and learning capabilities.

    Features:
    - ML-enhanced categorization with confidence scoring
    - Learning from user corrections and feedback
    - Content-based file analysis
    - Performance monitoring and recommendations
    - Backward compatibility with BasicCategorizer
    - Integration with 4 core skills (NodeJS, Security, Performance, Vite)
    """

    def __init__(
        self,
        config: Optional[FileOrganizerConfig] = None,
        enable_ml: bool = True,
        learning_data_path: Optional[Path] = None,
        confidence_threshold: float = 0.7,
    ):
        """
        Initialize the Enhanced File Organizer.

        Args:
            config: Optional configuration, uses default if not provided
            enable_ml: Whether to enable ML-enhanced categorization
            learning_data_path: Path to store learning data
            confidence_threshold: Minimum confidence for auto-categorization
        """
        self.config = config or FileOrganizerConfig()
        self.enable_ml = enable_ml
        self.confidence_threshold = confidence_threshold

        # Initialize components
        self.scanner = FileScanner(self.config.scanner)

        # Initialize categorizer based on ML preference
        if enable_ml:
            self.categorizer = EnhancedCategorizer(
                learning_data_path=learning_data_path, enable_learning=True, confidence_threshold=confidence_threshold
            )
            logger.info("Enhanced file organizer initialized with ML capabilities")
        else:
            self.categorizer = BasicCategorizer()
            logger.info("Enhanced file organizer initialized with basic categorization only")

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
        self._user_corrections = 0

        # ML-specific tracking
        self._categorization_results = []  # Store results for feedback processing

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
        self,
        directory: Path,
        progress_callback: Optional[callable] = None,
        feedback_callback: Optional[callable] = None,
    ) -> OrganizationResult:
        """
        Organize files in a directory according to configured rules.

        Args:
            directory: Directory path to organize
            progress_callback: Optional callback for progress updates
            feedback_callback: Optional callback for user feedback on low-confidence categorizations

        Returns:
            OrganizationResult with operation details
        """
        self._operation_start_time = datetime.now()
        self._processed_files = 0
        self._failed_files = 0
        self._skipped_files = 0
        self._categorization_results = []  # Reset for this operation

        logger.info(f"Starting enhanced organization of directory: {directory}")

        # Validate directory
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        # Check if directory is protected
        if self.config.is_directory_protected(directory):
            raise PermissionError(f"Directory is protected from modification: {directory}")

        try:
            # Scan files with progress tracking
            logger.info("Scanning directory for files...")
            file_infos = await self._scan_directory_with_progress(directory, progress_callback)

            if not file_infos:
                logger.warning("No files found to organize")
                return self._create_result([])

            # Categorize files with ML enhancement
            logger.info(
                f"Categorizing {len(file_infos)} files with {'ML' if self.enable_ml else 'basic'} categorization..."
            )
            categorized_files = await self._categorize_files_with_ml(file_infos, progress_callback)

            # Apply organization rules
            logger.info("Applying organization rules...")
            organized_paths = await self._apply_organization_rules(categorized_files, progress_callback)

            # Create and return result
            return self._create_result(organized_paths)

        except Exception as e:
            logger.error(f"Organization failed: {e}")
            return self._create_result([], [str(e)])

    async def _scan_directory_with_progress(
        self, directory: Path, progress_callback: Optional[callable]
    ) -> List[FileInfo]:
        """Scan directory with progress tracking."""
        file_infos = []

        async def scan_progress(progress: ScanProgress) -> None:
            if progress_callback:
                await progress_callback(f"Scanning: {progress.current_file} ({progress.files_scanned} files)")

        file_infos = await self.scanner.scan_directory(directory, scan_progress)
        logger.info(f"Found {len(file_infos)} files to process")

        return file_infos

    async def _categorize_files_with_ml(
        self, file_infos: List[FileInfo], progress_callback: Optional[callable]
    ) -> Dict[CategoryType, List[Tuple[FileInfo, Optional[ConfidenceScore]]]]:
        """Categorize files with ML enhancement and confidence tracking."""
        if self.enable_ml and isinstance(self.categorizer, EnhancedCategorizer):
            # Use enhanced categorizer with confidence scoring
            categorized = self.categorizer.categorize_files_batch(file_infos)

            # Extract confidence scores for tracking
            results_with_confidence = {}
            for category_type, files_with_confidence in categorized.items():
                results_with_confidence[category_type] = files_with_confidence

            # Store results for potential feedback
            self._categorization_results = [
                (file_info, category, confidence)
                for category_type, files in categorized.items()
                for file_info, confidence in files
                for category in [self.categorizer.get_category(category_type)]
                if category
            ]

            # Log categorization statistics
            auto_categorized = sum(
                1 for files in categorized.values() for _, conf in files if conf.overall >= self.confidence_threshold
            )
            logger.info(f"ML categorization: {auto_categorized}/{len(file_infos)} files auto-categorized")

            # Convert to expected format
            return {
                category_type: [(file_info, confidence) for file_info, confidence in files]
                for category_type, files in categorized.items()
            }

        else:
            # Use basic categorizer (no confidence scores)
            categorized = self.categorizer.categorize_files(file_infos)

            # Convert to expected format with None confidence
            return {
                category_type: [(file_info, None) for file_info in files]
                for category_type, files in categorized.items()
            }

    async def _apply_organization_rules(
        self,
        categorized_files: Dict[CategoryType, List[Tuple[FileInfo, Optional[ConfidenceScore]]]],
        progress_callback: Optional[callable],
    ) -> List[Dict[str, Union[str, Path]]]:
        """Apply organization rules to categorized files."""
        organized_paths = []

        for category_type, files_with_confidence in categorized_files.items():
            if not files_with_confidence:
                continue

            category = self.categorizer.get_category(category_type)
            if not category:
                continue

            for file_info, confidence in files_with_confidence:
                try:
                    # Check if we should process this file based on confidence
                    if confidence and not self.categorizer.should_auto_categorize(confidence):
                        logger.info(
                            f"Skipping low-confidence file: {file_info.name} (confidence: {confidence.overall:.2f})"
                        )
                        self._skipped_files += 1
                        continue

                    # Apply organization rules
                    result = await self._organize_single_file(file_info, category)
                    if result:
                        organized_paths.append(result)
                        self._processed_files += 1
                    else:
                        self._skipped_files += 1

                except Exception as e:
                    logger.error(f"Failed to organize {file_info.path}: {e}")
                    self._failed_files += 1

                # Progress update
                if progress_callback:
                    await progress_callback(f"Organized: {file_info.name} ({self._processed_files} files)")

        return organized_paths

    async def _organize_single_file(
        self, file_info: FileInfo, category: Category
    ) -> Optional[Dict[str, Union[str, Path]]]:
        """Organize a single file according to category rules."""
        # Find applicable organization rules
        applicable_rules = [
            rule
            for rule in self.config.organization_rules
            if rule.applies_to_file(file_info) and rule.category_type == category.type
        ]

        # Apply first matching rule or default behavior
        if applicable_rules:
            rule = applicable_rules[0]
            return await self._apply_rule(file_info, rule)
        else:
            # Default: move to category's target directory
            if category.target_directory:
                return await self._move_to_directory(file_info, category.target_directory)

        return None

    async def _apply_rule(self, file_info: FileInfo, rule: OrganizationRule) -> Optional[Dict[str, Union[str, Path]]]:
        """Apply a specific organization rule to a file."""
        if rule.action == OrganizationAction.MOVE and rule.target_directory:
            return await self._move_to_directory(file_info, rule.target_directory)
        elif rule.action == OrganizationAction.COPY and rule.target_directory:
            return await self._copy_to_directory(file_info, rule.target_directory)
        elif rule.action == OrganizationAction.DELETE:
            await self._delete_file(file_info)
            return {"action": "delete", "path": file_info.path}
        elif rule.action == OrganizationAction.RENAME:
            return await self._rename_file(file_info)
        # NONE action - no changes
        return None

    async def _move_to_directory(
        self, file_info: FileInfo, target_dir_name: str
    ) -> Optional[Dict[str, Union[str, Path]]]:
        """Move file to target directory."""
        # Security check: ensure target directory is within reasonable bounds
        target_path = file_info.path.parent / target_dir_name / file_info.name

        # Check if this would move outside expected bounds
        if self.config.is_directory_protected(target_path.parent):
            logger.warning(f"Target directory is protected: {target_path.parent}")
            return None

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if file already exists at target
            if target_path.exists():
                target_path = self._get_unique_filename(target_path)

            shutil.move(str(file_info.path), str(target_path))

            return {"action": "move", "from": file_info.path, "to": target_path}

        except Exception as e:
            logger.error(f"Failed to move {file_info.path}: {e}")
            return None

    async def _copy_to_directory(
        self, file_info: FileInfo, target_dir_name: str
    ) -> Optional[Dict[str, Union[str, Path]]]:
        """Copy file to target directory."""
        target_path = file_info.path.parent / target_dir_name / file_info.name

        if self.config.is_directory_protected(target_path.parent):
            logger.warning(f"Target directory is protected: {target_path.parent}")
            return None

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)

            if target_path.exists():
                target_path = self._get_unique_filename(target_path)

            shutil.copy2(str(file_info.path), str(target_path))

            return {"action": "copy", "from": file_info.path, "to": target_path}

        except Exception as e:
            logger.error(f"Failed to copy {file_info.path}: {e}")
            return None

    async def _delete_file(self, file_info: FileInfo) -> None:
        """Delete a file safely."""
        if self.config.protect_system_files and file_info.extension in ["exe", "dll", "sys"]:
            logger.warning(f"Refusing to delete system file: {file_info.path}")
            return

        try:
            file_info.path.unlink()
            logger.info(f"Deleted file: {file_info.path}")

        except Exception as e:
            logger.error(f"Failed to delete {file_info.path}: {e}")

    async def _rename_file(self, file_info: FileInfo) -> Optional[Dict[str, Union[str, Path]]]:
        """Rename file according to naming rules."""
        # This is a simplified implementation
        # In a real system, you'd have configurable naming patterns
        new_name = f"{file_info.stem}_organized{file_info.suffix}"
        new_path = file_info.path.parent / new_name

        try:
            if new_path.exists():
                new_path = self._get_unique_filename(new_path)

            file_info.path.rename(new_path)

            return {"action": "rename", "from": file_info.path, "to": new_path}

        except Exception as e:
            logger.error(f"Failed to rename {file_info.path}: {e}")
            return None

    def _get_unique_filename(self, path: Path) -> Path:
        """Generate unique filename if file already exists."""
        counter = 1
        stem = path.stem
        suffix = path.suffix
        parent = path.parent

        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    def _create_result(
        self, organized_paths: List[Dict[str, Union[str, Path]]], errors: List[str] = None
    ) -> OrganizationResult:
        """Create organization result object."""
        end_time = datetime.now()
        duration = (end_time - self._operation_start_time).total_seconds()

        return OrganizationResult(
            success=len(errors or []) == 0,
            total_files=self._processed_files + self._failed_files + self._skipped_files,
            organized_files=self._processed_files,
            failed_files=self._failed_files,
            skipped_files=self._skipped_files,
            errors=errors or [],
            organized_paths=organized_paths,
            duration_seconds=duration,
        )

    def process_user_feedback(
        self,
        file_path: Path,
        predicted_category: CategoryType,
        correct_category: CategoryType,
        user_comment: Optional[str] = None,
    ) -> bool:
        """
        Process user feedback to improve ML categorization.

        Args:
            file_path: Path to the file that was categorized
            predicted_category: ML-predicted category
            correct_category: User-corrected category
            user_comment: Optional user comment

        Returns:
            True if feedback processed successfully, False otherwise
        """
        if not self.enable_ml or not isinstance(self.categorizer, EnhancedCategorizer):
            logger.warning("ML categorization disabled - feedback not processed")
            return False

        # Find the file info for this path
        file_info = None
        confidence = None

        for info, cat, conf in self._categorization_results:
            if info.path == file_path:
                file_info = info
                confidence = conf
                break

        if not file_info:
            # Create minimal file info if not found in results
            file_info = FileInfo(
                path=file_path,
                name=file_path.name,
                size=file_path.stat().st_size if file_path.exists() else 0,
                is_file=True,
                is_directory=False,
                extension=file_path.suffix.lower().lstrip("."),
                created_time=datetime.fromtimestamp(file_path.stat().st_ctime)
                if file_path.exists()
                else datetime.now(),
                modified_time=datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_path.exists()
                else datetime.now(),
                accessed_time=datetime.fromtimestamp(file_path.stat().st_atime)
                if file_path.exists()
                else datetime.now(),
            )

        if not confidence:
            confidence = ConfidenceScore(overall=0.5)

        # Process feedback through enhanced categorizer
        success = self.categorizer.process_user_feedback(
            file_info, predicted_category, correct_category, confidence, user_comment
        )

        if success:
            self._user_corrections += 1
            logger.info(f"Processed user feedback #{self._user_corrections} for {file_path.name}")

        return success

    def get_categorization_statistics(self) -> Dict[str, Union[int, float, str]]:
        """
        Get comprehensive categorization statistics.

        Returns:
            Dictionary with statistics
        """
        stats = {
            "ml_enabled": self.enable_ml,
            "confidence_threshold": self.confidence_threshold,
            "user_corrections": self._user_corrections,
            "processed_files": self._processed_files,
            "failed_files": self._failed_files,
            "skipped_files": self._skipped_files,
        }

        # Add ML-specific statistics
        if self.enable_ml and isinstance(self.categorizer, EnhancedCategorizer):
            ml_stats = self.categorizer.get_categorization_statistics()
            stats.update(ml_stats)

        return stats

    def get_recommendations(self) -> Dict[str, List[str]]:
        """
        Get recommendations for improving categorization.

        Returns:
            Dictionary with recommendations
        """
        recommendations = {"general": [], "ml_specific": [], "configuration": []}

        if self.enable_ml and isinstance(self.categorizer, EnhancedCategorizer):
            # Get ML recommendations
            file_infos = [info for info, _, _ in self._categorization_results]
            if file_infos:
                ml_recs = self.categorizer.get_recommendations(file_infos)
                recommendations["ml_specific"].extend(ml_recs.get("learning_suggestions", []))
                recommendations["ml_specific"].extend(ml_recs.get("confidence_improvements", []))

        # General recommendations
        if self._failed_files > 0:
            recommendations["general"].append(f"Address {self._failed_files} failed organization attempts")

        if self._user_corrections > 0:
            correction_rate = self._user_corrections / max(self._processed_files, 1)
            if correction_rate > 0.2:
                recommendations["ml_specific"].append(
                    f"High correction rate ({correction_rate:.1%}) - consider providing more feedback"
                )

        return recommendations

    def export_learning_data(self, export_path: Path) -> bool:
        """
        Export learning data for backup or analysis.

        Args:
            export_path: Path to export data

        Returns:
            True if export successful, False otherwise
        """
        if self.enable_ml and isinstance(self.categorizer, EnhancedCategorizer):
            return self.categorizer.export_learning_data(export_path)
        return False

    # Compatibility methods
    def get_category(self, category_type: CategoryType) -> Optional[Category]:
        """Get category from categorizer."""
        return self.categorizer.get_category(category_type)

    def get_all_categories(self) -> List[Category]:
        """Get all categories from categorizer."""
        return self.categorizer.get_all_categories()
