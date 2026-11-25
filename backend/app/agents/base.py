import logging
from typing import Any
from app.config import settings

logger = logging.getLogger(__name__)

def get_llm(temperature: float = 0.0) -> Any:
    """
    Returns an initialized LangChain ChatOpenAI instance if installed and configured.
    Falls back gracefully if running in a lightweight local test environment.
    """
    api_key = settings.OPENAI_API_KEY
    if api_key and "mock" not in api_key.lower():
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.PRIMARY_LLM_MODEL,
                temperature=temperature,
                api_key=api_key
            )
        except ImportError:
            logger.info("langchain_openai not installed; falling back to mock LLM mode.")
    
    # Lightweight Mock LLM for local testing and deterministic execution
    class MockStructuredLLM:
        def __init__(self, schema):
            self.schema = schema

        async def ainvoke(self, prompt):
            # Returns an empty or default instance of the Pydantic schema
            from app.agents.extraction_agent import heuristic_extract_profile
            raw_text = prompt[1]["content"] if len(prompt) > 1 else ""
            return heuristic_extract_profile(raw_text)

    class MockChatModel:
        def with_structured_output(self, schema):
            return MockStructuredLLM(schema)

        async def ainvoke(self, prompt):
            return "Mock model output"

    return MockChatModel()
