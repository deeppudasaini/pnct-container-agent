import json
from typing import Dict, Any, Optional, List
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import re
import os
import asyncio

from app.layers.ai_agent.schemas.output_schema import ContainerParseSchema
from app.layers.mcp.clients.workflow_client import WorkflowClient
from app.layers.mcp.registry.tool_registry import ToolRegistry
from app.shared.config.settings.base import get_settings
from app.shared.utils.logger import get_logger
from app.layers.ai_agent.agent.base_agent import BaseAgent
from app.layers.ai_agent.prompts.system_prompts import SYSTEM_INSTRUCTION, PARSER_INSTRUCTION

settings = get_settings()
logger = get_logger(__name__)


class GeminiAgent(BaseAgent):
    async def generate_response(self, data: Dict[str, Any]) -> str:
        pass

    tool_agent: LlmAgent = None
    parser_agent: LlmAgent = None
    tool_registry: ToolRegistry = None
    workflow_client: WorkflowClient = None

    def __init__(self):
        if not os.environ.get('GOOGLE_API_KEY'):
            os.environ['GOOGLE_API_KEY'] = settings.GOOGLE_API_KEY
            logger.info("Google API key set from settings")

        # Initialize workflow client and tool registry
        self.workflow_client = WorkflowClient()
        self.tool_registry = ToolRegistry()
        self.tool_registry.initialize_with_workflow_client(self.workflow_client)

        # Get registered tools
        tools = self.tool_registry.get_all_tools()
        tool_names = self.tool_registry.list_tool_names()
        logger.info(f"Available tools: {tool_names}")

        # Tool Agent - calls tools and retrieves data
        self.tool_agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="tool_agent",
            description="Agent that extracts container IDs, determines intent, and calls appropriate tools",
            instruction=SYSTEM_INSTRUCTION,
            tools=tools,
        )

        # Parser Agent - structures tool results into ContainerParseSchema
        self.parser_agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="parser_agent",
            description="Agent that parses tool results into structured ContainerParseSchema JSON",
            instruction=PARSER_INSTRUCTION,
            tools=[],  # No tools for parser
        )

        logger.info(f"Gemini agents initialized")
        logger.info(f"Tool agent: {len(tools)} tools registered")
        logger.info(f"Parser agent: JSON output mode enabled")

    def list_available_tools(self) -> List[str]:
        """List all available tool names"""
        return self.tool_registry.list_tool_names()

    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """Get metadata for a specific tool"""
        return self.tool_registry.get_tool_metadata(tool_name)

    async def get_agent(self):
        """Get the tool agent instance"""
        return self.tool_agent

    async def setup_agent(self):
        pass

    async def parse_query(self, query: str) -> ContainerParseSchema:
        logger.info(f"Starting two-agent pipeline for query: {query}")

        session_service = InMemorySessionService()
        await session_service.create_session(
            app_name=settings.APP_NAME,
            user_id="sequential_user",
            session_id="sequential_session"
        )

        sequential_agent = SequentialAgent(
            name="container_pipeline",
            sub_agents=[self.tool_agent, self.parser_agent],
            description="Two-stage pipeline: tool calling → JSON parsing"
        )

        runner = Runner(
            agent=sequential_agent,
            app_name=settings.APP_NAME,
            session_service=session_service
        )

        content = types.Content(
            role="user",
            parts=[types.Part(text=query)]
        )

        events = runner.run(
            user_id="sequential_user",
            session_id="sequential_session",
            new_message=content
        )

        tool_agent_response = None
        parser_agent_response = None
        final_schema = None

        for event in events:
            logger.debug(f"Event: {type(event).__name__}")

            if event.is_final_response() and event.content:
                raw_text = "".join([p.text for p in event.content.parts if p.text]).strip()

                try:
                    parsed = self.sanitize_response(raw_text)
                    final_schema = parsed
                    logger.info(
                        f"Successfully parsed response from {event.agent_name if hasattr(event, 'agent_name') else 'agent'}")
                except Exception as e:
                    logger.debug(f"Response not parseable as schema (this is OK for tool agent): {e}")
                    if tool_agent_response is None:
                        tool_agent_response = raw_text

        if final_schema is None:
            logger.error("Pipeline failed to produce valid ContainerParseSchema")
            logger.error(f"Tool agent response: {tool_agent_response[:500] if tool_agent_response else 'None'}")

            return ContainerParseSchema(
                message=tool_agent_response if len(tool_agent_response)>0 else "I apologize, but I encountered an error processing your request. Please try again or contact support.",
                has_errors=True,
                error_message="Failed to parse agent pipeline output into valid schema"
            )

        if not final_schema.message:
            final_schema.message = self._generate_default_message(final_schema)
            logger.info(f"Generated default message: {final_schema.message}")

        logger.info(
            f"Pipeline completed successfully. Container: {final_schema.container_id}, Intent: {final_schema.intent}")
        return final_schema

    def _generate_default_message(self, schema: ContainerParseSchema) -> str:

        if schema.has_errors:
            return schema.error_message or "An error occurred while processing your request."

        if not schema.container_id:
            return "Please provide a container number to track."

        container_id = schema.container_id

        if schema.container_data:
            data = schema.container_data

            msg_parts = [f"Container {container_id}"]

            if data.available is not None:
                if data.available:
                    msg_parts.append("is available for pickup")
                else:
                    msg_parts.append("is not currently available")

            if data.location:
                msg_parts.append(f"at location {data.location}")

            if data.has_holds and data.holds:
                holds_str = ", ".join(data.holds)
                msg_parts.append(f"with holds: {holds_str}")

            if data.last_free_day:
                msg_parts.append(f"(LFD: {data.last_free_day})")

            return ". ".join(msg_parts) + "."

        if schema.intent == "check_availability":
            return f"Retrieved availability status for container {container_id}."
        elif schema.intent == "get_location":
            return f"Retrieved location information for container {container_id}."
        elif schema.intent == "check_holds":
            return f"Checked holds for container {container_id}."
        elif schema.intent == "get_lfd":
            return f"Retrieved last free day information for container {container_id}."
        else:
            return f"Retrieved information for container {container_id}."

    def sanitize_response(self, raw_response: str) -> ContainerParseSchema:
        match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", raw_response, re.IGNORECASE)
        if match:
            json_str = match.group(1)
        else:
            json_match = re.search(r'\{[\s\S]*\}', raw_response)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = raw_response.strip()

        try:
            data = json.loads(json_str)

            parsed_schema = ContainerParseSchema(**data)

            logger.debug(f"Successfully created ContainerParseSchema")
            return parsed_schema

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Attempted to parse: {json_str[:500]}")
            raise ValueError(f"Invalid JSON in response: {e}")

        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            logger.error(
                f"Data that failed validation: {json.dumps(data, indent=2)[:500] if 'data' in locals() else 'N/A'}")
            raise ValueError(f"Failed to create ContainerParseSchema: {e}")

    def get_schema_dict(self, schema: ContainerParseSchema) -> Dict[str, Any]:
        if hasattr(schema, 'model_dump'):
            return schema.model_dump()
        elif hasattr(schema, 'dict'):
            return schema.dict()
        else:
            return schema.__dict__

    def get_message_from_schema(self, schema: ContainerParseSchema) -> Optional[str]:

        if schema is None:
            return "No data available."

        if hasattr(schema, 'message') and schema.message:
            return schema.message

        schema_dict = self.get_schema_dict(schema)
        message = schema_dict.get('message')

        if message:
            return message

        return self._generate_default_message(schema)

    async def parse_raw_data(self, data: Dict[str, Any]) -> ContainerParseSchema:
        return await self.execute_parser_agent(data)

    async def execute_parser_agent(self, data: Dict[str, Any]) -> ContainerParseSchema:
        logger.info("Executing standalone parser agent")

        parsing_prompt = f"""Parse this data into ContainerParseSchema format.

Query: {data.get('query', 'N/A')}
Tool Response: {data.get('raw_response', 'N/A')}
Additional Context: {json.dumps({k: v for k, v in data.items() if k not in ['query', 'raw_response']}, indent=2)}

Output valid JSON matching ContainerParseSchema. Include a helpful message field."""

        session_service = InMemorySessionService()
        await session_service.create_session(
            app_name=settings.APP_NAME,
            user_id="parser_user",
            session_id="parser_session"
        )

        runner = Runner(
            agent=self.parser_agent,
            app_name=settings.APP_NAME,
            session_service=session_service
        )

        content = types.Content(
            role="user",
            parts=[types.Part(text=parsing_prompt)]
        )

        events = runner.run(
            user_id="parser_user",
            session_id="parser_session",
            new_message=content
        )

        final_data = None
        for event in events:
            if event.is_final_response() and event.content:
                raw_data = "".join([p.text for p in event.content.parts if p.text]).strip()
                try:
                    final_data = self.sanitize_response(raw_data)
                    break
                except Exception as e:
                    logger.error(f"Parser failed: {e}")
                    continue

        if final_data is None:
            raise ValueError("Parser agent failed to produce valid output")

        if not final_data.message:
            final_data.message = self._generate_default_message(final_data)

        return final_data
