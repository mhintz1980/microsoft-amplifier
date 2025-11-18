#!/usr/bin/env python3
"""
Skill Generator Module

Generates comprehensive SKILL.md files with extracted patterns,
quick references, and structured documentation.

This module handles the final stage of the skill creation process,
transforming scraped and categorized content into high-quality
Claude skills with practical examples and navigation guidance.
"""

import json
from pathlib import Path

from pydantic import BaseModel
from pydantic import Field


class CodeSample(BaseModel):
    """Represents a code sample with language detection."""

    code: str = Field(..., description="The code content")
    language: str = Field(..., description="Detected programming language")
    description: str | None = Field(None, description="Optional description of the code")


class Pattern(BaseModel):
    """Represents a documented pattern or example."""

    description: str = Field(..., description="Pattern description")
    code: str = Field(..., description="Example code")
    context: str | None = Field(None, description="Additional context")


class Page(BaseModel):
    """Represents a scraped documentation page."""

    url: str = Field(..., description="Page URL")
    title: str = Field(..., description="Page title")
    content: str = Field(..., description="Main content text")
    headings: list[dict[str, str]] = Field(default_factory=list, description="Page headings")
    code_samples: list[CodeSample] = Field(default_factory=list, description="Extracted code samples")
    patterns: list[Pattern] = Field(default_factory=list, description="Extracted patterns")
    links: list[str] = Field(default_factory=list, description="Linked pages")


class Category(BaseModel):
    """Represents a category of related pages."""

    name: str = Field(..., description="Category name")
    pages: list[Page] = Field(..., description="Pages in this category")
    keywords: list[str] = Field(default_factory=list, description="Category keywords")


class SkillConfig(BaseModel):
    """Configuration for skill generation."""

    name: str = Field(..., description="Skill name")
    description: str = Field(..., description="Skill description")
    base_url: str = Field(..., description="Base documentation URL")
    version: str = Field(default="1.0.0", description="Skill version")


class SkillGenerator:
    """
    Generates comprehensive SKILL.md files from categorized documentation.

    This class handles the transformation of scraped and categorized content
    into high-quality Claude skills with practical examples, quick references,
    and navigation guidance.
    """

    def __init__(self, config: SkillConfig, output_dir: str):
        """
        Initialize the skill generator.

        Args:
            config: Skill configuration
            output_dir: Directory to save generated files
        """
        self.config = config
        self.output_dir = Path(output_dir)
        self.skill_dir = self.output_dir / config.name
        self.references_dir = self.skill_dir / "references"
        self.scripts_dir = self.skill_dir / "scripts"
        self.assets_dir = self.skill_dir / "assets"

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [self.skill_dir, self.references_dir, self.scripts_dir, self.assets_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def extract_quick_reference_patterns(self, categories: dict[str, list[Page]]) -> list[Pattern]:
        """
        Extract the most useful quick reference patterns from all categories.

        Args:
            categories: Dictionary of category names to page lists

        Returns:
            List of high-quality patterns for quick reference
        """
        all_patterns = []
        seen_codes = set()

        # Collect patterns from all pages, prioritizing unique, practical examples
        for category_pages in categories.values():
            for page in category_pages:
                # Extract from dedicated patterns first
                for pattern in page.patterns:
                    code_hash = hash(pattern.code)
                    if code_hash not in seen_codes and len(pattern.code) < 500:
                        all_patterns.append(pattern)
                        seen_codes.add(code_hash)

                # Extract from code samples if no dedicated patterns
                if not page.patterns:
                    for sample in page.code_samples[:2]:  # Limit to avoid noise
                        code_hash = hash(sample.code)
                        if (
                            code_hash not in seen_codes
                            and len(sample.code) > 20
                            and len(sample.code) < 400
                            and sample.language != "unknown"
                        ):
                            # Create pattern from code sample
                            pattern = Pattern(
                                description=f"Example {sample.language} code",
                                code=sample.code,
                                context=f"From {page.title}",
                            )
                            all_patterns.append(pattern)
                            seen_codes.add(code_hash)

        # Sort by quality and limit to best patterns
        def pattern_score(pattern: Pattern) -> int:
            score = 0
            if "example" in pattern.description.lower():
                score += 2
            if "pattern" in pattern.description.lower():
                score += 2
            if len(pattern.code) > 50:
                score += 1
            if len(pattern.code) < 300:
                score += 1
            return score

        all_patterns.sort(key=pattern_score, reverse=True)
        return all_patterns[:15]  # Return top 15 patterns

    def extract_best_code_examples(self, categories: dict[str, list[Page]]) -> list[tuple[str, str]]:
        """
        Extract the best code examples from all categories.

        Args:
            categories: Dictionary of category names to page lists

        Returns:
            List of (language, code) tuples
        """
        examples = []
        seen_codes = set()

        # Extract from first few pages of each category for diversity
        for category_pages in categories.values():
            for page in category_pages[:3]:  # First 3 pages per category
                for sample in page.code_samples[:2]:  # First 2 samples per page
                    if sample.language != "unknown" and len(sample.code) > 30 and len(sample.code) < 300:
                        code_hash = hash(sample.code)
                        if code_hash not in seen_codes:
                            examples.append((sample.language, sample.code))
                            seen_codes.add(code_hash)
                            if len(examples) >= 10:
                                return examples

        return examples

    def create_reference_file(self, category_name: str, pages: list[Page]) -> None:
        """
        Create a reference file for a specific category.

        Args:
            category_name: Name of the category
            pages: List of pages in the category
        """
        if not pages:
            return

        lines = []
        display_name = category_name.replace("_", " ").title()
        lines.append(f"# {self.config.name.title()} - {display_name}\n")
        lines.append(f"**Pages:** {len(pages)}\n")
        lines.append("---\n")

        for page in pages:
            lines.append(f"## {page.title}\n")
            lines.append(f"**URL:** {page.url}\n")

            # Add table of contents from headings
            if page.headings:
                lines.append("**Contents:**")
                for heading in page.headings[:10]:
                    level = int(heading["level"][1]) if len(heading["level"]) > 1 else 1
                    indent = "  " * max(0, level - 2)
                    lines.append(f"{indent}- {heading['text']}")
                lines.append("")

            # Add content (truncated for readability)
            if page.content:
                content = page.content[:2500]
                if len(page.content) > 2500:
                    content += "\n\n*[Content truncated]*"
                lines.append(content)
                lines.append("")

            # Add code examples with language annotation
            if page.code_samples:
                lines.append("**Examples:**\n")
                for i, sample in enumerate(page.code_samples[:4], 1):
                    code = sample.code[:600] if len(sample.code) > 600 else sample.code
                    ellipsis = "...\n" if len(sample.code) > 600 else ""
                    lines.append(f"Example {i} ({sample.language}):")
                    lines.append(f"```{sample.language}")
                    lines.append(code)
                    lines.append(ellipsis)
                    lines.append("```\n")

            lines.append("---\n")

        # Write the reference file
        filepath = self.references_dir / f"{category_name}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"  ✓ {category_name}.md ({len(pages)} pages)")

    def create_index_file(self, categories: dict[str, list[Page]]) -> None:
        """
        Create an index file for all reference categories.

        Args:
            categories: Dictionary of category names to page lists
        """
        lines = []
        lines.append(f"# {self.config.name.title()} Documentation Index\n")
        lines.append("## Categories\n")

        for category_name, pages in sorted(categories.items()):
            display_name = category_name.replace("_", " ").title()
            lines.append(f"### {display_name}")
            lines.append(f"**File:** `{category_name}.md`")
            lines.append(f"**Pages:** {len(pages)}\n")

        # Write the index file
        filepath = self.references_dir / "index.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print("  ✓ index.md")

    def generate_skill_content(
        self, categories: dict[str, list[Page]], quick_ref: list[Pattern], examples: list[tuple[str, str]]
    ) -> str:
        """
        Generate the complete SKILL.md content.

        Args:
            categories: Categorized pages
            quick_ref: Quick reference patterns
            examples: Best code examples

        Returns:
            Complete SKILL.md content as string
        """
        content = f"""---
name: {self.config.name}
description: {self.config.description}
version: {self.config.version}
---

# {self.config.name.title()} Skill

{self.config.description}

## When to Use This Skill

This skill should be triggered when:
- Working with {self.config.name} development or implementation
- Asking about {self.config.name} features, APIs, or best practices
- Debugging {self.config.name} code or troubleshooting issues
- Learning {self.config.name} concepts and patterns
- Implementing {self.config.name} solutions or integrations

## Quick Reference

### Common Patterns

"""

        # Add quick reference patterns
        if quick_ref:
            for i, pattern in enumerate(quick_ref[:8], 1):
                content += f"**Pattern {i}:** {pattern.description}\n\n"
                content += "```\n"
                content += pattern.code[:300]
                if len(pattern.code) > 300:
                    content += "\n..."
                content += "\n```\n\n"
        else:
            content += "*Quick reference patterns will be added as you use the skill.*\n\n"

        # Add best code examples
        if examples:
            content += "### Example Code Patterns\n\n"
            for i, (language, code) in enumerate(examples[:5], 1):
                content += f"**Example {i}** ({language}):\n```{language}\n{code}\n```\n\n"

        content += """## Reference Files

This skill includes comprehensive documentation in `references/`:

"""

        # List all categories
        for category_name in sorted(categories.keys()):
            display_name = category_name.replace("_", " ").title()
            content += f"- **{category_name}.md** - {display_name} documentation\n"

        content += """
Use `view` to read specific reference files when detailed information is needed.

## Working with This Skill

### For Beginners
Start with getting_started, tutorial, or introductory reference files for foundational concepts and step-by-step guidance.

### For Specific Features
Use the appropriate category reference file (api, guides, reference, etc.) for detailed information about specific features.

### For Code Examples
The quick reference section above contains common patterns extracted from the official documentation.

### For Troubleshooting
Check the relevant category reference file for specific error solutions and debugging approaches.

## Resources

### references/
Organized documentation extracted from official sources. These files contain:
- Detailed explanations and concepts
- Code examples with language annotations
- Links to original documentation for further reading
- Structured table of contents for quick navigation

### scripts/
Add helper scripts here for common automation tasks, code generation, or development workflows.

### assets/
Add templates, boilerplate code, example projects, or configuration files here.

## Implementation Notes

- This skill was automatically generated from official documentation
- Reference files preserve the structure and examples from source documentation
- Code examples include language detection for better syntax highlighting
- Quick reference patterns are extracted from common usage examples
- Content is organized by topic for efficient access

## Updating

To refresh this skill with updated documentation:
1. Re-run the scraper with the same configuration
2. The skill will be rebuilt with the latest information
3. Custom additions in scripts/ and assets/ will be preserved

## Source

Generated from: {self.config.base_url}
Version: {self.config.version}
""".strip()

        return content

    def create_skill_file(
        self, categories: dict[str, list[Page]], quick_ref: list[Pattern], examples: list[tuple[str, str]]
    ) -> None:
        """
        Create the main SKILL.md file.

        Args:
            categories: Categorized pages
            quick_ref: Quick reference patterns
            examples: Best code examples
        """
        content = self.generate_skill_content(categories, quick_ref, examples)

        # Backup existing file if it exists
        skill_file = self.skill_dir / "SKILL.md"
        if skill_file.exists():
            backup_file = self.skill_dir / "SKILL.md.backup"
            skill_file.rename(backup_file)
            print("  ✓ Backed up existing SKILL.md")

        # Write new skill file
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  ✓ SKILL.md (enhanced with {len(examples)} examples)")

    def create_readme_file(self) -> None:
        """Create a README file for the skill directory."""
        content = f"""# {self.config.name.title()} Skill

A comprehensive Claude skill for {self.config.name} development, generated from official documentation.

## Files

- **SKILL.md** - Main skill file with examples and guidance
- **references/** - Organized documentation by category
- **scripts/** - Add your helper scripts here
- **assets/** - Add templates and examples here

## Usage

This skill provides:
- Quick reference patterns for common tasks
- Comprehensive documentation organized by topic
- Code examples with language detection
- Navigation guidance for different skill levels

## Generated

Generated from: {self.config.base_url}
Generator: Skill Seeker v2.0 (Modular)
Version: {self.config.version}
"""

        readme_file = self.skill_dir / "README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(content)

        print("  ✓ README.md")

    def generate_skill(self, categories: dict[str, list[Page]], create_readme: bool = True) -> bool:
        """
        Generate the complete skill from categorized pages.

        Args:
            categories: Dictionary of category names to page lists
            create_readme: Whether to create a README file

        Returns:
            True if successful, False otherwise
        """
        if not categories:
            print("✗ No categories provided!")
            return False

        print(f"\n{'=' * 60}")
        print(f"GENERATING SKILL: {self.config.name}")
        print(f"{'=' * 60}\n")

        # Count total pages
        total_pages = sum(len(pages) for pages in categories.values())
        print(f"Processing {len(categories)} categories with {total_pages} pages\n")

        # Create reference files
        print("Creating reference files...")
        for category_name, pages in categories.items():
            self.create_reference_file(category_name, pages)

        # Create index
        print("\nCreating index...")
        self.create_index_file(categories)

        # Extract patterns and examples
        print("Extracting quick reference patterns...")
        quick_ref = self.extract_quick_reference_patterns(categories)
        print(f"  ✓ Extracted {len(quick_ref)} patterns")

        print("Extracting best code examples...")
        examples = self.extract_best_code_examples(categories)
        print(f"  ✓ Extracted {len(examples)} examples\n")

        # Create main skill file
        print("Creating SKILL.md...")
        self.create_skill_file(categories, quick_ref, examples)

        # Create README if requested
        if create_readme:
            print("Creating README.md...")
            self.create_readme_file()

        print(f"\n✅ Skill generated: {self.skill_dir}/")
        return True

    @staticmethod
    def load_pages_from_data(data_dir: str) -> list[Page]:
        """
        Load pages from scraped data directory.

        Args:
            data_dir: Directory containing scraped page data

        Returns:
            List of loaded Page objects
        """
        pages = []
        pages_dir = Path(data_dir) / "pages"

        if not pages_dir.exists():
            print(f"⚠ Pages directory not found: {pages_dir}")
            return []

        for json_file in pages_dir.glob("*.json"):
            try:
                with open(json_file, encoding="utf-8") as f:
                    page_data = json.load(f)

                # Convert code samples to CodeSample objects
                code_samples = []
                for sample_data in page_data.get("code_samples", []):
                    if isinstance(sample_data, dict):
                        code_samples.append(CodeSample(**sample_data))
                    else:
                        # Handle legacy string format
                        code_samples.append(
                            CodeSample(code=sample_data, language="unknown", description="Legacy code sample")
                        )

                # Convert patterns to Pattern objects
                patterns = []
                for pattern_data in page_data.get("patterns", []):
                    if isinstance(pattern_data, dict):
                        patterns.append(Pattern(**pattern_data))

                # Create Page object
                page = Page(
                    url=page_data["url"],
                    title=page_data["title"],
                    content=page_data.get("content", ""),
                    headings=page_data.get("headings", []),
                    code_samples=code_samples,
                    patterns=patterns,
                    links=page_data.get("links", []),
                )

                pages.append(page)

            except Exception as e:
                print(f"⚠ Error loading {json_file}: {e}")

        print(f"✓ Loaded {len(pages)} pages from {data_dir}")
        return pages
