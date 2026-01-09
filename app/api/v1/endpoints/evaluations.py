from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.evaluation import EvaluationCreate, EvaluationResponse, EvaluationSummary, EvaluationPut
from app.services.evaluation import EvaluationService
from app.repositories.evaluation_repo import EvaluationRepository
from app.dependencies.dependencies import get_service, get_llm_provider
from app.services.llm.OllamaLLMProvider import OllamaLLMProvider

router = APIRouter()


@router.post("/evaluations", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    evaluation: EvaluationCreate,
    service: EvaluationService = Depends(get_service)
):
    return await service.create_evaluation(evaluation)

@router.get("/evaluations", response_model=EvaluationSummary)
async def get_evaluations(
    contestant_id: str,
    service: EvaluationService = Depends(get_service),
    llm_provider: OllamaLLMProvider = Depends(get_llm_provider)
):
    return await service.get_evaluations_for_contestant(contestant_id, llm_provider)

@router.put("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def update_evaluation(
    evaluation_id: UUID,
    evaluation_update: EvaluationPut,
    service: EvaluationService = Depends(get_service)
):
    return await service.update_evaluation(evaluation_id, evaluation_update)
    

@router.delete("/evaluations/{evaluation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evaluation(
    evaluation_id: UUID,
    service: EvaluationService = Depends(get_service)
):
    return await service.delete_evaluation(evaluation_id)