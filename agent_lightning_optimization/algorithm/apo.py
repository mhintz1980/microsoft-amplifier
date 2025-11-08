"""
Automatic Prompt Optimization (APO) Algorithm Implementation for Agent Lightning.

This module implements advanced prompt optimization techniques to replace baseline algorithms
with sophisticated reinforcement learning approaches for mechanical engineering agents.
"""

import random
import re
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np
from pydantic import BaseModel
from pydantic import validator

try:
    from agent_lightning import LightningAgent

    AGENT_LIGHTNING_AVAILABLE = True
except ImportError:
    AGENT_LIGHTNING_AVAILABLE = False

from ..utils.logger import get_logger

logger = get_logger(__name__)


class OptimizationStrategy(Enum):
    """Optimization strategies for prompt engineering."""

    GRADIENT_ASCENT = "gradient_ascent"
    GENETIC_ALGORITHM = "genetic_algorithm"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    EVOLUTIONARY_STRATEGIES = "evolutionary_strategies"


class PromptElementType(Enum):
    """Types of prompt elements that can be optimized."""

    INSTRUCTION = "instruction"
    EXAMPLE = "example"
    CONSTRAINT = "constraint"
    FORMAT_SPECIFIER = "format_specifier"
    CONTEXT_PROVIDER = "context_provider"
    ROLE_DEFINITION = "role_definition"


@dataclass
class PromptElement:
    """Individual element of a prompt that can be optimized."""

    element_type: PromptElementType
    content: str
    weight: float = 1.0
    mutable: bool = True
    position: int = 0

    def clone(self) -> "PromptElement":
        """Create a deep copy of the prompt element."""
        return PromptElement(
            element_type=self.element_type,
            content=self.content,
            weight=self.weight,
            mutable=self.mutable,
            position=self.position,
        )


@dataclass
class PromptTemplate:
    """Optimizable prompt template composed of multiple elements."""

    name: str
    description: str
    elements: list[PromptElement]
    base_reward: float = 0.0
    optimization_history: list[dict[str, Any]] = field(default_factory=list)

    def compile(self) -> str:
        """Compile the prompt template into a single prompt string."""
        sorted_elements = sorted(self.elements, key=lambda x: x.position)
        return "\n".join(elem.content for elem in sorted_elements)

    def clone(self) -> "PromptTemplate":
        """Create a deep copy of the prompt template."""
        return PromptTemplate(
            name=self.name + "_clone",
            description=self.description,
            elements=[elem.clone() for elem in self.elements],
            base_reward=self.base_reward,
            optimization_history=self.optimization_history.copy(),
        )


class RewardFunction(BaseModel):
    """Configurable reward function for prompt optimization."""

    name: str
    weights: dict[str, float] = {"accuracy": 0.4, "efficiency": 0.2, "clarity": 0.2, "safety": 0.2}

    @validator("weights")
    def validate_weights(self, v):
        """Ensure weights sum to 1.0."""
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        return v


class APOConfig(BaseModel):
    """Configuration for Automatic Prompt Optimization."""

    strategy: OptimizationStrategy = OptimizationStrategy.REINFORCEMENT_LEARNING
    max_iterations: int = 100
    population_size: int = 20
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    elite_fraction: float = 0.2
    convergence_threshold: float = 0.001
    patience: int = 10
    reward_function: RewardFunction = RewardFunction(name="default")

    class Config:
        use_enum_values = True


class MutationOperator:
    """Operators for mutating prompt elements."""

    @staticmethod
    def synonym_replacement(element: PromptElement) -> PromptElement:
        """Replace words with synonyms."""
        # Simple synonym replacement for demonstration
        synonyms = {
            "analyze": ["examine", "evaluate", "assess", "review"],
            "design": ["create", "develop", "engineer", "construct"],
            "optimize": ["improve", "enhance", "refine", "perfect"],
            "validate": ["verify", "confirm", "check", "ensure"],
        }

        content = element.content
        for word, synonym_list in synonyms.items():
            if word in content and random.random() < 0.3:
                content = content.replace(word, random.choice(synonym_list))

        return PromptElement(
            element_type=element.element_type,
            content=content,
            weight=element.weight,
            mutable=element.mutable,
            position=element.position,
        )

    @staticmethod
    def paraphrase(element: PromptElement) -> PromptElement:
        """Paraphrase the content while preserving meaning."""
        # Simple paraphrasing patterns
        content = element.content

        paraphrase_patterns = [
            (r"Please (\w+)", r"Could you please \1"),
            (r"You should (\w+)", r"It is recommended to \1"),
            (r"Make sure to", r"Ensure that you"),
            (r"Consider the", r"Take into account the"),
        ]

        for pattern, replacement in paraphrase_patterns:
            if random.random() < 0.2:
                content = re.sub(pattern, replacement, content)

        return PromptElement(
            element_type=element.element_type,
            content=content,
            weight=element.weight,
            mutable=element.mutable,
            position=element.position,
        )

    @staticmethod
    def adjust_weight(element: PromptElement) -> PromptElement:
        """Adjust the weight of a prompt element."""
        new_weight = element.weight * random.uniform(0.8, 1.2)
        new_weight = max(0.1, min(2.0, new_weight))  # Clamp to reasonable range

        return PromptElement(
            element_type=element.element_type,
            content=element.content,
            weight=new_weight,
            mutable=element.mutable,
            position=element.position,
        )

    @staticmethod
    def reorder_elements(template: PromptTemplate) -> PromptTemplate:
        """Reorder elements in the template."""
        mutable_elements = [e for e in template.elements if e.mutable]
        if len(mutable_elements) > 1:
            # Swap two random elements
            idx1, idx2 = random.sample(range(len(mutable_elements)), 2)
            mutable_elements[idx1].position, mutable_elements[idx2].position = (
                mutable_elements[idx2].position,
                mutable_elements[idx1].position,
            )

        return template


class APOptimizer:
    """Automatic Prompt Optimizer using advanced RL techniques."""

    def __init__(self, config: APOConfig, agent: LightningAgent | None = None):
        self.config = config
        self.agent = agent
        self.mutation_operators = [
            MutationOperator.synonym_replacement,
            MutationOperator.paraphrase,
            MutationOperator.adjust_weight,
        ]
        self.optimization_log = []

        if AGENT_LIGHTNING_AVAILABLE and not agent:
            self.agent = LightningAgent()

    async def optimize_prompt(
        self,
        initial_template: PromptTemplate,
        training_data: list[dict[str, Any]],
        validation_data: list[dict[str, Any]],
        domain_context: str | None = None,
    ) -> PromptTemplate:
        """
        Optimize a prompt template using the configured strategy.

        Args:
            initial_template: Starting prompt template
            training_data: Data for training/evaluation
            validation_data: Data for validation
            domain_context: Optional domain-specific context

        Returns:
            Optimized prompt template
        """
        logger.info(f"Starting prompt optimization with {self.config.strategy.value} strategy")

        # Initialize population
        population = await self._initialize_population(initial_template, self.config.population_size)

        best_template = initial_template
        best_reward = await self._evaluate_template(initial_template, validation_data)

        iteration = 0
        patience_counter = 0
        prev_best_reward = best_reward

        while iteration < self.config.max_iterations:
            logger.info(f"Optimization iteration {iteration + 1}/{self.config.max_iterations}")

            # Evaluate population
            evaluated_population = []
            for template in population:
                reward = await self._evaluate_template(template, validation_data)
                evaluated_population.append((template, reward))

            # Sort by reward
            evaluated_population.sort(key=lambda x: x[1], reverse=True)

            # Update best template
            current_best_template, current_best_reward = evaluated_population[0]
            if current_best_reward > best_reward:
                best_template = current_best_template
                best_reward = current_best_reward
                patience_counter = 0
                logger.info(f"New best reward: {best_reward:.4f}")
            else:
                patience_counter += 1

            # Check convergence
            if abs(current_best_reward - prev_best_reward) < self.config.convergence_threshold:
                patience_counter += 1

            if patience_counter >= self.config.patience:
                logger.info(f"Converged after {iteration + 1} iterations")
                break

            prev_best_reward = current_best_reward

            # Create next generation
            if self.config.strategy == OptimizationStrategy.GENETIC_ALGORITHM:
                population = await self._genetic_algorithm_step(evaluated_population)
            elif self.config.strategy == OptimizationStrategy.EVOLUTIONARY_STRATEGIES:
                population = await self._evolutionary_strategies_step(evaluated_population)
            elif self.config.strategy == OptimizationStrategy.REINFORCEMENT_LEARNING:
                population = await self._reinforcement_learning_step(evaluated_population, training_data)
            else:
                population = await self._gradient_ascent_step(evaluated_population, training_data)

            iteration += 1

        # Log optimization history
        optimization_summary = {
            "iterations": iteration + 1,
            "final_reward": best_reward,
            "improvement": best_reward - await self._evaluate_template(initial_template, validation_data),
            "strategy": self.config.strategy.value,
            "timestamp": datetime.now().isoformat(),
        }

        best_template.optimization_history.append(optimization_summary)
        self.optimization_log.append(optimization_summary)

        logger.info(f"Optimization completed. Final reward: {best_reward:.4f}")
        return best_template

    async def _initialize_population(self, base_template: PromptTemplate, population_size: int) -> list[PromptTemplate]:
        """Initialize population of prompt templates."""
        population = [base_template]

        for _ in range(population_size - 1):
            mutated_template = base_template.clone()

            # Apply random mutations
            for element in mutated_template.elements:
                if element.mutable and random.random() < self.config.mutation_rate:
                    operator = random.choice(self.mutation_operators)
                    if operator != MutationOperator.reorder_elements:
                        mutated_element = operator(element)
                        element_idx = mutated_template.elements.index(element)
                        mutated_template.elements[element_idx] = mutated_element

            # Occasionally reorder elements
            if random.random() < 0.1:
                mutated_template = MutationOperator.reorder_elements(mutated_template)

            population.append(mutated_template)

        return population

    async def _evaluate_template(self, template: PromptTemplate, evaluation_data: list[dict[str, Any]]) -> float:
        """Evaluate a prompt template on the given data."""
        if not evaluation_data:
            return 0.0

        prompt = template.compile()
        total_reward = 0.0

        for data_point in evaluation_data:
            reward = await self._compute_reward(prompt, data_point)
            total_reward += reward

        return total_reward / len(evaluation_data)

    async def _compute_reward(self, prompt: str, data_point: dict[str, Any]) -> float:
        """Compute reward for a prompt on a specific data point."""
        # Simulate prompt execution and reward calculation
        # In practice, this would execute the actual task and measure performance

        accuracy = self._compute_accuracy_metric(prompt, data_point)
        efficiency = self._compute_efficiency_metric(prompt, data_point)
        clarity = self._compute_clarity_metric(prompt, data_point)
        safety = self._compute_safety_metric(prompt, data_point)

        total_reward = (
            self.config.reward_function.weights["accuracy"] * accuracy
            + self.config.reward_function.weights["efficiency"] * efficiency
            + self.config.reward_function.weights["clarity"] * clarity
            + self.config.reward_function.weights["safety"] * safety
        )

        return total_reward

    def _compute_accuracy_metric(self, prompt: str, data_point: dict[str, Any]) -> float:
        """Compute accuracy metric for the prompt."""
        # Simulate accuracy calculation based on prompt quality
        base_accuracy = 0.7

        # Reward specific prompt elements
        if "analyze" in prompt.lower():
            base_accuracy += 0.05
        if "step by step" in prompt.lower():
            base_accuracy += 0.03
        if "consider" in prompt.lower():
            base_accuracy += 0.02

        # Add some noise
        noise = random.gauss(0, 0.05)

        return max(0.0, min(1.0, base_accuracy + noise))

    def _compute_efficiency_metric(self, prompt: str, data_point: dict[str, Any]) -> float:
        """Compute efficiency metric for the prompt."""
        # Efficiency based on prompt length and clarity
        length_penalty = min(0.1, len(prompt) / 10000)  # Penalize very long prompts
        clarity_bonus = 0.1 if "clear" in prompt.lower() or "specific" in prompt.lower() else 0.0

        base_efficiency = 0.8 - length_penalty + clarity_bonus
        noise = random.gauss(0, 0.03)

        return max(0.0, min(1.0, base_efficiency + noise))

    def _compute_clarity_metric(self, prompt: str, data_point: dict[str, Any]) -> float:
        """Compute clarity metric for the prompt."""
        clarity_indicators = [
            "please",
            "clearly",
            "specifically",
            "precisely",
            "step by step",
            "in detail",
            "thoroughly",
        ]

        clarity_score = 0.5
        for indicator in clarity_indicators:
            if indicator in prompt.lower():
                clarity_score += 0.05

        # Penalize ambiguous terms
        ambiguous_terms = ["maybe", "perhaps", "possibly", "might"]
        for term in ambiguous_terms:
            if term in prompt.lower():
                clarity_score -= 0.03

        noise = random.gauss(0, 0.04)
        return max(0.0, min(1.0, clarity_score + noise))

    def _compute_safety_metric(self, prompt: str, data_point: dict[str, Any]) -> float:
        """Compute safety metric for the prompt (critical for engineering)."""
        safety_indicators = ["safety", "secure", "verify", "validate", "check", "ensure", "compliance", "standards"]

        safety_score = 0.6
        for indicator in safety_indicators:
            if indicator in prompt.lower():
                safety_score += 0.05

        # Reward domain-specific safety mentions
        if any(term in prompt.lower() for term in ["mechanical", "structural", "load"]):
            safety_score += 0.03

        noise = random.gauss(0, 0.02)
        return max(0.0, min(1.0, safety_score + noise))

    async def _genetic_algorithm_step(
        self, evaluated_population: list[tuple[PromptTemplate, float]]
    ) -> list[PromptTemplate]:
        """Perform one step of genetic algorithm optimization."""
        # Select elite individuals
        elite_count = int(len(evaluated_population) * self.config.elite_fraction)
        elites = [template for template, _ in evaluated_population[:elite_count]]

        # Create offspring through crossover and mutation
        offspring = []

        while len(offspring) < self.config.population_size - elite_count:
            # Tournament selection
            parent1, parent2 = await self._tournament_selection(evaluated_population, 2)

            # Crossover
            if random.random() < self.config.crossover_rate:
                child1, child2 = await self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1.clone(), parent2.clone()

            # Mutation
            if random.random() < self.config.mutation_rate:
                child1 = await self._mutate(child1)
            if random.random() < self.config.mutation_rate:
                child2 = await self._mutate(child2)

            offspring.extend([child1, child2])

        # Return new population
        return elites + offspring[: self.config.population_size - elite_count]

    async def _evolutionary_strategies_step(
        self, evaluated_population: list[tuple[PromptTemplate, float]]
    ) -> list[PromptTemplate]:
        """Perform one step of evolutionary strategies optimization."""
        # Use the best templates as parents
        parent_count = max(2, len(evaluated_population) // 2)
        parents = [template for template, _ in evaluated_population[:parent_count]]

        offspring = []

        for parent in parents:
            # Create multiple offspring per parent
            offspring_per_parent = self.config.population_size // parent_count

            for _ in range(offspring_per_parent):
                child = parent.clone()

                # Apply adaptive mutation rate
                mutation_rate = self.config.mutation_rate * (1 + random.gauss(0, 0.5))
                mutation_rate = max(0.01, min(0.5, mutation_rate))

                if random.random() < mutation_rate:
                    child = await self._mutate(child)

                offspring.append(child)

        # Ensure correct population size
        return offspring[: self.config.population_size]

    async def _reinforcement_learning_step(
        self, evaluated_population: list[tuple[PromptTemplate, float]], training_data: list[dict[str, Any]]
    ) -> list[PromptTemplate]:
        """Perform one step of reinforcement learning optimization."""
        # Use policy gradient approach
        new_population = []

        for template, reward in evaluated_population:
            # Compute policy gradient
            policy_gradient = await self._compute_policy_gradient(template, reward, training_data)

            # Update template based on gradient
            updated_template = await self._apply_policy_gradient(template, policy_gradient)
            new_population.append(updated_template)

        # Add some exploration
        exploration_count = max(1, self.config.population_size // 4)
        for _ in range(exploration_count):
            random_template = random.choice(evaluated_population)[0].clone()
            mutated_template = await self._mutate(random_template)
            new_population.append(mutated_template)

        return new_population[: self.config.population_size]

    async def _gradient_ascent_step(
        self, evaluated_population: list[tuple[PromptTemplate, float]], training_data: list[dict[str, Any]]
    ) -> list[PromptTemplate]:
        """Perform one step of gradient ascent optimization."""
        # Compute gradients for each template
        new_population = []

        for template, _reward in evaluated_population:
            # Estimate gradient numerically
            gradient = await self._estimate_gradient(template, training_data)

            # Update template
            updated_template = await self._apply_gradient(template, gradient)
            new_population.append(updated_template)

        return new_population

    async def _tournament_selection(
        self, evaluated_population: list[tuple[PromptTemplate, float]], tournament_size: int
    ) -> tuple[PromptTemplate, PromptTemplate]:
        """Select parents using tournament selection."""
        tournament = random.sample(evaluated_population, min(tournament_size, len(evaluated_population)))
        tournament.sort(key=lambda x: x[1], reverse=True)

        parent1 = tournament[0][0]
        parent2 = tournament[1][0] if len(tournament) > 1 else tournament[0][0].clone()

        return parent1, parent2

    async def _crossover(
        self, parent1: PromptTemplate, parent2: PromptTemplate
    ) -> tuple[PromptTemplate, PromptTemplate]:
        """Perform crossover between two parent templates."""
        child1 = parent1.clone()
        child2 = parent2.clone()

        # Swap some elements between parents
        mutable_indices1 = [i for i, e in enumerate(child1.elements) if e.mutable]
        mutable_indices2 = [i for i, e in enumerate(child2.elements) if e.mutable]

        if mutable_indices1 and mutable_indices2:
            # Swap random elements
            idx1 = random.choice(mutable_indices1)
            idx2 = random.choice(mutable_indices2)

            child1.elements[idx1], child2.elements[idx2] = child2.elements[idx2], child1.elements[idx1]

        return child1, child2

    async def _mutate(self, template: PromptTemplate) -> PromptTemplate:
        """Apply mutation to a template."""
        mutated_template = template.clone()

        for element in mutated_template.elements:
            if element.mutable and random.random() < self.config.mutation_rate:
                operator = random.choice(self.mutation_operators)
                if operator != MutationOperator.reorder_elements:
                    mutated_element = operator(element)
                    element_idx = mutated_template.elements.index(element)
                    mutated_template.elements[element_idx] = mutated_element

        # Occasionally reorder elements
        if random.random() < 0.1:
            mutated_template = MutationOperator.reorder_elements(mutated_template)

        return mutated_template

    async def _compute_policy_gradient(
        self, template: PromptTemplate, reward: float, training_data: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Compute policy gradient for reinforcement learning."""
        # Simplified policy gradient computation
        gradient = {}

        for element in template.elements:
            if element.mutable:
                # Gradient based on reward and element properties
                element_gradient = reward * element.weight

                # Add exploration noise
                element_gradient += random.gauss(0, 0.1)

                gradient[f"element_{element.element_type.value}_{element.position}"] = element_gradient

        return gradient

    async def _apply_policy_gradient(self, template: PromptTemplate, gradient: dict[str, float]) -> PromptTemplate:
        """Apply policy gradient to update template."""
        updated_template = template.clone()

        learning_rate = 0.01

        for element in updated_template.elements:
            if element.mutable:
                gradient_key = f"element_{element.element_type.value}_{element.position}"
                if gradient_key in gradient:
                    # Update weight based on gradient
                    element.weight += learning_rate * gradient[gradient_key]
                    element.weight = max(0.1, min(2.0, element.weight))

        return updated_template

    async def _estimate_gradient(
        self, template: PromptTemplate, training_data: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Estimate gradient numerically."""
        gradient = {}
        epsilon = 0.01

        base_reward = await self._evaluate_template(template, training_data)

        for element in template.elements:
            if element.mutable:
                # Perturb element weight
                original_weight = element.weight
                element.weight = original_weight + epsilon

                perturbed_reward = await self._evaluate_template(template, training_data)

                # Compute gradient
                gradient_value = (perturbed_reward - base_reward) / epsilon
                gradient[f"element_{element.element_type.value}_{element.position}"] = gradient_value

                # Restore original weight
                element.weight = original_weight

        return gradient

    async def _apply_gradient(self, template: PromptTemplate, gradient: dict[str, float]) -> PromptTemplate:
        """Apply gradient to update template."""
        updated_template = template.clone()

        learning_rate = 0.01

        for element in updated_template.elements:
            if element.mutable:
                gradient_key = f"element_{element.element_type.value}_{element.position}"
                if gradient_key in gradient:
                    # Update weight based on gradient
                    element.weight += learning_rate * gradient[gradient_key]
                    element.weight = max(0.1, min(2.0, element.weight))

        return updated_template

    def get_optimization_summary(self) -> dict[str, Any]:
        """Get summary of optimization process."""
        if not self.optimization_log:
            return {"message": "No optimization performed yet"}

        return {
            "total_optimizations": len(self.optimization_log),
            "average_improvement": np.mean([log["improvement"] for log in self.optimization_log]),
            "best_strategy": self.config.strategy.value,
            "optimization_history": self.optimization_log,
        }


# Domain-specific template generators
class MechanicalEngineeringTemplateGenerator:
    """Generate optimized prompt templates for mechanical engineering tasks."""

    @staticmethod
    def create_cad_analysis_template() -> PromptTemplate:
        """Create template for CAD analysis tasks."""
        elements = [
            PromptElement(
                element_type=PromptElementType.ROLE_DEFINITION,
                content="You are an expert mechanical engineer specializing in CAD analysis and design optimization.",
                position=0,
            ),
            PromptElement(
                element_type=PromptElementType.INSTRUCTION,
                content="Analyze the provided CAD design thoroughly and provide detailed recommendations.",
                position=1,
            ),
            PromptElement(
                element_type=PromptElementType.CONTEXT_PROVIDER,
                content="Focus on acoustic performance, structural integrity, and manufacturability.",
                position=2,
            ),
            PromptElement(
                element_type=PromptElementType.CONSTRAINT,
                content="Ensure all recommendations follow industry standards and safety guidelines.",
                position=3,
            ),
            PromptElement(
                element_type=PromptElementType.FORMAT_SPECIFIER,
                content="Provide your analysis in a structured format with clear sections and priority levels.",
                position=4,
            ),
        ]

        return PromptTemplate(
            name="cad_analysis_template",
            description="Template for analyzing CAD designs of mechanical components",
            elements=elements,
        )

    @staticmethod
    def create_rag_template() -> PromptTemplate:
        """Create template for RAG-based technical Q&A."""
        elements = [
            PromptElement(
                element_type=PromptElementType.ROLE_DEFINITION,
                content="You are a diesel engine expert with extensive knowledge of mechanical systems.",
                position=0,
            ),
            PromptElement(
                element_type=PromptElementType.INSTRUCTION,
                content="Answer the technical question based on the provided context.",
                position=1,
            ),
            PromptElement(
                element_type=PromptElementType.CONTEXT_PROVIDER,
                content="Use only the information from the provided documents to answer accurately.",
                position=2,
            ),
            PromptElement(
                element_type=PromptElementType.CONSTRAINT,
                content="Always cite your sources and indicate confidence levels.",
                position=3,
            ),
            PromptElement(
                element_type=PromptElementType.SAFETY,
                content="Prioritize safety-critical information and warn about potential hazards.",
                position=4,
            ),
        ]

        return PromptTemplate(
            name="rag_template", description="Template for RAG-based technical Q&A", elements=elements
        )

    @staticmethod
    def create_ui_generation_template() -> PromptTemplate:
        """Create template for industrial UI generation."""
        elements = [
            PromptElement(
                element_type=PromptElementType.ROLE_DEFINITION,
                content="You are an expert UI/UX designer specializing in industrial interfaces.",
                position=0,
            ),
            PromptElement(
                element_type=PromptElementType.INSTRUCTION,
                content="Generate a factory-grade user interface based on the requirements.",
                position=1,
            ),
            PromptElement(
                element_type=PromptElementType.CONTEXT_PROVIDER,
                content="Focus on usability in factory environments with high contrast and clear visibility.",
                position=2,
            ),
            PromptElement(
                element_type=PromptElementType.CONSTRAINT,
                content="Ensure accessibility compliance and responsive design.",
                position=3,
            ),
            PromptElement(
                element_type=PromptElementType.FORMAT_SPECIFIER,
                content="Provide complete, working code with proper structure and documentation.",
                position=4,
            ),
        ]

        return PromptTemplate(
            name="ui_generation_template",
            description="Template for generating industrial UI components",
            elements=elements,
        )
