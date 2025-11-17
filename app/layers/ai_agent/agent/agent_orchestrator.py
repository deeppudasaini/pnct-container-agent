import time
import asyncio
from typing import Dict, Any, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime

from app.layers.ai_agent.agent.gemini_agent import GeminiAgent
from app.layers.ai_agent.parsers.query_parser import QueryParser
from app.layers.ai_agent.parsers.intent_parser import IntentParser
from app.layers.ai_agent.parsers.entity_extractor import EntityExtractor
from app.shared.utils.logger import get_logger
from app.shared.utils.cache import CacheManager
from app.shared.config.constants.app_constants import ProcessingStep, StepStatus
from app.shared.schemas.sse_schema import SSEStepUpdate

logger = get_logger(__name__)


@dataclass
class AgentResult:
    data: Dict[str, Any]
    container_id: str
    intent: str
    workflow_id: str
    processing_time_ms: int
    cached: bool


class AgentOrchestrator:

    def __init__(self):
        self.gemini_agent = GeminiAgent()
        self.query_parser = QueryParser()
        self.intent_parser = IntentParser()
        self.entity_extractor = EntityExtractor()
        self.cache = CacheManager()

    async def process_query(self, query: str) -> AgentResult:
        start_time = time.time()

        logger.info(f"Agent orchestrator processing query: {query}")

        cache_key = f"query:{query.lower()}"
        cached_result = await self.cache.get(cache_key)

        if cached_result:
            logger.info("Returning cached result")
            return AgentResult(
                data=cached_result["data"],
                container_id=cached_result["container_id"],
                intent=cached_result["intent"],
                workflow_id=cached_result["workflow_id"],
                processing_time_ms=int((time.time() - start_time) * 1000),
                cached=True
            )

        parsed = await self.gemini_agent.parse_query(query)
        print("PARSED RESPONSE FROM AGENT::"+parsed)
        container_id = parsed.get("container_id")
        intent = parsed.get("intent", "get_info")

        if not container_id:
            raise ValueError("Could not extract container ID from query")

        logger.info(f"Extracted - Container: {container_id}, Intent: {intent}")



        processing_time = int((time.time() - start_time) * 1000)

        cache_data = {
            "data": parsed.data,
            "container_id": container_id,
            "intent": intent,
            "workflow_id": parsed.workflow_id,
        }
        await self.cache.set(cache_key, cache_data, ttl=300)

        return AgentResult(
            data=parsed.data,
            container_id=container_id,
            intent=intent,
            workflow_id=parsed.workflow_id,
            processing_time_ms=processing_time,
            cached=False
        )

    async def process_query_stream(
            self,
            query: str
    ) -> AsyncGenerator[SSEStepUpdate, None]:

        start_time = time.time()

        try:
            yield SSEStepUpdate(
                step=ProcessingStep.PARSE_QUERY,
                status=StepStatus.IN_PROGRESS,
                message="Analyzing query with AI",
                progress=20,
                timestamp=datetime.utcnow().isoformat()
            )

            parsed = await self.gemini_agent.parse_query(query)

            yield SSEStepUpdate(
                step=ProcessingStep.PARSE_QUERY,
                status=StepStatus.COMPLETED,
                message="Query analyzed",
                progress=30,
                data={"parsed": parsed},
                timestamp=datetime.utcnow().isoformat()
            )

            yield SSEStepUpdate(
                step=ProcessingStep.EXTRACT_ENTITIES,
                status=StepStatus.IN_PROGRESS,
                message="Extracting container information",
                progress=35,
                timestamp=datetime.utcnow().isoformat()
            )

            container_id = parsed.get("container_id")

            if not container_id:
                yield SSEStepUpdate(
                    step=ProcessingStep.EXTRACT_ENTITIES,
                    status=StepStatus.FAILED,
                    message="Could not find container ID",
                    progress=35,
                    timestamp=datetime.utcnow().isoformat()
                )
                return

            yield SSEStepUpdate(
                step=ProcessingStep.EXTRACT_ENTITIES,
                status=StepStatus.COMPLETED,
                message=f"Found container: {container_id}",
                progress=45,
                data={"container_id": container_id},
                timestamp=datetime.utcnow().isoformat()
            )

            # Step 3: Classify intent
            yield SSEStepUpdate(
                step=ProcessingStep.CLASSIFY_INTENT,
                status=StepStatus.IN_PROGRESS,
                message="Understanding query intent",
                progress=50,
                timestamp=datetime.utcnow().isoformat()
            )

            intent = parsed.get("intent", "get_info")

            yield SSEStepUpdate(
                step=ProcessingStep.CLASSIFY_INTENT,
                status=StepStatus.COMPLETED,
                message=f"Intent: {intent}",
                progress=55,
                data={"intent": intent},
                timestamp=datetime.utcnow().isoformat()
            )

            yield SSEStepUpdate(
                step=ProcessingStep.SELECT_TOOL,
                status=StepStatus.IN_PROGRESS,
                message="Selecting appropriate tool",
                progress=60,
                timestamp=datetime.utcnow().isoformat()
            )

            tool_name = self._map_intent_to_tool(intent)

            yield SSEStepUpdate(
                step=ProcessingStep.SELECT_TOOL,
                status=StepStatus.COMPLETED,
                message=f"Tool selected: {tool_name}",
                progress=65,
                data={"tool": tool_name},
                timestamp=datetime.utcnow().isoformat()
            )

            yield SSEStepUpdate(
                step=ProcessingStep.TRIGGER_WORKFLOW,
                status=StepStatus.IN_PROGRESS,
                message="Starting data collection workflow",
                progress=70,
                timestamp=datetime.utcnow().isoformat()
            )

            result = None;

            yield SSEStepUpdate(
                step=ProcessingStep.TRIGGER_WORKFLOW,
                status=StepStatus.COMPLETED,
                message="Workflow completed",
                progress=95,
                data={
                    "workflow_id": result.workflow_id,
                    "data": result.data
                },
                timestamp=datetime.utcnow().isoformat()
            )

            yield SSEStepUpdate(
                step=ProcessingStep.FORMAT_RESPONSE,
                status=StepStatus.COMPLETED,
                message="Response ready",
                progress=100,
                data=result.data,
                timestamp=datetime.utcnow().isoformat()
            )

        except Exception as e:
            logger.error(f"Stream processing error: {str(e)}", exc_info=True)
            yield SSEStepUpdate(
                step=ProcessingStep.PARSE_QUERY,
                status=StepStatus.FAILED,
                message=str(e),
                progress=0,
                timestamp=datetime.utcnow().isoformat()
            )

    def _map_intent_to_tool(self, intent: str) -> str:
        intent_tool_map = {
            "get_info": "get_container_info",
            "check_availability": "check_container_availability",
            "get_location": "get_container_location",
            "check_holds": "check_container_holds",
            "get_lfd": "get_last_free_day",
        }
        return intent_tool_map.get(intent, "get_container_info")
