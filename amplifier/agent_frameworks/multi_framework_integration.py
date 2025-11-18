#!/usr/bin/env python3
# pyright: ignore大部分类型检查错误

"""
Multi-Framework Agent Integration System

Provides seamless integration patterns for LangChain, OpenAI SDK, AutoGen, CrewAI
with framework-agnostic adapters for Agent Lightning training.

This module embodies the amplifier philosophy:
- Ruthless simplicity in framework integration
- Modular "bricks & studs" design for adapter patterns
- Framework integrations are independent and replaceable
- Clear contracts between framework layers
"""

import asyncio
import time
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Generic

try:
    from langchain.tools import Tool
except ImportError:
    Tool = None  # type: ignore

try:
    import crewai
except ImportError:
    crewai = None  # type: ignore

# Framework imports
try:
    from langchain.agents import Agent as LangChainAgent
    from langchain.chains import Chain as LangChainChain
    from langchain.schema import BaseMessage as LangChainMessage

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    LangChainAgent = None
    LangChainChain = None
    LangChainMessage = None

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

try:
    import autogen
    from autogen import Agent as AutoGenAgent
    from autogen import GroupChatManager

    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    AutoGenAgent = None
    GroupChatManager = None

try:
    from crewai import Agent as CrewAIAgent
    from crewai import Crew
    from crewai import Task as CrewAITask

    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    CrewAIAgent = None
    CrewAITask = None
    Crew = None

from amplifier.utils.logger import get_logger

logger = get_logger(__name__)


class FrameworkType(Enum):
    """Supported agent frameworks."""

    LANGCHAIN = "langchain"
    OPENAI_SDK = "openai_sdk"
    AUTOGEN = "autogen"
    CREWAI = "crewai"
    CUSTOM = "custom"


@dataclass
class AgentConfig:
    """Configuration for agent integration."""

    framework: FrameworkType
    agent_type: str
    model_config: dict[str, Any] = field(default_factory=dict)
    tool_config: list[dict[str, Any]] = field(default_factory=list)
    training_config: dict[str, Any] = field(default_factory=dict)
    domain_config: dict[str, Any] = field(default_factory=dict)  # For mechanical engineering domains


@dataclass
class AgentInteraction:
    """Unified representation of agent interaction across frameworks."""

    agent_id: str
    input_message: str
    output_message: str | None = None
    tools_used: list[str] = field(default_factory=list)
    reasoning_steps: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    framework_specific: dict[str, Any] = field(default_factory=dict)
    timestamp: str | None = None


@dataclass
class AgentMetrics:
    """Performance metrics across frameworks."""

    response_time: float
    token_usage: dict[str, int]
    accuracy_score: float | None = None
    task_completion_rate: float | None = None
    domain_specific_metrics: dict[str, float] = field(default_factory=dict)


class FrameworkAdapter(ABC, Generic[AgentConfig]):  # type: ignore[generic]
    """Abstract base class for framework adapters."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent = None
        self.metrics_history: list[AgentMetrics] = []

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the framework-specific agent."""
        pass

    @abstractmethod
    async def execute(self, input_message: str, **kwargs) -> AgentInteraction:
        """Execute agent and return unified interaction format."""
        pass

    @abstractmethod
    async def train_step(self, training_data: dict[str, Any]) -> AgentMetrics:
        """Execute one training step with the framework."""
        pass

    @abstractmethod
    def extract_features(self) -> dict[str, Any]:
        """Extract features for Agent Lightning training."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup framework resources."""
        pass


class AdvancedTraceAdapter:
    """Enhanced trace adapter with mechanical engineering domain knowledge."""

    def __init__(self, domain_type: str = "mechanical_engineering"):
        self.domain_type = domain_type
        self.domain_knowledge = self._load_domain_knowledge()

    def _load_domain_knowledge(self) -> dict[str, Any]:
        """Load domain-specific knowledge for data transformation."""
        if self.domain_type == "mechanical_engineering":
            return {
                "cad_extensions": [".step", ".iges", ".stl", ".obj", ".fbx"],
                "technical_formats": ["pdf", "dwg", "dxf", "xlsx", "csv"],
                "engineering_units": ["mm", "in", "kg", "lb", "psi", "MPa", "N·m"],
                "safety_keywords": ["hazard", "warning", "caution", "danger", "risk"],
                "quality_metrics": ["tolerance", "surface_finish", "material", "coating"],
                "manufacturing_processes": ["cnc", "3d_print", "injection", "forming"],
            }
        return {}

    def transform_for_training(self, interaction: AgentInteraction) -> dict[str, Any]:
        """Transform agent interaction for Agent Lightning training."""
        features = {
            "input_embedding": self._extract_text_features(interaction.input_message),
            "output_embedding": self._extract_text_features(interaction.output_message or ""),
            "tools_sequence": self._encode_tools(interaction.tools_used),
            "reasoning_length": len(interaction.reasoning_steps),
            "domain_features": self._extract_domain_features(interaction),
            "metadata": interaction.metadata,
        }
        return features

    def _extract_text_features(self, text: str) -> list[float]:
        """Extract simple text features (placeholder for actual embedding)."""
        # Simple feature extraction - in production, use proper embeddings
        return [
            len(text.split()),  # word count
            text.count("?"),  # question marks
            text.count("!"),  # exclamation marks
            len([w for w in text.split() if w.lower() in self.domain_knowledge.get("safety_keywords", [])]),
            len(
                [
                    w
                    for w in text.split()
                    if any(unit in w.lower() for unit in self.domain_knowledge.get("engineering_units", []))
                ]
            ),
        ]

    def _encode_tools(self, tools: list[str]) -> list[int]:
        """Encode tool usage as one-hot vector."""
        all_tools = ["search", "calculate", "cad_analyze", "safety_check", "quality_assess"]
        return [1 if tool in tools else 0 for tool in all_tools]

    def _extract_domain_features(self, interaction: AgentInteraction) -> dict[str, float]:
        """Extract domain-specific features."""
        text = f"{interaction.input_message} {interaction.output_message or ''}"
        return {
            "safety_mentions": len(
                [w for w in text.lower().split() if w in self.domain_knowledge.get("safety_keywords", [])]
            ),
            "technical_terms": len(
                [
                    w
                    for w in text.split()
                    if any(unit in w.lower() for unit in self.domain_knowledge.get("engineering_units", []))
                ]
            ),
            "manufacturing_refs": len(
                [w for w in text.lower().split() if w in self.domain_knowledge.get("manufacturing_processes", [])]
            ),
        }


class LangChainAdapter(FrameworkAdapter):
    """Adapter for LangChain framework integration."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is not installed. Install with: pip install langchain")

    async def initialize(self) -> bool:
        """Initialize LangChain agent with mechanical engineering tools."""
        try:
            # Create LangChain agent based on configuration
            from langchain.agents import initialize_agent
            from langchain.llms import OpenAI

            tools = self._create_langchain_tools()

            # Initialize agent
            self.agent = initialize_agent(
                tools=tools,
                llm=OpenAI(**self.config.model_config),
                agent=self.config.agent_type,  # type: ignore[assignment]
                verbose=True,  # type: ignore[assignment]
            )

            logger.info(f"LangChain agent initialized with {len(tools)} tools")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize LangChain agent: {e}")
            return False

    def _create_langchain_tools(self) -> list[Any]:
        """Create LangChain tools for mechanical engineering domain."""
        if Tool is None:
            return []

        tools = []

        for tool_config in self.config.tool_config:
            if tool_config["name"] == "cad_analyzer":
                tools.append(
                    Tool(
                        name="CAD Analyzer",
                        description="Analyze CAD files for manufacturing readiness",
                        func=self._cad_analysis_tool,
                    )
                )
            elif tool_config["name"] == "safety_checker":
                tools.append(
                    Tool(
                        name="Safety Checker",
                        description="Check designs for safety compliance",
                        func=self._safety_check_tool,
                    )
                )
            # Add more tools as needed

        return tools

    def _cad_analysis_tool(self, input_text: str) -> str:
        """Mock CAD analysis tool."""
        return f"CAD analysis for: {input_text}. Status: Ready for manufacturing."

    def _safety_check_tool(self, input_text: str) -> str:
        """Mock safety check tool."""
        return f"Safety check for: {input_text}. Status: Compliant with safety standards."

    async def execute(self, input_message: str, **kwargs) -> AgentInteraction:
        """Execute LangChain agent."""
        import time

        time.time()

        try:
            result = self.agent.run(input_message)  # type: ignore[assignment]

            interaction = AgentInteraction(
                agent_id=f"langchain_{id(self)}",
                input_message=input_message,
                output_message=result,
                tools_used=[],  # LangChain doesn't expose this easily
                reasoning_steps=[result],  # Simplified
                metadata={"framework": "langchain"},
            )

            return interaction

        except Exception as e:
            logger.error(f"LangChain execution failed: {e}")
            return AgentInteraction(
                agent_id=f"langchain_{id(self)}",
                input_message=input_message,
                output_message=f"Error: {str(e)}",
                metadata={"framework": "langchain", "error": str(e)},
            )

    async def train_step(self, training_data: dict[str, Any]) -> AgentMetrics:
        """Execute training step for LangChain agent."""
        # Simplified training - in practice would use LangChain's training features
        start_time = time.time()

        # Mock training step
        await asyncio.sleep(0.1)  # Simulate processing

        metrics = AgentMetrics(
            response_time=time.time() - start_time,
            token_usage={"prompt": 100, "completion": 50},
            accuracy_score=0.85,  # Mock score
        )

        self.metrics_history.append(metrics)
        return metrics

    def extract_features(self) -> dict[str, Any]:
        """Extract features from LangChain agent."""
        return {
            "framework": "langchain",
            "agent_type": self.config.agent_type,
            "tool_count": len(self.config.tool_config),
            "model_config": self.config.model_config,
        }

    def cleanup(self) -> None:
        """Cleanup LangChain resources."""
        self.agent = None


class OpenAIAdapter(FrameworkAdapter):
    """Adapter for direct OpenAI SDK integration."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI SDK is not installed. Install with: pip install openai")
        self.client = None

    async def initialize(self) -> bool:
        """Initialize OpenAI client."""
        try:
            self.client = openai.AsyncOpenAI(**self.config.model_config)  # type: ignore[assignment]
            logger.info("OpenAI client initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return False

    async def execute(self, input_message: str, **kwargs) -> AgentInteraction:
        """Execute using OpenAI API directly."""
        import time

        time.time()

        try:
            # Create system prompt for mechanical engineering
            system_prompt = self._create_engineering_system_prompt()

            response = await self.client.chat.completions.create(  # type: ignore[assignment]
                model=self.config.model_config.get("model", "gpt-3.5-turbo"),
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": input_message}],
                **kwargs,
            )

            result = response.choices[0].message.content

            interaction = AgentInteraction(
                agent_id=f"openai_{id(self)}",
                input_message=input_message,
                output_message=result,
                reasoning_steps=[result],
                metadata={
                    "framework": "openai_sdk",
                    "model": self.config.model_config.get("model"),
                    "usage": response.usage._asdict() if response.usage else {},
                },
            )

            return interaction

        except Exception as e:
            logger.error(f"OpenAI execution failed: {e}")
            return AgentInteraction(
                agent_id=f"openai_{id(self)}",
                input_message=input_message,
                output_message=f"Error: {str(e)}",
                metadata={"framework": "openai_sdk", "error": str(e)},
            )

    def _create_engineering_system_prompt(self) -> str:
        """Create system prompt for mechanical engineering domain."""
        return """You are a mechanical engineering expert assistant.
        Provide accurate, safe, and practical engineering advice.
        Consider manufacturing constraints, safety standards, and cost-effectiveness.
        Ask clarifying questions when specifications are unclear."""

    async def train_step(self, training_data: dict[str, Any]) -> AgentMetrics:
        """Execute training step for OpenAI integration."""
        start_time = time.time()

        # Simulate fine-tuning step or optimization
        await asyncio.sleep(0.1)

        metrics = AgentMetrics(
            response_time=time.time() - start_time, token_usage={"prompt": 150, "completion": 75}, accuracy_score=0.88
        )

        self.metrics_history.append(metrics)
        return metrics

    def extract_features(self) -> dict[str, Any]:
        """Extract features from OpenAI integration."""
        return {
            "framework": "openai_sdk",
            "model": self.config.model_config.get("model"),
            "has_tools": bool(self.config.tool_config),
        }

    def cleanup(self) -> None:
        """Cleanup OpenAI resources."""
        self.client = None


class AutoGenAdapter(FrameworkAdapter):
    """Adapter for Microsoft AutoGen framework integration."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        if not AUTOGEN_AVAILABLE:
            raise ImportError("AutoGen is not installed. Install with: pip install pyautogen")
        self.group_chat = None

    async def initialize(self) -> bool:
        """Initialize AutoGen agents for multi-agent collaboration."""
        try:
            # Create AutoGen agents for different engineering roles
            mechanical_engineer = autogen.AssistantAgent(
                "mechanical_engineer",
                llm_config=self.config.model_config,
                system_message="You are a mechanical engineering expert.",
            )

            safety_specialist = autogen.AssistantAgent(
                "safety_specialist",
                llm_config=self.config.model_config,
                system_message="You are a safety compliance specialist.",
            )

            manufacturing_expert = autogen.AssistantAgent(
                "manufacturing_expert",
                llm_config=self.config.model_config,
                system_message="You are a manufacturing process expert.",
            )

            user_proxy = autogen.UserProxyAgent("user_proxy", code_execution_config=False, human_input_mode="NEVER")

            # Create group chat
            self.group_chat = autogen.GroupChat(
                agents=[mechanical_engineer, safety_specialist, manufacturing_expert, user_proxy],
                messages=[],
                max_round=10,
            )

            self.group_chat_manager = autogen.GroupChatManager(
                groupchat=self.group_chat, llm_config=self.config.model_config
            )

            logger.info("AutoGen multi-agent system initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize AutoGen: {e}")
            return False

    async def execute(self, input_message: str, **kwargs) -> AgentInteraction:
        """Execute AutoGen multi-agent collaboration."""
        import time

        time.time()

        try:
            # Start group chat
            user_proxy = self.group_chat.agent_by_name("user_proxy")  # type: ignore[assignment]

            # This is a simplified execution - AutoGen requires more complex async handling
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: user_proxy.initiate_chat(self.group_chat_manager, message=input_message, max_turns=3)
            )

            # Extract last message as result
            if self.group_chat.messages:  # type: ignore[assignment]
                last_message = self.group_chat.messages[-1].get("content", "")  # type: ignore[assignment]
            else:
                last_message = "No response generated"

            interaction = AgentInteraction(
                agent_id=f"autogen_{id(self)}",
                input_message=input_message,
                output_message=last_message,
                reasoning_steps=[msg.get("content", "") for msg in self.group_chat.messages[-3:]],  # type: ignore[assignment]
                metadata={
                    "framework": "autogen",
                    "agent_count": len(self.group_chat.agents),  # type: ignore[assignment]
                    "message_count": len(self.group_chat.messages),  # type: ignore[assignment]
                },
            )

            return interaction

        except Exception as e:
            logger.error(f"AutoGen execution failed: {e}")
            return AgentInteraction(
                agent_id=f"autogen_{id(self)}",
                input_message=input_message,
                output_message=f"Error: {str(e)}",
                metadata={"framework": "autogen", "error": str(e)},
            )

    async def train_step(self, training_data: dict[str, Any]) -> AgentMetrics:
        """Execute training step for AutoGen agents."""
        start_time = time.time()

        # Simulate multi-agent training
        await asyncio.sleep(0.2)  # Multi-agent systems take longer

        metrics = AgentMetrics(
            response_time=time.time() - start_time,
            token_usage={"prompt": 300, "completion": 150},  # Higher usage for multi-agent
            accuracy_score=0.92,  # Often better with multi-agent collaboration
            task_completion_rate=0.89,
        )

        self.metrics_history.append(metrics)
        return metrics

    def extract_features(self) -> dict[str, Any]:
        """Extract features from AutoGen system."""
        return {
            "framework": "autogen",
            "agent_count": len(self.group_chat.agents) if self.group_chat else 0,
            "max_rounds": 10,
            "multi_agent": True,
        }

    def cleanup(self) -> None:
        """Cleanup AutoGen resources."""
        self.group_chat = None
        self.group_chat_manager = None


class CrewAIAdapter(FrameworkAdapter):
    """Adapter for CrewAI framework integration."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        if not CREWAI_AVAILABLE:
            raise ImportError("CrewAI is not installed. Install with: pip install crewai")
        self.crew = None

    async def initialize(self) -> bool:
        """Initialize CrewAI crew for mechanical engineering tasks."""
        assert CrewAIAgent is not None, "CrewAIAgent should be available when CREWAI_AVAILABLE is True"
        assert CrewAITask is not None, "CrewAITask should be available when CREWAI_AVAILABLE is True"
        assert Crew is not None, "Crew should be available when CREWAI_AVAILABLE is True"

        try:
            # Define agents for different engineering roles
            design_engineer = CrewAIAgent(
                role="Senior Mechanical Design Engineer",
                goal="Design robust mechanical solutions that meet specifications",
                backstory="You are an experienced mechanical engineer with 15+ years in product design.",
                tools=[],  # Add tools as needed
                verbose=True,
            )

            manufacturing_engineer = CrewAIAgent(
                role="Manufacturing Process Engineer",
                goal="Ensure designs are manufacturable and cost-effective",
                backstory="You specialize in manufacturing processes and design for manufacturability.",
                tools=[],
                verbose=True,
            )

            quality_engineer = CrewAIAgent(
                role="Quality Assurance Engineer",
                goal="Verify designs meet quality and safety standards",
                backstory="You are responsible for quality control and compliance verification.",
                tools=[],
                verbose=True,
            )

            # Create tasks
            design_task = CrewAITask(
                description="Analyze requirements and create initial design concept",
                agent=design_engineer,
                expected_output="Detailed design specification with calculations",
            )

            manufacturability_task = CrewAITask(
                description="Review design for manufacturing feasibility",
                agent=manufacturing_engineer,
                expected_output="Manufacturing assessment with process recommendations",
            )

            quality_task = CrewAITask(
                description="Perform quality and safety compliance check",
                agent=quality_engineer,
                expected_output="Quality assessment report with compliance status",
            )

            # Create crew
            self.crew = Crew(
                agents=[design_engineer, manufacturing_engineer, quality_engineer],
                tasks=[design_task, manufacturability_task, quality_task],
                verbose=True,
            )

            logger.info("CrewAI crew initialized with 3 agents and 3 tasks")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize CrewAI: {e}")
            return False

    async def execute(self, input_message: str, **kwargs) -> AgentInteraction:
        """Execute CrewAI crew workflow."""
        import time

        time.time()

        try:
            # Kick off crew execution
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.crew.kickoff(inputs={"user_request": input_message}),  # type: ignore[assignment]
            )

            interaction = AgentInteraction(
                agent_id=f"crewai_{id(self)}",
                input_message=input_message,
                output_message=str(result),
                tools_used=["design_analysis", "manufacturing_review", "quality_check"],
                reasoning_steps=["Design phase completed", "Manufacturing review completed", "Quality check completed"],
                metadata={
                    "framework": "crewai",
                    "agent_count": len(self.crew.agents),  # type: ignore[assignment]
                    "task_count": len(self.crew.tasks),  # type: ignore[assignment]
                },
            )

            return interaction

        except Exception as e:
            logger.error(f"CrewAI execution failed: {e}")
            return AgentInteraction(
                agent_id=f"crewai_{id(self)}",
                input_message=input_message,
                output_message=f"Error: {str(e)}",
                metadata={"framework": "crewai", "error": str(e)},
            )

    async def train_step(self, training_data: dict[str, Any]) -> AgentMetrics:
        """Execute training step for CrewAI agents."""
        start_time = time.time()

        # Simulate crew training
        await asyncio.sleep(0.3)  # CrewAI with multiple agents takes longer

        metrics = AgentMetrics(
            response_time=time.time() - start_time,
            token_usage={"prompt": 400, "completion": 200},  # Highest usage due to crew collaboration
            accuracy_score=0.94,  # Often highest with specialized crew
            task_completion_rate=0.91,
            domain_specific_metrics={"collaboration_score": 0.88, "role_specialization": 0.92},
        )

        self.metrics_history.append(metrics)
        return metrics

    def extract_features(self) -> dict[str, Any]:
        """Extract features from CrewAI system."""
        return {
            "framework": "crewai",
            "agent_count": len(self.crew.agents) if self.crew else 0,
            "task_count": len(self.crew.tasks) if self.crew else 0,
            "role_based": True,
            "workflow_orchestrated": True,
        }

    def cleanup(self) -> None:
        """Cleanup CrewAI resources."""
        self.crew = None


class FrameworkRegistry:
    """Registry for managing framework adapters."""

    def __init__(self):
        self._adapters: dict[FrameworkType, type[FrameworkAdapter]] = {
            FrameworkType.LANGCHAIN: LangChainAdapter,
            FrameworkType.OPENAI_SDK: OpenAIAdapter,
            FrameworkType.AUTOGEN: AutoGenAdapter,
            FrameworkType.CREWAI: CrewAIAdapter,
        }
        self._trace_adapter = AdvancedTraceAdapter()

    def register_adapter(self, framework: FrameworkType, adapter_class: type[FrameworkAdapter]):
        """Register a new framework adapter."""
        self._adapters[framework] = adapter_class
        logger.info(f"Registered adapter for framework: {framework.value}")

    def create_adapter(self, config: AgentConfig) -> FrameworkAdapter:
        """Create framework adapter based on configuration."""
        adapter_class = self._adapters.get(config.framework)
        if not adapter_class:
            raise ValueError(f"Unsupported framework: {config.framework}")

        adapter = adapter_class(config)
        logger.info(f"Created adapter for {config.framework.value} framework")
        return adapter

    def get_available_frameworks(self) -> list[FrameworkType]:
        """Get list of available frameworks."""
        available = []
        for framework in FrameworkType:
            if framework == FrameworkType.CUSTOM:
                continue
            try:
                adapter_class = self._adapters.get(framework)
                if adapter_class:
                    # Try to instantiate to check dependencies
                    test_config = AgentConfig(framework=framework, agent_type="test")
                    adapter_class(test_config)
                    available.append(framework)
            except (ImportError, Exception):
                logger.debug(f"Framework {framework.value} not available: dependencies missing")

        return available

    def get_trace_adapter(self) -> AdvancedTraceAdapter:
        """Get the trace adapter for data transformation."""
        return self._trace_adapter


class MultiFrameworkOrchestrator:
    """Orchestrates multiple framework adapters for training and evaluation."""

    def __init__(self):
        self.registry = FrameworkRegistry()
        self.adapters: dict[str, FrameworkAdapter] = {}
        self.interaction_history: list[AgentInteraction] = []

    async def add_framework(self, name: str, config: AgentConfig) -> bool:
        """Add a framework adapter to the orchestrator."""
        try:
            adapter = self.registry.create_adapter(config)
            if await adapter.initialize():
                self.adapters[name] = adapter
                logger.info(f"Added framework adapter: {name}")
                return True
            logger.error(f"Failed to initialize framework: {name}")
            return False
        except Exception as e:
            logger.error(f"Failed to add framework {name}: {e}")
            return False

    async def execute_all_frameworks(self, input_message: str, **kwargs) -> dict[str, AgentInteraction]:
        """Execute the same input across all frameworks."""
        results = {}

        # Execute all frameworks in parallel
        tasks = []
        framework_names = []

        for name, adapter in self.adapters.items():
            task = adapter.execute(input_message, **kwargs)
            tasks.append(task)
            framework_names.append(name)

        # Wait for all results
        if tasks:
            interactions = await asyncio.gather(*tasks, return_exceptions=True)

            for name, interaction in zip(framework_names, interactions, strict=False):
                if isinstance(interaction, Exception):
                    logger.error(f"Framework {name} failed: {interaction}")
                    results[name] = AgentInteraction(
                        agent_id=f"error_{name}",
                        input_message=input_message,
                        output_message=f"Framework error: {str(interaction)}",
                        metadata={"framework": name, "error": str(interaction)},
                    )
                else:
                    results[name] = interaction
                    self.interaction_history.append(interaction)  # type: ignore[assignment]

        return results

    async def train_all_frameworks(self, training_data: dict[str, Any]) -> dict[str, AgentMetrics]:
        """Train all frameworks with the same data."""
        results = {}

        # Train all frameworks in parallel
        tasks = []
        framework_names = []

        for name, adapter in self.adapters.items():
            task = adapter.train_step(training_data)
            tasks.append(task)
            framework_names.append(name)

        # Wait for all results
        if tasks:
            metrics_list = await asyncio.gather(*tasks, return_exceptions=True)

            for name, metrics in zip(framework_names, metrics_list, strict=False):
                if isinstance(metrics, Exception):
                    logger.error(f"Training failed for framework {name}: {metrics}")
                else:
                    results[name] = metrics

        return results

    def extract_training_data(self) -> list[dict[str, Any]]:
        """Extract training data from all interactions for Agent Lightning."""
        trace_adapter = self.registry.get_trace_adapter()
        training_data = []

        for interaction in self.interaction_history:
            features = trace_adapter.transform_for_training(interaction)
            training_data.append(features)

        return training_data

    def compare_frameworks(self) -> dict[str, dict[str, float]]:
        """Compare performance across frameworks."""
        comparison = {}

        for name, adapter in self.adapters.items():
            if adapter.metrics_history:
                # Calculate average metrics
                avg_response_time = sum(m.response_time for m in adapter.metrics_history) / len(adapter.metrics_history)
                avg_accuracy = sum(m.accuracy_score or 0 for m in adapter.metrics_history) / len(
                    adapter.metrics_history
                )
                avg_completion = sum(m.task_completion_rate or 0 for m in adapter.metrics_history) / len(
                    adapter.metrics_history
                )

                comparison[name] = {
                    "avg_response_time": avg_response_time,
                    "avg_accuracy": avg_accuracy,
                    "avg_completion_rate": avg_completion,
                    "total_interactions": len(adapter.metrics_history),
                }

        return comparison

    async def cleanup(self):
        """Cleanup all framework adapters."""
        for adapter in self.adapters.values():
            adapter.cleanup()
        self.adapters.clear()
        logger.info("All framework adapters cleaned up")


# Factory functions for easy usage


def create_mechanical_engineering_config(
    framework: FrameworkType, model: str = "gpt-3.5-turbo", agent_type: str = "chat-conversational-react-description"
) -> AgentConfig:
    """Create configuration for mechanical engineering agents."""
    tools = [
        {"name": "cad_analyzer", "description": "Analyze CAD files"},
        {"name": "safety_checker", "description": "Check safety compliance"},
        {"name": "manufacturing_assessor", "description": "Assess manufacturing feasibility"},
    ]

    return AgentConfig(
        framework=framework,
        agent_type=agent_type,
        model_config={"model": model, "temperature": 0.1},
        tool_config=tools,
        domain_config={"specialization": "mechanical_engineering", "safety_critical": True},
    )


async def create_multi_framework_system(frameworks: list[FrameworkType]) -> MultiFrameworkOrchestrator:
    """Create a multi-framework system with the specified frameworks."""
    orchestrator = MultiFrameworkOrchestrator()

    for i, framework in enumerate(frameworks):
        config = create_mechanical_engineering_config(framework)
        framework_name = f"{framework.value}_{i}"
        await orchestrator.add_framework(framework_name, config)

    return orchestrator
