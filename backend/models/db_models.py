"""SQLAlchemy ORM models for database persistence."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class QueryHistory(Base):
    """History of all user queries and their results."""

    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), default="anonymous", index=True)
    original_query = Column(String(2000), nullable=False)
    generated_sql = Column(Text, nullable=True)
    execution_status = Column(String(50), default="pending")  # pending, success, error
    rows_returned = Column(Integer, nullable=True)
    api_tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    execution_error = Column(Text, nullable=True)
    is_valid_sql = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<QueryHistory(id={self.id}, status={self.execution_status})>"


class CostTracking(Base):
    """Track API costs per user per day."""

    __tablename__ = "cost_tracking"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    daily_tokens = Column(Integer, default=0)
    daily_cost_usd = Column(Float, default=0.0)
    daily_queries = Column(Integer, default=0)

    def __repr__(self):
        return f"<CostTracking(user={self.user_id}, cost=${self.daily_cost_usd})>"


class AgentConversation(Base):
    """Store agentic AI multi-turn conversations."""

    __tablename__ = "agent_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), default="anonymous", index=True)
    conversation_id = Column(String(255), unique=True, index=True)
    topic = Column(String(500))  # e.g., "sql_refinement", "test_validation"
    messages = Column(Text)  # JSON-serialized conversation history
    current_state = Column(String(100))  # e.g., "pending", "in_progress", "complete"
    result = Column(Text, nullable=True)  # Final result from agent
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AgentConversation(id={self.id}, topic={self.topic})>"
