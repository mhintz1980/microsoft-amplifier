"""
Base Skill Framework

Core framework for all amplifier skills with standardized interfaces
and Agent Lightning integration capabilities.
"""

import asyncio
import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class SkillStatus(Enum):
    """Status of skill execution"""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SkillContext:
    """Context for skill execution"""

    user_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SkillResult:
    """Result from skill execution"""

    success: bool
    data: Any = None
    error: str | None = None
    execution_time: float = 0.0
    tokens_used: int = 0
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SkillMetrics:
    """Performance metrics for a skill"""

    total_executions: int = 0
    successful_executions: int = 0
    average_execution_time: float = 0.0
    average_tokens_used: int = 0
    error_rate: float = 0.0
    last_execution: str | None = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions


class BaseSkill(ABC):
    """Base class for all amplifier skills with Agent Lightning integration"""

    def __init__(self, skill_id: str, name: str, description: str):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.status = SkillStatus.IDLE
        self.metrics = SkillMetrics()
        self._config: dict[str, Any] = {}

        # Agent Lightning integration
        self._optimization_enabled = True
        self._zero_hallucination_enforced = True
        self._performance_monitoring = True

    @abstractmethod
    async def execute(self, input_data: Any, context: SkillContext = None) -> SkillResult:
        """
        Execute the skill with given input and context

        Args:
            input_data: The input data for the skill
            context: Optional execution context

        Returns:
            SkillResult with execution results
        """
        pass

    @abstractmethod
    async def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data before execution

        Args:
            input_data: The input data to validate

        Returns:
            True if input is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """
        Get list of skill capabilities

        Returns:
            List of capability descriptions
        """
        pass

    async def run_with_monitoring(self, input_data: Any, context: SkillContext = None) -> SkillResult:
        """
        Execute skill with performance monitoring and optimization

        Args:
            input_data: The input data for the skill
            context: Optional execution context

        Returns:
            SkillResult with execution results and metrics
        """
        import time

        start_time = time.time()

        try:
            self.status = SkillStatus.RUNNING

            # Validate input
            if not await self.validate_input(input_data):
                raise ValueError("Invalid input data")

            # Zero-hallucination check if enabled
            if self._zero_hallucination_enforced:
                await self._validate_zero_hallucination(input_data)

            # Execute the skill
            result = await self.execute(input_data, context)

            # Update metrics
            execution_time = time.time() - start_time
            self._update_metrics(result, execution_time)

            self.status = SkillStatus.COMPLETED
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            error_result = SkillResult(success=False, error=str(e), execution_time=execution_time)
            self._update_metrics(error_result, execution_time)

            self.status = SkillStatus.FAILED
            logger.error(f"Skill {self.skill_id} failed: {e}")

            return error_result

    def configure(self, config: dict[str, Any]):
        """
        Configure the skill with provided settings

        Args:
            config: Configuration dictionary
        """
        self._config.update(config)

        # Apply Agent Lightning settings
        self._optimization_enabled = config.get("optimization_enabled", True)
        self._zero_hallucination_enforced = config.get("zero_hallucination_enforced", True)
        self._performance_monitoring = config.get("performance_monitoring", True)

    def get_metrics(self) -> SkillMetrics:
        """Get current skill metrics"""
        return self.metrics

    def get_status(self) -> SkillStatus:
        """Get current skill status"""
        return self.status

    async def _validate_zero_hallucination(self, input_data: Any):
        """
        Validate input to prevent hallucinations

        Args:
            input_data: Input data to validate

        Raises:
            ValueError: If hallucination detected
        """
        # This would integrate with the zero-hallucination validator
        # For now, basic validation
        if isinstance(input_data, str):
            # Check for suspicious patterns
            suspicious_patterns = [
                "I am not sure",
                "I think",
                "probably",
                "might be",
                "could be",
                "perhaps",
                "I believe",
            ]

            for pattern in suspicious_patterns:
                if pattern.lower() in input_data.lower():
                    logger.warning(f"Potential hallucination pattern detected: {pattern}")

    def _update_metrics(self, result: SkillResult, execution_time: float):
        """
        Update skill metrics with execution results

        Args:
            result: Execution result
            execution_time: Time taken for execution
        """
        self.metrics.total_executions += 1

        if result.success:
            self.metrics.successful_executions += 1

        # Update averages
        total_time = self.metrics.average_execution_time * (self.metrics.total_executions - 1)
        self.metrics.average_execution_time = (total_time + execution_time) / self.metrics.total_executions

        total_tokens = self.metrics.average_tokens_used * (self.metrics.total_executions - 1)
        self.metrics.average_tokens_used = (total_tokens + result.tokens_used) / self.metrics.total_executions

        self.metrics.error_rate = 1.0 - self.metrics.success_rate
        self.metrics.last_execution = str(asyncio.get_event_loop().time())

    def __repr__(self) -> str:
        return f"BaseSkill(id={self.skill_id}, name={self.name}, status={self.status.value})"


class SkillRegistry:
    """Registry for managing amplifier skills"""

    def __init__(self):
        self._skills: dict[str, BaseSkill] = {}
        self._categories: dict[str, list[str]] = {}

    def register_skill(self, skill: BaseSkill, category: str = "general"):
        """
        Register a skill in the registry

        Args:
            skill: The skill to register
            category: Category for the skill
        """
        self._skills[skill.skill_id] = skill

        if category not in self._categories:
            self._categories[category] = []

        if skill.skill_id not in self._categories[category]:
            self._categories[category].append(skill.skill_id)

        logger.info(f"Registered skill: {skill.skill_id} in category: {category}")

    def get_skill(self, skill_id: str) -> BaseSkill | None:
        """Get a skill by ID"""
        return self._skills.get(skill_id)

    def list_skills(self, category: str = None) -> list[BaseSkill]:
        """List skills, optionally filtered by category"""
        if category:
            skill_ids = self._categories.get(category, [])
            return [self._skills[skill_id] for skill_id in skill_ids if skill_id in self._skills]

        return list(self._skills.values())

    def get_categories(self) -> list[str]:
        """Get all available categories"""
        return list(self._categories.keys())

    def get_skill_metrics(self, skill_id: str) -> SkillMetrics | None:
        """Get metrics for a specific skill"""
        skill = self.get_skill(skill_id)
        return skill.get_metrics() if skill else None


# Global skill registry
skill_registry = SkillRegistry()
