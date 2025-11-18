from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class ScrapeResultBase(BaseModel):
    container_number: str
    operation: str
    raw_html: Optional[str] = None
    parsed_json: Optional[Any] = None
    status: Optional[str] = "success"
    error_message: Optional[str] = None

class ScrapeResultCreate(ScrapeResultBase):
    pass

class ScrapeResultUpdate(BaseModel):
    raw_html: Optional[str] = None
    parsed_json: Optional[Any] = None
    status: Optional[str] = None
    error_message: Optional[str] = None

class ScrapeResultResponse(ScrapeResultBase):
    id: int
    scraped_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
