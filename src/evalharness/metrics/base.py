"""Base interface for evaluation metrics."""

import json
from abc import ABC, abstractmethod

from evalharness.judges.base import BaseJudge


class BaseMetric(ABC):
    """A metric defines a scoring prompt and how to parse the judge's response."""

    name: str

    @abstractmethod
    def build_prompt(
        self, question: str, answer: str, context: list[str], expected: str | None
    ) -> str:
        ...

    def parse_score(self, raw: str) -> float:
        """Default parser — expects {"score": float} JSON. Override for custom logic."""
        try:
            parsed = json.loads(raw)
            return float(parsed.get("score", 0.0))
        except (json.JSONDecodeError, ValueError, TypeError):
            return 0.0

    def evaluate(
        self,
        judge: BaseJudge,
        question: str,
        answer: str,
        context: list[str],
        expected: str | None = None,
    ) -> float:
        prompt = self.build_prompt(question, answer, context, expected)
        raw = judge.score(prompt)
        return self.parse_score(raw)


# Registry
_METRICS: dict[str, type[BaseMetric]] = {}


def register_metric(name: str):
    def decorator(cls: type[BaseMetric]):
        cls.name = name
        _METRICS[name] = cls
        return cls
    return decorator


def get_metric(name: str) -> BaseMetric:
    if name not in _METRICS:
        raise KeyError(f"Metric '{name}' not registered. Available: {list(_METRICS.keys())}")
    return _METRICS[name]()


def list_metrics() -> list[str]:
    return list(_METRICS.keys())
