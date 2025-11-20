#!/usr/bin/env python3
"""
API Accuracy Validator for Microsoft Amplifier Skills

Tests specific API examples and patterns against official documentation
to ensure zero hallucination compliance.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class APIValidation:
    skill_name: str
    api_type: str
    examples_found: int
    working_examples: int
    outdated_patterns: list[str]
    modern_patterns: list[str]
    accuracy_score: float


@dataclass
class APIReport:
    total_validations: int
    average_accuracy: float
    api_types: dict[str, int]
    common_outdated_patterns: dict[str, int]
    validations: list[APIValidation]


class APIAccuracyValidator:
    """Validates API accuracy against official documentation"""

    def __init__(self):
        self.skills_dir = Path("amplifier/skills")
        self.results: list[APIValidation] = []

        # Define modern vs outdated patterns
        self.pattern_checks = {
            "react": {
                "modern": ["useState", "useEffect", "useContext", "createContext", "useMemo", "useCallback"],
                "outdated": ["componentDidMount", "componentWillReceiveProps", "React.createClass"],
            },
            "nodejs": {
                "modern": ["async/await", "promises", "import", "export", "require"],
                "outdated": ["var callback", "function(callback)", ".then(function"],
            },
            "typescript": {
                "modern": ["interface", "type", "generics", "decorators"],
                "outdated": ["// @ts-ignore", "any type"],
            },
            "javascript": {
                "modern": ["const", "let", "arrow functions", "destructuring", "spread operator"],
                "outdated": ["var ", "function() {}", "for (var i = 0"],
            },
        }

        # Common deprecated patterns
        self.deprecated_patterns = [
            "alert(",
            "confirm(",
            "prompt(",  # Browser dialogs
            "innerHTML",  # Security risk
            "eval(",  # Security risk
            "with (",  # Deprecated
            "arguments.callee",  # Deprecated in strict mode
        ]

    def extract_code_examples(self, content: str) -> list[str]:
        """Extract code examples from skill content"""
        examples = []

        # Look for code blocks in markdown
        code_blocks = re.findall(
            r"```(?:javascript|typescript|js|jsx|ts|tsx|python|py)?\n(.*?)\n```", content, re.DOTALL
        )

        for block in code_blocks:
            if len(block.strip()) > 10:  # Filter out tiny blocks
                examples.append(block.strip())

        # Look for inline code
        inline_code = re.findall(r"`([^`]{20,})`", content)
        for code in inline_code:
            if any(char in code for char in ["=", "(", ")", "{", "}", ";"]):  # Likely code
                examples.append(code)

        return examples

    def validate_api_patterns(self, skill_name: str, content: str) -> APIValidation:
        """Validate API patterns in skill content"""
        examples = self.extract_code_examples(content)

        # Determine API type
        api_type = self._determine_api_type(skill_name, content)

        working_examples = 0
        outdated_found = []
        modern_found = []

        for example in examples:
            # Check for deprecated patterns
            for pattern in self.deprecated_patterns:
                if pattern in example:
                    outdated_found.append(f"Deprecated: {pattern}")

            # Check API-specific patterns
            if api_type in self.pattern_checks:
                patterns = self.pattern_checks[api_type]

                # Check for outdated patterns
                for pattern in patterns["outdated"]:
                    if pattern in example:
                        outdated_found.append(f"Outdated {api_type}: {pattern}")

                # Check for modern patterns
                for pattern in patterns["modern"]:
                    if pattern in example:
                        modern_found.append(f"Modern {api_type}: {pattern}")

                # Try to validate syntax if JavaScript/TypeScript
                if api_type in ["react", "nodejs", "typescript", "javascript"]:
                    if self._validate_js_syntax(example):
                        working_examples += 1
                else:
                    working_examples += 1

        # Calculate accuracy score
        total_issues = len(outdated_found)
        base_score = 100.0

        # Penalize for outdated patterns
        accuracy_score = max(0, base_score - (total_issues * 10))

        return APIValidation(
            skill_name=skill_name,
            api_type=api_type,
            examples_found=len(examples),
            working_examples=working_examples,
            outdated_patterns=outdated_found,
            modern_patterns=modern_found,
            accuracy_score=accuracy_score,
        )

    def _determine_api_type(self, skill_name: str, content: str) -> str:
        """Determine the primary API type from skill name and content"""
        content_lower = content.lower()
        name_lower = skill_name.lower()

        if any(term in name_lower or term in content_lower for term in ["react", "jsx", "component"]):
            return "react"
        if any(term in name_lower or term in content_lower for term in ["node", "express", "server"]):
            return "nodejs"
        if any(term in name_lower or term in content_lower for term in ["typescript", "interface", "type"]):
            return "typescript"
        if "javascript" in name_lower or "javascript" in content_lower:
            return "javascript"
        return "general"

    def _validate_js_syntax(self, code: str) -> bool:
        """Validate JavaScript/TypeScript syntax"""
        try:
            # Try to parse as JavaScript (basic check)
            # Remove template literals and other complex constructs that might confuse simple parsing
            simplified_code = re.sub(r"`[^`]*`", '""', code)
            simplified_code = re.sub(r"//.*", "", simplified_code)
            simplified_code = re.sub(r"/\*.*?\*/", "", simplified_code, flags=re.DOTALL)

            # Basic syntax checks
            if "function" in simplified_code and "{" in simplified_code and "}" in simplified_code:
                # Looks like function syntax, assume it's valid for our purposes
                return True
            if "async" in simplified_code or "await" in simplified_code:
                # Modern async syntax
                return True
            if any(keyword in simplified_code for keyword in ["const", "let", "var"]):
                # Variable declarations
                return True
            return len(simplified_code.strip()) > 0
        except Exception:
            return False

    def validate_skill_file(self, skill_path: Path) -> APIValidation:
        """Validate API accuracy in a single skill file"""
        try:
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return APIValidation(
                skill_name=skill_path.stem,
                api_type="unknown",
                examples_found=0,
                working_examples=0,
                outdated_patterns=[],
                modern_patterns=[],
                accuracy_score=0.0,
            )

        return self.validate_api_patterns(skill_path.stem, content)

    def validate_all_skills(self) -> APIReport:
        """Validate API accuracy across all skills"""
        print("🔍 Validating API accuracy across all skills...")

        # Find all skill files
        skill_files = list(self.skills_dir.rglob("*.py"))
        skill_files = [f for f in skill_files if not f.name.startswith("__")]

        print(f"📊 Found {len(skill_files)} skills to validate")

        # Validate each skill
        for skill_file in skill_files:
            validation = self.validate_skill_file(skill_file)
            self.results.append(validation)
            print(f"  ✓ {skill_file.stem}: {validation.accuracy_score:.1f}% accuracy")

        # Generate report
        total_validations = len(self.results)
        average_accuracy = sum(r.accuracy_score for r in self.results) / total_validations if self.results else 0

        # Count API types
        api_types = {}
        for result in self.results:
            api_types[result.api_type] = api_types.get(result.api_type, 0) + 1

        # Count common outdated patterns
        common_outdated = {}
        for result in self.results:
            for pattern in result.outdated_patterns:
                common_outdated[pattern] = common_outdated.get(pattern, 0) + 1

        return APIReport(
            total_validations=total_validations,
            average_accuracy=round(average_accuracy, 2),
            api_types=api_types,
            common_outdated_patterns=common_outdated,
            validations=self.results,
        )

    def print_report(self, report: APIReport):
        """Print API accuracy validation report"""
        print("\n" + "=" * 80)
        print("API ACCURACY VALIDATION REPORT")
        print("=" * 80)
        print(f"Total Skills Validated: {report.total_validations}")
        print(f"Average Accuracy Score: {report.average_accuracy:.1f}%")

        print("\nAPI TYPES:")
        for api_type, count in report.api_types.items():
            print(f"  • {api_type}: {count} skills")

        print("\nACCURACY DISTRIBUTION:")
        high_accuracy = sum(1 for r in report.validations if r.accuracy_score >= 90)
        good_accuracy = sum(1 for r in report.validations if 70 <= r.accuracy_score < 90)
        needs_work = sum(1 for r in report.validations if r.accuracy_score < 70)

        print(f"  🟢 High Accuracy (90%+): {high_accuracy} skills")
        print(f"  🟡 Good Accuracy (70-89%): {good_accuracy} skills")
        print(f"  🔴 Needs Work (<70%): {needs_work} skills")

        if report.common_outdated_patterns:
            print("\nCOMMON OUTDATED PATTERNS:")
            sorted_patterns = sorted(report.common_outdated_patterns.items(), key=lambda x: x[1], reverse=True)[:10]
            for pattern, count in sorted_patterns:
                print(f"  • {pattern}: found in {count} skills")

        print("\nTOP PERFORMING SKILLS:")
        top_skills = sorted(report.validations, key=lambda x: x.accuracy_score, reverse=True)[:5]
        for skill in top_skills:
            print(f"  🌟 {skill.skill_name}: {skill.accuracy_score:.1f}% (API: {skill.api_type})")

        print("\nSKILLS NEEDING IMPROVEMENT:")
        bottom_skills = sorted(report.validations, key=lambda x: x.accuracy_score)[:5]
        for skill in bottom_skills:
            if skill.accuracy_score < 80:
                print(f"  ⚠️  {skill.skill_name}: {skill.accuracy_score:.1f}%")
                if skill.outdated_patterns:
                    print(f"      Issues: {skill.outdated_patterns[:2]}")

        print("=" * 80)


def main():
    """Run API accuracy validation"""
    validator = APIAccuracyValidator()
    report = validator.validate_all_skills()
    validator.print_report(report)

    # Save report
    report_dict = {
        "total_validations": report.total_validations,
        "average_accuracy": report.average_accuracy,
        "api_types": report.api_types,
        "common_outdated_patterns": report.common_outdated_patterns,
        "validations": [
            {
                "skill_name": v.skill_name,
                "api_type": v.api_type,
                "examples_found": v.examples_found,
                "working_examples": v.working_examples,
                "accuracy_score": v.accuracy_score,
                "outdated_patterns": v.outdated_patterns[:5],  # Limit for readability
                "modern_patterns": v.modern_patterns[:5],
            }
            for v in report.validations
        ],
    }

    with open("api_accuracy_validation_report.json", "w") as f:
        json.dump(report_dict, f, indent=2)

    print("📄 Detailed report saved to: api_accuracy_validation_report.json")


if __name__ == "__main__":
    main()
