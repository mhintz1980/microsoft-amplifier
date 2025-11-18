"""
Career Copilot Configuration

Configuration management for the AI Career Copilot service.
Integrates with amplifier's configuration system for consistent settings.
"""

import os
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from ..config.models import ModelConfig


class CareerCopilotConfig(BaseSettings):
    """Configuration for Career Copilot service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Configuration
    service_name: str = Field(default="career-copilot", description="Service name for logging and monitoring")
    service_version: str = Field(default="1.0.0", description="Service version")
    environment: str = Field(default="development", description="Environment (development, staging, production)")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    api_prefix: str = Field(default="/api/v1", description="API URL prefix")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"], description="CORS allowed origins"
    )

    # File Upload Configuration
    upload_max_size_mb: int = Field(default=10, description="Maximum upload file size in MB")
    upload_allowed_extensions: list[str] = Field(
        default=[".pdf", ".docx", ".txt", ".json", ".md"], description="Allowed file extensions for upload"
    )
    upload_temp_dir: str = Field(default="/tmp/career_copilot", description="Temporary directory for uploads")

    # AI Model Configuration
    claude_model_fast: str = Field(default="claude-3-5-haiku-20241022", description="Fast model for quick operations")
    claude_model_default: str = Field(default="claude-sonnet-4-20250514", description="Default model for analysis")
    claude_model_thinking: str = Field(
        default="claude-opus-4-1-20250805", description="Thinking model for complex analysis"
    )

    # Analysis Configuration
    skill_analysis_timeout: int = Field(default=30, description="Timeout for skill analysis in seconds")
    resume_parsing_timeout: int = Field(default=60, description="Timeout for resume parsing in seconds")
    job_matching_timeout: int = Field(default=45, description="Timeout for job matching in seconds")
    max_concurrent_analyses: int = Field(default=5, description="Maximum concurrent analysis tasks")

    # Caching Configuration
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")
    enable_redis_cache: bool = Field(default=False, description="Enable Redis caching")
    redis_url: str | None = Field(default=None, description="Redis connection URL")

    # Database Configuration
    database_url: str = Field(default="sqlite:///./career_copilot.db", description="Database connection URL")

    # External Services Configuration
    enable_llm_fallback: bool = Field(default=True, description="Enable fallback to rule-based analysis")
    job_api_enabled: bool = Field(default=False, description="Enable job market API integration")
    job_api_key: str | None = Field(default=None, description="Job market API key")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    log_file: str | None = Field(default=None, description="Log file path")

    # Feature Flags
    enable_background_processing: bool = Field(default=True, description="Enable background task processing")
    enable_email_notifications: bool = Field(default=False, description="Enable email notifications")
    enable_analytics: bool = Field(default=True, description="Enable analytics tracking")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests_per_minute: int = Field(default=60, description="Rate limit requests per minute")
    rate_limit_burst_size: int = Field(default=10, description="Rate limit burst size")

    # Security Configuration
    require_authentication: bool = Field(default=False, description="Require authentication for API")
    jwt_secret_key: str | None = Field(default=None, description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(default=24, description="JWT token expiration in hours")

    # Prompt Configuration
    prompts_directory: str = Field(
        default=str(Path(__file__).parent / "prompts"), description="Directory containing prompt templates"
    )

    # Model Configuration Integration
    amplifier_model_config: ModelConfig | None = Field(default=None, description="Amplifier model configuration")

    def get_model(self, category: str = "default") -> str:
        """Get model by category name.

        Args:
            category: One of "fast", "default", or "thinking"

        Returns:
            Model identifier string
        """
        if category == "fast":
            return self.claude_model_fast
        if category == "thinking":
            return self.claude_model_thinking
        return self.claude_model_default

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    def get_cors_origins(self) -> list[str]:
        """Get CORS origins based on environment."""
        if self.is_production():
            return [origin for origin in self.cors_origins if "localhost" not in origin]
        return self.cors_origins


# Global configuration instance
config = CareerCopilotConfig()


# Configuration Validation
def validate_config() -> bool:
    """Validate configuration settings."""
    try:
        # Validate upload directory
        upload_dir = Path(config.upload_temp_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Validate prompts directory
        prompts_dir = Path(config.prompts_directory)
        if not prompts_dir.exists():
            raise ValueError(f"Prompts directory not found: {prompts_dir}")

        # Validate model configuration
        if config.amplifier_model_config:
            try:
                # Test model config integration
                config.amplifier_model_config.get_model("default")
            except Exception as e:
                raise ValueError(f"Invalid model configuration: {e}")

        return True

    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False


def get_database_url() -> str:
    """Get database URL with environment variable fallback."""
    return os.getenv("DATABASE_URL", config.database_url)


def get_redis_url() -> str | None:
    """Get Redis URL with environment variable fallback."""
    return os.getenv("REDIS_URL", config.redis_url)


def get_jwt_secret_key() -> str:
    """Get JWT secret key with secure fallback."""
    if config.jwt_secret_key:
        return config.jwt_secret_key

    # Generate secure key for development
    if config.is_development():
        import secrets

        return secrets.token_urlsafe(32)

    raise ValueError("JWT secret key must be set in production")


# Environment-specific configuration
def get_config_for_environment() -> CareerCopilotConfig:
    """Get configuration based on current environment."""
    return config


# Configuration helpers
def setup_logging():
    """Setup logging based on configuration."""
    import logging
    import sys

    # Configure logging level
    level = getattr(logging, config.log_level.upper(), logging.INFO)

    # Create formatter
    if config.log_format == "json":
        try:
            from pythonjsonlogger import jsonlogger

            formatter = jsonlogger.JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s")
        except ImportError:
            # Fallback to standard formatter if json logger not available
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Setup handlers
    handlers = [logging.StreamHandler(sys.stdout)]

    if config.log_file:
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(level=level, handlers=handlers, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Set logger for career copilot
    logger = logging.getLogger("career_copilot")
    logger.setLevel(level)

    return logger


def get_upload_settings() -> dict[str, Any]:
    """Get upload settings as dictionary."""
    return {
        "max_file_size": config.upload_max_size_mb * 1024 * 1024,  # Convert to bytes
        "allowed_extensions": config.upload_allowed_extensions,
        "temp_directory": config.upload_temp_dir,
    }


def get_ai_model_settings() -> dict[str, Any]:
    """Get AI model settings as dictionary."""
    return {
        "fast_model": config.claude_model_fast,
        "default_model": config.claude_model_default,
        "thinking_model": config.claude_model_thinking,
        "fallback_enabled": config.enable_llm_fallback,
    }


def get_rate_limit_settings() -> dict[str, Any]:
    """Get rate limiting settings as dictionary."""
    return {
        "enabled": config.rate_limit_enabled,
        "requests_per_minute": config.rate_limit_requests_per_minute,
        "burst_size": config.rate_limit_burst_size,
    }


# Configuration validation
def check_required_settings() -> list[str]:
    """Check for required settings and return missing ones."""
    missing = []

    # Check database URL
    if not get_database_url():
        missing.append("DATABASE_URL")

    # Check JWT secret if authentication is required
    if config.require_authentication and not get_jwt_secret_key():
        missing.append("JWT_SECRET_KEY")

    # Check Redis URL if Redis caching is enabled
    if config.enable_redis_cache and not get_redis_url():
        missing.append("REDIS_URL")

    # Check prompts directory
    if not Path(config.prompts_directory).exists():
        missing.append(f"Prompts directory: {config.prompts_directory}")

    return missing


# Feature flag helpers
def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled."""
    feature_flags = {
        "background_processing": config.enable_background_processing,
        "email_notifications": config.enable_email_notifications,
        "analytics": config.enable_analytics,
        "rate_limiting": config.rate_limit_enabled,
        "redis_cache": config.enable_redis_cache,
        "llm_fallback": config.enable_llm_fallback,
        "job_api": config.job_api_enabled,
        "authentication": config.require_authentication,
    }

    return feature_flags.get(feature, False)
