"""
Tests for health routes.
"""

import pytest
from fastapi.testclient import TestClient
from app import create_app

# Create a test client
app = create_app()
client = TestClient(app)

def test_health_check():
    """
    Test the health check endpoint.
    """
    response = client.get("/api/v1/health/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "version" in response.json()
    assert "elevenlabs_api_key_set" in response.json()
    assert "twilio_account_sid_set" in response.json()

def test_service_status():
    """
    Test the service status endpoint.
    """
    response = client.get("/api/v1/health/status")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "active_calls" in response.json()
    assert "restaurants" in response.json()

def test_metrics():
    """
    Test the metrics endpoint.
    """
    response = client.get("/api/v1/health/metrics")
    assert response.status_code == 200
    assert "overall" in response.json()
    assert "restaurants" in response.json()
    assert "total_calls" in response.json()["overall"]
