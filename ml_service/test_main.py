import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "ready"
    assert "version" in data


def test_predict_endpoint_success():
    """Test the prediction endpoint with a valid URL."""
    payload = {
        "image_url": "https://example.com/dog.jpg"
    }
    response = client.post("/predict/", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "breed" in data
    assert "confidence" in data
    assert "model_version" in data
    assert "processing_time" in data
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["model_version"] == "v1.0"


def test_predict_endpoint_invalid_url():
    """Test the prediction endpoint with an invalid URL."""
    payload = {
        "image_url": "not-a-valid-url"
    }
    response = client.post("/predict/", json=payload)
    assert response.status_code == 422  # Validation error


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "endpoints" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
