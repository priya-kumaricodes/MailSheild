"""Tests for the health check endpoint.
"""

def test_health_check_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["backend"] is True
    assert data["database"] is True
    assert data["model_loaded"] is True
    assert "logistic_regression" in data["active_models"]
    assert data["status"] == "healthy"
