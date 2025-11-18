from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from app.layers.ai_agent.agent.agent_orchestrator import AgentResult
from app.layers.ai_agent.schemas.output_schema import ContainerParseSchema
from app.shared.schemas.response_schema import SuccessResponse, ErrorResponse


class QueryResponse(BaseModel):
    status: str = "success"
    data: str = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": "<LLM Message>",
                "metadata": {
                    "query_time_ms": 2341,
                    "workflow_id": "wf-abc123",
                    "cached": False,
                    "intent": "get_info"
                }
            }
        }


class ContainerResponse(BaseModel):
    status: str = "success"
    data: Dict[str, Any]
    cached: bool = False
    last_updated: Optional[str] = None