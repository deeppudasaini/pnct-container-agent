import json
from typing import Dict, Any, Optional, List

from google.api_core.client_options import ClientOptions
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from app.layers.ai_agent.schemas.output_schema import ContainerParseSchema
from app.layers.mcp.clients import workflow_client
from app.layers.mcp.clients.workflow_client import WorkflowClient
from app.layers.mcp.registry.tool_registry import ToolRegistry

from app.shared.config.settings.base import get_settings
from app.shared.utils.logger import get_logger
from app.layers.ai_agent.agent.base_agent import BaseAgent
from app.layers.ai_agent.prompts.system_prompts import QUERY_PARSING_PROMPT, SYSTEM_INSTRUCTION
import os
settings = get_settings()
logger = get_logger(__name__)


class GeminiAgent(BaseAgent):

    container_agent: LlmAgent = None
    tool_registry: ToolRegistry = None
    workflow_client: WorkflowClient = None

    def __init__(self):
        if not os.environ.get('GOOGLE_API_KEY'):
            os.environ['GOOGLE_API_KEY'] = settings.GOOGLE_API_KEY
            logger.info("Google API key set from settings")
        self.workflow_client = WorkflowClient()
        self.tool_registry = ToolRegistry()
        self.tool_registry.initialize_with_workflow_client(self.workflow_client)
        tools = self.tool_registry.get_all_tools()
        tool_names = self.tool_registry.list_tool_names()
        logger.info(f"Available tools: {tool_names}")

        self.container_agent = LlmAgent(
            model="gemini-2.0-flash",
            name="container_agent",
            description="Container management agent for retrieving information, checking availability, locations, holds, and last free days",
            instruction=SYSTEM_INSTRUCTION,
            tools=tools,
            output_schema=ContainerParseSchema
        )

        logger.info(f"Gemini agent initialized with model: {settings.GOOGLE_MODEL}")
        logger.info(f"Registered {len(tools)} tools: {', '.join(tool_names)}")

    def list_available_tools(self) -> List[str]:
        return self.tool_registry.list_tool_names()

    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        return self.tool_registry.get_tool_metadata(tool_name)

    async def get_agent(self):
        return self.container_agent

    async def setup_agent(self):
        pass

    async def parse_query(self, query: str) -> Dict[str, Any]:
        try:
            prompt = QUERY_PARSING_PROMPT.format(query=query)
            logger.info("Sending query to Gemini for parsing")

            session_service = InMemorySessionService()
            await session_service.create_session(
                app_name=settings.APP_NAME,
                user_id="user",
                session_id="session"
            )
            runner = Runner(
                agent=self.container_agent,
                app_name=settings.APP_NAME,
                session_service=session_service,
            )

            content = types.Content(role="user", parts=[types.Part(text=prompt)])

            events = runner.run(user_id="user", session_id="session", new_message=content)

            for event in events:

                if event.is_final_response() and event.content:
                    final_answer = event.content.parts[0].text.strip()
                    print("WHAT IS FINAL ANSWER:::"+final_answer)

            raise ValueError("No final response received")

        except Exception as e:
            logger.error(f"Gemini parsing error: {str(e)}", exc_info=True)
            raise

    async def generate_response(self, data: Dict[str, Any]) -> str:
        try:
            prompt = f"""
Given the following container data, generate a natural, conversational response:

Data: {data}

Generate a clear, concise response that a person would understand.
"""
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}", exc_info=True)
            return "I found the container information, but had trouble formatting the response."


