from app.config.settings import settings
from app.services.llm.base import LLMProvider
from app.services.llm.openai_client import OpenAIProvider

class LLMFactory:
    @staticmethod
    def get_provider() -> LLMProvider:
        provider_name = settings.LLM_PROVIDER.lower()
        if provider_name == "openai":
            return OpenAIProvider()
        return OpenAIProvider()
