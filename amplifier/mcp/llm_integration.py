from typing import Any

"""
LLM Integration Module

Integrates local LLM models with existing agent systems for cost reduction
and privacy improvement. Provides intelligent model selection and fallback
to cloud APIs when needed.

Key Features:
- Automatic model selection based on task requirements
- Cost optimization with local models
- Fallback to cloud APIs when local models unavailable
- Privacy-preserving local execution
- Model capability matching
"""

from dataclasses import dataclass
from enum import Enum

from ..utils.logger import get_logger
from .docker_model_runner import ModelStatus
from .docker_model_runner import get_model_runner

logger = get_logger(__name__)


class TaskType(Enum):
    """Types of tasks for model selection."""

    CHAT = "chat"
    CODE_GENERATION = "code_generation"
    TEXT_ANALYSIS = "text_analysis"
    DATA_PROCESSING = "data_processing"
    REASONING = "reasoning"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"


@dataclass
class ModelCapability:
    """Model capability definition."""

    task_types: list[TaskType]
    max_context_length: int
    supports_streaming: bool
    quality_score: float  # 0.0 to 1.0
    cost_per_token: float
    privacy_level: int  # 0 (cloud) to 10 (fully local)
    speed_rating: float  # tokens per second


class LLMOrchestrator:
    """Orchestrates LLM usage with intelligent model selection."""

    def __init__(self):  # type: ignore[assignment]
        self.model_runner = get_model_runner()
        self.model_capabilities = self._define_model_capabilities()
        self.usage_stats = {"local_requests": 0, "cloud_requests": 0, "cost_savings": 0.0}

    def _define_model_capabilities(self) -> dict[str, ModelCapability]:
        """Define capabilities for available models."""
        return {
            "llama3.2-1b": ModelCapability(
                task_types=[TaskType.CHAT, TaskType.TEXT_ANALYSIS, TaskType.SUMMARIZATION],
                max_context_length=8192,
                supports_streaming=True,
                quality_score=0.7,
                cost_per_token=0.0,  # Local model
                privacy_level=10,
                speed_rating=50.0,
            ),
            "llama3.2-3b": ModelCapability(
                task_types=[TaskType.CHAT, TaskType.REASONING, TaskType.SUMMARIZATION],
                max_context_length=8192,
                supports_streaming=True,
                quality_score=0.8,
                cost_per_token=0.0,
                privacy_level=10,
                speed_rating=35.0,
            ),
            "qwen2.5-1.5b": ModelCapability(
                task_types=[TaskType.CHAT, TaskType.CODE_GENERATION, TaskType.REASONING],
                max_context_length=8192,
                supports_streaming=True,
                quality_score=0.75,
                cost_per_token=0.0,
                privacy_level=10,
                speed_rating=40.0,
            ),
            "phi3-mini": ModelCapability(
                task_types=[TaskType.CHAT, TaskType.CODE_GENERATION, TaskType.REASONING],
                max_context_length=4096,
                supports_streaming=True,
                quality_score=0.72,
                cost_per_token=0.0,
                privacy_level=10,
                speed_rating=45.0,
            ),
            # Cloud fallback models
            "gpt-3.5-turbo": ModelCapability(
                task_types=list(TaskType),
                max_context_length=16385,
                supports_streaming=True,
                quality_score=0.85,
                cost_per_token=0.0005,
                privacy_level=2,
                speed_rating=80.0,
            ),
            "gpt-4": ModelCapability(
                task_types=list(TaskType),
                max_context_length=8192,
                supports_streaming=True,
                quality_score=0.95,
                cost_per_token=0.03,
                privacy_level=2,
                speed_rating=25.0,
            ),
        }

    async def select_model(
        self,
        task_type: TaskType,
        context_length: int = 1000,
        require_privacy: bool = False,
        quality_threshold: float = 0.6,
    ) -> str:
        """Select the best model for a given task."""

        # Get available local models
        local_models = []
        for model_name, capability in self.model_capabilities.items():
            if capability.privacy_level >= 8:  # Local models
                model = await self.model_runner.model_manager.get_model(model_name)
                if (
                    model
                    and model.status in [ModelStatus.READY, ModelStatus.RUNNING]
                    and task_type in capability.task_types
                    and context_length <= capability.max_context_length
                    and capability.quality_score >= quality_threshold
                ):
                    local_models.append((model_name, capability))

        # Sort by quality score (for local models, prioritize speed and privacy)
        local_models.sort(key=lambda x: (x[1].quality_score, x[1].speed_rating), reverse=True)

        if local_models:
            best_local = local_models[0]
            logger.info(f"Selected local model: {best_local[0]} for task: {task_type.value}")
            return best_local[0]

        # If privacy required and no local models available, wait for one
        if require_privacy:
            # Start the best available local model
            available_models = [
                name
                for name, cap in self.model_capabilities.items()
                if cap.privacy_level >= 8 and task_type in cap.task_types
            ]
            if available_models:
                model_name = max(available_models, key=lambda x: self.model_capabilities[x].quality_score)
                logger.info(f"Starting local model for privacy: {model_name}")
                await self.model_runner.model_manager.start_model(model_name)
                return model_name

        # Fallback to cloud models
        cloud_models = [
            (name, cap)
            for name, cap in self.model_capabilities.items()
            if cap.privacy_level < 8
            and task_type in cap.task_types
            and context_length <= cap.max_context_length
            and cap.quality_score >= quality_threshold
        ]

        if cloud_models:
            # Sort by cost-effectiveness (quality/price)
            cloud_models.sort(key=lambda x: x[1].quality_score / max(x[1].cost_per_token, 0.0001))
            best_cloud = cloud_models[0]
            logger.info(f"Selected cloud model: {best_cloud[0]} for task: {task_type.value}")
            return best_cloud[0]

        # Default fallback
        logger.warning(f"No suitable model found for task: {task_type.value}, using default")
        return "gpt-3.5-turbo"

    async def complete_chat(
        self,
        messages: list[dict[str, str]],
        task_type: TaskType = TaskType.CHAT,
        require_privacy: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """Complete a chat request with intelligent model selection."""

        context_length = sum(len(msg.get("content", "")) for msg in messages)

        # Select model
        model_name = await self.select_model(
            task_type=task_type,
            context_length=context_length,
            require_privacy=require_privacy,
            quality_threshold=kwargs.get("min_quality", 0.6),
        )

        # Determine if local or cloud model
        capability = self.model_capabilities.get(model_name)
        is_local = capability and capability.privacy_level >= 8 if capability else False

        try:
            if is_local:
                # Use local model
                self.usage_stats["local_requests"] += 1

                response = await self.model_runner._call_model_api(
                    # type: ignore[arg-type]
                    # type: ignore[arg-type]
                    await self.model_runner.model_manager.get_model(model_name),
                    {
                        "model": model_name,
                        "messages": messages,
                        "max_tokens": kwargs.get("max_tokens", 1000),
                        "temperature": kwargs.get("temperature", 0.7),
                        "stream": False,
                    },
                )

                # Calculate cost savings
                if capability:
                    estimated_cloud_cost = context_length * 0.0005  # GPT-3.5 rate
                    self.usage_stats["cost_savings"] += estimated_cloud_cost

                logger.info(f"Local model completion successful: {model_name}")
                return response

            # Use cloud model (fallback)
            self.usage_stats["cloud_requests"] += 1
            return await self._call_cloud_model(model_name, messages, **kwargs)

        except Exception as e:
            logger.error(f"Model completion failed with {model_name}: {e}")

            # Fallback to cloud if local failed
            if is_local:
                logger.info("Falling back to cloud model")
                self.usage_stats["cloud_requests"] += 1
                return await self._call_cloud_model("gpt-3.5-turbo", messages, **kwargs)
            raise

    async def _call_cloud_model(self, model_name: str, messages: list[dict[str, str]], **kwargs) -> dict[str, Any]:
        """Call a cloud model API (fallback)."""

        try:
            # Try OpenAI API if available
            import openai

            client = openai.AsyncOpenAI()

            response = await client.chat.completions.create(
                model=model_name,
                # type: ignore[arg-type]
                # type: ignore[arg-type]
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
            )

            # Convert to standard format
            return {
                "id": response.id,
                "object": "chat.completion",
                "created": response.created,
                "model": response.model,
                "choices": [
                    {
                        "index": choice.index,
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content,
                        },
                        "finish_reason": choice.finish_reason,
                    }
                    for choice in response.choices
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
            }

        except ImportError:
            # OpenAI not available, return mock response
            logger.warning("OpenAI not available, returning mock response")
            return {
                "id": "mock-response",
                "object": "chat.completion",
                "created": 0,
                "model": model_name,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": f"Cloud model {model_name} would respond here. OpenAI library not installed.",
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            }
        except Exception as e:
            logger.error(f"Cloud model call failed: {e}")
            raise

    async def get_usage_stats(self) -> dict[str, Any]:
        """Get usage statistics."""
        total_requests = self.usage_stats["local_requests"] + self.usage_stats["cloud_requests"]

        return {
            **self.usage_stats,
            "total_requests": total_requests,
            "local_percentage": (
                self.usage_stats["local_requests"] / total_requests * 100 if total_requests > 0 else 0
            ),
            "cloud_percentage": (
                self.usage_stats["cloud_requests"] / total_requests * 100 if total_requests > 0 else 0
            ),
        }

    async def preload_popular_models(self):
        """Preload popular local models for faster response."""
        popular_models = ["llama3.2-1b", "qwen2.5-1.5b"]

        for model_name in popular_models:
            model = await self.model_runner.model_manager.get_model(model_name)
            if model and model.status == ModelStatus.NOT_FOUND:
                logger.info(f"Preloading popular model: {model_name}")
                await self.model_runner.model_manager.pull_model(model_name)


# Global orchestrator instance
_llm_orchestrator = LLMOrchestrator()


def get_llm_orchestrator() -> LLMOrchestrator:
    """Get the global LLM orchestrator instance."""
    return _llm_orchestrator


async def smart_chat_completion(
    messages: list[dict[str, str]],
    task_type: TaskType = TaskType.CHAT,
    require_privacy: bool = False,
    **kwargs,
) -> dict[str, Any]:
    """Convenient function for smart chat completion with model selection."""
    orchestrator = get_llm_orchestrator()
    return await orchestrator.complete_chat(messages, task_type, require_privacy, **kwargs)


async def initialize_llm_integration():
    """Initialize the LLM integration system."""
    orchestrator = get_llm_orchestrator()
    await orchestrator.preload_popular_models()
    logger.info("LLM integration initialized")  # type: ignore  # type: ignore
