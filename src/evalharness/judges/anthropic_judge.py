"""Anthropic Claude judge implementation."""

import os

from evalharness.judges.base import BaseJudge, register_judge


@register_judge("anthropic")
class AnthropicJudge(BaseJudge):
    def __init__(self, model: str = "claude-sonnet-4-6", api_key: str | None = None):
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise ImportError(
                "Anthropic judge requires `pip install evalharness[anthropic]`"
            ) from e

        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model

    def score(self, prompt: str) -> str:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text if resp.content else "{}"
