"""End-to-end demo: register a mock pipeline, run it, score with Gemini."""

from evalharness import register_pipeline
from evalharness.pipelines import get_pipeline
from evalharness.storage import Storage
from evalharness.judges import get_judge
from evalharness.metrics import get_metric

# 1. Register a mock pipeline (in real life this is your RAG system)
@register_pipeline("mock_rag")
def mock_rag(question: str) -> dict:
    answers = {
        "What is the capital of France?": {
            "answer": "Paris is the capital of France.",
            "context": ["France's capital is Paris."],
        },
        "Who wrote Hamlet?": {
            "answer": "William Shakespeare wrote Hamlet around 1600.",
            "context": ["Hamlet is a tragedy by William Shakespeare."],
        },
    }
    return answers.get(question, {"answer": "I don't know.", "context": []})

# 2. Simulate the MCP flow manually
storage = Storage("./evalharness.db")
pipeline = get_pipeline("mock_rag")

# Fetch questions (agent side — no ground truth)
questions = storage.fetch_questions_for_agent("demo")
print(f"Fetched {len(questions)} questions")

# Run the pipeline
run_id = storage.create_run("mock_rag", "demo")
print(f"Created run {run_id}")

for q in questions:
    result = pipeline(q["question"])
    storage.persist_result(run_id, q["id"], result["answer"], result["context"])
    print(f"  Q: {q['question']!r:60s} → A: {result['answer']!r}")

storage.complete_run(run_id)

# Score with Gemini
print("\nScoring with Gemini...")
judge = get_judge("gemini")
results = storage.fetch_results_for_judge(run_id)

for r in results:
    scores = {}
    for metric_name in ["faithfulness", "relevance", "hallucination"]:
        metric = get_metric(metric_name)
        score = metric.evaluate(judge, r["question"], r["answer"], r["context"], r.get("expected_answer"))
        scores[metric_name] = score
    storage.write_scores(r["result_id"], scores)
    print(f"  {r['question']!r:60s} → {scores}")

# Summary
summary = storage.summarize_run(run_id)
print(f"\nRun {run_id} summary:")
for metric, stats in summary["metrics"].items():
    print(f"  {metric:15s} mean={stats['mean']:.3f} ± {stats['std']:.3f}  (n={stats['n']})")
