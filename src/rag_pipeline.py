"""Main RAG pipeline orchestrator.

This module provides the RAGPipeline class that orchestrates the entire retrieval-augmented
generation workflow, including document retrieval, embedding generation, and response generation.
The pipeline supports multiple prompt strategies and can be configured with different models.

Components:
    - Vector Store: ChromaDB for storing and retrieving document embeddings
    - Embedder: OpenAI embeddings for converting text to vectors
    - Retriever: Document retrieval with similarity search
    - Generator: Response generation using LLMs with multiple strategies
"""

from typing import List, Dict, Tuple, Optional
from pathlib import Path
from loguru import logger

from src.vectorstore.chroma_store import ChromaVectorStore
from src.embedding.embedder import OpenAIEmbedder
from src.generation.generator import ResponseGenerator
from src.retrieval.retriever import DocumentRetriever
from src.ingestion.pdf_extractor import PDFExtractor
from src.chunking.chunker import TokenChunker
from prompts.templates import get_prompt


class RAGPipeline:
    """Simple RAG pipeline for paper retrieval and answer generation."""

    def __init__(
        self,
        vector_store_path: str = "./vector_store",
        embedding_model: str = "text-embedding-3-small",
        generation_model: str = "gpt-4-turbo",
        n_results: int = 5,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            vector_store_path: Path to persist ChromaDB vector store
            embedding_model: OpenAI embedding model to use
            generation_model: OpenAI generation model to use (gpt-4-turbo, gpt-3.5-turbo, etc)
            n_results: Number of documents to retrieve per query
            chunk_size: Size of text chunks in tokens
            chunk_overlap: Overlap between consecutive chunks
            
        Raises:
            ValueError: If models or paths are invalid
        """
        self.n_results = n_results
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        try:
            self.embedder = OpenAIEmbedder(model=embedding_model)
            self.vector_store = ChromaVectorStore(persist_dir=vector_store_path)
            self.retriever = DocumentRetriever(self.vector_store, self.embedder)
            self.generator = ResponseGenerator(model=generation_model)
            self.pdf_extractor = PDFExtractor()
            self.chunker = TokenChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            
            logger.info(
                f"RAG Pipeline initialized | "
                f"Embedder: {embedding_model} | "
                f"Generator: {generation_model} | "
                f"Chunk: {chunk_size} tokens with {chunk_overlap} overlap"
            )
        except Exception as e:
            logger.error(f"Failed to initialize RAG Pipeline: {e}")
            raise ValueError(f"Pipeline initialization failed: {e}")

    def query(self, question: str, strategy: str = "v1") -> Tuple[str, List[Dict]]:
        """
        Query the RAG pipeline.

        Args:
            question: User question
            strategy: Prompt strategy to use

        Returns:
            Tuple of (answer, citations)
        """
        if not question or not question.strip():
            logger.warning("Empty question provided")
            return "Please provide a valid question.", []

        try:
            logger.info(f"Processing query: {question[:100]}...")

            # retrieve documents
            search_results = self.retriever.retrieve(question, n_results=self.n_results)

            if not search_results:
                logger.info("No relevant documents found")
                return (
                    "No relevant information found in the papers. Try rephrasing your question or check if papers have been ingested.",
                    []
                )

            retrieved_docs = [
                {
                    "text": doc["text"],
                    "metadata": doc["metadata"],
                    "relevance": doc["similarity_score"]
                }
                for doc in search_results
            ]

            logger.info(f"Retrieved {len(retrieved_docs)} documents")

            prompt_template = get_prompt(strategy)

            answer, citations = self.generator.generate(
                query=question,
                retrieved_docs=retrieved_docs,
                prompt_template=prompt_template,
                strategy=strategy
            )

            logger.info(f"Generated answer with {len(citations)} citations")
            return answer, citations

        except Exception as e:
            logger.error(f"Query error: {e}", exc_info=True)
            return f"An error occurred while processing your query: {str(e)}. Please try again.", []

    def get_papers_info(self) -> Dict:
        """
        Return vector store information.
        
        Returns:
            Dictionary with store type, status, and document count
        """
        try:
            # For ChromaDB, we can try to get collection info
            if hasattr(self.vector_store, 'collection') and self.vector_store.collection:
                count = self.vector_store.collection.count() if hasattr(self.vector_store.collection, 'count') else 0
                return {
                    "vector_store_type": "ChromaDB",
                    "status": "initialized",
                    "documents_count": count
                }
            else:
                return {
                    "vector_store_type": "ChromaDB (in-memory fallback)",
                    "status": "initialized",
                    "documents_count": "unknown"
                }
        except Exception as e:
            logger.warning(f"Could not get vector store info: {e}")
            return {"vector_store_type": "ChromaDB", "status": "initialized", "error": str(e)}

    def ingest_paper(
        self,
        pdf_path: str,
        paper_id: str,
        metadata: Dict
    ) -> bool:
        """
        Ingest a PDF paper into the RAG pipeline.
        
        This method:
        1. Extracts text from PDF
        2. Chunks the text into manageable pieces
        3. Generates embeddings for each chunk
        4. Stores chunks and embeddings in the vector store
        
        Args:
            pdf_path: Path to PDF file
            paper_id: Unique identifier for the paper
            metadata: Paper metadata (title, authors, year, etc)
            
        Returns:
            bool: True if ingestion succeeded, False otherwise
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If extraction or storage fails
        """
        try:
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                raise FileNotFoundError(f"PDF not found: {pdf_path}")
            
            logger.info(f"Ingesting paper: {paper_id} from {pdf_file.name}")
            
            # Extract text from PDF
            try:
                text = self.pdf_extractor.extract_text(str(pdf_path))
                if not text or len(text.strip()) == 0:
                    logger.warning(f"No text extracted from {paper_id}")
                    return False
                logger.info(f"Extracted {len(text)} characters from {paper_id}")
            except Exception as e:
                logger.error(f"PDF extraction failed for {paper_id}: {e}")
                return False
            
            # Chunk the text
            try:
                chunks = self.chunker.chunk_text(text, metadata)
                if not chunks:
                    logger.warning(f"No chunks created for {paper_id}")
                    return False
                logger.info(f"Created {len(chunks)} chunks for {paper_id}")
            except Exception as e:
                logger.error(f"Chunking failed for {paper_id}: {e}")
                return False
            
            # Generate embeddings
            try:
                chunk_texts = [chunk["text"] for chunk in chunks]
                embeddings = self.embedder.embed_texts(chunk_texts)
                if len(embeddings) != len(chunks):
                    logger.error(f"Embedding count mismatch for {paper_id}")
                    return False
                logger.info(f"Generated embeddings for {len(chunks)} chunks in {paper_id}")
            except Exception as e:
                logger.error(f"Embedding generation failed for {paper_id}: {e}")
                return False
            
            # Store in vector database
            try:
                # Ensure collection exists
                self.vector_store.create_collection(f"papers_{paper_id}")
                
                # Add documents
                chunk_ids = [f"{paper_id}_chunk_{i}" for i in range(len(chunks))]
                chunk_metadatas = [chunk.get("metadata", {}) for chunk in chunks]
                
                self.vector_store.add_documents(
                    ids=chunk_ids,
                    documents=chunk_texts,
                    embeddings=embeddings,
                    metadatas=chunk_metadatas
                )
                logger.info(f"Successfully stored {len(chunk_ids)} chunks for {paper_id}")
                return True
                
            except Exception as e:
                logger.error(f"Vector store storage failed for {paper_id}: {e}")
                return False
        
        except Exception as e:
            logger.error(f"Unexpected error during ingestion of {paper_id}: {e}", exc_info=True)
            return False