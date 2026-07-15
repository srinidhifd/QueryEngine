"""LLM service for Claude API interactions with error handling and retry logic."""

import asyncio
from typing import Optional

from anthropic import Anthropic, APIError, RateLimitError as AnthropicRateLimitError

from config import settings
from utils import logger, errors


app_logger = logger.setup_logger(__name__)


class LLMService:
    """Service for interacting with Claude API."""

    def __init__(self):
        """Initialize LLM service with Anthropic client."""
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.MODEL
        self.max_retries = 3

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        request_id: Optional[str] = None
    ) -> tuple[str, int]:
        """
        Generate text using Claude API with retry logic.

        Args:
            prompt: User prompt
            system_prompt: System context
            max_tokens: Maximum tokens in response
            request_id: Request ID for logging

        Returns:
            Tuple of (generated_text, tokens_used)

        Raises:
            RateLimitError: If API rate limited
            APIError: If API call fails
        """
        for attempt in range(self.max_retries):
            try:
                app_logger.info(
                    "llm_request_started",
                    extra={
                        "request_id": request_id,
                        "model": self.model,
                        "attempt": attempt + 1,
                        "prompt_length": len(prompt)
                    }
                )

                # Make API call synchronously (convert to async later)
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt if system_prompt else "",
                    messages=[{"role": "user", "content": prompt}]
                )

                # Extract response
                text = response.content[0].text
                tokens_used = response.usage.output_tokens

                app_logger.info(
                    "llm_request_completed",
                    extra={
                        "request_id": request_id,
                        "model": self.model,
                        "tokens_used": tokens_used,
                        "response_length": len(text)
                    }
                )

                return text, tokens_used

            except AnthropicRateLimitError as e:
                app_logger.warning(
                    "llm_rate_limit",
                    extra={
                        "request_id": request_id,
                        "attempt": attempt + 1,
                        "max_retries": self.max_retries
                    }
                )

                if attempt == self.max_retries - 1:
                    # Last attempt failed, raise error
                    raise errors.RateLimitError() from e

                # Wait before retry (exponential backoff)
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

            except APIError as e:
                app_logger.error(
                    "llm_api_error",
                    extra={
                        "request_id": request_id,
                        "error": str(e),
                        "status_code": getattr(e, "status_code", None)
                    }
                )

                if attempt == self.max_retries - 1:
                    raise errors.APIError(
                        f"Claude API error: {str(e)}"
                    ) from e

                # Wait before retry
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

            except Exception as e:
                app_logger.error(
                    "llm_unexpected_error",
                    extra={
                        "request_id": request_id,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                )
                raise errors.APIError(f"Unexpected error: {str(e)}") from e

        # This should not be reached, but just in case
        raise errors.APIError("Max retries exceeded")


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
