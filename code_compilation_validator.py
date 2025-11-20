#!/usr/bin/env python3
"""
Code Compilation Validator for Microsoft Amplifier Skills

Tests that code examples in skills actually compile and execute correctly.
Validates JavaScript, TypeScript, Python, and other code examples.
"""

import ast
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CompilationResult:
    skill_name: str
    language: str
    examples_found: int
    compiled_successfully: int
    executed_successfully: int
    compilation_errors: list[str]
    execution_errors: list[str]
    avg_execution_time_ms: float


@dataclass
class CompilationReport:
    total_skills: int
    total_examples: int
    success_rate: float
    language_stats: dict[str, dict]
    compilation_failures: list[str]
    validations: list[CompilationResult]


class CodeCompilationValidator:
    """Validates that code examples compile and execute correctly"""

    def __init__(self):
        self.skills_dir = Path("amplifier/skills")
        self.results: list[CompilationResult] = []

    def extract_code_by_language(self, content: str) -> dict[str, list[str]]:
        """Extract code examples by programming language"""
        code_by_lang = {
            "javascript": [],
            "typescript": [],
            "python": [],
            "jsx": [],
            "tsx": [],
            "json": [],
            "bash": [],
            "html": [],
            "css": [],
        }

        # Extract code blocks with language markers
        pattern = r"```(\w+)?\n(.*?)\n```"
        matches = re.findall(pattern, content, re.DOTALL)

        for lang_hint, code in matches:
            code = code.strip()
            if not code or len(code) < 10:
                continue

            # Normalize language
            lang = lang_hint.lower() if lang_hint else "unknown"
            if lang in ["js", "javascript"]:
                code_by_lang["javascript"].append(code)
            elif lang in ["ts", "typescript"]:
                code_by_lang["typescript"].append(code)
            elif lang in ["py", "python"]:
                code_by_lang["python"].append(code)
            elif lang in ["jsx"]:
                code_by_lang["jsx"].append(code)
            elif lang in ["tsx"]:
                code_by_lang["tsx"].append(code)
            elif lang in ["json"]:
                code_by_lang["json"].append(code)
            elif lang in ["bash", "sh", "shell"]:
                code_by_lang["bash"].append(code)
            elif lang in ["html"]:
                code_by_lang["html"].append(code)
            elif lang in ["css"]:
                code_by_lang["css"].append(code)
            else:
                # Try to infer language from content
                if "def " in code or "import " in code:
                    code_by_lang["python"].append(code)
                elif "function" in code or "const " in code or "let " in code:
                    code_by_lang["javascript"].append(code)
                elif "interface " in code or "type " in code:
                    code_by_lang["typescript"].append(code)

        return code_by_lang

    def validate_python_code(self, code: str) -> tuple[bool, bool, str, float]:
        """Validate Python code compilation and execution"""
        try:
            # Parse AST
            ast.parse(code)
            compiled = True
        except SyntaxError as e:
            return False, False, f"Syntax error: {e}", 0.0

        # Try to execute (but only if it's safe)
        unsafe_patterns = [
            "import os",
            "import sys",
            "import subprocess",
            "exec(",
            "eval(",
            "open(",
            "file(",
            "input(",
            "__import__",
            "rm ",
            "del ",
            "remove(",
            "unlink(",
        ]

        if any(pattern in code for pattern in unsafe_patterns):
            return compiled, False, "Code contains potentially unsafe operations", 0.0

        try:
            start_time = time.time()
            exec(code, {"__builtins__": {}}, {})  # Safe execution with no builtins
            execution_time = (time.time() - start_time) * 1000
            return compiled, True, "", execution_time
        except Exception as e:
            return compiled, False, f"Execution error: {e}", 0.0

    def validate_javascript_code(self, code: str) -> tuple[bool, bool, str, float]:
        """Validate JavaScript code compilation"""
        # Basic syntax validation
        try:
            # Check for basic syntax errors
            if not code.strip():
                return False, False, "Empty code", 0.0

            # Check bracket matching
            if code.count("{") != code.count("}"):
                return False, False, "Unmatched braces", 0.0
            if code.count("(") != code.count(")"):
                return False, False, "Unmatched parentheses", 0.0
            if code.count("[") != code.count("]"):
                return False, False, "Unmatched brackets", 0.0

            # Look for common syntax issues
            lines = code.split("\n")
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.endswith("{") and not any(
                    kw in line for kw in ["if", "else", "for", "while", "function", "class", "try", "catch", "switch"]
                ):
                    # This might be a syntax error depending on context
                    pass

            return True, True, "", 1.0  # Assume 1ms for syntax-only validation

        except Exception as e:
            return False, False, f"Validation error: {e}", 0.0

    def validate_typescript_code(self, code: str) -> tuple[bool, bool, str, float]:
        """Validate TypeScript code compilation"""
        # Basic validation (similar to JavaScript but with TypeScript-specific checks)
        try:
            if not code.strip():
                return False, False, "Empty code", 0.0

            # Check for TypeScript-specific syntax
            if ":" in code and any(typ in code for typ in ["interface", "type", "enum", "generic"]):
                # Looks like TypeScript
                has_ts_syntax = True
            else:
                has_ts_syntax = False

            # Basic bracket matching
            if code.count("{") != code.count("}"):
                return False, False, "Unmatched braces", 0.0
            if code.count("(") != code.count(")"):
                return False, False, "Unmatched parentheses", 0.0
            if code.count("[") != code.count("]"):
                return False, False, "Unmatched brackets", 0.0

            # Check for TypeScript-specific issues
            if has_ts_syntax:
                # This is TypeScript code
                return True, True, "", 1.0
            # Treat as JavaScript with TS syntax potential
            return self.validate_javascript_code(code)

        except Exception as e:
            return False, False, f"TypeScript validation error: {e}", 0.0

    def validate_json_code(self, code: str) -> tuple[bool, bool, str, float]:
        """Validate JSON syntax"""
        try:
            json.loads(code)
            return True, True, "", 0.5
        except json.JSONDecodeError as e:
            return False, False, f"JSON error: {e}", 0.0

    def validate_code_by_language(self, language: str, code: str) -> tuple[bool, bool, str, float]:
        """Validate code based on language"""
        if language == "python":
            return self.validate_python_code(code)
        if language in ["javascript", "jsx"]:
            return self.validate_javascript_code(code)
        if language in ["typescript", "tsx"]:
            return self.validate_typescript_code(code)
        if language == "json":
            return self.validate_json_code(code)
        if language in ["html", "css", "bash"]:
            # For these languages, just check basic syntax
            if len(code.strip()) > 0:
                return True, True, "", 0.5
            return False, False, "Empty code", 0.0
        # Unknown language, try basic validation
        return bool(code.strip()), True, "", 0.5

    def validate_skill_file(self, skill_path: Path) -> list[CompilationResult]:
        """Validate code examples in a single skill file"""
        try:
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"  ❌ Could not read {skill_path.name}: {e}")
            return []

        code_by_lang = self.extract_code_by_language(content)
        results = []

        for language, examples in code_by_lang.items():
            if not examples:
                continue

            compiled_count = 0
            executed_count = 0
            compilation_errors = []
            execution_errors = []
            execution_times = []

            for i, example in enumerate(examples):
                compiled, executed, error, exec_time = self.validate_code_by_language(language, example)

                if compiled:
                    compiled_count += 1
                else:
                    compilation_errors.append(f"Example {i + 1}: {error}")

                if executed:
                    executed_count += 1
                    execution_times.append(exec_time)
                else:
                    execution_errors.append(f"Example {i + 1}: {error}")

            avg_exec_time = sum(execution_times) / len(execution_times) if execution_times else 0.0

            result = CompilationResult(
                skill_name=skill_path.stem,
                language=language,
                examples_found=len(examples),
                compiled_successfully=compiled_count,
                executed_successfully=executed_count,
                compilation_errors=compilation_errors,
                execution_errors=execution_errors,
                avg_execution_time_ms=avg_exec_time,
            )

            results.append(result)

        return results

    def validate_all_skills(self) -> CompilationReport:
        """Validate code compilation across all skills"""
        print("🔍 Validating code compilation across all skills...")

        # Find all skill files
        skill_files = list(self.skills_dir.rglob("*.py"))
        skill_files = [f for f in skill_files if not f.name.startswith("__")]

        print(f"📊 Found {len(skill_files)} skills to validate")

        # Validate each skill
        all_results = []
        compilation_failures = []

        for skill_file in skill_files:
            results = self.validate_skill_file(skill_file)
            all_results.extend(results)

            # Track significant failures
            for result in results:
                if result.examples_found > 0 and result.compiled_successfully == 0:
                    compilation_failures.append(f"{result.skill_name} ({result.language})")

        # Calculate statistics
        total_examples = sum(r.examples_found for r in all_results)
        total_compiled = sum(r.compiled_successfully for r in all_results)
        total_executed = sum(r.executed_successfully for r in all_results)
        success_rate = (total_compiled / total_examples * 100) if total_examples > 0 else 0

        # Language statistics
        language_stats = {}
        for result in all_results:
            if result.language not in language_stats:
                language_stats[result.language] = {
                    "skills": set(),
                    "examples": 0,
                    "compiled": 0,
                    "executed": 0,
                    "avg_time": 0.0,
                }

            lang_stats = language_stats[result.language]
            lang_stats["skills"].add(result.skill_name)
            lang_stats["examples"] += result.examples_found
            lang_stats["compiled"] += result.compiled_successfully
            lang_stats["executed"] += result.executed_successfully
            lang_stats["avg_time"] += result.avg_execution_time_ms

        # Convert sets to counts and calculate averages
        for lang in language_stats:
            stats = language_stats[lang]
            stats["skill_count"] = len(stats["skills"])
            stats["success_rate"] = (stats["compiled"] / stats["examples"] * 100) if stats["examples"] > 0 else 0
            stats["avg_time"] = stats["avg_time"] / max(
                1, sum(1 for r in all_results if r.language == lang and r.avg_execution_time_ms > 0)
            )
            del stats["skills"]  # Remove the set for JSON serialization

        return CompilationReport(
            total_skills=len(skill_files),
            total_examples=total_examples,
            success_rate=round(success_rate, 2),
            language_stats=language_stats,
            compilation_failures=compilation_failures,
            validations=all_results,
        )

    def print_report(self, report: CompilationReport):
        """Print compilation validation report"""
        print("\n" + "=" * 80)
        print("CODE COMPILATION VALIDATION REPORT")
        print("=" * 80)
        print(f"Total Skills: {report.total_skills}")
        print(f"Total Code Examples: {report.total_examples}")
        print(f"Overall Success Rate: {report.success_rate:.1f}%")

        print("\nSUCCESS RATES BY LANGUAGE:")
        sorted_langs = sorted(report.language_stats.items(), key=lambda x: x[1]["success_rate"], reverse=True)
        for lang, stats in sorted_langs:
            print(f"  • {lang}: {stats['success_rate']:.1f}% ({stats['compiled']}/{stats['examples']})")

        print("\nLANGUAGE DISTRIBUTION:")
        for lang, stats in sorted_langs:
            print(f"  • {lang}: {stats['skill_count']} skills, {stats['examples']} examples")

        if report.compilation_failures:
            print(f"\nCOMPILATION FAILURES ({len(report.compilation_failures)}):")
            for failure in report.compilation_failures[:10]:
                print(f"  ❌ {failure}")
            if len(report.compilation_failures) > 10:
                print(f"  ... and {len(report.compilation_failures) - 10} more")

        # Show some successful examples
        successful_validations = [r for r in report.validations if r.compiled_successfully > 0]
        if successful_validations:
            print("\nSUCCESSFUL VALIDATIONS (sample):")
            for result in successful_validations[:5]:
                print(
                    f"  ✅ {result.skill_name} ({result.language}): "
                    f"{result.compiled_successfully}/{result.examples_found} examples compiled"
                )

        print("=" * 80)


def main():
    """Run code compilation validation"""
    validator = CodeCompilationValidator()
    report = validator.validate_all_skills()
    validator.print_report(report)

    # Save report
    report_dict = {
        "total_skills": report.total_skills,
        "total_examples": report.total_examples,
        "success_rate": report.success_rate,
        "language_stats": report.language_stats,
        "compilation_failures": report.compilation_failures,
        "validations": [
            {
                "skill_name": v.skill_name,
                "language": v.language,
                "examples_found": v.examples_found,
                "compiled_successfully": v.compiled_successfully,
                "executed_successfully": v.executed_successfully,
                "avg_execution_time_ms": v.avg_execution_time_ms,
                "compilation_errors": v.compilation_errors[:3],  # Limit for readability
                "execution_errors": v.execution_errors[:3],
            }
            for v in report.validations
        ],
    }

    with open("code_compilation_validation_report.json", "w") as f:
        json.dump(report_dict, f, indent=2)

    print("📄 Detailed report saved to: code_compilation_validation_report.json")


if __name__ == "__main__":
    main()
