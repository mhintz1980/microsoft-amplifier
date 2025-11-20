"""
Validation utilities for documentation system.
"""

import re
from typing import Any


def validate_skill_name(skill_name: str) -> list[str]:
    """
    Validate skill name format.

    Args:
        skill_name: Skill name to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not skill_name:
        errors.append("Skill name cannot be empty")
        return errors

    if len(skill_name) < 3:
        errors.append("Skill name must be at least 3 characters long")

    if len(skill_name) > 50:
        errors.append("Skill name must be 50 characters or less")

    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not re.match(r"^[a-zA-Z0-9_-]+$", skill_name):
        errors.append("Skill name can only contain letters, numbers, hyphens, and underscores")

    # Check for invalid patterns
    if skill_name.startswith(("-", "_")):
        errors.append("Skill name cannot start with hyphen or underscore")

    if skill_name.endswith(("-", "_")):
        errors.append("Skill name cannot end with hyphen or underscore")

    if "--" in skill_name or "__" in skill_name:
        errors.append("Skill name cannot contain consecutive hyphens or underscores")

    return errors


def validate_documentation_structure(documentation: dict[str, Any]) -> list[str]:
    """
    Validate documentation structure.

    Args:
        documentation: Documentation dictionary to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not isinstance(documentation, dict):
        errors.append("Documentation must be a dictionary")
        return errors

    # Check required levels
    required_levels = ["metadata", "summary", "detailed", "full"]
    for level in required_levels:
        if level not in documentation:
            errors.append(f"Missing required level: {level}")

    # Validate each level
    for level, content in documentation.items():
        if level in required_levels:
            level_errors = _validate_documentation_level(level, content)
            errors.extend([f"{level}: {error}" for error in level_errors])

    return errors


def _validate_documentation_level(level: str, content: Any) -> list[str]:
    """Validate a specific documentation level."""

    errors = []

    if content is None:
        return ["Content cannot be None"]

    if isinstance(content, dict):
        # Check for sections
        if "sections" in content:
            if not isinstance(content["sections"], dict):
                errors.append("Sections must be a dictionary")
            else:
                # Validate each section
                for section_name, section_content in content["sections"].items():
                    section_errors = _validate_section_content(section_name, section_content)
                    errors.extend([f"section '{section_name}': {error}" for error in section_errors])

    elif isinstance(content, str):
        # String content should be non-empty for most levels
        if level in ["summary", "detailed", "full"] and not content.strip():
            errors.append("Content cannot be empty")

    return errors


def _validate_section_content(section_name: str, content: Any) -> list[str]:
    """Validate content of a documentation section."""

    errors = []

    if not isinstance(content, (str, dict)):
        errors.append("Section content must be string or dictionary")

    if isinstance(content, str) and len(content.strip()) == 0:
        errors.append("Section content cannot be empty")

    return errors


def validate_tags(tags: list[str]) -> list[str]:
    """
    Validate skill tags.

    Args:
        tags: List of tags to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not isinstance(tags, list):
        errors.append("Tags must be a list")
        return errors

    if len(tags) == 0:
        errors.append("At least one tag is required")

    if len(tags) > 10:
        errors.append("Too many tags (maximum 10)")

    seen_tags = set()
    for tag in tags:
        if not isinstance(tag, str):
            errors.append(f"Tag '{tag}' must be a string")
            continue

        if not tag.strip():
            errors.append("Tag cannot be empty")
            continue

        if len(tag) > 20:
            errors.append(f"Tag '{tag}' is too long (maximum 20 characters)")

        if not re.match(r"^[a-zA-Z0-9_-]+$", tag):
            errors.append(f"Tag '{tag}' contains invalid characters")

        if tag in seen_tags:
            errors.append(f"Duplicate tag: '{tag}'")
        else:
            seen_tags.add(tag)

    return errors


def validate_examples(examples: list[dict[str, Any]]) -> list[str]:
    """
    Validate code examples.

    Args:
        examples: List of examples to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not isinstance(examples, list):
        errors.append("Examples must be a list")
        return errors

    for i, example in enumerate(examples):
        example_errors = _validate_single_example(example, i)
        errors.extend(example_errors)

    return errors


def _validate_single_example(example: dict[str, Any], index: int) -> list[str]:
    """Validate a single example."""

    errors = []

    if not isinstance(example, dict):
        errors.append(f"Example {index} must be a dictionary")
        return errors

    # Check required fields
    required_fields = ["description", "code"]
    for field in required_fields:
        if field not in example:
            errors.append(f"Example {index} missing required field: {field}")

    # Validate description
    if "description" in example:
        if not isinstance(example["description"], str):
            errors.append(f"Example {index} description must be a string")
        elif len(example["description"].strip()) == 0:
            errors.append(f"Example {index} description cannot be empty")

    # Validate code
    if "code" in example:
        if not isinstance(example["code"], str):
            errors.append(f"Example {index} code must be a string")
        elif len(example["code"].strip()) == 0:
            errors.append(f"Example {index} code cannot be empty")
        else:
            # Basic syntax check
            try:
                compile(example["code"], "<string>", "exec")
            except SyntaxError as e:
                errors.append(f"Example {index} has syntax error: {e}")

    # Validate explanation if present
    if "explanation" in example:
        if not isinstance(example["explanation"], str):
            errors.append(f"Example {index} explanation must be a string")

    return errors


def validate_cross_references(references: dict[str, Any]) -> list[str]:
    """
    Validate cross-references in documentation.

    Args:
        references: Cross-references dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not isinstance(references, dict):
        errors.append("Cross-references must be a dictionary")
        return errors

    # Validate related skills
    if "related_skills" in references:
        if not isinstance(references["related_skills"], dict):
            errors.append("Related skills must be a dictionary")

    # Validate recommendations
    if "recommendations" in references:
        if not isinstance(references["recommendations"], dict):
            errors.append("Recommendations must be a dictionary")
        else:
            for category, items in references["recommendations"].items():
                if not isinstance(items, list):
                    errors.append(f"Recommendations for '{category}' must be a list")

    return errors


def validate_version_info(version_info: dict[str, Any]) -> list[str]:
    """
    Validate version information.

    Args:
        version_info: Version information dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not isinstance(version_info, dict):
        errors.append("Version info must be a dictionary")
        return errors

    # Check required fields
    required_fields = ["version", "skill_name", "timestamp"]
    for field in required_fields:
        if field not in version_info:
            errors.append(f"Version info missing required field: {field}")

    # Validate version format
    if "version" in version_info:
        version = version_info["version"]
        if not isinstance(version, str):
            errors.append("Version must be a string")
        elif not re.match(r"^\d+\.\d+\.\d+$", version):
            errors.append("Version must follow semantic versioning (x.y.z)")

    # Validate skill name
    if "skill_name" in version_info:
        skill_errors = validate_skill_name(version_info["skill_name"])
        errors.extend([f"skill_name: {error}" for error in skill_errors])

    return errors


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to be safe for filesystem.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Remove control characters
    sanitized = re.sub(r"[\x00-\x1f\x7f]", "", sanitized)

    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[: 255 - len(ext)] + ext

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")

    return sanitized or "unnamed"


def is_valid_json_pointer(pointer: str) -> bool:
    """
    Validate JSON pointer format.

    Args:
        pointer: JSON pointer string

    Returns:
        True if valid, False otherwise
    """
    if not pointer:
        return True  # Empty pointer is valid (refers to root)

    if not pointer.startswith("/"):
        return False

    # Basic validation - more thorough validation would be more complex
    try:
        # Split into segments
        segments = pointer.split("/")[1:]

        # Check each segment
        for segment in segments:
            # Allow empty segments (escaped characters)
            if segment:
                # Check for unescaped tilde (should be ~0 or ~1)
                if "~" in segment and not all(c in "01" for c in segment.split("~")[1:]):
                    return False

        return True
    except:
        return False
