"""Query schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)


class ParsedQuery(BaseModel):
    original_query: str
    container_id: str
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    entities: Dict[str, Any] = Field(default_factory=dict)


class QueryMetadata(BaseModel):
    query_time_ms: int
    workflow_id: Optional[str] = None
    cached: bool = False
    container_id: Optional[str] = None
    intent: Optional[str] = None
    processing_steps: List[Dict[str, Any]] = Field(default_factory=list)


class QueryResponse(BaseModel):
    status: str = "success"
    data: Optional[Dict[str, Any]] = None
    metadata: QueryMetadata
    error: Optional[str] = None
