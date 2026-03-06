"""
Structured logging configuration for the Phi-Harmonic Trading Filter API
"""

from loguru import logger
import sys
from ..config.settings import settings


def setup_logging():
    """Configure loguru logger with structured JSON output for production monitoring"""
    # Remove default handler
    logger.remove()

    # Set log level based on environment
    log_level = "DEBUG" if settings.debug else "INFO"

    # Add console handler with JSON format
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {extra} | {message}",
        level=log_level,
        serialize=settings.debug,  # JSON format in production, text in debug
        backtrace=True,
        diagnose=True,
    )

    # Add file handler with rotation
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="1 week",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {extra} | {message}",
        level=log_level,
        serialize=True,  # Always JSON for files
        backtrace=True,
        diagnose=True,
    )

    # Add error-only file
    logger.add(
        "logs/error.log",
        rotation="10 MB",
        retention="1 month",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {extra} | {message}",
        level="ERROR",
        serialize=True,
        backtrace=True,
        diagnose=True,
    )


# TEMPLATE_BEGIN
# PURPOSE: Get a logger instance with context for the current request or module
# INPUTS: name (str) - module name for logger context
# PROCESS:
#   STEP[1]: Bind logger with module name
#   STEP[2]: Add extra context if available (request_id, user_id)
#   STEP[3]: Return configured logger instance
# OUTPUTS: Logger instance with context
# DEPENDENCIES: loguru logger configuration
# TEMPLATE_END
def get_logger(name: str):
    """Get a logger instance with context for the current request or module"""
    return logger.bind(module=name)
