#!/usr/bin/env python3
"""
Skills Validation Test - Critical Priority #1

Tests individual skills to identify and fix import and functionality issues.
Tests skills one at a time to isolate problems and provide clear validation results.
"""

import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class SkillTestResult:
    """Result of testing a single skill"""

    skill_name: str
    import_success: bool
    import_error: str = ""
    functionality_test: bool = False
    functionality_error: str = ""
    execution_time: float = 0.0
    capabilities: list[str] = None
    success: bool = False


class SkillsValidator:
    """Critical skills validation system"""

    def __init__(self):
        self.test_results: list[SkillTestResult] = []
        self.project_root = Path(__file__).parent.parent
        self.skills_dir = self.project_root / "amplifier" / "skills"

    def validate_skills(self, skill_patterns: list[str] = None) -> dict[str, Any]:
        """
        Validate skills with priority on core functionality

        Args:
            skill_patterns: List of skill file patterns to test

        Returns:
            Comprehensive validation report
        """
        print("🚀 Starting Critical Skills Validation...")
        print("=" * 60)

        # Start with database design expert (already partially fixed)
        self.test_single_skill("database_design_expert", "core_technology")

        # Test other critical skills one by one
        critical_skills = [
            ("typescript_expert", "core_technology"),
            ("nodejs_expert", "core_technology"),
            ("performance_testing_expert", "core_technology"),
            ("code_quality_expert", "core_technology"),
        ]

        for skill_name, category in critical_skills:
            self.test_single_skill(skill_name, category)

        # Generate summary report
        return self.generate_validation_report()

    def test_single_skill(self, skill_name: str, category: str) -> SkillTestResult:
        """Test a single skill comprehensively"""

        result = SkillTestResult(skill_name=skill_name, import_success=False, functionality_test=False, capabilities=[])

        print(f"\n🧪 Testing Skill: {skill_name}")
        print("-" * 40)

        try:
            # Test 1: Import skill
            start_time = time.time()

            skill_module_path = f"amplifier.skills.{category}.{skill_name}"
            skill_class_path = f"amplifier.skills.{category}.{skill_name}.{skill_name.title()}ExpertSkill"

            # Try to import the function first
            try:
                skill_module = __import__(skill_module_path, fromlist=[skill_name])
                skill_function = getattr(skill_module, skill_name)
                result.import_success = True
                print(f"✅ Function import successful: {skill_name}")
            except AttributeError as e:
                # Try function with different naming
                try:
                    skill_function = getattr(skill_module, f"{skill_name}_expert")
                    result.import_success = True
                    print(f"✅ Function import successful: {skill_name}_expert")
                except AttributeError:
                    result.import_error = f"Function not found: {e}"
                    print(f"❌ Function import failed: {result.import_error}")
                    return result

            # Test 2: Basic functionality
            if result.import_success:
                try:
                    test_input = f"Test {skill_name} functionality"
                    function_result = skill_function(test_input)
                    result.functionality_test = True
                    print("✅ Functionality test successful")
                    print(f"📊 Result type: {type(function_result)}")
                except Exception as e:
                    result.functionality_error = str(e)
                    print(f"❌ Functionality test failed: {result.functionality_error}")

            # Test 3: Skill class (if exists)
            try:
                skill_class_module = __import__(f"{skill_class_path}", fromlist=[""])
                skill_class = getattr(skill_class_module, f"{skill_name.title()}ExpertSkill")

                # Test instantiation
                skill_instance = skill_class()
                print(f"✅ Skill class instantiated: {skill_name.title()}ExpertSkill")

                # Test capabilities
                if hasattr(skill_instance, "get_capabilities"):
                    capabilities = skill_instance.get_capabilities()
                    result.capabilities = capabilities
                    print(f"🎯 Capabilities: {len(capabilities)} available")

                # Test async execution
                if hasattr(skill_instance, "execute"):
                    try:
                        import asyncio

                        async_result = asyncio.run(skill_instance.execute(test_input))
                        print("✅ Async execution successful")
                        print(f"📊 Success: {async_result.success}")
                    except Exception as e:
                        print(f"⚠️  Async execution failed: {e}")

            except ImportError as e:
                print(f"⚠️  Skill class not available: {e}")
            except Exception as e:
                print(f"⚠️  Skill class error: {e}")

            result.execution_time = time.time() - start_time
            result.success = result.import_success and result.functionality_test

        except Exception as e:
            result.import_error = str(e)
            print(f"❌ Critical error: {result.import_error}")

        # Store result
        self.test_results.append(result)

        # Print summary for this skill
        status = "✅ PASS" if result.success else "❌ FAIL"
        print(f"🏁 {skill_name}: {status} ({result.execution_time:.2f}s)")

        return result

    def generate_validation_report(self) -> dict[str, Any]:
        """Generate comprehensive validation report"""

        total_skills = len(self.test_results)
        successful_skills = sum(1 for r in self.test_results if r.success)
        failed_skills = total_skills - successful_skills

        report = {
            "summary": {
                "total_skills_tested": total_skills,
                "successful_skills": successful_skills,
                "failed_skills": failed_skills,
                "success_rate": f"{(successful_skills / total_skills * 100):.1f}%" if total_skills > 0 else "0%",
                "overall_status": "PASS" if failed_skills == 0 else "FAIL",
            },
            "detailed_results": [],
            "critical_issues": [],
            "recommendations": [],
        }

        for result in self.test_results:
            skill_report = {
                "skill_name": result.skill_name,
                "success": result.success,
                "import_success": result.import_success,
                "functionality_test": result.functionality_test,
                "execution_time": result.execution_time,
                "capabilities": len(result.capabilities) if result.capabilities else 0,
                "errors": [],
            }

            if result.import_error:
                skill_report["errors"].append(f"Import: {result.import_error}")
                report["critical_issues"].append(f"{result.skill_name}: {result.import_error}")

            if result.functionality_error:
                skill_report["errors"].append(f"Functionality: {result.functionality_error}")
                report["critical_issues"].append(f"{result.skill_name}: {result.functionality_error}")

            report["detailed_results"].append(skill_report)

        # Generate recommendations
        if failed_skills > 0:
            report["recommendations"].append("Fix import issues before proceeding with new features")
            report["recommendations"].append("Ensure all core skills pass basic functionality tests")

        if successful_skills == total_skills:
            report["recommendations"].append("Core skills are stable - proceed with remaining validation")

        return report

    def print_summary(self, report: dict[str, Any]):
        """Print validation summary"""

        print("\n" + "=" * 60)
        print("📊 SKILLS VALIDATION SUMMARY")
        print("=" * 60)

        summary = report["summary"]
        print(f"Total Skills Tested: {summary['total_skills_tested']}")
        print(f"Successful: {summary['successful_skills']}")
        print(f"Failed: {summary['failed_skills']}")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Overall Status: {summary['overall_status']}")

        if report["critical_issues"]:
            print(f"\n⚠️  Critical Issues ({len(report['critical_issues'])}):")
            for issue in report["critical_issues"]:
                print(f"   • {issue}")

        if report["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")

        print("\n" + "=" * 60)

        return report["summary"]["overall_status"] == "PASS"


def main():
    """Main validation execution"""
    validator = SkillsValidator()

    try:
        report = validator.validate_skills()
        success = validator.print_summary(report)

        if success:
            print("\n🎉 CRITICAL SKILLS VALIDATION PASSED!")
            print("Core skills are ready for production use.")
            return 0
        print("\n❌ CRITICAL SKILLS VALIDATION FAILED!")
        print("Fix critical issues before proceeding.")
        return 1

    except Exception as e:
        print(f"❌ Validation system error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
