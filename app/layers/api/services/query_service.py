import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
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

logger = get_logger(__name__)

class QueryService:
    async def execute_query(self, request:QueryRequest,
                            agent: AgentOrchestrator = Depends(get_agent_orchestrator),
                            db: AsyncSession = Depends(get_db_session),
                            api_key: str = Depends(verify_api_key)
                            ) ->QueryResponse:
        start_time = time.time()
        query_log_repo = None

        try:
            validate_query(request.query)
            logger.info(f"Processing query: {request.query}")

            repo_factory = RepositoryFactory()
            query_log_repo = repo_factory.get_query_log_repository(db)

            result = await agent.process_query(request.query)
            processing_time = int((time.time() - start_time) * 1000)

            container_id = result.data.container_id if result.data else None
            intent = result.data.intent if result.data else None

            await query_log_repo.create(
                user_query=request.query,
                extracted_container=container_id,
                intent=intent,
                response_time_ms=processing_time,
                status="success" if not result.data.has_errors else "partial_success",
                workflow_id=None,
                error_message=result.data.error_message if result.data.has_errors else None,
                query_result=None
            )
            await db.commit()

            logger.info(f"Query processed successfully in {processing_time}ms")

            return QueryResponse(
                status="success",
                data=result.raw_data,
                metadata={
                    "query_time_ms": processing_time,
                    "cached": result.cached,
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