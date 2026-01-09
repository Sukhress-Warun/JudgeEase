from langchain_ollama import ChatOllama
from app.services.llm.base import LLMProvider
from app.config.settings import settings
import asyncio


class OllamaLLMProvider(LLMProvider):
    """
    LLMProvider implementation backed by Ollama via LangChain's ChatOllama.

    This adapter hides vendor-specific HTTP details and exposes
    a simple async interface to the application layer.
    """

    def __init__(
        self,
        model: str,
        base_url: str,
        temperature: float = 0.2,
    ):
        self._llm = ChatOllama(
            model=model,
            base_url=base_url,
            temperature=temperature,
        )

    async def summarize(self, text: str) -> str:
        prompt = (
            "Write a short overall assessment of the contestant based on the following judge evaluations. "
            "Limit it to at most three sentences and do not add introductions or explanations.\n\n"
            f"{text}"
        )
        task = asyncio.to_thread(self._llm.invoke, prompt)
        result = await asyncio.wait_for(task, timeout=10)
        return result.content.strip()