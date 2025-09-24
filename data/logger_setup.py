"""
Logging setup for G.H.O.S.T. virtual assistant.

This module configures logging for the entire application with
proper formatting, file rotation, and different log levels.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "data/logs",
    log_file: str = "ghost.log",
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_output: bool = True
) -> logging.Logger:
    """
    Set up logging configuration for the G.H.O.S.T. virtual assistant.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        log_file: Name of the log file
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        console_output: Whether to output logs to console
        
    Returns:
        Configured logger instance
    """
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation
    file_path = log_path / log_file
    file_handler = logging.handlers.RotatingFileHandler(
        filename=file_path,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler (optional)
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        
        # Use a simpler format for console output
        console_formatter = logging.Formatter(
            fmt='%(levelname)s - %(name)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Create separate error log file
    error_file_path = log_path / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        filename=error_file_path,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # Log the logging setup
    logger.info(f"Logging initialized - Level: {log_level}, File: {file_path}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the logger (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_log_level(level: str) -> None:
    """
    Change the log level for all loggers.
    
    Args:
        level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Update root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Update all handlers
    for handler in root_logger.handlers:
        handler.setLevel(numeric_level)
    
    root_logger.info(f"Log level changed to {level}")


def log_system_info() -> None:
    """Log system information for debugging purposes."""
    import platform
    import sys
    
    logger = logging.getLogger(__name__)
    
    logger.info("=== G.H.O.S.T. Virtual Assistant Started ===")
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Architecture: {platform.architecture()}")
    logger.info(f"Processor: {platform.processor()}")
    logger.info(f"Hostname: {platform.node()}")
    logger.info("=" * 50)


def create_module_logger(module_name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Create a dedicated logger for a specific module.
    
    Args:
        module_name: Name of the module
        log_file: Optional separate log file for this module
        
    Returns:
        Module-specific logger
    """
    logger = logging.getLogger(module_name)
    
    if log_file:
        # Create separate file handler for this module
        log_path = Path("data/logs") / log_file
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_brain_logging() -> logging.Logger:
    """
    Set up specialized logging for the brain system.
    
    Returns:
        Brain logger instance
    """
    brain_logger = create_module_logger('brain', 'brain.log')
    brain_logger.info("Brain logging system initialized")
    return brain_logger


def setup_memory_logging() -> logging.Logger:
    """
    Set up specialized logging for the memory system.
    
    Returns:
        Memory logger instance
    """
    memory_logger = create_module_logger('memory', 'memory.log')
    memory_logger.info("Memory logging system initialized")
    return memory_logger
