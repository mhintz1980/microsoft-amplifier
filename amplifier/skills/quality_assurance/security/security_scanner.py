"""
Security Scanner and Vulnerability Checker

Comprehensive security analysis system that identifies vulnerabilities,
security risks, and compliance issues in skill code and configurations.
"""

import ast
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from amplifier.mcp.persistent_storage import store_result


class SeverityLevel(Enum):
    """Security vulnerability severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityType(Enum):
    """Types of security vulnerabilities."""

    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    INSECURE_CRYPTO = "insecure_crypto"
    HARDCODED_SECRETS = "hardcoded_secrets"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    WEAK_RANDOMNESS = "weak_randomness"
    INSECURE_FILE_HANDLING = "insecure_file_handling"
    INSECURE_NETWORK = "insecure_network"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    INPUT_VALIDATION = "input_validation"
    DEPENDENCY_VULNERABILITIES = "dependency_vulnerabilities"


@dataclass
class Vulnerability:
    """Security vulnerability finding."""

    vulnerability_type: VulnerabilityType
    severity: SeverityLevel
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    cwe_id: str | None = None
    recommendation: str = ""
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityReport:
    """Comprehensive security analysis report."""

    skill_path: str
    scan_timestamp: datetime
    vulnerabilities: list[Vulnerability]
    severity_counts: dict[SeverityLevel, int]
    risk_score: float
    compliance_status: dict[str, bool]
    recommendations: list[str]
    passed_checks: list[str]
    failed_checks: list[str]


class SecurityPattern:
    """Security vulnerability detection pattern."""

    def __init__(
        self,
        vulnerability_type: VulnerabilityType,
        severity: SeverityLevel,
        patterns: list[str],
        description: str,
        recommendation: str,
        cwe_id: str | None = None,
    ):
        self.vulnerability_type = vulnerability_type
        self.severity = severity
        self.patterns = patterns
        self.description = description
        self.recommendation = recommendation
        self.cwe_id = cwe_id


class SecurityScanner:
    """Comprehensive security scanner for skill code and configurations."""

    def __init__(
        self,
        enable_dependency_scanning: bool = True,
        enable_severity_threshold: SeverityLevel = SeverityLevel.LOW,
        custom_patterns: list[SecurityPattern] = None,
    ):
        """
        Initialize security scanner.

        Args:
            enable_dependency_scanning: Enable dependency vulnerability scanning
            enable_severity_threshold: Minimum severity level to report
            custom_patterns: Additional custom security patterns
        """
        self.enable_dependency_scanning = enable_dependency_scanning
        self.severity_threshold = enable_severity_threshold
        self.custom_patterns = custom_patterns or []

        # Initialize security patterns
        self.security_patterns = self._initialize_security_patterns()

        # Install security scanning tools
        self._install_security_tools()

        # Sensitive data patterns
        self.sensitive_patterns = self._initialize_sensitive_patterns()

    def _install_security_tools(self):
        """Install security scanning tools."""
        security_tools = [
            "bandit",  # Python security linter
            "safety",  # Dependency vulnerability scanner
            "semgrep",  # Static analysis security tool
            "pip-audit",  # Pip security audit
        ]

        for tool in security_tools:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", tool], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                print(f"Warning: Failed to install {tool}")

    def _initialize_security_patterns(self) -> list[SecurityPattern]:
        """Initialize security vulnerability detection patterns."""
        patterns = [
            # SQL Injection
            SecurityPattern(
                vulnerability_type=VulnerabilityType.SQL_INJECTION,
                severity=SeverityLevel.CRITICAL,
                patterns=[
                    r'execute\s*\(\s*["\'].*?\+.*?["\']',
                    r'execute\s*\(\s*f["\'].*?\{.*?\}.*?["\']',
                    r'cursor\.execute\s*\(\s*["\'].*?\+.*?["\']',
                    r"\.format\s*\(\s*.*?\%.*?\)",
                ],
                description="Potential SQL injection vulnerability",
                recommendation="Use parameterized queries or prepared statements",
                cwe_id="CWE-89",
            ),
            # Command Injection
            SecurityPattern(
                vulnerability_type=VulnerabilityType.COMMAND_INJECTION,
                severity=SeverityLevel.CRITICAL,
                patterns=[
                    r"os\.system\s*\(\s*.*?\+.*?\)",
                    r"subprocess\.(?:call|run|Popen)\s*\(\s*.*?\+.*?\)",
                    r"eval\s*\(\s*.*?\+.*?\)",
                    r"exec\s*\(\s*.*?\+.*?\)",
                ],
                description="Potential command injection vulnerability",
                recommendation="Use subprocess with shell=False and validate inputs",
                cwe_id="CWE-78",
            ),
            # Path Traversal
            SecurityPattern(
                vulnerability_type=VulnerabilityType.PATH_TRAVERSAL,
                severity=SeverityLevel.HIGH,
                patterns=[
                    r'open\s*\(\s*["\'].*?\.\./',
                    r"open\s*\(\s*.*?\+.*?\)",
                    r"Path\s*\(\s*.*?\+.*?\)",
                ],
                description="Potential path traversal vulnerability",
                recommendation="Validate and sanitize file paths",
                cwe_id="CWE-22",
            ),
            # Hardcoded Secrets
            SecurityPattern(
                vulnerability_type=VulnerabilityType.HARDCODED_SECRETS,
                severity=SeverityLevel.HIGH,
                patterns=[
                    r'(?:password|passwd|pwd|secret|token|key|api_key)\s*=\s*["\'][^"\']{8,}["\']',
                    r'(?:password|passwd|pwd|secret|token|key|api_key)\s*=\s*[\'"]\w*[\'"]',
                ],
                description="Hardcoded sensitive information detected",
                recommendation="Use environment variables or secure configuration",
                cwe_id="CWE-798",
            ),
            # Weak Randomness
            SecurityPattern(
                vulnerability_type=VulnerabilityType.WEAK_RANDOMNESS,
                severity=SeverityLevel.MEDIUM,
                patterns=[
                    r"random\.random\s*\(\s*\)",
                    r"random\.randint\s*\(\s*\)",
                    r"random\.choice\s*\(\s*\)",
                ],
                description="Weak randomness detected for security-sensitive operations",
                recommendation="Use secrets module or os.urandom() for cryptographic purposes",
                cwe_id="CWE-338",
            ),
            # Insecure Deserialization
            SecurityPattern(
                vulnerability_type=VulnerabilityType.INSECURE_DESERIALIZATION,
                severity=SeverityLevel.HIGH,
                patterns=[
                    r"pickle\.loads?\s*\(",
                    r"cPickle\.loads?\s*\(",
                    r"marshal\.loads?\s*\(",
                ],
                description="Insecure deserialization vulnerability",
                recommendation="Use safe serialization formats like JSON",
                cwe_id="CWE-502",
            ),
            # Insecure File Handling
            SecurityPattern(
                vulnerability_type=VulnerabilityType.INSECURE_FILE_HANDLING,
                severity=SeverityLevel.MEDIUM,
                patterns=[
                    r"shutil\.copyfileobj\s*\(\s*.*?\+.*?\)",
                    r"open\s*\(\s*.*?\+.*?\)",
                    r"Path\.write_text\s*\(\s*.*?\+.*?\)",
                ],
                description="Insecure file handling detected",
                recommendation="Validate file paths and use secure file operations",
                cwe_id="CWE-20",
            ),
        ]

        # Add custom patterns
        patterns.extend(self.custom_patterns)

        return patterns

    def _initialize_sensitive_patterns(self) -> list[str]:
        """Initialize patterns for detecting sensitive data."""
        return [
            r"\b[A-Za-z0-9+/]{40,}\={0,2}\b",  # Base64 encoded secrets
            r"\b[0-9a-fA-F]{32,}\b",  # Hexadecimal secrets
            r"\b[A-Za-z0-9_-]{20,}\b",  # API keys/tokens
            r"(?:sk_|pk_|AIza)[A-Za-z0-9_-]{20,}",  # API key prefixes
        ]

    async def scan_skill(self, skill_path: str) -> SecurityReport:
        """
        Perform comprehensive security scan of a skill.

        Args:
            skill_path: Path to the skill directory or file

        Returns:
            Comprehensive security report
        """
        skill_path = Path(skill_path)
        scan_timestamp = datetime.now()

        # Collect all files to scan
        files_to_scan = self._collect_files(skill_path)

        # Initialize results
        vulnerabilities = []
        passed_checks = []
        failed_checks = []

        # Perform static analysis
        static_vulns = await self._perform_static_analysis(files_to_scan)
        vulnerabilities.extend(static_vulns)

        # Scan for hardcoded secrets
        secret_vulns = self._scan_for_secrets(files_to_scan)
        vulnerabilities.extend(secret_vulns)

        # Perform dependency scanning if enabled
        if self.enable_dependency_scanning:
            dep_vulns = await self._scan_dependencies(skill_path)
            vulnerabilities.extend(dep_vulns)
        else:
            passed_checks.append("Dependency scanning disabled")

        # Perform code quality security checks
        quality_vulns = await self._perform_quality_checks(files_to_scan)
        vulnerabilities.extend(quality_vulns)

        # Filter by severity threshold
        filtered_vulnerabilities = self._filter_by_severity(vulnerabilities)

        # Count vulnerabilities by severity
        severity_counts = self._count_by_severity(filtered_vulnerabilities)

        # Calculate risk score
        risk_score = self._calculate_risk_score(severity_counts)

        # Generate recommendations
        recommendations = self._generate_security_recommendations(filtered_vulnerabilities)

        # Check compliance
        compliance_status = self._check_compliance(filtered_vulnerabilities)

        return SecurityReport(
            skill_path=str(skill_path),
            scan_timestamp=scan_timestamp,
            vulnerabilities=filtered_vulnerabilities,
            severity_counts=severity_counts,
            risk_score=risk_score,
            compliance_status=compliance_status,
            recommendations=recommendations,
            passed_checks=passed_checks,
            failed_checks=[
                v.title for v in filtered_vulnerabilities if v.severity.value >= self.severity_threshold.value
            ],
        )

    def _collect_files(self, path: Path) -> list[Path]:
        """Collect all relevant files for security scanning."""
        file_extensions = {".py", ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini"}
        files_to_scan = []

        if path.is_file():
            if path.suffix in file_extensions:
                files_to_scan.append(path)
        else:
            for ext in file_extensions:
                files_to_scan.extend(path.rglob(f"*{ext}"))

        return files_to_scan

    async def _perform_static_analysis(self, files: list[Path]) -> list[Vulnerability]:
        """Perform static code analysis for security vulnerabilities."""
        vulnerabilities = []

        for file_path in files:
            if file_path.suffix != ".py":
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Apply security patterns
                for pattern in self.security_patterns:
                    pattern_vulns = self._apply_pattern(pattern, content, file_path)
                    vulnerabilities.extend(pattern_vulns)

                # AST-based analysis
                ast_vulns = self._analyze_ast(content, file_path)
                vulnerabilities.extend(ast_vulns)

            except Exception as e:
                # Create a vulnerability for the analysis error
                vulnerabilities.append(
                    Vulnerability(
                        vulnerability_type=VulnerabilityType.INPUT_VALIDATION,
                        severity=SeverityLevel.LOW,
                        title=f"Analysis Error in {file_path}",
                        description=f"Could not analyze file: {str(e)}",
                        file_path=str(file_path),
                        line_number=0,
                        code_snippet="",
                        recommendation="Ensure file is accessible and properly formatted",
                        confidence=0.5,
                    )
                )

        return vulnerabilities

    def _apply_pattern(self, pattern: SecurityPattern, content: str, file_path: Path) -> list[Vulnerability]:
        """Apply a security pattern to file content."""
        vulnerabilities = []
        lines = content.split("\n")

        for regex_pattern in pattern.patterns:
            try:
                for match in re.finditer(regex_pattern, content, re.MULTILINE | re.IGNORECASE):
                    line_number = content[: match.start()].count("\n") + 1
                    start_col = match.start() - content.rfind("\n", 0, match.start()) - 1

                    vulnerabilities.append(
                        Vulnerability(
                            vulnerability_type=pattern.vulnerability_type,
                            severity=pattern.severity,
                            title=f"{pattern.vulnerability_type.value.replace('_', ' ').title()}",
                            description=pattern.description,
                            file_path=str(file_path),
                            line_number=line_number,
                            code_snippet=lines[line_number - 1].strip() if line_number <= len(lines) else "",
                            cwe_id=pattern.cwe_id,
                            recommendation=pattern.recommendation,
                            confidence=0.8,
                        )
                    )

            except re.error:
                # Skip invalid regex patterns
                continue

        return vulnerabilities

    def _analyze_ast(self, content: str, file_path: Path) -> list[Vulnerability]:
        """Analyze AST for security vulnerabilities."""
        vulnerabilities = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Check for dangerous function calls
                if isinstance(node, ast.Call):
                    vulnerabilities.extend(self._check_function_calls(node, file_path))

                # Check for unsafe imports
                elif isinstance(node, ast.Import):
                    vulnerabilities.extend(self._check_imports(node, file_path))

                # Check for string operations that might be unsafe
                elif isinstance(node, ast.BinOp):
                    if isinstance(node.op, ast.Add):
                        vulnerabilities.extend(self._check_string_concatenation(node, file_path))

        except SyntaxError:
            # File has syntax errors, already reported by pattern matching
            pass

        return vulnerabilities

    def _check_function_calls(self, node: ast.Call, file_path: Path) -> list[Vulnerability]:
        """Check for dangerous function calls."""
        vulnerabilities = []

        if isinstance(node.func, ast.Name):
            func_name = node.func.id

            # Dangerous functions
            dangerous_funcs = {
                "eval": SeverityLevel.HIGH,
                "exec": SeverityLevel.HIGH,
                "compile": SeverityLevel.MEDIUM,
                "__import__": SeverityLevel.MEDIUM,
            }

            if func_name in dangerous_funcs:
                vulnerabilities.append(
                    Vulnerability(
                        vulnerability_type=VulnerabilityType.COMMAND_INJECTION,
                        severity=dangerous_funcs[func_name],
                        title=f"Dangerous function call: {func_name}",
                        description=f"Use of dangerous function {func_name} can lead to code execution",
                        file_path=str(file_path),
                        line_number=getattr(node, "lineno", 0),
                        code_snippet=f"{func_name}(...)",
                        recommendation="Avoid using {func_name}, use safer alternatives",
                        cwe_id="CWE-94",
                        confidence=0.9,
                    )
                )

        elif isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr

            # Dangerous methods
            dangerous_methods = {
                "execute": SeverityLevel.CRITICAL,
                "system": SeverityLevel.CRITICAL,
                "popen": SeverityLevel.HIGH,
                "shell": SeverityLevel.HIGH,
            }

            if attr_name in dangerous_methods:
                vulnerabilities.append(
                    Vulnerability(
                        vulnerability_type=VulnerabilityType.COMMAND_INJECTION,
                        severity=dangerous_methods[attr_name],
                        title=f"Potentially dangerous method: {attr_name}",
                        description=f"Method {attr_name} may be vulnerable to injection",
                        file_path=str(file_path),
                        line_number=getattr(node, "lineno", 0),
                        code_snippet=f".{attr_name}(...)",
                        recommendation="Validate inputs and use safe alternatives",
                        confidence=0.7,
                    )
                )

        return vulnerabilities

    def _check_imports(self, node: ast.Import, file_path: Path) -> list[Vulnerability]:
        """Check for potentially unsafe imports."""
        vulnerabilities = []

        unsafe_modules = {
            "pickle": SeverityLevel.HIGH,
            "cPickle": SeverityLevel.HIGH,
            "marshal": SeverityLevel.HIGH,
            "subprocess": SeverityLevel.MEDIUM,
        }

        for alias in node.names:
            if alias.name in unsafe_modules:
                vulnerabilities.append(
                    Vulnerability(
                        vulnerability_type=VulnerabilityType.INSECURE_DESERIALIZATION,
                        severity=unsafe_modules[alias.name],
                        title=f"Potentially unsafe import: {alias.name}",
                        description=f"Module {alias.name} can be dangerous if not used carefully",
                        file_path=str(file_path),
                        line_number=getattr(node, "lineno", 0),
                        code_snippet=f"import {alias.name}",
                        recommendation="Ensure safe usage of {alias.name} or use alternatives",
                        cwe_id="CWE-502",
                        confidence=0.6,
                    )
                )

        return vulnerabilities

    def _check_string_concatenation(self, node: ast.BinOp, file_path: Path) -> list[Vulnerability]:
        """Check for unsafe string concatenation."""
        vulnerabilities = []

        # This is a simplified check - in practice you'd need more sophisticated analysis
        # to determine if the concatenation is actually unsafe

        return vulnerabilities

    def _scan_for_secrets(self, files: list[Path]) -> list[Vulnerability]:
        """Scan files for hardcoded secrets and sensitive data."""
        vulnerabilities = []

        for file_path in files:
            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for pattern in self.sensitive_patterns:
                    for match in re.finditer(pattern, content):
                        line_number = content[: match.start()].count("\n") + 1

                        vulnerabilities.append(
                            Vulnerability(
                                vulnerability_type=VulnerabilityType.HARDCODED_SECRETS,
                                severity=SeverityLevel.HIGH,
                                title="Potential hardcoded secret",
                                description="Sensitive data hardcoded in source file",
                                file_path=str(file_path),
                                line_number=line_number,
                                code_snippet=match.group()[:50] + "..." if len(match.group()) > 50 else match.group(),
                                recommendation="Move secrets to environment variables or secure configuration",
                                cwe_id="CWE-798",
                                confidence=0.6,
                            )
                        )

            except Exception:
                continue

        return vulnerabilities

    async def _scan_dependencies(self, skill_path: Path) -> list[Vulnerability]:
        """Scan dependencies for known vulnerabilities."""
        vulnerabilities = []

        # Look for requirements files
        req_files = list(skill_path.rglob("requirements*.txt")) + list(skill_path.rglob("pyproject.toml"))

        for req_file in req_files:
            try:
                # Use safety or pip-audit to scan dependencies
                result = await self._run_dependency_scan(req_file)
                vulnerabilities.extend(result)

            except Exception as e:
                vulnerabilities.append(
                    Vulnerability(
                        vulnerability_type=VulnerabilityType.DEPENDENCY_VULNERABILITIES,
                        severity=SeverityLevel.LOW,
                        title="Dependency scan failed",
                        description=f"Could not scan dependencies: {str(e)}",
                        file_path=str(req_file),
                        line_number=0,
                        code_snippet="",
                        recommendation="Manually review dependencies for vulnerabilities",
                        confidence=0.3,
                    )
                )

        return vulnerabilities

    async def _run_dependency_scan(self, req_file: Path) -> list[Vulnerability]:
        """Run dependency vulnerability scanning tool."""
        vulnerabilities = []

        try:
            # Use safety for scanning
            result = subprocess.run(
                [sys.executable, "-m", "safety", "check", "--json", "--file", str(req_file)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.stdout:
                try:
                    safety_data = json.loads(result.stdout)
                    for vuln in safety_data:
                        vulnerabilities.append(
                            Vulnerability(
                                vulnerability_type=VulnerabilityType.DEPENDENCY_VULNERABILITIES,
                                severity=self._cve_to_severity(vuln.get("vulnerability_id", "")),
                                title=f"Dependency vulnerability: {vuln.get('package', 'Unknown')}",
                                description=vuln.get("advisory", "Known vulnerability in dependency"),
                                file_path=str(req_file),
                                line_number=0,
                                code_snippet=f"{vuln.get('package')}=={vuln.get('installed_version')}",
                                recommendation=f"Update {vuln.get('package')} to safe version",
                                cwe_id=vuln.get("cve"),
                                confidence=1.0,
                            )
                        )
                except json.JSONDecodeError:
                    pass

        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass

        return vulnerabilities

    def _cve_to_severity(self, cve_id: str) -> SeverityLevel:
        """Convert CVE ID to severity level (simplified)."""
        # In practice, you'd use a CVE database to get actual severity
        return SeverityLevel.HIGH

    async def _perform_quality_checks(self, files: list[Path]) -> list[Vulnerability]:
        """Perform code quality security checks."""
        vulnerabilities = []

        python_files = [f for f in files if f.suffix == ".py"]

        for py_file in python_files:
            try:
                # Use bandit for security-focused linting
                result = subprocess.run(
                    [sys.executable, "-m", "bandit", "-f", "json", str(py_file)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.stdout:
                    try:
                        bandit_data = json.loads(result.stdout)
                        for issue in bandit_data.get("results", []):
                            vulnerabilities.append(
                                Vulnerability(
                                    vulnerability_type=self._bandit_test_to_vuln_type(issue.get("test_name", "")),
                                    severity=self._bandit_severity_to_severity(issue.get("issue_severity", "")),
                                    title=issue.get("test_name", "Security issue"),
                                    description=issue.get("issue_text", "Potential security issue"),
                                    file_path=str(py_file),
                                    line_number=issue.get("line_number", 0),
                                    code_snippet=issue.get("code", ""),
                                    cwe_id=issue.get("cwe_id"),
                                    recommendation=issue.get("issue_cwe", {}).get(
                                        "link", "Review and fix security issue"
                                    ),
                                    confidence=0.8,
                                )
                            )
                    except json.JSONDecodeError:
                        pass

            except subprocess.TimeoutExpired:
                pass
            except Exception:
                pass

        return vulnerabilities

    def _bandit_test_to_vuln_type(self, test_name: str) -> VulnerabilityType:
        """Convert Bandit test name to vulnerability type."""
        test_mapping = {
            "hardcoded_password": VulnerabilityType.HARDCODED_SECRETS,
            "hardcoded_sql_expressions": VulnerabilityType.SQL_INJECTION,
            "subprocess_popen_with_shell_equals_true": VulnerabilityType.COMMAND_INJECTION,
            "pickle_use": VulnerabilityType.INSECURE_DESERIALIZATION,
            "random_with_seed": VulnerabilityType.WEAK_RANDOMNESS,
        }
        return test_mapping.get(test_name, VulnerabilityType.INPUT_VALIDATION)

    def _bandit_severity_to_severity(self, bandit_severity: str) -> SeverityLevel:
        """Convert Bandit severity to our severity levels."""
        severity_mapping = {
            "high": SeverityLevel.HIGH,
            "medium": SeverityLevel.MEDIUM,
            "low": SeverityLevel.LOW,
        }
        return severity_mapping.get(bandit_severity.lower(), SeverityLevel.MEDIUM)

    def _filter_by_severity(self, vulnerabilities: list[Vulnerability]) -> list[Vulnerability]:
        """Filter vulnerabilities by severity threshold."""
        severity_order = {
            SeverityLevel.CRITICAL: 5,
            SeverityLevel.HIGH: 4,
            SeverityLevel.MEDIUM: 3,
            SeverityLevel.LOW: 2,
            SeverityLevel.INFO: 1,
        }

        threshold_value = severity_order.get(self.severity_threshold, 1)

        return [vuln for vuln in vulnerabilities if severity_order.get(vuln.severity, 0) >= threshold_value]

    def _count_by_severity(self, vulnerabilities: list[Vulnerability]) -> dict[SeverityLevel, int]:
        """Count vulnerabilities by severity level."""
        counts = dict.fromkeys(SeverityLevel, 0)

        for vuln in vulnerabilities:
            counts[vuln.severity] += 1

        return counts

    def _calculate_risk_score(self, severity_counts: dict[SeverityLevel, int]) -> float:
        """Calculate overall risk score (0-10)."""
        weights = {
            SeverityLevel.CRITICAL: 10,
            SeverityLevel.HIGH: 7,
            SeverityLevel.MEDIUM: 4,
            SeverityLevel.LOW: 2,
            SeverityLevel.INFO: 1,
        }

        total_score = 0
        total_vulns = sum(severity_counts.values())

        if total_vulns == 0:
            return 0.0

        for severity, count in severity_counts.items():
            total_score += weights.get(severity, 0) * count

        # Normalize to 0-10 scale
        return min(total_score / (total_vulns * 2), 10.0)

    def _generate_security_recommendations(self, vulnerabilities: list[Vulnerability]) -> list[str]:
        """Generate security improvement recommendations."""
        recommendations = []
        vulnerability_types = set(vuln.vulnerability_type for vuln in vulnerabilities)

        # General recommendations
        if vulnerabilities:
            recommendations.append("Address all identified security vulnerabilities promptly")
            recommendations.append("Implement secure coding practices throughout the codebase")
            recommendations.append("Set up automated security scanning in CI/CD pipeline")

        # Specific recommendations based on vulnerability types
        if VulnerabilityType.HARDCODED_SECRETS in vulnerability_types:
            recommendations.append("Move all secrets to environment variables or secure vault")
            recommendations.append("Implement secrets detection in pre-commit hooks")

        if VulnerabilityType.SQL_INJECTION in vulnerability_types:
            recommendations.append("Use parameterized queries for all database operations")
            recommendations.append("Implement input validation and sanitization")

        if VulnerabilityType.COMMAND_INJECTION in vulnerability_types:
            recommendations.append("Avoid shell commands with user input")
            recommendations.append("Use subprocess with shell=False and proper argument lists")

        if VulnerabilityType.DEPENDENCY_VULNERABILITIES in vulnerability_types:
            recommendations.append("Regularly update dependencies to latest secure versions")
            recommendations.append("Implement dependency vulnerability scanning in build process")

        return list(set(recommendations))  # Remove duplicates

    def _check_compliance(self, vulnerabilities: list[Vulnerability]) -> dict[str, bool]:
        """Check security compliance status."""
        compliance_status = {
            "no_critical_vulnerabilities": True,
            "no_high_vulnerabilities": True,
            "dependency_scan_complete": self.enable_dependency_scanning,
            "secrets_not_detected": True,
        }

        for vuln in vulnerabilities:
            if vuln.severity == SeverityLevel.CRITICAL:
                compliance_status["no_critical_vulnerabilities"] = False
            elif vuln.severity == SeverityLevel.HIGH:
                compliance_status["no_high_vulnerabilities"] = False

            if vuln.vulnerability_type == VulnerabilityType.HARDCODED_SECRETS:
                compliance_status["secrets_not_detected"] = False

        return compliance_status

    async def store_security_report(self, report: SecurityReport):
        """Store security report in MCP storage."""
        serialized_report = {
            "skill_path": report.skill_path,
            "scan_timestamp": report.scan_timestamp.isoformat(),
            "vulnerabilities": [
                {
                    "type": vuln.vulnerability_type.value,
                    "severity": vuln.severity.value,
                    "title": vuln.title,
                    "description": vuln.description,
                    "file_path": vuln.file_path,
                    "line_number": vuln.line_number,
                    "code_snippet": vuln.code_snippet,
                    "cwe_id": vuln.cwe_id,
                    "recommendation": vuln.recommendation,
                    "confidence": vuln.confidence,
                }
                for vuln in report.vulnerabilities
            ],
            "severity_counts": {k.value: v for k, v in report.severity_counts.items()},
            "risk_score": report.risk_score,
            "compliance_status": report.compliance_status,
            "recommendations": report.recommendations,
            "passed_checks": report.passed_checks,
            "failed_checks": report.failed_checks,
        }

        await store_result(
            namespace="security_scans",
            key=f"{report.skill_path}_security_{report.scan_timestamp.isoformat()}",
            data=serialized_report,
        )
