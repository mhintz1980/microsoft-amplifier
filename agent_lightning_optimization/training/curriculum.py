"""
Curriculum Learning Strategies for Progressive Agent Training.

This module implements sophisticated curriculum learning approaches that enable
agents to progressively learn from simple to complex tasks, improving training
efficiency and final performance.
"""

import math
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any

import numpy as np
from pydantic import BaseModel

from ..utils.logger import get_logger

logger = get_logger(__name__)


class DifficultyLevel(Enum):
    """Difficulty levels for curriculum learning."""

    BEGINNER = 1
    ELEMENTARY = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5


class CurriculumStrategy(Enum):
    """Types of curriculum learning strategies."""

    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    STEP_FUNCTION = "step_function"
    ADAPTIVE = "adaptive"
    SELF_PACED = "self_paced"
    TEACHER_FORCING = "teacher_forcing"


class TrainingStage(BaseModel):
    """Individual stage in a curriculum."""

    stage_id: str
    name: str
    difficulty_level: DifficultyLevel
    description: str
    required_accuracy: float = 0.8
    max_epochs: int = 100
    min_epochs: int = 10
    data_requirements: dict[str, Any] = field(default_factory=dict)
    evaluation_metrics: list[str] = field(default_factory=list)
    completion_criteria: dict[str, float] = field(default_factory=dict)


@dataclass
class CurriculumProgress:
    """Progress tracking for curriculum learning."""

    current_stage: int
    completed_stages: list[str]
    stage_performance: dict[str, dict[str, float]]
    total_epochs: int
    start_time: float
    stage_start_time: float
    adaptive_params: dict[str, float] = field(default_factory=dict)


class BaseCurriculumStrategy(ABC):
    """Base class for curriculum learning strategies."""

    def __init__(self, stages: list[TrainingStage]):
        self.stages = stages
        self.current_stage_idx = 0
        self.progress = CurriculumProgress(
            current_stage=0,
            completed_stages=[],
            stage_performance={},
            total_epochs=0,
            start_time=0.0,
            stage_start_time=0.0,
        )

    @abstractmethod
    def should_advance(self, stage_performance: dict[str, float]) -> bool:
        """Determine if training should advance to next stage."""
        pass

    @abstractmethod
    def get_training_params(self, epoch: int) -> dict[str, Any]:
        """Get training parameters for current epoch."""
        pass

    def get_current_stage(self) -> TrainingStage | None:
        """Get the current training stage."""
        if 0 <= self.current_stage_idx < len(self.stages):
            return self.stages[self.current_stage_idx]
        return None

    def advance_stage(self) -> bool:
        """Advance to the next stage."""
        if self.current_stage_idx < len(self.stages) - 1:
            current_stage = self.stages[self.current_stage_idx]
            self.progress.completed_stages.append(current_stage.stage_id)
            self.current_stage_idx += 1
            self.progress.current_stage = self.current_stage_idx
            self.progress.stage_start_time = 0.0  # Reset stage start time
            logger.info(f"Advanced to stage {self.current_stage_idx + 1}: {self.get_current_stage().name}")
            return True
        return False

    def is_complete(self) -> bool:
        """Check if curriculum is complete."""
        return self.current_stage_idx >= len(self.stages) - 1


class LinearCurriculumStrategy(BaseCurriculumStrategy):
    """Linear progression through curriculum stages."""

    def should_advance(self, stage_performance: dict[str, float]) -> bool:
        """Advance based on meeting accuracy threshold."""
        current_stage = self.get_current_stage()
        if not current_stage:
            return False

        # Check if required accuracy is met
        accuracy = stage_performance.get("accuracy", 0.0)
        if accuracy >= current_stage.required_accuracy:
            return True

        # Check if minimum epochs completed and performance plateaued
        epochs_in_stage = stage_performance.get("epochs_in_stage", 0)
        if epochs_in_stage >= current_stage.min_epochs:
            recent_improvement = stage_performance.get("recent_improvement", 1.0)
            if recent_improvement < 0.01:  # Performance plateaued
                return True

        return False

    def get_training_params(self, epoch: int) -> dict[str, Any]:
        """Get progressively challenging training parameters."""
        current_stage = self.get_current_stage()
        if not current_stage:
            return {}

        # Linear increase in difficulty
        progress_factor = (epoch - self.progress.stage_start_time) / current_stage.max_epochs
        progress_factor = min(1.0, max(0.0, progress_factor))

        return {
            "learning_rate": 0.001 * (1.0 - 0.5 * progress_factor),  # Decrease LR
            "batch_size": int(32 * (1.0 + 2.0 * progress_factor)),  # Increase batch size
            "data_difficulty": progress_factor,  # Increase data difficulty
            "noise_level": 0.1 * (1.0 - 0.8 * progress_factor),  # Decrease noise
            "regularization": 0.01 * (1.0 + progress_factor),  # Increase regularization
        }


class ExponentialCurriculumStrategy(BaseCurriculumStrategy):
    """Exponential progression through curriculum stages."""

    def should_advance(self, stage_performance: dict[str, float]) -> bool:
        """Advance with exponential acceleration."""
        current_stage = self.get_current_stage()
        if not current_stage:
            return False

        # Exponential decay of required epochs based on performance
        base_epochs = current_stage.min_epochs
        accuracy = stage_performance.get("accuracy", 0.0)

        if accuracy >= current_stage.required_accuracy:
            return True

        # Exponential reduction in required epochs as accuracy improves
        performance_factor = math.exp(-5 * (1.0 - accuracy))
        adjusted_min_epochs = int(base_epochs * performance_factor)

        epochs_in_stage = stage_performance.get("epochs_in_stage", 0)
        return epochs_in_stage >= adjusted_min_epochs

    def get_training_params(self, epoch: int) -> dict[str, Any]:
        """Get exponentially scaling training parameters."""
        current_stage = self.get_current_stage()
        if not current_stage:
            return {}

        epochs_in_stage = epoch - self.progress.stage_start_time
        progress_factor = epochs_in_stage / current_stage.max_epochs

        # Exponential scaling
        exp_factor = math.exp(2 * progress_factor) / math.exp(2)  # Normalized to [0, 1]

        return {
            "learning_rate": 0.001 * math.exp(-2 * exp_factor),
            "batch_size": int(32 * math.exp(exp_factor)),
            "data_difficulty": exp_factor,
            "complexity_penalty": 0.1 * exp_factor,
            "exploration_rate": 0.1 * math.exp(-2 * exp_factor),
        }


class AdaptiveCurriculumStrategy(BaseCurriculumStrategy):
    """Adaptive curriculum based on performance dynamics."""

    def __init__(self, stages: list[TrainingStage], adaptation_rate: float = 0.1):
        super().__init__(stages)
        self.adaptation_rate = adaptation_rate
        self.performance_history: list[dict[str, float]] = []
        self.difficulty_adjustment = 1.0

    def should_advance(self, stage_performance: dict[str, float]) -> bool:
        """Adaptive advancement based on performance trends."""
        current_stage = self.get_current_stage()
        if not current_stage:
            return False

        self.performance_history.append(stage_performance)
        if len(self.performance_history) > 10:
            self.performance_history.pop(0)

        # Analyze performance trend
        if len(self.performance_history) >= 3:
            recent_performance = [p.get("accuracy", 0.0) for p in self.performance_history[-3:]]
            trend = np.mean(np.diff(recent_performance))

            # Adaptive thresholds based on trend
            if trend > 0.05:  # Improving rapidly
                required_accuracy = current_stage.required_accuracy - 0.05
            elif trend < -0.02:  # Performance declining
                required_accuracy = current_stage.required_accuracy + 0.1
                self.difficulty_adjustment *= 0.9  # Reduce difficulty
            else:
                required_accuracy = current_stage.required_accuracy

            accuracy = stage_performance.get("accuracy", 0.0)
            return accuracy >= required_accuracy

        return stage_performance.get("accuracy", 0.0) >= current_stage.required_accuracy

    def get_training_params(self, epoch: int) -> dict[str, Any]:
        """Get adaptive training parameters."""
        current_stage = self.get_current_stage()
        if not current_stage:
            return {}

        # Analyze recent performance to adjust parameters
        if len(self.performance_history) >= 5:
            recent_acc = [p.get("accuracy", 0.0) for p in self.performance_history[-5:]]
            volatility = np.std(recent_acc)
            trend = np.mean(np.diff(recent_acc))

            # Adaptive learning rate
            if volatility > 0.1:  # High volatility - reduce LR
                lr_multiplier = 0.5
            elif trend < -0.02:  # Declining performance - reduce LR
                lr_multiplier = 0.7
            else:
                lr_multiplier = 1.0

            # Adaptive batch size
            if volatility > 0.05:  # High volatility - smaller batch
                batch_multiplier = 0.8
            else:
                batch_multiplier = 1.2
        else:
            lr_multiplier = 1.0
            batch_multiplier = 1.0

        epochs_in_stage = epoch - self.progress.stage_start_time
        base_progress = epochs_in_stage / current_stage.max_epochs

        return {
            "learning_rate": 0.001 * lr_multiplier * self.difficulty_adjustment,
            "batch_size": int(32 * batch_multiplier),
            "data_difficulty": base_progress * self.difficulty_adjustment,
            "regularization": 0.01 * (1.0 / self.difficulty_adjustment),
            "dropout": 0.1 * (1.0 + (1.0 - self.difficulty_adjustment)),
        }


class SelfPacedCurriculumStrategy(BaseCurriculumStrategy):
    """Self-paced learning based on loss difficulty."""

    def __init__(self, stages: list[TrainingStage], pace_factor: float = 0.5):
        super().__init__(stages)
        self.pace_factor = pace_factor
        self.sample_difficulties: list[float] = []
        self.current_difficulty_threshold = 0.0

    def should_advance(self, stage_performance: dict[str, float]) -> bool:
        """Advance based on self-paced learning criteria."""
        current_stage = self.get_current_stage()
        if not current_stage:
            return False

        # Self-paced advancement based on average loss
        avg_loss = stage_performance.get("loss", 1.0)
        epochs_in_stage = stage_performance.get("epochs_in_stage", 0)

        # Reduce difficulty threshold as training progresses
        self.current_difficulty_threshold = math.exp(-self.pace_factor * epochs_in_stage / 10)

        # Advance if most samples are learned
        learned_ratio = stage_performance.get("learned_ratio", 0.0)
        return learned_ratio > 0.8 and avg_loss < 0.5

    def get_training_params(self, epoch: int) -> dict[str, Any]:
        """Get self-paced training parameters."""
        current_stage = self.get_current_stage()
        if not current_stage:
            return {}

        # Sample difficulty selection
        epochs_in_stage = epoch - self.progress.stage_start_time
        pace_progress = min(1.0, epochs_in_stage / (current_stage.max_epochs * 0.7))

        return {
            "learning_rate": 0.001 * (1.0 - 0.5 * pace_progress),
            "batch_size": int(32 * (1.0 + pace_progress)),
            "difficulty_threshold": self.current_difficulty_threshold,
            "sample_weighting": self._compute_sample_weights(),
            "curriculum_lambda": self.pace_factor * (1.0 - 0.5 * pace_progress),
        }

    def _compute_sample_weights(self) -> dict[str, float]:
        """Compute sample weights based on difficulty."""
        if not self.sample_difficulties:
            return {"uniform": 1.0}

        # Weight easier samples more heavily initially
        avg_difficulty = np.mean(self.sample_difficulties)
        weights = {}

        for i, difficulty in enumerate(self.sample_difficulties):
            weight = math.exp(-self.pace_factor * (difficulty - avg_difficulty))
            weights[f"sample_{i}"] = weight

        return weights


class MechanicalEngineeringCurriculum:
    """Specialized curriculum for mechanical engineering agents."""

    @staticmethod
    def create_cad_analysis_curriculum() -> list[TrainingStage]:
        """Create curriculum for CAD analysis agent."""
        return [
            TrainingStage(
                stage_id="cad_basics",
                name="Basic CAD Analysis",
                difficulty_level=DifficultyLevel.BEGINNER,
                description="Learn to identify basic geometric features and simple design issues",
                required_accuracy=0.7,
                max_epochs=50,
                min_epochs=10,
                data_requirements={
                    "min_complexity": 1,
                    "max_features": 5,
                    "file_types": ["simple_shapes", "basic_parts"],
                },
                evaluation_metrics=["accuracy", "feature_detection_rate"],
                completion_criteria={"accuracy": 0.7, "feature_detection_rate": 0.8},
            ),
            TrainingStage(
                stage_id="geometric_analysis",
                name="Geometric Analysis",
                difficulty_level=DifficultyLevel.ELEMENTARY,
                description="Analyze geometric relationships and dimensional constraints",
                required_accuracy=0.75,
                max_epochs=60,
                min_epochs=15,
                data_requirements={"min_complexity": 2, "max_features": 10, "file_types": ["assemblies", "mechanisms"]},
                evaluation_metrics=["accuracy", "dimensional_accuracy", "constraint_detection"],
                completion_criteria={"accuracy": 0.75, "dimensional_accuracy": 0.8},
            ),
            TrainingStage(
                stage_id="structural_analysis",
                name="Structural Analysis",
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                description="Evaluate structural integrity and safety factors",
                required_accuracy=0.8,
                max_epochs=80,
                min_epochs=20,
                data_requirements={
                    "min_complexity": 3,
                    "max_features": 15,
                    "file_types": ["load_bearing_parts", "structural_assemblies"],
                },
                evaluation_metrics=["accuracy", "safety_factor_prediction", "stress_analysis"],
                completion_criteria={"accuracy": 0.8, "safety_factor_prediction": 0.85},
            ),
            TrainingStage(
                stage_id="acoustic_analysis",
                name="Acoustic Analysis",
                difficulty_level=DifficultyLevel.ADVANCED,
                description="Analyze acoustic performance and noise characteristics",
                required_accuracy=0.8,
                max_epochs=100,
                min_epochs=25,
                data_requirements={
                    "min_complexity": 4,
                    "max_features": 20,
                    "file_types": ["enclosures", "acoustic_assemblies"],
                },
                evaluation_metrics=["accuracy", "stc_prediction", "noise_reduction"],
                completion_criteria={"accuracy": 0.8, "stc_prediction": 0.85},
            ),
            TrainingStage(
                stage_id="integrated_analysis",
                name="Integrated Design Review",
                difficulty_level=DifficultyLevel.EXPERT,
                description="Comprehensive analysis of complex mechanical systems",
                required_accuracy=0.85,
                max_epochs=120,
                min_epochs=30,
                data_requirements={
                    "min_complexity": 5,
                    "max_features": 30,
                    "file_types": ["complete_systems", "industrial_machinery"],
                },
                evaluation_metrics=["accuracy", "overall_rating", "recommendation_quality"],
                completion_criteria={"accuracy": 0.85, "overall_rating": 0.8},
            ),
        ]

    @staticmethod
    def create_rag_curriculum() -> list[TrainingStage]:
        """Create curriculum for RAG-based technical Q&A."""
        return [
            TrainingStage(
                stage_id="basic_retrieval",
                name="Basic Information Retrieval",
                difficulty_level=DifficultyLevel.BEGINNER,
                description="Learn to retrieve relevant technical information",
                required_accuracy=0.75,
                max_epochs=40,
                min_epochs=10,
                data_requirements={
                    "document_types": ["specifications", "manuals"],
                    "query_complexity": "simple",
                    "answer_length": "short",
                },
                evaluation_metrics=["retrieval_accuracy", "answer_relevance"],
                completion_criteria={"retrieval_accuracy": 0.8},
            ),
            TrainingStage(
                stage_id="technical_reasoning",
                name="Technical Reasoning",
                difficulty_level=DifficultyLevel.ELEMENTARY,
                description="Apply technical reasoning to answer questions",
                required_accuracy=0.75,
                max_epochs=50,
                min_epochs=15,
                data_requirements={
                    "document_types": ["technical_guides", "procedures"],
                    "query_complexity": "moderate",
                    "answer_length": "medium",
                },
                evaluation_metrics=["reasoning_accuracy", "source_attribution"],
                completion_criteria={"reasoning_accuracy": 0.8},
            ),
            TrainingStage(
                stage_id="safety_critical_qa",
                name="Safety-Critical Q&A",
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                description="Handle safety-critical technical questions",
                required_accuracy=0.85,
                max_epochs=60,
                min_epochs=20,
                data_requirements={
                    "document_types": ["safety_manuals", "regulations"],
                    "query_complexity": "complex",
                    "answer_length": "detailed",
                },
                evaluation_metrics=["safety_accuracy", "warning_inclusion", "source_quality"],
                completion_criteria={"safety_accuracy": 0.9, "warning_inclusion": 0.95},
            ),
            TrainingStage(
                stage_id="troubleshooting_qa",
                name="Troubleshooting Q&A",
                difficulty_level=DifficultyLevel.ADVANCED,
                description="Provide troubleshooting guidance and solutions",
                required_accuracy=0.8,
                max_epochs=80,
                min_epochs=25,
                data_requirements={
                    "document_types": ["troubleshooting_guides", "repair_manuals"],
                    "query_complexity": "very_complex",
                    "answer_length": "comprehensive",
                },
                evaluation_metrics=["solution_accuracy", "step_clarity", "practicality"],
                completion_criteria={"solution_accuracy": 0.85, "step_clarity": 0.8},
            ),
            TrainingStage(
                stage_id="expert_consultation",
                name="Expert Consultation",
                difficulty_level=DifficultyLevel.EXPERT,
                description="Provide expert-level technical consultation",
                required_accuracy=0.85,
                max_epochs=100,
                min_epochs=30,
                data_requirements={
                    "document_types": ["all_types"],
                    "query_complexity": "expert_level",
                    "answer_length": "comprehensive",
                },
                evaluation_metrics=["expertise_level", "completeness", "accuracy"],
                completion_criteria={"expertise_level": 0.85, "accuracy": 0.9},
            ),
        ]

    @staticmethod
    def create_ui_generation_curriculum() -> list[TrainingStage]:
        """Create curriculum for industrial UI generation."""
        return [
            TrainingStage(
                stage_id="basic_components",
                name="Basic UI Components",
                difficulty_level=DifficultyLevel.BEGINNER,
                description="Generate basic UI components with proper structure",
                required_accuracy=0.7,
                max_epochs=30,
                min_epochs=8,
                data_requirements={
                    "component_types": ["buttons", "inputs", "labels"],
                    "complexity": "simple",
                    "framework": "html",
                },
                evaluation_metrics=["html_validity", "component_functionality"],
                completion_criteria={"html_validity": 0.95},
            ),
            TrainingStage(
                stage_id="responsive_design",
                name="Responsive Design",
                difficulty_level=DifficultyLevel.ELEMENTARY,
                description="Create responsive layouts for different screen sizes",
                required_accuracy=0.75,
                max_epochs=40,
                min_epochs=12,
                data_requirements={
                    "component_types": ["layouts", "forms"],
                    "complexity": "moderate",
                    "framework": "html_css",
                },
                evaluation_metrics=["responsiveness", "layout_quality"],
                completion_criteria={"responsiveness": 0.8},
            ),
            TrainingStage(
                stage_id="industrial_interfaces",
                name="Industrial Interfaces",
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                description="Design interfaces for industrial environments",
                required_accuracy=0.8,
                max_epochs=50,
                min_epochs=15,
                data_requirements={
                    "component_types": ["dashboards", "control_panels"],
                    "complexity": "complex",
                    "framework": "react",
                },
                evaluation_metrics=["accessibility", "contrast_ratio", "usability"],
                completion_criteria={"accessibility": 0.8, "contrast_ratio": 0.9},
            ),
            TrainingStage(
                stage_id="data_visualization",
                name="Data Visualization",
                difficulty_level=DifficultyLevel.ADVANCED,
                description="Create real-time data visualization interfaces",
                required_accuracy=0.8,
                max_epochs=60,
                min_epochs=20,
                data_requirements={
                    "component_types": ["charts", "graphs", "real_time_displays"],
                    "complexity": "very_complex",
                    "framework": "vue",
                },
                evaluation_metrics=["visualization_accuracy", "performance", "interactivity"],
                completion_criteria={"visualization_accuracy": 0.85},
            ),
            TrainingStage(
                stage_id="enterprise_systems",
                name="Enterprise Systems",
                difficulty_level=DifficultyLevel.EXPERT,
                description="Build comprehensive enterprise industrial systems",
                required_accuracy=0.85,
                max_epochs=80,
                min_epochs=25,
                data_requirements={
                    "component_types": ["full_applications", "systems"],
                    "complexity": "enterprise",
                    "framework": "any",
                },
                evaluation_metrics=["system_integration", "scalability", "maintainability"],
                completion_criteria={"system_integration": 0.85, "scalability": 0.8},
            ),
        ]


class CurriculumManager:
    """Manager for curriculum learning strategies."""

    def __init__(self):
        self.strategies = {
            CurriculumStrategy.LINEAR: LinearCurriculumStrategy,
            CurriculumStrategy.EXPONENTIAL: ExponentialCurriculumStrategy,
            CurriculumStrategy.ADAPTIVE: AdaptiveCurriculumStrategy,
            CurriculumStrategy.SELF_PACED: SelfPacedCurriculumStrategy,
        }
        self.active_curricula: dict[str, BaseCurriculumStrategy] = {}

    def create_curriculum(
        self,
        curriculum_id: str,
        stages: list[TrainingStage],
        strategy: CurriculumStrategy = CurriculumStrategy.ADAPTIVE,
        **kwargs,
    ) -> BaseCurriculumStrategy:
        """Create a new curriculum with specified strategy."""
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}")

        strategy_class = self.strategies[strategy]
        curriculum = strategy_class(stages, **kwargs)
        self.active_curricula[curriculum_id] = curriculum

        logger.info(f"Created curriculum {curriculum_id} with {len(stages)} stages using {strategy.value} strategy")
        return curriculum

    def get_curriculum(self, curriculum_id: str) -> BaseCurriculumStrategy | None:
        """Get active curriculum by ID."""
        return self.active_curricula.get(curriculum_id)

    def create_mechanical_engineering_curriculum(
        self, agent_type: str, strategy: CurriculumStrategy = CurriculumStrategy.ADAPTIVE, **kwargs
    ) -> BaseCurriculumStrategy:
        """Create curriculum for specific mechanical engineering agent type."""
        if agent_type == "cad_analysis":
            stages = MechanicalEngineeringCurriculum.create_cad_analysis_curriculum()
        elif agent_type == "rag_quality":
            stages = MechanicalEngineeringCurriculum.create_rag_curriculum()
        elif agent_type == "ui_generation":
            stages = MechanicalEngineeringCurriculum.create_ui_generation_curriculum()
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

        return self.create_curriculum(f"{agent_type}_curriculum", stages, strategy, **kwargs)

    def update_stage_performance(self, curriculum_id: str, stage_performance: dict[str, float]) -> bool:
        """Update performance for current stage and check advancement."""
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            return False

        current_stage = curriculum.get_current_stage()
        if not current_stage:
            return False

        # Update performance tracking
        curriculum.progress.stage_performance[current_stage.stage_id] = stage_performance

        # Check if should advance
        if curriculum.should_advance(stage_performance):
            return curriculum.advance_stage()

        return False

    def get_curriculum_status(self, curriculum_id: str) -> dict[str, Any] | None:
        """Get status of a curriculum."""
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            return None

        current_stage = curriculum.get_current_stage()
        if not current_stage:
            return None

        return {
            "curriculum_id": curriculum_id,
            "current_stage_idx": curriculum.current_stage_idx,
            "current_stage_name": current_stage.name,
            "difficulty_level": current_stage.difficulty_level.value,
            "completed_stages": curriculum.progress.completed_stages,
            "is_complete": curriculum.is_complete(),
            "total_stages": len(curriculum.stages),
            "progress_percentage": (curriculum.current_stage_idx / len(curriculum.stages)) * 100,
        }

    def list_active_curricula(self) -> list[dict[str, Any]]:
        """List all active curricula."""
        return [
            {
                "curriculum_id": curriculum_id,
                "current_stage": curriculum.get_current_stage().name if curriculum.get_current_stage() else None,
                "progress": curriculum.progress.current_stage,
                "total_stages": len(curriculum.stages),
            }
            for curriculum_id, curriculum in self.active_curricula.items()
        ]

    def remove_curriculum(self, curriculum_id: str) -> bool:
        """Remove a curriculum."""
        if curriculum_id in self.active_curricula:
            del self.active_curricula[curriculum_id]
            logger.info(f"Removed curriculum {curriculum_id}")
            return True
        return False
