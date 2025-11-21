#!/usr/bin/env python3
"""
Script to convert Framework B skills to Framework A compatibility
"""

import os
import re
from pathlib import Path


def convert_skill_file(file_path: Path) -> bool:
    """Convert a skill file from Framework B to Framework A"""
    print(f"Converting {file_path}...")

    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Step 1: Update imports
        content = re.sub(
            r"from \.\.skills_framework\.skill_template import (BaseSkill|SkillContext|SkillResult)",
            lambda m: f"from ..skills_framework.base_skill import {m.group(1)}",
            content,
        )

        # Step 2: Remove SkillLevel import if present
        content = re.sub(r"from \.\.skills_framework\.skill_template import SkillLevel.*?\n", "", content)

        # Step 3: Find the class definition
        class_pattern = r"class (\w+Skill)\(BaseSkill\):"
        class_match = re.search(class_pattern, content)

        if not class_match:
            print(f"  No BaseSkill class found in {file_path}")
            return False

        class_name = class_match.group(1)

        # Step 4: Remove @property decorators for description and tags
        content = re.sub(
            r"    @property\s+def description\(self\) -> str:.*?(?=\n    def|\n\n|\Z)", "", content, flags=re.DOTALL
        )
        content = re.sub(
            r"    @property\s+def tags\(self\) -> list\[str\]:.*?(?=\n    def|\n\n|\Z)", "", content, flags=re.DOTALL
        )

        # Step 5: Add constructor after class definition
        constructor = f'''    def __init__(self):
        super().__init__(
            skill_id="{class_name.lower().replace("skill", "_")}",
            name="{class_name.replace("Skill", " Expert")}",
            description="Expert skill for {class_name.replace("Skill", "").lower()}"
        )'''

        # Replace the class definition line and add constructor
        content = re.sub(class_pattern, f"class {class_name}(BaseSkill):\n\n" + constructor, content)

        # Step 6: Replace can_handle method with validate_input and get_capabilities
        can_handle_pattern = r"    def can_handle\(self, context: SkillContext\) -> float:.*?(?=\n    def|\n\n|\Z)"
        if re.search(can_handle_pattern, content, flags=re.DOTALL):
            # Extract tags from can_handle method if present
            can_handle_match = re.search(can_handle_pattern, content, flags=re.DOTALL)
            if can_handle_match:
                can_handle_content = can_handle_match.group(0)

                # Extract confidence terms to create capabilities
                high_confidence = re.findall(r'"([^"]+)"', can_handle_content)
                capabilities = [cap for cap in high_confidence if len(cap.split()) <= 3]  # Short terms only

                if not capabilities:
                    capabilities = [f"{class_name.replace('Skill', '').lower()} expertise"]

        # Step 7: Replace execute method signature
        execute_pattern = (
            r"    def execute\(self, context: SkillContext, level: SkillLevel = SkillLevel\.SUMMARY\) -> SkillResult:"
        )
        content = re.sub(
            execute_pattern,
            "    async def execute(self, input_data: Any, context: SkillContext = None) -> SkillResult:",
            content,
        )

        # Step 8: Add required abstract methods if missing
        if "def validate_input(self" not in content:
            validate_method = '''    async def validate_input(self, input_data: Any) -> bool:
        """Validate input data before execution"""
        return isinstance(input_data, str) and len(input_data.strip()) > 0

    '''
            content = content.replace(constructor, constructor + "\n" + validate_method)

        if "def get_capabilities(self" not in content:
            capabilities_text = (
                ", ".join(capabilities)
                if "capabilities" in locals()
                else f"{class_name.replace('Skill', '').lower()} expertise"
            )
            capabilities_method = f'''    def get_capabilities(self) -> list[str]:
        """Get list of skill capabilities"""
        return [
            "{capabilities_text}",
            "Best practices",
            "Production solutions"
        ]

    '''
            content = content.replace(constructor, constructor + "\n" + capabilities_method)

        # Step 9: Update SkillResult usage in execute method
        skill_result_pattern = r"SkillResult\(\s*skill_name=self\.skill_name,.*?\)"
        content = re.sub(
            skill_result_pattern,
            "SkillResult(success=True, data=result, execution_time=execution_time, tokens_used=estimate_tokens(result))",
            content,
            flags=re.DOTALL,
        )

        # Step 10: Write back to file
        with open(file_path, "w") as f:
            f.write(content)

        print(f"  Successfully converted {file_path}")
        return True

    except Exception as e:
        print(f"  Error converting {file_path}: {e}")
        return False


def main():
    """Convert all Framework B skill files"""
    base_path = Path("amplifier/skills")

    # Find all Python files that import from skill_template
    skill_files = []
    for file_path in base_path.rglob("*.py"):
        if file_path.name == "__init__.py":
            continue

        try:
            with open(file_path, "r") as f:
                content = f.read()
                if "from ..skills_framework.skill_template import BaseSkill" in content:
                    skill_files.append(file_path)
        except:
            continue

    print(f"Found {len(skill_files)} Framework B skill files to convert")

    success_count = 0
    for skill_file in skill_files:
        if convert_skill_file(skill_file):
            success_count += 1

    print(f"\nConverted {success_count}/{len(skill_files)} files successfully")


if __name__ == "__main__":
    main()
