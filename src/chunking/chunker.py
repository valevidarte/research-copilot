"""Token-based text chunking module."""
import tiktoken
from typing import List, Optional
from loguru import logger


class TokenChunker:
    """Chunk text into fixed-size token chunks with overlap."""
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        model: str = "gpt-4"
    ):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Number of tokens per chunk
            chunk_overlap: Number of overlapping tokens between chunks
            model: Model name to get tokenizer
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoder = tiktoken.encoding_for_model(model)
        logger.info(f"Initialized chunker: size={chunk_size}, overlap={chunk_overlap}")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))

    def chunk_text(self, text: str, metadata: Optional[dict] = None) -> List[dict]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        tokens = self.encoder.encode(text)
        chunks = []
        chunk_id = 0
        start = 0

        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoder.decode(chunk_tokens)

            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "token_count": len(chunk_tokens),
                "start_token": start,
                "end_token": end,
                "metadata": metadata or {}
            })

            start += self.chunk_size - self.chunk_overlap
            chunk_id += 1

        logger.info(f"Created {len(chunks)} chunks from {len(tokens)} tokens")
        return chunks
