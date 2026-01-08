import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.evaluation import EvaluationService
from app.schemas.evaluation import EvaluationCreate

@pytest.mark.asyncio
async def test_create_evaluation():
    # Mock dependencies
    mock_session = AsyncMock()
    service = EvaluationService(mock_session)
    service.repo = AsyncMock()
    service.llm_provider = AsyncMock()

    # Input
    payload = EvaluationCreate(contestant_id="c1", judge_id="j1", score=90, notes="Good")
    
    # Execution
    await service.create_evaluation(payload)
    
    # Assert
    service.repo.create.assert_called_once_with(payload)

@pytest.mark.asyncio
async def test_get_evaluations_summary_generation():
    mock_session = AsyncMock()
    service = EvaluationService(mock_session)
    
    # Mock Repository Return
    mock_eval = MagicMock()
    mock_eval.judge_id = "j1"
    mock_eval.score = 90
    mock_eval.notes = "Good"
    service.repo = AsyncMock()
    service.repo.get_by_contestant.return_value = [mock_eval]
    
    # Mock LLM
    service.llm_provider = AsyncMock()
    service.llm_provider.summarize.return_value = "Summary"

    # Execution
    result = await service.get_evaluations_for_contestant("c1")

    # Assert
    assert result.summary == "Summary"
    service.llm_provider.summarize.assert_called_once()
