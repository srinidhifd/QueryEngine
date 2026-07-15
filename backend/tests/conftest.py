"""Pytest configuration and fixtures."""

import pytest
import os
from unittest.mock import patch, MagicMock

# Set test environment
os.environ["TESTING"] = "true"


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    with patch("backend.services.llm_service.LLMService") as mock:
        service = MagicMock()
        service.generate_text = MagicMock(return_value=("SELECT * FROM sales", 100))
        service.model = "claude-haiku-3-5"
        mock.return_value = service
        yield service


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client."""
    with patch("backend.services.llm_service.Anthropic") as mock:
        client = MagicMock()
        response = MagicMock()
        response.content = [MagicMock(text="SELECT * FROM sales")]
        response.usage.output_tokens = 100
        client.messages.create.return_value = response
        mock.return_value = client
        yield client
