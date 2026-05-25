"""evalharness — agentic LLM evaluation harness."""

__version__ = "0.1.0"

from evalharness.pipelines import register_pipeline, get_pipeline

__all__ = ["register_pipeline", "get_pipeline", "__version__"]
