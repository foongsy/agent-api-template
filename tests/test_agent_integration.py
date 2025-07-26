"""
Integration tests for agent API endpoints using FastAPI TestClient.
"""

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from pydantic_ai import models
from pydantic_ai.models.test import TestModel

from agent import agent_service
from main import app

# Safety measure to prevent accidental real LLM calls during testing
models.ALLOW_MODEL_REQUESTS = False


class TestAgentAPI:
    """Integration tests for agent API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def test_image_bytes(self):
        """Create test image bytes for testing."""
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        return img_bytes.getvalue()

    @pytest.fixture
    def test_png_bytes(self):
        """Create test PNG image bytes for testing."""
        img = Image.new("RGB", (100, 100), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        return img_bytes.getvalue()

    def test_health_endpoint(self, client):
        """Test the health endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        assert "timestamp" in data

    def test_agent_chat_text_only(self, client):
        """Test agent chat endpoint with text-only input."""
        with agent_service.agent.override(model=TestModel()):
            response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Hello, this is a test message."},
                files={},
            )

            assert response.status_code == 200
            data = response.json()

            assert "response" in data
            assert "processing_time_ms" in data
            assert "model_used" in data

            response_data = data["response"]
            assert "content" in response_data
            assert "timestamp" in response_data

    def test_agent_chat_with_image(self, client, test_image_bytes):
        """Test agent chat endpoint with image input."""
        with agent_service.agent.override(model=TestModel()):
            response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Describe this image"},
                files={"images": ("test.jpg", test_image_bytes, "image/jpeg")},
            )

            assert response.status_code == 200
            data = response.json()

            assert "response" in data
            assert "processing_time_ms" in data
            assert "model_used" in data

    def test_agent_chat_multiple_images(self, client, test_image_bytes, test_png_bytes):
        """Test agent chat endpoint with multiple images."""
        with agent_service.agent.override(model=TestModel()):
            response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Compare these images"},
                files=[
                    ("images", ("test1.jpg", test_image_bytes, "image/jpeg")),
                    ("images", ("test2.png", test_png_bytes, "image/png")),
                ],
            )

            assert response.status_code == 200
            data = response.json()

            assert "response" in data
            assert "processing_time_ms" in data
            assert "model_used" in data

    def test_agent_chat_empty_message(self, client):
        """Test agent chat endpoint with empty message."""
        with agent_service.agent.override(model=TestModel()):
            response = client.post("/api/v1/agent/chat", data={"message": ""}, files={})

            assert response.status_code == 400  # Validation error

    def test_agent_chat_missing_message(self, client):
        """Test agent chat endpoint with missing message."""
        with agent_service.agent.override(model=TestModel()):
            response = client.post("/api/v1/agent/chat", data={}, files={})

            assert (
                response.status_code == 422
            )  # Validation error (missing required field)

    def test_agent_chat_invalid_image_format(self, client):
        """Test agent chat endpoint with invalid image format."""
        with agent_service.agent.override(model=TestModel()):
            # Create a fake image with invalid format
            fake_image = b"fake_image_data"

            response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Test message"},
                files={"images": ("test.bmp", fake_image, "image/bmp")},
            )

            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "Unsupported image format" in data["detail"]

    def test_agent_chat_image_size_exceeded(self, client):
        """Test agent chat endpoint with oversized image."""
        with agent_service.agent.override(model=TestModel()):
            # Create a large image that exceeds 8MB
            large_image = b"x" * (9 * 1024 * 1024)  # 9MB

            response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Test message"},
                files={"images": ("large.jpg", large_image, "image/jpeg")},
            )

            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "exceeds maximum size" in data["detail"]

    def test_agent_chat_mismatched_image_counts(self, client, test_image_bytes):
        """Test agent chat endpoint with mismatched image and MIME type counts."""
        with agent_service.agent.override(model=TestModel()):
            # This test is not applicable since the API doesn't accept image_mime_types as form data
            # The MIME types come from the uploaded files themselves
            # We'll test with multiple files instead
            response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Test message"},
                files=[
                    ("images", ("test1.jpg", test_image_bytes, "image/jpeg")),
                    ("images", ("test2.png", test_image_bytes, "image/png")),
                ],
            )

            assert response.status_code == 200
            data = response.json()
            assert "response" in data

    def test_agent_chat_with_session_id(self, client):
        """Test agent chat endpoint with session ID."""
        with agent_service.agent.override(model=TestModel()):
            response = client.post(
                "/api/v1/agent/chat",
                data={
                    "message": "Hello, this is a test message.",
                    "session_id": "test-session-123",
                },
                files={},
            )

            assert response.status_code == 200
            data = response.json()

            assert "response" in data
            assert "session_id" in data
            assert data["session_id"] == "test-session-123"

    def test_agent_chat_response_structure(self, client):
        """Test that agent chat responses have the correct structure."""
        with agent_service.agent.override(model=TestModel()):
            response = client.post(
                "/api/v1/agent/chat", data={"message": "Test message"}, files={}
            )

            assert response.status_code == 200
            data = response.json()

            # Check top-level fields
            required_fields = ["response", "processing_time_ms", "model_used"]
            for field in required_fields:
                assert field in data

            # Check response structure
            response_data = data["response"]
            required_response_fields = [
                "content",
                "confidence",
                "reasoning",
                "timestamp",
            ]
            for field in required_response_fields:
                assert field in response_data

            # Check types
            assert isinstance(data["processing_time_ms"], (int, float))
            assert isinstance(data["model_used"], str)
            assert isinstance(response_data["content"], str)
            assert isinstance(response_data["timestamp"], str)

    def test_agent_chat_error_handling(self, client):
        """Test error handling in agent chat endpoint."""
        with agent_service.agent.override(model=TestModel()):
            # Test with very long message
            long_message = "x" * 10001  # Exceeds 10000 character limit

            response = client.post(
                "/api/v1/agent/chat", data={"message": long_message}, files={}
            )

            assert response.status_code == 400  # Validation error

    def test_agent_chat_with_gif_format(self, client):
        """Test agent chat endpoint with GIF format."""
        with agent_service.agent.override(model=TestModel()):
            # Create a simple GIF-like data
            gif_data = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00;"

            response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Test GIF"},
                files={"images": ("test.gif", gif_data, "image/gif")},
            )

            assert response.status_code == 200
            data = response.json()
            assert "response" in data

    def test_agent_chat_multipart_form_data(self, client, test_image_bytes):
        """Test that multipart form data is handled correctly."""
        with agent_service.agent.override(model=TestModel()):
            response = client.post(
                "/api/v1/agent/chat",
                data={"message": "Test multipart", "session_id": "test-session"},
                files={"images": ("test.jpg", test_image_bytes, "image/jpeg")},
            )

            assert response.status_code == 200
            data = response.json()

            assert data["session_id"] == "test-session"
            assert "response" in data

    def test_agent_chat_processing_time_measurement(self, client):
        """Test that processing time is measured and returned."""
        with agent_service.agent.override(model=TestModel()):
            response = client.post(
                "/api/v1/agent/chat", data={"message": "Test processing time"}, files={}
            )

            assert response.status_code == 200
            data = response.json()

            assert "processing_time_ms" in data
            processing_time = data["processing_time_ms"]
            assert isinstance(processing_time, (int, float))
            assert processing_time >= 0  # Should be non-negative

    def test_agent_chat_model_used_field(self, client):
        """Test that the model_used field is populated correctly."""
        with agent_service.agent.override(model=TestModel()):
            response = client.post(
                "/api/v1/agent/chat", data={"message": "Test model field"}, files={}
            )

            assert response.status_code == 200
            data = response.json()

            assert "model_used" in data
            assert isinstance(data["model_used"], str)
            assert len(data["model_used"]) > 0
