"""Database service for persistence and CRUD operations."""

from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional, Dict, Any

from config import settings
from models.db_models import Base, QueryHistory, CostTracking, AgentConversation
from utils import logger

app_logger = logger.setup_logger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True  # Verify connections before using
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        app_logger.info("database_initialized")
    except Exception as e:
        app_logger.error(f"database_init_failed: {str(e)}")
        raise


def get_db() -> Session:
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseService:
    """Service for database operations."""

    @staticmethod
    def save_query_history(
        original_query: str,
        generated_sql: Optional[str],
        execution_status: str,
        rows_returned: Optional[int] = None,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        error: Optional[str] = None,
        is_valid: bool = False,
        user_id: str = "anonymous"
    ) -> QueryHistory:
        """Save query execution to history."""
        db = SessionLocal()
        try:
            query_record = QueryHistory(
                user_id=user_id,
                original_query=original_query[:2000],
                generated_sql=generated_sql,
                execution_status=execution_status,
                rows_returned=rows_returned,
                api_tokens_used=tokens_used,
                cost_usd=cost_usd,
                execution_error=error,
                is_valid_sql=is_valid
            )
            db.add(query_record)
            db.commit()
            db.refresh(query_record)

            app_logger.info(
                "query_saved",
                extra={
                    "query_id": query_record.id,
                    "status": execution_status,
                    "tokens": tokens_used
                }
            )

            return query_record
        except Exception as e:
            db.rollback()
            app_logger.error(f"query_save_failed: {str(e)}")
            raise
        finally:
            db.close()

    @staticmethod
    def update_cost_tracking(
        user_id: str,
        tokens_used: int,
        cost_usd: float
    ) -> CostTracking:
        """Update daily cost tracking."""
        db = SessionLocal()
        try:
            today = date.today()

            # Find or create today's record
            record = db.query(CostTracking).filter(
                CostTracking.user_id == user_id,
                CostTracking.date >= datetime(today.year, today.month, today.day)
            ).first()

            if record:
                record.daily_tokens += tokens_used
                record.daily_cost_usd += cost_usd
                record.daily_queries += 1
            else:
                record = CostTracking(
                    user_id=user_id,
                    daily_tokens=tokens_used,
                    daily_cost_usd=cost_usd,
                    daily_queries=1
                )
                db.add(record)

            db.commit()
            db.refresh(record)

            app_logger.info(
                "cost_updated",
                extra={
                    "user": user_id,
                    "daily_cost": record.daily_cost_usd
                }
            )

            return record
        except Exception as e:
            db.rollback()
            app_logger.error(f"cost_update_failed: {str(e)}")
            raise
        finally:
            db.close()

    @staticmethod
    def get_query_history(user_id: str, limit: int = 10) -> list:
        """Get recent queries for a user."""
        db = SessionLocal()
        try:
            records = db.query(QueryHistory).filter(
                QueryHistory.user_id == user_id
            ).order_by(QueryHistory.created_at.desc()).limit(limit).all()
            return records
        finally:
            db.close()

    @staticmethod
    def save_agent_conversation(
        user_id: str,
        conversation_id: str,
        topic: str,
        messages: str,
        state: str = "in_progress",
        result: Optional[str] = None
    ) -> AgentConversation:
        """Save agentic AI conversation."""
        db = SessionLocal()
        try:
            conv = AgentConversation(
                user_id=user_id,
                conversation_id=conversation_id,
                topic=topic,
                messages=messages,
                current_state=state,
                result=result
            )
            db.add(conv)
            db.commit()
            db.refresh(conv)

            app_logger.info(
                "agent_conversation_saved",
                extra={
                    "conv_id": conversation_id,
                    "topic": topic
                }
            )

            return conv
        except Exception as e:
            db.rollback()
            app_logger.error(f"agent_conversation_save_failed: {str(e)}")
            raise
        finally:
            db.close()

    @staticmethod
    def update_agent_conversation(
        conversation_id: str,
        messages: Optional[str] = None,
        state: Optional[str] = None,
        result: Optional[str] = None
    ) -> Optional[AgentConversation]:
        """Update agentic AI conversation."""
        db = SessionLocal()
        try:
            conv = db.query(AgentConversation).filter(
                AgentConversation.conversation_id == conversation_id
            ).first()

            if not conv:
                return None

            if messages:
                conv.messages = messages
            if state:
                conv.current_state = state
            if result:
                conv.result = result

            db.commit()
            db.refresh(conv)
            return conv
        except Exception as e:
            db.rollback()
            app_logger.error(f"agent_conversation_update_failed: {str(e)}")
            raise
        finally:
            db.close()

    @staticmethod
    def execute_query(sql_query: str) -> tuple:
        """Execute SQL query with security controls."""
        import re
        from sqlalchemy import text
        from sqlalchemy.exc import ArgumentError

        # Security: Validate query before execution
        query_upper = sql_query.strip().upper()

        # Reject dangerous operations
        dangerous_ops = {'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE', 'PRAGMA'}
        for op in dangerous_ops:
            if re.match(rf'^\s*{op}\b', query_upper):
                raise ValueError(f"Operation {op} not allowed. Only SELECT queries permitted.")

        # Reject excessive nesting
        if query_upper.count('SELECT') > settings.MAX_QUERY_COMPLEXITY:
            raise ValueError(f"Query too complex: max {settings.MAX_QUERY_COMPLEXITY} nested SELECT levels allowed")

        db = SessionLocal()
        try:
            # Execute with timeout
            result = db.execute(text(sql_query).execution_options(timeout=settings.QUERY_TIMEOUT_SECONDS))

            # Get column names
            columns = list(result.keys()) if hasattr(result, 'keys') else []

            # Get rows as list of dicts with row limit
            rows = []
            for idx, row in enumerate(result):
                if idx >= settings.MAX_QUERY_ROWS:
                    app_logger.warning(
                        "query_exceeded_max_rows",
                        extra={"max_rows": settings.MAX_QUERY_ROWS}
                    )
                    break
                row_dict = dict(row._mapping) if hasattr(row, '_mapping') else dict(zip(columns, row))
                rows.append(row_dict)

            app_logger.info(
                "query_executed",
                extra={
                    "rows_returned": len(rows),
                    "columns": len(columns)
                }
            )

            return rows, columns
        except ArgumentError as e:
            app_logger.error(f"query_syntax_error: {str(e)}")
            raise ValueError(f"Invalid SQL syntax: {str(e)}")
        except Exception as e:
            app_logger.error(f"query_execution_failed: {str(e)}")
            raise
        finally:
            db.close()
