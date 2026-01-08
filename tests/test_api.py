import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_evaluation(client: AsyncClient):
    payload = {
        "contestant_id": "c1",
        "judge_id": "j1",
        "score": 85,
        "notes": "Good performance"
    }
    response = await client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["contestant_id"] == "c1"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_evaluations_with_summary(client: AsyncClient):
    # Create two evaluations
    payload1 = {"contestant_id": "c2", "judge_id": "j1", "score": 80, "notes": "Solid"}
    payload2 = {"contestant_id": "c2", "judge_id": "j2", "score": 90, "notes": "Excellent"}
    await client.post("/api/v1/evaluations", json=payload1)
    await client.post("/api/v1/evaluations", json=payload2)

    response = await client.get("/api/v1/evaluations?contestant_id=c2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["evaluations"]) == 2
    assert data["summary"] == "Mock Summary"  

@pytest.mark.asyncio
async def test_update_evaluation(client: AsyncClient):
    # Create
    create_payload = {"contestant_id": "c3", "judge_id": "j1", "score": 70, "notes": "Okay"}
    create_resp = await client.post("/api/v1/evaluations", json=create_payload)
    eval_id = create_resp.json()["id"]

    # Update
    update_payload = {"contestant_id": "c3", "judge_id": "j1", "score": 75, "notes": "Better"}
    response = await client.put(f"/api/v1/evaluations/{eval_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["score"] == 75

@pytest.mark.asyncio
async def test_delete_evaluation(client: AsyncClient):
    # Create
    create_payload = {"contestant_id": "c4", "judge_id": "j1", "score": 60, "notes": "Pass"}
    create_resp = await client.post("/api/v1/evaluations", json=create_payload)
    eval_id = create_resp.json()["id"]

    # Delete
    response = await client.delete(f"/api/v1/evaluations/{eval_id}")
    assert response.status_code == 204

    # Verify connection
    get_resp = await client.put(f"/api/v1/evaluations/{eval_id}", json=create_payload)
    assert get_resp.status_code == 404
