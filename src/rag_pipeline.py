"""Main RAG pipeline orchestrator."""
import json
from pathlib import Path
from typing import List, Dict, Tuple
from loguru import logger

from src.ingestion.pdf_extractor import extract_text_from_pdf
from src.ingestion.text_cleaner import clean_extracted_text
from src.chunking.chunker import TokenChunker
from src.embedding.embedder import OpenAIEmbedder
from src.vectorstore.chroma_store import ChromaVectorStore
from src.retrieval.retriever import DocumentRetriever
from src.generation.generator import ResponseGenerator
from prompts.templates import get_prompt


class RAGPipeline:
    """Complete RAG pipeline for paper retrieval and answer generation."""
    
    def __init__(
        self,
        chroma_db_path: str = "./chroma_db",
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            chroma_db_path: Path to ChromaDB storage
            chunk_size: Token size for chunks
            chunk_overlap: Overlap between chunks
        """
        self.embedder = OpenAIEmbedder()
        self.vector_store = ChromaVectorStore(persist_directory=chroma_db_path)
        self.vector_store.create_collection("research_papers")
        self.chunker = TokenChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.retriever = DocumentRetriever(self.vector_store, self.embedder)
        self.generator = ResponseGenerator()
        logger.info("Initialized RAG Pipeline")

    def ingest_paper(
        self,
        pdf_path: str,
        paper_id: str,
        paper_metadata: Dict
    ) -> bool:
        """
        Ingest a single PDF paper into the pipeline.
        
        Args:
            pdf_path: Path to PDF file
            paper_id: Unique paper identifier
            paper_metadata: Paper metadata (title, authors, year, etc.)
            
        Returns:
            True if successful
        """
        try:
            # Extract text
            extracted = extract_text_from_pdf(pdf_path)
            text = extracted["text"]
            
            # Clean text
            cleaned_text = clean_extracted_text(text)
            
            # Create chunks
            metadata = {
                "paper_id": paper_id,
                "paper_title": paper_metadata.get("title", "Unknown"),
                "authors": ", ".join(paper_metadata.get("authors", ["Unknown"])),
                "year": paper_metadata.get("year", 0),
                "doi": paper_metadata.get("doi", ""),
                "section": "body"
            }
            
            chunks = self.chunker.chunk_text(cleaned_text, metadata)
            
            # Generate embeddings
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedder.embed_texts(chunk_texts)
            
            # Prepare for storage
            ids = [f"{paper_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [chunk["metadata"] for chunk in chunks]
            
            # Store in vector database
            self.vector_store.add_documents(
                ids=ids,
                documents=chunk_texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully ingested paper {paper_id}: {metadata['paper_title']}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting paper {paper_id}: {str(e)}")
            return False

    def query(
        self,
        question: str,
        strategy: str = "v1",
        n_results: int = 5,
        filter_papers: List[str] = None
    ) -> Tuple[str, List[Dict]]:
        """
        Query the RAG pipeline.
        
        Args:
            question: User question
            strategy: Prompt strategy (v1, v2, v3, v4)
            n_results: Number of documents to retrieve
            filter_papers: Optional list of paper IDs to filter by
            
        Returns:
            Tuple of (answer, citations)
        """
        try:
            # Retrieve relevant documents
            where = None
            if filter_papers:
                where = {"paper_id": {"$in": filter_papers}}
            
            retrieved_docs = self.retriever.retrieve(
                query=question,
                n_results=n_results,
                where=where
            )
            
            if not retrieved_docs:
                return "I could not find relevant information in the provided papers to answer this question.", []
            
            # Get prompt template
            prompt_template = get_prompt(strategy)
            
            # Generate response
            answer, citations = self.generator.generate(
                query=question,
                retrieved_docs=retrieved_docs,
                prompt_template=prompt_template,
                strategy=strategy
            )
            
            logger.info(f"Query completed with strategy: {strategy}")
            return answer, citations
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"Error processing query: {str(e)}", []

    def get_papers_info(self) -> Dict:
        """Get information about ingested papers."""
        return self.vector_store.get_collection_info()
