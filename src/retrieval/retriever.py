"""Document retrieval module for RAG pipeline."""
from typing import List, Dict
from loguru import logger


class DocumentRetriever:
    """Retrieve relevant documents from vector store."""
    
    def __init__(self, vector_store, embedder):
        """
        Initialize retriever.
        
        Args:
            vector_store: Vector store instance
            embedder: Embedder instance
        """
        self.vector_store = vector_store
        self.embedder = embedder
        logger.info("Initialized DocumentRetriever")

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        where: Dict = None
    ) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query text
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            List of relevant document chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)
        
        # Query vector store
        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=n_results,
            where=where
        )
        
        # Format results
        retrieved_docs = []
        if results and "documents" in results:
            for i, doc in enumerate(results["documents"][0]):
                retrieved_docs.append({
                    "chunk_id": i,
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if "metadatas" in results else {},
                    "similarity_score": 1 - results["distances"][0][i] if "distances" in results else 0
                })
        
        logger.info(f"Retrieved {len(retrieved_docs)} documents for query")
        return retrieved_docs
