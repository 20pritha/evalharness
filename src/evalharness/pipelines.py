"""Registry for user-defined RAG pipelines."""

from typing import Callable, Protocol


class PipelineFn(Protocol):
    """A user RAG pipeline takes a question and returns answer + context."""

    def __call__(self, question: str) -> dict: ...


_REGISTRY: dict[str, PipelineFn] = {}


def register_pipeline(name: str) -> Callable[[PipelineFn], PipelineFn]:
    """Decorator to register a RAG pipeline by name.

    Example:
        @register_pipeline("my_rag")
        def my_rag(question: str) -> dict:
            return {"answer": "...", "context": ["...", "..."]}
    """

    def decorator(fn: PipelineFn) -> PipelineFn:
        if name in _REGISTRY:
            raise ValueError(f"Pipeline '{name}' is already registered")
        _REGISTRY[name] = fn
        return fn

    return decorator


def get_pipeline(name: str) -> PipelineFn:
    """Retrieve a registered pipeline by name."""
    if name not in _REGISTRY:
        registered = list(_REGISTRY.keys())
        raise KeyError(
            f"Pipeline '{name}' not registered. Available: {registered or 'none'}"
        )
    return _REGISTRY[name]


def list_pipelines() -> list[str]:
    """Return all registered pipeline names."""
    return list(_REGISTRY.keys())
