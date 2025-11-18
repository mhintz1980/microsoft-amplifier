"""
Skills Framework Template

Base template for creating skills following ruthless simplicity principles.
Each skill is a self-contained module with progressive disclosure capabilities.
"""

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..utils.token_utils import estimate_tokens


class SkillLevel(Enum):
    """Progressive disclosure levels for skills."""

    METADATA = "metadata"  # Minimal info, <50 tokens
    SUMMARY = "summary"  # Key points, <200 tokens
    FULL = "full"  # Complete content


@dataclass
class SkillContext:
    """Context information for skill execution."""

    query: str
    conversation_history: list[dict[str, Any]]
    available_tokens: int
    user_preferences: dict[str, Any] = None


@dataclass
class SkillResult:
    """Result from skill execution with progressive levels."""

    skill_name: str
    level: SkillLevel
    content: str
    tokens_used: int
    execution_time: float
    metadata: dict[str, Any] = None
    next_level_available: bool = True


class BaseSkill(ABC):
    """Base class for all skills following our design principles."""

    def __init__(self):
        self.skill_name = self.__class__.__name__.replace("Skill", "").lower()
        self.last_execution = None
        self.execution_count = 0

    @property
    @abstractmethod
    def description(self) -> str:
        """Clear, concise description of what this skill does."""
        pass

    @property
    @abstractmethod
    def tags(self) -> list[str]:
        """Tags for skill discovery and matching."""
        pass

    @abstractmethod
    def can_handle(self, context: SkillContext) -> float:
        """
        Determine if this skill can handle the given context.
        Returns confidence score (0.0 to 1.0).
        """
        pass

    @abstractmethod
    def execute(self, context: SkillContext, level: SkillLevel = SkillLevel.SUMMARY) -> SkillResult:
        """
        Execute the skill at the specified level.
        Must respect token limits and return structured result.
        """
        pass

    def get_metadata(self) -> dict[str, Any]:
        """Get metadata about this skill for discovery."""
        return {
            "name": self.skill_name,
            "description": self.description,
            "tags": self.tags,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "execution_count": self.execution_count,
        }

    def _validate_result(self, result: SkillResult, context: SkillContext) -> bool:
        """Validate that result respects constraints."""
        if result.tokens_used > context.available_tokens:
            return False
        return not estimate_tokens(result.content) > context.available_tokens


class SkillRegistry:
    """Registry for managing and discovering skills."""

    def __init__(self):
        self._skills: list[BaseSkill] = []
        self._tag_index: dict[str, list[BaseSkill]] = {}

    def register(self, skill: BaseSkill) -> None:
        """Register a new skill."""
        self._skills.append(skill)

        # Update tag index
        for tag in skill.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            self._tag_index[tag].append(skill)

    def find_skills(self, context: SkillContext, min_confidence: float = 0.3) -> list[tuple[BaseSkill, float]]:
        """Find skills that can handle the given context."""
        candidates = []

        for skill in self._skills:
            confidence = skill.can_handle(context)
            if confidence >= min_confidence:
                candidates.append((skill, confidence))

        # Sort by confidence score
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates

    def find_by_tags(self, tags: list[str]) -> list[BaseSkill]:
        """Find skills by tags."""
        matching_skills = set()

        for tag in tags:
            if tag in self._tag_index:
                matching_skills.update(self._tag_index[tag])

        return list(matching_skills)

    def get_all_skills(self) -> list[BaseSkill]:
        """Get all registered skills."""
        return self._skills.copy()


# Global registry instance
_skill_registry = SkillRegistry()


def get_skill_registry() -> SkillRegistry:
    """Get the global skill registry."""
    return _skill_registry


def register_skill(skill: BaseSkill) -> None:
    """Register a skill in the global registry."""
    _skill_registry.register(skill)  # type: ignore  # type: ignore
