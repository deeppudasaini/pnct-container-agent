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

    start_time = time.time()

    try:
        validate_query(request.query)

        logger.info(f"Processing query: {request.query}")

        repo_factory = RepositoryFactory()
        query_log_repo = repo_factory.get_query_log_repository(db)

        result = await agent.process_query(request.query)

        processing_time = int((time.time() - start_time) * 1000)

        await query_log_repo.create(
            user_query=request.query,
            extracted_container=result.container_id,
            intent=result.intent,
            response_time_ms=processing_time,
            status="success",
            workflow_id=result.workflow_id
        )

        await db.commit()

        return QueryResponse(
            status="success",
            data=result.data,
            metadata={
                "query_time_ms": processing_time,
                "workflow_id": result.workflow_id,
                "cached": result.cached,
                "container_id": result.container_id,
                "intent": result.intent,
            }
        )

    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}", exc_info=True)

        try:
            await query_log_repo.create(
                user_query=request.query,
                response_time_ms=int((time.time() - start_time) * 1000),
                status="failed",
                error_message=str(e)
            )
            await db.commit()
        except:
            pass

        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
async def process_query_stream(
        request: QueryRequest,
        agent: AgentOrchestrator = Depends(get_agent_orchestrator),
        db: AsyncSession = Depends(get_db_session),
        api_key: str = Depends(verify_api_key)
):


    async def event_generator() -> AsyncGenerator[str, None]:
        start_time = time.time()

        try:
            yield format_sse_event(
                SSEStepUpdate(
                    step=ProcessingStep.VALIDATE_REQUEST,
                    status=StepStatus.IN_PROGRESS,
                    message="Validating request",
                    progress=5,
                    timestamp=datetime.utcnow().isoformat()
                )
            )

            validate_query(request.query)

            yield format_sse_event(
                SSEStepUpdate(
                    step=ProcessingStep.VALIDATE_REQUEST,
                    status=StepStatus.COMPLETED,
                    message="Request validated",
                    progress=10,
                    timestamp=datetime.utcnow().isoformat()
                )
            )

            yield format_sse_event(
                SSEStepUpdate(
                    step=ProcessingStep.PARSE_QUERY,
                    status=StepStatus.IN_PROGRESS,
                    message="Parsing query with AI",
                    progress=15,
                    timestamp=datetime.utcnow().isoformat()
                )
            )

            async for update in agent.process_query_stream(request.query):
                yield format_sse_event(update)

            processing_time = int((time.time() - start_time) * 1000)

            yield format_sse_event({
                "type": "complete",
                "status": "completed",
                "total_time_ms": processing_time,
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            logger.error(f"Stream processing failed: {str(e)}", exc_info=True)

            yield format_sse_event({
                "type": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
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
    if isinstance(data, SSEStepUpdate):
        data = data.model_dump()

    return f"data: {json.dumps(data)}\n\n"
