"""API routes for NLP-to-SQL application."""

import uuid
import asyncio
import tempfile
import os
import re
import ast
from fastapi import APIRouter, Request, Depends, HTTPException
from datetime import datetime

from config import settings
from constants import (
    SQL_GENERATION_SYSTEM_PROMPT,
    TEST_GENERATION_SYSTEM_PROMPT,
    TEST_GENERATION_ADVANCED_PROMPT
)
from models import schemas
from services import sanitizer, llm_service
from services.agent import SQLRefinementAgent
from services.database import DatabaseService
from utils import logger, errors


router = APIRouter()
app_logger = logger.setup_logger(__name__)

sanitizer_service = sanitizer.InputSanitizer()


def get_request_id(request: Request) -> str:
    """Get request ID from request state."""
    return getattr(request.state, "request_id", str(uuid.uuid4()))


@router.get("/status", response_model=schemas.ReadyResponse)
async def status(request: Request) -> schemas.ReadyResponse:
    """
    Check API readiness and configuration.

    Returns:
        ReadyResponse with status and configuration info
    """
    return schemas.ReadyResponse(
        status="ready",
        api_key_configured=True,
        model=llm_service.settings.MODEL
    )


@router.post("/sql/generate", response_model=schemas.SQLGenerationResponse)
async def generate_sql(
    request: schemas.QueryRequest,
    http_request: Request,
    request_id: str = Depends(get_request_id)
) -> schemas.SQLGenerationResponse:
    """
    Generate SQL from natural language query.

    Args:
        request: Query request with natural language
        http_request: FastAPI request object
        request_id: Request ID for tracing

    Returns:
        SQLGenerationResponse with generated SQL or error

    Raises:
        SanitizationError: If input fails sanitization
        SQLGenerationError: If SQL generation fails
    """
    try:
        # Sanitize input
        sanitized_query = sanitizer_service.sanitize(request.query)

        app_logger.info(
            "sql_generation_started",
            extra={
                "request_id": request_id,
                "query_length": len(sanitized_query)
            }
        )

        # Get LLM service
        llm = llm_service.get_llm_service()

        # Use extracted constant prompt
        system_prompt = SQL_GENERATION_SYSTEM_PROMPT

        # Generate SQL using Claude
        response_text, tokens_used = await llm.generate_text(
            prompt=sanitized_query,
            system_prompt=system_prompt,
            max_tokens=1024,
            request_id=request_id
        )

        # Extract SQL from response
        app_logger.info(f"extracting_sql_response_length: {len(response_text)}")
        sql_query = _extract_sql(response_text)
        app_logger.info(f"sql_extracted_length: {len(sql_query)}")

        # Validate SQL
        app_logger.info("validating_sql_query")
        is_valid, error_msg = sanitizer_service.validate_sql_query(sql_query)
        app_logger.info(f"sql_validation_completed: {is_valid}")

        app_logger.info(
            "sql_generation_completed",
            extra={
                "request_id": request_id,
                "is_valid": is_valid,
                "tokens_used": tokens_used
            }
        )

        return schemas.SQLGenerationResponse(
            status="success" if is_valid else "syntax_error",
            sql_query=sql_query if is_valid else None,
            original_request=request.query,
            is_valid=is_valid,
            error=error_msg if not is_valid else None,
            tokens_used=tokens_used,
            timestamp=datetime.utcnow()
        )

    except errors.NLPToSQLError:
        raise
    except Exception as e:
        app_logger.error(
            "sql_generation_error",
            extra={
                "request_id": request_id,
                "error": str(e)
            }
        )
        raise errors.SQLGenerationError(f"Failed to generate SQL: {str(e)}")


async def _execute_sql_service(sql_query: str, request_id: str) -> schemas.ExecutionResult:
    """
    Internal service function to execute SQL query.

    Args:
        sql_query: SQL query to execute
        request_id: Request ID for tracing

    Returns:
        ExecutionResult with query results
    """
    try:
        app_logger.info(
            "sql_execution_started",
            extra={
                "request_id": request_id,
                "query_length": len(sql_query)
            }
        )

        db_service = DatabaseService()
        rows, columns = db_service.execute_query(sql_query)

        result = schemas.ExecutionResult(
            timestamp=datetime.utcnow(),
            status="success",
            rows_returned=len(rows),
            columns=columns,
            sample_data=rows
        )

        app_logger.info(
            "sql_execution_completed",
            extra={
                "request_id": request_id,
                "rows_returned": result.rows_returned
            }
        )

        return result

    except Exception as e:
        app_logger.error(
            "sql_execution_error",
            extra={
                "request_id": request_id,
                "error": str(e)
            }
        )
        raise errors.SQLExecutionError(f"Failed to execute SQL: {str(e)}")


@router.post("/sql/execute", response_model=schemas.ExecutionResult)
async def execute_sql(
    request: schemas.SQLExecutionRequest,
    http_request: Request,
    request_id: str = Depends(get_request_id)
) -> schemas.ExecutionResult:
    """API endpoint for SQL execution."""
    return await _execute_sql_service(request.sql_query, request_id)


@router.post("/tests/generate", response_model=schemas.TestGenerationResponse)
async def generate_tests(
    request: schemas.TestGenerationRequest,
    http_request: Request,
    request_id: str = Depends(get_request_id)
) -> schemas.TestGenerationResponse:
    """
    Generate pytest test cases from SQL query.

    Args:
        request: SQL query and context
        http_request: FastAPI request object
        request_id: Request ID for tracing

    Returns:
        TestGenerationResponse with generated test code or error
    """
    try:
        app_logger.info(
            "test_generation_started",
            extra={
                "request_id": request_id,
                "sql_length": len(request.sql_query)
            }
        )

        # Get LLM service
        llm = llm_service.get_llm_service()

        system_prompt = """You are an expert pytest engineer. Generate comprehensive pytest test cases for SQL queries.

Requirements:
1. Generate valid Python pytest code
2. Include schema validation tests
3. Include data quality checks
4. Return ONLY valid Python code in a ```python``` code block."""

        prompt = f"""Generate pytest test cases for this SQL query:

SQL Query:
```sql
{request.sql_query}
```

User Request: {request.user_request or "Generate tests"}

Return ONLY the complete pytest code."""

        response_text, tokens_used = await llm.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2048,
            request_id=request_id
        )

        # Extract Python code
        test_code = _extract_python_code(response_text)

        app_logger.info(
            "test_generation_completed",
            extra={
                "request_id": request_id,
                "tokens_used": tokens_used,
                "code_length": len(test_code)
            }
        )

        # For now, return mock test file path
        test_file = f"tests/test_generated_{request_id[:8]}.py"

        return schemas.TestGenerationResponse(
            status="success",
            test_code=test_code,
            test_file=test_file,
            tokens_used=tokens_used,
            timestamp=datetime.utcnow()
        )

    except errors.NLPToSQLError:
        raise
    except Exception as e:
        app_logger.error(
            "test_generation_error",
            extra={
                "request_id": request_id,
                "error": str(e)
            }
        )
        raise errors.TestGenerationError(f"Failed to generate tests: {str(e)}")


@router.post("/full-pipeline", response_model=schemas.FullPipelineResponse)
async def full_pipeline(
    request: schemas.FullPipelineRequest,
    http_request: Request,
    request_id: str = Depends(get_request_id)
) -> schemas.FullPipelineResponse:
    """
    Run complete pipeline: NLP → SQL → Execute → Tests.

    Args:
        request: Natural language query
        http_request: FastAPI request object
        request_id: Request ID for tracing

    Returns:
        FullPipelineResponse with all phase results
    """
    try:
        app_logger.info(
            "full_pipeline_started",
            extra={
                "request_id": request_id,
                "query_length": len(request.query)
            }
        )

        # Phase 1: Generate SQL
        app_logger.info("about_to_generate_sql_direct")
        try:
            sanitized_query = sanitizer_service.sanitize(request.query)

            app_logger.info(
                "sql_generation_started",
                extra={
                    "request_id": request_id,
                    "query_length": len(sanitized_query)
                }
            )

            llm = llm_service.get_llm_service()

            system_prompt = """You are an expert SQL engineer. Your job is to convert plain English queries into valid SELECT SQL queries.

Database Schema:
- customers: customer_id (INTEGER), name (TEXT), email (TEXT), country (TEXT), region (TEXT), segment (TEXT), created_at (DATE)
- orders: order_id (INTEGER), customer_id (INTEGER), order_date (DATE), total_amount (REAL), status (TEXT)
- products: product_id (INTEGER), name (TEXT), category (TEXT), price (REAL), stock (INTEGER)
- order_items: order_item_id (INTEGER), order_id (INTEGER), product_id (INTEGER), quantity (INTEGER), unit_price (REAL)

Rules:
1. Generate ONLY valid SELECT queries (no INSERT, UPDATE, DELETE)
2. Return ONLY the SQL query in ```sql``` code block, no explanation
3. Use correct table names and column names from schema above
4. Join tables as needed (e.g., customers with orders via customer_id)
5. Use proper SQL syntax for SQLite database

Format: Return wrapped in ```sql``` code block."""

            response_text, sql_tokens = await llm.generate_text(
                prompt=sanitized_query,
                system_prompt=system_prompt,
                max_tokens=1024,
                request_id=request_id
            )

            sql_query = _extract_sql(response_text)
            is_valid, error_msg = sanitizer_service.validate_sql_query(sql_query)

            app_logger.info(
                "sql_generation_completed",
                extra={
                    "request_id": request_id,
                    "is_valid": is_valid,
                    "tokens_used": sql_tokens
                }
            )

            sql_response = schemas.SQLGenerationResponse(
                status="success" if is_valid else "syntax_error",
                sql_query=sql_query if is_valid else None,
                original_request=request.query,
                is_valid=is_valid,
                error=error_msg if not is_valid else None,
                tokens_used=sql_tokens,
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            app_logger.error(f"sql_generation_failed_in_pipeline: {str(e)}")
            raise

        if not sql_response.is_valid:
            return schemas.FullPipelineResponse(
                status="error",
                query=request.query,
                final_status=f"Phase 1 failed: {sql_response.error}",
                phases={
                    "phase1": {
                        "status": "error",
                        "error": sql_response.error
                    }
                },
                timestamp=datetime.utcnow()
            )

        # Phase 2: Execute SQL
        app_logger.info("about_to_execute_sql")
        exec_response = await _execute_sql_service(sql_response.sql_query, request_id)
        app_logger.info(f"execute_sql_completed: rows={exec_response.rows_returned}")

        # Phase 3: Generate Tests
        app_logger.info("about_to_generate_tests")
        try:
            # Call the LLM directly for test generation instead of the full route
            llm = llm_service.get_llm_service()
            system_prompt = TEST_GENERATION_ADVANCED_PROMPT

            prompt = f"""Analyze this SQL query and generate 3-5 DIFFERENT pytest tests that match its structure.

SQL Query:
```sql
{sql_response.sql_query}
```

Generate tests based on:
- Query type detection (SELECT, JOIN, GROUP BY, WHERE, ORDER BY, DISTINCT, etc.)
- Verify clauses match the query structure
- Test for required keywords specific to this query
- Check column/table names if visible
- Validate aggregation functions if present
- Test sorting/filtering if used

Generate diverse tests - NOT the same test 3 times. Each test should verify a DIFFERENT aspect.

Generate ONLY syntactically valid Python pytest code. No imports beyond pytest."""

            test_response_text, test_tokens = await llm.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=2048,
                request_id=request_id
            )

            test_code = _extract_python_code(test_response_text)

            # Run pytest and capture output (async, doesn't block event loop)
            test_output, exit_code = await _run_pytest(test_code, request_id)

            test_response = schemas.TestGenerationResponse(
                status="success" if exit_code == 0 else "test_failed",
                test_code=test_code,
                test_output=test_output,
                exit_code=exit_code,
                error=None if exit_code == 0 else f"Tests failed with exit code {exit_code}",
                test_file=f"tests/test_generated_{request_id[:8]}.py",
                tokens_used=test_tokens,
                timestamp=datetime.utcnow()
            )

            app_logger.info("generate_tests_completed")
        except Exception as e:
            app_logger.error(f"test_generation_failed: {str(e)}")
            raise

        app_logger.info(
            "full_pipeline_completed",
            extra={
                "request_id": request_id,
                "phases_completed": 3,
                "total_tokens": (
                    sql_response.tokens_used +
                    test_response.tokens_used
                )
            }
        )

        # Save query history to database
        try:
            total_tokens = sql_response.tokens_used + test_response.tokens_used
            cost_usd = (total_tokens * settings.COST_PER_1K_TOKENS) / 1000

            db_service = DatabaseService()
            db_service.save_query_history(
                original_query=request.query,
                generated_sql=sql_response.sql_query,
                execution_status="success",
                rows_returned=exec_response.rows_returned,
                tokens_used=total_tokens,
                cost_usd=cost_usd,
                is_valid=True,
                user_id="anonymous"
            )

            # Update cost tracking
            db_service.update_cost_tracking(
                user_id="anonymous",
                tokens_used=total_tokens,
                cost_usd=cost_usd
            )

            app_logger.info(
                "query_persisted",
                extra={
                    "request_id": request_id,
                    "cost": cost_usd,
                    "tokens": total_tokens
                }
            )
        except Exception as e:
            app_logger.warning(
                "query_persistence_failed",
                extra={
                    "request_id": request_id,
                    "error": str(e)
                }
            )
            # Don't fail the pipeline if database save fails

        response = schemas.FullPipelineResponse(
            status="success",
            query=request.query,
            final_status="All phases completed successfully",
            phases={
                "phase1": {
                    "status": "complete",
                    "sql_query": sql_response.sql_query,
                    "timestamp": sql_response.timestamp.isoformat(),
                    "tokens_used": sql_response.tokens_used
                },
                "execution": {
                    "status": "complete",
                    "rows_returned": exec_response.rows_returned,
                    "columns": exec_response.columns,
                    "sample_data": exec_response.sample_data,
                    "timestamp": exec_response.timestamp.isoformat()
                },
                "phase2": {
                    "status": "complete",
                    "test_code": test_response.test_code,
                    "test_output": test_response.test_output,
                    "exit_code": test_response.exit_code,
                    "test_file": test_response.test_file,
                    "tests_passed": test_response.exit_code == 0,
                    "timestamp": test_response.timestamp.isoformat(),
                    "tokens_used": test_response.tokens_used
                }
            },
            timestamp=datetime.utcnow()
        )
        return response

    except errors.NLPToSQLError as e:
        app_logger.error(
            "full_pipeline_error",
            extra={
                "request_id": request_id,
                "error": e.message,
                "error_type": e.error_type
            }
        )
        raise
    except Exception as e:
        app_logger.error(
            "full_pipeline_unexpected_error",
            extra={
                "request_id": request_id,
                "error": str(e)
            }
        )
        raise


@router.post("/agent/refine-sql", response_model=schemas.AgentRefineSqlResponse)
async def refine_sql_agent(
    request: schemas.AgentRefineSqlRequest,
    http_request: Request,
    request_id: str = Depends(get_request_id)
) -> schemas.AgentRefineSqlResponse:
    """
    Refine SQL through multi-turn agent conversation.

    Args:
        request: Initial query, generated SQL, and validation feedback
        http_request: FastAPI request object
        request_id: Request ID for tracing

    Returns:
        AgentRefineSqlResponse with refined SQL and conversation ID
    """
    try:
        app_logger.info(
            "agent_refine_sql_started",
            extra={
                "request_id": request_id,
                "query_length": len(request.initial_query)
            }
        )

        agent = SQLRefinementAgent(request_id)
        result = agent.refine_sql(
            initial_query=request.initial_query,
            generated_sql=request.generated_sql,
            validation_feedback=request.validation_feedback,
            user_id="anonymous"
        )

        app_logger.info(
            "agent_refine_sql_completed",
            extra={
                "request_id": request_id,
                "conversation_id": result["conversation_id"],
                "tokens_used": result["tokens_used"]
            }
        )

        return schemas.AgentRefineSqlResponse(**result)

    except Exception as e:
        app_logger.error(
            "agent_refine_sql_error",
            extra={
                "request_id": request_id,
                "error": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/validate-tests", response_model=schemas.AgentValidateTestsResponse)
async def validate_tests_agent(
    request: schemas.AgentValidateTestsRequest,
    http_request: Request,
    request_id: str = Depends(get_request_id)
) -> schemas.AgentValidateTestsResponse:
    """
    Validate and improve test cases through agent conversation.

    Args:
        request: SQL query, test code, and test output
        http_request: FastAPI request object
        request_id: Request ID for tracing

    Returns:
        AgentValidateTestsResponse with improved tests
    """
    try:
        app_logger.info(
            "agent_validate_tests_started",
            extra={
                "request_id": request_id
            }
        )

        agent = SQLRefinementAgent(request_id)
        result = agent.validate_tests(
            sql_query=request.sql_query,
            test_code=request.test_code,
            test_output=request.test_output,
            user_id="anonymous"
        )

        app_logger.info(
            "agent_validate_tests_completed",
            extra={
                "request_id": request_id,
                "conversation_id": result["conversation_id"],
                "tokens_used": result["tokens_used"]
            }
        )

        return schemas.AgentValidateTestsResponse(**result)

    except Exception as e:
        app_logger.error(
            "agent_validate_tests_error",
            extra={
                "request_id": request_id,
                "error": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/optimize-query", response_model=schemas.AgentOptimizeQueryResponse)
async def optimize_query_agent(
    request: schemas.AgentOptimizeQueryRequest,
    http_request: Request,
    request_id: str = Depends(get_request_id)
) -> schemas.AgentOptimizeQueryResponse:
    """
    Optimize SQL query through agent analysis.

    Args:
        request: SQL query and performance metrics
        http_request: FastAPI request object
        request_id: Request ID for tracing

    Returns:
        AgentOptimizeQueryResponse with optimized query and suggestions
    """
    try:
        app_logger.info(
            "agent_optimize_query_started",
            extra={
                "request_id": request_id
            }
        )

        agent = SQLRefinementAgent(request_id)
        result = agent.optimize_query(
            sql_query=request.sql_query,
            performance_metrics=request.performance_metrics or {},
            user_id="anonymous"
        )

        app_logger.info(
            "agent_optimize_query_completed",
            extra={
                "request_id": request_id,
                "conversation_id": result["conversation_id"],
                "tokens_used": result["tokens_used"]
            }
        )

        return schemas.AgentOptimizeQueryResponse(**result)

    except Exception as e:
        app_logger.error(
            "agent_optimize_query_error",
            extra={
                "request_id": request_id,
                "error": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(
    http_request: Request,
    limit: int = 10,
    request_id: str = Depends(get_request_id)
) -> dict:
    """
    Get query history for the user.

    Args:
        http_request: FastAPI request object
        limit: Number of records to return
        request_id: Request ID for tracing

    Returns:
        Dictionary with history records
    """
    try:
        db_service = DatabaseService()
        history = db_service.get_query_history(user_id="anonymous", limit=limit)

        app_logger.info(
            "history_retrieved",
            extra={
                "request_id": request_id,
                "records": len(history)
            }
        )

        return {
            "status": "success",
            "records": [
                {
                    "id": h.id,
                    "original_query": h.original_query,
                    "generated_sql": h.generated_sql,
                    "execution_status": h.execution_status,
                    "rows_returned": h.rows_returned,
                    "cost_usd": h.cost_usd,
                    "created_at": h.created_at.isoformat() if h.created_at else None
                }
                for h in history
            ]
        }

    except Exception as e:
        app_logger.error(
            "history_retrieval_error",
            extra={
                "request_id": request_id,
                "error": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions

def _extract_sql(response: str) -> str:
    """Extract SQL from LLM response."""
    try:
        if "```sql" in response:
            start = response.find("```sql") + 6
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        # If no proper code blocks found, return as-is
        return response.strip()
    except Exception as e:
        app_logger.error(f"sql_extraction_error: {str(e)}")
        return response.strip()


def _extract_python_code(response: str) -> str:
    """Extract Python code from LLM response."""
    try:
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        # If no proper code blocks found, return as-is
        return response.strip()
    except Exception as e:
        app_logger.error(f"python_extraction_error: {str(e)}")
        return response.strip()


def _validate_test_code_safety(test_code: str, request_id: str) -> bool:
    """Validate test code for dangerous imports and operations."""
    DANGEROUS_MODULES = {'os', 'sys', 'subprocess', 'requests', 'socket', 'urllib', 'httplib', 'telnetlib'}

    for module in DANGEROUS_MODULES:
        patterns = [
            rf'^\s*import\s+{module}\b',
            rf'^\s*from\s+{module}\b',
            rf'^\s*import\s+.*\b{module}\b'
        ]

        for pattern in patterns:
            if re.search(pattern, test_code, re.MULTILINE):
                error_msg = f"Dangerous import detected: {module}. Only pytest allowed."
                app_logger.warning(
                    "dangerous_import_attempt",
                    extra={
                        "request_id": request_id,
                        "module": module,
                        "code_length": len(test_code)
                    }
                )
                raise ValueError(error_msg)

    return True


async def _run_pytest(test_code: str, request_id: str) -> tuple:
    """Run pytest asynchronously without blocking event loop."""
    import sys
    import subprocess

    # Validate for dangerous imports first
    _validate_test_code_safety(test_code, request_id)

    try:
        # Validate Python syntax
        try:
            ast.parse(test_code)
        except SyntaxError as e:
            error_msg = f"Test code syntax error at line {e.lineno}: {e.msg}"
            app_logger.error(f"test_syntax_error: {error_msg}")
            return error_msg, 1

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=os.getcwd()) as f:
            f.write(test_code)
            test_file = f.name

        try:
            # Use venv Python explicitly
            venv_python = os.path.join(sys.prefix, 'Scripts', 'python.exe')
            if not os.path.exists(venv_python):
                venv_python = os.path.join(sys.prefix, 'bin', 'python')

            # Run in thread pool to avoid blocking (Windows doesn't support async subprocess)
            def run_pytest_sync():
                return subprocess.run(
                    [venv_python, '-m', 'pytest', test_file, '-v', '--tb=short'],
                    capture_output=True,
                    text=True,
                    timeout=settings.TEST_TIMEOUT_SECONDS,
                    cwd=os.getcwd()
                )

            result = await asyncio.to_thread(run_pytest_sync)
            output = result.stdout + result.stderr
            exit_code = result.returncode

        except subprocess.TimeoutExpired:
            return "Tests timed out after {} seconds".format(settings.TEST_TIMEOUT_SECONDS), 124
        finally:
            try:
                os.unlink(test_file)
            except:
                pass

        if not output:
            output = "Tests executed successfully (no output captured)"

        app_logger.info(
            "pytest_executed",
            extra={
                "request_id": request_id,
                "exit_code": exit_code,
                "output_length": len(output)
            }
        )

        return output, exit_code

    except Exception as e:
        app_logger.error(f"pytest_execution_error: {str(e)}")
        raise
