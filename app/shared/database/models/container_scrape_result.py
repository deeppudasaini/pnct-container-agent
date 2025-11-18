from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP, func
from app.shared.database.base import Base

class ContainerScrapeResult(Base):
    __tablename__ = "container_scrape_results"

    id = Column(Integer, primary_key=True, index=True)
    container_number = Column(String(11), nullable=False, index=True)
    operation = Column(String(50), nullable=False, index=True)
    raw_html = Column(Text, nullable=True)
    parsed_json = Column(JSON, nullable=True)
    status = Column(String(20), default="success", index=True)
    error_message = Column(Text, nullable=True)
    scraped_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
