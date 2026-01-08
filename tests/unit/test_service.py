import pytest
import uuid
import datetime
from unittest.mock import AsyncMock, MagicMock
from app.services.evaluation import EvaluationService
from app.schemas.evaluation import EvaluationCreate

@pytest.mark.asyncio
async def test_create_evaluation():
    mock_session = AsyncMock()
    service = EvaluationService(mock_session)
    service.repo = AsyncMock()
    

    payload = EvaluationCreate(contestant_id="c1", judge_id="j1", score=90, notes="Good")
    
    await service.create_evaluation(payload)
    
    service.repo.create.assert_called_once_with(payload)

@pytest.mark.asyncio
async def test_get_evaluations_summary_generation():
    mock_session = AsyncMock()
    service = EvaluationService(mock_session)
    
    mock_eval = MagicMock()
    mock_eval.id = uuid.uuid4()
    mock_eval.contestant_id = "c1"  
    mock_eval.judge_id = "j1"
    mock_eval.score = 90
    mock_eval.notes = "Good"
    mock_eval.created_at = datetime.datetime.now()
    mock_eval.updated_at = datetime.datetime.now()
    
    service.repo = AsyncMock()
    service.repo.get_by_contestant.return_value = [mock_eval]
    
    mock_provider_arg = AsyncMock()
    mock_provider_arg.summarize.return_value = "Summary"

    result = await service.get_evaluations_for_contestant("c1", mock_provider_arg)

    assert result.summary == "Summary"
    mock_provider_arg.summarize.assert_called_once()
