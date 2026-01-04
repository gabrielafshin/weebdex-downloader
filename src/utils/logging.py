"""Logging configuration for Weebdex Downloader."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    enabled: bool = False,
    level: int = logging.DEBUG,
    log_file: Optional[Path] = None
) -> None:
    """
    Configure application logging.
    
    Args:
        enabled: Whether to enable logging (default: False for silent operation)
        level: Logging level (default: DEBUG)
        log_file: Optional file path for log output
    """
    # Get root logger for the application
    logger = logging.getLogger("src")
    
    # Clear existing handlers
    logger.handlers.clear()
    
    if not enabled:
        # Disable all logging
        logger.addHandler(logging.NullHandler())
        logger.setLevel(logging.CRITICAL + 1)
        return
    
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.debug("Logging initialized")
