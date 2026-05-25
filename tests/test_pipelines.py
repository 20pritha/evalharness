"""Tests for the pipeline registry."""

import pytest

from evalharness import register_pipeline, get_pipeline
from evalharness.pipelines import _REGISTRY


@pytest.fixture(autouse=True)
def clear_registry():
    """Reset registry between tests so they're isolated."""
    snapshot = dict(_REGISTRY)
    _REGISTRY.clear()
    yield
    _REGISTRY.clear()
    _REGISTRY.update(snapshot)


def test_register_and_retrieve():
    @register_pipeline("test_rag")
    def my_rag(question: str) -> dict:
        return {"answer": "stub", "context": []}

    retrieved = get_pipeline("test_rag")
    assert retrieved is my_rag
    assert retrieved("anything")["answer"] == "stub"


def test_duplicate_registration_raises():
    @register_pipeline("dup")
    def first(q): return {"answer": "1", "context": []}

    with pytest.raises(ValueError, match="already registered"):
        @register_pipeline("dup")
        def second(q): return {"answer": "2", "context": []}


def test_get_unregistered_raises():
    with pytest.raises(KeyError, match="not registered"):
        get_pipeline("doesnt_exist")
