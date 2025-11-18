"""
Progressive Disclosure Formatter

Optimizes documentation for agent consumption with minimal token usage.
Implements multi-level compression while preserving information content.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import re
import json

from ..utils.token_utils import estimate_tokens


class DisclosureLevel(Enum):
    """Progressive disclosure levels with token targets."""

    METADATA = "metadata"  # <50 tokens - essential info only
    SUMMARY = "summary"  # <200 tokens - key points
    DETAILED = "detailed"  # <500 tokens - comprehensive info
    FULL = "full"  # <1000 tokens - complete documentation


@dataclass
class CompressionRule:
    """Rule for compressing content while preserving information."""

    name: str
    pattern: str
    replacement: str
    priority: int = 1
    token_savings: int = 0
    applies_to: List[DisclosureLevel] = field(default_factory=lambda: list(DisclosureLevel))


@dataclass
class FormattedContent:
    """Formatted content with metadata about compression."""

    content: str
    level: DisclosureLevel
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    applied_rules: List[str] = field(default_factory=list)
    next_level_available: bool = True
    expansion_points: List[str] = field(default_factory=list)


class ProgressiveFormatter:
    """Formats documentation for optimal agent consumption."""

    def __init__(self):
        self.compression_rules = self._initialize_compression_rules()
        self.format_patterns = self._initialize_format_patterns()

    def _initialize_compression_rules(self) -> List[CompressionRule]:
        """Initialize rules for content compression."""
        return [
            # Metadata level rules
            CompressionRule(
                name="remove_examples",
                pattern=r"\n### Examples\n.*?(?=\n### |\n## |\Z)",
                replacement="",
                priority=1,
                token_savings=200,
                applies_to=[DisclosureLevel.METADATA, DisclosureLevel.SUMMARY],
            ),
            CompressionRule(
                name="compress_descriptions",
                pattern=r"\*\*([^*]+)\*\*:\s*([^\n]+)",
                replacement=r"**\1**: \2",
                priority=1,
                applies_to=[DisclosureLevel.METADATA],
            ),
            CompressionRule(
                name="remove_code_blocks",
                pattern=r"```python\n.*?```",
                replacement="[code example]",
                priority=2,
                token_savings=150,
                applies_to=[DisclosureLevel.METADATA, DisclosureLevel.SUMMARY],
            ),
            # Summary level rules
            CompressionRule(
                name="summarize_bullets",
                pattern=r"\n- (.{50,})",
                replacement=r"\n- \1",
                priority=1,
                applies_to=[DisclosureLevel.SUMMARY],
            ),
            CompressionRule(
                name="compress_sections",
                pattern=r"\n### (.+)\n(.+?)(?=\n### |\n## |\Z)",
                replacement=self._section_compressor,
                priority=1,
                applies_to=[DisclosureLevel.SUMMARY],
            ),
            # Detailed level rules
            CompressionRule(
                name="optimize_code_blocks",
                pattern=r"```python\n([^`]+)```",
                replacement=self._code_optimizer,
                priority=1,
                applies_to=[DisclosureLevel.DETAILED],
            ),
            CompressionRule(
                name="compress_paragraphs",
                pattern=r"\n([A-Z][^.\n]{80,}\.)",
                replacement=self._paragraph_compressor,
                priority=2,
                applies_to=[DisclosureLevel.DETAILED],
            ),
        ]

    def _initialize_format_patterns(self) -> Dict[str, str]:
        """Initialize formatting patterns for different content types."""
        return {
            "skill_name": r"^# (.+)$",
            "section_header": r"^#{1,3} (.+)$",
            "bullet_point": r"^- (.+)$",
            "code_block": r"```(\w+)?\n(.+?)```",
            "inline_code": r"`([^`]+)`",
            "emphasis": r"\*\*([^*]+)\*\*",
            "parameter": r"([A-Za-z_][A-Za-z0-9_]*):",
            "url": r"https?://[^\s]+",
        }

    def format_content(
        self, content: str, level: DisclosureLevel, context: Optional[Dict[str, Any]] = None
    ) -> FormattedContent:
        """Format content for the specified disclosure level."""

        original_tokens = estimate_tokens(content)

        # Apply level-specific formatting
        formatted_content = self._apply_base_formatting(content, level)

        # Apply compression rules
        applied_rules = []
        for rule in self.compression_rules:
            if level in rule.applies_to:
                old_content = formatted_content
                formatted_content = self._apply_compression_rule(formatted_content, rule)
                if formatted_content != old_content:
                    applied_rules.append(rule.name)

        # Add expansion points for progressive loading
        expansion_points = self._identify_expansion_points(formatted_content, level)

        # Calculate compression metrics
        compressed_tokens = estimate_tokens(formatted_content)
        compression_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0

        return FormattedContent(
            content=formatted_content,
            level=level,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compression_ratio,
            applied_rules=applied_rules,
            next_level_available=level != DisclosureLevel.FULL,
            expansion_points=expansion_points,
        )

    def _apply_base_formatting(self, content: str, level: DisclosureLevel) -> str:
        """Apply base formatting rules for the level."""

        if level == DisclosureLevel.METADATA:
            return self._format_metadata(content)
        elif level == DisclosureLevel.SUMMARY:
            return self._format_summary(content)
        elif level == DisclosureLevel.DETAILED:
            return self._format_detailed(content)
        else:  # FULL
            return self._format_full(content)

    def _format_metadata(self, content: str) -> str:
        """Format for metadata level - essential info only."""

        lines = content.split("\n")
        essential_lines = []

        # Keep skill name and basic description
        for line in lines:
            if re.match(r"^# .+", line):  # Skill name
                essential_lines.append(line)
            elif "**Purpose**:" in line or "**Category**:" in line:
                essential_lines.append(line)
            elif line.strip().startswith("**Tags**:"):
                essential_lines.append(line)

        # Compress tags
        formatted = "\n".join(essential_lines)
        formatted = re.sub(r"\*\*Tags\*\*:\s*(.+)", r"**Tags**: \1", formatted)

        return formatted

    def _format_summary(self, content: str) -> str:
        """Format for summary level - key points."""

        # Extract key sections
        sections = self._extract_sections(content)
        summary_parts = []

        # Always include skill name and description
        if "skill_name" in sections:
            summary_parts.append(sections["skill_name"])

        # Include key interface info
        if "interface" in sections:
            interface = self._summarize_section(sections["interface"], max_items=3)
            summary_parts.append(interface)

        # Include brief usage
        if "usage" in sections:
            usage = self._summarize_section(sections["usage"], max_items=2)
            summary_parts.append(usage)

        return "\n\n".join(summary_parts)

    def _format_detailed(self, content: str) -> str:
        """Format for detailed level - comprehensive info."""

        # Optimize but keep most information
        sections = self._extract_sections(content)
        detailed_parts = []

        # Include all sections but optimize them
        for section_name, section_content in sections.items():
            if section_name == "examples":
                # Limit examples
                optimized = self._limit_examples(section_content, max_examples=2)
            elif section_name == "performance":
                # Keep performance metrics concise
                optimized = self._summarize_section(section_content, max_items=4)
            else:
                optimized = section_content

            detailed_parts.append(optimized)

        return "\n\n".join(detailed_parts)

    def _format_full(self, content: str) -> str:
        """Format for full level - complete documentation with optimizations."""

        # Apply light optimizations
        content = self._optimize_code_blocks(content)
        content = self._optimize_structure(content)

        return content

    def _apply_compression_rule(self, content: str, rule: CompressionRule) -> str:
        """Apply a single compression rule to content."""

        if callable(rule.replacement):
            return re.sub(rule.pattern, rule.replacement, content, flags=re.DOTALL)
        else:
            return re.sub(rule.pattern, rule.replacement, content, flags=re.DOTALL)

    def _section_compressor(self, match) -> str:
        """Compress section content while preserving key info."""
        section_title = match.group(1)
        section_content = match.group(2)

        # Extract first few key points
        lines = section_content.split("\n")
        key_lines = []

        for line in lines[:5]:  # Limit to first 5 lines
            line = line.strip()
            if line and (line.startswith("-") or line.startswith("**") or len(line) < 100):
                key_lines.append(line)

        if key_lines:
            return f"\n### {section_title}\n" + "\n".join(key_lines[:3])
        else:
            return f"\n### {section_title}\n{section_content[:100]}..."

    def _code_optimizer(self, match) -> str:
        """Optimize code blocks for token efficiency."""
        language = match.group(1) or "python"
        code = match.group(2)

        # Remove comments and blank lines
        lines = code.split("\n")
        optimized_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                optimized_lines.append(line)

        optimized_code = "\n".join(optimized_lines[:10])  # Limit to 10 lines

        return f"```{language}\n{optimized_code}\n```"

    def _paragraph_compressor(self, match) -> str:
        """Compress long paragraphs."""
        paragraph = match.group(1)

        if len(paragraph) > 100:
            # Keep first and last sentences
            sentences = re.split(r"[.!?]", paragraph)
            if len(sentences) > 2:
                return f"\n{sentences[0].strip()}. {sentences[-1].strip()}."

        return match.group(0)

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from documentation content."""
        sections = {}
        current_section = "intro"
        current_content = []

        lines = content.split("\n")

        for line in lines:
            if re.match(r"^#{1,3} ", line):
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                section_title = re.sub(r"^#{1,3} ", "", line).strip().lower()
                current_section = section_title.replace(" ", "_")
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _summarize_section(self, section: str, max_items: int = 3) -> str:
        """Summarize a section to include only key items."""

        lines = section.split("\n")
        summarized_lines = []
        item_count = 0

        for line in lines:
            if item_count >= max_items:
                break

            stripped = line.strip()
            if stripped:
                if stripped.startswith("-") or stripped.startswith("**"):
                    summarized_lines.append(line)
                    item_count += 1
                elif len(stripped) < 80:  # Short descriptive lines
                    summarized_lines.append(line)
                    item_count += 1

        return "\n".join(summarized_lines)

    def _limit_examples(self, section: str, max_examples: int = 2) -> str:
        """Limit the number of examples in a section."""

        # Split by example markers
        examples = re.split(r"\*\*Example \d+:", section)

        if len(examples) > max_examples + 1:  # +1 because split includes text before first example
            # Keep first part and specified number of examples
            limited = [examples[0]]
            for i in range(1, min(max_examples + 1, len(examples))):
                limited.append(f"**Example {i}: {examples[i]}")

            return "\n".join(limited)

        return section

    def _optimize_code_blocks(self, content: str) -> str:
        """Optimize all code blocks in content."""
        return re.sub(r"```python\n(.+?)```", self._code_optimizer, content, flags=re.DOTALL)

    def _optimize_structure(self, content: str) -> str:
        """Optimize document structure for readability."""

        # Remove excessive blank lines
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Ensure consistent spacing
        content = re.sub(r"\n(#{1,3})", "\n\n\\1", content)

        return content.strip()

    def _identify_expansion_points(self, content: str, level: DisclosureLevel) -> List[str]:
        """Identify points where content can be expanded for next level."""

        expansion_points = []

        if level == DisclosureLevel.METADATA:
            # Can expand to summary
            if "**Purpose**:" in content:
                expansion_points.append("full_description")
            if "**Tags**:" in content:
                expansion_points.append("detailed_tags")

        elif level == DisclosureLevel.SUMMARY:
            # Can expand to detailed
            if "### Interface" in content:
                expansion_points.append("full_interface")
            if "### Usage" in content:
                expansion_points.append("detailed_usage")

        elif level == DisclosureLevel.DETAILED:
            # Can expand to full
            if "[code example]" in content:
                expansion_points.append("full_examples")
            if "### Performance" in content:
                expansion_points.append("detailed_performance")

        return expansion_points

    def expand_content(
        self, content: FormattedContent, expansion_points: List[str], next_level_content: Optional[str] = None
    ) -> FormattedContent:
        """Expand content to include specified expansion points."""

        if not next_level_content:
            return content

        # This is a simplified expansion - in practice, you'd want
        # more sophisticated content merging
        expanded_content = content.content

        for point in expansion_points:
            if point == "full_description":
                # Extract and add full description from next level
                desc_match = re.search(r"\n(.*?\.\n)", next_level_content)
                if desc_match:
                    expanded_content += f"\n\n{desc_match.group(1)}"

            elif point == "full_examples":
                # Add full examples
                example_match = re.search(r"### Examples\n(.+?)(?=\n### |\Z)", next_level_content, re.DOTALL)
                if example_match:
                    expanded_content += f"\n\n### Examples\n{example_match.group(1)}"

        # Recalculate metrics
        new_tokens = estimate_tokens(expanded_content)

        return FormattedContent(
            content=expanded_content,
            level=content.level,
            original_tokens=content.original_tokens,
            compressed_tokens=new_tokens,
            compression_ratio=new_tokens / content.original_tokens,
            applied_rules=content.applied_rules,
            next_level_available=content.next_level_available,
            expansion_points=[],  # Expanded points are now included
        )

    def get_content_summary(self, content: FormattedContent) -> Dict[str, Any]:
        """Get a summary of the formatted content for indexing."""

        return {
            "level": content.level.value,
            "tokens": content.compressed_tokens,
            "compression_ratio": content.compression_ratio,
            "has_expansion_points": len(content.expansion_points) > 0,
            "key_topics": self._extract_key_topics(content.content),
            "complexity": self._assess_complexity(content.content),
        }

    def _extract_key_topics(self, content: str) -> List[str]:
        """Extract key topics from content for indexing."""
        topics = []

        # Extract from headings
        headings = re.findall(r"^#{1,3} (.+)$", content, re.MULTILINE)
        topics.extend([h.lower() for h in headings])

        # Extract from emphasized terms
        emphasized = re.findall(r"\*\*([^*]+)\*\*", content)
        topics.extend([e.lower() for e in emphasized])

        # Remove duplicates and limit
        return list(set(topics))[:10]

    def _assess_complexity(self, content: str) -> str:
        """Assess the complexity level of content."""

        # Simple heuristic based on content characteristics
        code_blocks = len(re.findall(r"```", content)) // 2
        sections = len(re.findall(r"^#{1,3} ", content, re.MULTILINE))
        length = len(content)

        if code_blocks > 5 or sections > 8 or length > 2000:
            return "high"
        elif code_blocks > 2 or sections > 4 or length > 800:
            return "medium"
        else:
            return "low"
