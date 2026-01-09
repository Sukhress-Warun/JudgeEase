import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from app.exceptions.customExceptions.client_exceptions import CustomException
from sqlalchemy.exc import SQLAlchemyError
from app.dependencies.dependencies import get_service, get_llm_provider
from app.main import app
from app.services.llm.base import LLMProvider

# Mock Service for DB Failure
class MockServiceDBFailure:
    async def create_evaluation(self, *args, **kwargs):
        raise SQLAlchemyError("Simulated DB Failure")

    async def get_evaluations_for_contestant(self, *args, **kwargs):
        raise SQLAlchemyError("Simulated DB Failure")

@pytest.mark.asyncio
async def test_api_create_evaluation_db_error(client: AsyncClient):
    app.dependency_overrides[get_service] = lambda: MockServiceDBFailure()
    
    payload = {"contestant_id": "c1", "judge_id": "j1", "score": 85, "notes": "Good"}
    response = await client.post("/api/v1/evaluations", json=payload)
    
    app.dependency_overrides = {}

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Database Error"

@pytest.mark.asyncio
async def test_api_get_evaluations_db_error(client: AsyncClient):
    app.dependency_overrides[get_service] = lambda: MockServiceDBFailure()
    
    response = await client.get("/api/v1/evaluations?contestant_id=c1")
    
    app.dependency_overrides = {}

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Database Error"


# Mock LLM for API Failure
class MockLLMFailure(LLMProvider):
    async def summarize(self, text: str) -> str:
        raise Exception("LLM Service Unavailable")

@pytest.mark.asyncio
async def test_api_get_evaluations_llm_error(client: AsyncClient):
    app.dependency_overrides[get_llm_provider] = lambda: MockLLMFailure()
    
    payload = {"contestant_id": "c_fail", "judge_id": "j1", "score": 90, "notes": "Test"}
    create_resp = await client.post("/api/v1/evaluations", json=payload)
    assert create_resp.status_code == 201

    response = await client.get("/api/v1/evaluations?contestant_id=c_fail")
    
    app.dependency_overrides = {}
    assert response.status_code == 200
    data = response.json()
    assert len(data["evaluations"]) == 1
    assert data["summary"] is None
    assert data["summary_error"] == "LLM generation failed"

@pytest.mark.asyncio
async def test_api_both_db_and_llm_error(client: AsyncClient):
    app.dependency_overrides[get_service] = lambda: MockServiceDBFailure()
    app.dependency_overrides[get_llm_provider] = lambda: MockLLMFailure()

    response = await client.get("/api/v1/evaluations?contestant_id=c1")
    
    app.dependency_overrides = {} 

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Database Error"
