"""LLM-as-judge providers. Importing each module triggers registration."""

from evalharness.judges.base import BaseJudge, get_judge, list_judges, register_judge

# Lazy imports — only register if the provider's deps are installed
def _try_import():
    for module in ("openai_judge", "gemini_judge", "anthropic_judge"):
        try:
            __import__(f"evalharness.judges.{module}")
        except ImportError:
            pass

_try_import()

__all__ = ["BaseJudge", "get_judge", "list_judges", "register_judge"]
