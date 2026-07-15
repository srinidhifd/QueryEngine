"""API middleware for error handling, logging, and request tracking."""

import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from utils import logger, errors


app_logger = logger.setup_logger(__name__)


def setup(app: FastAPI):
    """Setup middleware for the FastAPI app."""

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """Add request ID and log all requests."""
        # Generate request ID
        request.state.request_id = str(uuid.uuid4())

        # Log request start
        logger.log_request(
            app_logger,
            request.state.request_id,
            request.method,
            request.url.path
        )

        start_time = time.time()

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            logger.log_response(
                app_logger,
                request.state.request_id,
                response.status_code,
                duration_ms
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request.state.request_id

            return response

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            logger.log_error(
                app_logger,
                request.state.request_id,
                str(exc),
                duration_ms=duration_ms
            )
            raise

    @app.exception_handler(errors.NLPToSQLError)
    async def nlp_to_sql_error_handler(request: Request, exc: errors.NLPToSQLError):
        """Handle custom application errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "type": exc.error_type,
                "request_id": getattr(request.state, "request_id", None)
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors."""
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "type": "validation_error",
                "details": exc.errors(),
                "request_id": getattr(request.state, "request_id", None)
            }
        )

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        """Handle unexpected errors."""
        app_logger.error(
            "unexpected_error",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "error": str(exc),
                "error_type": type(exc).__name__
            }
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "type": "internal_error",
                "request_id": getattr(request.state, "request_id", None)
            }
        )
