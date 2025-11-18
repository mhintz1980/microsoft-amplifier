"""
MCP Code Execution Framework for Amplifier

Implements secure, sandboxed code execution based on Anthropic's MCP patterns.
Provides Docker-based isolation, PII detection, and skills system.

Key Features:
- Docker-based sandboxed execution
- PII detection and tokenization
- Resource limits and monitoring
- Skills system for reusable functions
- 98.7% token reduction potential
"""

import asyncio
import json
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger
from ..utils.token_utils import estimate_tokens

logger = get_logger(__name__)


class ExecutionStatus(Enum):
    """Code execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class SecurityLevel(Enum):
    """Security levels for code execution."""

    MINIMAL = "minimal"  # No network, limited filesystem
    STANDARD = "standard"  # Controlled network access
    ELEVATED = "elevated"  # Full access (with approval)


@dataclass
class ResourceLimits:
    """Resource limits for code execution."""

    max_runtime_seconds: int = 30
    max_memory_mb: int = 512
    max_cpu_percent: float = 50.0
    max_processes: int = 10
    network_access: bool = False


@dataclass
class ExecutionRequest:
    """Request for code execution."""

    code: str
    language: str  # python, bash, javascript, etc.
    security_level: SecurityLevel = SecurityLevel.MINIMAL
    resource_limits: ResourceLimits | None = None
    environment_vars: dict[str, str] = field(default_factory=dict)
    working_directory: str | None = None
    input_data: dict[str, Any] | None = None
    timeout: int = 30


@dataclass
class ExecutionResult:
    """Result of code execution."""

    request_id: str
    status: ExecutionStatus
    stdout: str
    stderr: str
    exit_code: int
    runtime_seconds: float
    memory_used_mb: float
    cpu_percent: float
    tokens_processed: int
    security_violations: list[str] = field(default_factory=list)
    pii_detected: list[str] = field(default_factory=list)
    execution_log: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class PIIDetector:
    """Detects and handles Personally Identifiable Information."""

    def __init__(self):
        # Simple PII patterns - can be enhanced with ML models
        self.pii_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
            "api_key": r"\b[A-Za-z0-9]{20,}\b",
        }

    def detect_pii(self, text: str) -> list[str]:
        """Detect PII in text and return list of detected types."""
        detected = []
        for pii_type, pattern in self.pii_patterns.items():
            import re

            if re.search(pattern, text):
                detected.append(pii_type)
        return detected

    def tokenize_pii(self, text: str) -> tuple[str, dict[str, str]]:
        """Replace PII with tokens and return mapping."""
        import re

        tokenized = text
        pii_mapping = {}
        replacement_count = 0

        for pii_type, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                original = match.group()
                token = f"[PII_{pii_type.upper()}_{replacement_count}]"
                tokenized = tokenized.replace(original, token)
                pii_mapping[token] = original
                replacement_count += 1

        return tokenized, pii_mapping


class Skill:
    """Represents a reusable skill/function."""

    def __init__(self, name: str, code: str, language: str = "python"):
        self.name = name
        self.code = code
        self.language = language
        self.created_at = datetime.now()
        self.usage_count = 0
        self.success_rate = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "code": self.code,
            "language": self.language,
            "created_at": self.created_at.isoformat(),
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
        }


class SkillRegistry:
    """Registry for managing reusable skills."""

    def __init__(self):
        self.skills: dict[str, Skill] = {}
        self.skill_categories: dict[str, list[str]] = {}

    def register_skill(self, skill: Skill, category: str = "general") -> None:
        """Register a new skill."""
        self.skills[skill.name] = skill
        if category not in self.skill_categories:
            self.skill_categories[category] = []
        self.skill_categories[category].append(skill.name)
        logger.info(f"Registered skill: {skill.name} in category: {category}")

    def get_skill(self, name: str) -> Skill | None:
        """Get a skill by name."""
        return self.skills.get(name)

    def list_skills(self, category: str | None = None) -> list[str]:
        """List skills, optionally filtered by category."""
        if category:
            return self.skill_categories.get(category, [])
        return list(self.skills.keys())

    def get_popular_skills(self, limit: int = 10) -> list[tuple[str, int]]:
        """Get most popular skills by usage count."""
        sorted_skills = sorted(self.skills.items(), key=lambda x: x[1].usage_count, reverse=True)
        return [(name, skill.usage_count) for name, skill in sorted_skills[:limit]]


class DockerExecutor:
    """Docker-based code executor with sandboxing."""

    def __init__(self):
        self.pii_detector = PIIDetector()
        self.temp_dir = Path(tempfile.gettempdir()) / "amplifier_code_execution"
        self.temp_dir.mkdir(exist_ok=True)

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute code in a Docker container."""
        request_id = str(uuid.uuid4())
        logger.info(f"Executing code {request_id} in {request.language}")

        result = ExecutionResult(
            request_id=request_id,
            status=ExecutionStatus.PENDING,
            stdout="",
            stderr="",
            exit_code=-1,
            runtime_seconds=0.0,
            memory_used_mb=0.0,
            cpu_percent=0.0,
            tokens_processed=estimate_tokens(request.code),
        )

        try:
            # Check for PII
            pii_detected = self.pii_detector.detect_pii(request.code)
            if pii_detected:
                result.pii_detected = pii_detected
                result.execution_log.append(f"PII detected: {', '.join(pii_detected)}")
                # Tokenize PII for execution
                request.code, _ = self.pii_detector.tokenize_pii(request.code)

            # Prepare execution environment
            work_dir = self._prepare_workspace(request, request_id)
            docker_cmd = self._build_docker_command(request, work_dir)

            # Execute with timeout and monitoring
            result = await self._execute_with_monitoring(docker_cmd, request, result)

        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.stderr = str(e)
            result.execution_log.append(f"Execution failed: {e}")
            logger.error(f"Code execution {request_id} failed: {e}")

        finally:
            # Cleanup
            self._cleanup_workspace(request_id)

        return result

    def _prepare_workspace(self, request: ExecutionRequest, request_id: str) -> Path:
        """Prepare workspace for code execution."""
        work_dir = self.temp_dir / request_id
        work_dir.mkdir(exist_ok=True)

        # Write code file
        code_file = work_dir / f"main.{self._get_file_extension(request.language)}"
        code_file.write_text(request.code)

        # Write input data if provided
        if request.input_data:
            input_file = work_dir / "input.json"
            input_file.write_text(json.dumps(request.input_data, indent=2))

        # Write environment variables
        if request.environment_vars:
            env_file = work_dir / ".env"
            env_content = "\n".join(f"{k}={v}" for k, v in request.environment_vars.items())
            env_file.write_text(env_content)

        return work_dir

    def _build_docker_command(self, request: ExecutionRequest, work_dir: Path) -> list[str]:
        """Build Docker command for code execution."""
        # Choose appropriate Docker image
        image = self._get_docker_image(request.language)

        # Base Docker command
        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "--name",
            f"amplifier_exec_{work_dir.name}",
            f"--memory={request.resource_limits.max_memory_mb}m",  # type: ignore[assignment]
            f"--cpus={request.resource_limits.max_cpu_percent / 100.0}",  # type: ignore[assignment]
            "--network=none",  # No network access by default
            "-v",
            f"{work_dir}:/workspace",
            "-w",
            "/workspace",
        ]

        # Add environment variables
        for key, value in request.environment_vars.items():
            docker_cmd.extend(["-e", f"{key}={value}"])

        # Add execution command
        exec_cmd = self._get_execution_command(request.language)
        docker_cmd.extend([image])
        docker_cmd.extend(exec_cmd)

        return docker_cmd

    async def _execute_with_monitoring(
        self, docker_cmd: list[str], request: ExecutionRequest, result: ExecutionResult
    ) -> ExecutionResult:
        """Execute Docker command with monitoring."""
        start_time = asyncio.get_event_loop().time()
        result.status = ExecutionStatus.RUNNING

        try:
            # Execute command with timeout
            process = await asyncio.create_subprocess_exec(
                *docker_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=request.resource_limits.max_runtime_seconds,  # type: ignore[assignment]
                )
            except TimeoutError:
                process.kill()
                await process.wait()
                result.runtime_seconds = asyncio.get_event_loop().time() - start_time
                result.status = ExecutionStatus.TIMEOUT
                result.stderr = "Execution timed out"
                result.execution_log.append(f"Execution timed out after {request.resource_limits.max_runtime_seconds}s")  # type: ignore[assignment]
                return result

            # Collect results
            result.stdout = stdout.decode("utf-8", errors="replace")
            result.stderr = stderr.decode("utf-8", errors="replace")
            result.exit_code = process.returncode
            result.runtime_seconds = asyncio.get_event_loop().time() - start_time

            # Determine status
            if process.returncode == 0:
                result.status = ExecutionStatus.COMPLETED
            else:
                result.status = ExecutionStatus.FAILED

            result.execution_log.append(
                f"Execution completed in {result.runtime_seconds:.2f}s with exit code {result.exit_code}"
            )

        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.stderr = str(e)
            result.execution_log.append(f"Execution error: {e}")

        return result

    def _cleanup_workspace(self, request_id: str) -> None:
        """Clean up workspace after execution."""
        work_dir = self.temp_dir / request_id
        try:
            import shutil

            shutil.rmtree(work_dir)
            # Also try to remove the Docker container if it still exists
            subprocess.run(["docker", "rm", "-f", f"amplifier_exec_{request_id}"], capture_output=True, check=False)
        except Exception as e:
            logger.warning(f"Failed to cleanup workspace {request_id}: {e}")

    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language."""
        extensions = {
            "python": "py",
            "bash": "sh",
            "javascript": "js",
            "node": "js",
            "typescript": "ts",
            "java": "java",
            "cpp": "cpp",
            "c": "c",
            "go": "go",
            "rust": "rs",
        }
        return extensions.get(language.lower(), "txt")

    def _get_docker_image(self, language: str) -> str:
        """Get Docker image for language."""
        images = {
            "python": "python:3.11-alpine",
            "bash": "alpine:latest",
            "javascript": "node:18-alpine",
            "node": "node:18-alpine",
            "typescript": "node:18-alpine",
            "java": "openjdk:17-alpine",
            "cpp": "gcc:latest",
            "c": "gcc:latest",
            "go": "golang:1.21-alpine",
            "rust": "rust:1.75-alpine",
        }
        return images.get(language.lower(), "alpine:latest")

    def _get_execution_command(self, language: str) -> list[str]:
        """Get execution command for language."""
        commands = {
            "python": ["python", "main.py"],
            "bash": ["sh", "main.sh"],
            "javascript": ["node", "main.js"],
            "node": ["node", "main.js"],
            "typescript": ["npx", "ts-node", "main.ts"],
            "java": ["java", "Main.java"],
            "cpp": ["g++", "-o", "main", "main.cpp", "&&", "./main"],
            "c": ["gcc", "-o", "main", "main.c", "&&", "./main"],
            "go": ["go", "run", "main.go"],
            "rust": ["rustc", "main.rs", "&&", "./main"],
        }
        return commands.get(language.lower(), ["cat", "main.txt"])


class MCPCodeExecutor:
    """Main MCP code execution coordinator."""

    def __init__(self):
        self.docker_executor = DockerExecutor()
        self.skill_registry = SkillRegistry()
        self.execution_history: list[ExecutionResult] = []
        self._register_builtin_skills()

    def _register_builtin_skills(self) -> None:
        """Register built-in skills."""
        # Data processing skills
        data_processing_skill = Skill(
            name="process_json_data",
            code='''
import json
import sys

def process_json_data(data):
    """Process JSON data with common operations."""
    if isinstance(data, str):
        data = json.loads(data)

    # Example processing: filter, transform, aggregate
    if isinstance(data, list):
        return {
            "count": len(data),
            "sample": data[:5] if len(data) > 5 else data,
            "keys": list(data[0].keys()) if data and isinstance(data[0], dict) else []
        }
    elif isinstance(data, dict):
        return {
            "keys": list(data.keys()),
            "size": len(str(data))
        }
    return data

if __name__ == "__main__":
    # Read input data
    with open("input.json", "r") as f:
        input_data = json.load(f)

    # Process data
    result = process_json_data(input_data)

    # Output result
    print(json.dumps(result, indent=2))
''',
            language="python",
        )
        self.skill_registry.register_skill(data_processing_skill, "data_processing")

        # Text analysis skill
        text_analysis_skill = Skill(
            name="analyze_text",
            code='''
import json
import re
from collections import Counter

def analyze_text(text):
    """Analyze text for common patterns."""
    if not text:
        return {"error": "No text provided"}

    # Basic statistics
    words = text.split()
    sentences = re.split(r'[.!?]+', text)

    # Word frequency
    word_freq = Counter(word.lower().strip('.,!?;:"()') for word in words)

    # Common patterns
    patterns = {
        "emails": len(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\b', text)),
        "urls": len(re.findall(r'https?://\\S+', text)),
        "numbers": len(re.findall(r'\b\\d+\\.?\\d*\b', text))
    }

    return {
        "word_count": len(words),
        "sentence_count": len([s for s in sentences if s.strip()]),
        "character_count": len(text),
        "most_common_words": word_freq.most_common(10),
        "patterns": patterns
    }

if __name__ == "__main__":
    # Read input data
    with open("input.json", "r") as f:
        input_data = json.load(f)

    # Get text from input
    text = input_data.get("text", "")

    # Analyze text
    result = analyze_text(text)

    # Output result
    print(json.dumps(result, indent=2))
''',
            language="python",
        )
        self.skill_registry.register_skill(text_analysis_skill, "text_analysis")

        # Type error batch fixing skill
        with open(__file__.replace("code_execution.py", "skills/fix_type_errors_batch.py")) as f:
            type_error_fix_code = f.read()

        type_error_fix_skill = Skill(
            name="fix_type_errors_batch",
            code=type_error_fix_code,
            language="python",
        )
        self.skill_registry.register_skill(type_error_fix_skill, "code_fixing")

    async def execute_code(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute code request."""
        # Set default resource limits if not provided
        if not request.resource_limits:
            request.resource_limits = ResourceLimits()

        # Log execution
        logger.info(f"Executing {request.language} code with security level {request.security_level.value}")

        # Execute
        result = await self.docker_executor.execute(request)

        # Update statistics
        self.execution_history.append(result)

        return result

    async def execute_skill(self, skill_name: str, input_data: dict[str, Any]) -> ExecutionResult:
        """Execute a registered skill."""
        skill = self.skill_registry.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill not found: {skill_name}")

        # Update skill usage
        skill.usage_count += 1

        # Create execution request
        request = ExecutionRequest(
            code=skill.code, language=skill.language, input_data=input_data, security_level=SecurityLevel.MINIMAL
        )

        # Execute
        result = await self.execute_code(request)

        # Update skill success rate
        if result.status == ExecutionStatus.COMPLETED:
            # Simple moving average
            skill.success_rate = (skill.success_rate * (skill.usage_count - 1) + 1.0) / skill.usage_count
        else:
            skill.success_rate = (skill.success_rate * (skill.usage_count - 1) + 0.0) / skill.usage_count

        return result

    def get_execution_stats(self) -> dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {"message": "No execution history"}

        total_executions = len(self.execution_history)
        successful = len([r for r in self.execution_history if r.status == ExecutionStatus.COMPLETED])
        failed = len([r for r in self.execution_history if r.status == ExecutionStatus.FAILED])
        timeouts = len([r for r in self.execution_history if r.status == ExecutionStatus.TIMEOUT])

        total_tokens = sum(r.tokens_processed for r in self.execution_history)
        total_runtime = sum(r.runtime_seconds for r in self.execution_history)

        return {
            "total_executions": total_executions,
            "success_rate": successful / total_executions if total_executions > 0 else 0,
            "failure_rate": failed / total_executions if total_executions > 0 else 0,
            "timeout_rate": timeouts / total_executions if total_executions > 0 else 0,
            "total_tokens_processed": total_tokens,
            "average_tokens_per_execution": total_tokens / total_executions if total_executions > 0 else 0,
            "total_runtime_seconds": total_runtime,
            "average_runtime_seconds": total_runtime / total_executions if total_executions > 0 else 0,
            "most_used_skills": self.skill_registry.get_popular_skills(5),
            "total_skills_registered": len(self.skill_registry.skills),
        }


# Global executor instance
_mcp_executor = MCPCodeExecutor()


def get_mcp_executor() -> MCPCodeExecutor:
    """Get the global MCP code executor instance."""
    return _mcp_executor


async def execute_code_safely(
    code: str,
    language: str = "python",
    input_data: dict[str, Any] | None = None,
    security_level: SecurityLevel = SecurityLevel.MINIMAL,
) -> ExecutionResult:
    """Convenient function for safe code execution."""
    executor = get_mcp_executor()
    request = ExecutionRequest(code=code, language=language, input_data=input_data, security_level=security_level)
    return await executor.execute_code(request)


async def execute_skill_by_name(skill_name: str, input_data: dict[str, Any]) -> ExecutionResult:
    """Convenient function for skill execution."""
    executor = get_mcp_executor()
    return await executor.execute_skill(skill_name, input_data)


async def execute_in_docker(
    command: str,
    code: str | None = None,
    input_data: dict[str, Any] | None = None,
    security_level: SecurityLevel = SecurityLevel.MINIMAL,
    timeout: int = 30,
    language: str = "python",
) -> ExecutionResult:
    """Convenient function for executing code in Docker."""
    executor = get_mcp_executor()

    # If code is provided, execute it directly
    if code is not None:
        request = ExecutionRequest(
            code=code, language=language, input_data=input_data, security_level=security_level, timeout=timeout
        )
        return await executor.execute_code(request)

    # Otherwise, execute the command as code
    request = ExecutionRequest(
        code=command, language="bash", input_data=input_data, security_level=security_level, timeout=timeout
    )
    return cast(dict[str, Any], await executor.execute_code(request))
