"""
Automatic Documentation Generator

Generates comprehensive documentation from skill specifications using
enhanced SDK patterns and zero-hallucination validation.
"""

import asyncio
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

from ..core.cross_reference_manager import CrossReferenceManager
from ..core.progressive_formatter import DisclosureLevel
from ..core.progressive_formatter import ProgressiveFormatter
from ..core.quality_validator import DocumentationValidator
from ..core.quality_validator import ValidationResult
from ..core.template_engine import DocumentationTemplate
from ..core.template_engine import SkillCategory
from ..core.template_engine import SkillDocumentationSpec
from ..core.version_manager import DocumentationVersionManager
from ..storage.mcp_integration import MCPDocumentationStorage
from ..storage.mcp_integration import StorageConfig
from .example_generator import ExampleGenerator
from .skill_analyzer import SkillAnalyzer


class GenerationMode(Enum):
    """Documentation generation modes."""

    FULL = "full"  # Generate complete documentation
    UPDATE = "update"  # Update existing documentation
    INCREMENTAL = "incremental"  # Add new sections only
    VALIDATE = "validate"  # Validate existing docs only


@dataclass
class GenerationConfig:
    """Configuration for documentation generation."""

    mode: GenerationMode = GenerationMode.FULL
    target_levels: list[DisclosureLevel] = field(
        default_factory=lambda: [
            DisclosureLevel.METADATA,
            DisclosureLevel.SUMMARY,
            DisclosureLevel.DETAILED,
            DisclosureLevel.FULL,
        ]
    )
    include_examples: bool = True
    include_cross_refs: bool = True
    validate_output: bool = True
    auto_fix_issues: bool = True
    max_examples_per_level: dict[str, int] = field(default_factory=lambda: {"summary": 1, "detailed": 2, "full": 5})
    storage_config: StorageConfig | None = None
    strict_validation: bool = True


@dataclass
class GenerationResult:
    """Result of documentation generation."""

    skill_name: str
    success: bool
    documentation: dict[str, Any] = field(default_factory=dict)
    validation_result: ValidationResult | None = None
    generation_time: float = 0.0
    issues_found: int = 0
    issues_fixed: int = 0
    levels_generated: list[str] = field(default_factory=list)
    cross_references: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class AutomaticDocumentationGenerator:
    """Automated documentation generator for skills."""

    def __init__(
        self,
        template_engine: DocumentationTemplate | None = None,
        formatter: ProgressiveFormatter | None = None,
        validator: DocumentationValidator | None = None,
        xref_manager: CrossReferenceManager | None = None,
        version_manager: DocumentationVersionManager | None = None,
        storage: MCPDocumentationStorage | None = None,
    ):
        self.template_engine = template_engine or DocumentationTemplate()
        self.formatter = formatter or ProgressiveFormatter()
        self.validator = validator or DocumentationValidator()
        self.xref_manager = xref_manager or CrossReferenceManager()
        self.version_manager = version_manager or DocumentationVersionManager()
        self.storage = storage

        self.skill_analyzer = SkillAnalyzer()
        self.example_generator = ExampleGenerator()

    async def generate_documentation(
        self,
        skill_class: type,
        config: GenerationConfig | None = None,
        existing_documentation: dict[str, Any] | None = None,
    ) -> GenerationResult:
        """Generate comprehensive documentation for a skill."""

        config = config or GenerationConfig()
        start_time = datetime.now()

        try:
            # Analyze the skill
            analysis = await self.skill_analyzer.analyze_skill(skill_class)

            # Create documentation specification
            doc_spec = self._create_documentation_spec(skill_class, analysis)

            # Generate base documentation
            base_documentation = self._generate_base_documentation(doc_spec, config)

            # Enhance with examples
            if config.include_examples:
                base_documentation = await self._enhance_with_examples(
                    base_documentation, skill_class, analysis, config
                )

            # Add cross-references
            if config.include_cross_refs:
                cross_refs = self.xref_manager.generate_documentation_cross_references(
                    doc_spec.skill_name, base_documentation
                )
                base_documentation["cross_references"] = cross_refs

            # Apply progressive formatting
            formatted_documentation = self._apply_progressive_formatting(base_documentation, config.target_levels)

            # Validate and fix issues
            validation_result = None
            issues_fixed = 0

            if config.validate_output:
                validation_result = self.validator.validate_documentation(
                    doc_spec.skill_name, formatted_documentation, skill_class=skill_class
                )

                if config.auto_fix_issues and not validation_result.is_valid:
                    fixed_docs, remaining_issues = self.validator.auto_fix_issues(
                        formatted_documentation, validation_result
                    )
                    issues_fixed = len(validation_result.issues) - len(remaining_issues)
                    formatted_documentation = fixed_docs

                    # Re-validate after fixes
                    if remaining_issues:
                        validation_result = self.validator.validate_documentation(
                            doc_spec.skill_name, formatted_documentation, skill_class=skill_class
                        )

            # Generate metadata
            metadata = self._generate_metadata(doc_spec, analysis, validation_result)

            # Store documentation if storage is configured
            if self.storage:
                await self.storage.store_documentation(doc_spec.skill_name, formatted_documentation, metadata=metadata)

            # Create version
            if self.version_manager:
                changes = self._create_version_changes(existing_documentation, formatted_documentation)
                self.version_manager.create_version(
                    doc_spec.skill_name, formatted_documentation, changes=changes, metadata=metadata
                )

            generation_time = (datetime.now() - start_time).total_seconds()

            return GenerationResult(
                skill_name=doc_spec.skill_name,
                success=True,
                documentation=formatted_documentation,
                validation_result=validation_result,
                generation_time=generation_time,
                issues_found=len(validation_result.issues) if validation_result else 0,
                issues_fixed=issues_fixed,
                levels_generated=[level.value for level in config.target_levels],
                cross_references=base_documentation.get("cross_references", {}),
                metadata=metadata,
            )

        except Exception as e:
            generation_time = (datetime.now() - start_time).total_seconds()

            return GenerationResult(
                skill_name=skill_class.__name__,
                success=False,
                generation_time=generation_time,
                metadata={"error": str(e)},
            )

    async def batch_generate_documentation(
        self, skill_classes: list[type], config: GenerationConfig | None = None, parallel: bool = True
    ) -> list[GenerationResult]:
        """Generate documentation for multiple skills."""

        if parallel:
            # Generate in parallel
            tasks = [self.generate_documentation(skill_class, config) for skill_class in skill_classes]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Convert exceptions to failed results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(
                        GenerationResult(
                            skill_name=skill_classes[i].__name__, success=False, metadata={"error": str(result)}
                        )
                    )
                else:
                    processed_results.append(result)

            return processed_results
        # Generate sequentially
        results = []
        for skill_class in skill_classes:
            result = await self.generate_documentation(skill_class, config)
            results.append(result)

        return results

    async def update_documentation(
        self, skill_name: str, updates: dict[str, Any], config: GenerationConfig | None = None
    ) -> GenerationResult:
        """Update existing documentation."""

        config = config or GenerationConfig()
        config.mode = GenerationMode.UPDATE

        # Load existing documentation
        existing_docs = None
        if self.storage:
            existing_docs = await self.storage.retrieve_documentation(skill_name)
        elif self.version_manager:
            version_info = self.version_manager.get_version(skill_name)
            if version_info:
                existing_docs = version_info.documentation

        if not existing_docs:
            raise ValueError(f"No existing documentation found for {skill_name}")

        # Apply updates
        updated_docs = existing_docs.copy()
        for section, content in updates.items():
            if section in updated_docs:
                updated_docs[section].update(content)
            else:
                updated_docs[section] = content

        # Re-validate updated documentation
        if config.validate_output:
            validation_result = self.validator.validate_documentation(skill_name, updated_docs)

            if not validation_result.is_valid and config.auto_fix_issues:
                updated_docs, _ = self.validator.auto_fix_issues(updated_docs, validation_result)

        # Store updated documentation
        if self.storage:
            await self.storage.store_documentation(skill_name, updated_docs)

        # Create new version
        if self.version_manager:
            changes = self._create_version_changes(existing_docs, updated_docs)
            self.version_manager.create_version(skill_name, updated_docs, changes=changes)

        return GenerationResult(
            skill_name=skill_name,
            success=True,
            documentation=updated_docs,
            metadata={"updated_sections": list(updates.keys())},
        )

    def _create_documentation_spec(self, skill_class: type, analysis: dict[str, Any]) -> SkillDocumentationSpec:
        """Create documentation specification from skill analysis."""

        skill_name = skill_class.__name__.replace("Skill", "").lower()

        # Determine category
        category = self._determine_skill_category(skill_class, analysis)

        # Extract description
        description = getattr(skill_class, "description", "")
        if not description and skill_class.__doc__:
            description = skill_class.__doc__.strip().split("\n")[0]

        # Extract tags
        tags = getattr(skill_class, "tags", [])
        tags.extend(analysis.get("suggested_tags", []))
        tags = list(set(tags))  # Remove duplicates

        # Extract inputs and outputs from analysis
        inputs = analysis.get("inputs", [])
        outputs = analysis.get("outputs", [])

        # Extract dependencies
        dependencies = analysis.get("dependencies", [])

        # Generate examples if not provided
        examples = []
        if hasattr(skill_class, "examples"):
            examples = skill_class.examples

        return SkillDocumentationSpec(
            skill_name=skill_name,
            category=category,
            skill_class=skill_class.__name__,
            description=description,
            tags=tags,
            inputs=inputs,
            outputs=outputs,
            dependencies=dependencies,
            examples=examples,
            related_skills=analysis.get("related_skills", []),
        )

    def _generate_base_documentation(self, spec: SkillDocumentationSpec, config: GenerationConfig) -> dict[str, Any]:
        """Generate base documentation using templates."""

        documentation = {}

        for level in config.target_levels:
            if level == DisclosureLevel.METADATA:
                docs = self.template_engine.generate_documentation(spec, "metadata")
            elif level == DisclosureLevel.SUMMARY:
                docs = self.template_engine.generate_documentation(spec, "summary")
            elif level == DisclosureLevel.DETAILED:
                docs = self.template_engine.generate_documentation(spec, "detailed")
            elif level == DisclosureLevel.FULL:
                docs = self.template_engine.generate_documentation(spec, "full")

            documentation[level.value] = docs

        return documentation

    async def _enhance_with_examples(
        self, documentation: dict[str, Any], skill_class: type, analysis: dict[str, Any], config: GenerationConfig
    ) -> dict[str, Any]:
        """Enhance documentation with generated examples."""

        enhanced_docs = documentation.copy()

        for level in config.target_levels:
            max_examples = config.max_examples_per_level.get(level.value, 0)
            if max_examples == 0:
                continue

            # Generate examples for this level
            examples = await self.example_generator.generate_examples(
                skill_class, analysis, level, max_count=max_examples
            )

            # Add examples to appropriate section
            level_docs = enhanced_docs.get(level.value, {})
            sections = level_docs.get("sections", {})

            if "usage" in sections:
                # Add examples to usage section
                current_usage = sections["usage"]
                examples_section = self._format_examples_section(examples, level)
                sections["usage"] = f"{current_usage}\n\n{examples_section}"

            enhanced_docs[level.value] = level_docs

        return enhanced_docs

    def _apply_progressive_formatting(
        self, documentation: dict[str, Any], target_levels: list[DisclosureLevel]
    ) -> dict[str, Any]:
        """Apply progressive disclosure formatting."""

        formatted_docs = {}

        for level in target_levels:
            level_docs = documentation.get(level.value, {})

            if isinstance(level_docs, dict) and "sections" in level_docs:
                # Combine all sections for formatting
                full_content = "\n\n".join(level_docs["sections"].values())

                # Format for the level
                formatted_result = self.formatter.format_content(full_content, level)

                # Update sections with formatted content
                # This is a simplified approach - in practice, you'd want
                # more sophisticated section-by-section formatting
                formatted_docs[level.value] = {
                    "content": formatted_result.content,
                    "tokens": formatted_result.compressed_tokens,
                    "compression_ratio": formatted_result.compression_ratio,
                    "expansion_points": formatted_result.expansion_points,
                    "sections": level_docs["sections"],  # Keep original sections
                }
            else:
                # Handle string content
                if isinstance(level_docs, str):
                    formatted_result = self.formatter.format_content(level_docs, level)
                    formatted_docs[level.value] = {
                        "content": formatted_result.content,
                        "tokens": formatted_result.compressed_tokens,
                        "compression_ratio": formatted_result.compression_ratio,
                        "expansion_points": formatted_result.expansion_points,
                    }
                else:
                    formatted_docs[level.value] = level_docs

        return formatted_docs

    def _determine_skill_category(self, skill_class: type, analysis: dict[str, Any]) -> SkillCategory:
        """Determine the category of a skill."""

        # Check for explicit category
        if hasattr(skill_class, "category"):
            try:
                return SkillCategory(skill_class.category)
            except ValueError:
                pass

        # Analyze skill name and functionality
        skill_name = skill_class.__name__.lower()

        if "context" in skill_name or "memory" in skill_name:
            return SkillCategory.CONTEXT_MANAGEMENT
        if "synthesis" in skill_name or "knowledge" in skill_name:
            return SkillCategory.KNOWLEDGE_SYNTHESIS
        if "generate" in skill_name or "code" in skill_name:
            return SkillCategory.CODE_GENERATION
        if "process" in skill_name or "data" in skill_name:
            return SkillCategory.DATA_PROCESSING
        if "analyze" in skill_name or "analysis" in skill_name:
            return SkillCategory.ANALYSIS
        if "optimize" in skill_name or "optimization" in skill_name:
            return SkillCategory.OPTIMIZATION
        if "integration" in skill_name or "connect" in skill_name:
            return SkillCategory.INTEGRATION
        return SkillCategory.UTILITY

    def _format_examples_section(self, examples: list[dict[str, Any]], level: DisclosureLevel) -> str:
        """Format examples into a documentation section."""

        if not examples:
            return ""

        if level == DisclosureLevel.METADATA:
            return "**Examples**: Available"

        if level == DisclosureLevel.SUMMARY:
            if examples:
                return f"**Example**: {examples[0].get('description', 'Basic usage')}"
            return ""

        if level in [DisclosureLevel.DETAILED, DisclosureLevel.FULL]:
            formatted_examples = []
            for i, example in enumerate(examples[:5], 1):  # Limit to 5 examples
                formatted_examples.append(f"**Example {i}**: {example.get('description', 'No description')}")

                if "code" in example:
                    formatted_examples.append(f"```python\n{example['code']}\n```")

                if "explanation" in example:
                    formatted_examples.append(f"*{example['explanation']}*")

                formatted_examples.append("")  # Empty line between examples

            return "### Examples\n\n" + "\n".join(formatted_examples)

        return ""

    def _create_version_changes(self, old_docs: dict[str, Any] | None, new_docs: dict[str, Any]) -> list[Any]:
        """Create version change entries."""
        from ..core.version_manager import ChangeType
        from ..core.version_manager import DocumentationChange

        changes = []

        if not old_docs:
            # Initial documentation
            changes.append(
                DocumentationChange(
                    version_from="0.0.0",
                    version_to="1.0.0",
                    change_type=ChangeType.MAJOR,
                    description="Initial documentation generation",
                    affected_sections=["all"],
                )
            )
        else:
            # Compare versions to determine changes
            old_hash = self._calculate_docs_hash(old_docs)
            new_hash = self._calculate_docs_hash(new_docs)

            if old_hash != new_hash:
                changes.append(
                    DocumentationChange(
                        version_from="previous",
                        version_to="current",
                        change_type=ChangeType.PATCH,
                        description="Documentation updated",
                        affected_sections=self._find_changed_sections(old_docs, new_docs),
                    )
                )

        return changes

    def _calculate_docs_hash(self, documentation: dict[str, Any]) -> str:
        """Calculate hash for documentation comparison."""
        import hashlib
        import json

        docs_str = json.dumps(documentation, sort_keys=True, separators=(",", ":"))
        return hashlib.md5(docs_str.encode()).hexdigest()[:16]

    def _find_changed_sections(self, old_docs: dict[str, Any], new_docs: dict[str, Any]) -> list[str]:
        """Find sections that changed between documentation versions."""

        changed_sections = []

        # Compare all levels
        for level in ["metadata", "summary", "detailed", "full"]:
            if level in old_docs and level in new_docs:
                if old_docs[level] != new_docs[level]:
                    changed_sections.append(level)
            elif level in new_docs:
                changed_sections.append(f"{level}_added")
            elif level in old_docs:
                changed_sections.append(f"{level}_removed")

        return changed_sections or ["unknown"]

    def _generate_metadata(
        self, spec: SkillDocumentationSpec, analysis: dict[str, Any], validation_result: ValidationResult | None
    ) -> dict[str, Any]:
        """Generate metadata for the documentation."""

        metadata = {
            "generated_at": datetime.now().isoformat(),
            "skill_name": spec.skill_name,
            "category": spec.category.value,
            "generator": "AutomaticDocumentationGenerator",
            "version": "1.0.0",
            "tags": spec.tags,
            "complexity": analysis.get("complexity", "unknown"),
            "input_count": len(spec.inputs),
            "output_count": len(spec.outputs),
            "dependency_count": len(spec.dependencies),
        }

        if validation_result:
            metadata["validation"] = {
                "is_valid": validation_result.is_valid,
                "issues_found": validation_result.total_issues,
                "critical_issues": validation_result.critical_issues,
                "validation_score": validation_result.validation_score,
                "tested_examples": len(validation_result.tested_examples),
            }

        return metadata
