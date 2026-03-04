"""Custom CSS styling for Streamlit application."""

ACADEMIC_THEME_CSS = """
<style>
/* Main color scheme */
:root {
    --primary-color: #1a1a2e;
    --secondary-color: #16213e;
    --accent-color: #4a4a8a;
    --success-color: #27ae60;
    --warning-color: #f39c12;
    --error-color: #e74c3c;
    --light-bg: #ecf0f1;
    --text-color: #2c3e50;
}

/* Main header */
.main-header {
    font-family: 'Georgia', serif;
    color: var(--primary-color);
    margin-bottom: 2rem;
    border-bottom: 2px solid var(--accent-color);
    padding-bottom: 1rem;
}

/* Citation boxes */
.citation-box {
    background-color: var(--light-bg);
    border-left: 4px solid var(--accent-color);
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
    font-size: 0.95rem;
}

/* Paper cards */
.paper-card {
    background-color: #fafafa;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 4px;
    border-left: 4px solid var(--secondary-color);
    transition: box-shadow 0.3s ease;
}

.paper-card:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Metric boxes */
.metric-box {
    background-color: var(--light-bg);
    padding: 1.5rem;
    border-radius: 4px;
    border-left: 4px solid var(--accent-color);
    text-align: center;
}

.metric-box h3 {
    color: var(--accent-color);
    margin: 0.5rem 0;
}

/* Chat messages */
.chat-message-user {
    background-color: #e3f2fd;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 4px;
}

.chat-message-assistant {
    background-color: #f5f5f5;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 4px;
    border-left: 4px solid var(--success-color);
}

/* Buttons */
.stButton > button {
    background-color: var(--accent-color);
    color: white;
    font-weight: 500;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
}

.stButton > button:hover {
    background-color: var(--secondary-color);
}

/* Sidebar styling */
.sidebar .sidebar-content {
    background-color: var(--light-bg);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 2px solid var(--accent-color);
}

.stTabs [aria-selected="true"] {
    color: var(--accent-color);
}
</style>
"""


def get_academic_theme() -> str:
    """Get academic theme CSS."""
    return ACADEMIC_THEME_CSS


def apply_dark_mode_css() -> str:
    """Get dark mode CSS variant."""
    return """
    <style>
    :root {
        color-scheme: dark;
    }
    </style>
    """
