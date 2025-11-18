"""Query log database model"""
from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.shared.database.base import Base


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(Text, nullable=False)
    extracted_container = Column(String(11), index=True)
    intent = Column(String(50))
    response_time_ms = Column(Integer)
    status = Column(String(20), default="success")
    error_message = Column(Text, nullable=True)
    workflow_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    query_result = Column(JSONB, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_query": self.user_query,
            "extracted_container": self.extracted_container,
            "intent": self.intent,
            "response_time_ms": self.response_time_ms,
            "status": self.status,
            "workflow_id": self.workflow_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "query_result":self.query_result
        }

