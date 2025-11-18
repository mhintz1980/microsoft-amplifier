"""
Quality Assurance Framework Main Entry Point

Comprehensive zero-hallucination quality assurance system for all 57 skills.
This module provides the main interface for running QA validation, testing,
performance monitoring, security scanning, and compliance checking.
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import QA components
from .validators.zero_hallucination_validator import ZeroHallucinationValidator
from .testing.automated_test_generator import AutomatedTestGenerator
from .performance.performance_monitor import PerformanceMonitor
from .security.security_scanner import SecurityScanner
from .compliance.compliance_validator import ComplianceValidator
from .learning.continuous_improvement import ContinuousImprovement
from .storage.quality_metrics_storage import QualityMetricsStorage


class QualityAssuranceFramework:
    """Main QA framework orchestrator."""

    def __init__(
        self,
        accuracy_threshold: float = 0.95,
        enable_learning: bool = True,
        auto_fix: bool = False,
        output_dir: str = "qa_reports",
    ):
        """
        Initialize QA framework.

        Args:
            accuracy_threshold: Minimum accuracy threshold for validation
            enable_learning: Enable continuous learning and improvement
            auto_fix: Enable automatic fixing of violations
            output_dir: Directory for QA reports
        """
        self.accuracy_threshold = accuracy_threshold
        self.enable_learning = enable_learning
        self.auto_fix = auto_fix
        self.output_dir = Path(output_dir)

        # Initialize QA components
        self.validator = ZeroHallucinationValidator(accuracy_threshold=accuracy_threshold, strict_mode=True)
        self.test_generator = AutomatedTestGenerator(coverage_threshold=0.80)
        self.performance_monitor = PerformanceMonitor(auto_optimize=True)
        self.security_scanner = SecurityScanner(enable_dependency_scanning=True)
        self.compliance_validator = ComplianceValidator(auto_fix=auto_fix)
        self.learning_system = ContinuousImprovement(auto_apply_improvements=enable_learning)
        self.storage = QualityMetricsStorage()

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

    async def run_full_qa(self, skill_path: str) -> Dict[str, Any]:
        """
        Run complete QA pipeline on a skill.

        Args:
            skill_path: Path to the skill

        Returns:
            Complete QA results
        """
        print(f"🔍 Running comprehensive QA on: {skill_path}")

        results = {
            "skill_path": skill_path,
            "timestamp": datetime.now().isoformat(),
            "validation_results": {},
            "test_results": {},
            "performance_results": {},
            "security_results": {},
            "compliance_results": {},
            "learning_insights": {},
            "overall_quality_score": 0.0,
            "recommendations": [],
            "status": "completed",
        }

        try:
            # 1. Zero Hallucination Validation
            print("📋 Running zero-hallucination validation...")
            validation_report = await self.validator.validate_and_store(skill_path)
            results["validation_results"] = {
                "passed": validation_report.overall_passed,
                "confidence": validation_report.overall_confidence,
                "critical_issues": validation_report.critical_issues,
                "layer_results": {
                    layer.value: {
                        "passed": result.passed,
                        "confidence": result.confidence,
                        "issues_count": len(result.issues),
                    }
                    for layer, result in validation_report.layer_results.items()
                },
            }

            # 2. Automated Testing
            print("🧪 Running automated testing...")
            test_suite = self.test_generator.generate_test_suite(skill_path)
            test_suite = await self.test_generator.execute_test_suite(test_suite)
            results["test_results"] = {
                "total_tests": len(test_suite.test_cases),
                "passed": test_suite.passed_count,
                "failed": test_suite.failed_count,
                "coverage": test_suite.coverage_percentage,
                "execution_time": test_suite.total_time,
            }

            # 3. Performance Monitoring
            print("⚡ Running performance analysis...")
            performance_report = self.performance_monitor.generate_performance_report(Path(skill_path).name)
            results["performance_results"] = {
                "overall_tier": performance_report.overall_tier.value,
                "optimization_score": performance_report.optimization_score,
                "bottlenecks": performance_report.bottlenecks,
                "recommendations": performance_report.recommendations,
            }

            # 4. Security Scanning
            print("🔒 Running security scan...")
            security_report = await self.security_scanner.scan_skill(skill_path)
            results["security_results"] = {
                "vulnerabilities_found": len(security_report.vulnerabilities),
                "risk_score": security_report.risk_score,
                "severity_counts": {k.value: v for k, v in security_report.severity_counts.items()},
                "compliance_status": security_report.compliance_status,
                "critical_vulnerabilities": [
                    v.title for v in security_report.vulnerabilities if v.severity.value == "critical"
                ],
            }

            # 5. Compliance Validation
            print("✅ Running compliance validation...")
            compliance_report = await self.compliance_validator.validate_skill(skill_path)
            results["compliance_results"] = {
                "overall_compliance": compliance_report.overall_compliance.value,
                "compliance_score": compliance_report.compliance_score,
                "violations_count": len(compliance_report.violations),
                "auto_fix_available": compliance_report.auto_fix_available,
                "standard_results": {
                    k.value: {
                        "compliance_level": v["compliance_level"].value,
                        "score": v["compliance_score"],
                        "failed_rules": v["failed_rules"],
                    }
                    for k, v in compliance_report.standard_results.items()
                },
            }

            # 6. Calculate overall quality score
            results["overall_quality_score"] = self._calculate_overall_score(results)

            # 7. Generate recommendations
            results["recommendations"] = self._generate_overall_recommendations(results)

            # 8. Store results in persistent storage
            await self._store_qa_results(results)

            # 9. Run learning cycle if enabled
            if self.enable_learning:
                print("🧠 Running continuous learning...")
                learning_report = await self.learning_system.start_learning_cycle()
                results["learning_insights"] = {
                    "insights_count": len(learning_report.insights),
                    "improvement_actions": len(learning_report.improvement_actions),
                    "key_findings": learning_report.key_findings,
                    "recommendations": learning_report.recommendations[:3],  # Top 3
                }

            print(f"✅ QA completed for {skill_path}")
            print(f"📊 Overall Quality Score: {results['overall_quality_score']:.2f}")

        except Exception as e:
            print(f"❌ QA failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)

        # Save detailed report
        await self._save_qa_report(results)

        return results

    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall quality score from all components."""
        scores = []

        # Validation score (40% weight)
        validation_confidence = results["validation_results"].get("confidence", 0.0)
        if validation_confidence >= self.accuracy_threshold:
            scores.append(validation_confidence * 0.4)

        # Test score (20% weight)
        test_coverage = results["test_results"].get("coverage", 0.0)
        if test_coverage >= 0.8:
            scores.append(test_coverage * 0.2)

        # Performance score (15% weight)
        perf_score = results["performance_results"].get("optimization_score", 0.0)
        scores.append(perf_score * 0.15)

        # Security score (15% weight)
        risk_score = results["security_results"].get("risk_score", 10.0)
        security_score = max(0, (10 - risk_score) / 10)  # Convert risk to security score
        scores.append(security_score * 0.15)

        # Compliance score (10% weight)
        compliance_score = results["compliance_results"].get("compliance_score", 0.0)
        scores.append(compliance_score * 0.1)

        return sum(scores) if scores else 0.0

    def _generate_overall_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate overall recommendations based on QA results."""
        recommendations = []

        # Validation recommendations
        validation_confidence = results["validation_results"].get("confidence", 0.0)
        if validation_confidence < self.accuracy_threshold:
            recommendations.append("Address zero-hallucination validation failures")
            critical_issues = results["validation_results"].get("critical_issues", [])
            if critical_issues:
                recommendations.append(f"Fix critical issues: {', '.join(critical_issues[:2])}")

        # Test recommendations
        test_coverage = results["test_results"].get("coverage", 0.0)
        if test_coverage < 0.8:
            recommendations.append("Increase test coverage to meet 80% threshold")

        failed_tests = results["test_results"].get("failed", 0)
        if failed_tests > 0:
            recommendations.append(f"Fix {failed_tests} failing test(s)")

        # Performance recommendations
        perf_bottlenecks = results["performance_results"].get("bottlenecks", [])
        if perf_bottlenecks:
            recommendations.append("Address performance bottlenecks")

        # Security recommendations
        critical_vulns = results["security_results"].get("critical_vulnerabilities", [])
        if critical_vulns:
            recommendations.append("URGENT: Fix critical security vulnerabilities")

        risk_score = results["security_results"].get("risk_score", 0.0)
        if risk_score > 7.0:
            recommendations.append("Review and improve security posture")

        # Compliance recommendations
        compliance_level = results["compliance_results"].get("overall_compliance", "")
        if compliance_level in ["non_compliant", "partially_compliant"]:
            recommendations.append("Improve compliance with project standards")

        # Overall recommendations
        overall_score = results["overall_quality_score"]
        if overall_score >= 0.95:
            recommendations.append("Excellent quality! Maintain current standards")
        elif overall_score >= 0.8:
            recommendations.append("Good quality, address minor issues for excellence")
        elif overall_score >= 0.6:
            recommendations.append("Fair quality, significant improvements needed")
        else:
            recommendations.append("Poor quality, comprehensive improvements required")

        return recommendations

    async def _store_qa_results(self, results: Dict[str, Any]):
        """Store QA results in persistent storage."""
        try:
            await self.storage.store_result(
                namespace="qa_results",
                key=f"qa_{Path(results['skill_path']).name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                data=results,
            )
        except Exception as e:
            print(f"Warning: Failed to store QA results: {e}")

    async def _save_qa_report(self, results: Dict[str, Any]):
        """Save detailed QA report to file."""
        try:
            skill_name = Path(results["skill_path"]).name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.output_dir / f"qa_report_{skill_name}_{timestamp}.json"

            with open(report_file, "w") as f:
                json.dump(results, f, indent=2, default=str)

            print(f"📄 Detailed report saved: {report_file}")

            # Generate summary report
            summary_file = self.output_dir / f"qa_summary_{skill_name}_{timestamp}.txt"
            with open(summary_file, "w") as f:
                f.write(f"Quality Assurance Report\n")
                f.write(f"{'=' * 50}\n\n")
                f.write(f"Skill: {results['skill_path']}\n")
                f.write(f"Timestamp: {results['timestamp']}\n")
                f.write(f"Overall Quality Score: {results['overall_quality_score']:.2f}\n")
                f.write(f"Status: {results['status']}\n\n")

                f.write(f"Validation Results:\n")
                f.write(f"  Passed: {results['validation_results'].get('passed', False)}\n")
                f.write(f"  Confidence: {results['validation_results'].get('confidence', 0.0):.2f}\n\n")

                f.write(f"Test Results:\n")
                f.write(f"  Total Tests: {results['test_results'].get('total_tests', 0)}\n")
                f.write(f"  Passed: {results['test_results'].get('passed', 0)}\n")
                f.write(f"  Failed: {results['test_results'].get('failed', 0)}\n")
                f.write(f"  Coverage: {results['test_results'].get('coverage', 0.0):.1%}\n\n")

                f.write(f"Security Results:\n")
                f.write(f"  Vulnerabilities: {results['security_results'].get('vulnerabilities_found', 0)}\n")
                f.write(f"  Risk Score: {results['security_results'].get('risk_score', 0.0):.1f}/10\n\n")

                f.write(f"Compliance Results:\n")
                f.write(f"  Level: {results['compliance_results'].get('overall_compliance', 'unknown')}\n")
                f.write(f"  Score: {results['compliance_results'].get('compliance_score', 0.0):.2f}\n\n")

                f.write(f"Recommendations:\n")
                for i, rec in enumerate(results["recommendations"], 1):
                    f.write(f"  {i}. {rec}\n")

            print(f"📋 Summary report saved: {summary_file}")

        except Exception as e:
            print(f"Warning: Failed to save QA reports: {e}")

    async def run_batch_qa(self, skills_dir: str, pattern: str = "**/*.py") -> Dict[str, Any]:
        """
        Run QA on multiple skills in batch.

        Args:
            skills_dir: Directory containing skills
            pattern: Glob pattern for skill files

        Returns:
            Batch QA results
        """
        skills_path = Path(skills_dir)
        skill_files = list(skills_path.glob(pattern))

        print(f"🚀 Starting batch QA on {len(skill_files)} skills")

        batch_results = {
            "batch_timestamp": datetime.now().isoformat(),
            "total_skills": len(skill_files),
            "results": {},
            "summary": {"completed": 0, "failed": 0, "average_quality_score": 0.0, "skills_above_threshold": 0},
        }

        total_score = 0.0

        for skill_file in skill_files:
            print(f"\n{'=' * 60}")
            try:
                result = await self.run_full_qa(str(skill_file))
                batch_results["results"][str(skill_file)] = result

                if result["status"] == "completed":
                    batch_results["summary"]["completed"] += 1
                    total_score += result["overall_quality_score"]
                    if result["overall_quality_score"] >= self.accuracy_threshold:
                        batch_results["summary"]["skills_above_threshold"] += 1
                else:
                    batch_results["summary"]["failed"] += 1

            except Exception as e:
                print(f"❌ Failed to process {skill_file}: {e}")
                batch_results["summary"]["failed"] += 1
                batch_results["results"][str(skill_file)] = {"status": "failed", "error": str(e)}

        # Calculate batch statistics
        completed_count = batch_results["summary"]["completed"]
        if completed_count > 0:
            batch_results["summary"]["average_quality_score"] = total_score / completed_count

        # Save batch report
        batch_report_file = self.output_dir / f"batch_qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(batch_report_file, "w") as f:
            json.dump(batch_results, f, indent=2, default=str)

        print(f"\n{'=' * 60}")
        print(f"🏁 Batch QA completed")
        print(f"📊 Completed: {batch_results['summary']['completed']}")
        print(f"❌ Failed: {batch_results['summary']['failed']}")
        print(f"📈 Average Quality Score: {batch_results['summary']['average_quality_score']:.2f}")
        print(f"✅ Skills Above Threshold: {batch_results['summary']['skills_above_threshold']}")
        print(f"📄 Batch report saved: {batch_report_file}")

        return batch_results


async def main():
    """Main entry point for QA framework."""
    parser = argparse.ArgumentParser(description="Quality Assurance Framework for Skills")
    parser.add_argument("path", help="Path to skill file or directory")
    parser.add_argument("--batch", action="store_true", help="Run QA on multiple skills")
    parser.add_argument("--pattern", default="**/*.py", help="Glob pattern for batch mode")
    parser.add_argument("--threshold", type=float, default=0.95, help="Accuracy threshold")
    parser.add_argument("--output", default="qa_reports", help="Output directory for reports")
    parser.add_argument("--no-learning", action="store_true", help="Disable continuous learning")
    parser.add_argument("--auto-fix", action="store_true", help="Enable automatic fixing")

    args = parser.parse_args()

    # Initialize QA framework
    qa_framework = QualityAssuranceFramework(
        accuracy_threshold=args.threshold,
        enable_learning=not args.no_learning,
        auto_fix=args.auto_fix,
        output_dir=args.output,
    )

    try:
        if args.batch:
            # Run batch QA
            results = await qa_framework.run_batch_qa(args.path, args.pattern)
        else:
            # Run single skill QA
            results = await qa_framework.run_full_qa(args.path)

        # Exit with appropriate code
        if args.batch:
            sys.exit(0 if results["summary"]["failed"] == 0 else 1)
        else:
            sys.exit(0 if results["status"] == "completed" else 1)

    except KeyboardInterrupt:
        print("\n⚠️ QA interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ QA failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
