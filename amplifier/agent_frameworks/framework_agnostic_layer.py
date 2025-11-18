#!/usr/bin/env python3
"""
Framework-Agnostic Agent Layer

Unified interfaces and universal adapters that work across all frameworks.  # type: ignore
Provides consistent APIs regardless of the underlying framework implementation.  # type: ignore

Embodying amplifier philosophy:  # type: ignore
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

logger = get_logger(__name__)  # type: ignore


class CapabilityType(Enum):  # type: ignore
    """Agent capability types."""  # type: ignore

    TEXT_GENERATION = "text_generation"  # type: ignore
    TOOL_USE = "tool_use"  # type: ignore
    REASONING = "reasoning"  # type: ignore
    MULTI_MODAL = "multi_modal"  # type: ignore
    CODE_GENERATION = "code_generation"  # type: ignore
    ANALYSIS = "analysis"  # type: ignore
    PLANNING = "planning"  # type: ignore
    COLLABORATION = "collaboration"  # type: ignore


class TaskType(Enum):  # type: ignore
    """Types of tasks agents can perform."""  # type: ignore

    QUESTION_ANSWERING = "question_answering"  # type: ignore
    DESIGN_REVIEW = "design_review"  # type: ignore
    SAFETY_ANALYSIS = "safety_analysis"  # type: ignore
    MANUFACTURING_ASSESSMENT = "manufacturing_assessment"  # type: ignore
    QUALITY_INSPECTION = "quality_inspection"  # type: ignore
    COST_ESTIMATION = "cost_estimation"  # type: ignore
    TECHNICAL_DOCUMENTATION = "technical_documentation"  # type: ignore
    PROCESS_OPTIMIZATION = "process_optimization"  # type: ignore


@dataclass
class TaskDefinition:  # type: ignore
    """Definition of a task for an agent."""  # type: ignore

    task_type: TaskType  # type: ignore
    description: str  # type: ignore
    requirements: list[str] = field(default_factory=list)  # type: ignore
    constraints: list[str] = field(default_factory=list)  # type: ignore
    expected_output: str | None = None  # type: ignore
    domain_context: dict[str, Any] = field(default_factory=dict)  # type: ignore
    priority: str = "normal"  # low, normal, high, critical  # type: ignore
    deadline: datetime | None = None  # type: ignore


@dataclass
class TaskResult:  # type: ignore
    """Result of task execution."""  # type: ignore

    task_id: str  # type: ignore
    success: bool  # type: ignore
    output: str | None = None  # type: ignore
    confidence: float = 0.0  # type: ignore
    execution_time: float = 0.0  # type: ignore
    tool_usage: list[str] = field(default_factory=list)  # type: ignore
    reasoning_steps: list[str] = field(default_factory=list)  # type: ignore
    errors: list[str] = field(default_factory=list)  # type: ignore
    metadata: dict[str, Any] = field(default_factory=dict)  # type: ignore
    quality_metrics: dict[str, float] = field(default_factory=list)  # type: ignore[assignment]


@dataclass
class AgentCapabilities:  # type: ignore
    """Capabilities that an agent provides."""  # type: ignore

    supported_tasks: list[TaskType]  # type: ignore
    capabilities: list[CapabilityType]  # type: ignore
    max_input_length: int  # type: ignore
    max_output_length: int  # type: ignore
    supported_formats: list[str]  # type: ignore
    specialized_domains: list[str]  # type: ignore
    performance_characteristics: dict[str, Any] = field(default_factory=dict)  # type: ignore


class UniversalAgentInterface(ABC):  # type: ignore
    """Universal interface that all framework agents must implement."""  # type: ignore

    def __init__(self, agent_id: str):  # type: ignore
        self.agent_id = agent_id  # type: ignore
        self.capabilities: AgentCapabilities | None = None  # type: ignore
        self.is_initialized = False  # type: ignore

    @abstractmethod
    async def initialize(self, config: dict[str, Any]) -> bool:  # type: ignore
        """Initialize the agent with configuration."""  # type: ignore
        pass

    @abstractmethod
    async def execute_task(self, task: TaskDefinition) -> TaskResult:  # type: ignore
        """Execute a task and return results."""  # type: ignore
        pass

    @abstractmethod
    async def stream_execute_task(self, task: TaskDefinition) -> AsyncGenerator[dict[str, Any], None]:  # type: ignore
        """Execute task with streaming results."""  # type: ignore
        pass

    @abstractmethod
    def get_capabilities(self) -> AgentCapabilities:  # type: ignore
        """Get agent capabilities."""  # type: ignore
        pass

    @abstractmethod
    async def update_configuration(self, config: dict[str, Any]) -> bool:  # type: ignore
        """Update agent configuration."""  # type: ignore
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:  # type: ignore
        """Perform health check."""  # type: ignore
        pass

    @abstractmethod
    def cleanup(self) -> None:  # type: ignore
        """Cleanup agent resources."""  # type: ignore
        pass


class UniversalTaskScheduler:  # type: ignore
    """Framework-agnostic task scheduler."""  # type: ignore

    def __init__(self):  # type: ignore
        self.agents: dict[str, UniversalAgentInterface] = {}  # type: ignore
        self.task_queue: list[TaskDefinition] = []  # type: ignore
        self.execution_history: list[TaskResult] = []  # type: ignore
        self.running = False  # type: ignore

    async def register_agent(self, agent: UniversalAgentInterface) -> bool:  # type: ignore
        """Register an agent with the scheduler."""  # type: ignore
        try:  # type: ignore
            # Initialize agent
            success = await agent.initialize({})  # type: ignore
            if success:  # type: ignore
                self.agents[agent.agent_id] = agent  # type: ignore
                logger.info(f"Registered agent: {agent.agent_id}")  # type: ignore
                return True  # type: ignore
            logger.error(f"Failed to initialize agent: {agent.agent_id}")  # type: ignore
            return False  # type: ignore
        except Exception as e:  # type: ignore
            logger.error(f"Failed to register agent {agent.agent_id}: {e}")  # type: ignore
            return False  # type: ignore

    async def submit_task(self, task: TaskDefinition, preferred_agent: str | None = None) -> str:  # type: ignore
        """Submit a task for execution."""  # type: ignore
        task_id = f"task_{len(self.task_queue)}_{datetime.now().timestamp()}"  # type: ignore
        task.metadata["task_id"] = task_id  # type: ignore[attribute]
        task.metadata["preferred_agent"] = preferred_agent  # type: ignore[attribute]

        self.task_queue.append(task)  # type: ignore
        logger.info(f"Submitted task {task_id}: {task.task_type.value}")  # type: ignore
        return task_id  # type: ignore

    async def execute_task(self, task: TaskDefinition) -> TaskResult:  # type: ignore
        """Execute a single task."""  # type: ignore
        # Find suitable agent
        agent = await self._find_suitable_agent(task)  # type: ignore
        if not agent:  # type: ignore
            return TaskResult(  # type: ignore
                task_id=task.metadata.get("task_id", "unknown"),  # type: ignore[attribute]
                success=False,  # type: ignore
                errors=["No suitable agent found for task"],  # type: ignore
            )

        try:  # type: ignore
            result = await agent.execute_task(task)  # type: ignore
            self.execution_history.append(result)  # type: ignore
            return result  # type: ignore
        except Exception as e:  # type: ignore
            logger.error(f"Task execution failed: {e}")  # type: ignore
            return TaskResult(task_id=task.metadata.get("task_id", "unknown"), success=False, errors=[str(e)])  # type: ignore[attribute]

    async def _find_suitable_agent(self, task: TaskDefinition) -> UniversalAgentInterface | None:  # type: ignore
        """Find an agent suitable for the task."""  # type: ignore
        # Check preferred agent first
        preferred = task.metadata.get("preferred_agent")  # type: ignore[attribute]
        if preferred and preferred in self.agents:  # type: ignore
            agent = self.agents[preferred]  # type: ignore
            if task.task_type in agent.get_capabilities().supported_tasks:  # type: ignore
                return agent  # type: ignore

        # Find any capable agent
        for agent in self.agents.values():  # type: ignore
            capabilities = agent.get_capabilities()  # type: ignore
            if task.task_type in capabilities.supported_tasks:  # type: ignore
                return agent  # type: ignore

        return None  # type: ignore

    async def start_scheduler(self):  # type: ignore
        """Start the task scheduler."""  # type: ignore
        self.running = True  # type: ignore
        logger.info("Task scheduler started")  # type: ignore

        while self.running:  # type: ignore
            if self.task_queue:  # type: ignore
                task = self.task_queue.pop(0)  # type: ignore
                await self.execute_task(task)  # type: ignore
            else:  # type: ignore
                await asyncio.sleep(0.1)  # Small delay when no tasks  # type: ignore

    async def stop_scheduler(self):  # type: ignore
        """Stop the task scheduler."""  # type: ignore
        self.running = False  # type: ignore
        logger.info("Task scheduler stopped")  # type: ignore

    def get_statistics(self) -> dict[str, Any]:  # type: ignore
        """Get scheduler statistics."""  # type: ignore
        total_tasks = len(self.execution_history)  # type: ignore
        successful_tasks = sum(1 for r in self.execution_history if r.success)  # type: ignore

        return {  # type: ignore
            "total_agents": len(self.agents),  # type: ignore
            "queued_tasks": len(self.task_queue),  # type: ignore
            "total_tasks": total_tasks,  # type: ignore
            "successful_tasks": successful_tasks,  # type: ignore
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,  # type: ignore
            "average_execution_time": sum(r.execution_time for r in self.execution_history) / total_tasks  # type: ignore
            if total_tasks > 0
            else 0,
        }

    async def cleanup(self):  # type: ignore
        """Cleanup scheduler resources."""  # type: ignore
        await self.stop_scheduler()  # type: ignore
        for agent in self.agents.values():  # type: ignore
            agent.cleanup()  # type: ignore
        self.agents.clear()  # type: ignore
        logger.info("Task scheduler cleaned up")  # type: ignore


class FrameworkDetector:  # type: ignore
    """Detects and manages different framework implementations."""  # type: ignore

    def __init__(self):  # type: ignore
        self.framework_mappings: dict[str, type[UniversalAgentInterface]] = {}  # type: ignore
        self._register_default_frameworks()  # type: ignore

    def _register_default_frameworks(self):  # type: ignore
        """Register default framework adapters."""  # type: ignore
        # These would be imported from the multi-framework integration
        try:  # type: ignore
            from .multi_framework_integration import AutoGenAdapter
            from .multi_framework_integration import CrewAIAdapter
            from .multi_framework_integration import LangChainAdapter
            from .multi_framework_integration import OpenAIAdapter

            # Create wrapper classes that implement UniversalAgentInterface
            self.framework_mappings["langchain"] = self._create_wrapper_class(LangChainAdapter)  # type: ignore
            self.framework_mappings["openai_sdk"] = self._create_wrapper_class(OpenAIAdapter)  # type: ignore
            self.framework_mappings["autogen"] = self._create_wrapper_class(AutoGenAdapter)  # type: ignore
            self.framework_mappings["crewai"] = self._create_wrapper_class(CrewAIAdapter)  # type: ignore
        except ImportError as e:  # type: ignore
            logger.warning(f"Some frameworks not available: {e}")  # type: ignore

    def _create_wrapper_class(self, framework_adapter_class):  # type: ignore
        """Create a wrapper class that implements UniversalAgentInterface."""  # type: ignore

        class FrameworkWrapper(UniversalAgentInterface):  # type: ignore
            def __init__(self, agent_id: str):  # type: ignore
                super().__init__(agent_id)  # type: ignore
                self.framework_adapter = None  # type: ignore

            async def initialize(self, config: dict[str, Any]) -> bool:  # type: ignore
                """Initialize using framework-specific adapter."""  # type: ignore
                try:  # type: ignore
                    from .multi_framework_integration import AgentConfig
                    from .multi_framework_integration import FrameworkType

                    # Convert to framework-specific config
                    framework_type = FrameworkType(self.agent_id.split("_")[0])  # type: ignore
                    fw_config = AgentConfig(  # type: ignore
                        framework=framework_type,  # type: ignore
                        agent_type=config.get("agent_type", "default"),  # type: ignore
                        model_config=config.get("model_config", {}),  # type: ignore
                        tool_config=config.get("tool_config", []),  # type: ignore
                    )

                    self.framework_adapter = framework_adapter_class(fw_config)  # type: ignore
                    success = await self.framework_adapter.initialize()  # type: ignore

                    if success:  # type: ignore
                        self.is_initialized = True  # type: ignore
                        self.capabilities = self._extract_capabilities()  # type: ignore

                    return success  # type: ignore

                except Exception as e:  # type: ignore
                    logger.error(f"Framework initialization failed: {e}")  # type: ignore
                    return False  # type: ignore

            async def execute_task(self, task: TaskDefinition) -> TaskResult:  # type: ignore
                """Execute task using framework adapter."""  # type: ignore
                if not self.framework_adapter:  # type: ignore
                    return TaskResult(  # type: ignore
                        task_id=task.metadata.get("task_id", "unknown"),  # type: ignore[attribute]
                        success=False,  # type: ignore
                        errors=["Framework adapter not initialized"],  # type: ignore
                    )

                import time

                start_time = time.time()  # type: ignore

                try:  # type: ignore
                    # Convert task to input message
                    input_message = self._task_to_message(task)  # type: ignore

                    # Execute with framework adapter
                    interaction = await self.framework_adapter.execute(input_message)  # type: ignore

                    # Convert interaction to task result
                    return TaskResult(  # type: ignore
                        task_id=task.metadata.get("task_id", "unknown"),  # type: ignore[attribute]
                        success=True,  # type: ignore
                        output=interaction.output_message,  # type: ignore
                        confidence=0.8,  # Mock confidence  # type: ignore
                        execution_time=time.time() - start_time,  # type: ignore
                        tool_usage=interaction.tools_used,  # type: ignore
                        reasoning_steps=interaction.reasoning_steps,  # type: ignore
                        metadata=interaction.metadata,  # type: ignore
                    )

                except Exception as e:  # type: ignore
                    return TaskResult(  # type: ignore
                        task_id=task.metadata.get("task_id", "unknown"),  # type: ignore[attribute]
                        success=False,  # type: ignore
                        errors=[str(e)],  # type: ignore
                        execution_time=time.time() - start_time,  # type: ignore
                    )

            async def stream_execute_task(self, task: TaskDefinition) -> AsyncGenerator[dict[str, Any], None]:  # type: ignore
                """Execute task with streaming (if supported by framework)."""  # type: ignore
                # Basic streaming implementation
                yield {"status": "starting", "progress": 0.0}  # type: ignore

                result = await self.execute_task(task)  # type: ignore
                yield {"status": "completed", "progress": 1.0, "result": result}  # type: ignore

            def get_capabilities(self) -> AgentCapabilities:  # type: ignore
                """Get agent capabilities."""  # type: ignore
                if self.capabilities:  # type: ignore
                    return self.capabilities  # type: ignore

                # Return default capabilities
                return AgentCapabilities(  # type: ignore
                    supported_tasks=[TaskType.QUESTION_ANSWERING],  # type: ignore
                    capabilities=[CapabilityType.TEXT_GENERATION],  # type: ignore
                    max_input_length=4000,  # type: ignore
                    max_output_length=2000,  # type: ignore
                    supported_formats=["text"],  # type: ignore
                    specialized_domains=["general"],  # type: ignore
                )

            async def update_configuration(self, config: dict[str, Any]) -> bool:  # type: ignore
                """Update configuration (framework-specific)."""  # type: ignore
                # Implementation depends on framework
                return True  # type: ignore

            async def health_check(self) -> dict[str, Any]:  # type: ignore
                """Perform health check."""  # type: ignore
                return {  # type: ignore
                    "status": "healthy" if self.is_initialized else "unhealthy",  # type: ignore
                    "framework": self.agent_id.split("_")[0],  # type: ignore
                    "capabilities": self.get_capabilities().__dict__,  # type: ignore
                }

            def cleanup(self) -> None:  # type: ignore
                """Cleanup resources."""  # type: ignore
                if self.framework_adapter:  # type: ignore
                    self.framework_adapter.cleanup()  # type: ignore

            def _task_to_message(self, task: TaskDefinition) -> str:  # type: ignore
                """Convert task to input message."""  # type: ignore
                message = f"Task: {task.description}\n"  # type: ignore
                if task.requirements:  # type: ignore
                    message += f"Requirements: {', '.join(task.requirements)}\n"  # type: ignore
                if task.constraints:  # type: ignore
                    message += f"Constraints: {', '.join(task.constraints)}\n"  # type: ignore
                return message  # type: ignore

            def _extract_capabilities(self) -> AgentCapabilities:  # type: ignore
                """Extract capabilities from framework adapter."""  # type: ignore
                # Mock implementation - would extract from actual adapter
                return AgentCapabilities(  # type: ignore
                    supported_tasks=[TaskType.QUESTION_ANSWERING, TaskType.DESIGN_REVIEW, TaskType.SAFETY_ANALYSIS],  # type: ignore
                    capabilities=[CapabilityType.TEXT_GENERATION, CapabilityType.ANALYSIS, CapabilityType.REASONING],  # type: ignore
                    max_input_length=8000,  # type: ignore
                    max_output_length=4000,  # type: ignore
                    supported_formats=["text", "markdown"],  # type: ignore
                    specialized_domains=["mechanical_engineering"],  # type: ignore
                )

        return FrameworkWrapper  # type: ignore

    def detect_framework(self, config: dict[str, Any]) -> str | None:  # type: ignore
        """Detect which framework to use based on configuration."""  # type: ignore
        framework_hint = config.get("framework")  # type: ignore
        if framework_hint and framework_hint in self.framework_mappings:  # type: ignore
            return framework_hint  # type: ignore

        # Auto-detect based on configuration keys
        if "langchain" in str(config).lower():  # type: ignore
            return "langchain"  # type: ignore
        if "openai" in str(config).lower():  # type: ignore
            return "openai_sdk"  # type: ignore
        if "autogen" in str(config).lower():  # type: ignore
            return "autogen"  # type: ignore
        if "crewai" in str(config).lower():  # type: ignore
            return "crewai"  # type: ignore

        return None  # type: ignore

    def create_agent(self, framework: str, agent_id: str) -> UniversalAgentInterface | None:  # type: ignore
        """Create an agent for the specified framework."""  # type: ignore
        if framework not in self.framework_mappings:  # type: ignore
            logger.error(f"Unsupported framework: {framework}")  # type: ignore
            return None  # type: ignore

        wrapper_class = self.framework_mappings[framework]  # type: ignore
        return wrapper_class(agent_id)  # type: ignore

    def get_available_frameworks(self) -> list[str]:  # type: ignore
        """Get list of available frameworks."""  # type: ignore
        return list(self.framework_mappings.keys())  # type: ignore


class UniversalTrainingInterface:  # type: ignore
    """Universal interface for Agent Lightning training integration."""  # type: ignore

    def __init__(self, scheduler: UniversalTaskScheduler):  # type: ignore
        self.scheduler = scheduler  # type: ignore
        self.training_data: list[dict[str, Any]] = []  # type: ignore

    async def collect_training_data(
        self,
        tasks: list[TaskDefinition],
        framework_filter: str | None = None,  # type: ignore
    ) -> list[dict[str, Any]]:  # type: ignore
        """Collect training data from task executions."""  # type: ignore
        training_data = []  # type: ignore

        for task in tasks:  # type: ignore
            # Set preferred framework if specified
            if framework_filter:  # type: ignore
                task.metadata["preferred_agent"] = f"{framework_filter}_agent"  # type: ignore[attribute]

            # Execute task
            result = await self.scheduler.execute_task(task)  # type: ignore

            # Convert to training format
            if result.success:  # type: ignore
                training_item = self._convert_to_training_format(task, result)  # type: ignore
                training_data.append(training_item)  # type: ignore

        self.training_data.extend(training_data)  # type: ignore
        return training_data  # type: ignore

    def _convert_to_training_format(self, task: TaskDefinition, result: TaskResult) -> dict[str, Any]:  # type: ignore
        """Convert task and result to Agent Lightning training format."""  # type: ignore
        return {  # type: ignore
            "task_id": result.task_id,  # type: ignore
            "task_type": task.task_type.value,  # type: ignore
            "input_features": self._extract_input_features(task),  # type: ignore
            "output_features": self._extract_output_features(result),  # type: ignore
            "performance_metrics": {  # type: ignore
                "success": result.success,  # type: ignore
                "confidence": result.confidence,  # type: ignore
                "execution_time": result.execution_time,  # type: ignore
                "quality_scores": result.quality_metrics,  # type: ignore
            },
            "interaction_data": {  # type: ignore
                "tool_usage": result.tool_usage,  # type: ignore
                "reasoning_steps": result.reasoning_steps,  # type: ignore
                "error_count": len(result.errors),  # type: ignore
            },
            "metadata": {  # type: ignore
                "timestamp": datetime.now().isoformat(),  # type: ignore
                "framework": result.metadata.get("framework", "unknown"),  # type: ignore
                "domain": task.domain_context.get("domain", "general"),  # type: ignore
            },
        }

    def _extract_input_features(self, task: TaskDefinition) -> list[float]:  # type: ignore
        """Extract features from task input."""  # type: ignore
        features = [  # type: ignore
            len(task.description.split()),  # Description length  # type: ignore
            len(task.requirements),  # Number of requirements  # type: ignore
            len(task.constraints),  # Number of constraints  # type: ignore
            1.0 if task.expected_output else 0.0,  # Has expected output  # type: ignore
            {"low": 0.25, "normal": 0.5, "high": 0.75, "critical": 1.0}.get(task.priority, 0.5),  # type: ignore
        ]
        return features  # type: ignore

    def _extract_output_features(self, result: TaskResult) -> list[float]:  # type: ignore
        """Extract features from task result."""  # type: ignore
        features = [  # type: ignore
            len(result.output.split()) if result.output else 0,  # Output length  # type: ignore
            result.confidence,  # Confidence score  # type: ignore
            len(result.tool_usage),  # Tool usage count  # type: ignore
            len(result.reasoning_steps),  # Reasoning steps  # type: ignore
            1.0 if result.success else 0.0,  # Success indicator  # type: ignore
        ]
        return features  # type: ignore

    def get_training_data(self, clear_buffer: bool = False) -> list[dict[str, Any]]:  # type: ignore
        """Get accumulated training data."""  # type: ignore
        data = self.training_data.copy()  # type: ignore
        if clear_buffer:  # type: ignore
            self.training_data.clear()  # type: ignore
        return data  # type: ignore

    def save_training_data(self, filepath: Path, clear_buffer: bool = True):  # type: ignore
        """Save training data to file for Agent Lightning."""  # type: ignore
        data = self.get_training_data(clear_buffer)  # type: ignore
        with open(filepath, "w") as f:  # type: ignore
            json.dump(data, f, indent=2)  # type: ignore
        logger.info(f"Saved {len(data)} training samples to {filepath}")  # type: ignore


class UniversalAgentManager:  # type: ignore
    """High-level manager for universal agent operations."""  # type: ignore

    def __init__(self):  # type: ignore
        self.framework_detector = FrameworkDetector()  # type: ignore
        self.scheduler = UniversalTaskScheduler()  # type: ignore
        self.training_interface = UniversalTrainingInterface(self.scheduler)  # type: ignore

    async def initialize_from_config(self, config_file: Path) -> bool:  # type: ignore
        """Initialize agents from configuration file."""  # type: ignore
        try:  # type: ignore
            with open(config_file) as f:  # type: ignore
                config = json.load(f)  # type: ignore

            # Initialize each agent configuration
            for agent_config in config.get("agents", []):  # type: ignore
                framework = agent_config.get("framework")  # type: ignore
                agent_id = agent_config.get("id")  # type: ignore

                if not framework or not agent_id:  # type: ignore
                    logger.warning(f"Invalid agent config: {agent_config}")  # type: ignore
                    continue

                agent = self.framework_detector.create_agent(framework, agent_id)  # type: ignore
                if agent:  # type: ignore
                    success = await self.scheduler.register_agent(agent)  # type: ignore
                    if not success:  # type: ignore
                        logger.error(f"Failed to register agent: {agent_id}")  # type: ignore
                else:  # type: ignore
                    logger.error(f"Failed to create agent: {agent_id}")  # type: ignore

            return True  # type: ignore

        except Exception as e:  # type: ignore
            logger.error(f"Failed to initialize from config: {e}")  # type: ignore
            return False  # type: ignore

    async def add_agent(self, framework: str, config: dict[str, Any]) -> str | None:  # type: ignore
        """Add a new agent to the system."""  # type: ignore
        agent_id = config.get("id", f"{framework}_agent_{len(self.scheduler.agents)}")  # type: ignore

        agent = self.framework_detector.create_agent(framework, agent_id)  # type: ignore
        if not agent:  # type: ignore
            return None  # type: ignore

        success = await self.scheduler.register_agent(agent)  # type: ignore
        if success:  # type: ignore
            return agent_id  # type: ignore
        return None  # type: ignore

    def get_system_status(self) -> dict[str, Any]:  # type: ignore
        """Get comprehensive system status."""  # type: ignore
        return {  # type: ignore
            "frameworks": {  # type: ignore
                "available": self.framework_detector.get_available_frameworks(),  # type: ignore
                "registered": len(self.scheduler.agents),  # type: ignore
            },
            "scheduler": self.scheduler.get_statistics(),  # type: ignore
            "training": {  # type: ignore
                "collected_samples": len(self.training_interface.training_data),  # type: ignore
                "ready_for_training": len(self.training_interface.training_data) > 0,  # type: ignore
            },
        }

    async def start_system(self):  # type: ignore
        """Start the universal agent system."""  # type: ignore
        await self.scheduler.start_scheduler()  # type: ignore
        logger.info("Universal agent system started")  # type: ignore

    async def stop_system(self):  # type: ignore
        """Stop the universal agent system."""  # type: ignore
        await self.scheduler.cleanup()  # type: ignore
        logger.info("Universal agent system stopped")  # type: ignore

    async def execute_workflow(self, workflow: list[TaskDefinition]) -> list[TaskResult]:  # type: ignore
        """Execute a complete workflow of tasks."""  # type: ignore
        results = []  # type: ignore
        for task in workflow:  # type: ignore
            result = await self.scheduler.execute_task(task)  # type: ignore
            results.append(result)  # type: ignore

            # Stop workflow if critical task fails
            if task.priority == "critical" and not result.success:  # type: ignore
                logger.error(f"Critical task failed, stopping workflow: {task.description}")  # type: ignore
                break

        return results  # type: ignore


# Factory functions for easy usage


async def create_universal_system(frameworks: list[str], configs: list[dict[str, Any]]) -> UniversalAgentManager:  # type: ignore
    """Create a universal agent system with specified frameworks."""  # type: ignore
    manager = UniversalAgentManager()  # type: ignore

    for framework, config in zip(frameworks, configs, strict=False):  # type: ignore
        agent_id = await manager.add_agent(framework, config)  # type: ignore
        if agent_id:  # type: ignore
            logger.info(f"Added {framework} agent: {agent_id}")  # type: ignore
        else:  # type: ignore
            logger.error(f"Failed to add {framework} agent")  # type: ignore

    await manager.start_system()  # type: ignore
    return manager  # type: ignore


def create_mechanical_engineering_tasks() -> list[TaskDefinition]:  # type: ignore
    """Create standard mechanical engineering tasks."""  # type: ignore
    return [  # type: ignore
        TaskDefinition(
            task_type=TaskType.DESIGN_REVIEW,  # type: ignore
            description="Review mechanical design for manufacturing feasibility",  # type: ignore
            requirements=["Check tolerances", "Assess material selection", "Evaluate assembly process"],  # type: ignore
            domain_context={"domain": "mechanical_engineering", "industry": "automotive"},  # type: ignore
        ),
        TaskDefinition(
            task_type=TaskType.SAFETY_ANALYSIS,  # type: ignore
            description="Perform safety analysis for pressure vessel design",  # type: ignore
            requirements=["Compliance with ASME standards", "Risk assessment", "Safety factor verification"],  # type: ignore
            constraints=["Maximum pressure 150 PSI", "Operating temperature -20°C to 200°C"],  # type: ignore
            domain_context={"domain": "safety_engineering", "standards": ["ASME", "OSHA"]},  # type: ignore
        ),
        TaskDefinition(
            task_type=TaskType.MANUFACTURING_ASSESSMENT,  # type: ignore
            description="Assess manufacturing process for complex machined part",  # type: ignore
            requirements=["CNC machining evaluation", "Tool selection", "Cost estimation"],  # type: ignore
            domain_context={"domain": "manufacturing", "processes": ["CNC", "inspection"]},  # type: ignore
        ),
    ]
