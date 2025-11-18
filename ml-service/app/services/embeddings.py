"""
Text embedding service using sentence transformers.

Provides semantic embeddings for content similarity and recommendations.
"""
import torch
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
from app.config import settings


class EmbeddingService:
    """
    Service for generating text embeddings.
    
    Uses sentence-transformers for semantic similarity.
    """
    
    def __init__(self):
        """Initialize embedding model."""
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL,
            cache_folder=settings.CACHE_DIR,
            device=settings.DEVICE
        )
        print(f"✅ Embedding model loaded on {settings.DEVICE}")
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = None,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Encode text(s) to embedding vectors.
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for encoding
            normalize: Whether to normalize embeddings
            
        Returns:
            numpy array of embeddings (shape: [n_texts, embedding_dim])
        """
        if isinstance(texts, str):
            texts = [texts]
        
        batch_size = batch_size or settings.BATCH_SIZE
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=normalize,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def compute_similarity(
        self,
        text_a: str,
        text_b: str
    ) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text_a: First text
            text_b: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        embeddings = self.encode([text_a, text_b])
        
        # Cosine similarity (already normalized)
        similarity = np.dot(embeddings[0], embeddings[1])
        
        return float(similarity)
    
    def find_similar(
        self,
        query_text: str,
        candidate_texts: List[str],
        top_k: int = None,
        threshold: float = None
    ) -> List[tuple]:
        """
        Find most similar texts to query.
        
        Args:
            query_text: Query text
            candidate_texts: List of candidate texts
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of (index, similarity_score) tuples
        """
        if not candidate_texts:
            return []
        
        top_k = top_k or settings.TOP_K_RECOMMENDATIONS
        threshold = threshold or settings.SIMILARITY_THRESHOLD
        
        # Encode all texts
        query_emb = self.encode(query_text)
        candidate_embs = self.encode(candidate_texts)
        
        # Compute similarities
        similarities = np.dot(candidate_embs, query_emb.T).flatten()
        
        # Filter by threshold
        mask = similarities >= threshold
        indices = np.where(mask)[0]
        scores = similarities[mask]
        
        # Sort by similarity
        sorted_idx = np.argsort(scores)[::-1]
        
        # Return top k
        results = [
            (int(indices[i]), float(scores[i]))
            for i in sorted_idx[:top_k]
        ]
        
        return results
    
    def batch_encode(
        self,
        texts: List[str],
        batch_size: int = None
    ) -> np.ndarray:
        """
        Batch encode texts for efficient processing.
        
        Args:
            texts: List of texts
            batch_size: Batch size
            
        Returns:
            Array of embeddings
        """
        return self.encode(texts, batch_size=batch_size)


# Global instance
embedding_service = EmbeddingService()
