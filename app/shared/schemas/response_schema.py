from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List, Generic, TypeVar

T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    status: str = "success"
    data: T
    metadata: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    error: str
    details: Optional[Dict[str, Any]] = None
    code: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    status: str = "success"
    data: List[T]
    pagination: Dict[str, Any] = Field(
        default_factory=lambda: {
            "total": 0,
            "page": 1,
            "per_page": 50,
            "total_pages": 0
        }
    )


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: str
    services: Dict[str, str] = Field(default_factory=dict)
