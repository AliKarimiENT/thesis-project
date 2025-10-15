"""
Logging utilities for QG experiments.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "qg_experiment",
    log_file: Optional[str] = None,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Set up logger with consistent formatting.
    
    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_config(logger: logging.Logger, config: dict):
    """
    Log configuration dictionary.
    
    Args:
        logger: Logger instance
        config: Configuration dictionary
    """
    logger.info("="*50)
    logger.info("Configuration:")
    logger.info("="*50)
    for key, value in sorted(config.items()):
        logger.info(f"  {key}: {value}")
    logger.info("="*50)


def log_metrics(logger: logging.Logger, metrics: dict, prefix: str = ""):
    """
    Log metrics dictionary.
    
    Args:
        logger: Logger instance
        metrics: Metrics dictionary
        prefix: Optional prefix for metric names
    """
    logger.info("="*50)
    logger.info(f"{prefix}Metrics:" if prefix else "Metrics:")
    logger.info("="*50)
    for key, value in sorted(metrics.items()):
        if isinstance(value, (int, float)):
            logger.info(f"  {key}: {value:.4f}")
        else:
            logger.info(f"  {key}: {value}")
    logger.info("="*50)


def log_step(logger: logging.Logger, step: str, status: str = "START"):
    """
    Log experiment step with visual separator.
    
    Args:
        logger: Logger instance
        step: Step description
        status: Status (START/COMPLETE/FAILED)
    """
    sep = "="*50
    logger.info("")
    logger.info(sep)
    logger.info(f"{status}: {step}")
    logger.info(sep)

