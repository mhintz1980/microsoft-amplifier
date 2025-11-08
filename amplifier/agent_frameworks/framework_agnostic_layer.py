#!/usr/bin/env python3
"""
Framework-Agnostic Agent Layer

Unified interfaces and universal adapters that work across all frameworks.
Provides consistent APIs regardless of the underlying framework implementation.

Embodying amplifier philosophy:
- Single clear contract for all framework interactions
- Independent and replaceable framework implementations
- Modular design with "bricks & studs" architecture
- Ruthless simplicity in universal interfaces
"""

import asyncio
import json
from abc import ABC
from abc import abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from amplifier.utils.logger import get_logger

logger = get_logger(__name__)


class CapabilityType(Enum):
    """Agent capability types."""

    TEXT_GENERATION = "text_generation"
    TOOL_USE = "tool_use"
    REASONING = "reasoning"
    MULTI_MODAL = "multi_modal"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    COLLABORATION = "collaboration"


class TaskType(Enum):
    """Types of tasks agents can perform."""

    QUESTION_ANSWERING = "question_answering"
    DESIGN_REVIEW = "design_review"
    SAFETY_ANALYSIS = "safety_analysis"
    MANUFACTURING_ASSESSMENT = "manufacturing_assessment"
    QUALITY_INSPECTION = "quality_inspection"
    COST_ESTIMATION = "cost_estimation"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    PROCESS_OPTIMIZATION = "process_optimization"


@dataclass
class TaskDefinition:
    """Definition of a task for an agent."""

    task_type: TaskType
    description: str
    requirements: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    expected_output: str | None = None
    domain_context: dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"  # low, normal, high, critical
    deadline: datetime | None = None


@dataclass
class TaskResult:
    """Result of task execution."""

    task_id: str
    success: bool
    output: str | None = None
    confidence: float = 0.0
    execution_time: float = 0.0
    tool_usage: list[str] = field(default_factory=list)
    reasoning_steps: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    quality_metrics: dict[str, float] = field(default_factory=list)


@dataclass
class AgentCapabilities:
    """Capabilities that an agent provides."""

    supported_tasks: list[TaskType]
    capabilities: list[CapabilityType]
    max_input_length: int
    max_output_length: int
    supported_formats: list[str]
    specialized_domains: list[str]
    performance_characteristics: dict[str, Any] = field(default_factory=dict)


class UniversalAgentInterface(ABC):
    """Universal interface that all framework agents must implement."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.capabilities: AgentCapabilities | None = None
        self.is_initialized = False

    @abstractmethod
    async def initialize(self, config: dict[str, Any]) -> bool:
        """Initialize the agent with configuration."""
        pass

    @abstractmethod
    async def execute_task(self, task: TaskDefinition) -> TaskResult:
        """Execute a task and return results."""
        pass

    @abstractmethod
    async def stream_execute_task(self, task: TaskDefinition) -> AsyncGenerator[dict[str, Any], None]:
        """Execute task with streaming results."""
        pass

    @abstractmethod
    def get_capabilities(self) -> AgentCapabilities:
        """Get agent capabilities."""
        pass

    @abstractmethod
    async def update_configuration(self, config: dict[str, Any]) -> bool:
        """Update agent configuration."""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Perform health check."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup agent resources."""
        pass


class UniversalTaskScheduler:
    """Framework-agnostic task scheduler."""

    def __init__(self):
        self.agents: dict[str, UniversalAgentInterface] = {}
        self.task_queue: list[TaskDefinition] = []
        self.execution_history: list[TaskResult] = []
        self.running = False

    async def register_agent(self, agent: UniversalAgentInterface) -> bool:
        """Register an agent with the scheduler."""
        try:
            # Initialize agent
            success = await agent.initialize({})
            if success:
                self.agents[agent.agent_id] = agent
                logger.info(f"Registered agent: {agent.agent_id}")
                return True
            logger.error(f"Failed to initialize agent: {agent.agent_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to register agent {agent.agent_id}: {e}")
            return False

    async def submit_task(self, task: TaskDefinition, preferred_agent: str | None = None) -> str:
        """Submit a task for execution."""
        task_id = f"task_{len(self.task_queue)}_{datetime.now().timestamp()}"
        task.metadata["task_id"] = task_id
        task.metadata["preferred_agent"] = preferred_agent

        self.task_queue.append(task)
        logger.info(f"Submitted task {task_id}: {task.task_type.value}")
        return task_id

    async def execute_task(self, task: TaskDefinition) -> TaskResult:
        """Execute a single task."""
        # Find suitable agent
        agent = await self._find_suitable_agent(task)
        if not agent:
            return TaskResult(
                task_id=task.metadata.get("task_id", "unknown"),
                success=False,
                errors=["No suitable agent found for task"],
            )

        try:
            result = await agent.execute_task(task)
            self.execution_history.append(result)
            return result
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return TaskResult(task_id=task.metadata.get("task_id", "unknown"), success=False, errors=[str(e)])

    async def _find_suitable_agent(self, task: TaskDefinition) -> UniversalAgentInterface | None:
        """Find an agent suitable for the task."""
        # Check preferred agent first
        preferred = task.metadata.get("preferred_agent")
        if preferred and preferred in self.agents:
            agent = self.agents[preferred]
            if task.task_type in agent.get_capabilities().supported_tasks:
                return agent

        # Find any capable agent
        for agent in self.agents.values():
            capabilities = agent.get_capabilities()
            if task.task_type in capabilities.supported_tasks:
                return agent

        return None

    async def start_scheduler(self):
        """Start the task scheduler."""
        self.running = True
        logger.info("Task scheduler started")

        while self.running:
            if self.task_queue:
                task = self.task_queue.pop(0)
                await self.execute_task(task)
            else:
                await asyncio.sleep(0.1)  # Small delay when no tasks

    async def stop_scheduler(self):
        """Stop the task scheduler."""
        self.running = False
        logger.info("Task scheduler stopped")

    def get_statistics(self) -> dict[str, Any]:
        """Get scheduler statistics."""
        total_tasks = len(self.execution_history)
        successful_tasks = sum(1 for r in self.execution_history if r.success)

        return {
            "total_agents": len(self.agents),
            "queued_tasks": len(self.task_queue),
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
            "average_execution_time": sum(r.execution_time for r in self.execution_history) / total_tasks
            if total_tasks > 0
            else 0,
        }

    async def cleanup(self):
        """Cleanup scheduler resources."""
        await self.stop_scheduler()
        for agent in self.agents.values():
            agent.cleanup()
        self.agents.clear()
        logger.info("Task scheduler cleaned up")


class FrameworkDetector:
    """Detects and manages different framework implementations."""

    def __init__(self):
        self.framework_mappings: dict[str, type[UniversalAgentInterface]] = {}
        self._register_default_frameworks()

    def _register_default_frameworks(self):
        """Register default framework adapters."""
        # These would be imported from the multi-framework integration
        try:
            from .multi_framework_integration import AutoGenAdapter
            from .multi_framework_integration import CrewAIAdapter
            from .multi_framework_integration import LangChainAdapter
            from .multi_framework_integration import OpenAIAdapter

            # Create wrapper classes that implement UniversalAgentInterface
            self.framework_mappings["langchain"] = self._create_wrapper_class(LangChainAdapter)
            self.framework_mappings["openai_sdk"] = self._create_wrapper_class(OpenAIAdapter)
            self.framework_mappings["autogen"] = self._create_wrapper_class(AutoGenAdapter)
            self.framework_mappings["crewai"] = self._create_wrapper_class(CrewAIAdapter)
        except ImportError as e:
            logger.warning(f"Some frameworks not available: {e}")

    def _create_wrapper_class(self, framework_adapter_class):
        """Create a wrapper class that implements UniversalAgentInterface."""

        class FrameworkWrapper(UniversalAgentInterface):
            def __init__(self, agent_id: str):
                super().__init__(agent_id)
                self.framework_adapter = None

            async def initialize(self, config: dict[str, Any]) -> bool:
                """Initialize using framework-specific adapter."""
                try:
                    from .multi_framework_integration import AgentConfig
                    from .multi_framework_integration import FrameworkType

                    # Convert to framework-specific config
                    framework_type = FrameworkType(self.agent_id.split("_")[0])
                    fw_config = AgentConfig(
                        framework=framework_type,
                        agent_type=config.get("agent_type", "default"),
                        model_config=config.get("model_config", {}),
                        tool_config=config.get("tool_config", []),
                    )

                    self.framework_adapter = framework_adapter_class(fw_config)
                    success = await self.framework_adapter.initialize()

                    if success:
                        self.is_initialized = True
                        self.capabilities = self._extract_capabilities()

                    return success

                except Exception as e:
                    logger.error(f"Framework initialization failed: {e}")
                    return False

            async def execute_task(self, task: TaskDefinition) -> TaskResult:
                """Execute task using framework adapter."""
                if not self.framework_adapter:
                    return TaskResult(
                        task_id=task.metadata.get("task_id", "unknown"),
                        success=False,
                        errors=["Framework adapter not initialized"],
                    )

                import time

                start_time = time.time()

                try:
                    # Convert task to input message
                    input_message = self._task_to_message(task)

                    # Execute with framework adapter
                    interaction = await self.framework_adapter.execute(input_message)

                    # Convert interaction to task result
                    return TaskResult(
                        task_id=task.metadata.get("task_id", "unknown"),
                        success=True,
                        output=interaction.output_message,
                        confidence=0.8,  # Mock confidence
                        execution_time=time.time() - start_time,
                        tool_usage=interaction.tools_used,
                        reasoning_steps=interaction.reasoning_steps,
                        metadata=interaction.metadata,
                    )

                except Exception as e:
                    return TaskResult(
                        task_id=task.metadata.get("task_id", "unknown"),
                        success=False,
                        errors=[str(e)],
                        execution_time=time.time() - start_time,
                    )

            async def stream_execute_task(self, task: TaskDefinition) -> AsyncGenerator[dict[str, Any], None]:
                """Execute task with streaming (if supported by framework)."""
                # Basic streaming implementation
                yield {"status": "starting", "progress": 0.0}

                result = await self.execute_task(task)
                yield {"status": "completed", "progress": 1.0, "result": result}

            def get_capabilities(self) -> AgentCapabilities:
                """Get agent capabilities."""
                if self.capabilities:
                    return self.capabilities

                # Return default capabilities
                return AgentCapabilities(
                    supported_tasks=[TaskType.QUESTION_ANSWERING],
                    capabilities=[CapabilityType.TEXT_GENERATION],
                    max_input_length=4000,
                    max_output_length=2000,
                    supported_formats=["text"],
                    specialized_domains=["general"],
                )

            async def update_configuration(self, config: dict[str, Any]) -> bool:
                """Update configuration (framework-specific)."""
                # Implementation depends on framework
                return True

            async def health_check(self) -> dict[str, Any]:
                """Perform health check."""
                return {
                    "status": "healthy" if self.is_initialized else "unhealthy",
                    "framework": self.agent_id.split("_")[0],
                    "capabilities": self.get_capabilities().__dict__,
                }

            def cleanup(self) -> None:
                """Cleanup resources."""
                if self.framework_adapter:
                    self.framework_adapter.cleanup()

            def _task_to_message(self, task: TaskDefinition) -> str:
                """Convert task to input message."""
                message = f"Task: {task.description}\n"
                if task.requirements:
                    message += f"Requirements: {', '.join(task.requirements)}\n"
                if task.constraints:
                    message += f"Constraints: {', '.join(task.constraints)}\n"
                return message

            def _extract_capabilities(self) -> AgentCapabilities:
                """Extract capabilities from framework adapter."""
                # Mock implementation - would extract from actual adapter
                return AgentCapabilities(
                    supported_tasks=[TaskType.QUESTION_ANSWERING, TaskType.DESIGN_REVIEW, TaskType.SAFETY_ANALYSIS],
                    capabilities=[CapabilityType.TEXT_GENERATION, CapabilityType.ANALYSIS, CapabilityType.REASONING],
                    max_input_length=8000,
                    max_output_length=4000,
                    supported_formats=["text", "markdown"],
                    specialized_domains=["mechanical_engineering"],
                )

        return FrameworkWrapper

    def detect_framework(self, config: dict[str, Any]) -> str | None:
        """Detect which framework to use based on configuration."""
        framework_hint = config.get("framework")
        if framework_hint and framework_hint in self.framework_mappings:
            return framework_hint

        # Auto-detect based on configuration keys
        if "langchain" in str(config).lower():
            return "langchain"
        if "openai" in str(config).lower():
            return "openai_sdk"
        if "autogen" in str(config).lower():
            return "autogen"
        if "crewai" in str(config).lower():
            return "crewai"

        return None

    def create_agent(self, framework: str, agent_id: str) -> UniversalAgentInterface | None:
        """Create an agent for the specified framework."""
        if framework not in self.framework_mappings:
            logger.error(f"Unsupported framework: {framework}")
            return None

        wrapper_class = self.framework_mappings[framework]
        return wrapper_class(agent_id)

    def get_available_frameworks(self) -> list[str]:
        """Get list of available frameworks."""
        return list(self.framework_mappings.keys())


class UniversalTrainingInterface:
    """Universal interface for Agent Lightning training integration."""

    def __init__(self, scheduler: UniversalTaskScheduler):
        self.scheduler = scheduler
        self.training_data: list[dict[str, Any]] = []

    async def collect_training_data(
        self, tasks: list[TaskDefinition], framework_filter: str | None = None
    ) -> list[dict[str, Any]]:
        """Collect training data from task executions."""
        training_data = []

        for task in tasks:
            # Set preferred framework if specified
            if framework_filter:
                task.metadata["preferred_agent"] = f"{framework_filter}_agent"

            # Execute task
            result = await self.scheduler.execute_task(task)

            # Convert to training format
            if result.success:
                training_item = self._convert_to_training_format(task, result)
                training_data.append(training_item)

        self.training_data.extend(training_data)
        return training_data

    def _convert_to_training_format(self, task: TaskDefinition, result: TaskResult) -> dict[str, Any]:
        """Convert task and result to Agent Lightning training format."""
        return {
            "task_id": result.task_id,
            "task_type": task.task_type.value,
            "input_features": self._extract_input_features(task),
            "output_features": self._extract_output_features(result),
            "performance_metrics": {
                "success": result.success,
                "confidence": result.confidence,
                "execution_time": result.execution_time,
                "quality_scores": result.quality_metrics,
            },
            "interaction_data": {
                "tool_usage": result.tool_usage,
                "reasoning_steps": result.reasoning_steps,
                "error_count": len(result.errors),
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "framework": result.metadata.get("framework", "unknown"),
                "domain": task.domain_context.get("domain", "general"),
            },
        }

    def _extract_input_features(self, task: TaskDefinition) -> list[float]:
        """Extract features from task input."""
        features = [
            len(task.description.split()),  # Description length
            len(task.requirements),  # Number of requirements
            len(task.constraints),  # Number of constraints
            1.0 if task.expected_output else 0.0,  # Has expected output
            {"low": 0.25, "normal": 0.5, "high": 0.75, "critical": 1.0}.get(task.priority, 0.5),
        ]
        return features

    def _extract_output_features(self, result: TaskResult) -> list[float]:
        """Extract features from task result."""
        features = [
            len(result.output.split()) if result.output else 0,  # Output length
            result.confidence,  # Confidence score
            len(result.tool_usage),  # Tool usage count
            len(result.reasoning_steps),  # Reasoning steps
            1.0 if result.success else 0.0,  # Success indicator
        ]
        return features

    def get_training_data(self, clear_buffer: bool = False) -> list[dict[str, Any]]:
        """Get accumulated training data."""
        data = self.training_data.copy()
        if clear_buffer:
            self.training_data.clear()
        return data

    def save_training_data(self, filepath: Path, clear_buffer: bool = True):
        """Save training data to file for Agent Lightning."""
        data = self.get_training_data(clear_buffer)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(data)} training samples to {filepath}")


class UniversalAgentManager:
    """High-level manager for universal agent operations."""

    def __init__(self):
        self.framework_detector = FrameworkDetector()
        self.scheduler = UniversalTaskScheduler()
        self.training_interface = UniversalTrainingInterface(self.scheduler)

    async def initialize_from_config(self, config_file: Path) -> bool:
        """Initialize agents from configuration file."""
        try:
            with open(config_file) as f:
                config = json.load(f)

            # Initialize each agent configuration
            for agent_config in config.get("agents", []):
                framework = agent_config.get("framework")
                agent_id = agent_config.get("id")

                if not framework or not agent_id:
                    logger.warning(f"Invalid agent config: {agent_config}")
                    continue

                agent = self.framework_detector.create_agent(framework, agent_id)
                if agent:
                    success = await self.scheduler.register_agent(agent)
                    if not success:
                        logger.error(f"Failed to register agent: {agent_id}")
                else:
                    logger.error(f"Failed to create agent: {agent_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize from config: {e}")
            return False

    async def add_agent(self, framework: str, config: dict[str, Any]) -> str | None:
        """Add a new agent to the system."""
        agent_id = config.get("id", f"{framework}_agent_{len(self.scheduler.agents)}")

        agent = self.framework_detector.create_agent(framework, agent_id)
        if not agent:
            return None

        success = await self.scheduler.register_agent(agent)
        if success:
            return agent_id
        return None

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "frameworks": {
                "available": self.framework_detector.get_available_frameworks(),
                "registered": len(self.scheduler.agents),
            },
            "scheduler": self.scheduler.get_statistics(),
            "training": {
                "collected_samples": len(self.training_interface.training_data),
                "ready_for_training": len(self.training_interface.training_data) > 0,
            },
        }

    async def start_system(self):
        """Start the universal agent system."""
        await self.scheduler.start_scheduler()
        logger.info("Universal agent system started")

    async def stop_system(self):
        """Stop the universal agent system."""
        await self.scheduler.cleanup()
        logger.info("Universal agent system stopped")

    async def execute_workflow(self, workflow: list[TaskDefinition]) -> list[TaskResult]:
        """Execute a complete workflow of tasks."""
        results = []
        for task in workflow:
            result = await self.scheduler.execute_task(task)
            results.append(result)

            # Stop workflow if critical task fails
            if task.priority == "critical" and not result.success:
                logger.error(f"Critical task failed, stopping workflow: {task.description}")
                break

        return results


# Factory functions for easy usage


async def create_universal_system(frameworks: list[str], configs: list[dict[str, Any]]) -> UniversalAgentManager:
    """Create a universal agent system with specified frameworks."""
    manager = UniversalAgentManager()

    for framework, config in zip(frameworks, configs, strict=False):
        agent_id = await manager.add_agent(framework, config)
        if agent_id:
            logger.info(f"Added {framework} agent: {agent_id}")
        else:
            logger.error(f"Failed to add {framework} agent")

    await manager.start_system()
    return manager


def create_mechanical_engineering_tasks() -> list[TaskDefinition]:
    """Create standard mechanical engineering tasks."""
    return [
        TaskDefinition(
            task_type=TaskType.DESIGN_REVIEW,
            description="Review mechanical design for manufacturing feasibility",
            requirements=["Check tolerances", "Assess material selection", "Evaluate assembly process"],
            domain_context={"domain": "mechanical_engineering", "industry": "automotive"},
        ),
        TaskDefinition(
            task_type=TaskType.SAFETY_ANALYSIS,
            description="Perform safety analysis for pressure vessel design",
            requirements=["Compliance with ASME standards", "Risk assessment", "Safety factor verification"],
            constraints=["Maximum pressure 150 PSI", "Operating temperature -20°C to 200°C"],
            domain_context={"domain": "safety_engineering", "standards": ["ASME", "OSHA"]},
        ),
        TaskDefinition(
            task_type=TaskType.MANUFACTURING_ASSESSMENT,
            description="Assess manufacturing process for complex machined part",
            requirements=["CNC machining evaluation", "Tool selection", "Cost estimation"],
            domain_context={"domain": "manufacturing", "processes": ["CNC", "inspection"]},
        ),
    ]
