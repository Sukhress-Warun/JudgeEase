import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.evaluation_repo import EvaluationRepository
from app.services.llm.OllamaLLMProvider import OllamaLLMProvider
from app.services.llm.base import LLMProvider   
from app.schemas.evaluation import EvaluationCreate, EvaluationSummary
from app.models.evaluation import Evaluation
from uuid import UUID
from app.exceptions.customExceptions.client_exceptions import NotFoundError
from app.schemas.evaluation import EvaluationPut
from app.config.settings import settings

logger = logging.getLogger(__name__)

class EvaluationService:
    def __init__(self, session: AsyncSession):
        self.repo = EvaluationRepository(session)
        self.llm_provider = OllamaLLMProvider(
            model=settings.LLM_MODEL,
            base_url=settings.LLM_BASE_URL,
        )

    async def create_evaluation(self, data: EvaluationCreate) -> Evaluation:
        return await self.repo.create(data)
    
    async def get_evaluation(self, evaluation_id: UUID) -> Evaluation | None:
        res = await self.repo.get(evaluation_id)
        if not res:
            raise NotFoundError(f"Evaluation {evaluation_id} not found")
        return res

    async def get_evaluations_for_contestant(self, contestant_id: str, llm_provider: LLMProvider) -> EvaluationSummary:
        evaluations = await self.repo.get_by_contestant(contestant_id)
        
        summary = None
        summary_error = None

        if evaluations:
            text_lines = []
            for ev in evaluations:
                text_lines.append(f"Judge {ev.judge_id} (Score: {ev.score}): {ev.notes}")
            full_text = "\n".join(text_lines)
            
            try:
                summary = await self.llm_provider.summarize(full_text)
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                summary_error = "Summary generation failed. Please try again later."

        return EvaluationSummary(
            evaluations=evaluations,
            summary=summary,
            summary_error=summary_error
        )
    
    async def update_evaluation(self, evaluation_id: UUID, data: EvaluationPut) -> Evaluation:
        res = await self.repo.update(evaluation_id, data)
        if not res:
            raise NotFoundError(f"Evaluation {evaluation_id} not found")
        return res

    async def delete_evaluation(self, evaluation_id: UUID) -> bool:
        res = await self.repo.delete(evaluation_id)
        if not res:
            raise NotFoundError(f"Evaluation {evaluation_id} not found")
        return res

