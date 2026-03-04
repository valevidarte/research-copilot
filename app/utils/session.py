"""Utility functions for session state management in Streamlit."""


def initialize_session_variables():
    """Initialize all required session variables."""
    session_vars = {
        "messages": [],
        "selected_papers": [],
        "current_strategy": "v1",
        "n_results": 5,
        "paper_catalog": {},
        "rag_pipeline": None,
        "query_history": [],
        "token_usage": 0
    }
    return session_vars


def add_message(session_state, role: str, content: str, citations=None):
    """Add a message to session history."""
    message = {
        "role": role,
        "content": content,
        "timestamp": None,
    }
    if citations:
        message["citations"] = citations
    
    session_state.messages.append(message)


def clear_messages(session_state):
    """Clear message history."""
    session_state.messages = []


def get_paper_titles(session_state) -> list:
    """Get list of all paper titles from catalog."""
    papers = session_state.get("paper_catalog", {}).get("papers", [])
    return [p.get("title", "Unknown") for p in papers]
