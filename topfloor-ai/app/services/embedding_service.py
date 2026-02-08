"""
Embedding Service - Generates embeddings for text using sentence transformers
"""

from typing import List, Optional
from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:
    """
    Service for generating text embeddings using sentence transformers.
    Uses a pre-trained model for semantic similarity.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence transformer model to use
                       Default: all-MiniLM-L6-v2 (384 dimensions, fast and efficient)
        """
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model on first use."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.embedding_dimension
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter out empty texts but keep track of indices
        non_empty_texts = []
        non_empty_indices = []
        
        for i, text in enumerate(texts):
            if text and text.strip():
                non_empty_texts.append(text)
                non_empty_indices.append(i)
        
        if not non_empty_texts:
            # All texts are empty, return zero vectors
            return [[0.0] * self.embedding_dimension] * len(texts)
        
        # Generate embeddings for non-empty texts
        embeddings = self.model.encode(non_empty_texts, convert_to_numpy=True)
        
        # Reconstruct full list with zero vectors for empty texts
        result = []
        embedding_idx = 0
        
        for i in range(len(texts)):
            if i in non_empty_indices:
                result.append(embeddings[embedding_idx].tolist())
                embedding_idx += 1
            else:
                result.append([0.0] * self.embedding_dimension)
        
        return result
    
    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self.model.get_sentence_embedding_dimension()
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between -1 and 1 (higher is more similar)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


# Global singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Get the global embedding service instance.
    
    Returns:
        EmbeddingService singleton
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
