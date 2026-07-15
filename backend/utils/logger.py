"""Structured JSON logging configuration."""

import logging
import json
import sys
from datetime import datetime
from typing import Optional

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()

        # Add log level
        log_record['level'] = record.levelname

        # Add logger name
        log_record['logger'] = record.name

        # Ensure message is present
        if 'message' not in log_record:
            log_record['message'] = record.getMessage()


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup a structured JSON logger.

    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # Remove existing handlers
    logger.handlers = []

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level))

    # Create JSON formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def log_request(logger: logging.Logger, request_id: str, method: str, path: str, **kwargs):
    """Log HTTP request."""
    logger.info(
        f"request_started",
        extra={"request_id": request_id, "method": method, "path": path, **kwargs}
    )


def log_response(logger: logging.Logger, request_id: str, status_code: int, duration_ms: float, **kwargs):
    """Log HTTP response."""
    logger.info(
        "request_completed",
        extra={"request_id": request_id, "status_code": status_code, "duration_ms": duration_ms, **kwargs}
    )


def log_error(logger: logging.Logger, request_id: str, error: str, **kwargs):
    """Log error."""
    logger.error(
        "request_error",
        extra={"request_id": request_id, "error": error, **kwargs}
    )
