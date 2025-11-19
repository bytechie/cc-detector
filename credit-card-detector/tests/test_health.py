"""Test the enhanced health endpoint."""
import pytest
import json
from unittest.mock import patch, MagicMock
from claude_subagent.app import _check_presidio_service, health


def test_check_presidio_service_healthy():
    """Test healthy Presidio service check."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = _check_presidio_service("http://localhost:3000", "test-service")

        assert result["name"] == "test-service"
        assert result["status"] == "healthy"
        assert result["url"] == "http://localhost:3000"


def test_check_presidio_service_unhealthy():
    """Test unhealthy Presidio service check."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = _check_presidio_service("http://localhost:3000", "test-service")

        assert result["name"] == "test-service"
        assert result["status"] == "unhealthy"
        assert "HTTP 500" in result["error"]


def test_check_presidio_service_unreachable():
    """Test unreachable Presidio service check."""
    import requests
    with patch('requests.get', side_effect=requests.exceptions.RequestException("Connection refused")):
        result = _check_presidio_service("http://localhost:3000", "test-service")

        assert result["name"] == "test-service"
        assert result["status"] == "unreachable"
        assert "Connection refused" in result["error"]


def test_health_endpoint_with_client():
    """Test health endpoint using Flask test client."""
    from claude_subagent.app import app

    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["service"] == "claude-subagent"
        assert "dependencies" in data
        assert "analyzer" in data["dependencies"]
        assert "anonymizer" in data["dependencies"]