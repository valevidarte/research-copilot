"""Unit tests for ingestion module."""
import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.text_cleaner import clean_extracted_text


class TestTextCleaner:
    """Tests for text cleaning module."""
    
    def test_remove_excessive_whitespace(self):
        """Test removal of excessive whitespace."""
        input_text = "This   is    a   test    with   excessive    spaces"
        output = clean_extracted_text(input_text)
        assert "   " not in output  # No triple spaces
        assert "This is a test with excessive spaces" in output
    
    def test_fix_hyphenated_words(self):
        """Test fixing hyphenated words at line breaks."""
        input_text = "The trans-\nformation process began"
        output = clean_extracted_text(input_text)
        assert "trans-\nformation" not in output
        assert "transformation" in output
    
    def test_normalize_quotes(self):
        """Test normalization of quotes."""
        input_text = 'He said "hello" and She said "goodbye"'
        output = clean_extracted_text(input_text)
        assert '"' in output or '"' in output
    
    def test_remove_multiple_newlines(self):
        """Test removal of multiple consecutive newlines."""
        input_text = "Line 1\n\n\n\nLine 2\n\n\nLine 3"
        output = clean_extracted_text(input_text)
        assert "\n\n\n" not in output
    
    def test_preserve_content(self):
        """Test that main content is preserved."""
        input_text = "This is the main content of the paper"
        output = clean_extracted_text(input_text)
        assert "main content" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
