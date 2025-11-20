#!/usr/bin/env python3
"""
Lightweight Skills Validation System for Microsoft Amplifier

Focused validation that prioritizes syntax and structure over complex import testing.
"""

import ast
import json
import time
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SkillSummary:
    name: str
    path: str
    category: str
    lines: int
    has_classes: bool
    has_functions: bool
    has_docstring: bool
    syntax_valid: bool
    imports: list[str]


@dataclass
class ValidationReport:
    total_skills: int
    syntax_valid: int
    categories: dict[str, int]
    avg_lines: float
    documented_skills: int
    skill_summaries: list[SkillSummary]
    timestamp: str


class LightweightValidator:
    """Fast, syntax-focused skills validator"""

    def __init__(self):
        self.skills_dir = Path("amplifier/skills")
        self.results: list[SkillSummary] = []

    def discover_skills(self) -> dict[str, list[Path]]:
        """Find all Python skill files"""
        categories = {}

        for skill_file in self.skills_dir.rglob("*.py"):
            if skill_file.name.startswith("__"):
                continue

            relative_path = skill_file.relative_to(self.skills_dir)
            parts = relative_path.parts

            # Determine category
            category = parts[0] if parts else "other"
            if category not in categories:
                categories[category] = []
            categories[category].append(skill_file)

        return categories

    def validate_skill_file(self, skill_path: Path) -> SkillSummary:
        """Analyze a single skill file"""

        try:
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
        except Exception:
            return SkillSummary(
                name=skill_path.stem,
                path=str(skill_path),
                category="unknown",
                lines=0,
                has_classes=False,
                has_functions=False,
                has_docstring=False,
                syntax_valid=False,
                imports=[],
            )

        # Parse AST to check syntax and structure
        try:
            tree = ast.parse(content)
            syntax_valid = True
        except SyntaxError:
            tree = None
            syntax_valid = False

        has_classes = False
        has_functions = False
        has_docstring = False
        imports = []

        if tree:
            # Check for docstring
            if (
                tree.body
                and isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, ast.Constant)
                and isinstance(tree.body[0].value.value, str)
            ):
                has_docstring = True

            # Analyze AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                    has_classes = True
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    has_functions = True
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

        # Determine category from path
        relative_path = skill_path.relative_to(self.skills_dir)
        category = relative_path.parts[0] if relative_path.parts else "other"

        return SkillSummary(
            name=skill_path.stem,
            path=str(skill_path),
            category=category,
            lines=len(lines),
            has_classes=has_classes,
            has_functions=has_functions,
            has_docstring=has_docstring,
            syntax_valid=syntax_valid,
            imports=imports,
        )

    def validate_all_skills(self) -> ValidationReport:
        """Validate all skills"""
        print("🔍 Starting lightweight skills validation...")

        categories = self.discover_skills()
        total_skills = sum(len(skills) for skills in categories.values())

        print(f"📊 Found {total_skills} skills in {len(categories)} categories:")
        for cat, skills in categories.items():
            print(f"  • {cat}: {len(skills)} skills")

        # Validate each skill
        for category, skill_files in categories.items():
            for skill_file in skill_files:
                summary = self.validate_skill_file(skill_file)
                self.results.append(summary)

        # Generate report
        syntax_valid = sum(1 for r in self.results if r.syntax_valid)
        documented_skills = sum(1 for r in self.results if r.has_docstring)
        avg_lines = sum(r.lines for r in self.results) / len(self.results) if self.results else 0

        return ValidationReport(
            total_skills=total_skills,
            syntax_valid=syntax_valid,
            categories={cat: len(skills) for cat, skills in categories.items()},
            avg_lines=round(avg_lines, 1),
            documented_skills=documented_skills,
            skill_summaries=self.results,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def print_report(self, report: ValidationReport):
        """Print validation report"""
        print("\n" + "=" * 80)
        print("LIGHTWEIGHT SKILLS VALIDATION REPORT")
        print("=" * 80)
        print(f"Timestamp: {report.timestamp}")
        print(f"Total Skills: {report.total_skills}")
        print(f"Syntax Valid: {report.syntax_valid} ({report.syntax_valid / report.total_skills * 100:.1f}%)")
        print(
            f"With Documentation: {report.documented_skills} ({report.documented_skills / report.total_skills * 100:.1f}%)"
        )
        print(f"Average Lines: {report.avg_lines}")

        print("\nCATEGORIES:")
        for category, count in report.categories.items():
            print(f"  • {category}: {count} skills")

        # Issues by category
        print("\nSYNTAX ISSUES BY CATEGORY:")
        syntax_issues = [r for r in report.skill_summaries if not r.syntax_valid]
        if syntax_issues:
            issues_by_category = {}
            for skill in syntax_issues:
                if skill.category not in issues_by_category:
                    issues_by_category[skill.category] = []
                issues_by_category[skill.category].append(skill.name)

            for category, skills in issues_by_category.items():
                print(f"  • {category}: {len(skills)} skills with syntax issues")
                for skill in skills[:3]:  # Show first 3
                    print(f"    - {skill}")
                if len(skills) > 3:
                    print(f"    ... and {len(skills) - 3} more")
        else:
            print("  ✅ No syntax issues found!")

        # Missing documentation
        print("\nMISSING DOCUMENTATION:")
        missing_docs = [r for r in report.skill_summaries if not r.has_docstring and r.syntax_valid]
        if missing_docs:
            print(f"  📝 {len(missing_docs)} skills missing documentation:")
            for skill in missing_docs[:5]:  # Show first 5
                print(f"    - {skill.name}")
            if len(missing_docs) > 5:
                print(f"    ... and {len(missing_docs) - 5} more")
        else:
            print("  ✅ All skills have documentation!")

        # Most common imports
        print("\nCOMMON IMPORTS:")
        import_counts = {}
        for skill in report.skill_summaries:
            for imp in skill.imports:
                base_import = imp.split(".")[0]
                import_counts[base_import] = import_counts.get(base_import, 0) + 1

        top_imports = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for imp, count in top_imports:
            print(f"  • {imp}: used in {count} skills")

        # Quality assessment
        print("\nQUALITY ASSESSMENT:")
        quality_score = (report.syntax_valid / report.total_skills) * 50 + (
            report.documented_skills / report.total_skills
        ) * 50

        if quality_score >= 80:
            status = "🟢 EXCELLENT"
        elif quality_score >= 60:
            status = "🟡 GOOD"
        elif quality_score >= 40:
            status = "🟠 NEEDS WORK"
        else:
            status = "🔴 CRITICAL"

        print(f"  Overall Quality: {quality_score:.1f}/100 - {status}")

        print("=" * 80)


def main():
    """Run lightweight validation"""
    validator = LightweightValidator()
    report = validator.validate_all_skills()
    validator.print_report(report)

    # Save report
    with open("skills_validation_light_report.json", "w") as f:
        json.dump(asdict(report), f, indent=2, default=str)

    print("📄 Detailed report saved to: skills_validation_light_report.json")


if __name__ == "__main__":
    main()
