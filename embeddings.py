"""
Embedding service using LlamaIndex with Hugging Face models.
"""

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing import List, Union
import numpy as np


class EmbeddingService:
    """Service class for generating text embeddings."""
    
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        """Initialize the embedding service with specified model."""
        self.model_name = model_name
        self.embedding_model = None
        self._setup_model()
    
    def _setup_model(self):
        """Setup the HuggingFace embedding model."""
        # TODO: Implement model setup with BAAI/bge-m3
        # This will be implemented in Milestone 2
        pass
    
    async def get_embeddings(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Generate embeddings for input text(s)."""
        # TODO: Implement embedding generation
        # This will be implemented in Milestone 2
        if isinstance(texts, str):
            return [0.1] * 1024  # Placeholder for single text
        else:
            return [[0.1] * 1024 for _ in texts]  # Placeholder for multiple texts


# Global embedding service instance
embedding_service = EmbeddingService() 