# Research Copilot - Architecture Documentation

Comprehensive technical documentation of the Research Copilot system design, components, and data flow.

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                         │
│                      Streamlit Web Application                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  • Q&A Chat Interface  • Paper Browser  • Search Filters       │ │
│  │  • Query History       • Citation Display  • Analytics          │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└────────────────┬────────────────────────────────────────────────────┘
                 │ (HTTP Requests)
                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATION LAYER                           │
│                         RAGPipeline Class                            │
│  • Coordinates all components  • Manages state  • Error handling    │
└────────────────┬────────────────────────────────────────────────────┘
                 │
         ┌───────┴───────┬─────────────┬──────────────┬─────────────┐
         ▼               ▼             ▼              ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────────────┐
│ INGESTION    │ │  RETRIEVAL   │ │ EMBEDDING    │ │ GENERATION        │
│              │ │              │ │              │ │                   │
│ • PDF Parse  │ │ • Vector Sim │ │ • OpenAI     │ │ • GPT-4 Integration│
│ • Extract    │ │ • Metadata   │ │ • Tokenize   │ │ • Prompt Strategies│
│ • Clean      │ │ • Filter     │ │ • Embed      │ │ • Citation Tracking│
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └────────┬─────────┘
       │                │                │                  │
       └────────┬───────┴────────────────┴──────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     CHUNKING LAYER                                   │
│  TokenChunker: Text → Overlapping Chunks with Metadata              │
│  • Chunk size: 512 tokens  • Overlap: 50 tokens                     │
└────────────────┬────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                                     │
│               ChromaDB Vector Database                               │
│  • Embeddings storage  • Metadata indexing  • Similarity search      │
│  • Fallback: In-memory store for development                        │
└────────────────┬────────────────────────────────────────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  File System    │
        │  • vector_store/│
        │  • papers/      │
        └─────────────────┘
```

## 📦 Component Details

### 1. Ingestion Pipeline (`src/ingestion/`)

**Purpose**: Process raw PDF documents into structured data.

#### PDFExtractor (`pdf_extractor.py`)
```
PDF File → Text Extraction → Cleaned Text
```

- Uses `pdfplumber` for robust PDF parsing
- Handles OCR and encrypted PDFs
- Removes images, headers, footers
- Preserves text structure (paragraphs, lists)

**Input**: PDF file path  
**Output**: Raw text string

#### TextCleaner (`text_cleaner.py`)
```
Raw Text → Normalization → Cleaned Text
```

- Removes special characters and extra whitespace
- Fixes encoding issues
- Normalizes quotes and punctuation
- Removes boilerplate content

**Input**: Raw text  
**Output**: Clean, normalized text

### 2. Chunking Layer (`src/chunking/`)

**Purpose**: Split long documents into retrievable units.

#### TokenChunker (`chunker.py`)
```
Text → Token Count → Chunks with Overlap
```

**Configuration**:
- **Chunk Size**: 512 tokens (~2000 characters)
- **Overlap**: 50 tokens (10% overlap for context)
- **Model**: gpt-4 tokenizer (for accurate token counting)

**Algorithm**:
1. Count tokens in entire text
2. Identify chunk boundaries at token limits
3. Create overlapping chunks to preserve context
4. Attach metadata to each chunk

**Input**: Text + metadata  
**Output**: List of chunks with chunk_id, text, metadata

### 3. Embedding Layer (`src/embedding/`)

**Purpose**: Convert text to vector representations.

#### OpenAIEmbedder (`embedder.py`)
```
Text → OpenAI API → 1536-dim Vector
```

**Model**: `text-embedding-3-small`
- Dimensions: 1536
- Cost: $0.02 per 1M tokens
- Quality: Very good for semantic search
- Speed: ~100 tokens/second

**Process**:
1. Batch texts (up to 2048 texts per request)
2. Call OpenAI Embeddings API
3. Return vector representations
4. Cache embeddings for performance

**Input**: List of text chunks  
**Output**: List of vectors (each ~1536 dimensions)

### 4. Vector Store Layer (`src/vectorstore/`)

**Purpose**: Store and retrieve embeddings with metadata.

#### ChromaVectorStore (`chroma_store.py`)
```
Embeddings + Metadata → ChromaDB → Vector Store
```

**Features**:
- Persistent local storage
- Metadata filtering (by paper_id, year, etc.)
- Cosine similarity search
- In-memory fallback (no external dependencies)

**Collections**:
- One collection per paper
- Named: `papers_{paper_id}`
- Contains all chunks from that paper

**Storage Options**:
- **Primary**: ChromaDB persistent (on-disk)
- **Fallback**: In-memory store (development/testing)

### 5. Retrieval Layer (`src/retrieval/`)

**Purpose**: Find relevant documents for queries.

#### DocumentRetriever (`retriever.py`)
```
Query → Embed → Search Vector Store → Ranked Results
```

**Process**:
1. Embed query using same model as training
2. Perform similarity search (cosine distance)
3. Return top-k results with scores
4. Format results with metadata

**Configuration**:
- **k (n_results)**: 5 documents (configurable)
- **Similarity Metric**: Cosine distance
- **Score Range**: 0-1 (higher = more similar)

**Input**: User query string  
**Output**: Ranked list of document chunks with metadata

### 6. Generation Layer (`src/generation/`)

**Purpose**: Generate answers using retrieved context.

#### ResponseGenerator (`generator.py`)
```
Query + Context → GPT-4 → Answer with Citations
```

**Model**: `gpt-4-turbo`
- ~128K context window
- Excellent for reasoning and analysis
- Cost: ~$0.03 per 1K tokens completion

**Prompt Strategies**:

| Strategy | Approach | Use Case |
|----------|----------|----------|
| V1: Clear Instructions | Simple prompt with delimiters | Factual questions |
| V2: Structured JSON | Machine-readable format | API integration |
| V3: Few-Shot Learning | Examples for consistency | Format preservation |
| V4: Chain-of-Thought | Step-by-step reasoning | Complex analysis |

**Citation Tracking**:
- Maps answer segments to source papers
- Provides APA-formatted citations
- Includes page numbers and DOIs

### 7. Orchestration Layer (`src/rag_pipeline.py`)

**Purpose**: Coordinate all components into a cohesive system.

#### RAGPipeline Class
```python
class RAGPipeline:
    - query(question, strategy) → (answer, citations)
    - ingest_paper(pdf_path, metadata) → bool
    - get_papers_info() → dict
```

**Responsibilities**:
- Initialize all components
- Manage dataflow between components
- Handle errors and provide fallbacks
- Log operations for debugging
- Coordinate concurrent operations

## 🔄 Data Flow

### Query Processing Flow
```
1. User Input (Streamlit)
   ↓
2. RAGPipeline.query(question)
   ↓
3. OpenAIEmbedder.embed_query(question)
   ↓
4. DocumentRetriever.retrieve(embedding)
   ↓
5. Vector Store Similarity Search
   ↓
6. Return Top-K Results
   ↓
7. ResponseGenerator.generate(question, results)
   ↓
8. OpenAI API Call (GPT-4)
   ↓
9. Format Answer + Citations
   ↓
10. Return to Streamlit
   ↓
11. Display to User
```

### Ingestion Flow
```
1. PDF File Upload
   ↓
2. PDFExtractor.extract_text()
   ↓
3. TextCleaner.clean()
   ↓
4. TokenChunker.chunk_text()
   ↓
5. OpenAIEmbedder.embed_texts()
   ↓
6. ChromaVectorStore.add_documents()
   ↓
7. Persisted to Disk
```

## 💾 Data Models

### Document Chunk
```python
{
    "chunk_id": "paper_001_chunk_5",  # Unique identifier
    "text": "Lorem ipsum dolor...",     # Actual content
    "metadata": {                       # Document info
        "paper_id": "paper_001",
        "title": "Sample Research Paper",
        "authors": "John Doe, Jane Smith",
        "year": "2023",
        "venue": "Conference Name",
        "topics": "ai, nlp, rag",
        "doi": "10.1234/example"
    },
    "token_count": 487                  # For accounting
}
```

### Query Result
```python
{
    "chunk_id": "paper_001_chunk_5",
    "text": "Retrieved text content...",
    "metadata": {...},  # Same as chunk metadata
    "similarity_score": 0.87            # 0-1, higher = better match
}
```

### Generated Answer
```python
{
    "answer": "The research shows that...",
    "citations": [
        {
            "text": "Key finding from paper",
            "paper_id": "paper_001",
            "paper_title": "Title",
            "authors": ["Author 1", "Author 2"],
            "year": "2023",
            "apa_citation": "Author, A. (2023). Title. Venue."
        }
    ]
}
```

## 🔐 Error Handling Strategy

### Component-Level Error Handling
1. **Input Validation**: Check types, ranges, non-null
2. **Graceful Degradation**: Fallbacks for failing components
3. **Error Logging**: Structured logs with context
4. **User Feedback**: Clear, actionable error messages

### System-Level Error Handling
1. **Initialization**: Verify all components on startup
2. **API Failures**: Retry logic with exponential backoff
3. **Storage Failures**: In-memory fallback
4. **Rate Limiting**: Token counting and request batching

## 📊 Performance Characteristics

### Latency by Component
| Component | Latency | Notes |
|-----------|---------|-------|
| Embedding Generation | 0.5s | OpenAI API call |
| Vector Similarity Search | 0.1s | ChromaDB lookup |
| LLM Response Generation | 5-15s | GPT-4 API call |
| **Total (Query→Answer)** | **6-16s** | Dominated by LLM |

### Memory Usage
| Component | Typical Usage | Notes |
|-----------|-------------|-------|
| Embeddings | ~1.2 MB per paper | 1536 dims × 4 bytes × chunks |
| Vector Store Index | ~500 KB per paper | ChromaDB overhead |
| LLM Context | ~3 MB | During generation |
| **Total** | **~5-10 MB** | Very memory-efficient |

### Storage Requirements
| Component | Storage | Notes |
|-----------|---------|-------|
| Embeddings | 2-3 MB per 100k tokens | Vectorized data |
| ChromaDB Index | 1-2 MB per 100k tokens | Search index |
| Original PDFs | ~50 MB | 20 papers average |
| **Total** | **~100-150 MB** | Very compact |

## 🔄 Concurrency & Async

**Current Implementation**: Synchronous (blocking)

**Future Improvements**:
- Async PDF ingestion
- Concurrent API calls
- Batch embedding requests
- Cache warm-up in background

## 🛡️ Security Considerations

1. **API Keys**: Stored in environment variables, never in code
2. **PDF Handling**: Validates file types, size limits
3. **User Input**: Sanitized before API calls
4. **Data Privacy**: No data persisted beyond vector store
5. **Access Control**: Local-only by default

## 📈 Scalability

**Current Architecture Supports**:
- ✅ 100+ papers
- ✅ 1000+ daily queries
- ✅ 100K+ text chunks
- ✅ Single machine deployment

**Scaling Path**:
1. **Horizontal**: Distribute vector store (Milvus, Weaviate)
2. **Vertical**: GPU acceleration for embeddings
3. **Caching**: Redis for query result caching
4. **Async**: Message queue for batch processing

## 🔧 Dependencies

### Core Dependencies
- **streamlit**: Web UI framework
- **openai**: LLM and embedding APIs
- **chromadb**: Vector database
- **pdfplumber**: PDF text extraction
- **loguru**: Structured logging

### Development Dependencies
- **pytest**: Unit testing
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking

## 📝 Design Decisions

### Why ChromaDB?
- Local, lightweight, no setup required
- Metadata filtering support
- Good performance for <1M vectors
- Development-friendly (in-memory fallback)

### Why OpenAI Embeddings?
- State-of-the-art quality
- Multiple models (small, large)
- Easy integration
- Cost-effective

### Why GPT-4-Turbo?
- Excellent reasoning for complex queries
- Large context window (128K)
- Reliable citations and formatting
- Cost-effective for production use

### Token-Based Chunking?
- More accurate than character/word based
- Accounts for tokenizer variations
- Respects model limitations
- Language-agnostic

## 🚀 Future Enhancements

### Short Term
- [ ] Query result caching
- [ ] Multi-language support
- [ ] Custom prompt management UI
- [ ] Analytics dashboard

### Medium Term
- [ ] Hybrid search (semantic + keyword)
- [ ] Document summarization
- [ ] Multi-turn conversations
- [ ] Fine-tuned embeddings

### Long Term
- [ ] Distributed vector store
- [ ] Real-time paper updates
- [ ] Collaborative features
- [ ] Advanced reasoning (CoT, ReAct)

---

**Last Updated**: March 2026  
**Version**: 1.0
