"""
Career Copilot CLI Entry Point

Run the AI Career Copilot service from the command line.
"""

import logging

import uvicorn

from .config import config
from .main import app

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"Starting AI Career Copilot server on {config.api_host}:{config.api_port}")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"API Documentation: http://{config.api_host}:{config.api_port}/docs")

    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        log_level=config.log_level.lower(),
        access_log=bool(config.is_development()),
    )
