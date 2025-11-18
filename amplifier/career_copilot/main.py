"""
Career Copilot Main Application

FastAPI application entry point for the AI Career Copilot service.
Integrates with amplifier's configuration and logging systems.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from .api.endpoints import router as api_router
from .api.middleware import setup_middleware
from .config import check_required_settings
from .config import config
from .config import setup_logging
from .config import validate_config

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(f"Starting Career Copilot v{config.service_version} in {config.environment} mode")

    # Validate configuration
    if not validate_config():
        logger.error("Configuration validation failed")
        raise RuntimeError("Invalid configuration")

    # Check required settings
    missing_settings = check_required_settings()
    if missing_settings:
        logger.error(f"Missing required settings: {missing_settings}")
        raise RuntimeError(f"Missing required settings: {missing_settings}")

    # Create necessary directories
    Path(config.upload_temp_dir).mkdir(parents=True, exist_ok=True)

    logger.info("Career Copilot started successfully")

    yield

    logger.info("Shutting down Career Copilot")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Create FastAPI instance
    app = FastAPI(
        title="AI Career Copilot",
        description="AI-powered career development assistant",
        version=config.service_version,
        debug=config.is_development(),
        lifespan=lifespan,
    )

    # Set up middleware
    setup_middleware(app)

    # Include API routes
    app.include_router(api_router)

    # Add health check endpoint
    @app.get("/")
    async def root():
        return {
            "service": "AI Career Copilot",
            "version": config.service_version,
            "environment": config.environment,
            "status": "healthy",
        }

    # Add API documentation
    if config.is_development():

        @app.get("/debug/config")
        async def debug_config():
            return {
                "config": config.dict(),
                "model_config": config.amplifier_model_config.dict() if config.amplifier_model_config else None,
                "features": {
                    "background_processing": config.enable_background_processing,
                    "email_notifications": config.enable_email_notifications,
                    "analytics": config.enable_analytics,
                    "rate_limiting": config.rate_limit_enabled,
                    "redis_cache": config.enable_redis_cache,
                    "llm_fallback": config.enable_llm_fallback,
                    "job_api": config.job_api_enabled,
                    "authentication": config.require_authentication,
                },
            }

    return app


# Application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {config.api_host}:{config.api_port}")

    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        log_level=config.log_level.lower(),
        access_log=bool(config.is_development()),
    )
