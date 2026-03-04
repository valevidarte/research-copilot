"""Evaluation script for RAG pipeline."""
import json
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_test_questions(filepath: str) -> List[Dict]:
    """Load test questions from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("test_questions", [])


def evaluate_response(response: str, question: Dict) -> Dict:
    """
    Evaluate a response based on test question criteria.
    
    Args:
        response: Generated response text
        question: Test question with expected content
        
    Returns:
        Evaluation metrics dict
    """
    metrics = {
        "question_id": question["id"],
        "category": question["category"],
        "length": len(response),
        "has_citations": "(" in response and ")" in response,
        "expected_topics_found": 0,
        "total_expected_topics": len(question.get("expected_topics", [])),
        "relevance_check": "not evaluated"
    }
    
    # Check for expected topics
    response_lower = response.lower()
    for topic in question.get("expected_topics", []):
        if topic.lower() in response_lower:
            metrics["expected_topics_found"] += 1
    
    # Calculate topic coverage
    if metrics["total_expected_topics"] > 0:
        metrics["topic_coverage"] = metrics["expected_topics_found"] / metrics["total_expected_topics"]
    else:
        metrics["topic_coverage"] = 0
    
    return metrics


def run_evaluation(questions_filepath: str = "eval/questions.json"):
    """
    Run evaluation on all test questions.
    
    Note: This is a template. Actual evaluation requires calling the RAG pipeline
    which needs an OpenAI API key and ingested papers.
    """
    print("=" * 60)
    print("RESEARCH COPILOT - EVALUATION TEMPLATE")
    print("=" * 60)
    
    # Load questions
    try:
        questions = load_test_questions(questions_filepath)
        print(f"\n✓ Loaded {len(questions)} test questions")
    except FileNotFoundError:
        print(f"\n✗ Questions file not found: {questions_filepath}")
        return
    
    # Group by category
    by_category = {}
    for q in questions:
        cat = q["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(q)
    
    print("\nTest Question Distribution:")
    for category, qs in by_category.items():
        print(f"  {category.upper()}: {len(qs)} questions")
    
    print("\nTo run actual evaluation:")
    print("1. Ensure papers are placed in papers/ directory")
    print("2. Update papers/paper_catalog.json with paper metadata")
    print("3. Run: python src/ingest.py")
    print("4. Then: python eval/evaluate.py --run-queries")
    
    print("\n" + "=" * 60)
    print("Sample Questions by Category:")
    print("=" * 60)
    
    for category, qs in by_category.items():
        print(f"\n{category.upper()} (showing first 2 of {len(qs)}):")
        for q in qs[:2]:
            print(f"  Q{q['id']}: {q['question']}")


if __name__ == "__main__":
    run_evaluation()
