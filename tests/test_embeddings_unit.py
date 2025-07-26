import pytest
import asyncio
from embeddings import EmbeddingService
from config import settings
from unittest.mock import patch

@pytest.fixture(scope="module")
def embedding_service():
    return EmbeddingService(model_name=settings.embedding_model_name, device=settings.embedding_device)

def test_model_initialization(embedding_service):
    assert embedding_service.embedding_model is not None

@pytest.mark.asyncio
async def test_model_validation(embedding_service):
    result = await embedding_service.validate_model()
    assert result is True

@pytest.mark.asyncio
async def test_single_text_embedding(embedding_service):
    result = await embedding_service.get_embeddings("hello world")
    assert isinstance(result, list)
    assert len(result) == 1024
    assert all(isinstance(x, float) for x in result)

@pytest.mark.asyncio
async def test_empty_string_raises(embedding_service):
    with pytest.raises(RuntimeError, match="Input text cannot be empty"):
        await embedding_service.get_embeddings("")

@pytest.mark.asyncio
async def test_whitespace_string_raises(embedding_service):
    with pytest.raises(RuntimeError, match="Input text cannot be empty"):
        await embedding_service.get_embeddings("   ")

@pytest.mark.asyncio
async def test_non_string_input_raises(embedding_service):
    with pytest.raises(RuntimeError, match="Input must be a string or list of strings"):
        await embedding_service.get_embeddings(123)
    with pytest.raises(RuntimeError, match="Input must be a string or list of strings"):
        await embedding_service.get_embeddings(None)

@pytest.mark.asyncio
async def test_empty_list_raises(embedding_service):
    with pytest.raises(RuntimeError, match="Input text list cannot be empty"):
        await embedding_service.get_embeddings([])

@pytest.mark.asyncio
async def test_list_with_empty_strings_raises(embedding_service):
    with pytest.raises(RuntimeError, match="No valid texts found in input list"):
        await embedding_service.get_embeddings(["", "   "])

def test_invalid_model_name():
    with pytest.raises(Exception):
        EmbeddingService(model_name="nonexistent-model-xyz", device="cpu")

def test_invalid_device():
    with pytest.raises(Exception):
        EmbeddingService(model_name=settings.embedding_model_name, device="invalid_device") 