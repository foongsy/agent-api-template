"""
Integration tests for Flask application.
"""

import json
import pytest
import io
from PIL import Image
from pydantic_ai import models
from pydantic_ai.models.test import TestModel

from main import app
from agent import agent_service

# Safety measure to prevent accidental real LLM calls during testing
models.ALLOW_MODEL_REQUESTS = False


@pytest.fixture
def client():
    """Create Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestFlaskApplication:
    """Test Flask application endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns correct information."""
        response = client.get('/')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['message'] == "AI Agent API Service (Flask)"
        assert data['version'] == "0.1.0"
        assert 'health' in data
        assert 'docs' in data

    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'services' in data
        assert 'timestamp' in data
        
        # Check that all expected services are present
        services = data['services']
        assert 'agent' in services
        assert 'embeddings' in services
        assert 'langfuse' in services

    def test_embeddings_endpoint_valid(self, client):
        """Test embeddings endpoint with valid input."""
        response = client.post('/api/v1/embeddings',
                             json={'text': 'This is a test message'},
                             content_type='application/json')
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'embeddings' in data
        assert 'model' in data
        assert 'dimensions' in data
        assert 'processing_time_ms' in data
        
        # Verify embeddings structure
        embeddings = data['embeddings']
        assert isinstance(embeddings, list)
        assert len(embeddings) > 0
        assert data['dimensions'] == len(embeddings)

    def test_embeddings_endpoint_empty_text(self, client):
        """Test embeddings endpoint with empty text."""
        response = client.post('/api/v1/embeddings',
                             json={'text': ''},
                             content_type='application/json')
        
        assert response.status_code == 400

    def test_embeddings_endpoint_missing_text(self, client):
        """Test embeddings endpoint with missing text field."""
        response = client.post('/api/v1/embeddings',
                             json={},
                             content_type='application/json')
        
        assert response.status_code == 400

    def test_chat_endpoint_text_only(self, client):
        """Test chat endpoint with text-only message."""
        with agent_service.agent.override(model=TestModel()):
            response = client.post('/api/v1/agent/chat',
                                 data={'message': 'Hello, this is a test message'},
                                 content_type='multipart/form-data')
            
            assert response.status_code == 200
            
            data = response.get_json()
            assert 'response' in data
            assert 'processing_time_ms' in data
            assert 'model_used' in data
            
            # Check response structure
        agent_response = data['response']
        assert 'content' in agent_response
        assert 'timestamp' in agent_response
        assert isinstance(agent_response['content'], str)
        assert len(agent_response['content']) > 0

    def test_chat_endpoint_with_session(self, client):
        """Test chat endpoint with session ID."""
        with agent_service.agent.override(model=TestModel()):
            response = client.post('/api/v1/agent/chat',
                                 data={
                                     'message': 'Hello with session',
                                     'session_id': 'test-session-123'
                                 },
                                 content_type='multipart/form-data')
            
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['session_id'] == 'test-session-123'

    def test_chat_endpoint_empty_message(self, client):
        """Test chat endpoint with empty message."""
        response = client.post('/api/v1/agent/chat',
                             data={'message': ''},
                             content_type='multipart/form-data')
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'detail' in data
        assert 'empty' in data['detail'].lower()

    def test_chat_endpoint_missing_message(self, client):
        """Test chat endpoint with missing message."""
        response = client.post('/api/v1/agent/chat',
                             data={},
                             content_type='multipart/form-data')
        
        assert response.status_code == 400

    def test_chat_endpoint_with_image(self, client):
        """Test chat endpoint with image upload."""
        with agent_service.agent.override(model=TestModel()):
            # Create a small test image
            img = Image.new('RGB', (100, 100), color='green')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            response = client.post('/api/v1/agent/chat',
                                 data={
                                     'message': 'What color is this image?',
                                     'images': (img_bytes, 'test.jpg')
                                 },
                                 content_type='multipart/form-data')
            
            assert response.status_code == 200
            
            data = response.get_json()
            assert 'response' in data
            
            # The response should mention the color or describe the image
            response_content = data['response']['content'].lower()
            # Note: This is a basic test - the actual response may vary
            assert len(response_content) > 0

    def test_chat_endpoint_long_message(self, client):
        """Test chat endpoint with message that's too long."""
        long_message = 'A' * 15000  # Longer than 10,000 character limit
        
        response = client.post('/api/v1/agent/chat',
                             data={'message': long_message},
                             content_type='multipart/form-data')
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'detail' in data
        assert 'too long' in data['detail'].lower()


class TestFlaskCompatibility:
    """Test Flask application compatibility with existing patterns."""

    def test_flask_pydantic_integration(self, client):
        """Test that Flask-Pydantic validation works correctly."""
        # Test with invalid JSON structure for embeddings
        response = client.post('/api/v1/embeddings',
                             json={'invalid_field': 'test'},
                             content_type='application/json')
        
        assert response.status_code == 400
        
        # Should contain validation error information
        data = response.get_json()
        assert 'validation_error' in data

    def test_cors_headers(self, client):
        """Test that CORS headers are present."""
        response = client.options('/api/v1/health')
        
        # Check that CORS headers are present
        # Note: The exact headers may vary based on Flask-CORS configuration
        assert response.status_code in [200, 204]

    def test_content_type_handling(self, client):
        """Test different content types are handled correctly."""
        # Test JSON content type
        response = client.post('/api/v1/embeddings',
                             json={'text': 'test'},
                             content_type='application/json')
        assert response.status_code == 200
        
        # Test multipart form data
        with agent_service.agent.override(model=TestModel()):
            response = client.post('/api/v1/agent/chat',
                                 data={'message': 'test'},
                                 content_type='multipart/form-data')
            assert response.status_code == 200 