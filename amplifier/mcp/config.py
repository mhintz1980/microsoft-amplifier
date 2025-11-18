"""
Configuration for Docker Model Runner

Provides centralized configuration management with environment variables
and sensible defaults following ruthless simplicity principles.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DockerModelConfig:
    """Configuration for Docker Model Runner."""

    # API server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # Model settings
    default_model: str = "llama3.2-1b"
    auto_pull: bool = True
    auto_start: bool = True

    # Resource limits
    max_memory_gb: int = 8
    max_gpu_memory_gb: int = 12

    # Performance settings
    base_port: int = 8080
    max_concurrent_models: int = 3

    # Privacy settings
    require_privacy_for_code: bool = True
    require_privacy_for_sensitive_data: bool = True

    # Storage settings
    storage_dir: str = str(Path.home() / ".amplifier" / "models")

    # Logging
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "DockerModelConfig":
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("AMPLIFIER_HOST", "0.0.0.0"),
            port=int(os.getenv("AMPLIFIER_PORT", "8000")),
            default_model=os.getenv("AMPLIFIER_DEFAULT_MODEL", "llama3.2-1b"),
            auto_pull=os.getenv("AMPLIFIER_AUTO_PULL", "true").lower() == "true",
            auto_start=os.getenv("AMPLIFIER_AUTO_START", "true").lower() == "true",
            max_memory_gb=int(os.getenv("AMPLIFIER_MAX_MEMORY_GB", "8")),
            max_gpu_memory_gb=int(os.getenv("AMPLIFIER_MAX_GPU_MEMORY_GB", "12")),
            base_port=int(os.getenv("AMPLIFIER_BASE_PORT", "8080")),
            max_concurrent_models=int(os.getenv("AMPLIFIER_MAX_CONCURRENT_MODELS", "3")),
            require_privacy_for_code=os.getenv("AMPLIFIER_REQUIRE_PRIVACY_CODE", "true").lower() == "true",
            require_privacy_for_sensitive_data=os.getenv("AMPLIFIER_REQUIRE_PRIVACY_DATA", "true").lower() == "true",
            storage_dir=os.getenv("AMPLIFIER_STORAGE_DIR", str(Path.home() / ".amplifier" / "models")),
            log_level=os.getenv("AMPLIFIER_LOG_LEVEL", "INFO"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "default_model": self.default_model,
            "auto_pull": self.auto_pull,
            "auto_start": self.auto_start,
            "max_memory_gb": self.max_memory_gb,
            "max_gpu_memory_gb": self.max_gpu_memory_gb,
            "base_port": self.base_port,
            "max_concurrent_models": self.max_concurrent_models,
            "require_privacy_for_code": self.require_privacy_for_code,
            "require_privacy_for_sensitive_data": self.require_privacy_for_sensitive_data,
            "storage_dir": self.storage_dir,
            "log_level": self.log_level,
        }

    def save(self, config_path: str | Path):
        """Save configuration to file."""
        import json

        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

        logger.info(f"Configuration saved to {config_path}")

    @classmethod
    def load(cls, config_path: str | Path) -> "DockerModelConfig":
        """Load configuration from file."""
        import json

        config_path = Path(config_path)
        if not config_path.exists():
            logger.warning(f"Configuration file not found: {config_path}, using defaults")
            return cls.from_env()

        with open(config_path) as f:
            data = json.load(f)

        config = cls(**data)
        logger.info(f"Configuration loaded from {config_path}")
        return config


def get_config() -> DockerModelConfig:
    """Get the current configuration."""
    config_path = Path.home() / ".amplifier" / "config.json"

    if config_path.exists():
        return DockerModelConfig.load(config_path)
    # Create default config
    config = DockerModelConfig.from_env()
    config.save(config_path)
    return config


def print_config():
    """Print current configuration."""
    config = get_config()
    print("Docker Model Runner Configuration:")
    print("=" * 40)
    for key, value in config.to_dict().items():
        print(f"{key:25}: {value}")
