"""Base interface for LLM-as-judge providers."""

from abc import ABC, abstractmethod


class BaseJudge(ABC):
    """Implement this to add a new judge provider."""

    name: str

    @abstractmethod
    def score(self, prompt: str) -> str:
        """Send a scoring prompt to the judge LLM and return raw text response."""
        ...


# Registry
_JUDGES: dict[str, type[BaseJudge]] = {}


def register_judge(name: str):
    def decorator(cls: type[BaseJudge]):
        cls.name = name
        _JUDGES[name] = cls
        return cls
    return decorator


def get_judge(name: str, **kwargs) -> BaseJudge:
    if name not in _JUDGES:
        raise KeyError(
            f"Judge '{name}' not registered. Available: {list(_JUDGES.keys())}"
        )
    return _JUDGES[name](**kwargs)


def list_judges() -> list[str]:
    return list(_JUDGES.keys())
