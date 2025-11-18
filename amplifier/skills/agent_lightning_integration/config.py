"""
Configuration for Agent Lightning Integration
"""

from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class PerformanceTrackingConfig:
    """Configuration for skill performance tracking"""

    # Metrics collection frequency (seconds)
    collection_interval: float = 60.0

    # Performance history window size
    history_window_size: int = 1000

    # Success rate thresholds
    excellent_threshold: float = 0.95
    good_threshold: float = 0.85
    acceptable_threshold: float = 0.75

    # Error pattern detection sensitivity
    error_detection_sensitivity: float = 0.8

    # Performance metrics to track
    tracked_metrics: List[str] = field(
        default_factory=lambda: [
            "success_rate",
            "execution_time",
            "error_rate",
            "hallucination_rate",
            "user_satisfaction",
            "resource_efficiency",
            "accuracy_score",
            "response_quality",
        ]
    )


@dataclass
class RLTrainingConfig:
    """Configuration for RL training components"""

    # APO Algorithm settings
    apo_learning_rate: float = 0.001
    apo_batch_size: int = 32
    apo_episode_length: int = 100
    apo_update_frequency: int = 10

    # VERL Algorithm settings
    verl_learning_rate: float = 0.0005
    verl_entropy_coefficient: float = 0.01
    verl_value_loss_coefficient: float = 0.5
    verl_max_grad_norm: float = 1.0

    # Training infrastructure
    gpu_acceleration: bool = True
    max_parallel_episodes: int = 4
    checkpoint_frequency: int = 50

    # Safety-critical training
    zero_hallucination_reward: float = 10.0
    hallucination_penalty: float = -50.0
    quality_bonus_multiplier: float = 2.0


@dataclass
class QualityGateConfig:
    """Configuration for quality gate enforcement"""

    # Validation thresholds
    minimum_success_rate: float = 0.90
    maximum_error_rate: float = 0.05
    maximum_hallucination_rate: float = 0.01

    # Quality assessment weights
    accuracy_weight: float = 0.4
    performance_weight: float = 0.3
    reliability_weight: float = 0.2
    efficiency_weight: float = 0.1

    # Automated testing
    test_suite_compliance: float = 1.0
    integration_test_threshold: float = 0.95
    edge_case_coverage: float = 0.8


@dataclass
class KnowledgeTransferConfig:
    """Configuration for knowledge transfer system"""

    # Pattern recognition settings
    pattern_similarity_threshold: float = 0.85
    min_successful_examples: int = 5

    # Transfer learning parameters
    transfer_learning_rate: float = 0.002
    adaptation_strength: float = 0.7

    # Knowledge base settings
    knowledge_retention_period: int = 30  # days
    max_pattern_cache_size: int = 10000

    # Cross-skill learning
    enable_cross_skill_transfer: bool = True
    skill_similarity_threshold: float = 0.75


@dataclass
class MonitoringConfig:
    """Configuration for production monitoring"""

    # Dashboard settings
    dashboard_refresh_interval: float = 5.0
    metrics_retention_days: int = 90

    # Alert thresholds
    performance_degradation_alert: float = 0.1
    error_spike_alert: float = 0.05
    quality_drop_alert: float = 0.15

    # Reporting
    generate_daily_reports: bool = True
    generate_weekly_analysis: bool = True
    executive_summary_frequency: str = "weekly"


@dataclass
class AgentLightningIntegrationConfig:
    """Main configuration for Agent Lightning Integration"""

    # Storage paths
    storage_root: Path = field(default_factory=lambda: Path("amplifier/skills/agent_lightning_integration/data"))
    checkpoint_dir: Path = field(
        default_factory=lambda: Path("amplifier/skills/agent_lightning_integration/checkpoints")
    )
    logs_dir: Path = field(default_factory=lambda: Path("amplifier/skills/agent_lightning_integration/logs"))

    # Component configurations
    performance_tracking: PerformanceTrackingConfig = field(default_factory=PerformanceTrackingConfig)
    rl_training: RLTrainingConfig = field(default_factory=RLTrainingConfig)
    quality_gates: QualityGateConfig = field(default_factory=QualityGateConfig)
    knowledge_transfer: KnowledgeTransferConfig = field(default_factory=KnowledgeTransferConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)

    # Integration settings
    enable_gpu_acceleration: bool = True
    auto_optimization_enabled: bool = True
    continuous_training_enabled: bool = True
    quality_enforcement_enabled: bool = True

    # Performance optimization
    parallel_execution: bool = True
    batch_size: int = 64
    max_concurrent_optimizations: int = 8

    # Agent Lightning connection
    agent_lightning_endpoint: str = "http://localhost:8000"
    connection_timeout: float = 30.0
    max_retry_attempts: int = 3

    def __post_init__(self):
        """Initialize directories and validate configuration"""
        # Create necessary directories
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Validate configuration
        self._validate_config()

    def _validate_config(self):
        """Validate configuration parameters"""
        if not 0 <= self.performance_tracking.excellent_threshold <= 1:
            raise ValueError("excellent_threshold must be between 0 and 1")

        if self.performance_tracking.excellent_threshold <= self.performance_tracking.good_threshold:
            raise ValueError("excellent_threshold must be greater than good_threshold")

        if not 0 <= self.quality_gates.minimum_success_rate <= 1:
            raise ValueError("minimum_success_rate must be between 0 and 1")

        if self.rl_training.apo_batch_size <= 0:
            raise ValueError("apo_batch_size must be positive")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "storage_root": str(self.storage_root),
            "checkpoint_dir": str(self.checkpoint_dir),
            "logs_dir": str(self.logs_dir),
            "performance_tracking": self.performance_tracking.__dict__,
            "rl_training": self.rl_training.__dict__,
            "quality_gates": self.quality_gates.__dict__,
            "knowledge_transfer": self.knowledge_transfer.__dict__,
            "monitoring": self.monitoring.__dict__,
            "enable_gpu_acceleration": self.enable_gpu_acceleration,
            "auto_optimization_enabled": self.auto_optimization_enabled,
            "continuous_training_enabled": self.continuous_training_enabled,
            "quality_enforcement_enabled": self.quality_enforcement_enabled,
            "parallel_execution": self.parallel_execution,
            "batch_size": self.batch_size,
            "max_concurrent_optimizations": self.max_concurrent_optimizations,
            "agent_lightning_endpoint": self.agent_lightning_endpoint,
            "connection_timeout": self.connection_timeout,
            "max_retry_attempts": self.max_retry_attempts,
        }
