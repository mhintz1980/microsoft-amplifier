"""
Meta-Learning System for Rapid Domain Adaptation in Engineering Agents

Implements advanced meta-learning techniques for quick adaptation to new engineering domains:
- MAML (Model-Agnostic Meta-Learning) for few-shot adaptation
- ProtoNets for metric learning across engineering tasks
- Memory-augmented networks for knowledge retention
- Continual learning with catastrophic forgetting prevention
"""

import asyncio
import json
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

logger = logging.getLogger(__name__)


class MetaLearningStrategy(Enum):
    """Meta-learning strategies."""

    MAML = "maml"  # Model-Agnostic Meta-Learning
    PROTO_NETS = "proto_nets"  # Prototypical Networks
    REPTILE = "reptile"  # First-order MAML
    META_SGD = "meta_sgd"  # Meta-SGD
    MEMORY_AUGMENTED = "memory_augmented"  # Memory networks
    CONTINUAL = "continual"  # Continual learning


class EngineeringDomain(Enum):
    """Engineering domains for meta-learning."""

    MECHANICAL_DESIGN = "mechanical_design"
    THERMAL_ANALYSIS = "thermal_analysis"
    STRUCTURAL_ANALYSIS = "structural_analysis"
    FLUID_DYNAMICS = "fluid_dynamics"
    MANUFACTURING = "manufacturing"
    CONTROL_SYSTEMS = "control_systems"
    MATERIALS_SCIENCE = "materials_science"
    ACOUSTICS = "acoustics"
    VIBRATION = "vibration"
    ELECTROMAGNETICS = "electromagnetics"


@dataclass
class Task:
    """Represents a learning task for meta-learning."""

    task_id: str
    domain: EngineeringDomain
    name: str
    description: str
    support_data: list[dict[str, Any]] = field(default_factory=list)
    query_data: list[dict[str, Any]] = field(default_factory=list)
    task_metadata: dict[str, Any] = field(default_factory=dict)

    def get_support_tensors(self) -> tuple[torch.Tensor, torch.Tensor]:
        """Convert support data to tensors."""
        if not self.support_data:
            return torch.empty(0), torch.empty(0)

        features = torch.tensor([item["features"] for item in self.support_data], dtype=torch.float32)
        labels = torch.tensor([item["label"] for item in self.support_data], dtype=torch.long)
        return features, labels

    def get_query_tensors(self) -> tuple[torch.Tensor, torch.Tensor]:
        """Convert query data to tensors."""
        if not self.query_data:
            return torch.empty(0), torch.empty(0)

        features = torch.tensor([item["features"] for item in self.query_data], dtype=torch.float32)
        labels = torch.tensor([item["label"] for item in self.query_data], dtype=torch.long)
        return features, labels


@dataclass
class DomainKnowledge:
    """Knowledge about an engineering domain."""

    domain: EngineeringDomain
    key_concepts: list[str] = field(default_factory=list)
    typical_parameters: dict[str, tuple[float, float]] = field(default_factory=dict)
    common_constraints: list[str] = field(default_factory=list)
    expert_rules: list[str] = field(default_factory=list)
    performance_metrics: list[str] = field(default_factory=list)
    data_characteristics: dict[str, Any] = field(default_factory=dict)


class FeatureExtractor(nn.Module):
    """Feature extractor for engineering data."""

    def __init__(self, input_dim: int, hidden_dims: list[int], output_dim: int):
        super().__init__()
        layers = []

        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.extend([nn.Linear(prev_dim, hidden_dim), nn.ReLU(), nn.BatchNorm1d(hidden_dim), nn.Dropout(0.1)])
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, output_dim))

        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class PrototypicalNetwork(nn.Module):
    """Prototypical network for few-shot learning."""

    def __init__(self, input_dim: int, hidden_dims: list[int], embedding_dim: int):
        super().__init__()
        self.feature_extractor = FeatureExtractor(input_dim, hidden_dims, embedding_dim)
        self.embedding_dim = embedding_dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Extract embeddings."""
        return self.feature_extractor(x)

    def compute_prototypes(self, support_features: torch.Tensor, support_labels: torch.Tensor) -> torch.Tensor:
        """Compute class prototypes from support set."""
        num_classes = support_labels.max().item() + 1
        prototypes = torch.zeros(num_classes, self.embedding_dim)

        for class_id in range(num_classes):
            class_mask = support_labels == class_id
            if class_mask.sum() > 0:
                class_features = support_features[class_mask]
                prototypes[class_id] = class_features.mean(dim=0)

        return prototypes

    def classify(self, query_features: torch.Tensor, prototypes: torch.Tensor) -> torch.Tensor:
        """Classify query samples using prototypes."""
        distances = torch.cdist(query_features, prototypes)
        return -distances  # Negative distances for higher probability = closer


class MAMLModel(nn.Module):
    """MAML (Model-Agnostic Meta-Learning) implementation."""

    def __init__(self, input_dim: int, hidden_dims: list[int], output_dim: int):
        super().__init__()
        self.feature_extractor = FeatureExtractor(input_dim, hidden_dims, hidden_dims[-1])
        self.classifier = nn.Linear(hidden_dims[-1], output_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.feature_extractor(x)
        return self.classifier(features)

    def clone_parameters(self) -> dict[str, torch.Tensor]:
        """Clone model parameters for inner loop updates."""
        return {name: param.clone() for name, param in self.named_parameters()}

    def load_parameters(self, parameters: dict[str, torch.Tensor]):
        """Load parameters into model."""
        for name, param in self.named_parameters():
            param.data.copy_(parameters[name])


class MemoryAugmentedNetwork(nn.Module):
    """Memory-augmented network for engineering knowledge storage."""

    def __init__(self, input_dim: int, memory_size: int, memory_dim: int, output_dim: int):
        super().__init__()
        self.memory_size = memory_size
        self.memory_dim = memory_dim

        # Feature extractor
        self.feature_extractor = nn.Sequential(nn.Linear(input_dim, 256), nn.ReLU(), nn.Linear(256, memory_dim))

        # External memory
        self.memory = nn.Parameter(torch.randn(memory_size, memory_dim) * 0.1)

        # Memory interface
        self.key_transform = nn.Linear(memory_dim, memory_dim)
        self.value_transform = nn.Linear(memory_dim, memory_dim)

        # Output layer
        self.output_layer = nn.Sequential(nn.Linear(memory_dim * 2, 256), nn.ReLU(), nn.Linear(256, output_dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with memory access."""
        x.shape[0]

        # Extract features
        query = self.feature_extractor(x)

        # Generate key for memory addressing
        key = self.key_transform(query)

        # Compute attention over memory
        memory_keys = self.key_transform(self.memory)
        attention_weights = F.softmax(torch.matmul(key, memory_keys.t()) / np.sqrt(self.memory_dim), dim=1)

        # Retrieve memory values
        memory_values = self.value_transform(self.memory)
        retrieved_memory = torch.matmul(attention_weights, memory_values)

        # Combine query and retrieved memory
        combined = torch.cat([query, retrieved_memory], dim=1)

        # Generate output
        output = self.output_layer(combined)
        return output

    def write_to_memory(self, keys: torch.Tensor, values: torch.Tensor, write_strength: float = 1.0):
        """Write new information to memory."""
        with torch.no_grad():
            # Find least used memory slots (simple LRU)
            torch.zeros(self.memory_size)

            # For now, just overwrite random slots
            num_writes = min(keys.shape[0], self.memory_size)
            write_indices = torch.randperm(self.memory_size)[:num_writes]

            self.memory.data[write_indices] = keys[:num_writes] * write_strength


class MetaLearningTrainer:
    """Meta-learning trainer for engineering agents."""

    def __init__(
        self,
        strategy: MetaLearningStrategy,
        input_dim: int,
        output_dim: int,
        hidden_dims: list[int] = None,
        embedding_dim: int = 128,
        memory_size: int = 1000,
    ):
        self.strategy = strategy
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.embedding_dim = embedding_dim
        self.memory_size = memory_size

        if hidden_dims is None:
            hidden_dims = [256, 128]

        # Initialize model based on strategy
        if strategy == MetaLearningStrategy.PROTO_NETS:
            self.model = PrototypicalNetwork(input_dim, hidden_dims, embedding_dim)
        elif strategy == MetaLearningStrategy.MAML:
            self.model = MAMLModel(input_dim, hidden_dims, output_dim)
        elif strategy == MetaLearningStrategy.MEMORY_AUGMENTED:
            self.model = MemoryAugmentedNetwork(input_dim, memory_size, embedding_dim, output_dim)
        else:
            # Default to MAML for other strategies
            self.model = MAMLModel(input_dim, hidden_dims, output_dim)

        # Optimizers
        self.meta_optimizer = optim.Adam(self.model.parameters(), lr=1e-3)
        self.inner_lr = 0.01

        # Training state
        self.training_history = []
        self.domain_performance = defaultdict(list)
        self.adaptation_history = []

    def meta_train(self, task_batch: list[Task], num_inner_steps: int = 5, num_epochs: int = 100) -> dict[str, Any]:
        """Perform meta-training on a batch of tasks."""
        logger.info(f"Starting meta-training with {len(task_batch)} tasks using {self.strategy.value}")

        for epoch in range(num_epochs):
            epoch_loss = 0.0
            adaptation_accuracies = []

            for task in task_batch:
                # Adapt to task
                if self.strategy == MetaLearningStrategy.MAML:
                    loss, accuracy = self._maml_adaptation(task, num_inner_steps)
                elif self.strategy == MetaLearningStrategy.PROTO_NETS:
                    loss, accuracy = self._proto_net_adaptation(task)
                elif self.strategy == MetaLearningStrategy.MEMORY_AUGMENTED:
                    loss, accuracy = self._memory_augmented_adaptation(task)
                else:
                    # Default to MAML
                    loss, accuracy = self._maml_adaptation(task, num_inner_steps)

                epoch_loss += loss
                adaptation_accuracies.append(accuracy)

            # Meta-update
            self.meta_optimizer.zero_grad()
            epoch_loss /= len(task_batch)
            epoch_loss.backward()
            self.meta_optimizer.step()

            # Record metrics
            avg_accuracy = np.mean(adaptation_accuracies)
            self.training_history.append(
                {
                    "epoch": epoch,
                    "loss": epoch_loss.item(),
                    "adaptation_accuracy": avg_accuracy,
                    "strategy": self.strategy.value,
                }
            )

            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}: Loss={epoch_loss.item():.4f}, Adaptation Acc={avg_accuracy:.4f}")

        return {
            "final_loss": epoch_loss.item(),
            "final_accuracy": np.mean(adaptation_accuracies),
            "total_epochs": num_epochs,
            "strategy": self.strategy.value,
        }

    def _maml_adaptation(self, task: Task, num_inner_steps: int) -> tuple[torch.Tensor, float]:
        """MAML inner loop adaptation."""
        # Clone model parameters
        original_params = self.model.clone_parameters()
        adapted_params = original_params.copy()

        # Get task data
        support_features, support_labels = task.get_support_tensors()
        query_features, query_labels = task.get_query_tensors()

        if len(support_features) == 0 or len(query_features) == 0:
            return torch.tensor(0.0), 0.0

        # Inner loop adaptation
        inner_optimizer = torch.optim.SGD(list(adapted_params.values()), lr=self.inner_lr)

        for _ in range(num_inner_steps):
            # Load adapted parameters
            self.model.load_parameters(adapted_params)

            # Forward pass on support set
            predictions = self.model(support_features)
            loss = F.cross_entropy(predictions, support_labels)

            # Update parameters
            inner_optimizer.zero_grad()
            loss.backward()
            inner_optimizer.step()

            # Update adapted parameters
            adapted_params = {name: param.clone() for name, param in self.model.named_parameters()}

        # Load final adapted parameters
        self.model.load_parameters(adapted_params)

        # Evaluate on query set
        with torch.no_grad():
            query_predictions = self.model(query_features)
            query_loss = F.cross_entropy(query_predictions, query_labels)

            # Calculate accuracy
            accuracy = (query_predictions.argmax(dim=1) == query_labels).float().mean().item()

        # Restore original parameters for meta-update
        self.model.load_parameters(original_params)

        return query_loss, accuracy

    def _proto_net_adaptation(self, task: Task) -> tuple[torch.Tensor, float]:
        """Prototypical network adaptation."""
        support_features, support_labels = task.get_support_tensors()
        query_features, query_labels = task.get_query_tensors()

        if len(support_features) == 0 or len(query_features) == 0:
            return torch.tensor(0.0), 0.0

        # Extract embeddings
        support_embeddings = self.model(support_features)
        query_embeddings = self.model(query_features)

        # Compute prototypes
        prototypes = self.model.compute_prototypes(support_embeddings, support_labels)

        # Classify query samples
        logits = self.model.classify(query_embeddings, prototypes)

        # Calculate loss and accuracy
        loss = F.cross_entropy(logits, query_labels)
        accuracy = (logits.argmax(dim=1) == query_labels).float().mean().item()

        return loss, accuracy

    def _memory_augmented_adaptation(self, task: Task) -> tuple[torch.Tensor, float]:
        """Memory-augmented network adaptation."""
        support_features, support_labels = task.get_support_tensors()
        query_features, query_labels = task.get_query_tensors()

        if len(support_features) == 0 or len(query_features) == 0:
            return torch.tensor(0.0), 0.0

        # Write support set to memory
        support_embeddings = self.model.feature_extractor(support_features)
        self.model.write_to_memory(support_embeddings, support_embeddings)

        # Forward pass on query set
        predictions = self.model(query_features)
        loss = F.cross_entropy(predictions, query_labels)
        accuracy = (predictions.argmax(dim=1) == query_labels).float().mean().item()

        return loss, accuracy

    def adapt_to_domain(
        self, domain: EngineeringDomain, adaptation_data: list[dict[str, Any]], num_steps: int = 10
    ) -> dict[str, Any]:
        """Adapt model to a new engineering domain."""
        logger.info(f"Adapting model to domain: {domain.value}")

        # Create adaptation task
        split_point = max(1, len(adaptation_data) // 2)
        support_data = adaptation_data[:split_point]
        query_data = adaptation_data[split_point:]

        task = Task(
            task_id=f"adapt_{domain.value}",
            domain=domain,
            name=f"adaptation_task_{domain.value}",
            description=f"Adaptation to {domain.value}",
            support_data=support_data,
            query_data=query_data,
        )

        # Perform adaptation
        adaptation_history = []
        self.model.clone_parameters()

        for step in range(num_steps):
            if self.strategy == MetaLearningStrategy.MAML:
                loss, accuracy = self._maml_adaptation(task, 1)
            elif self.strategy == MetaLearningStrategy.PROTO_NETS:
                loss, accuracy = self._proto_net_adaptation(task)
            elif self.strategy == MetaLearningStrategy.MEMORY_AUGMENTED:
                loss, accuracy = self._memory_augmented_adaptation(task)
            else:
                loss, accuracy = self._maml_adaptation(task, 1)

            adaptation_history.append({"step": step, "loss": loss.item(), "accuracy": accuracy})

            if step % 5 == 0:
                logger.info(f"Adaptation step {step}: Loss={loss.item():.4f}, Acc={accuracy:.4f}")

        # Record adaptation
        final_accuracy = adaptation_history[-1]["accuracy"]
        self.domain_performance[domain.value].append(final_accuracy)
        self.adaptation_history.append(
            {
                "domain": domain.value,
                "timestamp": datetime.now().isoformat(),
                "final_accuracy": final_accuracy,
                "adaptation_steps": num_steps,
                "history": adaptation_history,
            }
        )

        return {
            "domain": domain.value,
            "final_accuracy": final_accuracy,
            "adaptation_history": adaptation_history,
            "improvement": final_accuracy - adaptation_history[0]["accuracy"] if adaptation_history else 0.0,
        }

    def save_model(self, path: str):
        """Save model and training state."""
        save_data = {
            "model_state_dict": self.model.state_dict(),
            "meta_optimizer_state_dict": self.meta_optimizer.state_dict(),
            "training_history": self.training_history,
            "domain_performance": dict(self.domain_performance),
            "adaptation_history": self.adaptation_history,
            "strategy": self.strategy.value,
            "model_config": {
                "input_dim": self.input_dim,
                "output_dim": self.output_dim,
                "embedding_dim": self.embedding_dim,
                "memory_size": self.memory_size,
            },
        }

        torch.save(save_data, path)
        logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load model and training state."""
        save_data = torch.load(path, map_location="cpu")

        self.model.load_state_dict(save_data["model_state_dict"])
        self.meta_optimizer.load_state_dict(save_data["meta_optimizer_state_dict"])
        self.training_history = save_data["training_history"]
        self.domain_performance = defaultdict(list, save_data["domain_performance"])
        self.adaptation_history = save_data["adaptation_history"]

        logger.info(f"Model loaded from {path}")

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary across domains."""
        if not self.domain_performance:
            return {"status": "No performance data available"}

        summary = {
            "strategy": self.strategy.value,
            "total_domains": len(self.domain_performance),
            "domain_performance": {},
        }

        for domain, performances in self.domain_performance.items():
            if performances:
                summary["domain_performance"][domain] = {
                    "mean_accuracy": np.mean(performances),
                    "std_accuracy": np.std(performances),
                    "max_accuracy": np.max(performances),
                    "min_accuracy": np.min(performances),
                    "num_adaptations": len(performances),
                    "recent_trend": "improving"
                    if len(performances) >= 3 and performances[-1] > performances[-3]
                    else "stable",
                }

        return summary


class DomainKnowledgeBase:
    """Knowledge base for engineering domains."""

    def __init__(self):
        self.domains: dict[EngineeringDomain, DomainKnowledge] = {}
        self._initialize_domain_knowledge()

    def _initialize_domain_knowledge(self):
        """Initialize knowledge for common engineering domains."""
        # Mechanical Design
        self.domains[EngineeringDomain.MECHANICAL_DESIGN] = DomainKnowledge(
            domain=EngineeringDomain.MECHANICAL_DESIGN,
            key_concepts=["stress", "strain", "deformation", "fatigue", "fracture"],
            typical_parameters={
                "youngs_modulus": (50e9, 210e9),  # Steel range
                "yield_strength": (200e6, 2000e6),
                "density": (1000, 8000),
                "safety_factor": (1.1, 5.0),
            },
            common_constraints=["stress_limits", "deflection_limits", "fatigue_life"],
            expert_rules=[
                "stress_concentration_reduction",
                "material_selection_optimization",
                "manufacturability_considerations",
            ],
            performance_metrics=["strength_to_weight", "cost_effectiveness", "reliability"],
        )

        # Thermal Analysis
        self.domains[EngineeringDomain.THERMAL_ANALYSIS] = DomainKnowledge(
            domain=EngineeringDomain.THERMAL_ANALYSIS,
            key_concepts=["heat_transfer", "conduction", "convection", "radiation", "thermal_expansion"],
            typical_parameters={
                "thermal_conductivity": (0.1, 400),  # W/m·K
                "specific_heat": (100, 5000),  # J/kg·K
                "thermal_expansion_coeff": (1e-6, 25e-6),  # 1/K
                "operating_temperature": (200, 1500),  # K
            },
            common_constraints=["temperature_limits", "thermal_stress", "heat_dissipation"],
            expert_rules=[
                "thermal_resistance_minimization",
                "heat_spreader_optimization",
                "thermal_interface_management",
            ],
            performance_metrics=["thermal_efficiency", "temperature_uniformity", "thermal_stability"],
        )

        # Structural Analysis
        self.domains[EngineeringDomain.STRUCTURAL_ANALYSIS] = DomainKnowledge(
            domain=EngineeringDomain.STRUCTURAL_ANALYSIS,
            key_concepts=["load_paths", "buckling", "vibration", "modal_analysis", "finite_element"],
            typical_parameters={
                "natural_frequency": (1, 10000),  # Hz
                "damping_ratio": (0.01, 0.2),
                "load_magnitude": (100, 1e6),  # N
                "displacement_limit": (0.01, 10),  # mm
            },
            common_constraints=["frequency_separation", "stress_limits", "stability_requirements"],
            expert_rules=["load_path_optimization", "resonance_avoidance", "buckling_prevention"],
            performance_metrics=["stiffness", "natural_frequency", "load_capacity"],
        )

    def get_domain_knowledge(self, domain: EngineeringDomain) -> DomainKnowledge | None:
        """Get knowledge for a specific domain."""
        return self.domains.get(domain)

    def generate_domain_features(self, domain: EngineeringDomain, input_data: dict[str, Any]) -> np.ndarray:
        """Generate domain-specific features from input data."""
        knowledge = self.get_domain_knowledge(domain)
        if not knowledge:
            return np.array([])

        features = []

        # Parameter-based features
        for param, (min_val, max_val) in knowledge.typical_parameters.items():
            if param in input_data:
                normalized = (input_data[param] - min_val) / (max_val - min_val)
                features.append(np.clip(normalized, 0, 1))
            else:
                features.append(0.5)  # Default value

        # Concept indicators
        for concept in knowledge.key_concepts:
            concept_present = any(concept.lower() in str(input_data.get(k, "")).lower() for k in input_data)
            features.append(1.0 if concept_present else 0.0)

        # Constraint indicators
        for constraint in knowledge.common_constraints:
            constraint_present = any(constraint.lower() in str(input_data.get(k, "")).lower() for k in input_data)
            features.append(1.0 if constraint_present else 0.0)

        return np.array(features, dtype=np.float32)

    def get_domain_similarity(self, domain1: EngineeringDomain, domain2: EngineeringDomain) -> float:
        """Calculate similarity between two engineering domains."""
        knowledge1 = self.get_domain_knowledge(domain1)
        knowledge2 = self.get_domain_knowledge(domain2)

        if not knowledge1 or not knowledge2:
            return 0.0

        # Concept similarity
        concepts1 = set(knowledge1.key_concepts)
        concepts2 = set(knowledge2.key_concepts)
        concept_sim = len(concepts1 & concepts2) / len(concepts1 | concepts2) if concepts1 | concepts2 else 0.0

        # Constraint similarity
        constraints1 = set(knowledge1.common_constraints)
        constraints2 = set(knowledge2.common_constraints)
        constraint_sim = (
            len(constraints1 & constraints2) / len(constraints1 | constraints2) if constraints1 | constraints2 else 0.0
        )

        # Metric similarity
        metrics1 = set(knowledge1.performance_metrics)
        metrics2 = set(knowledge2.performance_metrics)
        metric_sim = len(metrics1 & metrics2) / len(metrics1 | metrics2) if metrics1 | metrics2 else 0.0

        # Weighted average
        return 0.5 * concept_sim + 0.3 * constraint_sim + 0.2 * metric_sim


# Factory functions
def create_meta_learner(
    domain: EngineeringDomain,
    strategy: MetaLearningStrategy = MetaLearningStrategy.MAML,
    input_dim: int = 64,
    output_dim: int = 10,
) -> MetaLearningTrainer:
    """Create meta-learner for specific engineering domain."""
    return MetaLearningTrainer(
        strategy=strategy,
        input_dim=input_dim,
        output_dim=output_dim,
        hidden_dims=[128, 64],
        embedding_dim=64,
        memory_size=500,
    )


def generate_synthetic_task(
    domain: EngineeringDomain, num_support: int = 5, num_query: int = 10, input_dim: int = 64, num_classes: int = 5
) -> Task:
    """Generate synthetic task for testing."""
    knowledge_base = DomainKnowledgeBase()
    domain_knowledge = knowledge_base.get_domain_knowledge(domain)

    # Generate synthetic data
    def generate_sample(label: int) -> dict[str, Any]:
        features = np.random.randn(input_dim).astype(np.float32)

        # Add domain-specific patterns
        if domain_knowledge:
            domain_features = np.random.randn(min(20, input_dim)) * 0.3
            features[: len(domain_features)] += domain_features

        return {"features": features.tolist(), "label": label}

    support_data = [generate_sample(i % num_classes) for i in range(num_support)]
    query_data = [generate_sample(i % num_classes) for i in range(num_query)]

    return Task(
        task_id=f"synthetic_{domain.value}_{uuid.uuid4().hex[:8]}",
        domain=domain,
        name=f"synthetic_task_{domain.value}",
        description=f"Synthetic task for {domain.value}",
        support_data=support_data,
        query_data=query_data,
    )


# CLI interface
async def main():
    """CLI interface for meta-learning training."""
    import argparse

    parser = argparse.ArgumentParser(description="Meta-Learning for Engineering Domain Adaptation")
    parser.add_argument(
        "--domain",
        choices=[d.value for d in EngineeringDomain],
        default="mechanical_design",
        help="Target engineering domain",
    )
    parser.add_argument(
        "--strategy", choices=[s.value for s in MetaLearningStrategy], default="maml", help="Meta-learning strategy"
    )
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--tasks", type=int, default=10, help="Number of tasks per batch")
    parser.add_argument("--model-path", default="./meta_model.pt", help="Path to save model")
    parser.add_argument("--adapt-domain", help="Domain to adapt to after training")

    args = parser.parse_args()

    # Create domain and strategy enums
    domain = EngineeringDomain(args.domain)
    strategy = MetaLearningStrategy(args.strategy)

    # Generate synthetic tasks
    tasks = []
    for _i in range(args.tasks):
        task = generate_synthetic_task(domain, num_support=10, num_query=15)
        tasks.append(task)

    # Create meta-learner
    meta_learner = create_meta_learner(domain, strategy)

    # Train
    logger.info(f"Training meta-learner for {domain.value} using {strategy.value}")
    training_results = meta_learner.meta_train(tasks, num_epochs=args.epochs)

    print("Training completed:")
    print(f"  Final loss: {training_results['final_loss']:.4f}")
    print(f"  Final accuracy: {training_results['final_accuracy']:.4f}")

    # Save model
    meta_learner.save_model(args.model_path)
    print(f"Model saved to: {args.model_path}")

    # Optional adaptation to new domain
    if args.adapt_domain:
        adapt_domain = EngineeringDomain(args.adapt_domain)
        adaptation_data = []

        # Generate adaptation data
        for _i in range(20):
            task = generate_synthetic_task(adapt_domain, num_support=5, num_query=5)
            adaptation_data.extend(task.support_data + task.query_data)

        # Perform adaptation
        adaptation_results = meta_learner.adapt_to_domain(adapt_domain, adaptation_data)

        print(f"\nAdaptation to {adapt_domain.value}:")
        print(f"  Final accuracy: {adaptation_results['final_accuracy']:.4f}")
        print(f"  Improvement: {adaptation_results['improvement']:.4f}")

    # Performance summary
    summary = meta_learner.get_performance_summary()
    print("\nPerformance Summary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
