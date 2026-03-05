# Getting Papers for Research Copilot

## For Memory & Human Rights in Peru Topic

### Step 1: Identify Key Search Terms

**Primary Terms:**
- Truth and Reconciliation Commission (CVR - Comisión de la Verdad y Reconciliación)
- Peru human rights violations
- Transitional justice Peru
- Historical memory Peru
- Peruvian indigenous testimony
- Justice and memory Peru

**Secondary Terms:**
- Victim reparation Peru
- Post-conflict reconciliation Peru
- Memory movements Latin America
- Indigenous rights Peru
- Testimony documentation Peru

### Step 2: Search Databases

#### Free Pre-Print Repositories
1. **arXiv.org** (https://arxiv.org)
   - Search: "Peru memory human rights"
   - Filter: Social sciences, Law

2. **Google Scholar** (https://scholar.google.com)
   - Advanced search with filters for Peru and specific topics
   - Link to full PDFs when available

3. **Semantic Scholar** (https://www.semanticscholar.org)
   - AI-powered search
   - Shows citations and related papers

#### Institutional Access (if available through your university)
- JSTOR Digital Library
- ProQuest Dissertations & Theses
- Oxford Academic
- Cambridge Core
- Sage Journals

#### Open Access Sources
- **Directory of Open Access Journals** (https://doaj.org)
  - Search "memory Peru" or "human rights Peru"
  - Filter by Open Access

- **Government & NGO Reports**
  - Amnesty International publications
  - Human Rights Watch
  - Peru government Truth Commission reports

### Step 3: Suggested Paper Authors

Key researchers in this field:
- **Elizabeth Jelin** - Argentine scholar on memory and justice
- **Alan Angell** - Peru human rights expert
- **David F. Sobrevilla** - Peruvian philosopher on CVR
- **Lissa Lincoln** - Transitional justice Peru
- **Claudia Dary** - Memory and reconciliation Guatemala/Peru
- **Priscilla Hayner** - Transitional justice mechanisms

### Step 4: Government/NGO Sources

Official Peru CVR Materials:
- Peru Truth Commission Final Report
- International Committee of the Red Cross - Peru country reports
- UN Human Rights Council - Peru country reviews
- Inter-American Commission on Human Rights - Peru reports

### Step 5: Citation Trail Method

1. Find one relevant paper
2. Look at its References/Bibliography
3. Look for papers citing it (Google Scholar "Cited by" feature)
4. Build a collection from interconnected papers

### Step 6: Paper Quality Checklist

Before including a paper, verify:
- [ ] Peer-reviewed or official publication
- [ ] Accessible as PDF (or convertible to PDF)
- [ ] Minimum 5 pages
- [ ] Clearly relevant to topic
- [ ] Recent enough (prefer 2015+, need at least 10 from 2020+)
- [ ] In English or Spanish

### Step 7: Organize Downloaded Papers

**Naming Convention:** `paper_001.pdf`, `paper_002.pdf`, ... `paper_020.pdf`

**Folder Structure:**
```
papers/
├── paper_001.pdf
├── paper_002.pdf
├── paper_003.pdf
...
├── paper_020.pdf
└── paper_catalog.json
```

### Step 8: Create Metadata

For each paper, collect:
```
Title: 
Authors: 
Year: 
Venue (Journal/Conference): 
DOI or URL: 
Topics: 
Abstract (first paragraph):
```

### Step 9: Update paper_catalog.json

Use the template in `papers/paper_catalog.json` to add all papers.

### Step 10: Test & Ingest

```bash
python src/ingest.py
```

---

## Recommended Distribution

To have a well-rounded collection:

| Category | Count |
|----------|-------|
| CVR/Truth Commissions | 4-5 |
| Transitional Justice | 3-4 |
| Human Rights Violations | 3-4 |
| Memory & Narrative | 2-3 |
| Indigenous/Victim Perspectives | 2-3 |
| International/Comparative | 2-3 |

---

## Current Status Template

**Number of papers collected:** __/20

**By recency:**
- 2020-2025: __/10+ (required)
- 2015-2020: __ / (good to have)
- Pre-2015: __ (seminal works)

---

## Troubleshooting Paper Collection

**Problem:** Can't find enough recent papers on this specific topic.
**Solution:** Expand to include:
- Latin American transitional justice generally
- Memory studies in post-conflict societies
- Indigenous rights documentation

**Problem:** Many papers require institutional access.
**Solution:** 
- Check your university/library access
- Contact authors directly (many will share PDFs)
- Use ResearchGate or Academia.edu

**Problem:** PDFs are paywalled.
**Solution:**
- Try Google Scholar → Links
- Check pre-print versions on arXiv
- Use Sci-Hub (educational fair use)
- Request from library via interlibrary loan
- Email authors directly

---

## Estimated Timeline

- Finding & evaluating papers: 2-3 hours
- Downloading: 30-60 minutes  
- Organizing & naming: 30 minutes
- Creating metadata: 1-2 hours
- **Total: 4-6 hours**

---

For more help, see [QUICKSTART.md](QUICKSTART.md)
