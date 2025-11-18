import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from datetime import datetime
import time

from app.layers.api.schemas.request import QueryRequest
from app.layers.api.schemas.response import QueryResponse
from app.layers.api.services.query_service import QueryService
from app.layers.api.validators.query_validator import validate_query
from app.layers.api.dependencies import get_agent_orchestrator, get_db_session, verify_api_key
from app.layers.ai_agent.agent.agent_orchestrator import AgentOrchestrator
from app.shared.database.repositories.repository_factory import RepositoryFactory
from app.shared.utils.logger import get_logger
from app.shared.config.constants.app_constants import ProcessingStep, StepStatus
from app.shared.schemas.sse_schema import SSEStepUpdate

router = APIRouter()
logger = get_logger(__name__)
query_service = QueryService()


@router.post("/query", response_model=QueryResponse)
async def process_query(
        request: QueryRequest,
        agent: AgentOrchestrator = Depends(get_agent_orchestrator),
        db: AsyncSession = Depends(get_db_session),
        api_key: str = Depends(verify_api_key)
) -> QueryResponse:
    return await query_service.execute_query(
        request=request,
        agent=agent,
        db=db,
        api_key=api_key
    )

@router.get("/tools")
async def list_tools(
        agent: AgentOrchestrator = Depends(get_agent_orchestrator),
        api_key: str = Depends(verify_api_key)
):
    tools = agent.gemini_agent.list_available_tools()

    tool_info = []
    for tool_name in tools:
        info = agent.gemini_agent.get_tool_info(tool_name)
        tool_info.append(info)

    return {
        "available_tools": tool_info,
        "count": len(tools)
    }