"""Custom exception classes for the application."""

from typing import Optional


class NLPToSQLError(Exception):
    """Base exception for NLP-to-SQL application."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_type: str = "internal_error"
    ):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(self.message)


class ValidationError(NLPToSQLError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400,
            error_type="validation_error"
        )


class SanitizationError(ValidationError):
    """Raised when input sanitization fails."""

    def __init__(self, message: str):
        super().__init__(message)


class SQLGenerationError(NLPToSQLError):
    """Raised when SQL generation fails."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=500,
            error_type="sql_generation_error"
        )


class SQLExecutionError(NLPToSQLError):
    """Raised when SQL execution fails."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=500,
            error_type="sql_execution_error"
        )


class TestGenerationError(NLPToSQLError):
    """Raised when test generation fails."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=500,
            error_type="test_generation_error"
        )


class TestExecutionError(NLPToSQLError):
    """Raised when test execution fails."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=500,
            error_type="test_execution_error"
        )


class RateLimitError(NLPToSQLError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, retry_after: Optional[int] = None):
        message = "API rate limited. Please try again in a moment."
        super().__init__(
            message=message,
            status_code=429,
            error_type="rate_limit_error"
        )
        self.retry_after = retry_after


class APIError(NLPToSQLError):
    """Raised when external API call fails."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(
            message=message,
            status_code=status_code,
            error_type="api_error"
        )


class DatabaseError(NLPToSQLError):
    """Raised when database operation fails."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=500,
            error_type="database_error"
        )
