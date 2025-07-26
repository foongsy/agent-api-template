"""
End-to-end tests for the complete API workflow.
"""

import pytest
import io
from PIL import Image
from fastapi.testclient import TestClient

from pydantic_ai import models
from pydantic_ai.models.test import TestModel

from main import app
from agent import agent_service
from embeddings import embedding_service

# Safety measure to prevent accidental real LLM calls during testing
models.ALLOW_MODEL_REQUESTS = False


class TestAPIEndToEnd:
    """End-to-end tests for the complete API workflow."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def test_image_bytes(self):
        """Create test image bytes for testing."""
        img = Image.new('RGB', (100, 100), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()

    def test_complete_api_workflow(self, client, test_image_bytes):
        """Test the complete API workflow: health -> embeddings -> agent chat."""
        with agent_service.agent.override(model=TestModel()):
            # Step 1: Check health
            health_response = client.get("/api/v1/health")
            assert health_response.status_code == 200
            health_data = health_response.json()
            assert health_data["status"] == "healthy"
            
            # Step 2: Test embeddings
            embedding_response = client.post(
                "/api/v1/embeddings",
                json={"text": "This is a test text for embedding"}
            )
            assert embedding_response.status_code == 200
            embedding_data = embedding_response.json()
            assert "embeddings" in embedding_data
            assert "model" in embedding_data
            assert "dimensions" in embedding_data
            assert "processing_time_ms" in embedding_data
            
            # Step 3: Test agent chat with text
            chat_response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Hello, this is a test message."},
                files={}
            )
            assert chat_response.status_code == 200
            chat_data = chat_response.json()
            assert "response" in chat_data
            assert "processing_time_ms" in chat_data
            assert "model_used" in chat_data
            
            # Step 4: Test agent chat with image
            multimodal_response = client.post(
                "/api/v1/agent/chat",
                data={
                    "message": "Describe this image",
                    "image_mime_types": ["image/jpeg"]
                },
                files={"images": ("test.jpg", test_image_bytes, "image/jpeg")}
            )
            assert multimodal_response.status_code == 200
            multimodal_data = multimodal_response.json()
            assert "response" in multimodal_data

    def test_api_endpoints_consistency(self, client):
        """Test that all API endpoints return consistent response structures."""
        with agent_service.agent.override(model=TestModel()):
            # Test health endpoint structure
            health_response = client.get("/api/v1/health")
            assert health_response.status_code == 200
            health_data = health_response.json()
            
            required_health_fields = ["status", "services", "timestamp"]
            for field in required_health_fields:
                assert field in health_data
            
            # Test embeddings endpoint structure
            embedding_response = client.post(
                "/api/v1/embeddings",
                json={"text": "Test text"}
            )
            assert embedding_response.status_code == 200
            embedding_data = embedding_response.json()
            
            required_embedding_fields = ["embeddings", "model", "dimensions", "processing_time_ms"]
            for field in required_embedding_fields:
                assert field in embedding_data
            
            # Test agent chat endpoint structure
            chat_response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Test message"},
                files={}
            )
            assert chat_response.status_code == 200
            chat_data = chat_response.json()
            
            required_chat_fields = ["response", "processing_time_ms", "model_used"]
            for field in required_chat_fields:
                assert field in chat_data

    def test_error_handling_consistency(self, client):
        """Test that error handling is consistent across all endpoints."""
        with agent_service.agent.override(model=TestModel()):
            # Test embeddings with invalid input
            embedding_response = client.post(
                "/api/v1/embeddings",
                json={"text": ""}  # Empty text
            )
            assert embedding_response.status_code == 422  # Validation error
            
            # Test agent chat with invalid input
            chat_response = client.post(
                "/api/v1/agent/chat",
                data={"message": ""},  # Empty message
                files={}
            )
            assert chat_response.status_code == 400  # Validation error

    def test_processing_time_consistency(self, client):
        """Test that processing time is measured consistently across endpoints."""
        with agent_service.agent.override(model=TestModel()):
            # Test embeddings processing time
            embedding_response = client.post(
                "/api/v1/embeddings",
                json={"text": "Test text for processing time"}
            )
            assert embedding_response.status_code == 200
            embedding_data = embedding_response.json()
            
            assert "processing_time_ms" in embedding_data
            embedding_time = embedding_data["processing_time_ms"]
            assert isinstance(embedding_time, (int, float))
            assert embedding_time >= 0
            
            # Test agent chat processing time
            chat_response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Test message for processing time"},
                files={}
            )
            assert chat_response.status_code == 200
            chat_data = chat_response.json()
            
            assert "processing_time_ms" in chat_data
            chat_time = chat_data["processing_time_ms"]
            assert isinstance(chat_time, (int, float))
            assert chat_time >= 0

    def test_multimodal_workflow(self, client, test_image_bytes):
        """Test a complete multimodal workflow."""
        with agent_service.agent.override(model=TestModel()):
            # Step 1: Get embeddings for text
            embedding_response = client.post(
                "/api/v1/embeddings",
                json={"text": "This is a test text for multimodal workflow"}
            )
            assert embedding_response.status_code == 200
            
            # Step 2: Send text + image to agent
            multimodal_response = client.post(
                "/api/v1/agent/chat",
                data={
                    "message": "Analyze this image and provide insights",
                    "image_mime_types": ["image/jpeg"]
                },
                files={"images": ("test.jpg", test_image_bytes, "image/jpeg")}
            )
            assert multimodal_response.status_code == 200
            
            # Step 3: Send follow-up text-only message
            followup_response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Can you elaborate on your previous response?"},
                files={}
            )
            assert followup_response.status_code == 200

    def test_api_documentation_endpoints(self, client):
        """Test that API documentation endpoints are accessible."""
        # Test OpenAPI schema
        schema_response = client.get("/openapi.json")
        assert schema_response.status_code == 200
        
        # Test Swagger UI
        docs_response = client.get("/docs")
        assert docs_response.status_code == 200
        
        # Test ReDoc
        redoc_response = client.get("/redoc")
        assert redoc_response.status_code == 200

    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests to different endpoints."""
        import asyncio
        import concurrent.futures
        
        def make_health_request():
            return client.get("/api/v1/health")
        
        def make_embedding_request():
            return client.post(
                "/api/v1/embeddings",
                json={"text": "Concurrent test text"}
            )
        
        def make_chat_request():
            with agent_service.agent.override(model=TestModel()):
                return client.post(
                    "/api/v1/agent/chat",
                    data={"message": "Concurrent test message"},
                    files={}
                )
        
        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(make_health_request),
                executor.submit(make_embedding_request),
                executor.submit(make_chat_request)
            ]
            
            responses = [future.result() for future in futures]
            
            # All requests should succeed
            for response in responses:
                assert response.status_code in [200, 422]  # 422 for validation errors is acceptable

    def test_large_text_handling(self, client):
        """Test handling of large text inputs."""
        with agent_service.agent.override(model=TestModel()):
            # Test embeddings with large text
            large_text = "This is a large text. " * 400  # ~8.8KB of text (within limit)
            embedding_response = client.post(
                "/api/v1/embeddings",
                json={"text": large_text}
            )
            assert embedding_response.status_code == 200
            
            # Test agent chat with large text
            chat_response = client.post(
                "/api/v1/agent/chat",
                data={"message": large_text},
                files={}
            )
            assert chat_response.status_code == 200

    def test_session_management_workflow(self, client):
        """Test session management workflow."""
        with agent_service.agent.override(model=TestModel()):
            session_id = "test-session-123"
            
            # First message with session
            response1 = client.post(
                "/api/v1/agent/chat",
                data={
                    "message": "Hello, this is my first message",
                    "session_id": session_id
                },
                files={}
            )
            assert response1.status_code == 200
            data1 = response1.json()
            assert data1["session_id"] == session_id
            
            # Second message with same session
            response2 = client.post(
                "/api/v1/agent/chat",
                data={
                    "message": "This is my second message",
                    "session_id": session_id
                },
                files={}
            )
            assert response2.status_code == 200
            data2 = response2.json()
            assert data2["session_id"] == session_id

    def test_error_recovery_workflow(self, client):
        """Test error recovery workflow."""
        with agent_service.agent.override(model=TestModel()):
            # Step 1: Make a valid request
            valid_response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Valid message"},
                files={}
            )
            assert valid_response.status_code == 200
            
            # Step 2: Make an invalid request
            invalid_response = client.post(
                "/api/v1/agent/chat",
                data={"message": ""},  # Empty message
                files={}
            )
            assert invalid_response.status_code == 400
            
            # Step 3: Make another valid request (should recover)
            recovery_response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Recovery message"},
                files={}
            )
            assert recovery_response.status_code == 200

    def test_api_versioning_consistency(self, client):
        """Test that API versioning is consistent."""
        # All endpoints should use /api/v1/ prefix
        endpoints = [
            "/api/v1/health",
            "/api/v1/embeddings",
            "/api/v1/agent/chat"
        ]
        
        for endpoint in endpoints:
            if endpoint == "/api/v1/health":
                response = client.get(endpoint)
            elif endpoint == "/api/v1/embeddings":
                response = client.post(endpoint, json={"text": "test"})
            elif endpoint == "/api/v1/agent/chat":
                with agent_service.agent.override(model=TestModel()):
                    response = client.post(endpoint, data={"message": "test"}, files={})
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404 