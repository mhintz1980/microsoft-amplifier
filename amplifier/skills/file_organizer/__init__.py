"""
File Organizer Skill

A modular file organization system that integrates with the 4 core skills:
- NodeJS Expert: File operations and path handling
- Security Expert: Safe file handling and permissions
- Performance Expert: Efficient scanning and progress tracking
- Vite Expert: Build-ready module structure

Enhanced with ML capabilities:
- Confidence-based categorization with intelligent learning
- Content analysis for accurate file classification
- User feedback processing for continuous improvement
- Pattern recognition and adaptive rule generation

Basic Usage:
    >>> from amplifier.skills.file_organizer import FileOrganizer
    >>> organizer = FileOrganizer()
    >>> result = await organizer.organize_directory("/path/to/files")

Enhanced Usage with ML:
    >>> from amplifier.skills.file_organizer import EnhancedFileOrganizer
    >>> organizer = EnhancedFileOrganizer(enable_ml=True, confidence_threshold=0.7)
    >>> result = await organizer.organize_directory("/path/to/files")
    >>>
    >>> # Process user feedback to improve accuracy
    >>> organizer.process_user_feedback(
    ...     file_path=Path("/path/to/file.pdf"),
    ...     predicted_category=CategoryType.CODE,
    ...     correct_category=CategoryType.DOCUMENTS,
    ...     user_comment="This is actually a document, not code"
    ... )
"""

from .core.file_organizer import FileOrganizer
from .core.enhanced_file_organizer import EnhancedFileOrganizer
from .core.cloud_enhanced_organizer import CloudEnhancedFileOrganizer
from .core.config import FileOrganizerConfig
from .models.file_models import FileInfo, Category, CategoryType, OrganizationRule
from .ml import EnhancedCategorizer, LearningEngine, ContentAnalyzer
from .cloud import CloudSyncManager, SyncConfig, CloudConfig, CloudProvider, SyncDirection

__all__ = [
    "FileOrganizer",
    "EnhancedFileOrganizer",
    "CloudEnhancedFileOrganizer",  # Phase 3: Integrated cloud + organization
    "FileOrganizerConfig",
    "FileInfo",
    "Category",
    "CategoryType",
    "OrganizationRule",
    "EnhancedCategorizer",
    "LearningEngine",
    "ContentAnalyzer",
    # Phase 3: Cloud Sync components
    "CloudSyncManager",
    "SyncConfig",
    "CloudConfig",
    "CloudProvider",
    "SyncDirection",
]
