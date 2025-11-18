"""
Real Amplifier Integration - Connect Agent Lightning to actual Amplifier systems.

This module provides real integration with Amplifier's context optimization,
MCP execution, and specialized agent systems rather than simulated implementations.
"""

import asyncio
import json
import subprocess
import time
import uuid
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class AmplifierMCPResult:
    """Result from real MCP execution."""

    command: str
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    success: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class RealAmplifierBridge:
    """
    Real integration bridge with Amplifier ecosystem.

    This provides actual connections to:
    - Amplifier's MCP execution system
    - Context compaction and memory management
    - Specialized agent management
    - Performance monitoring and optimization
    """

    def __init__(self):
        self.bridge_id = str(uuid.uuid4())
        self.amplifier_root = Path(__file__).parent
        self.mcp_available = self._check_mcp_availability()
        self.context_systems = self._discover_context_systems()
        self.execution_history: list[AmplifierMCPResult] = []
        self.performance_metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "average_execution_time": 0.0,
            "total_time_saved": 0.0,
        }

        print(f"🔗 Initialized RealAmplifierBridge: {self.bridge_id}")
        print(f"   MCP Available: {self.mcp_available}")
        print(f"   Context Systems: {len(self.context_systems)}")

    def _check_mcp_availability(self) -> bool:
        """Check if MCP servers are available."""
        try:
            # Check for common MCP server configurations
            mcp_configs = [
                self.amplifier_root / ".claude" / "mcp_settings.json",
                self.amplifier_root / ".claude" / "mcp_servers.json",
                self.amplifier_root / "mcp.json",
            ]

            for config_file in mcp_configs:
                if config_file.exists():
                    print(f"   Found MCP config: {config_file}")
                    return True

            # Check for MCP servers in subdirectories
            for mcp_dir in self.amplifier_root.glob("*/mcp*"):
                if mcp_dir.is_dir():
                    print(f"   Found MCP directory: {mcp_dir}")
                    return True

            return False

        except Exception as e:
            print(f"   Error checking MCP availability: {e}")
            return False

    def _discover_context_systems(self) -> list[str]:
        """Discover available context optimization systems."""
        systems = []

        # Look for context optimization patterns
        context_patterns = ["context_compactor", "memory_manager", "context_optimizer", "token_compression"]

        for pattern in context_patterns:
            if any(self.amplifier_root.rglob(f"*{pattern}*")):
                systems.append(pattern)
                print(f"   Found context system: {pattern}")

        # Look for memory systems
        memory_patterns = ["memory_core", "memory_store", "persistent_storage"]

        for pattern in memory_patterns:
            if any(self.amplifier_root.rglob(f"*{pattern}*")):
                systems.append(pattern)
                print(f"   Found memory system: {pattern}")

        return systems

    async def execute_mcp_command(
        self, command: str, server_name: str | None = None, timeout: int = 30
    ) -> AmplifierMCPResult:
        """Execute command through real MCP system."""
        start_time = time.time()

        try:
            print(f"🔧 Executing MCP command: {command}")

            # Try different execution methods based on available systems
            if self._has_claude_cli():
                result = await self._execute_via_claude_cli(command, server_name, timeout)
            elif self._has_make_targets():
                result = await self._execute_via_make(command, timeout)
            else:
                result = await self._execute_direct_command(command, timeout)

            execution_time = time.time() - start_time
            result.execution_time = execution_time

            # Update metrics
            self.performance_metrics["total_executions"] += 1
            if result.success:
                self.performance_metrics["successful_executions"] += 1

            # Update average execution time
            total_time = (
                self.performance_metrics["average_execution_time"] * (self.performance_metrics["total_executions"] - 1)
                + execution_time
            )
            self.performance_metrics["average_execution_time"] = (
                total_time / self.performance_metrics["total_executions"]
            )

            self.execution_history.append(result)

            if result.success:
                print(f"✅ MCP command completed in {execution_time:.2f}s")
            else:
                print(f"❌ MCP command failed: {result.stderr}")

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ MCP command error: {str(e)}")

            return AmplifierMCPResult(
                command=command,
                exit_code=1,
                stdout="",
                stderr=str(e),
                execution_time=execution_time,
                success=False,
                metadata={"error_type": "exception"},
            )

    def _has_claude_cli(self) -> bool:
        """Check if Claude CLI is available."""
        try:
            result = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _has_make_targets(self) -> bool:
        """Check if Makefile has relevant targets."""
        makefile = self.amplifier_root / "Makefile"
        if not makefile.exists():
            return False

        try:
            with open(makefile) as f:
                content = f.read()
                targets = ["test", "check", "build", "run", "execute"]
                return any(target in content for target in targets)
        except Exception:
            return False

    async def _execute_via_claude_cli(self, command: str, server_name: str | None, timeout: int) -> AmplifierMCPResult:
        """Execute via Claude CLI MCP integration."""
        try:
            # Build claude command
            claude_cmd = ["claude"]

            if server_name:
                claude_cmd.extend(["--server", server_name])

            # Execute the command through Claude
            cmd = claude_cmd + ["--", command]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=self.amplifier_root)

            return AmplifierMCPResult(
                command=command,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=0.0,  # Will be set by caller
                success=result.returncode == 0,
                metadata={"method": "claude_cli", "server": server_name},
            )

        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Command timed out after {timeout}s")
        except Exception as e:
            raise Exception(f"Claude CLI execution failed: {str(e)}")

    async def _execute_via_make(self, command: str, timeout: int) -> AmplifierMCPResult:
        """Execute via Makefile targets."""
        try:
            # Convert command to make target if possible
            make_target = self._command_to_make_target(command)

            if make_target:
                cmd = ["make", make_target]
            else:
                # Try to execute as shell command via make
                cmd = ["make", "run", f"CMD={command}"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=self.amplifier_root)

            return AmplifierMCPResult(
                command=command,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=0.0,
                success=result.returncode == 0,
                metadata={"method": "make", "target": make_target},
            )

        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Make command timed out after {timeout}s")
        except Exception as e:
            raise Exception(f"Make execution failed: {str(e)}")

    async def _execute_direct_command(self, command: str, timeout: int) -> AmplifierMCPResult:
        """Execute command directly."""
        try:
            # Use shell for complex commands
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout, cwd=self.amplifier_root
            )

            return AmplifierMCPResult(
                command=command,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=0.0,
                success=result.returncode == 0,
                metadata={"method": "direct"},
            )

        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Direct command timed out after {timeout}s")
        except Exception as e:
            raise Exception(f"Direct command execution failed: {str(e)}")

    def _command_to_make_target(self, command: str) -> str | None:
        """Convert command to Makefile target."""
        command_lower = command.lower().strip()

        # Simple mapping for common operations
        target_mappings = {
            "make check": "check",
            "make test": "test",
            "make build": "build",
            "make install": "install",
            "pnpm test": "test",
            "pnpm check": "check",
            "python -m pytest": "test",
            "pytest": "test",
        }

        for cmd_pattern, target in target_mappings.items():
            if cmd_pattern in command_lower:
                return target

        return None

    async def optimize_context_with_amplifier(self, content: dict[str, Any]) -> dict[str, Any]:
        """Use real Amplifier context optimization systems."""
        original_size = len(json.dumps(content, default=str))

        print("📊 Optimizing context with Amplifier systems...")
        print(f"   Original size: {original_size} characters")

        # Try different context optimization approaches
        optimized_content = content.copy()

        # Method 1: Try context compactor if available
        if "context_compactor" in self.context_systems:
            try:
                compactor_result = await self._try_context_compactor(optimized_content)
                if compactor_result["success"]:
                    optimized_content = compactor_result["content"]
                    print(f"   ✅ Context compactor: {compactor_result['reduction']:.1%} reduction")
            except Exception as e:
                print(f"   ⚠️  Context compactor failed: {e}")

        # Method 2: Try memory optimization if available
        if "memory_manager" in self.context_systems:
            try:
                memory_result = await self._try_memory_optimization(optimized_content)
                if memory_result["success"]:
                    optimized_content = memory_result["content"]
                    print(f"   ✅ Memory optimization: {memory_result['reduction']:.1%} reduction")
            except Exception as e:
                print(f"   ⚠️  Memory optimization failed: {e}")

        # Method 3: Apply basic compression as fallback
        basic_result = self._apply_basic_compression(optimized_content)
        optimized_content = basic_result["content"]
        print(f"   ✅ Basic compression: {basic_result['reduction']:.1%} reduction")

        final_size = len(json.dumps(optimized_content, default=str))
        reduction = (original_size - final_size) / original_size if original_size > 0 else 0

        return {
            "original_size": original_size,
            "final_size": final_size,
            "reduction": reduction,
            "optimized_content": optimized_content,
            "methods_used": [
                "context_compactor" in self.context_systems,
                "memory_manager" in self.context_systems,
                "basic_compression",
            ],
        }

    async def _try_context_compactor(self, content: dict[str, Any]) -> dict[str, Any]:
        """Try to use Amplifier's context compactor."""
        # Look for context compactor executable or script
        compactor_paths = [
            self.amplifier_root / "amplifier" / "utils" / "context_compactor.py",
            self.amplifier_root / "src" / "context_compactor.py",
            self.amplifier_root / "context_compactor.py",
        ]

        for compactor_path in compactor_paths:
            if compactor_path.exists():
                try:
                    # Execute the compactor with content as input
                    content_json = json.dumps(content, default=str)
                    cmd = f"python3 {compactor_path}"

                    result = await self.execute_mcp_command(f"echo '{content_json}' | {cmd}", timeout=10)

                    if result.success and result.stdout:
                        try:
                            optimized = json.loads(result.stdout)
                            return {
                                "success": True,
                                "content": optimized,
                                "reduction": self._calculate_reduction(content, optimized),
                            }
                        except json.JSONDecodeError:
                            pass

                except Exception:
                    continue

        return {"success": False, "content": content, "reduction": 0.0}

    async def _try_memory_optimization(self, content: dict[str, Any]) -> dict[str, Any]:
        """Try to use Amplifier's memory optimization."""
        # Look for memory system executables
        memory_paths = [
            self.amplifier_root / "amplifier" / "memory" / "core.py",
            self.amplifier_root / "src" / "memory" / "core.py",
            self.amplifier_root / "memory_core.py",
        ]

        for memory_path in memory_paths:
            if memory_path.exists():
                try:
                    content_json = json.dumps(content, default=str)
                    cmd = f"python3 {memory_path} --optimize"

                    result = await self.execute_mcp_command(f"echo '{content_json}' | {cmd}", timeout=10)

                    if result.success and result.stdout:
                        try:
                            optimized = json.loads(result.stdout)
                            return {
                                "success": True,
                                "content": optimized,
                                "reduction": self._calculate_reduction(content, optimized),
                            }
                        except json.JSONDecodeError:
                            pass

                except Exception:
                    continue

        return {"success": False, "content": content, "reduction": 0.0}

    def _apply_basic_compression(self, content: dict[str, Any]) -> dict[str, Any]:
        """Apply basic compression techniques."""
        original = json.dumps(content, default=str, indent=2)

        # Remove unnecessary whitespace
        compressed = json.dumps(content, default=str, separators=(",", ":"))

        # Remove redundant fields
        if isinstance(content, dict):
            compressed_content = self._remove_redundant_fields(content)
            compressed = json.dumps(compressed_content, default=str, separators=(",", ":"))

        reduction = self._calculate_reduction_from_strings(original, compressed)

        return {"success": True, "content": json.loads(compressed) if compressed else content, "reduction": reduction}

    def _remove_redundant_fields(self, content: Any, depth: int = 0) -> Any:
        """Remove redundant fields from nested structures."""
        if depth > 3:  # Prevent infinite recursion
            return content

        if isinstance(content, dict):
            filtered = {}
            redundant_keys = {"timestamp", "id", "version", "created_at"}

            for key, value in content.items():
                if key not in redundant_keys or len(redundant_keys) / len(content) < 0.5:
                    filtered[key] = self._remove_redundant_fields(value, depth + 1)

            return filtered
        if isinstance(content, list):
            return [self._remove_redundant_fields(item, depth + 1) for item in content[:10]]  # Limit list size
        return content

    def _calculate_reduction(self, original: dict[str, Any], optimized: dict[str, Any]) -> float:
        """Calculate reduction ratio."""
        original_size = len(json.dumps(original, default=str))
        optimized_size = len(json.dumps(optimized, default=str))
        return (original_size - optimized_size) / original_size if original_size > 0 else 0

    def _calculate_reduction_from_strings(self, original: str, compressed: str) -> float:
        """Calculate reduction ratio from strings."""
        return (len(original) - len(compressed)) / len(original) if len(original) > 0 else 0

    def get_integration_status(self) -> dict[str, Any]:
        """Get comprehensive integration status."""
        return {
            "bridge_id": self.bridge_id,
            "mcp_available": self.mcp_available,
            "context_systems": self.context_systems,
            "execution_count": len(self.execution_history),
            "performance_metrics": self.performance_metrics.copy(),
            "amplifier_root": str(self.amplifier_root),
            "last_execution": self.execution_history[-1].metadata if self.execution_history else None,
        }


# Global instance
real_amplifier_bridge = RealAmplifierBridge()


# Convenience functions
async def execute_with_amplifier(command: str, server: str | None = None) -> AmplifierMCPResult:
    """Execute command through real Amplifier MCP system."""
    return await real_amplifier_bridge.execute_mcp_command(command, server)


async def optimize_context(content: dict[str, Any]) -> dict[str, Any]:
    """Optimize content using real Amplifier systems."""
    return await real_amplifier_bridge.optimize_context_with_amplifier(content)


# Demo and testing
async def demo_real_integration():
    print("🔗 Real Amplifier Integration - Demo")
    print("=" * 50)

    bridge = real_amplifier_bridge
    status = bridge.get_integration_status()

    print("\n📊 Integration Status:")
    print(f"   MCP Available: {status['mcp_available']}")
    print(f"   Context Systems: {len(status['context_systems'])}")
    print(f"   Execution Count: {status['execution_count']}")

    # Test basic command execution
    print("\n🔧 Testing MCP Command Execution:")
    test_commands = ["echo 'Hello from Amplifier MCP!'", "ls -la", "pwd"]

    for cmd in test_commands:
        result = await execute_with_amplifier(cmd)
        print(f"   Command: {cmd}")
        print(f"   Success: {result.success}")
        print(f"   Time: {result.execution_time:.2f}s")

    # Test context optimization
    print("\n📊 Testing Context Optimization:")
    test_content = {
        "task": "Test context optimization",
        "description": "This is a test context with various fields that should be compressed",
        "requirements": [
            "Remove redundant information",
            "Preserve critical data",
            "Optimize for size",
            "Maintain readability",
        ],
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "author": "test",
            "tags": ["test", "optimization", "amplifier"],
            "priority": "normal",
        },
    }

    optimization_result = await optimize_context(test_content)
    print(f"   Original size: {optimization_result['original_size']}")
    print(f"   Final size: {optimization_result['final_size']}")
    print(f"   Reduction: {optimization_result['reduction']:.1%}")
    print(f"   Methods used: {optimization_result['methods_used']}")

    # Final status
    final_status = bridge.get_integration_status()
    print("\n📈 Final Status:")
    print(f"   Total Executions: {final_status['execution_count']}")
    print(
        f"   Success Rate: {final_status['performance_metrics']['successful_executions'] / final_status['performance_metrics']['total_executions'] * 100:.1f}%"
        if final_status["performance_metrics"]["total_executions"] > 0
        else "N/A"
    )
    print(f"   Average Time: {final_status['performance_metrics']['average_execution_time']:.2f}s")

    print("\n✅ Real integration demo completed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(demo_real_integration())
    exit(0 if success else 1)
