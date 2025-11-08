"""
Skill Discovery and Matching

Intelligent skill discovery based on context analysis and semantic matching.
Follows ruthless simplicity with token-efficient operations.
"""

import re
from typing import Any

from ...utils.logger import get_logger
from ..skills_framework.skill_template import BaseSkill
from ..skills_framework.skill_template import SkillContext
from ..skills_framework.skill_template import SkillLevel
from ..skills_framework.skill_template import SkillResult
from ..skills_framework.skill_template import get_skill_registry

logger = get_logger(__name__)


class SkillMatcher:
    """
    Intelligent skill discovery and matching system.
    Finds the best skills for given contexts using semantic analysis.
    """

    def __init__(self):
        self.registry = get_skill_registry()
        self._match_cache: dict[str, list[tuple[BaseSkill, float]]] = {}

    def find_best_skills(self, context: SkillContext, max_skills: int = 3) -> list[tuple[BaseSkill, float]]:
        """
        Find the best matching skills for the given context.
        Returns list of (skill, confidence) tuples.
        """
        # Check cache first
        cache_key = self._cache_key(context)
        if cache_key in self._match_cache:
            cached_results = self._match_cache[cache_key]
            # Return top N results
            return cached_results[:max_skills]

        # Find matching skills
        candidates = self.registry.find_skills(context, min_confidence=0.2)

        # Apply semantic boosting
        boosted_candidates = self._apply_semantic_boosting(candidates, context)

        # Cache results
        self._match_cache[cache_key] = boosted_candidates

        # Return top N results
        return boosted_candidates[:max_skills]

    def execute_best_skill(self, context: SkillContext, level: SkillLevel = SkillLevel.SUMMARY) -> SkillResult:
        """
        Automatically find and execute the best matching skill.
        """
        best_skills = self.find_best_skills(context, max_skills=1)

        if not best_skills:
            return SkillResult(
                skill_name="none",
                level=level,
                content="No suitable skill found for this context.",
                tokens_used=20,
                execution_time=0.0,
                next_level_available=False,
            )

        best_skill, confidence = best_skills[0]

        try:
            result = best_skill.execute(context, level)
            # Add confidence to metadata
            if result.metadata is None:
                result.metadata = {}
            result.metadata["match_confidence"] = confidence
            return result

        except Exception as e:
            logger.error(f"Skill execution failed: {e}")
            return SkillResult(
                skill_name=best_skill.skill_name,
                level=level,
                content=f"Skill execution failed: {str(e)}",
                tokens_used=50,
                execution_time=0.0,
                next_level_available=False,
            )

    def get_skill_recommendations(self, context: SkillContext, limit: int = 5) -> list[dict[str, Any]]:
        """
        Get skill recommendations with explanations.
        """
        candidates = self.find_best_skills(context, max_skills=limit)

        recommendations = []
        for skill, confidence in candidates:
            recommendations.append(
                {
                    "skill_name": skill.skill_name,
                    "description": skill.description,
                    "confidence": confidence,
                    "tags": skill.tags,
                    "reason": self._explain_match(skill, context),
                }
            )

        return recommendations

    def _apply_semantic_boosting(
        self, candidates: list[tuple[BaseSkill, float]], context: SkillContext
    ) -> list[tuple[BaseSkill, float]]:
        """Apply semantic boosting to candidate skills."""
        boosted = []

        for skill, base_confidence in candidates:
            boosted_confidence = base_confidence

            # Boost based on query similarity
            query_boost = self._calculate_query_similarity(skill, context.query)
            boosted_confidence += query_boost * 0.2

            # Boost based on conversation context
            context_boost = self._calculate_context_relevance(skill, context)
            boosted_confidence += context_boost * 0.1

            # Boost based on recent usage (recency bias)
            usage_boost = self._calculate_usage_boost(skill)
            boosted_confidence += usage_boost * 0.05

            # Cap at 1.0
            boosted_confidence = min(boosted_confidence, 1.0)

            boosted.append((skill, boosted_confidence))

        # Sort by boosted confidence
        boosted.sort(key=lambda x: x[1], reverse=True)
        return boosted

    def _calculate_query_similarity(self, skill: BaseSkill, query: str) -> float:
        """Calculate similarity between query and skill."""
        query_lower = query.lower()
        skill_desc_lower = skill.description.lower()

        # Direct keyword matches
        query_words = set(re.findall(r"\w+", query_lower))
        skill_words = set(re.findall(r"\w+", skill_desc_lower))

        if not query_words:
            return 0.0

        # Calculate Jaccard similarity
        intersection = query_words.intersection(skill_words)
        union = query_words.union(skill_words)

        if not union:
            return 0.0

        jaccard = len(intersection) / len(union)

        # Boost for tag matches
        tag_matches = sum(1 for tag in skill.tags if tag.lower() in query_lower)
        tag_boost = min(tag_matches * 0.1, 0.3)

        return min(jaccard + tag_boost, 1.0)

    def _calculate_context_relevance(self, skill: BaseSkill, context: SkillContext) -> float:
        """Calculate relevance based on conversation context."""
        if not context.conversation_history:
            return 0.0

        # Check recent messages for skill-related content
        recent_messages = context.conversation_history[-3:]  # Last 3 messages
        skill_keywords = skill.description.lower().split() + skill.tags

        relevance_score = 0.0
        total_content = 0

        for msg in recent_messages:
            content = msg.get("content", "").lower()
            if not content:
                continue

            total_content += len(content)
            keyword_matches = sum(1 for keyword in skill_keywords if keyword in content)
            relevance_score += keyword_matches

        if total_content == 0:
            return 0.0

        # Normalize by content length
        normalized_score = relevance_score / (total_content / 100)  # Per 100 chars
        return min(normalized_score, 1.0)

    def _calculate_usage_boost(self, skill: BaseSkill) -> float:
        """Calculate boost based on recent skill usage."""
        if skill.execution_count == 0:
            return 0.0

        # Simple recency boost - if used recently, boost slightly
        if skill.last_execution:
            import time

            hours_since_use = (time.time() - skill.last_execution.timestamp()) / 3600

            if hours_since_use < 1:
                return 0.2  # Used within last hour
            if hours_since_use < 24:
                return 0.1  # Used within last day

        return 0.0

    def _explain_match(self, skill: BaseSkill, context: SkillContext) -> str:
        """Generate explanation for why a skill matches."""
        reasons = []

        # Check keyword matches
        query_lower = context.query.lower()
        desc_lower = skill.description.lower()

        for tag in skill.tags:
            if tag.lower() in query_lower:
                reasons.append(f"matches tag '{tag}'")

        # Check description matches
        desc_words = desc_lower.split()
        query_words = query_lower.split()

        matches = set(desc_words).intersection(set(query_words))
        if matches:
            reasons.append(f"matches keywords {list(matches)[:2]}")

        # Check context relevance
        if context.conversation_history:
            recent_content = " ".join(msg.get("content", "").lower() for msg in context.conversation_history[-2:])
            for tag in skill.tags:
                if tag.lower() in recent_content:
                    reasons.append("relevant to recent conversation")
                    break

        if not reasons:
            reasons.append("general semantic match")

        return "; ".join(reasons[:2])  # Limit to top 2 reasons

    def _cache_key(self, context: SkillContext) -> str:
        """Generate cache key for context."""
        # Simple cache based on query and conversation length
        query_hash = hash(context.query.lower())
        conv_length = len(context.conversation_history)
        return f"{query_hash}_{conv_length}"


# Global matcher instance
_skill_matcher = SkillMatcher()


def get_skill_matcher() -> SkillMatcher:
    """Get the global skill matcher instance."""
    return _skill_matcher


def find_and_execute_skill(context: SkillContext, level: SkillLevel = SkillLevel.SUMMARY) -> SkillResult:
    """
    Convenience function to find and execute the best skill.
    """
    matcher = get_skill_matcher()
    return matcher.execute_best_skill(context, level)


def get_skill_recommendations(context: SkillContext, limit: int = 5) -> list[dict[str, Any]]:
    """
    Convenience function to get skill recommendations.
    """
    matcher = get_skill_matcher()
    return matcher.get_skill_recommendations(context, limit)
