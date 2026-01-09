from app.services.evaluation import EvaluationService
from app.db.session import get_db
from app.services.llm.OllamaLLMProvider import OllamaLLMProvider
from app.config.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


def get_llm_provider() -> OllamaLLMProvider:
    return OllamaLLMProvider(
        model=settings.LLM_MODEL,
        base_url=settings.LLM_BASE_URL,
    )


def get_service(session: AsyncSession = Depends(get_db)) -> EvaluationService:
    return EvaluationService(session)