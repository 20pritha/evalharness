"""FastMCP server exposing the 4 orchestration tools.

This is the heart of evalharness. Each tool is a thin orchestration wrapper
around the storage + judge + metrics modules. The agent drives the flow.
"""

from typing import Any

from evalharness.judges import get_judge, list_judges
from evalharness.metrics import get_metric, list_metrics
from evalharness.pipelines import get_pipeline, list_pipelines
from evalharness.storage import Storage


def build_server(db_path: str = "./evalharness.db"):
    """Build and return a FastMCP server instance."""
    try:
        from fastmcp import FastMCP
    except ImportError as e:
        raise ImportError("Install fastmcp: pip install fastmcp") from e

    mcp = FastMCP("evalharness")
    storage = Storage(db_path)

    # ─────────────────────────────────────────────────────────────────
    # Tool 1: fetch_questions
    # ─────────────────────────────────────────────────────────────────
    @mcp.tool()
    def fetch_questions(set_name: str) -> dict[str, Any]:
        """Fetch a test question set by name. Returns questions WITHOUT
        expected answers (ground truth is isolated at the DB layer).

        Args:
            set_name: name of the question set (e.g. "qfi_v1")
        """
        questions = storage.fetch_questions_for_agent(set_name)
        return {
            "set_name": set_name,
            "count": len(questions),
            "questions": questions,
        }

    # ─────────────────────────────────────────────────────────────────
    # Tool 2: run_pipeline
    # ─────────────────────────────────────────────────────────────────
    @mcp.tool()
    def run_pipeline(
        pipeline_name: str, question_set: str
    ) -> dict[str, Any]:
        """Invoke a registered RAG pipeline against every question in a set.
        Creates a new run record and persists each answer/context tuple atomically.

        Args:
            pipeline_name: name of the registered pipeline
            question_set: name of the question set to run against

        Returns:
            run_id, count, and status
        """
        pipeline = get_pipeline(pipeline_name)
        questions = storage.fetch_questions_for_agent(question_set)
        run_id = storage.create_run(pipeline_name, question_set)

        for q in questions:
            result = pipeline(q["question"])
            storage.persist_result(
                run_id=run_id,
                question_id=q["id"],
                answer=result["answer"],
                context=result.get("context", []),
            )

        storage.complete_run(run_id)
        return {
            "run_id": run_id,
            "pipeline": pipeline_name,
            "question_set": question_set,
            "count": len(questions),
            "status": "completed",
        }

    # ─────────────────────────────────────────────────────────────────
    # Tool 3: score_run
    # ─────────────────────────────────────────────────────────────────
    @mcp.tool()
    def score_run(
        run_id: int,
        judge: str = "openai",
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Score a completed run with LLM-as-judge across configurable metrics.

        Args:
            run_id: ID of the run to score
            judge: judge provider (openai, gemini, anthropic)
            metrics: list of metric names. Defaults to ["faithfulness", "relevance", "hallucination"]
        """
        if metrics is None:
            metrics = ["faithfulness", "relevance", "hallucination"]

        judge_instance = get_judge(judge)
        metric_instances = [get_metric(m) for m in metrics]

        results = storage.fetch_results_for_judge(run_id)

        for r in results:
            scores: dict[str, float] = {}
            for metric in metric_instances:
                prompt = metric.build_prompt(
                    question=r["question"],
                    answer=r["answer"],
                    context=r["context"],
                    expected=r.get("expected_answer"),
                )
                if not prompt:  # metric signaled skip
                    continue
                raw = judge_instance.score(prompt)
                scores[metric.name] = metric.parse_score(raw)
            storage.write_scores(r["result_id"], scores)

        return storage.summarize_run(run_id)

    # ─────────────────────────────────────────────────────────────────
    # Tool 4: list_available
    # ─────────────────────────────────────────────────────────────────
    @mcp.tool()
    def list_available() -> dict[str, list[str]]:
        """List registered pipelines, judges, and metrics available on this server."""
        return {
            "pipelines": list_pipelines(),
            "judges": list_judges(),
            "metrics": list_metrics(),
        }

    return mcp
