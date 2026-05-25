"""Tests for the storage layer. The most important property to verify is
that ground truth never leaks to the answering side."""

import tempfile
from pathlib import Path

import pytest

from evalharness.storage import Storage


@pytest.fixture
def storage():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield Storage(db_path)
    Path(db_path).unlink(missing_ok=True)


def test_load_and_fetch_for_agent(storage):
    """Agent-side fetch returns questions but never expected_answer."""
    storage.load_questions("test_set", [
        {"question": "Q1?", "expected_answer": "secret_A1"},
        {"question": "Q2?", "expected_answer": "secret_A2"},
    ])
    fetched = storage.fetch_questions_for_agent("test_set")
    assert len(fetched) == 2
    for row in fetched:
        assert "expected_answer" not in row, "Ground truth leaked to agent side!"
        assert "question" in row
        assert "id" in row


def test_judge_side_includes_ground_truth(storage):
    """Judge-side fetch must include expected_answer (it's allowed there)."""
    storage.load_questions("test_set", [
        {"question": "Q1?", "expected_answer": "A1"},
    ])
    fetched = storage.fetch_questions_for_judge("test_set")
    assert fetched[0]["expected_answer"] == "A1"


def test_atomic_run_ids(storage):
    """Concurrent run creation must produce unique sequential IDs."""
    id1 = storage.create_run("pipe", "set")
    id2 = storage.create_run("pipe", "set")
    id3 = storage.create_run("pipe", "set")
    assert id1 < id2 < id3
    assert id2 == id1 + 1
    assert id3 == id2 + 1


def test_summarize_run_with_no_scores(storage):
    """Summarizing an empty run returns zero counts, not an error."""
    run_id = storage.create_run("pipe", "set")
    summary = storage.summarize_run(run_id)
    assert summary["n"] == 0
    assert summary["metrics"] == {}


def test_summarize_run_aggregates_metrics(storage):
    """Mean and std are computed correctly across results."""
    storage.load_questions("set", [
        {"question": "Q1?", "expected_answer": "A1"},
        {"question": "Q2?", "expected_answer": "A2"},
    ])
    run_id = storage.create_run("pipe", "set")
    questions = storage.fetch_questions_for_judge("set")

    storage.persist_result(run_id, questions[0]["id"], "answer1", ["ctx1"])
    storage.persist_result(run_id, questions[1]["id"], "answer2", ["ctx2"])

    results = storage.fetch_results_for_judge(run_id)
    storage.write_scores(results[0]["result_id"], {"faithfulness": 0.8})
    storage.write_scores(results[1]["result_id"], {"faithfulness": 1.0})

    summary = storage.summarize_run(run_id)
    assert summary["n"] == 2
    assert summary["metrics"]["faithfulness"]["mean"] == 0.9
    assert summary["metrics"]["faithfulness"]["n"] == 2
