import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from main import app


def test_health_endpoint():
    """Test the health check endpoint."""
    client = TestClient(app)
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "ready"
    assert "version" in data


@pytest.mark.anyio
async def test_predict_endpoint_success():
    """Test the prediction endpoint with a valid URL without real network."""
    # Mock outbound HEAD to always return 200 and fix randomness
    with patch('main.httpx.AsyncClient') as MockClient, \
         patch('main.random.choice', return_value='normal'), \
         patch('main.random.uniform', return_value=0.2):
        inst = MockClient.return_value.__aenter__.return_value
        inst.head = AsyncMock(return_value=type('Resp', (), {'status_code': 200})())
        async with AsyncClient(app=app, base_url='http://test') as ac:
            response = await ac.post('/predict/', json={'image_url': 'https://example.com/img.jpg'})
        assert response.status_code == 200
        data = response.json()
        assert "diagnosis" in data
        assert "confidence" in data
        assert "model_version" in data
        assert "processing_time" in data
        assert 0.0 <= data["confidence"] <= 1.0


def test_predict_endpoint_invalid_url():
    """Test the prediction endpoint with an invalid URL (fastapi validation)."""
    client = TestClient(app)
    response = client.post("/predict/", json={"image_url": "not-a-valid-url"})
    assert response.status_code == 422  # Validation error


def test_root_endpoint():
    """Test the root endpoint."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "endpoints" in data
