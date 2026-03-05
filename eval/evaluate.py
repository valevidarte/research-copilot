"""Evaluation script for RAG pipeline."""
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_pipeline import RAGPipeline


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


def group_metrics_by_category(all_metrics: List[Dict]) -> Dict:
    """Group evaluation metrics by question category."""
    by_category = {}
    for metric in all_metrics:
        cat = metric["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(metric)
    return by_category
def run_evaluation(questions_filepath: str = "eval/questions.json", run_queries: bool = False):
    """
    Run evaluation on all test questions.
    
    Args:
        questions_filepath: Path to questions JSON file
        run_queries: If True, run queries against the RAG pipeline
    """
    print("=" * 80)
    print("RESEARCH COPILOT - EVALUATION")
    print("=" * 80)
    
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
    
    print("\nSample Questions by Category:")
    print("-" * 80)
    
    for category, qs in by_category.items():
        print(f"\n{category.upper()} (showing first 2 of {len(qs)}):")
        for q in qs[:2]:
            print(f"  Q{q['id']}: {q['question']}")
            print(f"     Topics: {', '.join(q.get('expected_topics', []))}")
    
    # Optional: Run actual evaluation
    if run_queries:
        print("\n" + "=" * 80)
        print("RUNNING ACTUAL QUERIES")
        print("=" * 80)
        
        try:
            rag = RAGPipeline()
            results = []
            
            for i, question in enumerate(questions, 1):
                print(f"\n[{i}/{len(questions)}] Q{question['id']}: {question['question'][:60]}...")
                
                try:
                    answer, sources = rag.query(question['question'])
                    metrics = evaluate_response(answer, question)
                    metrics['answer'] = answer
                    metrics['sources_count'] = len(sources)
                    results.append(metrics)
                    
                    print(f"     ✓ Response length: {metrics['length']} chars")
                    print(f"     ✓ Topic coverage: {metrics['topic_coverage']:.1%}")
                    print(f"     ✓ Has citations: {metrics['has_citations']}")
                    print(f"     ✓ Sources found: {metrics['sources_count']}")
                    
                except Exception as e:
                    print(f"     ✗ Error: {str(e)}")
            
            # Summary statistics
            if results:
                print("\n" + "=" * 80)
                print("EVALUATION SUMMARY")
                print("=" * 80)
                
                avg_length = sum(r['length'] for r in results) / len(results)
                avg_coverage = sum(r['topic_coverage'] for r in results) / len(results)
                with_citations = sum(1 for r in results if r['has_citations']) / len(results)
                avg_sources = sum(r['sources_count'] for r in results) / len(results)
                
                print(f"\nAverage Response Length: {avg_length:.0f} characters")
                print(f"Average Topic Coverage: {avg_coverage:.1%}")
                print(f"Responses with Citations: {with_citations:.1%}")
                print(f"Average Sources Retrieved: {avg_sources:.1f}")
                
                # By category
                grouped = group_metrics_by_category(results)
                print(f"\n{'Category':<15} {'Avg Coverage':<15} {'With Citations':<15} {'Avg Length':<15}")
                print("-" * 60)
                for cat, metrics in grouped.items():
                    cat_coverage = sum(m['topic_coverage'] for m in metrics) / len(metrics)
                    cat_citations = sum(1 for m in metrics if m['has_citations']) / len(metrics)
                    cat_length = sum(m['length'] for m in metrics) / len(metrics)
                    print(f"{cat:<15} {cat_coverage:<14.1%} {cat_citations:<14.1%} {cat_length:<14.0f}")
                
                # Save results
                output_file = Path("eval") / "evaluation_results.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "timestamp": Path(__file__).read_text()[:10],
                        "total_questions": len(questions),
                        "total_results": len(results),
                        "summary": {
                            "avg_response_length": avg_length,
                            "avg_topic_coverage": avg_coverage,
                            "pct_with_citations": with_citations,
                            "avg_sources": avg_sources
                        },
                        "results": results
                    }, f, indent=2, ensure_ascii=False)
                print(f"\n✓ Results saved to {output_file}")
        
        except Exception as e:
            print(f"\n✗ Error running evaluation: {e}")
    
    else:
        print("\n" + "-" * 80)
        print("To run actual queries against the RAG pipeline:")
        print("  1. Ensure papers are ingested: python src/ingest.py")
        print("  2. Run evaluation with queries: python eval/evaluate.py --run-queries")
        print("-" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate RAG pipeline")
    parser.add_argument("--run-queries", action="store_true", help="Run actual queries")
    parser.add_argument("--questions", default="eval/questions.json", help="Questions file path")
    
    args = parser.parse_args()
    
    run_evaluation(questions_filepath=args.questions, run_queries=args.run_queries)


if __name__ == "__main__":
    run_evaluation()
