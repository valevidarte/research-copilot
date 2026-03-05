# 🚀 Getting Started Guide

Complete step-by-step guide to get Research Copilot running in minutes.

## ⚡ Ultra-Quick Start (5 minutes)

### Windows
```powershell
# 1. Navigate to project
cd research-copilot

# 2. Run setup
.\setup.bat

# Done! Visit http://localhost:8501
```

### macOS/Linux
```bash
# 1. Navigate to project
cd research-copilot

# 2. Run setup
bash setup.sh

# Done! Visit http://localhost:8501
```

---

## 📋 Prerequisites Check

Before starting, ensure you have:

- ✅ Python 3.10+ installed
- ✅ pip package manager
- ✅ OpenAI API key (get one free at https://platform.openai.com)
- ✅ 2GB free disk space
- ✅ Internet connection

**Check Python Version:**
```bash
python --version          # Windows
python3 --version        # macOS/Linux
```

---

## 🔧 Detailed Setup (If Auto-Setup Fails)

### Step 1: Clone Repository
```bash
git clone https://github.com/valevidarte/research-copilot.git
cd research-copilot
```

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux (Bash):**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` or `(.venv)` at the start of your terminal line.

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- streamlit (web UI)
- openai (LLM & embeddings)
- chromadb (vector database)
- pdfplumber (PDF processing)
- loguru (logging)
- And other required packages

### Step 4: Configure OpenAI API

**Create .env file:**
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

**Edit .env and add your API key:**
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Get your key from: https://platform.openai.com/api-keys

### Step 5: Prepare Papers (Optional)

To use with actual papers:

1. Place 20-25 PDF files in `papers/` directory
2. Update `papers/paper_catalog.json` with metadata

Example metadata:
```json
{
  "papers": [
    {
      "id": "paper_001",
      "filename": "paper_001.pdf",
      "title": "Your Paper Title",
      "authors": ["Author 1", "Author 2"],
      "year": 2023,
      "venue": "Journal Name",
      "doi": "10.1234/example",
      "topics": ["topic1", "topic2"]
    }
  ]
}
```

### Step 6: Ingest Papers (Optional)

If you added papers:
```bash
python src/ingest.py
```

This will:
- Extract text from PDFs
- Create searchable chunks
- Generate embeddings
- Store in vector database

Progress will be shown with a progress bar.

### Step 7: Run the Application

```bash
streamlit run streamlit_app.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Open your browser to: **http://localhost:8501**

---

## 🎯 First Time Using

### The Interface

**Tab 1: Q&A Assistant**
- Type your question
- Click "🔍 Search"
- Get answer with citations

**Tab 2: Paper Browser**
- Search papers by title, author, topic
- Click to expand and see details
- View metadata and abstracts

**Sidebar**
- Statistics about loaded papers
- Clear history button
- Configuration details

### Example Queries

Try these to test the system:

1. **Factual**: "What is the Truth and Reconciliation Commission?"
2. **Analytical**: "How do memory and justice intersect in Peru?"
3. **Synthesis**: "What are common themes about human rights?"

---

## 🚨 Troubleshooting

### Python Not Found
```bash
# Make sure Python is installed
python --version

# If that doesn't work:
python3 --version
```

### Virtual Environment Issues
```bash
# Try creating fresh venv
rm -rf .venv      # or rmdir /s .venv on Windows
python -m venv .venv
```

### Module Not Found Errors
```bash
# Ensure venv is activated and reinstall
pip install --upgrade pip
pip install -r requirements.txt
```

### OpenAI API Key Error
- Check that OPENAI_API_KEY is in .env
- Use correct API key format (sk-...)
- Key should not have quotes around it
- Restart the app after changing .env

### Slow Performance
- First time will be slower (embeddings are being created)
- Subsequent queries should be ~5-15 seconds
- Check internet connection
- Verify API rate limits

### Chrome/Browser Issues
- Clear browser cache
- Try a different browser
- Check http://localhost:8501 (not https)

### Papers Not Loading
- Ensure PDFs are in `papers/` directory
- Check that `paper_catalog.json` exists
- Run `python src/ingest.py` to index them
- Check for errors in console

---

## ✅ Verify Installation

Run this command to verify everything works:

```bash
# Windows
python -c "from src.rag_pipeline import RAGPipeline; print('✓ Installation successful!')"

# macOS/Linux
python3 -c "from src.rag_pipeline import RAGPipeline; print('✓ Installation successful!')"
```

Expected output: `✓ Installation successful!`

---

## 📚 Next Steps

1. **Explore Features**
   - Try different types of questions
   - Browse papers in the interface
   - Check query history

2. **Add Your Papers**
   - Place PDFs in papers/
   - Update paper_catalog.json
   - Run: `python src/ingest.py`

3. **Customize**
   - Modify prompts in `prompts/templates.py`
   - Adjust embedding settings
   - Change UI in `streamlit_app.py`

4. **Learn More**
   - Read [README.md](README.md) for full documentation
   - Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
   - See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

---

## 💡 Tips & Tricks

### Faster Embeddings
- Use `gpt-3.5-turbo` for generation (faster, cheaper)
- Reduce `n_results` to 3 (fewer documents to process)

### Better Answers
- Use `gpt-4-turbo` model (better reasoning)
- Increase `n_results` to 7-10 (more context)
- Use longer prompts in `prompts/templates.py`

### Development Mode
- Set logging level to DEBUG for verbose output
- Use small paper sets for testing
- Disable rate limiting with: `os.environ["OPENAI_ORG_ID"]=""` 

### Production Deployment
- Use environment variables for secrets
- Add authentication layer
- Deploy on cloud platform (Heroku, AWS, GCP)
- Set up monitoring and logging

---

## 🆘 Still Having Issues?

1. **Check Logs**
   ```bash
   tail -f streamlit_app.log
   ```

2. **Verify Dependencies**
   ```bash
   pip list | grep -E "streamlit|openai|chromadb"
   ```

3. **Test Components**
   ```bash
   python -c "from src.rag_pipeline import RAGPipeline; p = RAGPipeline(); print(p.get_papers_info())"
   ```

4. **Open an Issue**
   - GitHub: https://github.com/valevidarte/research-copilot/issues
   - Include verbose output and system info
   - Attach streamlit_app.log

---

## 📞 Support

- **Documentation**: See README.md
- **Architecture**: See ARCHITECTURE.md  
- **Contributing**: See CONTRIBUTING.md
- **Issues**: GitHub Issues
- **Email**: (if applicable)

---

**Congratulations! You're ready to use Research Copilot!** 🎉

Start exploring papers and asking questions!
