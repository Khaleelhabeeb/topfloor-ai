import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health_endpoint():
    """Test that the health endpoint works"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "app is up and running"}


def test_exception_handler_prevents_stack_trace_exposure():
    """
    Test that unhandled exceptions return generic error messages without stack traces.
    Validates: Requirements 8.4
    """
    # Create a test endpoint that raises an exception
    @app.get("/test-error")
    def test_error_endpoint():
        raise ValueError("This is a test error with sensitive information")
    
    response = client.get("/test-error")
    
    # Should return 500 status code
    assert response.status_code == 500
    
    # Response should contain generic error message
    assert "detail" in response.json()
    assert response.json()["detail"] == "An internal server error occurred"
    
    # Response should NOT contain the actual error message or stack trace
    response_text = response.text.lower()
    assert "valueerror" not in response_text
    assert "traceback" not in response_text
    assert "test error with sensitive information" not in response_text
    assert "stack" not in response_text


def test_cors_middleware_configured():
    """Test that CORS middleware is configured"""
    # Test with a simple GET request to check CORS headers
    response = client.get("/", headers={"Origin": "http://localhost:3000"})
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "*"
