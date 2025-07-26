from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# Positive case: valid request
def test_embeddings_valid():
    response = client.post("/api/v1/embeddings", json={"text": "hello world"})
    assert response.status_code == 200
    data = response.json()
    assert "embeddings" in data
    assert isinstance(data["embeddings"], list)
    assert len(data["embeddings"]) == 1024
    assert data["model"] == "BAAI/bge-m3"
    assert data["dimensions"] == 1024
    assert "processing_time_ms" in data


# Negative case: empty string
def test_embeddings_empty_string():
    response = client.post("/api/v1/embeddings", json={"text": ""})
    assert response.status_code == 422
    assert "String should have at least 1 character" in response.text


# Negative case: whitespace string
def test_embeddings_whitespace_string():
    response = client.post("/api/v1/embeddings", json={"text": "   "})
    assert response.status_code == 400
    assert "Text cannot be empty" in response.text


# Negative case: very long text
def test_embeddings_very_long_text():
    long_text = "a" * 10001
    response = client.post("/api/v1/embeddings", json={"text": long_text})
    assert response.status_code == 422
    assert "String should have at most 10000 characters" in response.text


# Negative case: missing text field
def test_embeddings_missing_text_field():
    response = client.post("/api/v1/embeddings", json={})
    assert response.status_code == 422  # Unprocessable Entity


# Negative case: wrong field name
def test_embeddings_wrong_field_name():
    response = client.post("/api/v1/embeddings", json={"message": "hello"})
    assert response.status_code == 422


# Negative case: invalid JSON
def test_embeddings_invalid_json():
    response = client.post(
        "/api/v1/embeddings",
        data="not a json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422 or response.status_code == 400


# Negative case: wrong HTTP method
def test_embeddings_wrong_method():
    response = client.get("/api/v1/embeddings")
    assert response.status_code == 405


# Negative case: wrong content type
def test_embeddings_wrong_content_type():
    response = client.post(
        "/api/v1/embeddings",
        data='{"text": "hello"}',
        headers={"Content-Type": "text/plain"},
    )
    assert response.status_code == 422 or response.status_code == 400


# Edge case: very short text
def test_embeddings_very_short_text():
    response = client.post("/api/v1/embeddings", json={"text": "a"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["embeddings"]) == 1024
