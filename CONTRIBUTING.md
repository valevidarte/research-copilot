# Contributing to Research Copilot

Thank you for your interest in contributing to Research Copilot! This document provides guidelines and instructions for contributing.

## 🎯 Code Quality Standards

### Python Style Guide
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines
- Use type hints for all function parameters and return values
- Maximum line length: 100 characters
- Use 4 spaces for indentation (no tabs)

### Docstring Format
Use Google-style docstrings for all functions and classes:

```python
def retrieve_documents(query: str, n_results: int = 5) -> List[Dict]:
    """
    Retrieve relevant documents for a query.
    
    This is a description of what the function does, explaining the algorithm
    or logic used. Can span multiple lines.
    
    Args:
        query: The search query string
        n_results: Number of results to return (default: 5)
        
    Returns:
        List of dictionaries containing:
            - text: Document content
            - metadata: Dict with document info
            - score: Similarity score (0-1)
            
    Raises:
        ValueError: If query is empty
        Exception: If search backend fails
        
    Example:
        >>> docs = retrieve_documents("What is RAG?", n_results=3)
        >>> print(docs[0]['text'])
    """
```

### Error Handling
- Use specific exceptions (not bare `except:`)
- Log errors with context using loguru: `logger.error(f"Error: {e}", exc_info=True)`
- Provide user-friendly error messages in UI
- Always validate inputs before processing

```python
def process_pdf(pdf_path: str) -> str:
    """Process PDF file."""
    # Input validation
    if not pdf_path or not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    try:
        # Core logic
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        logger.error(f"PDF processing failed: {e}", exc_info=True)
        raise
```

## 🔄 Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Keep commits small and focused
- Write descriptive commit messages
- Test your changes thoroughly

### 3. Run Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Check coverage
pytest tests/ --cov=src
```

### 4. Code Quality Checks
```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/
pylint src/

# Type checking
mypy src/
```

### 5. Submit Pull Request
- Reference any related issues
- Provide clear description of changes
- Ensure all tests pass
- Update documentation if needed

## 📝 Module-Specific Guidelines

### Adding New Prompt Strategies

Edit `prompts/templates.py`:

```python
def get_prompt(strategy: str) -> str:
    """Get prompt template by strategy name."""
    strategies = {
        "v1": SYSTEM_PROMPT_V1_DELIMITERS,
        "v2": SYSTEM_PROMPT_V2_JSON,
        # Add your new strategy here
        "v5_custom": """
        You are an expert research assistant...
        """
    }
    if strategy not in strategies:
        raise ValueError(f"Unknown strategy: {strategy}")
    return strategies[strategy]
```

### Adding New Embedding Models

Edit in `src/embedding/embedder.py`:

```python
class OpenAIEmbedder:
    def __init__(self, model: str = "text-embedding-3-small"):
        """Initialize with any OpenAI embedding model."""
        valid_models = [
            "text-embedding-3-small",
            "text-embedding-3-large",
            # Add new models here
        ]
        if model not in valid_models:
            raise ValueError(f"Model {model} not supported")
        self.model = model
```

### Adding New Vector Stores

Create new file in `src/vectorstore/new_store.py`:

```python
"""New vector store implementation."""

class MyVectorStore:
    """
    Implement a new vector store backend.
    
    Must implement these methods:
        - create_collection(name: str)
        - add_documents(ids, documents, embeddings, metadatas)
        - query(query_embedding, n_results, where)
    """
    
    def create_collection(self, name: str):
        """Create a collection."""
        pass
    
    def add_documents(self, ids, documents, embeddings, metadatas):
        """Add documents to collection."""
        pass
    
    def query(self, query_embedding, n_results, where=None):
        """Query the store."""
        pass
```

## 🧪 Testing Guidelines

### Write Tests for New Features
```python
# tests/test_my_feature.py

import pytest
from src.my_module import MyClass

class TestMyFeature:
    """Test suite for my feature."""
    
    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        return MyClass()
    
    def test_basic_functionality(self, setup):
        """Test basic operation."""
        result = setup.do_something()
        assert result is not None
        assert len(result) > 0
    
    def test_error_handling(self, setup):
        """Test error handling."""
        with pytest.raises(ValueError):
            setup.invalid_operation()
```

### Test Coverage Requirement
- Aim for at least 80% code coverage
- All critical paths must be tested
- Include edge cases and error conditions

## 📚 Documentation Guidelines

### Update README
- Add feature to list of features
- Update technical specifications if applicable
- Add usage examples
- Update troubleshooting if relevant

### Update Code Comments
- Explain **why**, not **what**
- Keep comments concise
- Update comments if logic changes

### Add Docstrings
- Every public function/class must have a docstring
- Include type hints
- Provide usage examples for complex functions

## 🐛 Bug Reports

When reporting bugs, provide:
1. **Description**: What is the bug?
2. **Steps to Reproduce**: How to trigger it?
3. **Expected Behavior**: What should happen?
4. **Actual Behavior**: What happened instead?
5. **Environment**: OS, Python version, installed packages
6. **Error Traceback**: Full stack trace if applicable
7. **Screenshots**: For UI issues

Example:
```
## Bug: RAG Query Fails with Large Papers

**Description**: Queries fail when papers have >10000 tokens

**Steps**:
1. Ingest a long paper (>10k tokens)
2. Run a query
3. Get error

**Expected**: Query should work with large papers
**Actual**: ValueError: Chunk size exceeded

**Environment**: Windows 10, Python 3.10, streamlit 1.28

**Error**:
```
ValueError: Chunk size exceeded
  File "src/chunking/chunker.py", line 45
```

## ✅ Checklist Before Submitting PR

- [ ] Code follows PEP 8 guidelines
-[ ] All docstrings are present and correct
- [ ] Type hints are added
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Code coverage is acceptable
- [ ] No hardcoded secrets or credentials
- [ ] Documentation is updated
- [ ] Commit messages are descriptive
- [ ] No merge conflicts

## 🤝 Community Notes

- Be respectful and inclusive
- Assume good intent in discussions
- Ask for clarification when needed
- Help others when you can
- Provide constructive feedback

## 📞 Need Help?

- Check existing issues and PRs
- Review documentation
- Comment on related issues
- Open a new discussion

## 📄 License

By contributing, you agree that your contributions will be licensed under the same MIT License as the project.

---

**Thank you for making Research Copilot better!** 🎉
