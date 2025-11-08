"""
Logging utilities for CAD reviewer.
"""

import logging
import sys
from pathlib import Path


def get_logger(name: str, level: str | None = None) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # Already configured

    # Set default level
    if level is None:
        level = logging.INFO
    logger.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


def setup_file_logging(log_dir: Path, level: str = "INFO") -> None:
    """Setup file logging for the CAD reviewer."""
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger to also write to file
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Create file handler
    log_file = log_dir / "cad_reviewer.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, level.upper()))

    # Create formatter for file
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    # Add file handler to root logger
    root_logger.addHandler(file_handler)
