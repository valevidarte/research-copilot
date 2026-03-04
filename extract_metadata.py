import os
import json
import PyPDF2
from pathlib import Path

papers_dir = r"C:\Users\valev\Downloads\research_copilot\papers"
pdf_files = sorted([f for f in os.listdir(papers_dir) if f.endswith('.pdf')])

papers_data = []

for idx, pdf_file in enumerate(pdf_files, 1):
    pdf_path = os.path.join(papers_dir, pdf_file)
    paper_data = {
        "id": f"paper_{idx:03d}",
        "title": pdf_file.replace('.pdf', ''),
        "authors": ["Author TBD"],
        "year": 2024,
        "venue": "Venue TBD",
        "doi": "",
        "filename": pdf_file,
        "topics": ["memory", "human rights", "Peru"],
        "abstract": "Abstract TBD"
    }
    
    # Try to extract metadata from PDF
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            if reader.metadata:
                if reader.metadata.get("/Title"):
                    paper_data["title"] = reader.metadata.get("/Title")
                if reader.metadata.get("/Author"):
                    paper_data["authors"] = [reader.metadata.get("/Author")]
            
            # Get first page text for abstract hint
            if len(reader.pages) > 0:
                text = reader.pages[0].extract_text()
                if text:
                    abstract_hint = text[:500]
                    paper_data["abstract"] = abstract_hint
    except Exception as e:
        print(f"Error reading {pdf_file}: {e}")
    
    papers_data.append(paper_data)
    print(f"{idx}. {paper_data['title']}")

# Display results
for paper in papers_data:
    print(f"\nFile: {paper['filename']}")
    print(f"ID: {paper['id']}")
    print(f"Title: {paper['title']}")
    print(f"---")

# Save to JSON
catalog = {
    "metadata": {
        "topic": "Memoria y derechos humanos en Perú",
        "total_papers": len(papers_data),
        "last_updated": "2026-03-03"
    },
    "papers": papers_data
}

output_path = os.path.join(papers_dir, "paper_catalog_extracted.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"\n✓ Metadata extracted to: {output_path}")
