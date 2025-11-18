"""
Task Tool Integration for Dynamic Agent Loading

Provides seamless integration between the dynamic agent loading framework
and the existing Task tool workflow.

This module enables the Task tool to use the progressive agent discovery
pattern while maintaining compatibility with existing workflows.
"""

import logging
from typing import Any

from .dynamic_loader import get_agent_loader
from .dynamic_loader import load_agent

logger = logging.getLogger(__name__)


class TaskAgentResolver:
    """
    Resolves agent identifiers for Task tool using dynamic loading.

    Provides intelligent agent selection based on task requirements,
    with fallback to manual agent specification.
    """

    def __init__(self):
        self.loader = get_agent_loader()
        self._ensure_registry()

    def _ensure_registry(self):
        """Ensure agent registry is built"""
        if not self.loader.registry_file.exists():
            logger.info("Building agent registry...")
            self.loader.build_registry()

    def resolve_agent_for_task(
        self,
        task_description: str,
        required_tags: list[str] | None = None,
        preferred_tags: list[str] | None = None,
        manual_agent_id: str | None = None,
    ) -> str | None:
        """
        Resolve the best agent for a given task.

        Args:
            task_description: Description of the task to perform
            required_tags: Tags that agent MUST have
            preferred_tags: Tags that are preferred but not required
            manual_agent_id: Manually specified agent ID (bypasses discovery)

        Returns:
            Agent identifier or None if no suitable agent found
        """
        # Manual specification takes precedence
        if manual_agent_id:
            if manual_agent_id in self.loader.metadata_cache:
                logger.info(f"Using manually specified agent: {manual_agent_id}")
                return manual_agent_id
            logger.warning(f"Manual agent '{manual_agent_id}' not found in registry")
            return None

        # Use intelligent discovery
        return self._discover_best_agent(task_description, required_tags, preferred_tags)

    def _discover_best_agent(
        self,
        task_description: str,
        required_tags: list[str] | None = None,
        preferred_tags: list[str] | None = None,
    ) -> str | None:
        """
        Discover the best agent using multiple search strategies.
        """
        candidates = []

        # Strategy 1: Required tags filter
        if required_tags:
            tag_candidates = self.loader.find_agent_by_tags(required_tags, require_all=True)
            candidates.extend(tag_candidates)

        # Strategy 2: Description search
        desc_candidates = self.loader.find_agent_by_description(task_description)
        candidates.extend(desc_candidates)

        # Strategy 3: Preferred tags (if no candidates yet)
        if not candidates and preferred_tags:
            pref_candidates = self.loader.find_agent_by_tags(preferred_tags, require_all=False)
            candidates.extend(pref_candidates)

        # Strategy 4: Fallback to all agents sorted by relevance
        if not candidates:
            logger.warning("No specific agents found, using fallback strategy")
            candidates = self.loader.list_all_agents()

        # Remove duplicates and score candidates
        scored_candidates = self._score_candidates(candidates, task_description, required_tags, preferred_tags)

        if not scored_candidates:
            logger.warning("No suitable agents found")
            return None

        # Return the best candidate
        best_agent = scored_candidates[0]
        logger.info(f"Selected agent: {best_agent['name']} (score: {best_agent['score']:.2f})")
        return best_agent["agent_id"]

    def _score_candidates(
        self,
        candidates: list,
        task_description: str,
        required_tags: list[str] | None = None,
        preferred_tags: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Score and rank candidates based on relevance.
        """
        scored = []
        task_lower = task_description.lower()

        for agent in candidates:
            score = 0.0

            # Base score for having required tags
            if required_tags:
                required_score = sum(1 for tag in required_tags if tag in agent.tags)
                score += required_score * 10  # High weight for required tags

            # Score for preferred tags
            if preferred_tags:
                preferred_score = sum(1 for tag in preferred_tags if tag in agent.tags)
                score += preferred_score * 5  # Medium weight for preferred tags

            # Score for description keyword matching
            desc_lower = agent.description.lower() + " " + agent.when_to_use.lower()
            keyword_matches = sum(1 for word in task_lower.split() if word in desc_lower)
            score += keyword_matches * 2

            # Score for recency/frequency (agents used more recently get slight boost)
            if agent.load_count > 0:
                score += min(agent.load_count, 5) * 0.1

            # Specialization bonus (agents with fewer tags are more specialized)
            specialization_bonus = max(0, 10 - len(agent.tags)) * 0.5
            score += specialization_bonus

            scored.append(
                {
                    "agent_id": agent.identifier,
                    "name": agent.name,
                    "score": score,
                    "reasoning": self._generate_reasoning(agent, required_tags, preferred_tags, keyword_matches),
                }
            )

        # Sort by score (descending)
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def _generate_reasoning(
        self,
        agent,
        required_tags: list[str] | None = None,
        preferred_tags: list[str] | None = None,
        keyword_matches: int = 0,
    ) -> str:
        """Generate human-readable reasoning for agent selection."""
        reasons = []

        if required_tags:
            matched_required = [tag for tag in required_tags if tag in agent.tags]
            if matched_required:
                reasons.append(f"has required tags: {', '.join(matched_required)}")

        if preferred_tags:
            matched_preferred = [tag for tag in preferred_tags if tag in agent.tags]
            if matched_preferred:
                reasons.append(f"has preferred tags: {', '.join(matched_preferred)}")

        if keyword_matches > 0:
            reasons.append(f"matches {keyword_matches} keywords in description")

        if len(agent.tags) <= 5:
            reasons.append("specialized focus")

        return "; ".join(reasons) if reasons else "general match"

    def get_agent_content_for_task(self, agent_id: str) -> str | None:
        """
        Get full agent content for Task tool execution.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent content or None if loading failed
        """
        result = load_agent(agent_id)
        if result.success:
            return result.content
        logger.error(f"Failed to load agent '{agent_id}': {result.error}")
        return None

    def suggest_alternatives(
        self, task_description: str, excluded_agent_id: str, limit: int = 3
    ) -> list[dict[str, str]]:
        """
        Suggest alternative agents for a task.

        Args:
            task_description: Description of the task
            excluded_agent_id: Agent to exclude from suggestions
            limit: Maximum number of suggestions

        Returns:
            List of alternative agent suggestions
        """
        candidates = self.loader.find_agent_by_description(task_description)

        # Filter out excluded agent
        candidates = [a for a in candidates if a.identifier != excluded_agent_id]

        # Score and rank
        scored = self._score_candidates(candidates, task_description)

        suggestions = []
        for candidate in scored[:limit]:
            suggestions.append(
                {
                    "agent_id": candidate["agent_id"],
                    "name": candidate["name"],
                    "reasoning": candidate["reasoning"],
                    "score": candidate["score"],
                }
            )

        return suggestions

    def get_discovery_stats(self) -> dict[str, Any]:
        """Get statistics about agent discovery and usage."""
        return {
            "registry_stats": self.loader.get_registry_stats(),
            "loaded_agents": len(self.loader.loaded_agents),
            "available_tags": list(self.loader._get_tag_distribution().keys()),
            "total_capacity": self.loader.max_loaded_agents,
        }


# Global resolver instance
_global_resolver: TaskAgentResolver | None = None


def get_task_resolver() -> TaskAgentResolver:
    """Get global task resolver instance"""
    global _global_resolver
    if _global_resolver is None:
        _global_resolver = TaskAgentResolver()
    return _global_resolver


def resolve_agent_for_task(
    task_description: str,
    required_tags: list[str] | None = None,
    preferred_tags: list[str] | None = None,
    manual_agent_id: str | None = None,
) -> str | None:
    """
    Convenience function to resolve agent for task.

    Example:
        # Find agent for architecture task
        agent_id = resolve_agent_for_task(
            "Design a modular authentication system",
            required_tags=['architecture'],
            preferred_tags=['security']
        )
    """
    return get_task_resolver().resolve_agent_for_task(task_description, required_tags, preferred_tags, manual_agent_id)


def get_agent_content(agent_id: str) -> str | None:
    """Convenience function to get agent content"""
    return get_task_resolver().get_agent_content_for_task(agent_id)
