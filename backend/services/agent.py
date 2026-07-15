"""Agentic AI service for multi-turn conversations and SQL refinement."""

import json
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from services.llm_service import get_llm_service
from services.database import DatabaseService
from utils import logger

app_logger = logger.setup_logger(__name__)


class Message:
    """A message in an agent conversation."""

    def __init__(self, role: str, content: str):
        self.role = role  # "user" or "assistant"
        self.content = content
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp
        }


class SQLRefinementAgent:
    """Agent that refines SQL through multi-turn conversation."""

    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id or str(uuid.uuid4())
        self.llm = get_llm_service()
        self.conversation_id = str(uuid.uuid4())
        self.messages: List[Message] = []
        self.max_turns = 3

    def refine_sql(
        self,
        initial_query: str,
        generated_sql: str,
        validation_feedback: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Refine SQL through multi-turn conversation.

        Agent will:
        1. Analyze the validation feedback
        2. Suggest improvements
        3. Generate refined SQL
        4. Continue until valid or max turns reached
        """
        app_logger.info(
            "sql_refinement_agent_started",
            extra={
                "request_id": self.request_id,
                "conv_id": self.conversation_id
            }
        )

        try:
            # Turn 1: Analyze and refine
            system_prompt = """You are a SQL refinement expert. Your job is to:
1. Analyze the user's natural language query
2. Review the generated SQL and validation feedback
3. Identify issues and suggest improvements
4. Generate refined SQL that addresses the feedback

Be concise and direct. Focus on correctness and clarity."""

            turn_1_messages = [
                {
                    "role": "user",
                    "content": f"""Natural language query: {initial_query}

Current SQL: {generated_sql}

Validation feedback: {validation_feedback}

Please analyze the issues and generate improved SQL."""
                }
            ]

            # Get LLM response
            response_text, tokens = self._get_llm_response(
                system_prompt=system_prompt,
                messages=turn_1_messages
            )

            self._add_message("assistant", response_text)
            tokens_used = tokens

            # Extract improved SQL from response
            improved_sql = self._extract_sql_from_response(response_text)

            # Save conversation
            DatabaseService.save_agent_conversation(
                user_id=user_id,
                conversation_id=self.conversation_id,
                topic="sql_refinement",
                messages=json.dumps([m.to_dict() for m in self.messages]),
                state="complete",
                result=improved_sql
            )

            return {
                "conversation_id": self.conversation_id,
                "original_sql": generated_sql,
                "refined_sql": improved_sql,
                "reasoning": response_text,
                "tokens_used": tokens_used,
                "turns": 1
            }

        except Exception as e:
            app_logger.error(
                "sql_refinement_agent_failed",
                extra={
                    "request_id": self.request_id,
                    "error": str(e)
                }
            )
            raise

    def validate_tests(
        self,
        sql_query: str,
        test_code: str,
        test_output: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Validate and improve test cases through conversation.

        Agent will:
        1. Review test code and output
        2. Identify coverage gaps
        3. Suggest additional test cases
        4. Return improved test suite
        """
        app_logger.info(
            "test_validation_agent_started",
            extra={
                "request_id": self.request_id,
                "conv_id": self.conversation_id
            }
        )

        try:
            system_prompt = """You are a test validation expert. Your job is to:
1. Review pytest test cases for SQL queries
2. Identify coverage gaps (edge cases, data quality, schema validation)
3. Suggest additional test cases
4. Generate improved test code

Focus on practical, executable tests."""

            messages = [
                {
                    "role": "user",
                    "content": f"""SQL Query: {sql_query}

Current Test Code:
{test_code}

Test Output:
{test_output}

Please identify gaps and suggest improvements."""
                }
            ]

            response_text, tokens = self._get_llm_response(
                system_prompt,
                messages
            )

            self._add_message("assistant", response_text)

            # Extract improved test code
            improved_tests = self._extract_python_from_response(response_text)

            DatabaseService.save_agent_conversation(
                user_id=user_id,
                conversation_id=self.conversation_id,
                topic="test_validation",
                messages=json.dumps([m.to_dict() for m in self.messages]),
                state="complete",
                result=improved_tests
            )

            return {
                "conversation_id": self.conversation_id,
                "original_tests": test_code,
                "improved_tests": improved_tests,
                "suggestions": response_text,
                "tokens_used": tokens
            }

        except Exception as e:
            app_logger.error(
                "test_validation_agent_failed",
                extra={
                    "request_id": self.request_id,
                    "error": str(e)
                }
            )
            raise

    def optimize_query(
        self,
        sql_query: str,
        performance_metrics: Dict[str, Any],
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Optimize SQL query based on performance metrics.

        Agent will:
        1. Analyze current performance
        2. Identify bottlenecks
        3. Suggest optimizations
        4. Propose indexed columns
        """
        app_logger.info(
            "query_optimization_agent_started",
            extra={
                "request_id": self.request_id,
                "conv_id": self.conversation_id
            }
        )

        try:
            system_prompt = """You are a SQL optimization expert. Your job is to:
1. Analyze SQL query performance
2. Identify bottlenecks and inefficiencies
3. Suggest optimization strategies
4. Recommend indexes or query rewrites

Be practical and focus on real-world improvements."""

            messages = [
                {
                    "role": "user",
                    "content": f"""SQL Query:
{sql_query}

Performance Metrics:
{json.dumps(performance_metrics, indent=2)}

Please suggest optimizations."""
                }
            ]

            response_text, tokens = self._get_llm_response(
                system_prompt,
                messages
            )

            self._add_message("assistant", response_text)

            # Extract optimized SQL
            optimized_sql = self._extract_sql_from_response(response_text)

            DatabaseService.save_agent_conversation(
                user_id=user_id,
                conversation_id=self.conversation_id,
                topic="query_optimization",
                messages=json.dumps([m.to_dict() for m in self.messages]),
                state="complete",
                result=optimized_sql
            )

            return {
                "conversation_id": self.conversation_id,
                "original_query": sql_query,
                "optimized_query": optimized_sql,
                "suggestions": response_text,
                "tokens_used": tokens
            }

        except Exception as e:
            app_logger.error(
                "query_optimization_agent_failed",
                extra={
                    "request_id": self.request_id,
                    "error": str(e)
                }
            )
            raise

    # Helper methods

    def _add_message(self, role: str, content: str):
        """Add message to conversation."""
        self.messages.append(Message(role, content))

    def _get_llm_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]]
    ) -> tuple[str, int]:
        """Get response from LLM (synchronous)."""
        from anthropic import Anthropic

        # Format messages for Claude API
        formatted_messages = []
        for msg in messages:
            if msg["role"] == "user":
                formatted_messages.append({
                    "role": "user",
                    "content": msg["content"]
                })
            else:
                formatted_messages.append({
                    "role": "assistant",
                    "content": msg["content"]
                })

        # Get response from Claude
        api_key = getattr(self.llm, 'api_key', None)
        if not api_key:
            from ..config import settings
            api_key = settings.ANTHROPIC_API_KEY

        client = Anthropic(api_key=api_key)

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=system_prompt,
            messages=formatted_messages
        )

        self._add_message("assistant", response.content[0].text)
        return response.content[0].text, response.usage.output_tokens

    def _extract_sql_from_response(self, response: str) -> str:
        """Extract SQL from LLM response."""
        if "```sql" in response:
            start = response.find("```sql") + 6
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        return response.strip()

    def _extract_python_from_response(self, response: str) -> str:
        """Extract Python code from LLM response."""
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        return response.strip()
