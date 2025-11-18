"""
Safety-Critical Training Protocols for Engineering Agents

Implements comprehensive safety training and validation systems:
- Constraint-based reinforcement learning for safety requirements
- Robustness training for edge cases and failure scenarios
- Verification and validation training protocols
- Fail-safe mechanisms and error recovery training
- Safety compliance and regulatory requirement training
"""

import asyncio
import json
import logging
import uuid
from collections import defaultdict
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional
import torch.optim as optim

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety criticality levels."""

    NON_CRITICAL = "non_critical"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SAFETY_CRITICAL = "safety_critical"
    LIFE_CRITICAL = "life_critical"


class SafetyCategory(Enum):
    """Categories of safety requirements."""

    STRUCTURAL_INTEGRITY = "structural_integrity"
    THERMAL_SAFETY = "thermal_safety"
    ELECTRICAL_SAFETY = "electrical_safety"
    CHEMICAL_SAFETY = "chemical_safety"
    OPERATIONAL_SAFETY = "operational_safety"
    ENVIRONMENTAL_SAFETY = "environmental_safety"
    HUMAN_FACTORS = "human_factors"
    EMERGENCY_PROCEDURES = "emergency_procedures"


class FailureMode(Enum):
    """Types of failure modes to train against."""

    MATERIAL_FAILURE = "material_failure"
    DESIGN_ERROR = "design_error"
    MANUFACTURING_DEFECT = "manufacturing_defect"
    OPERATIONAL_ERROR = "operational_error"
    ENVIRONMENTAL_EXPOSURE = "environmental_exposure"
    SOFTWARE_BUG = "software_bug"
    SENSOR_FAILURE = "sensor_failure"
    ACTUATOR_FAILURE = "actuator_failure"
    COMMUNICATION_FAILURE = "communication_failure"


@dataclass
class SafetyConstraint:
    """Safety constraint specification."""

    constraint_id: str
    name: str
    category: SafetyCategory
    safety_level: SafetyLevel
    description: str
    threshold_value: float
    tolerance: float
    measurement_method: str
    validation_frequency: str
    criticality_weight: float = 1.0
    regulatory_reference: str | None = None
    historical_failures: list[str] = field(default_factory=list)

    def is_violated(self, measured_value: float) -> bool:
        """Check if constraint is violated."""
        return abs(measured_value - self.threshold_value) > self.tolerance

    def violation_severity(self, measured_value: float) -> float:
        """Calculate violation severity."""
        if not self.is_violated(measured_value):
            return 0.0

        excess = abs(measured_value - self.threshold_value) - self.tolerance
        severity = excess / self.tolerance if self.tolerance > 0 else float("inf")

        return min(severity, 10.0)  # Cap at 10.0


@dataclass
class SafetyScenario:
    """Safety training scenario."""

    scenario_id: str
    name: str
    description: str
    category: SafetyCategory
    safety_level: SafetyLevel
    initial_conditions: dict[str, Any] = field(default_factory=dict)
    failure_modes: list[FailureMode] = field(default_factory=list)
    success_criteria: dict[str, float] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    time_pressure: float = 1.0  # Multiplier for time constraints
    complexity_score: float = 0.5
    required_responses: list[str] = field(default_factory=list)
    learning_objectives: list[str] = field(default_factory=list)


@dataclass
class SafetyAssessment:
    """Safety assessment result."""

    assessment_id: str
    scenario_id: str
    agent_id: str
    timestamp: datetime
    safety_score: float
    constraint_violations: list[dict[str, Any]] = field(default_factory=list)
    response_times: dict[str, float] = field(default_factory=dict)
    decision_quality: float = 0.0
    risk_mitigation_effectiveness: float = 0.0
    overall_performance: float = 0.0
    recommendations: list[str] = field(default_factory=list)
    certification_level: str | None = None


class SafetyConstraintValidator:
    """Validates safety constraints during training."""

    def __init__(self):
        self.constraints: dict[str, SafetyConstraint] = {}
        self.violation_history: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.validation_rules = {}

    def register_constraint(self, constraint: SafetyConstraint):
        """Register a safety constraint."""
        self.constraints[constraint.constraint_id] = constraint
        logger.info(f"Registered safety constraint: {constraint.name}")

    def validate_state(self, state_data: dict[str, Any]) -> dict[str, Any]:
        """Validate current state against all constraints."""
        violations = []
        total_penalty = 0.0

        for constraint_id, constraint in self.constraints.items():
            if constraint.measurement_method in state_data:
                measured_value = state_data[constraint.measurement_method]

                if constraint.is_violated(measured_value):
                    severity = constraint.violation_severity(measured_value)
                    penalty = severity * constraint.criticality_weight

                    violation_record = {
                        "constraint_id": constraint_id,
                        "constraint_name": constraint.name,
                        "measured_value": measured_value,
                        "threshold": constraint.threshold_value,
                        "tolerance": constraint.tolerance,
                        "severity": severity,
                        "penalty": penalty,
                        "timestamp": datetime.now().isoformat(),
                    }

                    violations.append(violation_record)
                    total_penalty += penalty

                    # Record violation history
                    self.violation_history[constraint_id].append(violation_record)

        return {
            "violations": violations,
            "total_penalty": total_penalty,
            "safety_score": max(0.0, 1.0 - total_penalty / 10.0),  # Normalize to 0-1
            "is_safe": len(violations) == 0,
        }

    def get_constraint_statistics(self, constraint_id: str) -> dict[str, Any]:
        """Get statistics for a specific constraint."""
        if constraint_id not in self.constraints:
            return {"error": "Constraint not found"}

        violations = self.violation_history[constraint_id]
        constraint = self.constraints[constraint_id]

        if not violations:
            return {
                "constraint_name": constraint.name,
                "total_violations": 0,
                "violation_rate": 0.0,
                "average_severity": 0.0,
            }

        total_violations = len(violations)
        average_severity = np.mean([v["severity"] for v in violations])
        max_severity = max([v["severity"] for v in violations])

        # Calculate violation rate over time
        time_window = datetime.now().timestamp() - 86400  # Last 24 hours
        recent_violations = [v for v in violations if datetime.fromisoformat(v["timestamp"]).timestamp() > time_window]
        violation_rate = len(recent_violations) / 24.0  # Violations per hour

        return {
            "constraint_name": constraint.name,
            "total_violations": total_violations,
            "violation_rate": violation_rate,
            "average_severity": average_severity,
            "max_severity": max_severity,
            "recent_violations": len(recent_violations),
        }


class ConstrainedPolicyNetwork(nn.Module):
    """Neural network with safety constraint integration."""

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dims: list[int],
        safety_constraint_dim: int,
        constraint_layer_weight: float = 2.0,
    ):
        super().__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.safety_constraint_dim = safety_constraint_dim
        self.constraint_layer_weight = constraint_layer_weight

        # Base policy network
        layers = []
        prev_dim = state_dim

        for hidden_dim in hidden_dims:
            layers.extend([nn.Linear(prev_dim, hidden_dim), nn.ReLU(), nn.BatchNorm1d(hidden_dim), nn.Dropout(0.1)])
            prev_dim = hidden_dim

        self.base_network = nn.Sequential(*layers)

        # Action policy head
        self.policy_head = nn.Sequential(nn.Linear(prev_dim, action_dim), nn.Softmax(dim=-1))

        # Value function head
        self.value_head = nn.Linear(prev_dim, 1)

        # Safety constraint processing
        self.constraint_processor = nn.Sequential(
            nn.Linear(safety_constraint_dim, hidden_dims[-1]),
            nn.ReLU(),
            nn.Linear(hidden_dims[-1], hidden_dims[-1] // 2),
            nn.ReLU(),
        )

        # Safety-aware action modifier
        self.safety_modifier = nn.Sequential(
            nn.Linear(hidden_dims[-1] + hidden_dims[-1] // 2, hidden_dims[-1]),
            nn.ReLU(),
            nn.Linear(hidden_dims[-1], action_dim),
            nn.Tanh(),  # Outputs in [-1, 1] range for modification
        )

    def forward(self, state: torch.Tensor, safety_constraints: torch.Tensor) -> dict[str, torch.Tensor]:
        """Forward pass with safety constraint integration."""
        # Base features
        base_features = self.base_network(state)

        # Standard policy
        policy_probs = self.policy_head(base_features)
        value = self.value_head(base_features)

        # Process safety constraints
        safety_features = self.constraint_processor(safety_constraints)

        # Generate safety modification factors
        combined_features = torch.cat([base_features, safety_features], dim=-1)
        safety_modifications = self.safety_modifier(combined_features)

        # Apply safety modifications to policy
        # Convert modifications from [-1, 1] to multiplicative factors [0.1, 2.0]
        modification_factors = 1.0 + safety_modifications * 0.5
        modified_policy = policy_probs * modification_factors

        # Renormalize to ensure valid probability distribution
        modified_policy = torch.nn.functional.softmax(modified_policy, dim=-1)

        return {
            "policy": modified_policy,
            "original_policy": policy_probs,
            "value": value,
            "safety_modifications": safety_modifications,
            "modification_factors": modification_factors,
        }


class SafetyCritic:
    """Safety-focused critic for evaluating action safety."""

    def __init__(self, state_dim: int, action_dim: int, hidden_dims: list[int] = None):
        if hidden_dims is None:
            hidden_dims = [256, 128]

        self.network = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dims[0]),
            nn.ReLU(),
            nn.Linear(hidden_dims[0], hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(hidden_dims[1], 1),
            nn.Tanh(),  # Output in [-1, 1] range
        )

    def forward(self, state: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """Evaluate safety of state-action pair."""
        combined = torch.cat([state, action], dim=-1)
        return self.network(combined)


class RobustnessTrainer:
    """Trains agents for robustness against edge cases and failures."""

    def __init__(
        self,
        policy_network: ConstrainedPolicyNetwork,
        safety_critic: SafetyCritic,
        constraint_validator: SafetyConstraintValidator,
    ):
        self.policy_network = policy_network
        self.safety_critic = safety_critic
        self.constraint_validator = constraint_validator

        # Training components
        self.policy_optimizer = optim.Adam(policy_network.parameters(), lr=1e-4)
        self.critic_optimizer = optim.Adam(safety_critic.parameters(), lr=1e-4)

        # Training buffers
        self.safety_episodes: list[dict[str, Any]] = []
        self.failure_scenarios: list[SafetyScenario] = []
        self.robustness_metrics = defaultdict(list)

    def add_failure_scenario(self, scenario: SafetyScenario):
        """Add a failure scenario for training."""
        self.failure_scenarios.append(scenario)
        logger.info(f"Added failure scenario: {scenario.name}")

    async def train_on_failure_scenarios(
        self, num_episodes: int = 100, max_steps_per_episode: int = 50
    ) -> dict[str, Any]:
        """Train agent on failure scenarios."""
        logger.info(f"Starting robustness training on {len(self.failure_scenarios)} scenarios")

        total_rewards = []
        safety_violations = []
        recovery_success_rates = []

        for episode in range(num_episodes):
            # Randomly select a failure scenario
            scenario = np.random.choice(self.failure_scenarios)

            # Execute scenario
            episode_result = await self._execute_failure_scenario(scenario, max_steps_per_episode)

            total_rewards.append(episode_result["total_reward"])
            safety_violations.append(episode_result["safety_violations"])
            recovery_success_rates.append(episode_result["recovery_success_rate"])

            # Train on episode experience
            if episode_result["experience_buffer"]:
                await self._train_on_episode(episode_result["experience_buffer"])

            if episode % 20 == 0:
                avg_reward = np.mean(total_rewards[-20:])
                avg_violations = np.mean(safety_violations[-20:])
                logger.info(f"Episode {episode}: Avg Reward={avg_reward:.3f}, Avg Violations={avg_violations:.3f}")

        # Calculate final metrics
        final_metrics = {
            "average_reward": np.mean(total_rewards),
            "safety_violation_rate": np.mean(safety_violations),
            "recovery_success_rate": np.mean(recovery_success_rates),
            "robustness_score": self._calculate_robustness_score(
                total_rewards, safety_violations, recovery_success_rates
            ),
            "episodes_trained": num_episodes,
            "scenarios_covered": len({sc.scenario_id for sc in self.failure_scenarios}),
        }

        return final_metrics

    async def _execute_failure_scenario(self, scenario: SafetyScenario, max_steps: int) -> dict[str, Any]:
        """Execute a single failure scenario."""
        state = self._initialize_scenario_state(scenario)
        total_reward = 0.0
        safety_violations = 0
        recovery_attempts = 0
        successful_recoveries = 0

        experience_buffer = []

        for _step in range(max_steps):
            # Get safety constraints
            safety_constraints = self._get_safety_constraints(state, scenario)

            # Convert to tensors
            state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            constraints_tensor = torch.tensor(safety_constraints, dtype=torch.float32).unsqueeze(0)

            # Get action from policy
            with torch.no_grad():
                policy_output = self.policy_network(state_tensor, constraints_tensor)
                action_probs = policy_output["policy"]
                action_dist = torch.distributions.Categorical(action_probs)
                action = action_dist.sample()

            # Execute action and get next state
            next_state, reward, done, info = self._simulate_scenario_step(state, action.item(), scenario)

            # Validate safety
            validation_result = self.constraint_validator.validate_state(next_state)
            if validation_result["violations"]:
                safety_violations += len(validation_result["violations"])
                recovery_attempts += 1

                # Attempt recovery
                if self._attempt_recovery(next_state, scenario):
                    successful_recoveries += 1
                    reward += 0.5  # Bonus for successful recovery
                else:
                    reward -= 1.0  # Penalty for failed recovery

            # Store experience
            experience_buffer.append(
                {
                    "state": state,
                    "action": action.item(),
                    "reward": reward,
                    "next_state": next_state,
                    "done": done,
                    "safety_constraints": safety_constraints,
                    "safety_violation": len(validation_result["violations"]) > 0,
                }
            )

            total_reward += reward
            state = next_state

            if done:
                break

        recovery_success_rate = successful_recoveries / recovery_attempts if recovery_attempts > 0 else 1.0

        return {
            "total_reward": total_reward,
            "safety_violations": safety_violations,
            "recovery_success_rate": recovery_success_rate,
            "experience_buffer": experience_buffer,
        }

    def _initialize_scenario_state(self, scenario: SafetyScenario) -> list[float]:
        """Initialize state for failure scenario."""
        # Create base state with scenario-specific conditions
        base_state = np.random.randn(self.policy_network.state_dim).tolist()

        # Modify based on initial conditions
        if "stress_level" in scenario.initial_conditions:
            base_state[0] = scenario.initial_conditions["stress_level"]

        if "temperature" in scenario.initial_conditions:
            base_state[1] = scenario.initial_conditions["temperature"]

        if "pressure" in scenario.initial_conditions:
            base_state[2] = scenario.initial_conditions["pressure"]

        # Add failure mode indicators
        for failure_mode in scenario.failure_modes:
            if failure_mode == FailureMode.MATERIAL_FAILURE:
                base_state[10] = 1.0  # Material failure indicator
            elif failure_mode == FailureMode.SENSOR_FAILURE:
                base_state[11] = 1.0  # Sensor failure indicator
            elif failure_mode == FailureMode.ACTUATOR_FAILURE:
                base_state[12] = 1.0  # Actuator failure indicator

        return base_state

    def _get_safety_constraints(self, state: list[float], scenario: SafetyScenario) -> list[float]:
        """Get safety constraints for current state."""
        constraints = []

        # Stress constraint
        max_stress = 200.0  # MPa
        current_stress = abs(state[0]) * 100  # Normalize to MPa range
        stress_constraint = min(1.0, current_stress / max_stress)
        constraints.append(stress_constraint)

        # Temperature constraint
        max_temp = 150.0  # Celsius
        current_temp = abs(state[1]) * 50  # Normalize to temp range
        temp_constraint = min(1.0, current_temp / max_temp)
        constraints.append(temp_constraint)

        # Pressure constraint
        max_pressure = 10.0  # MPa
        current_pressure = abs(state[2]) * 5  # Normalize to pressure range
        pressure_constraint = min(1.0, current_pressure / max_pressure)
        constraints.append(pressure_constraint)

        # Failure mode constraints
        for _i, failure_mode in enumerate(scenario.failure_modes):
            if failure_mode == FailureMode.MATERIAL_FAILURE:
                constraints.append(state[10])  # Material failure severity
            elif failure_mode == FailureMode.SENSOR_FAILURE:
                constraints.append(state[11])  # Sensor failure severity
            elif failure_mode == FailureMode.ACTUATOR_FAILURE:
                constraints.append(state[12])  # Actuator failure severity

        # Pad to required dimension
        while len(constraints) < self.policy_network.safety_constraint_dim:
            constraints.append(0.0)

        return constraints[: self.policy_network.safety_constraint_dim]

    def _simulate_scenario_step(
        self, state: list[float], action: int, scenario: SafetyScenario
    ) -> tuple[list[float], float, bool, dict[str, Any]]:
        """Simulate one step in the failure scenario."""
        # Simple state transition simulation
        new_state = state.copy()

        # Apply action effects
        if action == 0:  # Reduce stress
            new_state[0] *= 0.9
        elif action == 1:  # Reduce temperature
            new_state[1] *= 0.9
        elif action == 2:  # Reduce pressure
            new_state[2] *= 0.9
        elif action == 3:  # Emergency shutdown
            new_state[0] *= 0.5
            new_state[1] *= 0.5
            new_state[2] *= 0.5

        # Add random noise and failure mode effects
        noise = np.random.randn(len(new_state)) * 0.01
        failure_effects = self._apply_failure_mode_effects(new_state, scenario.failure_modes)

        new_state = new_state + noise + failure_effects

        # Calculate reward
        reward = self._calculate_safety_reward(new_state, action, scenario)

        # Check termination conditions
        done = self._check_termination_conditions(new_state, scenario)

        info = {
            "safety_violations": self._count_safety_violations(new_state),
            "failure_active": any(new_state[i] > 0.8 for i in [10, 11, 12]),  # Failure indicators
            "time_step": len([s for s in self.failure_scenarios if s.scenario_id == scenario.scenario_id]),
        }

        return new_state, reward, done, info

    def _apply_failure_mode_effects(self, state: list[float], failure_modes: list[FailureMode]) -> list[float]:
        """Apply effects of active failure modes."""
        effects = [0.0] * len(state)

        for failure_mode in failure_modes:
            if failure_mode == FailureMode.MATERIAL_FAILURE:
                effects[0] += np.random.uniform(0.1, 0.3)  # Increased stress
                effects[3] += np.random.uniform(0.1, 0.2)  # Degraded structural integrity
            elif failure_mode == FailureMode.SENSOR_FAILURE:
                effects[4:8] = [np.random.uniform(-0.2, 0.2) for _ in range(4)]  # Noisy sensor readings
            elif failure_mode == FailureMode.ACTUATOR_FAILURE:
                effects[8:10] = [np.random.uniform(-0.3, 0.3) for _ in range(2)]  # Reduced actuator effectiveness

        return effects

    def _calculate_safety_reward(self, state: list[float], action: int, scenario: SafetyScenario) -> float:
        """Calculate safety-focused reward."""
        reward = 0.0

        # Base reward for maintaining safety
        if state[0] < 0.5:  # Stress level
            reward += 0.2
        if state[1] < 0.5:  # Temperature level
            reward += 0.2
        if state[2] < 0.5:  # Pressure level
            reward += 0.2

        # Penalty for safety violations
        violations = self._count_safety_violations(state)
        reward -= violations * 0.5

        # Bonus for emergency actions when needed
        if action == 3 and any(s > 0.7 for s in state[:3]):  # Emergency shutdown when critical
            reward += 0.5

        # Time pressure penalty (scenarios with higher time pressure require faster response)
        time_penalty = scenario.time_pressure * 0.01
        reward -= time_penalty

        return reward

    def _count_safety_violations(self, state: list[float]) -> int:
        """Count safety violations in current state."""
        violations = 0

        if state[0] > 0.8:  # High stress
            violations += 1
        if state[1] > 0.8:  # High temperature
            violations += 1
        if state[2] > 0.8:  # High pressure
            violations += 1

        return violations

    def _check_termination_conditions(self, state: list[float], scenario: SafetyScenario) -> bool:
        """Check if scenario should terminate."""
        # Critical failure conditions
        if any(s > 0.95 for s in state[:3]):  # Critical levels
            return True

        # Successful recovery conditions
        return all(s < 0.3 for s in state[:3]) and all(s < 0.1 for s in state[10:13])  # All safe

    def _attempt_recovery(self, state: list[float], scenario: SafetyScenario) -> bool:
        """Attempt recovery from unsafe state."""
        # Simulate recovery attempt
        recovery_success_probability = 0.7

        # Higher success probability for less severe conditions
        if state[0] < 0.7 and state[1] < 0.7 and state[2] < 0.7:
            recovery_success_probability = 0.9
        elif any(s > 0.9 for s in state[:3]):
            recovery_success_probability = 0.3

        return np.random.random() < recovery_success_probability

    async def _train_on_episode(self, experience_buffer: list[dict[str, Any]]):
        """Train policy and critic on episode experience."""
        if not experience_buffer:
            return

        # Convert experiences to tensors
        states = torch.tensor([exp["state"] for exp in experience_buffer], dtype=torch.float32)
        actions = torch.tensor([exp["action"] for exp in experience_buffer], dtype=torch.long)
        torch.tensor([exp["reward"] for exp in experience_buffer], dtype=torch.float32)
        safety_constraints = torch.tensor([exp["safety_constraints"] for exp in experience_buffer], dtype=torch.float32)

        # Calculate returns
        returns = []
        discounted_return = 0
        gamma = 0.99
        for exp in reversed(experience_buffer):
            discounted_return = exp["reward"] + gamma * discounted_return
            returns.insert(0, discounted_return)

        returns = torch.tensor(returns, dtype=torch.float32)

        # Normalize returns
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)

        # Train policy
        self.policy_optimizer.zero_grad()
        policy_output = self.policy_network(states, safety_constraints)
        action_probs = policy_output["policy"]

        # Calculate policy loss with safety weighting
        log_probs = torch.log(action_probs.gather(1, actions.unsqueeze(1)).squeeze())
        safety_weights = torch.tensor([1.0 if not exp["safety_violation"] else 2.0 for exp in experience_buffer])
        weighted_log_probs = log_probs * safety_weights

        policy_loss = -(weighted_log_probs * returns).mean()

        policy_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_network.parameters(), 0.5)
        self.policy_optimizer.step()

    def _calculate_robustness_score(
        self, rewards: list[float], violations: list[float], recoveries: list[float]
    ) -> float:
        """Calculate overall robustness score."""
        if not rewards:
            return 0.0

        avg_reward = np.mean(rewards)
        avg_violations = np.mean(violations)
        avg_recovery = np.mean(recoveries)

        # Weighted combination of metrics
        robustness_score = (
            0.4 * max(0, avg_reward)  # Reward component
            + 0.3 * (1.0 - min(1.0, avg_violations))  # Safety component
            + 0.3 * avg_recovery  # Recovery component
        )

        return max(0.0, min(1.0, robustness_score))


class SafetyCriticalTrainingSystem:
    """Main safety-critical training system."""

    def __init__(self, state_dim: int = 20, action_dim: int = 10, safety_constraint_dim: int = 10):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.safety_constraint_dim = safety_constraint_dim

        # Initialize components
        self.constraint_validator = SafetyConstraintValidator()
        self.policy_network = ConstrainedPolicyNetwork(state_dim, action_dim, [128, 64], safety_constraint_dim)
        self.safety_critic = SafetyCritic(state_dim, action_dim)
        self.robustness_trainer = RobustnessTrainer(self.policy_network, self.safety_critic, self.constraint_validator)

        # Training state
        self.training_history = []
        self.safety_assessments: list[SafetyAssessment] = []
        self.certification_records: dict[str, dict[str, Any]] = {}

        # Initialize standard safety constraints
        self._initialize_safety_constraints()

    def _initialize_safety_constraints(self):
        """Initialize standard engineering safety constraints."""
        constraints = [
            SafetyConstraint(
                constraint_id="max_stress",
                name="Maximum Allowable Stress",
                category=SafetyCategory.STRUCTURAL_INTEGRITY,
                safety_level=SafetyLevel.SAFETY_CRITICAL,
                description="Maximum stress allowed in structural components",
                threshold_value=200.0,  # MPa
                tolerance=10.0,
                measurement_method="von_mises_stress",
                validation_frequency="continuous",
                criticality_weight=2.0,
                regulatory_reference="ASME Boiler and Pressure Vessel Code",
            ),
            SafetyConstraint(
                constraint_id="max_temperature",
                name="Maximum Operating Temperature",
                category=SafetyCategory.THERMAL_SAFETY,
                safety_level=SafetyLevel.HIGH,
                description="Maximum safe operating temperature",
                threshold_value=150.0,  # Celsius
                tolerance=5.0,
                measurement_method="operating_temperature",
                validation_frequency="continuous",
                criticality_weight=1.5,
                regulatory_reference="IEC 60601-1",
            ),
            SafetyConstraint(
                constraint_id="max_pressure",
                name="Maximum System Pressure",
                category=SafetyCategory.STRUCTURAL_INTEGRITY,
                safety_level=SafetyLevel.SAFETY_CRITICAL,
                description="Maximum allowable system pressure",
                threshold_value=10.0,  # MPa
                tolerance=0.5,
                measurement_method="system_pressure",
                validation_frequency="continuous",
                criticality_weight=2.5,
            ),
            SafetyConstraint(
                constraint_id="vibration_limits",
                name="Vibration Amplitude Limits",
                category=SafetyCategory.STRUCTURAL_INTEGRITY,
                safety_level=SafetyLevel.MEDIUM,
                description="Maximum allowed vibration amplitude",
                threshold_value=5.0,  # mm/s
                tolerance=1.0,
                measurement_method="vibration_amplitude",
                validation_frequency="periodic",
                criticality_weight=1.0,
            ),
        ]

        for constraint in constraints:
            self.constraint_validator.register_constraint(constraint)

    async def train_agent(
        self, agent_id: str, training_scenarios: list[SafetyScenario] = None, num_episodes: int = 100
    ) -> dict[str, Any]:
        """Train agent on safety-critical scenarios."""
        logger.info(f"Starting safety-critical training for agent {agent_id}")

        # Use default scenarios if none provided
        if training_scenarios is None:
            training_scenarios = self._generate_default_scenarios()

        # Add scenarios to robustness trainer
        for scenario in training_scenarios:
            self.robustness_trainer.add_failure_scenario(scenario)

        # Train on failure scenarios
        training_results = await self.robustness_trainer.train_on_failure_scenarios(num_episodes=num_episodes)

        # Conduct final safety assessment
        assessment = await self._conduct_safety_assessment(agent_id, training_scenarios)
        self.safety_assessments.append(assessment)

        # Update training history
        training_record = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "training_results": training_results,
            "safety_assessment": asdict(assessment),
            "scenarios_trained": len(training_scenarios),
        }

        self.training_history.append(training_record)

        # Update certification if applicable
        self._update_certification(agent_id, assessment)

        return training_record

    def _generate_default_scenarios(self) -> list[SafetyScenario]:
        """Generate default safety training scenarios."""
        scenarios = []

        # Material failure scenario
        scenarios.append(
            SafetyScenario(
                scenario_id="material_failure_01",
                name="Catastrophic Material Failure",
                description="Sudden material failure in critical component",
                category=SafetyCategory.STRUCTURAL_INTEGRITY,
                safety_level=SafetyLevel.LIFE_CRITICAL,
                initial_conditions={"stress_level": 0.9, "material_integrity": 0.7},
                failure_modes=[FailureMode.MATERIAL_FAILURE],
                success_criteria={"survival_probability": 0.95, "response_time": 2.0},
                constraints=["max_stress", "structural_integrity"],
                time_pressure=2.0,
                complexity_score=0.8,
                required_responses=["emergency_shutdown", "failure_isolation", "safety_activation"],
            )
        )

        # Thermal runaway scenario
        scenarios.append(
            SafetyScenario(
                scenario_id="thermal_runaway_01",
                name="Thermal Runaway Event",
                description="Uncontrolled temperature increase leading to system failure",
                category=SafetyCategory.THERMAL_SAFETY,
                safety_level=SafetyLevel.SAFETY_CRITICAL,
                initial_conditions={"temperature": 0.8, "cooling_system_status": 0.3},
                failure_modes=[FailureMode.ACTUATOR_FAILURE, FailureMode.SENSOR_FAILURE],
                success_criteria={"temperature_control": 0.9, "system_integrity": 0.8},
                constraints=["max_temperature", "cooling_system_performance"],
                time_pressure=1.5,
                complexity_score=0.7,
                required_responses=["cooling_activation", "load_shedding", "emergency_procedures"],
            )
        )

        # Pressure vessel failure scenario
        scenarios.append(
            SafetyScenario(
                scenario_id="pressure_vessel_01",
                name="Pressure Vessel Over-pressurization",
                description="Rapid pressure increase beyond design limits",
                category=SafetyCategory.STRUCTURAL_INTEGRITY,
                safety_level=SafetyLevel.LIFE_CRITICAL,
                initial_conditions={"pressure": 0.85, "relief_valve_status": 0.4},
                failure_modes=[FailureMode.MANUFACTURING_DEFECT, FailureMode.SENSOR_FAILURE],
                success_criteria={"pressure_control": 0.95, "vessel_integrity": 0.9},
                constraints=["max_pressure", "relief_valve_operation"],
                time_pressure=3.0,
                complexity_score=0.9,
                required_responses=["pressure_relief", "emergency_depressurization", "area_evacuation"],
            )
        )

        return scenarios

    async def _conduct_safety_assessment(self, agent_id: str, scenarios: list[SafetyScenario]) -> SafetyAssessment:
        """Conduct comprehensive safety assessment."""
        logger.info(f"Conducting safety assessment for agent {agent_id}")

        total_safety_score = 0.0
        constraint_violations = []
        response_times = {}
        scenario_scores = []

        for scenario in scenarios:
            # Simulate agent response to scenario
            scenario_result = await self._simulate_scenario_response(agent_id, scenario)

            scenario_scores.append(scenario_result["safety_score"])
            total_safety_score += scenario_result["safety_score"]

            if scenario_result["violations"]:
                constraint_violations.extend(scenario_result["violations"])

            response_times[scenario.scenario_id] = scenario_result["response_time"]

        # Calculate overall metrics
        overall_safety_score = total_safety_score / len(scenarios)
        decision_quality = np.mean([sr["decision_quality"] for sr in scenario_scores])
        risk_mitigation = np.mean([sr["risk_mitigation"] for sr in scenario_scores])

        # Calculate overall performance
        overall_performance = 0.4 * overall_safety_score + 0.3 * decision_quality + 0.3 * risk_mitigation

        # Generate recommendations
        recommendations = self._generate_safety_recommendations(
            overall_safety_score, constraint_violations, scenario_scores
        )

        # Determine certification level
        certification_level = self._determine_certification_level(overall_performance)

        assessment = SafetyAssessment(
            assessment_id=str(uuid.uuid4()),
            scenario_id="comprehensive",
            agent_id=agent_id,
            timestamp=datetime.now(),
            safety_score=overall_safety_score,
            constraint_violations=constraint_violations,
            response_times=response_times,
            decision_quality=decision_quality,
            risk_mitigation_effectiveness=risk_mitigation,
            overall_performance=overall_performance,
            recommendations=recommendations,
            certification_level=certification_level,
        )

        return assessment

    async def _simulate_scenario_response(self, agent_id: str, scenario: SafetyScenario) -> dict[str, Any]:
        """Simulate agent response to safety scenario."""
        # This would interface with the actual agent in a real implementation
        # For now, simulate based on training level

        base_performance = 0.7  # Base performance level

        # Adjust based on scenario complexity and safety level
        complexity_factor = 1.0 - scenario.complexity_score * 0.2
        safety_factor = 1.0 - (scenario.safety_level.value.count("critical") - 1) * 0.1

        # Add randomness for realistic simulation
        performance_variation = np.random.normal(0, 0.1)

        safety_score = max(0.0, min(1.0, base_performance * complexity_factor * safety_factor + performance_variation))

        # Simulate response time based on time pressure
        base_response_time = 2.0  # seconds
        response_time = base_response_time * scenario.time_pressure * np.random.uniform(0.8, 1.2)

        # Simulate constraint violations
        violations = []
        if safety_score < 0.6:
            for constraint_id in scenario.constraints[:2]:  # Most critical constraints
                if np.random.random() > safety_score:
                    violations.append(
                        {
                            "constraint_id": constraint_id,
                            "severity": np.random.uniform(0.1, 0.5),
                            "scenario": scenario.scenario_id,
                        }
                    )

        return {
            "safety_score": safety_score,
            "response_time": response_time,
            "violations": violations,
            "decision_quality": safety_score * 0.9,
            "risk_mitigation": safety_score * 0.85,
        }

    def _generate_safety_recommendations(
        self, safety_score: float, violations: list[dict], scenario_scores: list[dict]
    ) -> list[str]:
        """Generate safety improvement recommendations."""
        recommendations = []

        if safety_score < 0.7:
            recommendations.append("Overall safety performance requires improvement")

        # Analyze violation patterns
        violation_constraints = [v["constraint_id"] for v in violations]
        constraint_counts = defaultdict(int)
        for constraint_id in violation_constraints:
            constraint_counts[constraint_id] += 1

        for constraint_id, count in constraint_counts.items():
            if count >= 2:
                recommendations.append(f"Focus training on {constraint_id} compliance")

        # Analyze scenario-specific performance
        low_scoring_scenarios = [i for i, score in enumerate(scenario_scores) if score["safety_score"] < 0.6]
        if len(low_scoring_scenarios) > len(scenario_scores) / 2:
            recommendations.append("Consider additional training on emergency procedures")

        return recommendations

    def _determine_certification_level(self, performance: float) -> str:
        """Determine safety certification level based on performance."""
        if performance >= 0.95:
            return "EXPERT"
        if performance >= 0.85:
            return "ADVANCED"
        if performance >= 0.75:
            return "COMPETENT"
        if performance >= 0.60:
            return "BASIC"
        return "INSUFFICIENT"

    def _update_certification(self, agent_id: str, assessment: SafetyAssessment):
        """Update agent certification records."""
        self.certification_records[agent_id] = {
            "latest_assessment": asdict(assessment),
            "certification_level": assessment.certification_level,
            "last_updated": assessment.timestamp.isoformat(),
            "assessment_history": [asdict(a) for a in self.safety_assessments if a.agent_id == agent_id],
        }

    def get_training_summary(self, agent_id: str = None) -> dict[str, Any]:
        """Get training summary for agent or system."""
        if agent_id:
            # Agent-specific summary
            agent_training = [t for t in self.training_history if t["agent_id"] == agent_id]
            if not agent_training:
                return {"error": "No training records found for agent"}

            latest_training = agent_training[-1]
            certification = self.certification_records.get(agent_id, {})

            return {
                "agent_id": agent_id,
                "latest_training": latest_training,
                "certification_level": certification.get("certification_level"),
                "total_training_sessions": len(agent_training),
                "safety_assessments": [asdict(a) for a in self.safety_assessments if a.agent_id == agent_id],
            }
        # System-wide summary
        return {
            "total_agents_trained": len({t["agent_id"] for t in self.training_history}),
            "total_training_sessions": len(self.training_history),
            "total_safety_assessments": len(self.safety_assessments),
            "certification_distribution": self._get_certification_distribution(),
            "constraint_statistics": {
                constraint_id: self.constraint_validator.get_constraint_statistics(constraint_id)
                for constraint_id in self.constraint_validator.constraints
            },
        }

    def _get_certification_distribution(self) -> dict[str, int]:
        """Get distribution of certification levels."""
        distribution = defaultdict(int)
        for cert_record in self.certification_records.values():
            level = cert_record.get("certification_level", "UNKNOWN")
            distribution[level] += 1
        return dict(distribution)

    def save_training_state(self, path: str):
        """Save training state and models."""
        save_data = {
            "policy_network_state": self.policy_network.state_dict(),
            "safety_critic_state": self.safety_critic.state_dict(),
            "training_history": self.training_history,
            "safety_assessments": [asdict(a) for a in self.safety_assessments],
            "certification_records": self.certification_records,
            "constraint_violation_history": dict(self.constraint_validator.violation_history),
        }

        torch.save(save_data, path)
        logger.info(f"Safety training state saved to {path}")

    def load_training_state(self, path: str):
        """Load training state and models."""
        save_data = torch.load(path, map_location="cpu")

        self.policy_network.load_state_dict(save_data["policy_network_state"])
        self.safety_critic.load_state_dict(save_data["safety_critic_state"])
        self.training_history = save_data["training_history"]
        self.safety_assessments = [SafetyAssessment(**a) for a in save_data["safety_assessments"]]
        self.certification_records = save_data["certification_records"]
        self.constraint_validator.violation_history = defaultdict(list, save_data["constraint_violation_history"])

        logger.info(f"Safety training state loaded from {path}")


# CLI interface
async def main():
    """CLI interface for safety-critical training."""
    import argparse

    parser = argparse.ArgumentParser(description="Safety-Critical Training System")
    parser.add_argument("--action", choices=["train", "assess", "summary"], required=True, help="Action to perform")
    parser.add_argument("--agent-id", help="Agent ID")
    parser.add_argument("--episodes", type=int, default=100, help="Number of training episodes")
    parser.add_argument("--model-path", default="./safety_model.pt", help="Path to save/load model")
    parser.add_argument("--scenarios-file", help="JSON file with custom scenarios")

    args = parser.parse_args()

    # Initialize safety training system
    safety_system = SafetyCriticalTrainingSystem()

    if args.action == "train":
        if not args.agent_id:
            print("Error: --agent-id required for train action")
            return

        # Load custom scenarios if provided
        scenarios = None
        if args.scenarios_file:
            try:
                with open(args.scenarios_file) as f:
                    scenario_data = json.load(f)
                    scenarios = [SafetyScenario(**s) for s in scenario_data]
            except Exception as e:
                print(f"Error loading scenarios: {e}")
                return

        # Train agent
        result = await safety_system.train_agent(args.agent_id, scenarios, args.episodes)

        # Save model
        safety_system.save_training_state(args.model_path)
        print(f"Training completed and saved to {args.model_path}")

        # Display results
        print(f"\nTraining Results for {args.agent_id}:")
        print(f"  Robustness Score: {result['training_results']['robustness_score']:.3f}")
        print(f"  Safety Violation Rate: {result['training_results']['safety_violation_rate']:.3f}")
        print(f"  Recovery Success Rate: {result['training_results']['recovery_success_rate']:.3f}")
        print(f"  Certification Level: {result['safety_assessment']['certification_level']}")

    elif args.action == "assess":
        if not args.agent_id:
            print("Error: --agent-id required for assess action")
            return

        # Load model if exists
        if Path(args.model_path).exists():
            safety_system.load_training_state(args.model_path)

        # Generate assessment scenarios
        scenarios = safety_system._generate_default_scenarios()
        assessment = await safety_system._conduct_safety_assessment(args.agent_id, scenarios)

        print(f"\nSafety Assessment for {args.agent_id}:")
        print(f"  Overall Safety Score: {assessment.safety_score:.3f}")
        print(f"  Decision Quality: {assessment.decision_quality:.3f}")
        print(f"  Risk Mitigation: {assessment.risk_mitigation_effectiveness:.3f}")
        print(f"  Overall Performance: {assessment.overall_performance:.3f}")
        print(f"  Certification Level: {assessment.certification_level}")

        if assessment.recommendations:
            print("  Recommendations:")
            for rec in assessment.recommendations:
                print(f"    - {rec}")

    elif args.action == "summary":
        # Load model if exists
        if Path(args.model_path).exists():
            safety_system.load_training_state(args.model_path)

        if args.agent_id:
            summary = safety_system.get_training_summary(args.agent_id)
            print(f"\nTraining Summary for {args.agent_id}:")
        else:
            summary = safety_system.get_training_summary()
            print("\nSystem-wide Training Summary:")

        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
