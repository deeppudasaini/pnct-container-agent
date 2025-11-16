"""Container database model"""
from sqlalchemy import Column, String, DateTime, JSON, Integer
from sqlalchemy.sql import func
from app.shared.database.base import Base


class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)
    container_number = Column(String(11), unique=True, index=True, nullable=False)
    data = Column(JSON, nullable=False)
    source = Column(String(50), default="PNCT")
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "container_number": self.container_number,
            "data": self.data,
            "source": self.source,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
