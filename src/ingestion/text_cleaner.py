"""Text cleaning module for PDF extracted content."""
import re
from loguru import logger


def clean_extracted_text(text: str) -> str:
    """
    Clean and normalize extracted PDF text.
    
    Args:
        text: Raw text extracted from PDF
        
    Returns:
        Cleaned and normalized text
    """
    original_length = len(text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix hyphenated words at line breaks
    text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)
    
    # Remove page numbers and headers/footers (basic)
    text = re.sub(r'\n\d+\n', '\n', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Remove multiple newlines
    text = re.sub(r'\n\n+', '\n\n', text)
    
    logger.info(f"Cleaned text: {original_length} -> {len(text)} characters")
    
    return text.strip()
