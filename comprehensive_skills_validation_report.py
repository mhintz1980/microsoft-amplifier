#!/usr/bin/env python3
"""
Comprehensive Skills Validation Report Generator

Synthesizes all validation results into a final comprehensive report
including system health assessment and critical issue identification.
"""

import json
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class SystemHealthScore:
    overall_score: float
    syntax_quality: float
    api_accuracy: float
    code_quality: float
    performance_score: float
    integration_readiness: float
    error_handling_coverage: float


@dataclass
class CriticalIssue:
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    description: str
    affected_skills: list[str]
    recommendation: str


@dataclass
class FinalValidationReport:
    validation_timestamp: str
    total_skills: int
    system_health: SystemHealthScore
    skill_categories: dict[str, int]
    validation_summary: dict[str, Any]
    critical_issues: list[CriticalIssue]
    top_performing_skills: list[dict]
    skills_requiring_improvement: list[dict]
    recommendations: list[str]
    system_stability_assessment: str


class ComprehensiveReportGenerator:
    """Generates final comprehensive validation report"""

    def __init__(self):
        self.load_validation_results()

    def load_validation_results(self):
        """Load all previous validation results"""
        self.lightweight_report = self._load_json("skills_validation_light_report.json")
        self.api_accuracy_report = self._load_json("api_accuracy_validation_report.json")
        self.compilation_report = self._load_json("code_compilation_validation_report.json")
        self.performance_report = self._load_json("integration_performance_validation_report.json")

    def _load_json(self, filename: str) -> dict:
        """Load JSON report file"""
        try:
            with open(filename) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filename} not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse {filename}: {e}")
            return {}

    def calculate_system_health(self) -> SystemHealthScore:
        """Calculate overall system health score"""
        # Syntax quality (from lightweight validation)
        syntax_valid = self.lightweight_report.get("syntax_valid", 0)
        total_skills = self.lightweight_report.get("total_skills", 1)
        syntax_quality = (syntax_valid / total_skills) * 100

        # API accuracy (from API validation)
        api_accuracy = self.api_accuracy_report.get("average_accuracy", 0)

        # Code quality (from compilation validation)
        compilation_success = self.compilation_report.get("success_rate", 0)

        # Performance score (from performance validation)
        performance_metrics = self.performance_report.get("performance_metrics", [])
        if performance_metrics:
            performance_score = sum(m.get("performance_score", 0) for m in performance_metrics) / len(
                performance_metrics
            )
        else:
            performance_score = 100

        # Integration readiness (from performance validation)
        if performance_metrics:
            integration_scores = [m.get("integration_score", 0) for m in performance_metrics]
            integration_readiness = sum(integration_scores) / len(integration_scores)
        else:
            integration_readiness = 0

        # Error handling coverage (from integration tests)
        integration_tests = self.performance_report.get("integration_tests", [])
        error_handling_tests = [t for t in integration_tests if t.get("integration_type") == "Error Handling"]
        if error_handling_tests:
            error_handling_passed = sum(1 for t in error_handling_tests if t.get("test_passed", False))
            error_handling_coverage = (error_handling_passed / len(error_handling_tests)) * 100
        else:
            error_handling_coverage = 0

        # Calculate overall score (weighted average)
        overall_score = (
            syntax_quality * 0.20
            + api_accuracy * 0.25
            + compilation_success * 0.25
            + performance_score * 0.15
            + integration_readiness * 0.10
            + error_handling_coverage * 0.05
        )

        return SystemHealthScore(
            overall_score=round(overall_score, 2),
            syntax_quality=round(syntax_quality, 2),
            api_accuracy=round(api_accuracy, 2),
            code_quality=round(compilation_success, 2),
            performance_score=round(performance_score, 2),
            integration_readiness=round(integration_readiness, 2),
            error_handling_coverage=round(error_handling_coverage, 2),
        )

    def identify_critical_issues(self) -> list[CriticalIssue]:
        """Identify critical issues requiring immediate attention"""
        issues = []

        # Performance critical issues
        performance_metrics = self.performance_report.get("performance_metrics", [])
        low_performance_skills = [m["skill_name"] for m in performance_metrics if m.get("performance_score", 100) < 70]

        if low_performance_skills:
            issues.append(
                CriticalIssue(
                    severity="HIGH",
                    category="Performance",
                    description=f"{len(low_performance_skills)} skills have low performance scores (<70%)",
                    affected_skills=low_performance_skills[:5],  # Limit display
                    recommendation="Optimize skill implementation and reduce computational overhead",
                )
            )

        # Integration critical issues
        critical_integration = self.performance_report.get("critical_issues", [])
        if critical_integration:
            issues.append(
                CriticalIssue(
                    severity="MEDIUM",
                    category="Integration",
                    description=f"{len(critical_integration)} skills have critical integration issues",
                    affected_skills=[issue.split(": ")[1].split(" ")[0] for issue in critical_integration[:3]],
                    recommendation="Improve integration patterns with Agent Lightning and MCP",
                )
            )

        # Compilation failures
        compilation_failures = self.compilation_report.get("compilation_failures", [])
        if compilation_failures:
            issues.append(
                CriticalIssue(
                    severity="HIGH",
                    category="Code Quality",
                    description=f"{len(compilation_failures)} skills have compilation failures",
                    affected_skills=compilation_failures[:5],
                    recommendation="Fix syntax errors and invalid code examples",
                )
            )

        # Low integration coverage
        agent_lightning_count = self.performance_report.get("agent_lightning_compatible", 0)
        mcp_count = self.performance_report.get("mcp_compatible", 0)
        total_skills = self.performance_report.get("total_skills", 1)

        if agent_lightning_count < total_skills * 0.5:
            issues.append(
                CriticalIssue(
                    severity="MEDIUM",
                    category="Integration",
                    description=f"Low Agent Lightning integration coverage ({agent_lightning_count}/{total_skills})",
                    affected_skills=[],
                    recommendation="Add Agent Lightning optimization to more skills",
                )
            )

        if mcp_count < total_skills * 0.3:
            issues.append(
                CriticalIssue(
                    severity="LOW",
                    category="Integration",
                    description=f"Low MCP integration coverage ({mcp_count}/{total_skills})",
                    affected_skills=[],
                    recommendation="Add Model Context Protocol integration where applicable",
                )
            )

        return issues

    def get_top_performing_skills(self) -> list[dict]:
        """Get top performing skills across all metrics"""
        performance_metrics = self.performance_report.get("performance_metrics", [])

        # Calculate combined score for each skill
        skill_scores = {}
        for metric in performance_metrics:
            skill_name = metric["skill_name"]
            perf_score = metric.get("performance_score", 0)
            integration_score = metric.get("integration_score", 0)

            # Combined score weighted towards performance
            combined_score = perf_score * 0.7 + integration_score * 0.3
            skill_scores[skill_name] = combined_score

        # Get top performers
        top_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)[:10]

        result = []
        for skill_name, score in top_skills:
            # Find the corresponding metric
            metric = next((m for m in performance_metrics if m["skill_name"] == skill_name), {})
            result.append(
                {
                    "skill_name": skill_name,
                    "combined_score": round(score, 2),
                    "performance_score": metric.get("performance_score", 0),
                    "integration_score": metric.get("integration_score", 0),
                    "has_agent_lightning": metric.get("has_agent_lightning", False),
                    "has_mcp_integration": metric.get("has_mcp_integration", False),
                }
            )

        return result

    def get_skills_requiring_improvement(self) -> list[dict]:
        """Get skills that require improvement"""
        performance_metrics = self.performance_report.get("performance_metrics", [])
        compilation_failures = self.compilation_report.get("compilation_failures", [])

        # Skills with low scores
        low_score_skills = [
            {
                "skill_name": m["skill_name"],
                "performance_score": m.get("performance_score", 0),
                "integration_score": m.get("integration_score", 0),
                "issue": "Low performance and/or integration scores",
            }
            for m in performance_metrics
            if m.get("performance_score", 100) < 80 or m.get("integration_score", 0) < 50
        ]

        # Skills with compilation failures
        compilation_skill_names = [failure.split(" ")[0] for failure in compilation_failures]
        compilation_issues = [
            {
                "skill_name": skill_name,
                "performance_score": 0,
                "integration_score": 0,
                "issue": "Code compilation failures",
            }
            for skill_name in compilation_skill_names
        ]

        # Combine and deduplicate
        all_issues = low_score_skills + compilation_issues
        unique_skills = {}
        for skill in all_issues:
            name = skill["skill_name"]
            if name not in unique_skills or skill["issue"] == "Code compilation failures":
                unique_skills[name] = skill

        return list(unique_skills.values())[:10]  # Limit to top 10

    def generate_recommendations(self, health: SystemHealthScore) -> list[str]:
        """Generate improvement recommendations"""
        recommendations = []

        if health.syntax_quality < 100:
            recommendations.append("Address syntax issues in skills that failed validation")

        if health.api_accuracy < 95:
            recommendations.append("Review and update outdated API patterns in skill examples")

        if health.code_quality < 90:
            recommendations.append("Fix compilation errors and ensure all code examples are valid")

        if health.performance_score < 90:
            recommendations.append("Optimize skill performance for faster execution")

        if health.integration_readiness < 70:
            recommendations.append("Improve integration capabilities with Agent Lightning and MCP")

        if health.error_handling_coverage < 95:
            recommendations.append("Add comprehensive error handling to all skills")

        # Specific recommendations based on validation results
        total_skills = self.performance_report.get("total_skills", 0)
        agent_lightning_count = self.performance_report.get("agent_lightning_compatible", 0)
        mcp_count = self.performance_report.get("mcp_compatible", 0)

        if agent_lightning_count < total_skills * 0.5:
            recommendations.append(
                f"Implement Agent Lightning optimization in {total_skills - agent_lightning_count} additional skills"
            )

        if mcp_count < total_skills * 0.3:
            recommendations.append(
                f"Add MCP integration to {total_skills - mcp_count} additional skills where applicable"
            )

        return recommendations

    def assess_system_stability(self, health: SystemHealthScore) -> str:
        """Assess overall system stability"""
        if health.overall_score >= 90:
            return "🟢 EXCELLENT - System is highly stable and production-ready"
        if health.overall_score >= 80:
            return "🟡 GOOD - System is stable with minor improvements recommended"
        if health.overall_score >= 70:
            return "🟠 NEEDS WORK - System has stability issues that should be addressed"
        return "🔴 CRITICAL - System has significant stability issues requiring immediate attention"

    def generate_final_report(self) -> FinalValidationReport:
        """Generate the final comprehensive validation report"""
        print("🔄 Generating comprehensive validation report...")

        # Calculate metrics
        health = self.calculate_system_health()
        critical_issues = self.identify_critical_issues()
        top_performers = self.get_top_performing_skills()
        improvement_needed = self.get_skills_requiring_improvement()
        recommendations = self.generate_recommendations(health)
        stability = self.assess_system_stability(health)

        # Get skill categories
        categories = self.lightweight_report.get("categories", {})

        # Validation summary
        validation_summary = {
            "syntax_validation": {
                "total": self.lightweight_report.get("total_skills", 0),
                "valid": self.lightweight_report.get("syntax_valid", 0),
                "success_rate": health.syntax_quality,
            },
            "api_accuracy": {
                "total": self.api_accuracy_report.get("total_validations", 0),
                "average_score": health.api_accuracy,
            },
            "code_compilation": {
                "total_examples": self.compilation_report.get("total_examples", 0),
                "success_rate": health.code_quality,
            },
            "performance": {
                "average_load_time_ms": self.performance_report.get("avg_load_time_ms", 0),
                "average_score": health.performance_score,
            },
            "integration": {
                "agent_lightning_compatible": self.performance_report.get("agent_lightning_compatible", 0),
                "mcp_compatible": self.performance_report.get("mcp_compatible", 0),
                "error_handling_coverage": health.error_handling_coverage,
            },
        }

        return FinalValidationReport(
            validation_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_skills=self.lightweight_report.get("total_skills", 0),
            system_health=health,
            skill_categories=categories,
            validation_summary=validation_summary,
            critical_issues=critical_issues,
            top_performing_skills=top_performers,
            skills_requiring_improvement=improvement_needed,
            recommendations=recommendations,
            system_stability_assessment=stability,
        )

    def print_final_report(self, report: FinalValidationReport):
        """Print the final comprehensive validation report"""
        print("\n" + "=" * 100)
        print("🏁 COMPREHENSIVE MICROSOFT AMPLIFIER SKILLS VALIDATION REPORT")
        print("=" * 100)
        print(f"Validation Timestamp: {report.validation_timestamp}")
        print(f"Total Skills Analyzed: {report.total_skills}")
        print(f"System Stability: {report.system_stability_assessment}")

        print(f"\n📊 SYSTEM HEALTH SCORE: {report.system_health.overall_score:.1f}/100")
        print("├─ Syntax Quality:        ", f"{report.system_health.syntax_quality:.1f}%")
        print("├─ API Accuracy:         ", f"{report.system_health.api_accuracy:.1f}%")
        print("├─ Code Quality:         ", f"{report.system_health.code_quality:.1f}%")
        print("├─ Performance:          ", f"{report.system_health.performance_score:.1f}%")
        print("├─ Integration Readiness:", f"{report.system_health.integration_readiness:.1f}%")
        print("└─ Error Handling:       ", f"{report.system_health.error_handling_coverage:.1f}%")

        print(f"\n📂 SKILL CATEGORIES ({len(report.skill_categories)} categories):")
        sorted_categories = sorted(report.skill_categories.items(), key=lambda x: x[1], reverse=True)
        for category, count in sorted_categories:
            if count > 0:
                print(f"  • {category:20} : {count:3d} skills")

        print("\n📈 VALIDATION SUMMARY:")
        summary = report.validation_summary
        print(
            f"  • Syntax Validation:    {summary['syntax_validation']['valid']}/{summary['syntax_validation']['total']} "
            f"({summary['syntax_validation']['success_rate']:.1f}%)"
        )
        print(f"  • API Accuracy:         {summary['api_accuracy']['average_score']:.1f}% average score")
        print(f"  • Code Compilation:     {summary['code_compilation']['success_rate']:.1f}% success rate")
        print(
            f"  • Performance:          {summary['performance']['average_score']:.1f}% average score "
            f"({summary['performance']['average_load_time_ms']:.2f}ms avg load)"
        )
        print("  • Integration:")
        print(
            f"    - Agent Lightning:    {summary['integration']['agent_lightning_compatible']}/{report.total_skills} skills"
        )
        print(f"    - MCP:                {summary['integration']['mcp_compatible']}/{report.total_skills} skills")
        print(f"    - Error Handling:     {summary['integration']['error_handling_coverage']:.1f}% coverage")

        if report.critical_issues:
            print(f"\n⚠️  CRITICAL ISSUES ({len(report.critical_issues)}):")
            for i, issue in enumerate(report.critical_issues, 1):
                severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}[issue.severity]
                print(f"  {i}. {severity_icon} {issue.severity}: {issue.description}")
                print(f"     Recommendation: {issue.recommendation}")
                if issue.affected_skills:
                    print(f"     Affected: {', '.join(issue.affected_skills[:3])}")
                    if len(issue.affected_skills) > 3:
                        print(f"                  and {len(issue.affected_skills) - 3} more...")

        if report.top_performing_skills:
            print(f"\n🏆 TOP PERFORMING SKILLS ({len(report.top_performing_skills)}):")
            for i, skill in enumerate(report.top_performing_skills[:5], 1):
                print(f"  {i}. {skill['skill_name']}")
                print(
                    f"     Combined Score: {skill['combined_score']:.1f} | "
                    f"Performance: {skill['performance_score']:.1f} | "
                    f"Integration: {skill['integration_score']:.1f}"
                )

        if report.skills_requiring_improvement:
            print(f"\n🔧 SKILLS REQUIRING IMPROVEMENT ({len(report.skills_requiring_improvement)}):")
            for i, skill in enumerate(report.skills_requiring_improvement[:5], 1):
                print(f"  {i}. {skill['skill_name']}: {skill['issue']}")
                print(
                    f"     Performance: {skill['performance_score']:.1f} | "
                    f"Integration: {skill['integration_score']:.1f}"
                )

        if report.recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")

        # Final assessment
        print("\n🎯 FINAL ASSESSMENT:")
        if report.system_health.overall_score >= 90:
            print("  ✅ The Microsoft Amplifier skills system is EXCELLENT and production-ready.")
            print("     All critical validation criteria have been met with high scores.")
        elif report.system_health.overall_score >= 80:
            print("  ✅ The Microsoft Amplifier skills system is GOOD and stable.")
            print("     Minor improvements are recommended for optimal performance.")
        elif report.system_health.overall_score >= 70:
            print("  ⚠️  The Microsoft Amplifier skills system NEEDS IMPROVEMENT.")
            print("     Several issues should be addressed before production deployment.")
        else:
            print("  ❌ The Microsoft Amplifier skills system has CRITICAL ISSUES.")
            print("     Immediate attention is required before production use.")

        print("=" * 100)


def main():
    """Generate final comprehensive validation report"""
    generator = ComprehensiveReportGenerator()
    report = generator.generate_final_report()
    generator.print_final_report(report)

    # Save final report
    with open("comprehensive_skills_validation_final_report.json", "w") as f:
        json.dump(asdict(report), f, indent=2, default=str)

    print("\n📄 Final comprehensive report saved to: comprehensive_skills_validation_final_report.json")


if __name__ == "__main__":
    main()
