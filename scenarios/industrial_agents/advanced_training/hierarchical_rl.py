"""
Hierarchical Reinforcement Learning for Complex Engineering Workflows

Implements hierarchical RL architectures for complex mechanical engineering tasks:
- Multi-level decision making for design processes
- Subtask decomposition and coordination
- Temporal abstraction for long-horizon problems
- Goal-conditioned policies for engineering workflows
"""

import asyncio
import json
import logging
import uuid
from collections import defaultdict
from collections import deque
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

import networkx as nx
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

logger = logging.getLogger(__name__)


class HierarchyLevel(Enum):
    """Levels in the engineering hierarchy."""

    STRATEGIC = "strategic"  # High-level project goals
    TACTICAL = "tactical"  # Design strategy and approach
    OPERATIONAL = "operational"  # Specific engineering tasks
    EXECUTION = "execution"  # Detailed implementation


class EngineeringDomain(Enum):
    """Engineering domains for specialization."""

    MECHANICAL_DESIGN = "mechanical_design"
    THERMAL_MANAGEMENT = "thermal_management"
    STRUCTURAL_ANALYSIS = "structural_analysis"
    FLUID_DYNAMICS = "fluid_dynamics"
    MANUFACTURING = "manufacturing"
    CONTROL_SYSTEMS = "control_systems"
    MATERIALS_SCIENCE = "materials_science"


class TaskStatus(Enum):
    """Status of engineering tasks."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class EngineeringTask:
    """Represents an engineering task in the hierarchy."""

    task_id: str
    name: str
    domain: EngineeringDomain
    level: HierarchyLevel
    description: str
    subtasks: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)
    requirements: dict[str, Any] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    priority: float = 0.5
    estimated_duration: float = 1.0
    actual_duration: float = 0.0
    start_time: datetime | None = None
    end_time: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_ready(self, completed_tasks: set) -> bool:
        """Check if task is ready to start based on dependencies."""
        return all(dep in completed_tasks for dep in self.dependencies)

    def get_state_vector(self) -> np.ndarray:
        """Get numerical state representation."""
        return np.array(
            [
                self.priority,
                self.estimated_duration,
                len(self.subtasks),
                len(self.dependencies),
                len(self.constraints),
                1.0 if self.status == TaskStatus.COMPLETED else 0.0,
                1.0 if self.status == TaskStatus.IN_PROGRESS else 0.0,
                1.0 if self.status == TaskStatus.FAILED else 0.0,
            ],
            dtype=np.float32,
        )


@dataclass
class HierarchyState:
    """State representation for hierarchical RL."""

    current_level: HierarchyLevel
    active_tasks: list[EngineeringTask]
    completed_tasks: list[EngineeringTask]
    available_actions: list[str]
    context: dict[str, Any] = field(default_factory=dict)
    time_step: int = 0
    project_progress: float = 0.0

    def to_tensor(self, max_tasks: int = 20) -> torch.Tensor:
        """Convert state to tensor representation."""
        # Pad task lists to fixed size
        active_features = []
        for task in self.active_tasks[:max_tasks]:
            active_features.extend(task.get_state_vector())

        # Pad with zeros if needed
        while len(active_features) < max_tasks * 8:
            active_features.extend([0.0] * 8)

        completed_features = []
        for task in self.completed_tasks[:max_tasks]:
            completed_features.extend(task.get_state_vector())

        # Pad with zeros if needed
        while len(completed_features) < max_tasks * 8:
            completed_features.extend([0.0] * 8)

        # Global features
        global_features = [
            self.time_step / 1000.0,  # Normalized time
            self.project_progress,
            len(self.active_tasks) / max_tasks,
            len(self.completed_tasks) / max_tasks,
            len(self.available_actions) / 20.0,
        ]

        return torch.tensor(active_features + completed_features + global_features, dtype=torch.float32)


class HierarchicalPolicy(nn.Module):
    """Hierarchical policy network for engineering tasks."""

    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256, num_levels: int = 4):
        super().__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.hidden_dim = hidden_dim
        self.num_levels = num_levels

        # Level-specific networks
        self.level_networks = nn.ModuleDict(
            {
                level.value: nn.Sequential(
                    nn.Linear(state_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, action_dim),
                    nn.Softmax(dim=-1),
                )
                for level in HierarchyLevel
            }
        )

        # Goal conditioning network
        self.goal_encoder = nn.Sequential(
            nn.Linear(32, hidden_dim // 2),  # Goal vector size
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, hidden_dim),
            nn.ReLU(),
        )

        # Level selector
        self.level_selector = nn.Sequential(
            nn.Linear(state_dim + hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, num_levels),
            nn.Softmax(dim=-1),
        )

        # Value function
        self.value_network = nn.Sequential(
            nn.Linear(state_dim + hidden_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, 1)
        )

    def forward(self, state: torch.Tensor, goal: torch.Tensor = None) -> dict[str, torch.Tensor]:
        """Forward pass through hierarchical policy."""
        batch_size = state.shape[0]

        # Encode goal if provided
        if goal is not None:
            goal_features = self.goal_encoder(goal)
            combined_input = torch.cat([state, goal_features], dim=-1)
        else:
            # Default goal vector
            default_goal = torch.zeros(batch_size, 32)
            goal_features = self.goal_encoder(default_goal)
            combined_input = torch.cat([state, goal_features], dim=-1)

        # Select active level
        level_probs = self.level_selector(combined_input)

        # Get action distributions for each level
        action_distributions = {}
        for level in HierarchyLevel:
            action_distributions[level.value] = self.level_networks[level.value](state)

        # Weight actions by level probabilities
        final_action_probs = torch.zeros(batch_size, self.action_dim)
        for i, level in enumerate(HierarchyLevel):
            level_weight = level_probs[:, i : i + 1]
            final_action_probs += level_weight * action_distributions[level.value]

        # Value prediction
        value = self.value_network(combined_input)

        return {
            "action_probs": final_action_probs,
            "value": value,
            "level_probs": level_probs,
            "level_actions": action_distributions,
        }


class TaskDecomposer:
    """Handles task decomposition for hierarchical planning."""

    def __init__(self):
        self.decomposition_rules = {}
        self.domain_knowledge = {}
        self._initialize_decomposition_rules()

    def _initialize_decomposition_rules(self):
        """Initialize task decomposition rules."""
        # Mechanical design decompositions
        self.decomposition_rules["mechanical_design"] = {
            "design_pump_enclosure": [
                "geometric_design",
                "material_selection",
                "structural_analysis",
                "manufacturability_review",
                "acoustic_analysis",
            ],
            "optimize_cooling_system": [
                "thermal_analysis",
                "component_selection",
                "fluid_dynamics_simulation",
                "integration_design",
            ],
            "manufacturing feasibility": [
                "process_selection",
                "tool_access_analysis",
                "cost_estimation",
                "quality_control_plan",
            ],
        }

        # Domain-specific knowledge
        self.domain_knowledge["mechanical_design"] = {
            "typical_duration": {
                "geometric_design": 2.0,
                "material_selection": 1.0,
                "structural_analysis": 3.0,
                "manufacturability_review": 1.5,
                "acoustic_analysis": 2.5,
            },
            "required_tools": {
                "geometric_design": ["cad_software", "design_guidelines"],
                "structural_analysis": ["fea_software", "material_database"],
                "acoustic_analysis": ["acoustic_simulator", "measurement_equipment"],
            },
            "common_constraints": [
                "safety_regulations",
                "cost_limits",
                "manufacturing_capabilities",
                "environmental_requirements",
            ],
        }

    def decompose_task(self, task: EngineeringTask) -> list[EngineeringTask]:
        """Decompose a task into subtasks."""
        if task.level == HierarchyLevel.EXECUTION:
            return []  # Cannot decompose further

        # Get decomposition rules for this task type
        domain_rules = self.decomposition_rules.get(task.domain.value, {})
        subtask_names = domain_rules.get(task.name, [])

        if not subtask_names:
            # Default decomposition for unknown tasks
            subtask_names = self._generate_default_decomposition(task)

        subtasks = []
        for i, subtask_name in enumerate(subtask_names):
            subtask = EngineeringTask(
                task_id=f"{task.task_id}_{i}",
                name=subtask_name,
                domain=task.domain,
                level=self._get_next_level(task.level),
                description=f"Subtask of {task.name}: {subtask_name}",
                dependencies=[task.task_id],
                priority=task.priority,
                estimated_duration=self._estimate_duration(subtask_name, task.domain),
            )

            subtasks.append(subtask)

        return subtasks

    def _generate_default_decomposition(self, task: EngineeringTask) -> list[str]:
        """Generate default decomposition for unknown tasks."""
        if task.level == HierarchyLevel.STRATEGIC:
            return ["planning_phase", "design_phase", "implementation_phase", "validation_phase"]
        if task.level == HierarchyLevel.TACTICAL:
            return ["analysis", "design", "verification"]
        if task.level == HierarchyLevel.OPERATIONAL:
            return ["preparation", "execution", "review"]
        return []

    def _get_next_level(self, current_level: HierarchyLevel) -> HierarchyLevel:
        """Get the next level in the hierarchy."""
        level_order = [
            HierarchyLevel.STRATEGIC,
            HierarchyLevel.TACTICAL,
            HierarchyLevel.OPERATIONAL,
            HierarchyLevel.EXECUTION,
        ]
        current_index = level_order.index(current_level)
        return level_order[min(current_index + 1, len(level_order) - 1)]

    def _estimate_duration(self, subtask_name: str, domain: EngineeringDomain) -> float:
        """Estimate duration for a subtask."""
        domain_knowledge = self.domain_knowledge.get(domain.value, {})
        durations = domain_knowledge.get("typical_duration", {})
        return durations.get(subtask_name, 1.0)


class WorkflowManager:
    """Manages engineering workflow execution."""

    def __init__(self, task_decomposer: TaskDecomposer):
        self.task_decomposer = task_decomposer
        self.task_graph = nx.DiGraph()
        self.active_tasks = {}
        self.completed_tasks = {}
        self.task_queue = deque()
        self.current_time = 0.0

    def initialize_workflow(self, root_task: EngineeringTask) -> None:
        """Initialize workflow with root task."""
        self.task_graph.clear()
        self.active_tasks.clear()
        self.completed_tasks.clear()
        self.task_queue.clear()

        # Add root task
        self.task_graph.add_node(root_task.task_id, task=root_task)
        self.active_tasks[root_task.task_id] = root_task

        # Decompose recursively
        self._decompose_recursive(root_task)

        # Initialize task queue
        self._update_task_queue()

    def _decompose_recursive(self, task: EngineeringTask) -> None:
        """Recursively decompose tasks."""
        if task.level == HierarchyLevel.EXECUTION:
            return

        # Decompose task
        subtasks = self.task_decomposer.decompose_task(task)

        for subtask in subtasks:
            # Add to graph
            self.task_graph.add_node(subtask.task_id, task=subtask)
            self.task_graph.add_edge(task.task_id, subtask.task_id)

            # Store in active tasks
            self.active_tasks[subtask.task_id] = subtask

            # Recursively decompose
            self._decompose_recursive(subtask)

    def _update_task_queue(self) -> None:
        """Update task queue with ready tasks."""
        completed_ids = set(self.completed_tasks.keys())

        # Find tasks that are ready to start
        ready_tasks = []
        for _task_id, task in self.active_tasks.items():
            if task.status == TaskStatus.PENDING and task.is_ready(completed_ids):
                ready_tasks.append(task)

        # Sort by priority and add to queue
        ready_tasks.sort(key=lambda t: t.priority, reverse=True)
        self.task_queue.extend(ready_tasks)

    def get_next_task(self) -> EngineeringTask | None:
        """Get next task to execute."""
        while self.task_queue:
            task = self.task_queue.popleft()
            if task.status == TaskStatus.PENDING:
                return task
        return None

    def complete_task(self, task_id: str, success: bool = True) -> None:
        """Mark task as completed."""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            task.end_time = datetime.now()

            if success:
                self.completed_tasks[task_id] = task
                del self.active_tasks[task_id]

            # Update queue with newly available tasks
            self._update_task_queue()

    def get_workflow_state(self) -> HierarchyState:
        """Get current workflow state."""
        all_tasks = list(self.active_tasks.values()) + list(self.completed_tasks.values())
        active_levels = {task.level for task in self.active_tasks.values()}

        # Determine current level (highest priority)
        current_level = HierarchyLevel.EXECUTION
        for level in [HierarchyLevel.STRATEGIC, HierarchyLevel.TACTICAL, HierarchyLevel.OPERATIONAL]:
            if level in active_levels:
                current_level = level
                break

        # Calculate project progress
        total_tasks = len(all_tasks)
        completed_count = len(self.completed_tasks)
        progress = completed_count / total_tasks if total_tasks > 0 else 0.0

        return HierarchyState(
            current_level=current_level,
            active_tasks=list(self.active_tasks.values()),
            completed_tasks=list(self.completed_tasks.values()),
            available_actions=[t.name for t in self.task_queue],
            time_step=int(self.current_time),
            project_progress=progress,
        )


class HierarchicalRLTrainer:
    """Trainer for hierarchical RL agents."""

    def __init__(
        self,
        policy_network: HierarchicalPolicy,
        workflow_manager: WorkflowManager,
        learning_rate: float = 3e-4,
        gamma: float = 0.99,
        entropy_coef: float = 0.01,
    ):
        self.policy = policy_network
        self.workflow_manager = workflow_manager
        self.gamma = gamma
        self.entropy_coef = entropy_coef

        self.optimizer = optim.Adam(policy_network.parameters(), lr=learning_rate)

        # Experience storage
        self.episodes = []
        self.current_episode = []

        # Training metrics
        self.training_losses = []
        self.level_usage = defaultdict(int)
        self.task_completion_rates = defaultdict(float)

    def collect_experience(
        self, state: HierarchyState, action: int, reward: float, next_state: HierarchyState, done: bool
    ) -> None:
        """Collect experience for training."""
        experience = {"state": state, "action": action, "reward": reward, "next_state": next_state, "done": done}
        self.current_episode.append(experience)

    def end_episode(self) -> None:
        """End current episode and store for training."""
        if self.current_episode:
            self.episodes.append(self.current_episode.copy())
            self.current_episode.clear()

    def compute_returns(self, episode: list[dict]) -> list[float]:
        """Compute discounted returns for episode."""
        returns = []
        discounted_return = 0

        for experience in reversed(episode):
            discounted_return = experience["reward"] + self.gamma * discounted_return
            returns.insert(0, discounted_return)

        return returns

    def train_step(self) -> dict[str, float]:
        """Perform one training step."""
        if len(self.episodes) < 1:
            return {}

        # Sample random episode
        episode = np.random.choice(self.episodes)
        returns = self.compute_returns(episode)

        # Convert states to tensors
        states = torch.stack([exp["state"].to_tensor() for exp in episode])
        actions = torch.tensor([exp["action"] for exp in episode])
        returns = torch.tensor(returns, dtype=torch.float32)

        # Forward pass
        policy_output = self.policy(states)

        action_probs = policy_output["action_probs"]
        values = policy_output["value"].squeeze()

        # Calculate advantages
        advantages = returns - values
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # Calculate policy loss
        log_probs = torch.log(action_probs.gather(1, actions.unsqueeze(1)).squeeze())
        policy_loss = -(log_probs * advantages.detach()).mean()

        # Calculate value loss
        value_loss = nn.functional.mse_loss(values, returns)

        # Calculate entropy loss
        entropy = -(action_probs * torch.log(action_probs + 1e-8)).sum(dim=-1).mean()
        entropy_loss = -self.entropy_coef * entropy

        # Total loss
        total_loss = policy_loss + 0.5 * value_loss + entropy_loss

        # Update network
        self.optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 0.5)
        self.optimizer.step()

        # Store metrics
        loss_dict = {
            "policy_loss": policy_loss.item(),
            "value_loss": value_loss.item(),
            "entropy_loss": entropy_loss.item(),
            "total_loss": total_loss.item(),
        }
        self.training_losses.append(loss_dict)

        return loss_dict

    async def train_workflow(self, root_task: EngineeringTask, max_steps: int = 1000) -> dict[str, Any]:
        """Train agent on a complete workflow."""
        logger.info(f"Starting hierarchical RL training for workflow: {root_task.name}")

        # Initialize workflow
        self.workflow_manager.initialize_workflow(root_task)

        total_reward = 0.0
        step = 0

        while step < max_steps:
            # Get current state
            state = self.workflow_manager.get_workflow_state()

            # Get action from policy
            state_tensor = state.to_tensor()
            policy_output = self.policy(state_tensor.unsqueeze(0))

            action_probs = policy_output["action_probs"].squeeze()
            action_dist = torch.distributions.Categorical(action_probs)
            action = action_dist.sample()

            # Execute action
            reward, done = await self._execute_action(action.item(), state)

            # Get next state
            next_state = self.workflow_manager.get_workflow_state()

            # Store experience
            self.collect_experience(state, action.item(), reward, next_state, done)
            total_reward += reward

            # Train if we have enough experience
            if len(self.episodes) >= 10:
                self.train_step()

            step += 1
            self.workflow_manager.current_time += 0.1

            if done:
                break

        # End episode
        self.end_episode()

        # Calculate final metrics
        final_state = self.workflow_manager.get_workflow_state()
        completion_rate = final_state.project_progress

        return {
            "total_reward": total_reward,
            "steps_taken": step,
            "completion_rate": completion_rate,
            "tasks_completed": len(self.workflow_manager.completed_tasks),
            "final_level": final_state.current_level.value,
        }

    async def _execute_action(self, action: int, state: HierarchyState) -> tuple[float, bool]:
        """Execute selected action and return reward."""
        # Get available tasks
        available_tasks = self.workflow_manager.get_next_task()
        if not available_tasks:
            return -0.1, True  # Small penalty for no available actions

        # For simplicity, assume action corresponds to task index
        if action >= len(available_tasks):
            return -0.5, False  # Penalty for invalid action

        task = available_tasks
        task.status = TaskStatus.IN_PROGRESS
        task.start_time = datetime.now()

        # Simulate task execution
        execution_time = task.estimated_duration
        success_probability = 0.8 + 0.2 * task.priority  # Higher priority = higher success

        # Simulate execution result
        await asyncio.sleep(0.01)  # Minimal delay for simulation
        success = np.random.random() < success_probability

        if success:
            # Calculate reward based on task properties
            base_reward = 1.0
            efficiency_bonus = max(0, 1.0 - execution_time / task.estimated_duration)
            priority_bonus = task.priority

            reward = base_reward + efficiency_bonus + priority_bonus
            self.workflow_manager.complete_task(task.task_id, True)
        else:
            reward = -0.5  # Penalty for failure
            self.workflow_manager.complete_task(task.task_id, False)

        # Check if workflow is complete
        workflow_complete = len(self.workflow_manager.active_tasks) == 0

        return reward, workflow_complete

    def get_training_summary(self) -> dict[str, Any]:
        """Get training summary statistics."""
        if not self.training_losses:
            return {"status": "No training data available"}

        recent_losses = self.training_losses[-100:] if len(self.training_losses) > 100 else self.training_losses

        avg_policy_loss = np.mean([loss["policy_loss"] for loss in recent_losses])
        avg_value_loss = np.mean([loss["value_loss"] for loss in recent_losses])
        avg_total_loss = np.mean([loss["total_loss"] for loss in recent_losses])

        return {
            "total_episodes": len(self.episodes),
            "recent_performance": {
                "avg_policy_loss": avg_policy_loss,
                "avg_value_loss": avg_value_loss,
                "avg_total_loss": avg_total_loss,
            },
            "training_stability": np.std([loss["total_loss"] for loss in recent_losses]),
            "level_usage_distribution": dict(self.level_usage),
        }


# Factory functions for creating hierarchical RL setups
def create_cad_design_hierarchy() -> tuple[HierarchicalPolicy, WorkflowManager, HierarchicalRLTrainer]:
    """Create hierarchical RL setup for CAD design tasks."""
    # Initialize components
    task_decomposer = TaskDecomposer()
    workflow_manager = WorkflowManager(task_decomposer)

    # Create policy network
    state_dim = 20 * 8 * 2 + 5  # max_tasks * features * 2 + global_features
    action_dim = 20  # Maximum number of possible actions
    policy = HierarchicalPolicy(state_dim, action_dim)

    # Create trainer
    trainer = HierarchicalRLTrainer(policy, workflow_manager)

    return policy, workflow_manager, trainer


def create_root_task(domain: EngineeringDomain, task_name: str, description: str) -> EngineeringTask:
    """Create a root task for hierarchical training."""
    return EngineeringTask(
        task_id=str(uuid.uuid4()),
        name=task_name,
        domain=domain,
        level=HierarchyLevel.STRATEGIC,
        description=description,
        priority=0.8,
        estimated_duration=10.0,
    )


# CLI interface
async def main():
    """CLI interface for hierarchical RL training."""
    import argparse

    parser = argparse.ArgumentParser(description="Hierarchical RL Training for Engineering Workflows")
    parser.add_argument(
        "--domain", choices=[d.value for d in EngineeringDomain], default="mechanical_design", help="Engineering domain"
    )
    parser.add_argument("--task", default="design_pump_enclosure", help="Root task name")
    parser.add_argument("--max-steps", type=int, default=1000, help="Maximum training steps")
    parser.add_argument("--episodes", type=int, default=10, help="Number of training episodes")

    args = parser.parse_args()

    # Create hierarchical RL setup
    policy, workflow_manager, trainer = create_cad_design_hierarchy()

    # Create root task
    domain = EngineeringDomain(args.domain)
    root_task = create_root_task(
        domain=domain, task_name=args.task, description=f"Complete {args.task} for {domain.value}"
    )

    # Train across multiple episodes
    all_results = []
    for episode in range(args.episodes):
        logger.info(f"Training episode {episode + 1}/{args.episodes}")

        result = await trainer.train_workflow(root_task, args.max_steps)
        all_results.append(result)

        logger.info(
            f"Episode {episode + 1} completed: "
            f"Reward={result['total_reward']:.2f}, "
            f"Completion={result['completion_rate']:.2%}"
        )

    # Generate summary
    training_summary = trainer.get_training_summary()
    training_summary["episode_results"] = all_results
    training_summary["average_completion_rate"] = np.mean([r["completion_rate"] for r in all_results])
    training_summary["average_reward"] = np.mean([r["total_reward"] for r in all_results])

    # Save results
    output_file = f"hrl_training_{args.domain}_{args.task}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(training_summary, f, indent=2, default=str)

    print("Hierarchical RL training completed!")
    print(f"Results saved to: {output_file}")
    print(f"Average completion rate: {training_summary['average_completion_rate']:.2%}")
    print(f"Average reward: {training_summary['average_reward']:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
