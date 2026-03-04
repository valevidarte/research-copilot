"""PDF text extraction module using PyMuPDF."""
import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional
from loguru import logger


def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract text and metadata from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        dict with keys: text, metadata, pages, total_pages, extraction_warnings
    """
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        pages = []
        warnings = []

        for page_num, page in enumerate(doc):
            text = page.get_text()
            pages.append({
                "page_number": page_num + 1,
                "text": text,
                "char_count": len(text)
            })
            full_text += f"\n[PAGE {page_num + 1}]\n{text}"

        # Document metadata
        metadata = doc.metadata

        logger.info(f"Successfully extracted {len(doc)} pages from {Path(pdf_path).name}")
        
        return {
            "text": full_text,
            "metadata": metadata,
            "pages": pages,
            "total_pages": len(doc),
            "extraction_warnings": warnings
        }
    except Exception as e:
        logger.error(f"Error extracting PDF {pdf_path}: {str(e)}")
        raise
