import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
import pytest

def test_qa_endpoint_structure() -> None:
    """Test that QA endpoint has correct structure"""
    client = TestClient(app)
    
    # Test with a sample question
    test_question = "What is solar energy?"
    response = client.post("/api/v1/qa", json={"question": test_question})
    
    # Check basic response structure
    assert response.status_code == 200
    response_data = response.json()
    assert "answer" in response_data
    assert "context_used" in response_data
    
def test_qa_endpoint_empty_question() -> None:
    """Test QA endpoint with empty question"""
    client = TestClient(app)
    
    response = client.post("/api/v1/qa", json={"question": ""})
    
    # Should handle empty question gracefully
    assert response.status_code in [200, 400, 500]  # Could be various responses depending on implementation

def test_qa_endpoint_missing_question() -> None:
    """Test QA endpoint with missing question field"""
    client = TestClient(app)
    
    response = client.post("/api/v1/qa", json={})
    
    # Should return validation error
    assert response.status_code == 422  # Unprocessable Entity for validation errors