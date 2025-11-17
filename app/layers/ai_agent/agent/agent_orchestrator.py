import time
import asyncio
from typing import Dict, Any, AsyncGenerator, Optional
from dataclasses import dataclass
from datetime import datetime

from app.layers.ai_agent.agent.gemini_agent import GeminiAgent
from app.layers.ai_agent.parsers.query_parser import QueryParser
from app.layers.ai_agent.parsers.intent_parser import IntentParser
from app.layers.ai_agent.parsers.entity_extractor import EntityExtractor
from app.layers.ai_agent.schemas.output_schema import ContainerParseSchema
from app.shared.utils.logger import get_logger
from app.shared.utils.cache import CacheManager
from app.shared.config.constants.app_constants import ProcessingStep, StepStatus
from app.shared.schemas.sse_schema import SSEStepUpdate

logger = get_logger(__name__)


@dataclass
class AgentResult:
    data: ContainerParseSchema
    processing_time_ms: int
    cached: bool
    raw_data:str


class AgentOrchestrator:

    def __init__(self):
        self.gemini_agent = GeminiAgent()
        self.query_parser = QueryParser()
        self.intent_parser = IntentParser()
        self.entity_extractor = EntityExtractor()
        self.cache = CacheManager()

    async def process_query(self, query: str) -> AgentResult:
        """
        Process a query through the two-agent system:
        1. Tool agent retrieves data
        2. Parser agent structures the data
        """
        start_time = time.time()

        logger.info(f"Agent orchestrator processing query: {query}")

        # Check cache first
        cache_key = f"query:{query.lower()}"
        cached_result = await self.cache.get(cache_key)

        # if cached_result:
        #     logger.info("Returning cached result")
        #     # Reconstruct ContainerParseSchema from cached data
        #     cached_schema = ContainerParseSchema(**cached_result["data"])
        #     return AgentResult(
        #         data=cached_schema,
        #         processing_time_ms=int((time.time() - start_time) * 1000),
        #         cached=True,
        #         raw_data=self._safe_get_message(cached_schema)
        #     )

        # Process with two-agent system
        try:
            # Full pipeline: tool agent -> parser agent
            parsed = await self.gemini_agent.parse_query(query)

            processing_time = int((time.time() - start_time) * 1000)

            # Cache the result (convert to dict for caching)
            cache_data = self.gemini_agent.get_schema_dict(parsed)
            await self.cache.set(cache_key, {"data": cache_data}, ttl=300)

            # Safely extract message
            raw_data = self._safe_get_message(parsed)

            return AgentResult(
                data=parsed,
                processing_time_ms=processing_time,
                cached=False,
                raw_data=raw_data
            )

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            # Return error result
            error_schema = ContainerParseSchema(
                message=f"Error processing query: {str(e)}",
                has_errors=True,
                error_message=str(e)
            )
            return AgentResult(
                data=error_schema,
                processing_time_ms=int((time.time() - start_time) * 1000),
                cached=False,
                raw_data=f"Error: {str(e)}"
            )

    def _safe_get_message(self, schema: Optional[ContainerParseSchema]) -> str:
        """
        Safely extract message from schema with fallbacks
        """
        if schema is None:
            return "No data available"

        # Try to get message using the agent's helper method
        message = self.gemini_agent.get_message_from_schema(schema)

        if message:
            return message

        # Fallback: generate message from available data
        if schema.container_id:
            return f"Information for container {schema.container_id} retrieved successfully."

        return "Container information processed."

