import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from app.services.evaluation import EvaluationService
from app.schemas.evaluation import EvaluationCreate

@pytest.mark.asyncio
async def test_create_evaluation_db_failure():
    mock_session = AsyncMock()
    service = EvaluationService(mock_session)
    service.repo = AsyncMock()
    service.repo.create.side_effect = SQLAlchemyError("DB Connection Error")

    payload = EvaluationCreate(contestant_id="c1", judge_id="j1", score=90, notes="Good")

    with pytest.raises(SQLAlchemyError):
        await service.create_evaluation(payload)

@pytest.mark.asyncio
async def test_get_evaluations_llm_failure():
    mock_session = AsyncMock()
    service = EvaluationService(mock_session)
    
    mock_eval = MagicMock()
    mock_eval.id = uuid.uuid4()
    mock_eval.contestant_id = "c1"
    mock_eval.judge_id = "j1"
    mock_eval.score = 90
    mock_eval.notes = "Good"
    mock_eval.created_at = datetime.utcnow()
    mock_eval.updated_at = datetime.utcnow()

    service.repo = AsyncMock()
    service.repo.get_by_contestant.return_value = [mock_eval]
    
    mock_provider = AsyncMock()
    mock_provider.summarize.side_effect = Exception("LLM Timeout")

    result = await service.get_evaluations_for_contestant("c1", mock_provider)

    assert len(result.evaluations) == 1
    assert result.evaluations[0].judge_id == "j1"
    assert result.summary is None
    assert result.summary_error == "LLM Timeout"

@pytest.mark.asyncio
async def test_get_evaluations_llm_timeout():
    mock_session = AsyncMock()
    service = EvaluationService(mock_session)
    
    mock_eval = MagicMock()
    mock_eval.id = uuid.uuid4()
    mock_eval.contestant_id = "c1"
    mock_eval.judge_id = "j1"
    mock_eval.score = 90
    mock_eval.notes = "Good"
    mock_eval.created_at = datetime.utcnow()
    mock_eval.updated_at = datetime.utcnow()

    service.repo = AsyncMock()
    service.repo.get_by_contestant.return_value = [mock_eval]
    
    mock_provider = AsyncMock()
    mock_provider.summarize.side_effect = TimeoutError("Connection timed out")

    result = await service.get_evaluations_for_contestant("c1", mock_provider)

    assert len(result.evaluations) == 1
    assert result.evaluations[0].judge_id == "j1"
    assert result.summary is None
    assert "Connection timed out" in str(result.summary_error)
