"""Document retrieval module for RAG pipeline.

This module handles retrieving relevant documents from the vector store based on
semantic similarity to user queries. It performs the following steps:

1. Generates embeddings for the query using the configured embedder
2. Searches the vector store for similar document chunks
3. Formats and returns the results with metadata and similarity scores

The retriever is a key component in the RAG pipeline that enables
context-aware answer generation.
"""

from typing import List, Dict, Optional
from loguru import logger


class DocumentRetriever:
    """
    Retrieve relevant documents from vector store using semantic similarity.
    
    This class handles the retrieval phase of the RAG pipeline by:
    - Converting queries to embeddings
    - Searching for similar documents in the vector store
    - Formatting results with metadata and similarity scores
    
    Attributes:
        vector_store: ChromaDB or compatible vector store instance
        embedder: OpenAI embedder for query encoding
    """
    
    def __init__(self, vector_store, embedder):
        """
        Initialize the document retriever.
        
        Args:
            vector_store: Vector store instance (ChromaDB, FAISS, etc.)
                         Must implement: query() method
            embedder: Embedder instance for query encoding
                     Must implement: embed_query() method
                     
        Raises:
            ValueError: If vector_store or embedder is None
        """
        if vector_store is None or embedder is None:
            raise ValueError("vector_store and embedder cannot be None")
            
        self.vector_store = vector_store
        self.embedder = embedder
        logger.info("Initialized DocumentRetriever")

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        This method:
        1. Encodes the query to a vector
        2. Searches the vector store for similar documents
        3. Formats results with metadata and similarity scores
        
        Args:
            query: Query string to find relevant documents for
            n_results: Number of results to return (default: 5)
            where: Optional metadata filter for document selection
                  Example: {"year": "2023"} to filter by year
            
        Returns:
            List of dictionaries, each containing:
                - chunk_id (str): Unique identifier for the text chunk
                - text (str): The actual document text
                - metadata (dict): Document metadata (title, authors, year, etc.)
                - similarity_score (float): Similarity score (0-1, higher is better)
                
        Raises:
            ValueError: If query is empty
            Exception: If embedding or search fails
            
        Example:
            >>> retriever = DocumentRetriever(vector_store, embedder)
            >>> results = retriever.retrieve("What is transitional justice?", n_results=3)
            >>> for result in results:
            ...     print(f"Title: {result['metadata']['title']}")
            ...     print(f"Score: {result['similarity_score']:.2f}")
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        try:
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
