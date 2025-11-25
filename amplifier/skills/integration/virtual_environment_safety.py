"""
Virtual Environment Safety and Isolation System

This module provides comprehensive safety measures for executing untrusted code
and processing potentially dangerous technical content in isolated environments.

Features:
- Sandboxed execution environments
- Resource limits and monitoring
- Security validation and scanning
- Safe code execution patterns
- Temporary file isolation
- Process isolation and cleanup
- Audit logging and monitoring
"""

import asyncio
import json
import logging
import os
import psutil
import signal
import subprocess
import tempfile
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Security libraries
try:
    import resource
except ImportError:
    resource = None
    logging.warning("resource module not available on this platform")


class SafetyLevel(Enum):
    """Safety levels for code execution."""

    MINIMAL = "minimal"  # Basic validation only
    STANDARD = "standard"  # Standard safety measures
    HIGH = "high"  # Comprehensive safety
    MAXIMUM = "maximum"  # Maximum isolation and security


class SecurityViolationType(Enum):
    """Types of security violations."""

    DANGEROUS_IMPORTS = "dangerous_imports"
    SYSTEM_CALLS = "system_calls"
    FILE_ACCESS = "file_access"
    NETWORK_ACCESS = "network_access"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    SUSPICIOUS_PATTERNS = "suspicious_patterns"
    TIMEOUT_VIOLATION = "timeout_violation"


@dataclass
class ResourceLimits:
    """Resource limits for isolated execution."""

    max_memory_mb: int = 512
    max_cpu_time_seconds: int = 30
    max_wall_time_seconds: int = 60
    max_processes: int = 10
    max_files: int = 100
    max_file_size_mb: int = 10
    max_network_connections: int = 0  # 0 = no network access

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary for subprocess limits."""
        return asdict(self)


@dataclass
class SecurityViolation:
    """Represents a detected security violation."""

    violation_type: SecurityViolationType
    severity: str  # "low", "medium", "high", "critical"
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    timestamp: str = None
    auto_blocked: bool = False

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ExecutionResult:
    """Result of safe code execution."""

    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    memory_used_mb: float
    violations: List[SecurityViolation] = None
    warnings: List[str] = None
    terminated_early: bool = False
    termination_reason: Optional[str] = None

    def __post_init__(self):
        if self.violations is None:
            self.violations = []
        if self.warnings is None:
            self.warnings = []


class VirtualEnvironmentSafety:
    """
    Comprehensive virtual environment safety system for isolated code execution.

    Provides:
    - Sandboxed Python execution
    - Resource monitoring and limits
    - Security scanning and validation
    - Process isolation
    - File system sandboxing
    - Network access control
    - Audit logging
    """

    def __init__(self, safety_level: SafetyLevel = SafetyLevel.HIGH):
        self.safety_level = safety_level
        self.temp_dirs = []
        self.active_processes = []
        self.audit_log = []

        # Security patterns to detect
        self.dangerous_patterns = {
            SecurityViolationType.DANGEROUS_IMPORTS: [
                r"import\s+subprocess",
                r"import\s+os(\.system)?",
                r"import\s+sys(\.modules)?",
                r"import\s+threading",
                r"import\s+multiprocessing",
                r"from\s+subprocess\s+import",
                r"from\s+os\s+import.*system",
                r"exec\s*\(",
                r"eval\s*\(",
                r"__import__\s*\(",
            ],
            SecurityViolationType.SYSTEM_CALLS: [
                r"subprocess\.call",
                r"subprocess\.run",
                r"subprocess\.Popen",
                r"os\.system",
                r"os\.popen",
                r"os\.spawn",
                r"os\.exec",
                r"commands\.",
                r"input\s*\(",  # Can be used for social engineering
            ],
            SecurityViolationType.FILE_ACCESS: [
                r"open\s*\([^)]*['\"][/\\]",  # Absolute paths
                r"\.read\s*\(",
                r"\.write\s*\(",
                r"\.read_text\s*\(",
                r"\.write_text\s*\(",
                r"shutil\.",
                r"pathlib\.Path\.",
                r"os\.remove",
                r"os\.rmdir",
            ],
            SecurityViolationType.NETWORK_ACCESS: [
                r"import\s+requests",
                r"import\s+urllib",
                r"import\s+socket",
                r"import\s+http\.",
                r"requests\.",
                r"urllib\.",
                r"socket\.",
                r"urlopen\s*\(",
            ],
        }

        # Safety level configurations
        self.safety_configs = {
            SafetyLevel.MINIMAL: ResourceLimits(
                max_memory_mb=1024, max_cpu_time_seconds=120, max_wall_time_seconds=180
            ),
            SafetyLevel.STANDARD: ResourceLimits(max_memory_mb=512, max_cpu_time_seconds=60, max_wall_time_seconds=90),
            SafetyLevel.HIGH: ResourceLimits(
                max_memory_mb=256, max_cpu_time_seconds=30, max_wall_time_seconds=45, max_network_connections=0
            ),
            SafetyLevel.MAXIMUM: ResourceLimits(
                max_memory_mb=128,
                max_cpu_time_seconds=15,
                max_wall_time_seconds=20,
                max_network_connections=0,
                max_processes=1,
            ),
        }

    @asynccontextmanager
    async def isolated_execution_environment(self, resource_limits: Optional[ResourceLimits] = None):
        """
        Context manager for creating an isolated execution environment.

        Args:
            resource_limits: Custom resource limits (uses safety level defaults if None)
        """
        if resource_limits is None:
            resource_limits = self.safety_configs[self.safety_level]

        temp_dir = None
        process_monitor = None

        try:
            # Create temporary directory
            temp_dir = Path(tempfile.mkdtemp(prefix="safe_exec_"))
            self.temp_dirs.append(temp_dir)

            # Create process monitor
            process_monitor = ProcessMonitor(resource_limits)

            logging.info(f"Created isolated environment: {temp_dir}")

            yield IsolatedEnvironment(temp_dir, process_monitor, self)

        except Exception as e:
            logging.error(f"Error in isolated execution environment: {e}")
            raise
        finally:
            # Cleanup
            if process_monitor:
                await process_monitor.cleanup()

            if temp_dir and temp_dir.exists():
                await self._safe_cleanup_directory(temp_dir)
                self.temp_dirs.remove(temp_dir)

    async def execute_code_safely(
        self, code: str, resource_limits: Optional[ResourceLimits] = None, allowed_imports: Optional[List[str]] = None
    ) -> ExecutionResult:
        """
        Execute code in a safe, isolated environment.

        Args:
            code: Python code to execute
            resource_limits: Custom resource limits
            allowed_imports: List of allowed import modules

        Returns:
            ExecutionResult: Complete execution result with safety analysis
        """
        start_time = time.time()
        violations = []
        warnings = []

        try:
            # Step 1: Security validation
            security_violations = await self._scan_code_for_violations(code)
            violations.extend(security_violations)

            # Block execution if critical violations found
            critical_violations = [v for v in violations if v.severity == "critical"]
            if critical_violations:
                return ExecutionResult(
                    success=False,
                    stdout="",
                    stderr="Execution blocked due to critical security violations",
                    exit_code=1,
                    execution_time=0,
                    memory_used_mb=0,
                    violations=violations,
                    terminated_early=True,
                    termination_reason="Critical security violations detected",
                )

            # Step 2: Prepare safe execution environment
            async with self.isolated_execution_environment(resource_limits) as env:
                # Step 3: Prepare safe code wrapper
                safe_code = await self._prepare_safe_code_wrapper(code, allowed_imports, violations)

                # Step 4: Execute code
                execution_result = await env.execute_python_code(safe_code)

                # Step 5: Analyze results for additional violations
                result_violations = await self._analyze_execution_results(execution_result)
                violations.extend(result_violations)

                # Update execution result with safety information
                execution_result.violations = violations
                execution_result.warnings = warnings
                execution_result.execution_time = time.time() - start_time

                # Log execution
                await self._log_execution(code, execution_result)

                return execution_result

        except Exception as e:
            logging.error(f"Safe code execution failed: {e}")
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                exit_code=1,
                execution_time=time.time() - start_time,
                memory_used_mb=0,
                violations=violations,
                terminated_early=True,
                termination_reason=f"Execution error: {str(e)}",
            )

    async def _scan_code_for_violations(self, code: str) -> List[SecurityViolation]:
        """Scan code for security violations."""
        violations = []
        lines = code.split("\n")

        for violation_type, patterns in self.dangerous_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE):
                    line_num = code[: match.start()].count("\n") + 1
                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""

                    # Determine severity based on violation type and safety level
                    severity = self._determine_violation_severity(violation_type, pattern)

                    violation = SecurityViolation(
                        violation_type=violation_type,
                        severity=severity,
                        description=f"Potentially dangerous {violation_type.value}: {pattern}",
                        line_number=line_num,
                        code_snippet=line_content.strip(),
                        auto_blocked=severity in ["high", "critical"],
                    )
                    violations.append(violation)

        return violations

    def _determine_violation_severity(self, violation_type: SecurityViolationType, pattern: str) -> str:
        """Determine severity of a security violation."""
        # Critical violations
        if any(keyword in pattern for keyword in ["exec", "eval", "__import__"]):
            return "critical"

        # High severity violations
        if violation_type in [SecurityViolationType.DANGEROUS_IMPORTS, SecurityViolationType.SYSTEM_CALLS]:
            return "high"

        # Medium severity violations
        if violation_type == SecurityViolationType.FILE_ACCESS:
            return "medium"

        # Default to low
        return "low"

    async def _prepare_safe_code_wrapper(
        self, code: str, allowed_imports: Optional[List[str]], violations: List[SecurityViolation]
    ) -> str:
        """Prepare a safe code wrapper with restrictions."""
        # Import restrictions
        import_restrictions = ""
        if allowed_imports:
            safe_imports = ", ".join(f"'{imp}'" for imp in allowed_imports)
            import_restrictions = f"""
# Import restrictions
__builtins__['__import__'] = lambda name, globals=None, locals=None, fromlist=(), level=0: (
    __import__(name, globals, locals, fromlist, level)
    if name in [{safe_imports}] else
    (_ for _ in ()).throw(ImportError(f"Import '{{name}}' is not allowed"))
)
"""

        # Resource monitoring wrapper
        resource_wrapper = """
# Resource monitoring wrapper
import sys
import time
import tracemalloc

start_time = time.time()
tracemalloc.start()

# Override potentially dangerous functions
def safe_input(prompt=""):
    return ""  # Disable input for security

def safe_exec(*args, **kwargs):
    raise RuntimeError("exec() is disabled for security")

def safe_eval(*args, **kwargs):
    raise RuntimeError("eval() is disabled for security")

# Replace dangerous built-ins
if 'input' in __builtins__:
    __builtins__['input'] = safe_input
if 'exec' in __builtins__:
    __builtins__['exec'] = safe_exec
if 'eval' in __builtins__:
    __builtins__['eval'] = safe_eval

# User code starts here
"""

        # Combine wrapper with user code
        safe_code = f"""
{import_restrictions}
{resource_wrapper}
# ===== USER CODE =====
{code}
# ===== END USER CODE =====

# Execution summary
execution_time = time.time() - start_time
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"EXECUTION_METRICS: time={{execution_time:.3f}},memory={{peak/1024/1024:.2f}}MB")
"""

        return safe_code

    async def _analyze_execution_results(self, execution_result: ExecutionResult) -> List[SecurityViolation]:
        """Analyze execution results for additional security violations."""
        violations = []

        # Check for suspicious output
        suspicious_patterns = [r"password", r"secret", r"token", r"api_key", r"private_key"]

        output_text = execution_result.stdout + execution_result.stderr
        for pattern in suspicious_patterns:
            if re.search(pattern, output_text, re.IGNORECASE):
                violations.append(
                    SecurityViolation(
                        violation_type=SecurityViolationType.SUSPICIOUS_PATTERNS,
                        severity="medium",
                        description=f"Suspicious content in output: {pattern}",
                    )
                )

        return violations

    async def _log_execution(self, code: str, result: ExecutionResult):
        """Log execution for audit purposes."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "safety_level": self.safety_level.value,
            "code_length": len(code),
            "success": result.success,
            "execution_time": result.execution_time,
            "memory_used": result.memory_used_mb,
            "violations_count": len(result.violations),
            "terminated_early": result.terminated_early,
            "critical_violations": len([v for v in result.violations if v.severity == "critical"]),
        }

        self.audit_log.append(log_entry)

        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

    async def _safe_cleanup_directory(self, directory: Path):
        """Safely clean up a directory."""
        try:
            import shutil

            shutil.rmtree(directory)
            logging.debug(f"Cleaned up directory: {directory}")
        except Exception as e:
            logging.warning(f"Failed to cleanup directory {directory}: {e}")

    async def validate_file_safety(self, file_path: Path) -> List[SecurityViolation]:
        """Validate a file for safety before processing."""
        violations = []

        try:
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > 50 * 1024 * 1024:  # 50MB limit
                violations.append(
                    SecurityViolation(
                        violation_type=SecurityViolationType.RESOURCE_EXHAUSTION,
                        severity="medium",
                        description=f"File too large: {file_size} bytes",
                    )
                )

            # Check file extension
            dangerous_extensions = [".exe", ".bat", ".cmd", ".sh", ".ps1", ".scr"]
            if file_path.suffix.lower() in dangerous_extensions:
                violations.append(
                    SecurityViolation(
                        violation_type=SecurityViolationType.SUSPICIOUS_PATTERNS,
                        severity="high",
                        description=f"Dangerous file extension: {file_path.suffix}",
                    )
                )

            # Scan file content
            if file_path.suffix.lower() in [".py", ".js", ".ts", ".jsx", ".tsx"]:
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    content_violations = await self._scan_code_for_violations(content)
                    violations.extend(content_violations)
                except Exception as e:
                    logging.warning(f"Failed to scan file content {file_path}: {e}")

        except Exception as e:
            logging.warning(f"Failed to validate file safety {file_path}: {e}")

        return violations

    def get_audit_summary(self) -> Dict[str, Any]:
        """Get summary of audit log."""
        if not self.audit_log:
            return {"total_executions": 0}

        total_executions = len(self.audit_log)
        successful_executions = sum(1 for entry in self.audit_log if entry["success"])
        critical_violations = sum(entry["critical_violations"] for entry in self.audit_log)
        avg_execution_time = sum(entry["execution_time"] for entry in self.audit_log) / total_executions

        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": successful_executions / total_executions,
            "critical_violations": critical_violations,
            "average_execution_time": avg_execution_time,
            "safety_level": self.safety_level.value,
            "active_temp_dirs": len(self.temp_dirs),
            "active_processes": len(self.active_processes),
        }

    async def cleanup_all(self):
        """Clean up all resources."""
        logging.info("Starting comprehensive cleanup")

        # Kill all active processes
        for process in self.active_processes:
            try:
                process.terminate()
                await asyncio.sleep(1)  # Give it time to terminate
                if process.is_alive():
                    process.kill()
            except Exception as e:
                logging.warning(f"Failed to terminate process {process}: {e}")

        self.active_processes.clear()

        # Clean up temporary directories
        for temp_dir in self.temp_dirs[:]:
            if temp_dir.exists():
                await self._safe_cleanup_directory(temp_dir)

        self.temp_dirs.clear()

        logging.info("Comprehensive cleanup completed")


class IsolatedEnvironment:
    """Represents an isolated execution environment."""

    def __init__(self, temp_dir: Path, process_monitor: "ProcessMonitor", safety_system: VirtualEnvironmentSafety):
        self.temp_dir = temp_dir
        self.process_monitor = process_monitor
        self.safety_system = safety_system

    async def execute_python_code(self, code: str) -> ExecutionResult:
        """Execute Python code in the isolated environment."""
        # Write code to temporary file
        code_file = self.temp_dir / "user_code.py"
        code_file.write_text(code, encoding="utf-8")

        # Prepare execution command
        cmd = [sys.executable, str(code_file)]

        # Execute with monitoring
        result = await self.process_monitor.execute_with_monitoring(cmd, cwd=str(self.temp_dir))

        return result


class ProcessMonitor:
    """Monitor and control process execution."""

    def __init__(self, resource_limits: ResourceLimits):
        self.resource_limits = resource_limits
        self.monitored_processes = []

    async def execute_with_monitoring(self, cmd: List[str], cwd: Optional[str] = None) -> ExecutionResult:
        """Execute command with resource monitoring."""
        start_time = time.time()

        try:
            # Start process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                preexec_fn=os.setsid if os.name != "nt" else None,  # Create new process group
            )

            self.monitored_processes.append(process)

            # Monitor execution
            stdout, stderr = await self._monitor_process_execution(process)

            # Get resource usage
            try:
                process_info = psutil.Process(process.pid)
                memory_mb = process_info.memory_info().rss / 1024 / 1024
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                memory_mb = 0

            execution_time = time.time() - start_time

            return ExecutionResult(
                success=process.returncode == 0,
                stdout=stdout.decode("utf-8", errors="ignore"),
                stderr=stderr.decode("utf-8", errors="ignore"),
                exit_code=process.returncode,
                execution_time=execution_time,
                memory_used_mb=memory_mb,
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=1,
                execution_time=time.time() - start_time,
                memory_used_mb=0,
            )

    async def _monitor_process_execution(self, process: asyncio.subprocess.Process) -> tuple[bytes, bytes]:
        """Monitor process execution with resource limits."""
        try:
            # Wait for process with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=self.resource_limits.max_wall_time_seconds
            )
            return stdout, stderr

        except asyncio.TimeoutError:
            # Process exceeded time limit
            logging.warning(f"Process {process.pid} exceeded time limit, terminating")
            self._terminate_process_tree(process)
            return b"", b"Execution terminated due to time limit"

    def _terminate_process_tree(self, process: asyncio.subprocess.Process):
        """Terminate entire process tree."""
        try:
            if os.name != "nt":
                # Unix-like systems: kill process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                # Windows: terminate process
                process.terminate()
                process.wait(timeout=5)
        except Exception as e:
            logging.warning(f"Failed to terminate process {process.pid}: {e}")

    async def cleanup(self):
        """Clean up monitored processes."""
        for process in self.monitored_processes:
            try:
                if process.returncode is None:  # Still running
                    self._terminate_process_tree(process)
            except Exception as e:
                logging.warning(f"Failed to cleanup process {process.pid}: {e}")

        self.monitored_processes.clear()


# Export main classes
__all__ = [
    "VirtualEnvironmentSafety",
    "SafetyLevel",
    "SecurityViolationType",
    "ResourceLimits",
    "SecurityViolation",
    "ExecutionResult",
]
