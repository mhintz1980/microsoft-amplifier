"""
Documentation Template Engine

Creates standardized, consistent documentation templates for all skill types.
Follows ruthless simplicity principles with agent-optimized structure.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pathlib import Path
import json
import re

from ..utils.token_utils import estimate_tokens


class SkillCategory(Enum):
    """Categories of skills with different documentation requirements."""

    CONTEXT_MANAGEMENT = "context_management"
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"
    CODE_GENERATION = "code_generation"
    DATA_PROCESSING = "data_processing"
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    INTEGRATION = "integration"
    UTILITY = "utility"


@dataclass
class DocumentationSection:
    """A section of skill documentation with progressive disclosure levels."""

    name: str
    required: bool = True
    metadata_template: str = ""
    summary_template: str = ""
    full_template: str = ""
    token_budget: Dict[str, int] = field(default_factory=lambda: {"metadata": 50, "summary": 200, "full": 800})
    validation_rules: List[str] = field(default_factory=list)


@dataclass
class SkillDocumentationSpec:
    """Complete specification for skill documentation."""

    skill_name: str
    category: SkillCategory
    skill_class: str
    description: str
    tags: List[str]
    inputs: List[Dict[str, Any]]
    outputs: List[Dict[str, Any]]
    dependencies: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    related_skills: List[str] = field(default_factory=list)
    custom_sections: List[DocumentationSection] = field(default_factory=list)


class DocumentationTemplate:
    """Template engine for consistent skill documentation."""

    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        self._load_templates()

    def _load_templates(self):
        """Load base templates for different skill categories."""
        self.category_templates = self._initialize_category_templates()
        self.base_sections = self._initialize_base_sections()

    def _initialize_category_templates(self) -> Dict[SkillCategory, Dict[str, str]]:
        """Initialize templates for each skill category."""
        return {
            SkillCategory.CONTEXT_MANAGEMENT: {
                "metadata": "# {skill_name}\n**Category**: {category}\n**Purpose**: {description}",
                "summary": "## {skill_name}\n\n{description}\n\n**Key Features**:\n{features}\n\n**Use Cases**:\n{use_cases}",
                "full": "## {skill_name}\n\n{description}\n\n### Overview\n{overview}\n\n### Key Features\n{features}\n\n### Usage\n{usage}\n\n### Examples\n{examples}\n\n### Performance\n{performance}",
            },
            SkillCategory.KNOWLEDGE_SYNTHESIS: {
                "metadata": "# {skill_name}\n**Category**: {category}\n**Purpose**: {description}",
                "summary": "## {skill_name}\n\n{description}\n\n**Synthesis Type**: {synthesis_type}\n**Input Requirements**: {input_req}\n**Output Format**: {output_format}",
                "full": "## {skill_name}\n\n{description}\n\n### Synthesis Approach\n{approach}\n\n### Input Processing\n{input_processing}\n\n### Output Generation\n{output_generation}\n\n### Quality Assurance\n{quality_assurance}\n\n### Examples\n{examples}",
            },
            SkillCategory.CODE_GENERATION: {
                "metadata": "# {skill_name}\n**Category**: {category}\n**Language**: {language}",
                "summary": "## {skill_name}\n\n{description}\n\n**Generates**: {generates}\n**Frameworks**: {frameworks}",
                "full": "## {skill_name}\n\n{description}\n\n### Generated Code Patterns\n{patterns}\n\n### Template System\n{templates}\n\n### Quality Checks\n{quality_checks}\n\n### Integration Points\n{integration}",
            },
            # Add more categories as needed
            SkillCategory.UTILITY: {
                "metadata": "# {skill_name}\n**Category**: {category}\n**Purpose**: {description}",
                "summary": "## {skill_name}\n\n{description}\n\n**Function**: {function}",
                "full": "## {skill_name}\n\n{description}\n\n### Implementation\n{implementation}\n\n### Usage Examples\n{examples}\n\n### Edge Cases\n{edge_cases}",
            },
        }

    def _initialize_base_sections(self) -> List[DocumentationSection]:
        """Initialize base documentation sections for all skills."""
        return [
            DocumentationSection(
                name="overview",
                metadata_template="# {skill_name}\n**Purpose**: {description}",
                summary_template="## {skill_name}\n\n{description}\n\n**Tags**: {tags}",
                full_template="## {skill_name}\n\n{description}\n\n### Purpose\n{purpose}\n\n### Tags\n{tags}\n\n### Category\n{category}",
            ),
            DocumentationSection(
                name="interface",
                required=True,
                metadata_template="**Inputs**: {input_count}\n**Outputs**: {output_count}",
                summary_template="### Interface\n\n**Inputs**:\n{inputs_summary}\n\n**Outputs**:\n{outputs_summary}",
                full_template="### Interface\n\n#### Inputs\n{inputs_detailed}\n\n#### Outputs\n{outputs_detailed}\n\n#### Dependencies\n{dependencies}",
            ),
            DocumentationSection(
                name="usage",
                required=True,
                metadata_template="**Usage**: Basic",
                summary_template="### Usage\n\n{usage_summary}\n\n**Example**:\n```python\n{example_basic}\n```",
                full_template="### Usage\n\n{usage_detailed}\n\n### Examples\n\n{examples_detailed}\n\n### Best Practices\n{best_practices}",
            ),
            DocumentationSection(
                name="performance",
                required=False,
                metadata_template="**Performance**: Optimized",
                summary_template="### Performance\n\n**Token Efficiency**: {token_efficiency}\n**Speed**: {speed}",
                full_template="### Performance Characteristics\n\n**Token Usage**:\n{token_usage}\n\n**Execution Time**:\n{execution_time}\n\n**Memory Usage**:\n{memory_usage}\n\n**Optimization Notes**:\n{optimization_notes}",
            ),
        ]

    def generate_documentation(self, spec: SkillDocumentationSpec, level: str = "full") -> Dict[str, Any]:
        """Generate documentation for a skill at the specified level."""

        if level not in ["metadata", "summary", "full"]:
            raise ValueError(f"Invalid documentation level: {level}")

        # Get category template
        category_template = self.category_templates.get(spec.category, self.category_templates[SkillCategory.UTILITY])

        # Generate content for each section
        sections = {}
        total_tokens = 0

        for section in self.base_sections:
            if section.required or level == "full":
                section_content = self._generate_section_content(section, spec, level, category_template)
                sections[section.name] = section_content
                total_tokens += estimate_tokens(section_content)

        # Add custom sections
        for custom_section in spec.custom_sections:
            section_content = self._generate_custom_section(custom_section, spec, level)
            sections[custom_section.name] = section_content
            total_tokens += estimate_tokens(section_content)

        # Validate token budgets
        self._validate_token_budgets(sections, level)

        return {
            "skill_name": spec.skill_name,
            "level": level,
            "sections": sections,
            "total_tokens": total_tokens,
            "metadata": self._extract_metadata(spec),
        }

    def _generate_section_content(
        self, section: DocumentationSection, spec: SkillDocumentationSpec, level: str, category_template: Dict[str, str]
    ) -> str:
        """Generate content for a specific section."""

        template = getattr(section, f"{level}_template")
        if not template:
            # Fall back to category template or base template
            template = category_template.get(level, "")

        # Prepare template variables
        variables = self._prepare_template_variables(spec)

        # Fill template
        try:
            content = template.format(**variables)
        except KeyError as e:
            # Missing variable - use placeholder
            content = template.replace(f"{{{e.args[0]}}}", f"[{e.args[0].upper()}]")

        return content

    def _generate_custom_section(self, section: DocumentationSection, spec: SkillDocumentationSpec, level: str) -> str:
        """Generate content for custom sections."""

        template = getattr(section, f"{level}_template")
        if not template:
            return ""

        variables = self._prepare_template_variables(spec)

        try:
            return template.format(**variables)
        except KeyError:
            return template

    def _prepare_template_variables(self, spec: SkillDocumentationSpec) -> Dict[str, str]:
        """Prepare variables for template substitution."""

        return {
            "skill_name": spec.skill_name,
            "category": spec.category.value,
            "description": spec.description,
            "tags": ", ".join(spec.tags),
            "input_count": str(len(spec.inputs)),
            "output_count": str(len(spec.outputs)),
            "dependencies": ", ".join(spec.dependencies) if spec.dependencies else "None",
            "inputs_summary": self._format_inputs_summary(spec.inputs),
            "outputs_summary": self._format_outputs_summary(spec.outputs),
            "inputs_detailed": self._format_inputs_detailed(spec.inputs),
            "outputs_detailed": self._format_outputs_detailed(spec.outputs),
            "examples": self._format_examples(spec.examples),
            "related_skills": ", ".join(spec.related_skills) if spec.related_skills else "None",
        }

    def _format_inputs_summary(self, inputs: List[Dict[str, Any]]) -> str:
        """Format inputs for summary level."""
        if not inputs:
            return "None"

        return "\n".join(
            [
                f"- {inp.get('name', 'unnamed')}: {inp.get('type', 'any')}"
                for inp in inputs[:3]  # Limit for summary
            ]
        )

    def _format_outputs_summary(self, outputs: List[Dict[str, Any]]) -> str:
        """Format outputs for summary level."""
        if not outputs:
            return "None"

        return "\n".join(
            [
                f"- {out.get('name', 'unnamed')}: {out.get('type', 'any')}"
                for out in outputs[:3]  # Limit for summary
            ]
        )

    def _format_inputs_detailed(self, inputs: List[Dict[str, Any]]) -> str:
        """Format inputs for detailed level."""
        if not inputs:
            return "No inputs required"

        formatted = []
        for inp in inputs:
            formatted.append(
                f"**{inp.get('name', 'unnamed')}** ({inp.get('type', 'any')}): "
                f"{inp.get('description', 'No description')}"
            )
            if inp.get("required", False):
                formatted[-1] += " *(required)*"

        return "\n".join(formatted)

    def _format_outputs_detailed(self, outputs: List[Dict[str, Any]]) -> str:
        """Format outputs for detailed level."""
        if not outputs:
            return "No outputs"

        formatted = []
        for out in outputs:
            formatted.append(
                f"**{out.get('name', 'unnamed')}** ({out.get('type', 'any')}): "
                f"{out.get('description', 'No description')}"
            )

        return "\n".join(formatted)

    def _format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples for documentation."""
        if not examples:
            return "No examples available"

        formatted = []
        for i, example in enumerate(examples[:3], 1):  # Limit examples
            formatted.append(f"**Example {i}**: {example.get('description', 'No description')}")
            if "code" in example:
                formatted.append(f"```python\n{example['code']}\n```")

        return "\n\n".join(formatted)

    def _validate_token_budgets(self, sections: Dict[str, str], level: str):
        """Validate that sections stay within token budgets."""
        for section_name, content in sections.items():
            tokens = estimate_tokens(content)

            # Find the section definition
            section_def = None
            for section in self.base_sections:
                if section.name == section_name:
                    section_def = section
                    break

            if section_def and tokens > section_def.token_budget.get(level, 1000):
                print(
                    f"Warning: Section '{section_name}' exceeds token budget ({tokens} > {section_def.token_budget[level]})"
                )

    def _extract_metadata(self, spec: SkillDocumentationSpec) -> Dict[str, Any]:
        """Extract metadata for indexing and discovery."""
        return {
            "name": spec.skill_name,
            "category": spec.category.value,
            "tags": spec.tags,
            "description": spec.description,
            "input_count": len(spec.inputs),
            "output_count": len(spec.outputs),
            "dependencies": spec.dependencies,
            "related_skills": spec.related_skills,
            "has_examples": len(spec.examples) > 0,
        }

    def create_skill_spec(
        self, skill_class: type, category: SkillCategory, custom_data: Optional[Dict[str, Any]] = None
    ) -> SkillDocumentationSpec:
        """Create a documentation specification from a skill class."""

        # Extract information from the skill class
        skill_name = skill_class.__name__.replace("Skill", "").lower()

        # Try to get description from docstring or class attribute
        description = getattr(skill_class, "description", "")
        if not description and skill_class.__doc__:
            description = skill_class.__doc__.strip().split("\n")[0]

        tags = getattr(skill_class, "tags", [])

        # Extract method signatures for inputs/outputs
        inputs = []
        outputs = []

        if hasattr(skill_class, "execute"):
            # Analyze execute method signature
            import inspect

            sig = inspect.signature(skill_class.execute)
            for param_name, param in sig.parameters.items():
                if param_name not in ["self", "context", "level"]:
                    inputs.append(
                        {
                            "name": param_name,
                            "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "any",
                            "required": param.default == inspect.Parameter.empty,
                            "description": f"Parameter {param_name}",
                        }
                    )

        return SkillDocumentationSpec(
            skill_name=skill_name,
            category=category,
            skill_class=skill_class.__name__,
            description=description,
            tags=tags,
            inputs=inputs,
            outputs=outputs,
            **(custom_data or {}),
        )

    def save_template(self, category: SkillCategory, templates: Dict[str, str]):
        """Save custom templates for a category."""
        self.category_templates[category] = templates

        # Persist to disk
        template_file = self.templates_dir / f"{category.value}_templates.json"
        with open(template_file, "w") as f:
            json.dump(templates, f, indent=2)

    def load_template(self, category: SkillCategory) -> Dict[str, str]:
        """Load custom templates for a category."""
        template_file = self.templates_dir / f"{category.value}_templates.json"

        if template_file.exists():
            with open(template_file, "r") as f:
                return json.load(f)

        return self.category_templates.get(category, {})
