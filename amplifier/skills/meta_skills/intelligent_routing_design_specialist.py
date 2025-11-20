"""
Intelligent Routing Design Specialist

A meta-skill that provides compound multiplier benefits by optimizing skill
selection, routing, and combination recommendations. This specialist analyzes
user requirements and recommends optimal skill combinations with minimal context
overhead, performance prediction, and learning-based optimization.

Core Functionality:
- Intelligent skill analysis and requirement mapping
- Optimal routing with minimal context overhead
- Dependency management and execution order optimization
- Performance prediction and resource requirement estimation
- Compound effect optimization and synergistic skill combinations
- Learning system for routing pattern improvement
- Agent-optimized routing decisions with sub-second decisions
"""

import json
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

from ...utils.logger import get_logger
from ..mcp_storage.skill_repository_manager import get_skill_repository
from ..skills_framework import BaseSkill
from ..skills_framework import SkillContext
from ..skills_framework import SkillLevel
from ..skills_framework import SkillResult

logger = get_logger(__name__)


class RoutingStrategy(Enum):
    """Routing strategies for different optimization goals."""

    PERFORMANCE = "performance"  # Optimize for speed and efficiency
    ACCURACY = "accuracy"  # Optimize for result quality
    TOKEN_EFFICIENCY = "token_efficiency"  # Optimize for minimal token usage
    BALANCED = "balanced"  # Balanced approach across all metrics
    SYNERGY = "synergy"  # Optimize for skill combination synergies


class SkillComplexity(Enum):
    """Complexity levels for skills."""

    TRIVIAL = "trivial"  # < 50 tokens, < 1s execution
    SIMPLE = "simple"  # < 200 tokens, < 5s execution
    MODERATE = "moderate"  # < 500 tokens, < 15s execution
    COMPLEX = "complex"  # < 1000 tokens, < 30s execution
    INTENSIVE = "intensive"  # > 1000 tokens, > 30s execution


@dataclass
class SkillCapability:
    """Capability definition for skill matching."""

    name: str
    description: str
    input_types: list[str]
    output_types: list[str]
    complexity: SkillComplexity
    estimated_tokens: int
    estimated_time: float
    dependencies: list[str] = field(default_factory=list)
    synergistic_skills: list[str] = field(default_factory=list)
    success_rate: float = 0.95
    tags: list[str] = field(default_factory=list)


@dataclass
class SkillCombination:
    """Optimal skill combination with execution plan."""

    skills: list[str]
    execution_order: list[str]
    estimated_tokens: int
    estimated_time: float
    confidence: float
    strategy: RoutingStrategy
    dependencies: list[str] = field(default_factory=list)
    synergistic_benefits: dict[str, float] = field(default_factory=dict)
    reasoning: str = ""


@dataclass
class RoutingMetrics:
    """Performance metrics for routing decisions."""

    routing_accuracy: float = 0.0
    prediction_error: float = 0.0
    optimization_success: float = 0.0
    context_savings: float = 0.0
    total_routes: int = 0
    successful_routes: int = 0
    average_tokens_saved: int = 0
    average_time_saved: float = 0.0


class SkillCapabilityDatabase:
    """Database of skill capabilities and performance metrics."""

    def __init__(self):
        self.capabilities: dict[str, SkillCapability] = {}
        self.performance_history: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.synergy_matrix: dict[tuple[str, str], float] = {}
        self.dependency_graph: dict[str, set[str]] = defaultdict(set)

    def register_skill_capability(self, skill_id: str, capability: SkillCapability) -> None:
        """Register a skill capability."""
        self.capabilities[skill_id] = capability

        # Update dependency graph
        for dep in capability.dependencies:
            self.dependency_graph[skill_id].add(dep)

        logger.debug(f"Registered capability for skill: {skill_id}")

    def get_capability(self, skill_id: str) -> SkillCapability | None:
        """Get skill capability by ID."""
        return self.capabilities.get(skill_id)

    def update_performance(self, skill_id: str, metrics: dict[str, Any]) -> None:
        """Update performance metrics for a skill."""
        self.performance_history[skill_id].append({"timestamp": datetime.now().isoformat(), **metrics})

        # Keep only last 100 records
        if len(self.performance_history[skill_id]) > 100:
            self.performance_history[skill_id] = self.performance_history[skill_id][-100:]

    def get_synergy_score(self, skill1: str, skill2: str) -> float:
        """Get synergy score between two skills."""
        key = tuple(sorted([skill1, skill2]))
        return self.synergy_matrix.get(key, 0.0)

    def set_synergy_score(self, skill1: str, skill2: str, score: float) -> None:
        """Set synergy score between two skills."""
        key = tuple(sorted([skill1, skill2]))
        self.synergy_matrix[key] = max(0.0, min(1.0, score))


class IntelligentRoutingDesignSpecialist(BaseSkill):
    """
    Intelligent Routing Design Specialist meta-skill.

    Provides compound multiplier benefits by optimizing skill selection, routing,
    and combination recommendations with machine learning-based optimization.
    """

    def __init__(self):
        super().__init__()
        self.skill_name = "intelligent_routing_design_specialist"

        # Core components
        self.capability_db = SkillCapabilityDatabase()
        self.skill_repository = get_skill_repository()
        self.routing_metrics = RoutingMetrics()

        # Learning components
        self.routing_patterns: dict[str, list[SkillCombination]] = defaultdict(list)
        self.user_preferences: dict[str, dict[str, Any]] = {}
        self.performance_cache: dict[str, SkillCombination] = {}

        # Initialize with known skill capabilities
        self._initialize_skill_capabilities()

    @property
    def description(self) -> str:
        """Clear, concise description of what this skill does."""
        return (
            "Intelligent routing specialist that optimizes skill selection, "
            "execution order, and combination strategies for maximum efficiency "
            "and compound multiplier benefits."
        )

    @property
    def tags(self) -> list[str]:
        """Tags for skill discovery and matching."""
        return ["routing", "optimization", "meta", "coordination", "performance", "efficiency", "synergy", "automation"]

    def can_handle(self, context: SkillContext) -> float:
        """Determine if this skill can handle the given context."""
        query_lower = context.query.lower()

        # High-confidence indicators
        high_confidence_patterns = [
            "optimize skill",
            "route request",
            "best combination",
            "skill selection",
            "execution order",
            "coordinate skills",
            "efficient workflow",
            "synergistic skills",
            "compound effect",
        ]

        # Medium-confidence indicators
        medium_confidence_patterns = [
            "multiple skills",
            "skill coordination",
            "workflow optimization",
            "process improvement",
            "skill integration",
            "task sequencing",
        ]

        # Check patterns
        for pattern in high_confidence_patterns:
            if pattern in query_lower:
                return 0.9

        for pattern in medium_confidence_patterns:
            if pattern in query_lower:
                return 0.7

        # Check for complexity indicators
        if any(word in query_lower for word in ["complex", "multiple", "many", "coordinate"]):
            return 0.6

        # Check if this involves skill orchestration
        skill_indicators = ["skill", "workflow", "process", "task", "execute"]
        skill_count = sum(1 for indicator in skill_indicators if indicator in query_lower)

        if skill_count >= 2:
            return 0.5

        return 0.2

    def execute(self, context: SkillContext, level: SkillLevel = SkillLevel.SUMMARY) -> SkillResult:
        """Execute the routing specialist skill."""
        start_time = time.time()

        try:
            # Analyze user requirements
            requirements = self._analyze_requirements(context.query)

            # Determine optimal strategy
            strategy = self._determine_strategy(requirements, context)

            # Generate skill combinations
            combinations = self._generate_skill_combinations(requirements, strategy)

            # Select optimal combination
            optimal_combo = self._select_optimal_combination(combinations, strategy)

            # Format result based on level
            content = self._format_result(optimal_combo, requirements, level)

            execution_time = time.time() - start_time
            tokens_used = len(content.split()) * 1.3  # Estimate tokens

            # Update metrics and learning
            self._update_metrics(optimal_combo, success=True)
            self._update_learning_patterns(context.query, optimal_combo)

            return SkillResult(
                skill_name=self.skill_name,
                level=level,
                content=content,
                tokens_used=int(tokens_used),
                execution_time=execution_time,
                metadata={
                    "strategy": strategy.value,
                    "skills_count": len(optimal_combo.skills) if optimal_combo else 0,
                    "estimated_tokens": optimal_combo.estimated_tokens if optimal_combo else 0,
                    "estimated_time": optimal_combo.estimated_time if optimal_combo else 0,
                    "confidence": optimal_combo.confidence if optimal_combo else 0.0,
                },
                next_level_available=level != SkillLevel.FULL,
            )

        except Exception as e:
            logger.error(f"Routing specialist execution failed: {e}")
            execution_time = time.time() - start_time

            return SkillResult(
                skill_name=self.skill_name,
                level=level,
                content=f"Routing analysis failed: {str(e)}",
                tokens_used=100,
                execution_time=execution_time,
                next_level_available=False,
            )

    def _analyze_requirements(self, query: str) -> dict[str, Any]:
        """Analyze user requirements from query."""
        requirements = {
            "primary_goal": self._extract_primary_goal(query),
            "constraints": self._extract_constraints(query),
            "preferences": self._extract_preferences(query),
            "complexity_indicators": self._assess_complexity(query),
            "context_needs": self._assess_context_needs(query),
        }

        return requirements

    def _extract_primary_goal(self, query: str) -> str:
        """Extract the primary goal from the query."""
        query_lower = query.lower()

        goal_patterns = {
            "performance": ["fast", "quick", "efficient", "optimize", "speed"],
            "accuracy": ["accurate", "precise", "quality", "best", "reliable"],
            "efficiency": ["efficient", "minimal", "save", "reduce"],
            "coordination": ["coordinate", "orchestrate", "manage", "organize"],
            "integration": ["integrate", "combine", "merge", "unify"],
        }

        scores = {}
        for goal, keywords in goal_patterns.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            scores[goal] = score

        return max(scores.items(), key=lambda x: x[1])[0] if any(scores.values()) else "balanced"

    def _extract_constraints(self, query: str) -> list[str]:
        """Extract constraints from the query."""
        query_lower = query.lower()

        constraints = []
        if any(word in query_lower for word in ["quick", "fast", "asap"]):
            constraints.append("time_critical")
        if any(word in query_lower for word in ["minimal", "few", "less"]):
            constraints.append("resource_minimal")
        if any(word in query_lower for word in ["accurate", "precise", "reliable"]):
            constraints.append("high_quality")
        if "simple" in query_lower or "easy" in query_lower:
            constraints.append("simplicity")

        return constraints

    def _extract_preferences(self, query: str) -> dict[str, Any]:
        """Extract user preferences from query."""
        query_lower = query.lower()

        preferences = {}

        # Strategy preferences
        if "performance" in query_lower:
            preferences["strategy"] = RoutingStrategy.PERFORMANCE
        elif "accuracy" in query_lower:
            preferences["strategy"] = RoutingStrategy.ACCURACY
        elif "efficient" in query_lower:
            preferences["strategy"] = RoutingStrategy.TOKEN_EFFICIENCY
        elif "synergy" in query_lower or "combine" in query_lower:
            preferences["strategy"] = RoutingStrategy.SYNERGY
        else:
            preferences["strategy"] = RoutingStrategy.BALANCED

        return preferences

    def _assess_complexity(self, query: str) -> dict[str, Any]:
        """Assess complexity indicators from the query."""
        words = query.split()
        sentences = query.split(".")

        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "has_multiple_goals": any(word in query.lower() for word in ["and", "also", "plus", "additionally"]),
            "has_conditional_logic": any(word in query.lower() for word in ["if", "when", "unless", "depending"]),
            "technical_complexity": self._assess_technical_complexity(query),
        }

    def _assess_technical_complexity(self, query: str) -> str:
        """Assess technical complexity of the query."""
        technical_indicators = [
            "api",
            "database",
            "algorithm",
            "system",
            "architecture",
            "integration",
            "deployment",
            "optimization",
            "performance",
        ]

        count = sum(1 for indicator in technical_indicators if indicator in query.lower())

        if count >= 4:
            return "high"
        if count >= 2:
            return "medium"
        if count >= 1:
            return "low"
        return "minimal"

    def _assess_context_needs(self, query: str) -> dict[str, Any]:
        """Assess context requirements."""
        query_lower = query.lower()

        needs = {
            "requires_detailed_analysis": any(word in query_lower for word in ["analyze", "detailed", "comprehensive"]),
            "requires_historical_data": any(word in query_lower for word in ["previous", "history", "past", "before"]),
            "requires_current_state": any(word in query_lower for word in ["current", "now", "present", "status"]),
            "requires_planning": any(word in query_lower for word in ["plan", "strategy", "approach", "method"]),
        }

        return needs

    def _determine_strategy(self, requirements: dict[str, Any], context: SkillContext) -> RoutingStrategy:
        """Determine optimal routing strategy based on requirements."""
        # User-specified strategy takes precedence
        if "strategy" in requirements["preferences"]:
            return requirements["preferences"]["strategy"]

        # Time-critical needs performance strategy
        if "time_critical" in requirements["constraints"]:
            return RoutingStrategy.PERFORMANCE

        # Resource constraints need token efficiency
        if "resource_minimal" in requirements["constraints"]:
            return RoutingStrategy.TOKEN_EFFICIENCY

        # High accuracy needs accuracy strategy
        if "high_quality" in requirements["constraints"]:
            return RoutingStrategy.ACCURACY

        # Complex coordination needs synergy strategy
        if requirements["complexity_indicators"]["has_multiple_goals"]:
            return RoutingStrategy.SYNERGY

        # Default to balanced
        return RoutingStrategy.BALANCED

    def _generate_skill_combinations(
        self, requirements: dict[str, Any], strategy: RoutingStrategy
    ) -> list[SkillCombination]:
        """Generate potential skill combinations based on requirements."""
        combinations = []

        # Get available skills
        available_skills = list(self.capability_db.capabilities.keys())

        # Generate combinations based on strategy
        if strategy == RoutingStrategy.SYNERGY:
            combinations.extend(self._generate_synergy_combinations(available_skills))
        elif strategy == RoutingStrategy.PERFORMANCE:
            combinations.extend(self._generate_performance_combinations(available_skills))
        elif strategy == RoutingStrategy.ACCURACY:
            combinations.extend(self._generate_accuracy_combinations(available_skills))
        elif strategy == RoutingStrategy.TOKEN_EFFICIENCY:
            combinations.extend(self._generate_efficiency_combinations(available_skills))
        else:
            combinations.extend(self._generate_balanced_combinations(available_skills))

        # Filter and rank combinations
        valid_combinations = []
        for combo in combinations:
            if self._validate_combination(combo, requirements):
                combo.confidence = self._calculate_combination_confidence(combo, requirements, strategy)
                valid_combinations.append(combo)

        # Sort by confidence
        valid_combinations.sort(key=lambda x: x.confidence, reverse=True)

        return valid_combinations[:10]  # Return top 10 combinations

    def _generate_synergy_combinations(self, available_skills: list[str]) -> list[SkillCombination]:
        """Generate combinations optimized for synergistic effects."""
        combinations = []

        # Find skill pairs with high synergy
        for i, skill1 in enumerate(available_skills):
            synergistic_skills = []

            for skill2 in available_skills[i + 1 :]:
                synergy_score = self.capability_db.get_synergy_score(skill1, skill2)
                if synergy_score > 0.7:
                    synergistic_skills.append(skill2)

            if synergistic_skills:
                # Create combination with primary skill and synergistic partners
                combo_skills = [skill1] + synergistic_skills[:3]  # Limit to 4 skills max
                combination = self._create_combination(combo_skills, RoutingStrategy.SYNERGY)
                combinations.append(combination)

        return combinations

    def _generate_performance_combinations(self, available_skills: list[str]) -> list[SkillCombination]:
        """Generate combinations optimized for performance."""
        # Sort by estimated time
        sorted_skills = sorted(
            available_skills,
            key=lambda s: self.capability_db.get_capability(s).estimated_time
            if self.capability_db.get_capability(s)
            else float("inf"),
        )

        combinations = []

        # Fast single-skill combinations
        for skill in sorted_skills[:5]:
            combination = self._create_combination([skill], RoutingStrategy.PERFORMANCE)
            combinations.append(combination)

        # Fast multi-skill combinations (up to 3 skills)
        for i in range(min(3, len(sorted_skills))):
            for j in range(i + 1, min(i + 3, len(sorted_skills))):
                combo_skills = [sorted_skills[i], sorted_skills[j]]
                combination = self._create_combination(combo_skills, RoutingStrategy.PERFORMANCE)
                combinations.append(combination)

        return combinations

    def _generate_accuracy_combinations(self, available_skills: list[str]) -> list[SkillCombination]:
        """Generate combinations optimized for accuracy."""
        # Sort by success rate
        sorted_skills = sorted(
            available_skills,
            key=lambda s: self.capability_db.get_capability(s).success_rate
            if self.capability_db.get_capability(s)
            else 0.0,
            reverse=True,
        )

        combinations = []

        # High-accuracy combinations
        for skill in sorted_skills[:5]:
            if self.capability_db.get_capability(skill).success_rate >= 0.9:
                combination = self._create_combination([skill], RoutingStrategy.ACCURACY)
                combinations.append(combination)

        # Complementary high-accuracy pairs
        for i in range(min(3, len(sorted_skills))):
            for j in range(i + 1, min(i + 4, len(sorted_skills))):
                if (
                    self.capability_db.get_capability(sorted_skills[i]).success_rate >= 0.9
                    and self.capability_db.get_capability(sorted_skills[j]).success_rate >= 0.85
                ):
                    combo_skills = [sorted_skills[i], sorted_skills[j]]
                    combination = self._create_combination(combo_skills, RoutingStrategy.ACCURACY)
                    combinations.append(combination)

        return combinations

    def _generate_efficiency_combinations(self, available_skills: list[str]) -> list[SkillCombination]:
        """Generate combinations optimized for token efficiency."""
        # Sort by estimated tokens
        sorted_skills = sorted(
            available_skills,
            key=lambda s: self.capability_db.get_capability(s).estimated_tokens
            if self.capability_db.get_capability(s)
            else float("inf"),
        )

        combinations = []

        # Low-token single-skill combinations
        for skill in sorted_skills[:5]:
            cap = self.capability_db.get_capability(skill)
            if cap and cap.estimated_tokens <= 200:
                combination = self._create_combination([skill], RoutingStrategy.TOKEN_EFFICIENCY)
                combinations.append(combination)

        # Low-token pairs
        for i in range(min(4, len(sorted_skills))):
            cap1 = self.capability_db.get_capability(sorted_skills[i])
            if not cap1 or cap1.estimated_tokens > 150:
                continue

            for j in range(i + 1, min(i + 3, len(sorted_skills))):
                cap2 = self.capability_db.get_capability(sorted_skills[j])
                if not cap2 or cap2.estimated_tokens > 150:
                    continue

                combo_skills = [sorted_skills[i], sorted_skills[j]]
                combination = self._create_combination(combo_skills, RoutingStrategy.TOKEN_EFFICIENCY)
                combinations.append(combination)

        return combinations

    def _generate_balanced_combinations(self, available_skills: list[str]) -> list[SkillCombination]:
        """Generate balanced combinations across all metrics."""
        combinations = []

        # Single-skill balanced options
        for skill in available_skills[:5]:
            combination = self._create_combination([skill], RoutingStrategy.BALANCED)
            combinations.append(combination)

        # Two-skill balanced combinations
        for i in range(min(3, len(available_skills))):
            for j in range(i + 1, min(i + 4, len(available_skills))):
                combo_skills = [available_skills[i], available_skills[j]]
                combination = self._create_combination(combo_skills, RoutingStrategy.BALANCED)
                combinations.append(combination)

        return combinations

    def _create_combination(self, skills: list[str], strategy: RoutingStrategy) -> SkillCombination:
        """Create a skill combination with calculated metrics."""
        total_tokens = 0
        total_time = 0
        dependencies = set()
        synergistic_benefits = {}

        # Calculate totals and dependencies
        for skill in skills:
            capability = self.capability_db.get_capability(skill)
            if capability:
                total_tokens += capability.estimated_tokens
                total_time += capability.estimated_time
                dependencies.update(capability.dependencies)

        # Calculate synergistic benefits
        for i, skill1 in enumerate(skills):
            for skill2 in skills[i + 1 :]:
                synergy = self.capability_db.get_synergy_score(skill1, skill2)
                if synergy > 0:
                    synergistic_benefits[f"{skill1}+{skill2}"] = synergy
                    # Apply synergy bonus (reduced time/tokens)
                    synergy_bonus = synergy * 0.2  # Up to 20% improvement
                    total_time *= 1 - synergy_bonus
                    total_tokens *= 1 - synergy_bonus

        # Determine optimal execution order (dependencies first)
        execution_order = self._resolve_execution_order(skills, list(dependencies))

        return SkillCombination(
            skills=skills,
            execution_order=execution_order,
            estimated_tokens=int(total_tokens),
            estimated_time=total_time,
            confidence=0.0,  # Will be calculated later
            strategy=strategy,
            dependencies=list(dependencies),
            synergistic_benefits=synergistic_benefits,
            reasoning="",  # Will be generated later
        )

    def _resolve_execution_order(self, skills: list[str], dependencies: list[str]) -> list[str]:
        """Resolve optimal execution order based on dependencies."""
        # Simple dependency resolution - skills with no dependencies first
        ordered = []
        remaining = skills.copy()

        while remaining:
            # Find skills with no unmet dependencies
            ready_skills = []
            for skill in remaining:
                capability = self.capability_db.get_capability(skill)
                if capability:
                    deps_met = all(dep in ordered for dep in capability.dependencies if dep in skills)
                    if deps_met:
                        ready_skills.append(skill)
                else:
                    ready_skills.append(skill)  # No capability info, assume ready

            if not ready_skills:
                # Circular dependency or missing info, add remaining skills
                ordered.extend(remaining)
                break

            # Add ready skills (prefer simpler ones first)
            ready_skills.sort(
                key=lambda s: self.capability_db.get_capability(s).estimated_time
                if self.capability_db.get_capability(s)
                else float("inf")
            )
            ordered.append(ready_skills[0])
            remaining.remove(ready_skills[0])

        return ordered

    def _validate_combination(self, combination: SkillCombination, requirements: dict[str, Any]) -> bool:
        """Validate if combination meets requirements."""
        # Check constraints
        if "resource_minimal" in requirements["constraints"]:
            if combination.estimated_tokens > 500:
                return False
            if combination.estimated_time > 30:
                return False

        if "time_critical" in requirements["constraints"]:
            if combination.estimated_time > 15:
                return False

        if "simplicity" in requirements["constraints"]:
            if len(combination.skills) > 2:
                return False

        return True

    def _calculate_combination_confidence(
        self, combination: SkillCombination, requirements: dict[str, Any], strategy: RoutingStrategy
    ) -> float:
        """Calculate confidence score for a combination."""
        confidence = 0.5  # Base confidence

        # Strategy alignment
        if strategy == RoutingStrategy.PERFORMANCE:
            # Prefer faster combinations
            time_score = max(0, 1 - (combination.estimated_time / 60))  # 60s as max acceptable
            confidence += time_score * 0.3
        elif strategy == RoutingStrategy.ACCURACY:
            # Prefer high success rate skills
            avg_success = sum(
                self.capability_db.get_capability(skill).success_rate
                for skill in combination.skills
                if self.capability_db.get_capability(skill)
            ) / len(combination.skills)
            confidence += (avg_success - 0.5) * 0.6
        elif strategy == RoutingStrategy.TOKEN_EFFICIENCY:
            # Prefer low token usage
            token_score = max(0, 1 - (combination.estimated_tokens / 1000))  # 1000 tokens as max
            confidence += token_score * 0.3
        elif strategy == RoutingStrategy.SYNERGY:
            # Prefer high synergy
            if combination.synergistic_benefits:
                avg_synergy = sum(combination.synergistic_benefits.values()) / len(combination.synergistic_benefits)
                confidence += avg_synergy * 0.4

        # Synergy bonus
        if combination.synergistic_benefits:
            synergy_bonus = sum(combination.synergistic_benefits.values()) / len(combination.synergistic_benefits)
            confidence += synergy_bonus * 0.2

        # Complexity penalty (prefer simpler solutions)
        complexity_penalty = min(0.2, len(combination.skills) * 0.05)
        confidence -= complexity_penalty

        return max(0.0, min(1.0, confidence))

    def _select_optimal_combination(
        self, combinations: list[SkillCombination], strategy: RoutingStrategy
    ) -> SkillCombination | None:
        """Select the optimal combination from candidates."""
        if not combinations:
            return None

        # Add reasoning to top combinations
        for combo in combinations[:3]:
            combo.reasoning = self._generate_combination_reasoning(combo, strategy)

        # Return highest confidence combination
        return combinations[0]

    def _generate_combination_reasoning(self, combination: SkillCombination, strategy: RoutingStrategy) -> str:
        """Generate reasoning for why this combination was selected."""
        reasons = []

        # Strategy-specific reasoning
        if strategy == RoutingStrategy.PERFORMANCE:
            reasons.append(f"Optimized for speed with {combination.estimated_time:.1f}s estimated execution time")
        elif strategy == RoutingStrategy.ACCURACY:
            avg_success = sum(
                self.capability_db.get_capability(skill).success_rate
                for skill in combination.skills
                if self.capability_db.get_capability(skill)
            ) / len(combination.skills)
            reasons.append(f"High accuracy with {avg_success:.1%} average success rate")
        elif strategy == RoutingStrategy.TOKEN_EFFICIENCY:
            reasons.append(f"Token efficient with {combination.estimated_tokens} estimated tokens")
        elif strategy == RoutingStrategy.SYNERGY:
            synergy_count = len(combination.synergistic_benefits)
            reasons.append(f"Optimized synergistic effects with {synergy_count} skill pairings")

        # Synergy reasoning
        if combination.synergistic_benefits:
            top_synergy = max(combination.synergistic_benefits.items(), key=lambda x: x[1])
            reasons.append(f"Strong synergy between {top_synergy[0]} ({top_synergy[1]:.1%} benefit)")

        # Complexity reasoning
        if len(combination.skills) == 1:
            reasons.append("Simple, focused approach with single skill")
        elif len(combination.skills) <= 3:
            reasons.append(f"Balanced complexity with {len(combination.skills)} coordinated skills")
        else:
            reasons.append(f"Comprehensive approach using {len(combination.skills)} skills")

        return "; ".join(reasons)

    def _format_result(
        self, combination: SkillCombination | None, requirements: dict[str, Any], level: SkillLevel
    ) -> str:
        """Format the result based on skill level."""
        if not combination:
            return "No suitable skill combination found for the given requirements."

        if level == SkillLevel.METADATA:
            return json.dumps(
                {
                    "skills_count": len(combination.skills),
                    "estimated_tokens": combination.estimated_tokens,
                    "estimated_time": combination.estimated_time,
                    "strategy": combination.strategy.value,
                    "confidence": combination.confidence,
                }
            )

        if level == SkillLevel.SUMMARY:
            result = [
                "**Optimal Skill Combination Found**",
                f"Strategy: {combination.strategy.value.title()}",
                f"Skills: {', '.join(combination.skills)}",
                f"Estimated: {combination.estimated_tokens} tokens, {combination.estimated_time:.1f}s",
                f"Confidence: {combination.confidence:.1%}",
                f"Execution Order: {' → '.join(combination.execution_order)}",
            ]

            if combination.synergistic_benefits:
                result.append(f"Synergistic Benefits: {len(combination.synergistic_benefits)} skill pairings")

            return "\n".join(result)

        # FULL level
        result = [
            "# Intelligent Routing Design Specialist Analysis",
            "",
            "## Requirements Analysis",
            f"- Primary Goal: {requirements['primary_goal']}",
            f"- Constraints: {', '.join(requirements['constraints']) if requirements['constraints'] else 'None'}",
            f"- Complexity: {requirements['complexity_indicators']['technical_complexity']}",
            "",
            "## Optimal Skill Combination",
            f"**Strategy:** {combination.strategy.value.title()}",
            f"**Confidence:** {combination.confidence:.1%}",
            "",
            f"### Skills ({len(combination.skills)})",
            "",
        ]

        for i, skill in enumerate(combination.execution_order, 1):
            capability = self.capability_db.get_capability(skill)
            if capability:
                result.append(
                    f"{i}. **{skill}** - {capability.description}\n"
                    f"   - Complexity: {capability.complexity.value}\n"
                    f"   - Est. Tokens: {capability.estimated_tokens}\n"
                    f"   - Est. Time: {capability.estimated_time:.1f}s\n"
                    f"   - Success Rate: {capability.success_rate:.1%}"
                )
            else:
                result.append(f"{i}. **{skill}")
            result.append("")

        result.extend(
            [
                "### Execution Metrics",
                f"- **Total Estimated Tokens:** {combination.estimated_tokens:,}",
                f"- **Total Estimated Time:** {combination.estimated_time:.1f} seconds",
                f"- **Optimal Execution Order:** {' → '.join(combination.execution_order)}",
                "",
                "### Synergistic Benefits",
            ]
        )

        if combination.synergistic_benefits:
            for pair, benefit in combination.synergistic_benefits.items():
                result.append(f"- **{pair}:** {benefit:.1%} efficiency gain")
        else:
            result.append("- No significant synergistic benefits detected")

        result.extend(
            [
                "",
                "### Reasoning",
                combination.reasoning,
                "",
                "### Dependencies",
            ]
        )

        if combination.dependencies:
            for dep in combination.dependencies:
                result.append(f"- {dep}")
        else:
            result.append("- No external dependencies required")

        result.extend(
            [
                "",
                "### Recommendations",
                "- Execute skills in the recommended order for optimal performance",
                "- Monitor execution metrics and adjust if necessary",
                "- Consider caching results for repeated use patterns",
            ]
        )

        return "\n".join(result)

    def _update_metrics(self, combination: SkillCombination | None, success: bool) -> None:
        """Update routing metrics."""
        if not combination:
            return

        self.routing_metrics.total_routes += 1

        if success:
            self.routing_metrics.successful_routes += 1

        self.routing_metrics.routing_accuracy = (
            self.routing_metrics.successful_routes / self.routing_metrics.total_routes
        )

    def _update_learning_patterns(self, query: str, combination: SkillCombination | None) -> None:
        """Update learning patterns for future routing decisions."""
        if not combination:
            return

        # Create pattern key
        pattern_key = self._create_pattern_key(query)

        # Store successful pattern
        self.routing_patterns[pattern_key].append(combination)

        # Keep only recent patterns (last 10)
        if len(self.routing_patterns[pattern_key]) > 10:
            self.routing_patterns[pattern_key] = self.routing_patterns[pattern_key][-10:]

        # Update synergy scores based on successful execution
        for i, skill1 in enumerate(combination.skills):
            for skill2 in combination.skills[i + 1 :]:
                current_synergy = self.capability_db.get_synergy_score(skill1, skill2)
                # Incrementally improve synergy score
                new_synergy = min(1.0, current_synergy + 0.01)
                self.capability_db.set_synergy_score(skill1, skill2, new_synergy)

    def _create_pattern_key(self, query: str) -> str:
        """Create a pattern key for learning."""
        # Extract key terms and normalize
        words = re.findall(r"\w+", query.lower())

        # Remove common stop words
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        key_words = [w for w in words if w not in stop_words and len(w) > 2]

        # Return first 3-5 key words
        return "_".join(key_words[:5])

    def _initialize_skill_capabilities(self) -> None:
        """Initialize known skill capabilities."""
        # Context management skills
        self.capability_db.register_skill_capability(
            "context_compactor",
            SkillCapability(
                name="context_compactor",
                description="Compresses and optimizes conversation context",
                input_types=["conversation", "context"],
                output_types=["compressed_context", "summary"],
                complexity=SkillComplexity.MODERATE,
                estimated_tokens=300,
                estimated_time=8.0,
                tags=["context", "optimization", "compression"],
            ),
        )

        self.capability_db.register_skill_capability(
            "token_budget",
            SkillCapability(
                name="token_budget",
                description="Manages and optimizes token usage",
                input_types=["tokens", "budget"],
                output_types=["optimized_tokens", "allocation"],
                complexity=SkillComplexity.SIMPLE,
                estimated_tokens=150,
                estimated_time=3.0,
                tags=["tokens", "budget", "efficiency"],
            ),
        )

        # Discovery skills
        self.capability_db.register_skill_capability(
            "skill_matcher",
            SkillCapability(
                name="skill_matcher",
                description="Matches queries to appropriate skills",
                input_types=["query", "context"],
                output_types=["skill_recommendations", "matches"],
                complexity=SkillComplexity.MODERATE,
                estimated_tokens=200,
                estimated_time=5.0,
                tags=["matching", "discovery", "recommendation"],
            ),
        )

        # Meta skills
        self.capability_db.register_skill_capability(
            "intelligent_routing",
            SkillCapability(
                name="intelligent_routing",
                description="Optimizes skill selection and execution order",
                input_types=["requirements", "skills"],
                output_types=["routing_plan", "optimization"],
                complexity=SkillComplexity.COMPLEX,
                estimated_tokens=500,
                estimated_time=12.0,
                tags=["routing", "optimization", "meta"],
            ),
        )

        # Set some initial synergy scores
        self.capability_db.set_synergy_score("context_compactor", "token_budget", 0.8)
        self.capability_db.set_synergy_score("skill_matcher", "intelligent_routing", 0.9)
        self.capability_db.set_synergy_score("context_compactor", "skill_matcher", 0.6)

    def get_routing_metrics(self) -> RoutingMetrics:
        """Get current routing metrics."""
        return self.routing_metrics

    def optimize_for_context(self, available_tokens: int, time_limit: float) -> SkillCombination:
        """Optimize routing for specific context constraints."""
        # Create context requirements
        requirements = {"constraints": [], "primary_goal": "balanced"}

        if available_tokens < 500:
            requirements["constraints"].append("resource_minimal")

        if time_limit < 10:
            requirements["constraints"].append("time_critical")

        strategy = self._determine_strategy(requirements, SkillContext("", [], available_tokens))
        combinations = self._generate_skill_combinations(requirements, strategy)
        optimal = self._select_optimal_combination(combinations, strategy)

        return optimal or SkillCombination([], [], 0, 0, 0, strategy)


# Global instance
_intelligent_routing_specialist = None


def get_intelligent_routing_specialist() -> IntelligentRoutingDesignSpecialist:
    """Get the global intelligent routing specialist instance."""
    global _intelligent_routing_specialist
    if _intelligent_routing_specialist is None:
        _intelligent_routing_specialist = IntelligentRoutingDesignSpecialist()
    return _intelligent_routing_specialist
