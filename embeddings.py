"""
Embedding service using LlamaIndex with Hugging Face models.
"""

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing import List, Union
import logging
from config import settings

# Configure logging
logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service class for generating text embeddings."""
    
    def __init__(self, model_name: str = None, device: str = None):
        """Initialize the embedding service with specified model."""
        self.model_name = model_name or settings.embedding_model_name
        self.device = device or settings.embedding_device
        self.embedding_model = None
        self._setup_model()
    
    def _setup_model(self):
        """Setup the HuggingFace embedding model."""
        try:
            logger.info(f"Initializing HuggingFace embedding model: {self.model_name} on {self.device}")
            self.embedding_model = HuggingFaceEmbedding(
                model_name=self.model_name,
                device=self.device
            )
            logger.info(f"Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {str(e)}")
            raise RuntimeError(f"Failed to initialize embedding model {self.model_name}: {str(e)}")
    
    async def validate_model(self):
        """Validate that the model can generate embeddings correctly."""
        try:
            logger.info("Validating embedding model...")
            test_embedding = self.embedding_model.get_text_embedding("test")
            logger.info(f"Model validation successful. Embedding dimensions: {len(test_embedding)}")
            return True
        except Exception as e:
            logger.error(f"Model validation failed: {str(e)}")
            raise RuntimeError(f"Embedding model validation failed: {str(e)}")
    
    async def get_embeddings(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Generate embeddings for input text(s)."""
        try:
            # Handle single text input
            if isinstance(texts, str):
                if not texts.strip():
                    raise ValueError("Input text cannot be empty")
                
                logger.debug(f"Generating embedding for single text (length: {len(texts)})")
                embedding = self.embedding_model.get_text_embedding(texts)
                logger.debug(f"Generated embedding with {len(embedding)} dimensions")
                return embedding
            
            # Handle list of texts input
            elif isinstance(texts, list):
                if not texts:
                    raise ValueError("Input text list cannot be empty")
                
                # Filter out empty texts
                valid_texts = [text for text in texts if text and text.strip()]
                if not valid_texts:
                    raise ValueError("No valid texts found in input list")
                
                logger.debug(f"Generating embeddings for {len(valid_texts)} texts")
                embeddings = []
                for i, text in enumerate(valid_texts):
                    embedding = self.embedding_model.get_text_embedding(text)
                    embeddings.append(embedding)
                    logger.debug(f"Generated embedding {i+1}/{len(valid_texts)} with {len(embedding)} dimensions")
                
                return embeddings
            
            else:
                raise TypeError("Input must be a string or list of strings")
                
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise RuntimeError(f"Failed to generate embeddings: {str(e)}")


# Global embedding service instance
embedding_service = EmbeddingService() 