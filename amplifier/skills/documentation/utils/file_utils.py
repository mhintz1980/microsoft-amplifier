"""
File utilities for safe file operations.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import tempfile
import shutil


def safe_write(file_path: Path, content: str, backup: bool = True) -> bool:
    """
    Safely write content to a file with atomic operation.

    Args:
        file_path: Path to write to
        content: Content to write
        backup: Whether to create backup of existing file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create backup if requested and file exists
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + ".backup")
            shutil.copy2(file_path, backup_path)

        # Write to temporary file first
        with tempfile.NamedTemporaryFile(
            mode="w", dir=file_path.parent, prefix=f".tmp_{file_path.name}_", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)

        # Atomic move to final location
        shutil.move(str(temp_file_path), str(file_path))

        return True

    except Exception:
        # Clean up temp file if it exists
        if "temp_file_path" in locals() and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except:
                pass
        return False


def safe_read(file_path: Path) -> Optional[str]:
    """
    Safely read content from a file.

    Args:
        file_path: Path to read from

    Returns:
        File content or None if failed
    """
    try:
        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    except Exception:
        return None


def safe_write_json(file_path: Path, data: Dict[str, Any], backup: bool = True) -> bool:
    """
    Safely write JSON data to a file.

    Args:
        file_path: Path to write to
        data: JSON data to write
        backup: Whether to create backup of existing file

    Returns:
        True if successful, False otherwise
    """
    try:
        content = json.dumps(data, indent=2, ensure_ascii=False)
        return safe_write(file_path, content, backup)

    except Exception:
        return False


def safe_read_json(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Safely read JSON data from a file.

    Args:
        file_path: Path to read from

    Returns:
        JSON data or None if failed
    """
    try:
        content = safe_read(file_path)
        if content:
            return json.loads(content)
        return None

    except Exception:
        return None


def ensure_directory(dir_path: Path) -> bool:
    """
    Ensure directory exists, creating if necessary.

    Args:
        dir_path: Directory path to ensure

    Returns:
        True if successful, False otherwise
    """
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        return True

    except Exception:
        return False


def cleanup_temp_files(directory: Path, pattern: str = ".tmp_*") -> int:
    """
    Clean up temporary files in a directory.

    Args:
        directory: Directory to clean
        pattern: Pattern to match temporary files

    Returns:
        Number of files cleaned up
    """
    cleaned = 0

    try:
        for temp_file in directory.glob(pattern):
            try:
                temp_file.unlink()
                cleaned += 1
            except:
                pass

    except Exception:
        pass

    return cleaned


def backup_file(file_path: Path, backup_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Create backup of a file.

    Args:
        file_path: File to backup
        backup_dir: Directory to store backup (default: same directory)

    Returns:
        Path to backup file or None if failed
    """
    try:
        if not file_path.exists():
            return None

        if backup_dir is None:
            backup_dir = file_path.parent

        backup_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped backup
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name

        shutil.copy2(file_path, backup_path)
        return backup_path

    except Exception:
        return None


def restore_file(backup_path: Path, target_path: Path) -> bool:
    """
    Restore file from backup.

    Args:
        backup_path: Backup file to restore from
        target_path: Target path to restore to

    Returns:
        True if successful, False otherwise
    """
    try:
        if not backup_path.exists():
            return False

        # Create backup of current target if it exists
        if target_path.exists():
            backup_file(target_path)

        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy backup to target
        shutil.copy2(backup_path, target_path)
        return True

    except Exception:
        return False
