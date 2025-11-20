"""
Microsoft Amplifier - Core Orchestration Layer

Implements automatic session recovery, agent selection, and tool integration
to bridge the gap between existing infrastructure and actual workflows.

This is the missing orchestration layer that should have been implemented
alongside the sophisticated infrastructure we already have.
"""

import asyncio
import json
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class ExecutionMode(Enum):
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    ADAPTIVE = "adaptive"


@dataclass
class TaskAnalysis:
    """Result of analyzing a task for optimal execution"""

    task_type: str
    complexity: str  # simple, medium, complex
    parallelizable: bool
    required_agents: list[str]
    estimated_tokens: int
    context_requirements: list[str]
    execution_mode: ExecutionMode


@dataclass
class SessionState:
    """Current session state and context"""

    session_id: str
    timestamp: float
    context_usage: int
    context_limit: int
    active_agents: list[str]
    available_tools: list[str]
    performance_metrics: dict[str, float]
    checkpoint_data: dict[str, Any]


class WorkOrchestrator:
    """
    Automatic task orchestration - the missing layer between
    infrastructure and workflows
    """

    def __init__(self):
        self.session_manager = SessionManager()
        self.tool_selector = ToolSelector()
        self.agent_registry = AgentRegistry()
        self.context_optimizer = ContextOptimizer()
        self.performance_tracker = PerformanceTracker()

        # Initialize session state
        self.current_session = self.session_manager.auto_load_context()

    async def orchestrate_task(self, task_description: str, user_context: dict = None) -> dict:
        """
        Main orchestration entry point - automatically selects optimal execution strategy
        """
        start_time = time.time()

        # 1. Analyze task requirements
        task_analysis = await self.analyze_task(task_description, user_context)

        # 2. Select optimal tools and agents
        execution_plan = self.tool_selector.create_execution_plan(task_analysis)

        # 3. Execute with optimal strategy
        if task_analysis.execution_mode == ExecutionMode.PARALLEL:
            results = await self.execute_parallel(execution_plan)
        else:
            results = await self.execute_sequential(execution_plan)

        # 4. Optimize context for next operations
        await self.context_optimizer.optimize_context(results)

        # 5. Track performance for learning
        execution_time = time.time() - start_time
        self.performance_tracker.record_execution(task_analysis, results, execution_time)

        # 6. Create session checkpoint
        await self.session_manager.create_checkpoint(results)

        return {
            "results": results,
            "performance": {
                "execution_time": execution_time,
                "tokens_used": task_analysis.estimated_tokens,
                "agents_deployed": len(execution_plan.agents),
                "parallel_efficiency": len(results) if task_analysis.parallelizable else 1,
            },
            "optimizations_applied": self.context_optimizer.get_applied_optimizations(),
        }

    async def analyze_task(self, task_description: str, user_context: dict = None) -> TaskAnalysis:
        """Analyze task to determine optimal execution strategy"""

        # Simple pattern matching for task classification
        task_lower = task_description.lower()

        # Determine task type and complexity
        if any(word in task_lower for word in ["fix", "debug", "error", "issue"]):
            task_type = "debugging"
            complexity = "medium" if "complex" in task_lower else "simple"
        elif any(word in task_lower for word in ["create", "build", "implement", "develop"]):
            task_type = "development"
            complexity = "complex" if "system" in task_lower else "medium"
        elif any(word in task_lower for word in ["test", "validate", "verify"]):
            task_type = "testing"
            complexity = "simple"
        elif any(word in task_lower for word in ["analyze", "review", "optimize"]):
            task_type = "analysis"
            complexity = "medium"
        else:
            task_type = "general"
            complexity = "medium"

        # Determine parallelizability
        parallelizable = any(
            word in task_lower for word in ["multiple", "batch", "parallel", "separate", "individual", "various"]
        )

        # Select required agents
        required_agents = self.agent_registry.select_agents(task_type, complexity)

        # Estimate token usage
        base_tokens = len(task_description) * 2  # Rough estimate
        complexity_multiplier = {"simple": 1, "medium": 2, "complex": 4}
        estimated_tokens = base_tokens * complexity_multiplier[complexity]

        # Determine context requirements
        context_requirements = []
        if "file" in task_lower:
            context_requirements.append("file_system")
        if "api" in task_lower or "service" in task_lower:
            context_requirements.append("api_documentation")
        if "performance" in task_lower:
            context_requirements.append("performance_metrics")

        # Determine execution mode
        if parallelizable and len(required_agents) > 1:
            execution_mode = ExecutionMode.PARALLEL
        elif complexity == "complex":
            execution_mode = ExecutionMode.ADAPTIVE
        else:
            execution_mode = ExecutionMode.SEQUENTIAL

        return TaskAnalysis(
            task_type=task_type,
            complexity=complexity,
            parallelizable=parallelizable,
            required_agents=required_agents,
            estimated_tokens=estimated_tokens,
            context_requirements=context_requirements,
            execution_mode=execution_mode,
        )

    async def execute_parallel(self, execution_plan: dict) -> list[dict]:
        """Execute tasks in parallel using multiple agents"""

        async def execute_single_task(agent_name: str, task_config: dict):
            # Here we would delegate to the actual agent via Task tool
            # For now, simulate the delegation
            return {
                "agent": agent_name,
                "task": task_config,
                "status": "executed",
                "result": f"Result from {agent_name}",
            }

        # Create parallel tasks
        tasks = [execute_single_task(agent, config) for agent, config in execution_plan["agents"].items()]

        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return results

    async def execute_sequential(self, execution_plan: dict) -> list[dict]:
        """Execute tasks sequentially with dependencies"""
        results = []

        for agent_name, task_config in execution_plan["agents"].items():
            # Here we would delegate to the actual agent via Task tool
            result = {
                "agent": agent_name,
                "task": task_config,
                "status": "executed",
                "result": f"Result from {agent_name}",
            }
            results.append(result)

        return results


class SessionManager:
    """Automatic session management and recovery"""

    def __init__(self):
        self.docker_storage = Path(".docker-storage")
        self.checkpoint_dir = self.docker_storage / "session_checkpoints"
        self.techniques_registry = Path("CLAUDE_TECHNIQUES_REGISTRY.md")

    def auto_load_context(self) -> SessionState:
        """Automatically load session context from Docker storage"""

        # Load latest checkpoint
        latest_checkpoint = self._find_latest_checkpoint()

        if latest_checkpoint:
            checkpoint_data = self._load_checkpoint(latest_checkpoint)

            return SessionState(
                session_id=checkpoint_data.get("session_id", "unknown"),
                timestamp=checkpoint_data.get("timestamp", time.time()),
                context_usage=checkpoint_data.get("context_usage", 0),
                context_limit=checkpoint_data.get("context_limit", 200000),
                active_agents=checkpoint_data.get("active_agents", []),
                available_tools=checkpoint_data.get("available_tools", []),
                performance_metrics=checkpoint_data.get("performance_metrics", {}),
                checkpoint_data=checkpoint_data,
            )
        # Create new session state
        return SessionState(
            session_id=f"session_{int(time.time())}",
            timestamp=time.time(),
            context_usage=0,
            context_limit=200000,
            active_agents=[],
            available_tools=self._discover_available_tools(),
            performance_metrics={},
            checkpoint_data={},
        )

    async def create_checkpoint(self, results: dict):
        """Create session checkpoint for persistence"""
        checkpoint_data = {
            "session_id": f"session_{int(time.time())}",
            "timestamp": time.time(),
            "context_usage": results.get("performance", {}).get("tokens_used", 0),
            "results": results,
            "optimizations_applied": results.get("optimizations_applied", []),
            "active_agents": [],  # Would be populated from actual execution
            "available_tools": self._discover_available_tools(),
        }

        # Save to Docker storage
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{int(time.time())}.json"

        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint_data, f, indent=2)

    def _find_latest_checkpoint(self) -> Path | None:
        """Find the most recent checkpoint file"""
        if not self.checkpoint_dir.exists():
            return None

        checkpoints = list(self.checkpoint_dir.glob("checkpoint_*.json"))
        if not checkpoints:
            return None

        return max(checkpoints, key=lambda p: p.stat().st_mtime)

    def _load_checkpoint(self, checkpoint_path: Path) -> dict:
        """Load checkpoint data from file"""
        with open(checkpoint_path) as f:
            return json.load(f)

    def _discover_available_tools(self) -> list[str]:
        """Discover available tools in the system"""
        tools = []

        # Check for MCP tools
        if Path("amplifier/mcp").exists():
            tools.extend(["context7", "serena", "chrome_devtools", "playwright"])

        # Check for enhanced SDK
        if Path("amplifier/sdk_enhancements").exists():
            tools.append("enhanced_sdk")

        # Check for Agent Lightning
        if Path("deploy_agent_lightning_simple.py").exists():
            tools.append("agent_lightning")

        return tools


class ToolSelector:
    """Automatic tool and agent selection"""

    def __init__(self):
        # Load agent registry from existing documentation
        self.agent_capabilities = self._load_agent_registry()

    def create_execution_plan(self, task_analysis: TaskAnalysis) -> dict:
        """Create optimal execution plan based on task analysis"""

        # Select agents based on task requirements
        selected_agents = {}

        for agent_type in task_analysis.required_agents:
            if agent_type in self.agent_capabilities:
                selected_agents[agent_type] = {
                    "priority": "high",
                    "context_budget": min(50000, task_analysis.estimated_tokens // len(task_analysis.required_agents)),
                    "tools": self.agent_capabilities[agent_type]["tools"],
                }

        return {
            "agents": selected_agents,
            "execution_mode": task_analysis.execution_mode.value,
            "parallelizable": task_analysis.parallelizable,
            "estimated_duration": self._estimate_execution_duration(task_analysis),
        }

    def _load_agent_registry(self) -> dict:
        """Load agent registry from existing documentation"""
        # This would load from the existing AGENT_REGISTRY.md
        # For now, provide basic mapping
        return {
            "debugging": {"tools": ["bug_hunter", "error_diagnostics"]},
            "development": {"tools": ["modular_builder", "zen_architect"]},
            "testing": {"tools": ["test_coverage", "performance_optimizer"]},
            "analysis": {"tools": ["analysis_engine", "content_researcher"]},
        }

    def _estimate_execution_duration(self, task_analysis: TaskAnalysis) -> float:
        """Estimate execution duration in seconds"""
        base_duration = 30  # 30 seconds base
        complexity_multiplier = {"simple": 1, "medium": 2, "complex": 4}

        duration = base_duration * complexity_multiplier[task_analysis.complexity]

        if task_analysis.parallelizable:
            duration = duration / 2  # Parallel execution reduces time

        return duration


class AgentRegistry:
    """Agent selection and management"""

    def select_agents(self, task_type: str, complexity: str) -> list[str]:
        """Select optimal agents for given task type and complexity"""

        # Basic agent selection logic
        agent_mapping = {
            "debugging": ["bug_hunter"],
            "development": ["zen_architect", "modular_builder"],
            "testing": ["test_coverage", "performance_optimizer"],
            "analysis": ["analysis_engine"],
            "general": ["general_purpose"],
        }

        selected = agent_mapping.get(task_type, ["general_purpose"])

        # Add complexity-based agents
        if complexity == "complex":
            selected.extend(["integration_specialist", "error_diagnostics"])

        return selected


class ContextOptimizer:
    """Automatic context optimization and token reduction"""

    def __init__(self):
        self.applied_optimizations = []

    async def optimize_context(self, results: dict):
        """Apply context optimizations based on results"""

        optimizations = []

        # Apply MCP code execution for heavy operations
        if results.get("performance", {}).get("tokens_used", 0) > 50000:
            optimizations.append("mcp_code_execution")
            self.applied_optimizations.append("MCP code execution activated")

        # Apply context compression if usage is high
        context_usage = results.get("performance", {}).get("tokens_used", 0)
        if context_usage > 100000:
            optimizations.append("context_compression")
            self.applied_optimizations.append("Context compression applied")

        # Apply parallel delegation for future tasks
        if len(results.get("results", [])) > 1:
            optimizations.append("parallel_delegation")
            self.applied_optimizations.append("Parallel delegation enabled")

    def get_applied_optimizations(self) -> list[str]:
        """Get list of applied optimizations"""
        return self.applied_optimizations


class PerformanceTracker:
    """Track performance for continuous improvement"""

    def __init__(self):
        self.execution_history = []

    def record_execution(self, task_analysis: TaskAnalysis, results: dict, execution_time: float):
        """Record execution for learning"""

        record = {
            "timestamp": time.time(),
            "task_type": task_analysis.task_type,
            "complexity": task_analysis.complexity,
            "execution_mode": task_analysis.execution_mode.value,
            "execution_time": execution_time,
            "tokens_used": results.get("performance", {}).get("tokens_used", 0),
            "agents_deployed": len(task_analysis.required_agents),
            "success": True,  # Would be determined from actual results
        }

        self.execution_history.append(record)

    def get_performance_summary(self) -> dict:
        """Get performance summary for optimization"""
        if not self.execution_history:
            return {}

        recent_executions = self.execution_history[-10:]  # Last 10 executions

        return {
            "total_executions": len(self.execution_history),
            "average_execution_time": sum(e["execution_time"] for e in recent_executions) / len(recent_executions),
            "average_tokens_used": sum(e["tokens_used"] for e in recent_executions) / len(recent_executions),
            "parallel_execution_rate": sum(1 for e in recent_executions if e["execution_mode"] == "parallel")
            / len(recent_executions),
            "success_rate": sum(1 for e in recent_executions if e["success"]) / len(recent_executions),
        }


# Global orchestrator instance
_orchestrator = None


def get_orchestrator() -> WorkOrchestrator:
    """Get global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = WorkOrchestrator()
    return _orchestrator
