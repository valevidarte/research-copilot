"""
Research Copilot Web Application

This Streamlit application provides an interactive interface for querying academic papers
about memory and human rights in Peru using a Retrieval-Augmented Generation (RAG) pipeline.

Features:
- 🤖 Q&A Assistant: Ask questions and get AI-powered answers with citations
- 📚 Paper Browser: Browse and search through all loaded papers
- 📜 Query History: Keep track of previous queries and answers
- 🔍 Advanced Search: Filter papers by title, author, topic, and year

Usage:
    streamlit run streamlit_app.py
    
Then visit: http://localhost:8501
"""

import streamlit as st
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

# Configure logging with error handling
try:
    logger.add("streamlit_app.log", rotation="500 MB", level="INFO")
except Exception as e:
    print(f"Warning: Could not configure logging file: {e}")

# Fix imports
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.rag_pipeline import RAGPipeline

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Research Copilot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

@st.cache_data
def load_paper_catalog() -> Dict:
    """
    Load paper catalog from JSON file with caching.
    
    Returns:
        dict: Catalog containing paper metadata, or empty dict if loading fails
    """
    catalog_path = ROOT_DIR / "papers" / "paper_catalog.json"
    try:
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
            logger.info(f"Loaded {len(catalog.get('papers', []))} papers from catalog")
            return catalog
    except FileNotFoundError:
        logger.warning(f"Paper catalog not found at {catalog_path}")
        st.error(f"Paper catalog not found. Please ensure papers/paper_catalog.json exists.")
        return {"papers": []}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in paper catalog: {e}")
        st.error(f"Invalid paper catalog format: {e}")
        return {"papers": []}
    except Exception as e:
        logger.error(f"Unexpected error loading catalog: {e}")
        st.error(f"Could not load paper catalog: {e}")
        return {"papers": []}


@st.cache_resource
def initialize_rag_pipeline() -> object:
    """
    Initialize RAG pipeline with caching for efficiency.
    
    Returns:
        RAGPipeline: Initialized pipeline instance
        
    Raises:
        Exception: If pipeline initialization fails
    """
    try:
        pipeline = RAGPipeline()
        logger.info("RAG Pipeline initialized successfully")
        return pipeline
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {e}")
        st.error(f"Failed to initialize RAG pipeline. Please check configuration.")
        raise


# Load catalog and initialize pipeline
catalog = load_paper_catalog()

try:
    rag_pipeline = initialize_rag_pipeline()
except Exception as e:
    st.error("Failed to start application. Please check your configuration and try again.")
    st.stop()

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header("📖 Research Copilot")
    st.write(
        "AI-powered research assistant for academic papers on "
        "memory and human rights in Peru."
    )
    
    st.markdown("---")
    st.subheader("📊 Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Papers", len(catalog.get('papers', [])))
    with col2:
        st.metric("Status", "Ready")
    
    st.markdown("---")
    
    # Session controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    with col2:
        if st.button("ℹ️ Help", use_container_width=True):
            st.session_state.show_help = True
            st.rerun()
    
    st.markdown("---")
    st.subheader("ℹ️ About")
    st.write(
        "This tool helps you query and analyze academic papers using "
        "advanced RAG (Retrieval-Augmented Generation) technology. "
        "All papers are indexed and searchable."
    )
    
    # Model info
    st.markdown("---")
    st.subheader("🔧 Configuration")
    st.write("""
    - **Embedding Model:** text-embedding-3-small
    - **Generation Model:** gpt-4-turbo
    - **Vector Store:** ChromaDB
    - **Chunk Size:** 512 tokens
    """)

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("📚 Research Copilot")

# Tabs
tab1, tab2 = st.tabs(["🤖 Q&A Assistant", "📚 Paper Browser"])

# Initialize session state
if "rag" not in st.session_state:
    st.session_state.rag = rag_pipeline
if "history" not in st.session_state:
    st.session_state.history = []

# ============================================================================
# TAB 1: Q&A ASSISTANT
# ============================================================================

with tab1:
    st.write("Ask questions about your academic papers and get AI-powered answers with citations.")
    
    # Query input
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            prompt = st.text_area(
                "Enter your research question:",
                placeholder="e.g., What are the main findings about memory initiatives in Peru?",
                height=100
            )
        with col2:
            search_button = st.button("🔍 Search", type="primary", use_container_width=True)

    if search_button and prompt.strip():
        try:
            with st.spinner("🔍 Searching papers and generating answer..."):
                answer, sources = st.session_state.rag.query(prompt)
            
            # Add to history
            st.session_state.history.append({
                "question": prompt,
                "answer": answer,
                "sources": sources
            })
            
            # Display result
            st.success("Answer generated successfully!")
            
            st.markdown("### 🤖 Answer")
            st.write(answer)
            
            if sources:
                st.markdown("### 📚 Sources")
                for i, s in enumerate(sources, 1):
                    with st.expander(f"Source {i}: {s['metadata'].get('paper_title', 'Unknown Paper')}"):
                        st.write(f"**Authors:** {s['metadata'].get('authors', 'Unknown')}")
                        st.write(f"**Year:** {s['metadata'].get('year', 'N/A')}")
                        if 'abstract' in s['metadata']:
                            st.write(f"**Abstract:** {s['metadata']['abstract'][:200]}...")
            else:
                st.info("No sources found for this query.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.write("Please try again or check your configuration.")

    # Display history
    if st.session_state.history:
        st.markdown("---")
        st.subheader("📜 Query History")
        for i, item in enumerate(reversed(st.session_state.history[-5:])):  # Show last 5
            with st.expander(f"Q: {item['question'][:50]}..."):
                st.write(f"**Question:** {item['question']}")
                st.write(f"**Answer:** {item['answer']}")
                if item['sources']:
                    st.write("**Sources:**")
                    for s in item['sources'][:3]:  # Show first 3 sources
                        st.write(f"- {s['metadata'].get('paper_title', 'Unknown')}")

with tab2:
    st.write("Browse and search through the loaded academic papers.")
    
    # Search/filter
    search_term = st.text_input("Search papers by title, author, or topic:")
    
    # Filter papers
    papers = catalog.get("papers", [])
    if search_term:
        filtered_papers = [
            p for p in papers 
            if search_term.lower() in p.get('title', '').lower() or
               any(search_term.lower() in author.lower() for author in p.get('authors', [])) or
               any(search_term.lower() in topic.lower() for topic in p.get('topics', []))
        ]
    else:
        filtered_papers = papers
    
    st.write(f"Showing {len(filtered_papers)} papers")
    
    # Display papers
    for paper in filtered_papers:
        with st.expander(f"📄 {paper.get('title', 'Unknown Title')}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Authors:** {', '.join(paper.get('authors', ['Unknown']))}")
                st.write(f"**Year:** {paper.get('year', 'N/A')}")
                st.write(f"**Venue:** {paper.get('venue', 'N/A')}")
                if paper.get('topics'):
                    st.write(f"**Topics:** {', '.join(paper.get('topics', []))}")
            with col2:
                if paper.get('doi'):
                    st.markdown(f"[DOI Link]({paper['doi']})")
            
            if paper.get('abstract'):
                st.write(f"**Abstract:** {paper['abstract']}")