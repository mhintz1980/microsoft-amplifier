"""
Documentation Version Management System

Tracks skill evolution and maintains documentation consistency across versions.
Handles version control integration and documentation evolution.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path
import json
import difflib
import hashlib
from semver import VersionInfo

from ..utils.token_utils import estimate_tokens


class ChangeType(Enum):
    """Types of changes in documentation."""

    MAJOR = "major"  # Breaking changes
    MINOR = "minor"  # New features, compatible changes
    PATCH = "patch"  # Bug fixes, documentation improvements
    REFACTOR = "refactor"  # Code refactoring without functional changes
    DEPRECATED = "deprecated"  # Marked as deprecated
    REMOVED = "removed"  # Removed functionality


@dataclass
class DocumentationChange:
    """A change to documentation between versions."""

    version_from: str
    version_to: str
    change_type: ChangeType
    description: str
    affected_sections: List[str] = field(default_factory=list)
    breaking_change: bool = False
    migration_notes: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    author: Optional[str] = None
    commit_hash: Optional[str] = None


@dataclass
class VersionInfo:
    """Information about a specific version of skill documentation."""

    version: str
    skill_name: str
    timestamp: datetime
    content_hash: str
    documentation: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    changelog: List[DocumentationChange] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)  # skill_name -> version
    compatibility_matrix: Dict[str, bool] = field(default_factory=dict)  # version -> compatible


class DocumentationVersionManager:
    """Manages versioning and evolution of skill documentation."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path(__file__).parent.parent / "data" / "versions"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.versions: Dict[str, Dict[str, VersionInfo]] = {}  # skill_name -> version -> info
        self.current_versions: Dict[str, str] = {}  # skill_name -> current version

        self._load_versions()

    def create_version(
        self,
        skill_name: str,
        documentation: Dict[str, Any],
        version_type: str = "patch",
        changes: Optional[List[DocumentationChange]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VersionInfo:
        """Create a new version of skill documentation."""

        # Generate version number
        current_version = self.current_versions.get(skill_name, "0.0.0")
        new_version = self._increment_version(current_version, version_type)

        # Generate content hash
        content_hash = self._generate_content_hash(documentation)

        # Create version info
        version_info = VersionInfo(
            version=new_version,
            skill_name=skill_name,
            timestamp=datetime.now(),
            content_hash=content_hash,
            documentation=documentation.copy(),
            metadata=metadata or {},
            changelog=changes or [],
        )

        # Store version
        if skill_name not in self.versions:
            self.versions[skill_name] = {}

        self.versions[skill_name][new_version] = version_info
        self.current_versions[skill_name] = new_version

        # Update compatibility matrix
        self._update_compatibility_matrix(skill_name, new_version)

        # Save to disk
        self._save_versions()

        return version_info

    def get_version(self, skill_name: str, version: Optional[str] = None) -> Optional[VersionInfo]:
        """Get documentation for a specific version."""

        if skill_name not in self.versions:
            return None

        if version is None:
            version = self.current_versions.get(skill_name)
            if version is None:
                return None

        return self.versions[skill_name].get(version)

    def list_versions(self, skill_name: str) -> List[VersionInfo]:
        """List all versions for a skill."""

        if skill_name not in self.versions:
            return []

        versions = list(self.versions[skill_name].values())
        versions.sort(key=lambda v: VersionInfo.parse(v.version), reverse=True)

        return versions

    def compare_versions(self, skill_name: str, version_from: str, version_to: str) -> Dict[str, Any]:
        """Compare two versions of documentation."""

        from_version = self.get_version(skill_name, version_from)
        to_version = self.get_version(skill_name, version_to)

        if not from_version or not to_version:
            raise ValueError(f"Version not found for skill {skill_name}")

        comparison = {
            "skill_name": skill_name,
            "version_from": version_from,
            "version_to": version_to,
            "changes": self._detect_changes(from_version, to_version),
            "token_diff": self._calculate_token_diff(from_version, to_version),
            "section_changes": self._analyze_section_changes(from_version, to_version),
            "metadata_changes": self._analyze_metadata_changes(from_version, to_version),
        }

        return comparison

    def generate_changelog(
        self, skill_name: str, from_version: Optional[str] = None, to_version: Optional[str] = None
    ) -> List[DocumentationChange]:
        """Generate changelog between versions."""

        if from_version is None:
            # Get earliest version
            versions = self.list_versions(skill_name)
            if versions:
                from_version = versions[-1].version
            else:
                return []

        if to_version is None:
            to_version = self.current_versions.get(skill_name, from_version)

        # Collect all changes between versions
        changes = []
        versions = self.list_versions(skill_name)

        # Find versions in range
        from_vinfo = VersionInfo.parse(from_version)
        to_vinfo = VersionInfo.parse(to_version)

        for version_info in reversed(versions):
            vinfo = VersionInfo.parse(version_info.version)

            if from_vinfo <= vinfo <= to_vinfo:
                changes.extend(version_info.changelog)

        # Sort by timestamp
        changes.sort(key=lambda c: c.timestamp, reverse=True)

        return changes

    def check_compatibility(self, skill_name: str, version1: str, version2: str) -> bool:
        """Check if two versions are compatible."""

        v1_info = self.get_version(skill_name, version1)
        v2_info = self.get_version(skill_name, version2)

        if not v1_info or not v2_info:
            return False

        # Check compatibility matrix
        return v2_info.compatibility_matrix.get(version1, True)

    def upgrade_documentation(
        self, skill_name: str, from_version: str, to_version: str
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Upgrade documentation from one version to another."""

        from_info = self.get_version(skill_name, from_version)
        to_info = self.get_version(skill_name, to_version)

        if not from_info or not to_info:
            raise ValueError(f"Version not found for skill {skill_name}")

        upgrade_notes = []

        # Get changes between versions
        changes = self.generate_changelog(skill_name, from_version, to_version)

        # Check for breaking changes
        breaking_changes = [c for c in changes if c.breaking_change]
        if breaking_changes:
            upgrade_notes.append(f"⚠️  {len(breaking_changes)} breaking changes detected")

        for change in breaking_changes:
            upgrade_notes.append(f"  - {change.description}")
            if change.migration_notes:
                upgrade_notes.append(f"    Migration: {change.migration_notes}")

        # Apply automatic upgrades where possible
        upgraded_docs = self._apply_automatic_upgrades(from_info.documentation, changes)

        return upgraded_docs, upgrade_notes

    def rollback_version(self, skill_name: str, target_version: str) -> VersionInfo:
        """Rollback to a previous version."""

        if skill_name not in self.versions or target_version not in self.versions[skill_name]:
            raise ValueError(f"Version {target_version} not found for skill {skill_name}")

        # Create rollback change entry
        current_version = self.current_versions.get(skill_name, "0.0.0")

        rollback_change = DocumentationChange(
            version_from=current_version,
            version_to=target_version,
            change_type=ChangeType.PATCH,
            description=f"Rollback from {current_version} to {target_version}",
            affected_sections=["all"],
            author="system",
        )

        # Set as current version
        version_info = self.versions[skill_name][target_version]
        version_info.changelog.append(rollback_change)

        self.current_versions[skill_name] = target_version
        self._save_versions()

        return version_info

    def merge_versions(
        self, skill_name: str, base_version: str, version1: str, version2: str
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Merge two divergent versions of documentation."""

        base_info = self.get_version(skill_name, base_version)
        v1_info = self.get_version(skill_name, version1)
        v2_info = self.get_version(skill_name, version2)

        if not all([base_info, v1_info, v2_info]):
            raise ValueError("One or more versions not found")

        merge_notes = []

        # Analyze conflicts
        conflicts = self._detect_merge_conflicts(base_info, v1_info, v2_info)

        if conflicts:
            merge_notes.append(f"⚠️  {len(conflicts)} merge conflicts detected")
            for conflict in conflicts:
                merge_notes.append(f"  - {conflict}")

        # Attempt automatic merge
        merged_docs = self._merge_documentations(base_info.documentation, v1_info.documentation, v2_info.documentation)

        return merged_docs, merge_notes

    def _increment_version(self, current_version: str, version_type: str) -> str:
        """Increment version number based on change type."""

        try:
            vinfo = VersionInfo.parse(current_version)

            if version_type == "major":
                vinfo = vinfo.bump_major()
            elif version_type == "minor":
                vinfo = vinfo.bump_minor()
            elif version_type == "patch":
                vinfo = vinfo.bump_patch()
            else:
                raise ValueError(f"Invalid version type: {version_type}")

            return str(vinfo)

        except ValueError:
            # If parsing fails, start with 1.0.0
            return "1.0.0"

    def _generate_content_hash(self, documentation: Dict[str, Any]) -> str:
        """Generate hash for documentation content."""

        # Create deterministic string representation
        content_str = json.dumps(documentation, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]

    def _detect_changes(self, from_version: VersionInfo, to_version: VersionInfo) -> List[Dict[str, Any]]:
        """Detect changes between two versions."""

        changes = []

        # Compare content hashes
        if from_version.content_hash == to_version.content_hash:
            return changes

        # Analyze section changes
        from_sections = from_version.documentation.get("sections", {})
        to_sections = to_version.documentation.get("sections", {})

        all_sections = set(from_sections.keys()) | set(to_sections.keys())

        for section in all_sections:
            from_content = from_sections.get(section, "")
            to_content = to_sections.get(section, "")

            if from_content != to_content:
                # Calculate diff
                diff = list(
                    difflib.unified_diff(
                        from_content.splitlines(keepends=True),
                        to_content.splitlines(keepends=True),
                        fromfile=f"{from_version.version}/{section}",
                        tofile=f"{to_version.version}/{section}",
                        n=3,
                    )
                )

                changes.append(
                    {
                        "section": section,
                        "type": "modified" if section in from_sections else "added",
                        "lines_changed": len([line for line in diff if line.startswith("+") or line.startswith("-")]),
                        "diff_preview": "".join(diff[:20]),  # Limit preview
                    }
                )

        return changes

    def _calculate_token_diff(self, from_version: VersionInfo, to_version: VersionInfo) -> Dict[str, int]:
        """Calculate token count differences between versions."""

        from_tokens = self._count_tokens(from_version.documentation)
        to_tokens = self._count_tokens(to_version.documentation)

        return {
            "from_total": from_tokens["total"],
            "to_total": to_tokens["total"],
            "total_diff": to_tokens["total"] - from_tokens["total"],
            "sections": {
                section: to_tokens[section] - from_tokens.get(section, 0)
                for section in set(from_tokens) | set(to_tokens)
                if section != "total"
            },
        }

    def _analyze_section_changes(self, from_version: VersionInfo, to_version: VersionInfo) -> Dict[str, Any]:
        """Analyze detailed changes in sections."""

        from_sections = from_version.documentation.get("sections", {})
        to_sections = to_version.documentation.get("sections", {})

        analysis = {"added": [], "removed": [], "modified": [], "unchanged": []}

        all_sections = set(from_sections.keys()) | set(to_sections.keys())

        for section in all_sections:
            from_content = from_sections.get(section, "")
            to_content = to_sections.get(section, "")

            if section not in from_sections:
                analysis["added"].append(section)
            elif section not in to_sections:
                analysis["removed"].append(section)
            elif from_content != to_content:
                analysis["modified"].append(
                    {
                        "section": section,
                        "from_length": len(from_content),
                        "to_length": len(to_content),
                        "similarity": difflib.SequenceMatcher(None, from_content, to_content).ratio(),
                    }
                )
            else:
                analysis["unchanged"].append(section)

        return analysis

    def _analyze_metadata_changes(self, from_version: VersionInfo, to_version: VersionInfo) -> Dict[str, Any]:
        """Analyze changes in metadata."""

        from_meta = from_version.metadata
        to_meta = to_version.metadata

        changes = {"added": {}, "removed": {}, "modified": {}}

        all_keys = set(from_meta.keys()) | set(to_meta.keys())

        for key in all_keys:
            if key not in from_meta:
                changes["added"][key] = to_meta[key]
            elif key not in to_meta:
                changes["removed"][key] = from_meta[key]
            elif from_meta[key] != to_meta[key]:
                changes["modified"][key] = {"from": from_meta[key], "to": to_meta[key]}

        return changes

    def _update_compatibility_matrix(self, skill_name: str, new_version: str) -> None:
        """Update compatibility matrix for new version."""

        if skill_name not in self.versions:
            return

        new_vinfo = self.versions[skill_name][new_version]

        # Check compatibility with existing versions
        for existing_version, existing_vinfo in self.versions[skill_name].items():
            if existing_version == new_version:
                continue

            # Determine compatibility based on semantic versioning
            try:
                new_semver = VersionInfo.parse(new_version)
                existing_semver = VersionInfo.parse(existing_version)

                # Major version changes are breaking
                if new_semver.major != existing_semver.major:
                    compatible = False
                else:
                    compatible = True

                # Update both directions
                new_vinfo.compatibility_matrix[existing_version] = compatible
                existing_vinfo.compatibility_matrix[new_version] = compatible

            except ValueError:
                # Fallback to assuming compatibility
                new_vinfo.compatibility_matrix[existing_version] = True
                existing_vinfo.compatibility_matrix[new_version] = True

    def _apply_automatic_upgrades(
        self, documentation: Dict[str, Any], changes: List[DocumentationChange]
    ) -> Dict[str, Any]:
        """Apply automatic upgrades to documentation."""

        upgraded_docs = documentation.copy()

        for change in changes:
            if change.change_type == ChangeType.PATCH:
                # Patch changes can usually be applied automatically
                self._apply_patch_change(upgraded_docs, change)

        return upgraded_docs

    def _apply_patch_change(self, documentation: Dict[str, Any], change: DocumentationChange) -> None:
        """Apply a patch change to documentation."""

        # This would contain logic for automatic patch application
        # For now, just mark that the change was considered
        pass

    def _detect_merge_conflicts(self, base_info: VersionInfo, v1_info: VersionInfo, v2_info: VersionInfo) -> List[str]:
        """Detect conflicts between two divergent versions."""

        conflicts = []

        base_sections = base_info.documentation.get("sections", {})
        v1_sections = v1_info.documentation.get("sections", {})
        v2_sections = v2_info.documentation.get("sections", {})

        # Check for conflicting changes in same sections
        for section in set(v1_sections.keys()) & set(v2_sections.keys()):
            v1_content = v1_sections[section]
            v2_content = v2_sections[section]
            base_content = base_sections.get(section, "")

            # If both changed from base and are different, there's a conflict
            if v1_content != base_content and v2_content != base_content and v1_content != v2_content:
                conflicts.append(f"Conflicting changes in section '{section}'")

        return conflicts

    def _merge_documentations(
        self, base_docs: Dict[str, Any], v1_docs: Dict[str, Any], v2_docs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Attempt to merge three-way documentation."""

        merged = base_docs.copy()

        # Merge sections
        base_sections = base_docs.get("sections", {})
        v1_sections = v1_docs.get("sections", {})
        v2_sections = v2_docs.get("sections", {})

        merged_sections = {}

        all_sections = set(base_sections.keys()) | set(v1_sections.keys()) | set(v2_sections.keys())

        for section in all_sections:
            base_content = base_sections.get(section, "")
            v1_content = v1_sections.get(section, "")
            v2_content = v2_sections.get(section, "")

            # Simple merge strategy: prefer non-base content
            if v1_content == base_content:
                merged_sections[section] = v2_content
            elif v2_content == base_content:
                merged_sections[section] = v1_content
            elif v1_content == v2_content:
                merged_sections[section] = v1_content
            else:
                # Conflict - use v1 content with conflict marker
                merged_sections[section] = f"""<!-- MERGE CONFLICT -->
{v1_content}

<!-- ALTERNATIVE VERSION -->
{v2_content}
<!-- END CONFLICT -->"""

        merged["sections"] = merged_sections

        return merged

    def _count_tokens(self, documentation: Dict[str, Any]) -> Dict[str, int]:
        """Count tokens in documentation by section."""

        counts = {}

        # Count sections
        sections = documentation.get("sections", {})
        for section_name, content in sections.items():
            counts[section_name] = estimate_tokens(str(content))

        # Total count
        counts["total"] = sum(counts.values())

        return counts

    def _load_versions(self) -> None:
        """Load versions from storage."""

        versions_file = self.storage_path / "versions.json"

        if versions_file.exists():
            try:
                with open(versions_file, "r") as f:
                    data = json.load(f)

                for skill_name, versions_data in data.get("skills", {}).items():
                    self.versions[skill_name] = {}

                    for version_str, version_data in versions_data.items():
                        # Convert timestamps
                        version_data["timestamp"] = datetime.fromisoformat(version_data["timestamp"])

                        # Convert changelog entries
                        changelog = []
                        for change_data in version_data.get("changelog", []):
                            change_data["timestamp"] = datetime.fromisoformat(change_data["timestamp"])
                            change_data["change_type"] = ChangeType(change_data["change_type"])
                            changelog.append(DocumentationChange(**change_data))

                        version_data["changelog"] = changelog

                        version_info = VersionInfo(**version_data)
                        self.versions[skill_name][version_str] = version_info

                    # Set current version
                    self.current_versions[skill_name] = data.get("current_versions", {}).get(skill_name, "0.0.0")

            except Exception as e:
                print(f"Error loading versions: {e}")

    def _save_versions(self) -> None:
        """Save versions to storage."""

        # Convert to serializable format
        data = {
            "skills": {},
            "current_versions": self.current_versions,
            "metadata": {
                "total_skills": len(self.versions),
                "total_versions": sum(len(versions) for versions in self.versions.values()),
                "last_updated": datetime.now().isoformat(),
            },
        }

        for skill_name, versions in self.versions.items():
            data["skills"][skill_name] = {}

            for version_str, version_info in versions.items():
                version_data = {
                    "version": version_info.version,
                    "skill_name": version_info.skill_name,
                    "timestamp": version_info.timestamp.isoformat(),
                    "content_hash": version_info.content_hash,
                    "documentation": version_info.documentation,
                    "metadata": version_info.metadata,
                    "dependencies": version_info.dependencies,
                    "compatibility_matrix": version_info.compatibility_matrix,
                    "changelog": [],
                }

                # Convert changelog entries
                for change in version_info.changelog:
                    change_data = {
                        "version_from": change.version_from,
                        "version_to": change.version_to,
                        "change_type": change.change_type.value,
                        "description": change.description,
                        "affected_sections": change.affected_sections,
                        "breaking_change": change.breaking_change,
                        "migration_notes": change.migration_notes,
                        "timestamp": change.timestamp.isoformat(),
                        "author": change.author,
                        "commit_hash": change.commit_hash,
                    }
                    version_data["changelog"].append(change_data)

                data["skills"][skill_name][version_str] = version_data

        # Save to file
        with open(self.storage_path / "versions.json", "w") as f:
            json.dump(data, f, indent=2)

    def get_version_statistics(self) -> Dict[str, Any]:
        """Get statistics about version management."""

        stats = {
            "total_skills": len(self.versions),
            "total_versions": sum(len(versions) for versions in self.versions.values()),
            "average_versions_per_skill": 0.0,
            "latest_versions": {},
            "version_distribution": {"major": 0, "minor": 0, "patch": 0},
        }

        if self.versions:
            stats["average_versions_per_skill"] = stats["total_versions"] / stats["total_skills"]

        # Collect latest versions
        for skill_name, version in self.current_versions.items():
            stats["latest_versions"][skill_name] = version

            # Count version types
            try:
                vinfo = VersionInfo.parse(version)
                if vinfo.patch > 0:
                    stats["version_distribution"]["patch"] += 1
                elif vinfo.minor > 0:
                    stats["version_distribution"]["minor"] += 1
                else:
                    stats["version_distribution"]["major"] += 1
            except:
                pass

        return stats
