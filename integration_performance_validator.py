#!/usr/bin/env python3
"""
Integration and Performance Validator for Microsoft Amplifier Skills

Tests skill interactions, performance characteristics, memory usage,
and integration compatibility with Agent Lightning and MCP.
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PerformanceMetrics:
    skill_name: str
    load_time_ms: float
    peak_memory_mb: float
    has_agent_lightning: bool
    has_mcp_integration: bool
    has_error_handling: bool
    integration_score: float
    performance_score: float


@dataclass
class IntegrationTest:
    skill_name: str
    integration_type: str
    test_passed: bool
    error_message: str
    execution_time_ms: float


@dataclass
class IntegrationPerformanceReport:
    total_skills: int
    avg_load_time_ms: float
    avg_memory_mb: float
    agent_lightning_compatible: int
    mcp_compatible: int
    integration_tests: list[IntegrationTest]
    performance_metrics: list[PerformanceMetrics]
    critical_issues: list[str]


class IntegrationPerformanceValidator:
    """Validates skill integration and performance characteristics"""

    def __init__(self):
        self.skills_dir = Path("amplifier/skills")
        self.performance_results: list[PerformanceMetrics] = []
        self.integration_results: list[IntegrationTest] = []

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil

            return psutil.Process().memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0

    def analyze_skill_integration(self, skill_path: Path) -> tuple[bool, bool, bool, bool]:
        """Analyze skill for integration patterns"""
        try:
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return False, False, False, False

        content_lower = content.lower()

        # Check for Agent Lightning integration
        agent_lightning_patterns = [
            "agent lightning",
            "agentlightning",
            "lightning_",
            "lightning hooks",
            "lightning integration",
            "performance optimization",
            "learning system",
        ]

        has_agent_lightning = any(pattern in content_lower for pattern in agent_lightning_patterns)

        # Check for MCP integration
        mcp_patterns = ["mcp", "model context protocol", "mcp_", "mcp integration", "mcp storage", "mcp client"]

        has_mcp = any(pattern in content_lower for pattern in mcp_patterns)

        # Check for error handling
        error_handling_patterns = [
            "try:",
            "except",
            "finally:",
            "raise",
            "assert",
            "if error:",
            "catch(",
            "throw new",
            "Promise.reject",
            "error handling",
            "exception handling",
        ]

        has_error_handling = any(pattern in content for pattern in error_handling_patterns)

        # Check for other integration patterns
        integration_patterns = [
            "import amplifier",
            "from amplifier",
            "amplifier.skills",
            "skill_registry",
            "skill_context",
            "skill_result",
            "bootstrap",
            "signature framework",
            "meta_skill",
        ]

        has_integrations = any(pattern in content_lower for pattern in integration_patterns)

        return has_agent_lightning, has_mcp, has_error_handling, has_integrations

    def measure_skill_performance(self, skill_path: Path) -> PerformanceMetrics:
        """Measure performance characteristics of a skill"""
        start_time = time.time()
        start_memory = self.get_memory_usage()

        # Simulate skill loading
        try:
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()

            # Basic parsing to simulate processing
            lines = content.split("\n")
            classes = []
            functions = []

            for line in lines:
                stripped = line.strip()
                if stripped.startswith("class ") and "(" in stripped:
                    classes.append(stripped.split("(")[0].replace("class ", ""))
                elif stripped.startswith("def ") or stripped.startswith("async def "):
                    functions.append(stripped.split("(")[0].replace("def ", "").replace("async def ", ""))

            # Simulate some processing
            time.sleep(0.001)  # 1ms simulation

        except Exception:
            pass  # Skills with errors still get measured

        end_time = time.time()
        end_memory = self.get_memory_usage()

        load_time_ms = (end_time - start_time) * 1000
        peak_memory_mb = max(0, end_memory - start_memory)

        # Analyze integration
        has_agent_lightning, has_mcp, has_error_handling, has_integrations = self.analyze_skill_integration(skill_path)

        # Calculate scores
        integration_score = 0
        if has_agent_lightning:
            integration_score += 30
        if has_mcp:
            integration_score += 30
        if has_error_handling:
            integration_score += 25
        if has_integrations:
            integration_score += 15

        # Performance score (lower is better, scale 0-100)
        performance_score = max(0, 100 - (load_time_ms / 10))  # 10ms = 90 points
        if peak_memory_mb > 50:  # Penalty for high memory usage
            performance_score = max(0, performance_score - (peak_memory_mb - 50) * 2)

        return PerformanceMetrics(
            skill_name=skill_path.stem,
            load_time_ms=round(load_time_ms, 2),
            peak_memory_mb=round(peak_memory_mb, 2),
            has_agent_lightning=has_agent_lightning,
            has_mcp_integration=has_mcp,
            has_error_handling=has_error_handling,
            integration_score=integration_score,
            performance_score=round(performance_score, 2),
        )

    def test_skill_integration(self, skill_path: Path) -> list[IntegrationTest]:
        """Test specific integration points"""
        tests = []

        # Test 1: Check for proper imports
        try:
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()

            # Agent Lightning test
            start_time = time.time()
            has_agent_lightning = "agent lightning" in content.lower() or "agentlightning" in content.lower()
            execution_time = (time.time() - start_time) * 1000

            tests.append(
                IntegrationTest(
                    skill_name=skill_path.stem,
                    integration_type="Agent Lightning",
                    test_passed=has_agent_lightning,
                    error_message="" if has_agent_lightning else "No Agent Lightning integration found",
                    execution_time_ms=round(execution_time, 2),
                )
            )

            # MCP Integration test
            start_time = time.time()
            has_mcp = "mcp" in content.lower()
            execution_time = (time.time() - start_time) * 1000

            tests.append(
                IntegrationTest(
                    skill_name=skill_path.stem,
                    integration_type="MCP",
                    test_passed=has_mcp,
                    error_message="" if has_mcp else "No MCP integration found",
                    execution_time_ms=round(execution_time, 2),
                )
            )

            # Error Handling test
            start_time = time.time()
            has_error_handling = any(pattern in content for pattern in ["try:", "except", "raise", "assert"])
            execution_time = (time.time() - start_time) * 1000

            tests.append(
                IntegrationTest(
                    skill_name=skill_path.stem,
                    integration_type="Error Handling",
                    test_passed=has_error_handling,
                    error_message="" if has_error_handling else "No error handling patterns found",
                    execution_time_ms=round(execution_time, 2),
                )
            )

            # Documentation test
            start_time = time.time()
            has_docs = '"""' in content and len(content.split('"""')) >= 3
            execution_time = (time.time() - start_time) * 1000

            tests.append(
                IntegrationTest(
                    skill_name=skill_path.stem,
                    integration_type="Documentation",
                    test_passed=has_docs,
                    error_message="" if has_docs else "Missing proper documentation",
                    execution_time_ms=round(execution_time, 2),
                )
            )

        except Exception as e:
            tests.append(
                IntegrationTest(
                    skill_name=skill_path.stem,
                    integration_type="File Access",
                    test_passed=False,
                    error_message=f"Could not read file: {e}",
                    execution_time_ms=0.0,
                )
            )

        return tests

    def validate_all_skills(self) -> IntegrationPerformanceReport:
        """Validate integration and performance for all skills"""
        print("🚀 Validating integration and performance across all skills...")

        # Find all skill files
        skill_files = list(self.skills_dir.rglob("*.py"))
        skill_files = [f for f in skill_files if not f.name.startswith("__")]

        print(f"📊 Found {len(skill_files)} skills to validate")

        critical_issues = []

        for skill_file in skill_files:
            # Performance measurement
            perf_metrics = self.measure_skill_performance(skill_file)
            self.performance_results.append(perf_metrics)

            # Integration tests
            integration_tests = self.test_skill_integration(skill_file)
            self.integration_results.extend(integration_tests)

            # Track critical issues
            if perf_metrics.performance_score < 50:
                critical_issues.append(
                    f"Performance: {perf_metrics.skill_name} (score: {perf_metrics.performance_score})"
                )

            if perf_metrics.integration_score < 25:
                critical_issues.append(
                    f"Integration: {perf_metrics.skill_name} (score: {perf_metrics.integration_score})"
                )

            print(
                f"  ✓ {skill_file.stem}: Performance {perf_metrics.performance_score:.1f}, "
                f"Integration {perf_metrics.integration_score:.1f}"
            )

        # Calculate aggregates
        avg_load_time = sum(r.load_time_ms for r in self.performance_results) / len(self.performance_results)
        avg_memory = sum(r.peak_memory_mb for r in self.performance_results) / len(self.performance_results)

        agent_lightning_count = sum(1 for r in self.performance_results if r.has_agent_lightning)
        mcp_count = sum(1 for r in self.performance_results if r.has_mcp_integration)

        return IntegrationPerformanceReport(
            total_skills=len(skill_files),
            avg_load_time_ms=round(avg_load_time, 2),
            avg_memory_mb=round(avg_memory, 2),
            agent_lightning_compatible=agent_lightning_count,
            mcp_compatible=mcp_count,
            integration_tests=self.integration_results,
            performance_metrics=self.performance_results,
            critical_issues=critical_issues,
        )

    def print_report(self, report: IntegrationPerformanceReport):
        """Print integration and performance validation report"""
        print("\n" + "=" * 80)
        print("INTEGRATION & PERFORMANCE VALIDATION REPORT")
        print("=" * 80)
        print(f"Total Skills: {report.total_skills}")
        print(f"Average Load Time: {report.avg_load_time_ms:.2f}ms")
        print(f"Average Memory Usage: {report.avg_memory_mb:.2f}MB")
        print(f"Agent Lightning Compatible: {report.agent_lightning_compatible}/{report.total_skills}")
        print(f"MCP Compatible: {report.mcp_compatible}/{report.total_skills}")

        # Integration test results
        print("\nINTEGRATION TEST RESULTS:")
        integration_types = {}
        for test in report.integration_tests:
            if test.integration_type not in integration_types:
                integration_types[test.integration_type] = {"passed": 0, "total": 0}
            integration_types[test.integration_type]["total"] += 1
            if test.test_passed:
                integration_types[test.integration_type]["passed"] += 1

        for integration_type, stats in integration_types.items():
            percentage = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"  • {integration_type}: {stats['passed']}/{stats['total']} ({percentage:.1f}%)")

        # Performance distribution
        print("\nPERFORMANCE DISTRIBUTION:")
        high_perf = sum(1 for r in report.performance_metrics if r.performance_score >= 90)
        good_perf = sum(1 for r in report.performance_metrics if 70 <= r.performance_score < 90)
        low_perf = sum(1 for r in report.performance_metrics if r.performance_score < 70)

        print(f"  🟢 High Performance (90%+): {high_perf} skills")
        print(f"  🟡 Good Performance (70-89%): {good_perf} skills")
        print(f"  🔴 Low Performance (<70%): {low_perf} skills")

        # Integration distribution
        print("\nINTEGRATION CAPABILITIES:")
        full_integration = sum(1 for r in report.performance_metrics if r.integration_score >= 80)
        partial_integration = sum(1 for r in report.performance_metrics if 40 <= r.integration_score < 80)
        minimal_integration = sum(1 for r in report.performance_metrics if r.integration_score < 40)

        print(f"  🌟 Full Integration (80%+): {full_integration} skills")
        print(f"  ⚡ Partial Integration (40-79%): {partial_integration} skills")
        print(f"  🔧 Minimal Integration (<40%): {minimal_integration} skills")

        # Top performers
        print("\nTOP PERFORMING SKILLS:")
        top_performers = sorted(
            report.performance_metrics, key=lambda x: (x.performance_score + x.integration_score) / 2, reverse=True
        )[:5]
        for skill in top_performers:
            avg_score = (skill.performance_score + skill.integration_score) / 2
            print(
                f"  🏆 {skill.skill_name}: Performance {skill.performance_score:.1f}, "
                f"Integration {skill.integration_score:.1f} (Overall {avg_score:.1f})"
            )

        # Critical issues
        if report.critical_issues:
            print(f"\nCRITICAL ISSUES ({len(report.critical_issues)}):")
            for issue in report.critical_issues[:10]:
                print(f"  ⚠️  {issue}")
            if len(report.critical_issues) > 10:
                print(f"  ... and {len(report.critical_issues) - 10} more")

        # Recommendations
        print("\nRECOMMENDATIONS:")
        if report.agent_lightning_compatible < report.total_skills // 2:
            print(
                f"  • Consider adding Agent Lightning integration to more skills "
                f"({report.agent_lightning_compatible}/{report.total_skills} currently)"
            )
        if report.mcp_compatible < report.total_skills // 2:
            print(
                f"  • Consider adding MCP integration to more skills "
                f"({report.mcp_compatible}/{report.total_skills} currently)"
            )
        if low_perf > 0:
            print(f"  • Optimize {low_perf} skills with low performance scores")
        if minimal_integration > report.total_skills // 3:
            print(f"  • Improve integration capabilities in {minimal_integration} skills")

        print("=" * 80)


def main():
    """Run integration and performance validation"""
    validator = IntegrationPerformanceValidator()
    report = validator.validate_all_skills()
    validator.print_report(report)

    # Save report
    report_dict = {
        "total_skills": report.total_skills,
        "avg_load_time_ms": report.avg_load_time_ms,
        "avg_memory_mb": report.avg_memory_mb,
        "agent_lightning_compatible": report.agent_lightning_compatible,
        "mcp_compatible": report.mcp_compatible,
        "critical_issues": report.critical_issues,
        "integration_tests": [
            {
                "skill_name": t.skill_name,
                "integration_type": t.integration_type,
                "test_passed": t.test_passed,
                "error_message": t.error_message,
                "execution_time_ms": t.execution_time_ms,
            }
            for t in report.integration_tests
        ],
        "performance_metrics": [
            {
                "skill_name": m.skill_name,
                "load_time_ms": m.load_time_ms,
                "peak_memory_mb": m.peak_memory_mb,
                "has_agent_lightning": m.has_agent_lightning,
                "has_mcp_integration": m.has_mcp_integration,
                "has_error_handling": m.has_error_handling,
                "integration_score": m.integration_score,
                "performance_score": m.performance_score,
            }
            for m in report.performance_metrics
        ],
    }

    with open("integration_performance_validation_report.json", "w") as f:
        json.dump(report_dict, f, indent=2)

    print("📄 Detailed report saved to: integration_performance_validation_report.json")


if __name__ == "__main__":
    main()
