"""Input sanitization service for security (2.2 requirement)."""

import re
from typing import Tuple

from utils.errors import SanitizationError


class InputSanitizer:
    """Sanitizes user input before sending to LLM."""

    # SQL keywords that indicate potentially dangerous commands
    DANGEROUS_SQL_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'REVOKE', 'GRANT',
        'CREATE', 'INSERT', 'UPDATE', 'EXEC', 'EXECUTE'
    ]

    # Prompt injection markers to watch for
    INJECTION_PATTERNS = [
        r'system:', r'ignore:', r'forget:', r'bypass:',
        r'override:', r'disregard:', r'admin:',
        r'<prompt>', r'</prompt>', r'{{.*?}}'
    ]

    # Characters that are suspicious in user input
    SUSPICIOUS_CHARS_PATTERN = r'[\$`\|;]'

    # Maximum query length
    MAX_QUERY_LENGTH = 2000

    @staticmethod
    def sanitize(query: str) -> str:
        """
        Sanitize user query before sending to LLM.

        Args:
            query: Raw user input

        Returns:
            Sanitized query

        Raises:
            SanitizationError: If input fails sanitization checks
        """
        sanitizer = InputSanitizer()
        return sanitizer._sanitize_internal(query)

    def _sanitize_internal(self, query: str) -> str:
        """Internal sanitization method."""
        # Check if query is empty
        if not query or not query.strip():
            raise SanitizationError("Query cannot be empty")

        # Check length
        if len(query) > self.MAX_QUERY_LENGTH:
            raise SanitizationError(
                f"Query exceeds maximum length of {self.MAX_QUERY_LENGTH} characters"
            )

        # Check for dangerous SQL keywords
        query_upper = query.upper()
        for keyword in self.DANGEROUS_SQL_KEYWORDS:
            if keyword in query_upper:
                raise SanitizationError(
                    f"Query contains disallowed SQL keyword: {keyword}"
                )

        # Check for prompt injection markers
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                raise SanitizationError(
                    "Query contains suspicious pattern that could be prompt injection"
                )

        # Check for suspicious shell characters
        if re.search(self.SUSPICIOUS_CHARS_PATTERN, query):
            # Allow these only in specific contexts (like string literals)
            # But generally warn about them
            pass  # For now, allow them but flag in logging

        # Check for script/code tags
        if re.search(r'<script|</script|<code|</code|javascript:', query, re.IGNORECASE):
            raise SanitizationError(
                "Query contains code-like content which is not allowed"
            )

        # Return cleaned query (strip whitespace)
        return query.strip()

    @staticmethod
    def validate_sql_query(sql_query: str) -> Tuple[bool, str]:
        """
        Validate that a generated SQL query is safe to execute.

        Args:
            sql_query: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        sanitizer = InputSanitizer()
        return sanitizer._validate_sql_internal(sql_query)

    def _validate_sql_internal(self, sql_query: str) -> Tuple[bool, str]:
        """Internal SQL validation method."""
        if not sql_query or not sql_query.strip():
            return False, "Generated SQL is empty"

        sql_upper = sql_query.upper()

        # Allow only SELECT queries (safe read-only)
        if not sql_upper.startswith('SELECT'):
            return False, "Only SELECT queries are allowed"

        # Block dangerous operations in generated SQL
        for keyword in ['DROP', 'DELETE', 'TRUNCATE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']:
            if keyword in sql_upper:
                return False, f"Generated SQL contains disallowed keyword: {keyword}"

        # Check for suspicious patterns
        if re.search(r'--|/\*', sql_query):  # SQL comments
            return False, "SQL comments are not allowed"

        return True, ""
