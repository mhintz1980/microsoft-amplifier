"""
Amplifier Skills Quality Assurance Framework

Zero hallucination enforcement system for 57 skills with comprehensive validation,
automated testing, performance monitoring, and continuous improvement.

This framework ensures 100% accuracy, security, and compliance across all skills
while maintaining high performance and user satisfaction.
"""

from .validators.zero_hallucination_validator import ZeroHallucinationValidator
from .testing.automated_test_generator import AutomatedTestGenerator
from .performance.performance_monitor import PerformanceMonitor
from .security.security_scanner import SecurityScanner
from .compliance.compliance_validator import ComplianceValidator
from .learning.continuous_improvement import ContinuousImprovement
from .storage.quality_metrics_storage import QualityMetricsStorage

__all__ = [
    "ZeroHallucinationValidator",
    "AutomatedTestGenerator",
    "PerformanceMonitor",
    "SecurityScanner",
    "ComplianceValidator",
    "ContinuousImprovement",
    "QualityMetricsStorage",
]

# QA Framework version and standards
QA_VERSION = "1.0.0"
HALLUCINATION_TOLERANCE = 0.0  # Zero tolerance
MIN_ACCURACY_THRESHOLD = 0.95  # 95% minimum accuracy
SECURITY_COMPLIANCE_REQUIRED = True
PERFORMANCE_MONITORING_ENABLED = True
CONTINUOUS_IMPROVEMENT_ENABLED = True
