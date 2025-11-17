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
from app.layers.api.validators.query_validator import validate_query
from app.layers.api.dependencies import get_agent_orchestrator, get_db_session, verify_api_key
from app.layers.ai_agent.agent.agent_orchestrator import AgentOrchestrator
from app.shared.database.repositories.repository_factory import RepositoryFactory
from app.shared.utils.logger import get_logger
from app.shared.config.constants.app_constants import ProcessingStep, StepStatus
from app.shared.schemas.sse_schema import SSEStepUpdate

router = APIRouter()
logger = get_logger(__name__)


@router.post("/query", response_model=QueryResponse)
async def process_query(
        request: QueryRequest,
        agent: AgentOrchestrator = Depends(get_agent_orchestrator),
        db: AsyncSession = Depends(get_db_session),
        api_key: str = Depends(verify_api_key)
) -> QueryResponse:
    """
    Process container tracking query through AI agent

    Flow:
    1. Validate query
    2. Process through two-agent pipeline (tool agent → parser agent)
    3. Log to database
    4. Return structured response
    """
    start_time = time.time()
    query_log_repo = None

    try:
        # Validate input
        validate_query(request.query)
        logger.info(f"Processing query: {request.query}")

        # Initialize repository
        repo_factory = RepositoryFactory()
        query_log_repo = repo_factory.get_query_log_repository(db)

        # Process through agent pipeline
        result = await agent.process_query(request.query)
        processing_time = int((time.time() - start_time) * 1000)

        # Extract container_id and intent from result
        container_id = result.data.container_id if result.data else None
        intent = result.data.intent if result.data else None

        # Log successful query
        await query_log_repo.create(
            user_query=request.query,
            extracted_container=container_id,
            intent=intent,
            response_time_ms=processing_time,
            status="success" if not result.data.has_errors else "partial_success",
            workflow_id=None,
            error_message=result.data.error_message if result.data.has_errors else None
        )
        await db.commit()

        logger.info(f"Query processed successfully in {processing_time}ms")

        # Build response
        return QueryResponse(
            status="success",
            data=result,
            metadata={
                "query_time_ms": processing_time,
                "cached": result.cached,
                "container_id": container_id,
                "intent": intent,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    except ValueError as e:
        # Validation errors
        logger.warning(f"Validation error: {str(e)}")
        processing_time = int((time.time() - start_time) * 1000)

        if query_log_repo:
            try:
                await query_log_repo.create(
                    user_query=request.query,
                    response_time_ms=processing_time,
                    status="failed",
                    error_message=f"Validation error: {str(e)}"
                )
                await db.commit()
            except Exception as log_error:
                logger.error(f"Failed to log validation error: {log_error}")

        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid query",
                "message": str(e),
                "query_time_ms": processing_time
            }
        )

    except Exception as e:
        # Unexpected errors
        logger.error(f"Query processing failed: {str(e)}", exc_info=True)
        processing_time = int((time.time() - start_time) * 1000)

        if query_log_repo:
            try:
                await query_log_repo.create(
                    user_query=request.query,
                    response_time_ms=processing_time,
                    status="failed",
                    error_message=str(e)
                )
                await db.commit()
            except Exception as log_error:
                logger.error(f"Failed to log error: {log_error}")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Processing failed",
                "message": "An error occurred while processing your query. Please try again.",
                "query_time_ms": processing_time
            }
        )


@router.post("/query/stream")
async def process_query_stream(
        request: QueryRequest,
        agent: AgentOrchestrator = Depends(get_agent_orchestrator),
        db: AsyncSession = Depends(get_db_session),
        api_key: str = Depends(verify_api_key)
):
    """
    Stream query processing updates via SSE

    Useful for long-running queries or when you want to show progress
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        start_time = time.time()

        try:
            # Validate
            validate_query(request.query)

            yield format_sse_event(SSEStepUpdate(
                step=ProcessingStep.VALIDATION,
                status=StepStatus.COMPLETED,
                message="Query validated"
            ))

            # Processing
            yield format_sse_event(SSEStepUpdate(
                step=ProcessingStep.AGENT_PROCESSING,
                status=StepStatus.IN_PROGRESS,
                message="Processing with AI agent..."
            ))

            result = await agent.process_query(request.query)
            processing_time = int((time.time() - start_time) * 1000)

            yield format_sse_event(SSEStepUpdate(
                step=ProcessingStep.AGENT_PROCESSING,
                status=StepStatus.COMPLETED,
                message="Agent processing completed"
            ))

            # Log to database
            repo_factory = RepositoryFactory()
            query_log_repo = repo_factory.get_query_log_repository(db)

            await query_log_repo.create(
                user_query=request.query,
                extracted_container=result.data.container_id,
                intent=result.data.intent,
                response_time_ms=processing_time,
                status="success",
                workflow_id=None
            )
            await db.commit()

            # Send final result
            yield format_sse_event({
                "step": "completed",
                "status": "success",
                "data": {
                    "message": result.raw_data,
                    "container_id": result.data.container_id,
                    "cached": result.cached,
                    "processing_time_ms": processing_time
                }
            })

        except Exception as e:
            logger.error(f"Stream processing error: {str(e)}", exc_info=True)
            yield format_sse_event({
                "step": "error",
                "status": "failed",
                "message": str(e)
            })

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


def format_sse_event(data: dict | SSEStepUpdate) -> str:
    """Format data as Server-Sent Event"""
    if isinstance(data, SSEStepUpdate):
        data = data.model_dump()

    return f"data: {json.dumps(data)}\n\n"


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "container-tracking-api"
    }


@router.get("/tools")
async def list_tools(
        agent: AgentOrchestrator = Depends(get_agent_orchestrator),
        api_key: str = Depends(verify_api_key)
):
    """List available tools and their descriptions"""
    tools = agent.gemini_agent.list_available_tools()

    tool_info = []
    for tool_name in tools:
        info = agent.gemini_agent.get_tool_info(tool_name)
        tool_info.append(info)

    return {
        "available_tools": tool_info,
        "count": len(tools)
    }