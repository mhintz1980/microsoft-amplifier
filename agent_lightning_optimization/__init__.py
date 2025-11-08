"""
Agent Lightning Optimization System for Mechanical Engineering.

This package provides advanced RL training optimizations for mechanical engineering agents,
including APO algorithms, GPU acceleration, curriculum learning, and comprehensive monitoring.
"""

from .algorithm.apo import APOConfig
from .algorithm.apo import APOptimizer
from .algorithm.apo import MechanicalEngineeringTemplateGenerator
from .monitoring.monitor import TrainingEvaluator
from .monitoring.monitor import TrainingMonitor
from .reward.domain_rewards import RewardFunctionRegistry
from .store.sqlite_store import LightningStoreManager
from .store.sqlite_store import SQLiteLightningStore
from .training.curriculum import CurriculumManager
from .training.curriculum import CurriculumStrategy
from .training.gpu_accelerator import GPUManager
from .training.gpu_accelerator import MultiProcessTrainer

__version__ = "1.0.0"
__author__ = "Agent Lightning Optimization Team"

__all__ = [
    # Core optimization
    "APOptimizer",
    "APOConfig",
    "MechanicalEngineeringTemplateGenerator",
    # Reward systems
    "RewardFunctionRegistry",
    # Storage
    "SQLiteLightningStore",
    "LightningStoreManager",
    # Curriculum learning
    "CurriculumManager",
    "CurriculumStrategy",
    # GPU acceleration
    "GPUManager",
    "MultiProcessTrainer",
    # Monitoring
    "TrainingMonitor",
    "TrainingEvaluator",
]
