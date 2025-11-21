"""
File Organizer Configuration Module

Handles configuration management with integration with the Vite Expert
skill for build-ready configuration structure.
"""

import json
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from ..models.file_models import Category, CategoryType, OrganizationRule, OrganizationAction, FileScannerConfig


logger = logging.getLogger(__name__)


class FileOrganizerConfig(BaseModel):
    """Main configuration class for the File Organizer system."""

    # Scanner configuration
    scanner: FileScannerConfig = Field(default_factory=FileScannerConfig)

    # Organization settings
    dry_run: bool = Field(True, description="Perform dry run without making actual changes")
    backup_enabled: bool = Field(True, description="Create backups before file operations")
    backup_directory: str = Field(".organizer_backup", description="Backup directory name")
    max_concurrent_operations: int = Field(5, description="Maximum concurrent file operations", ge=1, le=50)

    # Logging and monitoring
    log_level: str = Field("INFO", description="Logging level")
    log_file: Optional[str] = Field(None, description="Optional log file path")
    progress_reporting: bool = Field(True, description="Enable progress reporting")

    # Safety settings
    confirm_destructive_operations: bool = Field(True, description="Confirm before delete operations")
    protected_directories: List[str] = Field(
        default_factory=lambda: [
            "/bin",
            "/sbin",
            "/usr",
            "/etc",
            "/var",
            "/sys",
            "/proc",
            "/dev",
            "C:\\Windows",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
        ],
        description="Directories that cannot be modified",
    )
    max_file_size_mb: float = Field(1024.0, description="Maximum file size to process in MB", ge=1.0)

    # Custom categories and rules
    custom_categories: List[Category] = Field(default_factory=list)
    organization_rules: List[OrganizationRule] = Field(default_factory=list)

    # NodeJS integration settings
    use_nodejs_operations: bool = Field(True, description="Use NodeJS for file operations")
    nodejs_timeout_seconds: int = Field(30, description="Timeout for NodeJS operations", ge=1)

    # Performance settings
    enable_performance_monitoring: bool = Field(True, description="Enable performance monitoring")
    memory_limit_mb: int = Field(512, description="Memory limit in MB", ge=64)

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @validator("protected_directories")
    def validate_protected_directories(cls, v):
        """Validate protected directories are absolute paths."""
        for directory in v:
            if not Path(directory).is_absolute():
                raise ValueError(f"Protected directory must be absolute: {directory}")
        return v

    class Config:
        extra = "allow"  # Allow additional fields for extensibility
        json_encoders = {Path: lambda v: str(v)}

    @classmethod
    def from_file(cls, config_path: Path) -> "FileOrganizerConfig":
        """
        Load configuration from a JSON or YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            FileOrganizerConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                if config_path.suffix.lower() in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                elif config_path.suffix.lower() == ".json":
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")

            return cls(**data)

        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            raise ValueError(f"Invalid configuration file: {e}")

    def to_file(self, config_path: Path, format: str = "json") -> None:
        """
        Save configuration to a file.

        Args:
            config_path: Path to save configuration
            format: File format ('json' or 'yaml')

        Raises:
            ValueError: If format is not supported
        """
        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = self.dict()

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                if format.lower() == "yaml":
                    yaml.dump(data, f, default_flow_style=False, indent=2)
                elif format.lower() == "json":
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Configuration saved to {config_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
            raise

    def add_organization_rule(self, rule: OrganizationRule) -> None:
        """Add an organization rule to the configuration."""
        self.organization_rules.append(rule)

    def remove_organization_rule(self, rule_name: str) -> bool:
        """Remove an organization rule by name."""
        for i, rule in enumerate(self.organization_rules):
            if rule.name == rule_name:
                del self.organization_rules[i]
                return True
        return False

    def get_rules_for_category(self, category_type: CategoryType) -> List[OrganizationRule]:
        """Get all rules for a specific category."""
        return [rule for rule in self.organization_rules if rule.category_type == category_type]

    def validate_configuration(self) -> List[str]:
        """
        Validate the configuration for potential issues.

        Returns:
            List of validation warnings
        """
        warnings = []

        # Check backup directory
        backup_path = Path(self.backup_directory)
        if backup_path.exists() and not backup_path.is_dir():
            warnings.append(f"Backup path exists but is not a directory: {backup_path}")

        # Check protected directories
        for protected_dir in self.protected_directories:
            if not Path(protected_dir).exists():
                warnings.append(f"Protected directory does not exist: {protected_dir}")

        # Check organization rules for conflicts
        rule_names = [rule.name for rule in self.organization_rules]
        if len(rule_names) != len(set(rule_names)):
            warnings.append("Duplicate rule names found in organization rules")

        # Check custom categories for conflicts
        for category in self.custom_categories:
            if not category.target_directory:
                warnings.append(f"Custom category '{category.name}' has no target directory")

        return warnings

    def get_effective_rules(self) -> Dict[CategoryType, List[OrganizationRule]]:
        """
        Get effective rules combining defaults with custom rules.

        Returns:
            Dictionary mapping category types to their effective rules
        """
        # Create default rules for each category type
        default_rules = {
            CategoryType.DOCUMENTS: [
                OrganizationRule(
                    name="Move documents to documents folder",
                    category_type=CategoryType.DOCUMENTS,
                    action=OrganizationAction.MOVE,
                    target_directory="documents",
                )
            ],
            CategoryType.IMAGES: [
                OrganizationRule(
                    name="Move images to images folder",
                    category_type=CategoryType.IMAGES,
                    action=OrganizationAction.MOVE,
                    target_directory="images",
                )
            ],
            CategoryType.VIDEOS: [
                OrganizationRule(
                    name="Move videos to videos folder",
                    category_type=CategoryType.VIDEOS,
                    action=OrganizationAction.MOVE,
                    target_directory="videos",
                )
            ],
            CategoryType.AUDIO: [
                OrganizationRule(
                    name="Move audio to audio folder",
                    category_type=CategoryType.AUDIO,
                    action=OrganizationAction.MOVE,
                    target_directory="audio",
                )
            ],
            CategoryType.CODE: [
                OrganizationRule(
                    name="Move code to code folder",
                    category_type=CategoryType.CODE,
                    action=OrganizationAction.MOVE,
                    target_directory="code",
                )
            ],
            CategoryType.ARCHIVES: [
                OrganizationRule(
                    name="Move archives to archives folder",
                    category_type=CategoryType.ARCHIVES,
                    action=OrganizationAction.MOVE,
                    target_directory="archives",
                )
            ],
            CategoryType.TEMPORARY: [
                OrganizationRule(
                    name="Delete temporary files",
                    category_type=CategoryType.TEMPORARY,
                    action=OrganizationAction.DELETE,
                )
            ],
        }

        # Override with custom rules
        for rule in self.organization_rules:
            if rule.category_type not in default_rules:
                default_rules[rule.category_type] = []
            default_rules[rule.category_type].append(rule)

        return default_rules

    def create_default_config_file(self, config_path: Path) -> None:
        """
        Create a default configuration file for users to customize.

        Args:
            config_path: Path where to create the config file
        """
        default_config = FileOrganizerConfig()
        default_config.to_file(config_path, format="yaml")

        # Add comments and documentation
        with open(config_path, "r") as f:
            content = f.read()

        # Add header comments
        header = """# File Organizer Configuration
# This file controls how the File Organizer system operates
# For detailed documentation, see the README.md file

"""
        with open(config_path, "w") as f:
            f.write(header + content)

    def is_directory_protected(self, directory: Path) -> bool:
        """
        Check if a directory is protected from modifications.

        Args:
            directory: Directory path to check

        Returns:
            True if directory is protected
        """
        dir_str = str(directory.resolve())
        for protected in self.protected_directories:
            if dir_str.startswith(str(Path(protected).resolve())):
                return True
        return False

    def get_memory_limit_bytes(self) -> int:
        """Get memory limit in bytes."""
        return int(self.memory_limit_mb * 1024 * 1024)

    def get_max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return int(self.max_file_size_mb * 1024 * 1024)
