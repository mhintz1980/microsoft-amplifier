"""
Multi-Objective Optimization System for Engineering Agents

Implements advanced optimization techniques for balancing competing engineering objectives:
- Pareto frontier exploration and maintenance
- Dynamic weight adaptation based on performance
- Constraint handling for safety-critical requirements
- Multi-criteria decision making for engineering trade-offs
"""

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np
from scipy.spatial.distance import euclidean

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Optimization strategies for multi-objective problems."""

    WEIGHTED_SUM = "weighted_sum"
    PARETO_DOMINANCE = "pareto_dominance"
    EPSILON_CONSTRAINT = "epsilon_constraint"
    GOAL_PROGRAMMING = "goal_programming"
    REFERENCE_POINT = "reference_point"
    DYNAMIC_AGGREGATION = "dynamic_aggregation"


class EngineeringObjective(Enum):
    """Engineering-specific objectives."""

    SAFETY = "safety"
    RELIABILITY = "reliability"
    PERFORMANCE = "performance"
    EFFICIENCY = "efficiency"
    COST = "cost"
    MANUFACTURABILITY = "manufacturability"
    SUSTAINABILITY = "sustainability"
    MAINTAINABILITY = "maintainability"
    AESTHETICS = "aesthetics"
    INNOVATION = "innovation"


@dataclass
class ObjectiveSpecification:
    """Specification for an optimization objective."""

    name: EngineeringObjective
    weight: float
    target_value: float | None = None
    tolerance: float | None = None
    min_value: float = 0.0
    max_value: float = 1.0
    is_constraint: bool = False
    priority: int = 1  # Lower number = higher priority

    def normalize(self, value: float) -> float:
        """Normalize value to [0, 1] range."""
        if self.max_value == self.min_value:
            return 0.0
        return (value - self.min_value) / (self.max_value - self.min_value)

    def is_satisfied(self, value: float) -> bool:
        """Check if objective constraint is satisfied."""
        if not self.is_constraint or self.target_value is None:
            return True

        if self.tolerance is None:
            return abs(value - self.target_value) < 0.01

        return abs(value - self.target_value) <= self.tolerance


@dataclass
class Solution:
    """Represents a solution in multi-objective space."""

    objectives: dict[EngineeringObjective, float]
    decision_variables: dict[str, float]
    feasibility: bool = True
    constraint_violations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def dominates(self, other: "Solution", objectives: list[EngineeringObjective]) -> bool:
        """Check if this solution dominates another."""
        self_worse = False

        for obj in objectives:
            self_val = self.objectives.get(obj, 0.0)
            other_val = other.objectives.get(obj, 0.0)

            if self_val < other_val:
                self_worse = True
            elif self_val > other_val:
                return False

        return not self_worse

    def to_vector(self, objectives: list[EngineeringObjective]) -> np.ndarray:
        """Convert solution to objective vector."""
        return np.array([self.objectives.get(obj, 0.0) for obj in objectives])

    def crowding_distance(self, pareto_front: list["Solution"], objectives: list[EngineeringObjective]) -> float:
        """Calculate crowding distance for diversity preservation."""
        if len(pareto_front) <= 2:
            return float("inf")

        distance = 0.0

        for obj in objectives:
            # Sort by this objective
            sorted_front = sorted(pareto_front, key=lambda s: s.objectives.get(obj, 0.0))

            # Find position in sorted front
            for i, solution in enumerate(sorted_front):
                if solution == self:
                    if i == 0 or i == len(sorted_front) - 1:
                        distance += float("inf")
                    else:
                        obj_range = sorted_front[-1].objectives.get(obj, 0.0) - sorted_front[0].objectives.get(obj, 0.0)
                        if obj_range > 0:
                            distance += (
                                sorted_front[i + 1].objectives.get(obj, 0.0)
                                - sorted_front[i - 1].objectives.get(obj, 0.0)
                            ) / obj_range
                    break

        return distance


class ParetoFront:
    """Manages Pareto-optimal solutions."""

    def __init__(self, objectives: list[EngineeringObjective], max_size: int = 1000):
        self.objectives = objectives
        self.max_size = max_size
        self.solutions: list[Solution] = []
        self.hypervolume_history = []

    def add_solution(self, solution: Solution) -> bool:
        """Add solution to Pareto front if non-dominated."""
        # Remove dominated solutions
        dominated_solutions = []
        for existing in self.solutions:
            if solution.dominates(existing, self.objectives):
                dominated_solutions.append(existing)
            elif existing.dominates(solution, self.objectives):
                return False  # New solution is dominated

        # Remove dominated solutions
        for dominated in dominated_solutions:
            self.solutions.remove(dominated)

        # Add new solution
        self.solutions.append(solution)

        # Maintain size limit
        if len(self.solutions) > self.max_size:
            self._prune_solutions()

        return True

    def _prune_solutions(self):
        """Prune solutions maintaining diversity."""
        if len(self.solutions) <= self.max_size:
            return

        # Calculate crowding distances
        crowding_distances = []
        for solution in self.solutions:
            distance = solution.crowding_distance(self.solutions, self.objectives)
            crowding_distances.append((distance, solution))

        # Sort by crowding distance (descending)
        crowding_distances.sort(key=lambda x: x[0], reverse=True)

        # Keep top solutions
        self.solutions = [sol for _, sol in crowding_distances[: self.max_size]]

    def calculate_hypervolume(self, reference_point: np.ndarray) -> float:
        """Calculate hypervolume of Pareto front."""
        if not self.solutions:
            return 0.0

        # Simple hypervolume calculation (2D case)
        if len(self.objectives) == 2:
            volume = 0.0
            sorted_solutions = sorted(self.solutions, key=lambda s: s.objectives.get(self.objectives[0], 0.0))

            prev_x = 0.0
            for solution in sorted_solutions:
                x = solution.objectives.get(self.objectives[0], 0.0)
                y = solution.objectives.get(self.objectives[1], 0.0)

                if x > prev_x:
                    volume += (x - prev_x) * y
                    prev_x = x

            return volume

        # For higher dimensions, use approximation
        return len(self.solutions) / self.max_size

    def get_diverse_subset(self, size: int) -> list[Solution]:
        """Get diverse subset of solutions."""
        if len(self.solutions) <= size:
            return self.solutions.copy()

        # Use k-means clustering for diversity
        from sklearn.cluster import KMeans

        # Create objective matrix
        objective_matrix = np.array([sol.to_vector(self.objectives) for sol in self.solutions])

        # Cluster solutions
        kmeans = KMeans(n_clusters=size, random_state=42)
        cluster_labels = kmeans.fit_predict(objective_matrix)

        # Select one solution from each cluster (closest to centroid)
        diverse_solutions = []
        for cluster_id in range(size):
            cluster_indices = np.where(cluster_labels == cluster_id)[0]
            if len(cluster_indices) > 0:
                centroid = kmeans.cluster_centers_[cluster_id]
                distances = [euclidean(objective_matrix[i], centroid) for i in cluster_indices]
                best_idx = cluster_indices[np.argmin(distances)]
                diverse_solutions.append(self.solutions[best_idx])

        return diverse_solutions


class DynamicWeightOptimizer:
    """Dynamically optimizes objective weights based on performance."""

    def __init__(
        self,
        objectives: list[EngineeringObjective],
        initial_weights: dict[EngineeringObjective, float] = None,
        adaptation_rate: float = 0.1,
        performance_window: int = 50,
    ):
        self.objectives = objectives
        self.adaptation_rate = adaptation_rate
        self.performance_window = performance_window

        # Initialize weights
        if initial_weights:
            self.weights = initial_weights.copy()
        else:
            self.weights = {obj: 1.0 / len(objectives) for obj in objectives}

        # Performance tracking
        self.performance_history = defaultdict(list)
        self.weight_history = []
        self.satisfaction_rates = defaultdict(float)

    def update_performance(self, objective: EngineeringObjective, performance: float):
        """Update performance for an objective."""
        self.performance_history[objective].append(performance)

        # Maintain window size
        if len(self.performance_history[objective]) > self.performance_window:
            self.performance_history[objective].pop(0)

    def calculate_satisfaction_rate(self, objective: EngineeringObjective) -> float:
        """Calculate satisfaction rate for an objective."""
        if objective not in self.performance_history:
            return 0.5

        performances = self.performance_history[objective]
        if len(performances) < 10:
            return 0.5

        # Count how often performance meets threshold
        threshold = 0.7  # Adjustable
        satisfied_count = sum(1 for p in performances if p >= threshold)
        return satisfied_count / len(performances)

    def adapt_weights(self):
        """Adapt weights based on performance and satisfaction rates."""
        new_weights = self.weights.copy()

        for obj in self.objectives:
            satisfaction_rate = self.calculate_satisfaction_rate(obj)

            # Increase weight for poorly satisfied objectives
            if satisfaction_rate < 0.3:
                adjustment = self.adaptation_rate * 2
            elif satisfaction_rate < 0.5:
                adjustment = self.adaptation_rate
            elif satisfaction_rate > 0.8:
                adjustment = -self.adaptation_rate * 0.5
            else:
                adjustment = 0.0

            new_weights[obj] = max(0.01, new_weights[obj] + adjustment)

        # Normalize weights
        total_weight = sum(new_weights.values())
        for obj in new_weights:
            new_weights[obj] /= total_weight

        self.weights = new_weights
        self.weight_history.append(self.weights.copy())

        # Limit history size
        if len(self.weight_history) > 1000:
            self.weight_history.pop(0)

    def get_weight_stability(self) -> float:
        """Measure weight stability over time."""
        if len(self.weight_history) < 2:
            return 1.0

        # Calculate average change between consecutive weight sets
        changes = []
        for i in range(1, len(self.weight_history)):
            prev_weights = self.weight_history[i - 1]
            curr_weights = self.weight_history[i]

            change = sum(abs(curr_weights[obj] - prev_weights[obj]) for obj in self.objectives)
            changes.append(change)

        return 1.0 - (np.mean(changes) if changes else 0.0)


class ConstraintHandler:
    """Handles engineering constraints in optimization."""

    def __init__(self):
        self.constraints: dict[str, tuple[callable, bool]] = {}  # name: (function, is_hard)
        self.violation_history = defaultdict(list)

    def add_constraint(self, name: str, constraint_func: callable, is_hard: bool = True):
        """Add a constraint function."""
        self.constraints[name] = (constraint_func, is_hard)

    def evaluate_constraints(self, solution: Solution) -> tuple[bool, list[str], float]:
        """Evaluate all constraints for a solution."""
        violations = []
        penalty = 0.0

        for name, (constraint_func, is_hard) in self.constraints.items():
            try:
                is_satisfied, violation_magnitude = constraint_func(solution)

                if not is_satisfied:
                    violations.append(f"{name}: {violation_magnitude}")

                    if is_hard:
                        return False, violations, float("inf")
                    penalty += violation_magnitude

                # Track violation history
                self.violation_history[name].append(not is_satisfied)
                if len(self.violation_history[name]) > 100:
                    self.violation_history[name].pop(0)

            except Exception as e:
                logger.error(f"Error evaluating constraint {name}: {e}")
                violations.append(f"{name}: evaluation_error")
                if is_hard:
                    return False, violations, float("inf")

        return len(violations) == 0, violations, penalty

    def get_violation_rate(self, constraint_name: str) -> float:
        """Get violation rate for a constraint."""
        if constraint_name not in self.violation_history:
            return 0.0

        violations = self.violation_history[constraint_name]
        return sum(violations) / len(violations) if violations else 0.0


class MultiObjectiveOptimizer:
    """Main multi-objective optimization system."""

    def __init__(
        self,
        objectives: list[ObjectiveSpecification],
        strategy: OptimizationStrategy = OptimizationStrategy.DYNAMIC_AGGREGATION,
        max_iterations: int = 1000,
        convergence_threshold: float = 1e-6,
    ):
        self.objectives = objectives
        self.objective_names = [obj.name for obj in objectives]
        self.strategy = strategy
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold

        # Initialize components
        self.pareto_front = ParetoFront(self.objective_names)
        self.weight_optimizer = DynamicWeightOptimizer(
            self.objective_names, {obj.name: obj.weight for obj in objectives}
        )
        self.constraint_handler = ConstraintHandler()

        # Add constraint specifications as constraints
        for obj_spec in objectives:
            if obj_spec.is_constraint and obj_spec.target_value is not None:
                self._add_objective_as_constraint(obj_spec)

        # Optimization state
        self.current_iteration = 0
        self.best_solution = None
        self.optimization_history = []

    def _add_objective_as_constraint(self, obj_spec: ObjectiveSpecification):
        """Add objective specification as a constraint."""

        def constraint_func(solution: Solution) -> tuple[bool, float]:
            value = solution.objectives.get(obj_spec.name, 0.0)

            if obj_spec.tolerance is not None:
                is_satisfied = abs(value - obj_spec.target_value) <= obj_spec.tolerance
                violation = abs(value - obj_spec.target_value) - obj_spec.tolerance
            else:
                is_satisfied = abs(value - obj_spec.target_value) <= 0.01
                violation = abs(value - obj_spec.target_value) - 0.01

            return is_satisfied, max(0.0, violation)

        self.constraint_handler.add_constraint(f"constraint_{obj_spec.name.value}", constraint_func, is_hard=True)

    def aggregate_objectives(self, solution: Solution, weights: dict[EngineeringObjective, float] = None) -> float:
        """Aggregate multiple objectives into single value."""
        if weights is None:
            weights = self.weight_optimizer.weights

        aggregated_value = 0.0

        for obj_spec in self.objectives:
            obj_value = solution.objectives.get(obj_spec.name, 0.0)
            normalized_value = obj_spec.normalize(obj_value)
            weight = weights.get(obj_spec.name, obj_spec.weight)

            aggregated_value += weight * normalized_value

        return aggregated_value

    def evaluate_solution(self, decision_variables: dict[str, float]) -> Solution:
        """Evaluate a solution with given decision variables."""
        # This is a placeholder - in practice, this would call the actual evaluation function
        # For now, simulate evaluation based on decision variables

        objectives = {}

        # Simulate objective evaluations
        if "thickness" in decision_variables:
            thickness = decision_variables["thickness"]
            objectives[EngineeringObjective.SAFETY] = min(1.0, thickness / 10.0)
            objectives[EngineeringObjective.COST] = max(0.0, 1.0 - thickness / 20.0)
            objectives[EngineeringObjective.EFFICIENCY] = 0.8 - abs(thickness - 5.0) / 10.0

        if "material_quality" in decision_variables:
            quality = decision_variables["material_quality"]
            objectives[EngineeringObjective.RELIABILITY] = min(1.0, quality / 100.0)
            objectives[EngineeringObjective.PERFORMANCE] = min(1.0, quality / 80.0)

        # Add default values for missing objectives
        for obj_name in self.objective_names:
            if obj_name not in objectives:
                objectives[obj_name] = np.random.uniform(0.3, 0.9)

        solution = Solution(
            objectives=objectives, decision_variables=decision_variables, metadata={"iteration": self.current_iteration}
        )

        # Evaluate constraints
        is_feasible, violations, penalty = self.constraint_handler.evaluate_constraints(solution)
        solution.feasibility = is_feasible
        solution.constraint_violations = violations

        return solution

    async def optimize(
        self, initial_solution: Solution = None, bounds: dict[str, tuple[float, float]] = None
    ) -> tuple[Solution, ParetoFront]:
        """Run multi-objective optimization."""
        logger.info(f"Starting multi-objective optimization with strategy: {self.strategy.value}")

        # Initialize bounds
        if bounds is None:
            bounds = {"thickness": (1.0, 20.0), "material_quality": (10.0, 100.0), "complexity": (0.0, 1.0)}

        # Initialize population
        population_size = 50
        population = []

        for _i in range(population_size):
            decision_vars = {var: np.random.uniform(low, high) for var, (low, high) in bounds.items()}

            solution = self.evaluate_solution(decision_vars)
            population.append(solution)

        # Evolutionary optimization loop
        for iteration in range(self.max_iterations):
            self.current_iteration = iteration

            # Evaluate and update Pareto front
            for solution in population:
                if solution.feasible:
                    self.pareto_front.add_solution(solution)

            # Select parents using tournament selection
            parents = self._tournament_selection(population, size=10)

            # Create offspring through crossover and mutation
            offspring = self._create_offspring(parents, bounds)

            # Environmental selection (keep best solutions)
            population = self._environmental_selection(population + offspring, population_size)

            # Update weights if using dynamic strategy
            if self.strategy == OptimizationStrategy.DYNAMIC_AGGREGATION:
                self._update_performance_metrics(population)
                self.weight_optimizer.adapt_weights()

            # Check convergence
            if self._check_convergence():
                logger.info(f"Optimization converged at iteration {iteration}")
                break

            # Log progress
            if iteration % 100 == 0:
                avg_fitness = np.mean([self.aggregate_objectives(sol) for sol in population])
                hypervolume = self.pareto_front.calculate_hypervolume(np.ones(len(self.objective_names)))
                logger.info(f"Iteration {iteration}: Avg Fitness={avg_fitness:.4f}, Hypervolume={hypervolume:.4f}")

        # Select best solution
        best_solution = self._select_best_solution()

        logger.info(f"Optimization completed. Pareto front size: {len(self.pareto_front.solutions)}")
        return best_solution, self.pareto_front

    def _tournament_selection(self, population: list[Solution], size: int = 2) -> list[Solution]:
        """Tournament selection for parent selection."""
        selected = []

        while len(selected) < len(population):
            # Random tournament participants
            tournament = np.random.choice(population, size=min(size, len(population)), replace=False)

            # Select best based on aggregation
            best = max(tournament, key=lambda s: self.aggregate_objectives(s))
            selected.append(best)

        return selected

    def _create_offspring(self, parents: list[Solution], bounds: dict[str, tuple[float, float]]) -> list[Solution]:
        """Create offspring through crossover and mutation."""
        offspring = []

        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                parent1, parent2 = parents[i], parents[i + 1]

                # Crossover
                child1_vars, child2_vars = self._crossover(parent1.decision_variables, parent2.decision_variables)

                # Mutation
                child1_vars = self._mutate(child1_vars, bounds, mutation_rate=0.1)
                child2_vars = self._mutate(child2_vars, bounds, mutation_rate=0.1)

                # Create child solutions
                child1 = self.evaluate_solution(child1_vars)
                child2 = self.evaluate_solution(child2_vars)

                offspring.extend([child1, child2])

        return offspring

    def _crossover(self, vars1: dict[str, float], vars2: dict[str, float]) -> tuple[dict[str, float], dict[str, float]]:
        """Simulated binary crossover (SBX)."""
        child1, child2 = {}, {}

        for var in vars1:
            parent1_val = vars1[var]
            parent2_val = vars2[var]

            # SBX with eta = 20
            eta = 20.0
            u = np.random.random()

            if u <= 0.5:
                beta = (2 * u) ** (1 / (eta + 1))
            else:
                beta = (1 / (2 * (1 - u))) ** (1 / (eta + 1))

            child1[var] = 0.5 * ((1 + beta) * parent1_val + (1 - beta) * parent2_val)
            child2[var] = 0.5 * ((1 - beta) * parent1_val + (1 + beta) * parent2_val)

        return child1, child2

    def _mutate(
        self, vars_dict: dict[str, float], bounds: dict[str, tuple[float, float]], mutation_rate: float
    ) -> dict[str, float]:
        """Polynomial mutation."""
        mutated = vars_dict.copy()

        for var, (low, high) in bounds.items():
            if np.random.random() < mutation_rate:
                # Polynomial mutation with eta = 20
                eta = 20.0
                y = mutated[var]
                delta = (y - low) / (high - low)

                u = np.random.random()
                if u <= 0.5:
                    delta_q = (2 * u + (1 - 2 * u) * (1 - delta) ** (eta + 1)) ** (1 / (eta + 1)) - 1
                else:
                    delta_q = 1 - (2 * (1 - u) + 2 * (u - 0.5) * (1 - delta) ** (eta + 1)) ** (1 / (eta + 1))

                mutated[var] = low + delta_q * (high - low)

        return mutated

    def _environmental_selection(self, combined_population: list[Solution], target_size: int) -> list[Solution]:
        """Environmental selection to maintain population size."""
        # Separate feasible and infeasible solutions
        feasible = [sol for sol in combined_population if sol.feasible]
        infeasible = [sol for sol in combined_population if not sol.feasible]

        # Prefer feasible solutions
        if len(feasible) >= target_size:
            # Select best feasible solutions
            feasible.sort(key=lambda s: self.aggregate_objectives(s), reverse=True)
            return feasible[:target_size]
        # Take all feasible, fill with best infeasible
        infeasible.sort(key=lambda s: self.aggregate_objectives(s), reverse=True)
        return feasible + infeasible[: target_size - len(feasible)]

    def _update_performance_metrics(self, population: list[Solution]):
        """Update performance metrics for weight adaptation."""
        for obj_name in self.objective_names:
            performances = [sol.objectives.get(obj_name, 0.0) for sol in population if sol.feasible]
            if performances:
                avg_performance = np.mean(performances)
                self.weight_optimizer.update_performance(obj_name, avg_performance)

    def _check_convergence(self) -> bool:
        """Check if optimization has converged."""
        if len(self.pareto_front.solutions) < 2:
            return False

        # Check hypervolume convergence
        if len(self.pareto_front.hypervolume_history) >= 10:
            recent_volumes = self.pareto_front.hypervolume_history[-10:]
            volume_change = abs(recent_volumes[-1] - recent_volumes[0]) / recent_volumes[0]
            return volume_change < self.convergence_threshold

        return False

    def _select_best_solution(self) -> Solution:
        """Select best solution from Pareto front."""
        if not self.pareto_front.solutions:
            return Solution({}, {})  # Empty solution

        # Use current weights to select best
        best = max(self.pareto_front.solutions, key=lambda s: self.aggregate_objectives(s))

        return best

    def generate_report(self) -> dict[str, Any]:
        """Generate optimization report."""
        if not self.pareto_front.solutions:
            return {"error": "No solutions found"}

        # Calculate statistics
        objective_stats = {}
        for obj_name in self.objective_names:
            values = [sol.objectives.get(obj_name, 0.0) for sol in self.pareto_front.solutions]
            objective_stats[obj_name.value] = {
                "min": min(values),
                "max": max(values),
                "mean": np.mean(values),
                "std": np.std(values),
            }

        return {
            "optimization_summary": {
                "pareto_front_size": len(self.pareto_front.solutions),
                "total_iterations": self.current_iteration,
                "convergence_achieved": self._check_convergence(),
                "strategy": self.strategy.value,
            },
            "objective_statistics": objective_stats,
            "current_weights": {obj.value: weight for obj, weight in self.weight_optimizer.weights.items()},
            "constraint_violation_rates": {
                name: self.constraint_handler.get_violation_rate(name) for name in self.constraint_handler.constraints
            },
            "weight_stability": self.weight_optimizer.get_weight_stability(),
            "best_solution": asdict(self._select_best_solution()) if self.pareto_front.solutions else None,
        }


# Utility functions for common engineering optimization scenarios
def create_structural_optimization() -> MultiObjectiveOptimizer:
    """Create optimizer for structural design problems."""
    objectives = [
        ObjectiveSpecification(EngineeringObjective.SAFETY, weight=0.4, min_value=0.0, max_value=1.0),
        ObjectiveSpecification(EngineeringObjective.COST, weight=0.3, min_value=0.0, max_value=1.0),
        ObjectiveSpecification(EngineeringObjective.WEIGHT, weight=0.2, min_value=0.0, max_value=1000.0),
        ObjectiveSpecification(EngineeringObjective.MANUFACTURABILITY, weight=0.1, min_value=0.0, max_value=1.0),
    ]

    return MultiObjectiveOptimizer(objectives, OptimizationStrategy.DYNAMIC_AGGREGATION)


def create_thermal_optimization() -> MultiObjectiveOptimizer:
    """Create optimizer for thermal management problems."""
    objectives = [
        ObjectiveSpecification(EngineeringObjective.EFFICIENCY, weight=0.3, min_value=0.0, max_value=1.0),
        ObjectiveSpecification(EngineeringObjective.SAFETY, weight=0.3, min_value=0.0, max_value=1.0),
        ObjectiveSpecification(EngineeringObjective.COST, weight=0.2, min_value=0.0, max_value=1.0),
        ObjectiveSpecification(EngineeringObjective.RELIABILITY, weight=0.2, min_value=0.0, max_value=1.0),
    ]

    return MultiObjectiveOptimizer(objectives, OptimizationStrategy.PARETO_DOMINANCE)


# CLI interface
async def main():
    """CLI interface for multi-objective optimization."""
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Objective Optimization for Engineering")
    parser.add_argument(
        "--problem", choices=["structural", "thermal"], default="structural", help="Type of engineering problem"
    )
    parser.add_argument("--iterations", type=int, default=1000, help="Maximum optimization iterations")
    parser.add_argument("--output", default="./optimization_results.json", help="Output file for results")

    args = parser.parse_args()

    # Create optimizer
    if args.problem == "structural":
        optimizer = create_structural_optimization()
    else:
        optimizer = create_thermal_optimization()

    # Run optimization
    best_solution, pareto_front = await optimizer.optimize()

    # Generate and save report
    report = optimizer.generate_report()

    # Add Pareto front solutions
    report["pareto_front_solutions"] = [
        asdict(solution)
        for solution in pareto_front.solutions[:20]  # Limit to 20 solutions
    ]

    # Save results
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"Optimization completed! Results saved to {args.output}")
    print(f"Pareto front size: {len(pareto_front.solutions)}")
    print(f"Best solution objectives: {best_solution.objectives}")


if __name__ == "__main__":
    asyncio.run(main())
