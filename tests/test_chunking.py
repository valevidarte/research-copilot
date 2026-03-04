"""Unit tests for chunking module."""
import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chunking.chunker import TokenChunker


class TestChunker:
    """Tests for text chunking module."""
    
    @pytest.fixture
    def chunker(self):
        """Create a test chunker instance."""
        return TokenChunker(chunk_size=100, chunk_overlap=10)
    
    def test_chunker_initialization(self, chunker):
        """Test chunker initialization."""
        assert chunker.chunk_size == 100
        assert chunker.chunk_overlap == 10
    
    def test_token_counting(self, chunker):
        """Test token counting."""
        text = "Hello world test sentence"
        count = chunker.count_tokens(text)
        assert count > 0
        assert isinstance(count, int)
    
    def test_chunking_basic(self, chunker):
        """Test basic text chunking."""
        text = "This is a sample text. " * 50  # Create longer text
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 1
        assert all("chunk_id" in chunk for chunk in chunks)
        assert all("text" in chunk for chunk in chunks)
        assert all("token_count" in chunk for chunk in chunks)
    
    def test_chunking_with_metadata(self, chunker):
        """Test chunking with metadata."""
        text = "Sample text for testing. " * 30
        metadata = {"paper_id": "test_001", "title": "Test Paper"}
        
        chunks = chunker.chunk_text(text, metadata)
        
        for chunk in chunks:
            assert chunk["metadata"]["paper_id"] == "test_001"
            assert chunk["metadata"]["title"] == "Test Paper"
    
    def test_chunk_overlap(self, chunker):
        """Test that chunks overlap correctly."""
        text = "Word. " * 100  # Create a long text with distinct tokens
        chunks = chunker.chunk_text(text)
        
        if len(chunks) > 1:
            # Check overlap exists between consecutive chunks
            assert chunks[0]["end_token"] > chunks[1]["start_token"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
