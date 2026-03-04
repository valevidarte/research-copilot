"""Embedding generation using OpenAI embeddings."""
from openai import OpenAI
from typing import List
from loguru import logger


class OpenAIEmbedder:
    """Generate embeddings using OpenAI's embedding models."""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize the embedder.
        
        Args:
            model: OpenAI embedding model to use
        """
        self.client = OpenAI()
        self.model = model
        logger.info(f"Initialized embedder with model: {model}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            query: Query text to embed
            
        Returns:
            Embedding vector
        """
        return self.embed_texts([query])[0]
