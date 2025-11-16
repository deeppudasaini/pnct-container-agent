import google.genai as genai
from typing import Dict, Any
from app.shared.config.settings.base import get_settings
from app.shared.utils.logger import get_logger
from app.layers.ai_agent.agent.base_agent import BaseAgent
from app.layers.ai_agent.prompts.system_prompts import QUERY_PARSING_PROMPT

settings = get_settings()
logger = get_logger(__name__)

class GeminiAgent(BaseAgent):
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=settings.GOOGLE_MODEL,
            generation_config={
                "temperature": settings.GOOGLE_TEMPERATURE,
                "max_output_tokens": settings.GOOGLE_MAX_TOKENS,
            }
        )
        logger.info(f"Gemini agent initialized with model: {settings.GOOGLE_MODEL}")

    async def parse_query(self, query: str) -> Dict[str, Any]:
        try:
            prompt = QUERY_PARSING_PROMPT.format(query=query)
            logger.info("Sending query to Gemini for parsing")
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            import json
            result = json.loads(result_text)
            logger.info(
                "Query parsed successfully",
                container_id=result.get("container_id"),
                intent=result.get("intent")
            )
            return result
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
