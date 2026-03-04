"""Main Streamlit application for Research Copilot."""
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import sys
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_pipeline import RAGPipeline


# Page configuration
st.set_page_config(
    page_title="Research Copilot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for academic theme
st.markdown("""
<style>
    .main-header {
        font-family: 'Georgia', serif;
        color: #1a1a2e;
        margin-bottom: 2rem;
    }
    .citation-box {
        background-color: #f0f0f5;
        border-left: 4px solid #4a4a8a;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .paper-card {
        background-color: #fafafa;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
        border: 1px solid #e0e0e0;
    }
    .metric-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 4px;
        border-left: 4px solid #007bff;
    }
</style>
""", unsafe_allow_html=True)


def load_paper_catalog():
    """Load paper catalog from JSON."""
    catalog_path = Path("papers/paper_catalog.json")
    if catalog_path.exists():
        with open(catalog_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"papers": []}


def initialize_session_state():
    """Initialize Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "rag_pipeline" not in st.session_state:
        try:
            with st.spinner("Initializing RAG Pipeline..."):
                st.session_state.rag_pipeline = RAGPipeline()
        except Exception as e:
            st.error(f"Error initializing RAG Pipeline: {e}")
            st.warning("Using fallback mode without RAG features.")
            st.session_state.rag_pipeline = None
    
    if "paper_catalog" not in st.session_state:
        try:
            st.session_state.paper_catalog = load_paper_catalog()
        except Exception as e:
            st.error(f"Error loading paper catalog: {e}")
            st.session_state.paper_catalog = None


def get_all_paper_titles():
    """Get all paper titles from catalog."""
    papers = st.session_state.paper_catalog.get("papers", [])
    return [p.get("title", "Unknown") for p in papers]


def display_citations(citations):
    """Display citations in APA format."""
    if citations:
        st.markdown("### 📖 Sources")
        for citation in citations:
            citation_text = f"**{citation.get('authors', 'Unknown')} ({citation.get('year', 'N/A')})** - {citation.get('paper', 'Unknown Paper')}"
            if citation.get('doi'):
                citation_text += f" - DOI: {citation['doi']}"
            st.markdown(f"- {citation_text}")


def main():
    """Main application."""
    initialize_session_state()
    
    # Header
    st.markdown("<h1 class='main-header'>📚 Research Copilot</h1>", unsafe_allow_html=True)
    st.markdown("*Your AI research assistant for memory, transitional justice, and human rights in Peru*")
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150?text=Logo", width=150)
        st.title("Research Copilot")
        st.markdown("---")
        
        # Paper filter
        st.subheader("Filters")
        selected_papers = st.multiselect(
            "Filter by papers:",
            options=get_all_paper_titles(),
            help="Leave empty to search all papers"
        )
        
        # Prompt strategy selector
        strategy = st.selectbox(
            "Prompt Strategy:",
            {
                "v1": "Clear Instructions with Delimiters",
                "v2": "Structured JSON Output",
                "v3": "Few-Shot Learning",
                "v4": "Chain-of-Thought Reasoning"
            },
            format_func=lambda x: x,
            help="Different strategies produce different response styles"
        )
        
        # Number of results
        n_results = st.slider(
            "Number of documents to retrieve:",
            min_value=1,
            max_value=10,
            value=5,
            help="More documents = more comprehensive context"
        )
        
        st.markdown("---")
        
        # Clear conversation
        if st.button("🔄 Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
        
        # Info
        st.markdown("---")
        st.subheader("About")
        st.markdown("""
        Research Copilot uses Retrieval-Augmented Generation (RAG) to answer 
        questions about academic papers on memory and human rights in Peru.
        
        **Features:**
        - Chat interface
        - Paper filtering
        - Multiple prompt strategies
        - APA citations
        """)
    
    # Main content area
    tabs = st.tabs(["💬 Chat", "📄 Papers", "📊 Analytics", "⚙️ Settings"])
    
    # Tab 1: Chat
    with tabs[0]:
        st.subheader("Chat with Your Papers")
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "citations" in message and message["citations"]:
                    display_citations(message["citations"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about memory and human rights in Peru..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Get response
            with st.spinner("🔍 Searching papers and generating response..."):
                filter_papers = None
                if selected_papers:
                    # Map titles to IDs
                    catalog_papers = st.session_state.paper_catalog.get("papers", [])
                    filter_papers = [
                        p["id"] for p in catalog_papers 
                        if p.get("title") in selected_papers
                    ]
                
                response, citations = st.session_state.rag_pipeline.query(
                    question=prompt,
                    strategy=strategy,
                    n_results=n_results,
                    filter_papers=filter_papers
                )
            
            # Add assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "citations": citations
            })
            
            st.rerun()
    
    # Tab 2: Papers
    with tabs[1]:
        st.subheader("Paper Browser")
        
        papers = st.session_state.paper_catalog.get("papers", [])
        
        if not papers:
            st.warning("No papers loaded yet. Please add papers to the catalog.")
        else:
            # Search
            search_query = st.text_input("Search papers by title, author, or topic:")
            
            # Filters
            col1, col2 = st.columns(2)
            with col1:
                year_range = st.slider("Year range:", 2000, 2025, (2000, 2025))
            with col2:
                topic_filter = st.multiselect("Topics:", ["memory", "human rights", "Peru", "justice", "reconciliation"])
            
            # Display papers
            filtered_papers = papers
            
            if search_query:
                search_lower = search_query.lower()
                filtered_papers = [
                    p for p in filtered_papers
                    if search_lower in p.get("title", "").lower() or
                       search_lower in " ".join(p.get("authors", [])).lower()
                ]
            
            filtered_papers = [
                p for p in filtered_papers
                if year_range[0] <= p.get("year", 2025) <= year_range[1]
            ]
            
            if topic_filter:
                filtered_papers = [
                    p for p in filtered_papers
                    if any(t in p.get("topics", []) for t in topic_filter)
                ]
            
            st.write(f"**Found {len(filtered_papers)} papers**")
            
            for paper in filtered_papers:
                with st.container():
                    st.markdown(f"""
                    <div class='paper-card'>
                    <b>{paper.get('title', 'Unknown')}</b><br>
                    <small>{', '.join(paper.get('authors', []))} ({paper.get('year', 'N/A')})</small><br>
                    <small>{paper.get('venue', 'Unknown Venue')}</small><br>
                    {f"DOI: {paper.get('doi', 'N/A')}" if paper.get('doi') else ""}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Tab 3: Analytics
    with tabs[2]:
        st.subheader("Analytics Dashboard")
        
        papers = st.session_state.paper_catalog.get("papers", [])
        
        if papers:
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class='metric-box'>
                <b>Total Papers</b><br>
                <h3>{len(papers)}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                years = [p.get("year", 0) for p in papers]
                avg_year = sum(years) / len(years) if years else 0
                st.markdown(f"""
                <div class='metric-box'>
                <b>Average Year</b><br>
                <h3>{int(avg_year)}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                recent = len([p for p in papers if p.get("year", 0) >= 2020])
                st.markdown(f"""
                <div class='metric-box'>
                <b>Recent (2020+)</b><br>
                <h3>{recent}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                queries = len([m for m in st.session_state.messages if m["role"] == "user"])
                st.markdown(f"""
                <div class='metric-box'>
                <b>Queries</b><br>
                <h3>{queries}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            # Charts
            st.markdown("---")
            
            # Papers by year
            year_counts = {}
            for paper in papers:
                year = paper.get("year", 0)
                year_counts[year] = year_counts.get(year, 0) + 1
            
            if year_counts:
                st.subheader("Papers by Year")
                years = sorted(year_counts.keys())
                counts = [year_counts[y] for y in years]
                st.bar_chart(data={"Year": years, "Count": counts}, use_container_width=True)
        else:
            st.info("No papers loaded yet.")
    
    # Tab 4: Settings
    with tabs[3]:
        st.subheader("Settings")
        
        st.markdown("### Pipeline Configuration")
        st.markdown("""
        **Current Settings:**
        - Embedding Model: text-embedding-3-small
        - Generation Model: gpt-4-turbo
        - Vector Store: ChromaDB
        - Chunk Size: 512 tokens
        - Chunk Overlap: 50 tokens
        """)
        
        st.markdown("### Information")
        st.markdown("""
        **About this Project:**
        
        Research Copilot is an AI-powered research assistant that uses Retrieval-Augmented 
        Generation (RAG) to help researchers explore academic literature on memory and 
        human rights in Peru.
        
        **Technologies:**
        - OpenAI GPT-4 for text generation
        - ChromaDB for vector storage
        - Python for backend
        - Streamlit for web interface
        """)


if __name__ == "__main__":
    main()
