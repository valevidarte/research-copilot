"""Ingestion script to load papers into the RAG pipeline.

This module handles the batch ingestion of PDF papers into the RAG pipeline.
It reads paper metadata from a catalog file and processes each PDF by:
1. Extracting text content
2. Chunking the text into retrievable units
3. Generating embeddings
4. Storing in the vector database

Usage:
    python src/ingest.py
    
    This will:
    - Load papers from papers/paper_catalog.json
    - Process all PDFs in the papers/ directory
    - Store embeddings in ./vector_store/
"""

import json
import sys
from pathlib import Path
from tqdm import tqdm
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_pipeline import RAGPipeline


def load_paper_catalog(catalog_path: str) -> dict:
    """
    Load paper metadata catalog from JSON file.
    
    Args:
        catalog_path: Path to paper_catalog.json
        
    Returns:
        Dictionary containing catalog metadata and paper list
        
    Raises:
        FileNotFoundError: If catalog file doesn't exist
        json.JSONDecodeError: If catalog is invalid JSON
    """
    try:
        with open(catalog_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Catalog file not found: {catalog_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in catalog: {e}")
        raise


def validate_catalog(catalog: dict) -> bool:
    """
    Validate catalog structure.
    
    Args:
        catalog: Catalog dictionary to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if "papers" not in catalog:
        logger.error("Catalog missing 'papers' key")
        return False
    
    if not isinstance(catalog["papers"], list):
        logger.error("'papers' must be a list")
        return False
    
    if len(catalog["papers"]) == 0:
        logger.warning("Catalog contains no papers")
        return True
    
    # Check first paper structure
    first = catalog["papers"][0]
    required_fields = ["id", "title", "filename"]
    for field in required_fields:
        if field not in first:
            logger.error(f"Missing required field '{field}' in paper metadata")
            return False
    
    return True


def ingest_papers(
    papers_dir: str = "papers",
    catalog_file: str = "papers/paper_catalog.json",
    skip_existing: bool = False
) -> Dict[str, int]:
    """
    Ingest all papers from the catalog into the RAG pipeline.
    
    Args:
        papers_dir: Directory containing PDF files
        catalog_file: Path to paper catalog JSON file
        skip_existing: If True, skip papers already in vector store (not implemented)
        
    Returns:
        Dictionary with ingestion statistics:
            - total: Total papers in catalog
            - success: Successfully ingested papers
            - failed: Failed ingestion attempts
            - skipped: Papers with missing PDFs
            
    Raises:
        FileNotFoundError: If catalog doesn't exist
        ValueError: If catalog is invalid
    """
    logger.info("="*60)
    logger.info("Starting paper ingestion pipeline")
    logger.info("="*60)
    
    # Load and validate catalog
    try:
        catalog = load_paper_catalog(catalog_file)
        if not validate_catalog(catalog):
            raise ValueError("Invalid catalog structure")
    except Exception as e:
        logger.error(f"Failed to load catalog: {e}")
        return {"total": 0, "success": 0, "failed": 0, "skipped": 0}
    
    # Initialize pipeline
    try:
        pipeline = RAGPipeline()
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {e}")
        return {"total": 0, "success": 0, "failed": 0, "skipped": 0}
    
    # Process each paper
    papers = catalog.get("papers", [])
    stats = {
        "total": len(papers),
        "success": 0,
        "failed": 0,
        "skipped": 0
    }
    
    logger.info(f"Processing {len(papers)} papers from catalog")
    logger.info(f"Source directory: {papers_dir}")
    
    for paper in tqdm(papers, desc="Ingesting papers", unit="paper"):
        paper_id = paper.get("id", "unknown")
        pdf_filename = paper.get("filename")
        pdf_path = Path(papers_dir) / pdf_filename
        
        # Check if PDF exists
        if not pdf_path.exists():
            logger.warning(f"PDF not found for {paper_id}: {pdf_path}")
            stats["skipped"] += 1
            continue
        
        # Prepare metadata
        metadata = {
            "paper_id": paper_id,
            "title": paper.get("title", "Unknown"),
            "authors": ", ".join(paper.get("authors", [])) if paper.get("authors") else "Unknown",
            "year": str(paper.get("year", "Unknown")),
            "doi": paper.get("doi", ""),
            "venue": paper.get("venue", ""),
            "topics": ", ".join(paper.get("topics", [])) if paper.get("topics") else ""
        }
        
        # Ingest paper
        try:
            success = pipeline.ingest_paper(str(pdf_path), paper_id, metadata)
            if success:
                stats["success"] += 1
                logger.info(f"✓ Ingested {paper_id}")
            else:
                stats["failed"] += 1
                logger.error(f"✗ Failed to ingest {paper_id}")
        except Exception as e:
            stats["failed"] += 1
            logger.error(f"✗ Exception while ingesting {paper_id}: {e}")
    
    # Print summary
    logger.info("="*60)
    logger.info("INGESTION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total papers: {stats['total']}")
    logger.info(f"Successfully ingested: {stats['success']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Skipped (missing PDF): {stats['skipped']}")
    
    # Print collection info
    try:
        info = pipeline.get_papers_info()
        logger.info(f"Vector store status: {info}")
    except Exception as e:
        logger.warning(f"Could not get collection info: {e}")
    
    logger.info("="*60)
    
    return stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ingest academic papers into the RAG pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/ingest.py                           # Use default catalog and papers dir
  python src/ingest.py --catalog path/to/catalog.json
  python src/ingest.py --papers-dir path/to/pdfs
        """
    )
    parser.add_argument(
        "--catalog",
        default="papers/paper_catalog.json",
        help="Path to paper catalog JSON file (default: papers/paper_catalog.json)"
    )
    parser.add_argument(
        "--papers-dir",
        default="papers",
        help="Directory containing PDF files (default: papers)"
    )
    
    args = parser.parse_args()
    
    try:
        ingest_papers(papers_dir=args.papers_dir, catalog_file=args.catalog)
    except KeyboardInterrupt:
        logger.info("Ingestion interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
