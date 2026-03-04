"""Ingestion script to load papers into the RAG pipeline."""
import json
from pathlib import Path
from tqdm import tqdm
from loguru import logger
import sys
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_pipeline import RAGPipeline


def load_paper_catalog(catalog_path: str) -> dict:
    """Load paper catalog from JSON file."""
    with open(catalog_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def ingest_papers(papers_dir: str = "papers", catalog_file: str = "papers/paper_catalog.json"):
    """
    Ingest all papers from the catalog.
    
    Args:
        papers_dir: Directory containing PDF files
        catalog_file: Path to paper catalog JSON
    """
    logger.info("Starting paper ingestion...")
    
    # Load catalog
    try:
        catalog = load_paper_catalog(catalog_file)
    except FileNotFoundError:
        logger.error(f"Paper catalog not found at {catalog_file}")
        return False
    
    # Initialize pipeline
    pipeline = RAGPipeline()
    
    # Ingest each paper
    papers = catalog.get("papers", [])
    success_count = 0
    
    for paper in tqdm(papers, desc="Ingesting papers"):
        pdf_path = Path(papers_dir) / paper["filename"]
        
        if not pdf_path.exists():
            logger.warning(f"PDF not found: {pdf_path}")
            continue
        
        # Prepare metadata
        metadata = {
            "title": paper.get("title", "Unknown"),
            "authors": paper.get("authors", []),
            "year": paper.get("year", 0),
            "doi": paper.get("doi", ""),
            "venue": paper.get("venue", ""),
            "topics": paper.get("topics", [])
        }
        
        # Ingest paper
        if pipeline.ingest_paper(str(pdf_path), paper["id"], metadata):
            success_count += 1
    
    logger.info(f"Ingestion complete: {success_count}/{len(papers)} papers successfully ingested")
    
    # Print collection info
    info = pipeline.get_papers_info()
    logger.info(f"Collection info: {info}")
    
    return success_count == len(papers)


if __name__ == "__main__":
    ingest_papers()
