# Quick Start Guide - Research Copilot

## 5-Minute Setup

### Step 1: Clone/Navigate to Project
```bash
cd research-copilot
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows PowerShell
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up API Key
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Step 5: Prepare Papers
- Add 20 PDF papers to the `papers/` folder
- Update `papers/paper_catalog.json` with metadata

### Step 6: Ingest Papers
```bash
python src/ingest.py
```

### Step 7: Run Application
```bash
streamlit run app/main.py
```

Visit: `http://localhost:8501`

---

## Where to Find Papers

### Free Academic Resources
- [arXiv.org](https://arxiv.org) - Free preprints
- [Google Scholar](https://scholar.google.com) - Search and link to papers
- [Semantic Scholar](https://www.semanticscholar.org/) - AI-powered search
- [SSRN](https://ssrn.com) - Social science papers

### Specialized Databases for Your Topic
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/) - Medical/health papers
- [JSTOR Daily](https://daily.jstor.org/) - Open access articles
- [Project MUSE](https://muse.jhu.edu/) - Humanities and social sciences
- [RepEC](https://repec.org/) - Economics papers

### Search Terms for Memory & Human Rights in Peru
- "Truth and Reconciliation Commission Peru CVR"
- "Peruvian human rights violations documentation"
- "transitional justice Peru"
- "indigenous memory Peru"
- "reconciliation Peru justice"
- "historical memory Latin America Peru"

---

## Sample Paper Catalog Entry

```json
{
  "id": "paper_001",
  "title": "Memory, Justice, and Democracy in Peru",
  "authors": ["Author, A.", "Author, B."],
  "year": 2021,
  "venue": "Journal of Human Rights Studies",
  "doi": "10.1234/example.doi",
  "filename": "author_2021_memory.pdf",
  "topics": ["memory", "justice", "Peru", "reconciliation"],
  "abstract": "This paper examines the role of memory in Peru's transitional justice process..."
}
```

---

## Testing the System

### Run Tests
```bash
pytest tests/ -v
```

### Run Evaluation
```bash
python eval/evaluate.py
```

### Test with Sample Questions
Once papers are ingested, the app has 20 pre-loaded test questions:
- Simple factual questions
- Complex analytical questions
- Synthesis questions
- Edge cases

---

## Troubleshooting

### Issue: "OpenAI API Key error"
**Solution:** Ensure your `.env` file has `OPENAI_API_KEY=sk-...`

### Issue: "No papers found"
**Solution:** 
1. Check papers are in `papers/` folder (should be PDFs)
2. Update `papers/paper_catalog.json` with the papers
3. Run `python src/ingest.py`

### Issue: "ChromaDB connection error"
**Solution:** Delete `chroma_db/` folder and restart the app

### Issue: "PDF extraction failed"
**Solution:** 
- Ensure PDF is not corrupted
- Try opening it in a PDF reader first
- Check file size (very large PDFs may have issues)

---

## Next Steps

1. **Add Papers:** Gather 20 papers on memory and human rights in Peru
2. **Update Catalog:** Fill in `papers/paper_catalog.json`
3. **Ingest:** Run `python src/ingest.py`
4. **Test:** Ask questions in the chat interface
5. **Evaluate:** Run evaluation on test questions
6. **Record Video:** Demonstrate the system (3-5 minutes)
7. **Submit:** Push to GitHub and submit links

---

## Project Timeline

- **Day 1-2:** Gather papers and update catalog
- **Day 2-3:** Test ingestion and retrieval
- **Day 3-4:** Verify all features work
- **Day 4-5:** Record demonstration video
- **Day 5:** Final submission

---

## Support

Check the main [README.md](../README.md) for:
- Full documentation
- Architecture details
- API resources
- Troubleshooting guide
