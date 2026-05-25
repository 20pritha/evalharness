"""Tests for built-in metrics — verifies prompt construction and score parsing."""

from evalharness.metrics import get_metric


def test_faithfulness_prompt_includes_context():
    metric = get_metric("faithfulness")
    prompt = metric.build_prompt(
        question="What is X?",
        answer="X is Y.",
        context=["X is defined as Y in the docs.", "Z is unrelated."],
        expected=None,
    )
    assert "What is X?" in prompt
    assert "X is Y." in prompt
    assert "X is defined as Y in the docs." in prompt


def test_correctness_skips_without_expected():
    """Correctness metric returns empty prompt if no ground truth available."""
    metric = get_metric("correctness")
    prompt = metric.build_prompt(
        question="Q",
        answer="A",
        context=[],
        expected=None,
    )
    assert prompt == ""  # signals: skip


def test_score_parsing_handles_valid_json():
    metric = get_metric("faithfulness")
    assert metric.parse_score('{"score": 0.85, "reasoning": "well-grounded"}') == 0.85


def test_score_parsing_handles_malformed_response():
    """A bad LLM response shouldn't crash the run — return 0.0 and move on."""
    metric = get_metric("faithfulness")
    assert metric.parse_score("not json at all") == 0.0
    assert metric.parse_score("{broken json") == 0.0
    assert metric.parse_score('{"score": "not_a_number"}') == 0.0
